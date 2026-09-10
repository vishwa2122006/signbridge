from collections import Counter
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.db import get_db
from app.errors import ApiError
from app.ml import features
from app.models.schemas import SampleCreate, SubmitRequest
from app.models.tables import APPROVED, DRAFT, PENDING, Sample, User, Word, utcnow
from app.routers.deps import require_user
from app.services import notifications, sample_store
from app.services.recognition import engine
from app.services.vocabulary import vocabulary

router = APIRouter()

# A word recording where hands were visible in fewer frames than this is rejected.
MIN_HAND_FRAME_RATIO = 0.3
# The Teach page records 1.5 to 6 seconds; a little slack for slow cameras.
MAX_RECORDING_MS = 7000


def _word_to_record(db: Session, concept: str, user: User) -> Optional[Word]:
    """Approved words, or the caller's own proposed word; None is the Idle class."""
    if concept == config.NONE_LABEL:
        return None
    word = db.scalar(select(Word).where(Word.concept == concept))
    if word is None or not (word.status == APPROVED or (word.status == PENDING and word.proposed_by_id == user.id)):
        raise ApiError(404, "unknown_word", f"'{concept}' is not in the vocabulary")
    return word


def _reject_another_words_sign(concept: str, frames: List[dict], aspect: float):
    """Validation: a recording the trained model confidently recognizes as a different word
    isn't saved, so two words never share one sign and Idle recordings stay sign-free.
    Only words the current model was trained on can be matched."""
    match = engine.best_match({"frames": frames, "aspect": aspect})
    if match is None:
        return
    label, confidence = match
    other = vocabulary.get_by_concept(label)
    if label in (concept, config.NONE_LABEL) or other is None or confidence < config.DUPLICATE_SIGN_CONFIDENCE:
        return
    raise ApiError(
        409, "sign_already_used",
        f"Not saved: this sign matches '{other['english']}' ({confidence:.0%}), which already has its own sign.",
        word=label, english=other["english"], tamil=other["tamil"], confidence=round(confidence, 3), recorded=concept,
    )


def _own_sample(db: Session, sample_id: int, user: User) -> Sample:
    sample = db.get(Sample, sample_id)
    if sample is None or not (user.is_admin or sample.user_id == user.id):
        raise ApiError(404, "unknown_sample", "Unknown sample id")
    return sample


@router.post("/samples")
def create_sample(req: SampleCreate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Saves one recording: a trainer's as a draft to submit for review, an admin's approved straight away."""
    word = _word_to_record(db, req.concept, user)
    frames = [f.model_dump() for f in req.frames]
    if features.clip_duration_ms(frames) > MAX_RECORDING_MS:
        raise ApiError(422, "too_long", f"Recordings can be at most {MAX_RECORDING_MS // 1000} seconds long.")
    if word is not None and sample_store.count_hand_frames(frames) < len(frames) * MIN_HAND_FRAME_RATIO:
        raise ApiError(422, "no_hands",
                       "Hands were not visible in most of this recording - keep your hands inside the camera view.")
    _reject_another_words_sign(req.concept, frames, req.aspect)
    sample = sample_store.save_sample(db, word, frames, req.aspect, status=APPROVED if user.is_admin else DRAFT,
                                      user=user, source=req.source)
    db.commit()
    return {"id": sample.id, "concept": req.concept, "status": sample.status, "num_frames": sample.num_frames}


@router.get("/samples/stats")
def sample_stats(user: User = Depends(require_user), db: Session = Depends(get_db)):
    return sample_store.user_stats(db, user)


@router.post("/samples/submit")
def submit_samples(req: SubmitRequest, background: BackgroundTasks, user: User = Depends(require_user),
                   db: Session = Depends(get_db)):
    """Sends the caller's draft recordings (all, or of one word) to the admins for review."""
    query = (
        select(Sample, Word).outerjoin(Word, Sample.word_id == Word.id)
        .where(Sample.user_id == user.id, Sample.status == DRAFT)
    )
    if req.concept == config.NONE_LABEL:
        query = query.where(Sample.word_id.is_(None))
    elif req.concept:
        query = query.where(Word.concept == req.concept)
    rows = db.execute(query).all()
    if not rows:
        raise ApiError(400, "nothing_to_submit", "There are no draft recordings to submit.")
    now, counts = utcnow(), Counter()
    for sample, word in rows:
        sample.status, sample.submitted_at = PENDING, now
        counts[notifications.word_label(word)] += 1
    db.commit()
    background.add_task(notifications.samples_submitted, notifications.person(user), sorted(counts.items()),
                        notifications.admin_emails(db))
    return {"submitted": len(rows)}


@router.get("/samples/{sample_id}")
def get_sample(sample_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """One recording with its frames, for replay: your own, or anyone's as an admin."""
    sample = _own_sample(db, sample_id, user)
    return {"id": sample.id, "status": sample.status, "aspect": sample.aspect, "frames": sample.frames}


@router.delete("/samples/{sample_id}")
def delete_sample(sample_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Trainers can delete their own recordings until they're reviewed; admins any recording."""
    sample = _own_sample(db, sample_id, user)
    if not user.is_admin and sample.status not in (DRAFT, PENDING):
        raise ApiError(403, "already_reviewed", "Reviewed recordings can't be deleted.")
    db.delete(sample)
    db.commit()
    return {"ok": True}
