#!/usr/bin/env python3
"""Independently verify Goal5830 from preserved JSON/source/PTX bytes.

The verifier imports neither RTDL nor PyOptiX.  It reconstructs the sorting
relation and final stable order from raw records, checks the exact CP002 wrong
relation, and rehashes every executable/source identity used by the two runs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


EXPECTED_NATIVE_SHA256 = (
    "961d7c7526c4efcbdea2a4a63c67c8198fc49f35a3b64f5b86011bd1c666b176"
)
EXPECTED_RUNTIME_SOURCE_SHA256 = (
    "2be5b845c56176415f688f73e53c7c152cb2291a939d58d27a4489f4d88d00df"
)
EXPECTED_MAIN_ROWS = (
    (0, 0), (0, 1), (0, 3),
    (1, 1), (1, 3),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 3),
)
EXPECTED_CP002_ROWS = (
    (0, 1), (0, 2), (0, 3),
    (1, 2), (1, 3),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 2),
)
VALID_EXPRESSION = "optixReportIntersection(0.0f, 0u, item.item_id);"
CP002_EXPRESSION = "optixReportIntersection(0.0f, 0u, primitive_index);"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), f"{path}: root must be an object")
    return value


def pairs(value) -> tuple[tuple[int, int], ...]:
    return tuple((int(row[0]), int(row[1])) for row in value)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def verify_rtdl(repo: Path, evidence: Path) -> dict[str, object]:
    root = evidence / "rtdl"
    result_path = root / "GOAL5830_GPU_RESULT_V4.json"
    stdout_path = root / "GOAL5830_GPU_STDOUT_V4.json"
    require(result_path.read_bytes() == stdout_path.read_bytes(),
            "RTDL result/stdout bytes differ")
    result = load(result_path)
    require(result["schema"] == "rtdl.goal5830.public_stable_sort_gpu_functional.v2",
            "RTDL schema drift")
    require(result["status"] == "PASS", "RTDL result did not pass")
    require(result["case_count"] == 21 and len(result["cases"]) == 21,
            "RTDL case count mismatch")
    require(result["expected_rows_passed_into_execution"] is False,
            "application oracle entered RTDL execution")
    require(result["registered_performance_timing_count"] == 0,
            "unexpected RTDL timing")
    require(result["performance_claimed"] is False,
            "unexpected RTDL performance claim")
    require(result["sorting_algorithm_proved"] is False,
            "sorting theorem overclaim")
    require(result["arbitrary_sorting_supported"] is False,
            "arbitrary sorting overclaim")
    require(result["application_mapping_verified_by_rtdl"] is False,
            "application mapping overclaim")

    case_ids = []
    for case in result["cases"]:
        case_id = str(case["case_id"])
        case_ids.append(case_id)
        records = pairs(case["input_records"])
        require(tuple(item_id for _value, item_id in records)
                == tuple(range(len(records))), f"{case_id}: item ids drift")
        values = tuple(value for value, _item_id in records)
        expected_rows = tuple(
            (source_id, predecessor_id)
            for source_id in range(len(values))
            for predecessor_id in range(len(values))
            if (values[predecessor_id], predecessor_id)
            <= (values[source_id], source_id)
        )
        require(pairs(case["relation_rows"]) == expected_rows,
                f"{case_id}: raw relation mismatch")
        expected_records = tuple(sorted(
            ((value, item_id) for item_id, value in enumerate(values)),
            key=lambda record: (record[0], record[1]),
        ))
        expected_ranks = tuple(
            expected_records.index((value, item_id))
            for item_id, value in enumerate(values)
        )
        require(tuple(case["ranks_by_item_id"]) == expected_ranks,
                f"{case_id}: rank mismatch")
        require(pairs(case["sorted_records"]) == expected_records,
                f"{case_id}: stable order mismatch")
        require(pairs(case["python_stable_oracle"]) == expected_records,
                f"{case_id}: stored oracle mismatch")
        require(case["physical_executor_classification"]
                == "optix_traversal_observed",
                f"{case_id}: OptiX traversal not observed")
        require(case["lifecycle"]["protocol_contract_verdict"] == "ACCEPT",
                f"{case_id}: protocol contract did not accept")
        require(case["executable_identity_sha256"]
                == case["lifecycle"]["executable_identity_sha256"],
                f"{case_id}: result/lifecycle executable identity mismatch")
        require(all(len(str(case[key])) == 64 for key in (
            "program_identity_sha256", "executable_identity_sha256")),
            f"{case_id}: identity digest shape drift")
        require(case["expected_rows_passed_into_execution"] is False,
                f"{case_id}: oracle leakage")

    expected_case_ids = [
        "MAIN_DUPLICATE_DERANGED",
        "MAIN_SECOND_PHYSICAL_ORDER",
        "SIGNED_DUPLICATE",
        "SINGLETON",
        "MAXIMUM_EXACT_BINARY32_QUARTER_GRID",
        *(f"FROZEN_RANDOM_{seed:02d}" for seed in range(16)),
    ]
    require(case_ids == expected_case_ids and len(set(case_ids)) == 21,
            "exact 21-case identity set/order drift")
    main = next(case for case in result["cases"]
                if case["case_id"] == "MAIN_DUPLICATE_DERANGED")
    require(pairs(main["relation_rows"]) == EXPECTED_MAIN_ROWS,
            "main RTDL relation drift")
    require(pairs(main["primitive_index_attack"]["rows"])
            == EXPECTED_CP002_ROWS, "modeled CP002 rows drift")
    physical_position = {
        int(item_id): position
        for position, item_id in enumerate(main["indexed_physical_order"])
    }
    independently_derived_cp002 = tuple(sorted(
        (source_id, physical_position[predecessor_id])
        for source_id, predecessor_id in pairs(main["relation_rows"])
    ))
    require(independently_derived_cp002 == EXPECTED_CP002_ROWS,
            "CP002 rows do not follow from physical order")
    require(main["primitive_index_attack"]["matches_oracle"] is False,
            "modeled CP002 attack unexpectedly matched")

    boundary = result["capacity_boundary"]
    error = boundary["overflow_error"]
    require(boundary["complete_capacity"] == 10
            and boundary["complete_case_returned"] is True,
            "complete capacity boundary failed")
    require(boundary["overflow_capacity"] == 9
            and boundary["overflow_case_returned_result"] is False,
            "overflow exposed a result")
    require(error["type"] == "BoundedRelationError"
            and error["code"] == "capacity_overflow"
            and error["path"] == "rows",
            "overflow classification drift")
    for literal in ("observed_unique_count=10", "materialized=9", "capacity=9"):
        require(literal in error["message"], f"overflow omitted {literal}")

    native_path = root / "librtdl_optix.so"
    source_archive = root / "runtime_source.tar.gz"
    require(sha256(native_path) == EXPECTED_NATIVE_SHA256,
            "native bytes drift")
    require(sha256(source_archive) == EXPECTED_RUNTIME_SOURCE_SHA256,
            "runtime source archive drift")
    require(result["native_sha256"] == sha256(native_path),
            "result/native identity mismatch")
    example = repo / "examples/current/v4_public_stable_sort.py"
    runner = repo / "scripts/goal5830_v4_public_stable_sort_gpu_functional.py"
    require(result["example_source_sha256"] == sha256(example),
            "executed example differs from repo")
    require(result["runner_source_sha256"] == sha256(runner),
            "executed runner differs from repo")
    example_tree = ast.parse(example.read_text(encoding="utf-8"), filename=str(example))
    execute_calls = [
        node for node in ast.walk(example_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "execute"
    ]
    require(len(execute_calls) == 1
            and len(execute_calls[0].args) == 1
            and not execute_calls[0].keywords
            and isinstance(execute_calls[0].args[0], ast.Call)
            and getattr(execute_calls[0].args[0].func, "id", None)
            == "BoundedRelationBatch",
            "public example execute boundary can accept hidden oracle data")
    require(imported_roots(example) <= {
        "__future__", "argparse", "dataclasses", "hashlib", "json", "pathlib",
        "struct", "typing", "rtdsl",
    } and "rtdsl" in imported_roots(example),
            "public example import surface drift")
    require(result["proof_authority_scope"] == (
        "INHERITED_FROZEN_DIGEST__PROOF_BYTES_AND_SEMANTICS_NOT_REVALIDATED_"
        "BY_GOAL5830"), "proof scope drift")
    require("NVIDIA GeForce GTX 1070" in result["machine"]["nvidia_smi"],
            "Home GPU identity drift")
    return {
        "result_sha256": sha256(result_path),
        "case_count": len(result["cases"]),
        "all_exact_against_independent_pairwise_and_stable_oracles": True,
        "maximum_exact_binary32_boundary_executed": True,
        "capacity_10_success_9_fail_closed": True,
    }


def verify_pyoptix(repo: Path, evidence: Path) -> dict[str, object]:
    root = evidence / "pyoptix"
    result_path = root / "result_v2.json"
    stdout_path = root / "stdout_v2.json"
    require(result_path.read_bytes() == stdout_path.read_bytes(),
            "PyOptiX result/stdout bytes differ")
    result = load(result_path)
    require(result["schema"] == "rtdl.goal5830.pyoptix_stable_sort_cp002_control.v1",
            "PyOptiX schema drift")
    require(result["status"] == "PASS", "PyOptiX control did not pass")
    require(result["answer"] == (
        "NO__BROKEN_PROGRAM_LAUNCHED_AND_RETURNED_SILENT_WRONG_RELATION"),
        "PyOptiX answer drift")
    require(pairs(result["valid_program"]["relation_rows"])
            == EXPECTED_MAIN_ROWS, "valid PyOptiX relation drift")
    require(result["valid_program"]["application"][
        "matches_stable_sort_oracle"] is True,
        "valid PyOptiX sorting failed")
    broken = result["cp002_broken_program"]
    require(pairs(broken["relation_rows"]) == EXPECTED_CP002_ROWS,
            "CP002 PyOptiX relation drift")
    require(broken["platform_exception"] is None,
            "platform raised on CP002 program")
    require(broken["silent_wrong_before_application_postcheck"] is True,
            "CP002 was not silent before postcheck")
    require(broken["application"]["matches_stable_sort_oracle"] is False,
            "CP002 unexpectedly sorted correctly")
    indexed_order = tuple(int(value) for value in result["fixture"][
        "indexed_physical_order"])
    physical_position = {
        item_id: position for position, item_id in enumerate(indexed_order)
    }
    independently_derived_cp002 = tuple(sorted(
        (source_id, physical_position[predecessor_id])
        for source_id, predecessor_id in pairs(
            result["valid_program"]["relation_rows"])
    ))
    require(independently_derived_cp002 == pairs(broken["relation_rows"]),
            "PyOptiX CP002 rows do not derive from frozen physical order")

    mutation = result["exact_single_line_mutation"]
    require(mutation["before"] == VALID_EXPRESSION
            and mutation["after"] == CP002_EXPRESSION
            and mutation["changed_line_count"] == 1,
            "recorded one-line mutation drift")
    valid_source = root / "evidence_v2/device_sources/valid_nominal_item_id.cu"
    broken_source = (
        root / "evidence_v2/device_sources/cp002_physical_primitive_index.cu")
    valid_lines = valid_source.read_text(encoding="utf-8").splitlines()
    broken_lines = broken_source.read_text(encoding="utf-8").splitlines()
    deltas = [
        (before, after) for before, after in zip(valid_lines, broken_lines)
        if before != after
    ]
    require(len(valid_lines) == len(broken_lines)
            and deltas == [("        " + VALID_EXPRESSION,
                            "        " + CP002_EXPRESSION)],
            "device programs do not differ in exactly the declared line")
    require(valid_source.read_bytes() == (root / "matched_device.cu").read_bytes(),
            "valid source differs from frozen base")
    for name, identity in result["identities"].items():
        source_path = root / "evidence_v2/device_sources" / f"{name}.cu"
        ptx_path = root / "evidence_v2/ptx" / f"{name}.ptx"
        require(identity["device_source_sha256"] == sha256(source_path),
                f"{name}: source identity mismatch")
        require(identity["loaded_ptx_sha256"] == sha256(ptx_path),
                f"{name}: PTX identity mismatch")

    environment = result["environment"]
    baseline_path = root / "pyoptix_baseline.py"
    authority_path = (
        root / "goal5796_pyoptix_optix90_compatibility_preexecution_amendment_20260823.json")
    base_source_path = root / "matched_device.cu"
    require(environment["pyoptix_baseline_sha256"] == sha256(baseline_path),
            "preserved PyOptiX baseline identity mismatch")
    require(environment["compatibility_authority_sha256"] == sha256(authority_path),
            "preserved compatibility authority identity mismatch")
    require(environment["base_device_source_sha256"] == sha256(base_source_path),
            "preserved base device source identity mismatch")

    diagnostics = result["platform_diagnostics"]
    require(diagnostics["cuda_last_error_code"] == 0
            and diagnostics["cuda_last_error"] == "SUCCESS",
            "CUDA reported an error")
    require(diagnostics["optix_validation_error_message_count"] == 0
            and diagnostics["optix_validation"] == "NO_FATAL_OR_ERROR_MESSAGES",
            "OptiX reported fatal/error diagnostics")
    messages = diagnostics["all_optix_context_messages"]
    require(isinstance(messages, list) and len(messages) > 0,
            "full OptiX context messages were not preserved")
    require(not [message for message in messages if int(message["level"]) <= 2],
            "preserved OptiX messages contain a fatal/error")
    logs = diagnostics["pipeline_build_logs"]
    require(set(logs) == {
        "valid_nominal_item_id", "cp002_physical_primitive_index"},
        "pipeline logs incomplete")
    require(all(set(row) == {"module", "raygen", "miss", "hitgroup"}
                for row in logs.values()), "pipeline log stages incomplete")
    require(result["scope"]["imports_rtdl"] is False,
            "PyOptiX control imported RTDL")
    require(result["scope"]["performance_claimed"] is False
            and result["scope"]["registered_performance_timing_count"] == 0,
            "unexpected PyOptiX performance evidence")
    control = repo / "scripts/goal5830_pyoptix_stable_sort_cp002_control.py"
    require(sha256(control) == sha256(root / control.name),
            "executed PyOptiX control differs from repo")
    require("rtdsl" not in imported_roots(root / control.name),
            "executed PyOptiX control imports RTDL")
    return {
        "result_sha256": sha256(result_path),
        "valid_program_sorted_correctly": True,
        "one_line_cp002_program_returned_exact_silent_wrong_relation": True,
        "cuda_success_and_no_optix_fatal_or_error": True,
        "full_context_messages_and_all_api_returned_pipeline_logs_preserved": True,
    }


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    repo = args.repo_root.resolve()
    evidence = args.evidence_root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    rtdl = verify_rtdl(repo, evidence)
    pyoptix = verify_pyoptix(repo, evidence)
    manifest = {
        str(path.relative_to(evidence)).replace("\\", "/"): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(evidence.rglob("*"))
        if path.is_file()
    }
    result = {
        "schema": "rtdl.goal5830.independent_stable_sort_evidence_verification.v1",
        "status": "PASS",
        "imports_rtdl_or_pyoptix": False,
        "rtdl": rtdl,
        "pyoptix": pyoptix,
        "evidence_manifest": manifest,
        "claim_boundary": {
            "proves_one_sorting_instance_on_existing_bounded_relation_family": True,
            "proves_cp002_has_concrete_sorting_consequence": True,
            "proves_rtdl_invented_rt_sorting": False,
            "proves_application_mapping_correct_without_oracle": False,
            "proves_general_or_high_performance_sorting": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
