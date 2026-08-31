#!/usr/bin/env python3
"""Primary evaluator for the frozen Goal5776 real-scale V2/V4 cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

from goal5776_real_scale_formal_contract import (
    COLD,
    LIFECYCLES,
    METHODS,
    PAIR_COUNT,
    PREPARED,
    UNIT_BY_ID,
    UNITS,
    V2,
    V4,
    contract_document,
    contract_sha256,
    schedule,
    statistical_rows,
)
from goal5776_symmetric_endpoint import validate_behavioral_true_optix


BOUNDARY = "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1"
IDENTITIES = (
    "bundle_sha256",
    "data_archive_sha256",
    "execution_source_sha256",
    "source_tree_sha256",
    "rtdbscan_evidence_sha256",
    "native_library_sha256",
    "target_identity_sha256",
    "prepared_identity_sha256",
    "plan_sha256",
    "formal_identity_sha256",
    "leaf_cache_manifest_sha256",
    "expected_value_statement_sha256",
    "formal_contract_sha256",
    "runtime_sha256",
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _validate_registered_row_binding(
    receipt: dict[str, object], rows: list[dict[str, object]],
) -> None:
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
        raise RuntimeError("worker registered-row receipt binding mismatch")
    if receipt.get("schema") \
            == "rtdl.goal5776.combined_behavioral_optix_receipt.v1":
        components = receipt.get("component_receipts")
        if not isinstance(components, list) or (
            receipt.get("component_receipt_count") != len(components)
            or receipt.get("component_receipts_sha256") != _digest(components)
        ):
            raise RuntimeError("worker combined receipt components mismatch")
        for component in components:
            if not isinstance(component, dict):
                raise RuntimeError("worker combined receipt component malformed")
            validate_behavioral_true_optix(component)


def _bootstrap(values: list[float], seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    draws = sorted(
        statistics.median(rng.choices(values, k=len(values)))
        for _ in range(10_000)
    )
    return float(draws[249]), float(draws[9749])


def _read_workers(raw_root: Path) -> list[dict[str, object]]:
    paths = sorted((raw_root / "workers").glob("*.json"))
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def _validate_worker(row: dict[str, object]) -> None:
    unit_id = str(row.get("unit_id"))
    lifecycle = str(row.get("lifecycle"))
    method = str(row.get("method"))
    if unit_id not in UNIT_BY_ID or lifecycle not in LIFECYCLES or method not in METHODS:
        raise RuntimeError("unknown Goal5776 worker unit/lifecycle/method")
    if row.get("formal_contract_sha256") != contract_sha256():
        raise RuntimeError("worker does not bind exact formal contract")
    if (
        row.get("formal_worker") is not True
        or row.get("matched") is not True
        or row.get("comparator_inside_registered_timer") is not False
        or row.get("registered_endpoint_boundary_id") != BOUNDARY
        or row.get("default_selected_between_application_algorithms") is not False
        or row.get("retry_resume_replacement_row_drop_relabel_used") is not False
        or row.get("close_inside_registered_timer") is not (lifecycle == COLD)
    ):
        raise RuntimeError("Goal5776 formal worker contract violation")
    loading = row.get("loading_seconds_reported_separately")
    preparation = row.get("preparation_seconds_reported_separately")
    if lifecycle == COLD:
        if loading is not None or preparation is not None:
            raise RuntimeError(
                "cold worker moved loading or preparation outside its timer"
            )
    else:
        for name, value in (("loading", loading), ("preparation", preparation)):
            if not isinstance(value, (int, float)) or not math.isfinite(
                float(value)
            ) or float(value) < 0.0:
                raise RuntimeError(
                    f"prepared worker omitted its {name} observation"
                )
    session_wall = row.get(
        "prepared_session_complete_wall_seconds_reported_separately"
    )
    if UNIT_BY_ID[unit_id].app == "rayjoin" and lifecycle == PREPARED:
        if not isinstance(session_wall, (int, float)) or not math.isfinite(
            float(session_wall)
        ) or float(session_wall) <= 0.0:
            raise RuntimeError(
                "prepared RayJoin worker omitted complete-session wall"
            )
    elif session_wall is not None:
        raise RuntimeError("unexpected complete-session wall observation")
    validate_behavioral_true_optix(dict(row["traversal_receipt"]))
    output_rows = row.get("rows")
    accounting = row.get("phase_accounting")
    if not isinstance(accounting, dict) or set(accounting) != {
        "loading_seconds", "preparation_seconds", "close_seconds",
        "row_execute_seconds", "same_worker_mutually_exclusive_phases",
        "nested_phase_medians_summed",
    } or accounting["same_worker_mutually_exclusive_phases"] is not True \
            or accounting["nested_phase_medians_summed"] is not False:
        raise RuntimeError("worker lacks auditable mutually-exclusive phase accounting")
    expected_ids = set(UNIT_BY_ID[unit_id].statistical_row_ids_for(lifecycle))
    if not isinstance(output_rows, list) or {
        str(item.get("row_id")) for item in output_rows if isinstance(item, dict)
    } != expected_ids or len(output_rows) != len(expected_ids):
        raise RuntimeError("worker statistical row shape mismatch")
    _validate_registered_row_binding(
        dict(row["traversal_receipt"]), output_rows)
    for item in output_rows:
        if not isinstance(item, dict) or set(item) != {
            "row_id", "input_sha256", "output_sha256",
            "registered_complete_endpoint_seconds",
        }:
            raise RuntimeError("worker output row schema mismatch")
        seconds = item["registered_complete_endpoint_seconds"]
        if not isinstance(seconds, (int, float)) or not math.isfinite(
            float(seconds)
        ) or float(seconds) <= 0.0:
            raise RuntimeError("invalid registered endpoint seconds")
        if any(not isinstance(item[name], str) or len(item[name]) != 64
               for name in ("input_sha256", "output_sha256")):
            raise RuntimeError("invalid paired input/output digest")
        execute = accounting["row_execute_seconds"].get(item["row_id"])
        if not isinstance(execute, (int, float)) or not math.isfinite(
            float(execute)
        ) or float(execute) <= 0.0:
            raise RuntimeError("worker row lacks direct execute phase")
        expected = float(execute)
        if lifecycle == COLD:
            expected += sum(float(accounting[name]) for name in (
                "loading_seconds", "preparation_seconds", "close_seconds"
            ))
        if not math.isclose(float(seconds), expected, rel_tol=0.0, abs_tol=1e-12):
            raise RuntimeError("worker registered seconds do not match phase accounting")
    cache = row.get("leaf_cache")
    if method == V4:
        unit = UNIT_BY_ID[str(row["unit_id"])]
        if unit.v4_numba_leaf_cache_required:
            if not isinstance(cache, dict) or (
                cache.get("mode") != "sealed_read_only_manifest"
                or int(cache.get("hit_count", 0)) <= 0
                or int(cache.get("miss_count", -1)) != 0
                or int(cache.get("disabled_count", -1)) != 0
            ):
                raise RuntimeError("V4 formal worker did not use the sealed leaf cache")
        elif not isinstance(cache, dict) or (
            cache.get("mode") != "not_applicable_no_numba_leaf"
            or any(int(cache.get(key, -1)) != 0 for key in (
                "hit_count", "miss_count", "disabled_count"))
        ):
            raise RuntimeError("non-leaf V4 worker has invalid leaf-cache metadata")
    elif cache != {"mode": "not_applicable_to_v2_direct"}:
        raise RuntimeError("V2 worker has unexpected V4 leaf-cache metadata")


def evaluate(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    frozen_contract = raw_root / "FORMAL_CONTRACT.json"
    frozen_schedule = raw_root / "SCHEDULE.json"
    if json.loads(frozen_contract.read_text(encoding="utf-8")) != contract_document():
        raise RuntimeError("raw cohort contract differs from evaluator contract")
    if json.loads(frozen_schedule.read_text(encoding="utf-8")) != list(schedule()):
        raise RuntimeError("raw cohort schedule differs from frozen ABBA schedule")
    workers = _read_workers(raw_root)
    if len(workers) != len(schedule()) or len({row.get("parent_pid") for row in workers}) \
            != len(workers):
        raise RuntimeError("Goal5776 requires one fresh parent PID per worker")
    for identity in IDENTITIES:
        values = {row.get(identity) for row in workers}
        if len(values) != 1 or not isinstance(next(iter(values)), str) \
                or len(next(iter(values))) != 64:
            raise RuntimeError(f"mixed worker identity: {identity}")
    for row in workers:
        _validate_worker(row)

    grouped: dict[tuple[str, str, int], dict[str, dict[str, object]]] = {}
    for row in workers:
        key = (str(row["lifecycle"]), str(row["unit_id"]), int(row["pair_index"]))
        method = str(row["method"])
        pair = grouped.setdefault(key, {})
        if method in pair:
            raise RuntimeError("duplicate method in one Goal5776 pair")
        pair[method] = row
    expected_pair_groups = len(schedule()) // len(METHODS)
    if len(grouped) != expected_pair_groups:
        raise RuntimeError("Goal5776 paired group count mismatch")

    results: list[dict[str, object]] = []
    for row_index, description in enumerate(statistical_rows()):
        ratios: list[float] = []
        for pair_index in range(PAIR_COUNT):
            pair = grouped[(description["lifecycle"], description["unit_id"], pair_index)]
            if set(pair) != {V2, V4}:
                raise RuntimeError("Goal5776 pair is incomplete")
            timed = {}
            for method in METHODS:
                worker_row = {
                    item["row_id"]: item for item in pair[method]["rows"]
                }[description["row_id"]]
                timed[method] = worker_row
            if (
                timed[V2]["input_sha256"] != timed[V4]["input_sha256"]
                or timed[V2]["output_sha256"] != timed[V4]["output_sha256"]
            ):
                raise RuntimeError("Goal5776 paired input/output mismatch")
            numerator = float(timed[V2]["registered_complete_endpoint_seconds"])
            denominator = float(timed[V4]["registered_complete_endpoint_seconds"])
            ratios.append(numerator / denominator)
        median = float(statistics.median(ratios))
        lower, upper = _bootstrap(ratios, 57_760_000 + row_index)
        results.append({
            **description,
            "pair_count": PAIR_COUNT,
            "paired_v2_over_v4_ratios": ratios,
            "paired_ratio_median": median,
            "bootstrap_ci95": [lower, upper],
            "greater_than_one_favors": V4,
            "no_slower_pass": median >= 1.0,
            "independent_comparison_row": True,
        })

    lifecycle = {}
    for name in LIFECYCLES:
        rows = [row for row in results if row["lifecycle"] == name]
        lifecycle[name] = {
            "row_count": len(rows),
            "pass_count": sum(bool(row["no_slower_pass"]) for row in rows),
            "fail_count": sum(not bool(row["no_slower_pass"]) for row in rows),
            "all_row_no_slower": all(bool(row["no_slower_pass"]) for row in rows),
        }
    payload = {
        "schema": "rtdl.goal5776.real_scale_v2_v4_evaluation.v1",
        "formal_contract_sha256": contract_sha256(),
        "worker_count": len(workers),
        "execution_unit_count": len(UNITS),
        "row_count": len(results),
        "independent_row_count": len(results),
        "lifecycle_results": lifecycle,
        "rows": results,
        "cross_app_compensation_used": False,
        "cross_lifecycle_compensation_used": False,
        "rayjoin_derived_sum_used_as_independent_result": False,
        "fixed_speedup_target_used": False,
        "cold_result_replaced_by_prepared": False,
        "prepared_work_called_free": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(evaluate(args.raw_root, args.output))


if __name__ == "__main__":
    main()
