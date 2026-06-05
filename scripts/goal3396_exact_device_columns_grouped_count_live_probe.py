from __future__ import annotations

import argparse
from collections import Counter
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
    exact_columns = None
    grouped = None
    try:
        print("[goal3396] exact host counts", flush=True)
        exact_rows = tuple(prepared.run(points))
        host_counts = Counter(int(row["point_id"]) for row in exact_rows)
        max_point_id = max([int(point.id) for point in points] + list(host_counts.keys()))
        print("[goal3396] exact device columns", flush=True)
        exact_columns = prepared.exact_device_columns(points)
        print("[goal3396] grouped count continuation", flush=True)
        grouped = exact_columns.grouped_count_by_left_id_compact_device_columns(
            group_capacity=max_point_id + 1,
        )
        keys = grouped.as_cupy_group_keys()
        counts = grouped.as_cupy_counts()
        device_counts = {
            int(key): int(count)
            for key, count in zip(cp.asnumpy(keys).tolist(), cp.asnumpy(counts).tolist())
        }
    finally:
        if grouped is not None:
            grouped.close()
        if exact_columns is not None:
            exact_columns.close()
        prepared.close()

    missing_keys = sorted(set(host_counts) - set(device_counts))
    extra_keys = sorted(set(device_counts) - set(host_counts))
    mismatched_values = sorted(
        point_id
        for point_id in set(host_counts) & set(device_counts)
        if int(host_counts[point_id]) != int(device_counts[point_id])
    )
    return {
        "schema": "rtdl.goal3396.exact_device_columns_grouped_count_live_probe.v1",
        "goal": 3396,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "source_cdb": str(source),
        "county_cdb": str(slice_path),
        "start": int(args.start),
        "count": int(args.count),
        "point_count": len(points),
        "shape_count": len(shapes),
        "exact_row_count": len(exact_rows),
        "exact_device_row_count": int(exact_columns.row_count),
        "group_count": len(host_counts),
        "device_group_count": len(device_counts),
        "group_counts_match_host": device_counts == dict(host_counts),
        "missing_group_key_count": len(missing_keys),
        "extra_group_key_count": len(extra_keys),
        "mismatched_group_value_count": len(mismatched_values),
        "missing_group_key_sample": missing_keys[:20],
        "extra_group_key_sample": extra_keys[:20],
        "mismatched_group_value_sample": mismatched_values[:20],
        "grouped_source_row_count": int(grouped.source_row_count),
        "grouped_row_count": int(grouped.row_count),
        "grouped_overflow": bool(grouped.overflow),
        "grouped_reduction_seconds": float(grouped.reduction_seconds),
        "grouped_compaction_seconds": float(grouped.compaction_seconds),
        "exact_native_symbol": str(exact_columns.native_symbol),
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
    parser = argparse.ArgumentParser(description="Goal3396 exact device columns grouped count live probe.")
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
