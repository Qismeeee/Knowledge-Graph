from fastapi import Request

from app.config import settings
from app.core.file_scanner import FileScanner
from app.core.repo_service import RepoService
from app.core.sync_service import SyncService
from app.domain.graph.repository import GraphRepository
from app.infrastructure.git_client import GitClient
from app.infrastructure.neo4j_client import Neo4jClient


def get_neo4j_client(request: Request) -> Neo4jClient:
    return request.app.state.neo4j


def get_graph_repository(request: Request) -> GraphRepository:
    return request.app.state.graph


def get_repo_service(request: Request) -> RepoService:
    return RepoService(request.app.state.graph)


def get_sync_service(request: Request) -> SyncService:
    return SyncService(
        graph=request.app.state.graph,
        git_client=GitClient(settings.repo_clone_base_path),
        scanner=FileScanner(),
    )
