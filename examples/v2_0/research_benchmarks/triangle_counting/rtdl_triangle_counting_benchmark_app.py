from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.features.graph import rtdl_graph_triangle_count
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (
    build_rt_graph_triangle_contract,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import (
    build_rt_graph_triangle_summary_contract_cupy_binary,
)
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import fixture_edges
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import read_binary_edges
from examples.v2_0.research_benchmarks.triangle_counting.rt_graph_contract import read_text_edges
import rtdsl as rt


BENCHMARK_NAME = "triangle_counting"


@rt.kernel(backend="rtdl", precision="float_approx")
def _generic_ray_triangle_hit_count_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


CLAIM_BOUNDARY = {
    "benchmark_app": True,
    "paper_reproduction": False,
    "paper_code_intake_complete": True,
    "rt_graph_preprocessing_oracle": True,
    "rt_graph_id_ascending_adapter": True,
    "rt_graph_2a1_generic_rt_mapping": True,
    "rt_graph_1a2_generic_rt_mapping": True,
    "native_engine_customization": False,
    "bfs_in_benchmark": False,
    "visibility_edges_in_benchmark": False,
    "full_graph_database_claim": False,
    "distributed_graph_claim": False,
    "triangle_count_rt_core_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "public_speedup_claim_authorized": False,
}


def scope_payload() -> dict[str, Any]:
    return {
        "app": BENCHMARK_NAME,
        "status": "promoted_benchmark_with_boundary",
        "benchmark_kind": "single_contract_graph_benchmark",
        "paper_reference": {
            "title": (
                "A Case Study for Ray Tracing Cores: Performance Insights with "
                "Breadth-First Search and Triangle Counting in Graphs"
            ),
            "venue": "SIGMETRICS 2025",
            "code": "https://github.com/rubaolee/RT-Graph",
            "paper_pdf": "https://rubaolee.github.io/paper_pdfs/2025-rtgraph.pdf",
            "benchmark_scope": "triangle_counting_only",
            "reproduction_status": "contract_oracle_only",
        },
        "why_benchmark": (
            "Triangle counting is small enough to audit, has an unambiguous "
            "correctness contract, and stresses graph row/witness output plus "
            "compact summary continuation without mixing in BFS or visibility "
            "semantics."
        ),
        "supported_contracts": (
            {
                "name": "triangle_count",
                "contract": "triangle witness rows or compact triangle summary",
                "rt_role": "generic graph-row production and summary continuation where supported",
                "rt_graph_status": (
                    "benchmark-owned Python preprocessing/oracle exists; authors-code "
                    "pod reproduction and same-contract RTDL backend rows are pending"
                ),
            },
        ),
        "excluded_from_benchmark": (
            "BFS, visibility_edges, shortest path, graph database behavior, "
            "and distributed graph analytics remain learner/demo/example surfaces."
        ),
        "runtime_design_pressure": (
            "raw row views, compact row summaries, and clear separation between "
            "Python graph semantics and app-agnostic engine row contracts"
        ),
        "primary_reports": (
            "docs/reports/goal2586_graph_analytics_benchmark_promotion_2026-05-24.md",
            "docs/reports/goal2587_benchmark_apps_milestone_report_2026-05-24.md",
            "docs/reports/goal2588_rt_graph_triangle_counting_paper_code_intake_2026-05-24.md",
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_payload(*, backend: str, copies: int, output_mode: str, optix_graph_mode: str) -> dict[str, Any]:
    section = rtdl_graph_triangle_count.run_backend(
        backend,
        copies=copies,
        output_mode=output_mode,
        optix_graph_mode=optix_graph_mode,
    )
    return {
        "benchmark_app": BENCHMARK_NAME,
        "mode": "run",
        "contract": "triangle_count_only",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "triangle_count": section["summary"]["triangle_count"],
        "touched_vertex_count": section["summary"]["touched_vertex_count"],
        "section": section,
        "excluded_operations": ("bfs", "visibility_edges"),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def command_plan_payload() -> dict[str, Any]:
    return {
        "app": BENCHMARK_NAME,
        "mode": "command_plan",
        "local_correctness": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode run --backend cpu_python_reference --copies 2 --output-mode summary"
        ),
        "rt_graph_contract_oracle": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_contract --fixture degree_oriented_two_triangles"
        ),
        "rt_graph_rtdl_adapter_cpu": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_rtdl_adapter --fixture degree_oriented_two_triangles "
            "--backend cpu_python_reference"
        ),
        "rt_graph_2a1_generic_rt_cpu": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_2a1_generic_rt --fixture degree_oriented_two_triangles "
            "--backend cpu"
        ),
        "rt_graph_1a2_generic_rt_cpu": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_1a2_generic_rt --fixture degree_oriented_two_triangles "
            "--backend cpu"
        ),
        "rt_graph_2a1_generic_rt_optix": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_2a1_generic_rt --fixture degree_oriented_two_triangles "
            "--backend optix --detail summary"
        ),
        "rt_graph_2a1_generic_rt_optix_cupy_partner": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_2a1_generic_rt --edge-file graph.edge --edge-format binary "
            "--backend optix --detail summary --partner cupy"
        ),
        "rt_graph_1a2_generic_rt_optix": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_1a2_generic_rt --fixture degree_oriented_two_triangles "
            "--backend optix --detail summary"
        ),
        "rt_graph_1a2_generic_rt_optix_cupy_partner": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode rt_graph_1a2_generic_rt --edge-file graph.edge --edge-format binary "
            "--backend optix --detail summary --partner cupy"
        ),
        "embree_contract_check": (
            "PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/"
            "triangle_counting/rtdl_triangle_counting_benchmark_app.py "
            "--mode run --backend embree --copies 1000 --output-mode summary"
        ),
        "authors_code_env_probe": (
            "cd scratch/external/RT-Graph/tc && git rev-parse HEAD && "
            "nvidia-smi && /usr/local/cuda-12.8/bin/nvcc --version && "
            "test -n \"$OptiX_INSTALL_DIR\" && test -d \"$OptiX_INSTALL_DIR\""
        ),
        "authors_code_build": (
            "cd scratch/external/RT-Graph/tc && export PATH=/usr/local/cuda-12.8/bin:$PATH && "
            "cmake -B build -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.8/bin/nvcc "
            "-DBIN2C=/usr/local/cuda-12.8/bin/bin2c && cmake --build build -j"
        ),
        "authors_rt_tc_run_shape": (
            "cd scratch/external/RT-Graph/tc && ./bin/rt_tc "
            "dataset/com-dblp/com-dblp.ungraph.edge.pd 0"
        ),
        "authors_bs_tc_run_shape": (
            "cd scratch/external/RT-Graph/tc && ./bin/bs_tc "
            "dataset/com-dblp/com-dblp.ungraph.edge.pd 0"
        ),
        "future_harder_gate": (
            "Before any performance wording, reproduce the RT-Graph triangle-counting "
            "authors-code contract where possible, then compare same-input RTDL "
            "triangle-counting outputs against RT-Graph bs_tc and rt_tc baselines."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rt_graph_contract_payload(
    *,
    fixture: str,
    edge_file: str | None,
    edge_format: str,
    detail: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    edges, input_source = _load_rt_graph_edges(
        fixture=fixture,
        edge_file=edge_file,
        edge_format=edge_format,
    )
    loaded = time.perf_counter()
    contract = build_rt_graph_triangle_contract(edges)
    built = time.perf_counter()
    return {
        "app": BENCHMARK_NAME,
        "mode": "rt_graph_contract",
        "input_source": input_source,
        "contract": "rt_graph_style_degree_oriented_triangle_count",
        "status": "python_preprocessing_oracle_only",
        "authors_code_reproduction": False,
        "same_contract_rtdl_backend_rows": False,
        "rtdl_feature_gap": (
            "RT-Graph orients edges by degree/id. The benchmark now has an "
            "id-ascending relabeling adapter for RTDL's current triangle_match "
            "contract, but native same-contract timing is still pending."
        ),
        "timing_ms": {
            "load_edges": _elapsed_ms(started, loaded),
            "build_contract": _elapsed_ms(loaded, built),
            "total": _elapsed_ms(started, built),
        },
        "rt_graph_contract": _contract_payload(contract, detail=detail),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rt_graph_rtdl_adapter_payload(
    *,
    fixture: str,
    edge_file: str | None,
    edge_format: str,
    backend: str,
    detail: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    edges, input_source = _load_rt_graph_edges(
        fixture=fixture,
        edge_file=edge_file,
        edge_format=edge_format,
    )
    loaded = time.perf_counter()
    contract = build_rt_graph_triangle_contract(edges)
    built = time.perf_counter()
    graph = rt.csr_graph(
        row_offsets=contract.id_ascending_row_offsets,
        column_indices=contract.id_ascending_column_indices,
    )
    seeds = tuple(contract.id_ascending_edges)
    inputs = {"seeds": seeds, "graph": graph}
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(rtdl_graph_triangle_count.triangle_probe_kernel, **inputs)
    elif backend == "cpu":
        rows = rt.run_cpu(rtdl_graph_triangle_count.triangle_probe_kernel, **inputs)
    else:
        raise ValueError("rt_graph_rtdl_adapter currently supports backend cpu_python_reference or cpu")
    ran = time.perf_counter()
    summary = rt.summarize_triangle_rows(rows)
    reduced = time.perf_counter()
    return {
        "app": BENCHMARK_NAME,
        "mode": "rt_graph_rtdl_adapter",
        "input_source": input_source,
        "backend": backend,
        "contract": "rt_graph_contract_via_id_ascending_adapter",
        "authors_code_reproduction": False,
        "same_contract_native_timing": False,
        "oracle_triangle_count": contract.triangle_count,
        "rtdl_triangle_count": summary["triangle_count"],
        "triangle_count_matches_oracle": summary["triangle_count"] == contract.triangle_count,
        "timing_ms": {
            "load_edges": _elapsed_ms(started, loaded),
            "build_contract": _elapsed_ms(loaded, built),
            "run_backend": _elapsed_ms(built, ran),
            "reduce_rows": _elapsed_ms(ran, reduced),
            "total": _elapsed_ms(started, reduced),
        },
        "rtdl_rows": rows if detail == "full" else {"row_count": len(rows)},
        "rt_graph_contract": _contract_payload(contract, detail=detail),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rt_graph_2a1_generic_rt_payload(
    *,
    fixture: str,
    edge_file: str | None,
    edge_format: str,
    backend: str,
    detail: str,
    partner: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    use_cupy_summary = _use_cupy_summary_partner(
        partner=partner,
        backend=backend,
        detail=detail,
        edge_file=edge_file,
        edge_format=edge_format,
    )
    if use_cupy_summary:
        edges = None
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
    else:
        edges, input_source = _load_rt_graph_edges(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
        )
    loaded = time.perf_counter()
    if use_cupy_summary:
        contract = build_rt_graph_triangle_summary_contract_cupy_binary(edge_file)
    else:
        contract = build_rt_graph_triangle_contract(edges, include_id_ascending_adapter=detail == "full")
    built = time.perf_counter()
    normalized_backend = backend.lower().replace("-", "_")
    device_column_summary = use_cupy_summary and normalized_backend == "optix" and detail == "summary"
    if device_column_summary:
        triangles, rays, ray_weights = _build_rt_graph_2a1_device_geometry(contract)
    elif normalized_backend == "optix" and detail == "summary":
        triangles, rays, ray_weights = _build_rt_graph_2a1_packed_geometry(contract)
    else:
        triangles, rays, ray_weights = _build_rt_graph_2a1_geometry(contract)
    lowered = time.perf_counter()
    summary_result = None
    if device_column_summary:
        summary_result = _run_optix_ray_triangle_any_hit_weighted_sum_3d_device_columns(rays, triangles, ray_weights)
        rows = None
        hit_weight_sum = int(summary_result["weighted_hit_sum"])
    elif normalized_backend == "optix" and detail == "summary":
        summary_result = _run_optix_ray_triangle_any_hit_weighted_sum_3d(rays, triangles, ray_weights)
        rows = None
        hit_weight_sum = int(summary_result["weighted_hit_sum"])
    else:
        rows = rt.run_generic_ray_triangle_any_hit(rays, triangles, backend=backend)
        hit_weight_sum = sum(ray_weights[int(row["ray_id"])] for row in rows if int(row["any_hit"]))
    ran = time.perf_counter()
    reduced = time.perf_counter()
    return {
        "app": BENCHMARK_NAME,
        "mode": "rt_graph_2a1_generic_rt",
        "input_source": input_source,
        "backend": backend,
        "contract": "rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit",
        "authors_code_reproduction": False,
        "same_contract_native_timing": backend in {"embree", "optix"},
        "partner": partner,
        "partner_summary_contract_used": use_cupy_summary,
        "partner_timing_ms": getattr(contract, "partner_timing_ms", None),
        "primitive_layout": {
            "paper_method": "RT-2A1",
            "primitive_side": "directed 1-hop edges as Triangle3D primitives",
            "ray_side": "compacted 2-hop relations as Ray3D probes with add-value weights",
            "axis_offset": [contract.vertex_count / 2.0, 0.0, contract.vertex_count / 2.0],
            "triangle_eps": 0.2,
            "ray_tmax": 0.2,
            "device_column_lowering": device_column_summary,
        },
        "primitive_count": _record_count(triangles),
        "ray_count": _record_count(rays),
        "oracle_triangle_count": contract.triangle_count,
        "generic_rt_weighted_triangle_count": int(hit_weight_sum),
        "triangle_count_matches_oracle": int(hit_weight_sum) == contract.triangle_count,
        "timing_ms": {
            "load_edges": _elapsed_ms(started, loaded),
            "build_contract": _elapsed_ms(loaded, built),
            "build_geometry": _elapsed_ms(built, lowered),
            "run_backend": _elapsed_ms(lowered, ran),
            "reduce_hits": _elapsed_ms(ran, reduced),
            "total": _elapsed_ms(started, reduced),
        },
        "hit_rows": (
            rows
            if detail == "full"
            else {
                "row_count": _record_count(rays) if rows is None else len(rows),
                "materialized": rows is not None,
                "summary_primitive": None if summary_result is None else summary_result["contract"],
            }
        ),
        "ray_weights": _ray_weight_payload(ray_weights, detail=detail),
        "generic_rt_summary": summary_result,
        "rt_graph_contract": _contract_payload(contract, detail=detail),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def rt_graph_1a2_generic_rt_payload(
    *,
    fixture: str,
    edge_file: str | None,
    edge_format: str,
    backend: str,
    detail: str,
    partner: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    use_cupy_summary = _use_cupy_summary_partner(
        partner=partner,
        backend=backend,
        detail=detail,
        edge_file=edge_file,
        edge_format=edge_format,
    )
    if use_cupy_summary:
        edges = None
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
    else:
        edges, input_source = _load_rt_graph_edges(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
        )
    loaded = time.perf_counter()
    if use_cupy_summary:
        contract = build_rt_graph_triangle_summary_contract_cupy_binary(edge_file)
    else:
        contract = build_rt_graph_triangle_contract(edges, include_id_ascending_adapter=detail == "full")
    built = time.perf_counter()
    normalized_backend = backend.lower().replace("-", "_")
    device_column_summary = use_cupy_summary and normalized_backend == "optix" and detail == "summary"
    if device_column_summary:
        triangles, rays = _build_rt_graph_1a2_device_geometry(contract)
    elif normalized_backend == "optix" and detail == "summary":
        triangles, rays = _build_rt_graph_1a2_packed_geometry(contract)
    else:
        triangles, rays = _build_rt_graph_1a2_geometry(contract)
    lowered = time.perf_counter()
    summary_result = None
    if device_column_summary:
        summary_result = _run_optix_ray_triangle_hit_count_sum_3d_device_columns(rays, triangles)
        rows = None
        hit_count_sum = int(summary_result["hit_count_sum"])
    elif normalized_backend == "optix" and detail == "summary":
        summary_result = _run_optix_ray_triangle_hit_count_sum_3d(rays, triangles)
        rows = None
        hit_count_sum = int(summary_result["hit_count_sum"])
    else:
        rows = _run_ray_triangle_hit_count_3d(rays, triangles, backend=backend)
        hit_count_sum = sum(int(row["hit_count"]) for row in rows)
    ran = time.perf_counter()
    reduced = time.perf_counter()
    max_adj_len = _max_out_degree(contract)
    return {
        "app": BENCHMARK_NAME,
        "mode": "rt_graph_1a2_generic_rt",
        "input_source": input_source,
        "backend": backend,
        "contract": "rt_graph_1a2_mapped_to_generic_ray_triangle_hit_count",
        "authors_code_reproduction": False,
        "same_contract_native_timing": backend in {"embree", "optix"},
        "partner": partner,
        "partner_summary_contract_used": use_cupy_summary,
        "partner_timing_ms": getattr(contract, "partner_timing_ms", None),
        "primitive_layout": {
            "paper_method": "RT-1A2",
            "primitive_side": "2-hop relations as Triangle3D primitives",
            "ray_side": "directed 1-hop edges as Ray3D probes",
            "axis_offset": [max_adj_len / 2.0, contract.vertex_count / 2.0, contract.vertex_count / 2.0],
            "triangle_eps": 0.2,
            "device_column_lowering": device_column_summary,
        },
        "primitive_count": _record_count(triangles),
        "ray_count": _record_count(rays),
        "oracle_triangle_count": contract.triangle_count,
        "generic_rt_triangle_count": int(hit_count_sum),
        "triangle_count_matches_oracle": int(hit_count_sum) == contract.triangle_count,
        "timing_ms": {
            "load_edges": _elapsed_ms(started, loaded),
            "build_contract": _elapsed_ms(loaded, built),
            "build_geometry": _elapsed_ms(built, lowered),
            "run_backend": _elapsed_ms(lowered, ran),
            "reduce_hits": _elapsed_ms(ran, reduced),
            "total": _elapsed_ms(started, reduced),
        },
        "hit_count_rows": (
            rows
            if detail == "full"
            else {
                "row_count": _record_count(rays) if rows is None else len(rows),
                "materialized": rows is not None,
                "summary_primitive": None if summary_result is None else summary_result["contract"],
            }
        ),
        "generic_rt_summary": summary_result,
        "rt_graph_contract": _contract_payload(contract, detail=detail),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _run_optix_ray_triangle_any_hit_weighted_sum_3d(
    rays: tuple[rt.Ray3D, ...],
    triangles: tuple[rt.Triangle3D, ...],
    ray_weights: tuple[int, ...],
) -> dict[str, object]:
    with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
        return scene.ray_any_hit_weighted_sum(rays, ray_weights)


def _run_optix_ray_triangle_any_hit_weighted_sum_3d_device_columns(
    ray_columns: dict[str, object],
    triangle_columns: dict[str, object],
    ray_weights,
) -> dict[str, object]:
    with rt.prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns) as scene:
        return scene.ray_any_hit_weighted_sum_device_columns(ray_columns, ray_weights)


def _run_optix_ray_triangle_hit_count_sum_3d(
    rays: tuple[rt.Ray3D, ...],
    triangles: tuple[rt.Triangle3D, ...],
) -> dict[str, object]:
    with rt.prepare_optix_static_triangle_scene_3d(triangles) as scene:
        return scene.ray_hit_count_sum(rays)


def _run_optix_ray_triangle_hit_count_sum_3d_device_columns(
    ray_columns: dict[str, object],
    triangle_columns: dict[str, object],
) -> dict[str, object]:
    with rt.prepare_optix_static_triangle_scene_3d_device_triangles(triangle_columns) as scene:
        return scene.ray_hit_count_sum_device_columns(ray_columns)


def _run_ray_triangle_hit_count_3d(
    rays: tuple[rt.Ray3D, ...],
    triangles: tuple[rt.Triangle3D, ...],
    *,
    backend: str,
) -> tuple[dict[str, int], ...]:
    normalized = backend.lower().replace("-", "_")
    if normalized in {"cpu_python_reference", "cpu"}:
        return tuple(
            {"ray_id": int(row["ray_id"]), "hit_count": int(row["hit_count"])}
            for row in rt.ray_triangle_hit_count_cpu(rays, triangles)
        )
    if normalized == "embree":
        rows = rt.run_embree(_generic_ray_triangle_hit_count_3d_kernel, rays=rays, triangles=triangles)
    elif normalized == "optix":
        rows = rt.run_optix(_generic_ray_triangle_hit_count_3d_kernel, rays=rays, triangles=triangles)
    else:
        raise ValueError("rt_graph_1a2_generic_rt backend must be one of: cpu_python_reference, cpu, embree, optix")
    return tuple({"ray_id": int(row["ray_id"]), "hit_count": int(row["hit_count"])} for row in rows)


def _contract_payload(contract, *, detail: str) -> dict[str, object]:
    if detail == "full":
        return contract.to_payload()
    return {
        "original_edge_count": _contract_count(contract, "original_edge_count", "original_edges"),
        "compacted_vertex_count": _contract_count(contract, "compacted_vertex_count", "compacted_vertex_ids"),
        "directed_vertex_count": contract.vertex_count,
        "directed_edge_count": contract.directed_edge_count,
        "triangle_count": contract.triangle_count,
        "two_hop_ray_count_2a1": len(contract.two_hop_rays_2a1),
        "duplicate_two_hop_relation_count": contract.duplicate_two_hop_relation_count,
        "id_ascending_adapter_materialized": contract.id_ascending_adapter_materialized,
        "id_ascending_edge_count": len(contract.id_ascending_edges),
        "id_ascending_triangle_count": len(contract.id_ascending_triangle_witnesses),
        "removed_low_degree_vertex_count": contract.removed_low_degree_vertex_count,
        "removed_low_degree_edge_count": contract.removed_low_degree_edge_count,
        "removed_duplicate_or_self_edge_count": contract.removed_duplicate_or_self_edge_count,
        "partner": getattr(contract, "partner", "python"),
        "partner_timing_ms": getattr(contract, "partner_timing_ms", None),
    }


def _elapsed_ms(started: float, ended: float) -> float:
    return (ended - started) * 1000.0


def _record_count(records) -> int:
    if isinstance(records, dict) and "ids" in records:
        return int(records["ids"].size)
    count = getattr(records, "count", None)
    if count is not None and not callable(count):
        return int(count)
    return len(records)


def _contract_count(contract, count_attr: str, records_attr: str) -> int:
    if hasattr(contract, count_attr):
        return int(getattr(contract, count_attr))
    return len(getattr(contract, records_attr))


def _use_cupy_summary_partner(
    *,
    partner: str,
    backend: str,
    detail: str,
    edge_file: str | None,
    edge_format: str,
) -> bool:
    if partner == "none":
        return False
    if partner != "cupy":
        raise ValueError(f"unsupported partner: {partner}")
    normalized_backend = backend.lower().replace("-", "_")
    if normalized_backend != "optix" or detail != "summary":
        raise ValueError("--partner cupy currently supports only --backend optix --detail summary")
    if edge_file is None or edge_format != "binary":
        raise ValueError("--partner cupy currently requires --edge-file with --edge-format binary")
    return True


def _require_cupy_device_arrays(contract) -> dict[str, object]:
    device_arrays = getattr(contract, "device_arrays", None)
    if not isinstance(device_arrays, dict):
        raise ValueError("CuPy summary contract is missing partner-resident device arrays")
    required = {
        "row_offsets",
        "column_indices",
        "directed_src",
        "two_hop_src",
        "two_hop_dst",
        "two_hop_weights",
    }
    missing = sorted(required - set(device_arrays))
    if missing:
        raise ValueError(f"CuPy summary contract missing device arrays: {', '.join(missing)}")
    return device_arrays


def _build_rt_graph_1a2_device_geometry(contract):
    cp = __import__("cupy")

    device_arrays = _require_cupy_device_arrays(contract)
    row_offsets = device_arrays["row_offsets"]
    column_indices = device_arrays["column_indices"]
    out_degrees = row_offsets[1:] - row_offsets[:-1]
    max_adj_len = int(out_degrees.max().get()) if int(out_degrees.size) else 0
    axis_offset_x = max_adj_len / 2.0
    axis_offset_y = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2

    edge_count = int(column_indices.size)
    if edge_count:
        edge_src = cp.repeat(cp.arange(contract.vertex_count, dtype=cp.int64), out_degrees)
        edge_starts = cp.repeat(row_offsets[:-1], out_degrees)
        edge_local_index = cp.arange(edge_count, dtype=cp.int64) - edge_starts
        edge_mid = column_indices
        two_hop_counts = out_degrees[edge_mid]
        nonempty = two_hop_counts > 0
        active_counts = two_hop_counts[nonempty]
        primitive_count = int(active_counts.sum().get()) if int(active_counts.size) else 0
        if primitive_count:
            center_x = cp.repeat(edge_local_index[nonempty], active_counts).astype(cp.float64) - axis_offset_x
            center_y = cp.repeat(edge_src[nonempty], active_counts).astype(cp.float64) - axis_offset_y
            starts = row_offsets[edge_mid[nonempty]]
            repeated_starts = cp.repeat(starts, active_counts)
            repeated_prefix = cp.repeat(cp.cumsum(active_counts) - active_counts, active_counts)
            dst_index = repeated_starts + (cp.arange(primitive_count, dtype=cp.int64) - repeated_prefix)
            center_z = column_indices[dst_index].astype(cp.float64) - axis_offset_z
        else:
            center_x = cp.empty(0, dtype=cp.float64)
            center_y = cp.empty(0, dtype=cp.float64)
            center_z = cp.empty(0, dtype=cp.float64)
    else:
        primitive_count = 0
        center_x = cp.empty(0, dtype=cp.float64)
        center_y = cp.empty(0, dtype=cp.float64)
        center_z = cp.empty(0, dtype=cp.float64)

    triangles = {
        "ids": cp.arange(primitive_count, dtype=cp.uint32),
        "x0": center_x,
        "y0": center_y,
        "z0": center_z + eps,
        "x1": center_x,
        "y1": center_y - eps,
        "z1": center_z - eps,
        "x2": center_x,
        "y2": center_y + eps,
        "z2": center_z - eps,
    }

    ray_count = int(column_indices.size)
    if ray_count:
        ray_src = device_arrays["directed_src"]
        ray_dst = column_indices
        tmax = out_degrees[ray_src].astype(cp.float64)
        oy = ray_src.astype(cp.float64) - axis_offset_y
        oz = ray_dst.astype(cp.float64) - axis_offset_z
    else:
        tmax = cp.empty(0, dtype=cp.float64)
        oy = cp.empty(0, dtype=cp.float64)
        oz = cp.empty(0, dtype=cp.float64)
    rays = {
        "ids": cp.arange(ray_count, dtype=cp.uint32),
        "ox": cp.full(ray_count, -0.5 - axis_offset_x, dtype=cp.float64),
        "oy": oy,
        "oz": oz,
        "dx": cp.ones(ray_count, dtype=cp.float64),
        "dy": cp.zeros(ray_count, dtype=cp.float64),
        "dz": cp.zeros(ray_count, dtype=cp.float64),
        "tmax": tmax,
    }
    return triangles, rays


def _build_rt_graph_1a2_geometry(contract) -> tuple[tuple[rt.Triangle3D, ...], tuple[rt.Ray3D, ...]]:
    max_adj_len = _max_out_degree(contract)
    axis_offset_x = max_adj_len / 2.0
    axis_offset_y = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2
    triangles: list[rt.Triangle3D] = []
    primitive_id = 0
    for src in range(contract.vertex_count):
        neighbors = _contract_neighbors(contract, src)
        for local_index, mid in enumerate(neighbors):
            for dst in _contract_neighbors(contract, mid):
                center_x = float(local_index) - axis_offset_x
                center_y = float(src) - axis_offset_y
                center_z = float(dst) - axis_offset_z
                triangles.append(
                    rt.Triangle3D(
                        id=primitive_id,
                        x0=center_x,
                        y0=center_y,
                        z0=center_z + eps,
                        x1=center_x,
                        y1=center_y - eps,
                        z1=center_z - eps,
                        x2=center_x,
                        y2=center_y + eps,
                        z2=center_z - eps,
                    )
                )
                primitive_id += 1

    rays: list[rt.Ray3D] = []
    for ray_id, (src, dst) in enumerate(contract.directed_edges):
        rays.append(
            rt.Ray3D(
                id=ray_id,
                ox=-0.5 - axis_offset_x,
                oy=float(src) - axis_offset_y,
                oz=float(dst) - axis_offset_z,
                dx=1.0,
                dy=0.0,
                dz=0.0,
                tmax=float(len(_contract_neighbors(contract, src))),
            )
        )
    return tuple(triangles), tuple(rays)


def _build_rt_graph_1a2_packed_geometry(contract):
    import numpy as np

    row_offsets = np.asarray(contract.row_offsets, dtype=np.int64)
    column_indices = np.asarray(contract.column_indices, dtype=np.int64)
    out_degrees = np.diff(row_offsets)
    max_adj_len = int(out_degrees.max()) if out_degrees.size else 0
    axis_offset_x = max_adj_len / 2.0
    axis_offset_y = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2

    edge_count = len(column_indices)
    if edge_count:
        edge_src = np.repeat(np.arange(contract.vertex_count, dtype=np.int64), out_degrees)
        edge_starts = np.repeat(row_offsets[:-1], out_degrees)
        edge_local_index = np.arange(edge_count, dtype=np.int64) - edge_starts
        edge_mid = column_indices
        two_hop_counts = out_degrees[edge_mid]
        nonempty = two_hop_counts > 0
        two_hop_counts = two_hop_counts[nonempty]
        if two_hop_counts.size:
            primitive_count = int(two_hop_counts.sum())
            center_x = np.repeat(edge_local_index[nonempty], two_hop_counts).astype(np.float64) - axis_offset_x
            center_y = np.repeat(edge_src[nonempty], two_hop_counts).astype(np.float64) - axis_offset_y
            starts = row_offsets[edge_mid[nonempty]]
            repeated_starts = np.repeat(starts, two_hop_counts)
            repeated_prefix = np.repeat(np.cumsum(two_hop_counts) - two_hop_counts, two_hop_counts)
            dst_index = repeated_starts + (np.arange(primitive_count, dtype=np.int64) - repeated_prefix)
            center_z = column_indices[dst_index].astype(np.float64) - axis_offset_z
        else:
            primitive_count = 0
            center_x = np.empty(0, dtype=np.float64)
            center_y = np.empty(0, dtype=np.float64)
            center_z = np.empty(0, dtype=np.float64)
    else:
        primitive_count = 0
        center_x = np.empty(0, dtype=np.float64)
        center_y = np.empty(0, dtype=np.float64)
        center_z = np.empty(0, dtype=np.float64)

    triangles = rt.pack_triangles_3d_from_arrays(
        ids=np.arange(primitive_count, dtype=np.uint32),
        x0=center_x,
        y0=center_y,
        z0=center_z + eps,
        x1=center_x,
        y1=center_y - eps,
        z1=center_z - eps,
        x2=center_x,
        y2=center_y + eps,
        z2=center_z - eps,
    )

    edge_count = len(contract.directed_edges)
    ray_ids = np.arange(edge_count, dtype=np.uint32)
    if edge_count:
        edges = np.asarray(contract.directed_edges, dtype=np.int64)
        src_i = edges[:, 0]
        dst_i = edges[:, 1]
        tmax = out_degrees[src_i].astype(np.float64)
        src = src_i.astype(np.float64)
        dst = dst_i.astype(np.float64)
        oy = src - axis_offset_y
        oz = dst - axis_offset_z
    else:
        oy = np.empty(0, dtype=np.float64)
        oz = np.empty(0, dtype=np.float64)
        tmax = np.empty(0, dtype=np.float64)
    rays = rt.pack_rays_3d_from_arrays(
        ids=ray_ids,
        ox=np.full(edge_count, -0.5 - axis_offset_x, dtype=np.float64),
        oy=oy,
        oz=oz,
        dx=np.ones(edge_count, dtype=np.float64),
        dy=np.zeros(edge_count, dtype=np.float64),
        dz=np.zeros(edge_count, dtype=np.float64),
        tmax=tmax,
    )
    return triangles, rays


def _build_rt_graph_2a1_device_geometry(contract):
    cp = __import__("cupy")

    device_arrays = _require_cupy_device_arrays(contract)
    directed_src = device_arrays["directed_src"]
    directed_dst = device_arrays["column_indices"]
    axis_offset_x = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2

    edge_count = int(directed_dst.size)
    if edge_count:
        center_x = directed_src.astype(cp.float64) - axis_offset_x
        center_z = directed_dst.astype(cp.float64) - axis_offset_z
    else:
        center_x = cp.empty(0, dtype=cp.float64)
        center_z = cp.empty(0, dtype=cp.float64)
    zero = cp.zeros(edge_count, dtype=cp.float64)
    triangles = {
        "ids": cp.arange(edge_count, dtype=cp.uint32),
        "x0": center_x,
        "y0": zero,
        "z0": center_z + eps,
        "x1": center_x - eps,
        "y1": zero,
        "z1": center_z - eps,
        "x2": center_x + eps,
        "y2": zero,
        "z2": center_z - eps,
    }

    ray_src = device_arrays["two_hop_src"]
    ray_dst = device_arrays["two_hop_dst"]
    ray_count = int(ray_src.size)
    if ray_count:
        ox = ray_src.astype(cp.float64) - axis_offset_x
        oz = ray_dst.astype(cp.float64) - axis_offset_z
    else:
        ox = cp.empty(0, dtype=cp.float64)
        oz = cp.empty(0, dtype=cp.float64)
    rays = {
        "ids": cp.arange(ray_count, dtype=cp.uint32),
        "ox": ox,
        "oy": cp.full(ray_count, -0.1, dtype=cp.float64),
        "oz": oz,
        "dx": cp.zeros(ray_count, dtype=cp.float64),
        "dy": cp.ones(ray_count, dtype=cp.float64),
        "dz": cp.zeros(ray_count, dtype=cp.float64),
        "tmax": cp.full(ray_count, 0.2, dtype=cp.float64),
    }
    ray_weights = device_arrays["two_hop_weights"].astype(cp.uint64, copy=False)
    return triangles, rays, ray_weights


def _build_rt_graph_2a1_geometry(contract) -> tuple[tuple[rt.Triangle3D, ...], tuple[rt.Ray3D, ...], tuple[int, ...]]:
    axis_offset_x = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2
    triangles: list[rt.Triangle3D] = []
    for primitive_id, (src, dst) in enumerate(contract.directed_edges):
        center_x = float(src) - axis_offset_x
        center_y = 0.0
        center_z = float(dst) - axis_offset_z
        triangles.append(
            rt.Triangle3D(
                id=primitive_id,
                x0=center_x,
                y0=center_y,
                z0=center_z + eps,
                x1=center_x - eps,
                y1=center_y,
                z1=center_z - eps,
                x2=center_x + eps,
                y2=center_y,
                z2=center_z - eps,
            )
        )

    rays: list[rt.Ray3D] = []
    ray_weights: list[int] = []
    for ray_id, (src, dst, weight) in enumerate(contract.two_hop_rays_2a1):
        rays.append(
            rt.Ray3D(
                id=ray_id,
                ox=float(src) - axis_offset_x,
                oy=-0.1,
                oz=float(dst) - axis_offset_z,
                dx=0.0,
                dy=1.0,
                dz=0.0,
                tmax=0.2,
            )
        )
        ray_weights.append(int(weight))
    return tuple(triangles), tuple(rays), tuple(ray_weights)


def _build_rt_graph_2a1_packed_geometry(contract):
    import numpy as np

    axis_offset_x = contract.vertex_count / 2.0
    axis_offset_z = contract.vertex_count / 2.0
    eps = 0.2

    edge_count = len(contract.directed_edges)
    primitive_ids = np.arange(edge_count, dtype=np.uint32)
    if edge_count:
        edges = np.asarray(contract.directed_edges, dtype=np.int64)
        src = edges[:, 0].astype(np.float64)
        dst = edges[:, 1].astype(np.float64)
        center_x = src - axis_offset_x
        center_z = dst - axis_offset_z
    else:
        center_x = np.empty(0, dtype=np.float64)
        center_z = np.empty(0, dtype=np.float64)
    zero = np.zeros(edge_count, dtype=np.float64)
    triangles = rt.pack_triangles_3d_from_arrays(
        ids=primitive_ids,
        x0=center_x,
        y0=zero,
        z0=center_z + eps,
        x1=center_x - eps,
        y1=zero,
        z1=center_z - eps,
        x2=center_x + eps,
        y2=zero,
        z2=center_z - eps,
    )

    ray_count = len(contract.two_hop_rays_2a1)
    ray_ids = np.arange(ray_count, dtype=np.uint32)
    if ray_count:
        two_hop = np.asarray(contract.two_hop_rays_2a1, dtype=np.int64)
        ray_src = two_hop[:, 0].astype(np.float64)
        ray_dst = two_hop[:, 1].astype(np.float64)
        ray_weights = np.ascontiguousarray(two_hop[:, 2], dtype=np.uint64)
        ox = ray_src - axis_offset_x
        oz = ray_dst - axis_offset_z
    else:
        ray_weights = np.empty(0, dtype=np.uint64)
        ox = np.empty(0, dtype=np.float64)
        oz = np.empty(0, dtype=np.float64)
    rays = rt.pack_rays_3d_from_arrays(
        ids=ray_ids,
        ox=ox,
        oy=np.full(ray_count, -0.1, dtype=np.float64),
        oz=oz,
        dx=np.zeros(ray_count, dtype=np.float64),
        dy=np.ones(ray_count, dtype=np.float64),
        dz=np.zeros(ray_count, dtype=np.float64),
        tmax=np.full(ray_count, 0.2, dtype=np.float64),
    )
    return triangles, rays, ray_weights


def _ray_weight_payload(ray_weights, *, detail: str) -> object:
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None
    if np is not None and isinstance(ray_weights, np.ndarray):
        if detail == "full":
            return [int(weight) for weight in ray_weights.tolist()]
        return {"sum": int(ray_weights.sum(dtype=np.uint64)), "count": int(ray_weights.size)}
    if hasattr(ray_weights, "get") and hasattr(ray_weights, "sum") and hasattr(ray_weights, "size"):
        if detail == "full":
            return [int(weight) for weight in ray_weights.get().tolist()]
        return {"sum": int(ray_weights.sum().get()), "count": int(ray_weights.size), "device_resident": True}
    if detail == "full":
        return [int(weight) for weight in ray_weights]
    return {"sum": int(sum(ray_weights)), "count": len(ray_weights)}


def _contract_neighbors(contract, vertex: int) -> tuple[int, ...]:
    start = contract.row_offsets[vertex]
    end = contract.row_offsets[vertex + 1]
    return contract.column_indices[start:end]


def _max_out_degree(contract) -> int:
    if contract.vertex_count == 0:
        return 0
    return max(len(_contract_neighbors(contract, vertex)) for vertex in range(contract.vertex_count))


def _load_rt_graph_edges(
    *,
    fixture: str,
    edge_file: str | None,
    edge_format: str,
) -> tuple[tuple[tuple[int, int], ...], dict[str, str]]:
    if edge_file is None:
        edges = fixture_edges(fixture)
        input_source = {"kind": "fixture", "name": fixture}
    elif edge_format == "text":
        edges = read_text_edges(edge_file)
        input_source = {"kind": "edge_file", "format": "text", "path": edge_file}
    elif edge_format == "binary":
        edges = read_binary_edges(edge_file)
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
    else:
        raise ValueError(f"unsupported edge format: {edge_format}")
    return edges, input_source


def run_app(
    mode: str = "scope",
    *,
    backend: str = "cpu_python_reference",
    copies: int = 2,
    output_mode: str = "summary",
    optix_graph_mode: str = "auto",
    fixture: str = "single_triangle",
    edge_file: str | None = None,
    edge_format: str = "text",
    detail: str = "full",
    partner: str = "none",
) -> dict[str, Any]:
    if mode == "scope":
        return scope_payload()
    if mode == "run":
        return run_payload(
            backend=backend,
            copies=copies,
            output_mode=output_mode,
            optix_graph_mode=optix_graph_mode,
        )
    if mode == "command_plan":
        return command_plan_payload()
    if mode == "rt_graph_contract":
        return rt_graph_contract_payload(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
            detail=detail,
        )
    if mode == "rt_graph_rtdl_adapter":
        return rt_graph_rtdl_adapter_payload(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
            backend=backend,
            detail=detail,
        )
    if mode == "rt_graph_2a1_generic_rt":
        return rt_graph_2a1_generic_rt_payload(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
            backend=backend,
            detail=detail,
            partner=partner,
        )
    if mode == "rt_graph_1a2_generic_rt":
        return rt_graph_1a2_generic_rt_payload(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
            backend=backend,
            detail=detail,
            partner=partner,
        )
    raise ValueError(f"unsupported mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bounded triangle-counting research benchmark wrapper."
    )
    parser.add_argument(
        "--mode",
        choices=(
            "scope",
            "run",
            "command_plan",
            "rt_graph_contract",
            "rt_graph_rtdl_adapter",
            "rt_graph_2a1_generic_rt",
            "rt_graph_1a2_generic_rt",
        ),
        default="scope",
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=2)
    parser.add_argument("--output-mode", choices=("rows", "summary"), default="summary")
    parser.add_argument("--optix-graph-mode", choices=("auto", "host_indexed", "native"), default="auto")
    parser.add_argument(
        "--fixture",
        choices=("single_triangle", "degree_oriented_two_triangles", "duplicates_self_and_leaf"),
        default="single_triangle",
    )
    parser.add_argument("--edge-file")
    parser.add_argument("--edge-format", choices=("text", "binary"), default="text")
    parser.add_argument("--detail", choices=("full", "summary"), default="full")
    parser.add_argument("--partner", choices=("none", "cupy"), default="none")
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.mode,
                backend=args.backend,
                copies=args.copies,
                output_mode=args.output_mode,
                optix_graph_mode=args.optix_graph_mode,
                fixture=args.fixture,
                edge_file=args.edge_file,
                edge_format=args.edge_format,
                detail=args.detail,
                partner=args.partner,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
