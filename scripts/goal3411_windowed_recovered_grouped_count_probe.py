from __future__ import annotations

import argparse
from collections import Counter
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


def _windows(values: tuple[object, ...], size: int):
    for start in range(0, len(values), size):
        yield start, values[start : start + size]


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(args.county_cdb)
    points = tuple(rt.chains_to_probe_points(county))
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    grouped_outputs = []
    stream_outputs = []
    try:
        host_counts: Counter[int] = Counter()
        device_counts: Counter[int] = Counter()
        window_summaries: list[dict[str, object]] = []
        max_point_id = max(int(point.id) for point in points) if points else 0

        for window_index, (start, window_points) in enumerate(_windows(points, args.window_size)):
            print(f"[goal3411] window {window_index} start={start} count={len(window_points)}", flush=True)
            window_host_rows = tuple(prepared.run(window_points))
            host_counts.update(int(row["point_id"]) for row in window_host_rows)

            first_columns = prepared.exact_device_columns(window_points, max_rows=args.initial_max_rows)
            stream_outputs.append(first_columns)
            first_status = first_columns.capacity_status.to_metadata()
            retry_used = bool(first_columns.overflow)
            if retry_used:
                retry_hint = first_columns.retry_capacity_hint
                if retry_hint is None:
                    raise RuntimeError("window overflow did not provide retry_capacity_hint")
                recovered_columns = prepared.exact_device_columns(window_points, max_rows=retry_hint)
                stream_outputs.append(recovered_columns)
            else:
                retry_hint = None
                recovered_columns = first_columns

            grouped = recovered_columns.grouped_count_by_left_id_compact_device_columns(
                group_capacity=max_point_id + 1,
            )
            grouped_outputs.append(grouped)
            keys = grouped.as_cupy_group_keys()
            counts = grouped.as_cupy_counts()
            window_device_counts = {
                int(key): int(count)
                for key, count in zip(cp.asnumpy(keys).tolist(), cp.asnumpy(counts).tolist())
            }
            device_counts.update(window_device_counts)
            window_summaries.append(
                {
                    "window_index": window_index,
                    "start": int(start),
                    "point_count": int(len(window_points)),
                    "host_exact_rows": int(len(window_host_rows)),
                    "first_capacity_status": first_status,
                    "retry_used": retry_used,
                    "retry_capacity_hint": None if retry_hint is None else int(retry_hint),
                    "recovered_capacity_status": recovered_columns.capacity_status.to_metadata(),
                    "grouped_source_row_count": int(grouped.source_row_count),
                    "grouped_row_count": int(grouped.row_count),
                    "grouped_overflow": bool(grouped.overflow),
                    "device_group_count": int(len(window_device_counts)),
                }
            )
    finally:
        for grouped in reversed(grouped_outputs):
            grouped.close()
        for columns in reversed(stream_outputs):
            columns.close()
        prepared.close()

    missing_keys = sorted(set(host_counts) - set(device_counts))
    extra_keys = sorted(set(device_counts) - set(host_counts))
    mismatched_values = sorted(
        point_id
        for point_id in set(host_counts) & set(device_counts)
        if int(host_counts[point_id]) != int(device_counts[point_id])
    )
    retry_window_count = sum(1 for summary in window_summaries if bool(summary["retry_used"]))
    overflow_window_count = sum(
        1 for summary in window_summaries if bool(summary["first_capacity_status"]["overflowed"])  # type: ignore[index]
    )
    return {
        "schema": "rtdl.goal3411.windowed_recovered_grouped_count_probe.v1",
        "goal": 3411,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "window_size": int(args.window_size),
        "window_count": len(window_summaries),
        "initial_max_rows": int(args.initial_max_rows),
        "overflow_window_count": int(overflow_window_count),
        "retry_window_count": int(retry_window_count),
        "host_group_count": len(host_counts),
        "device_group_count": len(device_counts),
        "host_exact_row_count": int(sum(int(summary["host_exact_rows"]) for summary in window_summaries)),
        "device_grouped_source_row_count": int(sum(int(summary["grouped_source_row_count"]) for summary in window_summaries)),
        "device_grouped_row_count": int(sum(int(summary["grouped_row_count"]) for summary in window_summaries)),
        "group_counts_match_host": device_counts == host_counts,
        "missing_group_key_count": len(missing_keys),
        "extra_group_key_count": len(extra_keys),
        "mismatched_group_value_count": len(mismatched_values),
        "missing_group_key_sample": missing_keys[:20],
        "extra_group_key_sample": extra_keys[:20],
        "mismatched_group_value_sample": mismatched_values[:20],
        "window_summaries": window_summaries,
        "orchestration_boundary": {
            "python_windowed_orchestration_bridge": True,
            "native_paged_stream_implemented": False,
            "automatic_retry_authorized": False,
            "hidden_dispatch_authorized": False,
            "windows_are_caller_visible": True,
            "window_merge_requires_disjoint_left_ids": True,
        },
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3411 windowed recovered grouped-count probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--window-size", type=int, default=2048)
    parser.add_argument("--initial-max-rows", type=int, default=100)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.window_size <= 0:
        raise ValueError("window-size must be positive")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
