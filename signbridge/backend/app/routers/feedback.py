from fastapi import APIRouter
from app.models.schemas import FeedbackRequest, DatasetSampleRegisterRequest
from app.services import feedback_store

router = APIRouter()


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    entry = feedback_store.record_feedback(
        validator_id=req.validator_id,
        sign_id=req.sign_id,
        prediction=req.prediction,
        decision=req.decision,
        comment=req.comment,
    )
    return {"ok": True, "entry": entry}


@router.get("/feedback/{sign_id}")
def get_feedback(sign_id: str):
    return feedback_store.list_feedback(sign_id=sign_id)


@router.post("/dataset/sample")
def register_dataset_sample(req: DatasetSampleRegisterRequest):
    """Registers METADATA for a collected sample (Dataset Collection Mode).
    This MVP does not accept raw video upload here - the frontend's Dataset
    Mode saves the video locally / to local storage and calls this endpoint
    to log what was collected and confirm consent was captured."""
    entry = feedback_store.record_dataset_sample(
        sign_id=req.sign_id,
        signer_id=req.signer_id,
        source=req.source,
        frame_count=req.frame_count,
        fps=req.fps,
        consent_confirmed=req.consent_confirmed,
    )
    return {"ok": True, "entry": entry}
