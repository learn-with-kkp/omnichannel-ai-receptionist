"""
Telegram Bot API Integration.
Handles:
- Webhook registration & incoming message parsing
- Inline keyboard slot selection markup
- Resilient outbound message delivery via https://api.telegram.org/bot<token>/sendMessage
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("TelegramBotIntegration")


class TelegramBotClient:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.bot_token and not self.bot_token.startswith("your_"))

    def send_message(
        self,
        chat_id: str,
        text: str,
        quick_replies: Optional[List[str]] = None,
        parse_mode: str = "Markdown"
    ) -> Dict[str, Any]:
        """Sends message to Telegram user or group, optionally with inline keyboard buttons."""
        clean_chat_id = str(chat_id).strip()

        reply_markup = None
        if quick_replies:
            # Group quick replies into rows of 2
            keyboard = []
            row = []
            for btn in quick_replies:
                row.append({"text": btn, "callback_data": btn[:64]})
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            reply_markup = {"inline_keyboard": keyboard}

        if self.is_configured():
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    "chat_id": clean_chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
                if reply_markup:
                    payload["reply_markup"] = reply_markup

                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Telegram message dispatched to {clean_chat_id}")
                    return {"status": "sent", "channel": "telegram", "response": resp_data}
            except Exception as e:
                logger.error(f"Telegram Bot API failed: {e}")

        logger.info(f"✈️ [SIMULATION TELEGRAM] To: {clean_chat_id} | Body: {text}")
        simulated_payload: Dict[str, Any] = {
            "status": "simulated",
            "channel": "telegram",
            "chat_id": clean_chat_id,
            "text": text
        }
        if reply_markup:
            simulated_payload["reply_markup"] = reply_markup
        return simulated_payload

    @staticmethod
    def parse_incoming_update(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extracts sender chat_id, user_name, and text from incoming Telegram update."""
        if "message" in data:
            msg = data["message"]
            chat_id = str(msg.get("chat", {}).get("id", ""))
            from_user = msg.get("from", {})
            user_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip() or from_user.get("username", "Telegram User")
            text = msg.get("text", "")
            return {"chat_id": chat_id, "user_name": user_name, "text": text, "type": "message"}
        elif "callback_query" in data:
            cb = data["callback_query"]
            chat_id = str(cb.get("message", {}).get("chat", {}).get("id", ""))
            from_user = cb.get("from", {})
            user_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip() or "Telegram User"
            text = cb.get("data", "")
            return {"chat_id": chat_id, "user_name": user_name, "text": text, "type": "callback_query"}
        return None


telegram_client = TelegramBotClient()

