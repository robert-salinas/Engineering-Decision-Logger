from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from .models import Decision, get_engine, init_db
from ..adr_formatter.formatter import ADRFormatter
import os
from pathlib import Path

class DecisionManager:
    """
    Manages the lifecycle of engineering decisions, including database storage
    and ADR file generation.
    """
    def __init__(self, db_path: str = "edl.db", adr_dir: str = "docs/ADR"):
        """
        Initializes the DecisionManager.

        Args:
            db_path (str): Path to the SQLite database.
            adr_dir (str): Directory where ADR Markdown files will be saved.
        """
        self.db_path = db_path
        self.adr_dir = Path(adr_dir)
        self.engine = get_engine(db_path)
        self.formatter = ADRFormatter()
        
        # Ensure ADR directory exists
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        # Initialize DB
        init_db(db_path)

    def add_decision(self, data: Dict[str, Any]) -> Decision:
        """
        Adds a new decision to the database and generates its ADR file.

        Args:
            data (Dict[str, Any]): Dictionary containing decision details.

        Returns:
            Decision: The created Decision object.
        """
        with Session(self.engine) as session:
            # Get next ID
            statement = select(Decision).order_by(Decision.id.desc())
            last_decision = session.exec(statement).first()
            next_id = (last_decision.id + 1) if last_decision else 1
            
            # Prepare data for model
            decision = Decision(
                id=next_id,
                title=data["title"],
                status=data.get("status", "Proposed"),
                context=data["context"],
                drivers=",".join(data.get("drivers", [])),
                options=",".join(data.get("options", [])),
                chosen_option=data["chosen_option"],
                rationale=data["rationale"],
                consequences_good=data.get("consequences_good", ""),
                consequences_bad=data.get("consequences_bad", ""),
                commit_hash=data.get("commit_hash")
            )
            session.add(decision)
            session.commit()
            session.refresh(decision)
            
            # Generate ADR file
            self._save_adr_file(decision, data)
            
            return decision

    def _save_adr_file(self, decision: Decision, original_data: Dict[str, Any]) -> None:
        """
        Generates and saves the ADR Markdown file for a decision.

        Args:
            decision (Decision): The decision object.
            original_data (Dict[str, Any]): The original input data.
        """
        # Prepare data for formatter (need lists instead of comma separated strings)
        render_data = original_data.copy()
        render_data["id"] = decision.id
        render_data["date"] = decision.date
        
        # Ensure pros_cons is handled if provided, otherwise empty list
        if "pros_cons" not in render_data:
            render_data["pros_cons"] = []

        content = self.formatter.render(render_data)
        filename = self.formatter.get_filename(decision.id, decision.title)
        filepath = self.adr_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def list_decisions(self) -> List[Decision]:
        """
        Retrieves all decisions from the database.

        Returns:
            List[Decision]: A list of all Decision objects.
        """
        with Session(self.engine) as session:
            return session.exec(select(Decision)).all()

    def get_decision(self, decision_id: int) -> Optional[Decision]:
        """
        Retrieves a specific decision by its ID.

        Args:
            decision_id (int): The unique ID of the decision.

        Returns:
            Optional[Decision]: The Decision object if found, else None.
        """
        with Session(self.engine) as session:
            return session.get(Decision, decision_id)

    def search_decisions(self, query: str) -> List[Decision]:
        """
        Searches for decisions matching a query string.

        Args:
            query (str): The search query.

        Returns:
            List[Decision]: A list of matching Decision objects.
        """
        with Session(self.engine) as session:
            statement = select(Decision).where(
                (Decision.title.contains(query)) | 
                (Decision.context.contains(query)) |
                (Decision.rationale.contains(query)) |
                (Decision.chosen_option.contains(query))
            )
            return session.exec(statement).all()
