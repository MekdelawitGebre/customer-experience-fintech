# Fintech Customer Experience Intelligence Hub

**A data-driven platform to analyze customer reviews for Ethiopian banks, providing actionable insights into sentiment, themes, and market behavior.**

---

## Business Problem
Banks receive thousands of customer reviews daily from Google Play. Manually analyzing feedback is slow and error-prone, making it difficult to:
* **Identify customer pain points** (e.g., OTP failures, login issues).
* **Track app performance** and sentiment trends over time.
* **Benchmark against competitors** in the Ethiopian market.

This project automates review analysis, helping banks make data-driven decisions to improve services and customer satisfaction.

---

##  Solution Overview
* **Data Collection:** Aggregates customer reviews from multiple sources.
* **Data Processing:** Cleans, normalizes, and extracts key themes and sentiment.
* **Analysis:** Computes KPIs such as Market Volume, Average Rating, Sentiment Strength, and Polarization.
* **Visualization:** Interactive dashboards with benchmarking, rating distributions, and theme driver insights.
* **Architecture:** Python + Streamlit frontend, PostgreSQL/Neon backend, and pandas/plotly for analytics.



---

## Key Results
* **Market Insights:** Over **1,200+ reviews** analyzed for 3 major banks.
* **Customer Sentiment:** Accurate sentiment scoring for **English, Amharic**, and emoji-laden reviews.
* **Thematic Analysis:** Extracted actionable themes from reviews, enabling targeted improvements.
* **Dashboard Performance:** Near real-time insights with caching and optimized queries.

---

## Quick Start

### 1. Environment Setup
```bash
# Clone the repo
git clone https://github.com/mekdelawitgebre/customer-experience-fintech
cd customer-experience-fintech

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
2. Database & Data Initialization

``` bash
# Create database schema
python - <<'PY'
from src.db.postgres import create_schema
create_schema()
PY
```

# Insert reviews into PostgreSQL
``` bash
python scripts/insert_reviews.py
3. Launch Dashboard
```
# Run the professional dashboard
streamlit run src/dashboard/app.py

---

# Project structure
``` plaintext
customer-experience-fintech/
├─ data/
│  └─ output/                  # CSV files with processed reviews
├─ scripts/
│  └─ insert_reviews.py        # Insert reviews into DB
├─ src/
│  ├─ config/
│  │  └─ config.py             # Project configuration & Path management
│  ├─ db/
│  │  ├─ postgres.py           # DB connection & Schema logic
│  ├─ dashboard/
│  │  └─ app.py                # Streamlit UI & Visualizations
├─ tests/                      # Unit tests (Pytest)
├─ requirements.txt            # Dependency list
└─ README.md                   # Documentation
```

---


## Technical Details
Data Sources: Google Play reviews

Preprocessing: Text cleaning, sentiment scoring, and theme extraction using regex and NLP.

Analysis & Modeling:

Sentiment classification: XLM-RoBERTa for multilingual support.

Thematic Analysis: MultiLabelBinarizer for feature-impact analysis.

KPIs: Average rating, sentiment strength, and Polarization Index.

Infrastructure: PostgreSQL (Neon) for storage, Pytest for CI/CD integrity.

---

## Future Improvements
Automate live ingestion from app stores and social media.

Temporal analysis for tracking trends over time.

Advanced NLP for aspect-based sentiment analysis (ABSA).

Cloud deployment for multi-user access via Docker.

## Author
Mekdelawit Gebre

LinkedIn: https://www.linkedin.com/in/mekdelawit-gebre-a4b037236/

Email: Megdela21@gmail.com
