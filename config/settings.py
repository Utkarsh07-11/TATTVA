import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings


def resolve_base_dir() -> Path:
    """Project root in source mode, or PyInstaller extract dir when frozen."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


BASE_DIR = resolve_base_dir()


class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH 2026 PS 26009 - Manganese Decision Support"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SYNTHETIC_MODE: bool = True

    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    SYNTHETIC_DATA_DIR: Path = BASE_DIR / "data" / "synthetic"
    MODELS_DIR: Path = BASE_DIR / "data" / "models"
    FRONTEND_DIST: Path = BASE_DIR / "frontend" / "dist"

    CENTER_LAT: float = 21.8715
    CENTER_LON: float = 80.1843
    CRS_PROJECTION: str = "EPSG:32644"

    DEFAULT_MINE_BLOCK: str = "BLOCK_A"
    DEFAULT_HORIZON_DAYS: int = 30
    DEFAULT_MONTHLY_TARGET: float = 10000.0
    QUANTILES: list[float] = [0.1, 0.5, 0.9]

    WEIGHT_RECOVERY: float = 1.0
    WEIGHT_COST: float = 0.5
    WEIGHT_RISK: float = 0.3
    WEIGHT_FEASIBILITY: float = 0.2

    API_V1_STR: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()

for directory in [
    settings.DATA_DIR,
    settings.RAW_DATA_DIR,
    settings.PROCESSED_DATA_DIR,
    settings.SYNTHETIC_DATA_DIR,
    settings.MODELS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
