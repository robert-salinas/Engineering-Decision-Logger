import os
import pytest
from unittest.mock import patch
from src.logger.manager import DecisionManager
from src.logger.models import init_db

def test_generate_mkdocs_config(tmp_path):
    """Verifies that generate_mkdocs_config creates the .yml and index.md safely."""
    db_file = tmp_path / "test_edl.db"
    # Initialize DB (creates table)
    init_db(str(db_file))
    
    manager = DecisionManager(str(db_file))
    
    # Add a dummy decision
    manager.add_decision({
        "title": "Test MkDocs Decision",
        "context": "We need static docs",
        "chosen_option": "MkDocs Material",
        "rationale": "It is beautiful",
        "status": "Accepted",
        "impact": "Low"
    })
    
    adr_dir = tmp_path / "docs" / "ADR"
    os.makedirs(adr_dir, exist_ok=True)
    
    # Mock PROJECT_ROOT and DEFAULT_ADR_DIR to use tmp_path
    with patch("src.logger.models.PROJECT_ROOT", tmp_path), \
         patch("src.logger.models.DEFAULT_ADR_DIR", str(adr_dir)):
         
         res = manager.generate_mkdocs_config()
         
         assert "MkDocs config generated" in res
         assert (tmp_path / "mkdocs.yml").exists()
         assert (tmp_path / "docs" / "index.md").exists()
         
         # Read config and verify title
         with open(tmp_path / "mkdocs.yml", "r", encoding="utf-8") as f:
             content = f.read()
             assert "RS Engineering Decision Logger Docs" in content
             assert "theme" in content
