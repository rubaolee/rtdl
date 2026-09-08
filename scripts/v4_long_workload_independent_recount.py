#!/usr/bin/env python3
"""Independent, project-import-free recount of the 240-worker transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ARMS = ("old_v4", "new_v4", "pyoptix")
ENDPOINTS = ("complete", "prepared")
BLOCK_ORDERS = (
    ("old_v4", "new_v4", "pyoptix"),
    ("old_v4", "pyoptix", "new_v4"),
    ("new_v4", "old_v4", "pyoptix"),
    ("new_v4", "pyoptix", "old_v4"),
    ("pyoptix", "old_v4", "new_v4"),
    ("pyoptix", "new_v4", "old_v4"),
    ("old_v4", "new_v4", "pyoptix"),
    ("pyoptix", "new_v4", "old_v4"),
)
WORKER_MACHINE_SUPPLEMENTAL_FIELDS = frozenset({
    "hostname", "platform", "python", "python_executable",
})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def expected_schedule(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for unit_id, unit in config["units"].items():
        for endpoint in ENDPOINTS:
            repetitions = 1 if endpoint == "complete" \
                else int(unit["prepared_repetitions"])
            warmups = 0 if endpoint == "complete" else 1
            for block, order in enumerate(BLOCK_ORDERS):
                for position, arm in enumerate(order):
                    rows.append({
                        "ordinal": len(rows), "unit_id": unit_id,
                        "endpoint": endpoint, "block": block,
                        "position": position, "arm": arm,
                        "repetitions": repetitions, "warmups": warmups,
                    })
    if len(rows) != 240:
        raise ValueError("independent schedule does not contain 240 workers")
    return rows


def read_journal(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        if not isinstance(value, dict):
            raise TypeError(f"journal row is not an object: {path}")
        rows.append(value)
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_worker_machine(
    observed: object, common: Mapping[str, Any], *, ordinal: int,
) -> None:
    registered = common.get("registered_machine")
    require(isinstance(observed, Mapping),
            f"worker machine is not an object: {ordinal}")
    require(isinstance(registered, Mapping),
            "formal config lacks a registered machine")
    affinity_contract = common.get("cpu_affinity")
    expected_fields = set(registered) | WORKER_MACHINE_SUPPLEMENTAL_FIELDS
    if affinity_contract is not None:
        expected_fields.add("cpu_affinity")
    require(set(observed) == expected_fields,
            f"worker machine fields differ: {ordinal}")
    require(all(observed.get(key) == value for key, value in registered.items()),
            f"worker registered machine projection differs: {ordinal}")
    require(observed.get("python") == common.get("python_version"),
            f"worker machine Python version differs: {ordinal}")
    require(observed.get("python_executable") == common.get("python_executable"),
            f"worker machine Python executable differs: {ordinal}")
    for field in ("hostname", "platform"):
        require(isinstance(observed.get(field), str) and bool(observed[field]),
                f"worker machine {field} is invalid: {ordinal}")
    if affinity_contract is not None:
        require(isinstance(affinity_contract, Mapping),
                "formal CPU-affinity contract is invalid")
        evidence = observed.get("cpu_affinity")
        require(isinstance(evidence, Mapping)
                and set(evidence) == {"preflight", "postflight"},
                f"worker CPU-affinity evidence differs: {ordinal}")
        for phase in ("preflight", "postflight"):
            row = evidence[phase]
            require(isinstance(row, Mapping),
                    f"worker CPU-affinity {phase} is invalid: {ordinal}")
            require(row == affinity_contract,
                    f"worker CPU-affinity {phase} differs: {ordinal}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--dry-run-summary", type=Path, required=True)
    parser.add_argument("--formal-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    config_path = args.config.resolve(strict=True)
    prereg_path = args.preregistration.resolve(strict=True)
    dry_path = args.dry_run_summary.resolve(strict=True)
    root = args.formal_root.resolve(strict=True)
    summary_path = root / "FORMAL_SUMMARY.json"
    schedule_path = root / "SCHEDULE.json"
    progress_path = root / "CONTROLLER_PROGRESS.jsonl"
    config = read_object(config_path)
    prereg = read_object(prereg_path)
    dry = read_object(dry_path)
    summary = read_object(summary_path)
    schedule_file = read_object(schedule_path)

    require(config.get("schema") == "rtdl.v4_long_workload.formal_config.v1",
            "config schema differs")
    require(prereg.get("schema") == "rtdl.v4_long_workload.preregistration.v1",
            "preregistration schema differs")
    require(prereg.get("status") == "FROZEN_BEFORE_FORMAL_WORKER_ZERO",
            "preregistration status differs")
    require(prereg.get("formal_worker_zero_reached") is False,
            "preregistration was not pre-action")
    require(prereg.get("formal_config_sha256") == sha256(config_path),
            "config hash differs from preregistration")
    require(prereg.get("cpu_affinity") == config["common"].get("cpu_affinity"),
            "CPU affinity differs between config and preregistration")
    require(prereg.get("dry_run_summary_sha256") == sha256(dry_path),
            "dry-run hash differs from preregistration")
    require(dry.get("status") == "PASS" and dry.get("worker_count") == 15,
            "dry run did not pass all 15 workers")
    require(summary.get("schema") == "rtdl.v4_long_workload.formal_summary.v1",
            "formal summary schema differs")
    require(summary.get("retry_count") == 0 and summary.get("discard_count") == 0,
            "formal summary reports retry/discard")

    expected = expected_schedule(config)
    require(schedule_file.get("schema") == "rtdl.v4_long_workload.schedule.v1",
            "formal schedule schema differs")
    require(schedule_file.get("mode") == "formal",
            "formal schedule mode differs")
    require(schedule_file.get("rows") == expected,
            "formal schedule rows differ from independent reconstruction")
    require(schedule_file.get("worker_count") == 240,
            "formal schedule count differs")
    require(prereg.get("formal_schedule_sha256") == digest(schedule_file),
            "formal schedule digest differs from preregistration")
    require(summary.get("schedule_file_sha256") == sha256(schedule_path),
            "formal summary schedule file hash differs")
    require(summary.get("progress_file_sha256") == sha256(progress_path),
            "formal summary progress file hash differs")

    observed_rows = summary.get("rows")
    require(isinstance(observed_rows, list) and len(observed_rows) == 240,
            "formal summary does not retain 240 worker rows")
    process_ids = set()
    cells: dict[tuple[str, str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for expected_row, observed in zip(expected, observed_rows, strict=True):
        require(all(observed.get(key) == value for key, value in expected_row.items()),
                f"formal row schedule differs: {expected_row['ordinal']}")
        launch = observed.get("launch")
        worker = observed.get("worker")
        require(isinstance(launch, Mapping) and isinstance(worker, Mapping),
                f"worker row is incomplete: {expected_row['ordinal']}")
        require(launch.get("return_code") == 0 and launch.get("timeout") is False,
                f"worker launch failed: {expected_row['ordinal']}")
        for field in ("stdout", "stderr", "output", "journal"):
            relative = launch.get(f"{field}_relative")
            require(isinstance(relative, str),
                    f"worker lacks {field} path: {expected_row['ordinal']}")
            path = root / relative
            require(path.is_file() and sha256(path) == launch.get(f"{field}_sha256"),
                    f"worker {field} bytes differ: {expected_row['ordinal']}")
        output_path = root / launch["output_relative"]
        journal_path = root / launch["journal_relative"]
        require(read_object(output_path) == worker,
                f"embedded worker differs from retained bytes: {expected_row['ordinal']}")
        require(worker.get("status") == "PASS",
                f"worker status failed: {expected_row['ordinal']}")
        require(worker.get("formal_config_sha256") == sha256(config_path),
                f"worker config identity differs: {expected_row['ordinal']}")
        require(worker.get("formal_worker_sha256") == prereg.get("worker_sha256"),
                f"worker executable identity differs: {expected_row['ordinal']}")
        require(worker.get("retry_count") == 0 and worker.get("discard_count") == 0,
                f"worker reports retry/discard: {expected_row['ordinal']}")
        require(worker.get("retained_sample_count") == expected_row["repetitions"],
                f"worker sample count differs: {expected_row['ordinal']}")
        require(worker.get("warmup_count") == expected_row["warmups"],
                f"worker warmup count differs: {expected_row['ordinal']}")
        pid = worker.get("process_id")
        require(type(pid) is int and pid > 0 and pid not in process_ids,
                f"worker PID is invalid or reused: {expected_row['ordinal']}")
        process_ids.add(pid)
        validate_worker_machine(
            worker.get("machine"), config["common"],
            ordinal=expected_row["ordinal"],
        )
        identity = worker.get("implementation_identity")
        registered = config["implementations"][expected_row["arm"]]
        require(isinstance(identity, Mapping),
                f"implementation identity missing: {expected_row['ordinal']}")
        for key in ("source_root", "source_commit", "source_tree",
                    "native_library_path", "native_library_sha256"):
            require(identity.get(key) == registered.get(key),
                    f"implementation identity differs: {expected_row['ordinal']}:{key}")
        require(identity.get("source_status_clean") is True,
                f"implementation checkout was dirty: {expected_row['ordinal']}")
        journal = read_journal(journal_path)
        require(journal and journal[0].get("event") == "worker_started",
                f"worker journal has no start: {expected_row['ordinal']}")
        if config["common"].get("cpu_affinity") is not None:
            affinity_evidence = worker["machine"]["cpu_affinity"]
            for phase in ("preflight", "postflight"):
                events = [
                    row for row in journal
                    if row.get("event") == f"cpu_affinity_{phase}"
                ]
                require(len(events) == 1
                        and events[0].get("observation")
                        == affinity_evidence[phase],
                        f"worker CPU-affinity journal differs: "
                        f"{expected_row['ordinal']}:{phase}")
        if expected_row["endpoint"] == "prepared":
            samples = [row for row in journal if row.get("event") == "sample_complete"]
            warmups = [row for row in journal if row.get("event") == "warmup_complete"]
            require(len(samples) == expected_row["repetitions"],
                    f"journal sample count differs: {expected_row['ordinal']}")
            require(len(warmups) == expected_row["warmups"],
                    f"journal warmup count differs: {expected_row['ordinal']}")
            require([row["elapsed_ns"] for row in samples]
                    == worker.get("primary_samples_ns"),
                    f"journal samples differ from output: {expected_row['ordinal']}")
            require(sum(row.get("event") == "close_complete" for row in journal) == 1,
                    f"prepared close event differs: {expected_row['ordinal']}")
        else:
            samples = [
                row for row in journal
                if row.get("event") == "complete_sample_complete"
            ]
            require(len(samples) == 1 and [samples[0]["elapsed_ns"]]
                    == worker.get("primary_samples_ns"),
                    f"complete journal sample differs: {expected_row['ordinal']}")
        key = (expected_row["unit_id"], expected_row["endpoint"],
               expected_row["block"])
        require(expected_row["arm"] not in cells[key],
                f"duplicate arm in cell: {key}")
        cells[key][expected_row["arm"]] = worker

    require(len(process_ids) == 240 and len(cells) == 80,
            "worker/cell population differs")
    evaluations = []
    for unit_id in config["units"]:
        for endpoint in ENDPOINTS:
            ratios = []
            old_ratios = []
            repair_ratios = []
            for block in range(8):
                by_arm = cells[(unit_id, endpoint, block)]
                require(set(by_arm) == set(ARMS), f"cell arm population differs: {unit_id}")
                inputs = [by_arm[arm]["input_identity"] for arm in ARMS]
                outputs = [by_arm[arm]["output_sha256"] for arm in ARMS]
                require(len({digest(value) for value in inputs}) == 1,
                        f"cell input identity differs: {unit_id}:{endpoint}:{block}")
                require(len(set(outputs)) == 1,
                        f"cell output differs: {unit_id}:{endpoint}:{block}")
                medians = {
                    arm: int(statistics.median(by_arm[arm]["primary_samples_ns"]))
                    for arm in ARMS
                }
                ratios.append(medians["new_v4"] / medians["pyoptix"])
                old_ratios.append(medians["old_v4"] / medians["pyoptix"])
                repair_ratios.append(medians["new_v4"] / medians["old_v4"])
            median = statistics.median(ratios)
            maximum = max(ratios)
            evaluations.append({
                "unit_id": unit_id, "endpoint": endpoint,
                "new_v4_over_pyoptix_block_ratios": ratios,
                "median_new_v4_over_pyoptix": median,
                "max_new_v4_over_pyoptix": maximum,
                "median_old_v4_over_pyoptix": statistics.median(old_ratios),
                "median_new_v4_over_old_v4": statistics.median(repair_ratios),
                "engineering_target_met": median <= 1.20 and maximum <= 1.35,
            })
    all_target = all(row["engineering_target_met"] for row in evaluations)
    payload = {
        "schema": "rtdl.v4_long_workload.independent_recount.v1",
        "status": "PASS__METHOD_AND_TARGET" if all_target
        else "PASS__METHOD__ENGINEERING_TARGET_NOT_MET",
        "project_modules_imported": False,
        "formal_worker_count": 240,
        "distinct_process_id_count": 240,
        "formal_cell_count": 80,
        "retry_count": 0, "discard_count": 0,
        "all_raw_files_hash_verified": True,
        "all_journals_reconstructed": True,
        "all_input_and_output_parity_verified": True,
        "engineering_target_met_for_all_ten_rows": all_target,
        "evaluations": evaluations,
        "identities": {
            "config_sha256": sha256(config_path),
            "preregistration_sha256": sha256(prereg_path),
            "dry_run_summary_sha256": sha256(dry_path),
            "formal_summary_sha256": sha256(summary_path),
            "formal_schedule_sha256": sha256(schedule_path),
            "formal_progress_sha256": sha256(progress_path),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({
        "status": payload["status"], "output": str(args.output),
        "evaluation_count": len(evaluations),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
