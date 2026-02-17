import sys
from pathlib import Path
import pandas as pd
import ast
import json

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db import postgres


DATA_DIR = PROJECT_ROOT / 'data' / 'output'

for file in DATA_DIR.glob('*_themes.csv'):
    print(f"➡️ Processing file: {file.name}")
    try:
        df = pd.read_csv(file)

        # Fix column names: strip '_mXXX' suffix if present
        df.columns = [c.split('_m')[0] if '_m' in c else c for c in df.columns]

        # Ensure 'identified_theme' column exists and convert from string to list
        if 'identified_theme' in df.columns:
            def parse_theme(x):
                if pd.isna(x) or x.strip() == '':
                    return []
                try:
                    # Convert string like "['slow', 'account']" to Python list
                    return ast.literal_eval(x)
                except Exception:
                    return []
            df['identified_theme'] = df['identified_theme'].apply(parse_theme)
        else:
            df['identified_theme'] = [[] for _ in range(len(df))]

        # Ensure 'review_date' is datetime
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')

        # Determine bank name from file name 
        bank_name = file.stem.split('_')[0]

        # Insert into Neon/Postgres
        postgres.insert_reviews(df, bank_name=bank_name)

    except Exception as e:
        print(f"❌ Failed to process {file.name}: {e}")

print("✅ All CSV files processed and inserted successfully.")
