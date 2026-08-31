#!/usr/bin/env python3
"""Read-only cold-lifecycle reconstruction for Goal5781.

The program reads the immutable Goal5776 evidence archive directly.  It does
not import the submitted evaluator/recount and does not execute an app route.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import tarfile


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
COLD = "installed_cold_compile_prepare_execute"
PHASES = ("loading", "preparation", "execute", "close")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _worker_phase(worker: dict[str, object], name: str) -> float:
    phase = dict(worker["phase_accounting"])
    if name == "execute":
        values = list(dict(phase["row_execute_seconds"]).values())
        if len(values) != 1:
            raise RuntimeError("cold worker must contain exactly one execute row")
        return float(values[0])
    return float(phase[f"{name}_seconds"])


def _endpoint(worker: dict[str, object]) -> float:
    rows = list(worker["rows"])
    if len(rows) != 1:
        raise RuntimeError("cold worker must contain exactly one registered row")
    return float(rows[0]["registered_complete_endpoint_seconds"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    workers: list[dict[str, object]] = []
    with tarfile.open(args.archive, "r:gz") as archive:
        for member in archive.getmembers():
            if member.name.startswith("RAW/workers/") and member.name.endswith(".json"):
                stream = archive.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"cannot read {member.name}")
                workers.append(json.load(stream))
    if len(workers) != 464:
        raise RuntimeError("Goal5776 archive must contain 464 workers")
    cold = [worker for worker in workers if worker["lifecycle"] == COLD]
    if len(cold) != 240:
        raise RuntimeError("Goal5776 must contain 240 cold workers")
    if len({int(worker["parent_pid"]) for worker in workers}) != 464:
        raise RuntimeError("Goal5776 parent processes are not fresh")
    units = sorted({str(worker["unit_id"]) for worker in cold})
    if len(units) != 15:
        raise RuntimeError("Goal5781 requires exactly 15 cold rows")

    rows: list[dict[str, object]] = []
    for unit in units:
        pairs: list[dict[str, object]] = []
        for pair_index in range(8):
            selected = [worker for worker in cold
                        if worker["unit_id"] == unit
                        and int(worker["pair_index"]) == pair_index]
            by_method = {str(worker["method"]): worker for worker in selected}
            if set(by_method) != {V2, V4}:
                raise RuntimeError(f"unbalanced cold pair: {unit}/{pair_index}")
            v2, v4 = by_method[V2], by_method[V4]
            for worker in (v2, v4):
                phase_sum = sum(_worker_phase(worker, name) for name in PHASES)
                endpoint = _endpoint(worker)
                if abs(phase_sum - endpoint) > max(1.0e-8, endpoint * 1.0e-8):
                    raise RuntimeError("cold phase accounting does not conserve time")
                if worker["phase_accounting"]["same_worker_mutually_exclusive_phases"] is not True:
                    raise RuntimeError("non-exclusive phase accounting")
            deltas = {
                name: _worker_phase(v4, name) - _worker_phase(v2, name)
                for name in PHASES
            }
            endpoint_delta = _endpoint(v4) - _endpoint(v2)
            if abs(sum(deltas.values()) - endpoint_delta) \
                    > max(1.0e-8, abs(endpoint_delta) * 1.0e-8):
                raise RuntimeError("paired phase deltas do not conserve endpoint delta")
            positive = {name: value for name, value in deltas.items() if value > 0.0}
            dominant = max(positive, key=positive.get) if positive else "none"
            pairs.append({
                "pair_index": pair_index,
                "v2_endpoint_seconds": _endpoint(v2),
                "v4_endpoint_seconds": _endpoint(v4),
                "v2_over_v4": _endpoint(v2) / _endpoint(v4),
                "v4_minus_v2_endpoint_seconds": endpoint_delta,
                "v4_minus_v2_phase_seconds": deltas,
                "largest_positive_phase": dominant,
            })
        phase_dominance = {
            name: sum(pair["largest_positive_phase"] == name for pair in pairs)
            for name in (*PHASES, "none")
        }
        v4_workers = [worker for worker in cold
                      if worker["unit_id"] == unit and worker["method"] == V4]
        leaf_modes = sorted({str(worker["leaf_cache"]["mode"])
                             for worker in v4_workers})
        rows.append({
            "unit_id": unit,
            "row_id": str(v4_workers[0]["rows"][0]["row_id"]),
            "pair_count": len(pairs),
            "paired_ratio_median_v2_over_v4": statistics.median(
                float(pair["v2_over_v4"]) for pair in pairs),
            "median_v2_endpoint_seconds": statistics.median(
                float(pair["v2_endpoint_seconds"]) for pair in pairs),
            "median_v4_endpoint_seconds": statistics.median(
                float(pair["v4_endpoint_seconds"]) for pair in pairs),
            "median_v4_minus_v2_endpoint_seconds": statistics.median(
                float(pair["v4_minus_v2_endpoint_seconds"]) for pair in pairs),
            "median_v4_minus_v2_phase_seconds": {
                name: statistics.median(float(
                    pair["v4_minus_v2_phase_seconds"][name]) for pair in pairs)
                for name in PHASES
            },
            "largest_positive_phase_counts": phase_dominance,
            "preparation_dominant_at_least_six_of_eight_pairs": (
                phase_dominance["preparation"] >= 6),
            "execute_dominant_at_least_six_of_eight_pairs": (
                phase_dominance["execute"] >= 6),
            "leaf_cache_modes": leaf_modes,
            "v4_leaf_cache_hit_count": sum(
                int(worker["leaf_cache"].get("hit_count", 0))
                for worker in v4_workers),
            "v4_leaf_cache_miss_count": sum(
                int(worker["leaf_cache"].get("miss_count", 0))
                for worker in v4_workers),
            "v4_leaf_cache_disabled_count": sum(
                int(worker["leaf_cache"].get("disabled_count", 0))
                for worker in v4_workers),
            "pairs": pairs,
        })

    v4_cold = [worker for worker in cold if worker["method"] == V4]
    leaf_summary = {
        "v4_cold_worker_count": len(v4_cold),
        "sealed_read_only_manifest_worker_count": sum(
            worker["leaf_cache"]["mode"] == "sealed_read_only_manifest"
            for worker in v4_cold),
        "not_applicable_no_numba_leaf_worker_count": sum(
            worker["leaf_cache"]["mode"] == "not_applicable_no_numba_leaf"
            for worker in v4_cold),
        "hit_count": sum(int(worker["leaf_cache"].get("hit_count", 0))
                         for worker in v4_cold),
        "miss_count": sum(int(worker["leaf_cache"].get("miss_count", 0))
                          for worker in v4_cold),
        "disabled_count": sum(int(worker["leaf_cache"].get("disabled_count", 0))
                              for worker in v4_cold),
    }
    if leaf_summary != {
        "v4_cold_worker_count": 120,
        "sealed_read_only_manifest_worker_count": 96,
        "not_applicable_no_numba_leaf_worker_count": 24,
        "hit_count": 480,
        "miss_count": 0,
        "disabled_count": 0,
    }:
        raise RuntimeError("unexpected Goal5776 V4 leaf-cache census")

    source_root = args.source_root.resolve()
    source_paths = {
        "formal_frontdoors": source_root / "scripts/goal5776_real_scale_frontdoors.py",
        "formal_evaluator": source_root / "scripts/goal5776_evaluate_real_scale_v2_v4.py",
        "numba_codegen": source_root / "src/rtdsl/v4_callback_numba_codegen.py",
        "prepared_provider": source_root / "src/rtdsl/v4_prepared_provider.py",
        "hierarchy_frontier": source_root / "src/rtdsl/v4_hierarchy_frontier.py",
    }
    source_hashes = {name: _sha(path) for name, path in source_paths.items()}
    frontdoor_text = source_paths["formal_evaluator"].read_text(encoding="utf-8")
    if "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1" \
            not in frontdoor_text:
        raise RuntimeError("cold timer boundary marker is missing")
    result = {
        "schema": "rtdl.goal5781.cold_compiler_preparation_architecture_audit.v1",
        "status": "COMPLETE__READ_ONLY_ARCHITECTURE__NO_CACHE_OR_TIMER_CHANGE",
        "goal5776_evidence_archive_sha256": _sha(args.archive),
        "worker_reconstruction": {
            "total_workers": len(workers),
            "cold_workers": len(cold),
            "cold_rows": len(rows),
            "pairs_per_row": 8,
            "all_worker_pids_unique": True,
            "all_phase_rows_mutually_exclusive_and_conservative": True,
            "cold_pass_count_by_median": sum(
                float(row["paired_ratio_median_v2_over_v4"]) >= 1.0
                for row in rows),
            "cold_fail_count_by_median": sum(
                float(row["paired_ratio_median_v2_over_v4"]) < 1.0
                for row in rows),
            "preparation_dominant_failure_rows": sum(
                row["preparation_dominant_at_least_six_of_eight_pairs"]
                and float(row["paired_ratio_median_v2_over_v4"]) < 1.0
                for row in rows),
            "execute_dominant_failure_rows": sum(
                row["execute_dominant_at_least_six_of_eight_pairs"]
                and float(row["paired_ratio_median_v2_over_v4"]) < 1.0
                for row in rows),
        },
        "leaf_cache_census": leaf_summary,
        "source_hashes": source_hashes,
        "cold_rows": rows,
        "architecture_findings": {
            "numba_leaf_codegen_is_current_cold_systemic_cause": False,
            "basis": "all applicable V4 cold workers used the sealed read-only cache with 480 hits and zero misses or disabled lookups",
            "one_uniform_cold_cause_explains_all_failures": False,
            "preparation_dominant_failure_row_count": sum(
                row["preparation_dominant_at_least_six_of_eight_pairs"]
                and float(row["paired_ratio_median_v2_over_v4"]) < 1.0
                for row in rows),
            "execute_dominant_failure_row_count": sum(
                row["execute_dominant_at_least_six_of_eight_pairs"]
                and float(row["paired_ratio_median_v2_over_v4"]) < 1.0
                for row in rows),
            "installed_cold_contract": "loading_plus_required_compile_or_plan_validation_plus_native_preparation_plus_execute_plus_close",
            "prepared_contract": "preparation_reported_separately_and_never_called_free; execute-only rows cannot replace cold",
            "benchmark_repetition_is_authentic_reuse": False,
            "generic_cache_or_session_repair_proven_eliminable": False,
        },
        "required_future_cache_contract_if_ever_implemented": {
            "content_bound": True,
            "target_bound": True,
            "backend_version_bound": True,
            "native_binary_bound": True,
            "callback_ir_and_generated_leaf_bound": True,
            "schema_resource_and_role_set_bound": True,
            "dynamic_input_or_legality_reused_without_revalidation": False,
            "mismatch_fails_closed": True,
            "cold_timer_work_moved_outside_timer": False,
        },
        "decision": {
            "implement_new_cold_cache_or_session_now": False,
            "reason": "sealed leaf caching is already perfect in this cohort and the remaining preparation deficits split across application families; no single generic eliminable duplicate has been measured",
            "preserve_cold_and_prepared_as_separate_results": True,
            "proceed_to_mandatory_post_5779_5781_decision_register": True,
            "fourth_audit_goal_allowed": False
        },
        "claim_boundary": {
            "product_or_native_changed": False,
            "worker_or_gpu_used": False,
            "performance_or_no_slower_claimed": False,
            "predicted_saving_claimed": False,
            "cache_or_session_implemented": False,
            "goal5776_changed_or_relabelled": False
        }
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": result["status"], "sha256": _sha(args.output),
        "summary": result["worker_reconstruction"],
        "leaf_cache": leaf_summary,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
