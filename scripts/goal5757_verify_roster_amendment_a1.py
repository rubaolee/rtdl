from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
A1 = ROOT / "history/internal_docs/goal5757_roster_gate_amendment_a1_particle_tracking_known_regression_20260811.json"
CONTRACT_A1 = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_amendment_a1_20260811.json"


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(A1.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_A1.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS__NINE_PAPER_APP_COVERAGE_ROSTER_FROZEN"
    assert payload["authorized_paper_app_count"] == len(payload["authorized_app_ids"]) == 9
    assert len(set(payload["authorized_app_ids"])) == 9
    assert payload["authorized_lane_count"] == contract["authorized_lane_count_total"] == 13
    ninth = payload["ninth_app"]
    assert ninth["app_id"] == "particle_tracking"
    assert ninth["selection_was_before_support_observation"] is True
    assert ninth["replacement_allowed"] is False
    assert ninth["historical_goal5753_exam_status"] == "FAILED__MUST_NEVER_BE_RELABELLED_AS_HELD_OUT_PASS"
    assert ninth["current_goal5757_support_status"] == "UNOBSERVED"
    pins = {
        "history/internal_docs/goal5753_held_out_selection_20260811.json": ninth["selection_artifact_sha256"],
        "history/internal_docs/review_goal5753_owner_returned_external_20260811.md": ninth["owner_returned_review_sha256"],
        "history/internal_docs/goal5753_postreview_closure_20260811.md": ninth["postreview_closure_sha256"],
        "history/internal_docs/goal5757_paper_app_roster_gate_20260811.json": payload["supersedes_gate_result_sha256"],
        "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json": contract["base_contract_freeze_sha256"],
    }
    failures = []
    for path, expected in pins.items():
        observed = sha(path)
        if observed != expected:
            failures.append({"path": path, "expected": expected, "observed": observed})
    for path, expected in contract["promoted_known_regression_lane"]["source_pins"]:
        observed = sha(path)
        if observed != expected:
            failures.append({"path": path, "expected": expected, "observed": observed})
    assert all(value is False for value in payload["claim_boundary"].values())
    print(json.dumps({
        "schema": "rtdl.goal5757.roster_amendment_a1_check.v1",
        "authorized_apps": 9,
        "authorized_lanes": 13,
        "ninth_app": "particle_tracking",
        "goal5753_relabelled": False,
        "support_observed_before_freeze": False,
        "identity_failures": failures,
        "status": "PASS" if not failures else "FAIL_CLOSED",
    }, sort_keys=True, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
