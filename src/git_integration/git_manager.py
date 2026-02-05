import git
from pathlib import Path
import os

class GitManager:
    def __init__(self, repo_path: str = "."):
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            self.repo = None

    def get_current_commit(self) -> str:
        if self.repo and not self.repo.head.is_detached:
            try:
                return self.repo.head.commit.hexsha
            except (ValueError, git.GitCommandError):
                return "No commits yet"
        return "Unknown"

    def install_hook(self, hook_name: str = "pre-commit"):
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
        
        # Make it executable (might be tricky on Windows, but good practice)
        try:
            os.chmod(hook_path, 0o755)
        except OSError:
            pass
            
        return True, f"Hook {hook_name} installed at {hook_path}"

    def get_last_commit_msg(self) -> str:
        if self.repo:
            return self.repo.head.commit.message
        return ""
