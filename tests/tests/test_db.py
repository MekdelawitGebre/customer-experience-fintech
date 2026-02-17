from src.db import postgres
from sqlalchemy import text

def test_db_connection():
    engine = postgres.get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1, "Database connection failed"

def test_schema_creation():
    postgres.create_schema()
    engine = postgres.get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name IN ('banks', 'reviews')")
        ).fetchall()
    tables = [r[0] for r in result]
    assert 'banks' in tables and 'reviews' in tables, "Missing required tables"
