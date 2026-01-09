from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DesignValidationAI"
    ENV: str = "dev"

    DB_PATH: str = "./runs.db"

    EMU_DURATION_SEC: int = 15
    EMU_LOG_HZ: int = 15
    EMU_SEED: int = 42

    LATENCY_P95_MS_WARN: float = 40.0
    CACHE_MISS_WARN: float = 0.12
    ERROR_RATE_WARN: float = 0.02

    ANOMALY_CONTAMINATION: float = 0.05

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
