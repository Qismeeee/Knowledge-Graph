from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env"""
    # App
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="neo4j_default_password", env="NEO4J_PASSWORD")
    neo4j_db: str = Field(default="neo4j", env="NEO4J_DB")

    # Sync
    repos_sync_interval_hours: int = Field(default=24, env="REPOS_SYNC_INTERVAL_HOURS")
    max_concurrent_syncs: int = Field(default=2, env="MAX_CONCURRENT_SYNCS")
    repo_clone_base_path: str = Field(default="/workspace/repos", env="REPO_CLONE_BASE_PATH")

    # LLM
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")

    # Features
    enable_incremental_indexing: bool = Field(default=True, env="ENABLE_INCREMENTAL_INDEXING")
    enable_vector_search: bool = Field(default=False, env="ENABLE_VECTOR_SEARCH")
    enable_webhooks: bool = Field(default=True, env="ENABLE_WEBHOOKS")

    # Limits
    query_timeout_seconds: int = Field(default=30, env="QUERY_TIMEOUT_SECONDS")
    max_graph_depth: int = Field(default=5, env="MAX_GRAPH_DEPTH")
    batch_size: int = Field(default=1000, env="BATCH_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
