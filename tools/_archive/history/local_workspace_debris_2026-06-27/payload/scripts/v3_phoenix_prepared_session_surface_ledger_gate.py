#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
PACKAGE_INIT = ROOT / "src" / "rtdsl" / "__init__.py"
CURRENT_LEDGER = ROOT / "docs" / "reports" / "phoenix_v3_m37_prepared_session_step4_surface_ledger_2026-06-23.md"

RUNNER_SURFACE = {
    "run_prepared_execution_session",
    "run_repeated_prepared_execution_session",
}

EXPECTED_COUNTS = {
    "step4_ready": 9,
    "blocked_set_a_seed": 1,
    "blocked_set_b_control": 3,
}


def _literal_all_names(source: str) -> tuple[str, ...]:
    module = ast.parse(source)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        return tuple(str(item) for item in value)
    raise ValueError("__all__ not found in prepared_execution.py")


def public_helper_names(source: str) -> tuple[str, ...]:
    names = _literal_all_names(source)
    helpers = [
        name
        for name in names
        if name.startswith("run_")
        and name.endswith("_prepared_session")
        and name not in RUNNER_SURFACE
    ]
    return tuple(sorted(helpers))


def ledger_classifications(markdown: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    pattern = re.compile(r"^\|\s*`(?P<helper>run_[^`]+_prepared_session)`\s*\|\s*(?P<classification>[^|]+?)\s*\|", re.MULTILINE)
    for match in pattern.finditer(markdown):
        helper = match.group("helper").strip()
        classification = match.group("classification").strip()
        rows[helper] = classification
    return rows


def classify_counts(rows: dict[str, str]) -> dict[str, int]:
    counts = {
        "step4_ready": 0,
        "blocked_set_a_seed": 0,
        "blocked_set_b_control": 0,
        "other": 0,
    }
    for classification in rows.values():
        if classification == "Step-4 ready by local audit":
            counts["step4_ready"] += 1
        elif classification == "blocked Set-A seed":
            counts["blocked_set_a_seed"] += 1
        elif classification == "blocked Set-B control":
            counts["blocked_set_b_control"] += 1
        else:
            counts["other"] += 1
    return counts


def build_payload() -> dict[str, object]:
    source = PREPARED_EXECUTION.read_text(encoding="utf-8")
    package_source = PACKAGE_INIT.read_text(encoding="utf-8")
    ledger = CURRENT_LEDGER.read_text(encoding="utf-8")
    helpers = public_helper_names(source)
    package_all_names = set(_literal_all_names(package_source))
    rows = ledger_classifications(ledger)
    helper_set = set(helpers)
    row_set = set(rows)
    missing_from_ledger = sorted(helper_set - row_set)
    stale_ledger_rows = sorted(row_set - helper_set)
    missing_from_package_exports = [
        helper
        for helper in helpers
        if helper not in package_all_names
        or f"from .prepared_execution import {helper}" not in package_source
    ]
    counts = classify_counts(rows)
    count_mismatches = {
        key: {"expected": expected, "actual": counts.get(key, 0)}
        for key, expected in EXPECTED_COUNTS.items()
        if counts.get(key, 0) != expected
    }
    errors: list[str] = []
    if missing_from_ledger:
        errors.append("public_prepared_session_helpers_missing_from_current_ledger")
    if stale_ledger_rows:
        errors.append("current_ledger_rows_not_exported_public_helpers")
    if missing_from_package_exports:
        errors.append("prepared_session_helpers_missing_from_package_exports")
    if count_mismatches:
        errors.append("current_classification_count_mismatch")
    if counts.get("other", 0):
        errors.append("current_unknown_classification_present")
    return {
        "tool": "v3_phoenix_prepared_session_surface_ledger_gate",
        "version": "2026_06_23_m37",
        "package_init_source": str(PACKAGE_INIT.relative_to(ROOT)),
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "prepared_execution_source": str(PREPARED_EXECUTION.relative_to(ROOT)),
        "current_ledger": str(CURRENT_LEDGER.relative_to(ROOT)),
        "public_helper_count": len(helpers),
        "ledger_row_count": len(rows),
        "public_helpers": helpers,
        "ledger_classifications": rows,
        "classification_counts": counts,
        "expected_counts": EXPECTED_COUNTS,
        "count_mismatches": count_mismatches,
        "missing_from_ledger": missing_from_ledger,
        "stale_ledger_rows": stale_ledger_rows,
        "missing_from_package_exports": missing_from_package_exports,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_pod_spend_authorized": False,
    }


def main() -> int:
    payload = build_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
