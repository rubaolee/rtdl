#!/usr/bin/env python3
"""Audit Goal5792 artifact identity, historical schema, and documentation hygiene."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any


PINS = {
    "functional_rc": (
        "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz",
        "50e37b1d4a311bdde40d30392cd9201bc781e5d228d72df4f430b3e12f81955c",
    ),
    "performance_source": (
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz",
        "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
    ),
    "performance_evidence": (
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz",
        "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a",
    ),
    "performance_result": (
        "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json",
        "7f5cd38e625fa62233adfbb9df1f6aa56ebb050999b3154c1604bbc25f4e9064",
    ),
    "clean_linux_result": (
        "history/internal_docs/goal5792_clean_linux_rc_v6_rehearsal_result_20260820.json",
        "1db0a9fb5c3122875a342aaf6d5476f26449740c8ecdc2c08aa0b038788dd16b",
    ),
    "responsibility_v3": (
        "history/internal_docs/goal5792_source_backed_responsibility_audit_result_v3_20260820.json",
        "f4958306576ac3a6a0d182796c067cbd693018cb45318af3b6f77520f982682b",
    ),
    "unknown_preliminary": (
        "history/internal_docs/goal5792_preliminary_source_backed_unknown_lane_classification_20260820.json",
        "2f1030b93fc69834f093090bb513cccc701938590327f85c0c424d51bc7738c3",
    ),
    "design": (
        "docs/v4/restricted_python_optix_callbacks_design.md",
        "fa00ecbb582a185f4767470e386c9e1b3d7995c5bc3c4945dcba883be61ddc9c",
    ),
    "system_plan": (
        "docs/v4/v4_system_design_and_execution_plan.md",
        "9a05c07060d97c59f1829975096cfaf4d77595733409f66fcd422434a56cf6d3",
    ),
    "reproduction": (
        "docs/v4/cgo_artifact_reproduction.md",
        "514e290b61c6df19ae6148524c7c8ff8edea03261f9458a5053dd4ca81226341",
    ),
    "hygiene_v1_predecessor": (
        "history/internal_docs/goal5792_artifact_identity_hygiene_audit_result_20260820.json",
        "7b0720745bcf888d78e218a4b6f3e54c0dce2f060d2b2a59ee13e2b854d2adf9",
    ),
}


EXPECTED_GOAL5776_SCHEMAS = {
    "rtdl.goal5776.registered_row_binding.v1": 590,
    "rtdl.goal5776.real_scale_formal_worker.v1": 464,
    "rtdl.goal5776.combined_behavioral_optix_receipt.v1": 108,
    "rtdl.goal5776.real_scale_data_manifest.v1": 1,
    "rtdl.goal5776.home_derived_formal_runtime_budget.v1": 1,
    "rtdl.goal5776.real_scale_formal_evidence_manifest.v1": 1,
    "rtdl.goal5776.owner_formal_authority.v2": 1,
    "rtdl.goal5776.real_scale_plan.v1": 1,
    "rtdl.goal5776.create_only_target_prepare_result.v1": 1,
    "rtdl.goal5776.real_scale_runtime.v1": 1,
    "rtdl.goal5776.target_real_scale_functional_prepare.v1": 1,
    "rtdl.goal5776.real_scale_formal_controller_receipt.v1": 1,
    "rtdl.goal5776.real_scale_formal_contract.v1": 1,
    "rtdl.goal5776.real_scale_v2_v4_evaluation.v1": 1,
    "rtdl.goal5776.real_scale_v2_v4_final.v1": 1,
    "rtdl.goal5776.real_scale_v2_v4_independent_recount.v1": 1,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return _sha(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8"))


def _walk_schemas(value: Any, counter: Counter[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "schema" and isinstance(item, str) and "goal5776" in item.lower():
                counter[item] += 1
            _walk_schemas(item, counter)
    elif isinstance(value, list):
        for item in value:
            _walk_schemas(item, counter)


def _validate_performance_authority(
    authority: dict[str, Any], embedded_source_sha256: str,
) -> None:
    if type(authority.get("run_goal_id")) is not int or authority["run_goal_id"] != 5785:
        raise RuntimeError("controlling performance authority goal drifted")
    if authority.get("lineage", {}).get("execution_source_sha256") \
            != PINS["performance_source"][1]:
        raise RuntimeError("controlling authority source binding drifted")
    if authority.get("evidence", {}).get("archive_sha256") \
            != PINS["performance_evidence"][1]:
        raise RuntimeError("controlling authority evidence binding drifted")
    if embedded_source_sha256 != PINS["performance_source"][1]:
        raise RuntimeError("evidence-embedded execution source drifted")


def build_result(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pin_rows: dict[str, dict[str, Any]] = {}
    for role, (relative, expected) in PINS.items():
        path = root / relative
        data = path.read_bytes()
        if _sha(data) != expected:
            raise RuntimeError(f"{role} SHA mismatch")
        pin_rows[role] = {"path": relative, "sha256": expected, "bytes": len(data)}

    if PINS["functional_rc"][1] == PINS["performance_source"][1]:
        raise RuntimeError("functional RC and performance source were conflated")

    evidence_path = root / PINS["performance_evidence"][0]
    schemas: Counter[str] = Counter()
    filename_residue: list[str] = []
    json_member_count = 0
    schema_member_count = 0
    embedded_source_digests: list[str] = []
    with tarfile.open(evidence_path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            if member.name == "EXECUTION/EXECUTION_SOURCE.tar.gz":
                handle = archive.extractfile(member)
                if handle is None:
                    raise RuntimeError("unreadable embedded execution source")
                embedded_source_digests.append(_sha(handle.read()))
            if "goal5776" in member.name.lower():
                filename_residue.append(member.name)
            if not member.name.lower().endswith(".json"):
                continue
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable JSON member: {member.name}")
            try:
                value = json.loads(handle.read())
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            json_member_count += 1
            before = sum(schemas.values())
            _walk_schemas(value, schemas)
            if sum(schemas.values()) != before:
                schema_member_count += 1
    if dict(schemas) != EXPECTED_GOAL5776_SCHEMAS:
        raise RuntimeError("historical Goal5776 schema inventory drifted")
    if filename_residue != ["GOAL5776_EVIDENCE_MANIFEST.json"]:
        raise RuntimeError("historical Goal5776 filename inventory drifted")
    if embedded_source_digests != [PINS["performance_source"][1]]:
        raise RuntimeError("embedded execution-source member set or identity drifted")

    performance_authority = json.loads(
        (root / PINS["performance_result"][0]).read_text(encoding="utf-8"))
    if not isinstance(performance_authority, dict):
        raise RuntimeError("controlling performance authority is not an object")
    _validate_performance_authority(performance_authority, embedded_source_digests[0])

    design = (root / PINS["design"][0]).read_text(encoding="utf-8")
    plan = (root / PINS["system_plan"][0]).read_text(encoding="utf-8")
    reproduction = (root / PINS["reproduction"][0]).read_text(encoding="utf-8")
    required = {
        "design_current_evidence": "Current evidence boundary (2026-08-20)",
        "design_theory_boundary": "assume-guarantee compatibility interface",
        "plan_historical_status": "historical program-level design",
        "plan_mixed_result": "Goal5785 later returned a mixed result",
        "reproduction_clean_linux": "unmodified canonical validator has now run successfully",
        "reproduction_schema_lineage": "historical schema labels inside a Goal5785 evidence lineage",
        "reproduction_responsibility_narrowing": "0/6 are fully established",
    }
    combined_by_role = {
        "design": " ".join(design.split()),
        "plan": " ".join(plan.split()),
        "reproduction": " ".join(reproduction.split()),
    }
    role_for = {
        "design_current_evidence": "design",
        "design_theory_boundary": "design",
        "plan_historical_status": "plan",
        "plan_mixed_result": "plan",
        "reproduction_clean_linux": "reproduction",
        "reproduction_schema_lineage": "reproduction",
        "reproduction_responsibility_narrowing": "reproduction",
    }
    for key, phrase in required.items():
        if phrase not in combined_by_role[role_for[key]]:
            raise RuntimeError(f"required hygiene wording absent: {key}")

    result: dict[str, Any] = {
        "schema": "rtdl.goal5792.artifact_identity_hygiene_audit.v2",
        "goal": 5792,
        "status": "PASS__RC_PERFORMANCE_IDENTITY_SEPARATED__HISTORICAL_SCHEMA_RESIDUE_EXPLICIT",
        "pins": pin_rows,
        "identity_separation": {
            "functional_rc_sha256": PINS["functional_rc"][1],
            "performance_source_sha256": PINS["performance_source"][1],
            "performance_evidence_sha256": PINS["performance_evidence"][1],
            "all_three_distinct": len({
                PINS["functional_rc"][1], PINS["performance_source"][1],
                PINS["performance_evidence"][1],
            }) == 3,
            "functional_rc_may_reproduce_goal5785_performance_by_itself": False,
        },
        "outer_performance_authority": {
            "run_goal_id": 5785,
            "authority_file_sha256": PINS["performance_result"][1],
            "authority_binds_standalone_execution_source": True,
            "authority_binds_evidence_archive": True,
            "evidence_embeds_exact_standalone_execution_source": True,
            "embedded_execution_source_member": "EXECUTION/EXECUTION_SOURCE.tar.gz",
            "embedded_execution_source_sha256": embedded_source_digests[0],
        },
        "historical_schema_residue": {
            "outer_authority_goal": 5785,
            "inner_formal_harness_lineage_goal": 5776,
            "filename_residue": filename_residue,
            "goal5776_schema_counts": dict(sorted(schemas.items())),
            "goal5776_schema_occurrence_count": sum(schemas.values()),
            "goal5776_schema_json_member_count": schema_member_count,
            "parsed_json_member_count": json_member_count,
            "frozen_bytes_renamed_or_rewritten": False,
            "wrong_archive_inferred_from_historical_label": False,
        },
        "documentation_hygiene": {
            "plan_only_status_superseded": True,
            "historical_design_preserved": True,
            "mixed_performance_result_disclosed": True,
            "clean_linux_canonical_validation_disclosed": True,
            "responsibility_claim_narrowing_disclosed": True,
            "theory_guarantee_boundary_disclosed": True,
        },
        "claim_boundary": {
            "clean_linux_functional_rc_rehearsed": True,
            "goal5785_performance_reproduced_by_clean_linux_rehearsal": False,
            "historical_goal5776_labels_are_current_goal5792_schemas": False,
            "public_release_or_submission_ready_claimed": False,
        },
        "authorization": {
            "authorizes_gpu_or_pod": False,
            "authorizes_registered_timing": False,
            "authorizes_product_or_native_changes": False,
            "authorizes_publication_or_submission": False,
        },
    }
    result["result_sha256"] = _canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = build_result(Path(args.root))
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({
        "status": result["status"],
        "schema_occurrences": result["historical_schema_residue"]["goal5776_schema_occurrence_count"],
        "schema_members": result["historical_schema_residue"]["goal5776_schema_json_member_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
