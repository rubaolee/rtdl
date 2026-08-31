#!/usr/bin/env python3
"""Independent structural recount of the nine-app Home real-scale gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history/internal_docs"
FILES = {
    "Particle Tracking": "goal5776_particle_home_real_scale_smoke_20260813.json",
    "Triangle Counting": "goal5776_triangle_com_dblp_home_real_scale_smoke_20260813.json",
    "RT-DBSCAN": "goal5776_rtdbscan_home_real_scale_grouped_smoke_20260813.json",
    "RTNN": "goal5776_rtnn_home_real_scale_smoke_20260813.json",
    "RT-BarnesHut": "goal5776_rt_barneshut_home_real_scale_smoke_20260813.json",
    "X-HD": "goal5776_xhd_home_real_scale_smoke_20260813.json",
    "RayDB": "goal5776_raydb_home_real_scale_smoke_20260813.json",
    "LibRTS": "goal5776_librts_home_real_scale_smoke_20260813.json",
    "RayJoin": "goal5776_rayjoin_home_real_scale_smoke_20260813.json",
}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _receipts(value):
    if isinstance(value, dict):
        if value.get("schema") == "rtdl.physical_execution.traversal_receipt.v1":
            yield value
        for child in value.values():
            yield from _receipts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _receipts(child)


def _receipt_ok(receipt: dict[str, object], native_sha: str) -> bool:
    snapshot = receipt["native_snapshot"]
    successful = snapshot["successful_launch_count"]
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and receipt["provider_library_sha256"] == native_sha
        and isinstance(successful, int) and successful > 0
        and snapshot["complete_context_launch_count"] == successful
        and snapshot["failed_launch_count"] == 0
        and snapshot["incomplete_context_launch_count"] == 0
        and snapshot["pending_context_at_finish"] == 0
        and snapshot["session_error"] == 0
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _correct(app: str, data: dict[str, object]) -> bool:
    if data.get("status") != "passed" \
            or data.get("registered_performance_observation_created") is not False:
        return False
    if app == "Triangle Counting":
        return data.get("correct_lane_count") == 4 and all(
            row[method]["matched"] is True
            for row in data["rows"] for method in ("v2_direct", "v4"))
    if app == "LibRTS":
        expected = data["expected_counts"]
        return all(
            data["v4"][operation]["count"] == expected[operation]
            and data["v2_direct"]["operations"][operation]["count"] == expected[operation]
            for operation in expected)
    if app == "RayJoin":
        return data.get("batch_count") == 6 and len(data["canonical_output"]) == 6
    return data["v4"].get("matched") is True \
        and data["v2_direct"].get("matched") is True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    native_shas = set()
    total_receipts = 0
    for app, name in FILES.items():
        path = DOCS / name
        data = json.loads(path.read_text(encoding="utf-8"))
        native = data["native_library_sha256"]
        native_shas.add(native)
        receipts = tuple(_receipts(data))
        if not receipts or not all(_receipt_ok(row, native) for row in receipts):
            raise RuntimeError(f"{app} traversal receipt failed")
        if not _correct(app, data):
            raise RuntimeError(f"{app} correctness contract failed")
        total_receipts += len(receipts)
        rows.append({
            "app": app,
            "result_file": name,
            "result_sha256": _sha(path),
            "correct": True,
            "behaviorally_true_optix": True,
            "traversal_receipt_count": len(receipts),
            "registered_performance_observation_created": False,
        })
    if len(native_shas) != 1:
        raise RuntimeError(f"nine-app native identity split: {sorted(native_shas)}")
    result = {
        "schema": "rtdl.goal5776.home_real_scale_matrix_recount.v1",
        "status": "passed",
        "app_count": len(rows),
        "correct_app_count": sum(row["correct"] for row in rows),
        "behaviorally_true_optix_app_count": sum(
            row["behaviorally_true_optix"] for row in rows),
        "traversal_receipt_count": total_receipts,
        "distinct_native_count": len(native_shas),
        "native_library_sha256": next(iter(native_shas)),
        "rows": rows,
        "claim_boundary": {
            "formal_performance_result_created": False,
            "home_capacity_and_correctness_only": True,
            "modern_rtx_claimed": False,
            "no_slower_claimed": False,
        },
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)


if __name__ == "__main__":
    main()
