"""Independent structural recount of the Goal5783 Home receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-native-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    row = json.loads(args.receipt.read_text(encoding="utf-8"))
    lanes = [*row["cold_cases"], row["prepared"]]
    errors: list[str] = []
    for index, lane in enumerate(lanes):
        prefix = f"lane[{index}]"
        values = lane.get("input_values", [])
        intervals = lane.get("input_intervals", [])
        try:
            independently_expected = [
                min(range(int(left), int(right) + 1),
                    key=lambda item: (values[item], item))
                for left, right in intervals
            ]
        except (IndexError, TypeError, ValueError) as error:
            errors.append(f"{prefix}: malformed embedded input: {error}")
            independently_expected = []
        if lane.get("expected") != independently_expected:
            errors.append(f"{prefix}: submitted expected differs from raw recount")
        if not lane.get("matched") or lane.get("output") != independently_expected:
            errors.append(f"{prefix}: exact output mismatch")
        if lane.get("native_library_sha256") != args.expected_native_sha256:
            errors.append(f"{prefix}: native mismatch")
        receipt = lane.get("traversal_receipt", {})
        snapshot = receipt.get("native_snapshot", {})
        if receipt.get("physical_executor_classification") != "optix_traversal_observed":
            errors.append(f"{prefix}: no behavioral OptiX observation")
        if snapshot.get("successful_launch_count") != snapshot.get("complete_context_launch_count"):
            errors.append(f"{prefix}: successful/complete launch mismatch")
        for key in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ):
            if snapshot.get(key) != 0:
                errors.append(f"{prefix}: {key} is nonzero")
        if not snapshot.get("first_traversable") or not snapshot.get("raygen_invocation_count"):
            errors.append(f"{prefix}: missing traversable/raygen evidence")
    result = {
        "schema": "rtdl.goal5783.home_functional_independent_recount.v1",
        "receipt_sha256": sha(args.receipt),
        "lane_count": len(lanes),
        "exact_output_count": sum(
            lane.get("matched") and lane.get("output") == [
                min(range(int(left), int(right) + 1),
                    key=lambda item: (lane["input_values"][item], item))
                for left, right in lane["input_intervals"]
            ]
            for lane in lanes),
        "behavioral_true_optix_count": sum(
            lane.get("traversal_receipt", {}).get(
                "physical_executor_classification") == "optix_traversal_observed"
            for lane in lanes),
        "successful_launch_count": sum(
            lane["traversal_receipt"]["native_snapshot"]["successful_launch_count"]
            for lane in lanes),
        "raygen_invocation_count": sum(
            lane["traversal_receipt"]["native_snapshot"]["raygen_invocation_count"]
            for lane in lanes),
        "native_library_sha256": args.expected_native_sha256,
        "errors": errors,
        "all_gates_passed": not errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if errors:
        raise SystemExit("; ".join(errors))


if __name__ == "__main__":
    main()
