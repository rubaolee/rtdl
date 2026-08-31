"""Build the create-only Goal5791 terminal-transaction analysis successor.

This script never runs a formal worker and never mutates the preserved terminal
archive.  It proves that an extracted raw root is byte-for-byte derived from
that archive, validates the corrected primary evaluation and separately
implemented recount, and emits one sealed result that keeps controller-transaction
failure distinct from scientific-analysis completion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
from typing import Mapping


GOAL = 5791
SCHEMA = "rtdl.goal5791.formal_terminal_analysis_successor.v1"
STATUS = (
    "COMPLETE__96_WORKERS__CONTROLLER_TERMINAL__"
    "OFFLINE_PRIMARY_AND_INDEPENDENT_RECOUNT_PASS"
)
TERMINAL_ARCHIVE_SHA256 = (
    "53845c836bd5e0048ec9b997ab9f4732eb121ec9c1d116ed5486f02be77f0252"
)
TERMINAL_ARCHIVE_SIZE_BYTES = 92_199_259
TERMINAL_ROOT_NAME = ".goal5791_formal_output_v4_20260821.goal5791_incomplete"
EXECUTED_EVALUATOR_SHA256 = (
    "b5d545762f79adc8f6844f770f55f2d87e9b7bf953ee3d5ebbf986200010f4af"
)
EXECUTED_RECOUNT_SHA256 = (
    "43d3be5bff769728c2492c808e05a943f6473bca940a39d023f0bf9d585be60c"
)
CORRECTED_EVALUATOR_SHA256 = (
    "d72026fd93d2d40c3af12cdf9db52013c816015ed8345bda50557e2e6d492a17"
)
CORRECTED_RECOUNT_SHA256 = (
    "560a96837c68c8b543cba74875b7d3106dac898d9e621d12d7d66b0c69a0b435"
)
CORRECTED_TEST_SHA256 = (
    "fc8a98ed0e116377bc3d721768e590e3422f57bd208c79564dc9a728a8834995"
)
EVALUATION_FILE_SHA256 = (
    "69e56a6220d9495d40a74e0ca98b4fc7d1fd58ca049b8f910cb2a0eea970b819"
)
RECOUNT_FILE_SHA256 = (
    "d50d7ae765b2da96db97d8db6592c4eb856e53822c9fd8851f32d114a30ace38"
)
EXPECTED_ROW_IDS = [
    "com_dblp__cold_process_warm_system",
    "cit_patents__cold_process_warm_system",
    "soc_livejournal1__cold_process_warm_system",
    "com_dblp__prepared",
    "cit_patents__prepared",
    "soc_livejournal1__prepared",
]
EXPECTED_TRACE_INCONCLUSIVE_IDS = [
    "cit_patents__cold_process_warm_system",
    "soc_livejournal1__prepared",
]
AUTHORIZATION_FIELDS = (
    "authorizes_worker_rerun",
    "authorizes_controller_retry",
    "authorizes_replacement_worker",
    "authorizes_row_drop",
    "authorizes_timing_reuse",
    "authorizes_result_relabeling",
    "authorizes_new_pod",
    "authorizes_new_performance_measurement",
    "authorizes_universal_fusion_claim",
    "authorizes_particle_causal_claim",
    "authorizes_public_release",
    "authorizes_submission",
)


class Goal5791TerminalAnalysisError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return _sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8"))


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Goal5791TerminalAnalysisError(f"JSON root is not object: {path}")
    return value


def _validate_seal(value: Mapping[str, object], field: str, label: str) -> str:
    unsigned = dict(value)
    claimed = unsigned.pop(field, None)
    if not isinstance(claimed, str) or claimed != _digest(unsigned):
        raise Goal5791TerminalAnalysisError(f"{label} seal mismatch")
    return claimed


def _validate_terminal_archive(archive: Path, raw_root: Path) -> dict[str, object]:
    if _file_sha256(archive) != TERMINAL_ARCHIVE_SHA256 \
            or archive.stat().st_size != TERMINAL_ARCHIVE_SIZE_BYTES:
        raise Goal5791TerminalAnalysisError("terminal archive identity drifted")
    if raw_root.name != TERMINAL_ROOT_NAME or not raw_root.is_dir():
        raise Goal5791TerminalAnalysisError("terminal raw root identity drifted")

    archived_files: dict[str, tuple[str, int]] = {}
    directories: set[str] = set()
    seen: set[str] = set()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            name = member.name.removeprefix("./")
            path = PurePosixPath(name)
            if name in seen or path.is_absolute() or ".." in path.parts:
                raise Goal5791TerminalAnalysisError("unsafe/duplicate archive member")
            seen.add(name)
            if not path.parts or path.parts[0] != TERMINAL_ROOT_NAME:
                raise Goal5791TerminalAnalysisError("terminal archive root drifted")
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if member.isdir():
                directories.add(relative)
                continue
            if not member.isfile():
                raise Goal5791TerminalAnalysisError("link/special terminal member")
            stream = handle.extractfile(member)
            if stream is None:
                raise Goal5791TerminalAnalysisError("terminal member unreadable")
            data = stream.read()
            if len(data) != member.size:
                raise Goal5791TerminalAnalysisError("terminal member size drifted")
            archived_files[relative] = (_sha256(data), len(data))

    forbidden_publication = {
        "EVALUATION.json", "INDEPENDENT_RECOUNT.json",
        "COHORT_MANIFEST.json", "RESULT.json",
    }
    if forbidden_publication & set(archived_files):
        raise Goal5791TerminalAnalysisError(
            "terminal archive unexpectedly contains publication outputs")
    expected_workers = {
        f"workers/worker_{index:04d}.json" for index in range(96)
    }
    actual_workers = {
        name for name in archived_files if name.startswith("workers/")
    }
    if actual_workers != expected_workers:
        raise Goal5791TerminalAnalysisError("terminal worker set drifted")

    actual_files: dict[str, tuple[str, int]] = {}
    scan_root = raw_root
    if os.name == "nt" and not str(raw_root).startswith("\\\\?\\"):
        scan_root = Path("\\\\?\\" + str(raw_root))
    for path in scan_root.rglob("*"):
        if path.is_symlink():
            raise Goal5791TerminalAnalysisError("raw root contains symlink")
        if path.is_file():
            relative = path.relative_to(scan_root).as_posix()
            if relative == "EVALUATION.json":
                continue
            actual_files[relative] = (_file_sha256(path), path.stat().st_size)
    if actual_files != archived_files:
        raise Goal5791TerminalAnalysisError(
            "extracted raw root is not byte-exact terminal archive content")
    cache_payload_files = sorted(
        name for name in archived_files
        if name.startswith("worker_caches/") and not name.endswith("/")
    )
    return {
        "archive_file_sha256": TERMINAL_ARCHIVE_SHA256,
        "archive_size_bytes": TERMINAL_ARCHIVE_SIZE_BYTES,
        "archive_regular_file_count": len(archived_files),
        "archive_directory_count": len(directories),
        "archive_regular_file_bytes": sum(size for _, size in archived_files.values()),
        "worker_file_count": len(expected_workers),
        "worker_file_names_exact": True,
        "terminal_archive_contains_publication_outputs": False,
        "extracted_raw_matches_every_archived_regular_file": True,
        "terminal_cache_payload_file_count": len(cache_payload_files),
        "terminal_cache_payloads_preserved_as_non_authoritative_failure_evidence": True,
    }


def build_result(
    *, repository_root: Path, terminal_archive: Path, raw_root: Path,
    recount_path: Path,
) -> dict[str, object]:
    root = repository_root.resolve()
    terminal_archive = terminal_archive.resolve()
    raw_root = raw_root.resolve()
    recount_path = recount_path.resolve()
    archive_audit = _validate_terminal_archive(terminal_archive, raw_root)

    corrected_paths = {
        "evaluator": root / "scripts/goal5791_formal_evaluate.py",
        "recount": root / "scripts/goal5791_formal_independent_recount.py",
        "regression_test": root / "tests/goal5791_formal_evaluator_recount_test.py",
    }
    expected_corrected = {
        "evaluator": CORRECTED_EVALUATOR_SHA256,
        "recount": CORRECTED_RECOUNT_SHA256,
        "regression_test": CORRECTED_TEST_SHA256,
    }
    for role, path in corrected_paths.items():
        if _file_sha256(path) != expected_corrected[role]:
            raise Goal5791TerminalAnalysisError(
                f"corrected analysis source drifted: {role}")

    runtime = _load_json(raw_root / "RUNTIME.json")
    formal_sources = runtime.get("formal_identity_record", {}).get(
        "formal_sources", {})
    if not isinstance(formal_sources, dict) \
            or formal_sources.get("scripts/goal5791_formal_evaluate.py") \
                != EXECUTED_EVALUATOR_SHA256 \
            or formal_sources.get(
                "scripts/goal5791_formal_independent_recount.py") \
                != EXECUTED_RECOUNT_SHA256:
        raise Goal5791TerminalAnalysisError("executed analysis source pins drifted")

    evaluation_path = raw_root / "EVALUATION.json"
    if _file_sha256(evaluation_path) != EVALUATION_FILE_SHA256 \
            or _file_sha256(recount_path) != RECOUNT_FILE_SHA256:
        raise Goal5791TerminalAnalysisError("analysis output file identity drifted")
    evaluation = _load_json(evaluation_path)
    recount = _load_json(recount_path)
    evaluation_seal = _validate_seal(
        evaluation, "evaluation_sha256", "primary evaluation")
    recount_seal = _validate_seal(recount, "recount_sha256", "independent recount")
    if evaluation.get("schema") != "rtdl.goal5791.formal_primary_evaluation.v1" \
            or evaluation.get("status") \
                != "PASS__COMPLETE_FAIL_CLOSED_FORMAL_EVALUATION" \
            or recount.get("schema") \
                != "rtdl.goal5791.formal_independent_recount.v1" \
            or recount.get("status") \
                != "PASS__COMPLETE_INDEPENDENT_RAW_RECOUNT" \
            or recount.get("raw_root_mode") != "analysis_stage" \
            or recount.get("primary_evaluation_file_sha256") \
                != EVALUATION_FILE_SHA256 \
            or recount.get("primary_evaluation_sha256") != evaluation_seal \
            or recount.get("primary_evaluation_authority_pins_verified") is not True:
        raise Goal5791TerminalAnalysisError("analysis status/cross-pin drifted")

    excluded_common = {
        "schema", "status", "evaluation_sha256", "recount_sha256",
    }
    common_fields = sorted(
        (set(evaluation) & set(recount)) - excluded_common
    )
    mismatches = [
        field for field in common_fields
        if evaluation[field] != recount[field]
    ]
    if mismatches:
        raise Goal5791TerminalAnalysisError(
            f"primary/recount common field drift: {mismatches}")

    rows = evaluation.get("rows")
    selection = evaluation.get("paper_outcome_consequence_selection")
    if not isinstance(rows, list) or not isinstance(selection, dict):
        raise Goal5791TerminalAnalysisError("analysis rows/selection malformed")
    if [row.get("row_id") for row in rows if isinstance(row, dict)] \
            != EXPECTED_ROW_IDS:
        raise Goal5791TerminalAnalysisError("analysis row identity/order drifted")
    if any(
        not isinstance(row, dict)
        or row.get("operation_delta_exact_all_pairs_and_segments") is not True
        for row in rows
    ):
        raise Goal5791TerminalAnalysisError("operation delta proof drifted")
    if evaluation.get("worker_count") != 96 \
            or evaluation.get("unique_parent_pid_count") != 96 \
            or evaluation.get("exact_output_worker_count") != 96 \
            or evaluation.get("behavioral_true_optix_worker_count") != 96 \
            or evaluation.get("retry_resume_replacement_row_drop_relabel_used") is not False \
            or evaluation.get("ci_clear_win_count") != 2 \
            or evaluation.get("ci_clear_loss_count") != 0 \
            or evaluation.get("ci_crossing_count") != 4 \
            or evaluation.get("paper_clear_winning_row_count") != 0 \
            or evaluation.get("paper_clear_winning_row_ids") != [] \
            or evaluation.get("ci_clear_win_trace_cost_inconclusive_count") != 2 \
            or evaluation.get("ci_clear_win_trace_cost_inconclusive_row_ids") \
                != EXPECTED_TRACE_INCONCLUSIVE_IDS \
            or selection.get("paper_outcome_consequence_branch") \
                != "zero_clear_winning_rows" \
            or selection.get("selection_sha256") \
                != _digest({
                    key: value for key, value in selection.items()
                    if key != "selection_sha256"
                }):
        raise Goal5791TerminalAnalysisError("formal scientific outcome drifted")

    authorizations = {field: False for field in AUTHORIZATION_FIELDS}
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "goal": GOAL,
        "status": STATUS,
        "controller_transaction": {
            "controller_transaction_success": False,
            "controller_terminal_after_all_workers_before_publication": True,
            "published_formal_root_created": False,
            "formal_worker_count": 96,
            "launch_attempt_count": 96,
            "replacement_worker_count": 0,
            "worker_retry_count": 0,
            "registered_worker_timing_count": 96,
            "analysis_successor_does_not_reclassify_controller_transaction": True,
        },
        "terminal_archive": archive_audit,
        "analysis_source_lineage": {
            "executed_evaluator_sha256": EXECUTED_EVALUATOR_SHA256,
            "executed_independent_recount_sha256": EXECUTED_RECOUNT_SHA256,
            "executed_analysis_defects": [
                "invalid_materialization_nonce_equals_target_evidence_nonce_requirement",
                "plan_oracle_compared_to_generic_oracle_contract_instead_of_dataset_oracle_authority",
            ],
            "corrected_evaluator_sha256": CORRECTED_EVALUATOR_SHA256,
            "corrected_independent_recount_sha256": CORRECTED_RECOUNT_SHA256,
            "corrected_regression_test_sha256": CORRECTED_TEST_SHA256,
            "worker_source_or_worker_bytes_changed": False,
            "registered_timing_value_changed": False,
            "analysis_only_successor": True,
        },
        "primary_evaluation": {
            "file_sha256": EVALUATION_FILE_SHA256,
            "evaluation_sha256": evaluation_seal,
            "status": evaluation["status"],
        },
        "independent_recount": {
            "file_sha256": RECOUNT_FILE_SHA256,
            "recount_sha256": recount_seal,
            "status": recount["status"],
            "primary_evaluation_file_sha256": EVALUATION_FILE_SHA256,
            "primary_evaluation_sha256": evaluation_seal,
        },
        "primary_and_independent_common_fields_exactly_equal": True,
        "primary_and_independent_common_field_count": len(common_fields),
        "primary_and_independent_rows_exactly_equal": True,
        "formal_contract_sha256": evaluation["formal_contract_sha256"],
        "schedule_sha256": evaluation["schedule_sha256"],
        "runtime_file_sha256": evaluation["runtime_file_sha256"],
        "runtime_sha256": evaluation["runtime_sha256"],
        "raw_worker_set_sha256": evaluation["raw_worker_set_sha256"],
        "formal_worker_count": 96,
        "independent_row_count": 6,
        "ci_clear_win_count": 2,
        "ci_clear_loss_count": 0,
        "ci_crossing_count": 4,
        "paper_clear_winning_row_count": 0,
        "paper_clear_winning_row_ids": [],
        "ci_clear_win_trace_cost_inconclusive_count": 2,
        "ci_clear_win_trace_cost_inconclusive_row_ids": (
            EXPECTED_TRACE_INCONCLUSIVE_IDS
        ),
        "paper_outcome_consequence_selection": selection,
        "rows": rows,
        "claim_boundary": {
            "same_source_same_cohort_ablation_complete": True,
            "statistical_ci_clear_win_row_count": 2,
            "preregistered_trace_gate_eligible_clear_win_row_count": 0,
            "compiler_fusion_performance_claim_allowed": False,
            "c3_clear_end_to_end_fusion_benefit_demonstrated": False,
            "all_negative_and_uncertain_rows_retained": True,
            "paper_center_of_gravity": "C1_semantic_physical_contract",
            "cold_label": "cold_process_warm_system",
            "pure_device_kernel_timing_claimed": False,
        },
        "authorization": authorizations,
    }
    payload["analysis_successor_sha256"] = _digest(payload)
    return payload


def _write_create_only(path: Path, value: object) -> None:
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
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--terminal-archive", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--recount", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result(
        repository_root=args.repository_root,
        terminal_archive=args.terminal_archive,
        raw_root=args.raw_root,
        recount_path=args.recount,
    )
    _write_create_only(args.output, result)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
