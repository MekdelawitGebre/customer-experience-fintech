import sys
import os
import json
import time
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import MultiLabelBinarizer
from sqlalchemy.exc import SQLAlchemyError, PendingRollbackError

#SYSTEM CONFIGURATION

current_file = Path(__file__).resolve()
project_root = current_file.parents[2] 
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.db import postgres
except ImportError:
    st.error("🚨 Configuration Error: Ensure 'src' is in project root.")
    st.stop()

# ---------------------------------------------------------
# 2. UI STYLING & CENTERED LOADING
# ---------------------------------------------------------
st.set_page_config(page_title="Fintech Intelligence Hub", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    /* Centered Loading */
    .loader-container {
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; height: 70vh;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.7; }
        50% { transform: scale(1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.7; }
    }
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
        color: #38bdf8; font-size: 1.5rem; font-weight: 700;
    }

    /* Metric Cards */
    .metric-card {
        padding: 1.5rem; border-radius: 12px; border: 1px solid #1e293b;
        background-color: #1e293b; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Global Text */
    h1, h2, h3, p, span, label { color: #f8fafc !important; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #334155; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }
    
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# DATA ENGINE
@st.cache_data(ttl=300, show_spinner=False)
def fetch_production_data():
    try:
        df = postgres.get_all_reviews()
    except (PendingRollbackError, SQLAlchemyError):
        if hasattr(postgres, 'session'): postgres.session.rollback()
        df = postgres.get_all_reviews()
    
    if df.empty: return df

    s_col = next((c for c in ['sentiment_score', 'score'] if c in df.columns), df.columns[0])
    df['std_score'] = pd.to_numeric(df[s_col], errors='coerce').fillna(0)
    df['themes'] = df['themes'].apply(lambda x: json.loads(x) if isinstance(x, str) and x.startswith('[') else (x if isinstance(x, list) else []))
    return df

# Initialize Session State
if 'loaded' not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    center_load = st.empty()
    center_load.markdown("""
        <div class="loader-container">
            <div class="loading-pulse">Loading...</div>
            <div style="color: #64748b; margin-top: 10px;">Establishing Real-Time Postgres Link</div>
        </div>
    """, unsafe_allow_html=True)
    df_raw = fetch_production_data()
    time.sleep(1.2)
    st.session_state.loaded = True
    center_load.empty()
else:
    df_raw = fetch_production_data()


# 4. SIDEBAR & KPI

with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8;'> Bank</h2>", unsafe_allow_html=True)
    banks = sorted(df_raw['bank'].unique().tolist())
    selected_banks = st.multiselect("Benchmark Banks", banks, default=banks)

filtered_df = df_raw.loc[df_raw['bank'].isin(selected_banks)].reset_index(drop=True)

st.markdown("<h1 style='text-align: center; color:#38bdf8;'>Fintech Market Intelligence Hub</h1>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

vol = len(filtered_df)
rating = filtered_df['rating'].mean() if vol > 0 else 0
pos = (len(filtered_df[filtered_df['sentiment_label'] == 'POSITIVE']) / vol * 100) if vol > 0 else 0

def get_polar(sub):
    ones = len(sub[sub['rating'] == 1])
    fives = len(sub[sub['rating'] == 5])
    return abs(fives - ones) / len(sub) if len(sub) > 0 else 0

k1.metric("Market Volume", f"{vol:,}")
k2.metric("Avg Rating", f"{rating:.2f}")

with k3:
    s_col = "#ef4444" if pos < 40 else ("#f59e0b" if pos < 70 else "#22c55e")
    st.markdown(f"""
        <div class="metric-card" style="border-top:5px solid {s_col}">
            <p style="color:{s_col}; font-size:0.8rem; font-weight:bold; margin:0">SENTIMENT STRENGTH</p>
            <p style="color:{s_col}; font-size:1.8rem; font-weight:800; margin:0">{pos:.1f}%</p>
        </div>
    """, unsafe_allow_html=True)

k4.metric("Polarization Index", f"{get_polar(filtered_df):.2f}")

st.divider()


# 5. CORE ANALYSIS TABS
tab_bench, tab_dist, tab_shap = st.tabs(["Benchmarking", " Rating Profiles", " Driver Analysis"])

# Professional White Background for Charts
light_chart_theme = "plotly_white"

with tab_bench:
    st.subheader("Market Sentiment Distribution")
    sent_data = filtered_df.groupby(['bank', 'sentiment_label']).size().reset_index(name='count')
    fig_bench = px.bar(sent_data, x='bank', y='count', color='sentiment_label',
                       barmode='group', text_auto='.2s', template=light_chart_theme,
                       color_discrete_map={'POSITIVE': '#22c55e', 'NEUTRAL': '#64748b', 'NEGATIVE': '#ef4444'})
    st.plotly_chart(fig_bench, use_container_width=True)

with tab_dist:
    st.subheader("Comparative Rating Distribution")
    st.markdown("White-background visualization for maximum clarity on star distribution.")
    
    fig_dist = px.histogram(filtered_df, x="rating", color="bank", barmode="group",
                            nbins=5, template=light_chart_theme, 
                            color_discrete_sequence=px.colors.qualitative.Safe)
    fig_dist.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1), bargap=0.1)
    st.plotly_chart(fig_dist, use_container_width=True)

with tab_shap:
    st.subheader("Theme Drivers")
    st.markdown("Analysis of feature impact on overall sentiment scores.")
    if not filtered_df.empty and 'themes' in filtered_df.columns:
        mlb = MultiLabelBinarizer()
        X = pd.DataFrame(mlb.fit_transform(filtered_df['themes']), columns=mlb.classes_)
        shap_metrics = []
        for theme in mlb.classes_:
            mask = X[theme] == 1
            shap_metrics.append({'Theme': theme, 'Impact': filtered_df.loc[mask, 'std_score'].mean(), 'Volume': mask.sum()})
        
        shap_df = pd.DataFrame(shap_metrics).sort_values('Impact', ascending=False)
        
        fig_shap = px.bar(shap_df, x='Impact', y='Theme', orientation='h',
                          color='Impact', color_continuous_scale='RdYlGn', template=light_chart_theme)
        fig_shap.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_shap, use_container_width=True)

st.divider()
with st.expander(" Audit Trail: Raw Transactional Data"):
    st.dataframe(filtered_df[['bank', 'review_text', 'rating', 'sentiment_label', 'themes']], use_container_width=True)