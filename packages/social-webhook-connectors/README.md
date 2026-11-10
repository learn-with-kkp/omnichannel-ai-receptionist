# 💬 Social Webhook Connectors (`social-webhook-connectors`)

[![PyPI version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Enterprise multi-channel webhook ingestion and auto-reply suite connecting WhatsApp Business Cloud API, Meta Facebook Messenger, Instagram Direct, LinkedIn Messaging, and Twitter/X DMs to unified conversational AI agents.

## 🚀 Supported Platforms

- **Meta WhatsApp Cloud API**: Bidirectional text & voice note media transcription.
- **Facebook Messenger**: Graph API v19.0 webhooks with quick-reply buttons and carousels.
- **Instagram Direct**: Real-time business DM webhooks with hand-off triggers.
- **LinkedIn Messaging**: Company page conversational API with lead routing.
- **Twitter / X DMs**: Account Activity API with CRC challenge verification.
- **Telegram Bot API**: Long polling & webhook receiver with inline keyboards.

## 💻 Usage

```python
from social_webhook_connectors import WhatsAppConnector, MessengerConnector

# Mount easily into FastAPI
from fastapi import FastAPI
app = FastAPI()

app.include_router(WhatsAppConnector().router)
app.include_router(MessengerConnector().router)
```
