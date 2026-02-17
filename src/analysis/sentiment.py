"""
Sentiment Analysis Module (Multilingual + Emoji-Aware)
------------------------------------------------------
Handles Amharic, English, and emoji-rich reviews using
cardiffnlp/twitter-xlm-roberta-base-sentiment.
Supports offline fallback and CI-safe execution.
"""

from typing import List, Tuple
from transformers import pipeline
import logging
import os
import emoji

# --------------------------------------------------
# LOGGER CONFIG
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# MODEL LOADING (CI-SAFE)
# --------------------------------------------------
MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
_classifier = None

# Disable model loading in CI for faster, offline testing
DISABLE_MODEL = os.getenv("CI", "false").lower() == "true"

if not DISABLE_MODEL:
    try:
        _classifier = pipeline("sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME)
        logger.info(f"✅ Multilingual sentiment model '{MODEL_NAME}' loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to load multilingual model: {e}")
        _classifier = None
else:
    logger.warning("⚠️ Running in CI mode — skipping model load.")

# --------------------------------------------------
# EMOJI SENTIMENT MAP
# --------------------------------------------------
EMOJI_MAP = {
    "👍": ("POSITIVE", 0.95),
    "😀": ("POSITIVE", 0.9),
    "😊": ("POSITIVE", 0.92),
    "😍": ("POSITIVE", 0.95),
    "😢": ("NEGATIVE", 0.9),
    "😡": ("NEGATIVE", 0.9),
    "😐": ("NEUTRAL", 0.5),
    "😂": ("POSITIVE", 0.88),
    "😭": ("NEGATIVE", 0.85),
    "😞": ("NEGATIVE", 0.88),
}

# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------
def preprocess_text(text: str) -> str:
    """
    Normalize text by converting emojis to descriptive text and trimming whitespace.
    Handles Amharic and English.
    """
    if not isinstance(text, str):
        return ""
    text = emoji.demojize(text, language="en")
    text = text.replace("_", " ").replace(":", " ")
    return text.strip()

# --------------------------------------------------
# PREDICTION FUNCTION
# --------------------------------------------------
def predict_sentiment(texts: List[str]) -> List[Tuple[str, float]]:
    """
    Predict sentiment for a list of texts using multilingual Roberta model.
    Handles emoji-only texts with manual fallback.
    
    Args:
        texts (List[str]): List of review texts.
    Returns:
        List[Tuple[str, float]]: [(label, score), ...]
    """
    results = []

    for text in texts:
        text = str(text).strip()

        # 1️⃣ Emoji fallback
        if any(ch in EMOJI_MAP for ch in text):
            e = next((EMOJI_MAP[ch] for ch in text if ch in EMOJI_MAP), ("NEUTRAL", 0.5))
            results.append(e)
            continue

        # 2️⃣ Model-based inference (if available)
        if _classifier:
            try:
                processed = preprocess_text(text)
                pred = _classifier(processed)[0]
                label = pred["label"].upper().replace("LABEL_", "")
                score = round(float(pred["score"]), 4)
                results.append((label, score))
            except Exception as e:
                logger.error(f"❌ Model inference failed for text '{text}': {e}")
                results.append(("NEUTRAL", 0.5))
        else:
            # 3️⃣ Fallback for CI/offline environments
            results.append(("NEUTRAL", 0.5))

    logger.info(f"✅ Sentiment predictions generated for {len(results)} texts.")
    return results


# --------------------------------------------------
# MODULE TEST
# --------------------------------------------------
if __name__ == "__main__":
    sample_texts = [
        "The service is excellent!",
        "This app crashes every time 😡",
        "👍",
        "ይህ መተግበሪያ በጣም ጥሩ ነው!",
        "አይሰራም 😞"
    ]

    print("Running sentiment prediction test:")
    preds = predict_sentiment(sample_texts)
    for t, p in zip(sample_texts, preds):
        print(f"{t} → {p}")

