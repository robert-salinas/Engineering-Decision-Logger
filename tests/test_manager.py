import pytest
import os
from src.logger.manager import DecisionManager
from src.logger.models import Decision
from pathlib import Path


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_edl.db"
    adr_dir = tmp_path / "ADR"
    manager = DecisionManager(db_path=str(db_file), adr_dir=str(adr_dir))
    return manager, adr_dir


def test_add_decision(temp_db):
    manager, adr_dir = temp_db
    data = {
        "title": "Test Decision",
        "context": "Just a test",
        "chosen_option": "Option A",
        "rationale": "Because it works",
        "status": "Accepted",
        "drivers": ["Speed"],
        "options": ["Option A", "Option B"],
    }

    decision = manager.add_decision(data)

    assert decision.id == 1
    assert decision.title == "Test Decision"

    # Check if ADR file was created
    adr_files = list(adr_dir.glob("*.md"))
    assert len(adr_files) == 1
    assert "test-decision" in adr_files[0].name


def test_list_decisions(temp_db):
    manager, _ = temp_db
    manager.add_decision(
        {"title": "D1", "context": "C1", "chosen_option": "O1", "rationale": "R1"}
    )
    manager.add_decision(
        {"title": "D2", "context": "C2", "chosen_option": "O2", "rationale": "R2"}
    )

    decisions = manager.list_decisions()
    assert len(decisions) == 2
    assert decisions[0].title == "D1"
    assert decisions[1].title == "D2"


def test_search_decisions(temp_db):
    manager, _ = temp_db
    manager.add_decision(
        {
            "title": "Database Choice",
            "context": "Need storage",
            "chosen_option": "SQLite",
            "rationale": "Simple",
        }
    )
    manager.add_decision(
        {
            "title": "UI Framework",
            "context": "Need frontend",
            "chosen_option": "React",
            "rationale": "Popular",
        }
    )

    results = manager.search_decisions("SQLite")
    assert len(results) == 1
    assert results[0].title == "Database Choice"

    results = manager.search_decisions("frontend")
    assert len(results) == 1
    assert results[0].title == "UI Framework"
