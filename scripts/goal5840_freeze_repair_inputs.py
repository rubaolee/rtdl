#!/usr/bin/env python3
"""Freeze the append-only Goal5840 Attempt-01 transport-repair authority."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from scripts import goal5840_freeze_gpu_inputs as original_freezer


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
BASE_COMMIT = "91a8309d9ee234f0315b6640a8dde1db29abe7e9"
PRE_POD_AUTHORITY = GOAL_ROOT / "PRE_POD_INPUT_AUTHORITY.json"
ATTEMPT_01_INCIDENT = GOAL_ROOT / "ATTEMPT_01_ENGINEERING_FAILURE.md"
OUTPUT = GOAL_ROOT / "POST_ATTEMPT_01_REPAIR_AUTHORITY.json"
DOMAIN = b"rtdl.goal5840.post_attempt_01_repair_authority.v1\0"

ALLOWED_CHANGED_PATHS = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_01_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_01_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_repair_inputs.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_evidence_capture.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_real_target_evidence_capture_test.py",
)
SOURCE_PATHS = tuple(sorted({
    *original_freezer.SOURCE_PATHS,
    "scripts/goal5840_freeze_repair_inputs.py",
}))


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"git show {commit}:{path}: {completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def _changed_paths_since_base() -> tuple[str, ...]:
    tracked = {
        line
        for line in _git("diff", "--name-only", BASE_COMMIT, "--").splitlines()
        if line
    }
    untracked = {
        line
        for line in _git("ls-files", "--others", "--exclude-standard").splitlines()
        if line
    }
    return tuple(sorted(tracked | untracked))


def _verify_original_authority() -> dict[str, object]:
    relative = str(PRE_POD_AUTHORITY.relative_to(ROOT))
    current = PRE_POD_AUTHORITY.read_bytes()
    if current != _git_blob(BASE_COMMIT, relative):
        raise RuntimeError("original pre-pod authority differs from base commit")
    authority = json.loads(current.decode("ascii"))
    body = dict(authority)
    observed = body.get("authority_sha256")
    body["authority_sha256"] = ""
    expected = hashlib.sha256(
        original_freezer.DOMAIN + _canonical(body)
    ).hexdigest()
    if (
        observed != expected
        or authority.get("status")
        != "FROZEN_INPUTS_AND_TRUST_ROOTS__NO_GPU_RESULT"
        or authority.get("execution_counts_at_freeze")
        != {
            "goal5840_gpu_launches": 0,
            "goal5840_positive_target_bundles": 0,
            "goal5840_exact_bundle_mutations": 0,
        }
    ):
        raise RuntimeError("original pre-pod authority contract differs")
    return authority


def _source_rows() -> list[dict[str, object]]:
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"repair source missing: {relative}")
        rows.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha_file(path),
        })
    return rows


def build_authority(frozen_at_utc: str) -> dict[str, object]:
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
    ).returncode:
        raise RuntimeError("Attempt-01 source commit is not an ancestor of HEAD")
    changed_paths = _changed_paths_since_base()
    expected_paths = set(ALLOWED_CHANGED_PATHS)
    if not OUTPUT.exists():
        expected_paths.remove(str(OUTPUT.relative_to(ROOT)))
    if set(changed_paths) != expected_paths:
        raise RuntimeError(
            "repair changed-path set differs: "
            f"observed={changed_paths!r} expected={tuple(sorted(expected_paths))!r}"
        )

    original = _verify_original_authority()
    rebuilt = original_freezer.build_authority(str(original["frozen_at_utc"]))
    if (
        rebuilt["mode_cases"] != original["mode_cases"]
        or rebuilt["preregistration"] != original["preregistration"]
        or rebuilt["goal5838_frozen_core"] != original["goal5838_frozen_core"]
    ):
        raise RuntimeError("scientific inputs differ after transport repair")

    attempt_bytes = ATTEMPT_01_INCIDENT.read_bytes()
    result: dict[str, object] = {
        "schema": "rtdl.goal5840.post_attempt_01_repair_authority.v1",
        "goal": 5840,
        "frozen_at_utc": frozen_at_utc,
        "stage": "AFTER_ATTEMPT_01_BEFORE_ATTEMPT_02_GPU_EXECUTION",
        "status": "FROZEN_BOUNDED_EVIDENCE_TRANSPORT_REPAIR__NO_ACCEPTED_RESULT",
        "base_attempt": {
            "source_commit": BASE_COMMIT,
            "pre_pod_input_authority": {
                "path": str(PRE_POD_AUTHORITY.relative_to(ROOT)),
                "bytes": PRE_POD_AUTHORITY.stat().st_size,
                "file_sha256": _sha_file(PRE_POD_AUTHORITY),
                "authority_sha256": original["authority_sha256"],
            },
            "attempt_01_incident": {
                "path": str(ATTEMPT_01_INCIDENT.relative_to(ROOT)),
                "bytes": len(attempt_bytes),
                "file_sha256": hashlib.sha256(attempt_bytes).hexdigest(),
                "classification": "EVIDENCE_TRANSPORT_ENGINEERING_FAILURE",
            },
            "observed_counts": {
                "runner_processes_started": 1,
                "frozen_modes_entered": 1,
                "public_route_expected_outputs_returned": 1,
                "published_evidence_bundles": 0,
                "published_independent_property_reports": 0,
                "published_mutation_applications": 0,
                "accepted_positive_evidence_rows": 0,
            },
        },
        "repair_scope": {
            "defect": "nested_read_only_mapping_not_recursively_json_canonicalized",
            "repair": "recursive_mapping_sequence_to_canonical_json_tree",
            "nonsemantic_harness_hardening": (
                "generate_pod_mutation_report_under_python_isolated_mode"
            ),
            "allowed_changed_paths": list(ALLOWED_CHANGED_PATHS),
            "exact_changed_paths_since_base": list(ALLOWED_CHANGED_PATHS),
            "route_change_allowed": False,
            "fixture_or_oracle_change_allowed": False,
            "declaration_or_control_root_change_allowed": False,
            "property_or_mutation_change_allowed": False,
            "native_engine_change_allowed": False,
            "frozen_core_change_allowed": False,
        },
        "preregistration": original["preregistration"],
        "source_files": _source_rows(),
        "goal5838_frozen_core": original["goal5838_frozen_core"],
        "route_bundle_group_count": original["route_bundle_group_count"],
        "required_mode_count": original["required_mode_count"],
        "mode_cases": original["mode_cases"],
        "execution_counts_at_repair_freeze": {
            "attempted_runner_processes": 1,
            "entered_frozen_modes": 1,
            "returned_expected_outputs": 1,
            "published_evidence_bundles": 0,
            "published_independent_property_reports": 0,
            "published_mutation_applications": 0,
            "accepted_goal5840_positive_evidence_rows": 0,
        },
        "claim_boundary": {
            "append_only_engineering_repair_authority": True,
            "scientific_inputs_unchanged": True,
            "accepted_goal5840_result": False,
            "lowering_preservation_established": False,
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
        raise RuntimeError("stored repair authority differs from current inputs")
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
        "accepted_positive_evidence_rows": document[
            "execution_counts_at_repair_freeze"
        ]["accepted_goal5840_positive_evidence_rows"],
        "output": str(OUTPUT),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
