#!/usr/bin/env python3
"""Build Goal5443 ACM supplement access-gate summary.

The raw live probe is produced by ``probe_xhd_acm_supplement_live_access.py``.
This wrapper turns that raw result into a status-bearing goal artifact tied to
the current X-HD full-reproduction blocker.

It does not run the probe, inspect zip contents, run POD, run author code, or
run RTDL routes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5443_acm_supplement_access_gate.json"
RAW_PROBE = RESULTS / "xhd_goal5443_acm_supplement_live_access_retry.json"
PUBLIC_RESCAN = RESULTS / "xhd_goal5442_public_provenance_rescan.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def build_payload() -> dict[str, Any]:
    raw = _load_json(RAW_PROBE)
    rescan = _load_json(PUBLIC_RESCAN)
    checks = raw["url_checks"]
    head_statuses = [row["head"].get("status") for row in checks]
    range_statuses = [row["range_get"].get("status") for row in checks]
    zip_magic_observed = any(bool(row["range_get"].get("zip_magic")) for row in checks)
    all_forbidden = all(status == 403 for status in head_statuses + range_statuses)
    current_environment_can_download_zip = zip_magic_observed or any(
        bool(row["range_get"].get("ok")) and str(row["range_get"].get("content_type", "")).lower() != "text/html; charset=utf-8"
        for row in checks
    )
    status = (
        "acm_supplement_access_gate_zip_magic_observed__inspect_before_claim"
        if zip_magic_observed
        else "acm_supplement_access_gate_forbidden__external_access_still_needed"
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5443.acm_supplement_access_gate.v1",
        "goal": "Goal5443",
        "date": "2026-07-10",
        "purpose": "Convert the current ACM supplement live-access retry into an explicit paper-reproduction access gate.",
        "status": status,
        "source_artifacts": {
            "raw_live_probe": _rel(RAW_PROBE),
            "goal5442_public_rescan": _rel(PUBLIC_RESCAN),
            "probe_script": _rel(APP / "scripts" / "probe_xhd_acm_supplement_live_access.py"),
            "local_zip_inspector": _rel(APP / "scripts" / "inspect_xhd_acm_supplement_zip.py"),
            "artifact_ingestion_pipeline": _rel(APP / "scripts" / "run_xhd_acm_artifact_to_packet_pipeline.py"),
        },
        "raw_probe_summary": {
            "schema": raw["schema"],
            "artifact_name": raw["artifact_name"],
            "classification": raw["classification"],
            "used_cookie_header": raw["used_cookie_header"],
            "url_count": len(raw["urls"]),
            "head_statuses": head_statuses,
            "range_get_statuses": range_statuses,
            "range_content_types": [row["range_get"].get("content_type") for row in checks],
            "zip_magic_observed": zip_magic_observed,
            "all_current_attempts_forbidden": all_forbidden,
            "next_action": raw["next_action"],
        },
        "classification": {
            "acm_listing_visible": bool(rescan["classification"]["acm_zip_listing_observed"]),
            "current_environment_can_download_zip": current_environment_can_download_zip,
            "zip_contents_inspected": False,
            "acm_supplement_inspected": False,
            "exact_input_blocker_removed": False,
            "pod_expected_next": False,
        },
        "interpretation": {
            "access_gate_result": (
                "current_environment_forbidden"
                if all_forbidden and not zip_magic_observed
                else "requires_manual_review_before_use"
            ),
            "next_action": (
                "obtain authorized ACM access/cookie or author artifact; then run the local zip inspector and ingestion pipeline"
                if not zip_magic_observed
                else "inspect downloaded zip contents before any route/POD gate"
            ),
            "reason_pod_not_expected": (
                "POD cannot inspect a forbidden ACM supplement URL and cannot turn listing visibility into exact input provenance."
            ),
        },
        "claim_boundary": {
            "acm_access_gate_claimed": True,
            "acm_supplement_inspected": False,
            "zip_contents_inspected": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "ACM supplement access gate / artifact-intake governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: access/provenance gate, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "Goal5443 records that the current unauthenticated environment still cannot inspect the ACM "
            "ics26-106.zip supplement: all known URL attempts return forbidden HTML and no zip magic."
        ),
        "not_allowed": [
            "claiming the ACM supplement contents were inspected",
            "claiming the ACM supplement contains datasets",
            "claiming the ACM supplement contains no useful artifacts",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming an author-vs-RTDL performance ratio",
            "running POD or route work from this access gate",
        ],
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "current_environment_can_download_zip": payload["classification"]["current_environment_can_download_zip"],
        "exact_input_blocker_removed": payload["classification"]["exact_input_blocker_removed"],
        "pod_expected_next": payload["classification"]["pod_expected_next"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
