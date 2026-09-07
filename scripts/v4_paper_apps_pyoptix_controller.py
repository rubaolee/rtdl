#!/usr/bin/env python3
"""Dry-run and formal controller for the first V4/PyOptiX app batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/v4_paper_apps_pyoptix_worker.py"
ARMS = ("v4", "pyoptix")
BLOCK_ORDERS = (
    ("v4", "pyoptix"),
    ("pyoptix", "v4"),
    ("v4", "pyoptix"),
    ("pyoptix", "v4"),
    ("pyoptix", "v4"),
    ("v4", "pyoptix"),
    ("pyoptix", "v4"),
    ("v4", "pyoptix"),
)
UNITS = (
    ("particle_tracking", None, "particle_tracking"),
    ("triangle_counting", None, "triangle_counting__com_dblp__rt_2a1"),
    ("librts", "point_contains", "librts__parks__point_contains"),
    ("librts", "range_contains", "librts__parks__range_contains"),
)
ENDPOINTS = ("complete", "first_result", "prepared")


def _sha(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _write_create(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def _worker_command(
    *,
    python: Path,
    config: Path,
    app: str,
    operation: str | None,
    arm: str,
    endpoint: str,
    repetitions: int,
    warmups: int,
    output: Path,
) -> list[str]:
    command = [
        str(python),
        str(WORKER),
        "--config",
        str(config),
        "--app",
        app,
        "--arm",
        arm,
        "--endpoint",
        endpoint,
        "--repetitions",
        str(repetitions),
        "--warmups",
        str(warmups),
        "--output",
        str(output),
    ]
    if operation is not None:
        command.extend(("--operation", operation))
    return command


def _launch(
    command: list[str], *, cwd: Path, log: Path, timeout_seconds: int
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_seconds,
        )
        return_code = completed.returncode
        output = completed.stdout
        timeout = False
    except subprocess.TimeoutExpired as error:
        return_code = 124
        output = error.stdout if isinstance(error.stdout, str) else ""
        output += "\nCONTROLLER_TIMEOUT\n"
        timeout = True
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(output, encoding="utf-8")
    return {
        "return_code": return_code,
        "timeout": timeout,
        "wall_ns": time.perf_counter_ns() - started,
        "log": str(log),
        "command": command,
    }


def _git_identity(source_root: Path) -> tuple[str, str, str]:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=source_root,
            text=True,
            capture_output=True,
            check=True,
        )
        return completed.stdout.strip()

    return (
        run("rev-parse", "HEAD"),
        run("rev-parse", "HEAD^{tree}"),
        run("status", "--porcelain"),
    )


def _prepared_count(config: Mapping[str, Any], unit_id: str) -> int:
    values = config.get("prepared_repetitions", {})
    value = values.get(unit_id, 32) if isinstance(values, Mapping) else 32
    if type(value) is not int or value <= 0:
        raise ValueError(f"invalid prepared repetition count for {unit_id}")
    return value


def _run_dry(
    *,
    config_path: Path,
    config: Mapping[str, Any],
    output_root: Path,
    python: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    config_sha256 = _sha(config_path)
    worker_sha256 = _sha(WORKER)
    records = []
    for app, operation, unit_id in UNITS:
        pair = []
        for position, arm in enumerate(("v4", "pyoptix")):
            output = output_root / "workers" / f"{unit_id}__{arm}.json"
            log = output_root / "logs" / f"{unit_id}__{arm}.log"
            launch = _launch(
                _worker_command(
                    python=python,
                    config=config_path,
                    app=app,
                    operation=operation,
                    arm=arm,
                    endpoint="first_result",
                    repetitions=1,
                    warmups=0,
                    output=output,
                ),
                cwd=Path(config["source_root"]),
                log=log,
                timeout_seconds=timeout_seconds,
            )
            worker = _read(output) if output.is_file() else None
            pair.append(
                {"position": position, "arm": arm, "launch": launch, "worker": worker}
            )
        valid = all(
            row["launch"]["return_code"] == 0
            and isinstance(row["worker"], Mapping)
            and row["worker"].get("status") == "PASS"
            for row in pair
        )
        input_parity = valid and pair[0]["worker"].get("input_identity") == pair[1][
            "worker"
        ].get("input_identity")
        parity = (
            valid
            and pair[0]["worker"]["output_sha256"] == pair[1]["worker"]["output_sha256"]
        )
        records.append(
            {
                "unit_id": unit_id,
                "app": app,
                "operation": operation,
                "valid": valid,
                "input_identity_parity": input_parity,
                "output_parity": parity,
                "workers": pair,
            }
        )
    config_unchanged = _sha(config_path) == config_sha256
    worker_unchanged = _sha(WORKER) == worker_sha256
    records_pass = all(
        row["valid"] and row["input_identity_parity"] and row["output_parity"]
        for row in records
    )
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.dry_run.v1",
        "status": (
            "PASS" if records_pass and config_unchanged and worker_unchanged else "FAIL"
        ),
        "formal_worker_zero_reached": False,
        "unit_count": len(records),
        "records": records,
        "config_sha256": config_sha256,
        "config_unchanged_during_dry_run": config_unchanged,
        "worker_sha256": worker_sha256,
        "worker_unchanged_during_dry_run": worker_unchanged,
        "retry_count": 0,
        "discard_count": 0,
    }


def _worker_output_path(command: list[str]) -> Path:
    try:
        index = command.index("--output")
    except ValueError as error:
        raise RuntimeError("dry-run worker command lacks --output") from error
    if index + 1 >= len(command):
        raise RuntimeError("dry-run worker command has no output value")
    return Path(command[index + 1]).resolve(strict=True)


def _command_value(command: list[str], option: str) -> str | None:
    if option not in command:
        return None
    index = command.index(option)
    if index + 1 >= len(command):
        raise RuntimeError(f"dry-run worker command has no value for {option}")
    return command[index + 1]


def _validate_dry_run_authority(
    dry_run: Mapping[str, Any], *, config_path: Path
) -> dict[str, dict[str, Any]]:
    """Bind the untimed parity gate to the bytes used by formal execution."""

    config_sha256 = _sha(config_path)
    if dry_run.get("schema") != "rtdl.v4_paper_apps_pyoptix.dry_run.v1":
        raise PermissionError("formal run requires the registered dry-run schema")
    if dry_run.get("status") != "PASS":
        raise PermissionError("formal run requires a passing untimed dry run")
    if dry_run.get("formal_worker_zero_reached") is not False:
        raise PermissionError("dry-run authority must precede formal worker zero")
    if (
        dry_run.get("config_sha256") != config_sha256
        or dry_run.get("config_unchanged_during_dry_run") is not True
    ):
        raise PermissionError("dry-run authority is not bound to the formal config")
    if (
        dry_run.get("worker_sha256") != _sha(WORKER)
        or dry_run.get("worker_unchanged_during_dry_run") is not True
    ):
        raise PermissionError("dry-run authority is not bound to the formal worker")
    if dry_run.get("retry_count") != 0 or dry_run.get("discard_count") != 0:
        raise PermissionError("dry-run authority contains a retry or discard")

    records = dry_run.get("records")
    if (
        not isinstance(records, list)
        or len(records) != len(UNITS)
        or dry_run.get("unit_count") != len(UNITS)
    ):
        raise PermissionError("dry-run authority has the wrong unit population")
    expected_units = {(app, operation, unit_id) for app, operation, unit_id in UNITS}
    observed_units: set[tuple[str, str | None, str]] = set()
    registered_input_identities: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise PermissionError("dry-run authority contains a malformed unit")
        identity = (
            str(record.get("app")),
            record.get("operation"),
            str(record.get("unit_id")),
        )
        if identity not in expected_units or identity in observed_units:
            raise PermissionError("dry-run authority unit identity differs")
        observed_units.add(identity)
        workers = record.get("workers")
        if not isinstance(workers, list) or len(workers) != 2:
            raise PermissionError("dry-run authority lacks one exact arm pair")
        by_arm: dict[str, Mapping[str, Any]] = {}
        for arm_row in workers:
            if not isinstance(arm_row, Mapping):
                raise PermissionError("dry-run arm registration is malformed")
            arm = str(arm_row.get("arm"))
            position = arm_row.get("position")
            launch = arm_row.get("launch")
            embedded = arm_row.get("worker")
            if (
                type(position) is not int
                or position not in {0, 1}
                or arm != ARMS[position]
                or arm in by_arm
                or not isinstance(launch, Mapping)
                or not isinstance(embedded, Mapping)
            ):
                raise PermissionError("dry-run arm pair differs")
            command = launch.get("command")
            if not isinstance(command, list) or not all(
                isinstance(value, str) for value in command
            ):
                raise PermissionError("dry-run worker command is malformed")
            retained = _read(_worker_output_path(command))
            if retained != embedded:
                raise PermissionError(
                    "dry-run embedded worker differs from retained bytes"
                )
            source = retained.get("source_identity")
            expected_operation = identity[1]
            if (
                launch.get("return_code") != 0
                or _command_value(command, "--config") != str(config_path)
                or _command_value(command, "--app") != identity[0]
                or _command_value(command, "--arm") != arm
                or _command_value(command, "--endpoint") != "first_result"
                or _command_value(command, "--operation") != expected_operation
                or _command_value(command, "--repetitions") != "1"
                or _command_value(command, "--warmups") != "0"
                or retained.get("status") != "PASS"
                or retained.get("app") != identity[0]
                or retained.get("operation") != expected_operation
                or retained.get("arm") != arm
                or retained.get("endpoint") != "first_result"
                or not isinstance(source, Mapping)
                or source.get("config_sha256") != config_sha256
                or source.get("worker_sha256") != _sha(WORKER)
                or retained.get("retry_count") != 0
                or retained.get("discard_count") != 0
                or type(retained.get("process_id")) is not int
                or retained["process_id"] <= 0
            ):
                raise PermissionError("dry-run worker failed its registered identity")
            by_arm[arm] = retained
        parity = by_arm["v4"].get("output_sha256") == by_arm["pyoptix"].get(
            "output_sha256"
        )
        v4_input = by_arm["v4"].get("input_identity")
        pyoptix_input = by_arm["pyoptix"].get("input_identity")
        input_parity = (
            isinstance(v4_input, Mapping)
            and isinstance(pyoptix_input, Mapping)
            and v4_input == pyoptix_input
        )
        if (
            record.get("valid") is not True
            or record.get("input_identity_parity") is not True
            or record.get("output_parity") is not True
            or not input_parity
            or not parity
        ):
            raise PermissionError("dry-run input/output parity gate is not satisfied")
        registered_input_identities[identity[2]] = dict(v4_input)
    if observed_units != expected_units:
        raise PermissionError("dry-run authority does not cover every registered unit")
    return registered_input_identities


def _cell_summary(
    rows: list[dict[str, Any]],
    *,
    expected_config_sha256: str,
    expected_input_identity: Mapping[str, Any],
) -> dict[str, Any]:
    by_arm = {row["arm"]: row for row in rows}
    if set(by_arm) != {"v4", "pyoptix"}:
        return {"valid": False, "reason": "arm_pair_incomplete"}
    workers = {arm: row.get("worker") for arm, row in by_arm.items()}
    if any(
        by_arm[arm]["launch"]["return_code"] != 0
        or not isinstance(workers[arm], Mapping)
        or workers[arm].get("status") != "PASS"
        for arm in workers
    ):
        return {"valid": False, "reason": "worker_failure"}
    if workers["v4"]["output_sha256"] != workers["pyoptix"]["output_sha256"]:
        return {"valid": False, "reason": "output_digest_mismatch"}
    if any(
        workers[arm].get("input_identity") != expected_input_identity for arm in workers
    ):
        return {"valid": False, "reason": "input_identity_mismatch"}
    if any(
        workers[arm].get("source_identity", {}).get("config_sha256")
        != expected_config_sha256
        for arm in workers
    ):
        return {"valid": False, "reason": "worker_config_identity_mismatch"}
    medians = {
        arm: statistics.median(
            int(value) for value in workers[arm]["primary_samples_ns"]
        )
        for arm in workers
    }
    return {
        "valid": True,
        "output_sha256": workers["v4"]["output_sha256"],
        "v4_median_ns": medians["v4"],
        "pyoptix_median_ns": medians["pyoptix"],
        "v4_over_pyoptix": medians["v4"] / medians["pyoptix"],
    }


def _run_formal(
    *,
    config_path: Path,
    config: Mapping[str, Any],
    output_root: Path,
    python: Path,
    timeout_seconds: int,
    dry_run: Mapping[str, Any],
) -> dict[str, Any]:
    registered_input_identities = _validate_dry_run_authority(
        dry_run, config_path=config_path
    )
    source_root = Path(config["source_root"]).resolve(strict=True)
    commit, tree, dirty = _git_identity(source_root)
    if dirty:
        raise PermissionError("formal source checkout must be clean")
    if config.get("source_commit") != commit:
        raise PermissionError("formal config source_commit differs from checkout")
    if config.get("source_tree") != tree:
        raise PermissionError("formal config source_tree differs from checkout")
    config_sha256 = _sha(config_path)

    registrations = []
    formal_worker_zero_reached = False
    for app, operation, unit_id in UNITS:
        for endpoint in ENDPOINTS:
            repetitions = (
                _prepared_count(config, unit_id) if endpoint == "prepared" else 1
            )
            warmups = (
                int(config.get("prepared_warmups", 0)) if endpoint == "prepared" else 0
            )
            for block, order in enumerate(BLOCK_ORDERS):
                pair_rows = []
                for position, arm in enumerate(order):
                    stem = f"{unit_id}__{endpoint}__b{block:02d}__p{position}__{arm}"
                    output = output_root / "workers" / f"{stem}.json"
                    log = output_root / "logs" / f"{stem}.log"
                    formal_worker_zero_reached = True
                    launch = _launch(
                        _worker_command(
                            python=python,
                            config=config_path,
                            app=app,
                            operation=operation,
                            arm=arm,
                            endpoint=endpoint,
                            repetitions=repetitions,
                            warmups=warmups,
                            output=output,
                        ),
                        cwd=source_root,
                        log=log,
                        timeout_seconds=timeout_seconds,
                    )
                    worker = _read(output) if output.is_file() else None
                    pair_rows.append(
                        {
                            "position": position,
                            "arm": arm,
                            "launch": launch,
                            "worker_output_relative": output.relative_to(
                                output_root
                            ).as_posix(),
                            "worker": worker,
                        }
                    )
                registrations.append(
                    {
                        "unit_id": unit_id,
                        "app": app,
                        "operation": operation,
                        "endpoint": endpoint,
                        "block": block,
                        "order": list(order),
                        "workers": pair_rows,
                        "pair": _cell_summary(
                            pair_rows,
                            expected_config_sha256=config_sha256,
                            expected_input_identity=registered_input_identities[
                                unit_id
                            ],
                        ),
                    }
                )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in registrations:
        grouped.setdefault(f"{row['unit_id']}::{row['endpoint']}", []).append(row)
    evaluations = []
    for key, rows in sorted(grouped.items()):
        valid = all(row["pair"]["valid"] for row in rows)
        ratios = [
            row["pair"]["v4_over_pyoptix"] for row in rows if row["pair"]["valid"]
        ]
        evaluations.append(
            {
                "key": key,
                "valid": valid and len(ratios) == 8,
                "valid_block_count": len(ratios),
                "registered_block_count": 8,
                "median_v4_over_pyoptix": statistics.median(ratios)
                if len(ratios) == 8
                else None,
                "min_v4_over_pyoptix": min(ratios) if ratios else None,
                "max_v4_over_pyoptix": max(ratios) if ratios else None,
            }
        )
    end_commit, end_tree, end_dirty = _git_identity(source_root)
    source_unchanged = end_commit == commit and end_tree == tree and not bool(end_dirty)
    config_unchanged = _sha(config_path) == config_sha256
    status = (
        "PASS"
        if source_unchanged
        and config_unchanged
        and all(row["valid"] for row in evaluations)
        else "FAIL"
    )
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.formal_transaction.v1",
        "status": status,
        "formal_worker_zero_reached": formal_worker_zero_reached,
        "source_commit": commit,
        "source_tree": tree,
        "source_unchanged_during_transaction": source_unchanged,
        "worker_sha256": _sha(WORKER),
        "config_path": str(config_path),
        "config_sha256": config_sha256,
        "config_unchanged_during_transaction": config_unchanged,
        "registered_machine": config.get("registered_machine"),
        "registered_prepared_repetitions": {
            unit_id: _prepared_count(config, unit_id)
            for _app, _operation, unit_id in UNITS
        },
        "registered_prepared_warmups": int(config.get("prepared_warmups", 0)),
        "registered_input_identities": registered_input_identities,
        "dry_run_sha256": _sha(Path(str(dry_run["_path"]))),
        "block_orders": [list(row) for row in BLOCK_ORDERS],
        "registered_pair_count": len(registrations),
        "worker_process_count": len(registrations) * 2,
        "retry_count": 0,
        "discard_count": 0,
        "registrations": registrations,
        "evaluations": evaluations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dry-run", "formal"), required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--dry-run-summary", type=Path)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(args.output_root)
    if args.timeout_seconds <= 0:
        raise ValueError("timeout must be positive")
    args.output_root.mkdir(parents=True)
    config_path = args.config.resolve(strict=True)
    config = _read(config_path)
    if args.mode == "dry-run":
        summary = _run_dry(
            config_path=config_path,
            config=config,
            output_root=args.output_root,
            python=args.python.resolve(strict=True),
            timeout_seconds=args.timeout_seconds,
        )
        name = "DRY_RUN_SUMMARY.json"
    else:
        if args.dry_run_summary is None:
            parser.error("formal mode requires --dry-run-summary")
        dry_path = args.dry_run_summary.resolve(strict=True)
        dry = _read(dry_path)
        dry["_path"] = str(dry_path)
        summary = _run_formal(
            config_path=config_path,
            config=config,
            output_root=args.output_root,
            python=args.python.resolve(strict=True),
            timeout_seconds=args.timeout_seconds,
            dry_run=dry,
        )
        name = "FORMAL_SUMMARY.json"
    summary["controller_sha256"] = _sha(Path(__file__).resolve())
    _write_create(args.output_root / name, summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "mode": args.mode,
                "summary": str(args.output_root / name),
            },
            sort_keys=True,
        )
    )
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
