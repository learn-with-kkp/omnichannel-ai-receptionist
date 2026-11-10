# 🎛️ Omnichannel Orchestrator (`omnichannel-orchestrator`)

[![PyPI version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Universal conversational dialogue state machine and microsecond latency tracker engineered for enterprise multi-tenant voice and chat receptionists.

## 🚀 Features

- **Microsecond Latency Waterfall Tracking**: Nimbus-inspired profiling measuring ASR, RAG, LLM TTFT, Tool Execution, and TTS playback.
- **Multi-Tenant State Management**: Instant vertical switching across Real Estate, Legal, Salon, Dental, Automotive, and Healthcare.
- **Intent & Sentiment Detection**: Sub-millisecond intent extraction (Booking, Availability Check, Reschedule, Cancellation, Escalation) with sentiment classification.
- **OpenTelemetry & Langfuse Observability**: Native tracing hooks for every conversational turn.

## 📦 Installation

```bash
pip install omnichannel-orchestrator
```

## 💻 Quick Usage

```python
from omnichannel_orchestrator import UniversalReceptionistOrchestrator

orchestrator = UniversalReceptionistOrchestrator()

result = orchestrator.process_conversation_turn(
    user_message="Can I book a haircut tomorrow at 2:00 PM?",
    session_id="session-user-123",
    tenant_id="salon",
    caller_phone="+16673070119",
    caller_name="Kishor"
)

print(result["reply"])
print(f"Total orchestration latency: {result['metrics']['total_orchestration_ms']} ms")
```
