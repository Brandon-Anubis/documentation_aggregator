# src/utils/deduplication.py
import logging
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except Exception as import_err:
    # Handle cases where sentence-transformers (and its heavy deps) are not installed
    # or cannot be imported due to binary incompatibilities. We mark the library as
    # unavailable so that downstream code can gracefully degrade.
    SentenceTransformer = None
    logger.warning(
        "SentenceTransformer unavailable or failed to load: %s. Semantic duplicate removal will be skipped.",
        import_err,
    )

import numpy as np

class SemanticContentCleaner:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Attempt to load the embedding model only if SentenceTransformer imported successfully
        if SentenceTransformer is None:
            self.model = None
        else:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                logger.warning(
                    "Failed to load SentenceTransformer model '%s': %s. Semantic duplicate removal disabled.",
                    model_name,
                    e,
                )
                self.model = None

    def remove_semantic_duplicates(self, sections, similarity_threshold: float = 0.85):
        """Remove semantically duplicate sections using cosine similarity.

        If the embedding model is unavailable, returns the sections unchanged.
        """
        if not sections or self.model is None:
            return sections

        texts = [s["content"] for s in sections]
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        keep_indices = []
        for i in range(len(embeddings)):
            if not keep_indices:
                keep_indices.append(i)
                continue
            keep_embs = embeddings[keep_indices]
            sim_scores = np.dot(keep_embs, embeddings[i]) / (
                np.linalg.norm(keep_embs, axis=1) * np.linalg.norm(embeddings[i])
            )
            if np.max(sim_scores) < similarity_threshold:
                keep_indices.append(i)

        return [sections[i] for i in keep_indices]
