from __future__ import annotations

import argparse
import json
import statistics
import struct
import time
from pathlib import Path

import cupy as cp
import cudf
import cugraph
import numpy as np


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _sync() -> None:
    cp.cuda.Stream.null.synchronize()


def _load_edges(edge_file: Path) -> np.ndarray:
    data = np.fromfile(edge_file, dtype=np.int32)
    if data.size % 2:
        raise ValueError(f"{edge_file} does not contain int32 edge pairs")
    return data.reshape(-1, 2)


def _run_once(edge_file: Path) -> dict[str, object]:
    started = time.perf_counter()
    edges = _load_edges(edge_file)
    loaded = time.perf_counter()

    _sync()
    df = cudf.DataFrame(
        {
            "src": edges[:, 0],
            "dst": edges[:, 1],
        }
    )
    _sync()
    dataframe_built = time.perf_counter()

    graph = cugraph.Graph(directed=False)
    graph.from_cudf_edgelist(df, source="src", destination="dst", renumber=True)
    _sync()
    graph_built = time.perf_counter()

    counts = cugraph.triangle_count(graph)
    _sync()
    counted = time.perf_counter()

    triangle_count = int((counts["counts"].sum() / 3).item())
    _sync()
    reduced = time.perf_counter()

    return {
        "input_file": str(edge_file),
        "input_edges": int(edges.shape[0]),
        "triangle_count": triangle_count,
        "load_np_ms": (loaded - started) * 1000.0,
        "build_cudf_dataframe_ms": (dataframe_built - loaded) * 1000.0,
        "build_cugraph_graph_ms": (graph_built - dataframe_built) * 1000.0,
        "triangle_count_ms": (counted - graph_built) * 1000.0,
        "reduce_count_ms": (reduced - counted) * 1000.0,
        "total_ms": (reduced - started) * 1000.0,
    }


def _summarize(runs: list[dict[str, object]]) -> dict[str, object]:
    numeric_keys = [key for key, value in runs[0].items() if isinstance(value, (int, float))]
    summary: dict[str, object] = {"runs": runs}
    for key in numeric_keys:
        summary[f"median_{key}"] = _median([float(run[key]) for run in runs])
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAPIDS cuGraph triangle_count baseline.")
    parser.add_argument("--input", action="append", nargs=2, metavar=("NAME", "EDGE_FILE"), required=True)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    payload: dict[str, object] = {
        "baseline": "rapids_cugraph_triangle_count",
        "cugraph_version": cugraph.__version__,
        "cudf_version": cudf.__version__,
        "method": (
            "Build undirected cugraph.Graph from cudf edge list, run "
            "cugraph.triangle_count, sum per-vertex counts / 3."
        ),
        "results": {},
    }
    for name, edge_file in args.input:
        runs = [_run_once(Path(edge_file)) for _ in range(args.repeats)][args.warmup :]
        payload["results"][name] = {
            "repeats": args.repeats,
            "warmup": args.warmup,
            "measured_runs": len(runs),
            **_summarize(runs),
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
