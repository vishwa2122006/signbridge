"""Admin review: each word's submitted recordings from every trainer, approved
or rejected one by one or in bulk, and the new words trainers propose.

Decisions on recordings are saved as one batch, so a trainer gets a single
email per review instead of one per recording."""

from collections import Counter, defaultdict
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, aliased

from app import config
from app.db import get_db
from app.errors import ApiError
from app.models.schemas import ReviewSamplesRequest, ReviewWordRequest
from app.models.tables import APPROVED, DRAFT, PENDING, REJECTED, Sample, User, Word, utcnow
from app.routers.deps import require_admin
from app.services import notifications
from app.services.vocabulary import vocabulary, word_dict

router = APIRouter(prefix="/review", dependencies=[Depends(require_admin)])

REVIEW_STATUSES = (PENDING, APPROVED, REJECTED)
IDLE_WORD = {
    "sign_id": config.NONE_LABEL, "concept": config.NONE_LABEL, "english": notifications.IDLE_LABEL,
    "tamil": "ஓய்வு (சைகை இல்லை)", "category": "IDLE", "is_emergency": False, "source": "builtin", "status": APPROVED,
}


def _person(user: Optional[User]) -> Optional[dict]:
    return {"id": user.id, "name": user.name, "email": user.email} if user is not None else None


def _word_info(word: Optional[Word]) -> dict:
    if word is None:
        return {**IDLE_WORD, "proposed_by": None, "reviewed_by": None, "reviewed_at": None, "review_note": None}
    return {
        **word_dict(word),
        "proposed_by": _person(word.proposed_by),
        "reviewed_by": word.reviewed_by.name if word.reviewed_by else None,
        "reviewed_at": word.reviewed_at,
        "review_note": word.review_note,
    }


@router.get("/words")
def review_queue(db: Session = Depends(get_db)):
    """Words with submitted recordings, and proposed words awaiting approval: recording counts
    per status, how many trainers sent them, and the latest submission. Proposed words
    come first, then the words with the most recordings waiting."""
    counts = defaultdict(lambda: dict.fromkeys(REVIEW_STATUSES, 0))
    trainers = defaultdict(set)
    latest = {}
    rows = db.execute(
        select(Sample.word_id, Sample.status, Sample.user_id, func.count(), func.max(Sample.submitted_at))
        .where(Sample.status != DRAFT).group_by(Sample.word_id, Sample.status, Sample.user_id)
    )
    for word_id, status, user_id, count, submitted_at in rows:
        counts[word_id][status] += count
        if user_id is not None:
            trainers[word_id].add(user_id)
        if submitted_at and (word_id not in latest or submitted_at > latest[word_id]):
            latest[word_id] = submitted_at

    word_ids = [word_id for word_id in counts if word_id is not None]
    words = db.scalars(select(Word).where(or_(Word.id.in_(word_ids), Word.status == PENDING))).all()
    entries = ([(None, _word_info(None))] if None in counts else []) + [(w.id, _word_info(w)) for w in words]
    queue = [
        {**info, "counts": counts[word_id], "trainers": len(trainers[word_id]), "last_submitted_at": latest.get(word_id)}
        for word_id, info in entries
    ]
    queue.sort(key=lambda w: (w["status"] != PENDING, -w["counts"][PENDING], w["english"].lower()))
    return queue


@router.get("/words/{concept}/samples")
def word_recordings(concept: str, db: Session = Depends(get_db)):
    """A word's submitted recordings and who recorded them. No frames: GET /samples/{id} replays one."""
    word = None
    if concept != config.NONE_LABEL:
        word = db.scalar(select(Word).where(Word.concept == concept))
        if word is None:
            raise ApiError(404, "unknown_word", "Unknown word")
    reviewer = aliased(User)
    query = (
        select(Sample, User, reviewer.name)
        .outerjoin(User, Sample.user_id == User.id)
        .outerjoin(reviewer, Sample.reviewed_by_id == reviewer.id)
        .where(Sample.status != DRAFT, Sample.word_id.is_(None) if word is None else Sample.word_id == word.id)
        .order_by(Sample.created_at)
    )
    return {
        "word": _word_info(word),
        "samples": [
            {
                "id": sample.id,
                "status": sample.status,
                "signer_id": sample.signer_id,
                "source": sample.source,
                "num_frames": sample.num_frames,
                "hand_frames": sample.hand_frames,
                "duration_ms": sample.duration_ms,
                "created_at": sample.created_at,
                "submitted_at": sample.submitted_at,
                "reviewed_at": sample.reviewed_at,
                "reviewed_by": reviewer_name,
                "review_note": sample.review_note,
                "trainer": _person(trainer),
            }
            for sample, trainer, reviewer_name in db.execute(query)
        ],
    }


@router.post("/samples")
def review_samples(req: ReviewSamplesRequest, background: BackgroundTasks, admin: User = Depends(require_admin),
                   db: Session = Depends(get_db)):
    """Saves a batch of decisions on submitted recordings; earlier decisions can be changed.
    Each affected trainer gets one email, and the admins one summary."""
    decisions = {**{i: APPROVED for i in req.approve}, **{i: REJECTED for i in req.reject}}
    rows = db.execute(
        select(Sample, Word).outerjoin(Word, Sample.word_id == Word.id)
        .where(Sample.id.in_(list(decisions)), Sample.status != DRAFT)
    ).all()
    if not rows:
        raise ApiError(404, "unknown_samples", "None of these recordings were submitted for review.")
    blocked = sorted({
        word.english for sample, word in rows
        if word is not None and word.status != APPROVED and decisions[sample.id] == APPROVED
    })
    if blocked:
        raise ApiError(400, "word_not_approved", f"Approve the word itself first: {', '.join(blocked)}.", words=blocked)

    now, note = utcnow(), (req.note or "").strip() or None
    changed = defaultdict(lambda: {APPROVED: Counter(), REJECTED: Counter()})  # user id -> status -> word label -> n
    updated = 0
    for sample, word in rows:
        status = decisions[sample.id]
        if sample.status == status:
            continue
        sample.status, sample.reviewed_by_id, sample.reviewed_at = status, admin.id, now
        sample.review_note = note if status == REJECTED else None
        updated += 1
        if sample.user_id is not None:
            changed[sample.user_id][status][notifications.word_label(word)] += 1
    db.commit()

    if changed:
        users = {u.id: u for u in db.scalars(select(User).where(User.id.in_(list(changed))))}
        summary = []
        for user_id, by_status in changed.items():
            trainer = notifications.person(users[user_id])
            background.add_task(notifications.samples_reviewed, trainer, admin.name,
                                sorted(by_status[APPROVED].items()), sorted(by_status[REJECTED].items()), note)
            summary.append((trainer, sum(by_status[APPROVED].values()), sum(by_status[REJECTED].values())))
        background.add_task(notifications.review_summary, admin.name, summary, note, notifications.admin_emails(db))
    return {"updated": updated}


@router.post("/words/{sign_id}")
def review_word(sign_id: str, req: ReviewWordRequest, background: BackgroundTasks,
                admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Approves a proposed word into the vocabulary, or rejects it together with its
    recordings that were still waiting for review."""
    word = db.scalar(select(Word).where(Word.sign_id == sign_id))
    if word is None:
        raise ApiError(404, "unknown_word", "Unknown sign_id")
    if word.source == "builtin":
        raise ApiError(400, "builtin_word", "Built-in words don't need review.")
    status = APPROVED if req.action == "approve" else REJECTED
    if word.status != status:
        now, note = utcnow(), (req.note or "").strip() or None
        word.status, word.reviewed_by_id, word.reviewed_at, word.review_note = status, admin.id, now, note
        if status == REJECTED:
            db.execute(
                update(Sample)
                .where(Sample.word_id == word.id, Sample.status.in_((DRAFT, PENDING)))
                .values(status=REJECTED, reviewed_by_id=admin.id, reviewed_at=now,
                        review_note=note or "The word was not approved.")
            )
        db.commit()
        vocabulary.reload()
        proposer = notifications.person(word.proposed_by) if word.proposed_by else None
        background.add_task(notifications.word_reviewed, proposer, admin.name, notifications.word_label(word), status,
                            note, notifications.admin_emails(db))
    return _word_info(word)
