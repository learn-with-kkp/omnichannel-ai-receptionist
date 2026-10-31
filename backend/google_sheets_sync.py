import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("GoogleSheetsSync")

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/google_service_account.json")

def sync_appointment_to_google_sheets(appointment: Dict[str, Any], tenant_id: str = "default") -> bool:
    """
    Appends the appointment record directly to a live Google Sheet.
    Falls back gracefully to simulation mode if Google API credentials are not set.
    """
    creds = None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        if os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
            creds = service_account.Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes
            )
        elif GOOGLE_SERVICE_ACCOUNT_JSON:
            creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=scopes
            )
    except Exception as e:
        logger.debug(f"Google credentials initialization skipped or failed: {e}")

    if GOOGLE_SHEET_ID and creds:
        try:
            service = build("sheets", "v4", credentials=creds)
            
            row = [
                appointment.get("booking_id"),
                tenant_id,
                appointment.get("caller_name"),
                appointment.get("caller_phone"),
                appointment.get("service_name"),
                appointment.get("stylist_name"),
                appointment.get("start_time"),
                appointment.get("duration_minutes", 45),
                appointment.get("price", 75),
                appointment.get("status", "CONFIRMED")
            ]
            
            service.spreadsheets().values().append(
                spreadsheetId=GOOGLE_SHEET_ID,
                range="A:J",
                valueInputOption="USER_ENTERED",
                body={"values": [row]}
            ).execute()
            logger.info(f"✅ Appended booking {appointment.get('booking_id')} to Google Sheet {GOOGLE_SHEET_ID}")
            return True
        except Exception as e:
            logger.error(f"❌ Google Sheets Sync Error: {e}")
            return False
    else:
        # Development / Simulation mode
        logger.info(f"📊 [GOOGLE SHEETS SIMULATION] [Tenant: {tenant_id}] Synced booking {appointment.get('booking_id')}")
        return True

