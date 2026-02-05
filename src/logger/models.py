from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
import os

class Decision(SQLModel, table=True):
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

def get_engine(db_path: str = "edl.db"):
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url)

def init_db(db_path: str = "edl.db"):
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
