"""One fresh-process causal admission observation for Goal5842."""

from __future__ import annotations

import argparse
import gc
import json
import time
from pathlib import Path

from .contracts import CHECK_OFF, CHECK_ON, WORKER_RECEIPT_SCHEMA, digest
from .runtime import (
    create_json,
    load_execution_authority,
    schedule_row,
    validate_worker_receipt,
)
from .tasks import build_task, checker_off_program, program_signature

ROOT = Path(__file__).resolve().parents[2]


def measured(action):
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def run(args: argparse.Namespace) -> dict[str, object]:
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    row = schedule_row(prereg, args.worker_id)

    task = build_task(row["task"])

    gc.collect()
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        if row["arm"] == CHECK_ON:
            route, declaration_ns = measured(task.route_factory)
            program, generic_ns = measured(route.compile)
        elif row["arm"] == CHECK_OFF:
            route, declaration_ns = measured(task.route_factory)
            program, generic_ns = measured(lambda: checker_off_program(route))
        else:
            raise ValueError(f"unsupported causal arm: {row['arm']}")
    finally:
        if was_enabled:
            gc.enable()

    # This public admission runs only after the registered interval.  It is an
    # identity oracle, not common setup that can warm either causal arm.
    reference_program = route.compile()
    reference_signature = program_signature(reference_program)
    signature = program_signature(program)
    if signature != reference_signature:
        raise RuntimeError("causal arm changed the admitted program identity")
    receipt: dict[str, object] = {
        "schema": WORKER_RECEIPT_SCHEMA,
        "status": "PASS",
        "worker_id": row["worker_id"],
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "position": row["position"],
        "arm_sample_index": row["arm_sample_index"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": task.input_sha256,
        "program_signature": signature,
        "post_estimand_public_admission_signature": reference_signature,
        "normal_reference_admission_after_estimand": True,
        "garbage_collector_disabled_during_registered_phases": True,
        "clock": "time.perf_counter_ns",
        "phases_ns": {
            "route_declaration_and_artifact_binding": declaration_ns,
            "provider_projection_and_public_admission_or_unchecked_construction": generic_ns,
        },
        "registered_admission_total_ns": declaration_ns + generic_ns,
        "gpu_imported_or_executed": False,
    }
    receipt["receipt_sha256"] = digest(receipt)
    validate_worker_receipt(receipt, prereg=prereg, authority=authority, row=row)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
