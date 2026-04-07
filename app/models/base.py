"""Base domain models"""
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
    """Index run metadata"""
    id: str
    repo_id: str
    commit_sha: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: Literal["running", "success", "failed"] = "running"
    error_message: Optional[str] = None
