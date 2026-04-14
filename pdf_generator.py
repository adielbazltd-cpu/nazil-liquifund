"""
pdf_generator.py — Nazil | LiquiFund branded PDF reports.
Palette: Navy (#1A237E) headers, Green (#00E676) net-to-bank, white body.
Hebrew RTL via python-bidi + DejaVu font (bundled with fpdf2).
"""

import io
import os
from datetime import date
from typing import Optional

from fpdf import FPDF

# ---------------------------------------------------------------------------
# Hebrew RTL
# ---------------------------------------------------------------------------
try:
    from bidi.algorithm import get_display as _bidi
    _HAS_BIDI = True
except ImportError:
    _HAS_BIDI = False


def _h(text: str) -> str:
    """Reorder Hebrew string for LTR-mapped PDF rendering."""
    if not text:
        return ""
    if _HAS_BIDI:
        return _bidi(text)
    return " ".join(text.split()[::-1])


def _is_heb(text: str) -> bool:
    return any("\u0590" <= c <= "\u05FF" for c in text)


# ---------------------------------------------------------------------------
# Fonts — DejaVu Sans covers Hebrew Unicode (U+0590–U+05FF)
# ---------------------------------------------------------------------------
_FONT_DIR  = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_REG  = os.path.join(_FONT_DIR, "DejaVuSans.ttf")
_FONT_BOLD = os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")

# ---------------------------------------------------------------------------
# Brand palette — RGB tuples
# ---------------------------------------------------------------------------
_NAVY        = (26,  35,  126)   # #1A237E  — primary headers
_NAVY_LIGHT  = (48,  63,  159)   # #303F9F  — secondary / hover
_GREEN_NET   = (0,   200, 100)   # #00C864  — net-to-bank (printable shade of #00E676)
_WHITE       = (255, 255, 255)
_OFF_WHITE   = (248, 249, 252)
_TEXT_DARK   = (20,  20,  40)
_TEXT_MUTED  = (110, 110, 130)
_ROW_ALT     = (237, 239, 252)   # light navy tint for alternating rows
_ALERT_BG    = (255, 248, 225)
_ALERT_BORD  = (220, 160,  0)
_WARN_TEXT   = (130,  80,  0)
_GREEN_BG    = (232, 255, 242)   # light green background for net card
_RED_BOX     = (255, 235, 235)
_RED_BORD    = (200,  60,  60)

LEGAL_DISCLAIMER = (
    "המידע המוצג מבוסס על נתוני המסלקה הפנסיונית ומהווה סימולציה בלבד. "
    "אין לראות במידע זה ייעוץ פנסיוני או תחליף לייעוץ השקעות המותאם אישית. "
    "ביצוע פעולות במוצר פנסיוני עלול לפגוע בקצבת הפרישה וברצף הביטוחי."
)


# ---------------------------------------------------------------------------
# PDF class
# ---------------------------------------------------------------------------
class _NazilReport(FPDF):

    def __init__(self):
        super().__init__()
        self.add_font("dv", fname=_FONT_REG)
        self.add_font("dv", style="B", fname=_FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=26)
        self.set_margins(left=13, top=38, right=13)

    def header(self):
        # Navy header band
        self.set_fill_color(*_NAVY)
        self.rect(0, 0, 210, 32, style="F")
        # Thin green accent line
        self.set_fill_color(*_GREEN_NET)
        self.rect(0, 32, 210, 1.2, style="F")

        # Brand — left
        self.set_xy(13, 8)
        self.set_font("dv", style="B", size=20)
        self.set_text_color(*_WHITE)
        self.cell(50, 10, "Nazil", ln=False)

        # Sub-brand — left, smaller
        self.set_xy(13, 21)
        self.set_font("dv", size=7)
        self.set_text_color(180, 190, 230)
        self.cell(50, 5, "LiquiFund Platform", ln=False)

        # Tagline — right
        self.set_xy(13, 13)
        self.set_font("dv", size=8)
        self.set_text_color(200, 210, 240)
        self.cell(0, 6, _h("דוח ניתוח פנסיה אישי | סימולציה בלבד"), align="R")

    def footer(self):
        # Disable auto page break so footer drawing never triggers a new page
        self.set_auto_page_break(False)

        # Disclaimer band — full width
        y_disc = self.h - 20
        self.set_fill_color(245, 245, 250)
        self.rect(0, y_disc, 210, 12, style="F")
        self.set_fill_color(*_NAVY)
        self.rect(0, y_disc, 210, 0.5, style="F")

        self.set_xy(13, y_disc + 1)
        self.set_font("dv", size=5.5)
        self.set_text_color(*_TEXT_MUTED)
        # Use cell (not multi_cell) to avoid triggering page breaks inside footer
        self.cell(184, 4, _h(LEGAL_DISCLAIMER[:90]), align="R", ln=True)
        self.set_xy(13, y_disc + 5)
        self.cell(184, 4, _h(LEGAL_DISCLAIMER[90:]), align="R")

        # Page number + date — bottom strip
        self.set_fill_color(*_NAVY)
        self.rect(0, self.h - 8, 210, 8, style="F")
        self.set_xy(13, self.h - 7)
        self.set_font("dv", size=7)
        self.set_text_color(180, 190, 230)
        today = date.today().strftime("%d/%m/%Y")
        self.cell(0, 5, f"Nazil | {today}  ·  {_h('סימולציה בלבד')}", align="C")

        self.set_auto_page_break(True, margin=26)


# ---------------------------------------------------------------------------
# Helpers

def _ensure_space(pdf: "_NazilReport", needed_mm: float) -> None:
    """Add a new page if less than needed_mm of vertical space remains."""
    if pdf.get_y() + needed_mm > pdf.h - 26:
        pdf.add_page()


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _section_title(pdf: _NazilReport, title: str) -> None:
    pdf.ln(5)
    pdf.set_font("dv", style="B", size=11)
    pdf.set_text_color(*_NAVY)
    pdf.cell(0, 7, _h(title), ln=True, align="R")
    pdf.set_fill_color(*_NAVY_LIGHT)
    pdf.rect(pdf.get_x(), pdf.get_y(), 184, 0.5, style="F")
    pdf.ln(3)


def _summary_banner(pdf: _NazilReport, funds: list[dict], net_to_bank: float) -> None:
    total      = sum(f["total_balance"] for f in funds)
    total_pitz = sum(f["pitzuim"] for f in funds)
    total_tagm = sum(f["tagmulim"] for f in funds)

    # Main banner box
    y0 = pdf.get_y()
    pdf.set_fill_color(*_OFF_WHITE)
    pdf.set_draw_color(*_NAVY)
    pdf.rect(13, y0, 184, 24, style="FD")

    col_w = 184 / 4
    items = [
        (_h('סה"כ נכסים'), f"₪{total:,.0f}",      _TEXT_DARK),
        (_h("פיצויים"),    f"₪{total_pitz:,.0f}",  _TEXT_DARK),
        (_h("תגמולים"),    f"₪{total_tagm:,.0f}",  _TEXT_DARK),
        (_h("נטו לחשבון"), f"₪{net_to_bank:,.0f}", _GREEN_NET),
    ]
    for i, (lbl, val, val_color) in enumerate(items):
        x = 13 + i * col_w
        pdf.set_xy(x, y0 + 3)
        pdf.set_font("dv", size=7)
        pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w, 4, lbl, align="C")
        pdf.set_xy(x, y0 + 8)
        pdf.set_font("dv", style="B", size=10)
        pdf.set_text_color(*val_color)
        pdf.cell(col_w, 8, val, align="C")

    pdf.set_y(y0 + 27)


def _net_to_bank_card(pdf: _NazilReport, rec: dict) -> None:
    """Prominent green 'נטו לחשבון' card — the bottom-line close."""
    _section_title(pdf, 'נטו לחשבון הבנק — Bottom Line')

    y0 = pdf.get_y()
    pdf.set_fill_color(*_GREEN_BG)
    pdf.set_draw_color(*_GREEN_NET)
    pdf.rect(13, y0, 184, 28, style="FD")
    # Green left bar
    pdf.set_fill_color(*_GREEN_NET)
    pdf.rect(13, y0, 3, 28, style="F")

    net = rec["net_withdrawal"]
    pitz = net / (1 - 0.35)  # reverse to show gross
    tax  = pitz * 0.35

    pdf.set_xy(19, y0 + 3)
    pdf.set_font("dv", size=8)
    pdf.set_text_color(*_TEXT_MUTED)
    pdf.cell(0, 5, _h(f"סכום פיצויים ברוטו: ₪{pitz:,.0f}"), align="R")

    pdf.set_xy(19, y0 + 9)
    pdf.set_font("dv", size=8)
    pdf.set_text_color(_RED_BORD[0], _RED_BORD[1], _RED_BORD[2])
    pdf.cell(0, 5, _h(f"ניכוי מס (35%): ₪{tax:,.0f}−"), align="R")

    # The big green number
    pdf.set_xy(19, y0 + 15)
    pdf.set_font("dv", style="B", size=16)
    pdf.set_text_color(*_GREEN_NET)
    pdf.cell(0, 9, _h(f"נטו לחשבון: ₪{net:,.0f}"), align="R")

    pdf.set_y(y0 + 31)


def _fund_table(pdf: _NazilReport, funds: list[dict]) -> None:
    _section_title(pdf, "פירוט קרנות")

    headers = [_h('סה"כ (₪)'), _h("פיצויים (₪)"), _h("תגמולים (₪)"), _h("סוג קרן"), _h("שם חברה")]
    col_w   = [33, 33, 33, 40, 45]

    # Header row
    pdf.set_fill_color(*_NAVY)
    pdf.set_text_color(*_WHITE)
    pdf.set_font("dv", style="B", size=8)
    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, h, border=0, align="C", fill=True)
    pdf.ln()

    for idx, fund in enumerate(funds):
        pdf.set_fill_color(*(_ROW_ALT if idx % 2 == 0 else _WHITE))
        pdf.set_text_color(*_TEXT_DARK)
        pdf.set_font("dv", size=8)
        row = [
            f"₪{fund['total_balance']:,.0f}",
            f"₪{fund['pitzuim']:,.0f}",
            f"₪{fund['tagmulim']:,.0f}",
            _h(fund["fund_type"])    if _is_heb(fund["fund_type"])    else fund["fund_type"],
            _h(fund["company_name"]) if _is_heb(fund["company_name"]) else fund["company_name"],
        ]
        for val, w in zip(row, col_w):
            pdf.cell(w, 7, val, border=0, align="C", fill=True)
        pdf.ln()
    pdf.ln(3)


def _recommendation_box(pdf: _NazilReport, rec: dict) -> None:
    _section_title(pdf, "המלצת מומחה — ניתוח ארביטראז'")

    prefer_loan = rec["prefer_loan"]
    box_bg  = _GREEN_BG   if prefer_loan else _RED_BOX
    bar_col = _GREEN_NET  if prefer_loan else _RED_BORD
    hd_col  = (0, 140, 70) if prefer_loan else _RED_BORD

    y0 = pdf.get_y()
    pdf.set_fill_color(*box_bg)
    pdf.set_draw_color(*bar_col)
    pdf.rect(13, y0, 184, 32, style="FD")
    pdf.set_fill_color(*bar_col)
    pdf.rect(13, y0, 3, 32, style="F")

    pdf.set_xy(19, y0 + 4)
    pdf.set_font("dv", style="B", size=11)
    pdf.set_text_color(*hd_col)
    pdf.cell(0, 7, _h(rec["headline"]), align="R")

    pdf.set_xy(19, y0 + 13)
    pdf.set_font("dv", size=9)
    pdf.set_text_color(*_TEXT_DARK)
    pdf.cell(0, 6, _h(rec["detail"]), align="R")

    pdf.set_xy(19, y0 + 22)
    pdf.set_font("dv", size=8)
    pdf.set_text_color(*_TEXT_MUTED)
    pdf.cell(0, 5, _h(rec["note"]), align="R")

    pdf.set_y(y0 + 36)


def _alerts_section(pdf: _NazilReport, alerts: list[str]) -> None:
    if not alerts:
        return
    _section_title(pdf, "התראות הזדמנות — פטור ממס")
    for alert in alerts:
        y0 = pdf.get_y()
        pdf.set_fill_color(*_ALERT_BG)
        pdf.set_draw_color(*_ALERT_BORD)
        pdf.rect(13, y0, 184, 10, style="FD")
        pdf.set_fill_color(*_ALERT_BORD)
        pdf.rect(13, y0, 2.5, 10, style="F")
        pdf.set_xy(18, y0 + 2)
        pdf.set_font("dv", size=8)
        pdf.set_text_color(*_WARN_TEXT)
        pdf.cell(0, 6, _h(alert), align="R")
        pdf.ln(12)


def _action_plan(pdf: _NazilReport, calc_results: dict) -> None:
    """Three-calculator action plan section."""
    _section_title(pdf, "תוכנית פעולה — מחשבוני אופטימיזציה")

    et = calc_results.get("effective_tax", {})
    lr = calc_results.get("loan", {})
    ds = calc_results.get("debt_swap", {})

    col_w = 184 / 3
    BOX_H = 22  # box height + spacing needed per sub-section

    # ── 1. Effective Tax ────────────────────────────────────────────────────
    _ensure_space(pdf, BOX_H + 8)
    pdf.set_font("dv", style="B", size=9)
    pdf.set_text_color(*_NAVY)
    pdf.cell(0, 6, _h("1. מס אפקטיבי — עלות האמיתית של המשיכה"), ln=True, align="R")
    pdf.ln(1)

    y0 = pdf.get_y()
    boxes = [
        (_h("מס אפקטיבי"),   f"{et.get('effective_pct', 0):.1f}%",  _h("במקום 35% על הכל")),
        (_h("סכום מס בפועל"), f"₪{et.get('tax_amount', 0):,.0f}",   _h("לפני פטור")),
        (_h("נטו לחשבון"),    f"₪{et.get('net', 0):,.0f}",           _h("לאחר מס")),
    ]
    for i, (lbl, val, note) in enumerate(boxes):
        x = 13 + i * col_w
        pdf.set_fill_color(*_OFF_WHITE)
        pdf.set_draw_color(*_NAVY_LIGHT)
        pdf.rect(x, y0, col_w - 2, 18, style="FD")
        pdf.set_xy(x + 1, y0 + 1)
        pdf.set_font("dv", size=7); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, lbl, align="C")
        pdf.set_xy(x + 1, y0 + 6)
        pdf.set_font("dv", style="B", size=11)
        pdf.set_text_color(*_GREEN_NET if "נטו" in lbl or "אפקטיבי" in lbl else _NAVY)
        pdf.cell(col_w - 2, 7, val, align="C")
        pdf.set_xy(x + 1, y0 + 13)
        pdf.set_font("dv", size=6); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, note, align="C")
    pdf.set_y(y0 + 22)
    pdf.ln(3)

    # ── 2. Loan Repayment ───────────────────────────────────────────────────
    _ensure_space(pdf, BOX_H + 8)
    pdf.set_font("dv", style="B", size=9)
    pdf.set_text_color(*_NAVY)
    pdf.cell(0, 6, _h("2. כושר החזר הלוואה"), ln=True, align="R")
    pdf.ln(1)

    y0 = pdf.get_y()
    boxes = [
        (_h("החזר חודשי"),    f"₪{lr.get('monthly', 0):,.0f}",          _h(f"{lr.get('months',0)} חודשים")),
        (_h("סה\"כ ריבית"),   f"₪{lr.get('total_interest', 0):,.0f}",   _h("עלות הלוואה")),
        (_h("קרן ההלוואה"),   f"₪{lr.get('principal', 0):,.0f}",         _h(f"{lr.get('annual_rate',0):.2f}%")),
    ]
    for i, (lbl, val, note) in enumerate(boxes):
        x = 13 + i * col_w
        pdf.set_fill_color(*_OFF_WHITE)
        pdf.set_draw_color(*_NAVY_LIGHT)
        pdf.rect(x, y0, col_w - 2, 18, style="FD")
        pdf.set_xy(x + 1, y0 + 1)
        pdf.set_font("dv", size=7); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, lbl, align="C")
        pdf.set_xy(x + 1, y0 + 6)
        pdf.set_font("dv", style="B", size=11); pdf.set_text_color(*_NAVY)
        pdf.cell(col_w - 2, 7, val, align="C")
        pdf.set_xy(x + 1, y0 + 13)
        pdf.set_font("dv", size=6); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, note, align="C")
    pdf.set_y(y0 + 22)
    pdf.ln(3)

    # ── 3. Debt Swap ────────────────────────────────────────────────────────
    _ensure_space(pdf, BOX_H + 8)
    pdf.set_font("dv", style="B", size=9)
    pdf.set_text_color(*_NAVY)
    pdf.cell(0, 6, _h("3. סילוק חובות יקרים — חיסכון חודשי"), ln=True, align="R")
    pdf.ln(1)

    y0 = pdf.get_y()
    boxes = [
        (_h("החזר נוכחי (בנק)"),   f"₪{ds.get('current_monthly', 0):,.0f}", _h(f"ריבית {ds.get('current_rate',0):.1f}%")),
        (_h("החזר פנסיוני"),        f"₪{ds.get('pension_monthly', 0):,.0f}", _h(f"ריבית {ds.get('pension_rate',0):.2f}%")),
        (_h("חיסכון חודשי"),        f"₪{ds.get('monthly_saving', 0):,.0f}",  _h(f"סה\"כ: ₪{ds.get('total_saving',0):,.0f}")),
    ]
    colors = [_NAVY, _NAVY, _GREEN_NET]
    for i, ((lbl, val, note), col) in enumerate(zip(boxes, colors)):
        x = 13 + i * col_w
        bg = _GREEN_BG if col == _GREEN_NET else _OFF_WHITE
        pdf.set_fill_color(*bg)
        pdf.set_draw_color(*_NAVY_LIGHT)
        pdf.rect(x, y0, col_w - 2, 18, style="FD")
        pdf.set_xy(x + 1, y0 + 1)
        pdf.set_font("dv", size=7); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, lbl, align="C")
        pdf.set_xy(x + 1, y0 + 6)
        pdf.set_font("dv", style="B", size=11); pdf.set_text_color(*col)
        pdf.cell(col_w - 2, 7, val, align="C")
        pdf.set_xy(x + 1, y0 + 13)
        pdf.set_font("dv", size=6); pdf.set_text_color(*_TEXT_MUTED)
        pdf.cell(col_w - 2, 4, note, align="C")
    pdf.set_y(y0 + 25)


def _next_steps(pdf: _NazilReport) -> None:
    _ensure_space(pdf, 50)
    _section_title(pdf, "צעדים הבאים מומלצים")
    steps = [
        "קבע פגישת ייעוץ עם מומחה Nazil לניתוח מעמיק של תיק הפנסיה",
        "בדוק תנאי הלוואת פיצויים מול הגוף המנהל (ריבית, תקופה, בטוחות)",
        "וודא אישור מס מרואה חשבון לפני כל פעולת משיכה",
        "שקול קיבוע ריבית ההלוואה לטווח 3–5 שנים להגנה מפני עלייה",
        "בחן פיצול משיכה חלקית להפחתת עומס המס השנתי",
    ]
    for i, step in enumerate(steps, 1):
        pdf.set_font("dv", style="B", size=9)
        pdf.set_text_color(*_NAVY)
        pdf.cell(10, 7, f"{i}.")
        pdf.set_font("dv", size=9)
        pdf.set_text_color(*_TEXT_DARK)
        pdf.cell(0, 7, _h(step), ln=True, align="R")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_report_pdf(
    funds: list[dict],
    rec: dict,
    alerts: list[str],
    calc_results: Optional[dict] = None,
) -> bytes:
    """
    Generate a branded Nazil PDF report.

    Args:
        funds:        list of fund dicts from parse_maslaka_bytes / parse_maslaka_xml
        rec:          arbitrage dict (keys: prefer_loan, headline, detail, note, net_withdrawal)
        alerts:       list of opportunity alert strings
        calc_results: optional dict with keys effective_tax / loan / debt_swap

    Returns:
        Raw PDF bytes — pass directly to st.download_button.
    """
    pdf = _NazilReport()
    pdf.add_page()

    _summary_banner(pdf, funds, rec["net_withdrawal"])
    _net_to_bank_card(pdf, rec)
    _fund_table(pdf, funds)
    _recommendation_box(pdf, rec)
    _alerts_section(pdf, alerts)
    if calc_results:
        _action_plan(pdf, calc_results)
    _next_steps(pdf)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
