#!/usr/bin/env python3
"""Freeze Goal5840's append-only Attempt-06 checker-repair authority."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from scripts import goal5840_freeze_attempt05_repair_inputs as prior_freezer


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
BASE_COMMIT = "593a514637ab2075653bbd4e499c36860519bf31"
PRIOR_REPAIR_AUTHORITY = GOAL_ROOT / "POST_ATTEMPT_05_REPAIR_AUTHORITY.json"
ATTEMPT_06_INCIDENT = GOAL_ROOT / "ATTEMPT_06_ENGINEERING_FAILURE.md"
OUTPUT = GOAL_ROOT / "POST_ATTEMPT_06_REPAIR_AUTHORITY.json"
DOMAIN = b"rtdl.goal5840.post_attempt_06_repair_authority.v1\0"
ATTEMPT_06_INCIDENT_SHA256 = (
    "6cd031390db51cf20f24485de2a4f47d61d38e1d648de17f8c36553398f49e2f"
)

ALLOWED_CHANGED_PATHS = tuple(sorted((
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "ATTEMPT_06_ENGINEERING_FAILURE.md",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "POST_ATTEMPT_06_REPAIR_AUTHORITY.json",
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_attempt06_repair_inputs.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "tests/goal5840_gpu_evidence_harness_test.py",
    "tests/goal5840_gpu_evidence_verifier_test.py",
    "tests/goal5840_independent_target_checker_test.py",
)))
SOURCE_PATHS = tuple(sorted({
    *prior_freezer.SOURCE_PATHS,
    "scripts/goal5840_freeze_attempt06_repair_inputs.py",
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
        raise RuntimeError("prior repair authority differs from Attempt-06 commit")
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
        != "rtdl.goal5840.post_attempt_05_repair_authority.v1"
        or authority.get("stage")
        != "AFTER_ATTEMPT_05_BEFORE_ATTEMPT_06_GPU_EXECUTION"
        or authority.get("status")
        != (
            "FROZEN_EXACT_NATIVE_ENVIRONMENT_BINDING_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        )
        or not isinstance(counts, dict)
        or counts.get("formal_runner_processes") != 5
        or counts.get("published_evidence_bundles") != 6
        or counts.get("independently_accepted_per_mode_reports") != 4
        or counts.get("accepted_goal5840_complete_results") != 0
    ):
        raise RuntimeError("prior repair authority contract differs")
    if _changed_paths(prior_freezer.BASE_COMMIT, BASE_COMMIT) != tuple(
        sorted(prior_freezer.ALLOWED_CHANGED_PATHS)
    ):
        raise RuntimeError("Attempt-05 repair commit path set differs")
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
            raise RuntimeError(f"Attempt-06 repair source missing: {relative}")
        rows.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha_file(path),
        })
    return rows


def _attempt06_artifacts() -> list[dict[str, object]]:
    return [
        {
            "name": "mode_01_capacity_fail_closed_collection_bundle.json",
            "bytes": 1364075,
            "file_sha256": (
                "f259c779347b945229ac545fbe9765adfeff8e2fea9d27f9acc5a6c9251824ca"
            ),
            "internal_sha256": (
                "eba236fdc8b946392e6e45c1eb47d7b5e963278b8cdf0f7918b2b88c0b01ef0e"
            ),
        },
        {
            "name": (
                "mode_01_capacity_fail_closed_collection_independent_check.json"
            ),
            "bytes": 3967,
            "file_sha256": (
                "737cecffb9ccaf95a639e3a815bebec7e581af3ea80ac257714e4e3c67384c45"
            ),
            "internal_sha256": (
                "d76ef08ae8bae5a3c07c919c03238229138402d257a7fc1ede3a027cebac5a77"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
            "property_reject_count": 0,
        },
        {
            "name": "mode_02_all_hit_count_bundle.json",
            "bytes": 806032,
            "file_sha256": (
                "9e6cf9440ddb77724378a5dc3af7182dbc76cc8b8f801be299a197ec96f95712"
            ),
            "internal_sha256": (
                "3420e8f467d2fb18e3a1db6512a882a60ffc83df41ff202a5cfc76bd443c25f9"
            ),
        },
        {
            "name": "mode_02_all_hit_count_independent_check.json",
            "bytes": 3917,
            "file_sha256": (
                "16173ef87f0db27f3e326bbf612eb59d7f21bace48a22c72172d846cecfd4795"
            ),
            "internal_sha256": (
                "4cd4c21b89d668c206c45e98e6f4a92bc636e93680bf08ad9019b2dd628a0a91"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
            "property_reject_count": 0,
        },
        {
            "name": "mode_03_weighted_hit_count_bundle.json",
            "bytes": 806395,
            "file_sha256": (
                "9190d49385a1be87c2a7c27c7c01bfc64b79db841e27f17f348704d4f29bebde"
            ),
            "internal_sha256": (
                "33da537ebb69235d876b82928c573947a2c621e5c36ad26616c46e7a43472095"
            ),
        },
        {
            "name": "mode_03_weighted_hit_count_independent_check.json",
            "bytes": 3917,
            "file_sha256": (
                "e802c7de5d924956e8c5ae0489e12f244bc0e205e38822b86d0ab7b4b337ce7d"
            ),
            "internal_sha256": (
                "6402cad30d6968734cb35909cf5914e62cdc34bd180249785c6b0edd0ef6acd8"
            ),
            "verdict": "ACCEPT",
            "property_pass_count": 5,
            "property_reject_count": 0,
        },
        {
            "name": "mode_04_accept_every_hit_and_continue_bundle.json",
            "bytes": 779946,
            "file_sha256": (
                "275b474bb0f94c55e84cebcf9743daad6c4d80e19418099abbafa59bdcf97319"
            ),
            "internal_sha256": (
                "9aa0a5d6f85a82bda860b11b377e48f4c576cc87727e0462456f1625dda6e3f4"
            ),
        },
        {
            "name": "mode_04_accept_every_hit_and_continue_independent_check.json",
            "bytes": 3552,
            "file_sha256": (
                "edfc176172f213110da7422aa6eefa39d3acc4350d89688c86214aed7519c854"
            ),
            "internal_sha256": (
                "d5932d027e41d1041a3606497940b61bfa703e59cd46899fea014615c8d2da31"
            ),
            "verdict": "REJECT",
            "property_pass_count": 4,
            "property_reject_count": 1,
            "reason_id": "TC005_EXECUTABLE_PREIMAGE_PLAN_MISMATCH",
        },
    ]


def build_authority(frozen_at_utc: str) -> dict[str, object]:
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASE_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
    ).returncode:
        raise RuntimeError("Attempt-06 source commit is not an ancestor of HEAD")
    changed_paths = _changed_paths(BASE_COMMIT)
    expected_paths = set(ALLOWED_CHANGED_PATHS)
    if not OUTPUT.exists():
        expected_paths.remove(str(OUTPUT.relative_to(ROOT)))
    if set(changed_paths) != expected_paths:
        raise RuntimeError(
            "Attempt-06 repair changed-path set differs: "
            f"observed={changed_paths!r} "
            f"expected={tuple(sorted(expected_paths))!r}"
        )

    prior = _verify_prior_repair_authority()
    incident_bytes = ATTEMPT_06_INCIDENT.read_bytes()
    if _sha_bytes(incident_bytes) != ATTEMPT_06_INCIDENT_SHA256:
        raise RuntimeError("Attempt-06 incident identity differs")
    prior_bytes = PRIOR_REPAIR_AUTHORITY.read_bytes()
    result: dict[str, object] = {
        "schema": "rtdl.goal5840.post_attempt_06_repair_authority.v1",
        "goal": 5840,
        "frozen_at_utc": frozen_at_utc,
        "stage": "AFTER_ATTEMPT_06_BEFORE_ATTEMPT_07_GPU_EXECUTION",
        "status": (
            "FROZEN_TWO_LEVEL_PHYSICAL_PLAN_REFINEMENT_CHECKER_REPAIR__"
            "NO_COMPLETE_ACCEPTED_RESULT"
        ),
        "base_chain": {
            "attempt_06_source_commit": BASE_COMMIT,
            "post_attempt_05_repair_authority": {
                "path": str(PRIOR_REPAIR_AUTHORITY.relative_to(ROOT)),
                "bytes": len(prior_bytes),
                "file_sha256": _sha_bytes(prior_bytes),
                "authority_sha256": prior["authority_sha256"],
            },
            "attempt_06_incident": {
                "path": str(ATTEMPT_06_INCIDENT.relative_to(ROOT)),
                "bytes": len(incident_bytes),
                "file_sha256": ATTEMPT_06_INCIDENT_SHA256,
                "classification": (
                    "SPHERE_TWO_LEVEL_PHYSICAL_PLAN_REFINEMENT_"
                    "CHECKER_ENGINEERING_FAILURE"
                ),
                "published_failure_artifacts": _attempt06_artifacts(),
                "published_failure_bundle_count": 4,
                "published_independent_report_count": 4,
                "independently_accepted_per_mode_report_count": 3,
                "independent_property_pass_count": 19,
                "independent_property_reject_count": 1,
                "sphere_optix_launches": 1,
                "published_mutation_applications": 0,
                "accepted_complete_goal5840_results": 0,
            },
            "formal_observed_counts_through_attempt_06": {
                "runner_processes_started": 6,
                "frozen_modes_entered": 13,
                "public_route_expected_outputs_returned": 12,
                "published_evidence_bundles": 10,
                "published_independent_property_reports": 10,
                "independently_accepted_per_mode_reports": 7,
                "published_mutation_applications": 0,
                "accepted_complete_goal5840_results": 0,
            },
            "prior_post_failure_gpu_diagnostics": {
                "diagnostic_processes": 2,
                "diagnostic_mode_executions": 2,
                "accepted_as_evidence": 0,
            },
            "attempt_06_post_failure_gpu_diagnostics": {
                "diagnostic_processes": 0,
                "diagnostic_mode_executions": 0,
                "accepted_as_evidence": 0,
            },
        },
        "repair_scope": {
            "defect": (
                "sphere_inner_physical_plan_was_incorrectly_compared_to_"
                "outer_family_plan"
            ),
            "repair": (
                "independently_derive_target_bound_inner_physical_plan_from_"
                "existing_outer_commitments_and_compare_exactly"
            ),
            "allowed_changed_paths": list(ALLOWED_CHANGED_PATHS),
            "exact_changed_paths_since_base": list(ALLOWED_CHANGED_PATHS),
            "existing_bundle_fields_only": True,
            "physical_schema_authority_cross_binding_required": True,
            "runtime_authority_nonce_cross_binding_required": True,
            "adversarial_bridge_input_mutations_required": True,
            "direct_inner_outer_plan_equality_forbidden": True,
            "unverified_provider_emitted_bridge_forbidden": True,
            "independent_checker_change_allowed": True,
            "capture_and_final_verifier_chain_change_allowed": True,
            "route_change_allowed": False,
            "fixture_or_oracle_change_allowed": False,
            "declaration_or_control_root_change_allowed": False,
            "property_or_preregistered_mutation_change_allowed": False,
            "native_engine_or_runtime_change_allowed": False,
            "provider_or_compiler_codegen_change_allowed": False,
            "target_evidence_bundle_schema_change_allowed": False,
            "frozen_core_change_allowed": False,
        },
        "preregistration": prior["preregistration"],
        "source_files": _source_rows(),
        "goal5838_frozen_core": prior["goal5838_frozen_core"],
        "route_bundle_group_count": prior["route_bundle_group_count"],
        "required_mode_count": prior["required_mode_count"],
        "mode_cases": prior["mode_cases"],
        "execution_counts_at_repair_freeze": {
            "formal_runner_processes": 6,
            "formal_entered_modes": 13,
            "formal_returned_expected_outputs": 12,
            "prior_gpu_diagnostic_processes": 2,
            "prior_gpu_diagnostic_mode_executions": 2,
            "published_evidence_bundles": 10,
            "published_independent_property_reports": 10,
            "independently_accepted_per_mode_reports": 7,
            "published_mutation_applications": 0,
            "accepted_goal5840_complete_results": 0,
        },
        "claim_boundary": {
            "append_only_engineering_repair_authority": True,
            "six_prior_formal_failures_preserved": True,
            "attempt_06_three_per_mode_acceptances_preserved": True,
            "attempt_06_sphere_true_optix_launch_preserved": True,
            "attempt_06_incomplete_run_not_accepted_as_goal_result": True,
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
        raise RuntimeError("stored Attempt-06 repair authority differs")
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
