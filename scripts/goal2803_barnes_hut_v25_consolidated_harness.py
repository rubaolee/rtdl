from __future__ import annotations

import argparse
import contextlib
import io
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from scripts.goal2642_barnes_hut_embree_vs_optix_lowering_perf import run_case  # noqa: E402


GOAL2803_ENTRYPOINT_VERSION = "rtdl.goal2803.barnes_hut_v2_5_consolidated_harness.v1"
DEFAULT_CASES = ((512, 16), (2048, 32), (8192, 32))
DEFAULT_REPEATS = 3
DEFAULT_VECTOR_WARMUPS = 2
CLAIM_BOUNDARY = {
    "canonical_consolidated_harness": True,
    "public_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "paper_reproduction_claim_authorized": False,
    "paper_speedup_claim_authorized": False,
    "authors_code_comparison_authorized": False,
    "triton_vector_sum_auto_selection_authorized": False,
    "native_engine_customization": False,
}


def _log(message: str) -> None:
    print(f"[goal2803] {message}", flush=True)


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median for empty timings")
    return float(statistics.median(values))


def _run_membership_cases(
    *,
    cases: tuple[tuple[int, int], ...],
    repeats: int,
    validate_all_cases: bool,
    suppress_case_json: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (body_count, bucket_size) in enumerate(cases):
        validate_case = bool(validate_all_cases or index == 0)
        _log(
            "membership case "
            f"{index + 1}/{len(cases)}: bodies={body_count}, bucket={bucket_size}, "
            f"repeats={repeats}, validate={validate_case}"
        )
        start = time.perf_counter()
        with contextlib.redirect_stdout(io.StringIO()) if suppress_case_json else contextlib.nullcontext():
            case = run_case(
                body_count=int(body_count),
                bucket_size=int(bucket_size),
                theta=0.5,
                repeats=int(repeats),
                validate=validate_case,
            )
        embree = case["backends"]["embree"]
        optix = case["backends"]["optix"]
        row = {
            "body_count": int(body_count),
            "bucket_size": int(bucket_size),
            "frontier_row_count": int(optix["frontier_row_count"]),
            "near_zone_candidate_row_count": int(optix["near_zone_candidate_row_count"]),
            "rows_match_between_backends": bool(case["rows_match_between_backends"]),
            "optix_rt_core_accelerated": bool(optix["rt_core_accelerated"]),
            "embree_total_sec_median": float(embree["total_sec_median"]),
            "optix_total_sec_median": float(optix["total_sec_median"]),
            "optix_total_speedup_vs_embree": float(case["speedups_optix_vs_embree"]["total"]),
            "embree_frontier_lowering_sec_median": float(embree["frontier_lowering_sec_median"]),
            "optix_frontier_lowering_sec_median": float(optix["frontier_lowering_sec_median"]),
            "optix_frontier_lowering_speedup_vs_embree": float(
                case["speedups_optix_vs_embree"]["frontier_lowering"]
            ),
            "embree_membership_wrapper_sec_median": float(embree["membership_wrapper_sec_median"]),
            "optix_membership_wrapper_sec_median": float(optix["membership_wrapper_sec_median"]),
            "optix_membership_wrapper_speedup_vs_embree": float(
                case["speedups_optix_vs_embree"]["membership_wrapper"]
            ),
            "validation_skipped": bool(optix["validation_skipped"]),
            "case_elapsed_sec": time.perf_counter() - start,
        }
        rows.append(row)
        _log(
            "membership case done: "
            f"bodies={body_count}, rows_match={row['rows_match_between_backends']}, "
            f"rt_core={row['optix_rt_core_accelerated']}, "
            f"membership_speedup={row['optix_membership_wrapper_speedup_vs_embree']:.3f}x, "
            f"elapsed={row['case_elapsed_sec']:.2f}s"
        )
    return rows


def _run_vector_sum_probe(
    *,
    group_count: int,
    rows_per_group: int,
    repeats: int,
    triton_groups_per_program: int,
    warmups: int,
) -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment dependent
        return {"status": "skipped", "reason": f"torch import failed: {exc}"}
    if not torch.cuda.is_available():  # pragma: no cover - environment dependent
        return {"status": "skipped", "reason": "torch cuda is not available"}

    device = "cuda"
    group_count = int(group_count)
    rows_per_group = int(rows_per_group)
    row_count = group_count * rows_per_group
    base = torch.arange(row_count, dtype=torch.float64, device=device)
    group_ids = torch.arange(group_count, dtype=torch.int64, device=device).repeat_interleave(rows_per_group)
    row_offsets = torch.arange(0, row_count + 1, rows_per_group, dtype=torch.int64, device=device)
    values_x = torch.sin(base * 0.001) + 0.25 * torch.cos(base * 0.0003)
    values_y = torch.cos(base * 0.0007) - 0.125 * torch.sin(base * 0.0002)

    columns_with_offsets = {
        "group_ids": group_ids,
        "row_offsets": row_offsets,
        "values_x": values_x,
        "values_y": values_y,
    }
    columns_without_offsets = {
        "group_ids": group_ids,
        "values_x": values_x,
        "values_y": values_y,
    }

    torch_times: list[float] = []
    triton_times: list[float] = []
    torch_result = None
    triton_result = None

    _log(
        "vector-sum probe: "
        f"groups={group_count}, rows_per_group={rows_per_group}, repeats={repeats}, warmups={warmups}"
    )
    for index in range(int(warmups)):
        _log(f"vector-sum warmup {index + 1}/{warmups}")
        rt.grouped_vector_sum_2d_partner_columns(
            columns_without_offsets,
            group_count=group_count,
            partner="torch",
            return_metadata=True,
        )
        rt.grouped_vector_sum_2d_partner_columns(
            columns_with_offsets,
            group_count=group_count,
            partner="triton",
            triton_offset_groups_per_program=triton_groups_per_program,
            return_metadata=True,
        )
    torch.cuda.synchronize()

    for index in range(int(repeats)):
        _log(f"vector-sum timed repeat {index + 1}/{repeats}: torch")
        torch.cuda.synchronize()
        start = time.perf_counter()
        torch_result = rt.grouped_vector_sum_2d_partner_columns(
            columns_without_offsets,
            group_count=group_count,
            partner="torch",
            return_metadata=True,
        )
        torch.cuda.synchronize()
        torch_times.append(time.perf_counter() - start)

        _log(f"vector-sum timed repeat {index + 1}/{repeats}: triton")
        torch.cuda.synchronize()
        start = time.perf_counter()
        triton_result = rt.grouped_vector_sum_2d_partner_columns(
            columns_with_offsets,
            group_count=group_count,
            partner="triton",
            triton_offset_groups_per_program=triton_groups_per_program,
            return_metadata=True,
        )
        torch.cuda.synchronize()
        triton_times.append(time.perf_counter() - start)

    assert torch_result is not None and triton_result is not None
    matches = bool(
        torch.allclose(
            triton_result["columns"]["sum_x"],
            torch_result["columns"]["sum_x"],
            rtol=1.0e-9,
            atol=1.0e-9,
        )
        and torch.allclose(
            triton_result["columns"]["sum_y"],
            torch_result["columns"]["sum_y"],
            rtol=1.0e-9,
            atol=1.0e-9,
        )
    )
    torch_median = _median(torch_times)
    triton_median = _median(triton_times)
    _log(
        "vector-sum probe done: "
        f"matches={matches}, torch={torch_median:.6f}s, "
        f"triton={triton_median:.6f}s, ratio={triton_median / torch_median if torch_median > 0.0 else float('inf'):.3f}x"
    )
    return {
        "status": "pass" if matches else "mismatch",
        "group_count": group_count,
        "rows_per_group": rows_per_group,
        "row_count": row_count,
        "torch_median_sec": torch_median,
        "triton_median_sec": triton_median,
        "triton_over_torch_ratio": triton_median / torch_median if torch_median > 0.0 else None,
        "torch_faster": torch_median < triton_median,
        "matches_torch": matches,
        "warmups": int(warmups),
        "triton_metadata": triton_result["metadata"],
        "torch_metadata": torch_result["metadata"],
    }


def run_goal2803_barnes_hut_consolidated_harness(
    *,
    cases: tuple[tuple[int, int], ...] = DEFAULT_CASES,
    repeats: int = DEFAULT_REPEATS,
    vector_group_count: int = 8192,
    vector_rows_per_group: int = 16,
    triton_groups_per_program: int = 1,
    vector_warmups: int = DEFAULT_VECTOR_WARMUPS,
    validate_all_cases: bool = False,
    suppress_case_json: bool = True,
) -> dict[str, Any]:
    started = time.perf_counter()
    if repeats < 1:
        raise ValueError("repeats must be positive")
    if vector_warmups < 0:
        raise ValueError("vector_warmups must be non-negative")
    _log(
        "starting Barnes-Hut consolidated harness: "
        f"cases={cases}, repeats={repeats}, validate_all_cases={validate_all_cases}"
    )
    membership_rows = _run_membership_cases(
        cases=cases,
        repeats=repeats,
        validate_all_cases=validate_all_cases,
        suppress_case_json=suppress_case_json,
    )
    vector_sum = _run_vector_sum_probe(
        group_count=vector_group_count,
        rows_per_group=vector_rows_per_group,
        repeats=repeats,
        triton_groups_per_program=triton_groups_per_program,
        warmups=vector_warmups,
    )

    membership_ok = all(
        row["rows_match_between_backends"] and row["optix_rt_core_accelerated"]
        for row in membership_rows
    )
    vector_ok = vector_sum.get("status") in {"pass", "skipped"}
    status = "pass" if membership_ok and vector_ok else "mismatch"
    return {
        "goal": "Goal2803",
        "entrypoint_version": GOAL2803_ENTRYPOINT_VERSION,
        "status": status,
        "app": "barnes_hut",
        "benchmark_track": "consolidated_membership_and_vector_sum",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cases": [{"body_count": body_count, "bucket_size": bucket_size} for body_count, bucket_size in cases],
        "repeats": int(repeats),
        "membership_validation_policy": (
            "all_cases" if validate_all_cases else "first_case_reference_validation_plus_all_case_embree_optix_shape_parity"
        ),
        "vector_warmups": int(vector_warmups),
        "membership_rows": membership_rows,
        "min_optix_membership_speedup_vs_embree": min(
            row["optix_membership_wrapper_speedup_vs_embree"] for row in membership_rows
        ),
        "max_optix_membership_speedup_vs_embree": max(
            row["optix_membership_wrapper_speedup_vs_embree"] for row in membership_rows
        ),
        "vector_sum": vector_sum,
        "triton_vector_sum_auto_selection_allowed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "elapsed_sec": time.perf_counter() - started,
    }


def _parse_case(text: str) -> tuple[int, int]:
    body_count, bucket_size = (int(part.strip()) for part in text.split(":", 1))
    if body_count <= 0 or bucket_size <= 0:
        raise argparse.ArgumentTypeError("case values must be positive")
    return body_count, bucket_size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2803 Barnes-Hut v2.5 consolidated harness.")
    parser.add_argument("--case", action="append", type=_parse_case, dest="cases")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--vector-group-count", type=int, default=8192)
    parser.add_argument("--vector-rows-per-group", type=int, default=16)
    parser.add_argument("--vector-warmups", type=int, default=DEFAULT_VECTOR_WARMUPS)
    parser.add_argument("--triton-groups-per-program", type=int, default=1)
    parser.add_argument(
        "--validate-all-cases",
        action="store_true",
        help="Run the reference frontier validation for every membership case instead of only the first case.",
    )
    parser.add_argument(
        "--show-run-case-json",
        action="store_true",
        help="Let the underlying Goal2642 case runner print its full per-case JSON.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    cases = tuple(args.cases) if args.cases else DEFAULT_CASES
    payload = run_goal2803_barnes_hut_consolidated_harness(
        cases=cases,
        repeats=args.repeats,
        vector_group_count=args.vector_group_count,
        vector_rows_per_group=args.vector_rows_per_group,
        triton_groups_per_program=args.triton_groups_per_program,
        vector_warmups=args.vector_warmups,
        validate_all_cases=args.validate_all_cases,
        suppress_case_json=not args.show_run_case_json,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
