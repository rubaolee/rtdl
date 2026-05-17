from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_rayjoin_v2_spatial_join_app import rayjoin_point_location_positive_hits_reference
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_polygons
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb


SCHEMA = "rtdl.rayjoin.same_query_stream.v1"


def _resolve(path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return ROOT / value


def _base_bounds(base_cdb: Path) -> tuple[float, float, float, float]:
    dataset = load_cdb(base_cdb)
    xs = [point.x for chain in dataset.chains for point in chain.points]
    ys = [point.y for chain in dataset.chains for point in chain.points]
    if not xs or not ys:
        raise ValueError(f"{base_cdb} has no coordinates")
    return min(xs), min(ys), max(xs), max(ys)


def materialize_demo_stream(
    *,
    workload: str,
    base_cdb: str | Path,
    output: str | Path,
    gen_n: int,
    gen_t: float,
    seed: int,
) -> dict[str, object]:
    """Create a deterministic local smoke stream.

    This is not a RayJoin C++ generator clone. It exists so the RTDL consuming
    side can be tested without a pod. Strong same-contract evidence should set
    producer to rayjoin_query_exec_export_patch after exporting from RayJoin.
    """

    if workload not in {"lsi", "pip"}:
        raise ValueError("workload must be lsi or pip")
    if gen_n <= 0:
        raise ValueError("gen_n must be positive")
    base_path = _resolve(base_cdb)
    min_x, min_y, max_x, max_y = _base_bounds(base_path)
    width = max_x - min_x
    height = max_y - min_y
    if width <= 0 or height <= 0:
        raise ValueError("base CDB bounds must have positive area")

    # A tiny LCG keeps the fixture deterministic and dependency-free. Real
    # RayJoin-exported streams bypass this generator entirely.
    state = int(seed) & 0xFFFFFFFF

    def rand01() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 0x100000000

    queries: list[dict[str, float | int]] = []
    for index in range(gen_n):
        x0 = min_x + width * rand01()
        y0 = min_y + height * rand01()
        if workload == "pip":
            queries.append({"id": index + 1, "x": x0, "y": y0})
            continue
        theta = 2.0 * math.pi * rand01()
        length = float(gen_t) * (0.25 + 0.75 * rand01())
        queries.append(
            {
                "id": index + 1,
                "x0": x0,
                "y0": y0,
                "x1": x0 + math.cos(theta) * length,
                "y1": y0 + math.sin(theta) * length,
            }
        )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "producer": "rtdl_demo_generator_not_rayjoin_cpp",
        "workload": workload,
        "base_cdb": str(base_path),
        "rayjoin_query_exec_flags": {
            "poly1": str(base_path),
            "query": workload,
            "gen_n": gen_n,
            "gen_t": gen_t,
            "seed": seed,
        },
        "query_count": len(queries),
        "queries": queries,
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": False,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    out = _resolve(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def load_query_stream(path: str | Path) -> dict[str, object]:
    payload = json.loads(_resolve(path).read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"query stream must use schema {SCHEMA}")
    if payload.get("workload") not in {"lsi", "pip"}:
        raise ValueError("query stream workload must be lsi or pip")
    queries = payload.get("queries")
    if not isinstance(queries, list) or not queries:
        raise ValueError("query stream must contain a non-empty queries array")
    if int(payload.get("query_count", -1)) != len(queries):
        raise ValueError("query_count must match queries length")
    return payload


def _stream_points(stream: dict[str, object]) -> tuple[rt.Point, ...]:
    points = []
    for row in stream["queries"]:
        points.append(rt.Point(id=int(row["id"]), x=float(row["x"]), y=float(row["y"])))
    return tuple(points)


def _stream_segments(stream: dict[str, object]) -> tuple[rt.Segment, ...]:
    segments = []
    for row in stream["queries"]:
        segments.append(
            rt.Segment(
                id=int(row["id"]),
                x0=float(row["x0"]),
                y0=float(row["y0"]),
                x1=float(row["x1"]),
                y1=float(row["y1"]),
            )
        )
    return tuple(segments)


def _run_backend(workload: str, backend: str, inputs: dict[str, object]) -> tuple[dict[str, object], ...]:
    kernel = rayjoin_point_location_positive_hits_reference if workload == "pip" else county_zip_join_reference
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(kernel, **inputs)
    if backend == "cpu":
        return rt.run_cpu(kernel, **inputs)
    if backend == "embree":
        return rt.run_embree(kernel, **inputs)
    if backend == "optix":
        return rt.run_optix(kernel, **inputs)
    raise ValueError("backend must be cpu_python_reference, cpu, embree, or optix")


def _inputs_from_stream(stream: dict[str, object]) -> dict[str, object]:
    base_path = Path(str(stream["base_cdb"]))
    if not base_path.is_absolute():
        base_path = _resolve(base_path)
    base = load_cdb(base_path)
    if stream["workload"] == "pip":
        return {
            "points": _stream_points(stream),
            "polygons": chains_to_polygons(base),
        }
    return {
        "left": _stream_segments(stream),
        "right": segments_from_records(chains_to_segments(base)),
    }


def run_stream(
    *,
    query_stream: str | Path,
    backends: tuple[str, ...],
    reference_backend: str,
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    if warmups < 0 or repeats <= 0:
        raise ValueError("warmups must be non-negative and repeats must be positive")
    stream = load_query_stream(query_stream)
    workload = str(stream["workload"])
    inputs = _inputs_from_stream(stream)
    reference_rows = _run_backend(workload, reference_backend, inputs)
    baseline_workload = "pip" if workload == "pip" else "lsi"

    payload: dict[str, object] = {
        "goal": "2192",
        "schema": "rtdl.rayjoin.same_query_result.v1",
        "query_stream": str(_resolve(query_stream)),
        "query_stream_schema": stream["schema"],
        "query_stream_producer": stream["producer"],
        "workload": workload,
        "query_count": int(stream["query_count"]),
        "base_cdb": stream["base_cdb"],
        "reference_backend": reference_backend,
        "commit": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            cwd=ROOT,
            text=True,
            capture_output=True,
        ).stdout.strip(),
        "warmups": warmups,
        "repeats": repeats,
        "reference_row_count": len(reference_rows),
        "backends": {},
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": stream["producer"] == "rayjoin_query_exec_export_patch",
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }

    for backend in backends:
        timings = []
        row_counts = []
        parity = []
        for index in range(warmups):
            start = time.perf_counter()
            rows = _run_backend(workload, backend, inputs)
            elapsed = time.perf_counter() - start
            print(
                f"[goal2192] warmup {workload}/{backend} {index + 1}/{warmups} "
                f"rows={len(rows)} elapsed={elapsed:.6f}s",
                flush=True,
            )
        for index in range(repeats):
            start = time.perf_counter()
            rows = _run_backend(workload, backend, inputs)
            elapsed = time.perf_counter() - start
            timings.append(elapsed)
            row_counts.append(len(rows))
            parity_value = rt.compare_baseline_rows(baseline_workload, reference_rows, rows)
            parity.append(bool(parity_value))
            print(
                f"[goal2192] repeat {workload}/{backend} {index + 1}/{repeats} "
                f"rows={len(rows)} parity={parity[-1]} elapsed={elapsed:.6f}s",
                flush=True,
            )
        payload["backends"][backend] = {
            "status": "ok",
            "elapsed_sec_values": timings,
            "elapsed_sec_median": statistics.median(timings),
            "row_counts": row_counts,
            "row_count_consistent": len(set(row_counts)) == 1,
            "parity_reference_backend": reference_backend,
            "all_parity_vs_reference": all(parity),
            "all_parity_vs_cpu_python_reference": all(parity)
            if reference_backend == "cpu_python_reference"
            else None,
            "rt_core_accelerated": backend == "optix",
        }
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RTDL against a RayJoin same-query stream.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    materialize = subparsers.add_parser("materialize-demo-stream")
    materialize.add_argument("--workload", choices=("lsi", "pip"), required=True)
    materialize.add_argument("--base-cdb", required=True)
    materialize.add_argument("--output", required=True)
    materialize.add_argument("--gen-n", type=int, default=16)
    materialize.add_argument("--gen-t", type=float, default=0.1)
    materialize.add_argument("--seed", type=int, default=2192)

    run = subparsers.add_parser("run-stream")
    run.add_argument("--query-stream", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--backends", default="cpu_python_reference,cpu")
    run.add_argument("--reference-backend", default="cpu_python_reference")
    run.add_argument("--warmups", type=int, default=0)
    run.add_argument("--repeats", type=int, default=1)

    args = parser.parse_args(argv)
    if args.command == "materialize-demo-stream":
        materialize_demo_stream(
            workload=args.workload,
            base_cdb=args.base_cdb,
            output=args.output,
            gen_n=args.gen_n,
            gen_t=args.gen_t,
            seed=args.seed,
        )
        print(f"[goal2192] wrote {args.output}", flush=True)
        return 0

    backends = tuple(item.strip() for item in args.backends.split(",") if item.strip())
    payload = run_stream(
        query_stream=args.query_stream,
        backends=backends,
        reference_backend=args.reference_backend,
        warmups=args.warmups,
        repeats=args.repeats,
    )
    output = _resolve(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal2192] wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
