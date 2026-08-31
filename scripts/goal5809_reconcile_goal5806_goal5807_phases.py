"""Independently reconcile the absolute Goal5806/Goal5807 time boundaries.

This script reads only immutable archives plus the Goal5807 pilot source whose
identity is carried by every raw worker receipt.  It deliberately does not
read or import either goal's controller, evaluator, recount, result, or product
implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import tarfile
from typing import Any, Callable, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOAL5806_ARCHIVE = (
    ROOT / "history" / "internal_docs"
    / "goal5806_triangle_product_projection_evidence_20260826.tar.gz")
DEFAULT_GOAL5807_ARCHIVE = (
    ROOT / "history" / "internal_docs"
    / "goal5807_provider_ready_formal_v2_20260827_0112.tar.gz")
DEFAULT_GOAL5807_PILOT_SOURCE = (
    ROOT / "scripts" / "goal5807_provider_ready_pilot.py")
DEFAULT_OUTPUT = (
    ROOT / "history" / "internal_docs"
    / "goal5807_postreview_absolute_phase_reconciliation_20260827.json")

GOAL5806_MEMBER_FRAGMENT = "/formal_postimport_same_source_v1/workers/"
GOAL5806_SOURCE_SUFFIX = "/experiments/goal5805_successor/formal_worker.py"
GOAL5806_ADAPTER_SOURCE_SUFFIX = \
    "/experiments/goal5802_premeasurement/rtdlexe_arm.py"
GOAL5806_RUNTIME_SOURCE_SUFFIX = "/src/rtdsl/v4_rtdlexe.py"
GOAL5807_MEMBER_FRAGMENT = "/workers/"

GOAL5806_TASKS = ("relation", "triangle")
GOAL5806_ARMS = ("PYOPTIX", "RTDL")
GOAL5807_ARMS = (
    "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY",
    "RTDL_PROVIDER_READY",
)
GOAL5807_PHASES = (
    "runtime_preload",
    "input_admission",
    "adapter_construct",
    "install_load",
    "provider_bind",
    "app_prepare",
    "first_exact_execute",
)
GOAL5807_ALL_PHASES = (
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
GOAL5807_PREFIXES = (
    "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT",
    "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_record(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.name,
        "bytes": len(payload),
        "sha256": _sha256(payload),
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _regular_file_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    names = [member.name for member in members]
    _require(len(names) == len(set(names)), "archive contains duplicate paths")
    for member in members:
        path = Path(member.name.replace("\\", "/"))
        _require(not path.is_absolute() and ".." not in path.parts,
                 f"archive contains unsafe path: {member.name}")
    return [member for member in members if member.isfile()]


def _load_json_members(
    archive_path: Path,
    predicate: Callable[[str], bool],
) -> tuple[list[tuple[str, bytes, dict[str, Any]]], dict[str, object]]:
    rows: list[tuple[str, bytes, dict[str, Any]]] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in _regular_file_members(archive):
            if not predicate(member.name):
                continue
            stream = archive.extractfile(member)
            _require(stream is not None, f"archive member unreadable: {member.name}")
            payload = stream.read()
            value = json.loads(payload)
            _require(isinstance(value, dict),
                     f"JSON root is not an object: {member.name}")
            rows.append((member.name, payload, value))
    rows.sort(key=lambda row: row[0].encode("utf-8"))
    manifest = [
        {"member": name, "bytes": len(payload), "sha256": _sha256(payload)}
        for name, payload, _ in rows
    ]
    return rows, {
        "member_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in manifest),
        "payload_manifest_sha256": _sha256(_canonical(manifest)),
    }


def _read_single_archive_member(
    archive_path: Path, suffix: str,
) -> tuple[str, bytes]:
    with tarfile.open(archive_path, "r:gz") as archive:
        matches = [
            member for member in _regular_file_members(archive)
            if member.name.endswith(suffix)
        ]
        _require(len(matches) == 1,
                 f"expected one archive member ending {suffix!r}; got {len(matches)}")
        stream = archive.extractfile(matches[0])
        _require(stream is not None, f"archive member unreadable: {matches[0].name}")
        return matches[0].name, stream.read()


def _median(values: Iterable[int]) -> int | float:
    rows = list(values)
    _require(bool(rows), "median input is empty")
    return statistics.median(rows)


def _ratio(numerator: int | float, denominator: int | float) -> float:
    _require(denominator > 0, "ratio denominator is not positive")
    return float(numerator) / float(denominator)


def _group_counts(
    rows: Iterable[Mapping[str, Any]], arms: tuple[str, ...],
) -> dict[str, int]:
    counts = {
        f"{task}/{arm}": 0
        for task in GOAL5806_TASKS for arm in arms
    }
    for row in rows:
        key = f"{row.get('task')}/{row.get('arm')}"
        _require(key in counts, f"unexpected task/arm: {key}")
        counts[key] += 1
    return counts


def _reconstruct_goal5806(
    archive_path: Path,
) -> dict[str, Any]:
    members, raw_manifest = _load_json_members(
        archive_path,
        lambda name: (
            GOAL5806_MEMBER_FRAGMENT in name
            and name.endswith("/stdout.bin")
        ),
    )
    rows = [value for _, _, value in members]
    _require(len(rows) == 128, "Goal5806 raw worker count differs")
    _require(all(row.get("schema") == "rtdl.goal5805.formal_worker_result.v1"
                 for row in rows), "Goal5806 raw worker schema differs")
    _require(all(row.get("status") == "PASS" for row in rows),
             "Goal5806 raw worker status differs")
    counts = _group_counts(rows, GOAL5806_ARMS)
    _require(set(counts.values()) == {32}, "Goal5806 task/arm counts differ")
    _require(sum(int(row["registered_performance_timing_count"])
                 for row in rows) == 8_448,
             "Goal5806 registered timing count differs")
    _require(all(len(row["steady_ns"]) == 64 for row in rows),
             "Goal5806 steady sample count differs")
    _require(all(row["deployment_cold_ns"] == (
        row["load_ns"] + row["prepare_ns"] + row["first_execute_ns"])
        for row in rows), "Goal5806 deployment-cold additive closure differs")
    _require(all(row["steady_median_ns"]
                 == int(statistics.median(row["steady_ns"]))
                 for row in rows), "Goal5806 worker steady median differs")

    absolute_rows: list[dict[str, Any]] = []
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for task in GOAL5806_TASKS:
        for arm in GOAL5806_ARMS:
            group = [row for row in rows
                     if row["task"] == task and row["arm"] == arm]
            value = {
                "task": task,
                "arm": arm,
                "raw_worker_count": len(group),
                "absolute_median_ns": {
                    "LOAD": _median(int(row["load_ns"]) for row in group),
                    "PREPARE": _median(int(row["prepare_ns"]) for row in group),
                    "FIRST_EXACT_EXECUTE": _median(
                        int(row["first_execute_ns"]) for row in group),
                    "DEPLOYMENT_COLD": _median(
                        int(row["deployment_cold_ns"]) for row in group),
                    "STEADY_E2E": _median(
                        int(row["steady_median_ns"]) for row in group),
                },
            }
            absolute_rows.append(value)
            lookup[(task, arm)] = value

    ratios: list[dict[str, Any]] = []
    for task in GOAL5806_TASKS:
        for regime in ("PREPARE", "DEPLOYMENT_COLD", "STEADY_E2E"):
            rtdl = lookup[(task, "RTDL")]["absolute_median_ns"][regime]
            pyoptix = lookup[(task, "PYOPTIX")]["absolute_median_ns"][regime]
            ratios.append({
                "task": task,
                "regime": regime,
                "ratio_of_absolute_arm_medians_rtdl_over_pyoptix":
                    _ratio(rtdl, pyoptix),
            })

    source_name, source_bytes = _read_single_archive_member(
        archive_path, GOAL5806_SOURCE_SUFFIX)
    source_text = source_bytes.decode("utf-8")
    boundary_tokens = (
        "load_start = time.perf_counter_ns()",
        "adapter.load()",
        "load_end = time.perf_counter_ns()",
        "adapter.prepare()",
        "prepare_end = time.perf_counter_ns()",
        '"prepare_ns": prepare_end - load_end',
        '"deployment_cold_ns": first_end - load_start',
    )
    token_offsets = [source_text.index(token) for token in boundary_tokens]
    _require(token_offsets == sorted(token_offsets),
             "Goal5806 frozen worker timer sequence differs")

    adapter_name, adapter_bytes = _read_single_archive_member(
        archive_path, GOAL5806_ADAPTER_SOURCE_SUFFIX)
    adapter_text = adapter_bytes.decode("utf-8")
    adapter_tokens = (
        "self.prepared = self.loaded.prepare(",
        "static, native_library_path=self.paths.native_library)",
    )
    adapter_offsets = [adapter_text.index(token) for token in adapter_tokens]
    _require(adapter_offsets == sorted(adapter_offsets),
             "Goal5806 frozen adapter default prepare route differs")

    runtime_name, runtime_bytes = _read_single_archive_member(
        archive_path, GOAL5806_RUNTIME_SOURCE_SUFFIX)
    runtime_text = runtime_bytes.decode("utf-8")
    loaded_class_offset = runtime_text.index("class LoadedRTDLExecutable")
    loaded_prepare_offset = runtime_text.index(
        "    def prepare(", loaded_class_offset)
    native_load_offset = runtime_text.index(
        "library = _load_native_library(", loaded_prepare_offset)
    prepared_return_offset = runtime_text.index(
        "return PreparedRTDLExecutable(", native_load_offset)
    _require(loaded_prepare_offset < native_load_offset < prepared_return_offset,
             "Goal5806 frozen runtime provider acquisition route differs")

    return {
        "archive": _file_record(archive_path),
        "raw_stdout": raw_manifest,
        "raw_worker_count": len(rows),
        "raw_task_arm_counts": counts,
        "registered_performance_timing_count_recounted": 8_448,
        "steady_sample_count_recounted": 8_192,
        "frozen_worker_source": {
            "member": source_name,
            "bytes": len(source_bytes),
            "sha256": _sha256(source_bytes),
            "timer_sequence_tokens_found_in_order": list(boundary_tokens),
        },
        "frozen_rtdl_adapter_source": {
            "member": adapter_name,
            "bytes": len(adapter_bytes),
            "sha256": _sha256(adapter_bytes),
            "default_prepare_calls_loaded_prepare_with_native_library": True,
            "source_tokens_found_in_order": list(adapter_tokens),
        },
        "frozen_rtdl_runtime_source": {
            "member": runtime_name,
            "bytes": len(runtime_bytes),
            "sha256": _sha256(runtime_bytes),
            "loaded_prepare_loads_native_provider_before_constructing_prepared_"
            "owner": True,
        },
        "absolute_arm_medians": absolute_rows,
        "descriptive_ratios": ratios,
        "boundary_definitions_from_frozen_worker": {
            "PREPARE": (
                "prepare_end_minus_load_end__one_adapter_prepare_call_only__"
                "excludes_adapter_load_and_first_execute"),
            "DEPLOYMENT_COLD": (
                "first_end_minus_load_start__adapter_load_plus_adapter_prepare_"
                "plus_first_exact_execute"),
            "STEADY_E2E": (
                "median_of_64_execute_call_durations_inside_each_worker__then_"
                "absolute_median_across_32_workers_per_task_arm"),
        },
    }


def _reconstruct_goal5807(
    archive_path: Path, pilot_source_path: Path,
) -> dict[str, Any]:
    members, raw_manifest = _load_json_members(
        archive_path,
        lambda name: (
            GOAL5807_MEMBER_FRAGMENT in name
            and name.endswith("/stdout.bin")
        ),
    )
    rows = [value for _, _, value in members]
    _require(len(rows) == 128, "Goal5807 raw worker count differs")
    _require(all(row.get("schema")
                 == "rtdl.goal5807.provider_ready_formal_worker.v2"
                 for row in rows), "Goal5807 raw worker schema differs")
    _require(all(row.get("status") == "PASS__EXACT_ORACLE_AND_PHASE_LEDGER"
                 for row in rows), "Goal5807 raw worker status differs")
    counts = _group_counts(rows, GOAL5807_ARMS)
    _require(set(counts.values()) == {32}, "Goal5807 task/arm counts differ")
    _require(sum(int(row["registered_performance_timing_count"])
                 for row in rows) == 384,
             "Goal5807 registered timing count differs")

    pilot_source = pilot_source_path.read_bytes()
    pilot_sha = _sha256(pilot_source)
    pilot_size = len(pilot_source)
    _require(all(row["pilot_receipt"]["pilot_source"]["sha256"] == pilot_sha
                 and row["pilot_receipt"]["pilot_source"]["bytes"] == pilot_size
                 for row in rows),
             "Goal5807 raw receipts do not bind the supplied pilot source")
    source_text = pilot_source.decode("utf-8")
    source_tokens = (
        'with ledger.phase("provider_bind"):',
        'with ledger.phase("app_prepare"):',
        "adapter.prepare()",
        'with ledger.phase("first_exact_execute"):',
    )
    provider_offset = source_text.index(source_tokens[0])
    app_offset = source_text.index(source_tokens[1])
    execute_offset = source_text.index(source_tokens[3])
    _require(provider_offset < app_offset < execute_offset,
             "Goal5807 pilot source phase order differs")

    provider_before_app_count = 0
    additive_boundary_match_count = 0
    prefix_match_count = 0
    for row in rows:
        receipt = row["pilot_receipt"]
        ledger = receipt["phase_ledger"]
        phases = ledger["phases"]
        _require(set(phases) == set(GOAL5807_ALL_PHASES),
                 "Goal5807 phase ledger is incomplete")
        provider = phases["provider_bind"]
        app = phases["app_prepare"]
        if (int(provider["start_offset_ns"]) + int(provider["duration_ns"])
                <= int(app["start_offset_ns"])):
            provider_before_app_count += 1
        additive = (int(app["duration_ns"])
                    + int(phases["first_exact_execute"]["duration_ns"]))
        if additive == int(row["primary_app_prepare_plus_first_exact_execute_ns"]):
            additive_boundary_match_count += 1
        prefixes = receipt["contiguous_prefix_boundaries"]
        if all(
            prefixes[name]["single_contiguous_timer"] is True
            and int(prefixes[name]["duration_ns"])
            == int(row["registered_timing_ns"][name])
            for name in GOAL5807_PREFIXES
        ):
            prefix_match_count += 1
    _require(provider_before_app_count == 128,
             "Goal5807 provider_bind does not precede app_prepare in every row")
    _require(additive_boundary_match_count == 128,
             "Goal5807 additive app boundary differs")
    _require(prefix_match_count == 128,
             "Goal5807 continuous prefix receipt differs")

    absolute_rows: list[dict[str, Any]] = []
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for task in GOAL5806_TASKS:
        for arm in GOAL5807_ARMS:
            group = [row for row in rows
                     if row["task"] == task and row["arm"] == arm]
            phase_medians = {
                name: _median(int(row["pilot_receipt"]["phase_ledger"]
                                      ["phases"][name]["duration_ns"])
                              for row in group)
                for name in GOAL5807_PHASES
            }
            prefix_medians = {
                name: _median(int(row["registered_timing_ns"][name])
                              for row in group)
                for name in GOAL5807_PREFIXES
            }
            value = {
                "task": task,
                "arm": arm,
                "raw_worker_count": len(group),
                "absolute_phase_median_ns": phase_medians,
                "absolute_continuous_prefix_median_ns": prefix_medians,
                "absolute_additive_app_prepare_plus_first_exact_execute_"
                "median_ns": _median(
                    int(row["primary_app_prepare_plus_first_exact_execute_ns"])
                    for row in group),
            }
            absolute_rows.append(value)
            lookup[(task, arm)] = value

    ratio_rows: list[dict[str, Any]] = []
    for task in GOAL5806_TASKS:
        rtdl = lookup[(task, "RTDL_PROVIDER_READY")]
        pyoptix = lookup[(task, "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY")]
        phase_ratios = {
            name: _ratio(
                rtdl["absolute_phase_median_ns"][name],
                pyoptix["absolute_phase_median_ns"][name])
            for name in GOAL5807_PHASES
        }
        prefix_ratios = {
            name: _ratio(
                rtdl["absolute_continuous_prefix_median_ns"][name],
                pyoptix["absolute_continuous_prefix_median_ns"][name])
            for name in GOAL5807_PREFIXES
        }
        ratio_rows.append({
            "task": task,
            "ratio_of_absolute_arm_medians_rtdl_over_pyoptix": {
                "phases": phase_ratios,
                "continuous_prefixes": prefix_ratios,
                "additive_app_prepare_plus_first_exact_execute": _ratio(
                    rtdl[
                        "absolute_additive_app_prepare_plus_first_exact_execute_"
                        "median_ns"],
                    pyoptix[
                        "absolute_additive_app_prepare_plus_first_exact_execute_"
                        "median_ns"]),
            },
        })

    return {
        "archive": _file_record(archive_path),
        "raw_stdout": raw_manifest,
        "raw_worker_count": len(rows),
        "raw_task_arm_counts": counts,
        "registered_performance_timing_count_recounted": 384,
        "phase_observation_count_recounted": 128 * len(GOAL5807_ALL_PHASES),
        "pilot_source": {
            "path": pilot_source_path.name,
            "bytes": pilot_size,
            "sha256": pilot_sha,
            "bound_by_all_raw_worker_receipts": True,
            "provider_bind_app_prepare_first_execute_tokens_found_in_order":
                list(source_tokens),
        },
        "raw_invariants": {
            "provider_bind_ends_no_later_than_app_prepare_starts_count":
                provider_before_app_count,
            "additive_app_boundary_exact_match_count":
                additive_boundary_match_count,
            "continuous_prefix_exact_match_count": prefix_match_count,
        },
        "absolute_arm_medians": absolute_rows,
        "descriptive_ratios": ratio_rows,
        "boundary_definitions_from_raw_receipts": {
            "app_prepare": (
                "adapter.prepare_only_after_provider_bind_completed__excludes_"
                "runtime_preload_input_admission_adapter_construct_install_load_"
                "and_provider_bind"),
            "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE": (
                "sum_of_two_observed_phase_durations__not_one_contiguous_timer"),
            "HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT": (
                "single_contiguous_timer_from_harness_run_entry_to_validated_"
                "first_exact_output"),
            "POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT": (
                "single_contiguous_timer_from_runtime_preload_return_to_"
                "validated_first_exact_output"),
        },
    }


def build_reconciliation(
    goal5806_archive: Path,
    goal5807_archive: Path,
    goal5807_pilot_source: Path,
) -> dict[str, Any]:
    goal5806_archive = goal5806_archive.resolve(strict=True)
    goal5807_archive = goal5807_archive.resolve(strict=True)
    goal5807_pilot_source = goal5807_pilot_source.resolve(strict=True)
    value: dict[str, Any] = {
        "schema": "rtdl.goal5807.postreview_absolute_phase_reconciliation.v1",
        "date": "2026-08-27",
        "status": "COMPLETE__DESCRIPTIVE_RAW_ARCHIVE_RECONSTRUCTION_ONLY",
        "method": {
            "primary_evaluator_imported": False,
            "primary_evaluator_output_read": False,
            "controller_output_read": False,
            "published_result_read": False,
            "product_implementation_imported": False,
            "threshold_evaluation_performed": False,
            "inferential_claim_authorized": False,
        },
        "goal5806": _reconstruct_goal5806(goal5806_archive),
        "goal5807": _reconstruct_goal5807(
            goal5807_archive, goal5807_pilot_source),
        "reconciliation": {
            "same_named_prepare_boundary": False,
            "goal5806_prepare": (
                "The frozen Goal5806 worker starts PREPARE immediately after "
                "adapter.load returns and stops immediately after one "
                "adapter.prepare call.  The default RTDL prepare route owns "
                "provider acquisition inside that call; first execution is "
                "excluded."),
            "goal5807_app_prepare": (
                "Every raw Goal5807 ledger ends a separately observed "
                "provider_bind phase before app_prepare starts.  Exact program "
                "bytes, provider/runtime readiness, and the device-0 primary "
                "context are therefore already established; first execution "
                "is separately observed."),
            "why_ratios_can_change_without_contradiction": (
                "Goal5807 moves provider readiness out of app_prepare for both "
                "arms and reports app_prepare plus first exact execute as an "
                "additive boundary.  Goal5806 PREPARE leaves provider work in "
                "the RTDL default prepare call and excludes first execute.  "
                "The measurements answer different lifecycle questions; a "
                "favorable Goal5807 app-boundary ratio does not replace or "
                "contradict the unfavorable Goal5806 PREPARE or "
                "DEPLOYMENT_COLD observations."),
            "continuous_boundary_correspondence": (
                "Neither Goal5807 continuous prefix is Goal5806 "
                "DEPLOYMENT_COLD.  Goal5806 begins after runtime preload and "
                "adapter construction, at adapter.load; the Goal5807 harness "
                "prefix begins earlier, while its post-runtime prefix still "
                "includes adapter construction, install/load, and the separate "
                "provider bind."),
        },
        "limits": {
            "descriptive_absolute_medians_only": True,
            "ratios_are_ratio_of_arm_medians_not_registered_paired_estimator":
                True,
            "new_performance_sample_count": 0,
            "new_gpu_execution_count": 0,
            "new_scientific_verdict_emitted": False,
            "goal5806_or_goal5807_result_replaced": False,
        },
    }
    value["reconciliation_sha256"] = _sha256(_canonical(value))
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--goal5806-archive", type=Path, default=DEFAULT_GOAL5806_ARCHIVE)
    parser.add_argument(
        "--goal5807-archive", type=Path, default=DEFAULT_GOAL5807_ARCHIVE)
    parser.add_argument(
        "--goal5807-pilot-source", type=Path,
        default=DEFAULT_GOAL5807_PILOT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    value = build_reconciliation(
        args.goal5806_archive, args.goal5807_archive,
        args.goal5807_pilot_source)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": _sha256(output.read_bytes()),
        "reconciliation_sha256": value["reconciliation_sha256"],
    }, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
