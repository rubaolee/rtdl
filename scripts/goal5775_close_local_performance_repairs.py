from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVIDER_DIR = ROOT / "history/internal_docs/goal5775_home_provider_identity_diagnostic_20260813"
CACHE_DIR = ROOT / "history/internal_docs/goal5775_home_performance_repair_diagnostic_20260813"
OUTPUT = ROOT / "history/internal_docs/goal5775_v4_local_performance_repair_result_20260813.json"


def _read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _by_lane(document: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(row["lane_id"]): row for row in document["rows"]}


def _median(values) -> float:
    return float(statistics.median(float(value) for value in values))


def main() -> None:
    provider_files = {
        name: PROVIDER_DIR / f"{name}.json"
        for name in ("baseline", "candidate", "hierarchy_candidate", "v2_control")
    }
    cache_files = {
        name: CACHE_DIR / f"leaf_cache_{name}.json"
        for name in ("cold", "warm")
    }
    documents = {name: _read(path) for name, path in provider_files.items()}
    cache = {name: _read(path) for name, path in cache_files.items()}

    lane_sets = [set(_by_lane(document)) for document in documents.values()]
    lane_sets.extend(set(_by_lane(document)) for document in cache.values())
    if not lane_sets or any(lanes != lane_sets[0] for lanes in lane_sets[1:]):
        raise RuntimeError("Goal5775 diagnostic lane identities differ")
    lanes = sorted(lane_sets[0])
    if len(lanes) != 13:
        raise RuntimeError("Goal5775 diagnostic must contain exactly thirteen lanes")

    baseline = _by_lane(documents["baseline"])
    candidate = _by_lane(documents["candidate"])
    hierarchy = _by_lane(documents["hierarchy_candidate"])
    v2 = _by_lane(documents["v2_control"])
    warm = _by_lane(cache["warm"])

    provider_speedups = {
        lane: float(baseline[lane]["registered_seconds_median"])
        / float(candidate[lane]["registered_seconds_median"])
        for lane in lanes
    }
    current_v2_over_v4 = {
        lane: float(v2[lane]["registered_seconds_median"])
        / float(warm[lane]["registered_seconds_median"])
        for lane in lanes
    }
    slow_lanes = [lane for lane in lanes if current_v2_over_v4[lane] < 1.0]
    fast_lanes = [lane for lane in lanes if current_v2_over_v4[lane] >= 1.0]

    for document in (*documents.values(), *cache.values()):
        if document.get("formal_performance_row_created") is not False:
            raise RuntimeError("Goal5775 diagnostics must not create formal rows")
        if document.get("observation_only") is not True:
            raise RuntimeError("Goal5775 diagnostics must remain observation-only")
        if document.get("predicted_saving_claimed") is not False:
            raise RuntimeError("Goal5775 diagnostics must not claim predicted savings")
    for document in (
        documents["candidate"], documents["hierarchy_candidate"],
        documents["v2_control"], cache["cold"], cache["warm"],
    ):
        if any(int(row["native_provider_read_bytes_calls"]) != 0 for row in document["rows"]):
            raise RuntimeError("final Goal5775 diagnostic reread the provider during execute")

    manifest = _read(CACHE_DIR / "leaf_cache_manifest.json")
    if int(manifest["entry_count"]) != 7:
        raise RuntimeError("sealed formal leaf cache must contain exactly seven roles")
    if cache["warm"]["formal_leaf_cache_after"] != {
        "schema": "rtdl.v4.formal_numba_leaf_cache.v1",
        "environment_variable": "RTDL_V4_FORMAL_LEAF_CACHE",
        "hit_count": 72,
        "miss_count": 0,
        "disabled_count": 0,
    }:
        raise RuntimeError("warm process did not exclusively consume exact cache hits")

    source_paths = (
        "src/rtdsl/physical_execution_provenance.py",
        "src/rtdsl/optix_runtime.py",
        "src/rtdsl/v4_multiround_spatial_optix_runtime.py",
        "src/rtdsl/v4_hierarchy_frontier.py",
        "src/rtdsl/action_numba_continuation.py",
        "src/rtdsl/v4_grouped_event_reduction.py",
        "src/rtdsl/v4_callback_numba_codegen.py",
        "src/rtdsl/canonical_physical_resolution.py",
        "src/rtdsl/default_physical_selection.py",
    )

    result: dict[str, object] = {
        "schema": "rtdl.goal5775.v4_local_performance_repair_result.v1",
        "status": "local_generic_performance_repairs_complete__real_scale_measurement_not_started",
        "scope": {
            "home_gpu_observation_only": True,
            "formal_performance_result_created": False,
            "real_scale_claimed": False,
            "modern_rtx_claimed": False,
            "no_slower_claimed": False,
        },
        "lane_count": len(lanes),
        "loaded_provider_identity": {
            "median_baseline_over_candidate": _median(provider_speedups.values()),
            "minimum_baseline_over_candidate": min(provider_speedups.values()),
            "maximum_baseline_over_candidate": max(provider_speedups.values()),
            "all_final_execute_provider_file_reads": 0,
            "fresh_receipt_per_call_preserved": True,
        },
        "formal_leaf_cache": {
            "sealed_manifest_sha256": _sha(CACHE_DIR / "leaf_cache_manifest.json"),
            "entry_count": int(manifest["entry_count"]),
            "cold_miss_count": int(cache["cold"]["formal_leaf_cache_after"]["miss_count"]),
            "cold_hit_count": int(cache["cold"]["formal_leaf_cache_after"]["hit_count"]),
            "warm_miss_count": int(cache["warm"]["formal_leaf_cache_after"]["miss_count"]),
            "warm_hit_count": int(cache["warm"]["formal_leaf_cache_after"]["hit_count"]),
            "cold_prepare_median_seconds": _median(row["prepare_seconds"] for row in cache["cold"]["rows"]),
            "warm_prepare_median_seconds": _median(row["prepare_seconds"] for row in cache["warm"]["rows"]),
            "cold_prepare_sum_seconds": sum(float(row["prepare_seconds"]) for row in cache["cold"]["rows"]),
            "warm_prepare_sum_seconds": sum(float(row["prepare_seconds"]) for row in cache["warm"]["rows"]),
            "cold_over_warm_prepare_median": (
                _median(row["prepare_seconds"] for row in cache["cold"]["rows"])
                / _median(row["prepare_seconds"] for row in cache["warm"]["rows"])
            ),
            "missing_or_mutated_entry_fails_closed": True,
            "cache_disabled_by_default": True,
        },
        "current_micro_fixture_observation": {
            "v2_over_v4_median": _median(current_v2_over_v4.values()),
            "v4_not_slower_lane_count": len(fast_lanes),
            "v4_slower_lane_count": len(slow_lanes),
            "v4_not_slower_lanes": fast_lanes,
            "v4_slower_lanes": slow_lanes,
            "formal_claim_allowed": False,
            "reason": "unpaired Home observation on sub-15ms micro fixtures",
        },
        "generic_repairs": {
            "loaded_provider_identity_once_per_handle": True,
            "prepared_hierarchy_static_authority": True,
            "prepared_grouped_i64x2_device_workspace": True,
            "sealed_formal_numba_leaf_cache": True,
            "new_native_symbol_added": False,
            "application_named_dispatch_added": False,
            "paper_algorithm_or_output_changed": False,
            "registered_timer_boundary_changed": False,
        },
        "source_sha256": {path: _sha(ROOT / path) for path in source_paths},
        "input_artifacts": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha(path)
            for path in (*provider_files.values(), *cache_files.values(),
                         CACHE_DIR / "leaf_cache_manifest.json",
                         CACHE_DIR / "leaf_cache_install.json",
                         CACHE_DIR / "leaf_cache_sealed.json")
        },
        "claim_boundary": {
            "goal5774_replaced": False,
            "real_scale_nine_app_status_known": False,
            "performance_objective_closed": False,
            "pod_used_or_authorized": False,
            "next_required_work": "freeze_and_validate_real_scale_nine_app_input_matrix",
        },
    }
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["result_sha256"] = hashlib.sha256(encoded).hexdigest()
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "result_sha256": result["result_sha256"],
        "provider_median_speedup": result["loaded_provider_identity"]["median_baseline_over_candidate"],
        "warm_prepare_median_seconds": result["formal_leaf_cache"]["warm_prepare_median_seconds"],
        "micro_fixture_split": [len(fast_lanes), len(slow_lanes)],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
