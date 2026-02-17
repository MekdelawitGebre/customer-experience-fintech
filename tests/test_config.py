from src.config import config
from pathlib import Path

def test_data_directories_exist():
    assert Path(config.CLEAN_DIR).exists(), "Clean data directory should exist"
    assert Path(config.OUTPUT_DIR).exists(), "Output directory should exist"

def test_database_url_present():
    assert config.DB_URL.startswith("postgresql"), "DB_URL should be a valid Postgres connection string"
