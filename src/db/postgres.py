# src/db/postgres.py

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date, Float, ForeignKey, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from pathlib import Path
from src.config import config
import json

_engine: Engine = None

def get_engine() -> Engine:
    """Create or return a singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(config.DB_URL)
    return _engine


def create_schema():
    """Create the database schema for banks and reviews."""
    engine = get_engine()
    metadata = MetaData()

    banks = Table(
        'banks', metadata,
        Column('bank_id', Integer, primary_key=True),
        Column('bank_name', String, unique=True, nullable=False),
        Column('app_name', String)
    )

    reviews = Table(
        'reviews', metadata,
        Column('review_id', Integer, primary_key=True),
        Column('bank_id', Integer, ForeignKey('banks.bank_id'), nullable=False),
        Column('review_text', Text, nullable=False),
        Column('rating', Integer),
        Column('review_date', Date),
        Column('sentiment_label', String(20)),
        Column('sentiment_score', Float),
        Column('themes', Text), 
        Column('source', String(50)),
    )

    metadata.create_all(engine)
    print("✅ Database schema created successfully.")


def insert_reviews(df: pd.DataFrame, bank_name: str):
    """
    Insert reviews into the database.
    Expects df to have a column 'identified_theme' as a list or string.
    Automatically converts lists to JSON strings for DB storage.
    """
    engine = get_engine()

    try:
        with engine.begin() as conn:  # Transaction auto-commit
            # Check if bank exists
            existing = conn.execute(
                text("SELECT bank_id FROM banks WHERE bank_name = :bn"),
                {"bn": bank_name}
            ).fetchone()

            if existing is None:
                conn.execute(
                    text("INSERT INTO banks (bank_name, app_name) VALUES (:bn, :app)"),
                    {"bn": bank_name, "app": bank_name}
                )
                existing = conn.execute(
                    text("SELECT bank_id FROM banks WHERE bank_name = :bn"),
                    {"bn": bank_name}
                ).fetchone()

            bank_id = existing[0]

            insert_df = df[['review_text','rating','review_date','sentiment_label','sentiment_score','source','identified_theme']].copy()
            insert_df.rename(columns={'identified_theme':'themes'}, inplace=True)
            insert_df['bank_id'] = bank_id

            # Convert review_date to datetime
            insert_df['review_date'] = pd.to_datetime(insert_df['review_date'], errors='coerce')

            # Ensure themes are JSON strings
            def to_json(val):
                if isinstance(val, list):
                    return json.dumps(val)
                elif isinstance(val, str):
                    val = val.strip()
                    if val.startswith('[') and val.endswith(']'):
                        try:
                            return json.dumps(json.loads(val.replace("'", '"')))
                        except Exception:
                            return json.dumps([val])
                    else:
                        return json.dumps([val])
                else:
                    return json.dumps([])

            insert_df['themes'] = insert_df['themes'].apply(to_json)

            # Insert into DB
            insert_df.to_sql('reviews', con=conn, if_exists='append', index=False, method='multi')
            print(f"✅ Inserted {len(insert_df)} reviews for bank '{bank_name}'")

    except Exception as e:
        print(f"❌ Failed to insert reviews for '{bank_name}': {e}")


def get_all_reviews(use_fallback=True) -> pd.DataFrame:
    """Retrieve all reviews joined with bank names."""
    engine = get_engine()
    try:
        df = pd.read_sql(
            'SELECT r.*, b.bank_name as bank FROM reviews r JOIN banks b ON r.bank_id=b.bank_id',
            con=engine
        )
        return df
    except Exception as e:
        print("⚠️ DB query failed:", e)
        if use_fallback and Path(config.FALLBACK_CSV).exists():
            print("ℹ️ Using fallback CSV instead")
            return pd.read_csv(config.FALLBACK_CSV)
        raise
