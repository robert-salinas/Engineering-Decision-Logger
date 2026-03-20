from sqlalchemy import Engine
from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
from pathlib import Path
import os

# PU-9: Resolve DB path relative to project root, not CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = str(PROJECT_ROOT / "edl.db")
DEFAULT_ADR_DIR = str(PROJECT_ROOT / "docs" / "ADR")


class Decision(SQLModel, table=True):
    """
    Represents an Engineering Decision Record (ADR) in the database.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = "Proposed"  # Proposed, Accepted, Deprecated, Superseded
    impact: str = "Medium"  # Low, Medium, Critical
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    context: str
    drivers: str = ""  # Comma separated or JSON string
    options: str = ""  # Comma separated or JSON string
    chosen_option: str
    rationale: str
    consequences_good: str = ""
    consequences_bad: str = ""
    commit_hash: Optional[str] = None
    depends_on: str = ""  # Comma-separated IDs (e.g., "1,2")


def get_engine(db_path: str = DEFAULT_DB_PATH) -> Engine:
    """
    Creates and returns a SQLModel engine for the database.

    Args:
        db_path (str): The file path to the SQLite database.

    Returns:
        Engine: The SQLModel/SQLAlchemy engine.
    """
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url)


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes the database by creating all necessary tables.

    Args:
        db_path (str): The file path to the SQLite database.
    """
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    
    # Ensure column existence for existing DBs without migration tooling
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE decision ADD COLUMN depends_on VARCHAR DEFAULT ''"))
            conn.commit()
        except Exception:
            pass
