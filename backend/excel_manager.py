import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

def _resolve_excel_path() -> str:
    is_serverless = bool(
        os.getenv("VERCEL")
        or os.getenv("VERCEL_ENV")
        or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        or os.getenv("LAMBDA_TASK_ROOT")
        or not os.access(".", os.W_OK)
    )
    if is_serverless:
        custom = os.getenv("SALON_EXCEL_PATH")
        if custom and custom.startswith("/tmp"):
            return custom
        return "/tmp/salon_appointments.xlsx"
    return os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")

EXCEL_FILE = _resolve_excel_path()

HEADERS = [
    "Booking ID",
    "Client Name",
    "Phone Number",
    "Service",
    "Stylist",
    "Appointment Start",
    "Duration (Min)",
    "Price ($)",
    "Status",
    "24h WhatsApp Sent",
    "1h Auto Call Status",
    "Created At"
]

TEST_USER_NAMES = {
    "sarah connor",
    "elena fisher",
    "automated verification test",
    "test client",
    "david beckham",
    "alexander hamilton",
    "grace hopper",
    "alice wonder",
    "dr. watson",
    "test user",
    "john doe",
    "jane doe",
    "test"
}

def is_real_user_appointment(appointment: Dict[str, Any]) -> bool:
    """
    Discriminates real user bookings from synthetic test / default_salon records.
    Returns True ONLY for real customer appointments.
    """
    tenant_id = str(appointment.get("tenant_id", "")).strip().lower()
    caller_name = str(appointment.get("caller_name", "")).strip().lower()
    caller_phone = str(appointment.get("caller_phone", "")).strip().lower()

    # Explicitly filter out default_salon test records
    if tenant_id in ("default_salon", "test_salon", "test"):
        return False

    # Filter out explicit test tags
    if appointment.get("is_test"):
        return False

    # Filter out synthetic mock names
    if caller_name in TEST_USER_NAMES or "test" in caller_name:
        return False

    # Filter out dummy 555 / test phone numbers
    if "55501" in caller_phone or "55502" in caller_phone or "55500" in caller_phone or "4443322" in caller_phone:
        return False

    return True

def get_or_create_workbook(filepath: str = EXCEL_FILE) -> openpyxl.Workbook:
    p = Path(filepath)
    if p.exists():
        wb = openpyxl.load_workbook(filepath)
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Salon Appointments"
        
        # Header formatting
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        ws.append(HEADERS)
        for col_idx in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border
        
        ws.row_dimensions[1].height = 28
        wb.save(filepath)
    return wb

def append_appointment_to_excel(appointment: Dict[str, Any], filepath: str = EXCEL_FILE):
    is_test_file = "test_" in str(filepath).lower() or "test." in str(filepath).lower()
    is_pytest = bool(os.getenv("PYTEST_CURRENT_TEST"))

    # If writing to the production user Excel sheet, enforce strict real-user filter
    if not is_test_file and not is_pytest:
        if not is_real_user_appointment(appointment):
            logger.info(f"🛡️ Filtered synthetic test/default_salon booking '{appointment.get('booking_id')}' from production Excel.")
            return

    wb = get_or_create_workbook(filepath)
    ws = wb["Salon Appointments"]
    
    row_values = [
        appointment.get("booking_id") or appointment.get("id") or "LUXE-0000",
        appointment.get("caller_name", "Valued Client"),
        appointment.get("caller_phone", ""),
        appointment.get("service_name", ""),
        appointment.get("stylist_name", "Elena"),
        appointment.get("start_time", ""),
        appointment.get("duration_minutes", 45),
        appointment.get("price", 75),
        appointment.get("status", "CONFIRMED"),
        "PENDING",
        "PENDING",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ]
    
    ws.append(row_values)
    current_row = ws.max_row
    
    # Styling for data row
    row_fill = PatternFill(start_color="F2F5F9" if current_row % 2 == 0 else "FFFFFF", fill_type="solid")
    regular_font = Font(name="Calibri", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    
    for col_idx, val in enumerate(row_values, 1):
        cell = ws.cell(row=current_row, column=col_idx)
        cell.font = regular_font
        cell.fill = row_fill
        cell.alignment = center_align if col_idx not in [2, 4] else left_align
    
    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
        
    ws.row_dimensions[current_row].height = 22
    wb.save(filepath)

def rebuild_real_user_excel_sheet(filepath: str = EXCEL_FILE, appointments: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Completely regenerates the Excel spreadsheet with ONLY real user appointments.
    Guarantees 0 default_salon test records and 0 synthetic test user rows.
    """
    if appointments is None:
        try:
            from backend.database import get_db_connection
            with get_db_connection() as db:
                cursor = db.cursor()
                cursor.execute("""
                    SELECT id, tenant_id, caller_name, caller_phone, service_name, stylist_name,
                           start_time, status, created_at, whatsapp_24h_sent, call_1h_sent
                    FROM appointments
                    WHERE tenant_id != 'default_salon'
                    ORDER BY start_time ASC
                """)
                rows = db.fetchall() if hasattr(db, 'fetchall') else cursor.fetchall()
                appointments = [dict(r) for r in rows] if rows else []
        except Exception as e:
            logger.warning(f"Failed to query database for Excel rebuild: {e}")
            appointments = []

    # Filter strictly for real users
    real_records = [a for a in appointments if is_real_user_appointment(a)]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Salon Appointments"

    # Header styling
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    ws.append(HEADERS)
    for col_idx in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    regular_font = Font(name="Calibri", size=10)
    left_align = Alignment(horizontal="left", vertical="center")

    for idx, a in enumerate(real_records, start=2):
        row_values = [
            a.get("booking_id") or a.get("id") or f"LUXE-{idx:04d}",
            a.get("caller_name", "Valued Client"),
            a.get("caller_phone", ""),
            a.get("service_name", ""),
            a.get("stylist_name", "Elena"),
            (a.get("start_time") or "").replace("T", " "),
            a.get("duration_minutes", 45),
            a.get("price", 75),
            a.get("status", "CONFIRMED"),
            "SENT" if a.get("whatsapp_24h_sent") == 1 else "PENDING",
            "CALLED" if a.get("call_1h_sent") == 1 else "PENDING",
            (a.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M"))[:16].replace("T", " ")
        ]
        ws.append(row_values)
        row_fill = PatternFill(start_color="F2F5F9" if idx % 2 == 0 else "FFFFFF", fill_type="solid")
        for col_idx, val in enumerate(row_values, 1):
            cell = ws.cell(row=idx, column=col_idx)
            cell.font = regular_font
            cell.fill = row_fill
            cell.alignment = center_align if col_idx not in [2, 4] else left_align
        ws.row_dimensions[idx].height = 22

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(filepath)
    return filepath

def update_excel_reminders(booking_id: str, whatsapp_24h: Optional[str] = None, 
                           call_1h: Optional[str] = None, status: Optional[str] = None,
                           filepath: str = EXCEL_FILE):
    p = Path(filepath)
    if not p.exists():
        return
    wb = openpyxl.load_workbook(filepath)
    ws = wb["Salon Appointments"]
    
    for row in range(2, ws.max_row + 1):
        if str(ws.cell(row=row, column=1).value).strip() == str(booking_id).strip():
            if status:
                ws.cell(row=row, column=9).value = status
            if whatsapp_24h:
                ws.cell(row=row, column=10).value = whatsapp_24h
            if call_1h:
                ws.cell(row=row, column=11).value = call_1h
            break
            
    wb.save(filepath)
