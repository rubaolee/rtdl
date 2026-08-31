#!/usr/bin/env python3
"""Independent final-byte and claim-boundary verifier for Goal5757.

This verifier intentionally imports none of the probe generator, semantic
coverage checker, primary evidence verifier, or migration verifier.  It checks
the immutable review packet and the small set of load-bearing aggregate facts
directly from their serialized artifacts.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PINNED_SHA256 = {
    "history/internal_docs/goal5757_v4_nine_paper_app_coverage_result_20260811.json":
        "c4b5aa643475b0e0be92af6ff5176c6f007ffd2e6bd4948e7208e02e28383d0e",
    "history/internal_docs/goal5757_v4_nine_paper_app_coverage_technical_report_20260811.md":
        "3edb95bd89e3b6c0b5ac0c867768e0c1f188eecf7a6e620c4b970683c38a171a",
    "history/internal_docs/self_review_goal5757_v4_nine_paper_app_coverage_20260811.md":
        "b929708663153dae711b7a1a3e090374a4637e680a177f058907145ad70832da",
    "history/internal_docs/call_for_review_goal5757_v4_nine_paper_app_coverage_and_migration_20260811.md":
        "9fc0267cea57c96d8cecc7ae5318749fc2edd393e975c791cf7a85ccb959f38d",
    "history/internal_docs/goal5757_lane_probe_evidence_20260811/MATRIX.json":
        "ac208986065be66b1378c5458e7deb7c065e720a01432b76f32eaa43e70a5e34",
    "history/internal_docs/goal5757_lane_probe_evidence_20260811/MANIFEST.json":
        "92d86fd92fc532be2935dc81c242a5bc70fc9f57c785eda9d5db7ef074bcc680",
    "history/internal_docs/goal5757_lane_probe_evidence_20260811.tar.gz":
        "536be08b2c4d8c56c4ff430fce08da0b6d79ee9881bd160f75846889eb009673",
    "history/internal_docs/goal5757_lane_probe_evidence_twin_20260811.tar.gz":
        "536be08b2c4d8c56c4ff430fce08da0b6d79ee9881bd160f75846889eb009673",
    "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json":
        "70f6dff47af6ac5a857cd37448d753dc11c6ddecb29e60857eaaa1bc9082a113",
    "scripts/goal5757_run_lane_probes.py":
        "7d6dbe9adfc8bb15bd726f42d121f33d03f33d570c7c78b30dc1981784b3489b",
    "scripts/goal5757_verify_lane_probe_evidence.py":
        "30c095f5e6acd4e41be8b09af3aa05087167fb01f2d483748b51749f8a430703",
    "scripts/goal5757_semantic_coverage.py":
        "d154e4279fc26faa88086d8cac6244b6a2fc3b4adaa55064ab9762dd27540e32",
    "scripts/goal5757_verify_migration_batches.py":
        "c604f7f0319f361d5786e8a660e0e0666b6843501df9a0586cee382ab088eabf",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    for relative, expected in PINNED_SHA256.items():
        path = ROOT / relative
        require(path.is_file(), f"missing pinned artifact: {relative}")
        actual = sha256(path)
        require(actual == expected, f"SHA mismatch: {relative}: {actual} != {expected}")

    result = load_json(
        "history/internal_docs/goal5757_v4_nine_paper_app_coverage_result_20260811.json"
    )
    matrix = load_json("history/internal_docs/goal5757_lane_probe_evidence_20260811/MATRIX.json")
    migration = load_json(
        "history/internal_docs/goal5757_v4_nine_app_migration_batches_20260811.json"
    )

    require(result["goal"] == 5757, "wrong goal")
    require(result["frozen_v4_identity"]["frozen_file_count"] == 19, "wrong core freeze size")
    require(result["frozen_v4_identity"]["core_mismatch_count"] == 0, "core drift")
    require(result["roster_and_contracts"]["paper_app_count"] == 9, "wrong app count")
    require(result["roster_and_contracts"]["lane_count"] == 13, "wrong lane count")

    lanes = matrix["results"]
    require(len(lanes) == 13, "matrix does not contain 13 lanes")
    require(len({lane["app_id"] for lane in lanes}) == 9, "matrix does not contain 9 apps")
    classifications = Counter(lane["classification"] for lane in lanes)
    require(
        classifications
        == Counter({"MISSING_GENERIC_SEMANTIC": 12, "SUPPORTED_NOW": 1}),
        f"unexpected classifications: {dict(classifications)}",
    )
    supported = [lane for lane in lanes if lane["classification"] == "SUPPORTED_NOW"]
    require(
        f"{supported[0]['app_id']}.{supported[0]['lane_id']}"
        == "particle_tracking.tetrahedral_face_point_location_and_boundary_detection",
        "unexpected supported lane",
    )

    missing_lane_ids = {
        f"{lane['app_id']}.{lane['lane_id']}"
        for lane in lanes
        if lane["classification"] == "MISSING_GENERIC_SEMANTIC"
    }
    batches = migration["proposed_batches"]
    assigned = [lane_id for batch in batches for lane_id in batch["lanes"]]
    require(len(batches) == 6, "wrong migration batch count")
    require(Counter(assigned) == Counter(missing_lane_ids), "missing lanes not assigned exactly once")
    require(
        all(batch["implementation_authorized"] is False for batch in batches),
        "migration implementation was authorized",
    )

    boundary = result["claim_boundary"]
    require(boundary["goal5757_coverage_audit_complete"] is True, "audit not closed")
    for key in (
        "nine_app_v4_implementation_complete",
        "v4_core_native_or_paper_app_changed",
        "new_primitive_added",
        "app_named_runtime_dispatch_added",
        "pod_or_performance_used",
        "goal5753_held_out_pass_claimed",
        "held_out_generalization_claimed",
        "production_public_submission_claimed",
        "migration_implementation_authorized",
    ):
        require(boundary[key] is False, f"claim boundary violated: {key}")

    print(
        json.dumps(
            {
                "status": "PASS",
                "pinned_artifacts": len(PINNED_SHA256),
                "paper_apps": 9,
                "lanes": 13,
                "classifications": dict(sorted(classifications.items())),
                "migration_batches": 6,
                "missing_lanes_assigned_exactly_once": True,
                "nine_app_v4_implementation_complete": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # fail closed with one stable diagnostic line
        print(f"GOAL5757_CLOSEOUT_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
