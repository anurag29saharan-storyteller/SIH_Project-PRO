"""
Enterprise Multi-Provider LLM Engine supporting OpenAI, Anthropic Claude,
Local Ollama, and HuggingFace with automatic fallback to LocalEngine,
token cost tracking, and exponential backoff via tenacity.
"""
import json
import requests
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.engines.base import BaseEngine
from src.engines.local_engine import LocalEngine
from src.domain.schemas import AnalysisResultSchema, SeverityCategory
from src.domain.constants import HIGH_ENERGY_SOURCES
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger("llm_engine")

_SYSTEM_PROMPT = (
    "You are an expert Senior HSE (Health, Safety & Environment) Investigator and SIF (Serious Injury & Fatality) Prevention Specialist for Oil India Limited.\n"
    "Analyze the incident/near-miss report using the Campbell Institute / DuPont High-Energy & Control Barrier methodology.\n\n"
    "A Critical SIF Precursor requires:\n"
    "1. High-Energy Source present (e.g. Fall from height >1.8m, Heavy vehicle/crane, Fire/Explosion, Toxic H2S gas release, High-voltage electrical, Confined space, High pressure).\n"
    "2. Direct Control or Barrier was Absent, Failed, or Bypassed (e.g. No harness, bypassed interlock, no permit, unguarded machine).\n\n"
    "Return STRICT JSON only matching this exact schema:\n"
    "{\n"
    '  "category": "Critical SIF Precursor" | "Potential Precursor / Elevated Risk" | "Routine Safety Observation",\n'
    '  "score": <integer from 0 to 100 representing SIF severity potential>,\n'
    '  "matched_energy": [<list of matched high-energy source names from standard catalog>],\n'
    '  "matched_controls": [<list of specific control/barrier failures detected in text>],\n'
    '  "barrier_status": "FAILED" | "DEGRADED" | "INTACT",\n'
    '  "root_cause_hypothesis": "<concise 1-sentence technical hypothesis>",\n'
    '  "corrective_actions": [<list of 2 to 4 immediate actionable hierarchy-of-control steps>]\n'
    "}"
)


class LLMEngine(BaseEngine):
    def __init__(self, provider: str = "openai", model_name: Optional[str] = None):
        super().__init__(name=f"LLM Engine ({provider})")
        self.provider = provider.lower()
        self.config = get_config()
        self.local_engine = LocalEngine()
        self.model_name = model_name

    def _execute_analysis(self, text: str, **kwargs) -> AnalysisResultSchema:
        """Executes LLM inference with graceful fallback to LocalEngine on any error."""
        try:
            if self.provider == "openai":
                return self._call_openai(text)
            elif self.provider in ["anthropic", "claude"]:
                return self._call_anthropic(text)
            elif self.provider == "ollama":
                return self._call_ollama(text)
            elif self.provider in ["huggingface", "hf"]:
                return self._call_huggingface(text)
            else:
                logger.warning(f"Unknown LLM provider '{self.provider}'. Falling back to LocalEngine.")
                res = self.local_engine.analyze(text)
                res.used_fallback = True
                res.fallback_reason = f"Unknown provider: {self.provider}"
                return res
        except Exception as e:
            logger.error(f"LLM provider '{self.provider}' failed: {e}. Falling back to LocalEngine.")
            fallback_res = self.local_engine.analyze(text)
            fallback_res.engine_name = f"Local Engine ({self.provider} fallback)"
            fallback_res.used_fallback = True
            fallback_res.fallback_reason = str(e)
            return fallback_res

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
    def _call_openai(self, text: str) -> AnalysisResultSchema:
        api_key = self.config.get_api_key("openai")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured in .env or secrets.toml")

        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = self.model_name or self.config.openai_model

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Incident Report: {text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=600
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        total_tokens = prompt_tokens + completion_tokens

        cost_usd = (
            (prompt_tokens / 1_000_000.0) * self.config.openai_in_price +
            (completion_tokens / 1_000_000.0) * self.config.openai_out_price
        )

        return AnalysisResultSchema(
            category=SeverityCategory(data.get("category", "Potential Precursor / Elevated Risk")),
            score=int(data.get("score", 50)),
            matched_energy=data.get("matched_energy", []),
            matched_controls=data.get("matched_controls", []),
            corrective_actions=data.get("corrective_actions", []),
            engine_name=f"OpenAI ({model})",
            used_fallback=False,
            confidence=0.98,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=round(cost_usd, 6)
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6), reraise=True)
    def _call_anthropic(self, text: str) -> AnalysisResultSchema:
        api_key = self.config.get_api_key("anthropic")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured in .env or secrets.toml")

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        model = self.model_name or self.config.anthropic_model

        prompt = _SYSTEM_PROMPT + "\n\nIncident Report to analyze:\n" + text + "\n\nOutput only valid JSON:"
        response = client.messages.create(
            model=model,
            max_tokens=600,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        clean_json = content.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]

        data = json.loads(clean_json.strip())

        prompt_tokens = response.usage.input_tokens
        completion_tokens = response.usage.output_tokens
        total_tokens = prompt_tokens + completion_tokens

        cost_usd = (
            (prompt_tokens / 1_000_000.0) * self.config.anthropic_in_price +
            (completion_tokens / 1_000_000.0) * self.config.anthropic_out_price
        )

        return AnalysisResultSchema(
            category=SeverityCategory(data.get("category", "Potential Precursor / Elevated Risk")),
            score=int(data.get("score", 50)),
            matched_energy=data.get("matched_energy", []),
            matched_controls=data.get("matched_controls", []),
            corrective_actions=data.get("corrective_actions", []),
            engine_name=f"Anthropic ({model})",
            used_fallback=False,
            confidence=0.98,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=round(cost_usd, 6)
        )

    def _call_ollama(self, text: str) -> AnalysisResultSchema:
        base_url = self.config.ollama_base_url.rstrip("/")
        model = self.model_name or self.config.ollama_model

        payload = {
            "model": model,
            "prompt": _SYSTEM_PROMPT + "\n\nAnalyze this incident report:\n" + text + "\n\nJSON Output:",
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}
        }

        resp = requests.post(f"{base_url}/api/generate", json=payload, timeout=20)
        resp.raise_for_status()
        raw_res = resp.json()
        data = json.loads(raw_res.get("response", "{}"))

        return AnalysisResultSchema(
            category=SeverityCategory(data.get("category", "Potential Precursor / Elevated Risk")),
            score=int(data.get("score", 50)),
            matched_energy=data.get("matched_energy", []),
            matched_controls=data.get("matched_controls", []),
            corrective_actions=data.get("corrective_actions", []),
            engine_name=f"Ollama Local ({model})",
            used_fallback=False,
            confidence=0.94,
            prompt_tokens=raw_res.get("prompt_eval_count", 0),
            completion_tokens=raw_res.get("eval_count", 0),
            total_tokens=raw_res.get("prompt_eval_count", 0) + raw_res.get("eval_count", 0),
            cost_usd=0.0
        )

    def _call_huggingface(self, text: str) -> AnalysisResultSchema:
        api_url = self.config.hf_model_url
        token = self.config.get_api_key("huggingface")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": [
                    "Critical SIF Precursor",
                    "Potential Precursor / Elevated Risk",
                    "Routine Safety Observation"
                ]
            }
        }
        resp = requests.post(api_url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        res_data = resp.json()
        
        if "labels" not in res_data:
            raise ValueError(f"Unexpected HuggingFace response format: {res_data}")

        cat_str = res_data["labels"][0]
        score = int(res_data["scores"][0] * 100)

        # Enhance with local keyword extraction
        _, _, matched_e, matched_c, actions = self.local_engine._execute_analysis(text).model_dump().values()

        return AnalysisResultSchema(
            category=SeverityCategory(cat_str),
            score=score,
            matched_energy=matched_e,
            matched_controls=matched_c,
            corrective_actions=actions,
            engine_name="HuggingFace Zero-Shot",
            used_fallback=False,
            confidence=round(float(res_data["scores"][0]), 2)
        )
