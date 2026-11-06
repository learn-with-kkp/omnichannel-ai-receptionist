import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly from root directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("GoogleSheetsSync")

def get_google_sheet_id() -> Optional[str]:
    return os.getenv("GOOGLE_SHEET_ID")

def sync_appointment_to_google_sheets(appointment: Dict[str, Any], tenant_id: str = "default") -> bool:
    """
    Appends the appointment record directly to a live Google Sheet.
    Falls back gracefully to simulation mode if Google API credentials are not set.
    """
    load_dotenv(dotenv_path=env_path)
    sheet_id = get_google_sheet_id()
    key_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/google_service_account.json")
    if not os.path.isabs(key_file):
        key_file = str(Path(__file__).resolve().parent.parent / key_file)
    json_creds_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    creds = None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        if os.path.exists(key_file):
            creds = service_account.Credentials.from_service_account_file(
                key_file, scopes=scopes
            )
        elif json_creds_str:
            creds_dict = json.loads(json_creds_str) if isinstance(json_creds_str, str) else json_creds_str
            if "private_key" in creds_dict and isinstance(creds_dict["private_key"], str):
                if "\\n" in creds_dict["private_key"]:
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=scopes
            )
    except Exception as e:
        logger.error(f"Google credentials initialization failed: {e}")

    if sheet_id and sheet_id != "your_google_spreadsheet_id_here" and creds:
        try:
            service = build("sheets", "v4", credentials=creds, cache_discovery=False)
            
            row = [
                appointment.get("booking_id"),
                tenant_id,
                appointment.get("caller_name"),
                str(appointment.get("caller_phone")),
                appointment.get("service_name"),
                appointment.get("stylist_name"),
                appointment.get("start_time"),
                str(appointment.get("duration_minutes", 45)),
                str(appointment.get("price", 75)),
                appointment.get("status", "CONFIRMED")
            ]
            
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="A:J",
                valueInputOption="USER_ENTERED",
                body={"values": [row]}
            ).execute()
            logger.info(f"✅ Appended booking {appointment.get('booking_id')} to Google Sheet {sheet_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Google Sheets Sync Error: {e}")
            return False
    else:
        logger.warning(f"⚠️ Google Sheets sync bypassed (sheet_id: {sheet_id}, creds present: {creds is not None})")
        return False

