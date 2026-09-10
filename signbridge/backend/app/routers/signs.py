from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.schemas import SignCreate
from app.services import sample_store
from app.services.recognition import engine
from app.services.vocabulary import vocabulary

router = APIRouter()


@router.get("/signs")
def list_signs(category: Optional[str] = None):
    stats = sample_store.stats()
    trained = set(engine.labels) if engine.model_loaded else set()
    return [
        {**row, "samples": stats.get(row["concept"], {}).get("count", 0), "trained": row["concept"] in trained}
        for row in vocabulary.list_all(category=category)
    ]


@router.get("/signs/categories")
def list_categories():
    return vocabulary.categories()


@router.post("/signs")
def create_sign(req: SignCreate):
    try:
        return vocabulary.add_custom(req.english, req.tamil, req.category, req.is_emergency)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/signs/{sign_id}")
def delete_sign(sign_id: str):
    """Deletes a custom word and its recorded samples."""
    try:
        row = vocabulary.delete_custom(sign_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown sign_id")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    sample_store.delete_concept(row["concept"])
    return {"ok": True, "deleted": row}
