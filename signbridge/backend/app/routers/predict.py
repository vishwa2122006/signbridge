from fastapi import APIRouter
from app.models.schemas import PredictRequest, SimulatePredictRequest, PredictResponse
from app.services.recognition import engine
from app.services.vocabulary import vocabulary

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """Real recognition endpoint. Landmarks are extracted client-side (see
    frontend CameraFeed component) so raw video never has to leave the
    browser - only numeric landmark coordinates are sent here."""
    hand_detected = any(f.hand_detected for f in req.window)
    # Flatten the window into whatever shape the loaded model expects.
    window_features = [f.features for f in req.window]
    result = engine.predict(req.session_id, hand_detected, window_features)
    return PredictResponse(**result)


@router.post("/predict/simulate", response_model=PredictResponse)
def predict_simulate(req: SimulatePredictRequest):
    """DEMO-ONLY. Lets you walk a judge through the full downstream UX
    (bilingual output, confidence display, emergency banner, conversation
    log) using a manually chosen concept, without a live model. Always
    returns simulated=True so the UI can badge it clearly and it can never
    be mistaken for a real camera-based recognition."""
    row = vocabulary.get(req.sign_id)
    if row is None:
        return PredictResponse(
            status="UNKNOWN_SIGN",
            session_id=req.session_id,
            simulated=True,
            message_en="Unknown sign_id.",
            message_ta="தெரியாத அடையாள குறியீடு.",
        )
    return PredictResponse(
        status="RECOGNIZED",
        session_id=req.session_id,
        simulated=True,
        accepted_sign_id=row["sign_id"],
        accepted_concept=row["concept"],
        english=row["english"],
        tamil=row["tamil"],
        confidence=1.0,
        top_candidates=[],
        message_en=f"(Simulated) Detected: {row['english']}",
        message_ta=f"(உருவகப்படுத்தப்பட்டது) கண்டறியப்பட்டது: {row['tamil']}",
        is_emergency=vocabulary.is_emergency(row["concept"]),
    )


@router.post("/predict/reset/{session_id}")
def reset_session(session_id: str):
    engine.reset_session(session_id)
    return {"ok": True}
