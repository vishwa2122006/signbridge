from fastapi import APIRouter

from app.models.schemas import TextToSignsRequest, TranslateRequest
from app.services.templates import build_sentence
from app.services.text_to_signs import text_to_signs

router = APIRouter()


@router.post("/translate")
def translate(req: TranslateRequest):
    """Signed words (in signing order) -> English + Tamil text via offline rule templates."""
    return build_sentence(req.words)


@router.post("/text-to-signs")
def message_to_signs(req: TextToSignsRequest):
    """A hearing person's message -> vocabulary words in order, marking which ones
    have recordings that can be replayed to the signer as hand signs."""
    return {"items": text_to_signs(req.text)}
