#!/usr/bin/env python3
"""Populate, seal and functionally validate every Goal5776 target path."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from goal5776_real_scale_formal_contract import UNITS, V2, V4
from goal5776_real_scale_frontdoors import run_real_scale_endpoint
from goal5776_real_scale_formal_worker import _validate_receipt_row_binding
from goal5776_real_scale_runtime_inputs import build_real_scale_inputs
from rtdsl.v4_callback_numba_codegen import (
    formal_numba_leaf_cache_lifecycle_metadata,
    materialize_formal_numba_leaf_cache_manifest,
)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _records_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha(path)))
    return digest.hexdigest()


def _delta(before: dict[str, object], after: dict[str, object]) -> dict[str, int]:
    return {
        key: int(after[key]) - int(before[key])
        for key in ("hit_count", "miss_count", "disabled_count")
    }


def _seal_read_only(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        path.chmod(path.stat().st_mode & ~0o222)
    root.chmod(root.stat().st_mode & ~0o222)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61", "89"), required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--rtdbscan-evidence", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--cache-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve()
    native = args.native.resolve()
    cache = args.cache_root.resolve()
    manifest = args.cache_manifest.resolve()
    output = args.output_root.resolve()
    for path in (cache, manifest, output):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    if not native.is_file():
        raise FileNotFoundError(native)
    cache.mkdir(parents=True)
    output.mkdir(parents=True)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(cache)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST", None)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256", None)
    runtime = {
        "source_root": str(source),
        "native_library_path": str(native),
        "compute_capability": [int(args.compute_capability[0]),
                               int(args.compute_capability[1])],
        "optix_sdk_version": "9.0.0",
        "optix_include": str(args.optix_include.resolve()),
        "cuda_include": str(args.cuda_include.resolve()),
        "inputs": build_real_scale_inputs(
            args.data_root.resolve(),
            refinement_evidence_path=args.rtdbscan_evidence.resolve(),
        ),
    }
    expected = sum(len(unit.supported_lifecycles) * 2 for unit in UNITS)
    records = []
    cache_population_observations = []
    total_v4_cache = {key: 0 for key in (
        "hit_count", "miss_count", "disabled_count")}
    for unit in UNITS:
        for lifecycle in unit.supported_lifecycles:
            for method in (V2, V4):
                before = formal_numba_leaf_cache_lifecycle_metadata()
                endpoint = run_real_scale_endpoint(
                    unit_id=unit.unit_id, method=method,
                    lifecycle=lifecycle, runtime=runtime,
                )
                after = formal_numba_leaf_cache_lifecycle_metadata()
                delta = _delta(before, after)
                if method == V4:
                    for key, value in delta.items():
                        total_v4_cache[key] += value
                    if delta["disabled_count"] != 0:
                        raise RuntimeError("V4 target prepare disabled the formal leaf cache")
                    if not unit.v4_numba_leaf_cache_required and any(
                        delta[key] != 0 for key in delta
                    ):
                        raise RuntimeError("non-leaf V4 route touched formal leaf cache")
                    if delta["miss_count"] > 0:
                        cache_population_observations.append({
                            "unit_id": unit.unit_id,
                            "lifecycle": lifecycle,
                            "cache_miss_count": delta["miss_count"],
                            "observed_v4_preparation_seconds_not_pure_compile_cost":
                                float(endpoint["phase_accounting"]["preparation_seconds"]),
                        })
                receipt = dict(endpoint["traversal_receipt"])
                _validate_receipt_row_binding(receipt, endpoint["rows"])
                snapshot = dict(receipt["native_snapshot"])
                if (
                    endpoint["matched"] is not True
                    or receipt.get("physical_executor_classification")
                        != "optix_traversal_observed"
                    or int(snapshot.get("successful_launch_count", 0)) <= 0
                    or int(snapshot.get("successful_launch_count", 0))
                        != int(snapshot.get("complete_context_launch_count", -1))
                    or any(int(snapshot.get(key, 0)) != 0 for key in (
                        "failed_launch_count", "incomplete_context_launch_count",
                        "unbound_launch_count", "pending_context_at_finish",
                        "session_error"))
                ):
                    raise RuntimeError(
                        f"target functional path failed: {unit.unit_id}/{lifecycle}/{method}")
                record = {
                    "unit_id": unit.unit_id, "app": unit.app,
                    "lifecycle": lifecycle, "method": method,
                    "matched": True, "row_count": len(endpoint["rows"]),
                    "rows": endpoint["rows"],
                    "phase_accounting": endpoint["phase_accounting"],
                    "traversal_receipt": receipt,
                    "formal_leaf_cache_delta": (
                        {**delta, "mode": (
                            "population_or_hit"
                            if unit.v4_numba_leaf_cache_required
                            else "not_applicable_no_numba_leaf")}
                        if method == V4
                        else {"mode": "not_applicable_to_v2_direct"}
                    ),
                    "formal_performance_result_created": False,
                }
                path = output / f"{len(records):03d}.json"
                path.write_text(
                    json.dumps(record, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")
                records.append(record)
                print(json.dumps({
                    "completed": len(records), "expected": expected,
                    "unit_id": unit.unit_id, "lifecycle": lifecycle,
                    "method": method,
                }, sort_keys=True), flush=True)
    if len(records) != expected or total_v4_cache["miss_count"] <= 0:
        raise RuntimeError("target functional/cache population cardinality failed")
    materialize_formal_numba_leaf_cache_manifest(cache, manifest)
    _seal_read_only(cache)
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    summary = {
        "schema": "rtdl.goal5776.target_real_scale_functional_prepare.v1",
        "paper_app_count": 9,
        "execution_unit_count": len(UNITS),
        "functional_trial_count": len(records),
        "functional_records_sha256": _records_digest(
            sorted(output.glob("[0-9][0-9][0-9].json"))),
        "all_correct_and_behaviorally_true_optix": True,
        "leaf_cache_population": total_v4_cache,
        "leaf_cache_entry_count": manifest_payload["entry_count"],
        "leaf_cache_entries_sha256": manifest_payload["entries_sha256"],
        "leaf_cache_manifest_sha256": _sha(manifest),
        "cache_population_observation_count": len(cache_population_observations),
        "cache_population_observations": cache_population_observations,
        "cache_population_cost_is_free": False,
        "cache_population_observation_is_not_formal_performance": True,
        "formal_worker_count": 0,
        "registered_formal_timing_count": 0,
        "formal_performance_result_created": False,
    }
    (output / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
