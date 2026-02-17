from src.analysis.thematic import extract_themes_per_review

def test_theme_extraction_keywords():
    texts = ["The app is slow and crashes often", "Great interface, love it"]
    themes = extract_themes_per_review(texts)
    assert len(themes) == 2
    assert isinstance(themes[0], list)
    assert any("slow" in t for t in themes[0])
