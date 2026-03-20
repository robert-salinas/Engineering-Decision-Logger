from typing import Tuple, Optional
import git
from pathlib import Path
import os
import sys


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
        Installs a functional Git hook that checks for unresolved 'Proposed' decisions.

        Args:
            hook_name (str): The name of the hook (e.g., "pre-commit").

        Returns:
            Tuple[bool, str]: A tuple containing a success flag and a message.
        """
        if not self.repo:
            return False, "Not a git repository"

        hook_path = Path(self.repo.git_dir) / "hooks" / hook_name

        # PU-8: Functional hook that checks for Proposed decisions in the DB
        # Determine the path to the project root from the git dir
        project_root = Path(self.repo.working_dir).as_posix()

        hook_content = f"""#!/bin/sh
# EDL Pre-Commit Hook — RS Engineering Decision Logger
# This hook checks for unresolved 'Proposed' decisions before allowing a commit.

echo "🔍 EDL: Checking for unresolved Engineering Decisions..."

# Use Python to query the database
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '{project_root}')
try:
    from src.logger.manager import DecisionManager
    manager = DecisionManager()
    stats = manager.get_stats()
    proposed = stats['by_status'].get('Proposed', 0)
    if proposed > 0:
        print(f'WARNING: {{proposed}} decision(s) still in Proposed status.')
        sys.exit(1)
    else:
        print('OK: All decisions are resolved.')
        sys.exit(0)
except Exception as e:
    print(f'EDL hook error: {{e}}')
    sys.exit(0)
" 2>&1)

EXIT_CODE=$?

echo "$RESULT"

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "⚠️  EDL: You have unresolved decisions. Consider updating their status before committing."
    echo "    Use 'edl list-decisions' to review them."
    echo "    To skip this check, use: git commit --no-verify"
    exit 1
fi

echo "✅ EDL: All decisions resolved. Proceeding with commit."
exit 0
"""

        with open(hook_path, "w", encoding="utf-8") as f:
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
