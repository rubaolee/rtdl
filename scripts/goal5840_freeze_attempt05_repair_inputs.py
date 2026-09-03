#!/usr/bin/env python3
"""Freeze Goal5840's append-only Attempt-05 runner-repair authority."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from scripts import goal5840_freeze_attempt04_repair_inputs as prior_freezer


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
BASE_COMMIT = "16fb9523e3688e792ff4083a6600434c75d8c9e6"
PRIOR_REPAIR_AUTHORITY = GOAL_ROOT / "POST_ATTEMPT_04_REPAIR_AUTHORITY.json"
ATTEMPT_05_INCIDENT = GOAL_ROOT / "ATTEMPT_05_ENGINEERING_FAILURE.md"
OUTPUT = GOAL_ROOT / "POST_ATTEMPT_05_REPAIR_AUTHORITY.json"
DOMAIN = b"rtdl.goal5840.post_attempt_05_repair_authority.v1\0"
ATTEMPT_05_INCIDENT_SHA256 = (
    "8bbe23346ea96e11b86c32df163f61c2f2aac1565f9e414fa235316c38ef2fd0"
)

ALLOWED_CHANGED_PATHS = tuple(sorted((
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_05_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_05_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt05_repair_inputs.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
)))
SOURCE_PATHS = tuple(sorted({
    *prior_freezer.SOURCE_PATHS,
    "scripts/goal5840_freeze_attempt05_repair_inputs.py",
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
        for line in _git(
            "ls-files", "--others", "--exclude-standard"
        ).splitlines()
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
        raise RuntimeError("prior repair authority differs from Attempt-05 commit")
    authority = json.loads(current.decode("ascii"))
    _verify_seal(
        authority,
        "authority_sha256",
        prior_freezer.DOMAIN,
        "prior repair authority",
    )
    counts = authority.get("execution_counts_at_repair_freeze")
    if (
        authority.get("schema")
        != "rtdl.goal5840.post_attempt_04_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_04_BEFORE_ATTEMPT_05_GPU_EXECUTION"
        or authority.get("status")
        != (
            "FROZEN_TRIANGLE_STATUS_FLOW_CHECKER_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        )
        or not isinstance(counts, dict)
        or counts.get("formal_runner_processes") != 4
        or counts.get("published_evidence_bundles") != 3
        or counts.get("independently_accepted_per_mode_reports") != 1
        or counts.get("accepted_goal5840_complete_results") != 0
    ):
        raise RuntimeError("prior repair authority contract differs")
    if _changed_paths(prior_freezer.BASE_COMMIT, BASE_COMMIT) != tuple(
        sorted(prior_freezer.ALLOWED_CHANGED_PATHS)
    ):
        raise RuntimeError("Attempt-04 repair commit path set differs")
    rows = authority.get("source_files")
    if not isinstance(rows, list):
        raise RuntimeError("prior repair source inventory is absent")
    observed_paths = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("prior repair source row is malformed")
        source_path = str(row["path"])
        blob = _git_blob(BASE_COMMIT, source_path)
        if (
            source_path in observed_paths
            or row.get("bytes") != len(blob)
            or row.get("sha256") != _sha_bytes(blob)
        ):
            raise RuntimeError(
                f"prior repair source identity differs: {source_path}"
            )
        observed_paths.add(source_path)
    if observed_paths != set(prior_freezer.SOURCE_PATHS):
        raise RuntimeError("prior repair source denominator differs")
    return authority


def _source_rows() -> list[dict[str, object]]:
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"Attempt-05 repair source missing: {relative}")
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
        raise RuntimeError("Attempt-05 source commit is not an ancestor of HEAD")
    changed_paths = _changed_paths(BASE_COMMIT)
    expected_paths = set(ALLOWED_CHANGED_PATHS)
    if not OUTPUT.exists():
        expected_paths.remove(str(OUTPUT.relative_to(ROOT)))
    if set(changed_paths) != expected_paths:
        raise RuntimeError(
            "Attempt-05 repair changed-path set differs: "
            f"observed={changed_paths!r} "
            f"expected={tuple(sorted(expected_paths))!r}"
        )

    prior = _verify_prior_repair_authority()
    incident_bytes = ATTEMPT_05_INCIDENT.read_bytes()
    if _sha_bytes(incident_bytes) != ATTEMPT_05_INCIDENT_SHA256:
        raise RuntimeError("Attempt-05 incident identity differs")
    prior_bytes = PRIOR_REPAIR_AUTHORITY.read_bytes()
    artifacts = [
        {
            "name": "mode_01_capacity_fail_closed_collection_bundle.json",
            "bytes": 1364072,
            "file_sha256": (
                "944f4dd717af365e31ad5d624dbd7ed5a8b71a8e5d6c6304c5336c348b6242c3"
            ),
            "internal_sha256": (
                "1f93c9f763f28b72247b88e048ca50a2d62f1431e32da732dfb59662f8a55531"
            ),
        },
        {
            "name": (
                "mode_01_capacity_fail_closed_collection_independent_check.json"
            ),
            "bytes": 3967,
            "file_sha256": (
                "246a867b35a793439926e65e9791d4874525ba937bb793d9b737b215094439da"
            ),
            "internal_sha256": (
                "aba46744b907f16c44700cd39c14c67b3de3c048217a9c9b02c1bb2a05596b90"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
        },
        {
            "name": "mode_02_all_hit_count_bundle.json",
            "bytes": 806033,
            "file_sha256": (
                "84645793be976b021bea510365d6936a67df056dbc837ed710093ea8ac191645"
            ),
            "internal_sha256": (
                "1818eaa45162b94215060e688639d32e9f0ffde2c521354f955abe6f586e67c7"
            ),
        },
        {
            "name": "mode_02_all_hit_count_independent_check.json",
            "bytes": 3917,
            "file_sha256": (
                "423e6f61672cf91110089c38409e1befee4fb26d506104214580d5d577fe1431"
            ),
            "internal_sha256": (
                "40d760e5932e6e7e66f0e4618a29a32d620c2b8a4b743192065842447c0bb8b7"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
        },
        {
            "name": "mode_03_weighted_hit_count_bundle.json",
            "bytes": 806393,
            "file_sha256": (
                "990eb99867984d959afdd2d65ba804d4813620e74108b3531bd0e8de192b64a4"
            ),
            "internal_sha256": (
                "14de9b974fb0f873899aaa782a4febc9118661a5b6ec0513402bd4149f3203c5"
            ),
        },
        {
            "name": "mode_03_weighted_hit_count_independent_check.json",
            "bytes": 3917,
            "file_sha256": (
                "8c2ee19cfea08ab192f9c0bab89dda9d35383f0044bdcd101785e932753213db"
            ),
            "internal_sha256": (
                "449af0f81b8e434f1fd525ac50bcd485bbe58afe96245397112cb4ea08b3dc87"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
        },
    ]
    result: dict[str, object] = {
        "schema": "rtdl.goal5840.post_attempt_05_repair_authority.v1",
        "goal": 5840,
        "frozen_at_utc": frozen_at_utc,
        "stage": "AFTER_ATTEMPT_05_BEFORE_ATTEMPT_06_GPU_EXECUTION",
        "status": (
            "FROZEN_EXACT_NATIVE_ENVIRONMENT_BINDING_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        ),
        "base_chain": {
            "attempt_05_source_commit": BASE_COMMIT,
            "post_attempt_04_repair_authority": {
                "path": str(PRIOR_REPAIR_AUTHORITY.relative_to(ROOT)),
                "bytes": len(prior_bytes),
                "file_sha256": _sha_bytes(prior_bytes),
                "authority_sha256": prior["authority_sha256"],
            },
            "attempt_05_incident": {
                "path": str(ATTEMPT_05_INCIDENT.relative_to(ROOT)),
                "bytes": len(incident_bytes),
                "file_sha256": ATTEMPT_05_INCIDENT_SHA256,
                "classification": (
                    "SPHERE_RUNTIME_NATIVE_LIBRARY_ENV_BINDING_"
                    "ENGINEERING_FAILURE"
                ),
                "published_failure_artifacts": artifacts,
                "published_failure_bundle_count": 3,
                "published_independent_report_count": 3,
                "independently_accepted_per_mode_report_count": 3,
                "independent_property_pass_count": 15,
                "sphere_optix_launches": 0,
                "published_mutation_applications": 0,
                "accepted_complete_goal5840_results": 0,
            },
            "formal_observed_counts_through_attempt_05": {
                "runner_processes_started": 5,
                "frozen_modes_entered": 9,
                "public_route_expected_outputs_returned": 8,
                "published_evidence_bundles": 6,
                "published_independent_property_reports": 6,
                "independently_accepted_per_mode_reports": 4,
                "published_mutation_applications": 0,
                "accepted_complete_goal5840_results": 0,
            },
            "prior_post_failure_gpu_diagnostics": {
                "diagnostic_processes": 2,
                "diagnostic_mode_executions": 2,
                "accepted_as_evidence": 0,
            },
            "attempt_05_post_failure_gpu_diagnostics": {
                "diagnostic_processes": 0,
                "diagnostic_mode_executions": 0,
                "accepted_as_evidence": 0,
            },
        },
        "repair_scope": {
            "defect": "missing_sphere_runtime_native_library_environment_binding",
            "repair": (
                "fail_closed_exact_native_dso_environment_binding_before_"
                "route_materialization"
            ),
            "allowed_changed_paths": list(ALLOWED_CHANGED_PATHS),
            "exact_changed_paths_since_base": list(ALLOWED_CHANGED_PATHS),
            "absent_matching_and_conflicting_bindings_tested": True,
            "exact_binding_recorded_in_result": True,
            "route_change_allowed": False,
            "fixture_or_oracle_change_allowed": False,
            "declaration_or_control_root_change_allowed": False,
            "property_or_mutation_change_allowed": False,
            "native_engine_or_runtime_change_allowed": False,
            "independent_checker_change_allowed": False,
            "frozen_core_change_allowed": False,
        },
        "preregistration": prior["preregistration"],
        "source_files": _source_rows(),
        "goal5838_frozen_core": prior["goal5838_frozen_core"],
        "route_bundle_group_count": prior["route_bundle_group_count"],
        "required_mode_count": prior["required_mode_count"],
        "mode_cases": prior["mode_cases"],
        "execution_counts_at_repair_freeze": {
            "formal_runner_processes": 5,
            "formal_entered_modes": 9,
            "formal_returned_expected_outputs": 8,
            "prior_gpu_diagnostic_processes": 2,
            "prior_gpu_diagnostic_mode_executions": 2,
            "published_evidence_bundles": 6,
            "published_independent_property_reports": 6,
            "independently_accepted_per_mode_reports": 4,
            "published_mutation_applications": 0,
            "accepted_goal5840_complete_results": 0,
        },
        "claim_boundary": {
            "append_only_engineering_repair_authority": True,
            "five_prior_formal_failures_preserved": True,
            "attempt_05_three_per_mode_acceptances_preserved": True,
            "attempt_05_incomplete_run_not_accepted_as_goal_result": True,
            "diagnostic_processes_not_accepted_as_evidence": True,
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
        raise RuntimeError("stored Attempt-05 repair authority differs")
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
        "accepted_goal5840_complete_results": document[
            "execution_counts_at_repair_freeze"
        ]["accepted_goal5840_complete_results"],
        "output": str(OUTPUT),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
