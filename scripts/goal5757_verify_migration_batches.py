from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811/MATRIX.json"
BATCH_PATH = ROOT / "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    batches = json.loads(BATCH_PATH.read_text(encoding="utf-8"))
    assert batches["coverage_matrix_sha256"] == hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest()
    assert batches["observed_baseline"] == {
        "paper_apps": 9,
        "lanes": 13,
        "supported_now": 1,
        "partner_only_gap": 0,
        "missing_generic_semantic": 12,
    }
    missing = {
        f"{item['app_id']}.{item['lane_id']}"
        for item in matrix["results"]
        if item["classification"] == "MISSING_GENERIC_SEMANTIC"
    }
    assigned = [lane for batch in batches["proposed_batches"] for lane in batch["lanes"]]
    assert len(assigned) == len(set(assigned)) == 12
    assert set(assigned) == missing
    assert batches["already_supported"]["lanes"] == [
        "particle_tracking.tetrahedral_face_point_location_and_boundary_detection"
    ]
    assert len(batches["proposed_batches"]) == len(batches["ordering"]) == 6
    assert {item["batch_id"] for item in batches["proposed_batches"]} == set(batches["ordering"])
    for batch in batches["proposed_batches"]:
        assert batch["implementation_authorized"] is False
        assert len(batch["kill_gates"]) >= 3
        assert "arkade" not in json.dumps(batch).lower()
    assert all(value is False for value in batches["claim_boundary"].values())
    print(json.dumps({
        "status": "PASS",
        "missing_lanes_assigned_once": len(assigned),
        "migration_batches": len(batches["proposed_batches"]),
        "supported_lanes_frozen": len(batches["already_supported"]["lanes"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
