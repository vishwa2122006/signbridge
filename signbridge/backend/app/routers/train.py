import logging
import threading

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.ml import trainer
from app.models.tables import TrainingRun, User
from app.routers.deps import require_admin
from app.services import model_store
from app.services.recognition import engine

router = APIRouter()
log = logging.getLogger(__name__)
_training = threading.Lock()


@router.post("/train")
def train(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Trains on every approved recording, keeps it as a new model version and hot-swaps the
    live model. Admins only. Errors carry a `code` so the app can explain them in Tamil or English."""
    if not _training.acquire(blocking=False):
        raise ApiError(409, "busy", "Training is already running.")
    try:
        run = model_store.train(db, admin)
    except trainer.NotEnoughDataError as e:
        raise ApiError(400, "not_enough_data", str(e), counts=e.counts, min_samples=trainer.MIN_SAMPLES_PER_WORD)
    except Exception as e:
        log.exception("Training failed")
        raise ApiError(500, "training_failed", f"Training failed: {e}")
    finally:
        _training.release()
    return {**run.meta, "model_id": run.id}


@router.get("/model")
def model_info():
    return {"model_loaded": engine.model_loaded, **engine.model_metadata}


def _find_model(db: Session, model_id: int) -> TrainingRun:
    run = db.get(TrainingRun, model_id)
    if run is None or not run.succeeded:
        raise ApiError(404, "unknown_model", "Unknown model")
    return run


@router.get("/models")
def list_models(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Every trained model version, newest first; `is_active` marks the one the translator uses."""
    return model_store.list_models(db)


@router.post("/models/{model_id}/activate")
def activate_model(model_id: int, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Makes this version the one the translator uses."""
    run = _find_model(db, model_id)
    if not model_store.describe(run)["available"]:
        raise ApiError(409, "model_missing", "This model's files are missing, so it can't be used.")
    model_store.activate(db, run)
    return {"model_loaded": engine.model_loaded, **engine.model_metadata}


@router.delete("/models/{model_id}")
def delete_model(model_id: int, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Deletes a model version. Deleting the one in use leaves the translator without a model
    until another version is used or the model is trained again."""
    was_active = model_store.delete(db, _find_model(db, model_id))
    return {"ok": True, "was_active": was_active, "model_loaded": engine.model_loaded}
