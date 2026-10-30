import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_FILE = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")

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
    wb = get_or_create_workbook(filepath)
    ws = wb["Salon Appointments"]
    
    row_values = [
        appointment.get("booking_id", "LUXE-0000"),
        appointment.get("caller_name", "Guest"),
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

