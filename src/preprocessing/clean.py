from typing import List
import pandas as pd
import re
from dateutil import parser
from src.config import config
from pathlib import Path

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text.strip()
    t = re.sub(r'\s+', ' ', t)
    return t

def normalize_date(x):
    try:
        return pd.to_datetime(x)
    except Exception:
        try:
            return pd.to_datetime(parser.parse(str(x)))
        except Exception:
            return pd.NaT

def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['review_text'] = df.get('review_text','').fillna('').apply(clean_text)
    df = df[df['review_text'].str.len() > 0]
    if 'review_date' in df.columns:
        df['review_date'] = df['review_date'].apply(normalize_date)
    df = df.drop_duplicates(subset=['review_text','review_date'])
    df['rating'] = pd.to_numeric(df.get('rating'), errors='coerce')
    df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
    df = df.reset_index(drop=True)
    return df

def save_clean(df: pd.DataFrame, bank:str) -> str:
    Path(config.CLEAN_DIR).mkdir(parents=True, exist_ok=True)
    out = config.CLEAN_DIR / f"{bank.lower()}_clean.csv"
    df.to_csv(out, index=False)
    return str(out)
