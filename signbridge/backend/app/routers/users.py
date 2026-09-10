"""Admin: registered trainers and admins with their details and recording counts."""

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.models.schemas import UserOut, UserUpdate
from app.models.tables import Sample, User
from app.routers.deps import require_admin
from app.services import sample_store

router = APIRouter(prefix="/admin/users", dependencies=[Depends(require_admin)])


@router.get("")
def list_users(db: Session = Depends(get_db)):
    counts = defaultdict(lambda: dict.fromkeys(sample_store.STATUSES, 0))
    rows = db.execute(
        select(Sample.user_id, Sample.status, func.count())
        .where(Sample.user_id.is_not(None)).group_by(Sample.user_id, Sample.status)
    )
    for user_id, status, count in rows:
        counts[user_id][status] = count
    users = db.scalars(select(User).order_by(User.role, User.created_at)).all()
    return [{**UserOut.model_validate(u).model_dump(), "recordings": counts[u.id]} for u in users]


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, req: UserUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Enables or disables an account. A disabled account can't log in, and its current logins stop working."""
    user = db.get(User, user_id)
    if user is None:
        raise ApiError(404, "unknown_user", "Unknown user")
    if user.id == admin.id:
        raise ApiError(400, "cannot_disable_self", "You can't disable your own account.")
    user.is_active = req.is_active
    db.commit()
    return user
