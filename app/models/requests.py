from typing import Literal

from pydantic import BaseModel


class RegisterRepoRequest(BaseModel):
    org_name: str
    repo_name: str
    url: str
    branch: str = "main"
    repo_type: Literal["multi-repo", "monorepo"] = "multi-repo"
    auth_method: Literal["ssh", "https", "token"] = "https"
