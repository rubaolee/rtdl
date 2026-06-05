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


def _pairs_from_refined_columns(cp, columns: dict[str, object]) -> Counter[tuple[int, int]]:
    point_ids = cp.asnumpy(columns["point_id"]).tolist()
    shape_ids = cp.asnumpy(columns["shape_id"]).tolist()
    return Counter((int(point_id), int(shape_id)) for point_id, shape_id in zip(point_ids, shape_ids))


def _pairs_from_host_rows(rows: tuple[dict[str, int], ...]) -> Counter[tuple[int, int]]:
    return Counter((int(row["point_id"]), int(row["shape_id"])) for row in rows)


def _group_counts_from_refined_columns(cp, columns: dict[str, object], group_capacity: int) -> dict[int, int]:
    if int(columns["row_count"]) == 0:
        return {}
    point_ids = columns["point_id"].astype(cp.int64, copy=False)
    counts = cp.bincount(point_ids, minlength=int(group_capacity))
    keys = cp.nonzero(counts)[0]
    values = counts[keys]
    return {
        int(key): int(value)
        for key, value in zip(cp.asnumpy(keys).tolist(), cp.asnumpy(values).tolist())
    }


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
    stream_outputs = []
    try:
        host_counts: Counter[int] = Counter()
        refined_page_count_maps: list[dict[int, int]] = []
        page_records: list[PairColumnPageRecoveryRecord] = []
        host_pair_counter: Counter[tuple[int, int]] = Counter()
        refined_pair_counter: Counter[tuple[int, int]] = Counter()
        candidate_pair_count = 0
        dropped_candidate_count = 0
        max_point_id = max(int(point.id) for point in points) if points else 0

        for request in requests:
            page_points = tuple(request.slice(points))
            print(
                "[goal3421] RT candidate + CuPy refine page "
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
                    raise RuntimeError("CuPy-refined device predicate expected overflow retry_capacity_hint")
                recovered_columns = prepared.candidate_device_columns(page_points, max_rows=retry_hint)
                stream_outputs.append(recovered_columns)
            else:
                retry_hint = None
                recovered_columns = first_columns

            refined = rt.refine_closed_shape_membership_candidate_columns_exact_cupy(
                recovered_columns,
                page_points,
                shapes,
            )
            page_refined_pairs = _pairs_from_refined_columns(cp, refined)
            refined_pair_counter.update(page_refined_pairs)
            page_refined_counts = _group_counts_from_refined_columns(cp, refined, max_point_id + 1)
            refined_page_count_maps.append(page_refined_counts)
            candidate_pair_count += int(refined["candidate_row_count"])
            dropped_candidate_count += int(refined["dropped_candidate_row_count"])
            page_records.append(
                PairColumnPageRecoveryRecord(
                    request=request,
                    host_exact_rows=int(len(page_host_rows)),
                    first_capacity_status=first_status,
                    retry_used=retry_used,
                    retry_capacity_hint=None if retry_hint is None else int(retry_hint),
                    recovered_capacity_status=recovered_columns.capacity_status.to_metadata(),
                    grouped_source_row_count=int(refined["row_count"]),
                    grouped_row_count=int(len(page_refined_counts)),
                    grouped_overflow=False,
                    device_group_count=int(len(page_refined_counts)),
                )
            )
    finally:
        for columns in reversed(stream_outputs):
            columns.close()
        prepared.close()

    refined_counts = Counter(merge_grouped_count_maps(refined_page_count_maps))
    missing_keys = sorted(set(host_counts) - set(refined_counts))
    extra_keys = sorted(set(refined_counts) - set(host_counts))
    mismatched_values = sorted(
        point_id
        for point_id in set(host_counts) & set(refined_counts)
        if int(host_counts[point_id]) != int(refined_counts[point_id])
    )
    pair_missing_sample = _counter_diff_sample(host_pair_counter, refined_pair_counter)
    pair_extra_sample = _counter_diff_sample(refined_pair_counter, host_pair_counter)
    recovery_summary = summarize_page_recovery_records(page_records)
    pair_multiset_match = host_pair_counter == refined_pair_counter
    group_counts_match = refined_counts == host_counts
    return {
        "schema": "rtdl.goal3421.cupy_refined_device_predicate_page_probe.v1",
        "goal": 3421,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "contract": contract.to_metadata(),
        "recovery_summary": recovery_summary,
        "host_exact_pair_count": int(sum(host_pair_counter.values())),
        "rt_candidate_pair_count": int(candidate_pair_count),
        "cupy_refined_pair_count": int(sum(refined_pair_counter.values())),
        "dropped_candidate_pair_count": int(dropped_candidate_count),
        "pair_multiset_match_host_exact": bool(pair_multiset_match),
        "pair_missing_from_refined_sample": pair_missing_sample,
        "pair_extra_on_refined_sample": pair_extra_sample,
        "host_group_count": len(host_counts),
        "refined_group_count": len(refined_counts),
        "group_counts_match_host": bool(group_counts_match),
        "missing_group_key_count": len(missing_keys),
        "extra_group_key_count": len(extra_keys),
        "mismatched_group_value_count": len(mismatched_values),
        "refinement_boundary": {
            "rt_candidate_columns_produced": True,
            "cupy_device_refinement_used": True,
            "host_refinement_used_to_produce_refined_columns": False,
            "host_exact_used_only_as_oracle": True,
            "refined_columns_match_host_exact_on_this_dataset": bool(pair_multiset_match and group_counts_match),
            "native_exact_device_predicate_implemented": False,
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
            "native_exact_device_predicate_claim_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3421 RT candidate plus CuPy exact-refine page probe.")
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
