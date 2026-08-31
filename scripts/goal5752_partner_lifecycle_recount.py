#!/usr/bin/env python3
"""Independent raw-evidence recount for Goal5752.

This verifier imports no V4 compiler, native runtime, partner adapter, primary
validation script, or application code.  It rehashes the evidence directory
and reconstructs the four functional rows from the raw JSON receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


UINT32_MAX = (1 << 32) - 1


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected(batch: int):
    if batch == 0:
        return ((3, 4.0), (UINT32_MAX, 100.0))
    if batch == 1:
        return ((UINT32_MAX, 3.0), (UINT32_MAX, 100.0), (3, 0.0))
    raise AssertionError(batch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    manifest = json.loads((root / "MANIFEST.json").read_text())
    rows = manifest["payloads"]
    mismatches = []
    for item in rows:
        path = root / item["path"]
        if (not path.is_file() or path.is_symlink()
                or path.stat().st_size != item["size_bytes"]
                or _sha256(path) != item["sha256"]):
            mismatches.append(item["path"])
    if mismatches:
        raise RuntimeError(f"evidence manifest mismatch: {mismatches!r}")
    if manifest["payload_count"] != len(rows):
        raise RuntimeError("payload count mismatch")
    if manifest["payload_bytes"] != sum(item["size_bytes"] for item in rows):
        raise RuntimeError("payload-byte sum mismatch")

    raw_paths = sorted((root / "RAW").glob("*.json"))
    if len(raw_paths) != 4:
        raise RuntimeError("Goal5752 requires exactly four raw partner executions")
    raw_rows = [json.loads(path.read_text()) for path in raw_paths]
    observed_keys = {(row["partner"], int(row["query_batch_index"])) for row in raw_rows}
    expected_keys = {(partner, batch) for partner in ("cupy", "numba") for batch in (0, 1)}
    if observed_keys != expected_keys:
        raise RuntimeError("partner/batch matrix is incomplete")
    session_identities = {row["prepared_session_identity"] for row in raw_rows}
    if len(session_identities) != 1:
        raise RuntimeError("raw executions do not share one prepared owner")

    reconstructed = []
    for row in raw_rows:
        batch = int(row["query_batch_index"])
        expected = _expected(batch)
        observed = tuple(zip(
            (int(item) for item in row["output_ids"]),
            (float(item) for item in row["output_distance"]),
        ))
        if observed != expected:
            raise RuntimeError(f"output mismatch for {row['partner']} batch {batch}")
        valid = tuple(bool(item) for item in row["valid_hit_mask"])
        if valid != tuple(item_id != UINT32_MAX for item_id, _ in expected):
            raise RuntimeError("valid-hit continuation mismatch")
        masked = tuple(float(item) for item in row["masked_distance"])
        if masked != tuple(distance if item_id != UINT32_MAX else 0.0
                           for item_id, distance in expected):
            raise RuntimeError("masked-distance continuation mismatch")
        if len(row["role_counters"]) != 7 or any(int(item) <= 0 for item in row["role_counters"]):
            raise RuntimeError("not all seven roles executed")
        if any(int(item["first_error_claimed"]) or int(item["error_code"])
               for item in row["launch_status"]):
            raise RuntimeError("device status is not clean")
        receipt = row["traversal_receipt"]
        snapshot = receipt["native_snapshot"]
        if (receipt["physical_executor_classification"] != "optix_traversal_observed"
                or int(snapshot["successful_launch_count"]) != 1
                or int(snapshot["complete_context_launch_count"]) != 1
                or any(int(snapshot[name]) != 0 for name in (
                    "failed_launch_count", "incomplete_context_launch_count",
                    "pending_context_at_finish", "session_error"))):
            raise RuntimeError("behavioral OptiX receipt is invalid")
        buffer = row["buffer_receipt"]
        if (buffer["native_boundary_host_staging"]
                or not buffer["single_explicit_nondefault_stream"]
                or not buffer["same_device_pointer_passed_to_native_and_partner"]
                or buffer["native_output_pointer_digest"] != buffer["partner_input_pointer_digest"]
                or int(buffer["host_materialization_count_before_partner_continuation"]) != 0
                or int(buffer["host_materialization_count_after_stream_synchronization"]) != 6):
            raise RuntimeError("device-pointer/stream ordering receipt is invalid")
        lifecycle = row["lifecycle_contract"]
        if (not lifecycle["cold_endpoint_includes_prepare"]
                or lifecycle["prepared_result_may_replace_cold_result"]
                or lifecycle["performance_claimed"]):
            raise RuntimeError("cold/prepared claim boundary is invalid")
        reconstructed.append({
            "partner": row["partner"], "query_batch_index": batch,
            "execution_index": int(row["execution_index"]),
            "output": [list(item) for item in observed],
            "valid_hit_count": sum(valid),
        })
    if sorted(item["execution_index"] for item in reconstructed) != [1, 2, 3, 4]:
        raise RuntimeError("prepared execution indices are not exact")

    primary = json.loads((root / "RESULT.json").read_text())
    if (primary["prepare_count"] != 1 or primary["execute_count"] != 4
            or primary["distinct_query_batch_count"] != 2
            or not primary["use_after_close_failed_closed"]
            or not primary["native_double_destroy_failed_closed"]
            or not primary["native_forged_token_failed_closed"]
            or primary["claims"]["performance_claimed"]
            or primary["claims"]["prepared_may_replace_cold"]):
        raise RuntimeError("primary lifecycle summary is invalid")
    if _sha256(root / "EXECUTION_SOURCE.tar.gz") != primary["execution_source_archive_sha256"]:
        raise RuntimeError("execution source archive identity mismatch")
    if _sha256(root / "librtdl_optix.so") != primary["native_library_sha256"]:
        raise RuntimeError("native library identity mismatch")

    args.output.write_text(json.dumps({
        "schema": "rtdl.goal5752.independent_partner_lifecycle_recount.v1",
        "manifest_payload_count": manifest["payload_count"],
        "manifest_payload_bytes": manifest["payload_bytes"],
        "manifest_mismatch_count": 0,
        "raw_execution_count": 4,
        "partners": ["cupy", "numba"],
        "query_batch_count": 2,
        "one_prepared_session": True,
        "cpu_device_partner_exact_count": 4,
        "behavioral_optix_count": 4,
        "native_boundary_zero_host_stage_count": 4,
        "same_pointer_partner_handoff_count": 4,
        "reconstructed": sorted(reconstructed, key=lambda item: item["execution_index"]),
        "performance_claimed": False,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
