from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # App
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_default_password"
    neo4j_db: str = "neo4j"
    neo4j_max_connection_pool_size: int = 50

    # Sync
    repos_sync_interval_hours: int = 24
    max_concurrent_syncs: int = 2
    repo_clone_base_path: str = "/workspace/repos"

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""

    # Features
    enable_incremental_indexing: bool = True
    enable_vector_search: bool = False
    enable_webhooks: bool = True

    # Limits
    query_timeout_seconds: int = 30
    max_graph_depth: int = 5
    batch_size: int = 1000


settings = Settings()
