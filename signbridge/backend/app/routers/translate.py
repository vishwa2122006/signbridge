from fastapi import APIRouter

from app.models.schemas import TranslateRequest
from app.services.templates import build_sentence

router = APIRouter()


@router.post("/translate")
def translate(req: TranslateRequest):
    """Signed words (in signing order) -> English + Tamil text via offline rule templates."""
    return build_sentence(req.words)
