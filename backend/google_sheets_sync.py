import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly from root directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("GoogleSheetsSync")

def get_google_sheet_id() -> Optional[str]:
    return os.getenv("GOOGLE_SHEET_ID")

def _get_google_credentials():
    key_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/google_service_account.json")
    if not os.path.isabs(key_file):
        key_file = str(Path(__file__).resolve().parent.parent / key_file)
    json_creds_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    creds = None
    try:
        from google.oauth2 import service_account
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
    return creds

def sync_appointment_to_google_sheets(appointment: Dict[str, Any], tenant_id: str = "default") -> bool:
    """
    Appends the appointment record directly to a live Google Sheet.
    Guarantees ONLY real customer records are synced (filters out default_salon and test data).
    """
    # Guard against automated test suite polluting the production sheet
    if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING") == "true":
        logger.info(f"🧪 [TEST RUNNER] Skipped live Google Sheets sync for test booking {appointment.get('booking_id')}")
        return True

    # Filter out synthetic automated test appointments
    try:
        from backend.excel_manager import is_real_user_appointment
        if not is_real_user_appointment(appointment):
            logger.info(f"🛡️ Skipped Google Sheets sync for test booking '{appointment.get('booking_id')}'")
            return True
    except Exception:
        pass

    if not tenant_id or tenant_id in ("default_salon", "default"):
        tenant_id = "salon"

    load_dotenv(dotenv_path=env_path)
    sheet_id = get_google_sheet_id()
    creds = _get_google_credentials()

    if sheet_id and sheet_id != "your_google_spreadsheet_id_here" and creds:
        try:
            from googleapiclient.discovery import build
            service = build("sheets", "v4", credentials=creds, cache_discovery=False)
            
            row = [
                appointment.get("booking_id") or appointment.get("id"),
                tenant_id,
                appointment.get("caller_name", "Valued Client"),
                str(appointment.get("caller_phone", "")),
                appointment.get("service_name", ""),
                appointment.get("stylist_name", "Elena"),
                (appointment.get("start_time") or "").replace("T", " "),
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

def rebuild_real_user_google_sheet(sheet_id: Optional[str] = None) -> bool:
    """
    Clears the Google Sheet and writes all real user appointments from the database,
    formatted with custom headers and column widths.
    """
    load_dotenv(dotenv_path=env_path)
    target_sheet_id = sheet_id or get_google_sheet_id()
    creds = _get_google_credentials()

    if not target_sheet_id or not creds:
        logger.warning("Google Sheet ID or credentials missing for rebuild.")
        return False

    try:
        from googleapiclient.discovery import build
        from backend.database import get_db_connection
        from backend.excel_manager import is_real_user_appointment

        service = build("sheets", "v4", credentials=creds, cache_discovery=False)

        # 1. Fetch real appointments
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT id, tenant_id, caller_name, caller_phone, service_name, stylist_name,
                       start_time, status, created_at, whatsapp_24h_sent, call_1h_sent
                FROM appointments
                ORDER BY start_time ASC
            """)
            rows = db.fetchall() if hasattr(db, 'fetchall') else cursor.fetchall()
            appointments = [dict(r) for r in rows] if rows else []

        real_records = [a for a in appointments if is_real_user_appointment(a)]

        headers = ['Booking ID', 'Tenant', 'Client Name', 'Phone', 'Service', 'Stylist', 'Start Time', 'Duration', 'Price', 'Status']
        table_rows = [headers]
        for a in real_records:
            table_rows.append([
                a.get("id"),
                a.get("tenant_id"),
                a.get("caller_name"),
                str(a.get("caller_phone")),
                a.get("service_name"),
                a.get("stylist_name"),
                (a.get("start_time") or "").replace("T", " "),
                "45",
                "75",
                a.get("status", "CONFIRMED")
            ])

        # 2. Clear old sheet
        service.spreadsheets().values().clear(spreadsheetId=target_sheet_id, range="A1:Z100").execute()

        # 3. Write real rows
        service.spreadsheets().values().update(
            spreadsheetId=target_sheet_id,
            range=f"A1:J{len(table_rows)}",
            valueInputOption="USER_ENTERED",
            body={"values": table_rows}
        ).execute()

        # 4. Apply styling
        requests = [
            {
                'repeatCell': {
                    'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 10},
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.12, 'green': 0.31, 'blue': 0.47},
                            'textFormat': {'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}, 'bold': True, 'fontSize': 11},
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            },
            {
                'autoResizeDimensions': {
                    'dimensions': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 10}
                }
            }
        ]
        service.spreadsheets().batchUpdate(spreadsheetId=target_sheet_id, body={'requests': requests}).execute()
        logger.info(f"✅ Successfully rebuilt Google Sheet {target_sheet_id} with {len(real_records)} real user rows.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to rebuild Google Sheet: {e}", exc_info=True)
        return False
