"""
TikTok Direct Messaging & Business Webhook Integration.
Handles:
- Webhook subscription verification
- Incoming direct message parsing
- Auto-response delivery via TikTok Business Messaging API (https://business-api.tiktok.com/open_api/v1.3/im/message/send/)
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("TikTokIntegration")


class TikTokClient:
    def __init__(
        self,
        client_key: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        self.client_key = client_key or os.getenv("TIKTOK_CLIENT_KEY", "")
        self.client_secret = client_secret or os.getenv("TIKTOK_CLIENT_SECRET", "")
        self.access_token = access_token or os.getenv("TIKTOK_ACCESS_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.access_token and not self.access_token.startswith("your_"))

    def send_direct_message(
        self,
        recipient_open_id: str,
        text: str
    ) -> Dict[str, Any]:
        """Dispatches a direct message to a TikTok user via TikTok Business Messaging API."""
        clean_recipient = str(recipient_open_id).strip()

        if self.is_configured():
            try:
                url = "https://business-api.tiktok.com/open_api/v1.3/im/message/send/"
                payload = {
                    "to_user_id": clean_recipient,
                    "msg_type": "text",
                    "content": json.dumps({"text": text})
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Access-Token": self.access_token,
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ TikTok DM sent to {clean_recipient}")
                    return {"status": "sent", "channel": "tiktok", "response": resp_data}
            except Exception as e:
                logger.error(f"TikTok Direct Messaging API failed: {e}")

        logger.info(f"🎵 [SIMULATION TIKTOK] To: {clean_recipient} | Body: {text}")
        return {
            "status": "simulated",
            "channel": "tiktok",
            "recipient_open_id": clean_recipient,
            "text": text
        }

    @staticmethod
    def parse_incoming_dm(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses TikTok Webhook Event."""
        event = data.get("event", "")
        payload = data.get("content", {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {"text": payload}

        sender_id = data.get("from_user_id") or payload.get("sender_id") or data.get("sender_id", "")
        text = payload.get("text") or data.get("text", "")
        if sender_id and text:
            return {"sender_id": str(sender_id), "text": str(text), "event": event}
        return None


tiktok_client = TikTokClient()

