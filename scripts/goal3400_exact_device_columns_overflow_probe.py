from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(args.county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    columns = None
    try:
        columns = prepared.exact_device_columns(points, max_rows=args.max_rows)
        as_cupy_raised = False
        as_cupy_error = ""
        try:
            columns.as_cupy_columns()
        except Exception as exc:
            as_cupy_raised = True
            as_cupy_error = str(exc)
        return {
            "schema": "rtdl.goal3400.exact_device_columns_overflow_probe.v1",
            "goal": 3400,
            "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "county_cdb": str(args.county_cdb),
            "point_count": len(points),
            "shape_count": len(shapes),
            "max_rows": int(args.max_rows),
            "row_count": int(columns.row_count),
            "capacity": int(columns.capacity),
            "capacity_status": columns.capacity_status.to_metadata(),
            "candidate_event_count": int(columns.candidate_event_count),
            "relation_row_count": int(columns.relation_row_count),
            "required_capacity": int(columns.required_capacity),
            "retry_capacity_hint": columns.retry_capacity_hint,
            "overflow": bool(columns.overflow),
            "device_resident": bool(columns.device_resident),
            "as_cupy_columns_raised": as_cupy_raised,
            "as_cupy_columns_error": as_cupy_error,
            "native_symbol": str(columns.native_symbol),
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
    finally:
        if columns is not None:
            columns.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3400 exact device-column overflow probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count4096.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=100)
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
