"""Independent stdlib audit of the Goal5791 terminal analysis successor."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import random
import statistics
import tarfile
from fractions import Fraction
from typing import Mapping


GOAL = 5791
TERMINAL_ARCHIVE_SHA256 = (
    "53845c836bd5e0048ec9b997ab9f4732eb121ec9c1d116ed5486f02be77f0252"
)
TERMINAL_ROOT = ".goal5791_formal_output_v4_20260821.goal5791_incomplete"
RESULT_FILE_SHA256 = (
    "e8417161e33574bb76d1652a3783bfeae77fbe1777e236bfdb066f149b0c6bc5"
)
RESULT_INTERNAL_SHA256 = (
    "b91c1dc8cb76f2785f89e7ba6a658bd44eedd449c4c5271b68dfba75347c1bc8"
)
EVALUATION_FILE_SHA256 = (
    "69e56a6220d9495d40a74e0ca98b4fc7d1fd58ca049b8f910cb2a0eea970b819"
)
EVALUATION_INTERNAL_SHA256 = (
    "0d5d9029e614405487915f93676b7910d344c0797968b86715e50897bc0858c4"
)
RECOUNT_FILE_SHA256 = (
    "d50d7ae765b2da96db97d8db6592c4eb856e53822c9fd8851f32d114a30ace38"
)
RECOUNT_INTERNAL_SHA256 = (
    "a368174c1046e4b45a2bc03e6c2b32616e133b5258b9eea6358ed771d469d6e3"
)
RESULT_FIELDS = {
    "schema", "goal", "status", "controller_transaction", "terminal_archive",
    "analysis_source_lineage", "primary_evaluation", "independent_recount",
    "primary_and_independent_common_fields_exactly_equal",
    "primary_and_independent_common_field_count",
    "primary_and_independent_rows_exactly_equal", "formal_contract_sha256",
    "schedule_sha256", "runtime_file_sha256", "runtime_sha256",
    "raw_worker_set_sha256", "formal_worker_count", "independent_row_count",
    "ci_clear_win_count", "ci_clear_loss_count", "ci_crossing_count",
    "paper_clear_winning_row_count", "paper_clear_winning_row_ids",
    "ci_clear_win_trace_cost_inconclusive_count",
    "ci_clear_win_trace_cost_inconclusive_row_ids",
    "paper_outcome_consequence_selection", "rows", "claim_boundary",
    "authorization", "analysis_successor_sha256",
}
EVALUATION_FIELDS = {
    "all_six_rows_retained", "behavioral_true_optix_worker_count",
    "cache_payloads_must_be_removed_before_final_cohort_publication",
    "cache_payloads_non_authoritative", "cache_receipts_preserved",
    "ci_clear_loss_count", "ci_clear_win_count",
    "ci_clear_win_trace_cost_inconclusive_count",
    "ci_clear_win_trace_cost_inconclusive_row_ids", "ci_crossing_count",
    "claim_boundary", "cold_process_warm_system_definition",
    "cold_process_warm_system_excludes",
    "cross_dataset_lifecycle_or_row_compensation_used",
    "cuda_driver_jit_cache_controlled_or_isolated", "data_admission_sha256",
    "empty_cache_directory_shells_are_authoritative_evidence",
    "evaluation_sha256", "every_figure_caption_must_state_includes_evidence_overhead",
    "exact_output_worker_count", "failed_terminal_staging_may_preserve_cache_payloads",
    "formal_authority_file_sha256", "formal_contract_sha256", "goal",
    "independent_recount_external_review_status", "independent_row_count",
    "operating_system_page_cache_controlled_or_dropped",
    "operating_system_page_cache_scope", "operation_delta_exact_all_workers",
    "optix_disk_cache_controlled_or_isolated", "paper_clear_winning_row_count",
    "paper_clear_winning_row_ids", "paper_outcome_consequence_selection",
    "preexecution_authority_file_sha256", "raw_authority_manifest_sha256",
    "raw_worker_set_sha256", "resource_admission_file_sha256",
    "resource_admission_sha256", "result_lifecycle_labels",
    "retry_resume_replacement_row_drop_relabel_used",
    "round_major_abba_is_uncontrolled_cache_mitigation_not_control", "rows",
    "runtime_file_sha256", "runtime_sha256",
    "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control",
    "same_host_root_race_excluded", "same_host_root_race_tcb_boundary",
    "same_source_target_and_optix_producer_all_workers", "schedule_sha256",
    "schema", "source_admission_policy_verified", "source_admission_sha256",
    "source_exact_path_set_verified", "source_rehash_receipt_worker_count",
    "status", "successful_cohort_empty_cache_directory_shell_count",
    "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount",
    "target_materialization_authority_file_sha256",
    "target_materialization_binding_sha256",
    "target_runtime_admission_file_sha256", "target_runtime_admission_sha256",
    "trace_cost_diagnostic_authority", "unique_execution_token_count",
    "unique_parent_pid_count", "unique_worker_cache_count", "worker_count",
}
RECOUNT_FIELDS = (
    EVALUATION_FIELDS - {"evaluation_sha256"}
) | {
    "primary_evaluation_authority_pins_verified",
    "primary_evaluation_file_sha256", "primary_evaluation_sha256",
    "raw_root_mode", "recount_sha256",
}
EXPECTED_ROW_IDS = [
    "com_dblp__cold_process_warm_system",
    "cit_patents__cold_process_warm_system",
    "soc_livejournal1__cold_process_warm_system",
    "com_dblp__prepared",
    "cit_patents__prepared",
    "soc_livejournal1__prepared",
]
EXPECTED_INTERNAL_ROW_IDS = [
    "com_dblp__cold", "cit_patents__cold", "soc_livejournal1__cold",
    "com_dblp__prepared", "cit_patents__prepared", "soc_livejournal1__prepared",
]
AUTHORIZATION_FIELDS = {
    "authorizes_worker_rerun", "authorizes_controller_retry",
    "authorizes_replacement_worker", "authorizes_row_drop",
    "authorizes_timing_reuse", "authorizes_result_relabeling",
    "authorizes_new_pod", "authorizes_new_performance_measurement",
    "authorizes_universal_fusion_claim", "authorizes_particle_causal_claim",
    "authorizes_public_release", "authorizes_submission",
}
EXPECTED_CONTROLLER_TRANSACTION = {
    "controller_transaction_success": False,
    "controller_terminal_after_all_workers_before_publication": True,
    "published_formal_root_created": False,
    "formal_worker_count": 96,
    "launch_attempt_count": 96,
    "replacement_worker_count": 0,
    "worker_retry_count": 0,
    "registered_worker_timing_count": 96,
    "analysis_successor_does_not_reclassify_controller_transaction": True,
}
EXPECTED_TERMINAL_ARCHIVE = {
    "archive_file_sha256": TERMINAL_ARCHIVE_SHA256,
    "archive_size_bytes": 92_199_259,
    "archive_regular_file_count": 962,
    "archive_directory_count": 388,
    "archive_regular_file_bytes": 1_430_937_943,
    "worker_file_count": 96,
    "worker_file_names_exact": True,
    "terminal_archive_contains_publication_outputs": False,
    "extracted_raw_matches_every_archived_regular_file": True,
    "terminal_cache_payload_file_count": 848,
    "terminal_cache_payloads_preserved_as_non_authoritative_failure_evidence": True,
}
EXPECTED_ANALYSIS_LINEAGE = {
    "executed_evaluator_sha256": (
        "b5d545762f79adc8f6844f770f55f2d87e9b7bf953ee3d5ebbf986200010f4af"
    ),
    "executed_independent_recount_sha256": (
        "43d3be5bff769728c2492c808e05a943f6473bca940a39d023f0bf9d585be60c"
    ),
    "executed_analysis_defects": [
        "invalid_materialization_nonce_equals_target_evidence_nonce_requirement",
        "plan_oracle_compared_to_generic_oracle_contract_instead_of_dataset_oracle_authority",
    ],
    "corrected_evaluator_sha256": (
        "d72026fd93d2d40c3af12cdf9db52013c816015ed8345bda50557e2e6d492a17"
    ),
    "corrected_independent_recount_sha256": (
        "560a96837c68c8b543cba74875b7d3106dac898d9e621d12d7d66b0c69a0b435"
    ),
    "corrected_regression_test_sha256": (
        "fc8a98ed0e116377bc3d721768e590e3422f57bd208c79564dc9a728a8834995"
    ),
    "worker_source_or_worker_bytes_changed": False,
    "registered_timing_value_changed": False,
    "analysis_only_successor": True,
}
EXPECTED_CLAIM_BOUNDARY = {
    "same_source_same_cohort_ablation_complete": True,
    "statistical_ci_clear_win_row_count": 2,
    "preregistered_trace_gate_eligible_clear_win_row_count": 0,
    "compiler_fusion_performance_claim_allowed": False,
    "c3_clear_end_to_end_fusion_benefit_demonstrated": False,
    "all_negative_and_uncertain_rows_retained": True,
    "paper_center_of_gravity": "C1_semantic_physical_contract",
    "cold_label": "cold_process_warm_system",
    "pure_device_kernel_timing_claimed": False,
}
ROW_FIELDS = {
    "absolute_median_seconds_difference", "bootstrap_ci_indices",
    "bootstrap_ci95", "bootstrap_draws", "bootstrap_seed", "classification",
    "dataset_display_id", "dataset_id", "demonstrated_clear_win",
    "diagnostic_may_change_row_statistic_ci_threshold_or_verdict",
    "estimand_includes_evidence_overhead", "exact_row_segment_count",
    "extra_trace_event_count_per_segment",
    "five_extra_event_differential_bound_per_segment_ns", "frozen_input_role",
    "fusion_off_seconds_median", "fusion_on_seconds_median",
    "greater_than_one_favors", "independent_comparison_row", "input_sha256_slot",
    "lifecycle", "lifecycle_internal_schedule_id", "mechanism_id",
    "mechanism_performance_statement_classification",
    "mechanism_performance_statement_eligible",
    "operation_delta_exact_all_pairs_and_segments", "oracle_authority_sha256_slot",
    "pair_count", "paired_fusion_off_over_fusion_on_ratios",
    "paired_ratio_median", "pairs", "paper_algorithm",
    "per_event_record_cost_bound_ns", "pure_device_kernel_timing_claimed",
    "row_id", "row_id_internal_schedule_id", "row_index",
    "row_total_trace_differential_bound_ns",
    "row_total_trace_differential_bound_seconds",
    "statistical_classification_unchanged_by_trace_diagnostic",
    "trace_cost_bound_small_relative_to_observed_difference",
    "trace_cost_diagnostic_authority_file_sha256",
    "trace_cost_diagnostic_authority_sha256",
    "trace_differential_fraction_of_absolute_median_seconds_difference",
    "trace_small_relative_max_fraction",
}
SELECTION_FIELDS = {
    "schema", "paper_clear_winning_row_count", "paper_clear_winning_row_ids",
    "ci_clear_win_count", "ci_clear_win_trace_cost_inconclusive_count",
    "ci_clear_win_trace_cost_inconclusive_row_ids",
    "paper_outcome_consequence_contract_sha256",
    "paper_outcome_consequence_branch", "paper_outcome_consequence",
    "selection_sha256",
}


class Goal5791TerminalAuditError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_sha(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Goal5791TerminalAuditError(f"non-object JSON: {path}")
    return value


def _seal(value: Mapping[str, object], field: str, label: str) -> str:
    unsigned = dict(value)
    claimed = unsigned.pop(field, None)
    if not isinstance(claimed, str) or claimed != _digest(unsigned):
        raise Goal5791TerminalAuditError(f"{label} seal mismatch")
    return claimed


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return float((ordered[middle - 1] + ordered[middle]) / 2.0)


def _bootstrap(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(10_000):
        draws.append(_median(rng.choices(values, k=len(values))))
    draws.sort()
    return [float(draws[249]), float(draws[9749])]


def _integer_median(values: list[int]) -> Fraction:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return Fraction(ordered[middle], 1)
    return Fraction(ordered[middle - 1] + ordered[middle], 2)


def _exact_int(value: object, expected: int) -> bool:
    return type(value) is int and value == expected


def _archive_worker_bytes(archive: Path, raw_root: Path) -> dict[str, bytes]:
    if _file_sha(archive) != TERMINAL_ARCHIVE_SHA256:
        raise Goal5791TerminalAuditError("terminal archive SHA drifted")
    workers: dict[str, bytes] = {}
    files: dict[str, tuple[str, int]] = {}
    directories: set[str] = set()
    seen: set[str] = set()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            name = member.name.removeprefix("./")
            path = PurePosixPath(name)
            parts = path.parts
            if name in seen or path.is_absolute() or ".." in parts:
                raise Goal5791TerminalAuditError("unsafe/duplicate archive member")
            seen.add(name)
            if not parts or parts[0] != TERMINAL_ROOT:
                raise Goal5791TerminalAuditError("terminal archive root drifted")
            relative = PurePosixPath(*parts[1:]).as_posix()
            if member.isdir():
                directories.add(relative)
                continue
            if not member.isfile():
                raise Goal5791TerminalAuditError("link/special terminal member")
            stream = handle.extractfile(member)
            if stream is None:
                raise Goal5791TerminalAuditError("archive member unreadable")
            data = stream.read()
            if len(data) != member.size:
                raise Goal5791TerminalAuditError("archive member size drifted")
            files[relative] = (hashlib.sha256(data).hexdigest(), len(data))
            if len(parts) == 3 and parts[0] == TERMINAL_ROOT \
                    and parts[1] == "workers" and member.isfile():
                if parts[2] in workers:
                    raise Goal5791TerminalAuditError("duplicate worker member")
                workers[parts[2]] = data
    if len(files) != 962 or len(directories) != 388 \
            or sum(size for _, size in files.values()) != 1_430_937_943:
        raise Goal5791TerminalAuditError("terminal archive inventory drifted")
    if {
        "EVALUATION.json", "INDEPENDENT_RECOUNT.json",
        "COHORT_MANIFEST.json", "RESULT.json",
    } & set(files):
        raise Goal5791TerminalAuditError("terminal archive publication drifted")
    expected = {f"worker_{index:04d}.json" for index in range(96)}
    if set(workers) != expected:
        raise Goal5791TerminalAuditError("archive worker set drifted")
    scan_root = raw_root
    if os.name == "nt" and not str(raw_root).startswith("\\\\?\\"):
        scan_root = Path("\\\\?\\" + str(raw_root.resolve()))
    extracted: dict[str, tuple[str, int]] = {}
    for path in scan_root.rglob("*"):
        if path.is_symlink():
            raise Goal5791TerminalAuditError("raw root contains symlink")
        if path.is_file():
            relative = path.relative_to(scan_root).as_posix()
            if relative == "EVALUATION.json":
                continue
            extracted[relative] = (_file_sha(path), path.stat().st_size)
    if extracted != files:
        raise Goal5791TerminalAuditError("raw extraction differs from archive")
    return workers


def audit(
    *, result_path: Path, evaluation_path: Path, recount_path: Path,
    terminal_archive: Path, raw_root: Path,
) -> dict[str, object]:
    result = _json(result_path)
    evaluation = _json(evaluation_path)
    recount = _json(recount_path)
    if set(result) != RESULT_FIELDS:
        raise Goal5791TerminalAuditError("successor result exact keys drifted")
    if set(evaluation) != EVALUATION_FIELDS:
        raise Goal5791TerminalAuditError("evaluation exact keys drifted")
    if set(recount) != RECOUNT_FIELDS:
        raise Goal5791TerminalAuditError("recount exact keys drifted")
    result_seal = _seal(result, "analysis_successor_sha256", "successor")
    evaluation_seal = _seal(evaluation, "evaluation_sha256", "evaluation")
    recount_seal = _seal(recount, "recount_sha256", "recount")
    if _file_sha(result_path) != RESULT_FILE_SHA256 \
            or result_seal != RESULT_INTERNAL_SHA256 \
            or _file_sha(evaluation_path) != EVALUATION_FILE_SHA256 \
            or evaluation_seal != EVALUATION_INTERNAL_SHA256 \
            or _file_sha(recount_path) != RECOUNT_FILE_SHA256 \
            or recount_seal != RECOUNT_INTERNAL_SHA256:
        raise Goal5791TerminalAuditError("exact analysis artifact identity drifted")
    if result.get("schema") \
            != "rtdl.goal5791.formal_terminal_analysis_successor.v1" \
            or result.get("goal") != GOAL \
            or result.get("status") \
                != ("COMPLETE__96_WORKERS__CONTROLLER_TERMINAL__"
                    "OFFLINE_PRIMARY_AND_INDEPENDENT_RECOUNT_PASS") \
            or not _exact_int(result.get("formal_worker_count"), 96) \
            or not _exact_int(result.get("independent_row_count"), 6):
        raise Goal5791TerminalAuditError("successor header drifted")
    if evaluation.get("schema") \
            != "rtdl.goal5791.formal_primary_evaluation.v1" \
            or evaluation.get("goal") != GOAL \
            or evaluation.get("status") \
                != "PASS__COMPLETE_FAIL_CLOSED_FORMAL_EVALUATION" \
            or recount.get("schema") \
                != "rtdl.goal5791.formal_independent_recount.v1" \
            or recount.get("goal") != GOAL \
            or recount.get("status") \
                != "PASS__COMPLETE_INDEPENDENT_RAW_RECOUNT" \
            or recount.get("raw_root_mode") != "analysis_stage":
        raise Goal5791TerminalAuditError("analysis header drifted")
    if result["primary_evaluation"] != {
        "file_sha256": _file_sha(evaluation_path),
        "evaluation_sha256": evaluation_seal,
        "status": evaluation.get("status"),
    }:
        raise Goal5791TerminalAuditError("evaluation cross-pin drifted")
    if result["independent_recount"] != {
        "file_sha256": _file_sha(recount_path),
        "recount_sha256": recount_seal,
        "status": recount.get("status"),
        "primary_evaluation_file_sha256": _file_sha(evaluation_path),
        "primary_evaluation_sha256": evaluation_seal,
    }:
        raise Goal5791TerminalAuditError("recount cross-pin drifted")
    for field in (
        "ci_clear_win_count", "ci_clear_loss_count", "ci_crossing_count",
        "paper_clear_winning_row_count", "paper_clear_winning_row_ids",
        "ci_clear_win_trace_cost_inconclusive_count",
        "ci_clear_win_trace_cost_inconclusive_row_ids",
    ):
        if evaluation.get(field) != result.get(field) \
                or recount.get(field) != result.get(field):
            raise Goal5791TerminalAuditError(
                f"analysis/result outcome field drifted: {field}")
    if recount.get("primary_evaluation_file_sha256") != _file_sha(evaluation_path) \
            or recount.get("primary_evaluation_sha256") != evaluation_seal \
            or recount.get("primary_evaluation_authority_pins_verified") is not True:
        raise Goal5791TerminalAuditError("recount primary binding drifted")
    common_fields = sorted(
        (set(evaluation) & set(recount))
        - {"schema", "status", "evaluation_sha256", "recount_sha256"}
    )
    if any(evaluation[field] != recount[field] for field in common_fields) \
            or result.get(
                "primary_and_independent_common_fields_exactly_equal") is not True \
            or result.get("primary_and_independent_common_field_count") \
                != len(common_fields) \
            or result.get("primary_and_independent_rows_exactly_equal") is not True:
        raise Goal5791TerminalAuditError("primary/recount common fields drifted")
    rows = result.get("rows")
    if not isinstance(rows, list) or rows != evaluation.get("rows") \
            or rows != recount.get("rows"):
        raise Goal5791TerminalAuditError("three-way row drifted")
    if [row.get("row_id") for row in rows if isinstance(row, dict)] \
            != EXPECTED_ROW_IDS:
        raise Goal5791TerminalAuditError("row order drifted")
    if not isinstance(result.get("authorization"), dict) \
            or set(result["authorization"]) != AUTHORIZATION_FIELDS \
            or any(value is not False for value in result["authorization"].values()):
        raise Goal5791TerminalAuditError("authorization widened")
    controller = result.get("controller_transaction")
    if controller != EXPECTED_CONTROLLER_TRANSACTION:
        raise Goal5791TerminalAuditError("controller terminal boundary drifted")
    if result.get("terminal_archive") != EXPECTED_TERMINAL_ARCHIVE:
        raise Goal5791TerminalAuditError("terminal archive receipt drifted")
    if result.get("analysis_source_lineage") != EXPECTED_ANALYSIS_LINEAGE:
        raise Goal5791TerminalAuditError("analysis source lineage drifted")
    if result.get("claim_boundary") != EXPECTED_CLAIM_BOUNDARY:
        raise Goal5791TerminalAuditError("claim boundary drifted")
    repository_root = Path(__file__).resolve().parents[1]
    source_checks = {
        repository_root / "scripts/goal5791_formal_evaluate.py": (
            EXPECTED_ANALYSIS_LINEAGE["corrected_evaluator_sha256"]),
        repository_root / "scripts/goal5791_formal_independent_recount.py": (
            EXPECTED_ANALYSIS_LINEAGE["corrected_independent_recount_sha256"]),
        repository_root / "tests/goal5791_formal_evaluator_recount_test.py": (
            EXPECTED_ANALYSIS_LINEAGE["corrected_regression_test_sha256"]),
        result_path.parent / "executed_analysis_sources/scripts/goal5791_formal_evaluate.py": (
            EXPECTED_ANALYSIS_LINEAGE["executed_evaluator_sha256"]),
        result_path.parent / (
            "executed_analysis_sources/scripts/"
            "goal5791_formal_independent_recount.py"
        ): EXPECTED_ANALYSIS_LINEAGE["executed_independent_recount_sha256"],
    }
    for path, expected in source_checks.items():
        if not isinstance(expected, str) or _file_sha(path) != expected:
            raise Goal5791TerminalAuditError(
                f"analysis source file cross-pin drifted: {path}")

    selection = result.get("paper_outcome_consequence_selection")
    if not isinstance(selection, dict) or set(selection) != SELECTION_FIELDS:
        raise Goal5791TerminalAuditError("paper selection malformed")
    selection_unsigned = dict(selection)
    selection_seal = selection_unsigned.pop("selection_sha256", None)
    if selection_seal != _digest(selection_unsigned) \
            or selection.get("schema") \
                != "rtdl.goal5791.paper_outcome_consequence_selection.v1" \
            or selection.get("paper_outcome_consequence_contract_sha256") \
                != "8c9119f854f603ef9ac2898b0c92f2510b171d968c86eaf9a7f19fb34e3c518c" \
            or selection != evaluation.get("paper_outcome_consequence_selection") \
            or selection != recount.get("paper_outcome_consequence_selection") \
            or not _exact_int(selection.get("paper_clear_winning_row_count"), 0) \
            or selection.get("paper_clear_winning_row_ids") != [] \
            or not _exact_int(selection.get("ci_clear_win_count"), 2) \
            or not _exact_int(
                selection.get("ci_clear_win_trace_cost_inconclusive_count"), 2) \
            or selection.get("ci_clear_win_trace_cost_inconclusive_row_ids") != [
                "cit_patents__cold_process_warm_system",
                "soc_livejournal1__prepared",
            ] \
            or selection.get("paper_outcome_consequence_branch") \
                != "zero_clear_winning_rows" \
            or selection.get("paper_outcome_consequence") != {
                "all_negative_and_uncertain_rows_retained": True,
                "c3_disposition": (
                    "preregistered_same_source_same_cohort_measurement_found_"
                    "no_clear_end_to_end_fusion_benefit"
                ),
                "compiler_fusion_performance_claim_allowed": False,
                "paper_center_of_gravity": "C1_semantic_physical_contract",
                "submission_decision_deferred_until_complete_evidence_review": True,
            }:
        raise Goal5791TerminalAuditError("paper outcome selection drifted")

    schedule = _json(raw_root / "SCHEDULE.json")
    runtime = _json(raw_root / "RUNTIME.json")
    preexecution = _json(raw_root / "PREEXECUTION_AUTHORITY.json")
    target_binding = _json(raw_root / "TARGET_BINDING.json")
    formal_authority = _json(raw_root / "OWNER_FORMAL_AUTHORITY.json")
    data_admission = _json(raw_root / "DATA_ADMISSION.json")
    authority_manifest = _json(raw_root / "AUTHORITY_MANIFEST.json")
    source_admission = _json(raw_root / "SOURCE_ADMISSION.json")
    target_runtime = _json(raw_root / "TARGET_RUNTIME_ADMISSION.json")
    resource_admission = _json(raw_root / "RESOURCE_ADMISSION.json")
    raw_cross_pins = {
        "schedule_sha256": _digest(schedule),
        "preexecution_authority_file_sha256": _file_sha(
            raw_root / "PREEXECUTION_AUTHORITY.json"),
        "target_materialization_binding_sha256": _seal(
            target_binding, "binding_sha256", "target binding"),
        "target_materialization_authority_file_sha256": _file_sha(
            raw_root / "TARGET_MATERIALIZATION_AUTHORITY.json"),
        "formal_authority_file_sha256": _file_sha(
            raw_root / "OWNER_FORMAL_AUTHORITY.json"),
        "runtime_sha256": _seal(runtime, "runtime_sha256", "runtime"),
        "runtime_file_sha256": _file_sha(raw_root / "RUNTIME.json"),
        "data_admission_sha256": _seal(
            data_admission, "admission_sha256", "data admission"),
        "raw_authority_manifest_sha256": _seal(
            authority_manifest, "manifest_sha256", "authority manifest"),
        "source_admission_sha256": _seal(
            source_admission, "admission_sha256", "source admission"),
        "target_runtime_admission_sha256": _seal(
            target_runtime, "admission_sha256", "target runtime admission"),
        "target_runtime_admission_file_sha256": _file_sha(
            raw_root / "TARGET_RUNTIME_ADMISSION.json"),
        "resource_admission_sha256": _seal(
            resource_admission, "admission_sha256", "resource admission"),
        "resource_admission_file_sha256": _file_sha(
            raw_root / "RESOURCE_ADMISSION.json"),
    }
    _seal(preexecution, "authority_sha256", "preexecution authority")
    _seal(formal_authority, "authority_sha256", "formal authority")
    for field, expected in raw_cross_pins.items():
        if evaluation.get(field) != expected or recount.get(field) != expected:
            raise Goal5791TerminalAuditError(
                f"raw authority cross-pin drifted: {field}")
    for field in (
        "formal_contract_sha256", "schedule_sha256", "runtime_file_sha256",
        "runtime_sha256", "raw_worker_set_sha256",
    ):
        if result.get(field) != evaluation.get(field):
            raise Goal5791TerminalAuditError(
                f"successor/evaluation identity drifted: {field}")

    archived_workers = _archive_worker_bytes(terminal_archive, raw_root)
    workers: list[dict[str, object]] = []
    seen_pids: set[int] = set()
    worker_seals: list[str] = []
    for index in range(96):
        name = f"worker_{index:04d}.json"
        raw_path = raw_root / "workers" / name
        raw_bytes = raw_path.read_bytes()
        if raw_bytes != archived_workers[name]:
            raise Goal5791TerminalAuditError("raw worker differs from archive")
        worker = json.loads(raw_bytes)
        if not isinstance(worker, dict):
            raise Goal5791TerminalAuditError("worker root malformed")
        seal = _seal(worker, "worker_sha256", f"worker {index}")
        pid = worker.get("parent_pid")
        if not _exact_int(worker.get("worker_index"), index) \
                or worker.get("status") != "COMPLETE" \
                or worker.get("formal_worker") is not True \
                or worker.get("retry_resume_replacement_row_drop_relabel_used") is not False \
                or type(worker.get("output_scalar_u64")) is not int \
                or type(worker.get("oracle_output_scalar_u64")) is not int \
                or worker.get("output_scalar_u64") != worker.get("oracle_output_scalar_u64") \
                or type(pid) is not int or pid in seen_pids:
            raise Goal5791TerminalAuditError(f"worker identity/result drifted: {index}")
        seen_pids.add(pid)
        worker_seals.append(seal)
        workers.append(worker)
    if _digest(worker_seals) != result.get("raw_worker_set_sha256"):
        raise Goal5791TerminalAuditError("raw worker set seal drifted")

    for row_index, (internal_row_id, published) in enumerate(
        zip(EXPECTED_INTERNAL_ROW_IDS, rows, strict=True)
    ):
        if not isinstance(published, dict) or set(published) != ROW_FIELDS:
            raise Goal5791TerminalAuditError("published row malformed")
        selected = [worker for worker in workers if worker["row_index"] == row_index]
        if len(selected) != 16 or {worker["row_id"] for worker in selected} \
                != {internal_row_id}:
            raise Goal5791TerminalAuditError("worker row membership drifted")
        ratios: list[float] = []
        off_seconds: list[float] = []
        on_seconds: list[float] = []
        expected_pairs: list[dict[str, object]] = []
        for pair_index in range(8):
            pair = [worker for worker in selected if worker["pair_index"] == pair_index]
            off = [worker for worker in pair if worker["variant"] == "fusion_off"]
            on = [worker for worker in pair if worker["variant"] == "fusion_on"]
            if len(off) != 1 or len(on) != 1:
                raise Goal5791TerminalAuditError("pair membership drifted")
            off_value = float(off[0]["registered_complete_endpoint_seconds"])
            on_value = float(on[0]["registered_complete_endpoint_seconds"])
            ratio = off_value / on_value
            ratios.append(ratio)
            off_seconds.append(off_value)
            on_seconds.append(on_value)
            expected_pairs.append({
                "pair_index": pair_index,
                "fusion_off_worker_index": off[0]["worker_index"],
                "fusion_on_worker_index": on[0]["worker_index"],
                "fusion_off_seconds": off_value,
                "fusion_on_seconds": on_value,
                "fusion_off_over_fusion_on": ratio,
                "operation_delta_exact_7_vs_2_per_segment": True,
            })
        segment_counts = {worker.get("segment_count") for worker in selected}
        if len(segment_counts) != 1:
            raise Goal5791TerminalAuditError("row segment count drifted")
        segment_count = next(iter(segment_counts))
        if type(segment_count) is not int or segment_count <= 0:
            raise Goal5791TerminalAuditError("row segment count malformed")
        off_ns = [int(round(value * 1_000_000_000)) for value in off_seconds]
        on_ns = [int(round(value * 1_000_000_000)) for value in on_seconds]
        absolute_difference_ns = abs(_integer_median(off_ns) - _integer_median(on_ns))
        bound_ns = 61_010 * segment_count
        trace_fraction = (
            float(Fraction(bound_ns, 1) / absolute_difference_ns)
            if absolute_difference_ns > 0 else None
        )
        ci = _bootstrap(ratios, 57_900_000 + row_index)
        classification = (
            "ci_clear_win" if ci[0] > 1.0
            else "ci_clear_loss" if ci[1] < 1.0
            else "ci_crosses_one__not_a_demonstrated_win"
        )
        trace_small = trace_fraction is not None and trace_fraction <= 0.01
        eligible = classification == "ci_clear_win" and trace_small
        claim_classification = (
            "eligible_clear_win" if eligible
            else "trace_cost_inconclusive"
            if classification == "ci_clear_win" else "not_a_statistical_clear_win"
        )
        dataset_id = str(selected[0]["dataset_id"])
        lifecycle_internal = str(selected[0]["lifecycle"])
        display_ids = {
            "com_dblp": "com-dblp",
            "cit_patents": "cit-Patents",
            "soc_livejournal1": "soc-LiveJournal1",
        }
        frozen_roles = {
            "com_dblp": "small_graph_control",
            "cit_patents": "medium_graph",
            "soc_livejournal1": "large_graph",
        }
        lifecycle_label = (
            "cold_process_warm_system"
            if lifecycle_internal == "cold" else "prepared"
        )
        if ratios != published.get("paired_fusion_off_over_fusion_on_ratios") \
                or _median(ratios) != published.get("paired_ratio_median") \
                or ci != published.get("bootstrap_ci95") \
                or expected_pairs != published.get("pairs") \
                or _median(off_seconds) != published.get("fusion_off_seconds_median") \
                or _median(on_seconds) != published.get("fusion_on_seconds_median") \
                or float(absolute_difference_ns / 1_000_000_000) \
                    != published.get("absolute_median_seconds_difference") \
                or not _exact_int(
                    published.get("exact_row_segment_count"), segment_count) \
                or not _exact_int(
                    published.get("row_total_trace_differential_bound_ns"), bound_ns) \
                or published.get("row_total_trace_differential_bound_seconds") \
                    != bound_ns / 1_000_000_000.0 \
                or published.get(
                    "trace_differential_fraction_of_absolute_median_seconds_difference"
                ) != trace_fraction \
                or published.get("classification") != classification \
                or published.get(
                    "trace_cost_bound_small_relative_to_observed_difference"
                ) is not trace_small \
                or published.get("demonstrated_clear_win") is not eligible \
                or published.get(
                    "mechanism_performance_statement_eligible") is not eligible \
                or published.get(
                    "mechanism_performance_statement_classification"
                ) != claim_classification \
                or not _exact_int(published.get("row_index"), row_index) \
                or published.get("row_id_internal_schedule_id") != internal_row_id \
                or published.get("row_id") != EXPECTED_ROW_IDS[row_index] \
                or published.get("dataset_id") != dataset_id \
                or published.get("dataset_display_id") != display_ids[dataset_id] \
                or published.get("frozen_input_role") != frozen_roles[dataset_id] \
                or published.get("lifecycle_internal_schedule_id") \
                    != lifecycle_internal \
                or published.get("lifecycle") != lifecycle_label \
                or published.get("paper_algorithm") != selected[0]["paper_algorithm"] \
                or published.get("mechanism_id") != selected[0]["mechanism_id"] \
                or published.get("input_sha256_slot") \
                    != f"dataset_input_sha256.{dataset_id}" \
                or published.get("oracle_authority_sha256_slot") \
                    != f"oracle_authority_sha256.{dataset_id}" \
                or published.get("greater_than_one_favors") != "fusion_on" \
                or published.get("independent_comparison_row") is not True \
                or not _exact_int(published.get("pair_count"), 8) \
                or not _exact_int(published.get("bootstrap_draws"), 10_000) \
                or not _exact_int(
                    published.get("bootstrap_seed"), 57_900_000 + row_index) \
                or published.get("bootstrap_ci_indices") != [249, 9749] \
                or not _exact_int(
                    published.get("extra_trace_event_count_per_segment"), 5) \
                or not _exact_int(published.get(
                    "five_extra_event_differential_bound_per_segment_ns"), 61_010) \
                or not _exact_int(
                    published.get("per_event_record_cost_bound_ns"), 12_202) \
                or published.get("trace_cost_diagnostic_authority_file_sha256") \
                    != "8a5d5924b54e0746a1ff83fa92d94c5977764b1b49fde8ac06790365f25436a2" \
                or published.get("trace_cost_diagnostic_authority_sha256") \
                    != "f4dd262c6ae7338db39aaf307176b5673baa956fc18f202551cb8115467ad364" \
                or published.get("trace_small_relative_max_fraction") != 0.01 \
                or published.get("estimand_includes_evidence_overhead") is not True \
                or published.get("pure_device_kernel_timing_claimed") is not False \
                or published.get(
                    "diagnostic_may_change_row_statistic_ci_threshold_or_verdict"
                ) is not False \
                or published.get(
                    "statistical_classification_unchanged_by_trace_diagnostic"
                ) is not True \
                or published.get(
                    "operation_delta_exact_all_pairs_and_segments") is not True:
            raise Goal5791TerminalAuditError(
                f"independent row statistic mismatch: {internal_row_id}")

    if not _exact_int(result.get("ci_clear_win_count"), 2) \
            or not _exact_int(result.get("ci_clear_loss_count"), 0) \
            or not _exact_int(result.get("ci_crossing_count"), 4) \
            or not _exact_int(result.get("paper_clear_winning_row_count"), 0) \
            or result.get("paper_clear_winning_row_ids") != [] \
            or not _exact_int(
                result.get("ci_clear_win_trace_cost_inconclusive_count"), 2) \
            or result.get("paper_outcome_consequence_selection", {}).get(
                "paper_outcome_consequence_branch") != "zero_clear_winning_rows" \
            or result.get("claim_boundary", {}).get(
                "compiler_fusion_performance_claim_allowed") is not False \
            or result.get("claim_boundary", {}).get(
                "c3_clear_end_to_end_fusion_benefit_demonstrated") is not False:
        raise Goal5791TerminalAuditError("outcome/claim boundary drifted")

    payload: dict[str, object] = {
        "schema": "rtdl.goal5791.formal_terminal_analysis_successor_audit.v3",
        "goal": GOAL,
        "status": (
            "PASS__INDEPENDENT_EXACT_SCHEMA_FULL_TERMINAL_ARCHIVE_"
            "AND_RAW_STATISTICS_AUDIT"
        ),
        "result_file_sha256": _file_sha(result_path),
        "analysis_successor_sha256": result_seal,
        "evaluation_file_sha256": _file_sha(evaluation_path),
        "evaluation_sha256": evaluation_seal,
        "recount_file_sha256": _file_sha(recount_path),
        "recount_sha256": recount_seal,
        "terminal_archive_file_sha256": _file_sha(terminal_archive),
        "worker_file_count": 96,
        "unique_parent_pid_count": len(seen_pids),
        "worker_seals_rebuilt": True,
        "raw_worker_set_sha256_rebuilt": result["raw_worker_set_sha256"],
        "paired_ratios_medians_and_bootstrap_ci_rebuilt": True,
        "three_way_rows_exactly_equal": True,
        "controller_terminal_boundary_preserved": True,
        "paper_clear_winning_row_count": 0,
        "paper_outcome_consequence_branch": "zero_clear_winning_rows",
        "external_review_claimed": False,
        "authorization_granted": False,
    }
    payload["audit_sha256"] = _digest(payload)
    return payload


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
            + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--recount", type=Path, required=True)
    parser.add_argument("--terminal-archive", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _write(args.output, audit(
        result_path=args.result.resolve(),
        evaluation_path=args.evaluation.resolve(),
        recount_path=args.recount.resolve(),
        terminal_archive=args.terminal_archive.resolve(),
        raw_root=args.raw_root.resolve(),
    ))
    print(args.output.resolve())


if __name__ == "__main__":
    main()
