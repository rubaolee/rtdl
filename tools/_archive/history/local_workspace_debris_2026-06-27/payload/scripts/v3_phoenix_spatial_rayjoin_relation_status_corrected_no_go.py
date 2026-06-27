#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REJECTED_LOG = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_rayjoin_relation_status_corrected_rejected_smoke_20260621"
    / "run.log"
)
EXACT_EXECUTOR_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.json"
)
STATUS = "spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch"


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phoenix V3 Spatial relation-status corrected executor no-go packet."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.json",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=ROOT
        / "docs"
        / "rebuild"
        / "v3"
        / "phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def build_payload() -> dict[str, Any]:
    log_text = REJECTED_LOG.read_text(encoding="utf-8") if REJECTED_LOG.exists() else ""
    exact_count, observed_count = _parse_mismatch(log_text)
    exact_intake = json.loads(EXACT_EXECUTOR_INTAKE.read_text(encoding="utf-8"))
    checks = {
        "rejected_log_exists": REJECTED_LOG.exists(),
        "mismatch_recorded": exact_count == 47262 and observed_count == 47259,
        "relation_status_mode_was_explicit": "relation_status_corrected_executor_validated" in log_text,
        "failed_before_evidence_promotion": "RuntimeError" in log_text and "did not match exact" in log_text,
        "exact_executor_intake_remains_not_m7": (
            exact_intake.get("status") == "spatial_rayjoin_exact_executor_intake_not_m7"
            and exact_intake.get("m7_promotion_authorized") is False
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "tool": "v3_phoenix_spatial_rayjoin_relation_status_corrected_no_go",
        "status": "fail" if failed_checks else STATUS,
        "generic_capability": "point_location_topology_stream",
        "candidate_route": "relation_status_corrected_executor_validated",
        "source_log": _rel(REJECTED_LOG),
        "dataset": "/root/rtdl_v3_rebuild_20260620/current/data/rayjoin_public_cdb/br_county.cdb",
        "gpu": "NVIDIA RTX 4000 Ada Generation, 550.127.05",
        "exact_authority_count": exact_count,
        "candidate_count": observed_count,
        "candidate_minus_exact": None if exact_count is None or observed_count is None else observed_count - exact_count,
        "failure_class": "validated_candidate_exactness_mismatch",
        "interpretation": (
            "The relation-status corrected executor is a reusable generic device-side scalar-count candidate, "
            "but it is not exact on the public county packet. The fail-closed validation worked and no "
            "Spatial RayJoin M7 or public speedup claim is authorized."
        ),
        "next_engine_action": (
            "Keep the route diagnostic-only until relation-status boundary semantics match exact prepared "
            "closed-shape membership on public county plus adverse subset evidence."
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Reject the relation-status corrected Spatial executor for Phoenix M7 after exact-count "
                "validation failed on public county."
            ),
            "was_i_foolish": (
                "No. I tried a plausible existing generic continuation route but required exact parity before "
                "allowing evidence promotion."
            ),
            "foolish_actions": (
                "The foolish action would be to keep the faster-looking route, hide the 47259 != 47262 mismatch, "
                "or call it an acceptable approximation for V3."
            ),
            "other_path": (
                "I could have skipped this route because old history had mixed correctness. Testing it with a "
                "fail-closed gate was better because it produced current evidence."
            ),
            "different_path_now": (
                "Do not promote relation-status corrected Spatial. Continue with exact topology-continuation "
                "correctness repair or another generic engine target."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial RayJoin Relation-Status Corrected Executor No-Go",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet records a rejected generic point-location topology-stream candidate.",
        "It is not a release packet, not M7, and not public speedup evidence.",
        "",
        "## Evidence",
        "",
        f"- Source log: `{payload['source_log']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- GPU: `{payload['gpu']}`",
        f"- Candidate route: `{payload['candidate_route']}`",
        f"- Exact authority count: `{payload['exact_authority_count']}`",
        f"- Candidate count: `{payload['candidate_count']}`",
        f"- Candidate minus exact: `{payload['candidate_minus_exact']}`",
        f"- Failure class: `{payload['failure_class']}`",
        "",
        "## Interpretation",
        "",
        payload["interpretation"],
        "",
        "## Claim Boundary",
        "",
        f"- `release_authorized: {str(payload['release_authorized']).lower()}`",
        f"- `public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}`",
        f"- `m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}`",
        f"- `m7_qualified_release_rows_added: {payload['m7_qualified_release_rows_added']}`",
        "",
        "## Next Engine Action",
        "",
        payload["next_engine_action"],
        "",
        "## Goal-Level Decision Self-Audit",
        "",
        f"Decision: {audit['decision']}",
        "",
        "1. Was I foolish?",
        f"   {audit['was_i_foolish']}",
        "2. If yes, what actions made the decision foolish?",
        f"   {audit['foolish_actions']}",
        "3. Was there another path that would have avoided getting stuck on one idea?",
        f"   {audit['other_path']}",
        "4. Can I now try a different path that actually solves the problem?",
        f"   {audit['different_path_now']}",
        "",
    ]
    return "\n".join(lines)


def _parse_mismatch(text: str) -> tuple[int | None, int | None]:
    cleaned = re.sub(r"\x1b\[[0-9;]*m", "", text)
    match = re.search(r"did not match exact prepared count:\s*(\d+)\s*!=\s*(\d+)", cleaned)
    if not match:
        return None, None
    observed = int(match.group(1))
    exact = int(match.group(2))
    return exact, observed


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
