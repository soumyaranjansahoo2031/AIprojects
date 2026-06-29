from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OpenSlate Backend"
    database_url: str
    qdrant_url: str = "http://localhost:6333"
    storage_dir: str = "storage"

    class Config:
        env_file = ".env"


settings = Settings()