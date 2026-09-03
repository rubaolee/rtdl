"""Create-only controller for Goal5842's causal admission cohort."""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .contracts import (
    BOOTSTRAP_DRAWS,
    BOOTSTRAP_LOWER_INDEX,
    BOOTSTRAP_SEED_BASE,
    BOOTSTRAP_UPPER_INDEX,
    CAUSAL_BLOCKS,
    CHECK_OFF,
    CHECK_ON,
    CONTROLLER_RESULT_SCHEMA,
    digest,
)
from .runtime import (
    create_json,
    create_text,
    load_execution_authority,
    validate_worker_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
ROUTE_PHASE = "route_declaration_and_artifact_binding"
CAUSAL_PHASE = "provider_projection_and_public_admission_or_unchecked_construction"


def integer_median(values: list[int]) -> int:
    if not values or any(type(value) is not int for value in values):
        raise ValueError("integer median requires a nonempty integer vector")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def bootstrap_interval(values: list[int], *, seed: int) -> tuple[int, int]:
    if len(values) != CAUSAL_BLOCKS:
        raise ValueError(
            f"Goal5842 bootstrap requires exactly {CAUSAL_BLOCKS} block values"
        )
    random_source = random.Random(seed)
    draws = []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = [values[random_source.randrange(len(values))] for _ in values]
        draws.append(integer_median(sample))
    draws.sort()
    return draws[BOOTSTRAP_LOWER_INDEX], draws[BOOTSTRAP_UPPER_INDEX]


def summarize(receipts: list[dict[str, Any]]) -> list[dict[str, object]]:
    tasks = []
    for task_index, task in enumerate(dict.fromkeys(row["task"] for row in receipts)):
        task_rows = [row for row in receipts if row["task"] == task]
        blocks = []
        for block in range(CAUSAL_BLOCKS):
            rows = [row for row in task_rows if row["block"] == block]
            on_rows = [row for row in rows if row["arm"] == CHECK_ON]
            off_rows = [row for row in rows if row["arm"] == CHECK_OFF]
            if len(on_rows) != 2 or len(off_rows) != 2:
                raise RuntimeError(f"incomplete causal block: {task} block {block}")
            on_causal = integer_median(
                [row["phases_ns"][CAUSAL_PHASE] for row in on_rows]
            )
            off_causal = integer_median(
                [row["phases_ns"][CAUSAL_PHASE] for row in off_rows]
            )
            on_route = integer_median(
                [row["phases_ns"][ROUTE_PHASE] for row in on_rows]
            )
            off_route = integer_median(
                [row["phases_ns"][ROUTE_PHASE] for row in off_rows]
            )
            on_total = integer_median(
                [row["registered_admission_total_ns"] for row in on_rows]
            )
            off_total = integer_median(
                [row["registered_admission_total_ns"] for row in off_rows]
            )
            blocks.append(
                {
                    "block": block,
                    "check_on_causal_phase_median_ns": on_causal,
                    "check_off_causal_phase_median_ns": off_causal,
                    "causal_phase_on_minus_off_ns": on_causal - off_causal,
                    "route_declaration_on_minus_off_ns": on_route - off_route,
                    "total_capability_on_minus_off_ns": on_total - off_total,
                }
            )
        causal_deltas = [row["causal_phase_on_minus_off_ns"] for row in blocks]
        total_deltas = [row["total_capability_on_minus_off_ns"] for row in blocks]
        lower, upper = bootstrap_interval(
            causal_deltas, seed=BOOTSTRAP_SEED_BASE + task_index
        )
        total_lower, total_upper = bootstrap_interval(
            total_deltas, seed=BOOTSTRAP_SEED_BASE + 100 + task_index
        )
        tasks.append(
            {
                "task": task,
                "worker_count": len(task_rows),
                "block_count": len(blocks),
                "check_on_causal_phase_median_ns": integer_median(
                    [
                        row["phases_ns"][CAUSAL_PHASE]
                        for row in task_rows
                        if row["arm"] == CHECK_ON
                    ]
                ),
                "check_off_causal_phase_median_ns": integer_median(
                    [
                        row["phases_ns"][CAUSAL_PHASE]
                        for row in task_rows
                        if row["arm"] == CHECK_OFF
                    ]
                ),
                "primary_causal_phase_delta_median_ns": integer_median(causal_deltas),
                "primary_causal_phase_delta_bootstrap_95_percent_ns": [lower, upper],
                "route_declaration_negative_control_delta_median_ns": integer_median(
                    [row["route_declaration_on_minus_off_ns"] for row in blocks]
                ),
                "secondary_total_capability_delta_median_ns": integer_median(
                    total_deltas
                ),
                "secondary_total_capability_delta_bootstrap_95_percent_ns": [
                    total_lower,
                    total_upper,
                ],
                "block_rows": blocks,
                "ratio_to_check_off_reported": False,
            }
        )
    return tasks


def run_worker(
    *,
    python: str,
    preregistration: Path,
    authority: Path,
    row: dict[str, Any],
    worker_dir: Path,
    prereg: dict[str, Any],
    authority_value: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    worker_dir.mkdir(parents=False, exist_ok=False)
    output = worker_dir / "receipt.json"
    command = [
        python,
        "-m",
        "experiments.goal5842_causal_admission.admission_worker",
        "--preregistration",
        str(preregistration),
        "--execution-authority",
        str(authority),
        "--worker-id",
        row["worker_id"],
        "--output",
        str(output),
    ]
    create_json(
        worker_dir / "command.json",
        {
            "schema": "rtdl.goal5842.worker_command.v1",
            "worker_id": row["worker_id"],
            "argv": command,
        },
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        (
            str(ROOT / "src"),
            str(ROOT),
            environment.get("PYTHONPATH", ""),
        )
    )
    started = time.perf_counter_ns()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    process_wall_ns = time.perf_counter_ns() - started
    create_text(worker_dir / "stdout.txt", completed.stdout)
    create_text(worker_dir / "stderr.txt", completed.stderr)
    if completed.returncode != 0:
        create_json(
            worker_dir / "failure.json",
            {
                "schema": "rtdl.goal5842.worker_failure.v1",
                "worker_id": row["worker_id"],
                "returncode": completed.returncode,
                "process_wall_ns": process_wall_ns,
                "retry_permitted": False,
            },
        )
        raise RuntimeError(f"formal causal worker failed: {row['worker_id']}")
    receipt = json.loads(output.read_text(encoding="utf-8"))
    validate_worker_receipt(
        receipt,
        prereg=prereg,
        authority=authority_value,
        row=row,
    )
    return receipt, process_wall_ns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    prereg_path = args.preregistration.resolve()
    authority_path = args.execution_authority.resolve()
    prereg, authority = load_execution_authority(
        authority_path,
        preregistration_path=prereg_path,
        root=ROOT,
        require_clean_repository=True,
    )
    if Path(args.python).resolve(strict=True) != Path(
        authority["host"]["python_executable"]
    ).resolve(strict=True):
        raise RuntimeError("causal worker Python executable differs from authority")
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    create_json(
        output_root / "transaction_start.json",
        {
            "schema": "rtdl.goal5842.transaction_start.v1",
            "status": "WORKER_ZERO_WILL_FOLLOW",
            "source_commit": authority["source_commit"],
            "preregistration_sha256": prereg["preregistration_sha256"],
            "execution_authority_sha256": authority["authority_sha256"],
            "formal_worker_retry": False,
            "formal_worker_drop": False,
        },
    )
    receipts = []
    process_rows = []
    for index, row in enumerate(prereg["causal_schedule"]):
        receipt, process_wall_ns = run_worker(
            python=args.python,
            preregistration=prereg_path,
            authority=authority_path,
            row=row,
            worker_dir=output_root / f"{index:03d}_{row['worker_id']}",
            prereg=prereg,
            authority_value=authority,
        )
        receipts.append(receipt)
        process_rows.append(
            {
                "worker_id": row["worker_id"],
                "process_wall_ns": process_wall_ns,
            }
        )
    summaries = summarize(receipts)
    result: dict[str, object] = {
        "schema": CONTROLLER_RESULT_SCHEMA,
        "status": "PASS__CAUSAL_ADMISSION_COHORT_COMPLETE",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "worker_count": len(receipts),
        "registered_primary_observation_count": len(receipts),
        "task_summaries": summaries,
        "process_wall_rows": process_rows,
        "process_wall_is_not_causal_estimand": True,
        "normal_reference_admission_after_estimand": True,
        "gpu_execution_count": 0,
        "identity_witness_required_before_claim": True,
        "external_review_or_consensus": False,
    }
    result["result_sha256"] = digest(result)
    create_json(output_root / "result.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
