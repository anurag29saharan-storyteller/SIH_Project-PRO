# ??? SIF Precursor AI Intelligence Platform ? Oil India Limited

An enterprise-grade, production-ready AI/NLP platform engineered for **Serious Injury & Fatality (SIF)** precursor detection in unsafe acts, unsafe conditions, and near-miss reports. Built on the **Campbell Institute** and **DuPont SIF Prevention Methodology**.

---

## ?? Key Architectural Features

1. **Modular Enterprise Architecture**:
   - `app.py`: Streamlined entrypoint with PIN authentication, dark/light theme toggle, and tab routing.
   - `src/domain/`: Domain constants (12 High-Energy Sources, 35+ Barrier Failures), Pydantic schemas, and Campbell Institute decision rules.
   - `src/database/`: Persistent SQLite/PostgreSQL layer using SQLAlchemy 2.0 with WAL-mode concurrency.
   - `src/engines/`:
     - `LocalEngine`: Zero-latency, deterministic, multilingual (English + Hindi) rule engine.
     - `LLMEngine`: Multi-provider LLM orchestrator supporting OpenAI (`gpt-4o-mini`), Anthropic Claude (`3 Haiku`), Local Ollama (`llama3`), and HuggingFace with exponential backoff retries (`tenacity`) and automated token cost tracking.
     - `SemanticSearchEngine`: Embedding similarity search (`sentence-transformers` + TF-IDF fallback) to surface matching historical near-misses when typing new reports.
     - `TrendForecastingEngine`: Time-series predictive risk model (Prophet / ARIMA / Holt-Winters) forecasting 14-day forward risk trajectories.
   - `src/utils/`: Rotating file logger (`logs/sif_app.log`), input sanitization, security helpers, and executive PDF generation (`ReportLab`).
   - `src/ui/`: Glassmorphic Dark/Light CSS themes, Plotly indicator gauges, factor waterfalls, and Folium geospatial risk heatmaps.

---

## ?? Project Structure

```
sif_dashboard/
??? app.py                      # Main application entrypoint
??? config.yaml                 # Tunable hazard weights, models, locations, pricing
??? requirements.txt            # Enterprise pinned dependencies
??? .env.example                # Environment variable template
??? .streamlit/
?   ??? config.toml             # Streamlit server and theme configuration
?   ??? secrets.toml.example    # Streamlit secrets template
??? data/
?   ??? sif_dashboard.db        # Persistent SQLite database
??? logs/
?   ??? sif_app.log             # Rotating application logs
??? src/
?   ??? domain/                 # Domain logic, models, constants, and schemas
?   ??? database/               # SQLAlchemy session, migrations, repository CRUD
?   ??? engines/                # Local, LLM, Semantic Search, and Forecasting engines
?   ??? utils/                  # Logger, security, config loader, PDF exporter
?   ??? ui/                     # CSS themes, charts, maps, and page views
??? README.md
```

---

## ?? Quickstart & Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional for Cloud AI)
Copy `.env.example` to `.env` (or configure `.streamlit/secrets.toml`):
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HF_API_TOKEN=hf_...
APP_SECURITY_PIN=1959
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

---

## ??? SIF Methodology Summary

A report is classified as a **Critical SIF Precursor** if:
1. **High-Energy Source Present:** Gravitational (fall > 1.8m), kinetic (moving plant/vehicle), chemical (H2S gas), electrical, pressure, or thermal energy.
2. **Direct Barrier Compromised:** Missing safety harness, bypassed interlock, lack of Permit-To-Work (PTW), or absent ventilation.
