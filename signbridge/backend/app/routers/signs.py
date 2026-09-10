from typing import Optional
from fastapi import APIRouter, HTTPException
from app.services.vocabulary import vocabulary

router = APIRouter()


@router.get("/signs")
def list_signs(category: Optional[str] = None, validation_status: Optional[str] = None):
    return vocabulary.list_all(category=category, validation_status=validation_status)


@router.get("/sign/{sign_id}")
def get_sign(sign_id: str):
    row = vocabulary.get(sign_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Unknown sign_id")
    return row


@router.get("/signs/demo-priority")
def demo_priority_signs():
    """The small guaranteed-to-work set for the hackathon demo (spec section
    25) - currently these are PRIORITY CANDIDATES only. None are promoted to
    validation_status=validated yet; that only happens once real recorded,
    sourced signs back them (see DATASET_SOURCES.md)."""
    return [r for r in vocabulary.list_all() if r["priority_demo_candidate"] == "yes"]
