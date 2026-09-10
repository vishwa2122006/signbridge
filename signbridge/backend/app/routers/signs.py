from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.models.schemas import SignCreate, SignUpdate
from app.models.tables import APPROVED, PENDING, User, Word, utcnow
from app.routers.deps import optional_user, require_admin, require_user
from app.services import notifications, sample_store, sign_demos
from app.services.recognition import engine
from app.services.vocabulary import CUSTOM_CATEGORY, add_word, slugify, vocabulary, word_dict

router = APIRouter()


def _find_word(db: Session, sign_id: str) -> Word:
    word = db.scalar(select(Word).where(Word.sign_id == sign_id))
    if word is None:
        raise ApiError(404, "unknown_word", "Unknown sign_id")
    return word


@router.get("/signs/{concept}/demo")
def sign_demo(concept: str):
    """The most typical approved recording of a word, replayed to the signer as a hand sign."""
    row = vocabulary.get_by_concept(concept)
    if row is None:
        raise ApiError(404, "unknown_word", "Unknown word")
    sample = sign_demos.representative_sample(concept)
    if sample is None:
        raise ApiError(404, "no_recording", f"No recording of '{row['english']}' yet.")
    return {
        "concept": concept,
        "english": row["english"],
        "tamil": row["tamil"],
        "signer_id": sample.get("signer_id"),
        "aspect": sample.get("aspect"),
        "frames": sample["frames"],
    }


@router.get("/signs")
def list_signs(category: Optional[str] = None, user: Optional[User] = Depends(optional_user),
               db: Session = Depends(get_db)):
    """Approved words, with how many approved recordings each has and whether the model
    knows it. A logged-in trainer also gets the words they proposed that await review."""
    rows = vocabulary.list_all(category=category)
    if user is not None:
        query = select(Word).where(Word.status == PENDING, Word.proposed_by_id == user.id)
        if category:
            query = query.where(Word.category == category)
        rows += [word_dict(w) for w in db.scalars(query.order_by(Word.id))]
    stats = sample_store.approved_stats(db)
    trained = set(engine.labels) if engine.model_loaded else set()
    return [
        {**row, "samples": stats.get(row["concept"], {}).get("count", 0), "trained": row["concept"] in trained}
        for row in rows
    ]


@router.get("/signs/categories")
def list_categories():
    return vocabulary.categories()


@router.post("/signs")
def create_sign(req: SignCreate, background: BackgroundTasks, user: User = Depends(require_user),
                db: Session = Depends(get_db)):
    """An admin's new word is added straight away; a trainer's waits for an admin's approval."""
    word = add_word(db, req.english, req.tamil, req.category, req.is_emergency,
                    status=APPROVED if user.is_admin else PENDING, proposed_by=user)
    if user.is_admin:
        word.reviewed_by_id, word.reviewed_at = user.id, utcnow()
    db.commit()
    vocabulary.reload()
    if not user.is_admin:
        background.add_task(notifications.word_proposed, notifications.person(user), notifications.word_label(word),
                            notifications.admin_emails(db))
    return word_dict(word)


@router.patch("/signs/{sign_id}")
def update_sign(sign_id: str, req: SignUpdate, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Corrects a word's text or category. The concept (the word's id in recordings and the model) stays the same."""
    word = _find_word(db, sign_id)
    for field, value in req.model_dump(exclude_unset=True).items():
        if field == "category":
            value = slugify(value).upper() or CUSTOM_CATEGORY
        elif isinstance(value, str):
            value = value.strip()
        setattr(word, field, value)
    db.commit()
    vocabulary.reload()
    return word_dict(word)


@router.delete("/signs/{sign_id}")
def delete_sign(sign_id: str, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Deletes a word and all its recordings: an admin any word that isn't built in,
    a trainer only a word they proposed that hasn't been approved."""
    word = _find_word(db, sign_id)
    if word.source == "builtin":
        raise ApiError(400, "builtin_word", "Built-in words can't be deleted.")
    if not user.is_admin and not (word.proposed_by_id == user.id and word.status != APPROVED):
        raise ApiError(403, "not_allowed", "You can only delete words you proposed that haven't been approved.")
    row = word_dict(word)
    db.delete(word)  # recordings go with it (ON DELETE CASCADE)
    db.commit()
    vocabulary.reload()
    return {"ok": True, "deleted": row}
