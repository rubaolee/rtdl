#!/usr/bin/env python3
"""Freeze Goal5791 preregistration and Stage-A pretarget authority.

Both outputs are CPU/static, create-only, and explicitly non-executable.  The
pretarget authority rehashes and semantically validates all five frozen input
authorities but leaves the target materialization slot null.  A target prepare
may later create an append-only postprepare successor by filling that one slot;
this helper never creates either target or owner-formal authorization.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import goal5791_formal_contract as contract


AUTHORITY_PATHS = {
    "source_authority": (
        "history/internal_docs/"
        "goal5791_successor_source_authority_v2_20260817.json"
    ),
    "data_authority": (
        "history/internal_docs/"
        "goal5791_frozen_triangle_data_and_oracle_authority_20260817.json"
    ),
    "runtime_budget_authority": (
        "history/internal_docs/"
        "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
    ),
    "expected_value_authority": (
        "history/internal_docs/"
        "goal5790_preregistered_expected_value_and_fallback_20260816.json"
    ),
    "citation_authority": (
        "history/internal_docs/"
        "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
    ),
}


def _write_create_only(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def _record(path: Path, relative: str) -> dict[str, object]:
    return {
        # ``history`` is a Windows junction in the author workspace.  Preserve
        # the registered lexical repository path instead of resolving it onto
        # another drive and then attempting an invalid ``relative_to``.
        "path": relative,
        "sha256": contract.file_sha256(path),
        "bytes": path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--preregistration-output", type=Path, required=True)
    parser.add_argument("--authority-output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repository_root.resolve()
    if args.preregistration_output.resolve() == args.authority_output.resolve():
        raise ValueError("Goal5791 outputs must be distinct")
    paths = {
        role: root / Path(*relative.split("/"))
        for role, relative in AUTHORITY_PATHS.items()
    }
    if any(not path.is_file() for path in paths.values()):
        raise FileNotFoundError("Goal5791 authority input is absent")
    contract.validate_source_authority(paths["source_authority"])
    data = contract.validate_data_authority(paths["data_authority"])
    contract.validate_runtime_budget_authority(
        paths["runtime_budget_authority"])
    contract.validate_expected_value_authority(
        paths["expected_value_authority"])
    contract.validate_citation_authority(paths["citation_authority"])

    preregistration_body = {
        "schema": "rtdl.goal5791.preregistration.v1",
        "goal": 5791,
        "status": "FROZEN_PRETARGET__NOT_EXECUTION_AUTHORITY",
        "formal_contract_source_path": "scripts/goal5791_formal_contract.py",
        "formal_contract_source_sha256": contract.file_sha256(
            root / "scripts/goal5791_formal_contract.py"),
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "formal_contract": contract.contract_document(),
        "schedule": contract.schedule_document(),
        "target_derived_values_present": False,
        "goal5791_target_timing_observed": False,
        "formal_worker_count_executed": 0,
        "registered_performance_timing_count": 0,
        "authorizes_pod": False,
        "authorizes_target_prepare": False,
        "authorizes_formal_worker_zero": False,
        "authorizes_registered_timing": False,
    }
    preregistration = {
        **preregistration_body,
        "preregistration_sha256": contract.digest(preregistration_body),
    }
    _write_create_only(args.preregistration_output, preregistration)

    records = {
        role: _record(path, AUTHORITY_PATHS[role])
        for role, path in paths.items()
    }
    authority_body = {
        "schema": contract.PREEXECUTION_AUTHORITY_SCHEMA,
        "goal": 5791,
        "status": contract.PRETARGET_STATUS,
        "formal_contract_sha256": contract.contract_sha256(),
        "schedule_sha256": contract.schedule_sha256(),
        "authority_records": records,
        "dataset_input_sha256": {
            dataset_id: data["datasets"][dataset_id]["sha256"]
            for dataset_id in contract.DATASET_IDS
        },
        "oracle_authority_sha256": {
            dataset_id: data["datasets"][dataset_id][
                "oracle_authority_sha256"]
            for dataset_id in contract.DATASET_IDS
        },
        "target_materialization_binding": None,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "authorization": {
            "authorizes_pod": False,
            "authorizes_target_prepare": False,
            "authorizes_formal_workers": False,
            "authorizes_registered_timing": False,
        },
    }
    authority = {
        **authority_body,
        "authority_sha256": contract.digest(authority_body),
    }
    _write_create_only(args.authority_output, authority)
    # In the author Windows workspace ``history`` is a junction to the same
    # repository-shaped tree on D:.  The shared loader intentionally resolves
    # paths before its containment check, so validate against the resolved
    # repository root there.  A clean archive has no junction and uses *root*.
    resolved_history = (root / "history").resolve()
    validation_root = (
        resolved_history.parent
        if resolved_history != (root / "history") else root
    )
    contract.load_preexecution_authority(
        args.authority_output,
        repository_root=validation_root,
        require_target_binding=False,
    )
    print(json.dumps({
        "status": "PASS__PRETARGET_ONLY__NO_EXECUTION_AUTHORITY",
        "preregistration": str(args.preregistration_output),
        "preregistration_file_sha256": contract.file_sha256(
            args.preregistration_output),
        "preregistration_sha256": preregistration[
            "preregistration_sha256"],
        "preexecution_authority": str(args.authority_output),
        "preexecution_authority_file_sha256": contract.file_sha256(
            args.authority_output),
        "preexecution_authority_sha256": authority["authority_sha256"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
