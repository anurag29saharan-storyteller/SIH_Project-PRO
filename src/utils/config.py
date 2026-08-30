"""
Configuration loader merging config.yaml, environment variables (.env),
and Streamlit secrets into a centralized typed configuration dataclass.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

# Load .env if present
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"


class AppConfig:
    def __init__(self, raw_cfg: Dict[str, Any]):
        self.raw = raw_cfg
        
        # App
        app = raw_cfg.get("app", {})
        self.app_name = app.get("name", "SIF AI Dashboard")
        self.organization = app.get("organization", "Oil India Limited")
        self.version = app.get("version", "2.0.0 Enterprise")
        self.default_theme = app.get("default_theme", "dark")
        self.default_engine = app.get("default_engine", "local")

        # Security
        sec = raw_cfg.get("security", {})
        self.auth_enabled = sec.get("auth_enabled", False)
        self.default_pin = os.getenv("APP_SECURITY_PIN", str(sec.get("default_pin", "1959")))

        # Database
        db = raw_cfg.get("database", {})
        self.database_url = os.getenv("DATABASE_URL", db.get("url", "sqlite:///data/sif_dashboard.db"))

        # LLM Pricing & Models
        llm = raw_cfg.get("llm", {})
        self.openai_model = llm.get("openai", {}).get("default_model", "gpt-4o-mini")
        self.openai_in_price = llm.get("openai", {}).get("pricing", {}).get("input_per_million", 0.15)
        self.openai_out_price = llm.get("openai", {}).get("pricing", {}).get("output_per_million", 0.60)

        self.anthropic_model = llm.get("anthropic", {}).get("default_model", "claude-3-haiku-20240307")
        self.anthropic_in_price = llm.get("anthropic", {}).get("pricing", {}).get("input_per_million", 0.25)
        self.anthropic_out_price = llm.get("anthropic", {}).get("pricing", {}).get("output_per_million", 1.25)

        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", llm.get("ollama", {}).get("base_url", "http://localhost:11434"))
        self.ollama_model = llm.get("ollama", {}).get("default_model", "llama3")

        self.hf_model_url = llm.get("huggingface", {}).get("model_url", "https://api-inference.huggingface.co/models/facebook/bart-large-mnli")

        # API Keys from env or secrets
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.hf_api_token = os.getenv("HF_API_TOKEN")

    def get_api_key(self, provider: str) -> Optional[str]:
        """Helper to fetch keys with Streamlit secrets fallback."""
        try:
            import streamlit as st
            if provider == "openai":
                return self.openai_api_key or st.secrets.get("OPENAI_API_KEY", None)
            elif provider == "anthropic":
                return self.anthropic_api_key or st.secrets.get("ANTHROPIC_API_KEY", None)
            elif provider == "huggingface":
                return self.hf_api_token or st.secrets.get("HF_API_TOKEN", None)
        except Exception:
            pass

        if provider == "openai":
            return self.openai_api_key
        elif provider == "anthropic":
            return self.anthropic_api_key
        elif provider == "huggingface":
            return self.hf_api_token
        return None


_cached_config = None


def get_config() -> AppConfig:
    """Singleton accessor for AppConfig."""
    global _cached_config
    if _cached_config is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        else:
            raw = {}
        _cached_config = AppConfig(raw)
    return _cached_config
