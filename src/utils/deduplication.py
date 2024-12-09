# src/utils/deduplication.py
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticContentCleaner:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def remove_semantic_duplicates(self, sections, similarity_threshold=0.85):
        if not sections:
            return sections

        texts = [s['content'] for s in sections]
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        keep_indices = []
        for i in range(len(embeddings)):
            if not keep_indices:
                keep_indices.append(i)
                continue
            keep_embs = embeddings[keep_indices]
            sim_scores = np.dot(keep_embs, embeddings[i]) / (np.linalg.norm(keep_embs, axis=1)*np.linalg.norm(embeddings[i]))
            if np.max(sim_scores) < similarity_threshold:
                keep_indices.append(i)

        return [sections[i] for i in keep_indices]
