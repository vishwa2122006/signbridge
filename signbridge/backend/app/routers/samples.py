from fastapi import APIRouter, HTTPException

from app import config
from app.models.schemas import SampleCreate
from app.services import sample_store
from app.services.vocabulary import vocabulary

router = APIRouter()

# A word recording where hands were visible in fewer frames than this is rejected.
MIN_HAND_FRAME_RATIO = 0.3


@router.post("/samples")
def create_sample(req: SampleCreate):
    if req.concept != config.NONE_LABEL and vocabulary.get_by_concept(req.concept) is None:
        raise HTTPException(status_code=404, detail=f"'{req.concept}' is not in the vocabulary")
    frames = [f.model_dump() for f in req.frames]
    hand_frames = sum(1 for f in frames if f["left"] is not None or f["right"] is not None)
    if req.concept != config.NONE_LABEL and hand_frames < len(frames) * MIN_HAND_FRAME_RATIO:
        raise HTTPException(status_code=422, detail={
            "code": "no_hands",
            "message": "Hands were not visible in most of this recording - keep your hands inside the camera view.",
        })
    return sample_store.save_sample(req.concept, req.signer_id, frames, req.aspect, req.source)


@router.get("/samples/stats")
def sample_stats():
    return sample_store.stats()


@router.delete("/samples/{sample_id}")
def delete_sample(sample_id: str):
    if not sample_store.delete_sample(sample_id):
        raise HTTPException(status_code=404, detail="Unknown sample id")
    return {"ok": True}
