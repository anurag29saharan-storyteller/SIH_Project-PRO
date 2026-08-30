"""
Deterministic rule-based SIF NLP engine.
Zero-latency, 100% offline, multilingual English & Hindi heuristic matching.
"""
from src.engines.base import BaseEngine
from src.domain.schemas import AnalysisResultSchema, SeverityCategory
from src.domain.rules import calculate_rule_based_sif


class LocalEngine(BaseEngine):
    def __init__(self):
        super().__init__(name="Local Rule Engine")

    def _execute_analysis(self, text: str, **kwargs) -> AnalysisResultSchema:
        cat_str, score, matched_e, matched_c, actions = calculate_rule_based_sif(text)
        
        category = SeverityCategory(cat_str)
        confidence = 0.92 if matched_e and matched_c else 0.85

        return AnalysisResultSchema(
            category=category,
            score=score,
            matched_energy=matched_e,
            matched_controls=matched_c,
            corrective_actions=actions,
            engine_name="Local Rule Engine",
            used_fallback=False,
            confidence=confidence,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost_usd=0.0
        )
