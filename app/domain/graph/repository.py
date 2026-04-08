from typing import Any

from app.domain.graph.enums import NodeLabel, RelationType
from app.infrastructure.neo4j_client import Neo4jClient


class GraphRepository:
    def __init__(self, client: Neo4jClient) -> None:
        self._client = client

    async def upsert_node(
        self, label: NodeLabel, node_id: str, props: dict[str, Any], run_id: str
    ) -> None:
        await self.upsert_nodes(label, [{"id": node_id, **props}], run_id)

    async def upsert_nodes(
        self, label: NodeLabel, rows: list[dict[str, Any]], run_id: str
    ) -> None:
        if not rows:
            return
        prepared = [
            {"id": row["id"], "props": {
                k: v for k, v in row.items() if k != "id"}}
            for row in rows
        ]
        cypher = (
            "UNWIND $rows AS row "
            f"MERGE (n:{label.value} {{id: row.id}}) "
            "ON CREATE SET "
            "  n.created_at = datetime(), "
            "  n.first_seen_run_id = $run_id "
            "SET "
            "  n += row.props, "
            "  n.last_touched_run_id = $run_id, "
            "  n.active = true, "
            "  n.updated_at = datetime()"
        )
        await self._client.write_batch(cypher, prepared, {"run_id": run_id})

    async def upsert_relationship(
        self,
        rel_type: RelationType,
        source_id: str,
        target_id: str,
        props: dict[str, Any],
        run_id: str,
    ) -> None:
        await self.upsert_relationships(
            rel_type,
            [{"source_id": source_id, "target_id": target_id, **props}],
            run_id,
        )

    async def upsert_relationships(
        self,
        rel_type: RelationType,
        rows: list[dict[str, Any]],
        run_id: str,
    ) -> None:
        if not rows:
            return
        prepared = [
            {
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "props": {
                    k: v
                    for k, v in row.items()
                    if k not in ("source_id", "target_id")
                },
            }
            for row in rows
        ]
        cypher = (
            "UNWIND $rows AS row "
            "MATCH (a {id: row.source_id}) "
            "MATCH (b {id: row.target_id}) "
            f"MERGE (a)-[r:{rel_type.value}]->(b) "
            "ON CREATE SET "
            "  r.first_seen_run_id = $run_id "
            "SET "
            "  r += row.props, "
            "  r.last_touched_run_id = $run_id, "
            "  r.active = true"
        )
        await self._client.write_batch(cypher, prepared, {"run_id": run_id})

    async def deactivate_untouched(
        self,
        label: NodeLabel,
        parent_label: NodeLabel,
        parent_id: str,
        run_id: str,
    ) -> int:
        cypher = (
            f"MATCH (p:{parent_label.value} {{id: $parent_id}})"
            f"-[:CONTAINS*]->(n:{label.value}) "
            "WHERE n.active = true AND n.last_touched_run_id <> $run_id "
            "SET n.active = false, "
            "    n.deactivated_in_run_id = $run_id, "
            "    n.updated_at = datetime() "
            "RETURN count(n) AS deactivated"
        )
        result = await self._client.write(
            cypher, {"parent_id": parent_id, "run_id": run_id}
        )
        return result[0]["deactivated"] if result else 0

    async def query(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return await self._client.execute(cypher, params)

    async def execute_write(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return await self._client.write(cypher, params)
