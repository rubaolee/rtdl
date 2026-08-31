from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INTERNAL_DOCS = ROOT / "history" / "internal_docs"

SCHEMA = "rtdl.goal5053.v2_14_4_release_preflight.v1"

REQUIRED_REPORTS = [
    "goal5043_public_device_column_buffer_contract_2026-07-05.md",
    "goal5044_public_prepared_session_query_batch_contract_2026-07-05.md",
    "goal5045_public_device_order_by_cuda_lexsort_2026-07-05.md",
    "goal5046_device_group_by_public_readiness_decision_2026-07-06.md",
    "goal5047_numba_partner_continuation_public_api_2026-07-06.md",
    "goal5048_non_rayjoin_numba_partner_public_api_genericity_2026-07-06.md",
    "goal5049_rayjoin_public_v2144_surface_migration_2026-07-06.md",
    "goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md",
    "goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md",
    "goal5052_v2_14_4_public_api_pod_smoke_runner_2026-07-06.md",
    "goal5055_v2_14_4_pod_smoke_remote_launcher_2026-07-06.md",
    "goal5056_v2_14_4_strict_pod_smoke_result_2026-07-06.md",
    "goal5057_v2_14_4_pod_env_bootstrap_2026-07-06.md",
    "goal5058_v2_14_4_review_debt_content_gate_2026-07-06.md",
    "goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md",
    "goal5060_v2_14_4_substantive_review_gate_hardening_2026-07-06.md",
    "goal5061_v2_14_4_consolidated_review_quality_gate_2026-07-06.md",
    "goal5062_v2_14_4_dynamic_rayjoin_export_disclosure_gate_2026-07-06.md",
]

REVIEW_REQUIRED_GOALS = [5048, 5049, 5050, 5051, 5052, 5053, 5055, 5056, 5057, 5058, 5059, 5060, 5061, 5062]

REVIEW_MIN_CHARACTERS = 800
REVIEW_MIN_GOAL_SECTION_CHARACTERS = 350

REVIEW_REQUIRED_FIELDS = [
    "verdict_label:",
    "pass/fail/required_amendments:",
    "blocking_findings:",
    "non_blocking_notes:",
]

REVIEW_REQUIRED_GOAL_TERMS = {
    5048: ["non-rayjoin", "numba", "partner"],
    5049: ["rayjoin", "device_order_by", "app"],
    5050: ["boundary", "legacy", "compatibility"],
    5051: ["api consolidation", "devicecolumnbuffer", "performance boundary"],
    5052: ["pod smoke", "strict", "host_fallback"],
    5053: ["preflight", "external_review_debt", "blocked"],
    5055: ["remote", "pod", "launcher"],
    5056: ["strict pod smoke", "pass", "limits"],
    5057: ["cuda", "numba", "bootstrap"],
    5058: ["review debt", "malformed", "content"],
    5059: ["legacy public exports", "compatibility debt", "rtdsl.__all__"],
    5060: ["substantive review", "template", "gate"],
    5061: ["consolidated review", "padding", "goal section"],
    5062: ["dynamic", "rayjoin", "__all__"],
}

REVIEW_FORBIDDEN_PADDING_PHRASES = [
    "additional padding text",
    "satisfy the length requirement",
    "necessary target keywords",
    "terms we need for the goals include",
    "successfully satisfied all constraints",
]

CONSOLIDATED_REVIEW_PATTERNS = [
    "*review*v2_14_4*review*debt*.md",
    "*review*all_open_review_debt*.md",
]

EXPECTED_RAYJOIN_PUBLIC_EXPORTS = [
    "PreparedEmbreeRayjoinCdbPointLocation2D",
    "PreparedOptixRayjoinCdbPointLocation2D",
    "PreparedOptixRayjoinCdbPointLocationPoints2D",
    "RAYJOIN_PAPER_TARGETS",
    "RayJoinBoundedPlan",
    "RayJoinFeatureServiceLayer",
    "RayJoinPlan",
    "RayJoinPublicAsset",
    "chains_to_rayjoin_cdb_segments",
    "download_rayjoin_sample",
    "lower_to_rayjoin",
    "pack_rayjoin_cdb_segments",
    "prepare_rayjoin_cdb_point_location_2d_embree",
    "prepare_rayjoin_cdb_point_location_2d_optix",
    "rayjoin_bounded_plans",
    "rayjoin_feature_service_layers",
    "rayjoin_public_assets",
]

LEGACY_RAYJOIN_BOUNDARY_REPORTS = [
    "goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md",
    "goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md",
    "goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md",
]

POD_SMOKE_RESULT = INTERNAL_DOCS / "goal5052_v2144_public_api_pod_smoke_result.json"

PUBLIC_SCAN_TARGETS = [
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "examples" / "current",
    ROOT / "tutorials",
    ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "README.md",
]

PUBLIC_LEAK_PATTERNS = [
    re.compile(r"Goal[0-9]+"),
    re.compile(r"\bClaude\b|\bGemini\b|\bAntigravity\b|\bCodex\b"),
    re.compile(r"call_for_review|verdict", re.IGNORECASE),
    re.compile(r"history/internal_docs|internal_docs"),
    re.compile(r"\bV3\b|\bV4\b|v3\.0|v4\.0", re.IGNORECASE),
]

NOT_AUTHORIZED = {
    "public_release_ready_without_review": True,
    "public_release_ready_without_pod_smoke": True,
    "v2_14_4_speedup_claim": True,
    "true_zero_copy_claim": True,
    "author_parity_claim": True,
    "device_group_by_public_ready": True,
}


def _status(blocked: bool) -> str:
    return "blocked" if blocked else "pass"


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_required_reports() -> dict[str, Any]:
    missing = [name for name in REQUIRED_REPORTS if not (INTERNAL_DOCS / name).is_file()]
    return {
        "id": "required_goal_reports_present",
        "status": _status(bool(missing)),
        "missing": missing,
    }


def check_review_debt() -> dict[str, Any]:
    open_goals: list[str] = []
    malformed: dict[str, list[str]] = {}
    malformed_reasons: dict[str, dict[str, list[str]]] = {}
    found: dict[str, list[str]] = {}
    consolidated_paths = []
    for pattern in CONSOLIDATED_REVIEW_PATTERNS:
        consolidated_paths.extend(
            p
            for p in INTERNAL_DOCS.glob(pattern)
            if p.is_file() and not p.name.startswith("call_for_review_")
        )
    consolidated_paths = sorted(set(consolidated_paths))

    for goal in REVIEW_REQUIRED_GOALS:
        paths = sorted(
            p
            for p in INTERNAL_DOCS.glob(f"*review*goal{goal}*.md")
            if p.is_file() and not p.name.startswith("call_for_review_")
        )
        paths = sorted(set(paths + consolidated_paths))
        valid_paths: list[str] = []
        malformed_paths: list[str] = []
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            reasons = _review_content_rejection_reasons(text, goal)
            if not reasons:
                valid_paths.append(path.name)
            else:
                malformed_paths.append(path.name)
                malformed_reasons.setdefault(f"Goal{goal}", {})[path.name] = reasons
        if valid_paths:
            found[f"Goal{goal}"] = valid_paths
        if malformed_paths:
            malformed[f"Goal{goal}"] = malformed_paths
        if valid_paths:
            continue
        else:
            open_goals.append(f"Goal{goal}")
    return {
        "id": "external_review_debt",
        "status": _status(bool(open_goals or malformed)),
        "required_goals": [f"Goal{goal}" for goal in REVIEW_REQUIRED_GOALS],
        "found": found,
        "malformed": malformed,
        "malformed_reasons": malformed_reasons,
        "open": open_goals,
        "minimum_review_characters": REVIEW_MIN_CHARACTERS,
        "consolidated_review_patterns": CONSOLIDATED_REVIEW_PATTERNS,
    }


def _review_content_rejection_reasons(text: str, goal: int) -> list[str]:
    lowered = text.lower()
    section = _extract_goal_review_section(text, goal)
    section_lowered = section.lower()
    reasons: list[str] = []
    if len(text.strip()) < REVIEW_MIN_CHARACTERS:
        reasons.append(f"too_short_min_{REVIEW_MIN_CHARACTERS}_characters")
    if len(section.strip()) < REVIEW_MIN_GOAL_SECTION_CHARACTERS:
        reasons.append(f"goal_section_too_short_min_{REVIEW_MIN_GOAL_SECTION_CHARACTERS}_characters")
    forbidden_hits = [phrase for phrase in REVIEW_FORBIDDEN_PADDING_PHRASES if phrase in lowered]
    if forbidden_hits:
        reasons.append("forbidden_padding_or_keyword_stuffing_phrase:" + ",".join(forbidden_hits))
    for field in REVIEW_REQUIRED_FIELDS:
        if field not in section_lowered:
            reasons.append(f"missing_field_{field.rstrip(':')}")
    if not section:
        reasons.append(f"missing_goal{goal}_section")
    missing_terms = [
        term
        for term in REVIEW_REQUIRED_GOAL_TERMS.get(goal, [])
        if term.lower() not in section_lowered
    ]
    if missing_terms:
        reasons.append("missing_goal_specific_terms:" + ",".join(missing_terms))
    has_decision = any(token in section_lowered for token in ("approve", "pass", "revise", "fail", "block"))
    if not has_decision:
        reasons.append("missing_review_decision_token")
    verdict_value = _field_value(section, "verdict_label")
    disposition_value = _field_value(section, "pass/fail/required_amendments")
    blocking_value = _field_value(section, "blocking_findings")
    if verdict_value and not _is_passing_verdict(verdict_value):
        reasons.append("non_passing_verdict_label")
    if disposition_value and not _is_passing_disposition(disposition_value):
        reasons.append("non_passing_disposition")
    if blocking_value and not _is_no_blocking_findings(blocking_value):
        reasons.append("blocking_findings_present")
    return reasons


def _extract_goal_review_section(text: str, goal: int) -> str:
    pattern = re.compile(
        rf"(?ims)^#+\s*Goal{goal}\b.*?(?=^#+\s*Goal\d+\b|\Z)"
    )
    match = pattern.search(text)
    if match:
        return match.group(0)
    if f"goal{goal}" in text.lower():
        return text
    return ""


def _field_value(section: str, field: str) -> str:
    pattern = re.compile(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*?)\s*$")
    match = pattern.search(section)
    return match.group(1).strip().lower() if match else ""


def _is_passing_verdict(value: str) -> bool:
    return ("approve" in value or "pass" in value) and not any(
        token in value for token in ("revise", "fail", "block", "required_amendment")
    )


def _is_passing_disposition(value: str) -> bool:
    return value in {"pass", "passed", "approve", "approved"} or (
        value.startswith("pass") and not any(token in value for token in ("amend", "revise", "fail", "block"))
    )


def _is_no_blocking_findings(value: str) -> bool:
    normalized = value.strip().lower().rstrip(".")
    return normalized in {"none", "no", "no blocking findings", "n/a", "na"}


def check_pod_smoke() -> dict[str, Any]:
    if not POD_SMOKE_RESULT.is_file():
        return {
            "id": "strict_pod_smoke",
            "status": "blocked",
            "required_result": _rel(POD_SMOKE_RESULT),
            "reason": "missing strict Goal5052 POD smoke JSON",
        }

    try:
        payload = json.loads(POD_SMOKE_RESULT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "id": "strict_pod_smoke",
            "status": "blocked",
            "required_result": _rel(POD_SMOKE_RESULT),
            "reason": f"invalid JSON: {exc}",
        }

    strict = payload.get("strict")
    overall = payload.get("overall_status")
    blocked = not (strict is True and overall == "pass")
    return {
        "id": "strict_pod_smoke",
        "status": _status(blocked),
        "required_result": _rel(POD_SMOKE_RESULT),
        "observed_strict": strict,
        "observed_overall_status": overall,
        "reason": None if not blocked else "Goal5052 POD smoke must be strict=true and overall_status=pass",
    }


def _iter_public_files() -> list[Path]:
    files: list[Path] = []
    for target in PUBLIC_SCAN_TARGETS:
        if not target.exists():
            continue
        if target.is_file():
            files.append(target)
            continue
        files.extend(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".py", ".txt"})
    return sorted(files)


def check_public_leak_scan() -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for path in _iter_public_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in PUBLIC_LEAK_PATTERNS:
                if pattern.search(line):
                    hits.append(
                        {
                            "file": _rel(path),
                            "line": str(line_no),
                            "pattern": pattern.pattern,
                            "text": line.strip()[:200],
                        }
                    )
    return {
        "id": "public_surface_internal_leak_scan",
        "status": _status(bool(hits)),
        "targets": [_rel(p) for p in PUBLIC_SCAN_TARGETS],
        "hits": hits,
    }


def check_legacy_rayjoin_public_exports_disclosed() -> dict[str, Any]:
    init_path = ROOT / "src" / "rtdsl" / "__init__.py"
    init_text = init_path.read_text(encoding="utf-8", errors="replace")
    observed_exports = _rayjoin_exports_from_init_all(init_text)
    missing_exports = [
        name
        for name in EXPECTED_RAYJOIN_PUBLIC_EXPORTS
        if name not in observed_exports
    ]
    unexpected_exports = [
        name
        for name in observed_exports
        if name not in EXPECTED_RAYJOIN_PUBLIC_EXPORTS
    ]

    missing_reports: list[str] = []
    missing_phrases: dict[str, list[str]] = {}
    required_phrases = [
        "legacy public exports",
        "compatibility debt",
    ]
    for report_name in LEGACY_RAYJOIN_BOUNDARY_REPORTS:
        path = INTERNAL_DOCS / report_name
        if not path.is_file():
            missing_reports.append(report_name)
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        missing = [phrase for phrase in required_phrases if phrase not in text]
        missing += [name for name in observed_exports if name.lower() not in text]
        if missing:
            missing_phrases[report_name] = missing

    blocked = bool(missing_exports or unexpected_exports or missing_reports or missing_phrases)
    return {
        "id": "legacy_rayjoin_public_exports_disclosed",
        "status": _status(blocked),
        "exports": observed_exports,
        "expected_exports": EXPECTED_RAYJOIN_PUBLIC_EXPORTS,
        "missing_expected_exports_from_rtdsl_all": missing_exports,
        "unexpected_rayjoin_exports_from_rtdsl_all": unexpected_exports,
        "required_reports": LEGACY_RAYJOIN_BOUNDARY_REPORTS,
        "missing_reports": missing_reports,
        "missing_report_phrases": missing_phrases,
        "required_classification": "legacy public exports / compatibility debt; not new v2.14.4 public generic API",
    }


def _rayjoin_exports_from_init_all(init_text: str) -> list[str]:
    start = init_text.find("__all__")
    if start < 0:
        return []
    segment = init_text[start:]
    quoted = re.findall(r'"([^"]*rayjoin[^"]*)"', segment, flags=re.IGNORECASE)
    return sorted(set(quoted), key=str.lower)


def build_payload() -> dict[str, Any]:
    checks = [
        check_required_reports(),
        check_review_debt(),
        check_pod_smoke(),
        check_public_leak_scan(),
        check_legacy_rayjoin_public_exports_disclosed(),
    ]
    blockers = [
        {"id": check["id"], "detail": check}
        for check in checks
        if check["status"] == "blocked"
    ]
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": "ready_for_public_release_staging" if not blockers else "blocked_by_release_gates",
        "checks": checks,
        "blockers": blockers,
        "not_authorized": NOT_AUTHORIZED,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal5053 v2.14.4 release preflight.")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=INTERNAL_DOCS / "goal5053_v2144_release_preflight_result.json",
        help="Path to write the machine-readable preflight result.",
    )
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="Return success even when release gates are blocked; useful for evidence generation.",
    )
    args = parser.parse_args(argv)

    payload = build_payload()
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))

    if payload["overall_status"] == "blocked_by_release_gates" and not args.allow_blocked:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
