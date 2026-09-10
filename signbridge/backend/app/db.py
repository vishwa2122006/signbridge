"""PostgreSQL access through SQLAlchemy.

Routers get a session from the `get_db` dependency and commit explicitly.
Scripts and services use `session_scope()`, which commits on success.
`init_db()` creates missing tables and seeds the built-in vocabulary. It runs
when the API starts, so a new, empty database needs no separate setup step.
"""

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app import config


class Base(DeclarativeBase):
    pass


_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(config.database_url(), pool_pre_ping=True)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def new_session() -> Session:
    engine()
    return _session_factory()


def get_db() -> Iterator[Session]:
    db = new_session()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope(db: Optional[Session] = None) -> Iterator[Session]:
    """A new session committed on success, or `db` itself when given (its owner commits)."""
    if db is not None:
        yield db
        return
    session = new_session()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    from app.models import tables  # noqa: F401 - registers the tables on Base.metadata
    from app.services.vocabulary import seed_builtin_words, vocabulary

    Base.metadata.create_all(engine())
    with session_scope() as db:
        seed_builtin_words(db)
    vocabulary.reload()
