#!/usr/bin/env python3
"""Independently recount a Goal5769 Home functional result directory.

This verifier imports neither the transaction harness nor the application
frontdoors.  It creates no workers and ignores all elapsed-time fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


METHODS = (
    "v2_direct_true_optix_backport",
    "v3_compiler_true_optix",
    "v4_restricted_callback_true_optix",
)
EXPECTED_LANES = (
    "librts__overlap_filter",
    "librts__range_rows",
    "particle__cell_transition",
    "raydb__q21",
    "rayjoin__grouped_events",
    "rayjoin__point_location",
    "rayjoin__segment_pairs",
    "rtbh__force",
    "rtdbscan__components",
    "rtnn__ranked_window",
    "triangle__rt_1a2",
    "triangle__rt_2a1",
    "xhd__global_witness",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: object) -> str:
    return sha256_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def recount(root: Path) -> dict[str, Any]:
    result_path = root / "RESULT.json"
    require(result_path.is_file(), "RESULT.json missing")
    submitted = json.loads(result_path.read_text(encoding="utf-8"))
    files = sorted((root / "functional_raw").glob("*.json"))
    expected_names = {
        f"{lane}__{method}.json" for lane in EXPECTED_LANES for method in METHODS
    }
    require({path.name for path in files} == expected_names,
            "functional raw membership differs from the frozen 39-lane matrix")

    records: list[dict[str, Any]] = []
    file_rows: list[dict[str, Any]] = []
    pids: set[int] = set()
    natives: set[str] = set()
    receipt_count = 0
    launch_count = 0
    raygen_count = 0
    lane_rows: list[dict[str, Any]] = []
    for path in files:
        record = json.loads(path.read_text(encoding="utf-8"))
        records.append(record)
        file_rows.append({
            "path": f"functional_raw/{path.name}",
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
        lane = record.get("lane_id")
        method = record.get("method")
        require(lane in EXPECTED_LANES and method in METHODS,
                f"unexpected lane or method: {path.name}")
        require(path.name == f"{lane}__{method}.json",
                f"filename/content mismatch: {path.name}")
        require(record.get("schema") ==
                "rtdl.goal5768.three_way_functional_smoke.v1",
                f"unexpected worker schema: {path.name}")
        require(record.get("formal_worker") is False and
                record.get("registered_performance_observation") is False and
                record.get("performance_interpretation_allowed") is False,
                f"functional worker crossed performance boundary: {path.name}")
        pid = record.get("parent_pid")
        require(type(pid) is int and pid > 0 and pid not in pids,
                f"nonfresh/duplicate PID: {path.name}")
        pids.add(pid)

        endpoint = record.get("endpoint")
        require(isinstance(endpoint, dict), f"endpoint missing: {path.name}")
        require(endpoint.get("lane_id") == lane and
                endpoint.get("method") == method,
                f"endpoint identity mismatch: {path.name}")
        require(endpoint.get("matched") is True and
                endpoint.get("output") == endpoint.get("expected"),
                f"exact output mismatch: {path.name}")
        require(endpoint.get("output_sha256") == endpoint.get("expected_sha256") ==
                canonical_digest(endpoint.get("output")),
                f"output digest mismatch: {path.name}")
        require(endpoint.get("performance_claimed") is False and
                endpoint.get("comparator_inside_registered_timer") is False,
                f"endpoint claim/timer boundary mismatch: {path.name}")
        native = endpoint.get("native_library_sha256")
        require(isinstance(native, str) and len(native) == 64,
                f"native identity missing: {path.name}")
        natives.add(native)

        receipt = endpoint.get("traversal_receipt")
        require(isinstance(receipt, dict) and
                receipt.get("physical_executor_classification") ==
                "optix_traversal_observed" and
                receipt.get("provider_library_sha256") == native,
                f"behavioral traversal receipt invalid: {path.name}")
        receipt_body = dict(receipt)
        receipt_claimed = receipt_body.pop("receipt_sha256", None)
        require(receipt_claimed == canonical_digest(receipt_body),
                f"traversal receipt digest mismatch: {path.name}")
        require(isinstance(receipt.get("output_digest"), str) and
                len(receipt["output_digest"]) == 64,
                f"receipt edge output digest missing: {path.name}")
        expected_bundles = receipt.get("expected_program_bundles")
        require(isinstance(expected_bundles, list) and
                (not expected_bundles or
                 receipt.get("expected_program_observed_at_receipt_edge") is True),
                f"expected program bundle not observed: {path.name}")
        snapshot = receipt.get("native_snapshot")
        require(isinstance(snapshot, dict), f"native snapshot missing: {path.name}")
        attempted = snapshot.get("attempted_launch_count")
        successful = snapshot.get("successful_launch_count")
        complete = snapshot.get("complete_context_launch_count")
        require(type(attempted) is int and attempted > 0 and
                attempted == successful == complete ==
                snapshot.get("context_bind_count"),
                f"incomplete launch binding: {path.name}")
        require(snapshot.get("failed_launch_count") == 0 and
                snapshot.get("incomplete_context_launch_count") == 0 and
                snapshot.get("incomplete_callsite_record_count") == 0 and
                snapshot.get("pending_context_at_finish") == 0 and
                snapshot.get("session_error") == 0 and
                snapshot.get("first_traversable", 0) != 0 and
                snapshot.get("last_traversable", 0) != 0 and
                snapshot.get("raygen_invocation_count", 0) > 0,
                f"failed/unbound traversal state: {path.name}")
        receipt_count += 1
        launch_count += attempted
        raygen_count += snapshot["raygen_invocation_count"]

    require(len(records) == len(pids) == 39, "cohort is not 39 fresh workers")
    require(len(natives) == 1, "cohort does not bind one exact native")
    native = next(iter(natives))
    for lane in EXPECTED_LANES:
        cohort = [row for row in records if row["lane_id"] == lane]
        require(len(cohort) == 3 and {row["method"] for row in cohort} == set(METHODS),
                f"three-way lane incomplete: {lane}")
        endpoints = [row["endpoint"] for row in cohort]
        require(len({row["input_sha256"] for row in endpoints}) == 1 and
                len({row["output_sha256"] for row in endpoints}) == 1 and
                all(row["native_library_sha256"] == native for row in endpoints),
                f"three-way identity mismatch: {lane}")
        lane_rows.append({
            "lane_id": lane,
            "input_sha256": endpoints[0]["input_sha256"],
            "output_sha256": endpoints[0]["output_sha256"],
            "methods": sorted(row["method"] for row in endpoints),
            "exact_three_way_match": True,
            "behaviorally_true_optix_three_way": True,
        })

    require(submitted.get("bundle_sha256") == sha256_file(root / "BUNDLE.tar.gz")
            if (root / "BUNDLE.tar.gz").is_file() else True,
            "optional copied bundle differs from submitted identity")
    require(submitted.get("native_sha256") == native and
            submitted.get("functional_count") == 39 and
            submitted.get("functional_correct_count") == 39 and
            submitted.get("functional_behavioral_true_optix_count") == 39 and
            submitted.get("formal_worker_count") == 0 and
            submitted.get("registered_performance_timing_count") == 0 and
            submitted.get("performance_claimed") is False,
            "submitted summary differs from raw recount")

    return {
        "schema": "rtdl.goal5769.home_functional_independent_recount.v1",
        "goal": 5769,
        "result_sha256": sha256_file(result_path),
        "bundle_sha256": submitted["bundle_sha256"],
        "portable_source_archive_sha256":
            submitted["portable_source_archive_sha256"],
        "execution_source_archive_sha256": submitted["source_archive_sha256"],
        "source_tree_sha256": submitted["source_tree_sha256"],
        "native_sha256": native,
        "worker_count": len(records),
        "unique_parent_pid_count": len(pids),
        "lane_count": len(EXPECTED_LANES),
        "method_count": len(METHODS),
        "exact_output_count": len(records),
        "behaviorally_true_optix_count": receipt_count,
        "successful_complete_bound_launch_count": launch_count,
        "raygen_invocation_count": raygen_count,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_interpretation_allowed": False,
        "lane_rows": lane_rows,
        "raw_files": file_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = recount(args.result_root.resolve())
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
