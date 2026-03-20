import pytest
from src.adr_formatter.formatter import ADRFormatter


@pytest.fixture
def formatter():
    return ADRFormatter()


class TestADRFormatter:
    """Tests for the ADR Markdown formatter."""

    def test_render_basic(self, formatter):
        data = {
            "id": 1,
            "title": "Use SQLite",
            "status": "Accepted",
            "date": "2026-01-15",
            "context": "Need a simple database",
            "drivers": ["Simplicity", "No server needed"],
            "options": ["SQLite", "PostgreSQL"],
            "chosen_option": "SQLite",
            "rationale": "it requires no setup",
            "consequences_good": "Easy to deploy",
            "consequences_bad": "Limited concurrency",
            "pros_cons": [],
        }
        result = formatter.render(data)

        assert "# 1-Use SQLite" in result
        assert "* Status: Accepted" in result
        assert "* Date: 2026-01-15" in result
        assert "Need a simple database" in result
        assert "* Simplicity" in result
        assert "* No server needed" in result
        assert '\"SQLite\"' in result
        assert "Easy to deploy" in result
        assert "Limited concurrency" in result

    def test_render_with_pros_cons(self, formatter):
        data = {
            "id": 2,
            "title": "Frontend Framework",
            "status": "Proposed",
            "date": "2026-02-10",
            "context": "Need a frontend",
            "drivers": [],
            "options": [],
            "chosen_option": "React",
            "rationale": "large community",
            "consequences_good": "Lots of libraries",
            "consequences_bad": "Heavy bundle size",
            "pros_cons": [
                {"name": "React", "pros": "large ecosystem", "cons": "complex state"},
                {"name": "Vue", "pros": "easier learning", "cons": "smaller community"},
            ],
        }
        result = formatter.render(data)

        assert "### React" in result
        assert "large ecosystem" in result
        assert "### Vue" in result
        assert "easier learning" in result

    def test_render_adds_date_if_missing(self, formatter):
        data = {
            "id": 3,
            "title": "Date Test",
            "status": "Accepted",
            "context": "Testing date",
            "drivers": [],
            "options": [],
            "chosen_option": "Option A",
            "rationale": "because",
            "consequences_good": "",
            "consequences_bad": "",
            "pros_cons": [],
        }
        result = formatter.render(data)
        assert "* Date:" in result

    def test_render_empty_lists(self, formatter):
        data = {
            "id": 4,
            "title": "Empty Lists",
            "status": "Proposed",
            "date": "2026-03-01",
            "context": "No drivers or options",
            "drivers": [],
            "options": [],
            "chosen_option": "Only option",
            "rationale": "no alternatives",
            "consequences_good": "",
            "consequences_bad": "",
            "pros_cons": [],
        }
        result = formatter.render(data)
        assert "# 4-Empty Lists" in result
        # No bullet points for empty lists
        assert "## Decision Drivers" in result

    def test_get_filename(self):
        filename = ADRFormatter.get_filename(1, "Use SQLModel for ORM")
        assert filename == "0001-use-sqlmodel-for-orm.md"

    def test_get_filename_special_chars(self):
        filename = ADRFormatter.get_filename(42, "API v2.0 - REST vs GraphQL!")
        assert filename.startswith("0042-")
        assert filename.endswith(".md")
        # Slugify should handle special chars
        assert "!" not in filename

    def test_get_filename_padding(self):
        filename = ADRFormatter.get_filename(7, "Short")
        assert filename.startswith("0007-")
