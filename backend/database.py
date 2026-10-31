import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    from backend.excel_manager import (
        get_or_create_workbook,
        append_appointment_to_excel,
        update_excel_reminders
    )
    from backend.google_sheets_sync import sync_appointment_to_google_sheets
except ImportError:
    from excel_manager import (
        get_or_create_workbook,
        append_appointment_to_excel,
        update_excel_reminders
    )
    from google_sheets_sync import sync_appointment_to_google_sheets

DB_PATH = os.getenv("SALON_DB_PATH", "salon_bookings.db")
DEFAULT_TENANT_ID = "default_salon"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tenants Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            created_at TEXT NOT NULL
        )
    """)

    # 2. Salon Services Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # 3. Salon Stylists Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stylists (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # 4. Multi-Tenant Appointments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL DEFAULT 'default_salon',
            caller_name TEXT NOT NULL,
            caller_phone TEXT NOT NULL,
            service_name TEXT NOT NULL,
            stylist_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            whatsapp_24h_sent INTEGER DEFAULT 0,
            call_1h_sent INTEGER DEFAULT 0,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # Check and migrate columns if table already existed
    cursor.execute("PRAGMA table_info(appointments)")
    columns = [row[1] for row in cursor.fetchall()]
    if "tenant_id" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN tenant_id TEXT DEFAULT 'default_salon'")
    if "whatsapp_24h_sent" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN whatsapp_24h_sent INTEGER DEFAULT 0")
    if "call_1h_sent" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN call_1h_sent INTEGER DEFAULT 0")

    # Seed Default Salon if not exists
    cursor.execute("SELECT COUNT(*) FROM tenants WHERE id = ?", (DEFAULT_TENANT_ID,))
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO tenants (id, name, phone_number, address, currency, created_at)
            VALUES (?, 'Luxe Hair & Wellness Salon', '+16175550100', '450 Newbury Street, Boston', 'USD', ?)
        """, (DEFAULT_TENANT_ID, now))

        default_services = [
            ("Womens Haircut", 45, 75),
            ("Mens Cut", 30, 45),
            ("Balayage", 150, 180),
            ("Full Highlights", 120, 160),
            ("Keratin Treatment", 120, 220),
            ("Mani Pedi", 60, 65)
        ]
        for s_name, dur, pr in default_services:
            s_id = f"{DEFAULT_TENANT_ID}_{s_name.replace(' ', '_').lower()}"
            cursor.execute("""
                INSERT OR IGNORE INTO services (id, tenant_id, name, duration_minutes, price)
                VALUES (?, ?, ?, ?, ?)
            """, (s_id, DEFAULT_TENANT_ID, s_name, dur, pr))

        default_stylists = ["Elena", "Marcus", "Chloe"]
        for st_name in default_stylists:
            st_id = f"{DEFAULT_TENANT_ID}_{st_name.lower()}"
            cursor.execute("""
                INSERT OR IGNORE INTO stylists (id, tenant_id, name, active)
                VALUES (?, ?, ?, 1)
            """, (st_id, DEFAULT_TENANT_ID, st_name))

    conn.commit()
    conn.close()

    excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
    get_or_create_workbook(excel_path)

# --- Multi-Tenant Query & Mutation Functions ---

def get_tenant_by_inbound_phone(phone: str) -> Dict[str, Any]:
    """Finds tenant by the dialed inbound phone number. Falls back to default if unmatched."""
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    clean = "".join(filter(str.isdigit, phone))[-10:] if phone else ""
    c.execute("SELECT * FROM tenants WHERE phone_number LIKE ? LIMIT 1", (f"%{clean}%",))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return get_tenant(DEFAULT_TENANT_ID)

def get_tenant(tenant_id: str) -> Dict[str, Any]:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": DEFAULT_TENANT_ID,
        "name": "Luxe Hair & Wellness Salon",
        "phone_number": "+16175550100",
        "address": "450 Newbury Street, Boston"
    }

def get_all_tenants() -> List[Dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tenants ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def create_tenant(tenant_id: str, name: str, phone: str, address: str, 
                  services: List[Tuple[str, int, int]], stylists: List[str]) -> Dict[str, Any]:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    c.execute("""
        INSERT OR REPLACE INTO tenants (id, name, phone_number, address, currency, created_at)
        VALUES (?, ?, ?, ?, 'USD', ?)
    """, (tenant_id, name, phone, address, now))

    for s_name, dur, pr in services:
        s_id = f"{tenant_id}_{s_name.replace(' ', '_').lower()}"
        c.execute("""
            INSERT OR REPLACE INTO services (id, tenant_id, name, duration_minutes, price)
            VALUES (?, ?, ?, ?, ?)
        """, (s_id, tenant_id, s_name, dur, pr))

    for st_name in stylists:
        st_id = f"{tenant_id}_{st_name.lower()}"
        c.execute("""
            INSERT OR REPLACE INTO stylists (id, tenant_id, name, active)
            VALUES (?, ?, ?, 1)
        """, (st_id, tenant_id, st_name))

    conn.commit()
    conn.close()
    return get_tenant(tenant_id)

def get_tenant_services(tenant_id: str) -> List[Dict[str, Any]]:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE tenant_id = ?", (tenant_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_tenant_stylists(tenant_id: str) -> List[str]:
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM stylists WHERE tenant_id = ? AND active = 1", (tenant_id,))
    rows = [r["name"] for r in c.fetchall()]
    conn.close()
    return rows if rows else ["Elena", "Marcus", "Chloe"]

# --- Availability & Booking Engine ---

def check_slots_availability(target_date: str, service_name: str, preferred_stylist: str = "any",
                             tenant_id: str = DEFAULT_TENANT_ID) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get service duration
    cursor.execute("SELECT duration_minutes FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
    row = cursor.fetchone()
    duration = row[0] if row else 45

    # Query active appointments for target_date and tenant
    cursor.execute("""
        SELECT stylist_name, start_time, end_time 
        FROM appointments 
        WHERE tenant_id = ? AND date(start_time) = date(?) AND status = 'CONFIRMED'
    """, (tenant_id, target_date))
    booked_slots = cursor.fetchall()

    # Query active stylists for this tenant
    stylists_pool = get_tenant_stylists(tenant_id)
    stylists = stylists_pool if preferred_stylist.lower() in ("any", "") else [preferred_stylist]

    available_times = []
    candidate_hours = [9, 10, 11, 13, 14, 15, 16]
    for hour in candidate_hours:
        for minute in [0, 30]:
            candidate_start = datetime.strptime(f"{target_date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
            candidate_end = candidate_start + timedelta(minutes=duration)

            if candidate_end.hour > 18 or (candidate_end.hour == 18 and candidate_end.minute > 0):
                continue

            for stylist in stylists:
                has_conflict = False
                for b in booked_slots:
                    if b["stylist_name"].lower() == stylist.lower():
                        b_start = datetime.fromisoformat(b["start_time"])
                        b_end = datetime.fromisoformat(b["end_time"])
                        if candidate_start < b_end and candidate_end > b_start:
                            has_conflict = True
                            break
                if not has_conflict:
                    slot_str = candidate_start.strftime("%I:%M %p")
                    if slot_str not in available_times:
                        available_times.append(slot_str)
                    break

    conn.close()
    return available_times[:4]

def book_new_appointment(caller_name: str, caller_phone: str, service_name: str, 
                         appointment_datetime: str, stylist_name: str = "Elena",
                         tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    dt_clean = appointment_datetime.replace("Z", "")
    start_dt = datetime.fromisoformat(dt_clean)

    cursor.execute("SELECT duration_minutes, price FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
    srv_row = cursor.fetchone()
    duration = srv_row[0] if srv_row else 45
    price = srv_row[1] if srv_row else 75
    end_dt = start_dt + timedelta(minutes=duration)

    booking_id = f"LUXE-{start_dt.strftime('%m%d')}-{cursor.execute('SELECT COUNT(*) FROM appointments').fetchone()[0] + 101}"
    now_str = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO appointments (id, tenant_id, caller_name, caller_phone, service_name, stylist_name, start_time, end_time, status, created_at, whatsapp_24h_sent, call_1h_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, 0, 0)
    """, (booking_id, tenant_id, caller_name, caller_phone, service_name, stylist_name, start_dt.isoformat(), end_dt.isoformat(), now_str))

    conn.commit()
    conn.close()

    booking_record = {
        "booking_id": booking_id,
        "tenant_id": tenant_id,
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "service_name": service_name,
        "stylist_name": stylist_name,
        "start_time": start_dt.strftime("%Y-%m-%d %H:%M"),
        "duration_minutes": duration,
        "price": price,
        "status": "CONFIRMED"
    }

    # 1. Sync into Local Excel Workbook
    excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
    append_appointment_to_excel(booking_record, filepath=excel_path)

    # 2. Sync to Live Google Sheet
    sync_appointment_to_google_sheets(booking_record, tenant_id=tenant_id)

    return {
        "booking_id": booking_id,
        "tenant_id": tenant_id,
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "service_name": service_name,
        "stylist_name": stylist_name,
        "start_time": start_dt.strftime("%A, %b %d at %I:%M %p"),
        "price": f"${price}"
    }

def lookup_by_phone(caller_phone: str, tenant_id: str = DEFAULT_TENANT_ID) -> Optional[Dict[str, str]]:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]
    cursor.execute("""
        SELECT * FROM appointments 
        WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
        ORDER BY start_time DESC LIMIT 1
    """, (tenant_id, f"%{phone_clean}%"))
    row = cursor.fetchone()
    conn.close()
    if row:
        start_dt = datetime.fromisoformat(row["start_time"])
        return {
            "booking_id": row["id"],
            "caller_name": row["caller_name"],
            "service_name": row["service_name"],
            "stylist_name": row["stylist_name"],
            "start_time": start_dt.strftime("%A, %b %d at %I:%M %p")
        }
    return None

def cancel_existing_appointment(caller_phone: str, booking_id: Optional[str] = None,
                                tenant_id: str = DEFAULT_TENANT_ID) -> bool:
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]

    if booking_id:
        cursor.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ? AND tenant_id = ?", (booking_id, tenant_id))
    else:
        cursor.execute("""
            UPDATE appointments SET status = 'CANCELLED' 
            WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
        """, (tenant_id, f"%{phone_clean}%"))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    if updated:
        excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
        update_excel_reminders(booking_id or "", status="CANCELLED", filepath=excel_path)

    return updated

def get_pending_24h_reminders() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    window_start = (now + timedelta(hours=23)).isoformat()
    window_end = (now + timedelta(hours=25)).isoformat()

    cursor.execute("""
        SELECT * FROM appointments 
        WHERE status = 'CONFIRMED' 
          AND whatsapp_24h_sent = 0
          AND start_time BETWEEN ? AND ?
    """, (window_start, window_end))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def mark_24h_reminder_sent(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET whatsapp_24h_sent = 1 WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
    update_excel_reminders(booking_id, whatsapp_24h="SENT", filepath=excel_path)

def get_pending_1h_call_reminders() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now()
    window_start = (now + timedelta(minutes=50)).isoformat()
    window_end = (now + timedelta(minutes=70)).isoformat()

    cursor.execute("""
        SELECT * FROM appointments 
        WHERE status = 'CONFIRMED' 
          AND call_1h_sent = 0
          AND start_time BETWEEN ? AND ?
    """, (window_start, window_end))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def mark_1h_call_sent(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET call_1h_sent = 1 WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
    update_excel_reminders(booking_id, call_1h="CALLED", filepath=excel_path)
