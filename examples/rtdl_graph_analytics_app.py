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


BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")
SCENARIOS = ("bfs", "triangle_count", "all")


def run_app(backend: str, scenario: str = "all") -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")

    sections: dict[str, Any] = {}
    if scenario in {"bfs", "all"}:
        sections["bfs"] = rtdl_graph_bfs.run_backend(backend)
    if scenario in {"triangle_count", "all"}:
        sections["triangle_count"] = rtdl_graph_triangle_count.run_backend(backend)

    return {
        "app": "graph_analytics",
        "backend": backend,
        "scenario": scenario,
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
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, args.scenario), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
