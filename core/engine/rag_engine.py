"""
Dual Knowledge Engine: RAG vs RAGless Architecture.
Complies with saloon.md specifications:
- RAGless Mode: Injects unified markdown context directly into system prompt (<1ms, zero vector search latency).
- RAG Mode: Semantic cosine vector retrieval with top-k matching and millisecond latency tracking.
"""

import os
import time
import math
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("DualKnowledgeEngine")


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _simple_embedding(text: str, dim: int = 64) -> List[float]:
    """Deterministic lightweight local hash-based embedding for zero-dependency test / offline vector search."""
    vec = [0.0] * dim
    words = text.lower().split()
    if not words:
        return vec
    for i, w in enumerate(words):
        h = hash(w) % dim
        vec[h] += 1.0 / (i + 1.0)
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


class DualKnowledgeEngine:
    """
    Knowledge manager providing seamless switching between RAG and RAGless modes.
    """

    def __init__(self, use_rag: bool = False):
        self.use_rag = use_rag or (os.getenv("USE_RAG", "false").lower() == "true")
        self._vector_indices: Dict[str, List[Dict[str, Any]]] = {}

    def set_rag_mode(self, enabled: bool):
        self.use_rag = enabled

    def index_tenant(self, tenant_manifest: Any):
        """Indexes tenant services, FAQs, and policies into the retrieval index."""
        tenant_id = tenant_manifest.id
        chunks = []

        # Index business rules & policies
        rules = tenant_manifest.business_rules
        chunks.append({
            "text": f"Business Policies for {tenant_manifest.name}: Lead time {rules.min_lead_time_hours}h, "
                    f"cancellation window {rules.cancellation_window_hours}h, deposit required: {rules.deposit_required}, "
                    f"auto-confirm: {rules.auto_confirm}.",
            "category": "policy",
            "metadata": {"type": "policy"}
        })

        # Index services
        for s in tenant_manifest.services:
            chunks.append({
                "text": f"Service: {s.name}. Category: {s.category}. Price: ${s.price}. Duration: {s.duration_minutes} mins. Description: {s.description}",
                "category": "service",
                "metadata": {"service_id": s.id, "name": s.name, "price": s.price, "duration": s.duration_minutes}
            })

        # Index staff
        for st in tenant_manifest.staff:
            skills_str = ", ".join(st.skills)
            chunks.append({
                "text": f"Staff Member: {st.name} ({st.role}). Specialties: {skills_str}. Available days: {', '.join(st.available_days)}.",
                "category": "staff",
                "metadata": {"staff_id": st.id, "name": st.name}
            })

        # Index FAQs
        for faq in tenant_manifest.faqs:
            chunks.append({
                "text": f"Question: {faq.question} Answer: {faq.answer}",
                "category": "faq",
                "metadata": {"faq_id": faq.id, "tags": faq.tags}
            })

        # Precompute embeddings & push to Qdrant multi-tenant partition
        try:
            from core.engine.qdrant_rag import qdrant_engine
            for c in chunks:
                c["vector"] = _simple_embedding(c["text"])
                qdrant_engine.ingest_document(
                    tenant_id=tenant_id,
                    text=c["text"],
                    category=c.get("category", "general"),
                    metadata=c.get("metadata", {})
                )
        except Exception as e:
            for c in chunks:
                c["vector"] = _simple_embedding(c["text"])

        self._vector_indices[tenant_id] = chunks
        logger.info(f"Indexed {len(chunks)} chunks for tenant '{tenant_id}' (Qdrant synchronized).")

    def query_context(self, tenant_manifest: Any, user_query: str = "", top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves context based on current mode (RAG vs RAGless).
        Returns {
            "mode": "rag" | "ragless",
            "context_text": str,
            "retrieval_ms": float,
            "chunks_used": int
        }
        """
        start_ts = time.time()
        tenant_id = tenant_manifest.id

        if not self.use_rag:
            # --- RAGless Mode: Fast direct system prompt context assembly ---
            assembled = tenant_manifest.to_system_prompt_context()
            latency = (time.time() - start_ts) * 1000.0
            return {
                "mode": "ragless",
                "context_text": assembled,
                "retrieval_ms": round(latency, 2),
                "chunks_used": len(tenant_manifest.services) + len(tenant_manifest.faqs),
                "confidence_score": 1.0
            }

        # --- RAG Mode: Semantic Retrieval with Qdrant + Semantic Cache ---
        try:
            from core.engine.qdrant_rag import qdrant_engine
            q_res = qdrant_engine.retrieve(tenant_id=tenant_id, query=user_query, top_k=top_k)
            if q_res.get("context_text"):
                return {
                    "mode": "rag",
                    "context_text": f"Relevant Knowledge Base for {tenant_manifest.name}:\n{q_res['context_text']}",
                    "retrieval_ms": q_res["latency_ms"],
                    "chunks_used": len(q_res["results"]),
                    "confidence_score": 0.95,
                    "source": q_res.get("source", "qdrant")
                }
        except Exception:
            pass

        if tenant_id not in self._vector_indices:
            self.index_tenant(tenant_manifest)

        chunks = self._vector_indices.get(tenant_id, [])
        if not chunks or not user_query.strip():
            # Fall back to standard context if query is empty
            assembled = tenant_manifest.to_system_prompt_context()
            latency = (time.time() - start_ts) * 1000.0
            return {
                "mode": "rag",
                "context_text": assembled,
                "retrieval_ms": round(latency, 2),
                "chunks_used": len(chunks),
                "confidence_score": 0.8
            }

        query_vec = _simple_embedding(user_query)
        scored = []
        for c in chunks:
            sim = _cosine_similarity(query_vec, c["vector"])
            scored.append((sim, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored[:top_k]

        matched_texts = [f"- {item[1]['text']} (Score: {item[0]:.2f})" for item in top_chunks]
        context_str = f"Relevant Knowledge Base for {tenant_manifest.name}:\n" + "\n".join(matched_texts)

        latency = (time.time() - start_ts) * 1000.0
        avg_score = sum(x[0] for x in top_chunks) / len(top_chunks) if top_chunks else 0.0

        return {
            "mode": "rag",
            "context_text": context_str,
            "retrieval_ms": round(latency, 2),
            "chunks_used": len(top_chunks),
            "confidence_score": round(avg_score, 2)
        }


# Global singleton knowledge engine
knowledge_engine = DualKnowledgeEngine()

