#!/usr/bin/env python3
"""Freeze Goal5840's append-only Attempt-02 identity-repair authority."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from scripts import goal5840_freeze_gpu_inputs as original_freezer
from scripts import goal5840_freeze_repair_inputs as prior_repair_freezer


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
BASE_COMMIT = "3dcd92e3c2ebc71faffbcae0783b747b9820d71e"
PRIOR_REPAIR_AUTHORITY = GOAL_ROOT / "POST_ATTEMPT_01_REPAIR_AUTHORITY.json"
ATTEMPT_02_INCIDENT = GOAL_ROOT / "ATTEMPT_02_ENGINEERING_FAILURE.md"
OUTPUT = GOAL_ROOT / "POST_ATTEMPT_02_REPAIR_AUTHORITY.json"
DOMAIN = b"rtdl.goal5840.post_attempt_02_repair_authority.v1\0"
ATTEMPT_02_INCIDENT_SHA256 = (
    "865eeb8d5ccacb4f87fe2a3bd73e99e9c835974e27dcae8ebd294ae12c5c7ade"
)

ALLOWED_CHANGED_PATHS = (
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_02_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_02_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_target_evidence_bundle_test.py",
)
SOURCE_PATHS = tuple(sorted({
    *prior_repair_freezer.SOURCE_PATHS,
    "scripts/goal5840_freeze_attempt02_repair_inputs.py",
}))


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


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
            f"git show {commit}:{path}: "
            f"{completed.stderr.decode(errors='replace')}"
        )
    return completed.stdout


def _changed_paths(base: str, revision: str | None = None) -> tuple[str, ...]:
    target = base if revision is None else f"{base}..{revision}"
    tracked = {
        line
        for line in _git("diff", "--name-only", target, "--").splitlines()
        if line
    }
    if revision is not None:
        return tuple(sorted(tracked))
    untracked = {
        line
        for line in _git("ls-files", "--others", "--exclude-standard").splitlines()
        if line
    }
    return tuple(sorted(tracked | untracked))


def _verify_seal(
    document: dict[str, object], field: str, domain: bytes, label: str
) -> None:
    body = dict(document)
    observed = body.get(field)
    body[field] = ""
    if observed != hashlib.sha256(domain + _canonical(body)).hexdigest():
        raise RuntimeError(f"{label} seal differs")


def _verify_prior_repair_authority() -> dict[str, object]:
    relative = str(PRIOR_REPAIR_AUTHORITY.relative_to(ROOT))
    current = PRIOR_REPAIR_AUTHORITY.read_bytes()
    if current != _git_blob(BASE_COMMIT, relative):
        raise RuntimeError("prior repair authority differs from its commit")
    authority = json.loads(current.decode("ascii"))
    _verify_seal(
        authority,
        "authority_sha256",
        prior_repair_freezer.DOMAIN,
        "prior repair authority",
    )
    if (
        authority.get("schema")
        != "rtdl.goal5840.post_attempt_01_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_01_BEFORE_ATTEMPT_02_GPU_EXECUTION"
        or authority.get("status")
        != "FROZEN_BOUNDED_EVIDENCE_TRANSPORT_REPAIR__NO_ACCEPTED_RESULT"
        or authority.get("execution_counts_at_repair_freeze")
        != {
            "attempted_runner_processes": 1,
            "entered_frozen_modes": 1,
            "returned_expected_outputs": 1,
            "published_evidence_bundles": 0,
            "published_independent_property_reports": 0,
            "published_mutation_applications": 0,
            "accepted_goal5840_positive_evidence_rows": 0,
        }
    ):
        raise RuntimeError("prior repair authority contract differs")
    if _changed_paths(prior_repair_freezer.BASE_COMMIT, BASE_COMMIT) != tuple(
        sorted(prior_repair_freezer.ALLOWED_CHANGED_PATHS)
    ):
        raise RuntimeError("prior repair commit path set differs")
    rows = authority.get("source_files")
    if not isinstance(rows, list):
        raise RuntimeError("prior repair source inventory is absent")
    observed_paths = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("prior repair source row is malformed")
        relative = str(row["path"])
        blob = _git_blob(BASE_COMMIT, relative)
        if (
            relative in observed_paths
            or row.get("bytes") != len(blob)
            or row.get("sha256") != _sha_bytes(blob)
        ):
            raise RuntimeError(f"prior repair source identity differs: {relative}")
        observed_paths.add(relative)
    if observed_paths != set(prior_repair_freezer.SOURCE_PATHS):
        raise RuntimeError("prior repair source denominator differs")
    return authority


def _source_rows() -> list[dict[str, object]]:
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"Attempt-02 repair source missing: {relative}")
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
        raise RuntimeError("Attempt-02 source commit is not an ancestor of HEAD")
    changed_paths = _changed_paths(BASE_COMMIT)
    expected_paths = set(ALLOWED_CHANGED_PATHS)
    if not OUTPUT.exists():
        expected_paths.remove(str(OUTPUT.relative_to(ROOT)))
    if set(changed_paths) != expected_paths:
        raise RuntimeError(
            "Attempt-02 repair changed-path set differs: "
            f"observed={changed_paths!r} expected={tuple(sorted(expected_paths))!r}"
        )

    prior = _verify_prior_repair_authority()
    original_document = json.loads(
        original_freezer.OUTPUT.read_text(encoding="ascii")
    )
    original = original_freezer.build_authority(
        str(original_document["frozen_at_utc"])
    )
    if (
        original["mode_cases"] != prior["mode_cases"]
        or original["preregistration"] != prior["preregistration"]
        or original["goal5838_frozen_core"] != prior["goal5838_frozen_core"]
    ):
        raise RuntimeError("scientific inputs differ after Attempt-02 repair")

    incident_bytes = ATTEMPT_02_INCIDENT.read_bytes()
    if _sha_bytes(incident_bytes) != ATTEMPT_02_INCIDENT_SHA256:
        raise RuntimeError("Attempt-02 incident identity differs")
    prior_bytes = PRIOR_REPAIR_AUTHORITY.read_bytes()
    result: dict[str, object] = {
        "schema": "rtdl.goal5840.post_attempt_02_repair_authority.v1",
        "goal": 5840,
        "frozen_at_utc": frozen_at_utc,
        "stage": "AFTER_ATTEMPT_02_BEFORE_ATTEMPT_03_GPU_EXECUTION",
        "status": (
            "FROZEN_BOUNDED_EXECUTABLE_IDENTITY_REPAIR__NO_ACCEPTED_RESULT"
        ),
        "base_chain": {
            "attempt_01_source_commit": prior_repair_freezer.BASE_COMMIT,
            "attempt_01_repair_commit": BASE_COMMIT,
            "post_attempt_01_repair_authority": {
                "path": str(PRIOR_REPAIR_AUTHORITY.relative_to(ROOT)),
                "bytes": len(prior_bytes),
                "file_sha256": _sha_bytes(prior_bytes),
                "authority_sha256": prior["authority_sha256"],
            },
            "attempt_02_incident": {
                "path": str(ATTEMPT_02_INCIDENT.relative_to(ROOT)),
                "bytes": len(incident_bytes),
                "file_sha256": ATTEMPT_02_INCIDENT_SHA256,
                "classification": (
                    "EVIDENCE_EXECUTABLE_IDENTITY_CANONICALIZATION_"
                    "ENGINEERING_FAILURE"
                ),
            },
            "formal_observed_counts_through_attempt_02": {
                "runner_processes_started": 2,
                "frozen_modes_entered": 2,
                "public_route_expected_outputs_returned": 2,
                "published_evidence_bundles": 0,
                "published_independent_property_reports": 0,
                "published_mutation_applications": 0,
                "accepted_positive_evidence_rows": 0,
            },
            "post_failure_diagnostics": {
                "diagnostic_processes": 2,
                "diagnostic_mode_executions": 2,
                "diagnostic_expected_outputs_returned": 2,
                "diagnostic_evidence_files_published": 0,
                "accepted_positive_evidence_rows": 0,
            },
        },
        "repair_scope": {
            "defect": "str_derived_enum_role_stringified_to_enum_qualname",
            "repair": "preserve_and_validate_underlying_string_enum_value",
            "allowed_changed_paths": list(ALLOWED_CHANGED_PATHS),
            "exact_changed_paths_since_base": list(ALLOWED_CHANGED_PATHS),
            "route_change_allowed": False,
            "fixture_or_oracle_change_allowed": False,
            "declaration_or_control_root_change_allowed": False,
            "property_or_mutation_change_allowed": False,
            "native_engine_change_allowed": False,
            "frozen_core_change_allowed": False,
        },
        "preregistration": prior["preregistration"],
        "source_files": _source_rows(),
        "goal5838_frozen_core": prior["goal5838_frozen_core"],
        "route_bundle_group_count": prior["route_bundle_group_count"],
        "required_mode_count": prior["required_mode_count"],
        "mode_cases": prior["mode_cases"],
        "execution_counts_at_repair_freeze": {
            "formal_runner_processes": 2,
            "formal_entered_modes": 2,
            "formal_returned_expected_outputs": 2,
            "diagnostic_processes": 2,
            "diagnostic_mode_executions": 2,
            "published_evidence_bundles": 0,
            "published_independent_property_reports": 0,
            "published_mutation_applications": 0,
            "accepted_goal5840_positive_evidence_rows": 0,
        },
        "claim_boundary": {
            "append_only_engineering_repair_authority": True,
            "two_prior_formal_failures_preserved": True,
            "diagnostic_launches_not_accepted_as_evidence": True,
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
        raise RuntimeError("stored Attempt-02 repair authority differs")
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
        document = build_authority(
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
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
