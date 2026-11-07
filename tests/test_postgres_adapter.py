"""
Unit Tests for Neon PostgreSQL / Universal Database Adapter.
Verifies:
- URL parsing and normalization (postgres:// -> postgresql://)
- is_postgres() logic
- DBConnectionContext abstraction
- Safe file paths on serverless (Vercel / Lambda)
"""

import os
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database import (
    get_database_url,
    is_postgres,
    get_sqlite_path,
    get_excel_path,
    DBConnectionContext,
    init_db,
    create_tenant,
    get_tenant,
    check_slots_availability,
    book_new_appointment,
    lookup_by_phone,
    list_all_appointments
)


def test_postgres_detection_and_url_normalization(monkeypatch):
    monkeypatch.delenv("SALON_DB_PATH", raising=False)
    monkeypatch.delenv("NEON_POSTGRES_CONNECTION_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@ep-demo.us-east-2.aws.neon.tech/neondb")
    assert is_postgres() is True
    normalized = get_database_url()
    assert normalized.startswith("postgresql://")
    assert "ep-demo.us-east-2.aws.neon.tech" in normalized

    # Neon custom URL key
    monkeypatch.delenv("DATABASE_URL")
    monkeypatch.setenv("NEON_DATABASE_URL", "postgresql://neondb_owner:secret@ep-cool.aws.neon.tech/neondb?sslmode=require")
    assert is_postgres() is True
    assert "ep-cool.aws.neon.tech" in get_database_url()


def test_sqlite_fallback_and_serverless_safe_path(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("NEON_DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("SALON_DB_PATH", raising=False)
    monkeypatch.delenv("SALON_EXCEL_PATH", raising=False)

    # Local mode
    monkeypatch.delenv("VERCEL", raising=False)
    assert get_sqlite_path() == "salon_bookings.db"
    assert get_excel_path() == "salon_appointments.xlsx"

    # Serverless Vercel mode
    monkeypatch.setenv("VERCEL", "1")
    assert get_sqlite_path() == "/tmp/salon_bookings.db"
    assert get_excel_path() == "/tmp/salon_appointments.xlsx"


def test_universal_db_lifecycle(tmp_path, monkeypatch):
    # Test full lifecycle on clean DB
    test_db = str(tmp_path / "test_lifecycle.db")
    monkeypatch.setenv("SALON_DB_PATH", test_db)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("NEON_DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)

    init_db()

    # Create tenant
    t = create_tenant(
        tenant_id="neon_test_tenant",
        name="Neon Test Medical Spa",
        phone="+15554443322",
        address="100 Neon Blvd",
        services=[("Hydrafacial", 60, 150)],
        stylists=["Dr. Chloe"]
    )
    assert t["id"] == "neon_test_tenant"

    # Verify lookup
    retrieved = get_tenant("neon_test_tenant")
    assert retrieved["name"] == "Neon Test Medical Spa"

    # Check slots
    slots = check_slots_availability("2026-11-20", "Hydrafacial", "Dr. Chloe", tenant_id="neon_test_tenant")
    assert len(slots) > 0

    # Book appointment
    booking = book_new_appointment(
        caller_name="Alice Wonder",
        caller_phone="+15554443322",
        service_name="Hydrafacial",
        appointment_datetime="2026-11-20T10:00:00",
        stylist_name="Dr. Chloe",
        tenant_id="neon_test_tenant"
    )
    assert "booking_id" in booking

    # Lookup
    found = lookup_by_phone("+15554443322", tenant_id="neon_test_tenant")
    assert found is not None
    assert found["caller_name"] == "Alice Wonder"

    # List
    all_appts = list_all_appointments(tenant_id="neon_test_tenant")
    assert len(all_appts) == 1

