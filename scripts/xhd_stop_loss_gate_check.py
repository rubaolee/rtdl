#!/usr/bin/env python3
"""Stop-loss / kill-gate checker for app-artifact-parity work (rules G-1..G-4).

Governance rule:
  history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md

Usage:
  py scripts/xhd_stop_loss_gate_check.py <goal_report_or_call_for_review.md> [...]

Exit code:
  0  -> no parity work detected, or parity work correctly gated (fields present + passing)
  2  -> parity work detected but NOT gated (G-1 fields missing or answers fail-closed)

It scans a goal report / call-for-review for "app-artifact parity" signals and,
when found, requires the G-1 machine-readable answer block:

  gate_generic_capability_produced: true|false
  gate_non_app_consumer: <name or "none">
  gate_requires_app_specific_logic: true|false
  gate_downstream_consumer_reachable: true|false

A parity item is BLOCKED (must fail-close, per G-1) if any of:
  - gate_generic_capability_produced is false, OR
  - gate_requires_app_specific_logic is true, OR
  - gate_downstream_consumer_reachable is false.
Missing fields are treated as blocked (cannot self-certify).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Signals that a document is pursuing byte/row/hash parity with an app/author
# implementation artifact (rather than producing a generic capability).
PARITY_SIGNALS = [
    r"hash[_ ]?parity",
    r"row[_ ]?identity",
    r"row[_ ]?count[_ ]?parity",
    r"byte[- ]?identical",
    r"offload[_ ]?stream",
    r"raw[_ ]?offload",
    r"author[_ ]?raw[_ ]?row",
    r"sample[_ ]?rows[_ ]?not[_ ]?recovered",
    r"namespace[_ ]?reconciliation",
    r"full[_ ]?cover[_ ]?surface",
    r"parity[_ ]?with[_ ]?author",
    r"-lb\b|explicit[_ ]?-?lb\b",
]

FIELD_RE = {
    "generic": re.compile(r"gate_generic_capability_produced\s*[:=]\s*(true|false)", re.I),
    "consumer": re.compile(r"gate_non_app_consumer\s*[:=]\s*(.+)", re.I),
    "appspecific": re.compile(r"gate_requires_app_specific_logic\s*[:=]\s*(true|false)", re.I),
    "reachable": re.compile(r"gate_downstream_consumer_reachable\s*[:=]\s*(true|false)", re.I),
}


def _b(v: str | None) -> bool | None:
    if v is None:
        return None
    return v.strip().lower() == "true"


def check_file(path: Path) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    low = text.lower()
    signals = sorted({s for s in PARITY_SIGNALS if re.search(s, low)})
    if not signals:
        return True, [f"{path.name}: no app-artifact-parity signals; gate N/A"]

    notes = [f"{path.name}: PARITY WORK DETECTED (signals: {', '.join(signals[:6])})"]
    generic = _b(FIELD_RE["generic"].search(text).group(1)) if FIELD_RE["generic"].search(text) else None
    appspec = _b(FIELD_RE["appspecific"].search(text).group(1)) if FIELD_RE["appspecific"].search(text) else None
    reach = _b(FIELD_RE["reachable"].search(text).group(1)) if FIELD_RE["reachable"].search(text) else None
    consumer_m = FIELD_RE["consumer"].search(text)
    consumer = consumer_m.group(1).strip() if consumer_m else None

    missing = [k for k, v in (("gate_generic_capability_produced", generic),
                              ("gate_requires_app_specific_logic", appspec),
                              ("gate_downstream_consumer_reachable", reach)) if v is None]
    if missing:
        notes.append("  BLOCKED (G-1): parity work without gate answers -> " + ", ".join(missing))
        return False, notes

    reasons = []
    if generic is False:
        reasons.append("no generic capability produced")
    if appspec is True:
        reasons.append("requires app-specific logic (success would violate core-neutrality)")
    if reach is False:
        reasons.append("downstream consumer unreachable (parent blocked)")
    if generic is True and (not consumer or consumer.lower() in {"none", "n/a", ""}):
        reasons.append("claims generic capability but names no non-app consumer")

    if reasons:
        notes.append("  BLOCKED (G-1): must fail-close -> " + "; ".join(reasons))
        return False, notes

    notes.append("  PASS: parity work is gated and produces a generic capability with a non-app consumer")
    return True, notes


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 0
    ok_all = True
    for arg in argv[1:]:
        p = Path(arg)
        if not p.is_file():
            print(f"{arg}: NOT FOUND")
            ok_all = False
            continue
        ok, notes = check_file(p)
        for n in notes:
            print(n)
        ok_all = ok_all and ok
    print()
    print("RESULT:", "PASS" if ok_all else "BLOCKED (fail-close required per G-1)")
    return 0 if ok_all else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
