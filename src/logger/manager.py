from sqlmodel import Session, select
from .models import Decision, get_engine, init_db
from ..adr_formatter.formatter import ADRFormatter
import os
from pathlib import Path

class DecisionManager:
    def __init__(self, db_path: str = "edl.db", adr_dir: str = "docs/ADR"):
        self.db_path = db_path
        self.adr_dir = Path(adr_dir)
        self.engine = get_engine(db_path)
        self.formatter = ADRFormatter()
        
        # Ensure ADR directory exists
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        # Initialize DB
        init_db(db_path)

    def add_decision(self, data: dict) -> Decision:
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

    def _save_adr_file(self, decision: Decision, original_data: dict):
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

    def list_decisions(self) -> list[Decision]:
        with Session(self.engine) as session:
            return session.exec(select(Decision)).all()

    def get_decision(self, decision_id: int) -> Decision:
        with Session(self.engine) as session:
            return session.get(Decision, decision_id)

    def search_decisions(self, query: str) -> list[Decision]:
        with Session(self.engine) as session:
            statement = select(Decision).where(
                (Decision.title.contains(query)) | 
                (Decision.context.contains(query)) |
                (Decision.rationale.contains(query)) |
                (Decision.chosen_option.contains(query))
            )
            return session.exec(statement).all()
