from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _materialize_slice(source: Path, output: Path, *, start: int, count: int) -> Path:
    if output.exists():
        return output
    source_dataset = rt.load_cdb(source)
    sliced = CdbDataset(
        name=f"{source.stem}_start{start}_count{count}",
        chains=tuple(source_dataset.chains[start : start + count]),
    )
    rt.write_cdb(sliced, output)
    return output


def _row_pairs(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _column_pairs(cp_module, columns: dict[str, object]) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(columns["point_id"]).tolist()),
            (int(value) for value in cp_module.asnumpy(columns["shape_id"]).tolist()),
        )
    )


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    source = args.source_cdb
    slice_path = args.data_dir / f"br_county_start{args.start}_count{args.count}.cdb"
    _materialize_slice(source, slice_path, start=args.start, count=args.count)
    county = rt.load_cdb(slice_path)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    try:
        print("[goal3392] exact OptiX run", flush=True)
        exact_start = time.perf_counter()
        exact_rows = tuple(prepared.run(points))
        exact_seconds = time.perf_counter() - exact_start
        print("[goal3392] materialize bridge columns", flush=True)
        bridge_start = time.perf_counter()
        columns = rt.materialize_closed_shape_membership_rows_as_cupy_columns(
            exact_rows,
            source_protocol="host_refined_optix_exact_rows",
        )
        cp.cuda.Stream.null.synchronize()
        bridge_seconds = time.perf_counter() - bridge_start
    finally:
        prepared.close()

    exact_pairs = _row_pairs(exact_rows)
    column_pairs = _column_pairs(cp, columns)
    missing = sorted(exact_pairs - column_pairs)
    extra = sorted(column_pairs - exact_pairs)
    return {
        "schema": "rtdl.goal3392.exact_membership_bridge_live_probe.v1",
        "goal": 3392,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "source_cdb": str(source),
        "county_cdb": str(slice_path),
        "start": int(args.start),
        "count": int(args.count),
        "point_count": len(points),
        "shape_count": len(shapes),
        "exact_row_count": len(exact_rows),
        "bridge_row_count": int(columns["row_count"]),
        "pairs_match_exact_rows": column_pairs == exact_pairs,
        "missing_exact_pair_count": len(missing),
        "extra_pair_count": len(extra),
        "missing_sample": [list(pair) for pair in missing[:20]],
        "extra_sample": [list(pair) for pair in extra[:20]],
        "exact_run_seconds": exact_seconds,
        "bridge_upload_seconds": bridge_seconds,
        "bridge_metadata": {
            "source_protocol": columns["source_protocol"],
            "output_residency": columns["output_residency"],
            "host_refined_rows_materialized": columns["host_refined_rows_materialized"],
            "native_exact_device_row_stream_produced": columns["native_exact_device_row_stream_produced"],
            "true_zero_copy_claim_authorized": columns["true_zero_copy_claim_authorized"],
            "release_authorized": columns["release_authorized"],
            "public_speedup_claim_authorized": columns["public_speedup_claim_authorized"],
            "rt_core_speedup_claim_authorized": columns["rt_core_speedup_claim_authorized"],
        },
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "native_default_route_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3392 exact membership bridge live probe.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
    )
    parser.add_argument(
        "--source-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--count", type=int, default=4096)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
