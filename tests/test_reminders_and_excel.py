import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytest
import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["SALON_DB_PATH"] = "test_reminders.db"
os.environ["SALON_EXCEL_PATH"] = "test_appointments.xlsx"

from backend.database import (
    init_db,
    book_new_appointment,
    get_pending_24h_reminders,
    get_pending_1h_call_reminders,
    mark_24h_reminder_sent,
    mark_1h_call_sent,
    get_db_connection
)
from backend.reminder_service import run_reminder_cycle

@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    yield
    for f in ["test_reminders.db", "test_appointments.xlsx"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def test_booking_creates_excel_record():
    dt_str = (datetime.now() + timedelta(days=2)).isoformat()
    booking = book_new_appointment(
        caller_name="Alice Smith",
        caller_phone="+16175550999",
        service_name="Balayage",
        appointment_datetime=dt_str,
        stylist_name="Elena"
    )
    
    assert os.path.exists("test_appointments.xlsx")
    wb = openpyxl.load_workbook("test_appointments.xlsx")
    ws = wb["Salon Appointments"]
    assert ws.max_row >= 2
    
    last_row = [cell.value for cell in ws[ws.max_row]]
    assert booking["booking_id"] in last_row
    assert "Alice Smith" in last_row
    assert "Balayage" in last_row
    assert "PENDING" in last_row  # reminder pending

def test_24h_and_1h_reminder_detection(monkeypatch):
    import backend.reminder_service as rs
    monkeypatch.setattr(rs, "send_whatsapp_message", lambda to_num, msg: True)
    monkeypatch.setattr(rs, "trigger_vapi_outbound_reminder_call", lambda p, n, s, st, stt: True)
    now = datetime.now()
    
    # 1. Appointment in 24 hours
    dt_24h = (now + timedelta(hours=24)).isoformat()
    b24 = book_new_appointment("Bob 24h", "+16175550240", "Womens Haircut", dt_24h, "Marcus")
    
    # 2. Appointment in 1 hour
    dt_1h = (now + timedelta(minutes=60)).isoformat()
    b1h = book_new_appointment("Charlie 1h", "+16175550010", "Mens Cut", dt_1h, "Chloe")

    # Detect 24h
    pending_24 = get_pending_24h_reminders()
    ids_24 = [p["id"] for p in pending_24]
    assert b24["booking_id"] in ids_24

    # Detect 1h
    pending_1 = get_pending_1h_call_reminders()
    ids_1 = [p["id"] for p in pending_1]
    assert b1h["booking_id"] in ids_1

    # Run cycle and ensure statuses update
    run_reminder_cycle()

    # Verify marked as sent in DB
    conn = get_db_connection()
    c = conn.cursor()
    row_24 = c.execute("SELECT whatsapp_24h_sent FROM appointments WHERE id = ?", (b24["booking_id"],)).fetchone()
    row_1 = c.execute("SELECT call_1h_sent FROM appointments WHERE id = ?", (b1h["booking_id"],)).fetchone()
    conn.close()

    assert row_24[0] == 1
    assert row_1[0] == 1

    # Verify Excel was updated
    wb = openpyxl.load_workbook("test_appointments.xlsx")
    ws = wb["Salon Appointments"]
    values = [[cell.value for cell in row] for row in ws.iter_rows(values_only=False)]

    # Find Bob and Charlie rows
    b24_row = next(r for r in values[1:] if r[0] == b24["booking_id"])
    b1h_row = next(r for r in values[1:] if r[0] == b1h["booking_id"])

    assert b24_row[9] == "SENT"  # column 10: 24h WhatsApp
    assert b1h_row[10] == "CALLED"  # column 11: 1h Auto Call
