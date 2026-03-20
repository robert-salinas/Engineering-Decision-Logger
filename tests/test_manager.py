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


# PU-3: Update decisions
def test_update_decision(temp_db):
    manager, _ = temp_db
    data = {
        "title": "Original Title",
        "context": "Original context",
        "chosen_option": "Option A",
        "rationale": "Original rationale",
    }
    decision = manager.add_decision(data)
    assert decision.title == "Original Title"

    updated = manager.update_decision(decision.id, {
        "title": "Updated Title",
        "context": "Updated context",
    })
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.context == "Updated context"
    # Unchanged fields
    assert updated.chosen_option == "Option A"


def test_update_decision_not_found(temp_db):
    manager, _ = temp_db
    result = manager.update_decision(999, {"title": "Nope"})
    assert result is None


# PU-3: Delete decisions
def test_delete_decision(temp_db):
    manager, adr_dir = temp_db
    data = {
        "title": "To Delete",
        "context": "Will be deleted",
        "chosen_option": "None",
        "rationale": "Testing delete",
    }
    decision = manager.add_decision(data)
    assert len(manager.list_decisions()) == 1

    # Check ADR file exists
    adr_files = list(adr_dir.glob("*.md"))
    assert len(adr_files) == 1

    success = manager.delete_decision(decision.id)
    assert success is True
    assert len(manager.list_decisions()) == 0

    # ADR file should be removed
    adr_files = list(adr_dir.glob("*.md"))
    assert len(adr_files) == 0


def test_delete_decision_not_found(temp_db):
    manager, _ = temp_db
    result = manager.delete_decision(999)
    assert result is False


# PU-6: Stats
def test_get_stats_empty(temp_db):
    manager, _ = temp_db
    stats = manager.get_stats()
    assert stats["total"] == 0
    assert stats["by_impact"]["Low"] == 0
    assert stats["by_impact"]["Medium"] == 0
    assert stats["by_impact"]["Critical"] == 0


def test_get_stats_with_data(temp_db):
    manager, _ = temp_db
    manager.add_decision({"title": "D1", "context": "C", "chosen_option": "O", "rationale": "R", "impact": "Critical", "status": "Accepted"})
    manager.add_decision({"title": "D2", "context": "C", "chosen_option": "O", "rationale": "R", "impact": "Low", "status": "Proposed"})
    manager.add_decision({"title": "D3", "context": "C", "chosen_option": "O", "rationale": "R", "impact": "Critical", "status": "Proposed"})

    stats = manager.get_stats()
    assert stats["total"] == 3
    assert stats["by_impact"]["Critical"] == 2
    assert stats["by_impact"]["Low"] == 1
    assert stats["by_status"]["Proposed"] == 2
    assert stats["by_status"]["Accepted"] == 1


# PU-9: Get decision
def test_get_decision_not_found(temp_db):
    manager, _ = temp_db
    result = manager.get_decision(999)
    assert result is None
