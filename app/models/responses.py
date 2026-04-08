from pydantic import BaseModel, ConfigDict


class RepoDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    url: str
    default_branch: str
    repo_type: str
    status: str
    last_indexed_commit: str | None = None


class SyncResponse(BaseModel):
    repo_id: str
    status: str
    commit_sha: str | None = None
    files_processed: int = 0
    files_skipped: int = 0
