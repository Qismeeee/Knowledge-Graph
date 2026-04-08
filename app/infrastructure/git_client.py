from pathlib import Path

import git

from app.config.logger import get_logger

logger = get_logger(__name__)


class GitClient:
    def __init__(self, base_path: str) -> None:
        self._base_path = Path(base_path)

    def clone_or_pull(self, url: str, branch: str, repo_dir: str) -> Path:
        local_path = self._base_path / repo_dir
        if (local_path / ".git").exists():
            return self._pull(local_path, branch)
        return self._clone(url, branch, local_path)

    def get_head_commit(self, local_path: Path) -> str:
        repo = git.Repo(local_path)
        return repo.head.commit.hexsha

    def _clone(self, url: str, branch: str, local_path: Path) -> Path:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Cloning %s (branch=%s) → %s", url, branch, local_path)
        git.Repo.clone_from(url, str(local_path), branch=branch, depth=1)
        return local_path

    def _pull(self, local_path: Path, branch: str) -> Path:
        logger.info("Pulling %s (branch=%s)", local_path, branch)
        repo = git.Repo(local_path)
        repo.remotes.origin.fetch(depth=1)
        repo.git.reset("--hard", f"origin/{branch}")
        return local_path
