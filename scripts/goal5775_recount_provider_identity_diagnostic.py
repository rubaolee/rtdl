#!/usr/bin/env python3
"""Independent reconstruction of the Goal5775 Home causal screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics


EXPECTED_LANES = {
    "triangle__rt_1a2", "triangle__rt_2a1", "raydb__q21",
    "librts__range_rows", "librts__overlap_filter", "rtnn__ranked_window",
    "rtdbscan__components", "xhd__global_witness",
    "rayjoin__point_location", "rayjoin__segment_pairs",
    "rayjoin__grouped_events", "rtbh__force", "particle__cell_transition",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    value = json.loads(path.read_text())
    if value.get("schema") != "rtdl.goal5775.home_provider_identity_diagnostic.v1":
        raise ValueError(f"wrong diagnostic schema: {path}")
    if value.get("observation_only") is not True \
            or value.get("formal_performance_row_created") is not False \
            or value.get("predicted_saving_claimed") is not False:
        raise ValueError(f"diagnostic claim boundary changed: {path}")
    rows = value.get("rows")
    if not isinstance(rows, list) or {row.get("lane_id") for row in rows} != EXPECTED_LANES:
        raise ValueError(f"diagnostic lane universe changed: {path}")
    return value


def recount(baseline_path: Path, candidate_path: Path, output: Path) -> Path:
    baseline = _load(baseline_path)
    candidate = _load(candidate_path)
    if baseline["native_library_sha256"] != candidate["native_library_sha256"]:
        raise ValueError("diagnostic native identity changed")
    if baseline["repeat_per_lane"] != candidate["repeat_per_lane"]:
        raise ValueError("diagnostic repetition count changed")
    baseline_rows = {row["lane_id"]: row for row in baseline["rows"]}
    candidate_rows = {row["lane_id"]: row for row in candidate["rows"]}
    rows = []
    for lane_id in sorted(EXPECTED_LANES):
        left = baseline_rows[lane_id]
        right = candidate_rows[lane_id]
        left_calls = left["calls"]
        right_calls = right["calls"]
        if len(left_calls) != len(right_calls) or not left_calls:
            raise ValueError(f"{lane_id}: call count mismatch")
        for base_call, candidate_call in zip(left_calls, right_calls, strict=True):
            if base_call["call_index"] != candidate_call["call_index"] \
                    or base_call["output_sha256"] != candidate_call["output_sha256"]:
                raise ValueError(f"{lane_id}: dynamic request/output drift")
            for call in (base_call, candidate_call):
                if call["provider_library_sha256"] != baseline["native_library_sha256"]:
                    raise ValueError(f"{lane_id}: receipt provider drift")
        if len({call["receipt_sha256"] for call in left_calls}) != len(left_calls) \
                or len({call["receipt_sha256"] for call in right_calls}) != len(right_calls):
            raise ValueError(f"{lane_id}: traversal receipts were reused")
        base_seconds = statistics.median(
            float(call["registered_seconds"]) for call in left_calls)
        candidate_seconds = statistics.median(
            float(call["registered_seconds"]) for call in right_calls)
        rows.append({
            "lane_id": lane_id,
            "app": left["app"],
            "paper_algorithm": left["paper_algorithm"],
            "baseline_median_seconds": base_seconds,
            "candidate_median_seconds": candidate_seconds,
            "diagnostic_baseline_over_candidate": base_seconds / candidate_seconds,
            "diagnostic_absolute_reduction_seconds": base_seconds - candidate_seconds,
            "baseline_native_sha_function_calls": left[
                "native_provider_sha256_function_calls"],
            "baseline_native_read_bytes_calls": left[
                "native_provider_read_bytes_calls"],
            "candidate_native_sha_function_calls": right[
                "native_provider_sha256_function_calls"],
            "candidate_native_read_bytes_calls": right[
                "native_provider_read_bytes_calls"],
            "output_digest_sequence": [call["output_sha256"] for call in left_calls],
        })
    if not all(
        row["baseline_native_sha_function_calls"] > 0
        and row["candidate_native_sha_function_calls"] == 0
        and row["candidate_native_read_bytes_calls"] == 0
        for row in rows
    ):
        raise ValueError("provider reread elimination contract not observed")
    payload = {
        "schema": "rtdl.goal5775.home_provider_identity_diagnostic_recount.v1",
        "status": "PASS__GENERIC_PROVIDER_REREADS_ELIMINATED",
        "observation_only": True,
        "formal_performance_row_created": False,
        "baseline_sha256": _sha(baseline_path),
        "candidate_sha256": _sha(candidate_path),
        "native_library_sha256": baseline["native_library_sha256"],
        "lane_count": len(rows),
        "call_count_per_variant": sum(len(row["output_digest_sequence"]) for row in rows),
        "all_outputs_identical": True,
        "all_receipts_fresh": True,
        "rows": rows,
        "summary": {
            "diagnostic_speedup_median": statistics.median(
                row["diagnostic_baseline_over_candidate"] for row in rows),
            "diagnostic_speedup_min": min(
                row["diagnostic_baseline_over_candidate"] for row in rows),
            "diagnostic_speedup_max": max(
                row["diagnostic_baseline_over_candidate"] for row in rows),
            "absolute_reduction_median_seconds": statistics.median(
                row["diagnostic_absolute_reduction_seconds"] for row in rows),
            "baseline_native_sha_function_calls": sum(
                row["baseline_native_sha_function_calls"] for row in rows),
            "baseline_native_read_bytes_calls": sum(
                row["baseline_native_read_bytes_calls"] for row in rows),
            "candidate_native_sha_function_calls": 0,
            "candidate_native_read_bytes_calls": 0,
        },
        "claim_boundary": {
            "paired_formal_performance_claimed": False,
            "modern_rtx_claimed": False,
            "nine_app_full_scale_claimed": False,
            "predicted_saving_claimed": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(recount(args.baseline, args.candidate, args.output))


if __name__ == "__main__":
    main()
