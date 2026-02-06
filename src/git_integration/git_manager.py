from typing import Tuple, Optional
import git
from pathlib import Path
import os


class GitManager:
    """
    Handles interactions with the Git repository, such as retrieving commit hashes
    and installing hooks.
    """

    def __init__(self, repo_path: str = "."):
        """
        Initializes the GitManager.

        Args:
            repo_path (str): The path to the Git repository.
        """
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            self.repo = None

    def get_current_commit(self) -> str:
        """
        Retrieves the hexsha of the current Git commit.

        Returns:
            str: The commit hash, "No commits yet", or "Unknown".
        """
        if self.repo:
            try:
                if not self.repo.head.is_detached:
                    return self.repo.head.commit.hexsha
            except (ValueError, git.GitCommandError):
                return "No commits yet"
        return "Unknown"

    def install_hook(self, hook_name: str = "pre-commit") -> Tuple[bool, str]:
        """
        Installs a Git hook in the current repository.

        Args:
            hook_name (str): The name of the hook (e.g., "pre-commit").

        Returns:
            Tuple[bool, str]: A tuple containing a success flag and a message.
        """
        if not self.repo:
            return False, "Not a git repository"

        hook_path = Path(self.repo.git_dir) / "hooks" / hook_name
        hook_content = f"""#!/bin/sh
# EDL Git Hook
echo "Checking for new Engineering Decisions..."
# You can add logic here to enforce ADR creation if needed
"""

        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make it executable
        try:
            os.chmod(hook_path, 0o755)
        except OSError:
            pass

        return True, f"Hook {hook_name} installed at {hook_path}"

    def get_last_commit_msg(self) -> str:
        """
        Retrieves the message of the last Git commit.

        Returns:
            str: The commit message or an empty string.
        """
        if self.repo:
            try:
                return self.repo.head.commit.message
            except (ValueError, git.GitCommandError, AttributeError):
                return ""
        return ""
