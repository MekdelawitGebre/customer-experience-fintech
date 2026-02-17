# src/analysis/thematic.py
from typing import List
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_themes(texts: List[str], top_n: int = 5) -> List[str]:
    """Extract top keywords/themes for a single review."""
    doc = nlp(" ".join(texts))
    # Only consider nouns and adjectives as themes
    words = [token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "ADJ")]
    most_common = [w for w, _ in Counter(words).most_common(top_n)]
    return most_common

def extract_themes_per_review(reviews: List[str], top_n: int = 5) -> List[str]:
    themes_list = []
    for review in reviews:
        if not review.strip():
            themes_list.append([])
            continue
        themes_list.append(extract_themes([review], top_n))
    return themes_list
