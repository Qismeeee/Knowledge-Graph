from fastapi import APIRouter, Depends

from app.api.dependencies import get_repo_service, get_sync_service
from app.core.repo_service import RepoService
from app.core.sync_service import SyncService
from app.models.requests import RegisterRepoRequest
from app.models.responses import RepoDetail, SyncResponse

router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.post("", status_code=201, response_model=RepoDetail)
async def register_repo(
    body: RegisterRepoRequest,
    service: RepoService = Depends(get_repo_service),
) -> RepoDetail:
    return await service.register(body)


@router.get("", response_model=list[RepoDetail])
async def list_repos(
    service: RepoService = Depends(get_repo_service),
) -> list[RepoDetail]:
    return await service.list_repos()


@router.get("/{org_name}/{repo_name}", response_model=RepoDetail)
async def get_repo(
    org_name: str,
    repo_name: str,
    service: RepoService = Depends(get_repo_service),
) -> RepoDetail:
    return await service.get_repo(org_name, repo_name)


@router.delete("/{org_name}/{repo_name}", status_code=204)
async def delete_repo(
    org_name: str,
    repo_name: str,
    service: RepoService = Depends(get_repo_service),
) -> None:
    await service.delete_repo(org_name, repo_name)


@router.post("/{org_name}/{repo_name}/sync", response_model=SyncResponse)
async def sync_repo(
    org_name: str,
    repo_name: str,
    repo_service: RepoService = Depends(get_repo_service),
    sync_service: SyncService = Depends(get_sync_service),
) -> SyncResponse:
    repo = await repo_service.get_repo(org_name, repo_name)
    return await sync_service.sync(
        org_name=org_name,
        repo_name=repo_name,
        url=repo.url,
        branch=repo.default_branch,
    )
