#!/usr/bin/env python3
"""RTDL-free evaluator for a sealed Goal5834-B1 raw GPU receipt."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(
        encoding="utf-8", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")))


def _load_oracle(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8", errors="strict"))
    allowed = {"__future__", "math", "struct"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = {item.name.split(".")[0] for item in node.names}
            if not names <= allowed:
                raise RuntimeError(f"oracle imports non-stdlib modules: {names}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in allowed:
                raise RuntimeError(f"oracle imports non-stdlib module: {node.module}")
    spec = importlib.util.spec_from_file_location(
        "goal5834_b1_independent_oracle", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("independent oracle cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(args):
    authority_path = args.fixture_authority.resolve(strict=True)
    worker_inputs_path = args.worker_inputs.resolve(strict=True)
    target_path = args.target_preaction.resolve(strict=True)
    raw_path = args.raw_receipt.resolve(strict=True)
    oracle_path = args.oracle.resolve(strict=True)
    authority = _load(authority_path)
    worker_inputs = _load(worker_inputs_path)
    target = _load(target_path)
    raw = _load(raw_path)
    if authority.get("schema") != "rtdl.goal5834_b1.fixture_authority.v1" \
            or worker_inputs.get("schema") != \
                "rtdl.goal5834_b1.boolean_worker_inputs.v1":
        raise RuntimeError("B1 evidence schema differs")
    lineage = target.get("lineage", "B1")
    expected_target_schema = (
        "rtdl.goal5834_b3.home_target_preaction.v1"
        if lineage == "B3" else
        "rtdl.goal5834_b2.home_target_preaction.v1"
        if lineage == "B2" else
        "rtdl.goal5834_b1.home_target_preaction.v1")
    expected_raw_schema = (
        "rtdl.goal5834_b3.raw_gpu_boolean_receipt.v1"
        if lineage == "B3" else
        "rtdl.goal5834_b2.raw_gpu_boolean_receipt.v1"
        if lineage == "B2" else
        "rtdl.goal5834_b1.raw_gpu_boolean_receipt.v1")
    if target.get("schema") != expected_target_schema \
            or raw.get("schema") != expected_raw_schema \
            or raw.get("lineage", "B1") != lineage:
        raise RuntimeError("B1/B2 execution lineage differs")
    if authority["worker_inputs"]["sha256"] != _sha(worker_inputs_path) \
            or target["fixture_authority_sha256"] != _sha(authority_path) \
            or target["worker_inputs_sha256"] != _sha(worker_inputs_path) \
            or raw["fixture_authority_sha256"] != _sha(authority_path) \
            or raw["worker_inputs_sha256"] != _sha(worker_inputs_path) \
            or raw["target_preaction_sha256"] != _sha(target_path):
        raise RuntimeError("B1 evidence custody differs")
    if raw.get("status") != "RAW_GPU_BITS_SEALED__UNEVALUATED" \
            or raw.get("oracle_imported_or_called") is not False \
            or raw.get("expected_output_available_to_worker") is not False \
            or raw.get("registered_performance_timing_count") != 0:
        raise RuntimeError("raw receipt was not an oracle-free functional run")
    if raw.get("primary_worker_count") != 11 \
            or len(raw.get("rows", ())) != 11:
        raise RuntimeError("raw primary worker denominator differs")

    oracle = _load_oracle(oracle_path)
    authority_rows = {
        row["execution_id"]: row
        for row in authority["fixture_manifest"]["executable"]}
    expected_preaction = {
        row["execution_id"]: row
        for row in authority["expected_before_execution"]}
    worker_rows = {
        row["execution_id"]: row for row in worker_inputs["rows"]}
    raw_rows = {row["execution_id"]: row for row in raw["rows"]}
    if len(authority_rows) != 11 or set(authority_rows) != set(worker_rows) \
            or set(authority_rows) != set(raw_rows) \
            or set(authority_rows) != set(expected_preaction):
        raise RuntimeError("fixture/worker/result execution identities differ")

    evaluation_rows = []
    mismatch_rows = []
    for execution_id in sorted(authority_rows):
        frozen = authority_rows[execution_id]
        worker = worker_rows[execution_id]
        observed = raw_rows[execution_id]
        original_input = frozen["original_input"]
        normalized = frozen["normalization"]
        original = oracle.evaluate_scene(
            original_input["capsules"], original_input["queries"])
        canonical = oracle.evaluate_scene(
            normalized["capsules"], normalized["queries"])
        expected = expected_preaction[execution_id]
        expected_bits = tuple(expected["expected_per_query_hit"])
        observed_bits = tuple(observed["per_query_hit"])
        if tuple(canonical["per_query_hit"]) != expected_bits \
                or canonical["collision"] != expected["expected_collision"] \
                or original["collision"] != \
                    expected["original_oracle_collision"]:
            raise RuntimeError(f"preaction oracle drift at {execution_id}")
        if original["collision"] != canonical["collision"] \
                or expected["oracle_boolean_equal"] is not True:
            raise RuntimeError(f"original/canonical oracle differs at {execution_id}")
        if worker["normalized_input_sha256"] != \
                normalized["normalized_input_sha256"] \
                or observed["normalized_input_sha256"] != \
                    worker["normalized_input_sha256"] \
                or observed["public_static_input_commitment_sha256"] != \
                    worker["public_static_input_commitment_sha256"] \
                or observed["public_query_commitment_sha256"] != \
                    worker["public_query_commitment_sha256"]:
            raise RuntimeError(f"input/receipt binding differs at {execution_id}")
        output_digest = _digest({
            "schema": "rtdl.v4.curve_provider_any_contact_bits.v1",
            "per_query_hit": list(observed_bits),
        })
        if output_digest != observed["raw_gpu_bit_vector_commitment_sha256"] \
                or output_digest != observed["traversal_receipt"]["output_digest"] \
                or observed["physical_receipt"][
                    "raw_gpu_bit_vector_commitment_sha256"] != output_digest:
            raise RuntimeError(f"raw GPU vector seal differs at {execution_id}")
        match = observed_bits == expected_bits \
            and observed["collision_host_or"] == canonical["collision"]
        if not match:
            mismatch_rows.append(execution_id)
        evaluation_rows.append({
            "execution_id": execution_id,
            "expected_per_query_hit": list(expected_bits),
            "observed_per_query_hit": list(observed_bits),
            "expected_collision": canonical["collision"],
            "observed_collision_host_or": observed["collision_host_or"],
            "match": match,
            "repeat_preserved": observed["repeat_per_query_hit"] == \
                observed["per_query_hit"],
            "reversed_preserved": observed["reversed_per_query_hit"] == \
                list(reversed(observed["per_query_hit"])),
            "true_optix": observed["traversal_receipt"].get(
                "physical_executor_classification") ==
                "optix_traversal_observed",
        })

    if mismatch_rows:
        status = (
            "TERMINAL_NEGATIVE__BUILTIN_CURVE_BOOLEAN_UNRELIABLE_FOR_REGISTERED_CORE")
        goal5835_authorized = False
    else:
        status = (
            "GOAL5834_B3_COMPLETE_REGISTERED_FIXTURE_EVALUATION"
            if lineage == "B3" else
            "GOAL5834_B2_COMPLETE_REGISTERED_FIXTURE_EVALUATION"
            if lineage == "B2" else
            "GOAL5834_B1_COMPLETE_REGISTERED_FIXTURE_EVALUATION")
        goal5835_authorized = True
    return {
        "schema": (
            "rtdl.goal5834_b3.independent_evaluation.v1"
            if lineage == "B3" else
            "rtdl.goal5834_b2.independent_evaluation.v1"
            if lineage == "B2" else
            "rtdl.goal5834_b1.independent_evaluation.v1"),
        "status": status,
        "lineage": lineage,
        "controlling_for_goal5834_b1": True,
        "fixture_authority_sha256": _sha(authority_path),
        "worker_inputs_sha256": _sha(worker_inputs_path),
        "target_preaction_sha256": _sha(target_path),
        "raw_gpu_receipt_sha256": _sha(raw_path),
        "independent_oracle_sha256": _sha(oracle_path),
        "fixture_family_count": 10,
        "primary_execution_count": 11,
        "matching_primary_execution_count": 11 - len(mismatch_rows),
        "mismatch_execution_ids": mismatch_rows,
        "evaluation_rows": evaluation_rows,
        "evaluator_ineligible_worker_count": 0,
        "malformed_prelaunch_rejection_count": 1,
        "registered_performance_timing_count": 0,
        "generalization_exam_count": 0,
        "paper_app_claimed": False,
        "provider_capsule_theorem_claimed": False,
        "goal5835_registered_fixture_mapping_authorized":
            goal5835_authorized,
        "goal5835_authorization_scope": (
            "REGISTERED_FIXTURE_SUI_DERIVED_EDGE_CROSSING_MAPPING_ONLY"
            if goal5835_authorized else "NONE"),
        "first_contact_general_numeric_goal_status":
            "INCOMPLETE__UNCHANGED_BY_BOOLEAN_RESULT",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-authority", required=True, type=Path)
    parser.add_argument("--worker-inputs", required=True, type=Path)
    parser.add_argument("--target-preaction", required=True, type=Path)
    parser.add_argument("--raw-receipt", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"],
        "matching_primary_execution_count":
            result["matching_primary_execution_count"],
        "primary_execution_count": result["primary_execution_count"],
        "goal5835_registered_fixture_mapping_authorized":
            result["goal5835_registered_fixture_mapping_authorized"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
