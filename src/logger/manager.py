from typing import List, Dict, Any, Optional
from sqlmodel import Session, select, col
from .models import Decision, get_engine, init_db, DEFAULT_DB_PATH, DEFAULT_ADR_DIR
from ..adr_formatter.formatter import ADRFormatter
import os
from pathlib import Path


class DecisionManager:
    """
    Manages the lifecycle of engineering decisions, including database storage
    and ADR file generation.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH, adr_dir: str = DEFAULT_ADR_DIR):
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
                impact=data.get("impact", "Medium"),
                context=data["context"],
                drivers=",".join(data.get("drivers", [])) if isinstance(data.get("drivers"), list) else data.get("drivers", ""),
                options=",".join(data.get("options", [])) if isinstance(data.get("options"), list) else data.get("options", ""),
                chosen_option=data["chosen_option"],
                rationale=data["rationale"],
                consequences_good=data.get("consequences_good", ""),
                consequences_bad=data.get("consequences_bad", ""),
                commit_hash=data.get("commit_hash"),
                depends_on=data.get("depends_on", ""),
            )
            session.add(decision)
            session.commit()
            session.refresh(decision)

            # Generate ADR file
            self._save_adr_file(decision, data)

            return decision

    def update_decision(self, decision_id: int, data: Dict[str, Any]) -> Optional[Decision]:
        """
        Updates an existing decision in the database and regenerates its ADR file.

        Args:
            decision_id (int): The ID of the decision to update.
            data (Dict[str, Any]): Dictionary containing updated decision details.

        Returns:
            Optional[Decision]: The updated Decision object, or None if not found.
        """
        with Session(self.engine) as session:
            decision = session.get(Decision, decision_id)
            if not decision:
                return None

            # Update fields
            for field in ["title", "status", "impact", "context", "chosen_option", "rationale",
                          "consequences_good", "consequences_bad", "commit_hash", "depends_on"]:
                if field in data:
                    setattr(decision, field, data[field])

            if "drivers" in data:
                decision.drivers = ",".join(data["drivers"]) if isinstance(data["drivers"], list) else data["drivers"]
            if "options" in data:
                decision.options = ",".join(data["options"]) if isinstance(data["options"], list) else data["options"]

            session.add(decision)
            session.commit()
            session.refresh(decision)

            # Regenerate ADR file
            self._save_adr_file(decision, data)

            return decision

    def delete_decision(self, decision_id: int) -> bool:
        """
        Deletes a decision from the database.

        Args:
            decision_id (int): The ID of the decision to delete.

        Returns:
            bool: True if the decision was deleted, False if not found.
        """
        with Session(self.engine) as session:
            decision = session.get(Decision, decision_id)
            if not decision:
                return False

            # Remove ADR file if it exists
            filename = self.formatter.get_filename(decision.id, decision.title)
            filepath = self.adr_dir / filename
            if filepath.exists():
                filepath.unlink()

            session.delete(decision)
            session.commit()
            return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about decisions for the dashboard.

        Returns:
            Dict[str, Any]: Dictionary with total count and counts by impact level.
        """
        with Session(self.engine) as session:
            all_decisions = session.exec(select(Decision)).all()
            total = len(all_decisions)
            by_impact = {"Low": 0, "Medium": 0, "Critical": 0}
            by_status = {"Proposed": 0, "Accepted": 0, "Deprecated": 0, "Superseded": 0}

            for d in all_decisions:
                if d.impact in by_impact:
                    by_impact[d.impact] += 1
                if d.status in by_status:
                    by_status[d.status] += 1

            return {
                "total": total,
                "by_impact": by_impact,
                "by_status": by_status,
            }

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

        # Ensure list fields are lists for Jinja2 iteration
        if "drivers" not in render_data or not isinstance(render_data.get("drivers"), list):
            raw = render_data.get("drivers", decision.drivers or "")
            render_data["drivers"] = [d.strip() for d in raw.split(",") if d.strip()] if raw else []

        if "options" not in render_data or not isinstance(render_data.get("options"), list):
            raw = render_data.get("options", decision.options or "")
            render_data["options"] = [o.strip() for o in raw.split(",") if o.strip()] if raw else []

        # Ensure all required template fields exist
        render_data.setdefault("status", decision.status)
        render_data.setdefault("context", decision.context)
        render_data.setdefault("chosen_option", decision.chosen_option)
        render_data.setdefault("rationale", decision.rationale)
        render_data.setdefault("consequences_good", decision.consequences_good or "")
        render_data.setdefault("consequences_bad", decision.consequences_bad or "")
        render_data.setdefault("pros_cons", [])

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
                (Decision.title.contains(query))
                | (Decision.context.contains(query))
                | (Decision.rationale.contains(query))
                | (Decision.chosen_option.contains(query))
            )
            return session.exec(statement).all()

    def get_dependency_relations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves nodes and edges for building a dependency graph.
        
        Returns:
             Dict with 'nodes' and 'edges'.
        """
        with Session(self.engine) as session:
            decisions = session.exec(select(Decision)).all()
            
            nodes = []
            edges = []
            
            for d in decisions:
                nodes.append({"id": d.id, "title": f"ADR-{d.id:03d}\n{d.title[:15]}..."})
                if d.depends_on:
                    for dep_str in d.depends_on.split(","):
                        dep_str = dep_str.strip()
                        if dep_str.isdigit():
                            edges.append({"from": d.id, "to": int(dep_str)})
                            
            return {"nodes": nodes, "edges": edges}

    def generate_mkdocs_config(self) -> str:
        """
        Generates an mkdocs.yml and an index.md for static site generation.
        """
        import yaml
        from src.logger.models import DEFAULT_ADR_DIR, PROJECT_ROOT
        
        with Session(self.engine) as session:
            decisions = session.exec(select(Decision)).all()
            decisions.sort(key=lambda x: x.id)
            
        config = {
            "site_name": "RS Engineering Decision Logger Docs",
            "theme": {
                "name": "material",
                "palette": {
                    "scheme": "slate",
                    "primary": "deep orange",
                    "accent": "deep orange"
                },
                "features": ["navigation.tabs", "navigation.sections"]
            },
            "nav": [
                {"Home": "index.md"},
                {"Decisiones (ADRs)": []}
            ]
        }
        
        from src.adr_formatter.formatter import ADRFormatter
        formatter = ADRFormatter()
        
        for d in decisions:
             filename = ADRFormatter.get_filename(d.id, d.title)
             config["nav"][1]["Decisiones (ADRs)"].append({f"ADR-{d.id:03d}: {d.title}": f"ADR/{filename}"})
             
        yml_path = os.path.join(str(PROJECT_ROOT), "mkdocs.yml")
        with open(yml_path, "w", encoding="utf-8") as f:
             yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
             
        index_path = os.path.join(DEFAULT_ADR_DIR, "..", "index.md")
        index_content = """# 🏛️ Registro de Decisiones de Arquitectura (ADR)

Bienvenido a la documentación estática de decisiones técnicas de este proyecto.

## 📊 Resumen de Decisiones

| ID | Título | Impacto | Estado | Fecha |
|:---|:---|:---|:---|:---|
"""
        for d in decisions:
             index_content += f"| {d.id} | [{d.title}](ADR/{ADRFormatter.get_filename(d.id, d.title)}) | {d.impact} | {d.status} | {d.date} |\n"
             
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
             f.write(index_content)
             
        return f"✅ MkDocs config generated: {yml_path}\n✅ Index created: {index_path}"
