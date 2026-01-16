import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG PGVector Engine"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Security & API Key
    API_KEY_ENABLED: bool = False
    API_KEY_HEADER_NAME: str = "X-API-Key"
    API_KEYS: List[str] = ["sk-rag-admin-enterprise-key-2026"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"

    # PostgreSQL & PGVector
    POSTGRES_USER: str = Field(default="postgres", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(default="localhost", alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="vectordb", alias="POSTGRES_DB")
    PGVECTOR_COLLECTION_NAME: str = "rag_enterprise_docs"

    # Redis
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, alias="REDIS_DB")
    CONVERSATION_TTL_SECONDS: int = 86400  # 24 hours

    # LLM & Embeddings
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_API_BASE: Optional[str] = Field(default=None, alias="OPENAI_API_BASE")
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"

    # RAG Retrieval Settings
    DEFAULT_TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.3
    RETRIEVAL_SEARCH_TYPE: str = "similarity"  # "similarity" or "mmr"
    MMR_LAMBDA_MULT: float = 0.7

    # Ingestion Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    UNSTRUCTURED_API_KEY: Optional[str] = None
    DATA_DIR: str = "./data"

    @property
    def sync_database_uri(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def async_database_uri(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
