from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
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
    columns = None
    try:
        print("[goal3394] exact host rows", flush=True)
        exact_rows = tuple(prepared.run(points))
        exact_pairs = _row_pairs(exact_rows)
        print("[goal3394] exact device columns", flush=True)
        columns = prepared.exact_device_columns(points)
        cupy_columns = columns.as_cupy_columns()
        column_pairs = _column_pairs(cp, cupy_columns)
        metadata = columns.to_metadata()
    finally:
        if columns is not None:
            columns.close()
        prepared.close()

    missing = sorted(exact_pairs - column_pairs)
    extra = sorted(column_pairs - exact_pairs)
    return {
        "schema": "rtdl.goal3394.optix_exact_membership_device_columns_live_probe.v1",
        "goal": 3394,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "source_cdb": str(source),
        "county_cdb": str(slice_path),
        "start": int(args.start),
        "count": int(args.count),
        "point_count": len(points),
        "shape_count": len(shapes),
        "exact_row_count": len(exact_rows),
        "device_column_row_count": int(columns.row_count),
        "candidate_event_count": int(columns.candidate_event_count),
        "device_resident": bool(columns.device_resident),
        "overflow": bool(columns.overflow),
        "native_symbol": str(columns.native_symbol),
        "traversal_seconds": float(columns.traversal_seconds),
        "pairs_match_exact_rows": column_pairs == exact_pairs,
        "missing_exact_pair_count": len(missing),
        "extra_pair_count": len(extra),
        "missing_sample": [list(pair) for pair in missing[:20]],
        "extra_sample": [list(pair) for pair in extra[:20]],
        "metadata": metadata,
        "implementation_boundary": {
            "host_refined_exact_rows_inside_native_bridge": True,
            "native_exact_device_row_stream_produced": True,
            "device_only_exact_predicate_produced": False,
            "true_zero_copy_claim_authorized": False,
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
    parser = argparse.ArgumentParser(description="Goal3394 OptiX exact membership device columns live probe.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "rayjoin_public_cdb")
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
