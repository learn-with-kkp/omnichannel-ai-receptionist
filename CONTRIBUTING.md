# Contributing to Omnichannel AI Voice Receptionist

Thank you for your interest in contributing to the **Omnichannel AI Voice Receptionist** platform!

We follow **Principal Engineer Rigor** and the **Enterprise AI Architect Roadmap (Phases 0–5)**. Please review these guidelines before submitting a pull request.

---

## 🛠️ Development Workflow

### 1. Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ (for Web SDK components)
- Docker & Docker Compose (optional for local PostgreSQL / Qdrant)

### 2. Local Setup
```bash
# Clone the repository
git clone https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist.git
cd omnichannel-voice-chat-ai-receptionist

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and local packages
pip install -r requirements.txt
pip install -e .

# Copy environment variables
cp .env.example .env
```

### 3. Running the Test Suite
All PRs must maintain 100% test pass rate across the 78 unit & integration tests:
```bash
PYTHONPATH=. pytest tests/ -v
```

### 4. Running the Development Server
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📐 Architecture Standards

1. **Sub-500ms Conversational Latency**: Avoid introducing blocking network calls on conversational voice paths. Use asynchronous tasks or background workers.
2. **Cultural & Dialect Integrity**: Regional talking styles must be delivered through acoustic timbre (TTS voice parameters) rather than stereotypical text caricatures.
3. **Observability**: Instrument new conversational turns or tools with Langfuse `@observe()` or OpenTelemetry spans.

---

## 🤝 Code of Conduct & Pull Requests

- Use conventional commits: `feat:`, `fix:`, `perf:`, `docs:`, `test:`, `chore:`.
- Link related GitHub issues in your PR description.
- Ensure all CI checks pass.
