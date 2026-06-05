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
from rtdsl.pair_column_paged_recovery import PairColumnPageRecoveryRecord  # noqa: E402
from rtdsl.pair_column_paged_recovery import merge_grouped_count_maps  # noqa: E402
from rtdsl.pair_column_paged_recovery import summarize_page_recovery_records  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(args.county_cdb)
    points = tuple(rt.chains_to_probe_points(county))
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    grouped_outputs = []
    stream_outputs = []
    native_plan = None
    try:
        native_plan = prepared.exact_device_columns_native_page_plan(
            points,
            page_size=int(args.page_size),
            initial_max_rows=int(args.initial_max_rows),
        )
        host_counts: Counter[int] = Counter()
        page_count_maps: list[dict[int, int]] = []
        page_records: list[PairColumnPageRecoveryRecord] = []
        max_point_id = max(int(point.id) for point in points) if points else 0

        for page_index in range(native_plan.page_count):
            request = native_plan.request(page_index)
            page_points = tuple(request.slice(points))
            print(
                "[goal3418] native plan page "
                f"{request.page_index} start={request.start} count={request.item_count}",
                flush=True,
            )
            page_host_rows = tuple(prepared.run(page_points))
            host_counts.update(int(row["point_id"]) for row in page_host_rows)

            first_columns = native_plan.produce_page(page_index)
            stream_outputs.append(first_columns)
            first_status = first_columns.capacity_status.to_metadata()
            retry_used = bool(first_columns.overflow)
            if retry_used:
                retry_hint = first_columns.retry_capacity_hint
                if retry_hint is None:
                    raise RuntimeError("native page plan expected overflow retry_capacity_hint")
                recovered_columns = native_plan.produce_page(page_index, max_rows=retry_hint)
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
            page_device_counts = {
                int(key): int(count)
                for key, count in zip(cp.asnumpy(keys).tolist(), cp.asnumpy(counts).tolist())
            }
            page_count_maps.append(page_device_counts)
            page_records.append(
                PairColumnPageRecoveryRecord(
                    request=request,
                    host_exact_rows=int(len(page_host_rows)),
                    first_capacity_status=first_status,
                    retry_used=retry_used,
                    retry_capacity_hint=None if retry_hint is None else int(retry_hint),
                    recovered_capacity_status=recovered_columns.capacity_status.to_metadata(),
                    grouped_source_row_count=int(grouped.source_row_count),
                    grouped_row_count=int(grouped.row_count),
                    grouped_overflow=bool(grouped.overflow),
                    device_group_count=int(len(page_device_counts)),
                )
            )
        native_plan_metadata = native_plan.to_metadata()
    finally:
        for grouped in reversed(grouped_outputs):
            grouped.close()
        for columns in reversed(stream_outputs):
            columns.close()
        if native_plan is not None:
            native_plan.close()
        prepared.close()

    device_counts = Counter(merge_grouped_count_maps(page_count_maps))
    missing_keys = sorted(set(host_counts) - set(device_counts))
    extra_keys = sorted(set(device_counts) - set(host_counts))
    mismatched_values = sorted(
        point_id
        for point_id in set(host_counts) & set(device_counts)
        if int(host_counts[point_id]) != int(device_counts[point_id])
    )
    recovery_summary = summarize_page_recovery_records(page_records)
    return {
        "schema": "rtdl.goal3418.native_page_plan_handle_probe.v1",
        "goal": 3418,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "native_page_plan": native_plan_metadata,
        "recovery_summary": recovery_summary,
        "host_group_count": len(host_counts),
        "device_group_count": len(device_counts),
        "host_exact_row_count": int(sum(int(record.host_exact_rows or 0) for record in page_records)),
        "device_grouped_source_row_count": int(recovery_summary["grouped_source_row_count"]),
        "device_grouped_row_count": int(recovery_summary["grouped_row_count"]),
        "group_counts_match_host": device_counts == host_counts,
        "missing_group_key_count": len(missing_keys),
        "extra_group_key_count": len(extra_keys),
        "mismatched_group_value_count": len(mismatched_values),
        "native_page_plan_boundary": {
            "native_page_plan_handle_implemented": True,
            "native_page_release_function_implemented": True,
            "native_plan_owns_host_point_copy": True,
            "produce_page_api_used": True,
            "device_only_exact_predicate_produced": False,
            "automatic_retry_authorized": False,
            "hidden_dispatch_authorized": False,
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
    parser = argparse.ArgumentParser(description="Goal3418 native page-plan handle probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--page-size", type=int, default=2048)
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
