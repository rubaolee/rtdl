#!/usr/bin/env python3
"""Independent raw-worker recount for the V4/PyOptiX formal transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections.abc import Mapping
from pathlib import Path
from typing import Any

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


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _retained_worker_path(
    formal_root: Path, relative_text: object, command: list[str]
) -> Path:
    if not isinstance(relative_text, str):
        raise TypeError("formal worker relative path is malformed")
    relative = Path(relative_text)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise RuntimeError("formal worker relative path escapes transaction root")
    command_output = _command_value(command, "--output")
    if command_output is None:
        raise RuntimeError("formal worker command lacks --output")
    command_parts = Path(command_output).parts
    if (
        len(command_parts) < len(relative.parts)
        or tuple(command_parts[-len(relative.parts) :]) != relative.parts
    ):
        raise RuntimeError("formal worker command/output path binding differs")
    root = formal_root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as error:
        raise RuntimeError(
            "formal worker resolved path escapes transaction root"
        ) from error
    return path


def _command_value(command: list[str], option: str) -> str | None:
    if option not in command:
        return None
    index = command.index(option)
    if index + 1 >= len(command):
        raise RuntimeError(f"formal worker command has no value for {option}")
    return command[index + 1]


def recount(formal_path: Path) -> dict[str, Any]:
    formal = _read(formal_path)
    if formal.get("schema") != "rtdl.v4_paper_apps_pyoptix.formal_transaction.v1":
        raise ValueError("unexpected formal transaction schema")
    registrations = formal.get("registrations")
    if not isinstance(registrations, list):
        raise TypeError("formal transaction lacks registrations")
    expected_pair_count = len(UNITS) * len(ENDPOINTS) * len(BLOCK_ORDERS)
    if (
        len(registrations) != expected_pair_count
        or formal.get("registered_pair_count") != expected_pair_count
        or formal.get("worker_process_count") != expected_pair_count * 2
        or formal.get("block_orders") != [list(row) for row in BLOCK_ORDERS]
    ):
        raise RuntimeError("formal transaction population differs from registration")
    prepared_repetitions = formal.get("registered_prepared_repetitions")
    prepared_warmups = formal.get("registered_prepared_warmups")
    registered_input_identities = formal.get("registered_input_identities")
    if (
        not isinstance(prepared_repetitions, Mapping)
        or set(prepared_repetitions) != {row[2] for row in UNITS}
        or any(
            type(value) is not int or value <= 0
            for value in prepared_repetitions.values()
        )
        or type(prepared_warmups) is not int
        or prepared_warmups < 0
        or not isinstance(registered_input_identities, Mapping)
        or set(registered_input_identities) != {row[2] for row in UNITS}
        or any(
            not isinstance(value, Mapping)
            for value in registered_input_identities.values()
        )
    ):
        raise RuntimeError("formal sampling/input registration is malformed")
    if formal.get("formal_worker_zero_reached") is not True:
        raise RuntimeError("formal transaction did not record worker zero")
    worker_files = []
    observed_worker_paths: set[Path] = set()
    recomputed_rows = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    observed_cells: set[tuple[str, str, int]] = set()
    unit_by_id = {unit_id: (app, operation) for app, operation, unit_id in UNITS}
    for row in registrations:
        unit_id = str(row.get("unit_id"))
        endpoint = str(row.get("endpoint"))
        block = row.get("block")
        if (
            unit_id not in unit_by_id
            or endpoint not in ENDPOINTS
            or type(block) is not int
            or not 0 <= block < len(BLOCK_ORDERS)
        ):
            raise RuntimeError("formal cell identity differs from registration")
        cell = (unit_id, endpoint, block)
        if cell in observed_cells:
            raise RuntimeError("formal transaction contains a duplicate cell")
        observed_cells.add(cell)
        expected_app, expected_operation = unit_by_id[unit_id]
        expected_order = BLOCK_ORDERS[block]
        if (
            row.get("app") != expected_app
            or row.get("operation") != expected_operation
            or row.get("order") != list(expected_order)
        ):
            raise RuntimeError("formal cell contract differs from registration")
        arm_rows = row.get("workers")
        if not isinstance(arm_rows, list) or len(arm_rows) != 2:
            raise RuntimeError("formal cell lacks one exact arm pair")
        workers: dict[str, Mapping[str, Any]] = {}
        valid = True
        reason = None
        for arm_row in arm_rows:
            if not isinstance(arm_row, Mapping):
                raise TypeError("formal worker registration is malformed")
            position = arm_row.get("position")
            arm = str(arm_row.get("arm"))
            if (
                type(position) is not int
                or position not in {0, 1}
                or arm != expected_order[position]
                or arm in workers
            ):
                raise RuntimeError("formal worker order differs from registration")
            launch = arm_row.get("launch")
            if not isinstance(launch, Mapping):
                raise TypeError("formal worker launch is malformed")
            command = launch.get("command")
            if not isinstance(command, list) or not all(
                isinstance(value, str) for value in command
            ):
                raise RuntimeError("formal worker command is malformed")
            path = _retained_worker_path(
                formal_path.parent,
                arm_row.get("worker_output_relative"),
                command,
            )
            if path in observed_worker_paths:
                raise RuntimeError("formal transaction reuses a worker output path")
            observed_worker_paths.add(path)
            raw = _read(path)
            if raw != arm_row["worker"]:
                raise RuntimeError(
                    f"embedded worker differs from retained bytes: {path}"
                )
            worker_files.append(
                {
                    "path": str(path),
                    "relative_path": arm_row["worker_output_relative"],
                    "sha256": _sha(path),
                }
            )
            repetitions = (
                int(prepared_repetitions[unit_id]) if endpoint == "prepared" else 1
            )
            warmups = int(prepared_warmups) if endpoint == "prepared" else 0
            primary_samples = raw.get("primary_samples_ns")
            execute_samples = raw.get("execute_samples_ns")
            outputs = raw.get("outputs")
            output_contract_valid = (
                isinstance(primary_samples, list)
                and len(primary_samples) == repetitions
                and all(type(value) is int and value > 0 for value in primary_samples)
                and isinstance(execute_samples, list)
                and len(execute_samples) == repetitions
                and all(type(value) is int and value > 0 for value in execute_samples)
                and isinstance(outputs, list)
                and len(outputs) == repetitions
                and all(
                    isinstance(output, Mapping)
                    and output.get("matched") is True
                    and output.get("output_sha256") == raw.get("output_sha256")
                    and isinstance(output.get("compact_execution_evidence"), Mapping)
                    and output.get("detailed_receipt_retention_count") == 0
                    and output.get("public_output_materialized_inside_call") is True
                    for output in outputs
                )
                and raw.get("complete_timer_includes_prepare_execute_close")
                is (endpoint == "complete")
                and raw.get("input_load_included_in_primary_timer") is False
            )
            expected_command_operation = (
                None if expected_operation is None else expected_operation
            )
            if (
                _command_value(command, "--app") != expected_app
                or _command_value(command, "--arm") != arm
                or _command_value(command, "--endpoint") != endpoint
                or _command_value(command, "--operation") != expected_command_operation
                or _command_value(command, "--repetitions") != str(repetitions)
                or _command_value(command, "--warmups") != str(warmups)
                or raw.get("app") != expected_app
                or raw.get("operation") != expected_operation
                or raw.get("arm") != arm
                or raw.get("endpoint") != endpoint
                or raw.get("retained_sample_count") != repetitions
                or raw.get("warmup_count") != warmups
                or raw.get("retry_count") != 0
                or raw.get("discard_count") != 0
                or raw.get("input_identity") != registered_input_identities[unit_id]
                or {
                    "gpu": raw.get("machine", {}).get("gpu"),
                    "cuda_visible_devices": raw.get("machine", {}).get(
                        "cuda_visible_devices"
                    ),
                }
                != formal.get("registered_machine")
                or raw.get("source_identity", {}).get("git_commit")
                != formal.get("source_commit")
                or raw.get("source_identity", {}).get("git_tree")
                != formal.get("source_tree")
                or raw.get("source_identity", {}).get("git_status_clean") is not True
                or raw.get("source_identity", {}).get("worker_sha256")
                != formal.get("worker_sha256")
                or not output_contract_valid
            ):
                raise RuntimeError("formal worker contract differs from registration")
            workers[arm] = raw
            if launch.get("return_code") != 0 or raw.get("status") != "PASS":
                valid = False
                reason = "worker_failure"
            if type(raw.get("process_id")) is not int or raw["process_id"] <= 0:
                valid = False
                reason = "worker_process_identity_missing"
        if set(workers) != {"v4", "pyoptix"}:
            valid = False
            reason = "arm_pair_incomplete"
        if (
            valid
            and workers["v4"]["output_sha256"] != workers["pyoptix"]["output_sha256"]
        ):
            valid = False
            reason = "output_digest_mismatch"
        if valid and any(
            workers[arm].get("source_identity", {}).get("config_sha256")
            != formal.get("config_sha256")
            for arm in workers
        ):
            valid = False
            reason = "worker_config_identity_mismatch"
        pair: dict[str, Any] = {"valid": valid}
        if valid:
            v4 = statistics.median(
                int(value) for value in workers["v4"]["primary_samples_ns"]
            )
            pyoptix = statistics.median(
                int(value) for value in workers["pyoptix"]["primary_samples_ns"]
            )
            pair.update(
                {
                    "output_sha256": workers["v4"]["output_sha256"],
                    "v4_median_ns": v4,
                    "pyoptix_median_ns": pyoptix,
                    "v4_over_pyoptix": v4 / pyoptix,
                }
            )
        else:
            pair["reason"] = reason
        if pair != row["pair"]:
            raise RuntimeError(
                f"controller pair differs from recount: {row['unit_id']} {row['endpoint']} block {row['block']}"
            )
        recomputed_rows.append(
            {
                "unit_id": unit_id,
                "endpoint": endpoint,
                "block": block,
                "pair": pair,
            }
        )
        grouped.setdefault(f"{unit_id}::{endpoint}", []).append(pair)

    expected_cells = {
        (unit_id, endpoint, block)
        for _app, _operation, unit_id in UNITS
        for endpoint in ENDPOINTS
        for block in range(len(BLOCK_ORDERS))
    }
    if observed_cells != expected_cells or len(worker_files) != expected_pair_count * 2:
        raise RuntimeError(
            "formal transaction does not cover the registered population"
        )

    evaluations = []
    for key, pairs in sorted(grouped.items()):
        ratios = [pair["v4_over_pyoptix"] for pair in pairs if pair["valid"]]
        evaluations.append(
            {
                "key": key,
                "valid": len(ratios) == 8 and all(pair["valid"] for pair in pairs),
                "valid_block_count": len(ratios),
                "registered_block_count": 8,
                "median_v4_over_pyoptix": statistics.median(ratios)
                if len(ratios) == 8
                else None,
                "min_v4_over_pyoptix": min(ratios) if ratios else None,
                "max_v4_over_pyoptix": max(ratios) if ratios else None,
            }
        )
    if evaluations != formal.get("evaluations"):
        raise RuntimeError("controller evaluations differ from independent recount")
    recomputed_status = (
        "PASS"
        if formal.get("source_unchanged_during_transaction") is True
        and formal.get("config_unchanged_during_transaction") is True
        and formal.get("retry_count") == 0
        and formal.get("discard_count") == 0
        and all(row["valid"] for row in evaluations)
        else "FAIL"
    )
    if formal.get("status") != recomputed_status:
        raise RuntimeError("formal status differs from independent recount")
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.independent_recount.v1",
        "status": "RECOUNT_MATCH",
        "formal_summary_path": str(formal_path),
        "formal_summary_sha256": _sha(formal_path),
        "formal_status_preserved": formal.get("status"),
        "worker_file_count": len(worker_files),
        "worker_files": worker_files,
        "recomputed_pairs": recomputed_rows,
        "evaluations": evaluations,
        "retry_count": formal.get("retry_count"),
        "discard_count": formal.get("discard_count"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = recount(args.formal_summary.resolve(strict=True))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "formal_status": result["formal_status_preserved"],
                "worker_file_count": result["worker_file_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
