"""V2.14 direct front door for both required RT-Graph triangle algorithms."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
BENCHMARK_PATH = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)


def _load_benchmark():
    name = "goal5725_triangle_counting_benchmark"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, BENCHMARK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BENCHMARK_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_v2_14(
    *,
    paper_algorithm: str,
    fixture: str = "degree_oriented_two_triangles",
    backend: str = "cpu",
    edge_file: str | None = None,
    edge_format: str = "text",
    partner: str = "none",
    expected_triangle_count: int | None = None,
    segmented: bool = False,
    max_relation_rows: int = 1_000_000,
) -> dict[str, object]:
    """Run exactly the caller-requested paper algorithm; never choose one."""

    app = _load_benchmark()
    if segmented:
        if backend != "optix" or edge_file is None or edge_format != "binary":
            raise ValueError("segmented V2.14 requires OptiX binary edge-file execution")
        if expected_triangle_count is None:
            raise ValueError("segmented paper-dataset execution requires author expected count")
        contract = app.build_segmented_rt_graph_csr_binary(
            edge_file,
            expected_triangle_count=expected_triangle_count,
        )
        source = app.run_rt_graph_segmented_optix_scalar_summary(
            contract,
            paper_method=paper_algorithm,
            max_relation_rows=max_relation_rows,
        )
        actual = int(source["scalar_sum"])
        expected = int(contract.expected_triangle_count)
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
        return {
            "schema": "rtdl.paper_reproduction.rt_graph_triangle_counting.v2_14.v2",
            "version": "v2.14",
            "paper_algorithm": paper_algorithm,
            "application_selected_algorithm": True,
            "default_selected_between_paper_algorithms": False,
            "backend": backend,
            "input_source": input_source,
            "output": {"triangle_count": actual},
            "expected": {"triangle_count": expected},
            "matched": actual == expected,
            "behavioral_true_optix_required_for_optix_claim": True,
            "segmented_execution": True,
            "source_result": source,
        }

    common = dict(
        fixture=fixture,
        edge_file=edge_file,
        edge_format=edge_format,
        backend=backend,
        detail="summary",
        partner=partner,
        warmup=0,
        repeat=1,
        rt_graph_copies=1,
    )
    if paper_algorithm == "RT-1A2":
        source = app.rt_graph_1a2_generic_rt_payload(**common)
        actual = int(source["generic_rt_triangle_count"])
    elif paper_algorithm == "RT-2A1":
        source = app.rt_graph_2a1_generic_rt_payload(**common)
        actual = int(source["generic_rt_weighted_triangle_count"])
    else:
        raise ValueError("paper_algorithm must be RT-1A2 or RT-2A1")
    expected = int(source["oracle_triangle_count"])
    return {
        "schema": "rtdl.paper_reproduction.rt_graph_triangle_counting.v2_14.v1",
        "version": "v2.14",
        "paper_algorithm": paper_algorithm,
        "application_selected_algorithm": True,
        "default_selected_between_paper_algorithms": False,
        "backend": backend,
        "input_source": source["input_source"],
        "output": {"triangle_count": actual},
        "expected": {"triangle_count": expected},
        "matched": actual == expected,
        "behavioral_true_optix_required_for_optix_claim": True,
        "source_result": source,
    }


def run_v2_14_segmented_contract_epoch(
    *,
    graph_contract,
    paper_algorithm: str,
    max_relation_rows: int,
    start_segment_id: int,
    stop_segment_id: int,
) -> dict[str, object]:
    """Execute one fresh-process epoch over an already prepared CSR."""

    app = _load_benchmark()
    source = app.run_rt_graph_segmented_optix_scalar_summary(
        graph_contract,
        paper_method=paper_algorithm,
        max_relation_rows=max_relation_rows,
        start_segment_id=start_segment_id,
        stop_segment_id=stop_segment_id,
    )
    return {
        "version": "v2.14",
        "paper_algorithm": paper_algorithm,
        "output": {"triangle_count": int(source["scalar_sum"])},
        "source_result": source,
    }


__all__ = ["run_v2_14", "run_v2_14_segmented_contract_epoch"]
