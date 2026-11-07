"""
Universal Database Access Layer.
Supports:
1. Neon Cloud PostgreSQL (NEON_POSTGRES_CONNECTION_URL / DATABASE_URL) in production.
2. Local & In-Memory SQLite fallback for development and isolated unit test suites.
3. Automatic SQL syntax translation between SQLite and PostgreSQL.
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("DatabaseAccessLayer")

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

# Optional psycopg2 import
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def get_database_url() -> Optional[str]:
    """Retrieves Neon / PostgreSQL connection string from environment."""
    # When running isolated pytest unit tests with explicit test DB, prefer SQLite
    if os.getenv("PYTEST_CURRENT_TEST") and os.getenv("SALON_DB_PATH"):
        return None

    url = (
        os.getenv("NEON_POSTGRES_CONNECTION_URL")
        or os.getenv("DATABASE_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRESQL_URL")
    )
    if url and ("postgres://" in url or "postgresql://" in url):
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url.strip()
    return None


def is_postgres() -> bool:
    return bool(PSYCOPG2_AVAILABLE and get_database_url())


# Connection Pool for PostgreSQL
_pg_pool: Optional[Any] = None

def get_pg_pool():
    global _pg_pool
    if _pg_pool is None and is_postgres():
        url = get_database_url()
        try:
            _pg_pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=url, connect_timeout=10)
            logger.info("🐘 Connected to Neon PostgreSQL connection pool.")
        except Exception as e:
            logger.error(f"Failed to create Neon Postgres connection pool: {e}")
            _pg_pool = None
    return _pg_pool


class DBConnectionContext:
    """
    Unified Database Context Manager.
    Automatically handles PostgreSQL connection pooling or SQLite connection.
    Translates query placeholders from '?' to '%s' for PostgreSQL.
    """
    def __init__(self):
        self.is_pg = is_postgres()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        if self.is_pg:
            p = get_pg_pool()
            if p:
                self.conn = p.getconn()
            else:
                self.conn = psycopg2.connect(get_database_url(), connect_timeout=10)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            self.conn = sqlite3.connect(os.getenv("SALON_DB_PATH", DB_PATH))
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.cursor.close()
            if self.is_pg:
                p = get_pg_pool()
                if p and self.conn:
                    p.putconn(self.conn)
                elif self.conn:
                    self.conn.close()
            else:
                self.conn.close()

    def execute(self, sql: str, params: Tuple = ()) -> Any:
        if self.is_pg:
            # Translate SQLite syntax to PostgreSQL
            pg_sql = sql.replace("?", "%s")
            pg_sql = pg_sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
            pg_sql = pg_sql.replace("INSERT OR REPLACE INTO", "INSERT INTO")
            if "INSERT INTO" in pg_sql and "ON CONFLICT" not in pg_sql:
                if "tenants" in pg_sql:
                    pg_sql += " ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, phone_number = EXCLUDED.phone_number, address = EXCLUDED.address"
                elif "services" in pg_sql:
                    pg_sql += " ON CONFLICT (id) DO NOTHING"
                elif "stylists" in pg_sql:
                    pg_sql += " ON CONFLICT (id) DO NOTHING"
            self.cursor.execute(pg_sql, params)
        else:
            self.cursor.execute(sql, params)
        return self.cursor

    def fetchone(self) -> Optional[Dict[str, Any]]:
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def rowcount(self) -> int:
        return self.cursor.rowcount


def get_db_connection():
    """Backward compatibility helper for raw sqlite3 connections."""
    conn = sqlite3.connect(os.getenv("SALON_DB_PATH", DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes schema and seeds default salon tenant on Neon Postgres or SQLite."""
    with DBConnectionContext() as db:
        # 1. Tenants Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL,
                currency TEXT DEFAULT 'USD',
                created_at TEXT NOT NULL
            )
        """)

        # 2. Services Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                price INTEGER NOT NULL,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)

        # 3. Stylists Table
        db.execute("""
            CREATE TABLE IF NOT EXISTS stylists (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)

        # 4. Appointments Table
        db.execute("""
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

        # Seed Default Salon if not exists
        db.execute("SELECT COUNT(*) as count FROM tenants WHERE id = ?", (DEFAULT_TENANT_ID,))
        row = db.fetchone()
        count = row.get("count", 0) if row else 0
        if count == 0:
            now = datetime.now().isoformat()
            db.execute("""
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
                db.execute("""
                    INSERT INTO services (id, tenant_id, name, duration_minutes, price)
                    VALUES (?, ?, ?, ?, ?)
                """, (s_id, DEFAULT_TENANT_ID, s_name, dur, pr))

            default_stylists = ["Elena", "Marcus", "Chloe"]
            for st_name in default_stylists:
                st_id = f"{DEFAULT_TENANT_ID}_{st_name.lower()}"
                db.execute("""
                    INSERT INTO stylists (id, tenant_id, name, active)
                    VALUES (?, ?, ?, 1)
                """, (st_id, DEFAULT_TENANT_ID, st_name))


def get_tenant(tenant_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
        return db.fetchone()


def get_tenant_by_inbound_phone(phone_number: str) -> Optional[Dict[str, Any]]:
    init_db()
    if not phone_number:
        return get_tenant(DEFAULT_TENANT_ID)
    clean_phone = "".join(filter(str.isdigit, phone_number))[-10:]
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants WHERE phone_number LIKE ?", (f"%{clean_phone}%",))
        tenant = db.fetchone()
        if not tenant:
            return get_tenant(DEFAULT_TENANT_ID)
        return tenant


def get_all_tenants() -> List[Dict[str, Any]]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants ORDER BY created_at DESC")
        return db.fetchall()


def create_tenant(tenant_id: str, name: str, phone_number: str = "", address: str = "",
                  services: Optional[List[Tuple[str, int, int]]] = None, stylists: Optional[List[str]] = None,
                  phone: Optional[str] = None) -> Dict[str, Any]:
    init_db()
    actual_phone = phone or phone_number or ""
    srv_list = services or []
    st_list = stylists or []
    with DBConnectionContext() as db:
        now = datetime.now().isoformat()
        db.execute("""
            INSERT OR REPLACE INTO tenants (id, name, phone_number, address, currency, created_at)
            VALUES (?, ?, ?, ?, 'USD', ?)
        """, (tenant_id, name, actual_phone, address, now))

        for s_name, dur, pr in srv_list:
            s_id = f"{tenant_id}_{s_name.replace(' ', '_').lower()}"
            db.execute("""
                INSERT OR REPLACE INTO services (id, tenant_id, name, duration_minutes, price)
                VALUES (?, ?, ?, ?, ?)
            """, (s_id, tenant_id, s_name, dur, pr))

        for st_name in st_list:
            st_id = f"{tenant_id}_{st_name.lower()}"
            db.execute("""
                INSERT OR REPLACE INTO stylists (id, tenant_id, name, active)
                VALUES (?, ?, ?, 1)
            """, (st_id, tenant_id, st_name))

    return get_tenant(tenant_id) or {}


def get_tenant_services(tenant_id: str) -> List[Dict[str, Any]]:
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM services WHERE tenant_id = ?", (tenant_id,))
        return db.fetchall()


def get_tenant_stylists(tenant_id: str) -> List[Dict[str, Any]]:
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM stylists WHERE tenant_id = ? AND active = 1", (tenant_id,))
        return db.fetchall()


def check_slots_availability(date_str: str, service_name: str, preferred_time: Optional[str] = None,
                             tenant_id: str = DEFAULT_TENANT_ID) -> List[str]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT duration_minutes FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        service_row = db.fetchone()
        duration = service_row["duration_minutes"] if service_row else 45

        stylists = get_tenant_stylists(tenant_id)
        if not stylists:
            return []
        total_stylists = len(stylists)

        # Standard business hours: 9:00 AM to 6:00 PM
        work_start = datetime.strptime(f"{date_str} 09:00", "%Y-%m-%d %H:%M")
        work_end = datetime.strptime(f"{date_str} 18:00", "%Y-%m-%d %H:%M")

        all_slots = []
        current = work_start
        while current + timedelta(minutes=duration) <= work_end:
            all_slots.append(current)
            current += timedelta(minutes=30)

        # Query existing bookings
        start_bound = f"{date_str} 00:00:00"
        end_bound = f"{date_str} 23:59:59"
        db.execute("""
            SELECT start_time, end_time FROM appointments
            WHERE tenant_id = ? AND status = 'CONFIRMED' AND start_time BETWEEN ? AND ?
        """, (tenant_id, start_bound, end_bound))
        existing_bookings = db.fetchall()

    available_slots = []
    for slot_start in all_slots:
        slot_end = slot_start + timedelta(minutes=duration)
        overlapping_count = 0
        for b in existing_bookings:
            b_start = datetime.fromisoformat(b["start_time"].replace("Z", ""))
            b_end = datetime.fromisoformat(b["end_time"].replace("Z", ""))
            if (slot_start < b_end) and (slot_end > b_start):
                overlapping_count += 1
        if overlapping_count < total_stylists:
            available_slots.append(slot_start.strftime("%I:%M %p"))

    if preferred_time:
        pref = preferred_time.lower()
        if "morning" in pref:
            available_slots = [s for s in available_slots if "AM" in s]
        elif "afternoon" in pref:
            available_slots = [s for s in available_slots if "PM" in s and int(s.split(":")[0]) < 5]
        elif "evening" in pref:
            available_slots = [s for s in available_slots if "PM" in s and int(s.split(":")[0]) >= 5]

    return available_slots[:4]


def book_new_appointment(caller_name: str, caller_phone: str, service_name: str,
                         appointment_datetime: str, stylist_name: str = "Elena",
                         tenant_id: str = DEFAULT_TENANT_ID) -> Dict[str, Any]:
    init_db()
    dt_clean = appointment_datetime.replace("Z", "")
    start_dt = datetime.fromisoformat(dt_clean)

    with DBConnectionContext() as db:
        db.execute("SELECT duration_minutes, price FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        srv_row = db.fetchone()
        duration = srv_row["duration_minutes"] if srv_row else 45
        price = srv_row["price"] if srv_row else 75

        end_dt = start_dt + timedelta(minutes=duration)
        booking_id = f"LUXE-{start_dt.strftime('%m%d')}-{abs(hash(caller_phone + str(start_dt))) % 9000 + 1000}"
        now_str = datetime.now().isoformat()

        db.execute("""
            INSERT INTO appointments (id, tenant_id, caller_name, caller_phone, service_name, 
                                     stylist_name, start_time, end_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?)
        """, (booking_id, tenant_id, caller_name, caller_phone, service_name, 
              stylist_name, start_dt.isoformat(), end_dt.isoformat(), now_str))

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
    try:
        excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
        append_appointment_to_excel(booking_record, filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel sync bypassed: {e}")

    # 2. Sync to Live Google Sheet
    try:
        sync_appointment_to_google_sheets(booking_record, tenant_id=tenant_id)
    except Exception as e:
        logger.debug(f"Google Sheets sync bypassed: {e}")

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
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]
    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
            ORDER BY start_time DESC LIMIT 1
        """, (tenant_id, f"%{phone_clean}%"))
        row = db.fetchone()

    if row:
        start_dt = datetime.fromisoformat(row["start_time"].replace("Z", ""))
        return {
            "booking_id": row["id"],
            "caller_name": row["caller_name"],
            "service_name": row["service_name"],
            "stylist_name": row["stylist_name"],
            "start_time": start_dt.strftime("%A, %b %d at %I:%M %p")
        }
    return None


def reschedule_existing_appointment(
    caller_phone: str,
    new_datetime: str,
    booking_id: Optional[str] = None,
    new_stylist_name: Optional[str] = None,
    tenant_id: str = DEFAULT_TENANT_ID
) -> Optional[Dict[str, Any]]:
    init_db()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]

    with DBConnectionContext() as db:
        if booking_id:
            db.execute("SELECT * FROM appointments WHERE id = ? AND tenant_id = ?", (booking_id, tenant_id))
        else:
            db.execute("""
                SELECT * FROM appointments 
                WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
                ORDER BY start_time DESC LIMIT 1
            """, (tenant_id, f"%{phone_clean}%"))
        row = db.fetchone()

        if not row:
            return None

        actual_booking_id = row["id"]
        stylist = new_stylist_name or row["stylist_name"]
        service_name = row["service_name"]

        dt_clean = new_datetime.replace("Z", "")
        new_start_dt = datetime.fromisoformat(dt_clean)

        db.execute("SELECT duration_minutes, price FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        srv_row = db.fetchone()
        duration = srv_row["duration_minutes"] if srv_row else 45
        new_end_dt = new_start_dt + timedelta(minutes=duration)

        db.execute("""
            UPDATE appointments 
            SET start_time = ?, end_time = ?, stylist_name = ?, whatsapp_24h_sent = 0, call_1h_sent = 0
            WHERE id = ?
        """, (new_start_dt.isoformat(), new_end_dt.isoformat(), stylist, actual_booking_id))

    try:
        excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
        update_excel_reminders(actual_booking_id, status="CONFIRMED (RESCHEDULED)", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel update bypassed: {e}")

    return {
        "booking_id": actual_booking_id,
        "caller_name": row["caller_name"],
        "caller_phone": row["caller_phone"],
        "service_name": service_name,
        "stylist_name": stylist,
        "start_time": new_start_dt.strftime("%A, %b %d at %I:%M %p")
    }


def cancel_existing_appointment(caller_phone: str, booking_id: Optional[str] = None,
                                tenant_id: str = DEFAULT_TENANT_ID) -> bool:
    init_db()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]

    with DBConnectionContext() as db:
        if booking_id:
            db.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ? AND tenant_id = ?", (booking_id, tenant_id))
        else:
            db.execute("""
                UPDATE appointments SET status = 'CANCELLED' 
                WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
            """, (tenant_id, f"%{phone_clean}%"))
        updated = db.rowcount > 0

    if updated:
        try:
            excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
            update_excel_reminders(booking_id or "", status="CANCELLED", filepath=excel_path)
        except Exception as e:
            logger.debug(f"Excel cancel update bypassed: {e}")

    return updated


def list_all_appointments(tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    init_db()
    with DBConnectionContext() as db:
        if tenant_id:
            db.execute("SELECT * FROM appointments WHERE tenant_id = ? ORDER BY start_time DESC", (tenant_id,))
        else:
            db.execute("SELECT * FROM appointments ORDER BY start_time DESC")
        return db.fetchall()


def get_pending_24h_reminders() -> List[Dict[str, Any]]:
    now = datetime.now()
    window_start = (now + timedelta(hours=23)).isoformat()
    window_end = (now + timedelta(hours=25)).isoformat()

    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE status = 'CONFIRMED' 
              AND whatsapp_24h_sent = 0
              AND start_time BETWEEN ? AND ?
        """, (window_start, window_end))
        return db.fetchall()


def mark_24h_reminder_sent(booking_id: str):
    with DBConnectionContext() as db:
        db.execute("UPDATE appointments SET whatsapp_24h_sent = 1 WHERE id = ?", (booking_id,))
    try:
        excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
        update_excel_reminders(booking_id, whatsapp_24h="SENT", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel reminder update bypassed: {e}")


def get_pending_1h_call_reminders() -> List[Dict[str, Any]]:
    now = datetime.now()
    window_start = (now + timedelta(minutes=50)).isoformat()
    window_end = (now + timedelta(minutes=70)).isoformat()

    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE status = 'CONFIRMED' 
              AND call_1h_sent = 0
              AND start_time BETWEEN ? AND ?
        """, (window_start, window_end))
        return db.fetchall()


def mark_1h_call_sent(booking_id: str):
    with DBConnectionContext() as db:
        db.execute("UPDATE appointments SET call_1h_sent = 1 WHERE id = ?", (booking_id,))
    try:
        excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
        update_excel_reminders(booking_id, call_1h="CALLED", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel reminder update bypassed: {e}")
