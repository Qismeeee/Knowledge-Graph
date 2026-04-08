from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncManagedTransaction

from app.config.logger import get_logger

logger = get_logger(__name__)


class Neo4jClient:
    def __init__(
        self,
        uri: str,
        auth: tuple[str, str],
        database: str = "neo4j",
        max_connection_pool_size: int = 50,
        batch_size: int = 1000,
    ) -> None:
        self._uri = uri
        self._auth = auth
        self._database = database
        self._max_pool_size = max_connection_pool_size
        self._batch_size = batch_size
        self._driver: AsyncDriver | None = None

    @property
    def driver(self) -> AsyncDriver:
        if not self._driver:
            raise RuntimeError("Neo4jClient is not connected. Call connect() first.")
        return self._driver

    async def connect(self) -> None:
        self._driver = AsyncGraphDatabase.driver(
            self._uri,
            auth=self._auth,
            max_connection_pool_size=self._max_pool_size,
        )
        await self._driver.verify_connectivity()
        logger.info("Connected to Neo4j at %s", self._uri)

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Disconnected from Neo4j")

    async def verify_connectivity(self) -> bool:
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    async def execute(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        async with self.driver.session(database=self._database) as session:
            result = await session.run(cypher, params or {})
            records = [record.data() async for record in result]
            await result.consume()
            return records

    async def write(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        async with self.driver.session(database=self._database) as session:

            async def _work(tx: AsyncManagedTransaction) -> list[dict[str, Any]]:
                result = await tx.run(cypher, params or {})
                return [record.data() async for record in result]

            return await session.execute_write(_work)

    async def write_batch(
        self,
        cypher: str,
        rows: list[dict[str, Any]],
        params: dict[str, Any] | None = None,
    ) -> None:
        if not rows:
            return
        extra = params or {}
        for i in range(0, len(rows), self._batch_size):
            chunk = rows[i : i + self._batch_size]
            await self.write(cypher, {"rows": chunk, **extra})
