#!/usr/bin/env python3
"""Independent raw recount for Goal5784; imports no controller/evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

from goal5784_targeted_formal_contract import (
    COLD, LIFECYCLES, METHODS, PAIR_COUNT, UNIT_BY_ID, UNITS, V2, V4,
    contract_document, contract_sha256, schedule, statistical_rows,
)
from goal5776_symmetric_endpoint import validate_behavioral_true_optix


BOUNDARY = "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1"
IDENTITIES = (
    "bundle_sha256", "data_archive_sha256", "execution_source_sha256",
    "source_tree_sha256", "rtdbscan_evidence_sha256",
    "native_library_sha256", "target_identity_sha256",
    "prepared_identity_sha256", "plan_sha256", "formal_identity_sha256",
    "leaf_cache_manifest_sha256", "expected_value_statement_sha256",
    "runtime_budget_sha256", "preregistration_sha256",
    "formal_contract_sha256", "runtime_sha256",
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _bootstrap(values: list[float], seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    draws = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(10_000)
    )
    return float(draws[249]), float(draws[9749])


def _validate_binding(receipt: dict[str, object], rows: list[dict[str, object]]) -> None:
    binding = receipt.get("registered_row_binding")
    canonical = [{
        "row_id": str(row["row_id"]),
        "input_sha256": str(row["input_sha256"]),
        "output_sha256": str(row["output_sha256"]),
    } for row in rows]
    unbound = dict(receipt)
    unbound.pop("registered_row_binding", None)
    if not isinstance(binding, dict) or (
        binding.get("schema") != "rtdl.goal5776.registered_row_binding.v1"
        or binding.get("binding_scope")
        != "post_timer_evidence_binding__not_native_claim"
        or binding.get("row_count") != len(canonical)
        or binding.get("ordered_rows_sha256") != _digest(canonical)
        or binding.get("unbound_traversal_receipt_sha256") != _digest(unbound)
    ):
        raise RuntimeError("Goal5784 receipt-row binding mismatch")


def _validate_worker(worker: dict[str, object]) -> None:
    unit_id = str(worker.get("unit_id"))
    lifecycle = str(worker.get("lifecycle"))
    method = str(worker.get("method"))
    if unit_id not in UNIT_BY_ID or lifecycle not in LIFECYCLES \
            or method not in METHODS:
        raise RuntimeError("Goal5784 unknown unit/lifecycle/method")
    if worker.get("schema") != "rtdl.goal5784.targeted_formal_worker.v1" \
            or worker.get("run_goal_id") != 5784 \
            or worker.get("formal_contract_sha256") != contract_sha256():
        raise RuntimeError("Goal5784 worker identity mismatch")
    if any(worker.get(key) is not expected for key, expected in (
        ("formal_worker", True), ("matched", True),
        ("comparator_inside_registered_timer", False),
        ("default_selected_between_application_algorithms", False),
        ("retry_resume_replacement_row_drop_relabel_used", False),
    )) or worker.get("registered_endpoint_boundary_id") != BOUNDARY:
        raise RuntimeError("Goal5784 worker contract violation")
    if worker.get("close_inside_registered_timer") is not (lifecycle == COLD):
        raise RuntimeError("Goal5784 timer boundary mismatch")
    binding = worker.get("mechanism_binding")
    unit = UNIT_BY_ID[unit_id]
    if method == V2:
        if binding != {"mode": "not_applicable_to_v2_direct"}:
            raise RuntimeError("Goal5784 V2 mechanism binding mismatch")
    elif unit.app == "triangle_counting":
        if not isinstance(binding, dict) or set(binding) != {
            "schema", "mechanism_id", "evidence_level", "segment_count",
            "reduction_receipts_sha256",
            "all_segments_one_device_kernel_one_host_sync",
            "all_segments_bounds_validated_before_sum_trust",
            "observation_outside_registered_endpoint_timer",
        } or (
            binding.get("schema") != "rtdl.goal5784.mechanism_binding.v1"
            or binding.get("mechanism_id")
                != "compiler_fused_checked_u64_device_reduction"
            or binding.get("evidence_level")
                != "actual_per_segment_device_reduction_receipts"
            or not isinstance(binding.get("segment_count"), int)
            or int(binding["segment_count"]) <= 0
            or not isinstance(binding.get("reduction_receipts_sha256"), str)
            or len(str(binding["reduction_receipts_sha256"])) != 64
            or binding.get("all_segments_one_device_kernel_one_host_sync") is not True
            or binding.get("all_segments_bounds_validated_before_sum_trust") is not True
            or binding.get("observation_outside_registered_endpoint_timer") is not True
        ):
            raise RuntimeError("Goal5784 Triangle mechanism binding mismatch")
    elif binding != {
        "schema": "rtdl.goal5784.mechanism_binding.v1",
        "mechanism_id": "canonical_packed_hierarchy_output_binding",
        "evidence_level": "frozen_source_route__not_fusion",
        "execution_source_sha256": worker["execution_source_sha256"],
        "rt_barneshut_is_fusion": False,
    }:
        raise RuntimeError("Goal5784 RT-BarnesHut mechanism binding mismatch")
    if lifecycle == COLD:
        if worker.get("loading_seconds_reported_separately") is not None \
                or worker.get("preparation_seconds_reported_separately") is not None:
            raise RuntimeError("Goal5784 cold work moved outside timer")
    else:
        for key in ("loading_seconds_reported_separately",
                    "preparation_seconds_reported_separately"):
            value = worker.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)) \
                    or float(value) < 0.0:
                raise RuntimeError("Goal5784 prepared accounting missing")
    receipt = worker.get("traversal_receipt")
    rows = worker.get("rows")
    if not isinstance(receipt, dict) or not isinstance(rows, list):
        raise RuntimeError("Goal5784 worker omitted evidence")
    validate_behavioral_true_optix(receipt)
    expected_ids = set(UNIT_BY_ID[unit_id].statistical_row_ids_for(lifecycle))
    if len(rows) != 1 or {str(row.get("row_id")) for row in rows} != expected_ids:
        raise RuntimeError("Goal5784 row shape mismatch")
    _validate_binding(receipt, rows)
    accounting = worker.get("phase_accounting")
    if not isinstance(accounting, dict) or set(accounting) != {
        "loading_seconds", "preparation_seconds", "close_seconds",
        "row_execute_seconds", "same_worker_mutually_exclusive_phases",
        "nested_phase_medians_summed",
    } or accounting["same_worker_mutually_exclusive_phases"] is not True \
            or accounting["nested_phase_medians_summed"] is not False:
        raise RuntimeError("Goal5784 phase accounting mismatch")
    for row in rows:
        if set(row) != {"row_id", "input_sha256", "output_sha256",
                       "registered_complete_endpoint_seconds"}:
            raise RuntimeError("Goal5784 timed row schema mismatch")
        seconds = float(row["registered_complete_endpoint_seconds"])
        execute = float(accounting["row_execute_seconds"][row["row_id"]])
        expected = execute
        if lifecycle == COLD:
            expected += sum(float(accounting[name]) for name in (
                "loading_seconds", "preparation_seconds", "close_seconds"))
        if not math.isfinite(seconds) or seconds <= 0.0 \
                or not math.isclose(seconds, expected, rel_tol=0.0, abs_tol=1e-12):
            raise RuntimeError("Goal5784 registered seconds mismatch")
        if any(not isinstance(row[key], str) or len(row[key]) != 64
               for key in ("input_sha256", "output_sha256")):
            raise RuntimeError("Goal5784 row digest malformed")
    cache = worker.get("leaf_cache")
    if method == V4 and unit.v4_numba_leaf_cache_required:
        if not isinstance(cache, dict) or cache.get("mode") != "sealed_read_only_manifest" \
                or int(cache.get("hit_count", 0)) <= 0 \
                or int(cache.get("miss_count", -1)) != 0 \
                or int(cache.get("disabled_count", -1)) != 0:
            raise RuntimeError("Goal5784 V4 leaf cache mismatch")
    elif method == V4:
        if cache != {"mode": "not_applicable_no_numba_leaf", "hit_count": 0,
                     "miss_count": 0, "disabled_count": 0}:
            raise RuntimeError("Goal5784 non-leaf cache mismatch")
    elif cache != {"mode": "not_applicable_to_v2_direct"}:
        raise RuntimeError("Goal5784 V2 leaf-cache metadata mismatch")


def recount(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    if json.loads((raw_root / "FORMAL_CONTRACT.json").read_text(encoding="utf-8")) \
            != contract_document():
        raise RuntimeError("Goal5784 raw contract mismatch")
    if json.loads((raw_root / "SCHEDULE.json").read_text(encoding="utf-8")) \
            != list(schedule()):
        raise RuntimeError("Goal5784 raw schedule mismatch")
    paths = sorted((raw_root / "workers").glob("*.json"))
    workers = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if len(workers) != len(schedule()) or len({
        row.get("parent_pid") for row in workers
    }) != len(schedule()):
        raise RuntimeError("Goal5784 worker/PID cardinality mismatch")
    for identity in IDENTITIES:
        values = {row.get(identity) for row in workers}
        if len(values) != 1 or not isinstance(next(iter(values)), str) \
                or len(next(iter(values))) != 64:
            raise RuntimeError(f"Goal5784 mixed identity: {identity}")
    for worker in workers:
        _validate_worker(worker)
    observed_schedule = [{key: worker[key] for key in (
        "worker_index", "lifecycle", "unit_id", "pair_index",
        "order_ordinal", "method")}
        for worker in sorted(workers, key=lambda row: int(row["worker_index"]))]
    if observed_schedule != list(schedule()):
        raise RuntimeError("Goal5784 worker schedule mismatch")
    grouped: dict[tuple[str, str, int], dict[str, dict[str, object]]] = {}
    for worker in workers:
        key = (str(worker["lifecycle"]), str(worker["unit_id"]),
               int(worker["pair_index"]))
        pair = grouped.setdefault(key, {})
        method = str(worker["method"])
        if method in pair:
            raise RuntimeError("Goal5784 duplicate paired method")
        pair[method] = worker
    results = []
    for row_index, description in enumerate(statistical_rows()):
        ratios = []
        for pair_index in range(PAIR_COUNT):
            pair = grouped[(description["lifecycle"], description["unit_id"],
                            pair_index)]
            if set(pair) != {V2, V4}:
                raise RuntimeError("Goal5784 incomplete pair")
            by_method = {}
            for method in METHODS:
                by_method[method] = next(
                    row for row in pair[method]["rows"]
                    if row["row_id"] == description["row_id"])
            if by_method[V2]["input_sha256"] != by_method[V4]["input_sha256"] \
                    or by_method[V2]["output_sha256"] != by_method[V4]["output_sha256"]:
                raise RuntimeError("Goal5784 paired semantic mismatch")
            ratios.append(
                float(by_method[V2]["registered_complete_endpoint_seconds"])
                / float(by_method[V4]["registered_complete_endpoint_seconds"]))
        median = float(statistics.median(ratios))
        lower, upper = _bootstrap(ratios, 57_760_000 + row_index)
        results.append({
            **description, "pair_count": PAIR_COUNT,
            "paired_v2_over_v4_ratios": ratios,
            "paired_ratio_median": median,
            "bootstrap_ci95": [lower, upper],
            "greater_than_one_favors": V4,
            "no_slower_pass": median >= 1.0,
            "independent_comparison_row": True,
        })
    payload = {
        "schema": "rtdl.goal5784.targeted_independent_recount.v1",
        "formal_contract_sha256": contract_sha256(),
        "worker_count": len(workers),
        "unique_parent_pid_count": len(workers),
        "execution_unit_count": len(UNITS),
        "independent_row_count": len(results),
        "rows": results,
        "triangle_clear_fusion_rows": [row["row_id"] for row in results
            if row["app"] == "triangle_counting" and row["bootstrap_ci95"][0] > 1.0],
        "cross_row_or_lifecycle_compensation_used": False,
        "goal5776_replaced_or_relabelled": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(recount(args.raw_root, args.output))


if __name__ == "__main__":
    main()
