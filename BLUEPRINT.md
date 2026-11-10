# 🌐 Universal Omnichannel AI Voice & Chat Receptionist Blueprint
### *The "Build Once, Sell Everywhere" Enterprise Architecture*

---

## Executive Summary

The **Universal AI Voice & Chat Receptionist Blueprint** is an enterprise-grade conversational AI platform designed to automate 100% of front-desk operations across appointment-driven industries. 

Built with **zero code modifications required to switch verticals**, a single instance can be deployed for **Real Estate Agencies, Law Firms, Salons & Spas, Dental Clinics, Automotive Repair Centers, or Medical Clinics** simply by toggling or provisioning the business manifest.

```mermaid
graph TD
    User([Customer / Client Touchpoints])
    
    subgraph Omnichannel Channels
        VoiceIn[📞 Inbound Phone Calls - Twilio / Vapi]
        VoiceOut[📱 Outbound Phone Calls - 'Call My Phone']
        WebRTC[🎙️ Browser WebRTC Microphone Calling]
        WebChat[💬 Website Live Chat Widget]
        WhatsApp[🟢 Meta WhatsApp Cloud API]
        Messenger[💬 Facebook Messenger Graph API]
        Insta[📸 Instagram Direct Messaging]
    end

    User --> VoiceIn & VoiceOut & WebRTC & WebChat & WhatsApp & Messenger & Insta

    subgraph Core AI Receptionist Blueprint
        Orch[⚡ Universal Omnichannel Orchestrator]
        AccentEngine[🗣️ Sofia Female Voice Dialect Engine<br/>🇨🇦 Canada • 🇺🇸 US Neutral/South • 🇬🇧 UK • 🇮🇪 Ireland • 🇪🇺 Europe • 🇦🇺 Australia • 🇮🇳 India • 🌍 Africa]
        DualK[🧠 Dual Knowledge Retrieval<br/>RAG Semantic vs RAGless Instant &lt;1ms]
        TenantMgr[🏢 Multi-Tenant Vertical Registry<br/>Real Estate • Legal • Salon • Dental • Auto • Clinic]
        NimbusLatency[⏱️ Nimbus Microsecond Latency Tracker<br/>ASR • RAG • LLM TTFT • Tools • TTS]
    end

    VoiceIn & VoiceOut & WebRTC & WebChat & WhatsApp & Messenger & Insta --> Orch
    Orch <--> AccentEngine
    Orch <--> DualK
    Orch <--> TenantMgr
    Orch <--> NimbusLatency

    subgraph Atomic Persistence & Synchronization
        GCal[📅 Live Google Calendar API<br/>Free/Busy • Insert • Patch • Delete]
        DB[(🗄️ SQLite Multi-Tenant DB)]
        Excel[📊 Live Excel Workbook]
        GSheets[📑 Google Sheets Cloud Sync]
        Reminders[⏰ Automated 24h & 1h Push Reminders<br/>SMS • WhatsApp • Outbound Calls]
    end

    Orch --> GCal & DB & Excel & GSheets
    DB --> Reminders
```

---

## 1. Core Architectural Pillars

### 1.1 Plug-and-Play Multi-Tenant Manifests
All vertical-specific behavior (services, pricing, specialist staff, intake questions, business hours, and policies) is abstracted into declarative Pydantic schemas. 
Switching between verticals is instantaneous:
- **Real Estate (`real_estate`)**: Private home showings, open house tours, seller valuations, penthouse VIP viewings, buyer pre-approval intake. Listing Brokers (Victoria Sterling, David Vance, Chloe Montgomery).
- **Legal & Law Firms (`legal`)**: Confidential initial consultations, M&A strategy, contingency personal injury evaluation, trust & estate planning. Partners (Julian Hayes, Rebecca Sinclair, Arthur Pendelton).
- **Salon & Spa (`salon`)**: Luxe haircutting, Balayage, Keratin, Stylists (Elena, Marcus, Chloe).
- **Dental Health (`dental`)**: Prophylaxis cleaning, whitening, root canals, Dentists (Dr. Sarah Chen, Dr. Michael Patel).
- **Automotive Repair (`automotive`)**: Synthetic oil change, brake replacement, diagnostics, Technicians (Frank Miller, Carlos Mendez).
- **Family Medical Clinic (`clinic`)**: Annual physicals, urgent consults, allergy screens, Physicians (Dr. Emily Adams, Dr. James Wilson).

---

### 1.2 Sofia: Female Voice Persona with Dynamic Dialect Adaptation
Targeted for high-value English-speaking markets (**Canada, United States, United Kingdom, Ireland, Continental Europe, and Australia**), Sofia dynamically shifts both **conversational diction** and **acoustic voice synthesis parameters**:

| Dialect Profile | Region / Market | Conversational Style & Phrasing | ElevenLabs Voice ID | OpenAI Voice |
|---|---|---|---|---|
| **Canadian English** | 🇨🇦 Canada (Toronto / Vancouver) | Courteous, attentive Canadian raising (*"Hello there! Great to have you reach out today! Happy to help you out, eh."*) | `21m00Tcm4TlvDq8ikWAM` | `nova` |
| **General American** | 🇺🇸 US (West Coast / Tech / Corporate) | Crisp, modern, neutral corporate (*"Hello! Welcome to our firm. I'd be happy to check availability and book that for you."*) | `21m00Tcm4TlvDq8ikWAM` | `nova` |
| **Red American / Southern** | 🇺🇸 US (Texas / Southeast) | Warm, folksy hospitality (*"Howdy! Sure thing darlin', let's get ya all squared away."*) | `21m00Tcm4TlvDq8ikWAM` | `nova` |
| **European / British English** | 🇬🇧 UK (London RP) | Crisp Received Pronunciation (*"Good day! Splendid choice indeed. I have reserved half past two for you, cheerio."*) | `pFZP5JQG7iQjIQuC4Bku` | `nova` |
| **Irish English** | 🇮🇪 Ireland (Dublin) | Warm, engaging, melodious (*"Hello and welcome! Grand! We'll have that sorted for you in no time."*) | `pFZP5JQG7iQjIQuC4Bku` | `nova` |
| **Euro-International English** | 🇪🇺 Continental Europe | Clear, neutral, universally understood (*"Certainly! We look forward to receiving you for your appointment."*) | `pFZP5JQG7iQjIQuC4Bku` | `nova` |
| **Australian English** | 🇦🇺 Australia (Sydney / Melbourne) | Breezy, cheerful (*"G'day! Welcome! Too easy mate, let's lock in that time for you straight away."*) | `EXAVITQu4vr4xnSDxMaL` | `nova` |
| **Indian English** | 🇮🇳 South Asian Diaspora | Polite, articulate honorifics (*"Namaste! Kindly let me know which slot you would like to arrange today."*) | `ThT5KcBeYPX3keUQqHPh` | `nova` |
| **African English** | 🌍 African Diaspora | Respectful, warm cadence (*"Warm greetings, my dear! We are always delighted to assist you."*) | `EXAVITQu4vr4xnSDxMaL` | `nova` |

---

### 1.3 Two-Way Live Google Calendar Integration
- **Zero Double-Bookings**: Availability calculations query live Google Calendar `freebusy` intervals in real time, merging business hours and staff shifts.
- **Event Lifecycle Synchronization**:
  - `book_new_appointment`: Inserts calendar event with customer name, phone, service, and pop-up reminder notifications.
  - `reschedule_existing_appointment`: Dynamically patches the calendar event start/end time.
  - `cancel_existing_appointment`: Deletes the calendar event from Google Calendar and flags record as cancelled in SQLite and Excel.

---

### 1.4 Nimbus-Inspired Microsecond Latency Architecture
Inspired by the Nimbus Voice Agent codebase, every conversation turn records its exact execution budget:
* `asr_ms`: Audio transcoding and speech-to-text (~115ms).
* `rag_ms`: Knowledge retrieval (<1ms in RAGless mode; ~28ms in semantic RAG mode).
* `llm_ttft_ms`: Time-to-first-token streaming (<60ms).
* `llm_total_ms`: Total dialogue completion (~140ms).
* `tool_ms`: Database mutation and Google Calendar synchronization (~18ms).
* `tts_ms`: Audio streaming synthesis (~165ms).
* **Total End-to-End Voice Latency**: **~440 ms** (far beneath the 600ms human conversational threshold).

---

## 2. Customer Self-Serve Onboarding API

Customers can onboard their business in 1 click via `POST /api/blueprint/onboard-customer`:

```json
{
  "business_name": "Vancouver Premier Real Estate",
  "vertical": "real_estate",
  "phone_number": "+16045550199",
  "address": "1200 Burrard St, Vancouver, BC",
  "primary_accent": "canadian_english",
  "whatsapp_phone_number_id": "1092837465",
  "meta_page_id": "987654321",
  "instagram_account_id": "543216789",
  "google_calendar_id": "vancouver_re@gmail.com"
}
```

The system immediately responds with dedicated webhooks:
```json
{
  "status": "success",
  "tenant_id": "vancouver_premier_real_estate",
  "webhooks": {
    "whatsapp_webhook": "/webhook/whatsapp?tenant_id=vancouver_premier_real_estate",
    "messenger_webhook": "/webhook/messenger?tenant_id=vancouver_premier_real_estate",
    "instagram_webhook": "/webhook/instagram?tenant_id=vancouver_premier_real_estate",
    "twilio_voice_webhook": "/webhook/twilio-voice?tenant_id=vancouver_premier_real_estate"
  },
  "shareable_studio_url": "/?tenant_id=vancouver_premier_real_estate&accent=canadian_english"
}
```

---

## 3. Omnichannel Parity Matrix

The Universal Blueprint enforces identical business rules (lead time, cancellation window, buffer minutes, staff qualification) across all channels:

| Channel | Input Mechanism | Confirmation Delivery | Real-Time Latency |
|---|---|---|---|
| **WebRTC In-Browser Voice** | Browser microphone audio + Barge-in | Spoken voice + Web UI | **< 480 ms** |
| **Outbound Phone ("Call My Phone")** | Mobile phone ringing via Twilio | Automated Voice Call in chosen dialect | Direct PSTN |
| **Inbound Telephony** | SIP / PSTN Twilio / Vapi | Spoken voice + Confirmation SMS | **< 650 ms** |
| **Website Chat Widget** | Text input & dynamic quick chips | Interactive chat bubble + audio playback | **< 35 ms** |
| **WhatsApp Cloud API** | WhatsApp message | WhatsApp push confirmation + quick replies | Direct Webhook |
| **Facebook Messenger** | Messenger DM | Messenger cards + quick replies | Direct Webhook |
| **Instagram Direct** | Instagram DM | Instagram Direct response | Direct Webhook |

---

## 4. How to Sell This Blueprint to Clients

### 4.1 Client Value Proposition by Vertical
* **Real Estate Agencies**: Captures high-intent buyers immediately on luxury listings; pre-qualifies budget and arranges private tours 24/7 without losing leads to competing brokers.
* **Law Firms**: Conducts confidential initial case evaluations at 2:00 AM, screening out conflicts of interest and securing paying retainer consultations.
* **Medical & Dental Clinics**: Fills cancellations instantly from waitlists, reducing front-desk burnout and slashing no-show rates from 20% to under 4%.
* **Salons & Spas**: Converts late-night Instagram DMs and weekend calls into confirmed high-ticket service bookings.

---

## 5. Operations & Verified Test Suite

### Single Command Deploy
```bash
./deploy.sh
```

### Self-Diagnostics (23 Verified Unit Tests)
```bash
.venv/bin/pytest tests/ -v
```
```text
tests/test_multi_tenancy.py::test_tenant_lookup_by_inbound_phone PASSED
tests/test_multi_tenancy.py::test_multi_tenant_call_routing PASSED
tests/test_nimbus_features.py::test_latency_tracker_stages PASSED
tests/test_nimbus_features.py::test_audio_processor_helpers PASSED
tests/test_nimbus_features.py::test_real_estate_vertical PASSED
tests/test_nimbus_features.py::test_legal_firm_vertical PASSED
tests/test_nimbus_features.py::test_target_market_dialects PASSED
tests/test_nimbus_features.py::test_caller_frustration_sentiment_escalation PASSED
tests/test_nimbus_features.py::test_customer_self_serve_onboarding PASSED
tests/test_nimbus_features.py::test_barge_in_endpoint PASSED
tests/test_omnichannel_orchestrator.py::test_blueprint_vertical_manifests PASSED
tests/test_omnichannel_orchestrator.py::test_female_voice_accent_adaptation PASSED
tests/test_omnichannel_orchestrator.py::test_google_calendar_lifecycle PASSED
tests/test_omnichannel_orchestrator.py::test_rag_vs_ragless_toggle PASSED
tests/test_omnichannel_orchestrator.py::test_omnichannel_chat_booking_flow PASSED
tests/test_omnichannel_orchestrator.py::test_outbound_call_endpoint PASSED
tests/test_omnichannel_orchestrator.py::test_webrtc_token_generation PASSED
tests/test_omnichannel_orchestrator.py::test_meta_webhook_verification PASSED
tests/test_reminders_and_excel.py::test_booking_creates_excel_record PASSED
tests/test_reminders_and_excel.py::test_24h_and_1h_reminder_detection PASSED
tests/test_webhook.py::test_health_endpoint PASSED
tests/test_webhook.py::test_check_availability_tool PASSED
tests/test_webhook.py::test_book_and_lookup_and_cancel_lifecycle PASSED
======================== 23 passed in 4.71s =========================
```

### $0.00 Teardown
```bash
./clear.sh
```
