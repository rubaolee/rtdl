#!/usr/bin/env python3
"""Freeze the independent cit-Patents replication before worker zero."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import v4_long_workload_replication_controller as controller


PRIOR_ARCHIVE_SHA256 = (
    "ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc"
)
PRIOR_FORMAL_SUMMARY_SHA256 = (
    "74c8196f6e6f8e3fc13f1d4bce312087950d1e38571909042815ff6470d0672d"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dry-run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--transaction-id", required=True)
    parser.add_argument(
        "--replication-scope", choices=controller.REPLICATION_SCOPES,
        required=True,
    )
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if not args.transaction_id.strip() or any(
            character.isspace() for character in args.transaction_id):
        raise ValueError("transaction ID must be nonempty and whitespace-free")

    config_path = args.config.resolve(strict=True)
    dry_path = args.dry_run_summary.resolve(strict=True)
    config = controller.read_object(config_path)
    controller.validate_config(config)
    registered_machine = config["common"]["registered_machine"]
    if not controller.replication_scope_matches(
            args.replication_scope, registered_machine):
        raise PermissionError(
            "registered GPU does not match the declared replication scope")
    dry = controller.read_object(dry_path)
    if (
        dry.get("schema") != controller.SUMMARY_SCHEMA
        or dry.get("mode") != "dry-run"
        or dry.get("status") != "COMPLETE__DRY_RUN_PARITY_PASS"
        or dry.get("formal_worker_zero_reached") is not False
        or dry.get("config_sha256") != controller.sha256(config_path)
        or dry.get("controller_sha256")
            != controller.sha256(Path(controller.__file__).resolve())
        or dry.get("worker_sha256") != controller.sha256(controller.WORKER)
        or dry.get("worker_count") != 2
        or dry.get("valid_block_count") != 1
        or dry.get("retry_count") != 0
        or dry.get("discard_count") != 0
    ):
        raise PermissionError("dry-run result is not a valid replication authority")
    dry_cells = dry.get("cells")
    dry_rows = dry.get("rows")
    if not isinstance(dry_cells, list) or len(dry_cells) != 1 \
            or dry_cells[0].get("valid") is not True \
            or not isinstance(dry_rows, list) or len(dry_rows) != 2:
        raise PermissionError("dry-run input/output parity is incomplete")

    schedule = controller.schedule_payload(
        config_path, config, mode="formal")
    unit = config["units"][controller.UNIT_ID]
    first_worker = dry_rows[0].get("worker")
    if not isinstance(first_worker, dict):
        raise PermissionError("dry-run first worker is incomplete")
    input_identity = first_worker.get("input_identity")
    output_sha256 = first_worker.get("output_sha256")
    if not isinstance(input_identity, dict) or not isinstance(output_sha256, str):
        raise PermissionError("dry-run input/output identity is invalid")
    for row in dry_rows:
        worker = row.get("worker")
        if not isinstance(worker, dict) \
                or controller.digest(worker.get("input_identity")) \
                != controller.digest(input_identity) \
                or worker.get("output_sha256") != output_sha256:
            raise PermissionError("dry-run arm identity or output differs")

    payload = {
        "schema": controller.PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_REPLICATION_WORKER_ZERO",
        "transaction_id": args.transaction_id,
        "replication_scope": args.replication_scope,
        "formal_worker_zero_reached": False,
        "formal_result_precommitted": False,
        "formal_config_sha256": controller.sha256(config_path),
        "dry_run_summary_sha256": controller.sha256(dry_path),
        "controller_sha256": controller.sha256(
            Path(controller.__file__).resolve()),
        "worker_sha256": controller.sha256(controller.WORKER),
        "formal_schedule_sha256": controller.digest(schedule),
        "formal_worker_count": 16,
        "unit_id": controller.UNIT_ID,
        "endpoint": controller.ENDPOINT,
        "arms": list(controller.ARMS),
        "paired_blocks": 8,
        "block_orders": [list(row) for row in controller.BLOCK_ORDERS],
        "prepared_repetitions_per_worker": int(
            unit["prepared_repetitions"]),
        "prepared_warmups_per_worker": 1,
        "engineering_thresholds": controller.THRESHOLDS,
        "retry_allowed": False,
        "discard_allowed": False,
        "all_adverse_rows_retained": True,
        "registered_machine": config["common"]["registered_machine"],
        "cpu_affinity": config["common"]["cpu_affinity"],
        "unit": unit,
        "input_identity": input_identity,
        "input_identity_sha256": controller.digest(input_identity),
        "expected_output_sha256": output_sha256,
        "implementations": {
            arm: config["implementations"][arm]
            for arm in controller.ARMS
        },
        "prior_transaction": {
            "archive_sha256": PRIOR_ARCHIVE_SHA256,
            "formal_summary_sha256": PRIOR_FORMAL_SUMMARY_SHA256,
            "observed_median_new_v4_over_pyoptix": 1.057361,
            "observed_max_new_v4_over_pyoptix": 1.083735,
            "pooled_into_this_replication": False,
            "registered_gpu": controller.PRIOR_REGISTERED_GPU,
        },
        "selection_disclosure": (
            "This replication was requested after observing the prior result. "
            "It changes no source, input, algorithm, endpoint, repetitions, "
            "CPU affinity, output contract, or engineering threshold."
        ),
        "claim_boundary": (
            "This separately scheduled same-host temporal replication can "
            "test whether the registered cit-Patents/4M prepared A/C "
            "observation repeats on the original GPU. It is not an "
            "independent machine, application-coverage, broad language-"
            "overhead, or new-workload result and is never pooled with the "
            "prior transaction."
            if args.replication_scope == "same_host_temporal" else
            "This separately identified cross-GPU reproducibility transaction "
            "can test the exact cit-Patents/4M prepared A/C contract on a "
            "different physical GPU. It is not a same-host temporal replay, "
            "application-coverage, broad language-overhead, or new-workload "
            "result and is never pooled with the prior transaction."
        ),
    }
    controller.write_create(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "transaction_id": payload["transaction_id"],
        "output": str(args.output),
        "formal_schedule_sha256": payload["formal_schedule_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
