# 🎙️ Omnichannel AI Voice & Chat Receptionist

> **Production-grade, sub-500ms conversational voice receptionist and appointment scheduling engine. Handles inbound PSTN calls, WebRTC in-browser audio, calendar bookings, and multi-channel confirmations 24/7 with zero hallucinations.**

---

[![Production Status](https://img.shields.io/badge/Production-Live-success?style=for-the-badge&logo=vercel)](https://ai-voice-receptionist.kishor.tech/)
[![Test Suite](https://img.shields.io/badge/Tests-78%2F78%20Passed%20(100%25)-brightgreen?style=for-the-badge&logo=pytest)](https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)
[![Database](https://img.shields.io/badge/Database-Neon%20PostgreSQL-336791?style=for-the-badge&logo=postgresql)](https://neon.tech/)
[![Voice Engine](https://img.shields.io/badge/Voice-Vapi%20%7C%20Cartesia%20Sonic--3.5-7952b3?style=for-the-badge)](https://vapi.ai/)
[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 🌐 Live Touchpoints

| Channel | Access / Endpoint | Experience |
| :--- | :--- | :--- |
| **Production Web App** | [ai-voice-receptionist.kishor.tech](https://ai-voice-receptionist.kishor.tech/) | Full multi-tenant dashboard, appointment manager & voice studio |
| **In-Browser WebRTC Studio** | [/vapi-call](https://ai-voice-receptionist.kishor.tech/vapi-call) | Direct real-time browser calling powered by `@vapi-ai/web` & Cartesia Sonic-3.5 |
| **PSTN Telephony Line** | `+1 (667) 307-0119` | Dedicated Vapi SIP/PSTN line with sub-500ms turnaround |
| **Outbound Voice Callback** | Web Studio $\rightarrow$ *Call Me* | Triggers Sofia to dial client phone directly via Twilio / Vapi REST API |

---

## ⚡ Core Capabilities

- **Sub-500ms Conversational Latency**: Deepgram Nova-2 speech-to-text (<180ms), FastAPI mid-call tool execution (<40ms), and Cartesia Sonic-3.5 text-to-speech (<110ms) provide instant, human-like voice conversations without awkward pauses.
- **Atomic Two-Way Calendar Booking**: Queries real-time open windows against Google Calendar and internal database, blocks conflicts, books appointments, and supports conversational rescheduling or cancellations.
- **Enterprise Multi-Tenancy**: Isolated business profiles, custom service menus, stylist schedules, and dedicated phone routing supported out of the box.
- **Neon Cloud PostgreSQL + SQLite Fallback**: Production runs on high-performance pooled Neon Serverless PostgreSQL with automatic query translation; local testing seamlessly runs isolated in SQLite.
- **Automated Omnichannel Confirmations**: Immediately dispatches SMS and WhatsApp appointment confirmations with cancellation/reschedule links, alongside automated 24-hour and 1-hour reminders.

---

## 🏛️ System Architecture

```mermaid
sequenceDiagram
    autonumber
    actor Caller as Client / Caller
    participant Vapi as Vapi Voice Platform
    participant STT as Deepgram Nova-2 (<180ms)
    participant API as FastAPI Backend Engine
    participant DB as Neon PostgreSQL / Google Calendar
    participant TTS as Cartesia Sonic-3.5 (<110ms)
    participant SMS as Twilio / WhatsApp Engine

    Caller->>Vapi: Audio Stream (PSTN or WebRTC)
    Vapi->>STT: Stream 16kHz PCM
    STT-->>Vapi: Live Interim & Final Transcript
    Vapi->>API: POST /webhook/vapi-tools (Mid-Call Tool Calling)
    
    rect rgb(240, 248, 255)
        API->>DB: Query Availability / Reserve Time Slot
        DB-->>API: Confirmed Slot & Booking Ref
    end

    API-->>Vapi: JSON Response { results: [...] }
    Vapi->>TTS: Stream Synthesis Text
    TTS-->>Vapi: 24kHz High-Fidelity Audio Buffer
    Vapi-->>Caller: Natural Voice Response (<500ms Turnaround)

    API->>SMS: Dispatch Instant SMS Confirmation + Reschedule Link
    SMS-->>Caller: Delivery Receipt
```

---

## 🛠️ Tech Stack

- **Voice & Telephony**: [Vapi](https://vapi.ai/) (Orchestration & WebRTC), [Cartesia](https://cartesia.ai/) (Sonic-3.5 Voice), [Deepgram](https://deepgram.com/) (Nova-2 STT), [Twilio](https://www.twilio.com/) (PSTN & SMS).
- **Backend & API**: Python 3.12, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic v2.
- **Database & Storage**: [Neon PostgreSQL](https://neon.tech/) (Serverless pooled driver) with fallback SQLite.
- **Calendar & Sync**: Google Calendar API (v3 OAuth2 & Service Accounts).
- **Frontend & Web SDK**: Modern responsive HTML5/Vanilla JS, `@vapi-ai/web` audio SDK.
- **Deployment**: Vercel Serverless (`λ api/index`), Docker, Cloudflare Tunnels.

---

## 🚀 Quick Start

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist.git
cd omnichannel-voice-chat-ai-receptionist

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` in the root directory:

```env
# Database
NEON_POSTGRES_CONNECTION_URL=postgresql://user:pass@ep-xyz-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

# Vapi Credentials
VAPI_PRIVATE_API_KEY=your_vapi_private_key
VAPI_PUBLIC_API_KEY=your_vapi_public_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id

# Google Calendar & Twilio (Optional)
GOOGLE_CALENDAR_ID=primary
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### 3. Run Locally

```bash
# Start FastAPI application
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000` to open the web portal, or `http://localhost:8000/vapi-call` to test in-browser voice calling.

---

## 🧪 Testing & Quality Assurance

The codebase includes comprehensive test suites covering multi-tenancy, mid-call tool execution, PostgreSQL connection pooling, and calendar synchronizations.

```bash
# Run full test suite
pytest tests/
```

```text
============================== 78 passed in 41.82s ==============================
```

> **🛡️ Branch Protection**: The `main` branch is safeguarded with an automated Git pre-push hook (`.githooks/pre-push`) that blocks direct force-pushes and automatically enforces passing tests before any code can be published.

---

## 🚢 Deployment

### Vercel Serverless
The project includes a root `vercel.json` and `api/index.py` configured for zero-downtime serverless deployment:
```bash
vercel --prod
```

### Docker
```bash
docker build -t ai-voice-receptionist .
docker run -p 8000:8000 --env-file .env ai-voice-receptionist
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
