from app.core.exceptions import NotFoundError
from app.domain.graph import GraphRepository, NodeLabel, RelationType
from app.domain.graph import identity
from app.models.requests import RegisterRepoRequest
from app.models.responses import RepoDetail


class RepoService:
    _RUN_ID = "manual"

    def __init__(self, graph: GraphRepository) -> None:
        self._graph = graph

    async def register(self, request: RegisterRepoRequest) -> RepoDetail:
        oid = identity.org_id(request.org_name)
        rid = identity.repo_id(request.org_name, request.repo_name)
        wid = identity.workspace_id(request.org_name, request.repo_name)

        await self._graph.upsert_node(
            NodeLabel.ORG, oid, {"name": request.org_name}, self._RUN_ID
        )

        repo_props = {
            "name": request.repo_name,
            "url": request.url,
            "default_branch": request.branch,
            "repo_type": request.repo_type,
            "auth_method": request.auth_method,
            "status": "pending",
        }
        await self._graph.upsert_node(NodeLabel.REPO, rid, repo_props, self._RUN_ID)

        await self._graph.upsert_node(
            NodeLabel.WORKSPACE,
            wid,
            {"name": request.repo_name, "path": "."},
            self._RUN_ID,
        )

        await self._graph.upsert_relationship(
            RelationType.CONTAINS, oid, rid, {}, self._RUN_ID
        )
        await self._graph.upsert_relationship(
            RelationType.CONTAINS, rid, wid, {}, self._RUN_ID
        )

        return RepoDetail(
            id=rid,
            name=request.repo_name,
            url=request.url,
            default_branch=request.branch,
            repo_type=request.repo_type,
            status="pending",
        )

    async def list_repos(self) -> list[RepoDetail]:
        result = await self._graph.query(
            "MATCH (n:Repo) WHERE n.active = true "
            "RETURN properties(n) AS props ORDER BY n.name"
        )
        return [RepoDetail.model_validate(r["props"]) for r in result]

    async def get_repo(self, org_name: str, repo_name: str) -> RepoDetail:
        rid = identity.repo_id(org_name, repo_name)
        result = await self._graph.query(
            "MATCH (n:Repo {id: $id}) WHERE n.active = true "
            "RETURN properties(n) AS props",
            {"id": rid},
        )
        if not result:
            raise NotFoundError("Repo", rid)
        return RepoDetail.model_validate(result[0]["props"])

    async def delete_repo(self, org_name: str, repo_name: str) -> None:
        rid = identity.repo_id(org_name, repo_name)
        exists = await self._graph.query(
            "MATCH (n:Repo {id: $id}) WHERE n.active = true RETURN n.id AS id",
            {"id": rid},
        )
        if not exists:
            raise NotFoundError("Repo", rid)
        await self._graph.execute_write(
            "MATCH (n:Repo {id: $id})-[:CONTAINS*0..]->(child) "
            "SET child.active = false, child.updated_at = datetime()",
            {"id": rid},
        )


