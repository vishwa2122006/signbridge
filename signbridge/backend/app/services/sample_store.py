"""
sample_store.py — recorded training samples, in the `samples` table.

Only landmark coordinates are stored (JSONB), never video. A recording moves
through these statuses:
  draft     just recorded by a trainer; only they see it, until they submit
  pending   submitted, waiting for an admin's review
  approved  accepted by an admin: the only recordings used for training and
            replayed to signers as hand signs
  rejected  declined by an admin, with an optional note for the trainer
What an admin records or imports is approved straight away. Recordings of
the Idle ("no sign") class belong to no word: their word_id is NULL.
"""

from typing import Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app import config
from app import db as database
from app.models.tables import APPROVED, DRAFT, PENDING, REJECTED, Sample, User, Word, utcnow

STATUSES = (DRAFT, PENDING, APPROVED, REJECTED)


def count_hand_frames(frames: List[dict]) -> int:
    return sum(1 for f in frames if f.get("left") is not None or f.get("right") is not None)


def save_sample(db: Session, word: Optional[Word], frames: List[dict], aspect: float, *, status: str,
                user: Optional[User] = None, signer_id: Optional[str] = None, source: str = "webcam",
                created_at=None) -> Sample:
    sample = Sample(
        word_id=word.id if word else None,
        user_id=user.id if user else None,
        signer_id=(signer_id or (user.signer_id if user else "unknown"))[:60],
        source=source[:200],
        aspect=aspect,
        num_frames=len(frames),
        hand_frames=count_hand_frames(frames),
        frames=frames,
        status=status,
        created_at=created_at or utcnow(),
    )
    if status == APPROVED and user is not None:
        sample.reviewed_by_id, sample.reviewed_at = user.id, sample.created_at
    db.add(sample)
    db.flush()
    return sample


def _usable():
    """Approved recordings of approved words, plus approved Idle recordings (needs an outer join to Word)."""
    return (Sample.status == APPROVED) & or_(Sample.word_id.is_(None), Word.status == APPROVED)


def training_samples(db: Optional[Session] = None) -> List[dict]:
    with database.session_scope(db) as s:
        rows = s.execute(
            select(Sample.id, Word.concept, Sample.signer_id, Sample.aspect, Sample.frames)
            .outerjoin(Word, Sample.word_id == Word.id).where(_usable()).order_by(Sample.id)
        ).all()
    return [
        {"id": r.id, "concept": r.concept or config.NONE_LABEL, "signer_id": r.signer_id, "aspect": r.aspect,
         "frames": r.frames}
        for r in rows
    ]


def approved_stats(db: Optional[Session] = None) -> Dict[str, dict]:
    """{concept: {"count", "signers", "last_id"}} over the recordings used for training."""
    with database.session_scope(db) as s:
        rows = s.execute(
            select(Word.concept, Sample.signer_id, func.count(), func.max(Sample.id))
            .select_from(Sample).outerjoin(Word, Sample.word_id == Word.id)
            .where(_usable()).group_by(Word.concept, Sample.signer_id)
        ).all()
    out: Dict[str, dict] = {}
    for concept, signer, count, last_id in rows:
        entry = out.setdefault(concept or config.NONE_LABEL, {"count": 0, "signers": [], "last_id": 0})
        entry["count"] += count
        entry["signers"].append(signer)
        entry["last_id"] = max(entry["last_id"], last_id)
    return out


def approved_for_concept(concept: str, db: Optional[Session] = None) -> List[dict]:
    with database.session_scope(db) as s:
        query = (
            select(Sample.id, Sample.signer_id, Sample.aspect, Sample.frames)
            .outerjoin(Word, Sample.word_id == Word.id).where(_usable())
        )
        query = query.where(Sample.word_id.is_(None)) if concept == config.NONE_LABEL else query.where(Word.concept == concept)
        rows = s.execute(query.order_by(Sample.id)).all()
    return [
        {"id": r.id, "concept": concept, "signer_id": r.signer_id, "aspect": r.aspect, "frames": r.frames}
        for r in rows
    ]


def user_stats(db: Session, user: User) -> Dict[str, dict]:
    """Per word, for the Teach page: the user's own recordings by status (`mine`), the latest
    one they may still delete, the note on their latest rejected recording, and the
    approved recordings from everyone (`approved_total`, from `signers` people)."""
    out: Dict[str, dict] = {}

    def entry(concept: Optional[str]) -> dict:
        return out.setdefault(concept or config.NONE_LABEL, {
            "mine": dict.fromkeys(STATUSES, 0), "approved_total": 0, "signers": 0, "last_id": None, "last_note": None,
        })

    deletable = STATUSES if user.is_admin else (DRAFT, PENDING)
    mine = db.execute(
        select(Word.concept, Sample.status, func.count(), func.max(Sample.id))
        .select_from(Sample).outerjoin(Word, Sample.word_id == Word.id)
        .where(Sample.user_id == user.id).group_by(Word.concept, Sample.status)
    )
    for concept, status, count, last_id in mine:
        e = entry(concept)
        e["mine"][status] = count
        if status in deletable:
            e["last_id"] = max(e["last_id"] or 0, last_id)

    notes = db.execute(
        select(Word.concept, Sample.review_note)
        .select_from(Sample).outerjoin(Word, Sample.word_id == Word.id)
        .where(Sample.user_id == user.id, Sample.status == REJECTED, Sample.review_note.is_not(None))
        .order_by(Sample.reviewed_at.desc())
    )
    for concept, note in notes:
        e = entry(concept)
        e["last_note"] = e["last_note"] or note

    for concept, stats in approved_stats(db).items():
        e = entry(concept)
        e["approved_total"], e["signers"] = stats["count"], len(stats["signers"])
    return out
