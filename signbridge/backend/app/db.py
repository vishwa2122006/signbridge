"""PostgreSQL access through SQLAlchemy.

Routers get a session from the `get_db` dependency and commit explicitly.
Scripts and services use `session_scope()`, which commits on success.
`init_db()` creates missing tables and seeds the built-in vocabulary. It runs
when the API starts, so a new, empty database needs no separate setup step.
"""

from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine, text
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


# Columns added after the tables were first created (create_all only creates missing tables).
_UPGRADES = [
    "ALTER TABLE samples ADD COLUMN IF NOT EXISTS duration_ms INTEGER",
    "UPDATE samples SET duration_ms = GREATEST(0, ROUND((frames -> -1 ->> 't')::numeric - (frames -> 0 ->> 't')::numeric))::int "
    "WHERE duration_ms IS NULL AND jsonb_array_length(frames) > 0",
    "ALTER TABLE training_runs ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT false",
]


def init_db():
    from app.models import tables  # noqa: F401 - registers the tables on Base.metadata
    from app.services.vocabulary import seed_builtin_words, vocabulary

    Base.metadata.create_all(engine())
    with session_scope() as db:
        for statement in _UPGRADES:
            db.execute(text(statement))
    with session_scope() as db:
        seed_builtin_words(db)
    vocabulary.reload()
