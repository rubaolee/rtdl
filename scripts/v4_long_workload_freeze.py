#!/usr/bin/env python3
"""Freeze the long-workload config, dry run, and formal schedule pre-action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import v4_long_workload_controller as controller


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dry-run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    config_path = args.config.resolve(strict=True)
    dry_path = args.dry_run_summary.resolve(strict=True)
    config = controller.read_object(config_path)
    controller.validate_config(config)
    dry = controller.read_object(dry_path)
    if (
        dry.get("schema") != "rtdl.v4_long_workload.dry-run_summary.v1"
        or dry.get("status") != "PASS"
        or dry.get("formal_worker_zero_reached") is not False
        or dry.get("config_sha256") != controller.sha256(config_path)
        or dry.get("worker_count") != 15
        or dry.get("retry_count") != 0
        or dry.get("discard_count") != 0
    ):
        raise PermissionError("dry-run result is not a valid pre-action authority")
    schedule = controller.build_schedule(config, mode="formal")
    schedule_payload = {
        "schema": controller.SCHEDULE_SCHEMA,
        "mode": "formal",
        "config_sha256": controller.sha256(config_path),
        "controller_sha256": controller.sha256(Path(controller.__file__).resolve()),
        "worker_sha256": controller.sha256(controller.WORKER),
        "worker_count": len(schedule),
        "rows": schedule,
    }
    payload = {
        "schema": controller.PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_FORMAL_WORKER_ZERO",
        "formal_worker_zero_reached": False,
        "formal_config_sha256": controller.sha256(config_path),
        "dry_run_summary_sha256": controller.sha256(dry_path),
        "controller_sha256": controller.sha256(Path(controller.__file__).resolve()),
        "worker_sha256": controller.sha256(controller.WORKER),
        "formal_schedule_sha256": controller.digest(schedule_payload),
        "formal_worker_count": 240,
        "unit_count": 5,
        "endpoints": list(controller.ENDPOINTS),
        "arms": list(controller.ARMS),
        "paired_blocks": 8,
        "block_orders": [list(row) for row in controller.BLOCK_ORDERS],
        "engineering_thresholds": {
            "median_new_v4_over_pyoptix_max": 1.20,
            "every_block_new_v4_over_pyoptix_max": 1.35,
        },
        "retry_allowed": False,
        "discard_allowed": False,
        "all_adverse_rows_retained": True,
        "formal_result_precommitted": False,
        "units": config["units"],
        "implementations": config["implementations"],
        "registered_machine": config["common"]["registered_machine"],
        "cpu_affinity": config["common"].get("cpu_affinity"),
        "claim_boundary": (
            "This transaction can support only four repaired old-input units "
            "and one preselected cit-Patents/4M long graph unit. It is not a "
            "broad language-overhead, nine-application, or intrinsic-speed claim."
        ),
    }
    controller.write_create(args.output, payload)
    print(json.dumps({
        "status": payload["status"], "output": str(args.output),
        "formal_schedule_sha256": payload["formal_schedule_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
