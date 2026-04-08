from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class RepoConfig(BaseModel):
    """Repository configuration"""
    id: str
    name: str
    url: str
    branch: str = "main"
    repo_type: Literal["multi-repo", "monorepo"] = "multi-repo"
    auth_method: Literal["ssh", "https", "token"] = "https"
    languages: list[str] = Field(default_factory=list)
    last_indexed_commit: Optional[str] = None
    status: Literal["pending", "indexing", "indexed", "error"] = "pending"


class IndexRun(BaseModel):
    id: str
    repo_id: str
    commit_sha: str
    mode: Literal["full", "incremental"] = "full"
    status: Literal["running", "success", "failed"] = "running"
    started_at: datetime
    completed_at: Optional[datetime] = None
    files_processed: int = 0
    files_skipped: int = 0
    error_message: Optional[str] = None
