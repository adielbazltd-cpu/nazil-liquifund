"""
crm.py — Nazil CRM module.
Handles all Supabase client operations.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from supabase import create_client, Client
import streamlit as st

STATUSES = ["ליד", "יצירת קשר", "פגישה", "הצעה", "חתימה", "סגור ✅", "לא רלוונטי ❌"]
STATUS_COLORS = {
    "ליד":             "#6666aa",
    "יצירת קשר":      "#0088ff",
    "פגישה":          "#f0a020",
    "הצעה":           "#f0c040",
    "חתימה":          "#00d4aa",
    "סגור ✅":         "#00e676",
    "לא רלוונטי ❌":  "#555555",
}
SOURCES = ["ישיר", "חבר/הפנייה", "פרסום", "רשתות חברתיות", "אתר", "אחר"]


@st.cache_resource
def _get_client() -> Optional[Client]:
    try:
        url = _secret("SUPABASE_URL")
        key = _secret("SUPABASE_KEY")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


def _secret(key: str) -> str:
    try:
        return st.secrets[key]
    except Exception:
        import os
        return os.getenv(key, "")


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def save_client(
    name: str, phone: str, email: str, id_number: str,
    total_balance: float, total_pitz: float, total_tagm: float,
    num_funds: int, net_to_bank: float, rec_prefer_loan: bool,
    advisor_fee: float, notes: str, fund_data: list,
    source: str = "ישיר",
) -> dict | None:
    sb = _get_client()
    if not sb:
        return None
    row = dict(
        name=name, phone=phone, email=email, id_number=id_number,
        total_balance=total_balance, total_pitz=total_pitz,
        total_tagm=total_tagm, num_funds=num_funds,
        net_to_bank=net_to_bank, rec_prefer_loan=rec_prefer_loan,
        advisor_fee=advisor_fee, notes=notes,
        status="ליד", fund_data=fund_data, source=source,
        call_log=[],
    )
    res = sb.table("clients").insert(row).execute()
    return res.data[0] if res.data else None


def create_lead(
    name: str, phone: str, email: str = "", source: str = "ישיר", notes: str = ""
) -> dict | None:
    """Create a manual lead without a pension file."""
    sb = _get_client()
    if not sb:
        return None
    row = dict(
        name=name, phone=phone, email=email,
        status="ליד", source=source, notes=notes,
        total_balance=0, total_pitz=0, total_tagm=0,
        num_funds=0, net_to_bank=0, rec_prefer_loan=False,
        advisor_fee=0, fund_data=None, call_log=[],
    )
    res = sb.table("clients").insert(row).execute()
    return res.data[0] if res.data else None


def add_call_log(client_id: str, note: str) -> None:
    sb = _get_client()
    if not sb or not note.strip():
        return
    client = sb.table("clients").select("call_log").eq("id", client_id).execute()
    log = client.data[0].get("call_log") or [] if client.data else []
    log.append({
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "note": note.strip(),
    })
    sb.table("clients").update({"call_log": log}).eq("id", client_id).execute()


def update_status(client_id: str, status: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").update({"status": status}).eq("id", client_id).execute()


def update_follow_up(client_id: str, follow_up: date | None) -> None:
    sb = _get_client()
    if sb:
        val = follow_up.isoformat() if follow_up else None
        sb.table("clients").update({"follow_up_date": val}).eq("id", client_id).execute()


def update_notes(client_id: str, notes: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").update({"notes": notes}).eq("id", client_id).execute()


def delete_client(client_id: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").delete().eq("id", client_id).execute()


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_all_clients() -> list[dict]:
    sb = _get_client()
    if not sb:
        return []
    res = sb.table("clients").select("*").order("created_at", desc=True).execute()
    return res.data or []
