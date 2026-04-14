"""
app.py — Nazil | LiquiFund Platform
Production-ready: password gate, zero-footprint parsing, legal gating, GDPR-style cleanup.
"""

import hmac
import os
import xml.etree.ElementTree as ET
import streamlit as st
import pandas as pd

from maslaka_parser import parse_maslaka_bytes
from pdf_generator import generate_report_pdf
import crm
import email_sender
from datetime import date as _date

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Nazil | ניתוח קרנות פנסיה",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TAX_RATE           = 0.35
TAX_FREE_THRESHOLD = 8_000
DEFAULT_FUND_RETURN = 7.0
DEFAULT_PRIME       = 4.5
DEFAULT_SPREAD      = 1.0
def _get_secret(key: str, default: str) -> str:
    """Read from st.secrets (Streamlit Cloud) with fallback to env var, then default."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

_APP_PASSWORD  = _get_secret("NAZIL_PASSWORD",   "Nazil2026")
_AGENT_CODE_TV = _get_secret("NAZIL_AGENT_CODE", "agent2026")

LEGAL_DISCLAIMER = (
    "המידע המוצג מבוסס על נתוני המסלקה הפנסיונית ומהווה סימולציה בלבד. "
    "אין לראות במידע זה ייעוץ פנסיוני או תחליף לייעוץ השקעות המותאם אישית. "
    "ביצוע פעולות במוצר פנסיוני עלול לפגוע בקצבת הפרישה וברצף הביטוחי."
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
  html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0d;
    color: #e8e8e8;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  html { direction: rtl; }
  [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
  .stMarkdown, .stDataFrame, label, p, h1, h2, h3, h4, span {
    direction: rtl; text-align: right;
  }
  [data-testid="stSidebar"] {
    background-color: #161616; border-left: 1px solid #2a2a2a;
  }
  .lf-header {
    font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #00d4aa, #0088ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
  }
  .lf-subheader { font-size: 0.95rem; color: #666; margin-bottom: 2rem; }
  [data-testid="stFileUploader"] {
    background: #161616; border: 1.5px dashed #2a2a2a;
    border-radius: 12px; padding: 1rem;
  }
  .net-metric {
    background: #0a1f1a; border: 1px solid #00d4aa33;
    border-radius: 14px; padding: 1.4rem 1.6rem; margin-top: 1rem;
  }
  .net-metric .label { font-size: 0.8rem; color: #888; margin-bottom: 0.3rem; }
  .net-metric .value { font-size: 2rem; font-weight: 700; color: #00d4aa; letter-spacing: -1px; }
  .net-metric .note  { font-size: 0.75rem; color: #555; margin-top: 0.4rem; }
  .lf-divider { border: none; border-top: 1px solid #222; margin: 1.5rem 0; }
  .stat-card {
    background: #161616; border: 1px solid #252525;
    border-radius: 12px; padding: 1rem 1.2rem; text-align: right;
  }
  .stat-card .s-label { font-size: 0.78rem; color: #666; }
  .stat-card .s-value { font-size: 1.5rem; font-weight: 600; color: #e8e8e8; }
  .stat-card .s-sub   { font-size: 0.78rem; color: #444; margin-top: 2px; }
  .rec-box { border-radius: 12px; padding: 1.2rem 1.4rem; border-right: 4px solid; margin: 1rem 0; }
  .rec-loan     { background: #071a14; border-color: #00d4aa; }
  .rec-withdraw { background: #1a0707; border-color: #e05555; }
  .rec-box .rec-headline { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.4rem; }
  .rec-box .rec-detail   { font-size: 0.88rem; color: #aaa; }
  .rec-box .rec-note     { font-size: 0.78rem; color: #666; margin-top: 0.5rem; }
  .alert-row {
    background: #1a1500; border: 1px solid #665500;
    border-radius: 8px; padding: 0.65rem 1rem;
    margin-bottom: 0.4rem; font-size: 0.85rem; color: #f0c040;
  }
  /* Legal checkbox highlight */
  .legal-box {
    background: #0d1a2a; border: 1px solid #1a4a7a;
    border-radius: 10px; padding: 1rem 1.2rem; margin: 1rem 0;
  }
  /* Sticky legal footer */
  .legal-footer {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: rgba(10,10,10,0.97); border-top: 1px solid #1e1e1e;
    padding: 0.45rem 2rem; font-size: 0.69rem; color: #444;
    text-align: right; direction: rtl; z-index: 999;
  }
  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { background: #161616; border-radius: 10px; padding: 4px; gap: 4px; }
  .stTabs [data-baseweb="tab"] { background: transparent; color: #666; border-radius: 7px; padding: 6px 16px; }
  .stTabs [aria-selected="true"] { background: #252525 !important; color: #00d4aa !important; }
  /* Calc result cards */
  .calc-result {
    background: #0a1a14; border: 1px solid #00d4aa22;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.8rem;
  }
  .calc-result .cr-label { font-size: 0.78rem; color: #666; }
  .calc-result .cr-value { font-size: 1.6rem; font-weight: 700; color: #00e676; letter-spacing: -0.5px; }
  .calc-result .cr-note  { font-size: 0.75rem; color: #444; margin-top: 4px; }
  .saving-card { background: #071a0e; border: 1px solid #00e67644; border-radius: 10px; padding: 0.9rem 1.1rem; margin-top: 0.8rem; }
  /* Login screen */
  .login-card {
    max-width: 380px; margin: 5rem auto;
    background: #161616; border: 1px solid #252525;
    border-radius: 16px; padding: 2.5rem 2rem; text-align: center;
  }
  .login-card .lock { font-size: 2.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------

def compute_arbitrage(
    pitzuim_total: float,
    fund_return_pct: float,
    prime_pct: float,
    spread_pct: float,
) -> dict:
    loan_rate        = prime_pct + spread_pct
    annual_advantage = fund_return_pct - loan_rate
    prefer_loan      = annual_advantage > 0
    net_withdrawal   = pitzuim_total * (1 - TAX_RATE)
    tax_cost_ils     = pitzuim_total * TAX_RATE

    if prefer_loan and annual_advantage > 0:
        break_even = round(TAX_RATE * 100 / annual_advantage, 1)
        note = f"נקודת איזון: כ-{break_even} שנים לכיסוי קנס המס דרך עודף התשואה"
    else:
        break_even = None
        note = f"נטו לאחר משיכה: ₪{net_withdrawal:,.0f} (חיסכון מס: ₪{tax_cost_ils:,.0f})"

    return {
        "prefer_loan":      prefer_loan,
        "loan_rate":        loan_rate,
        "fund_return":      fund_return_pct,
        "annual_advantage": annual_advantage,
        "net_withdrawal":   net_withdrawal,
        "break_even_years": break_even,
        "headline": (
            "✅ הלוואה עדיפה — השאר את הכסף בקרן"
            if prefer_loan else
            "⚠️ משיכה עדיפה — ריבית ההלוואה גבוהה מתשואת הקרן"
        ),
        "detail": (
            f"תשואת הקרן ({fund_return_pct:.1f}%) גבוהה מריבית ההלוואה ({loan_rate:.1f}%) "
            f"ב-{annual_advantage:.1f}% לשנה — כדאי לשמור את הכסף מושקע"
            if prefer_loan else
            f"ריבית ההלוואה ({loan_rate:.1f}%) גבוהה מתשואת הקרן ({fund_return_pct:.1f}%) — "
            f"קנס המס ({int(TAX_RATE*100)}%) עשוי להיות זול יותר"
        ),
        "note": note,
    }


def scan_alerts(funds: list[dict]) -> list[str]:
    return [
        f"{f['company_name']} ({f['fund_type']}) — "
        f"יתרה ₪{f['total_balance']:,.0f} | זכאי למשיכה פטורה ממס (מתחת לסף ₪{TAX_FREE_THRESHOLD:,})"
        for f in funds
        if 0 < f["total_balance"] < TAX_FREE_THRESHOLD
    ]


# ---------------------------------------------------------------------------
# Calculator 1 — Effective Tax Rate
# ---------------------------------------------------------------------------
def calc_effective_tax(total_pitzuim: float, exempt_amount: float) -> dict:
    """
    Weighted effective tax: only the portion above the exempt ceiling is taxed.
    Shows the client their *real* tax rate is far below 35%.
    """
    exempt        = min(exempt_amount, total_pitzuim)
    taxable       = max(0.0, total_pitzuim - exempt)
    tax_amount    = taxable * TAX_RATE
    effective_pct = (tax_amount / total_pitzuim * 100) if total_pitzuim > 0 else 0.0
    return {
        "total_pitzuim": total_pitzuim,
        "exempt":        exempt,
        "taxable":       taxable,
        "tax_amount":    tax_amount,
        "effective_pct": effective_pct,
        "net":           total_pitzuim - tax_amount,
    }


# ---------------------------------------------------------------------------
# Calculator 2 — Loan Monthly Repayment
# ---------------------------------------------------------------------------
def calc_loan(principal: float, annual_rate_pct: float, months: int) -> dict:
    """Standard amortizing loan: P × r(1+r)^n / ((1+r)^n − 1)."""
    r = annual_rate_pct / 100 / 12
    if r == 0 or months == 0:
        monthly = principal / max(months, 1)
    else:
        monthly = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    total_paid     = monthly * months
    total_interest = total_paid - principal
    return {
        "principal":      principal,
        "monthly":        monthly,
        "total_paid":     total_paid,
        "total_interest": total_interest,
        "annual_rate":    annual_rate_pct,
        "months":         months,
    }


# ---------------------------------------------------------------------------
# Calculator 3 — Debt Consolidation / Swap
# ---------------------------------------------------------------------------
def calc_debt_swap(
    debt: float,
    current_rate_pct: float,
    pension_rate_pct: float,
    months: int,
) -> dict:
    """Compare bank overdraft/loan cost vs. pension loan cost."""
    def _monthly(p: float, apr: float, n: int) -> float:
        r = apr / 100 / 12
        if r == 0 or n == 0:
            return p / max(n, 1)
        return p * r * (1 + r) ** n / ((1 + r) ** n - 1)

    current_monthly  = _monthly(debt, current_rate_pct, months)
    pension_monthly  = _monthly(debt, pension_rate_pct, months)
    monthly_saving   = current_monthly - pension_monthly
    total_saving     = monthly_saving * months
    # Withdrawal alternative: pay 35% tax once, no monthly cost → amortised monthly "saving"
    withdrawal_tax   = debt * TAX_RATE
    withdrawal_monthly_saving = current_monthly - (withdrawal_tax / months)
    return {
        "debt":                      debt,
        "current_rate":              current_rate_pct,
        "pension_rate":              pension_rate_pct,
        "current_monthly":           current_monthly,
        "pension_monthly":           pension_monthly,
        "monthly_saving":            monthly_saving,
        "total_saving":              total_saving,
        "withdrawal_tax":            withdrawal_tax,
        "withdrawal_monthly_saving": withdrawal_monthly_saving,
        "months":                    months,
    }


def _clear_session() -> None:
    """Wipe all client financial data from session state."""
    for key in ("funds", "alerts", "rec", "legal_accepted"):
        st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# ── GATE 1: Password ─────────────────────────────────────────────────────
# ---------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-card">
      <div class="lock">🔐</div>
      <div style="font-size:1.6rem;font-weight:700;color:#e8e8e8;margin-bottom:.3rem">Nazil</div>
      <div style="font-size:.85rem;color:#555;margin-bottom:1.5rem">מערכת מוגנת — נדרשת סיסמה לכניסה</div>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1, 1])
    with center:
        pwd = st.text_input("סיסמה", type="password", label_visibility="collapsed",
                            placeholder="הזן סיסמה...")
        if st.button("כניסה למערכת", type="primary", use_container_width=True):
            # Constant-time comparison — prevents timing-based brute-force
            if hmac.compare_digest(pwd.encode(), _APP_PASSWORD.encode()):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("סיסמה שגויה. נסה שנית.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧮 חישובים מהירים")
    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

    st.markdown("### מחשבון משיכה נטו")
    gross = st.number_input("סכום ברוטו (₪)", min_value=0.0,
                            value=100_000.0, step=1_000.0, format="%.0f")
    tax_exempt = st.toggle("פטור ממס?", value=False)

    if tax_exempt:
        sidebar_net, sidebar_note = gross, "✅ פטור ממס הוחל — אין ניכוי"
    else:
        deducted    = gross * TAX_RATE
        sidebar_net = gross - deducted
        sidebar_note = f"מס ניכוי (35%): ₪{deducted:,.0f}"

    st.markdown(f"""
    <div class="net-metric">
      <div class="label">סכום נטו לאחר מס</div>
      <div class="value">₪{sidebar_net:,.0f}</div>
      <div class="note">{sidebar_note}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

    st.markdown("### הגדרות ארביטראז'")
    fund_return = st.number_input("תשואת קרן משוערת (%)", min_value=0.0,
                                  max_value=20.0, value=DEFAULT_FUND_RETURN,
                                  step=0.1, format="%.1f")
    prime_rate  = st.number_input("ריבית פריים (%)", min_value=0.0,
                                  max_value=15.0, value=DEFAULT_PRIME,
                                  step=0.1, format="%.1f")
    spread      = st.number_input("מרווח ריבית (% מעל פריים)", min_value=0.0,
                                  max_value=5.0, value=DEFAULT_SPREAD,
                                  step=0.25, format="%.2f")
    st.caption(f"ריבית הלוואה אפקטיבית: **{prime_rate + spread:.2f}%**")

    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

    if st.button("🗑️ נקה נתוני לקוח", use_container_width=True):
        _clear_session()
        st.rerun()

    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)
    _page = st.radio("ניווט", ["ניתוח לקוח", "ניהול לקוחות"],
                     horizontal=True, label_visibility="collapsed",
                     key="main_nav")

    st.markdown(
        '<span style="color:#333;font-size:0.7rem;">Nazil | LiquiFund v1.0 · כל הזכויות שמורות</span>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# CRM page — renders and stops if selected
# ---------------------------------------------------------------------------
if st.session_state.get("main_nav") == "ניהול לקוחות":
    st.markdown('<div class="lf-header">Nazil 📋</div>', unsafe_allow_html=True)
    st.markdown('<div class="lf-subheader">ניהול לקוחות · מקצה לקצה</div>', unsafe_allow_html=True)

    clients = crm.get_all_clients()
    today   = _date.today()

    # ── Alerts bar ───────────────────────────────────────────────────────
    followups_today = [c for c in clients
                       if c.get("follow_up_date") and str(c["follow_up_date"])[:10] <= str(today)
                       and c.get("status") not in ("סגור ✅","לא רלוונטי ❌")]
    unpaid = [c for c in clients
              if c.get("status") == "סגור ✅"
              and c.get("payment_status","טרם שולם") != "שולם מלא"]

    if followups_today or unpaid:
        alert_cols = st.columns(2)
        with alert_cols[0]:
            if followups_today:
                st.warning(f"⏰ **{len(followups_today)} פולו-אפ** ממתין היום: " +
                           " · ".join(c.get("name","") for c in followups_today[:3]))
        with alert_cols[1]:
            if unpaid:
                st.error(f"💸 **{len(unpaid)} עסקאות סגורות** ללא תשלום מלא: " +
                         " · ".join(c.get("name","") for c in unpaid[:3]))

    # ── Pipeline summary ──────────────────────────────────────────────────
    pipeline_cols = st.columns(len(crm.STATUSES))
    for col, status in zip(pipeline_cols, crm.STATUSES):
        count     = sum(1 for c in clients if c.get("status") == status)
        total_val = sum(c.get("total_balance",0) for c in clients if c.get("status") == status)
        color     = crm.STATUS_COLORS.get(status, "#555")
        with col:
            st.markdown(f"""
<div style="background:#161616;border:1px solid #252525;border-top:3px solid {color};
     border-radius:10px;padding:.7rem .5rem;text-align:center;margin-bottom:.5rem">
  <div style="font-size:.65rem;color:#666;margin-bottom:.2rem">{status}</div>
  <div style="font-size:1.5rem;font-weight:700;color:{color};line-height:1">{count}</div>
  {f'<div style="font-size:.6rem;color:#444;margin-top:.2rem">₪{total_val:,.0f}</div>' if total_val else ''}
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

    # ── Main tabs ─────────────────────────────────────────────────────────
    crm_tab_list, crm_tab_new = st.tabs(["רשימת לקוחות", "הוסף ליד חדש"])

    # ════════════════════════════════════════════════════════════════════
    with crm_tab_new:
        st.markdown("#### ליד חדש")
        with st.form("new_lead_form"):
            nl1, nl2 = st.columns(2)
            with nl1:
                nl_name   = st.text_input("שם מלא *")
                nl_phone  = st.text_input("טלפון *")
            with nl2:
                nl_email  = st.text_input("אימייל")
                nl_source = st.selectbox("מקור הליד", crm.SOURCES)
            nl_notes = st.text_area("הערת פתיחה", height=70,
                                    placeholder="צורך, דחיפות, רקע...")
            if st.form_submit_button("הוסף ליד", type="primary", use_container_width=True):
                if not nl_name or not nl_phone:
                    st.warning("שם וטלפון הם שדות חובה.")
                else:
                    if crm.create_lead(nl_name, nl_phone, nl_email, nl_source, nl_notes):
                        st.success(f"הליד **{nl_name}** נוסף!")
                        st.rerun()
                    else:
                        st.error("שגיאה בשמירה.")

    # ════════════════════════════════════════════════════════════════════
    with crm_tab_list:
        f1, f2, f3 = st.columns([3, 2, 2])
        with f1:
            search = st.text_input("🔍", placeholder="חיפוש שם / טלפון / מייל...",
                                   label_visibility="collapsed", key="crm_search")
        with f2:
            status_filter = st.selectbox("סטטוס", ["הכל"] + crm.STATUSES,
                                         label_visibility="collapsed", key="crm_sf")
        with f3:
            source_filter = st.selectbox("מקור", ["הכל"] + crm.SOURCES,
                                         label_visibility="collapsed", key="crm_src")

        filtered = [
            c for c in clients
            if (not search or search.lower() in
                (c.get("name","") + c.get("phone","") + c.get("email","")).lower())
            and (status_filter == "הכל" or c.get("status") == status_filter)
            and (source_filter == "הכל" or c.get("source","") == source_filter)
        ]
        st.caption(f"{len(filtered)} לקוחות")

        if not filtered:
            st.info("אין לקוחות.")
        else:
            for c in filtered:
                cid     = c["id"]
                status  = c.get("status", "ליד")
                color   = crm.STATUS_COLORS.get(status, "#555")
                bal     = c.get("total_balance", 0)
                follow  = c.get("follow_up_date","") or ""
                pstatus = c.get("payment_status","טרם שולם")
                logs    = c.get("call_log") or []
                subs    = c.get("submissions") or {}

                pay_icon  = "💸" if status == "סגור ✅" and pstatus != "שולם מלא" else ""
                fup_icon  = "⏰" if follow and str(follow)[:10] <= str(today) else ""
                bal_str   = f" · ₪{bal:,.0f}" if bal else ""

                with st.expander(
                    f"{pay_icon}{fup_icon} **{c.get('name','ללא שם')}** · "
                    f"{c.get('phone','')} · [{status}]{bal_str}"
                ):
                    # ── Client tabs ───────────────────────────────────────
                    t1,t2,t3,t4,t5 = st.tabs(["סקירה","יומן שיחות","מיילים","תשלום","הגשה לגופים"])

                    # ── Tab 1: Overview ───────────────────────────────────
                    with t1:
                        st.markdown("**עדכן סטטוס:**")
                        btn_cols = st.columns(len(crm.STATUSES))
                        for bcol, s in zip(btn_cols, crm.STATUSES):
                            with bcol:
                                if st.button(s, key=f"sb_{cid}_{s}",
                                             type="primary" if status==s else "secondary",
                                             use_container_width=True):
                                    if s != status:
                                        crm.update_status(cid, s)
                                        st.rerun()

                        if bal:
                            st.markdown("<div style='margin:.6rem 0'></div>",
                                        unsafe_allow_html=True)
                            fd1,fd2,fd3,fd4 = st.columns(4)
                            for fc,lbl,val in [
                                (fd1,'סה"כ נכסים', f"₪{bal:,.0f}"),
                                (fd2,"פיצויים",     f"₪{c.get('total_pitz',0):,.0f}"),
                                (fd3,"תגמולים",     f"₪{c.get('total_tagm',0):,.0f}"),
                                (fd4,"נטו לחשבון",  f"₪{c.get('net_to_bank',0):,.0f}"),
                            ]:
                                with fc:
                                    st.markdown(f"""
<div class="stat-card" style="padding:.5rem .7rem">
  <div class="s-label">{lbl}</div>
  <div class="s-value" style="font-size:.9rem">{val}</div>
</div>""", unsafe_allow_html=True)

                        if st.button("🗑 מחק לקוח", key=f"del_{cid}", type="secondary"):
                            crm.delete_client(cid)
                            st.rerun()

                    # ── Tab 2: Call log ───────────────────────────────────
                    with t2:
                        if logs:
                            for entry in reversed(logs):
                                st.markdown(f"""
<div style="background:#0d0d0d;border-right:3px solid #00d4aa;border-radius:6px;
     padding:.5rem .8rem;margin-bottom:.4rem">
  <div style="font-size:.7rem;color:#555">{entry.get('date','')}</div>
  <div style="font-size:.85rem;color:#ccc">{entry.get('note','')}</div>
</div>""", unsafe_allow_html=True)
                        else:
                            st.caption("אין שיחות עדיין.")

                        with st.form(f"call_form_{cid}"):
                            new_note = st.text_area(
                                "סיכום שיחה", height=90,
                                placeholder="מה עלה? מה ההחלטה? השלב הבא?",
                                key=f"cn_{cid}")
                            n1,n2 = st.columns([3,1])
                            with n1:
                                follow_val = st.date_input("תזכורת מעקב",
                                                           value=None, key=f"fu_{cid}")
                            with n2:
                                st.markdown("<div style='margin-top:1.7rem'></div>",
                                            unsafe_allow_html=True)
                                save_note = st.form_submit_button("שמור", type="primary",
                                                                   use_container_width=True)
                        if save_note:
                            if new_note.strip():
                                crm.add_call_log(cid, new_note)
                            if follow_val:
                                crm.update_follow_up(cid, follow_val)
                            st.rerun()

                    # ── Tab 3: Emails & Contracts ─────────────────────────
                    with t3:
                        from pdf_generator import generate_contract_pdf
                        client_email = c.get("email","")
                        if not client_email:
                            st.warning("אין כתובת מייל ללקוח זה.")
                        else:
                            st.caption(f"שולח אל: {client_email}")

                        em1, em2 = st.columns(2)
                        with em1:
                            st.markdown("**שלח דוח PDF**")
                            if st.button("📧 שלח דוח ניתוח", key=f"email_pdf_{cid}",
                                         disabled=not client_email):
                                # Build PDF from stored fund_data
                                _pdf_bytes = None
                                _fund_data = c.get("fund_data") or []
                                if _fund_data:
                                    try:
                                        _rec = compute_arbitrage(
                                            pitzuim_total=float(c.get("total_pitz", 0)),
                                            fund_return_pct=DEFAULT_FUND_RETURN,
                                            prime_pct=DEFAULT_PRIME,
                                            spread_pct=DEFAULT_SPREAD,
                                        )
                                        _alerts = scan_alerts(_fund_data)
                                        _pdf_bytes = generate_report_pdf(
                                            funds=_fund_data,
                                            rec=_rec,
                                            alerts=_alerts,
                                        )
                                    except Exception:
                                        _pdf_bytes = None
                                body = email_sender.template_report(c.get("name","לקוח"))
                                ok, err = email_sender.send_email(
                                    client_email,
                                    "דוח ניתוח פנסיה אישי — Nazil",
                                    body,
                                    attachment_bytes=_pdf_bytes,
                                    attachment_name="nazil_report.pdf" if _pdf_bytes else None,
                                )
                                if ok:
                                    crm.add_call_log(cid, "📧 נשלח דוח PDF במייל")
                                    st.success("נשלח!")
                                else:
                                    st.error(f"שגיאה: {err}")

                        with em2:
                            st.markdown("**פולו-אפ ידני**")
                            with st.form(f"email_fup_{cid}"):
                                fup_msg = st.text_area("תוכן ההודעה", height=80,
                                                       key=f"fup_msg_{cid}")
                                if st.form_submit_button("שלח מייל", type="primary",
                                                          use_container_width=True,
                                                          disabled=not client_email):
                                    body = email_sender.template_followup(
                                        c.get("name","לקוח"), fup_msg)
                                    ok, err = email_sender.send_email(
                                        client_email, "עדכון מ-Nazil", body)
                                    if ok:
                                        crm.add_call_log(cid, f"📧 נשלח מייל: {fup_msg[:60]}")
                                        st.success("נשלח!")
                                    else:
                                        st.error(f"שגיאה: {err}")

                        st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)
                        st.markdown("**📝 הסכם שירות לחתימה**")

                        contract_signed = bool(c.get("contract_signed", False))
                        signed_label = "✅ חתום" if contract_signed else "⏳ ממתין לחתימה"
                        signed_color = "#00e676" if contract_signed else "#f0c040"
                        st.markdown(
                            f'<span style="color:{signed_color};font-size:.85rem">'
                            f'סטטוס חוזה: <strong>{signed_label}</strong></span>',
                            unsafe_allow_html=True,
                        )

                        contr_col1, contr_col2, contr_col3 = st.columns(3)

                        with contr_col1:
                            # Download button — always available
                            try:
                                contract_bytes = generate_contract_pdf(
                                    client_name=c.get("name","לקוח"),
                                    id_number=c.get("id_number",""),
                                    phone=c.get("phone",""),
                                    email=client_email,
                                    advisor_fee=float(c.get("advisor_fee",0)),
                                )
                                st.download_button(
                                    "⬇️ הורד חוזה PDF",
                                    data=contract_bytes,
                                    file_name=f"contract_{c.get('name','client').replace(' ','_')}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_contract_{cid}",
                                    use_container_width=True,
                                )
                            except Exception as ex:
                                st.error(f"שגיאה ביצירת PDF: {ex}")
                                contract_bytes = None

                        with contr_col2:
                            if st.button("📨 שלח חוזה למייל", key=f"send_contract_{cid}",
                                         disabled=not client_email,
                                         use_container_width=True):
                                try:
                                    cb = generate_contract_pdf(
                                        client_name=c.get("name","לקוח"),
                                        id_number=c.get("id_number",""),
                                        phone=c.get("phone",""),
                                        email=client_email,
                                        advisor_fee=float(c.get("advisor_fee",0)),
                                    )
                                    body = email_sender.template_contract(c.get("name","לקוח"))
                                    ok, err = email_sender.send_email(
                                        client_email,
                                        "הסכם שירות לחתימה — Nazil",
                                        body,
                                        attachment_bytes=cb,
                                        attachment_name="contract_nazil.pdf",
                                    )
                                    if ok:
                                        crm.add_call_log(cid, "📝 נשלח חוזה לחתימה במייל")
                                        st.success("החוזה נשלח!")
                                    else:
                                        st.error(f"שגיאה: {err}")
                                except Exception as ex:
                                    st.error(f"שגיאה: {ex}")

                        with contr_col3:
                            new_signed = st.toggle(
                                "סמן כחתום",
                                value=contract_signed,
                                key=f"contract_toggle_{cid}",
                            )
                            if new_signed != contract_signed:
                                crm.update_contract_status(cid, new_signed)
                                crm.add_call_log(cid, "📝 חוזה סומן כחתום" if new_signed else "📝 חוזה סומן כלא חתום")
                                st.rerun()

                    # ── Tab 4: Payment ────────────────────────────────────
                    with t4:
                        pay_col, pay_status_col = st.columns(2)
                        with pay_col:
                            pcolor = {"שולם מלא":"#00e676","שולם חלקית":"#f0c040",
                                      "טרם שולם":"#e05555"}.get(pstatus,"#555")
                            st.markdown(f"""
<div style="background:#161616;border:1px solid #252525;border-radius:12px;
     padding:1rem 1.2rem;text-align:center">
  <div style="font-size:.75rem;color:#666">סטטוס תשלום</div>
  <div style="font-size:1.4rem;font-weight:700;color:{pcolor}">{pstatus}</div>
  <div style="font-size:.8rem;color:#555;margin-top:.3rem">
    שולם: ₪{c.get('payment_amount',0):,.0f}
  </div>
</div>""", unsafe_allow_html=True)

                        with pay_status_col:
                            with st.form(f"pay_form_{cid}"):
                                new_pstatus = st.selectbox(
                                    "עדכן סטטוס תשלום",
                                    ["טרם שולם","שולם חלקית","שולם מלא"],
                                    index=["טרם שולם","שולם חלקית","שולם מלא"].index(
                                        pstatus) if pstatus in ["טרם שולם","שולם חלקית","שולם מלא"] else 0,
                                    key=f"ps_{cid}"
                                )
                                new_pamount = st.number_input(
                                    "סכום ששולם (₪)", min_value=0.0,
                                    value=float(c.get("payment_amount",0)),
                                    step=100.0, key=f"pa_{cid}")
                                new_pdue = st.date_input(
                                    "תאריך יעד לתשלום",
                                    value=None, key=f"pd_{cid}")
                                if st.form_submit_button("עדכן תשלום", type="primary",
                                                          use_container_width=True):
                                    crm.update_payment(cid, new_pstatus, new_pamount,
                                                       new_pdue)
                                    crm.add_call_log(cid,
                                        f"💸 עודכן תשלום: {new_pstatus} | ₪{new_pamount:,.0f}")
                                    st.rerun()

                    # ── Tab 5: Submissions ────────────────────────────────
                    with t5:
                        st.caption("עקוב אחר הגשת מסמכים לכל גוף פנסיוני")
                        BODIES = [
                            ("מנורה מבטחים", "https://www.menora-mivt.co.il"),
                            ("הפניקס",        "https://www.phoenix.co.il"),
                            ("מגדל",          "https://www.migdal.co.il"),
                            ("הראל",          "https://www.harel.co.il"),
                            ("כלל ביטוח",     "https://www.clal.co.il"),
                            ("הכשרה",         "https://www.hachshara-ins.co.il"),
                            ("אלטשולר שחם",   "https://www.altshul.co.il"),
                            ("מיטב",          "https://www.meitav.co.il"),
                            ("ילין לפידות",   "https://www.yelin-lapidot.co.il"),
                        ]
                        updated_subs = dict(subs)
                        changed = False
                        for body_name, body_url in BODIES:
                            col_check, col_link = st.columns([3, 1])
                            with col_check:
                                checked = st.checkbox(
                                    f"הוגש — {body_name}",
                                    value=bool(subs.get(body_name)),
                                    key=f"sub_{cid}_{body_name}"
                                )
                                if checked != bool(subs.get(body_name)):
                                    updated_subs[body_name] = checked
                                    changed = True
                            with col_link:
                                st.markdown(
                                    f"[כניסה לאתר]({body_url})",
                                    unsafe_allow_html=False
                                )
                        if changed:
                            crm.update_submissions(cid, updated_subs)
                            st.rerun()

                        submitted_count = sum(1 for v in updated_subs.values() if v)
                        st.caption(f"הוגש ל-{submitted_count}/{len(BODIES)} גופים")

    st.stop()

# ---------------------------------------------------------------------------
# Main — header
# ---------------------------------------------------------------------------
st.markdown('<div class="lf-header">Nazil 💰</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lf-subheader">פלטפורמת ניתוח קרנות פנסיה ישראלית · '
    'העלה קובץ מסלקה לקבלת תמונה מלאה</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# ── GATE 2: Legal disclaimer checkbox ────────────────────────────────────
# ---------------------------------------------------------------------------
st.markdown('<div class="legal-box">', unsafe_allow_html=True)
legal_accepted = st.checkbox(
    "אני מצהיר כי המידע המוצג הוא סימולציה בלבד, וכי הובהר לי שמשיכת כספים עלולה לפגוע "
    "בזכויותיי הפנסיוניות. אני מאשר את תנאי השימוש.",
    value=st.session_state.get("legal_accepted", False),
    key="legal_accepted",
)
st.markdown("</div>", unsafe_allow_html=True)

if not legal_accepted:
    st.warning("יש לאשר את תנאי השימוש כדי להמשיך.")
    st.stop()

# ---------------------------------------------------------------------------
# File upload + zero-footprint in-memory parse
# ---------------------------------------------------------------------------
uploaded_files = st.file_uploader(
    "העלה קבצי מסלקה (XML או DAT) — ניתן לבחור מספר קבצים",
    type=["xml", "dat"],
    accept_multiple_files=True,
    help="קבצי DAT/XML מהמסלקה הפנסיונית — מעובדים בזיכרון בלבד, ללא שמירה לדיסק",
)

if not uploaded_files:
    st.info("ממתין לקבצי DAT/XML מהמסלקה הפנסיונית...")
    st.stop()

funds: list[dict] = []
for uf in uploaded_files:
    try:
        funds.extend(parse_maslaka_bytes(uf.getvalue()))
    except ET.ParseError as exc:
        st.warning(f"קובץ לא תקין ({uf.name}): {exc} — דולג")

if not funds:
    st.error("לא נמצאו קרנות בקבצים שהועלו.")
    st.stop()

# ---------------------------------------------------------------------------
# Derived data
# ---------------------------------------------------------------------------
alerts = scan_alerts(funds)
rec    = compute_arbitrage(
    pitzuim_total   = sum(f["pitzuim"] for f in funds),
    fund_return_pct = fund_return,
    prime_pct       = prime_rate,
    spread_pct      = spread,
)

df = pd.DataFrame(funds)
df.rename(columns={
    "company_name":  "שם חברה",
    "fund_type":     "סוג קרן",
    "tagmulim":      "יתרת תגמולים (₪)",
    "pitzuim":       "יתרת פיצויים (₪)",
    "total_balance": 'סה"כ יתרה (₪)',
}, inplace=True)

total      = df['סה"כ יתרה (₪)'].sum()
total_pitz = df["יתרת פיצויים (₪)"].sum()
total_tagm = df["יתרת תגמולים (₪)"].sum()
net_to_bank = rec["net_withdrawal"]

# ---------------------------------------------------------------------------
# Auto client form — shown immediately after file upload
# ---------------------------------------------------------------------------
_file_key = str(sorted([f.name for f in uploaded_files]))
_saved_key = f"client_saved_{_file_key}"

if not st.session_state.get(_saved_key):
    st.markdown("""
<div style="background:#071a14;border:2px solid #00d4aa55;border-radius:14px;
     padding:1.2rem 1.5rem;margin-bottom:1rem">
  <div style="font-size:1rem;font-weight:700;color:#00d4aa;margin-bottom:.8rem">
    פתח תיק לקוח — הנתונים הפיננסיים ממולאים אוטומטית
  </div>""", unsafe_allow_html=True)

    with st.form("auto_client_form"):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            ac_name   = st.text_input("שם מלא *", placeholder="ישראל ישראלי")
            ac_phone  = st.text_input("טלפון *", placeholder="050-0000000")
        with ac2:
            ac_email  = st.text_input("אימייל", placeholder="israel@gmail.com")
            ac_source = st.selectbox("מקור הליד", crm.SOURCES)
        with ac3:
            ac_note   = st.text_area("הערת פתיחה", height=88,
                                     placeholder="צורך, דחיפות, רקע...")
        col_save, col_skip = st.columns([3, 1])
        with col_save:
            do_save = st.form_submit_button("פתח תיק לקוח", type="primary",
                                            use_container_width=True)
        with col_skip:
            do_skip = st.form_submit_button("דלג", use_container_width=True)

    if do_save:
        if not ac_name or not ac_phone:
            st.warning("שם וטלפון הם שדות חובה.")
        else:
            saved = crm.save_client(
                name=ac_name, phone=ac_phone, email=ac_email,
                id_number="", total_balance=total,
                total_pitz=total_pitz, total_tagm=total_tagm,
                num_funds=len(funds), net_to_bank=net_to_bank,
                rec_prefer_loan=rec["prefer_loan"],
                advisor_fee=0, notes=ac_note,
                fund_data=funds, source=ac_source,
            )
            if saved:
                st.session_state[_saved_key] = True
                st.success(f"תיק **{ac_name}** נפתח בהצלחה — נשמר ב-CRM.")
                st.rerun()
            else:
                st.error("שגיאה בשמירה.")

    if do_skip:
        st.session_state[_saved_key] = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Summary stat cards
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
for col, label, value, sub in [
    (c1, 'סה"כ נכסים',         f"₪{total:,.0f}",       f"{len(funds)} קרנות"),
    (c2, "יתרת פיצויים",        f"₪{total_pitz:,.0f}",  "ניתן למשיכה"),
    (c3, "יתרת תגמולים",        f"₪{total_tagm:,.0f}",  "פחות נזיל"),
    (c4, "נטו לחשבון (לאחר מס)", f"₪{net_to_bank:,.0f}", "Bottom Line"),
]:
    with col:
        val_color = "#00e676" if label == "נטו לחשבון (לאחר מס)" else "#e8e8e8"
        st.markdown(f"""
        <div class="stat-card">
          <div class="s-label">{label}</div>
          <div class="s-value" style="color:{val_color}">{value}</div>
          <div class="s-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Fund table + alerts
# ---------------------------------------------------------------------------
st.markdown("### פירוט קרנות")

fmt_cols  = ["יתרת תגמולים (₪)", "יתרת פיצויים (₪)", 'סה"כ יתרה (₪)']
styled_df = df.style.format({c: "{:,.0f}" for c in fmt_cols})
st.dataframe(styled_df, use_container_width=True, hide_index=True)

if alerts:
    st.markdown("#### התראות הזדמנות — פטור ממס")
    for alert in alerts:
        st.markdown(f'<div class="alert-row">⚡ {alert}</div>', unsafe_allow_html=True)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Arbitrage recommendation
# ---------------------------------------------------------------------------
st.markdown("### המלצת מומחה — ניתוח ארביטראז'")

box_class  = "rec-loan" if rec["prefer_loan"] else "rec-withdraw"
head_color = "#00d4aa"  if rec["prefer_loan"] else "#e05555"

st.markdown(f"""
<div class="rec-box {box_class}">
  <div class="rec-headline" style="color:{head_color}">{rec['headline']}</div>
  <div class="rec-detail">{rec['detail']}</div>
  <div class="rec-note">{rec['note']}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Loan Bridging Recommendation
# ---------------------------------------------------------------------------
st.markdown("### גשר פנסיוני — הלוואה מול משיכה")

max_loan_pitz = total_pitz * 0.70
max_loan_tagm = total_tagm * 0.30
max_loan_total = max_loan_pitz + max_loan_tagm

bridge_rate = max(0.1, prime_rate - 0.5)
bridge_months = 60

def _amort(p: float, apr: float, n: int) -> float:
    r = apr / 100 / 12
    if r == 0 or n == 0:
        return p / max(n, 1)
    return p * r * (1 + r) ** n / ((1 + r) ** n - 1)

loan_monthly     = _amort(max_loan_total, bridge_rate, bridge_months)
loan_total_paid  = loan_monthly * bridge_months
loan_total_int   = loan_total_paid - max_loan_total
withdrawal_tax   = max_loan_total * TAX_RATE
withdrawal_net   = max_loan_total - withdrawal_tax
savings_vs_withdrawal = withdrawal_tax - loan_total_int

# ── Comparison table ──────────────────────────────────────────────────────
col_w, col_l = st.columns(2)

with col_w:
    wcolor = "#e05555"
    st.markdown(f"""
<div style="background:#1a0707;border:1px solid #e0555533;border-radius:14px;padding:1.3rem 1.5rem">
  <div style="font-size:0.8rem;color:#888;margin-bottom:.5rem">אפשרות א׳ — משיכת כספים</div>
  <div style="font-size:1.6rem;font-weight:700;color:{wcolor}">₪{withdrawal_net:,.0f}</div>
  <div style="font-size:0.8rem;color:#888;margin-top:.3rem">נטו לחשבון לאחר מס 35%</div>
  <hr style="border-color:#2a1010;margin:.8rem 0">
  <table style="width:100%;font-size:0.83rem;color:#aaa;border-collapse:collapse">
    <tr><td>סכום ברוטו</td><td style="text-align:left;color:#e8e8e8">₪{max_loan_total:,.0f}</td></tr>
    <tr><td>מס 35% (נגבה)</td><td style="text-align:left;color:{wcolor}">−₪{withdrawal_tax:,.0f}</td></tr>
    <tr><td>קרן פנסיה לאחר משיכה</td><td style="text-align:left;color:{wcolor}">₪{total - max_loan_total:,.0f}</td></tr>
    <tr><td>כיסוי ביטוחי</td><td style="text-align:left;color:{wcolor}">נפגע</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

with col_l:
    lcolor = "#00d4aa"
    st.markdown(f"""
<div style="background:#071a14;border:1px solid #00d4aa33;border-radius:14px;padding:1.3rem 1.5rem">
  <div style="font-size:0.8rem;color:#888;margin-bottom:.5rem">אפשרות ב׳ — הלוואה פנסיונית (מומלץ)</div>
  <div style="font-size:1.6rem;font-weight:700;color:{lcolor}">₪{loan_monthly:,.0f} / חודש</div>
  <div style="font-size:0.8rem;color:#888;margin-top:.3rem">ריבית פריים פחות 0.5% = {bridge_rate:.2f}% | {bridge_months} חודשים</div>
  <hr style="border-color:#0a2a1e;margin:.8rem 0">
  <table style="width:100%;font-size:0.83rem;color:#aaa;border-collapse:collapse">
    <tr><td>סכום הלוואה מקסימלי</td><td style="text-align:left;color:#e8e8e8">₪{max_loan_total:,.0f}</td></tr>
    <tr><td style="padding-right:.5rem">70% מפיצויים</td><td style="text-align:left;color:{lcolor}">₪{max_loan_pitz:,.0f}</td></tr>
    <tr><td style="padding-right:.5rem">30% מתגמולים</td><td style="text-align:left;color:{lcolor}">₪{max_loan_tagm:,.0f}</td></tr>
    <tr><td>סה"כ ריבית ({bridge_months} חודשים)</td><td style="text-align:left;color:#e8e8e8">₪{loan_total_int:,.0f}</td></tr>
    <tr><td>כיסוי ביטוחי</td><td style="text-align:left;color:{lcolor}">שמור במלואו</td></tr>
  </table>
</div>""", unsafe_allow_html=True)

# ── Savings button ────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
if st.button("חשב חיסכון מהלוואה", type="primary", key="bridge_calc_btn"):
    if savings_vs_withdrawal > 0:
        st.success(
            f"על ידי לקיחת הלוואה במקום משיכה — הלקוח **חוסך ₪{savings_vs_withdrawal:,.0f}**. "
            f"(מס שנחסך: ₪{withdrawal_tax:,.0f} | עלות ריבית: ₪{loan_total_int:,.0f})"
        )
    else:
        st.warning(
            f"במקרה זה עלות הריבית (₪{loan_total_int:,.0f}) גבוהה מהמס שנחסך (₪{withdrawal_tax:,.0f}). "
            f"בדוק קיצור תקופה או הפחתת ריבית."
        )
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.metric("מס נחסך (לא משלמים)", f"₪{withdrawal_tax:,.0f}", delta="חיסכון מיידי")
    with c_s2:
        st.metric("עלות ריבית כוללת", f"₪{loan_total_int:,.0f}", delta=f"−₪{loan_monthly:,.0f}/חודש", delta_color="inverse")
    with c_s3:
        net_save_label = "חיסכון נטו" if savings_vs_withdrawal > 0 else "עלות נטו"
        st.metric(net_save_label, f"₪{abs(savings_vs_withdrawal):,.0f}",
                  delta="עדיף הלוואה" if savings_vs_withdrawal > 0 else "שקול משיכה",
                  delta_color="normal" if savings_vs_withdrawal > 0 else "inverse")

# ── Step-by-step guide ────────────────────────────────────────────────────
with st.expander("איך מגישים בקשת הלוואה מהקרן? — מדריך שלב-בשלב"):
    steps = [
        ("1", "קבל אישור יתרה עדכני",
         "פנה לחברה המנהלת (אתר, אפליקציה, או שיחת טלפון) וקבל דף יתרה עדכני לתאריך היום."),
        ("2", "בדוק זכאות להלוואה",
         f"ודא כי יש לך לפחות 6 חודשי ותק בקרן. סכום מקסימלי: "
         f"70% מפיצויים (₪{max_loan_pitz:,.0f}) + 30% מתגמולים (₪{max_loan_tagm:,.0f})."),
        ("3", "מלא טופס בקשת הלוואה",
         "הורד טופס בקשת הלוואה מאתר הקרן. ציין: סכום מבוקש, מספר תשלומים, ומטרת ההלוואה."),
        ("4", "צרף מסמכים נדרשים",
         "בדרך כלל: ת.ז, תלוש שכר אחרון, ולעיתים אישור מעסיק. בדוק דרישות ספציפיות אצל הקרן שלך."),
        ("5", "הגש ועקוב",
         "ניתן להגיש באתר הקרן, בדוא\"ל, או בסניף. זמן אישור טיפוסי: 5–10 ימי עסקים. "
         "לאחר האישור — הכסף מועבר ישירות לחשבון הבנק."),
    ]
    for num, title, desc in steps:
        st.markdown(f"""
<div style="display:flex;gap:1rem;margin-bottom:.9rem;align-items:flex-start">
  <div style="min-width:28px;height:28px;background:#00d4aa22;border:1px solid #00d4aa55;
       border-radius:50%;display:flex;align-items:center;justify-content:center;
       font-size:.8rem;font-weight:700;color:#00d4aa;flex-shrink:0">{num}</div>
  <div>
    <div style="font-size:.9rem;font-weight:600;color:#e8e8e8;margin-bottom:.2rem">{title}</div>
    <div style="font-size:.82rem;color:#888">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Action Plan — 3 Sales Calculators
# ---------------------------------------------------------------------------
st.markdown("### תוכנית פעולה — מחשבוני אופטימיזציה")

tab_tax, tab_loan, tab_swap = st.tabs(["מס אפקטיבי", "כושר החזר הלוואה", "סילוק חובות"])

# ── Calculator 1: Effective Tax ───────────────────────────────────────────
with tab_tax:
    st.markdown("#### כמה מס תשלם באמת?")
    st.caption("פיצויים פטורים מורידים את שיעור המס האפקטיבי הרבה מתחת ל-35%")
    exempt_input = st.number_input(
        "סכום פיצויים פטור ממס (₪)",
        min_value=0.0,
        max_value=max(1.0, float(total_pitz)),
        value=min(total_pitz * 0.4, total_pitz),
        step=1_000.0,
        format="%.0f",
        help="סכום הפיצויים שצבר פטור ממס לפי סעיף 9(7א)",
        key="exempt_input",
    )
    et = calc_effective_tax(total_pitz, exempt_input)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">מס אפקטיבי אמיתי</div>
          <div class="cr-value">{et['effective_pct']:.1f}%</div>
          <div class="cr-note">במקום 35% על הכל</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">נטו לחשבון</div>
          <div class="cr-value">₪{et['net']:,.0f}</div>
          <div class="cr-note">מס בפועל: ₪{et['tax_amount']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    st.info(f"💬 **משפט מכירה:** 'אדוני, כולם מפחידים אותך מ-35% מס, אבל במקרה שלך בגלל הפיצויים הפטורים, המשיכה תעלה לך רק **{et['effective_pct']:.1f}%**. זה הכסף הכי זול שתוכל להשיג כרגע.'")

# ── Calculator 2: Loan Repayment ──────────────────────────────────────────
with tab_loan:
    st.markdown("#### מה ההחזר החודשי?")
    st.caption("מחשב עלות הלוואה מהקרן מול שמירת קרן שלמה")
    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1:
        loan_amount = st.number_input("סכום הלוואה (₪)", min_value=1_000.0,
                                      value=max(1_000.0, min(50_000.0, total_pitz * 0.7)),
                                      step=1_000.0, format="%.0f", key="loan_amount")
    with l_col2:
        loan_rate = st.number_input("ריבית שנתית (%)", min_value=0.1, max_value=20.0,
                                    value=prime_rate + spread, step=0.1,
                                    format="%.2f", key="loan_rate")
    with l_col3:
        loan_months = st.number_input("תקופה (חודשים)", min_value=6, max_value=240,
                                      value=60, step=6, key="loan_months")
    lr = calc_loan(loan_amount, loan_rate, int(loan_months))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">החזר חודשי</div>
          <div class="cr-value">₪{lr['monthly']:,.0f}</div>
          <div class="cr-note">{int(loan_months)} חודשים × {loan_rate:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">סה"כ ריבית</div>
          <div class="cr-value">₪{lr['total_interest']:,.0f}</div>
          <div class="cr-note">עלות ההלוואה הכוללת</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        withdrawal_cost = loan_amount * TAX_RATE
        saving_vs_withdrawal = withdrawal_cost - lr['total_interest']
        label = "חיסכון לעומת משיכה" if saving_vs_withdrawal > 0 else "יוקר לעומת משיכה"
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">{label}</div>
          <div class="cr-value" style="color:{'#00e676' if saving_vs_withdrawal > 0 else '#e05555'}">₪{abs(saving_vs_withdrawal):,.0f}</div>
          <div class="cr-note">ביחס לקנס מס של ₪{withdrawal_cost:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    st.info(f"💬 **משפט מכירה:** 'במקום למשוך ולשלם מס של ₪{withdrawal_cost:,.0f}, קח הלוואה של ₪{loan_amount:,.0f}. ההחזר החודשי שלך יהיה רק **₪{lr['monthly']:,.0f}** — הרבה יותר משתלם.'")

# ── Calculator 3: Debt Swap ───────────────────────────────────────────────
with tab_swap:
    st.markdown("#### האם כדאי להחליף חוב יקר בהלוואה פנסיונית?")
    st.caption("משווה ריבית בנק / מינוס מול הלוואה מהקרן")
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        swap_debt = st.number_input("סכום החוב (₪)", min_value=1_000.0,
                                    value=50_000.0, step=1_000.0, format="%.0f", key="swap_debt")
    with s_col2:
        swap_current_rate = st.number_input("ריבית נוכחית (%)", min_value=1.0,
                                            max_value=30.0, value=14.0, step=0.5,
                                            format="%.1f", key="swap_curr_rate",
                                            help="ריבית מינוס / הלוואה חוץ-בנקאית")
    with s_col3:
        swap_pension_rate = st.number_input("ריבית הלוואה פנסיונית (%)", min_value=0.1,
                                            max_value=15.0, value=prime_rate + spread,
                                            step=0.1, format="%.2f", key="swap_pen_rate")
    with s_col4:
        swap_months = st.number_input("תקופה (חודשים)", min_value=6, max_value=120,
                                      value=36, step=6, key="swap_months")
    ds = calc_debt_swap(swap_debt, swap_current_rate, swap_pension_rate, int(swap_months))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="saving-card">
          <div class="cr-label" style="color:#888">החזר חודשי נוכחי (בנק)</div>
          <div style="font-size:1.3rem;font-weight:700;color:#e05555">₪{ds['current_monthly']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="saving-card">
          <div class="cr-label" style="color:#888">החזר חודשי (פנסיה)</div>
          <div style="font-size:1.3rem;font-weight:700;color:#e8e8e8">₪{ds['pension_monthly']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="calc-result">
          <div class="cr-label">חיסכון חודשי</div>
          <div class="cr-value">₪{ds['monthly_saving']:,.0f}</div>
          <div class="cr-note">סה"כ {int(swap_months)} חודשים: ₪{ds['total_saving']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    st.info(f"💬 **משפט מכירה:** 'אתה משלם לבנק **₪{ds['current_monthly']:,.0f}** ריבית כל חודש. אם נחליף להלוואה פנסיונית, ההחזר יהיה **₪{ds['pension_monthly']:,.0f}**. אתה חוסך **₪{ds['monthly_saving']:,.0f} בחודש** מהיום הראשון.'")

# Store for PDF
calc_results = {
    "effective_tax": et,
    "loan":          lr,
    "debt_swap":     ds,
}

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Summary — insights + action options
# ---------------------------------------------------------------------------
st.markdown("### סיכום נתונים ואפשרויות פעולה")

# ── Core numbers ─────────────────────────────────────────────────────────
num_funds          = len(funds)
tax_free_funds     = [f for f in funds if 0 < f["total_balance"] < TAX_FREE_THRESHOLD]
large_pitz_funds   = [f for f in funds if f["pitzuim"] > 50_000]
pitzuim_share_pct  = (total_pitz / total * 100) if total > 0 else 0
loan_rate_eff      = prime_rate + spread
arb_advantage      = fund_return - loan_rate_eff

# ── What the data says ────────────────────────────────────────────────────
st.markdown("#### מה הנתונים אומרים")

insight_rows = []

if total_pitz > 0:
    insight_rows.append(
        f"💰 **{pitzuim_share_pct:.0f}% מהנכסים הם פיצויים** (₪{total_pitz:,.0f}) — "
        f"הנזיל ביותר לפעולה מיידית"
    )

if num_funds > 1:
    insight_rows.append(
        f"📂 **{num_funds} קרנות פעילות** — ריבוי קרנות עשוי לגרור דמי ניהול כפולים ופיצול כיסוי ביטוחי"
    )

if tax_free_funds:
    insight_rows.append(
        f"⚡ **{len(tax_free_funds)} קרן/ות מתחת לסף הפטור (₪{TAX_FREE_THRESHOLD:,})** — "
        f"ניתן למשוך ללא מס לחלוטין"
    )

if et["effective_pct"] < 20:
    insight_rows.append(
        f"📊 **מס אפקטיבי נמוך: {et['effective_pct']:.1f}%** — "
        f"הרבה מתחת ל-35% בגלל הפטורים. המשיכה זולה יותר ממה שהלקוח חושב"
    )
elif et["effective_pct"] >= 25:
    insight_rows.append(
        f"⚠️ **מס אפקטיבי גבוה יחסית: {et['effective_pct']:.1f}%** — "
        f"הלוואה עשויה להיות עדיפה על משיכה"
    )

if arb_advantage > 0:
    insight_rows.append(
        f"📈 **ארביטראז' חיובי: תשואה גבוהה מריבית ב-{arb_advantage:.1f}%** — "
        f"כל שנה שהכסף נשאר בקרן שווה ₪{total_pitz * arb_advantage / 100:,.0f} נוספים"
    )
else:
    insight_rows.append(
        f"📉 **ריבית ההלוואה ({loan_rate_eff:.1f}%) גבוהה מהתשואה ({fund_return:.1f}%)** — "
        f"משיכה עשויה להיות הפתרון הכלכלי"
    )

for row in insight_rows:
    st.markdown(row)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ── Action options ranked ─────────────────────────────────────────────────
st.markdown("#### אפשרויות פעולה — מדורגות לפי כדאיות")

options = []

# Option A: Tax-free withdrawal
if tax_free_funds:
    tf_total = sum(f["total_balance"] for f in tax_free_funds)
    options.append(("high", "משיכה פטורה ממס — פעולה מיידית",
        f"קרנות עם יתרה מתחת לסף ₪{TAX_FREE_THRESHOLD:,} ניתנות למשיכה ללא מס. "
        f"סך ניתן למשיכה: ₪{tf_total:,.0f}",
        "פנה ישירות לחברה המנהלת עם טופס בקשת משיכה"))

# Option B: Pension loan
if rec["prefer_loan"] and total_pitz > 10_000:
    options.append(("high", "הלוואה מהקרן — הכסף הכי זול בשוק",
        f"ריבית הלוואה פנסיונית ({loan_rate_eff:.1f}%) נמוכה מתשואת הקרן ({fund_return:.1f}%). "
        f"החזר חודשי על ₪{min(50_000.0, total_pitz * 0.7):,.0f}: ₪{lr['monthly']:,.0f}",
        "פנה לחברה המנהלת — ניתן לקבל עד 50% מהפיצויים כהלוואה"))

# Option C: Debt swap
if ds["monthly_saving"] > 500:
    options.append(("medium", "סילוק חוב יקר — החלפת ריבית",
        f"במקום ריבית בנק {swap_current_rate:.1f}%, הלוואה פנסיונית חוסכת "
        f"₪{ds['monthly_saving']:,.0f} בחודש (₪{ds['total_saving']:,.0f} סה\"כ לתקופה)",
        "הכן הסכם פירעון מוקדם מהבנק + בקשת הלוואה פנסיונית"))

# Option D: Consolidation
if num_funds > 2:
    options.append(("medium", "איחוד קרנות — הפחתת דמי ניהול",
        f"ריבוי {num_funds} קרנות יוצר עלות נסתרת. איחוד לקרן אחת מפחית דמי ניהול "
        f"ומחזק כיסוי ביטוחי",
        "בדוק תנאי ניוד בין קרנות — ניוד פנסיוני אינו חייב במס"))

# Option E: Taxed withdrawal (last resort)
if not rec["prefer_loan"] or not tax_free_funds:
    options.append(("low", "משיכה חייבת במס — כמוצא אחרון",
        f"מס אפקטיבי: {et['effective_pct']:.1f}% — נטו לחשבון: ₪{et['net']:,.0f}. "
        f"מומלץ רק אם אין חלופה זולה יותר",
        "ודא קבלת אישור ניכוי מס מהחברה לפני הגשת דוח שנתי"))

color_map = {"high": "#00d4aa", "medium": "#f0c040", "low": "#e05555"}
label_map  = {"high": "עדיפות גבוהה", "medium": "שקול", "low": "אחרון בסדר עדיפות"}

for priority, title, detail, action in options:
    color = color_map[priority]
    badge = label_map[priority]
    st.markdown(f"""
<div style="background:#161616;border:1px solid #252525;border-right:4px solid {color};
     border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:0.8rem">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem">
    <span style="font-size:1rem;font-weight:700;color:{color}">{title}</span>
    <span style="font-size:0.72rem;color:{color};border:1px solid {color};
          border-radius:20px;padding:2px 10px">{badge}</span>
  </div>
  <div style="font-size:0.87rem;color:#aaa;margin-bottom:.5rem">{detail}</div>
  <div style="font-size:0.78rem;color:#555">▸ {action}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PDF export — gated on legal_accepted (already enforced above by st.stop)
# ---------------------------------------------------------------------------
st.markdown("### דוח לקוח")

if st.button("📄 צור דוח PDF", type="primary", disabled=not legal_accepted):
    with st.spinner("מייצר דוח..."):
        try:
            pdf_bytes = generate_report_pdf(funds, rec, alerts, calc_results)
            st.download_button(
                label="⬇️ הורד דוח PDF",
                data=pdf_bytes,
                file_name=f"nazil_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"שגיאה ביצירת הדוח: {e}")
            st.info("ודא ש-fpdf2 ו-python-bidi מותקנים: pip install fpdf2 python-bidi")

# ---------------------------------------------------------------------------
# Internal Revenue & Pricing Calculator — agent-only, never in PDF
# ---------------------------------------------------------------------------
_AGENT_CODE = _AGENT_CODE_TV

with st.sidebar:
    st.markdown('<hr class="lf-divider">', unsafe_allow_html=True)
    agent_code = st.text_input("קוד סוכן (פנימי)", type="password",
                               placeholder="הזן קוד גישה...",
                               label_visibility="collapsed",
                               key="agent_code_input")

_agent_mode = hmac.compare_digest(
    agent_code.encode() if agent_code else b"",
    _AGENT_CODE.encode(),
)

if _agent_mode:
    st.markdown("---")
    st.markdown("""
<div style="background:#0a0a1a;border:2px solid #3a3a6a;border-radius:14px;
     padding:1.4rem 1.6rem;margin-bottom:1rem">
  <div style="font-size:1.1rem;font-weight:700;color:#8888ff;margin-bottom:.3rem">
    🔒 מחשבון עמלות פנימי — סוכן בלבד
  </div>
  <div style="font-size:0.78rem;color:#555">המידע הזה לא מופיע בדוח הלקוח</div>
</div>""", unsafe_allow_html=True)

    # ── Inputs (pre-filled from file data, editable) ──────────────────────
    fee_col1, fee_col2 = st.columns(2)
    with fee_col1:
        fee_pitz = st.number_input("פיצויים (₪)", min_value=0.0,
                                   value=float(total_pitz), step=1_000.0,
                                   format="%.0f", key="fee_pitz")
        fee_tagm = st.number_input("תגמולים (₪)", min_value=0.0,
                                   value=float(total_tagm), step=1_000.0,
                                   format="%.0f", key="fee_tagm")
    with fee_col2:
        fee_loan = st.number_input("סכום הלוואה (₪)", min_value=0.0,
                                   value=float(max_loan_total), step=1_000.0,
                                   format="%.0f", key="fee_loan")
        fee_pct  = st.number_input("אחוז עמלה (%)", min_value=0.0,
                                   max_value=30.0, value=15.0,
                                   step=0.5, format="%.1f", key="fee_pct")

    # ── Logic ─────────────────────────────────────────────────────────────
    LOAN_FLAT    = 2_500.0
    REPORT_FEE   = 350.0
    OVERHEAD_PCT = 0.25   # assumed cost ratio for profit calc
    DISCOUNT_PCT = 0.70   # minimum floor = 70% of recommended

    base_fee      = (fee_pitz + fee_tagm) * (fee_pct / 100)
    loan_fee      = LOAN_FLAT if fee_loan > 0 else 0.0
    total_fee_excl_vat = base_fee + loan_fee + REPORT_FEE
    min_fee       = total_fee_excl_vat * DISCOUNT_PCT
    projected_profit = total_fee_excl_vat * (1 - OVERHEAD_PCT)

    # ── Display ───────────────────────────────────────────────────────────
    r1, r2, r3 = st.columns(3)
    metrics = [
        (r1, "עמלה מומלצת (לפני מע\"מ)", f"₪{total_fee_excl_vat:,.0f}",
         f"בסיס: ₪{base_fee:,.0f} | הלוואה: ₪{loan_fee:,.0f} | פתיחת תיק: ₪{REPORT_FEE:,.0f}", "#8888ff"),
        (r2, "מינימום עם הנחה (70%)", f"₪{min_fee:,.0f}",
         "רצפת ניהול משא ומתן", "#f0c040"),
        (r3, "רווח צפוי אחרי עלויות", f"₪{projected_profit:,.0f}",
         f"בהנחת {int(OVERHEAD_PCT*100)}% עלויות תפעול", "#00d4aa"),
    ]
    for col, label, value, note, color in metrics:
        with col:
            st.markdown(f"""
<div style="background:#0d0d1f;border:1px solid #2a2a4a;border-radius:10px;
     padding:.9rem 1rem;text-align:center">
  <div style="font-size:.72rem;color:#555;margin-bottom:.3rem">{label}</div>
  <div style="font-size:1.5rem;font-weight:700;color:{color}">{value}</div>
  <div style="font-size:.68rem;color:#444;margin-top:.25rem">{note}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:#0a0a1a;border:1px solid #2a2a4a;border-radius:8px;
     padding:.7rem 1rem;margin-top:.8rem;font-size:.8rem;color:#666">
  💡 עם מע"מ (17%): <strong style="color:#8888ff">₪{total_fee_excl_vat * 1.17:,.0f}</strong>
  &nbsp;|&nbsp; מינימום עם מע"מ: <strong style="color:#f0c040">₪{min_fee * 1.17:,.0f}</strong>
</div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sticky legal footer — always visible
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="legal-footer">
  ⚖️ {LEGAL_DISCLAIMER}
</div>
""", unsafe_allow_html=True)
