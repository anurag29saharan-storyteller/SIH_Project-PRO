"""
Abstract Base Class for all SIF detection and NLP analysis engines.
"""
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.domain.schemas import AnalysisResultSchema
from src.utils.logger import get_logger

logger = get_logger("base_engine")


class BaseEngine(ABC):
    def __init__(self, name: str = "BaseEngine"):
        self.name = name

    @abstractmethod
    def _execute_analysis(self, text: str, **kwargs) -> AnalysisResultSchema:
        """Subclasses must implement actual inference logic."""
        pass

    def analyze(self, text: str, **kwargs) -> AnalysisResultSchema:
        """Wraps inference in execution timers and standardized error handlers."""
        start_time = time.perf_counter()
        try:
            result = self._execute_analysis(text, **kwargs)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            result.latency_ms = round(latency_ms, 2)
            result.text = text
            return result
        except Exception as e:
            logger.exception(f"Error during analysis in engine {self.name}: {e}")
            raise

    def batch_analyze(self, texts: List[str], **kwargs) -> List[AnalysisResultSchema]:
        """Batch analysis wrapper over sequential or parallel items."""
        results = []
        for text in texts:
            results.append(self.analyze(text, **kwargs))
        return results
