from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    BASE_DIR: Path = Path(__file__).resolve().parents[1]
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    CLEAN_DIR: Path = DATA_DIR / "cleaned"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    MODELS_DIR: Path = BASE_DIR / "models"
    FALLBACK_CSV: str = os.getenv("FALLBACK_CSV", str(DATA_DIR / "output" / "fallback_reviews.csv"))
    DB_URL: str = os.getenv("DB_URL", "postgresql://postgres:password@localhost:5432/bank_reviews")
    SENTIMENT_MODEL_NAME: str = os.getenv("SENTIMENT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    MAX_SCRAPE_PER_BANK: int = 500
    SLEEP_BETWEEN_REQUESTS: float = 0.5

config = Config()
