#!/usr/bin/env python3
"""Independent raw recount for Goal5776.

This file intentionally imports neither the primary evaluator nor the Python
contract module.  It rebuilds row membership from the frozen JSON contract and
reimplements pairing, median and bootstrap locally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
METHODS = {V2, V4}
BOUNDARY = (
    "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1"
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
        raise RuntimeError("Goal5776 recount registered-row binding mismatch")
    if receipt.get("schema") \
            == "rtdl.goal5776.combined_behavioral_optix_receipt.v1":
        components = receipt.get("component_receipts")
        if not isinstance(components, list) or (
            receipt.get("component_receipt_count") != len(components)
            or receipt.get("component_receipts_sha256") != _digest(components)
        ):
            raise RuntimeError("Goal5776 recount combined components mismatch")
        for component in components:
            try:
                snapshot = component["native_snapshot"]
                successful = int(snapshot["successful_launch_count"])
                complete = int(snapshot["complete_context_launch_count"])
                unbound_count = int(snapshot.get(
                    "unbound_launch_count", successful - complete))
                valid = (
                    component["physical_executor_classification"]
                    == "optix_traversal_observed"
                    and successful > 0 and complete == successful
                    and unbound_count == 0
                    and all(int(snapshot[name]) == 0 for name in (
                        "failed_launch_count", "incomplete_context_launch_count",
                        "pending_context_at_finish", "session_error"))
                    and bool(snapshot["first_traversable"])
                    and bool(snapshot["last_traversable"])
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError(
                    "Goal5776 recount malformed combined component") from exc
            if not valid:
                raise RuntimeError("Goal5776 recount unproven combined component")


def _quantiles(values: list[float], seed: int) -> tuple[float, float]:
    generator = random.Random(seed)
    sample_size = len(values)
    simulations = []
    for _ in range(10_000):
        sample = generator.choices(values, k=sample_size)
        simulations.append(float(statistics.median(sample)))
    simulations.sort()
    return simulations[249], simulations[9749]


def recount(raw_root: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(output)
    contract = json.loads((raw_root / "FORMAL_CONTRACT.json").read_text(encoding="utf-8"))
    schedule = json.loads((raw_root / "SCHEDULE.json").read_text(encoding="utf-8"))
    if (
        contract.get("schema") != "rtdl.goal5776.real_scale_formal_contract.v1"
        or contract.get("execution_unit_count") != 15
        or contract.get("independent_row_count_by_lifecycle") != {
            "installed_cold_compile_prepare_execute": 15,
            "prepared_first_execute": 19,
        }
        or contract.get("independent_row_count_total") != 34
        or contract.get("formal_worker_count") != 464
        or contract.get("pair_count_per_unit_lifecycle") != 8
        or len(schedule) != 464
    ):
        raise RuntimeError("unexpected Goal5776 frozen contract shape")
    units = {
        row["unit_id"]: {
            lifecycle: tuple(row["statistical_row_ids_by_lifecycle"][lifecycle])
            for lifecycle in contract["lifecycles"]
        }
        for row in contract["units"]
    }
    if (
        len(units) != 15
        or sum(len(rows["installed_cold_compile_prepare_execute"])
               for rows in units.values()) != 15
        or sum(len(rows["prepared_first_execute"])
               for rows in units.values()) != 19
    ):
        raise RuntimeError("Goal5776 unit-to-row membership mismatch")
    lifecycles = tuple(contract["lifecycles"])
    if len(lifecycles) != 2:
        raise RuntimeError("Goal5776 lifecycle count mismatch")
    workers = [json.loads(path.read_text(encoding="utf-8"))
               for path in sorted((raw_root / "workers").glob("*.json"))]
    if len(workers) != 464 or len({row.get("parent_pid") for row in workers}) != 464:
        raise RuntimeError("Goal5776 fresh-worker cardinality mismatch")
    identities = (
        "bundle_sha256", "data_archive_sha256",
        "execution_source_sha256", "source_tree_sha256",
        "rtdbscan_evidence_sha256",
        "native_library_sha256", "target_identity_sha256",
        "prepared_identity_sha256", "plan_sha256",
        "formal_identity_sha256", "leaf_cache_manifest_sha256",
        "expected_value_statement_sha256",
        "formal_contract_sha256", "runtime_sha256",
    )
    for name in identities:
        values = {row.get(name) for row in workers}
        if len(values) != 1 or not isinstance(next(iter(values)), str) \
                or len(next(iter(values))) != 64:
            raise RuntimeError(f"mixed identity in recount: {name}")
    scheduled = {
        (str(row["lifecycle"]), str(row["unit_id"]), int(row["pair_index"]), str(row["method"]))
        for row in schedule
    }
    observed = {
        (str(row["lifecycle"]), str(row["unit_id"]), int(row["pair_index"]), str(row["method"]))
        for row in workers
    }
    if scheduled != observed or len(observed) != 464:
        raise RuntimeError("Goal5776 schedule/worker membership mismatch")

    grouped = {}
    for worker in workers:
        if (
            worker.get("matched") is not True
            or worker.get("formal_worker") is not True
            or worker.get("comparator_inside_registered_timer") is not False
            or worker.get("registered_endpoint_boundary_id") != BOUNDARY
            or worker.get("default_selected_between_application_algorithms") is not False
            or worker.get("retry_resume_replacement_row_drop_relabel_used") is not False
        ):
            raise RuntimeError("Goal5776 recount worker contract mismatch")
        lifecycle = str(worker["lifecycle"])
        loading = worker.get("loading_seconds_reported_separately")
        preparation = worker.get("preparation_seconds_reported_separately")
        if worker.get("close_inside_registered_timer") is not (
            lifecycle == "installed_cold_compile_prepare_execute"
        ):
            raise RuntimeError("Goal5776 recount teardown boundary mismatch")
        if lifecycle == "installed_cold_compile_prepare_execute":
            if loading is not None or preparation is not None:
                raise RuntimeError("Goal5776 recount cold boundary mismatch")
        else:
            if any(
                not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0.0
                for value in (loading, preparation)
            ):
                raise RuntimeError("Goal5776 recount prepared boundary mismatch")
        unit_description = next(
            item for item in contract["units"] if item["unit_id"] == worker["unit_id"]
        )
        cache = worker.get("leaf_cache")
        if worker["method"] == V4:
            if unit_description["v4_numba_leaf_cache_required"]:
                cache_ok = (
                    isinstance(cache, dict)
                    and cache.get("mode") == "sealed_read_only_manifest"
                    and int(cache.get("hit_count", 0)) > 0
                    and int(cache.get("miss_count", -1)) == 0
                    and int(cache.get("disabled_count", -1)) == 0
                )
            else:
                cache_ok = (
                    isinstance(cache, dict)
                    and cache.get("mode") == "not_applicable_no_numba_leaf"
                    and all(int(cache.get(key, -1)) == 0 for key in (
                        "hit_count", "miss_count", "disabled_count"))
                )
            if not cache_ok:
                raise RuntimeError("Goal5776 recount V4 leaf-cache contract mismatch")
        elif cache != {"mode": "not_applicable_to_v2_direct"}:
            raise RuntimeError("Goal5776 recount V2 leaf-cache metadata mismatch")
        session_wall = worker.get(
            "prepared_session_complete_wall_seconds_reported_separately"
        )
        if unit_description["app"] == "rayjoin" and lifecycle == \
                "prepared_first_execute":
            if not isinstance(session_wall, (int, float)) or not math.isfinite(
                float(session_wall)
            ) or float(session_wall) <= 0.0:
                raise RuntimeError(
                    "Goal5776 recount missing RayJoin complete-session wall"
                )
        elif session_wall is not None:
            raise RuntimeError("Goal5776 recount unexpected session wall")
        accounting = worker.get("phase_accounting")
        if not isinstance(accounting, dict) or set(accounting) != {
            "loading_seconds", "preparation_seconds", "close_seconds",
            "row_execute_seconds", "same_worker_mutually_exclusive_phases",
            "nested_phase_medians_summed",
        } or accounting["same_worker_mutually_exclusive_phases"] is not True \
                or accounting["nested_phase_medians_summed"] is not False:
            raise RuntimeError("Goal5776 recount phase accounting mismatch")
        try:
            receipt = worker["traversal_receipt"]
            snapshot = receipt["native_snapshot"]
            successful = int(snapshot["successful_launch_count"])
            complete = int(snapshot["complete_context_launch_count"])
            unbound = int(snapshot.get(
                "unbound_launch_count", successful - complete
            ))
            receipt_ok = (
                receipt["physical_executor_classification"]
                == "optix_traversal_observed"
                and successful > 0
                and complete == successful
                and unbound == 0
                and all(int(snapshot[name]) == 0 for name in (
                    "failed_launch_count", "incomplete_context_launch_count",
                    "pending_context_at_finish",
                    "session_error",
                ))
                and bool(snapshot["first_traversable"])
                and bool(snapshot["last_traversable"])
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("Goal5776 recount malformed traversal receipt") from exc
        if not receipt_ok:
            raise RuntimeError("Goal5776 recount unproven OptiX traversal")
        unit_id = str(worker["unit_id"])
        if unit_id not in units or {row["row_id"] for row in worker["rows"]} != set(
            units[unit_id][lifecycle]
        ):
            raise RuntimeError("Goal5776 recount row membership mismatch")
        _validate_registered_row_binding(receipt, worker["rows"])
        for timed_row in worker["rows"]:
            execute = accounting["row_execute_seconds"].get(timed_row["row_id"])
            if not isinstance(execute, (int, float)) or not math.isfinite(
                float(execute)
            ) or float(execute) <= 0.0:
                raise RuntimeError("Goal5776 recount missing direct execute phase")
            expected = float(execute)
            if lifecycle == "installed_cold_compile_prepare_execute":
                expected += sum(float(accounting[name]) for name in (
                    "loading_seconds", "preparation_seconds", "close_seconds"
                ))
            if not math.isclose(
                float(timed_row["registered_complete_endpoint_seconds"]),
                expected, rel_tol=0.0, abs_tol=1.0e-12,
            ):
                raise RuntimeError("Goal5776 recount phase sum mismatch")
        key = (str(worker["lifecycle"]), unit_id, int(worker["pair_index"]))
        method = str(worker["method"])
        grouped.setdefault(key, {})[method] = worker

    results = []
    row_index = 0
    for lifecycle in lifecycles:
        for unit in contract["units"]:
            for row_id in unit["statistical_row_ids_by_lifecycle"][lifecycle]:
                ratios = []
                for pair_index in range(8):
                    pair = grouped[(lifecycle, unit["unit_id"], pair_index)]
                    if set(pair) != METHODS:
                        raise RuntimeError("Goal5776 recount incomplete pair")
                    resolved = {}
                    for method in (V2, V4):
                        resolved[method] = next(
                            item for item in pair[method]["rows"] if item["row_id"] == row_id
                        )
                    if (
                        resolved[V2]["input_sha256"] != resolved[V4]["input_sha256"]
                        or resolved[V2]["output_sha256"] != resolved[V4]["output_sha256"]
                    ):
                        raise RuntimeError("Goal5776 recount paired digest mismatch")
                    numerator = float(resolved[V2]["registered_complete_endpoint_seconds"])
                    denominator = float(resolved[V4]["registered_complete_endpoint_seconds"])
                    if not all(math.isfinite(value) and value > 0.0
                               for value in (numerator, denominator)):
                        raise RuntimeError("Goal5776 recount invalid seconds")
                    ratios.append(numerator / denominator)
                median = float(statistics.median(ratios))
                lower, upper = _quantiles(ratios, 57_760_000 + row_index)
                results.append({
                    "lifecycle": lifecycle,
                    "unit_id": unit["unit_id"],
                    "row_id": row_id,
                    "paired_ratio_median": median,
                    "bootstrap_ci95": [lower, upper],
                    "no_slower_pass": median >= 1.0,
                })
                row_index += 1
    payload = {
        "schema": "rtdl.goal5776.real_scale_v2_v4_independent_recount.v1",
        "worker_count": len(workers),
        "row_count": len(results),
        "pass_count": sum(bool(row["no_slower_pass"]) for row in results),
        "fail_count": sum(not bool(row["no_slower_pass"]) for row in results),
        "rows": results,
        "primary_evaluator_imported": False,
        "python_contract_module_imported": False,
        "cross_app_or_lifecycle_compensation_used": False,
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
    print(recount(args.raw_root, args.output))


if __name__ == "__main__":
    main()
