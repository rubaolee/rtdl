#!/usr/bin/env python3
"""Freeze Goal5840 declarations, fixtures, and source roots before GPU use."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from rtdsl.v4_target_control_flow_evidence import (
    capture_target_control_flow_evidence,
)
from rtdsl.v4_target_evidence_bundle import build_family_target_declaration
from scripts.goal5840_gpu_cases import goal5840_mode_cases


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
OUTPUT = GOAL_ROOT / "PRE_POD_INPUT_AUTHORITY.json"
PREREGISTRATION = GOAL_ROOT / "GOAL5840_PREREGISTRATION.json"
DOMAIN = b"rtdl.goal5840.pre_pod_input_authority.v1\0"
SOURCE_PATHS = (
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_gpu_inputs.py",
    "scripts/goal5840_gpu_cases.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_mutation_suite.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_control_flow_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "src/rtdsl/v4_target_evidence_capture.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_independent_target_checker_test.py",
    "tests/goal5840_real_target_evidence_capture_test.py",
    "tests/goal5840_target_evidence_bundle_test.py",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonable(value: object) -> object:
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def build_authority(frozen_at_utc: str) -> dict[str, object]:
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
    seal_path = (
        ROOT
        / "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "GENERIC_CORE_SEAL.json"
    )
    seal = json.loads(seal_path.read_text(encoding="ascii"))
    frozen_files = []
    for row in seal["frozen_core_files"]:
        path = ROOT / row["path"]
        observed = _sha_file(path)
        if observed != row["sha256"]:
            raise RuntimeError(f"Goal5838 frozen core changed: {row['path']}")
        frozen_files.append({
            "path": row["path"],
            "bytes": path.stat().st_size,
            "sha256": observed,
        })

    source_files = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        source_files.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha_file(path),
        })

    mode_rows = []
    for case in goal5840_mode_cases():
        declaration = build_family_target_declaration(
            case.route_id, case.route.plan
        )
        control = capture_target_control_flow_evidence(
            case.route_id, repository_root=ROOT
        )
        expected = _jsonable(case.expected_output)
        fixture = _jsonable(case.fixture_document)
        mode_rows.append({
            "key": case.key,
            "route_id": case.route_id,
            "mode": case.mode,
            "target_kind": case.target_kind,
            "plan_sha256": case.route.plan.plan_sha256,
            "declaration_sha256": declaration["declaration_sha256"],
            "control_flow_manifest_sha256": control["manifest_sha256"],
            "fixture_sha256": _digest(fixture),
            "expected_output": expected,
            "expected_output_sha256": _digest(expected),
        })
    expected_keys = {
        "stable::bounded_relation::canonical_bounded_pair_collection::"
        "capacity_fail_closed_collection",
        "stable::triangle_reduction::checked_u64_reduction::all_hit_count",
        "stable::triangle_reduction::checked_u64_reduction::weighted_hit_count",
        "prospective::builtin_sphere::any_hit_count_continue_u64_per_query::"
        "accept_every_hit_and_continue",
    }
    if {row["key"] for row in mode_rows} != expected_keys:
        raise RuntimeError("Goal5840 four-mode key set differs")

    result: dict[str, object] = {
        "schema": "rtdl.goal5840.pre_pod_input_authority.v1",
        "goal": 5840,
        "frozen_at_utc": frozen_at_utc,
        "stage": "BEFORE_ANY_GOAL5840_GPU_EXECUTION",
        "status": "FROZEN_INPUTS_AND_TRUST_ROOTS__NO_GPU_RESULT",
        "preregistration": {
            "path": str(PREREGISTRATION.relative_to(ROOT)),
            "bytes": PREREGISTRATION.stat().st_size,
            "file_sha256": _sha_file(PREREGISTRATION),
            "authority_sha256": preregistration["authority_sha256"],
            "mutation_count": preregistration["mutation_count"],
        },
        "source_files": source_files,
        "goal5838_frozen_core": {
            "seal_sha256": seal["seal_sha256"],
            "files": frozen_files,
            "changed_file_count": 0,
        },
        "route_bundle_group_count": 3,
        "required_mode_count": 4,
        "mode_cases": mode_rows,
        "execution_counts_at_freeze": {
            "goal5840_gpu_launches": 0,
            "goal5840_positive_target_bundles": 0,
            "goal5840_exact_bundle_mutations": 0,
        },
        "claim_boundary": {
            "input_and_declaration_freeze_only": True,
            "lowering_preservation_established": False,
            "gpu_result": False,
            "performance_or_speedup": False,
            "application_correctness": False,
            "external_review_or_consensus": False,
        },
        "authority_sha256": "",
    }
    result["authority_sha256"] = hashlib.sha256(
        DOMAIN + _canonical(result)
    ).hexdigest()
    return result


def _verify_stored() -> dict[str, object]:
    stored = json.loads(OUTPUT.read_text(encoding="ascii"))
    rebuilt = build_authority(str(stored["frozen_at_utc"]))
    if rebuilt != stored:
        raise RuntimeError("stored pre-pod input authority differs from source")
    return stored


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write-stored", action="store_true")
    action.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_stored:
        if OUTPUT.exists():
            raise FileExistsError(OUTPUT)
        frozen_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        document = build_authority(frozen_at)
        OUTPUT.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )
    else:
        document = _verify_stored()
    print(json.dumps({
        "status": document["status"],
        "authority_sha256": document["authority_sha256"],
        "required_mode_count": document["required_mode_count"],
        "output": str(OUTPUT),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
