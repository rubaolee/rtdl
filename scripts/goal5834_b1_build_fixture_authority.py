#!/usr/bin/env python3
"""Freeze Goal5834-B1 fixtures before any Boolean GPU worker exists."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from examples.curve_boolean_contact.fixtures import (
    build_evaluation_manifest,
    runtime_static_input,
)
from rtdsl.v4_curve import BuiltinCurveStaticInput, CurveBooleanSegmentBatch


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MEMBERS = (
    "examples/curve_boolean_contact/independent_oracle.py",
    "examples/curve_boolean_contact/fixtures.py",
    "src/rtdsl/v4_builtin_curve_standard_library.py",
    "src/rtdsl/v4_curve_physical_schema.py",
    "src/rtdsl/v4_sphere_optix_wrapper_codegen.py",
    "src/rtdsl/v4_curve_optix_wrapper_codegen.py",
    "src/rtdsl/v4_public_builtin_curve.py",
    "src/rtdsl/v4_curve_prepared_runtime.py",
    "src/rtdsl/v4_curve.py",
    "tests/goal5834_b1_curve_boolean_specialization_test.py",
    "tests/goal5834_b1_boolean_fixture_oracle_test.py",
)


def _bytes(value) -> bytes:
    return (json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=True,
        allow_nan=False) + "\n").encode("utf-8")


def _sha_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _git_observation():
    def run(*arguments):
        completed = subprocess.run(
            ["git", *arguments], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False)
        return {
            "returncode": completed.returncode,
            "text": completed.stdout.strip(),
        }
    return {
        "workspace": str(ROOT),
        "rev_parse": run("rev-parse", "HEAD"),
        "status": run("status", "--short"),
        "commit_identity_claimed": False,
        "binding_kind": "EXACT_SOURCE_MEMBER_HASHES__BROKEN_GIT_DISCLOSED",
    }


def build(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = build_evaluation_manifest()
    source_members = []
    for name in SOURCE_MEMBERS:
        path = (ROOT / name).resolve(strict=True)
        if ROOT not in path.parents or not path.is_file():
            raise RuntimeError(f"unsafe source member: {name}")
        source_members.append({
            "path": name,
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        })

    worker_rows = []
    expected_rows = []
    for row in manifest["executable"]:
        static_values = runtime_static_input(row)
        public_static = BuiltinCurveStaticInput(**static_values)
        public_batch = CurveBooleanSegmentBatch(
            row["normalization"]["queries"])
        worker_rows.append({
            "family_id": row["family_id"],
            "execution_id": row["execution_id"],
            "normalization_origin_f64_bits": list(
                row["normalization"]["origin_f64_bits"]),
            "normalization_scale_f64_bits":
                row["normalization"]["scale_f64_bits"],
            "original_input_sha256":
                row["normalization"]["original_input_sha256"],
            "normalized_input_sha256":
                row["normalization"]["normalized_input_sha256"],
            "static_input": static_values,
            "queries": row["normalization"]["queries"],
            "public_static_input_commitment_sha256":
                public_static.commitment_sha256,
            "public_query_commitment_sha256": public_batch.commitment_sha256,
        })
        expected_rows.append({
            "execution_id": row["execution_id"],
            "expected_per_query_hit": list(
                row["canonical_oracle"]["per_query_hit"]),
            "expected_collision": row["canonical_oracle"]["collision"],
            "original_oracle_collision": row["original_oracle"]["collision"],
            "oracle_boolean_equal": row["oracle_boolean_equal"],
        })

    worker_inputs = {
        "schema": "rtdl.goal5834_b1.boolean_worker_inputs.v1",
        "contains_expected_output": False,
        "contains_pairwise_geometry_result": False,
        "primary_execution_count": 11,
        "rows": worker_rows,
    }
    worker_body = _bytes(worker_inputs)
    worker_path = output_dir / "WORKER_INPUTS.json"
    worker_path.write_bytes(worker_body)

    authority = {
        "schema": "rtdl.goal5834_b1.fixture_authority.v1",
        "status": "SCIENTIFIC_FIXTURES_FROZEN__WORKER_ZERO_FORBIDDEN",
        "goal": "5834-B1",
        "performance_measurement_authorized": False,
        "external_review_requested": False,
        "goal5835_authorized": False,
        "public_executable_semantics": "provider_any_contact_bit",
        "mathematical_comparison_scope": "FROZEN_QUALIFIED_FIXTURES_ONLY",
        "fixture_manifest": manifest,
        "expected_before_execution": expected_rows,
        "worker_inputs": {
            "path": "WORKER_INPUTS.json",
            "bytes": len(worker_body),
            "sha256": _sha_bytes(worker_body),
            "expected_output_bytes_present": False,
        },
        "source_members": source_members,
        "repository_binding": _git_observation(),
        "predeclared_outcomes": {
            "all_match": "GOAL5834_B1_COMPLETE_REGISTERED_FIXTURE_EVALUATION",
            "provider_boolean_mismatch":
                "TERMINAL_NEGATIVE__BUILTIN_CURVE_BOOLEAN_UNRELIABLE_FOR_REGISTERED_CORE",
            "qualification_or_execution_failure":
                "TERMINAL_NEGATIVE__B1_REGISTERED_FIXTURE_NOT_EXECUTABLE_AS_FROZEN",
        },
        "claim_ceiling": {
            "generalization_exam_count": 0,
            "paper_app_claimed": False,
            "full_collision_detection_claimed": False,
            "exact_toi_or_id_claimed": False,
            "arbitrary_capsule_correctness_claimed": False,
            "performance_claimed": False,
        },
    }
    authority_body = _bytes(authority)
    authority_path = output_dir / "FIXTURE_AUTHORITY.json"
    authority_path.write_bytes(authority_body)
    return {
        "fixture_authority_path": str(authority_path),
        "fixture_authority_sha256": _sha_bytes(authority_body),
        "fixture_authority_bytes": len(authority_body),
        "worker_inputs_path": str(worker_path),
        "worker_inputs_sha256": _sha_bytes(worker_body),
        "worker_inputs_bytes": len(worker_body),
        "fixture_family_count": manifest["fixture_family_count"],
        "primary_execution_count": manifest["concrete_gpu_execution_count"],
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
