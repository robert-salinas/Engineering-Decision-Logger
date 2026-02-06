from sqlalchemy import Engine
from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
import os


class Decision(SQLModel, table=True):
    """
    Represents an Engineering Decision Record (ADR) in the database.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = "Accepted"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    context: str
    drivers: str  # Comma separated or JSON string
    options: str  # Comma separated or JSON string
    chosen_option: str
    rationale: str
    consequences_good: str
    consequences_bad: str
    commit_hash: Optional[str] = None


def get_engine(db_path: str = "edl.db") -> Engine:
    """
    Creates and returns a SQLModel engine for the database.

    Args:
        db_path (str): The file path to the SQLite database. Defaults to "edl.db".

    Returns:
        Engine: The SQLModel/SQLAlchemy engine.
    """
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url)


def init_db(db_path: str = "edl.db") -> None:
    """
    Initializes the database by creating all necessary tables.

    Args:
        db_path (str): The file path to the SQLite database. Defaults to "edl.db".
    """
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
