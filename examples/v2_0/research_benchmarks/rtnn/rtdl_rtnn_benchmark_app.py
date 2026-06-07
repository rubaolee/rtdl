from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.apps.ml import rtdl_ann_candidate_app as ann_app


BENCHMARK_NAME = "rtnn_neighbor_search"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2388_rtnn_fair_fight_pod"
RTNN_V2_8_RANKED_SUMMARY_TYPED_STREAM_VERSION = "rtdl.rtnn.v2_8.ranked_summary_typed_stream.v1"
RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH = "generic_ranked_summary_typed_stream_partner_columns"


SUPPORTED_CONTRACTS = (
    {
        "name": "ann_candidate_quality_2d",
        "owner": "examples/v2_0/apps/ml/rtdl_ann_candidate_app.py",
        "contract": "candidate-subset exact top-1 rerank compared with exact full-set top-1",
        "runtime_shape": "Python-selected candidate set plus RTDL or partner exact top-k rows",
    },
    {
        "name": "ann_candidate_threshold_2d",
        "owner": "examples/v2_0/apps/ml/rtdl_ann_candidate_app.py",
        "contract": "prepared fixed-radius candidate-coverage threshold",
        "runtime_shape": "generic prepared 2-D fixed-radius threshold-reached count",
    },
    {
        "name": "rtnn_ranked_summary_3d",
        "owner": "scripts/goal2348_rtnn_v2_2_external_runner.py",
        "contract": "exact fixed-radius bounded ranked-neighbor summary row per query",
        "runtime_shape": "packed columns, prepared OptiX 3-D search structure, explicit query batches",
    },
)


CLAIM_BOUNDARY = {
    "benchmark_app": True,
    "native_engine_customization": False,
    "full_rtnn_paper_reproduction": False,
    "ann_index_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "public_speedup_claim_authorized": False,
}


def _load_artifact(name: str) -> dict[str, Any]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _sum_phase(payload: dict[str, Any], key: str) -> float:
    return sum(float(item.get(key, 0.0)) for item in payload.get("batch_phase_timings", ()))


def _official_timing(payload: dict[str, Any], name: str) -> float | None:
    timings = payload.get("timings", {})
    row = timings.get(name)
    if not row:
        return None
    return float(row["last_ms"])


def scope_payload() -> dict[str, Any]:
    return {
        "app": BENCHMARK_NAME,
        "status": "promoted_benchmark_with_boundary",
        "paper_reference": {
            "name": "RTNN: Accelerating Neighbor Search Using Hardware Ray Tracing",
            "public_code_used_by_runner": "https://github.com/horizon-research/rtnn",
            "relationship": (
                "RTDL reproduces RTNN-shaped fixed-radius neighbor-search contracts; "
                "it does not claim full RTNN paper-system reproduction."
            ),
        },
        "supported_contracts": SUPPORTED_CONTRACTS,
        "runtime_design_pressure": (
            "prepared search-side structures, packed-column inputs, device-side ranked summaries, "
            "explicit query batching, density-aware partitioning, and optional partner exact top-k references"
        ),
        "non_goals": (
            "no native ANN index, no graph/IVF/HNSW training phase, no RTNN-specific native symbol, "
            "no broad nearest-neighbor speedup claim"
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "primary_reports": (
            "docs/reports/goal1983_exact_ann_candidate_quality_partner_reference_2026-05-14.md",
            "docs/reports/goal2388_rtnn_fair_fight_benchmark_2026-05-19.md",
            "docs/reports/goal2585_rtnn_benchmark_front_door_2026-05-24.md",
        ),
    }


def ann_cpu_quality_payload(*, copies: int) -> dict[str, Any]:
    payload = ann_app.run_app(
        "cpu_python_reference",
        copies=copies,
        output_mode="quality_summary",
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "ann_cpu_quality",
        "contract": "candidate-subset exact top-1 rerank quality against full-set exact top-1",
        **payload,
        "claim_boundary": {
            "ann_index_claim_authorized": False,
            "native_engine_customization": False,
            "rt_core_speedup_claim_authorized": False,
        },
    }


def ann_partner_quality_payload(*, copies: int, partner: str) -> dict[str, Any]:
    payload = ann_app.run_app(
        "partner_exact_quality",
        copies=copies,
        output_mode="quality_summary",
        partner=partner,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "ann_partner_quality",
        "contract": "partner-owned exact candidate-subset top-k and full-set top-k quality reference",
        **payload,
    }


def rtnn_known_results_payload() -> dict[str, Any]:
    rows = []
    for distribution in ("uniform", "clustered", "shell"):
        rtdl = _load_artifact(f"rtdl_batched_ranked_summary_{distribution}_65536_r002_k50.json")
        cupy = _load_artifact(f"cupy_exact_ranked_summary_{distribution}_65536_r002_k50.json")
        official = _load_artifact(f"rtnn_official_radius_{distribution}_65536_r002_k50.json")
        rows.append(
            {
                "distribution": distribution,
                "point_count": int(rtdl["query_count"]),
                "radius": float(rtdl["radius"]),
                "k_max": int(rtdl["k_max"]),
                "rtdl_prepared_optix_sec": float(rtdl["elapsed_sec"]),
                "cupy_cuda_core_all_pairs_sec": float(cupy["elapsed_sec"]),
                "cupy_over_rtdl": float(cupy["elapsed_sec"]) / float(rtdl["elapsed_sec"]),
                "rtdl_raw_candidates": int(_sum_phase(rtdl, "raw_candidate_count")),
                "cupy_bounded_neighbors": int(cupy["summary"]["bounded_neighbor_count"]),
                "official_rtnn_process_sec": float(official["elapsed_sec"]),
                "official_rtnn_search_compute_ms": _official_timing(official, "search compute"),
                "official_rtnn_total_search_ms": _official_timing(official, "total search time"),
                "same_contract_with_official_rtnn": False,
            }
        )

    scale_rows = []
    for distribution in ("uniform", "clustered", "shell"):
        rtdl = _load_artifact(f"rtdl_batched_ranked_summary_{distribution}_262144_r002_k50.json")
        official = _load_artifact(f"rtnn_official_radius_{distribution}_262144_r002_k50.json")
        scale_rows.append(
            {
                "distribution": distribution,
                "point_count": int(rtdl["query_count"]),
                "rtdl_prepared_optix_sec": float(rtdl["elapsed_sec"]),
                "rtdl_row_count": int(rtdl["row_count"]),
                "rtdl_raw_candidates": int(_sum_phase(rtdl, "raw_candidate_count")),
                "official_rtnn_returncode": int(official["returncode"]),
                "official_rtnn_process_sec": float(official["elapsed_sec"]),
                "same_contract_with_official_rtnn": False,
            }
        )

    return {
        "app": BENCHMARK_NAME,
        "mode": "rtnn_known_results",
        "artifact_dir": str(ARTIFACT_DIR.relative_to(ROOT)),
        "contract": "exact fixed-radius bounded ranked-neighbor summary row per query",
        "rows_65536": rows,
        "rtdl_scale_rows_262144": scale_rows,
        "interpretation": (
            "RTDL prepared OptiX is much faster than the included CuPy all-pairs CUDA-core baseline "
            "for the same ranked-summary contract; official RTNN rows are diagnostic because their "
            "pipeline and materialization contract differ."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rtnn_command_plan_payload() -> dict[str, Any]:
    runner = "scripts/goal2348_rtnn_v2_2_external_runner.py"
    return {
        "app": BENCHMARK_NAME,
        "mode": "rtnn_command_plan",
        "from_repo_root": True,
        "commands": (
            f"PYTHONPATH=src:. python3 {runner} generate --point-file /tmp/rtnn_uniform_65536.csv --point-count 65536 --dimension 3 --distribution uniform",
            f"PYTHONPATH=src:. python3 {runner} run-rtdl-batched-3d-neighbors --point-file /tmp/rtnn_uniform_65536.csv --radius 0.02 --k-max 50 --result-mode ranked-summary-raw --query-batch-size 65536",
            f"PYTHONPATH=src:. python3 {runner} run-cupy-grid-3d-ranked-summary --point-file /tmp/rtnn_uniform_65536.csv --radius 0.02 --k-max 50 --query-batch-size 65536",
        ),
        "optional_external_rtnn": {
            "source": "https://github.com/horizon-research/rtnn",
            "patch_command": f"PYTHONPATH=src:. python3 {runner} patch-rtnn-cuda12 --rtnn-root /path/to/rtnn",
            "boundary": "external code is diagnostic unless the same output contract is proven",
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def describe_rtnn_v2_8_ranked_summary_typed_stream(
    *,
    operation: str = "grouped_topk_f64",
    partner: str = "torch",
    k: int = 8,
) -> dict[str, Any]:
    request = rt.execute_ranked_summary_typed_stream_partner_columns(
        group_ids=(0, 0, 1),
        item_ids=(7, 3, 9),
        scores=(0.5, 1.25, 0.75),
        group_count=2,
        operation=operation,
        partner=partner,
        stream_id="rtnn_v2_8_ranked_summary_descriptor",
        producer_primitive="fixed_radius_ranked_summary_columns_3d",
        k=k if operation == "grouped_topk_f64" else None,
        dry_run=True,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "contract_version": RTNN_V2_8_RANKED_SUMMARY_TYPED_STREAM_VERSION,
        "execution_path": RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH,
        "operation": operation,
        "partner": partner,
        "k": k if operation == "grouped_topk_f64" else None,
        "uses_v2_8_typed_result_stream": True,
        "uses_v2_8_ranked_summary_front_door": True,
        "requires_caller_supplied_partner_columns": True,
        "source_materialization": request["source_materialization"],
        "typed_stream": request["typed_stream"],
        "continuation_plan": request["continuation_plan"],
        "partner_policy": {
            "explicit_user_partner_choice_required": True,
            "automatic_partner_selection_allowed": False,
            "argmin_argmax_partners": ("numba", "torch", "triton"),
            "topk_partners": ("torch", "triton"),
            "numba_topk_status": "not_promoted_in_current_partner_adapter",
        },
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "device_resident_result_stream_proven": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "full_rtnn_paper_reproduction": False,
        },
    }


def describe_rtnn_ranked_summary_typed_stream(
    *,
    operation: str = "grouped_topk_f64",
    partner: str = "torch",
    k: int = 8,
) -> dict[str, Any]:
    """Current alias for the legacy v2.8 ranked-summary typed-stream descriptor."""

    descriptor = describe_rtnn_v2_8_ranked_summary_typed_stream(
        operation=operation,
        partner=partner,
        k=k,
    )
    return {
        **descriptor,
        "legacy_helper_alias": "describe_rtnn_v2_8_ranked_summary_typed_stream",
        "current_helper": "describe_rtnn_ranked_summary_typed_stream",
        "current_mode_alias": "ranked_summary_typed_stream_plan",
    }


def run_rtnn_v2_8_ranked_summary_typed_stream_preview(
    inputs: dict[str, Any],
    *,
    operation: str = "grouped_topk_f64",
    partner: str = "torch",
    k: int = 8,
    block_size: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    request = rt.execute_ranked_summary_typed_stream_partner_columns(
        group_ids=inputs["group_ids"],
        item_ids=inputs["item_ids"],
        scores=inputs["scores"],
        group_count=int(inputs["group_count"]),
        operation=operation,
        partner=partner,
        stream_id=str(inputs.get("stream_id", "rtnn_v2_8_ranked_summary_preview")),
        producer_primitive=str(inputs.get("producer_primitive", "fixed_radius_ranked_summary_columns_3d")),
        k=k if operation == "grouped_topk_f64" else None,
        block_size=block_size,
        dry_run=dry_run,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "contract_version": RTNN_V2_8_RANKED_SUMMARY_TYPED_STREAM_VERSION,
        "execution_path": RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH,
        **request,
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "device_resident_result_stream_proven": False,
            "true_zero_copy_claim_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "full_rtnn_paper_reproduction": False,
        },
    }


def run_rtnn_ranked_summary_typed_stream_preview(
    inputs: dict[str, Any],
    *,
    operation: str = "grouped_topk_f64",
    partner: str = "torch",
    k: int = 8,
    block_size: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Current alias for the legacy v2.8 ranked-summary typed-stream runner."""

    payload = run_rtnn_v2_8_ranked_summary_typed_stream_preview(
        inputs,
        operation=operation,
        partner=partner,
        k=k,
        block_size=block_size,
        dry_run=dry_run,
    )
    return {
        **payload,
        "legacy_helper_alias": "run_rtnn_v2_8_ranked_summary_typed_stream_preview",
        "current_helper": "run_rtnn_ranked_summary_typed_stream_preview",
    }


def run_app(
    mode: str = "scope",
    *,
    copies: int = 1,
    partner: str = "torch",
    operation: str = "grouped_topk_f64",
    k: int = 8,
) -> dict[str, Any]:
    if mode == "scope":
        return scope_payload()
    if mode == "ann_cpu_quality":
        return ann_cpu_quality_payload(copies=copies)
    if mode == "ann_partner_quality":
        return ann_partner_quality_payload(copies=copies, partner=partner)
    if mode == "rtnn_known_results":
        return rtnn_known_results_payload()
    if mode == "rtnn_command_plan":
        return rtnn_command_plan_payload()
    if mode == "ranked_summary_typed_stream_plan":
        return describe_rtnn_ranked_summary_typed_stream(operation=operation, partner=partner, k=k)
    if mode == "rtnn_v2_8_ranked_summary_plan":
        return describe_rtnn_v2_8_ranked_summary_typed_stream(operation=operation, partner=partner, k=k)
    raise ValueError(f"unsupported mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Formal RTNN benchmark front door with strict claim boundaries."
    )
    parser.add_argument(
        "--mode",
        choices=(
            "scope",
            "ann_cpu_quality",
            "ann_partner_quality",
            "rtnn_known_results",
            "rtnn_command_plan",
            "ranked_summary_typed_stream_plan",
            "rtnn_v2_8_ranked_summary_plan",
        ),
        default="scope",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--partner", choices=("torch", "cupy", "numba", "triton"), default="torch")
    parser.add_argument(
        "--operation",
        choices=("grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"),
        default="grouped_topk_f64",
    )
    parser.add_argument("--k", type=int, default=8)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(args.mode, copies=args.copies, partner=args.partner, operation=args.operation, k=args.k),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
