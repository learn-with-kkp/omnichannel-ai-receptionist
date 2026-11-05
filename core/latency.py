"""
Canonical Microsecond Latency Collector.
Inspired by Nimbus Voice Agent architecture.
Tracks per-stage pipeline execution:
- asr_ms: Automatic Speech Recognition (STT)
- rag_ms: Knowledge Retrieval / Context Assembly
- llm_ttft_ms: LLM Time To First Token
- llm_total_ms: Total LLM completion generation
- tool_ms: Tool execution (Google Calendar, DB mutation, Excel)
- tts_ms: Text-to-Speech synthesis
- buffer_ms: Audio buffering & network transport
- total_ms: End-to-end voice loop latency
"""

from __future__ import annotations
import time
from typing import Dict
from contextlib import contextmanager

STAGES = (
    "asr",
    "rag",
    "llm_ttft",
    "llm_total",
    "tool",
    "tts",
    "buffer",
)


class LatencyTracker:
    """Immutable per-request stage latency recorder."""

    def __init__(self) -> None:
        self._ms: Dict[str, float] = {}

    @contextmanager
    def stage(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000.0
            self.add(name, elapsed)

    def add(self, name: str, ms: float) -> None:
        self._ms[name] = round(self._ms.get(name, 0.0) + ms, 2)

    def as_dict(self) -> Dict[str, float]:
        out = {f"{name}_ms": self._ms.get(name, 0.0) for name in STAGES}
        # Total excludes llm_ttft as it is a sub-measure of llm_total
        total = sum(v for k, v in self._ms.items() if k != "llm_ttft")
        out["total_ms"] = round(total, 2)
        return out
