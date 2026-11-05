"""
Chat Router: Live Website Chatbot, WebSocket Streaming, and Female Voice TTS Synthesis.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Response
from pydantic import BaseModel

from core.blueprint.schema import OmniChannelType
from core.blueprint.tenant_manager import tenant_registry
from core.engine.orchestrator import universal_orchestrator

logger = logging.getLogger("ChatRouter")
router = APIRouter(prefix="", tags=["Chat"])


class ChatMessageRequest(BaseModel):
    message: str
    tenant_id: Optional[str] = "salon"
    accent: Optional[str] = "red_american"
    caller_name: Optional[str] = "Guest"
    caller_phone: Optional[str] = "+16673070119"
    session_id: Optional[str] = "default-session"
    channel: Optional[str] = "website_chat"


@router.post("/api/chat/message")
async def send_chat_message(payload: ChatMessageRequest):
    """
    Unified chat message handler.
    Processes natural conversation, fuzzy-matches services and staff,
    checks live Google Calendar availability, and coordinates atomic booking commits.
    """
    ch_type = OmniChannelType.WEBSITE_CHAT
    try:
        ch_type = OmniChannelType(payload.channel)
    except Exception:
        pass

    result = universal_orchestrator.process_conversation_turn(
        user_message=payload.message,
        session_id=payload.session_id or "web-session",
        tenant_id=payload.tenant_id or "salon",
        channel=ch_type,
        accent_key=payload.accent or "red_american",
        caller_phone=payload.caller_phone,
        caller_name=payload.caller_name
    )

    return result


@router.get("/api/chat/tts")
async def synthesize_speech(
    text: str = Query(..., description="Text to synthesize"),
    accent: str = Query("red_american", description="Accent profile key")
):
    """
    Female Voice Audio TTS Synthesis endpoint.
    Converts assistant response into spoken audio using ElevenLabs or OpenAI TTS.
    If third-party keys are not provided, returns browser speech parameters.
    """
    accent_profile = tenant_registry.get_accent(accent)
    eleven_key = os.getenv("ELEVENLABS_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # 1. ElevenLabs TTS if key configured
    if eleven_key and not eleven_key.startswith("your_"):
        try:
            import urllib.request
            voice_id = accent_profile.elevenlabs_voice_id
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            body = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": accent_profile.stability,
                    "similarity_boost": accent_profile.similarity_boost
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "xi-api-key": eleven_key,
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                audio_bytes = resp.read()
                return Response(content=audio_bytes, media_type="audio/mpeg")
        except Exception as e:
            logger.warning(f"ElevenLabs TTS failed: {e}. Falling back to client-side synthesis.")

    # 2. OpenAI TTS if key configured
    if openai_key and not openai_key.startswith("your_"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            return Response(content=response.read(), media_type="audio/mpeg")
        except Exception as e:
            logger.warning(f"OpenAI TTS failed: {e}. Falling back to client-side synthesis.")

    # 3. Client-side browser synthesis instructions
    return {
        "status": "client_synthesis",
        "voice_name": "Sofia",
        "accent": accent_profile.name,
        "pitch": accent_profile.pitch,
        "rate": accent_profile.speaking_rate,
        "text": text
    }


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Real-time bi-directional WebSocket chat for the web studio."""
    await websocket.accept()
    session_id = f"ws-{id(websocket)}"
    tenant_id = "salon"
    accent_key = "red_american"

    try:
        while True:
            raw_text = await websocket.receive_text()
            data = {}
            try:
                data = json.loads(raw_text)
            except Exception:
                data = {"message": raw_text}

            msg = data.get("message", "")
            tenant_id = data.get("tenant_id", tenant_id)
            accent_key = data.get("accent", accent_key)
            caller_phone = data.get("caller_phone", "+16673070119")
            caller_name = data.get("caller_name", "Web Guest")

            res = universal_orchestrator.process_conversation_turn(
                user_message=msg,
                session_id=session_id,
                tenant_id=tenant_id,
                channel=OmniChannelType.WEBSITE_CHAT,
                accent_key=accent_key,
                caller_phone=caller_phone,
                caller_name=caller_name
            )

            await websocket.send_text(json.dumps(res))
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {session_id} disconnected.")
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass

