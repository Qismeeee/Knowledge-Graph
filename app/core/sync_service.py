import asyncio
import time
from datetime import datetime, timezone

from app.config.logger import get_logger
from app.core.file_scanner import FileScanner
from app.domain.graph import GraphRepository, NodeLabel, RelationType
from app.domain.graph import identity
from app.infrastructure.git_client import GitClient
from app.models.responses import SyncResponse

logger = get_logger(__name__)


class SyncService:
    def __init__(
        self,
        graph: GraphRepository,
        git_client: GitClient,
        scanner: FileScanner,
    ) -> None:
        self._graph = graph
        self._git = git_client
        self._scanner = scanner

    async def sync(
        self,
        org_name: str,
        repo_name: str,
        url: str,
        branch: str,
    ) -> SyncResponse:
        rid = identity.repo_id(org_name, repo_name)
        wid = identity.workspace_id(org_name, repo_name)
        repo_dir = f"{org_name}/{repo_name}"
        run_id = ""

        try:
            await self._update_repo_status(rid, "indexing")

            local_path = await asyncio.to_thread(
                self._git.clone_or_pull, url, branch, repo_dir
            )
            commit_sha = await asyncio.to_thread(
                self._git.get_head_commit, local_path
            )

            epoch = int(time.time())
            run_id = identity.indexrun_id(
                org_name, repo_name, commit_sha, epoch)
            await self._create_index_run(run_id, rid, commit_sha)

            scan_result = await asyncio.to_thread(self._scanner.scan, local_path)
            logger.info(
                "Scanned %s: %d files, %d skipped",
                rid,
                len(scan_result.files),
                scan_result.skipped,
            )

            await self._populate_files(org_name, repo_name, wid, scan_result.files, run_id)

            deactivated = await self._graph.deactivate_untouched(
                NodeLabel.FILE, NodeLabel.WORKSPACE, wid, run_id
            )
            if deactivated:
                logger.info("Deactivated %d stale files in %s",
                            deactivated, rid)

            await self._complete_index_run(
                run_id, len(scan_result.files), scan_result.skipped
            )
            await self._update_repo_status(rid, "indexed", commit_sha)

            return SyncResponse(
                repo_id=rid,
                status="success",
                commit_sha=commit_sha,
                files_processed=len(scan_result.files),
                files_skipped=scan_result.skipped,
            )

        except Exception as e:
            logger.exception("Sync failed for %s: %s", rid, e)
            await self._handle_error(rid, run_id, e)
            raise

    async def _update_repo_status(
        self, rid: str, status: str, commit_sha: str | None = None
    ) -> None:
        props: dict = {"status": status}
        if commit_sha:
            props["last_indexed_commit"] = commit_sha
        await self._graph.upsert_node(NodeLabel.REPO, rid, props, "sync")

    async def _create_index_run(self, run_id: str, rid: str, commit_sha: str) -> None:
        await self._graph.upsert_node(
            NodeLabel.INDEX_RUN,
            run_id,
            {
                "repo_id": rid,
                "commit_sha": commit_sha,
                "mode": "full",
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
            run_id,
        )

    async def _populate_files(
        self,
        org_name: str,
        repo_name: str,
        wid: str,
        files: list,
        run_id: str,
    ) -> None:
        file_rows = [
            {
                "id": identity.file_id(org_name, repo_name, f.path),
                "path": f.path,
                "language": f.language,
                "sha256": f.sha256,
                "loc": f.loc,
            }
            for f in files
        ]
        await self._graph.upsert_nodes(NodeLabel.FILE, file_rows, run_id)

        edge_rows = [
            {
                "source_id": wid,
                "target_id": identity.file_id(org_name, repo_name, f.path),
            }
            for f in files
        ]
        await self._graph.upsert_relationships(
            RelationType.CONTAINS, edge_rows, run_id
        )

    async def _complete_index_run(
        self, run_id: str, files_processed: int, files_skipped: int
    ) -> None:
        await self._graph.upsert_node(
            NodeLabel.INDEX_RUN,
            run_id,
            {
                "status": "success",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "files_processed": files_processed,
                "files_skipped": files_skipped,
            },
            run_id,
        )

    async def _handle_error(self, rid: str, run_id: str, error: Exception) -> None:
        await self._update_repo_status(rid, "error")
        if run_id:
            await self._graph.upsert_node(
                NodeLabel.INDEX_RUN,
                run_id,
                {
                    "status": "failed",
                    "error_message": str(error),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
                run_id,
            )
