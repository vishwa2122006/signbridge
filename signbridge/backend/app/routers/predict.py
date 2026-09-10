from fastapi import APIRouter

from app.ml.features import has_hands
from app.models.schemas import PredictRequest, PredictResponse
from app.services.recognition import engine

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """Live recognition. Landmarks are extracted in the browser, so only
    numeric coordinates reach the server - never video."""
    frames = [f.model_dump() for f in req.window]
    result = engine.predict(req.session_id, has_hands(frames), {"frames": frames, "aspect": req.aspect})
    return PredictResponse(**result)


@router.post("/predict/reset/{session_id}")
def reset_session(session_id: str):
    engine.reset_session(session_id)
    return {"ok": True}
