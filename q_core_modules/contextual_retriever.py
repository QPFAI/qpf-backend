#!/usr/bin/env python3
"""
contextual_retriever.py

Provides semantic retrieval over the MemoryGraph using configurable embedding
models, an LRU cache for speed, and batch‐mode retrieval.
"""

from typing import Callable, List, Optional, Any
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from q_core_modules.memory_graph import MemoryGraph, MemoryEvent

class ContextualRetriever:
    """
    Given a MemoryGraph, retrieves the most relevant past events for a query
    using semantic embeddings.
    """

    def __init__(
        self,
        memory_graph: MemoryGraph,
        embedder: Optional[Callable[[str], Any]] = None
    ):
        """
        Args:
            memory_graph: the MemoryGraph to search.
            embedder: a function text→vector. Defaults to
                      SentenceTransformer('all-MiniLM-L6-v2').encode
        """
        self.memory_graph = memory_graph
        # default embedder
        model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedder = embedder or model.encode

    @lru_cache(maxsize=128)
    def retrieve_semantic(self, text: str, k: int) -> List[MemoryEvent]:
        """
        Return the top-k MemoryEvent objects whose payload text is most
        semantically similar to `text`.
        Caches the last 128 distinct queries for speed.
        """
        # 1) Get embedding for the query
        query_vec = np.array(self.embedder(text))
        # 2) Compute embeddings for all candidates
        candidates = list(self.memory_graph.graph.nodes(data=True))
        event_ids, events = zip(*[(nid, d["event"]) for nid, d in candidates])
        texts = []
        for ev in events:
            # assume payload has a 'text' key, else fallback to string
            txt = ev.payload.get("text")
            texts.append(txt if isinstance(txt, str) else str(ev.payload))
        embeddings = np.array(self.embedder(texts))

        # 3) Compute cosine similarities
        # handle zero‐vectors safely
        dot = embeddings @ query_vec
        norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
        sims = np.divide(dot, norms, out=np.zeros_like(dot), where=norms!=0)

        # 4) Select top‐k
        idx = np.argsort(sims)[-k:][::-1]
        return [events[i] for i in idx]

    def retrieve_semantic_batch(self, texts: List[str], k: int) -> List[List[MemoryEvent]]:
        """
        Bulk version: apply retrieve_semantic to each text in `texts`.
        """
        return [self.retrieve_semantic(text, k) for text in texts]
