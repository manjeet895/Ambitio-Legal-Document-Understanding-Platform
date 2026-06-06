from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(...)
    openai_model: str = "gpt-3.5-turbo"
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "text-embedding-3-small"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    feedback_store_path: str = "./data/feedback_history.json"
    sample_documents_path: str = "./data/samples"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    return Settings()
