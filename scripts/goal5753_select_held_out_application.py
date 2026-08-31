#!/usr/bin/env python3
"""Select Goal5753's held-out application from frozen NIST beacon entropy."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


DOMAIN = b"rtdl-v4-goal5753-held-out-selection-v1\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_key(child, key)
            if found is not None:
                return found
    return None


def timestamp_ms(value: Any) -> int:
    if isinstance(value, (int, float)):
        number = int(value)
        return number if number > 10_000_000_000 else number * 1000
    if not isinstance(value, str):
        raise ValueError(f"unsupported beacon timestamp: {value!r}")
    text = value.replace("Z", "+00:00")
    return int(dt.datetime.fromisoformat(text).timestamp() * 1000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, required=True)
    parser.add_argument("--beacon-response", type=Path, required=True)
    parser.add_argument("--core-freeze-sha256", required=True)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--freeze-commit-time-ms", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    universe = json.loads(args.universe.read_text(encoding="utf-8"))
    beacon = json.loads(args.beacon_response.read_text(encoding="utf-8"))
    candidates = universe["eligible_candidates_sorted"]
    if not candidates:
        raise ValueError("empty candidate universe")

    # The target minute is committed before it exists: the second UTC minute
    # boundary after the freeze commit.  This prevents pulse cherry-picking.
    target_ms = (args.freeze_commit_time_ms // 60_000 + 2) * 60_000
    output_value = str(find_key(beacon, "outputValue") or "").lower()
    if len(output_value) != 128 or any(ch not in "0123456789abcdef" for ch in output_value):
        raise ValueError("NIST beacon outputValue must be 512-bit hex")
    pulse_time_raw = find_key(beacon, "timeStamp")
    pulse_time_ms = timestamp_ms(pulse_time_raw)
    if not target_ms <= pulse_time_ms < target_ms + 60_000:
        raise ValueError(
            f"beacon pulse timestamp {pulse_time_ms} is outside committed target minute {target_ms}"
        )

    universe_sha = sha256(args.universe)
    material = (
        DOMAIN
        + args.core_freeze_sha256.encode("ascii")
        + b"\n"
        + universe_sha.encode("ascii")
        + b"\n"
        + output_value.encode("ascii")
        + b"\n"
    )
    digest = hashlib.sha256(material).hexdigest()
    selected_index = int(digest, 16) % len(candidates)
    selected = candidates[selected_index]

    result = {
        "schema": "rtdl.v4.goal5753.held_out_selection.v1",
        "status": "held_out_application_selected_and_irrevocably_frozen",
        "freeze_commit": args.freeze_commit,
        "freeze_commit_time_ms": args.freeze_commit_time_ms,
        "committed_target_minute_ms": target_ms,
        "core_freeze_sha256": args.core_freeze_sha256,
        "candidate_universe_sha256": universe_sha,
        "beacon_response_sha256": sha256(args.beacon_response),
        "beacon": {
            "time_stamp": pulse_time_raw,
            "time_stamp_ms": pulse_time_ms,
            "chain_index": find_key(beacon, "chainIndex"),
            "pulse_index": find_key(beacon, "pulseIndex"),
            "output_value": output_value,
        },
        "selection": {
            "domain": DOMAIN.decode("ascii").rstrip("\n"),
            "material_sha256": digest,
            "candidate_count": len(candidates),
            "selected_index_zero_based": selected_index,
            "selected_candidate": selected,
            "replacement_allowed": False,
        },
        "post_selection_change_policy": {
            "allowed": [
                "held_out_application_callback_source",
                "held_out_application_typed_schema",
                "held_out_application_input_output_glue",
                "held_out_application_independent_oracle",
                "held_out_application_tests_and_evidence_tools",
                "goal5753_reports_and_evidence",
            ],
            "forbidden": [
                "src_rtdsl_core_or_compiler",
                "callback_ir_or_verifier",
                "cpu_interpreter",
                "numba_codegen",
                "ptx_composer",
                "optix_wrapper_or_native",
                "partner_runtime_or_lifecycle",
                "toolchain_or_dependency_versions",
            ],
            "any_forbidden_diff_fails_exam": True,
        },
        "claim_boundary": {
            "expressibility_passed": False,
            "correctness_passed": False,
            "behavioral_true_optix_passed": False,
            "performance_claimed": False,
            "production_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
