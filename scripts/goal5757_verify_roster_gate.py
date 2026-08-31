from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "history/internal_docs/goal5757_paper_app_roster_gate_20260811.json"


def main() -> None:
    payload = json.loads(ROSTER.read_text(encoding="utf-8"))
    assert payload["schema"] == "rtdl.goal5757.paper_app_roster_gate.v1"
    assert payload["required_authorized_paper_app_count"] == 9
    assert payload["authorized_paper_app_count"] == len(payload["authorized_apps"]) == 8
    assert payload["owner_qualified_ninth_app"] is None
    assert payload["support_observation_allowed_after_gate"] is False
    assert payload["status"] == "FAIL_CLOSED__NINTH_PAPER_APP_NOT_OWNER_QUALIFIED"
    assert {row["app_id"] for row in payload["authorized_apps"]} == {
        "rtnn", "raydb", "librts", "x_hd", "rt_dbscan", "rayjoin",
        "rt_barneshut", "triangle_counting",
    }
    assert {row["app_id"] for row in payload["excluded_candidates"]} == {
        "arkade", "particle_tracking",
    }
    assert sum(len(row["lanes"]) for row in payload["authorized_apps"]) == 12
    failures: list[dict[str, str]] = []
    for row in payload["authorized_apps"] + payload["excluded_candidates"]:
        path = ROOT / row["contract_path"]
        if not path.is_file():
            failures.append({"path": row["contract_path"], "error": "missing"})
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != row["contract_sha256"]:
            failures.append({
                "path": row["contract_path"],
                "error": "sha256_mismatch",
                "expected": row["contract_sha256"],
                "observed": observed,
            })
    claims = payload["claim_boundary"]
    assert all(value is False for value in claims.values())
    print(json.dumps({
        "schema": "rtdl.goal5757.paper_app_roster_gate_check.v1",
        "authorized_apps": len(payload["authorized_apps"]),
        "authorized_lanes": sum(len(row["lanes"]) for row in payload["authorized_apps"]),
        "excluded_candidates": len(payload["excluded_candidates"]),
        "identity_failures": failures,
        "status": payload["status"] if not failures else "FAIL_CLOSED__ROSTER_IDENTITY_MISMATCH",
    }, sort_keys=True, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
