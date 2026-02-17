from src.analysis.sentiment import predict_sentiment

def test_english_sentiment():
    result = predict_sentiment(["This app is great!"])
    label, score = result[0]
    assert label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert 0 <= score <= 1

def test_amharic_sentiment():
    result = predict_sentiment(["መተግበሪያው ጥሩ ነው"])
    label, score = result[0]
    assert label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]

def test_emoji_sentiment():
    result = predict_sentiment(["👍"])
    assert result[0][0] == "POSITIVE"
