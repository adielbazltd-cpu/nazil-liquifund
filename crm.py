"""
crm.py — Nazil CRM module.
Handles all Supabase client operations.
"""

from __future__ import annotations
from typing import Optional
from supabase import create_client, Client
import streamlit as st

STATUSES = ["ליד", "פגישה", "הצעה", "חתימה", "סגור"]
STATUS_COLORS = {
    "ליד":    "#555580",
    "פגישה":  "#0088ff",
    "הצעה":   "#f0c040",
    "חתימה":  "#00d4aa",
    "סגור":   "#00e676",
}


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


def save_client(
    name: str,
    phone: str,
    email: str,
    id_number: str,
    total_balance: float,
    total_pitz: float,
    total_tagm: float,
    num_funds: int,
    net_to_bank: float,
    rec_prefer_loan: bool,
    advisor_fee: float,
    notes: str,
    fund_data: list,
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
        status="ליד", fund_data=fund_data,
    )
    res = sb.table("clients").insert(row).execute()
    return res.data[0] if res.data else None


def get_all_clients() -> list[dict]:
    sb = _get_client()
    if not sb:
        return []
    res = sb.table("clients").select("*").order("created_at", desc=True).execute()
    return res.data or []


def update_status(client_id: str, status: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").update({"status": status}).eq("id", client_id).execute()


def update_notes(client_id: str, notes: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").update({"notes": notes}).eq("id", client_id).execute()


def delete_client(client_id: str) -> None:
    sb = _get_client()
    if sb:
        sb.table("clients").delete().eq("id", client_id).execute()
