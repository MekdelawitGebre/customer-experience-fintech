"""
Sentiment Analysis Module (Multilingual + Emoji-Aware)
------------------------------------------------------
Handles Amharic, English, and emoji-rich reviews using
cardiffnlp/twitter-xlm-roberta-base-sentiment.
"""

from typing import List, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import logging


# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load multilingual sentiment model

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

try:
    _classifier = pipeline("sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME)
    logger.info(f"✅ Multilingual sentiment model '{MODEL_NAME}' loaded successfully.")
except Exception as e:
    logger.error(f"❌ Failed to load multilingual model: {e}")
    _classifier = None


# Utility: Emoji and Amharic normalization
def preprocess_text(text: str) -> str:
    """
    Normalize emojis and strip excessive punctuation for better model performance.
    """
    import emoji
    # Convert emojis to textual meaning (😊 -> :smiling_face_with_smiling_eyes:)
    text = emoji.demojize(text, language="en")
    # Remove redundant underscores introduced by demojize
    text = text.replace("_", " ").replace(":", " ")
    return text.strip()


# Sentiment Prediction Function
def predict_sentiment(texts: List[str]) -> List[Tuple[str, float]]:
    """
    Predict sentiment for a list of texts using multilingual Roberta model.
    Args:
        texts (List[str]): List of reviews.
    Returns:
        List[Tuple[str, float]]: [(label, score), ...]
    """
    if _classifier is None:
        logger.warning("⚠️ Using fallback neutral sentiment (model not loaded).")
        return [("NEUTRAL", 0.5) for _ in texts]

    results = []
    try:
        processed_texts = [preprocess_text(t) for t in texts]
        outputs = _classifier(processed_texts)
        for o in outputs:
            label = o["label"].upper().replace("LABEL_", "")
            score = round(float(o["score"]), 4)
            results.append((label, score))
        logger.info(f"✅ Analyzed {len(results)} reviews successfully.")
    except Exception as e:
        logger.error(f"❌ Error during prediction: {e}")
        results = [("NEUTRAL", 0.5) for _ in texts]
    return results
