from fastapi import APIRouter
from app.models.schemas import TemplateRequest
from app.services.templates import match_template

router = APIRouter()


@router.post("/translate-template")
def translate_template(req: TemplateRequest):
    result = match_template(req.concept_slugs)
    if result is None:
        return {"matched": False, "template": None}
    return {"matched": True, "template": result}
