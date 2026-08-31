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
from rtdsl.pair_column_paged_recovery import PairColumnPagedRecoveryContract  # noqa: E402
from rtdsl.pair_column_paged_recovery import iter_pair_column_page_requests  # noqa: E402
from rtdsl.pair_column_paged_recovery import merge_grouped_count_maps  # noqa: E402
from rtdsl.pair_column_paged_recovery import summarize_page_recovery_records  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _pairs_from_device_columns(cp, columns) -> Counter[tuple[int, int]]:
    cupy_columns = columns.as_cupy_columns()
    left = cp.asnumpy(cupy_columns[columns.field_names[0]]).tolist()
    right = cp.asnumpy(cupy_columns[columns.field_names[1]]).tolist()
    return Counter((int(left_id), int(right_id)) for left_id, right_id in zip(left, right))


def _pairs_from_host_rows(rows: tuple[dict[str, int], ...]) -> Counter[tuple[int, int]]:
    return Counter((int(row["point_id"]), int(row["shape_id"])) for row in rows)


def _counter_diff_sample(left: Counter[tuple[int, int]], right: Counter[tuple[int, int]]) -> list[list[int]]:
    diff = left - right
    return [[int(point_id), int(shape_id), int(count)] for (point_id, shape_id), count in diff.items()][:20]


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(args.county_cdb)
    points = tuple(rt.chains_to_probe_points(county))
    shapes = rt.chains_to_polygons(county)
    contract = PairColumnPagedRecoveryContract(
        page_size=int(args.page_size),
        initial_capacity=int(args.initial_max_rows),
    )
    requests = iter_pair_column_page_requests(
        total_count=len(points),
        page_size=contract.page_size,
        initial_capacity=contract.initial_capacity,
    )
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    grouped_outputs = []
    stream_outputs = []
    try:
        host_counts: Counter[int] = Counter()
        device_page_count_maps: list[dict[int, int]] = []
        page_records: list[PairColumnPageRecoveryRecord] = []
        host_pair_counter: Counter[tuple[int, int]] = Counter()
        device_pair_counter: Counter[tuple[int, int]] = Counter()
        max_point_id = max(int(point.id) for point in points) if points else 0

        for request in requests:
            page_points = tuple(request.slice(points))
            print(
                "[goal3420] device predicate page "
                f"{request.page_index} start={request.start} count={request.item_count}",
                flush=True,
            )
            page_host_rows = tuple(prepared.run(page_points))
            page_host_pairs = _pairs_from_host_rows(page_host_rows)
            host_pair_counter.update(page_host_pairs)
            host_counts.update(int(row["point_id"]) for row in page_host_rows)

            first_columns = prepared.candidate_device_columns(
                page_points,
                max_rows=request.initial_capacity,
            )
            stream_outputs.append(first_columns)
            first_status = first_columns.capacity_status.to_metadata()
            retry_used = bool(first_columns.overflow)
            if retry_used:
                retry_hint = first_columns.retry_capacity_hint
                if retry_hint is None:
                    raise RuntimeError("device predicate page expected overflow retry_capacity_hint")
                recovered_columns = prepared.candidate_device_columns(page_points, max_rows=retry_hint)
                stream_outputs.append(recovered_columns)
            else:
                retry_hint = None
                recovered_columns = first_columns

            page_device_pairs = _pairs_from_device_columns(cp, recovered_columns)
            device_pair_counter.update(page_device_pairs)
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
            device_page_count_maps.append(page_device_counts)
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
    finally:
        for grouped in reversed(grouped_outputs):
            grouped.close()
        for columns in reversed(stream_outputs):
            columns.close()
        prepared.close()

    device_counts = Counter(merge_grouped_count_maps(device_page_count_maps))
    missing_keys = sorted(set(host_counts) - set(device_counts))
    extra_keys = sorted(set(device_counts) - set(host_counts))
    mismatched_values = sorted(
        point_id
        for point_id in set(host_counts) & set(device_counts)
        if int(host_counts[point_id]) != int(device_counts[point_id])
    )
    pair_missing_sample = _counter_diff_sample(host_pair_counter, device_pair_counter)
    pair_extra_sample = _counter_diff_sample(device_pair_counter, host_pair_counter)
    recovery_summary = summarize_page_recovery_records(page_records)
    pair_multiset_match = host_pair_counter == device_pair_counter
    group_counts_match = device_counts == host_counts
    return {
        "schema": "rtdl.goal3420.device_predicate_page_equivalence_probe.v1",
        "goal": 3420,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "contract": contract.to_metadata(),
        "recovery_summary": recovery_summary,
        "host_exact_pair_count": int(sum(host_pair_counter.values())),
        "device_predicate_pair_count": int(sum(device_pair_counter.values())),
        "pair_multiset_match_host_exact": bool(pair_multiset_match),
        "pair_missing_from_device_sample": pair_missing_sample,
        "pair_extra_on_device_sample": pair_extra_sample,
        "host_group_count": len(host_counts),
        "device_group_count": len(device_counts),
        "group_counts_match_host": bool(group_counts_match),
        "missing_group_key_count": len(missing_keys),
        "extra_group_key_count": len(extra_keys),
        "mismatched_group_value_count": len(mismatched_values),
        "device_predicate_boundary": {
            "device_predicate_columns_produced": True,
            "host_refinement_used_to_produce_device_columns": False,
            "host_exact_used_only_as_oracle": True,
            "device_predicate_matches_host_exact_on_this_dataset": bool(pair_multiset_match and group_counts_match),
            "universal_exact_predicate_claim_authorized": False,
            "native_page_plan_handle_used": False,
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
            "universal_device_exact_claim_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3420 device-predicate page equivalence probe.")
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
