import logging
import threading

from fastapi import APIRouter, HTTPException

from app.ml import trainer
from app.ml.classifier import SignClassifier
from app.services.recognition import engine

router = APIRouter()
log = logging.getLogger(__name__)
_training = threading.Lock()


@router.post("/train")
def train():
    """Trains on every recorded sample and hot-swaps the live model.
    Errors carry a `code` so the app can explain them in Tamil or English."""
    if not _training.acquire(blocking=False):
        raise HTTPException(status_code=409, detail={"code": "busy", "message": "Training is already running."})
    try:
        meta = trainer.train_and_save()
    except trainer.NotEnoughDataError as e:
        raise HTTPException(status_code=400, detail={
            "code": "not_enough_data",
            "message": str(e),
            "counts": e.counts,
            "min_samples": trainer.MIN_SAMPLES_PER_WORD,
        })
    except Exception as e:
        log.exception("Training failed")
        raise HTTPException(status_code=500, detail={"code": "training_failed", "message": f"Training failed: {e}"})
    finally:
        _training.release()
    classifier = SignClassifier.load()
    if classifier is not None:
        engine.load_classifier(classifier)
    return meta


@router.get("/model")
def model_info():
    return {"model_loaded": engine.model_loaded, **engine.model_metadata}
