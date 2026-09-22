"""Database engine and session management."""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from halal_screener.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Initialize database tables (used for local SQLite dev/tests; production

    schema is managed via the raw SQL files in backend/migrations/).
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    with Session(engine) as session:
        yield session
