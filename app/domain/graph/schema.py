from app.domain.graph.enums import NodeLabel
from app.infrastructure.neo4j_client import Neo4jClient
from app.config.logger import get_logger

logger = get_logger(__name__)

CONSTRAINTS = [
    f"CREATE CONSTRAINT {label.value.lower()}_id IF NOT EXISTS "
    f"FOR (n:{label.value}) REQUIRE n.id IS UNIQUE"
    for label in NodeLabel
]

INDEXES = [
    "CREATE INDEX file_active IF NOT EXISTS FOR (n:File) ON (n.active)",
    "CREATE INDEX symbol_active IF NOT EXISTS FOR (n:Symbol) ON (n.active)",
    "CREATE INDEX symbol_kind IF NOT EXISTS FOR (n:Symbol) ON (n.kind)",
    'CREATE FULLTEXT INDEX symbol_search IF NOT EXISTS FOR (n:Symbol) ON EACH [n.name, n.qualified_name]',
    'CREATE FULLTEXT INDEX file_search IF NOT EXISTS FOR (n:File) ON EACH [n.path]',
    'CREATE FULLTEXT INDEX repo_search IF NOT EXISTS FOR (n:Repo) ON EACH [n.name]',
    'CREATE FULLTEXT INDEX service_search IF NOT EXISTS FOR (n:Service) ON EACH [n.name]',
    'CREATE FULLTEXT INDEX package_search IF NOT EXISTS FOR (n:Package) ON EACH [n.name]',
    'CREATE FULLTEXT INDEX endpoint_search IF NOT EXISTS FOR (n:Endpoint) ON EACH [n.route]',
]


class SchemaManager:
    def __init__(self, client: Neo4jClient) -> None:
        self._client = client

    async def setup(self) -> None:
        await self._create_constraints()
        await self._create_indexes()
        logger.info("Schema setup completed")

    async def _create_constraints(self) -> None:
        for stmt in CONSTRAINTS:
            await self._client.execute(stmt)
        logger.info("Created %d unique constraints", len(CONSTRAINTS))

    async def _create_indexes(self) -> None:
        for stmt in INDEXES:
            await self._client.execute(stmt)
        logger.info("Created %d indexes", len(INDEXES))
