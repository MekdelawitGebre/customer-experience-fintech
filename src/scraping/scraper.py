from typing import List
import time
import pandas as pd
from google_play_scraper import reviews
from src.config import config
from pathlib import Path

APP_IDS = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "Dashen": "com.dashen.dashensuperapp",

}

def scrape_reviews_for_app(app_package: str, n: int = 500) -> pd.DataFrame:
    all_reviews = []
    count = 0
    token = None
    while count < n:
        result, token = reviews(app_package, lang='en', country='us', count=min(200, n-count), continuation_token=token)
        for r in result:
            all_reviews.append({
                "review_text": r.get("content",""),
                "rating": r.get("score"),
                "review_date": r.get("at"),
                "user_name": r.get("userName",""),
                "source": "google_play"
            })
        count += len(result)
        if not token:
            break
        time.sleep(config.SLEEP_BETWEEN_REQUESTS)
    return pd.DataFrame(all_reviews)

def scrape_and_save(bank: str, n:int = None) -> str:
    n = n or config.MAX_SCRAPE_PER_BANK
    app_id = APP_IDS.get(bank)
    if not app_id:
        raise ValueError(f"No app id for {bank}")
    df = scrape_reviews_for_app(app_id, n=n)
    Path(config.RAW_DIR).mkdir(parents=True, exist_ok=True)
    out = config.RAW_DIR / f"{bank.lower()}_raw.csv"
    df.to_csv(out, index=False)
    return str(out)
