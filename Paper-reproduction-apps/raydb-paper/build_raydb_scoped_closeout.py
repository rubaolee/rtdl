#!/usr/bin/env python3
"""Build the fail-closed RayDB scoped reproduction closeout artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from author_source_policy import validate_author_source_identity


QUERY_IDS = (
    "q11", "q12", "q13", "q21", "q22", "q23", "q31",
    "q32", "q33", "q34", "q41", "q42", "q43",
)
AUTHOR_LAUNCH_PATTERN = re.compile(r"\[Time\] Launch: (?P<launch>[0-9.]+) ms")
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
COHORT_SCHEMA = "rtdl.paper_reproduction.execution_cohort.v1"
BUILD_SCHEMA = "rtdl.paper_reproduction.raydb.ssb_single_query_packet_build.v1"
AUTHOR_SCHEMA = "rtdl.paper_reproduction.raydb.author_packet_gate.v2"
RTDL_SCHEMA = "rtdl.paper_reproduction.raydb.ssb_packet_rtdl_gate.v3"


def _load(path: Path) -> dict[str, Any]:
    return _load_json_bytes(path.read_bytes(), label=str(path))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load_json_bytes(raw: bytes, *, label: str) -> dict[str, Any]:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label} contains duplicate JSON key {key!r}")
            result[key] = value
        return result

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    _require(isinstance(value, dict), f"{label} must contain a JSON object")
    return value


def _strict_json_int(value: object, *, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact JSON integer")
    if value < INT64_MIN or value > INT64_MAX:
        raise OverflowError(f"{label} is outside signed int64")
    return value


def _strict_rows(
    payload: dict[str, Any], key: str, *, expected_group_arity: int
) -> list[tuple[tuple[int, ...], int]]:
    raw_rows = payload.get(key)
    _require(isinstance(raw_rows, list), f"{key} must be a JSON row list")
    rows: list[tuple[tuple[int, ...], int]] = []
    groups: set[tuple[int, ...]] = set()
    for index, row in enumerate(raw_rows):
        _require(isinstance(row, dict), f"{key}[{index}] must be an object")
        group_values = row.get("group")
        _require(isinstance(group_values, list), f"{key}[{index}].group must be a list")
        _require(
            len(group_values) == expected_group_arity,
            f"{key}[{index}] group arity mismatch",
        )
        group = tuple(
            _strict_json_int(value, label=f"{key}[{index}].group")
            for value in group_values
        )
        _require(group not in groups, f"{key} contains duplicate group {group!r}")
        groups.add(group)
        rows.append(
            (group, _strict_json_int(row.get("value"), label=f"{key}[{index}].value"))
        )
    return sorted(rows)


def _normalized_archive_name(name: str) -> str:
    _require("\\" not in name, "archive members must use POSIX separators")
    path = PurePosixPath(name)
    _require(not path.is_absolute(), f"unsafe absolute archive member: {name}")
    _require(".." not in path.parts, f"unsafe parent archive member: {name}")
    normalized = "/".join(part for part in path.parts if part not in ("", "."))
    _require(bool(normalized), f"empty archive member: {name}")
    return normalized


def _read_child_archive(path: Path) -> dict[str, tuple[dict[str, Any], str]]:
    records: dict[str, tuple[dict[str, Any], str]] = {}
    with tarfile.open(path, mode="r:gz") as archive:
        for member in archive.getmembers():
            if member.isdir():
                if member.name not in (".", "./"):
                    _normalized_archive_name(member.name)
                continue
            _require(member.isfile(), f"archive contains non-regular member: {member.name}")
            name = _normalized_archive_name(member.name)
            _require(name.endswith(".json"), f"archive contains non-JSON member: {name}")
            _require(name not in records, f"archive contains duplicate member: {name}")
            _require(member.size <= 64 * 1024 * 1024, f"archive member too large: {name}")
            stream = archive.extractfile(member)
            _require(stream is not None, f"cannot read archive member: {name}")
            raw = stream.read()
            _require(len(raw) == member.size, f"archive member size mismatch: {name}")
            records[name] = (
                _load_json_bytes(raw, label=name),
                hashlib.sha256(raw).hexdigest(),
            )
    return records


def _audit_child_archive(
    archive_path: Path,
    matrix: dict[str, Any],
    *,
    scale_factor: int,
    compatibility_patch_path: Path,
) -> dict[str, Any]:
    records = _read_child_archive(archive_path)
    _require(len(records) == 40, f"SF{scale_factor} archive must contain 40 JSON files")
    cohort_records: list[tuple[str, dict[str, Any], str]] = []
    by_schema: dict[str, dict[str, tuple[dict[str, Any], str]]] = {
        BUILD_SCHEMA: {},
        AUTHOR_SCHEMA: {},
        RTDL_SCHEMA: {},
    }
    for name, (payload, digest) in records.items():
        schema = payload.get("schema")
        if schema == COHORT_SCHEMA:
            cohort_records.append((name, payload, digest))
            continue
        _require(schema in by_schema, f"unexpected archive schema in {name}: {schema!r}")
        query_id = payload.get("query_id")
        _require(query_id in QUERY_IDS, f"unexpected query id in {name}: {query_id!r}")
        _require(query_id not in by_schema[schema], f"duplicate {schema} record for {query_id}")
        by_schema[schema][query_id] = (payload, digest)
    _require(len(cohort_records) == 1, "archive must contain exactly one cohort record")
    for schema, values in by_schema.items():
        _require(set(values) == set(QUERY_IDS), f"archive query set mismatch for {schema}")

    cohort_name, cohort, cohort_digest = cohort_records[0]
    _require(cohort == matrix.get("execution_identity"), "archive cohort differs from matrix")
    cases = {case.get("query_id"): case for case in matrix.get("cases", [])}
    _require(set(cases) == set(QUERY_IDS), "matrix case set is not canonical")
    source_identities: list[dict[str, Any]] = []
    total_rows = 0
    for query_id in QUERY_IDS:
        case = cases[query_id]
        bundle = case.get("evidence_bundle", {})
        build, build_digest = by_schema[BUILD_SCHEMA][query_id]
        author, author_digest = by_schema[AUTHOR_SCHEMA][query_id]
        rtdl, rtdl_digest = by_schema[RTDL_SCHEMA][query_id]
        _require(build_digest == bundle.get("build_result_sha256"), f"{query_id} build SHA")
        _require(author_digest == bundle.get("author_result_sha256"), f"{query_id} author SHA")
        _require(rtdl_digest == bundle.get("rtdl_result_sha256"), f"{query_id} RTDL SHA")
        packet = build.get("packet")
        _require(isinstance(packet, dict), f"{query_id} build lacks packet object")
        arity = _strict_json_int(
            packet.get("group_dimension_count"),
            label=f"{query_id}.packet.group_dimension_count",
        )
        _require(arity >= 0, f"{query_id} group arity must be nonnegative")
        expected_rows = _strict_rows(packet, "expected_rows", expected_group_arity=arity)
        author_rows = _strict_rows(author, "author_rows", expected_group_arity=arity)
        rtdl_rows = _strict_rows(rtdl, "rtdl_rows", expected_group_arity=arity)
        _require(
            expected_rows == author_rows == rtdl_rows,
            f"{query_id} archived complete grouped rows differ",
        )
        total_rows += len(expected_rows)
        for hash_name in ("data_sha256", "predicate_sha256", "expected_rows_sha256"):
            expected_hash = bundle.get(hash_name)
            _require(packet.get(hash_name) == expected_hash, f"{query_id} packet {hash_name}")
            _require(author.get(hash_name) == expected_hash, f"{query_id} author {hash_name}")
            _require(rtdl.get(hash_name) == expected_hash, f"{query_id} RTDL {hash_name}")
        _require(
            author.get("packet_json_sha256") == bundle.get("packet_json_sha256"),
            f"{query_id} author packet JSON SHA",
        )
        _require(
            rtdl.get("packet_json_sha256") == bundle.get("packet_json_sha256"),
            f"{query_id} RTDL packet JSON SHA",
        )
        _require(
            rtdl.get("author_result_sha256") == bundle.get("author_result_sha256"),
            f"{query_id} RTDL author-result SHA",
        )
        expected_child_identity = {
            "evidence_cohort_id": cohort["evidence_cohort_id"],
            "host": cohort["host"],
            "gpu_identity": cohort["gpu_identity"],
            "matrix_runner_sha256": cohort["matrix_runner_sha256"],
        }
        _require(
            author.get("execution_identity") == expected_child_identity,
            f"{query_id} author child identity",
        )
        _require(
            rtdl.get("execution_identity") == expected_child_identity,
            f"{query_id} RTDL child identity",
        )
        source_identity = author.get("author_source_identity")
        _require(isinstance(source_identity, dict), f"{query_id} author source identity")
        _require(
            source_identity == bundle.get("author_source_identity"),
            f"{query_id} source identity differs from matrix bundle",
        )
        validate_author_source_identity(
            source_identity,
            compatibility_patch_path=compatibility_patch_path,
        )
        source_identities.append(source_identity)

    canonical_sources = {
        json.dumps(value, sort_keys=True, separators=(",", ":"))
        for value in source_identities
    }
    _require(len(canonical_sources) == 1, "author source identity differs across cases")
    return {
        "schema": "rtdl.paper_reproduction.raydb.child_archive_audit.v2",
        "scale_factor": scale_factor,
        "archive_sha256": _sha256(archive_path),
        "member_count": len(records),
        "cohort_member": cohort_name,
        "cohort_member_sha256": cohort_digest,
        "query_count": len(QUERY_IDS),
        "complete_grouped_row_count": total_rows,
        "all_complete_grouped_rows_equal": True,
        "strict_json_integer_admission": True,
        "unique_group_keys": True,
        "author_source_identity_posthoc_audited": True,
        "author_source_identity_matches_pinned_policy": True,
        "author_source_identity_execution_cohort_locked": False,
        "compatibility_patch_sha256": _sha256(compatibility_patch_path),
        "author_source_identity": source_identities[0],
    }


def _validate_provenance(value: dict[str, Any], scale_factor: int) -> None:
    _require(
        value.get("schema")
        == "rtdl.paper_reproduction.raydb.ssb_generated_dataset_provenance.v1",
        f"SF{scale_factor} dataset provenance schema mismatch",
    )
    _require(value.get("scale_factor") == scale_factor, "dataset scale mismatch")
    boundary = value.get("claim_boundary", {})
    _require(boundary.get("deterministic_generated_same_source_claimed") is True,
             "generated same-source provenance is required")
    for key in (
        "exact_paper_input_claimed",
        "paper_dataset_hash_claimed",
        "exact_paper_dataset_claimed",
    ):
        _require(boundary.get(key) is False, f"forbidden provenance claim: {key}")
    _require(value.get("dbgen_checkout_clean") is True, "dbgen checkout must be clean")


def _validate_matrix(value: dict[str, Any], scale_factor: int) -> None:
    _require(
        value.get("schema")
        == "rtdl.paper_reproduction.raydb.generated_ssb_partitioned_matrix.v3",
        f"SF{scale_factor} matrix schema mismatch",
    )
    _require(value.get("scale_factor") == scale_factor, "matrix scale mismatch")
    _require(value.get("requested_query_ids") == list(QUERY_IDS),
             "matrix must request the canonical 13-query sequence")
    _require(value.get("completed_query_ids") == list(QUERY_IDS),
             "matrix must complete the canonical 13-query sequence")
    _require(value.get("all_requested_queries_passed") is True,
             "all requested queries must pass")
    cases = value.get("cases")
    _require(isinstance(cases, list) and len(cases) == len(QUERY_IDS),
             "matrix must contain exactly 13 cases")
    for expected_query_id, case in zip(QUERY_IDS, cases, strict=True):
        _require(case.get("query_id") == expected_query_id,
                 f"unexpected query order at {expected_query_id}")
        for key in (
            "passed",
            "same_packet_hashes",
            "same_case_identity",
            "dataset_provenance_verified",
            "partition_evidence_verified",
            "primitive_value_derivation_verified",
            "evidence_schema_verified",
            "author_execution_identity_verified",
            "rtdl_execution_identity_verified",
            "same_execution_cohort_verified",
            "timing_evidence_verified",
            "author_matches_oracle",
            "rtdl_matches_oracle",
            "complete_grouped_rows_equal",
        ):
            _require(case.get(key) is True, f"{expected_query_id} failed gate {key}")
    boundary = value.get("claim_boundary", {})
    for key in (
        "exact_paper_input_claimed",
        "figure12_reproduced",
        "paper_performance_claimed",
        "author_rtdl_performance_ratio_authorized",
        "author_algorithm_equivalence_claimed",
    ):
        _require(boundary.get(key) is False, f"forbidden matrix claim: {key}")


def _validate_phase(value: dict[str, Any], scale_factor: int) -> None:
    _require(
        value.get("schema")
        == "rtdl.paper_reproduction.raydb.ssb_partitioned_phase_matrix.v2",
        f"SF{scale_factor} phase schema mismatch",
    )
    _require(value.get("scale_factor") == scale_factor, "phase scale mismatch")
    _require(value.get("query_count") == len(QUERY_IDS), "phase query count mismatch")
    _require(value.get("all_correctness_and_identity_gates_passed") is True,
             "phase matrix must preserve all correctness and identity gates")
    cases = value.get("cases")
    _require(isinstance(cases, list) and len(cases) == len(QUERY_IDS),
             "phase matrix must contain exactly 13 cases")
    _require([case.get("query_id") for case in cases] == list(QUERY_IDS),
             "phase matrix query order mismatch")
    boundary = value.get("claim_boundary", {})
    for key in (
        "exact_paper_input_claimed",
        "author_algorithm_equivalence_claimed",
        "figure12_reproduced",
        "full_paper_reproduction_claimed",
    ):
        _require(boundary.get(key) is False, f"forbidden phase claim: {key}")
    _require(
        value.get("launch_only_summary", {}).get(
            "cross_query_aggregate_speedup_authorized"
        ) is False,
        "cross-query aggregate speedup must remain unauthorized",
    )


def _validate_hardware_gate(value: dict[str, Any]) -> None:
    _require(
        value.get("schema") == "rtdl.generic.partitioned_grouped_i64_hardware_gate.v5",
        "hardware gate schema mismatch",
    )
    _require(value.get("overall_passed") is True, "generic hardware gate failed")
    checks = value.get("partition_contract_checks", {})
    _require(checks.get("observed_tail_primitive_count") == 1,
             "hardware discriminator must report a one-row tail")
    _require(checks.get("observed_total_primitive_count") == 3,
             "hardware discriminator must report three total primitives")
    _require(value.get("claim_boundary", {}).get("app_specific_semantics_claimed") is False,
             "generic hardware gate must remain app-neutral")


def _scale_summary(
    matrix: dict[str, Any],
    phase: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    phase_summary = phase.get("launch_only_summary", {})
    return {
        "scale_factor": matrix["scale_factor"],
        "lineorder_row_count": provenance["lineorder_row_count"],
        "query_count": len(matrix["cases"]),
        "matched_query_count": sum(bool(case["passed"]) for case in matrix["cases"]),
        "complete_grouped_rows_equal": all(
            case["complete_grouped_rows_equal"] for case in matrix["cases"]
        ),
        "partition_rows": matrix["partition_rows"],
        "partition_count_range": [
            min(case["partition_count"] for case in matrix["cases"]),
            max(case["partition_count"] for case in matrix["cases"]),
        ],
        "same_execution_cohort": all(
            case["same_execution_cohort_verified"] for case in matrix["cases"]
        ),
        "author_launch_median_ms": phase_summary.get("author_launch_median_ms"),
        "rtdl_partitioned_launch_sum_median_ms": phase_summary.get(
            "rtdl_partitioned_launch_sum_median_ms"
        ),
        "median_per_query_author_over_rtdl_launch_ratio": phase_summary.get(
            "per_query_author_over_rtdl_ratio_median"
        ),
        "launch_topology_aligned": all(
            case.get("same_launch_topology") is True for case in phase["cases"]
        ),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    inputs = {
        "author_compatibility_patch": args.author_compatibility_patch,
        "generic_hardware_gate": args.generic_hardware_gate,
        "sf10_provenance": args.sf10_provenance,
        "sf10_matrix": args.sf10_matrix,
        "sf10_phase": args.sf10_phase,
        "sf10_child_archive": args.sf10_child_archive,
        "sf10_monolithic_q11": args.sf10_monolithic_q11,
        "sf10_monolithic_q11_author": args.sf10_monolithic_q11_author,
        "sf20_provenance": args.sf20_provenance,
        "sf20_matrix": args.sf20_matrix,
        "sf20_phase": args.sf20_phase,
        "sf20_child_archive": args.sf20_child_archive,
    }
    loaded = {
        name: _load(path)
        for name, path in inputs.items()
        if not name.endswith("_child_archive") and name != "author_compatibility_patch"
    }
    _validate_hardware_gate(loaded["generic_hardware_gate"])
    for scale in (10, 20):
        _validate_provenance(loaded[f"sf{scale}_provenance"], scale)
        _validate_matrix(loaded[f"sf{scale}_matrix"], scale)
        _validate_phase(loaded[f"sf{scale}_phase"], scale)
        _require(
            loaded[f"sf{scale}_matrix"].get("dataset_provenance_sha256")
            == _sha256(inputs[f"sf{scale}_provenance"]),
            f"SF{scale} matrix does not bind the supplied provenance file",
        )
        _require(
            loaded[f"sf{scale}_matrix"].get("execution_identity")
            == loaded[f"sf{scale}_phase"].get("execution_identity"),
            f"SF{scale} correctness and phase matrices use different execution identities",
        )
    archive_audits = {
        f"sf{scale}": _audit_child_archive(
            inputs[f"sf{scale}_child_archive"],
            loaded[f"sf{scale}_matrix"],
            scale_factor=scale,
            compatibility_patch_path=inputs["author_compatibility_patch"],
        )
        for scale in (10, 20)
    }
    monolithic = loaded["sf10_monolithic_q11"]
    _require(monolithic.get("all_requested_queries_passed") is True,
             "SF10 q11 monolithic capacity gate failed")
    _require(monolithic.get("requested_query_ids") == ["q11"],
             "monolithic capacity gate must be q11-only")
    mono_case = monolithic["cases"][0]
    _require(mono_case.get("partition_count") == 1, "q11 gate is not monolithic")
    _require(mono_case.get("complete_grouped_rows_equal") is True,
             "q11 monolithic grouped rows mismatch")
    mono_author = loaded["sf10_monolithic_q11_author"]
    _require(mono_author.get("query_id") == "q11", "monolithic author case mismatch")
    _require(mono_author.get("author_matches_cpu_oracle") is True,
             "monolithic author result does not match the oracle")
    mono_bundle = mono_case.get("evidence_bundle", {})
    _require(
        _sha256(inputs["sf10_monolithic_q11_author"])
        == mono_bundle.get("author_result_sha256"),
        "monolithic author JSON does not match the capacity matrix bundle",
    )
    _require(
        mono_author.get("packet_json_sha256") == mono_bundle.get("packet_json_sha256"),
        "monolithic author packet identity mismatch",
    )
    _require(
        mono_author.get("execution_identity")
        == {
            "evidence_cohort_id": mono_bundle["execution_identity"]["evidence_cohort_id"],
            "host": mono_bundle["execution_identity"]["host"],
            "gpu_identity": mono_bundle["execution_identity"]["gpu_identity"],
            "matrix_runner_sha256": mono_bundle["execution_identity"]["matrix_runner_sha256"],
        },
        "monolithic author execution identity mismatch",
    )
    _require(
        mono_author.get("author_source_identity") == mono_bundle.get("author_source_identity"),
        "monolithic author source identity mismatch",
    )
    validate_author_source_identity(
        mono_author.get("author_source_identity"),
        compatibility_patch_path=inputs["author_compatibility_patch"],
    )
    author_launch_match = AUTHOR_LAUNCH_PATTERN.search(str(mono_author.get("raw_stdout", "")))
    _require(author_launch_match is not None, "monolithic author launch timing missing")

    return {
        "schema": "rtdl.paper_reproduction.raydb.scoped_closeout.v3",
        "status": "scoped_generated_ssb_correctness_and_system_extraction_complete",
        "paper_app": "RayDB",
        "query_ids": list(QUERY_IDS),
        "system_capability": {
            "contract": "generic_partitioned_ray_triangle_grouped_i64_reduction_3d_v2",
            "generic_hardware_gate_passed": True,
            "grouped_reductions": ["count", "sum", "min", "max", "sum_count"],
            "partition_contract": "exact contiguous primitive-id coverage with bounded live scene",
            "app_specific_semantics_in_core": False,
        },
        "scales": [
            _scale_summary(
                loaded["sf10_matrix"], loaded["sf10_phase"], loaded["sf10_provenance"]
            ),
            _scale_summary(
                loaded["sf20_matrix"], loaded["sf20_phase"], loaded["sf20_provenance"]
            ),
        ],
        "archive_audits": archive_audits,
        "source_identity_boundary": {
            "future_execution_cohort_schema": "rtdl.paper_reproduction.execution_cohort.v2",
            "current_source_identity_audited_from_every_author_child": True,
            "current_source_identity_matches_pinned_policy": True,
            "current_source_identity_locked_in_original_execution_cohort": False,
            "compatibility_patch_sha256": _sha256(
                inputs["author_compatibility_patch"]
            ),
        },
        "sf10_q11_monolithic_capacity": {
            "row_count": mono_case["row_count"],
            "complete_grouped_rows_equal": True,
            "author_launch_ms": float(author_launch_match.group("launch")),
            "rtdl_launch_ms": 1000.0 * mono_case["phase_timing_seconds"]["launch"],
            "rtdl_route_total_seconds": mono_case["phase_timing_seconds"][
                "route_total_including_partition_triangle_pack"
            ],
            "app_lowering_seconds": mono_case["phase_timing_seconds"]["app_lowering"],
            "scope": "single-query launch-topology diagnostic, not a paper ratio",
        },
        "evidence": {
            name: {"path": path.as_posix(), "sha256": _sha256(path)}
            for name, path in inputs.items()
        },
        "claim_boundary": {
            "deterministic_generated_same_source_ssb_claimed": True,
            "same_packet_author_oracle_rtdl_complete_grouped_rows_claimed": True,
            "sf10_all_13_queries_claimed": True,
            "sf20_all_13_queries_claimed": True,
            "generic_signed_i64_partition_capability_claimed": True,
            "exact_paper_input_claimed": False,
            "figure12_reproduced": False,
            "paper_modified_crystal_reproduced": False,
            "paper_hardware_reproduced": False,
            "paper_performance_claimed": False,
            "cross_query_aggregate_speedup_claimed": False,
            "whole_program_ratio_authorized": False,
            "author_algorithm_equivalence_claimed": False,
            "zero_copy_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-compatibility-patch", type=Path, required=True)
    parser.add_argument("--generic-hardware-gate", type=Path, required=True)
    parser.add_argument("--sf10-provenance", type=Path, required=True)
    parser.add_argument("--sf10-matrix", type=Path, required=True)
    parser.add_argument("--sf10-phase", type=Path, required=True)
    parser.add_argument("--sf10-child-archive", type=Path, required=True)
    parser.add_argument("--sf10-monolithic-q11", type=Path, required=True)
    parser.add_argument("--sf10-monolithic-q11-author", type=Path, required=True)
    parser.add_argument("--sf20-provenance", type=Path, required=True)
    parser.add_argument("--sf20-matrix", type=Path, required=True)
    parser.add_argument("--sf20-phase", type=Path, required=True)
    parser.add_argument("--sf20-child-archive", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = build(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
