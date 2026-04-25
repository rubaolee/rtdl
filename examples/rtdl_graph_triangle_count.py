from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


def make_case(copies: int = 1) -> dict[str, object]:
    if copies <= 0:
        raise ValueError("copies must be positive")
    row_offsets = [0]
    column_indices: list[int] = []
    seeds: list[tuple[int, int]] = []
    for copy_index in range(copies):
        base = copy_index * 4
        adjacency = ((base + 1, base + 2), (base + 0, base + 2), (base + 0, base + 1), ())
        seeds.extend(((base + 0, base + 1), (base + 1, base + 2), (base + 0, base + 2)))
        for neighbors in adjacency:
            column_indices.extend(neighbors)
            row_offsets.append(len(column_indices))
    return {
        "seeds": tuple(seeds),
        "graph": rt.csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(column_indices)),
    }


def _summarize(rows) -> dict[str, object]:
    row_list = list(rows)
    vertices = {int(row[name]) for row in row_list for name in ("u", "v", "w")}
    return {
        "triangle_count": len(row_list),
        "touched_vertex_count": len(vertices),
    }


def _enforce_rt_core_requirement(backend: str, require_rt_core: bool) -> None:
    if not require_rt_core:
        return
    if backend != "optix":
        raise ValueError("--require-rt-core is only meaningful with --backend optix")
    raise RuntimeError(
        "graph_triangle_count OptiX native graph-ray mode is not NVIDIA RT-core "
        "traversal claim-safe until the RTX cloud gate passes"
    )


def run_backend(
    backend: str,
    copies: int = 1,
    output_mode: str = "rows",
    *,
    require_rt_core: bool = False,
    optix_graph_mode: str = "auto",
) -> dict[str, object]:
    if output_mode not in {"rows", "summary"}:
        raise ValueError(f"unsupported output_mode: {output_mode}")
    if optix_graph_mode not in {"auto", "host_indexed", "native"}:
        raise ValueError(f"unsupported optix_graph_mode: {optix_graph_mode}")
    _enforce_rt_core_requirement(backend, require_rt_core)
    case = make_case(copies)
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(triangle_probe_kernel, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(triangle_probe_kernel, **case)
    elif backend == "embree":
        rows = rt.run_embree(triangle_probe_kernel, **case)
    elif backend == "optix":
        previous = os.environ.get("RTDL_OPTIX_GRAPH_MODE")
        if optix_graph_mode != "auto":
            os.environ["RTDL_OPTIX_GRAPH_MODE"] = "native" if optix_graph_mode == "native" else "host_indexed"
        try:
            rows = rt.run_optix(triangle_probe_kernel, **case)
        finally:
            if optix_graph_mode != "auto":
                if previous is None:
                    os.environ.pop("RTDL_OPTIX_GRAPH_MODE", None)
                else:
                    os.environ["RTDL_OPTIX_GRAPH_MODE"] = previous
    elif backend == "vulkan":
        rows = rt.run_vulkan(triangle_probe_kernel, **case)
    else:
        raise ValueError(f"unsupported backend: {backend}")

    return {
        "app": "graph_triangle_count",
        "backend": backend,
        "copies": copies,
        "output_mode": output_mode,
        "optix_graph_mode": optix_graph_mode if backend == "optix" else "not_applicable",
        "graph_vertex_count": 4 * copies,
        "graph_edge_count": 6 * copies,
        "seed_count": len(case["seeds"]),
        "row_count": len(rows),
        "rows": rows if output_mode == "rows" else [],
        "summary": _summarize(rows),
        "ray_tracing_accelerated": backend == "embree",
        "ray_tracing_note": (
            "Embree uses ray traversal over graph-edge primitives to collect "
            "candidate neighbor sets; CPU-side set intersection and uniqueness "
            "bookkeeping remain outside the RT traversal."
            if backend == "embree"
            else "This backend is not currently classified as the graph triangle-count ray-tracing path."
        ),
        "rt_core_accelerated": False,
        "optix_performance": {
            "class": "host_indexed_fallback",
            "note": (
                "OptiX triangle-count currently uses a host-indexed CSR probe correctness path; "
                "native graph-ray mode is available behind RTDL_OPTIX_GRAPH_MODE=native "
                "but is not an RTX graph acceleration claim until cloud-gated."
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release-facing RTDL graph triangle-count one-step example.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    parser.add_argument("--copies", type=int, default=1, help="Repeat the deterministic triangle fixture this many times.")
    parser.add_argument("--output-mode", default="rows", choices=("rows", "summary"))
    parser.add_argument("--optix-graph-mode", default="auto", choices=("auto", "host_indexed", "native"))
    parser.add_argument(
        "--require-rt-core",
        action="store_true",
        help="Fail if the selected path is not a true NVIDIA RT-core traversal path.",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            run_backend(
                args.backend,
                copies=args.copies,
                output_mode=args.output_mode,
                require_rt_core=args.require_rt_core,
                optix_graph_mode=args.optix_graph_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
