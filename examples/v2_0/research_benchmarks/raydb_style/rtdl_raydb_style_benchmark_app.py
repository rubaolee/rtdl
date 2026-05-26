from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt

CPU_RESULT_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
EMBREE_RESULT_MODES = ("count", "sum")
OPTIX_RESULT_MODES = ("count", "sum")
OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND = "optix_partner_resident_experimental"
OPTIX_PARTNER_RESIDENT_RESULT_MODES = ("count", "sum", "min", "max", "avg_as_sum_count")
BACKENDS = (
    "cpu_python_reference",
    "embree",
    "optix",
    OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
)
RESULT_MODES = CPU_RESULT_MODES


def make_fixture(copies: int = 1) -> dict[str, Any]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    base = {
        "row_ids": (1, 2, 3, 4, 5, 6, 7, 8),
        "columns": {
            "region_id": (0, 1, 0, 1, 2, 2, 1, 0),
            "ship_year": (1994, 1994, 1995, 1996, 1994, 1995, 1995, 1994),
            "discount": (5, 6, 3, 5, 7, 4, 5, 6),
            "quantity": (10, 20, 15, 9, 30, 18, 28, 12),
            "revenue": (100, 200, 150, 50, 300, 80, 120, 90),
        },
    }
    if copies == 1:
        return base
    row_count = len(base["row_ids"])
    row_ids: list[int] = []
    columns: dict[str, list[int]] = {name: [] for name in base["columns"]}
    for copy_index in range(copies):
        offset = copy_index * row_count
        row_ids.extend(offset + int(row_id) for row_id in base["row_ids"])
        for name, values in base["columns"].items():
            columns[name].extend(int(value) for value in values)
    return {
        "row_ids": tuple(row_ids),
        "columns": {name: tuple(values) for name, values in columns.items()},
    }


def make_plan(mode: str) -> dict[str, Any]:
    if mode not in RESULT_MODES:
        raise ValueError(f"unsupported result mode: {mode}")
    plan: dict[str, Any] = {
        "predicates": (
            ("ship_year", "between", 1994, 1995),
            ("discount", "between", 4, 6),
            ("quantity", "lt", 25),
        ),
        "group_keys": ("region_id",),
        "aggregate": mode,
    }
    if mode != "count":
        plan["value_field"] = "revenue"
    return plan


def run_result_mode(
    mode: str,
    *,
    backend: str = "cpu_python_reference",
    copies: int = 1,
) -> dict[str, Any]:
    fixture = make_fixture(copies=copies)
    plan = make_plan(mode)
    if backend == "embree":
        return _run_native_result_mode(
            backend="embree",
            fixture=fixture,
            plan=plan,
            mode=mode,
            prepare_dataset=rt.prepare_embree_columnar_record_set,
            result_modes=EMBREE_RESULT_MODES,
            contract="columnar_grouped_aggregate_embree_columnar_payload",
            rt_core_accelerated=False,
            copies=copies,
        )
    if backend == "optix":
        return _run_native_result_mode(
            backend="optix",
            fixture=fixture,
            plan=plan,
            mode=mode,
            prepare_dataset=rt.prepare_optix_columnar_record_set,
            result_modes=OPTIX_RESULT_MODES,
            contract="columnar_grouped_aggregate_optix_columnar_payload",
            rt_core_accelerated=True,
            copies=copies,
        )
    if backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        return _run_optix_partner_resident_experimental_result_mode(
            fixture=fixture,
            plan=plan,
            mode=mode,
            copies=copies,
        )
    if backend != "cpu_python_reference":
        raise ValueError(f"unsupported backend: {backend}")
    started = time.perf_counter()
    result = rt.evaluate_columnar_grouped_aggregate(fixture, plan)
    elapsed_sec = time.perf_counter() - started
    lowering_plan = rt.plan_columnar_aggregate_lowering(backend).to_dict()
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": elapsed_sec,
        "rows": list(result.rows),
        "metadata": {
            **result.metadata,
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {"cpu_reference_sec": elapsed_sec},
            "fixture": "tiny_denormalized_columnar",
            "lowering_plan": lowering_plan,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": False,
            "claim_boundary": (
                "RayDB-style CPU reference fixture only. This validates a generic "
                "columnar grouped aggregate contract; it does not reproduce RayDB, "
                "time authors code, or authorize performance wording."
            ),
        },
    }


def require_optix_partner_resident_experimental_backend() -> Any:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch with CUDA is required for optix_partner_resident_experimental") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for optix_partner_resident_experimental")
    rt.optix_version()
    return torch


def _run_optix_partner_resident_experimental_result_mode(
    *,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    copies: int = 1,
) -> dict[str, Any]:
    if mode not in OPTIX_PARTNER_RESIDENT_RESULT_MODES:
        raise ValueError(
            "OptiX partner-resident experimental RayDB-style slice currently supports only "
            "count/sum/min/max/avg_as_sum_count"
        )
    torch = require_optix_partner_resident_experimental_backend()
    record_set = {
        "row_ids": torch.tensor(fixture["row_ids"], dtype=torch.int64, device="cuda"),
        "columns": {
            name: torch.tensor(values, dtype=torch.int64, device="cuda")
            for name, values in fixture["columns"].items()
        },
    }
    prepare_started = time.perf_counter()
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    prepare_sec = time.perf_counter() - prepare_started
    query = rt.columnar_plan_to_grouped_query(plan)
    group_capacity = _infer_dense_group_capacity(fixture, plan)
    dispatch_query = query
    reduction = mode
    composite_lowering: tuple[str, ...] = ()
    if mode == "avg_as_sum_count":
        decomposed_plans = rt.decompose_columnar_aggregate_plan(plan)
        composite_lowering = tuple(item.aggregate for item in decomposed_plans)
        dispatch_query = rt.columnar_plan_to_grouped_query(decomposed_plans[0])
        reduction = "sum_count"
    query_started = time.perf_counter()
    dispatch_result = rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
        descriptor,
        dispatch_query,
        reduction=reduction,
        allow_experimental_native=True,
        group_capacity=group_capacity,
        semantic_aggregate=mode,
    )
    query_sec = time.perf_counter() - query_started
    result_rows = tuple(dispatch_result["rows"])
    dispatch_metadata = dict(dispatch_result["metadata"])
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": prepare_sec + query_sec,
        "rows": list(result_rows),
        "matches_cpu_reference": tuple(result_rows) == tuple(cpu_rows),
        "metadata": {
            "contract": "columnar_grouped_aggregate_optix_partner_resident_experimental",
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "prepare_sec": prepare_sec,
                "query_sec": query_sec,
                "elapsed_sec": prepare_sec + query_sec,
            },
            "fixture": "tiny_denormalized_columnar",
            "lowering_plan": rt.plan_columnar_aggregate_lowering(
                OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND
            ).to_dict(),
            **dispatch_metadata,
            "partner_resident_descriptor": descriptor.to_metadata(),
            "partner_input_constructed_by_fixture": True,
            "composite_lowering": list(composite_lowering),
            "native_avg_abi_added": False,
            "native_abi_added": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": False,
            "true_zero_copy_authorized": False,
            "claim_boundary": (
                "Experimental OptiX partner-resident count/sum/min/max parity and composite "
                "avg_as_sum_count=sum+count lowering through a generic fused sum_count pass for "
                "the synthetic RayDB-style columnar aggregate contract. This demonstrates "
                "Python+partner+RTDL descriptor execution for CUDA tensors, but it does not "
                "reproduce RayDB, expose SQL/DBMS behavior, authorize true zero-copy wording, "
                "or authorize performance wording."
            ),
        },
    }


def _infer_dense_group_capacity(fixture: dict[str, Any], plan: dict[str, Any]) -> int:
    group_key = plan["group_keys"][0]
    values = tuple(int(value) for value in fixture["columns"][group_key])
    if any(value < 0 for value in values):
        raise ValueError("experimental partner-resident backend requires non-negative dense group keys")
    return max(values) + 1


def _run_native_result_mode(
    *,
    backend: str,
    fixture: dict[str, Any],
    plan: dict[str, Any],
    mode: str,
    prepare_dataset: Any,
    result_modes: tuple[str, ...],
    contract: str,
    rt_core_accelerated: bool,
    copies: int = 1,
) -> dict[str, Any]:
    backend_label = "OptiX" if backend == "optix" else backend.title()
    if mode not in result_modes:
        raise ValueError(f"{backend_label} RayDB-style slice currently supports only count and sum")
    query = rt.columnar_plan_to_grouped_query(plan)
    lowering_plan = rt.plan_columnar_aggregate_lowering(backend).to_dict()
    prepare_started = time.perf_counter()
    dataset = prepare_dataset(
        fixture,
        primary_fields=("ship_year", "discount", "quantity"),
    )
    prepare_sec = time.perf_counter() - prepare_started
    try:
        preparation_metadata = dataset.columnar_preparation_metadata()
        query_started = time.perf_counter()
        result_rows = dataset.grouped_count(query) if mode == "count" else dataset.grouped_sum(query)
        query_sec = time.perf_counter() - query_started
    finally:
        dataset.close()
    cpu_rows = rt.evaluate_columnar_grouped_aggregate(fixture, plan).rows
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "mode": mode,
        "copies": int(copies),
        "row_count": len(fixture["row_ids"]),
        "elapsed_sec": prepare_sec + query_sec,
        "rows": list(result_rows),
        "matches_cpu_reference": tuple(result_rows) == tuple(cpu_rows),
        "metadata": {
            "contract": contract,
            "copies": int(copies),
            "row_count": len(fixture["row_ids"]),
            "timings": {
                "prepare_sec": prepare_sec,
                "query_sec": query_sec,
                "elapsed_sec": prepare_sec + query_sec,
            },
            "fixture": "tiny_denormalized_columnar",
            "lowering_plan": lowering_plan,
            "uses_existing_compatibility_wrapper": False,
            "materializes_input_rows_for_wrapper": False,
            "direct_columnar_record_set_api": True,
            "columnar_preparation": preparation_metadata,
            "native_abi_added": False,
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "rt_core_accelerated": rt_core_accelerated,
            "claim_boundary": (
                f"{backend_label} parity for count/sum over the synthetic RayDB-style "
                "columnar aggregate contract. This uses existing generic columnar "
                "payload capability through direct record-set preparation; it does not "
                "add native RayDB ABI, reproduce RayDB, or authorize performance wording."
            ),
        },
    }


def run_suite(*, backend: str = "cpu_python_reference", copies: int = 1) -> dict[str, Any]:
    if backend == "cpu_python_reference":
        modes = CPU_RESULT_MODES
    elif backend == "embree":
        modes = EMBREE_RESULT_MODES
    elif backend == "optix":
        modes = OPTIX_RESULT_MODES
    elif backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND:
        modes = OPTIX_PARTNER_RESIDENT_RESULT_MODES
    else:
        raise ValueError(f"unsupported backend: {backend}")
    results = {
        mode: run_result_mode(mode, backend=backend, copies=copies)
        for mode in modes
    }
    return {
        "app": "raydb_style_columnar_aggregate",
        "backend": backend,
        "copies": int(copies),
        "row_count": len(make_fixture(copies=copies)["row_ids"]),
        "modes": results,
        "all_match_cpu_reference": all(payload.get("matches_cpu_reference", True) for payload in results.values()),
        "claim_boundary": (
            "CPU-only synthetic RayDB-style fixture for RTDL contract design. "
            "No Embree, OptiX, authors-code, SQL engine, DBMS, or speedup claim."
            if backend == "cpu_python_reference"
            else (
                "Experimental OptiX partner-resident count/sum/min/max plus composite avg_as_sum_count "
                "parity for the synthetic RayDB-style contract. "
                "No authors-code, SQL engine, DBMS, true zero-copy, or speedup claim."
                if backend == OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND
                else f"{'OptiX' if backend == 'optix' else backend.title()} count/sum parity for the synthetic RayDB-style contract. "
                "No authors-code, SQL engine, DBMS, or speedup claim."
            )
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the RayDB-style CPU reference benchmark slice.")
    parser.add_argument("--mode", choices=("all", *RESULT_MODES), default="all")
    parser.add_argument("--backend", choices=BACKENDS, default="cpu_python_reference")
    parser.add_argument("--copies", type=int, default=1)
    args = parser.parse_args(argv)
    payload = (
        run_suite(backend=args.backend, copies=args.copies)
        if args.mode == "all"
        else run_result_mode(args.mode, backend=args.backend, copies=args.copies)
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
