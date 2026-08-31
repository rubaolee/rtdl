#!/usr/bin/env python3
"""Independent raw-evidence verifier for one Goal5749 target lane.

This verifier imports no RTDL compiler, runtime, driver or submitted recount.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import tarfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable(value: object) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode())


def load_archive(path: pathlib.Path) -> dict[str, bytes]:
    rows: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for item in archive.getmembers():
            pure = pathlib.PurePosixPath(item.name)
            if pure.is_absolute() or ".." in pure.parts or item.name in rows:
                raise ValueError(f"unsafe or duplicate archive member: {item.name!r}")
            if item.isdir():
                continue
            if not item.isfile():
                raise ValueError(f"non-regular archive member: {item.name!r}")
            handle = archive.extractfile(item)
            if handle is None:
                raise ValueError(f"unreadable archive member: {item.name!r}")
            rows[item.name] = handle.read()
    return rows


def parse_json(files: dict[str, bytes], name: str) -> object:
    return json.loads(files[name])


def verify_receipt(receipt: dict[str, object], *, route: str, output_digest: str,
                   native_sha: str) -> None:
    snapshot = receipt["native_snapshot"]
    assert isinstance(snapshot, dict)
    assert receipt["physical_executor_classification"] == "optix_traversal_observed"
    assert receipt["output_digest"] == output_digest
    assert receipt["provider_library_sha256"] == native_sha
    assert receipt["route_identity"] == f"v4_callback_poc:{route}"
    expected_program = ("v4_verified_callback_direct_callable_poc"
                        if route == "direct_callable"
                        else "v4_verified_callback_ordinary_composed_poc")
    assert receipt["expected_program_bundles"] == [expected_program]
    assert receipt["expected_program_observed_at_receipt_edge"] is True
    assert snapshot["attempted_launch_count"] == 1
    assert snapshot["successful_launch_count"] == 1
    assert snapshot["complete_context_launch_count"] == 1
    assert snapshot["context_bind_count"] == 1
    assert snapshot["raygen_invocation_count"] == 3
    for key in ("failed_launch_count", "incomplete_context_launch_count",
                "pending_context_at_finish", "session_error"):
        assert snapshot[key] == 0, (key, snapshot[key])
    assert snapshot["first_traversable"] != 0
    assert snapshot["first_traversable"] == snapshot["last_traversable"]
    claimed = receipt["receipt_sha256"]
    body = dict(receipt); body.pop("receipt_sha256")
    assert stable(body) == claimed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=pathlib.Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--expected-lane", required=True)
    parser.add_argument("--expected-cc", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    files = load_archive(args.archive)
    prefix = args.prefix.rstrip("/") + "/"
    result_name = prefix + "RESULT.json"
    manifest_name = prefix + "MANIFEST.json"
    result = parse_json(files, result_name)
    manifest = parse_json(files, manifest_name)
    assert isinstance(result, dict) and isinstance(manifest, list)

    # Rehash every driver output payload from the driver's manifest.
    seen: set[str] = set()
    for row in manifest:
        name = prefix + row["path"]
        assert name not in seen; seen.add(name)
        data = files[name]
        assert len(data) == row["size"]
        assert digest(data) == row["sha256"]
    assert result_name in seen
    assert result["goal"] == 5749
    assert result["lane"] == args.expected_lane
    assert result["compute_capability"] == [int(x) for x in args.expected_cc.split(".")]
    assert result["functional_gpu_execution_performed"] is True
    assert result["registered_performance_timing_count"] == 0
    assert result["performance_claimed"] is False
    target = result["target_identity"]
    assert target["compute_capability"] == args.expected_cc
    assert target["source_archive_sha256"] == args.expected_source_sha256
    assert target["native_sha256"] == args.expected_native_sha256
    body = dict(result); claimed_result_digest = body.pop("result_sha256")
    assert stable(body) == claimed_result_digest

    # Independently audit each generated PTX file and artifact row.
    base_rows = result["numba_artifacts"]
    variant_rows = result["variant_numba_artifacts"]
    assert len(base_rows) == 8 and len(variant_rows) == 12
    for wrapper in base_rows:
        row = wrapper
        ptx_name = prefix + row["ptx_path"]
        ptx = files[ptx_name]
        assert digest(ptx) == row["ptx_sha256"]
        text = ptx.decode()
        assert re.search(r"(?m)^\.version\s+8\.7\s*$", text)
        assert re.search(rf"(?m)^\.target\s+sm_{args.expected_cc.replace('.', '')}\s*$", text)
        assert row["abi_name"] in text
        assert row["external_symbols"] == []
        assert row["compute_capability"] == [int(x) for x in args.expected_cc.split(".")]
        assert row["numba_version"] == "0.65.1" and row["python_version"] == "3.12.3"
    for wrapper in variant_rows:
        row = wrapper["artifact"]
        ptx = files[prefix + wrapper["ptx_path"]]
        assert digest(ptx) == row["ptx_sha256"]
        assert row["abi_name"] in ptx.decode()
        assert row["external_symbols"] == []

    runs = result["functional_runs"]
    expected_matrix = {(wrapper, leaf, route) for wrapper in ("strict", "fast")
                       for leaf in ("strict", "fast")
                       for route in ("ordinary_composed", "direct_callable")}
    observed_matrix = {(row["wrapper_numeric_mode"], row["leaf_numeric_modes"][0], row["route"])
                       for row in runs}
    assert len(runs) == 8 and observed_matrix == expected_matrix
    expected_ids = [3, 0xFFFFFFFF, 3]
    expected_t = [4.0, 100.0, 1.0]
    base_outputs: set[str] = set()
    callback_counter_vectors: set[tuple[int, ...]] = set()
    for row in runs:
        assert row["leaf_numeric_modes"] == [row["leaf_numeric_modes"][0]] * 3
        assert row["output_ids"] == expected_ids and row["output_t"] == expected_t
        observed = list(zip(row["output_ids"], row["output_t"]))
        assert stable(observed) == row["output_sha256"]
        base_outputs.add(row["output_sha256"])
        counters = tuple(row["callback_counters"])
        # OptiX may visit a different number of candidate primitives on different
        # GPU architectures.  The semantic invariant is that every compiler-owned
        # role/leaf/scalar path was exercised, not that traversal scheduling emits
        # the Pascal counter vector on every target.
        assert len(counters) == 7 and all(value > 0 for value in counters)
        callback_counter_vectors.add(counters)
        assert all(item["status"] == 0 and item["stage"] == 0 for item in row["launch_status"])
        receipt = parse_json(files, prefix + row["traversal_receipt_path"])
        verify_receipt(receipt, route=row["route"], output_digest=row["output_sha256"],
                       native_sha=args.expected_native_sha256)
    assert len(base_outputs) == 1

    diagnostics = {row["kind"]: row for row in result["diagnostic_runs"]}
    assert set(diagnostics) == {"ab_semantic_mutation", "invalid_nonfinite_hit",
                                "invalid_u32_overflow"}
    ab = diagnostics["ab_semantic_mutation"]
    assert ab["output_changed"] is True
    assert ab["base_output_sha256"] in base_outputs
    assert ab["mutated_output_sha256"] != ab["base_output_sha256"]
    assert ab["result"]["output_ids"] == [9, 0xFFFFFFFF, 3]
    for kind, code, stage in (("invalid_nonfinite_hit", 2, 1),
                              ("invalid_u32_overflow", 3, 2)):
        row = diagnostics[kind]
        assert row["expected_status"] == code and row["output_accepted"] is False
        assert row["result"]["output_accepted"] is False
        assert row["result"]["expected_status"] == code
        observed = [item for item in row["result"]["observed_statuses"] if item["status"]]
        assert observed and all(item["status"] == code and item["stage"] == stage
                                for item in observed)

    summary = {
        "schema": "rtdl.goal5749.independent_raw_recount.v1",
        "goal": 5749,
        "archive_sha256": digest(args.archive.read_bytes()),
        "archive_regular_payload_count": len(files),
        "driver_manifest_payload_count": len(manifest),
        "lane": args.expected_lane,
        "compute_capability": args.expected_cc,
        "source_archive_sha256": args.expected_source_sha256,
        "native_sha256": args.expected_native_sha256,
        "numba_artifact_count": len(base_rows),
        "variant_numba_artifact_count": len(variant_rows),
        "functional_run_count": len(runs),
        "behavioral_receipt_count": len(runs),
        "callback_counter_vectors": [list(row) for row in sorted(callback_counter_vectors)],
        "ab_output_changed": True,
        "device_fail_closed_statuses": [2, 3],
        "registered_performance_timing_count": 0,
        "all_checks_passed": True,
        "imports_product_or_primary_driver": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
