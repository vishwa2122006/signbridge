"""
model_store.py — trained model versions.

Every successful training is kept as its own version in DATA_DIR/models/<run id>/
(model.joblib + model_meta.json) and recorded in the training_runs table. One
version is active: the one the translator uses. Admins can switch to another
version or delete versions; deleting the active one leaves the translator
without a model until another version is used or the model is trained again.
"""

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app import config
from app import db as database
from app.ml import trainer
from app.ml.classifier import META_FILE, MODEL_FILE, SignClassifier
from app.models.tables import TrainingRun, User
from app.services import sample_store
from app.services.recognition import engine

log = logging.getLogger(__name__)


def run_dir(run_id: int) -> str:
    return os.path.join(config.model_dir(), str(run_id))


def _size_bytes(run_id: int) -> Optional[int]:
    path = os.path.join(run_dir(run_id), MODEL_FILE)
    return os.path.getsize(path) if os.path.exists(path) else None


def train(db: Session, user: Optional[User]) -> TrainingRun:
    """Trains on every approved recording, keeps the result as a new version and makes it active.
    Raises trainer.NotEnoughDataError; any other failure is recorded as a failed run and re-raised."""
    os.makedirs(config.model_dir(), exist_ok=True)
    staging = tempfile.mkdtemp(prefix=".training-", dir=config.model_dir())
    try:
        meta = trainer.train_and_save(sample_store.training_samples(db), staging)
    except trainer.NotEnoughDataError:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(staging, ignore_errors=True)
        db.rollback()
        db.add(TrainingRun(user_id=user.id if user else None, succeeded=False, error=str(e)))
        db.commit()
        raise
    run = TrainingRun(user_id=user.id if user else None, succeeded=True, meta=meta)
    db.add(run)
    db.flush()
    shutil.rmtree(run_dir(run.id), ignore_errors=True)  # a stale folder from an old database
    os.replace(staging, run_dir(run.id))
    activate(db, run)
    return run


def activate(db: Session, run: TrainingRun):
    db.execute(update(TrainingRun).values(is_active=False))
    run.is_active = True
    db.commit()
    load_active(db)


def delete(db: Session, run: TrainingRun) -> bool:
    """Deletes a version's record and files. Returns whether it was the one in use."""
    was_active, run_id = run.is_active, run.id
    db.delete(run)
    db.commit()
    shutil.rmtree(run_dir(run_id), ignore_errors=True)
    if was_active:
        engine.unload()
    return was_active


def load_active(db: Optional[Session] = None) -> Optional[TrainingRun]:
    """Loads the active version into the recognition engine, or unloads it when there is none."""
    with database.session_scope(db) as s:
        run = s.scalar(select(TrainingRun).where(TrainingRun.is_active.is_(True)))
        classifier = SignClassifier.load(run_dir(run.id)) if run is not None else None
        if run is not None and classifier is None:
            log.warning("The active model (version %s) has no usable files in %s.", run.id, run_dir(run.id))
        if classifier is None:
            engine.unload()
        else:
            engine.load_classifier(classifier, model_id=run.id)
        return run


def describe(run: TrainingRun, trained_by: Optional[str] = None) -> dict:
    meta = run.meta or {}
    size = _size_bytes(run.id)
    return {
        "id": run.id,
        "created_at": run.created_at,
        "trained_by": trained_by,
        "is_active": run.is_active,
        "available": size is not None,
        "size_bytes": size,
        "model_type": meta.get("model_type"),
        "cv_accuracy": meta.get("cv_accuracy"),
        "cv_method": meta.get("cv_method"),
        "words": meta.get("words", []),
        "has_idle_class": meta.get("has_idle_class"),
        "num_samples": meta.get("num_samples"),
        "num_signers": meta.get("num_signers"),
        "max_window_ms": meta.get("max_window_ms"),
    }


def list_models(db: Session) -> List[dict]:
    """Successful trainings, newest first."""
    rows = db.execute(
        select(TrainingRun, User.name).outerjoin(User, TrainingRun.user_id == User.id)
        .where(TrainingRun.succeeded.is_(True)).order_by(TrainingRun.created_at.desc())
    ).all()
    return [describe(run, name) for run, name in rows]


def adopt_legacy_model(db: Session):
    """A model saved directly in DATA_DIR/models/ (before versions existed) becomes a version,
    and the active one unless another version already is."""
    legacy = os.path.join(config.model_dir(), MODEL_FILE)
    if not os.path.exists(legacy):
        return
    meta_path = os.path.join(config.model_dir(), META_FILE)
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    has_active = db.scalar(select(TrainingRun.id).where(TrainingRun.is_active.is_(True))) is not None
    run = TrainingRun(succeeded=True, meta=meta, is_active=not has_active,
                      created_at=datetime.fromtimestamp(os.path.getmtime(legacy), timezone.utc))
    db.add(run)
    db.flush()
    os.makedirs(run_dir(run.id), exist_ok=True)
    os.replace(legacy, os.path.join(run_dir(run.id), MODEL_FILE))
    if os.path.exists(meta_path):
        os.replace(meta_path, os.path.join(run_dir(run.id), META_FILE))
    db.commit()
    log.warning("Kept the existing trained model as model version %s.", run.id)


def start():
    """On startup: adopt a pre-versions model, then load the active version."""
    with database.session_scope() as db:
        adopt_legacy_model(db)
        load_active(db)
