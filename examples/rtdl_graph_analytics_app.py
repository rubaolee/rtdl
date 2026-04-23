from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_graph_bfs
from examples import rtdl_graph_triangle_count
import rtdsl as rt


BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")
SCENARIOS = ("bfs", "triangle_count", "all")


def _enforce_rt_core_requirement(backend: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    raise RuntimeError(
        "graph_analytics OptiX path is host-indexed fallback today, not NVIDIA RT-core traversal"
    )


def run_app(
    backend: str,
    scenario: str = "all",
    copies: int = 1,
    output_mode: str = "rows",
    *,
    require_rt_core: bool = False,
) -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")
    if copies <= 0:
        raise ValueError("copies must be positive")
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    _enforce_rt_core_requirement(backend, require_rt_core)

    sections: dict[str, Any] = {}
    if scenario in {"bfs", "all"}:
        sections["bfs"] = rtdl_graph_bfs.run_backend(backend, copies=copies, output_mode=output_mode)
    if scenario in {"triangle_count", "all"}:
        sections["triangle_count"] = rtdl_graph_triangle_count.run_backend(backend, copies=copies, output_mode=output_mode)

    return {
        "app": "graph_analytics",
        "backend": backend,
        "scenario": scenario,
        "copies": copies,
        "output_mode": output_mode,
        "sections": sections,
        "data_flow": [
            "application graph data",
            "bounded RTDL graph kernels",
            "BFS discovery rows and triangle rows",
            "Python-owned graph analytics summary JSON",
        ],
        "unifies": [
            "examples/rtdl_graph_bfs.py",
            "examples/rtdl_graph_triangle_count.py",
        ],
        "optix_performance": {
            "class": rt.optix_app_performance_support("graph_analytics").performance_class,
            "note": rt.optix_app_performance_support("graph_analytics").note,
        },
        "rt_core_accelerated": False,
        "honesty_boundary": "Unified app over bounded v0.6.1 graph kernels; not a full graph database or distributed graph analytics system.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Unified RTDL graph analytics app over BFS and triangle-count kernels."
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=BACKENDS,
    )
    parser.add_argument(
        "--scenario",
        default="all",
        choices=SCENARIOS,
        help="Run one graph scenario or the complete unified app.",
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic graph fixture this many times.")
    parser.add_argument("--output-mode", default="rows", choices=("rows", "summary"))
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_app(
                args.backend,
                args.scenario,
                copies=args.copies,
                output_mode=args.output_mode,
                require_rt_core=args.require_rt_core,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
