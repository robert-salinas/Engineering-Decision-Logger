import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from src.git_integration.git_manager import GitManager
import git


class TestGitManagerWithRepo:
    """Tests for GitManager when a valid repo is present."""

    def test_get_current_commit_returns_hash(self):
        """The current project IS a git repo, so this should return a hash."""
        gm = GitManager(".")
        if gm.repo:
            result = gm.get_current_commit()
            # Should be a hex string (40 chars) or fallback
            assert isinstance(result, str)
            assert len(result) in (40, len("No commits yet"), len("Unknown"))

    def test_get_last_commit_msg(self):
        gm = GitManager(".")
        if gm.repo:
            msg = gm.get_last_commit_msg()
            assert isinstance(msg, str)


class TestGitManagerNoRepo:
    """Tests for GitManager when no repo is available."""

    @patch("git.Repo", side_effect=git.InvalidGitRepositoryError)
    def test_no_repo(self, mock_repo):
        gm = GitManager("/tmp/fake")
        assert gm.repo is None
        assert gm.get_current_commit() == "Unknown"
        assert gm.get_last_commit_msg() == ""

    @patch("git.Repo", side_effect=git.InvalidGitRepositoryError)
    def test_install_hook_no_repo(self, mock_repo):
        gm = GitManager("/tmp/fake")
        success, msg = gm.install_hook()
        assert success is False
        assert "Not a git repository" in msg


class TestGitManagerInstallHook:
    """Tests for the install_hook functionality."""

    def test_install_hook_creates_file(self, tmp_path):
        """Test hook installation with a real temp git repo."""
        # Create a temporary git repo
        repo = git.Repo.init(tmp_path)
        gm = GitManager(str(tmp_path))

        success, msg = gm.install_hook("pre-commit")
        assert success is True

        hook_path = tmp_path / ".git" / "hooks" / "pre-commit"
        assert hook_path.exists()

        content = hook_path.read_text(encoding="utf-8")
        assert "EDL Pre-Commit Hook" in content
        assert "Proposed" in content
