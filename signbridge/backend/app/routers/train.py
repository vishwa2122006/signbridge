import logging
import threading

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.ml import trainer
from app.ml.classifier import SignClassifier
from app.models.tables import TrainingRun, User
from app.routers.deps import require_admin
from app.services import sample_store
from app.services.recognition import engine

router = APIRouter()
log = logging.getLogger(__name__)
_training = threading.Lock()


@router.post("/train")
def train(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Trains on every approved recording and hot-swaps the live model. Admins only.
    Errors carry a `code` so the app can explain them in Tamil or English."""
    if not _training.acquire(blocking=False):
        raise ApiError(409, "busy", "Training is already running.")
    try:
        meta = trainer.train_and_save(sample_store.training_samples(db))
    except trainer.NotEnoughDataError as e:
        raise ApiError(400, "not_enough_data", str(e), counts=e.counts, min_samples=trainer.MIN_SAMPLES_PER_WORD)
    except Exception as e:
        log.exception("Training failed")
        db.rollback()
        db.add(TrainingRun(user_id=admin.id, succeeded=False, error=str(e)))
        db.commit()
        raise ApiError(500, "training_failed", f"Training failed: {e}")
    finally:
        _training.release()
    db.add(TrainingRun(user_id=admin.id, succeeded=True, meta=meta))
    db.commit()
    classifier = SignClassifier.load()
    if classifier is not None:
        engine.load_classifier(classifier)
    return meta


@router.get("/model")
def model_info():
    return {"model_loaded": engine.model_loaded, **engine.model_metadata}
