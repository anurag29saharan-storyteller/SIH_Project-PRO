"""
Semantic Similarity Search Engine for historical SIF incident discovery.
Uses Sentence-Transformers with graceful fallback to TF-IDF & Cosine Similarity.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.domain.schemas import SimilarReportSchema
from src.utils.logger import get_logger

logger = get_logger("semantic_engine")


class SemanticSearchEngine:
    def __init__(self):
        self._model = None
        self._is_transformer_ready = False
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None
        self._corpus_records: List[Dict[str, Any]] = []

    def _init_transformer(self):
        """Lazy loads sentence_transformers model."""
        if self._model is None and not self._is_transformer_ready:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                self._is_transformer_ready = True
                logger.info("SentenceTransformer 'all-MiniLM-L6-v2' successfully initialized.")
            except Exception as e:
                logger.warning(f"SentenceTransformers unavailable ({e}). Using TF-IDF vectorizer fallback.")
                self._is_transformer_ready = False

    def index_reports(self, reports: List[Dict[str, Any]]):
        """Indexes a list of historical report dictionaries."""
        self._corpus_records = reports
        if not reports:
            return

        texts = [r.get("narrative", "") or r.get("Narrative", "") for r in reports]
        
        # Always build TF-IDF index as immediate fallback
        self._tfidf_vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(texts)

    def find_similar(self, query_text: str, top_k: int = 4) -> List[SimilarReportSchema]:
        """Finds top-K most semantically similar past incident reports."""
        if not query_text or not self._corpus_records:
            return []

        try:
            self._init_transformer()
            if self._is_transformer_ready and self._model is not None:
                texts = [r.get("narrative", "") or r.get("Narrative", "") for r in self._corpus_records]
                corpus_embeddings = self._model.encode(texts, convert_to_numpy=True)
                query_embedding = self._model.encode([query_text], convert_to_numpy=True)
                sim_scores = cosine_similarity(query_embedding, corpus_embeddings)[0]
            else:
                # TF-IDF Cosine Similarity Fallback
                if self._tfidf_vectorizer is None or self._tfidf_matrix is None:
                    return []
                query_vec = self._tfidf_vectorizer.transform([query_text])
                sim_scores = cosine_similarity(query_vec, self._tfidf_matrix)[0]

            top_indices = np.argsort(sim_scores)[::-1][:top_k]
            matches = []

            for idx in top_indices:
                score_val = float(sim_scores[idx])
                if score_val < 0.10:  # Threshold for relevance
                    continue
                rec = self._corpus_records[idx]
                narr = rec.get("narrative", "") or rec.get("Narrative", "")
                snippet = (narr[:110] + "...") if len(narr) > 110 else narr
                
                matches.append(SimilarReportSchema(
                    report_id=rec.get("id") or rec.get("Report_ID", idx + 1),
                    location=rec.get("location") or rec.get("Location", "Unknown"),
                    category=rec.get("category") or rec.get("Category", "Observation"),
                    score=int(rec.get("score") or rec.get("Risk_Score", 0)),
                    snippet=snippet,
                    similarity_score=round(score_val * 100.0, 1)
                ))
            return matches

        except Exception as e:
            logger.error(f"Error executing semantic search: {e}")
            return []
