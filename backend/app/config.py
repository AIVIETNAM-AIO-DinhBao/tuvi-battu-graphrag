from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://test:test@localhost:5432/test"
    GEMINI_API_KEYS: str = ""
    GEMINI_API_KEY: str = "test-key"
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    GEMINI_API_KEY_4: str = ""
    GEMINI_API_KEY_5: str = ""
    GEMINI_API_KEY_6: str = ""
    GEMINI_API_KEY_7: str = ""
    GEMINI_API_KEY_8: str = ""

    NEXT_PUBLIC_SUPABASE_URL: str = "http://localhost:54321"
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = "test-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "test-service-role-key"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "test-password"
    NEO4J_DATABASE: str = "neo4j"
    NEO4J_CONNECTION_TIMEOUT: float = 5.0
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: float = 5.0
    NEO4J_MAX_TRANSACTION_RETRY_TIME: float = 5.0

    LANGFUSE_SECRET_KEY: str = "test-secret-key"
    LANGFUSE_PUBLIC_KEY: str = "test-public-key"
    LANGFUSE_BASE_URL: str = "http://localhost:3000"

    DENSE_QUERY_EMBEDDING_BACKEND: str = "local"
    DENSE_QUERY_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    DENSE_QUERY_EMBEDDING_DEVICE: str = "cpu"
    DENSE_QUERY_EMBEDDING_SLOT: str = "bge_m3"
    DENSE_QUERY_EMBEDDING_DIM: int = 1024
    DENSE_QUERY_EMBEDDING_IMPLEMENTATION: str = "auto"
    DENSE_QUERY_EMBEDDING_NORMALIZE: bool = True

    DEFAULT_EXPERIMENT_CONFIG: str = "configs/default_production.yaml"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
