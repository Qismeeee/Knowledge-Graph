from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.config import settings
from app.config.logger import get_logger
from app.core.exceptions import NotFoundError
from app.domain.graph import GraphRepository, SchemaManager
from app.infrastructure.neo4j_client import Neo4jClient

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = Neo4jClient(
        uri=settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        database=settings.neo4j_db,
        max_connection_pool_size=settings.neo4j_max_connection_pool_size,
        batch_size=settings.batch_size,
    )
    await client.connect()

    schema_manager = SchemaManager(client)
    await schema_manager.setup()

    app.state.neo4j = client
    app.state.graph = GraphRepository(client)

    logger.info("Application started")
    yield

    await client.close()
    logger.info("Application stopped")


app = FastAPI(
    title="Code Knowledge Graph",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: object, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/health")
async def health_check() -> dict:
    neo4j_ok = await app.state.neo4j.verify_connectivity()
    return {
        "status": "ok" if neo4j_ok else "degraded",
        "neo4j": "connected" if neo4j_ok else "disconnected",
        "environment": settings.environment,
    }


@app.get("/")
async def root() -> dict:
    return {
        "message": "Code Knowledge Graph API",
        "docs": "/docs",
    }
