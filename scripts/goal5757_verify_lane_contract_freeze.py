from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json"


def main() -> None:
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    lanes = payload["lanes"]
    assert payload["status"] == "CONTRACTS_FROZEN__V4_SUPPORT_NOT_OBSERVED"
    assert len(lanes) == 14
    assert len([row for row in lanes if row["qualification"] == "AUTHORIZED_PAPER_APP"]) == 12
    assert len([row for row in lanes if row["qualification"] == "CANDIDATE__NOT_PAPER_APP_9"]) == 2
    assert len({row["lane_id"] for row in lanes}) == len(lanes)
    failures: list[dict[str, str]] = []
    for row in lanes + [payload["held_out_control"]]:
        for relative, expected in row["source_pins"]:
            path = ROOT / relative
            if not path.is_file():
                failures.append({"path": relative, "error": "missing"})
                continue
            observed = hashlib.sha256(path.read_bytes()).hexdigest()
            if observed != expected:
                failures.append({
                    "path": relative, "error": "sha256_mismatch",
                    "expected": expected, "observed": observed,
                })
        for field in ("input_contract", "output_contract", "oracle_contract"):
            if not isinstance(row[field], str) or not row[field].strip():
                failures.append({"path": row["lane_id"], "error": f"missing_{field}"})
    assert payload["claim_boundary"] == {
        "contract_freeze_only": True,
        "v4_support_observed": False,
        "arkade_qualified": False,
        "particle_tracking_relabelled": False,
        "core_native_app_or_data_changed": False,
    }
    print(json.dumps({
        "schema": "rtdl.goal5757.lane_contract_freeze_check.v1",
        "authorized_lane_count": 12,
        "candidate_lane_count": 2,
        "held_out_control_count": 1,
        "identity_or_contract_failures": failures,
        "status": "PASS" if not failures else "FAIL_CLOSED",
    }, sort_keys=True, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
