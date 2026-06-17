from __future__ import annotations

import argparse
import contextlib
import io
from argparse import Namespace
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.current.apps.ml import rtdl_ann_candidate_app as ann_app


BENCHMARK_NAME = "rtnn_neighbor_search"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2388_rtnn_fair_fight_pod"
RTNN_V2_8_RANKED_SUMMARY_TYPED_STREAM_VERSION = "rtdl.rtnn.v2_8.ranked_summary_typed_stream.v1"
RTNN_V2_8_RANKED_SUMMARY_EXECUTION_PATH = "generic_ranked_summary_typed_stream_partner_columns"


SUPPORTED_CONTRACTS = (
    {
        "name": "ann_candidate_quality_2d",
        "owner": "examples/current/apps/ml/rtdl_ann_candidate_app.py",
        "contract": "candidate-subset exact top-1 rerank compared with exact full-set top-1",
        "runtime_shape": "Python-selected candidate set plus RTDL or partner exact top-k rows",
    },
    {
        "name": "ann_candidate_threshold_2d",
        "owner": "examples/current/apps/ml/rtdl_ann_candidate_app.py",
        "contract": "prepared fixed-radius candidate-coverage threshold",
        "runtime_shape": "generic prepared 2-D fixed-radius threshold-reached count",
    },
    {
        "name": "rtnn_ranked_summary_3d",
        "owner": "scripts/goal2348_rtnn_v2_2_external_runner.py",
        "contract": "exact fixed-radius bounded ranked-neighbor summary row per query",
        "runtime_shape": "packed columns, prepared OptiX or Embree 3-D search structure, explicit query batches",
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


def _count_rtnn_csv_xyz_rows(path: Path) -> int:
    if not path.exists():
        raise FileNotFoundError(f"RTNN point file does not exist: {path}")
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if raw_line.strip():
                count += 1
    if count <= 0:
        raise ValueError("RTNN point file must contain at least one point row")
    return count


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


def ann_embree_quality_payload(*, copies: int) -> dict[str, Any]:
    payload = ann_app.run_app(
        "embree",
        copies=copies,
        output_mode="quality_summary",
    )
    inherited_optix_note = payload.pop("optix_performance", None)
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "ann_embree_quality",
        "contract": "Embree CPU candidate-subset exact top-1 rerank compared with exact full-set top-1",
        **payload,
        "rt_path_note": inherited_optix_note,
        "inherited_ann_optix_performance_note_present": inherited_optix_note is not None,
        "app": BENCHMARK_NAME,
        "uses_embree": True,
        "uses_numba": False,
        "rt_core_accelerated": False,
        "boundary": (
            "Embree CPU front door for the 2-D ANN candidate-quality contract. "
            "This removes the RTNN Embree-packet special case, but it is not the "
            "3-D RTNN ranked-summary path and not full RTNN paper reproduction."
        ),
        "claim_boundary": {
            "embree_cpu_compatibility_front_door": True,
            "native_engine_customization": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
        },
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


def rtnn_prepared_optix_ranked_summary_payload(
    *,
    point_count: int | None,
    radius: float,
    k: int,
    repeat: int,
    query_batch_size: int | None,
    distribution: str,
    seed: int,
    point_file: str | Path | None = None,
) -> dict[str, Any]:
    """Run the current prepared OptiX ranked-summary aggregate front door.

    This wraps the existing generic Goal2348 RTNN runner so benchmark users can
    execute the promoted RTDL/OptiX ranked-summary contract from this app
    directory instead of jumping to a historical goal script.
    """

    external_point_file = Path(point_file).resolve() if point_file is not None else None
    inferred_point_count = _count_rtnn_csv_xyz_rows(external_point_file) if external_point_file else None
    if point_count is None:
        point_count = inferred_point_count
    if point_count is None or point_count <= 0:
        raise ValueError("point_count must be positive")
    if inferred_point_count is not None and int(point_count) != inferred_point_count:
        raise ValueError("point_count must match the external RTNN point-file row count")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if k <= 0:
        raise ValueError("k must be positive")
    if repeat <= 0:
        raise ValueError("repeat must be positive")
    point_count = int(point_count)
    batch_size = query_batch_size or point_count
    if batch_size <= 0:
        raise ValueError("query_batch_size must be positive")
    point_fingerprint = (
        {
            "point_count": point_count,
            "source": "external_rtnn_csv_xyz",
            "path": str(external_point_file),
        }
        if external_point_file
        else {
            "point_count": point_count,
            "distribution": distribution,
            "seed": seed,
        }
    )
    query_fingerprint = {**point_fingerprint, "query_batch_size": batch_size}
    session_key = rt.make_prepared_session_cache_key(
        primitive="fixed_radius_neighbors_3d_ranked_summary",
        backend="optix",
        input_fingerprints={"points": point_fingerprint, "queries": query_fingerprint},
        parameters={"radius": radius, "k": k},
        partner="none",
        device="cuda:0",
    )
    session_policy = rt.RtdlPreparedSessionResidencyPolicy(
        cache_key=session_key,
        cache_enabled=False,
        lifetime_state="session_retained",
        reuse_scope="explicit_user_session",
        invalidation_events=("explicit_invalidate", "backend_context_reset", "close"),
    )

    from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner

    def run_payload_with_file(active_point_file: Path) -> dict[str, Any]:
        runner_stdout = io.StringIO()
        with contextlib.redirect_stdout(runner_stdout):
            runner_payload = rtnn_runner.run_rtdl_batched_3d_neighbors(
                Namespace(
                    point_file=active_point_file,
                    query_file=None,
                    radius=radius,
                    k_max=k,
                    backend="optix",
                    query_batch_size=batch_size,
                    result_mode="ranked-summary-aggregate-prepared-query-batch-float32",
                    aggregate_request_count=1,
                    aggregate_radius_multipliers=None,
                    aggregate_k_values=None,
                    repeat=repeat,
                    row_label="rtnn_current_prepared_optix_ranked_summary",
                )
            )
        return {
            "runner_payload": runner_payload,
            "runner_progress": tuple(line for line in runner_stdout.getvalue().splitlines() if line.strip()),
        }

    if external_point_file:
        generated = {
            "path": str(external_point_file),
            "point_count": point_count,
            "dimension": 3,
            "format": "rtnn_csv_xyz",
            "source": "external_point_file",
            "generated": False,
        }
        runner_result = run_payload_with_file(external_point_file)
    else:
        with tempfile.TemporaryDirectory(prefix="rtdl_rtnn_current_") as tmp:
            generated_point_file = Path(tmp) / f"rtnn_{distribution}_{point_count}.csv"
            generated = rtnn_runner.generate_point_file(
                generated_point_file,
                point_count=point_count,
                dimension=3,
                seed=seed,
                distribution=distribution,
            )
            runner_result = run_payload_with_file(generated_point_file)
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_optix_ranked_summary",
        "contract": "prepared 3-D fixed-radius bounded ranked-summary aggregate",
        "generated_input": generated,
        "point_count": point_count,
        "radius": radius,
        "k": k,
        "repeat": repeat,
        "query_batch_size": batch_size,
        "distribution": distribution,
        "seed": seed,
        "external_point_file_used": bool(external_point_file),
        "runner_progress": runner_result["runner_progress"],
        "runner_payload": runner_result["runner_payload"],
        "prepared_session_residency": {
            "cache_key": session_key.to_metadata(),
            "policy": session_policy.to_metadata(),
            "explicit_reuse_helper": "get_or_prepare_explicit_session",
            "cache_enabled_by_default": False,
            "cold_hot_phase_split_required": True,
            "prepare_once_query_many_pattern": True,
            "automatic_partner_selection_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "amd_performance_claim_authorized": False,
        },
    }


def rtnn_prepared_ranked_summary_raw_payload(
    *,
    backend: str,
    point_count: int,
    radius: float,
    k: int,
    repeat: int,
    query_batch_size: int | None,
    distribution: str,
    seed: int,
) -> dict[str, Any]:
    """Run the same raw ranked-summary row contract on OptiX or Embree."""

    if backend not in {"optix", "embree"}:
        raise ValueError("backend must be optix or embree")
    if point_count <= 0:
        raise ValueError("point_count must be positive")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if k <= 0:
        raise ValueError("k must be positive")
    if repeat <= 0:
        raise ValueError("repeat must be positive")
    batch_size = query_batch_size or point_count
    if batch_size <= 0:
        raise ValueError("query_batch_size must be positive")

    session_key = rt.make_prepared_session_cache_key(
        primitive="fixed_radius_neighbors_3d_ranked_summary_raw",
        backend=backend,
        input_fingerprints={
            "points": {
                "point_count": point_count,
                "distribution": distribution,
                "seed": seed,
            },
            "queries": {
                "query_batch_size": batch_size,
                "distribution": distribution,
                "seed": seed,
            },
        },
        parameters={"radius": radius, "k": k},
        partner="none",
        device="cuda:0" if backend == "optix" else "cpu",
    )
    session_policy = rt.RtdlPreparedSessionResidencyPolicy(
        cache_key=session_key,
        cache_enabled=False,
        lifetime_state="session_retained",
        reuse_scope="explicit_user_session",
        invalidation_events=("explicit_invalidate", "backend_context_reset", "close"),
    )

    from scripts import goal2348_rtnn_v2_2_external_runner as rtnn_runner

    with tempfile.TemporaryDirectory(prefix="rtdl_rtnn_same_contract_") as tmp:
        point_file = Path(tmp) / f"rtnn_{distribution}_{point_count}.csv"
        generated = rtnn_runner.generate_point_file(
            point_file,
            point_count=point_count,
            dimension=3,
            seed=seed,
            distribution=distribution,
        )
        runner_stdout = io.StringIO()
        with contextlib.redirect_stdout(runner_stdout):
            payload = rtnn_runner.run_rtdl_batched_3d_neighbors(
                Namespace(
                    point_file=point_file,
                    query_file=None,
                    radius=radius,
                    k_max=k,
                    backend=backend,
                    query_batch_size=batch_size,
                    result_mode="ranked-summary-raw",
                    aggregate_request_count=1,
                    aggregate_radius_multipliers=None,
                    aggregate_k_values=None,
                    repeat=repeat,
                    row_label=f"rtnn_current_prepared_{backend}_ranked_summary_raw",
                )
            )

    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_ranked_summary_raw",
        "backend": backend,
        "contract": "prepared 3-D fixed-radius bounded ranked-summary raw rows",
        "generated_input": generated,
        "point_count": point_count,
        "radius": radius,
        "k": k,
        "repeat": repeat,
        "query_batch_size": batch_size,
        "distribution": distribution,
        "seed": seed,
        "runner_progress": tuple(line for line in runner_stdout.getvalue().splitlines() if line.strip()),
        "runner_payload": payload,
        "same_contract_comparison_role": {
            "comparison_key": "rtnn_prepared_3d_ranked_summary_raw",
            "backend_variable": "optix_rt_core_or_embree_cpu",
            "fixed_inputs": (
                "point_count",
                "radius",
                "k",
                "repeat",
                "query_batch_size",
                "distribution",
                "seed",
                "result_mode",
            ),
            "row_signature_field": "runner_payload.raw_ranked_summary_aggregate",
        },
        "prepared_session_residency": {
            "cache_key": session_key.to_metadata(),
            "policy": session_policy.to_metadata(),
            "explicit_reuse_helper": "get_or_prepare_explicit_session",
            "cache_enabled_by_default": False,
            "cold_hot_phase_split_required": True,
            "prepare_once_query_many_pattern": True,
            "automatic_partner_selection_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "amd_performance_claim_authorized": False,
            "same_contract_backend_comparison_candidate": True,
            "materializes_summary_rows": True,
        },
    }


def rtnn_prepared_ranked_summary_graph_partner_bridge_payload(
    *,
    point_count: int,
    query_count: int | None = None,
    distribution: str,
    warmups: int,
    repeats: int,
    transfer_counter_library: str | Path | None = None,
    hardware: str = "unspecified",
) -> dict[str, Any]:
    """Run the V3 prepared ranked-summary graph bridge from the RTNN app.

    The underlying graph is app-agnostic: RTDL prepares an OptiX 3-D fixed-radius
    ranked-summary graph, keeps partial aggregates on device, and explicitly
    runs both CuPy and Numba same-stream partner reductions before materializing.
    """

    if point_count <= 0:
        raise ValueError("point_count must be positive")
    normalized_query_count = point_count if query_count is None else int(query_count)
    if normalized_query_count <= 0:
        raise ValueError("query_count must be positive")
    if normalized_query_count > point_count:
        raise ValueError("query_count must not exceed point_count")
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    library = transfer_counter_library or os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_LIBRARY")
    if not library:
        raise ValueError(
            "prepared_ranked_summary_graph_partner_bridge requires a transfer counter library; "
            "use --transfer-counter-library or set RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"
        )
    payload = rt.run_v3_m19_ranked_summary_bridge_case(
        transfer_counter_library=Path(library),
        point_count=point_count,
        query_count=normalized_query_count,
        distribution=distribution,
        warmups=warmups,
        repeats=repeats,
        hardware=hardware,
    )
    validation = rt.validate_v3_m19_ranked_summary_bridge_payload(payload)
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_ranked_summary_graph_partner_bridge",
        "contract": "prepared 3-D fixed-radius ranked-summary graph partials plus CuPy/Numba same-stream device reductions",
        "point_count": point_count,
        "query_count": normalized_query_count,
        "distribution": distribution,
        "warmups": warmups,
        "repeats": repeats,
        "uses_v3_m19_bridge": True,
        "runner_payload": payload,
        "validation": validation,
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "same_stream_partner_continuation_evidence": True,
        },
    }


def rtnn_prepared_ranked_summary_graph_partner_bridge_plan_payload(
    *,
    point_count: int,
    query_count: int | None = None,
    distribution: str,
) -> dict[str, Any]:
    """Return the explicit M19 partner-continuation chunk plan without running CUDA."""

    if point_count <= 0:
        raise ValueError("point_count must be positive")
    normalized_query_count = point_count if query_count is None else int(query_count)
    if normalized_query_count <= 0:
        raise ValueError("query_count must be positive")
    if normalized_query_count > point_count:
        raise ValueError("query_count must not exceed point_count")
    plan = rt.plan_v3_m19_ranked_summary_bridge_chunks(
        point_count=point_count,
        query_count=normalized_query_count,
        distribution=distribution,
    )
    validation = rt.validate_v3_m19_ranked_summary_bridge_chunk_plan(plan)
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_ranked_summary_graph_partner_bridge_plan",
        "contract": "dry-run explicit chunk plan for prepared ranked-summary graph partials plus same-stream partners",
        "point_count": point_count,
        "query_count": normalized_query_count,
        "distribution": distribution,
        "uses_v3_m19_bridge": True,
        "runtime_executed": False,
        "execution_path_plan": plan,
        "validation": validation,
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "aggregate_only_full_batch_direct_substitute_allowed": False,
            "large_chunk_runtime_evidence_required": bool(
                plan["large_chunk_runtime_evidence_required"]
            ),
        },
    }


def rtnn_prepared_ranked_summary_graph_partner_bridge_chunked_payload(
    *,
    point_count: int,
    query_count: int | None = None,
    distribution: str,
    warmups: int,
    repeats: int,
    transfer_counter_library: str | Path | None = None,
    hardware: str = "unspecified",
) -> dict[str, Any]:
    """Run the explicit M19 chunked same-stream partner-continuation route."""

    if point_count <= 0:
        raise ValueError("point_count must be positive")
    normalized_query_count = point_count if query_count is None else int(query_count)
    if normalized_query_count <= 0:
        raise ValueError("query_count must be positive")
    if normalized_query_count > point_count:
        raise ValueError("query_count must not exceed point_count")
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    library = transfer_counter_library or os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_LIBRARY")
    if not library:
        raise ValueError(
            "prepared_ranked_summary_graph_partner_bridge_chunked requires a transfer counter library; "
            "use --transfer-counter-library or set RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"
        )
    payload = rt.run_v3_m19_ranked_summary_bridge_chunked_case(
        transfer_counter_library=Path(library),
        point_count=point_count,
        query_count=normalized_query_count,
        distribution=distribution,
        warmups=warmups,
        repeats=repeats,
        hardware=hardware,
    )
    validation = rt.validate_v3_m19_ranked_summary_bridge_chunked_payload(payload)
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_ranked_summary_graph_partner_bridge_chunked",
        "contract": "prepared 3-D fixed-radius ranked-summary graph partials plus CuPy/Numba same-stream device reductions across explicit query chunks",
        "point_count": point_count,
        "query_count": normalized_query_count,
        "distribution": distribution,
        "warmups": warmups,
        "repeats": repeats,
        "uses_v3_m19_bridge": True,
        "runner_payload": payload,
        "validation": validation,
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "large_chunked_runtime_evidence": True,
            "same_stream_partner_continuation_evidence": True,
        },
    }


def rtnn_prepared_session_reuse_idiom_payload(
    *,
    point_count: int,
    radius: float,
    k: int,
    distribution: str,
    seed: int,
) -> dict[str, Any]:
    """Demonstrate the explicit prepared-session cache idiom without timing claims."""

    if point_count <= 0:
        raise ValueError("point_count must be positive")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if k <= 0:
        raise ValueError("k must be positive")

    session_key = rt.make_prepared_session_cache_key(
        primitive="fixed_radius_neighbors_3d_ranked_summary",
        backend="optix",
        input_fingerprints={
            "points": {
                "point_count": point_count,
                "distribution": distribution,
                "seed": seed,
            },
            "queries": {
                "query_batch_size": point_count,
                "distribution": distribution,
                "seed": seed,
            },
        },
        parameters={"radius": radius, "k": k},
        partner="none",
        device="cuda:0",
    )
    session_policy = rt.RtdlPreparedSessionResidencyPolicy(
        cache_key=session_key,
        cache_enabled=True,
        lifetime_state="session_retained",
        reuse_scope="explicit_user_session",
        invalidation_events=("explicit_invalidate", "backend_context_reset", "close"),
    )
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)
    prepare_calls: list[str] = []

    def prepare_session_descriptor() -> dict[str, Any]:
        prepare_calls.append("prepare")
        return {
            "primitive": session_key.primitive,
            "backend": session_key.backend,
            "partner": session_key.partner,
            "device": session_key.device,
            "point_count": point_count,
            "radius": radius,
            "k": k,
            "distribution": distribution,
            "seed": seed,
            "descriptor_only": True,
        }

    first = rt.get_or_prepare_explicit_session(
        cache,
        session_key,
        prepare_session_descriptor,
        policy=session_policy,
    )
    second = rt.get_or_prepare_explicit_session(
        cache,
        session_key,
        prepare_session_descriptor,
        policy=session_policy,
    )

    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "prepared_session_reuse_idiom",
        "contract": "explicit prepared-session cache miss/hit idiom for a generic ranked-neighbor primitive",
        "point_count": point_count,
        "radius": radius,
        "k": k,
        "distribution": distribution,
        "seed": seed,
        "live_helper_invoked": True,
        "native_runner_invoked": False,
        "performance_evidence": False,
        "prepared_call_count": len(prepare_calls),
        "cache_hit_sequence": (first.cache_hit, second.cache_hit),
        "cache_event_log": second.cache_event_log,
        "prepared_descriptor": second.value,
        "prepared_session_residency": {
            "cache_key": session_key.to_metadata(),
            "policy": session_policy.to_metadata(),
            "explicit_reuse_helper": "get_or_prepare_explicit_session",
            "explicit_cache_enabled_for_this_demo": True,
            "cache_enabled_by_default": False,
            "cold_hot_phase_split_required": True,
            "prepare_once_query_many_pattern": True,
            "automatic_partner_selection_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            **CLAIM_BOUNDARY,
            "native_engine_customization": False,
            "full_rtnn_paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "amd_performance_claim_authorized": False,
            "not_performance_evidence": True,
        },
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
    backend: str = "optix",
    operation: str = "grouped_topk_f64",
    k: int = 8,
    distribution: str = "uniform",
    warmups: int = 2,
    repeats: int = 5,
    query_count: int | None = None,
    transfer_counter_library: str | Path | None = None,
    hardware: str = "unspecified",
    point_file: str | Path | None = None,
) -> dict[str, Any]:
    if mode == "scope":
        return scope_payload()
    if mode == "ann_cpu_quality":
        return ann_cpu_quality_payload(copies=copies)
    if mode == "ann_partner_quality":
        return ann_partner_quality_payload(copies=copies, partner=partner)
    if mode == "ann_embree_quality":
        return ann_embree_quality_payload(copies=copies)
    if mode == "rtnn_known_results":
        return rtnn_known_results_payload()
    if mode == "rtnn_command_plan":
        return rtnn_command_plan_payload()
    if mode == "prepared_optix_ranked_summary":
        use_external_points = point_file is not None
        return rtnn_prepared_optix_ranked_summary_payload(
            point_count=None if use_external_points else copies,
            radius=0.02,
            k=k,
            repeat=1,
            query_batch_size=None if use_external_points else copies,
            distribution="uniform",
            seed=20260519,
            point_file=point_file,
        )
    if mode == "prepared_ranked_summary_raw":
        return rtnn_prepared_ranked_summary_raw_payload(
            backend=backend,
            point_count=copies,
            radius=0.02,
            k=k,
            repeat=1,
            query_batch_size=copies,
            distribution="uniform",
            seed=20260519,
        )
    if mode == "prepared_ranked_summary_graph_partner_bridge":
        return rtnn_prepared_ranked_summary_graph_partner_bridge_payload(
            point_count=copies,
            query_count=query_count,
            distribution=distribution,
            warmups=warmups,
            repeats=repeats,
            transfer_counter_library=transfer_counter_library,
            hardware=hardware,
        )
    if mode == "prepared_ranked_summary_graph_partner_bridge_plan":
        return rtnn_prepared_ranked_summary_graph_partner_bridge_plan_payload(
            point_count=copies,
            query_count=query_count,
            distribution=distribution,
        )
    if mode == "prepared_ranked_summary_graph_partner_bridge_chunked":
        return rtnn_prepared_ranked_summary_graph_partner_bridge_chunked_payload(
            point_count=copies,
            query_count=query_count,
            distribution=distribution,
            warmups=warmups,
            repeats=repeats,
            transfer_counter_library=transfer_counter_library,
            hardware=hardware,
        )
    if mode == "prepared_session_reuse_idiom":
        return rtnn_prepared_session_reuse_idiom_payload(
            point_count=copies,
            radius=0.02,
            k=k,
            distribution="uniform",
            seed=20260519,
        )
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
            "ann_embree_quality",
            "rtnn_known_results",
            "rtnn_command_plan",
            "prepared_optix_ranked_summary",
            "prepared_ranked_summary_raw",
            "prepared_ranked_summary_graph_partner_bridge",
            "prepared_ranked_summary_graph_partner_bridge_plan",
            "prepared_ranked_summary_graph_partner_bridge_chunked",
            "prepared_session_reuse_idiom",
            "ranked_summary_typed_stream_plan",
            "rtnn_v2_8_ranked_summary_plan",
        ),
        default="scope",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--point-count", type=int, default=None)
    parser.add_argument("--point-file", type=Path, default=None)
    parser.add_argument("--query-count", type=int, default=None)
    parser.add_argument("--radius", type=float, default=0.02)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--query-batch-size", type=int, default=None)
    parser.add_argument("--distribution", choices=("uniform", "clustered", "shell"), default="uniform")
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--backend", choices=("optix", "embree"), default="optix")
    parser.add_argument("--partner", choices=("torch", "cupy", "numba", "triton"), default="torch")
    parser.add_argument("--transfer-counter-library", type=Path, default=None)
    parser.add_argument("--hardware", default="unspecified")
    parser.add_argument(
        "--operation",
        choices=("grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"),
        default="grouped_topk_f64",
    )
    parser.add_argument("--k", type=int, default=8)
    args = parser.parse_args(argv)
    if args.mode == "prepared_optix_ranked_summary":
        point_count = args.point_count if args.point_count is not None else (None if args.point_file else args.copies)
        payload = rtnn_prepared_optix_ranked_summary_payload(
            point_count=point_count,
            radius=args.radius,
            k=args.k,
            repeat=args.repeat,
            query_batch_size=args.query_batch_size,
            distribution=args.distribution,
            seed=args.seed,
            point_file=args.point_file,
        )
    elif args.mode == "prepared_ranked_summary_raw":
        payload = rtnn_prepared_ranked_summary_raw_payload(
            backend=args.backend,
            point_count=args.point_count or args.copies,
            radius=args.radius,
            k=args.k,
            repeat=args.repeat,
            query_batch_size=args.query_batch_size,
            distribution=args.distribution,
            seed=args.seed,
        )
    elif args.mode == "prepared_ranked_summary_graph_partner_bridge":
        payload = rtnn_prepared_ranked_summary_graph_partner_bridge_payload(
            point_count=args.point_count or args.copies,
            query_count=args.query_count,
            distribution=args.distribution,
            warmups=args.warmups,
            repeats=args.repeat,
            transfer_counter_library=args.transfer_counter_library,
            hardware=args.hardware,
        )
    elif args.mode == "prepared_ranked_summary_graph_partner_bridge_plan":
        payload = rtnn_prepared_ranked_summary_graph_partner_bridge_plan_payload(
            point_count=args.point_count or args.copies,
            query_count=args.query_count,
            distribution=args.distribution,
        )
    elif args.mode == "prepared_ranked_summary_graph_partner_bridge_chunked":
        payload = rtnn_prepared_ranked_summary_graph_partner_bridge_chunked_payload(
            point_count=args.point_count or args.copies,
            query_count=args.query_count,
            distribution=args.distribution,
            warmups=args.warmups,
            repeats=args.repeat,
            transfer_counter_library=args.transfer_counter_library,
            hardware=args.hardware,
        )
    elif args.mode == "prepared_session_reuse_idiom":
        payload = rtnn_prepared_session_reuse_idiom_payload(
            point_count=args.point_count or args.copies,
            radius=args.radius,
            k=args.k,
            distribution=args.distribution,
            seed=args.seed,
        )
    else:
        payload = run_app(
            args.mode,
            copies=args.copies,
            partner=args.partner,
            backend=args.backend,
            operation=args.operation,
            k=args.k,
            distribution=args.distribution,
            warmups=args.warmups,
            repeats=args.repeat,
            query_count=args.query_count,
            transfer_counter_library=args.transfer_counter_library,
            hardware=args.hardware,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
