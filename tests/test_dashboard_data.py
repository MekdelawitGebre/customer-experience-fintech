# tests/test_dashboard_data.py

import sys
import json
import pandas as pd
import importlib
from pathlib import Path

# Ensure project root is in path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.db import postgres  

# Utility to reload dashboard
def reload_dashboard_with_mock(mock_df):
    """
    Force reload of src.dashboard.app after patching postgres.get_all_reviews
    so it doesn't connect to Neon DB.
    """
    postgres.get_all_reviews = lambda: mock_df
    if "src.dashboard.app" in sys.modules:
        del sys.modules["src.dashboard.app"]
    import src.dashboard.app as app
    return app



# Test fetch_production_data()
def test_fetch_production_data():
    """Verify data parsing and std_score creation."""
    mock_df = pd.DataFrame({
        "bank": ["CBE", "Dashen"],
        "review_text": ["Good app", "Slow app"],
        "rating": [5, 2],
        "sentiment_label": ["POSITIVE", "NEGATIVE"],
        "sentiment_score": [0.9, 0.3],
        "themes": ['["good", "app"]', '["slow", "app"]']
    })

    app = reload_dashboard_with_mock(mock_df)
    df = app.fetch_production_data()

    assert not df.empty, "Returned dataframe should not be empty"
    assert "std_score" in df.columns, "std_score should exist"
    assert isinstance(df["themes"].iloc[0], list), "Themes must be parsed to list"
    assert df["themes"].iloc[0] == ["good", "app"], f"Unexpected themes: {df['themes'].iloc[0]}"



# Test theme driver computation
def test_theme_driver_computation():
    """Check MultiLabelBinarizer-driven aggregation logic."""
    from sklearn.preprocessing import MultiLabelBinarizer

    df = pd.DataFrame({
        "bank": ["CBE", "CBE", "Dashen"],
        "std_score": [0.9, 0.2, 0.4],
        "themes": [["fast", "good"], ["slow"], ["good", "slow"]]
    })

    mlb = MultiLabelBinarizer()
    X = pd.DataFrame(mlb.fit_transform(df["themes"]), columns=mlb.classes_)

    result = []
    for theme in mlb.classes_:
        mask = X[theme] == 1
        result.append({
            "Theme": theme,
            "Impact": df.loc[mask, "std_score"].mean(),
            "Volume": mask.sum()
        })

    good = next(r for r in result if r["Theme"] == "good")
    assert "Impact" in good
    assert good["Volume"] > 0



