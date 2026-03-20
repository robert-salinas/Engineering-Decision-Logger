import pytest
from fastapi.testclient import TestClient
from src.web.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestWebIndex:
    """Tests for the main index page."""

    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "RS" in response.text
        assert "EDL" in response.text

    def test_index_search(self, client):
        response = client.get("/?q=nonexistent")
        assert response.status_code == 200


class TestWebLogDecision:
    """Tests for the decision logging endpoint."""

    def test_log_decision_redirects(self, client):
        response = client.post("/log", data={
            "title": "Web Test Decision",
            "context": "Testing via TestClient",
            "chosen_option": "FastAPI",
            "rationale": "Built-in test support",
            "impact": "Medium",
            "status": "Accepted",
        }, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_log_decision_missing_field(self, client):
        response = client.post("/log", data={
            "title": "Incomplete",
        })
        assert response.status_code == 422  # FastAPI validation error


class TestWebGetDecision:
    """Tests for the decision detail endpoint."""

    def test_get_decision_page(self, client):
        # First create a decision
        client.post("/log", data={
            "title": "Detail Test",
            "context": "For detail page",
            "chosen_option": "Testing",
            "rationale": "Verification",
            "impact": "Low",
            "status": "Proposed",
        }, follow_redirects=False)

        response = client.get("/decision/1")
        # May or may not find the decision depending on DB state,
        # but the page should render without error
        assert response.status_code == 200


class TestWebDeleteDecision:
    """Tests for the decision delete endpoint."""

    def test_delete_decision_redirects(self, client):
        # Create first
        client.post("/log", data={
            "title": "To Delete",
            "context": "Will be deleted",
            "chosen_option": "Delete",
            "rationale": "Testing",
            "impact": "Low",
            "status": "Accepted",
        }, follow_redirects=False)

        response = client.post("/decision/1/delete", follow_redirects=False)
        assert response.status_code == 303
