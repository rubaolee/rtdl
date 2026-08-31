#!/usr/bin/env python3
"""Create-only Goal5790 static harness materializer.

This controller intentionally has no subprocess facility.  Goal5790 may freeze
and test a later Goal5791 cohort, but it cannot launch a target worker.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.goal5790_static_formal_contract import (
    EXECUTION_STATE,
    contract_document,
    contract_sha256,
    file_sha256,
    schedule,
    statistical_rows,
    validate_shared_freeze,
)


def execute_target_workers(*_args: object, **_kwargs: object) -> None:
    """Fail before any worker or output side effect."""

    raise PermissionError(
        "Goal5790 is static-only; target execution requires a distinct Goal5791 "
        "bundle, review, and exact owner authorization"
    )


def _write_json_create_only(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def prepare_static_draft(*, output_root: Path, shared_freeze_path: Path) -> Path:
    if output_root.exists():
        raise FileExistsError(output_root)
    shared = validate_shared_freeze(shared_freeze_path)
    output_root.mkdir(parents=False)
    contract_path = output_root / "FORMAL_CONTRACT.json"
    schedule_path = output_root / "SCHEDULE.json"
    gate_path = output_root / "EXECUTION_GATE.json"
    _write_json_create_only(contract_path, contract_document())
    _write_json_create_only(schedule_path, list(schedule()))
    _write_json_create_only(
        gate_path,
        {
            "schema": "rtdl.goal5790.static_execution_gate.v1",
            "goal": 5790,
            "execution_state": EXECUTION_STATE,
            "formal_contract_sha256": contract_sha256(),
            "shared_freeze_file_sha256": file_sha256(shared_freeze_path),
            "shared_freeze_content_sha256": shared[
                "shared_contract_freeze_sha256"
            ],
            "worker_count": len(schedule()),
            "independent_row_count": len(statistical_rows()),
            "target_worker_count": 0,
            "registered_target_timing_count": 0,
            "owner_authority_present": False,
            "retry_resume_replacement_allowed": False,
            "future_goal5791_must_use_a_new_exact_bundle_and_authority": True,
        },
    )
    _write_json_create_only(
        output_root / "STATIC_DRAFT_RECEIPT.json",
        {
            "schema": "rtdl.goal5790.static_controller_receipt.v1",
            "formal_contract_sha256": file_sha256(contract_path),
            "schedule_sha256": file_sha256(schedule_path),
            "execution_gate_sha256": file_sha256(gate_path),
            "target_workers_executed": 0,
            "registered_target_timings": 0,
            "create_only": True,
        },
    )
    return output_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--shared-freeze", type=Path, required=True)
    args = parser.parse_args()
    print(
        prepare_static_draft(
            output_root=args.output_root,
            shared_freeze_path=args.shared_freeze,
        )
    )


if __name__ == "__main__":
    main()
