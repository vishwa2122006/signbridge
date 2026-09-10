"""Who's calling. Public endpoints take `optional_user`; recording needs a
logged-in trainer or admin (`require_user` - both roles can record); reviewing
and training need an admin (`require_admin`)."""

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.models.tables import User
from app.services import security

_bearer = HTTPBearer(auto_error=False)


def optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
                  db: Session = Depends(get_db)) -> Optional[User]:
    """The logged-in user, or None for the public (an expired login counts as public)."""
    return security.user_for_token(db, credentials.credentials) if credentials else None


def require_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
                 db: Session = Depends(get_db)) -> User:
    user = security.user_for_token(db, credentials.credentials) if credentials else None
    if user is None:
        if credentials:
            raise ApiError(401, "session_expired", "Your login has expired - please log in again.")
        raise ApiError(401, "login_required", "Please log in as a trainer or admin.")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise ApiError(403, "admin_only", "Only an admin can do this.")
    return user
