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


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


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

    county = rt.load_cdb(args.county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    overflow_columns = None
    retry_columns = None
    try:
        exact_rows = tuple(prepared.run(points))
        exact_pairs = _row_pairs(exact_rows)

        overflow_columns = prepared.exact_device_columns(points, max_rows=args.initial_max_rows)
        overflow_error = ""
        overflow_wrap_raised = False
        try:
            overflow_columns.as_cupy_columns()
        except Exception as exc:
            overflow_wrap_raised = True
            overflow_error = str(exc)
        retry_hint = overflow_columns.retry_capacity_hint
        if retry_hint is None:
            raise RuntimeError("explicit retry probe expected an overflow retry_capacity_hint")

        retry_columns = prepared.exact_device_columns(points, max_rows=retry_hint)
        retry_cupy_columns = retry_columns.as_cupy_columns()
        retry_pairs = _column_pairs(cp, retry_cupy_columns)

        missing = sorted(exact_pairs - retry_pairs)
        extra = sorted(retry_pairs - exact_pairs)
        return {
            "schema": "rtdl.goal3404.exact_device_columns_explicit_retry_probe.v1",
            "goal": 3404,
            "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "county_cdb": str(args.county_cdb),
            "point_count": len(points),
            "shape_count": len(shapes),
            "initial_max_rows": int(args.initial_max_rows),
            "overflow_capacity_status": overflow_columns.capacity_status.to_metadata(),
            "overflow_row_count": int(overflow_columns.row_count),
            "overflow_capacity": int(overflow_columns.capacity),
            "overflow_required_capacity": int(overflow_columns.required_capacity),
            "overflow_retry_capacity_hint": int(retry_hint),
            "overflow_wrap_raised": overflow_wrap_raised,
            "overflow_wrap_error": overflow_error,
            "retry_capacity_status": retry_columns.capacity_status.to_metadata(),
            "retry_row_count": int(retry_columns.row_count),
            "retry_capacity": int(retry_columns.capacity),
            "retry_overflow": bool(retry_columns.overflow),
            "retry_device_resident": bool(retry_columns.device_resident),
            "exact_row_count": len(exact_rows),
            "pairs_match_exact_rows": retry_pairs == exact_pairs,
            "missing_exact_pair_count": len(missing),
            "extra_pair_count": len(extra),
            "missing_sample": [list(pair) for pair in missing[:20]],
            "extra_sample": [list(pair) for pair in extra[:20]],
            "native_symbol": str(retry_columns.native_symbol),
            "claim_boundary": {
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rayjoin_paper_reproduction_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "native_default_route_authorized": False,
                "hidden_dispatch_authorized": False,
                "automatic_retry_authorized": False,
            },
        }
    finally:
        if retry_columns is not None:
            retry_columns.close()
        if overflow_columns is not None:
            overflow_columns.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3404 explicit retry probe for exact device columns.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count4096.cdb",
    )
    parser.add_argument("--initial-max-rows", type=int, default=100)
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
