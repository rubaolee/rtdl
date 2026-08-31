#!/usr/bin/env python3
"""Independent raw recount for Goal5780's observation-only ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    if raw["status"] != "COMPLETE__OBSERVATION_ONLY__NO_REPAIR_AUTHORIZED":
        raise RuntimeError("unexpected Goal5780 status")
    observations = list(raw["observations"])
    if len(observations) != 8:
        raise RuntimeError("Goal5780 must contain four observations per method")
    expected_orders = {
        0: ("v2", "v4"), 1: ("v4", "v2"),
        2: ("v2", "v4"), 3: ("v4", "v2"),
    }
    for block, order in expected_orders.items():
        actual = tuple(row["method"] for row in sorted(
            (row for row in observations if int(row["block"]) == block),
            key=lambda row: int(row["order"]),
        ))
        if actual != order:
            raise RuntimeError(f"block {block} is not strict alternating AB/BA")
    if len({row["output_sha256"] for row in observations}) != 1:
        raise RuntimeError("cross-method output digest mismatch")
    if not all(_receipt_ok(dict(row["traversal_receipt"]))
               for row in observations):
        raise RuntimeError("behavioral true-OptiX receipt mismatch")
    if len({row["traversal_receipt"]["provider_library_sha256"]
            for row in observations}) != 1:
        raise RuntimeError("more than one native provider in Goal5780")

    for row in observations:
        accounting = dict(row["mutually_exclusive_accounting"])
        observed = sum(float(value) for name, value in accounting.items()
                       if name.endswith("observed_not_saving"))
        registered = float(
            row["complete_endpoint_seconds_profiled_not_formal"]
            if row["method"] == "v2"
            else row["registered_endpoint_seconds_profiled_not_formal"]
        )
        if abs(observed - registered) > max(1.0e-6, registered * 1.0e-5):
            raise RuntimeError("mutually exclusive accounting does not reconcile")
        if abs(float(accounting["reconciled_complete_seconds"]) - registered) \
                > max(1.0e-6, registered * 1.0e-5):
            raise RuntimeError("stored reconciliation mismatch")

    v2 = [float(row["complete_endpoint_seconds_profiled_not_formal"])
          for row in observations if row["method"] == "v2"]
    v4 = [float(row["registered_endpoint_seconds_profiled_not_formal"])
          for row in observations if row["method"] == "v4"]
    v4_rows = [row for row in observations if row["method"] == "v4"]
    category_names = sorted(
        name for name in v4_rows[0]["mutually_exclusive_accounting"]
        if name.endswith("observed_not_saving"))
    category_medians = {
        name: statistics.median(float(
            row["mutually_exclusive_accounting"][name]) for row in v4_rows)
        for name in category_names
    }
    summary = {
        "v2_complete_median_seconds_profiled_not_formal": statistics.median(v2),
        "v4_registered_endpoint_median_seconds_profiled_not_formal": statistics.median(v4),
        "v4_minus_v2_median_endpoint_delta_seconds_profiled_not_formal": (
            statistics.median(v4) - statistics.median(v2)),
        "v4_category_medians_observed_not_saving": category_medians,
        "output_digest": observations[0]["output_sha256"],
        "native_library_sha256": observations[0][
            "traversal_receipt"]["provider_library_sha256"],
        "all_eight_receipts_behaviorally_true_optix": True,
        "all_eight_outputs_equal": True,
        "all_eight_accounting_rows_reconcile": True,
    }
    submitted = raw["summary"]
    for name in (
        "v2_complete_median_seconds_profiled_not_formal",
        "v4_registered_endpoint_median_seconds_profiled_not_formal",
        "v4_minus_v2_median_endpoint_delta_seconds_profiled_not_formal",
    ):
        if float(summary[name]) != float(submitted[name]):
            raise RuntimeError(f"submitted summary mismatch: {name}")
    result = {
        "schema": "rtdl.goal5780.independent_raw_recount.v1",
        "status": "PASS__RAW_LEDGER_REBUILT_INDEPENDENTLY",
        "imports_profile_implementation": False,
        "raw_sha256": _sha(args.raw),
        "observation_count": len(observations),
        "method_counts": {"v2": len(v2), "v4": len(v4)},
        "summary": summary,
        "claim_boundary": {
            "formal_performance_result_created": False,
            "observed_seconds_called_saving": False,
            "repair_authorized_or_implemented": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": result["status"], "sha256": _sha(args.output),
        "summary": summary,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
