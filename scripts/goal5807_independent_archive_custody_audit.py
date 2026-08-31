#!/usr/bin/env python3
"""Standalone raw-byte custody and statistics audit for Goal5807.

This audit deliberately does not import any Goal5807 implementation module.
Its statistical input is the JSON decoded directly from each archived
``workers/*/stdout.bin``.  Row, evaluation, and recount JSON are used only as
objects to check after the raw reconstruction has been completed.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import random
import tarfile
from typing import Any


ARCHIVE_SHA256 = (
    "dc95d0295b2d4f525255a1543a4adff2dcd2f18c7aa755284921f55e98ec36ee")
CONTRACT_SHA256 = (
    "6a3540fae2a0283af4bd91ac44190f6df1154775f518f1d088293972a63a7fe7")
ROOT_NAME = "goal5807_provider_ready_formal_v2_20260827_0112"
TASKS = ("relation", "triangle")
ARMS = ("RTDL_PROVIDER_READY", "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY")
REGIMES = (
    "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE",
    "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT",
    "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT",
)
PHASES = (
    "input_admission",
    "runtime_preload",
    "adapter_construct",
    "install_load",
    "provider_bind",
    "app_prepare",
    "first_exact_execute",
    "steady",
    "evidence_identity",
    "prepared_close",
    "provider_session_close",
)
BLOCKS = 16
POSITIONS = 4
BOOTSTRAP_DRAWS = 10_000
CI_INDICES = (249, 9749)
SEEDS = {"relation": 58_070_000, "triangle": 58_070_001}
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_json(raw: bytes, *, label: str, canonical_line: bool = True) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON value {value} in {label}")

    try:
        value = json.loads(raw.decode("utf-8"), parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(f"invalid JSON in {label}: {error}") from error
    if canonical_line and raw != canonical(value) + b"\n":
        raise RuntimeError(f"non-canonical JSON bytes in {label}")
    return value


def median(values: list[int | float]) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise RuntimeError("median input is empty")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def bootstrap_ci(values: list[float], *, seed: int) -> tuple[float, float]:
    generator = random.Random(seed)
    distribution = []
    for _ in range(BOOTSTRAP_DRAWS):
        distribution.append(median(generator.choices(values, k=len(values))))
    distribution.sort()
    return distribution[CI_INDICES[0]], distribution[CI_INDICES[1]]


def expected_coordinates() -> list[tuple[str, int, int, str, str]]:
    result = []
    order = (ARMS[0], ARMS[1], ARMS[1], ARMS[0])
    for task in TASKS:
        for block in range(BLOCKS):
            for position, arm in enumerate(order):
                slug = "rtdl" if arm == ARMS[0] else "pyoptix"
                worker_id = f"{task}_b{block:02d}_p{position}_{slug}"
                result.append((task, block, position, arm, worker_id))
    return result


def expected_members(root: str) -> set[str]:
    names = {
        root,
        f"{root}/controller.json",
        f"{root}/evaluation.json",
        f"{root}/recount.json",
        f"{root}/rows",
        f"{root}/workers",
    }
    for _task, _block, _position, _arm, worker_id in expected_coordinates():
        worker = f"{root}/workers/{worker_id}"
        names.update({
            worker,
            f"{worker}/command.json",
            f"{worker}/stdout.bin",
            f"{worker}/stderr.bin",
            f"{worker}/isolated_caches",
            f"{worker}/isolated_caches/cuda",
            f"{worker}/isolated_caches/cupy",
            f"{worker}/isolated_caches/optix",
            f"{worker}/isolated_caches/tmp",
            f"{worker}/isolated_caches/xdg",
            f"{root}/rows/{worker_id}.json",
        })
    return names


def validate_phase_ledger(ledger: object, *, label: str) -> tuple[int, dict[str, int | None]]:
    if not isinstance(ledger, dict):
        raise RuntimeError(f"phase ledger is absent: {label}")
    phases = ledger.get("phases")
    if not isinstance(phases, dict) or set(phases) != set(PHASES):
        raise RuntimeError(f"phase universe differs: {label}")
    if ledger.get("phases_are_sequential_and_nonoverlapping") is not True:
        raise RuntimeError(f"phase ordering assertion absent: {label}")
    if ledger.get("nonobserved_phase_zero_imputed") is not False:
        raise RuntimeError(f"unobserved phase was imputed: {label}")
    observed_sum = 0
    last_end = 0
    projection: dict[str, int | None] = {}
    for name in PHASES:
        row = phases[name]
        if not isinstance(row, dict):
            raise RuntimeError(f"phase is not an object: {label}:{name}")
        duration = row.get("duration_ns")
        projection[name] = duration
        if duration is None:
            if name != "provider_session_close" \
                    or row.get("status") != "UNAVAILABLE__NO_EQUIVALENT_PUBLIC_STATE" \
                    or row.get("start_offset_ns") is not None:
                raise RuntimeError(f"unexpected unavailable phase: {label}:{name}")
            continue
        start = row.get("start_offset_ns")
        if row.get("status") != "OBSERVED" \
                or type(start) is not int or start < last_end \
                or type(duration) is not int or duration < 0:
            raise RuntimeError(f"invalid observed phase: {label}:{name}")
        observed_sum += duration
        last_end = start + duration
    total = ledger.get("total_profiled_full_process_ns")
    between = ledger.get("between_phase_unclassified_ns_additive")
    if type(total) is not int or total <= 0 \
            or type(between) is not int or between < 0 \
            or ledger.get("observed_phase_sum_ns_additive") != observed_sum \
            or observed_sum + between != total \
            or ledger.get("additive_closure_ns") != total:
        raise RuntimeError(f"phase additive closure differs: {label}")
    return total, projection


def regime_results(
    timings: dict[tuple[str, int, int, str], dict[str, int]], *,
    regime: str, thresholds: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    order = (ARMS[0], ARMS[1], ARMS[1], ARMS[0])
    for task in TASKS:
        ratios: list[float] = []
        rtdl_values: list[int] = []
        pyoptix_values: list[int] = []
        blocks: list[dict[str, Any]] = []
        for block in range(BLOCKS):
            by_arm = {
                arm: [
                    timings[(task, block, position, candidate)][regime]
                    for position, candidate in enumerate(order)
                    if candidate == arm
                ]
                for arm in ARMS
            }
            rtdl_block = median(by_arm[ARMS[0]])
            pyoptix_block = median(by_arm[ARMS[1]])
            ratio = rtdl_block / pyoptix_block
            rtdl_values.extend(by_arm[ARMS[0]])
            pyoptix_values.extend(by_arm[ARMS[1]])
            ratios.append(ratio)
            blocks.append({
                "block": block,
                "rtdl_median_ns": rtdl_block,
                "pyoptix_median_ns": pyoptix_block,
                "rtdl_over_pyoptix": ratio,
            })
        point = median(ratios)
        ci_low, ci_high = bootstrap_ci(ratios, seed=SEEDS[task])
        rtdl_median = median(rtdl_values)
        pyoptix_median = median(pyoptix_values)
        positive_gap = max(0.0, rtdl_median - pyoptix_median)
        row: dict[str, Any] = {
            "block_count": len(blocks),
            "block_rows": blocks,
            "median_block_ratio_rtdl_over_pyoptix": point,
            "bootstrap_ci_low": ci_low,
            "bootstrap_ci_high": ci_high,
            "rtdl_arm_median_ns": rtdl_median,
            "pyoptix_arm_median_ns": pyoptix_median,
            "ratio_of_arm_medians": rtdl_median / pyoptix_median,
            "positive_rtdl_minus_pyoptix_arm_median_gap_ns": positive_gap,
            "threshold_applied": thresholds is not None,
        }
        if thresholds is None:
            row["gates"] = None
            row["hypothesis_pass"] = None
        else:
            gates = {
                "median_ratio_pass": point <= thresholds[
                    "median_block_ratio_rtdl_over_pyoptix_max"],
                "bootstrap_ci_upper_pass": ci_high <= thresholds[
                    "bootstrap_ci_upper_max"],
                "positive_slower_gap_pass": positive_gap <= thresholds[
                    "positive_rtdl_minus_pyoptix_arm_median_gap_ns_max"],
            }
            row["gates"] = gates
            row["hypothesis_pass"] = all(gates.values())
        result[task] = row
    return result


def _require(condition: bool, message: str, findings: list[str]) -> None:
    if not condition:
        findings.append(message)


def audit(archive_path: Path, contract_path: Path, root_path: Path) -> dict[str, Any]:
    findings: list[str] = []
    archive_sha = sha_file(archive_path)
    _require(archive_sha == ARCHIVE_SHA256, "archive_sha256", findings)
    contract_raw = contract_path.read_bytes()
    contract_sha = sha_bytes(contract_raw)
    _require(contract_sha == CONTRACT_SHA256, "contract_sha256", findings)
    contract = strict_json(
        contract_raw, label="contract", canonical_line=False)
    if not isinstance(contract, dict):
        raise RuntimeError("contract root is not an object")
    pinned_files = contract.get("files")
    pin_mismatches: list[str] = []
    if not isinstance(pinned_files, dict):
        findings.append("contract_file_pins_absent")
    else:
        for name, descriptor in sorted(pinned_files.items()):
            if not isinstance(descriptor, dict) \
                    or set(descriptor) != {"path", "bytes", "sha256"}:
                pin_mismatches.append(name)
                continue
            path = Path(descriptor["path"])
            path = path if path.is_absolute() else root_path / path
            if not path.is_file() \
                    or path.stat().st_size != descriptor["bytes"] \
                    or sha_file(path) != descriptor["sha256"]:
                pin_mismatches.append(name)
        _require(not pin_mismatches, "contract_pinned_file_identity", findings)

    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name.rstrip("/") for member in members]
        _require(len(names) == len(set(names)), "duplicate_tar_member", findings)
        _require(len({name.casefold() for name in names}) == len(names),
                 "casefold_duplicate_tar_member", findings)
        for member, name in zip(members, names):
            path = PurePosixPath(name)
            _require(not path.is_absolute() and ".." not in path.parts
                     and "." not in path.parts and bool(path.parts),
                     f"unsafe_tar_path:{name}", findings)
            _require(member.isfile() or member.isdir(),
                     f"non_regular_tar_member:{name}", findings)
            _require(path.parts[0] == ROOT_NAME,
                     f"outside_single_root:{name}", findings)
        expected = expected_members(ROOT_NAME)
        _require(set(names) == expected, "tar_member_universe", findings)
        _require(len(members) == 1414, "tar_member_count", findings)
        _require(sum(member.isfile() for member in members) == 515,
                 "tar_file_count", findings)
        _require(sum(member.isdir() for member in members) == 899,
                 "tar_directory_count", findings)
        by_name = {name: member for name, member in zip(names, members)}

        def raw(relative: str) -> bytes:
            full = f"{ROOT_NAME}/{relative}"
            member = by_name[full]
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"file payload unavailable: {full}")
            return stream.read()

        controller_raw = raw("controller.json")
        evaluation_raw = raw("evaluation.json")
        recount_raw = raw("recount.json")
        controller = strict_json(controller_raw, label="controller")
        evaluation = strict_json(evaluation_raw, label="evaluation")
        recount = strict_json(recount_raw, label="recount")
        controller_sha = sha_bytes(controller_raw)
        evaluation_file_sha = sha_bytes(evaluation_raw)
        recount_file_sha = sha_bytes(recount_raw)

        _require(isinstance(controller, dict), "controller_root", findings)
        _require(isinstance(evaluation, dict), "evaluation_root", findings)
        _require(isinstance(recount, dict), "recount_root", findings)
        if not all(isinstance(value, dict)
                   for value in (controller, evaluation, recount)):
            raise RuntimeError("top-level receipt root differs")
        evaluation_body = dict(evaluation)
        evaluation_seal = evaluation_body.pop("evaluation_sha256", None)
        recount_body = dict(recount)
        recount_seal = recount_body.pop("recount_sha256", None)
        _require(evaluation_seal == sha_bytes(canonical(evaluation_body)),
                 "evaluation_self_seal", findings)
        _require(recount_seal == sha_bytes(canonical(recount_body)),
                 "recount_self_seal", findings)
        _require(evaluation.get("controller_sha256") == controller_sha,
                 "evaluation_controller_file_sha256", findings)
        _require(recount.get("controller_sha256") == controller_sha,
                 "recount_controller_file_sha256", findings)
        _require(recount.get("evaluation_sha256") == evaluation_file_sha,
                 "recount_evaluation_file_sha256", findings)
        for receipt_name, receipt in (
            ("controller", controller), ("evaluation", evaluation),
            ("recount", recount),
        ):
            _require(receipt.get("contract_sha256") == contract_sha,
                     f"{receipt_name}_contract_sha256", findings)

        coordinates = expected_coordinates()
        row_manifest = controller.get("row_sha256")
        _require(isinstance(row_manifest, dict)
                 and len(row_manifest) == len(coordinates),
                 "controller_row_manifest_shape", findings)
        if not isinstance(row_manifest, dict):
            row_manifest = {}

        pids: set[int] = set()
        timings: dict[tuple[str, int, int, str], dict[str, int]] = {}
        phase_values: dict[tuple[str, str, str], list[int]] = {}
        full_values: dict[tuple[str, str], list[int]] = {}
        full_by_worker: dict[str, dict[str, Any]] = {}
        python_paths: set[str] = set()
        source_roots: set[str] = set()
        command_contract_paths: set[str] = set()
        stdout_bytes = 0
        stderr_bytes = 0
        command_bytes = 0
        semantic_oracle_receipt_count = 0

        for task, block, position, arm, worker_id in coordinates:
            label = worker_id
            row_raw = raw(f"rows/{worker_id}.json")
            row = strict_json(row_raw, label=f"row:{label}")
            if not isinstance(row, dict):
                findings.append(f"row_root:{label}")
                continue
            _require(row_manifest.get(f"{worker_id}.json") == sha_bytes(row_raw),
                     f"row_manifest_sha256:{label}", findings)

            command_raw = raw(f"workers/{worker_id}/command.json")
            stdout_raw = raw(f"workers/{worker_id}/stdout.bin")
            stderr_raw = raw(f"workers/{worker_id}/stderr.bin")
            command_bytes += len(command_raw)
            stdout_bytes += len(stdout_raw)
            stderr_bytes += len(stderr_raw)
            command = strict_json(command_raw, label=f"command:{label}")
            worker = strict_json(stdout_raw, label=f"stdout:{label}")
            _require(isinstance(command, list) and len(command) == 13,
                     f"command_shape:{label}", findings)
            if isinstance(command, list) and len(command) == 13:
                expected_tail = [
                    "-m", "scripts.goal5807_provider_ready_formal_worker",
                    "--root", command[4], "--contract", command[6],
                    "--arm", arm, "--task", task, "--worker-id", worker_id,
                ]
                _require(command[1:] == expected_tail,
                         f"command_coordinates:{label}", findings)
                _require(all(isinstance(value, str) for value in command),
                         f"command_string_universe:{label}", findings)
                if all(isinstance(value, str) for value in command):
                    python_paths.add(command[0])
                    source_roots.add(command[4])
                    command_contract_paths.add(command[6])
            _require(stderr_raw == b"", f"stderr_nonempty:{label}", findings)
            _require(row.get("stderr_sha256") == sha_bytes(stderr_raw)
                     == EMPTY_SHA256, f"stderr_sha256:{label}", findings)
            _require(row.get("stdout_sha256") == sha_bytes(stdout_raw),
                     f"stdout_sha256:{label}", findings)
            _require(worker == row.get("worker_result"),
                     f"stdout_worker_result_equality:{label}", findings)
            _require(row.get("cache_files_after") == [],
                     f"cache_files_after:{label}", findings)

            expected_row = {
                "schema": "rtdl.goal5807.provider_ready_formal_row.v2",
                "status": "PASS",
                "contract_sha256": contract_sha,
                "worker_id": worker_id,
                "task": task,
                "block": block,
                "position": position,
                "arm": arm,
                "returncode": 0,
                "registered_performance_timing_count": 3,
            }
            for key, value in expected_row.items():
                _require(row.get(key) == value, f"row_{key}:{label}", findings)
            pid = row.get("pid")
            _require(type(pid) is int and pid > 0 and pid not in pids,
                     f"pid:{label}", findings)
            if type(pid) is int and pid > 0:
                pids.add(pid)
            if not isinstance(worker, dict):
                findings.append(f"worker_root:{label}")
                continue
            worker_body = dict(worker)
            worker_seal = worker_body.pop("worker_receipt_sha256", None)
            _require(worker_seal == sha_bytes(canonical(worker_body)),
                     f"worker_self_seal:{label}", findings)
            expected_worker = {
                "schema": "rtdl.goal5807.provider_ready_formal_worker.v2",
                "status": "PASS__EXACT_ORACLE_AND_PHASE_LEDGER",
                "contract_sha256": contract_sha,
                "worker_id": worker_id,
                "task": task,
                "arm": arm,
                "pid": pid,
                "formal_worker_count": 1,
                "registered_performance_timing_count": 3,
                "all_phases_preserved_nonprimary": True,
            }
            for key, value in expected_worker.items():
                _require(worker.get(key) == value,
                         f"worker_{key}:{label}", findings)
            registered = worker.get("registered_timing_ns")
            _require(isinstance(registered, dict)
                     and set(registered) == set(REGIMES)
                     and all(type(value) is int and value > 0
                             for value in registered.values()),
                     f"registered_timings:{label}", findings)
            if not isinstance(registered, dict) \
                    or set(registered) != set(REGIMES):
                continue
            timings[(task, block, position, arm)] = dict(registered)
            primary = worker.get(
                "primary_app_prepare_plus_first_exact_execute_ns")
            _require(primary == registered[REGIMES[0]],
                     f"primary_timing_projection:{label}", findings)

            pilot = worker.get("pilot_receipt")
            if not isinstance(pilot, dict):
                findings.append(f"pilot_receipt:{label}")
                continue
            pilot_body = dict(pilot)
            pilot_seal = pilot_body.pop("pilot_sha256", None)
            _require(pilot_seal == sha_bytes(canonical(pilot_body)),
                     f"pilot_self_seal:{label}", findings)
            _require(worker.get("pilot_receipt_sha256")
                     == sha_bytes(canonical(pilot)),
                     f"worker_pilot_receipt_sha256:{label}", findings)
            _require(pilot.get("schema") == "rtdl.goal5807.provider_ready_pilot.v3"
                     and pilot.get("formal_worker_count") == 0
                     and pilot.get("registered_performance_timing_count") == 0
                     and pilot.get("task") == task and pilot.get("arm") == arm,
                     f"pilot_identity:{label}", findings)
            boundaries = pilot.get("contiguous_prefix_boundaries")
            comparable = pilot.get("comparable_app_boundary")
            _require(isinstance(boundaries, dict)
                     and boundaries.get(REGIMES[1], {}).get("duration_ns")
                     == registered[REGIMES[1]]
                     and boundaries.get(REGIMES[2], {}).get("duration_ns")
                     == registered[REGIMES[2]],
                     f"prefix_timing_projection:{label}", findings)
            _require(isinstance(comparable, dict)
                     and comparable.get("duration_ns_additive") == primary,
                     f"app_timing_projection:{label}", findings)
            total, projection = validate_phase_ledger(
                pilot.get("phase_ledger"), label=label)
            _require(worker.get("full_process_total_ns_nonprimary") == total,
                     f"full_process_timing_projection:{label}", findings)
            _require(projection["app_prepare"] is not None
                     and projection["first_exact_execute"] is not None
                     and projection["app_prepare"]
                     + projection["first_exact_execute"] == primary,
                     f"phase_primary_projection:{label}", findings)
            full_values.setdefault((task, arm), []).append(total)
            for phase, value in projection.items():
                if value is not None:
                    phase_values.setdefault((task, arm, phase), []).append(value)
            full_by_worker[worker_id] = {
                "task": task,
                "arm": arm,
                "full_process_total_ns_nonprimary": total,
                "phase_duration_ns_nonprimary": projection,
            }
            validation = pilot.get("validation")
            if isinstance(validation, dict):
                first = validation.get("first_evidence")
                first_sha = validation.get("first_evidence_sha256")
                if validation.get("oracle_validated_execution_count") == 2 \
                        and isinstance(first, dict) \
                        and first_sha == sha_bytes(canonical(first)):
                    semantic_oracle_receipt_count += 1
                else:
                    findings.append(f"oracle_evidence_receipt:{label}")
            else:
                findings.append(f"oracle_validation:{label}")

        _require(len(pids) == 128, "unique_pid_count", findings)
        _require(len(timings) == 128, "raw_timing_worker_count", findings)
        _require(semantic_oracle_receipt_count == 128,
                 "oracle_evidence_receipt_count", findings)
        _require(len(python_paths) == len(source_roots)
                 == len(command_contract_paths) == 1,
                 "command_environment_path_consistency", findings)
        if len(source_roots) == 1 and len(command_contract_paths) == 1:
            source_root = next(iter(source_roots))
            expected_contract = (
                f"{source_root}/history/internal_docs/"
                "goal5807_provider_ready_confirmatory_formal_contract_v2_20260827.json")
            _require(next(iter(command_contract_paths)) == expected_contract,
                     "command_contract_path", findings)

        thresholds = contract["hypotheses"]["app_boundary"]
        raw_results = {
            regime: regime_results(
                timings, regime=regime,
                thresholds=(thresholds if regime != REGIMES[2] else None))
            for regime in REGIMES
        }
        expected_thresholded = {
            REGIMES[0]: raw_results[REGIMES[0]],
            REGIMES[1]: raw_results[REGIMES[1]],
        }
        expected_unthresholded = {REGIMES[2]: raw_results[REGIMES[2]]}
        _require(evaluation.get("thresholded_results") == expected_thresholded,
                 "evaluation_thresholded_raw_reconstruction", findings)
        _require(evaluation.get("unthresholded_first_class_results")
                 == expected_unthresholded,
                 "evaluation_unthresholded_raw_reconstruction", findings)
        _require(recount.get("recomputed_thresholded_results")
                 == expected_thresholded,
                 "recount_thresholded_raw_reconstruction", findings)
        _require(recount.get("recomputed_unthresholded_first_class_results")
                 == expected_unthresholded,
                 "recount_unthresholded_raw_reconstruction", findings)

        phase_medians = {
            task: {
                arm: {
                    phase: (
                        median(phase_values[(task, arm, phase)])
                        if (task, arm, phase) in phase_values else None)
                    for phase in PHASES
                }
                for arm in ARMS
            }
            for task in TASKS
        }
        full_medians = {
            task: {
                arm: median(full_values[(task, arm)]) for arm in ARMS
            }
            for task in TASKS
        }
        _require(evaluation.get("nonprimary_phase_medians_ns") == phase_medians,
                 "evaluation_phase_medians_raw_reconstruction", findings)
        _require(evaluation.get("nonprimary_full_process_total_medians_ns")
                 == full_medians,
                 "evaluation_full_medians_raw_reconstruction", findings)
        _require(evaluation.get("nonprimary_full_process_evidence_by_worker")
                 == full_by_worker,
                 "evaluation_full_worker_projection", findings)
        _require(recount.get("recomputed_nonprimary_phase_medians_ns")
                 == phase_medians,
                 "recount_phase_medians_raw_reconstruction", findings)
        _require(recount.get(
            "recomputed_nonprimary_full_process_total_medians_ns")
            == full_medians,
            "recount_full_medians_raw_reconstruction", findings)

        all_thresholds_pass = all(
            row["hypothesis_pass"]
            for regime in expected_thresholded.values()
            for row in regime.values())
        _require(evaluation.get(
            "all_thresholded_regimes_and_tasks_hypothesis_pass")
            == all_thresholds_pass, "evaluation_overall_result", findings)
        _require(evaluation.get("status") == "VALID_RESULT__HYPOTHESES_PASS",
                 "evaluation_status", findings)
        _require(recount.get("status") == "PASS"
                 and recount.get("finding_count") == 0
                 and recount.get("findings") == [],
                 "recount_status", findings)
        for receipt_name, receipt in (
            ("controller", controller), ("evaluation", evaluation),
            ("recount", recount),
        ):
            _require(receipt.get("worker_count") == 128
                     and receipt.get("unique_worker_pid_count") == 128
                     and receipt.get("registered_performance_timing_count") == 384,
                     f"{receipt_name}_aggregate_counts", findings)

    concise_stats = {
        regime: {
            task: {
                key: raw_results[regime][task][key]
                for key in (
                    "median_block_ratio_rtdl_over_pyoptix",
                    "bootstrap_ci_low",
                    "bootstrap_ci_high",
                    "rtdl_arm_median_ns",
                    "pyoptix_arm_median_ns",
                    "ratio_of_arm_medians",
                    "positive_rtdl_minus_pyoptix_arm_median_gap_ns",
                    "hypothesis_pass",
                )
            }
            for task in TASKS
        }
        for regime in REGIMES
    }
    return {
        "schema": "rtdl.goal5807.independent_archive_custody_audit.v1",
        "status": "PASS" if not findings else "FAIL",
        "archive_sha256": archive_sha,
        "archive_bytes": archive_path.stat().st_size,
        "contract_sha256": contract_sha,
        "contract_pinned_file_count": (
            len(pinned_files) if isinstance(pinned_files, dict) else 0),
        "contract_pinned_file_mismatches": pin_mismatches,
        "tar_member_count": 1414,
        "tar_file_count": 515,
        "tar_directory_count": 899,
        "worker_count": 128,
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": len(timings) * 3,
        "semantic_oracle_receipt_count": semantic_oracle_receipt_count,
        "worker_stdout_bytes": stdout_bytes,
        "worker_stderr_bytes": stderr_bytes,
        "worker_command_bytes": command_bytes,
        "controller_file_sha256": controller_sha,
        "evaluation_logical_seal": evaluation_seal,
        "evaluation_file_sha256": evaluation_file_sha,
        "recount_logical_seal": recount_seal,
        "recount_file_sha256": recount_file_sha,
        "raw_stdout_recomputed_results": concise_stats,
        "evaluation_exact_match": (
            evaluation.get("thresholded_results") == expected_thresholded
            and evaluation.get("unthresholded_first_class_results")
            == expected_unthresholded),
        "recount_exact_match": (
            recount.get("recomputed_thresholded_results")
            == expected_thresholded
            and recount.get("recomputed_unthresholded_first_class_results")
            == expected_unthresholded),
        "custody_scope": {
            "controller_row_manifest_binds_row_bytes": True,
            "row_binds_stdout_and_stderr_sha256": True,
            "stdout_exactly_equals_embedded_worker_result": True,
            "row_schema_binds_command_sha256": False,
            "row_schema_binds_cache_payload_sha256": False,
            "exact_outer_archive_sha256_binds_all_archived_bytes": True,
            "contract_embedded_in_archive": False,
            "actual_subprocess_environment_embedded_in_archive": False,
        },
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.archive.resolve(strict=True),
        args.contract.resolve(strict=True),
        args.root.resolve(strict=True),
    )
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
