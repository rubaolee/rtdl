#!/usr/bin/env python3
"""Independent raw-observation recount for Goal5779."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(path: Path) -> dict[str, object]:
    source = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    provider_shas = set()
    for expected_index, row in enumerate(source["rows"]):
        if row["row_index"] != expected_index or len(row["observations"]) != 16:
            raise RuntimeError("row index/pair-count drift")
        values = []
        for expected_pair, item in enumerate(row["observations"]):
            if item["pair_index"] != expected_pair:
                raise RuntimeError("pair index drift")
            expected_order = (
                ["handwritten_direct_optix_control", "generated_v4"]
                if expected_pair % 2 == 0
                else ["generated_v4", "handwritten_direct_optix_control"])
            if item["order"] != expected_order:
                raise RuntimeError("ABBA order drift")
            ratio = (item["handwritten_control_seconds"] /
                     item["generated_v4_seconds"])
            if not all(math.isfinite(value) and value > 0.0 for value in (
                    item["handwritten_control_seconds"],
                    item["generated_v4_seconds"], ratio)):
                raise RuntimeError("nonpositive or nonfinite observation")
            if abs(ratio - item["handwritten_over_generated_ratio"]) > 1e-15:
                raise RuntimeError("stored ratio drift")
            values.append(ratio)
        rng = random.Random(57_790_000 + expected_index)
        draws = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(10000))
        median = statistics.median(values); ci = [draws[249], draws[9749]]
        if abs(median - row["paired_ratio_median"]) > 1e-15 \
                or any(abs(a - b) > 1e-15 for a, b in zip(ci, row["bootstrap_ci95"])):
            raise RuntimeError("primary statistic drift")
        generated_output = row["functional"]["generated_v4"]["output_sha256"]
        control_output = row["functional"][
            "handwritten_direct_optix_control"]["output_sha256"]
        if generated_output != control_output:
            raise RuntimeError("functional output digest mismatch")
        for name in ("generated_v4", "handwritten_direct_optix_control"):
            receipt = row["functional"][name]["traversal_receipt"]
            snapshot = receipt["native_snapshot"]
            provider_shas.add(receipt["provider_library_sha256"])
            if receipt["physical_executor_classification"] != \
                    "optix_traversal_observed" \
                    or not receipt["expected_program_observed_at_receipt_edge"] \
                    or snapshot["attempted_launch_count"] <= 0 \
                    or snapshot["attempted_launch_count"] != snapshot["successful_launch_count"] \
                    or snapshot["successful_launch_count"] != snapshot["complete_context_launch_count"] \
                    or snapshot["failed_launch_count"] \
                    or snapshot["incomplete_context_launch_count"] \
                    or snapshot["pending_context_at_finish"] \
                    or snapshot["session_error"] \
                    or not snapshot["first_traversable"] \
                    or not snapshot["last_traversable"] \
                    or snapshot["raygen_invocation_count"] <= 0:
                raise RuntimeError("functional receipt drift")
        rows.append({
            "row_index": expected_index, "family_id": row["family_id"],
            "paired_ratio_median": median, "bootstrap_ci95": ci,
            "competitive": ci[0] >= 0.95,
        })
    return {
        "schema": "rtdl.goal5779.independent_recount.v1",
        "source_path": str(path.resolve()), "source_sha256": _sha(path),
        "rows": rows,
        "summary": {"row_count": len(rows),
                    "competitive_count": sum(x["competitive"] for x in rows),
                    "failed_count": sum(not x["competitive"] for x in rows),
                    "distinct_provider_library_count": len(provider_shas),
                    "broad_controlled_audit_competitiveness": all(
                        x["competitive"] for x in rows)},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    payload = run(Path(args.result))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    output.write_bytes(data.encode("utf-8"))
    print(json.dumps({"status": "PASS", "output": str(output.resolve()),
                      "sha256": hashlib.sha256(data.encode()).hexdigest(),
                      "summary": payload["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
