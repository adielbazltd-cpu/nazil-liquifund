"""
maslaka_parser.py
Parses Israeli Maslaka (מסלקה פנסיונית) DAT/XML files.
Supports the real Mimshak format sent by the pension clearinghouse.
"""

import xml.etree.ElementTree as ET
from typing import Optional

# ---------------------------------------------------------------------------
# SUG-MUTZAR code → Hebrew label
# ---------------------------------------------------------------------------
_FUND_TYPE_LABELS = {
    "1": "קרן פנסיה ותיקה",
    "2": "קרן פנסיה חדשה מקיפה",
    "3": "קרן פנסיה חדשה כללית",
    "4": "קופת גמל לתגמולים",
    "5": "קופת גמל להשקעה",
    "6": "ביטוח מנהלים",
    "7": "קרן השתלמות",
}


def _txt(el: Optional[ET.Element]) -> str:
    return el.text.strip() if el is not None and el.text else ""


def _sum_tag(parent: ET.Element, tag: str) -> float:
    return sum(
        float(e.text.strip().replace(",", ""))
        for e in parent.findall(f".//{tag}")
        if e.text and e.text.strip()
    )


# ---------------------------------------------------------------------------
# Real Maslaka format: root tag = <Mimshak>
# ---------------------------------------------------------------------------
def _parse_mimshak(root: ET.Element) -> list[dict]:
    company_name = _txt(root.find(".//YeshutYatzran/SHEM-YATZRAN"))
    records: list[dict] = []

    for mutzar in root.findall(".//Mutzar"):
        # Company name: file-level, but fallback to inside mutzar
        name = company_name or _txt(mutzar.find(".//SHEM-YATZRAN"))

        sug_code = _txt(mutzar.find(".//SUG-MUTZAR"))
        fund_type = _FUND_TYPE_LABELS.get(sug_code, _txt(mutzar.find(".//SHEM-TOCHNIT")) or "לא מוגדר")
        fund_name = _txt(mutzar.find(".//SHEM-TOCHNIT")) or fund_type

        total_balance = _sum_tag(mutzar, "TOTAL-CHISACHON-MTZBR")
        pitzuim       = _sum_tag(mutzar, "YITRAT-PITZUIM-LELO-HITCHASHBENOT")
        tagmulim      = max(0.0, total_balance - pitzuim)

        if total_balance == 0:
            continue

        records.append({
            "company_name":  name,
            "fund_type":     f"{fund_name} — {fund_type}" if fund_name != fund_type else fund_type,
            "tagmulim":      tagmulim,
            "pitzuim":       pitzuim,
            "total_balance": total_balance,
        })

    return records


# ---------------------------------------------------------------------------
# Legacy / generic XML format fallback
# ---------------------------------------------------------------------------
_NS = {"ms": "http://www.mas.gov.il/MaslakaSchema"}


def _find_text(el: ET.Element, *paths: str) -> Optional[str]:
    for path in paths:
        node = el.find(path, _NS)
        if node is not None and node.text:
            return node.text.strip()
    return None


def _parse_generic(root: ET.Element) -> list[dict]:
    def find(el: ET.Element, bare: str, ns_path: str) -> Optional[str]:
        return _find_text(el, ns_path, bare)

    containers = (
        root.findall(".//ms:MutzarPensioni", _NS)
        or root.findall(".//ms:Mutzar", _NS)
        or root.findall(".//MutzarPensioni")
        or root.findall(".//Mutzar")
        or root.findall(".//PolicyDetails")
    )

    records: list[dict] = []
    for mutzar in containers:
        company_name = (
            find(mutzar, ".//ShemGuf",       ".//ms:ShemGuf")
            or find(mutzar, ".//GufMishpati", ".//ms:GufMishpati")
            or "לא ידוע"
        )
        fund_type = (
            find(mutzar, ".//TeurMutzar", ".//ms:TeurMutzar")
            or find(mutzar, ".//SugMutzar", ".//ms:SugMutzar")
            or "לא מוגדר"
        )
        tagmulim = float(find(mutzar, ".//YitratTagmulim", ".//ms:YitratTagmulim") or 0)
        pitzuim  = float(find(mutzar, ".//YitratPitzuim",  ".//ms:YitratPitzuim")  or 0)
        raw_total = find(mutzar, ".//YitratKolel", ".//ms:YitratKolel")
        total = float(raw_total) if raw_total else tagmulim + pitzuim

        if total == 0:
            continue

        records.append({
            "company_name":  company_name,
            "fund_type":     fund_type,
            "tagmulim":      tagmulim,
            "pitzuim":       pitzuim,
            "total_balance": total,
        })
    return records


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def _parse_root(root: ET.Element) -> list[dict]:
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag == "Mimshak":
        return _parse_mimshak(root)
    return _parse_generic(root)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_maslaka_xml(xml_path: str) -> list[dict]:
    """Parse from a file path."""
    return _parse_root(ET.parse(xml_path).getroot())


def parse_maslaka_bytes(xml_bytes: bytes) -> list[dict]:
    """Parse from raw bytes — zero footprint, no disk write."""
    return _parse_root(ET.fromstring(xml_bytes))
