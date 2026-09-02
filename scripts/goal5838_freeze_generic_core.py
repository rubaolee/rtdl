#!/usr/bin/env python3
"""Freeze the Goal5838 generic family core before challenge revelation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "history/internal_docs/goal5838_generic_core_exam_20260902"
TABLE_PATH = OUT_DIR / "CHALLENGE_TABLE.json"
SEAL_PATH = OUT_DIR / "GENERIC_CORE_SEAL.json"
PROTOCOL_PATH = OUT_DIR / "CHALLENGE_SELECTION_PROTOCOL.md"
PREREGISTRATION_PATH = OUT_DIR / "GOAL5838_PREREGISTRATION.json"
SELECTION_CLIENT_PATH = ROOT / "scripts/goal5838_select_challenge.py"
CALIBRATION_PATH = OUT_DIR / "NIST_PRETARGET_CALIBRATION.json"
CALIBRATION_CERTIFICATE_PATH = OUT_DIR / "NIST_PRETARGET_CERTIFICATE.pem"

CORE_FILES = (
    "src/rtdsl/v4_family_schema.py",
    "src/rtdsl/v4_generic_family_lifecycle.py",
    "src/rtdsl/v4_family.py",
)
MIGRATION_FILES = (
    "src/rtdsl/v4_family_route_adapters.py",
    "tests/fixtures/goal5838_external_provider.py",
    "tests/goal5838_generic_family_lifecycle_test.py",
    "tests/goal5838_family_route_migration_test.py",
)

TARGET_TIMESTAMP = "2026-09-02T19:00:00.000Z"
TARGET_TIMESTAMP_MS = 1_788_375_600_000
TARGET_PULSE_URI = (
    "https://beacon.nist.gov/beacon/2.0/pulse/time/1788375600000"
)
PREVIOUS_PULSE_URI = (
    "https://beacon.nist.gov/beacon/2.0/pulse/time/1788375540000"
)
PINNED_CERTIFICATE_ID = (
    "528943a555f5f8ca54423be6dfb95925a35c7b552046420e7d7cd072058a14d6"
    "536ad3a8e9754b6582f164a90b0cd86a65d659f5426a2659a947595d1c816c8c"
)

PRIMITIVES = (
    {
        "primitive_id": "builtin_round_linear_curve",
        "graph_node_kind": "builtin",
        "geometry_contract": "optix.builtin_round_linear_curve.v1",
        "geometry_roles": [],
        "capabilities": ["builtin_round_linear_curve_intersection"],
    },
    {
        "primitive_id": "builtin_sphere",
        "graph_node_kind": "builtin",
        "geometry_contract": "optix.builtin_sphere.v1",
        "geometry_roles": [],
        "capabilities": ["builtin_sphere_intersection"],
    },
    {
        "primitive_id": "builtin_triangle",
        "graph_node_kind": "builtin",
        "geometry_contract": "optix.builtin_triangle.v1",
        "geometry_roles": [],
        "capabilities": ["builtin_triangle_intersection"],
    },
    {
        "primitive_id": "custom_primitive",
        "graph_node_kind": "custom",
        "geometry_contract": "rtdl.custom_aabb_intersection.v1",
        "geometry_roles": [
            {"role": "bounds", "effects": ["aabb"]},
            {"role": "intersection", "effects": ["hit", "no_hit"]},
        ],
        "capabilities": ["custom_primitive_intersection"],
    },
)

TOPOLOGIES = (
    {
        "topology_id": "any_hit_terminate_bool_per_query",
        "roles": [
            {"role": "make_ray", "effects": ["trace_request"]},
            {"role": "any_hit", "effects": ["terminate"]},
            {"role": "miss", "effects": ["payload"]},
            {"role": "finalize", "effects": ["output"]},
        ],
        "metadata_channels": [],
        "result": {
            "operator_id": "rtdl.result.per_query_bool.v1",
            "value_type": "bool",
            "count_relation": "query_count",
        },
        "continuation": "terminate_on_first_accepted_hit",
        "capabilities": ["any_hit_terminate", "per_query_bool_output"],
    },
    {
        "topology_id": "any_hit_count_continue_u64_per_query",
        "roles": [
            {"role": "make_ray", "effects": ["trace_request"]},
            {"role": "any_hit", "effects": ["accept_continue"]},
            {"role": "miss", "effects": ["payload"]},
            {"role": "finalize", "effects": ["output"]},
        ],
        "metadata_channels": [],
        "result": {
            "operator_id": "rtdl.result.per_query_u64.v1",
            "value_type": "u64",
            "count_relation": "query_count",
        },
        "continuation": "accept_every_hit_and_continue",
        "capabilities": ["any_hit_accept_continue", "per_query_u64_output"],
    },
    {
        "topology_id": "any_hit_filtered_count_u64_per_query",
        "roles": [
            {"role": "make_ray", "effects": ["trace_request"]},
            {
                "role": "any_hit",
                "effects": ["accept_continue", "ignore"],
            },
            {"role": "miss", "effects": ["payload"]},
            {"role": "finalize", "effects": ["output"]},
        ],
        "metadata_channels": [
            {
                "semantic": "primitive.include",
                "value_type": "u32",
                "domain": "primitive",
                "consumer_role": "any_hit",
            }
        ],
        "result": {
            "operator_id": "rtdl.result.per_query_u64.v1",
            "value_type": "u64",
            "count_relation": "query_count",
        },
        "continuation": "ignore_excluded_hits_accept_included_hits_and_continue",
        "capabilities": [
            "any_hit_accept_continue",
            "any_hit_ignore",
            "primitive_metadata_lookup",
            "per_query_u64_output",
        ],
    },
)

# These exact callback topologies already existed before Goal5838. Excluding
# them is conservative: a global reduction wrapper does not make them unseen.
EXCLUDED_EXACT_CALLBACK_TOPOLOGIES = {
    ("builtin_triangle", "any_hit_count_continue_u64_per_query"): {
        "source": "src/rtdsl/v4_triangle_standard_library.py",
        "symbol": "compile_count_callback",
        "reason": "exact any-hit accept-continue per-ray u64 count callback existed",
    },
    ("builtin_triangle", "any_hit_filtered_count_u64_per_query"): {
        "source": "src/rtdsl/v4_triangle_standard_library.py",
        "symbol": "compile_keyed_callback",
        "reason": "exact any-hit ignore-or-continue filtered count callback existed",
    },
}


class Goal5838SealError(RuntimeError):
    pass


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def pretty_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(relative: str | Path) -> str:
    path = ROOT / relative
    return sha256_bytes(path.read_bytes())


def seal_document(document: Mapping[str, Any], field: str, domain: str) -> str:
    payload = dict(document)
    payload[field] = ""
    return sha256_bytes(domain.encode("ascii") + b"\0" + canonical_json_bytes(payload))


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _file_rows(paths: tuple[str, ...]) -> list[dict[str, object]]:
    rows = []
    for relative in paths:
        payload = (ROOT / relative).read_bytes()
        rows.append(
            {"path": relative, "bytes": len(payload), "sha256": sha256_bytes(payload)}
        )
    return rows


def _candidate_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for primitive in PRIMITIVES:
        for topology in TOPOLOGIES:
            key = (primitive["primitive_id"], topology["topology_id"])
            exclusion = EXCLUDED_EXACT_CALLBACK_TOPOLOGIES.get(key)
            candidate_id = f"{key[0]}::{key[1]}"
            if exclusion is not None:
                exclusions.append(
                    {
                        "candidate_id": candidate_id,
                        "primitive_id": key[0],
                        "topology_id": key[1],
                        **exclusion,
                    }
                )
                continue
            roles = [*primitive["geometry_roles"], *topology["roles"]]
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "primitive_id": key[0],
                    "topology_id": key[1],
                    "graph_node_kind": primitive["graph_node_kind"],
                    "geometry_contract": primitive["geometry_contract"],
                    "role_effect_topology": roles,
                    "metadata_channels": topology["metadata_channels"],
                    "result_topology": topology["result"],
                    "continuation": topology["continuation"],
                    "required_capabilities": sorted(
                        [
                            "callback_ir",
                            "fail_closed_status",
                            *primitive["capabilities"],
                            *topology["capabilities"],
                        ]
                    ),
                    "single_static_gas": True,
                    "independent_cpu_oracle_feasible": True,
                    "true_gpu_receipt_required": True,
                    "exact_pre_goal5838_callback_topology_exists": False,
                    "selection_status": "ELIGIBLE_UNSELECTED",
                }
            )
    rows.sort(key=lambda row: str(row["candidate_id"]).encode("utf-8"))
    exclusions.sort(key=lambda row: str(row["candidate_id"]).encode("utf-8"))
    for index, row in enumerate(rows):
        row["stable_index"] = index
    return rows, exclusions


def build_challenge_table() -> dict[str, Any]:
    rows, exclusions = _candidate_rows()
    table: dict[str, Any] = {
        "schema": "rtdl.goal5838.prospective_challenge_table.v1",
        "status": "FROZEN_COMPLETE_TABLE__NO_CHALLENGE_SELECTED",
        "generation_rule": {
            "cartesian_product": (
                "all four primitive kinds exercised by pre-Goal5838 V4 provider "
                "paths crossed with all three predeclared challenge topologies"
            ),
            "exclusion_rule": (
                "exclude only exact callback role/effect/result topologies whose "
                "implementation existed before Goal5838"
            ),
            "sorting_rule": "candidate_id ascending by UTF-8 bytes",
            "manual_row_addition_or_removal": False,
        },
        "primitive_domain": list(PRIMITIVES),
        "topology_domain": list(TOPOLOGIES),
        "excluded_exact_preexisting_topologies": exclusions,
        "eligible_candidate_count": len(rows),
        "eligible_candidates": rows,
        "selection": {
            "provider": "NIST Randomness Beacon 2.0 Beta",
            "target_timestamp": TARGET_TIMESTAMP,
            "target_timestamp_ms": TARGET_TIMESTAMP_MS,
            "target_pulse_uri": TARGET_PULSE_URI,
            "previous_pulse_uri": PREVIOUS_PULSE_URI,
            "pinned_certificate_id_sha512_der": PINNED_CERTIFICATE_ID,
            "entropy_field": "target.pulse.localRandomValue",
            "mapping": "domain-separated SHA-256 with rejection sampling",
            "selected_candidate_id": None,
        },
        "claim_boundary": {
            "every_row_is_a_full_protocol_shape_not_merely_a_geometry_name": True,
            "existing_near_matches_are_not_called_unseen": True,
            "selection_occurs_only_after_core_seal": True,
            "candidate_implementation_before_selection": False,
            "one_success_is_one_bounded_prospective_result": True,
            "arbitrary_callback_ir_execution_claimed": False,
        },
        "challenge_table_sha256": "",
    }
    table["challenge_table_sha256"] = seal_document(
        table,
        "challenge_table_sha256",
        "rtdl.goal5838.prospective_challenge_table.v1",
    )
    return table


def build_core_seal(table: Mapping[str, Any]) -> dict[str, Any]:
    preregistration = json.loads(PREREGISTRATION_PATH.read_text(encoding="ascii"))
    core_last_commit = _git("log", "-1", "--format=%H", "--", *CORE_FILES)
    seal: dict[str, Any] = {
        "schema": "rtdl.goal5838.generic_core_seal.v1",
        "status": "GENERIC_CORE_FROZEN__CHALLENGE_NOT_SELECTED",
        "preregistration": {
            "path": str(PREREGISTRATION_PATH.relative_to(ROOT)),
            "authority_sha256": preregistration["authority_sha256"],
            "file_sha256": sha256_path(PREREGISTRATION_PATH.relative_to(ROOT)),
            "baseline_git_commit": preregistration["baseline"]["git_commit"],
        },
        "repository": {
            "branch": _git("branch", "--show-current"),
            "seal_tooling_commit": _git("rev-parse", "HEAD"),
            "last_core_mutation_commit": core_last_commit,
            "core_mutation_allowed_after_seal": False,
        },
        "frozen_core_files": _file_rows(CORE_FILES),
        "public_api": {
            "module": "rtdsl.v4_family",
            "version": "1.0.0",
            "surface_sha256": sha256_path("src/rtdsl/v4_family.py"),
        },
        "stage_b_evidence_files_at_seal": _file_rows(MIGRATION_FILES),
        "stage_b_results": {
            "stable_fixed_constructors_migrated": 2,
            "closed_successor_routes_migrated": 1,
            "classifications_changed": 0,
            "package_external_provider_fixture_count": 1,
            "focused_tests": {"passed": 67, "failed": 0, "errors": 0},
            "goal583x_regression": {
                "run": 265,
                "passed": 264,
                "known_historical_errors": 1,
                "known_error": (
                    "goal5832_protocol_shape_algebra_test."
                    "test_authority_matches_repository: "
                    "goal5831.source_authorities[6] byte count drift"
                ),
                "new_goal5838_regressions": 0,
            },
        },
        "challenge_table": {
            "path": str(TABLE_PATH.relative_to(ROOT)),
            "authority_sha256": table["challenge_table_sha256"],
            "eligible_candidate_count": table["eligible_candidate_count"],
            "selected_candidate_count": 0,
        },
        "selection_protocol": {
            "path": str(PROTOCOL_PATH.relative_to(ROOT)),
            "sha256": sha256_path(PROTOCOL_PATH.relative_to(ROOT)),
            "client_path": str(SELECTION_CLIENT_PATH.relative_to(ROOT)),
            "client_sha256": sha256_path(SELECTION_CLIENT_PATH.relative_to(ROOT)),
            "target_timestamp": TARGET_TIMESTAMP,
            "target_timestamp_ms": TARGET_TIMESTAMP_MS,
            "target_was_future_when_protocol_committed": True,
            "pretarget_live_calibration": {
                "path": str(CALIBRATION_PATH.relative_to(ROOT)),
                "sha256": sha256_path(CALIBRATION_PATH.relative_to(ROOT)),
                "certificate_path": str(
                    CALIBRATION_CERTIFICATE_PATH.relative_to(ROOT)
                ),
                "certificate_sha256": sha256_path(
                    CALIBRATION_CERTIFICATE_PATH.relative_to(ROOT)
                ),
            },
        },
        "pre_selection_activity": {
            "selected_candidate_count": 0,
            "candidate_specific_provider_implementation_count": 0,
            "candidate_execution_count": 0,
            "true_gpu_receipt_count": 0,
            "prospective_success_count": 0,
        },
        "review": {
            "internal_hostile_review_required_before_seal": True,
            "external_review_count": 0,
            "external_review_deferred_by_owner_while_traveling": True,
            "multi_ai_consensus_claimed": False,
        },
        "claim_boundary": {
            "seal_is_stage_b_engineering_evidence": True,
            "seal_is_not_prospective_success": True,
            "seal_is_not_true_gpu_evidence": True,
            "ordinary_extension_or_infrastructure_bug_is_scientific_failure": False,
            "scientific_failure_requires_preregistered_minimal_core_change_witness": True,
        },
        "seal_sha256": "",
    }
    seal["seal_sha256"] = seal_document(
        seal,
        "seal_sha256",
        "rtdl.goal5838.generic_core_seal.v1",
    )
    return seal


def _verify_file_rows(rows: object, *, current: bool) -> None:
    if not isinstance(rows, list):
        raise Goal5838SealError("file rows must be a list")
    for row in rows:
        if not isinstance(row, dict):
            raise Goal5838SealError("file row must be an object")
        relative = row.get("path")
        if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise Goal5838SealError("unsafe sealed path")
        if current:
            payload = (ROOT / relative).read_bytes()
            if len(payload) != row.get("bytes") or sha256_bytes(payload) != row.get("sha256"):
                raise Goal5838SealError(f"sealed file drift: {relative}")


def verify_stored() -> dict[str, Any]:
    table = json.loads(TABLE_PATH.read_text(encoding="ascii"))
    seal = json.loads(SEAL_PATH.read_text(encoding="ascii"))
    expected_table = build_challenge_table()
    if canonical_json_bytes(table) != canonical_json_bytes(expected_table):
        raise Goal5838SealError("challenge table no longer matches frozen generator")
    if table.get("challenge_table_sha256") != seal_document(
        table,
        "challenge_table_sha256",
        "rtdl.goal5838.prospective_challenge_table.v1",
    ):
        raise Goal5838SealError("challenge table seal mismatch")
    if seal.get("seal_sha256") != seal_document(
        seal,
        "seal_sha256",
        "rtdl.goal5838.generic_core_seal.v1",
    ):
        raise Goal5838SealError("generic core seal mismatch")
    if seal.get("challenge_table", {}).get("authority_sha256") != table.get(
        "challenge_table_sha256"
    ):
        raise Goal5838SealError("seal/table cross-binding mismatch")
    if seal.get("challenge_table", {}).get("selected_candidate_count") != 0:
        raise Goal5838SealError("pre-selection seal selected-count drift")
    if table.get("selection", {}).get("selected_candidate_id") is not None:
        raise Goal5838SealError("frozen challenge table was mutated after selection")
    protocol = seal.get("selection_protocol")
    if not isinstance(protocol, dict):
        raise Goal5838SealError("selection protocol seal missing")
    pinned_files = (
        (protocol.get("path"), protocol.get("sha256"), "selection protocol"),
        (
            protocol.get("client_path"),
            protocol.get("client_sha256"),
            "selection client",
        ),
        (
            protocol.get("pretarget_live_calibration", {}).get("path"),
            protocol.get("pretarget_live_calibration", {}).get("sha256"),
            "pretarget calibration",
        ),
        (
            protocol.get("pretarget_live_calibration", {}).get("certificate_path"),
            protocol.get("pretarget_live_calibration", {}).get("certificate_sha256"),
            "pretarget certificate",
        ),
    )
    for relative, expected_sha256, label in pinned_files:
        if not isinstance(relative, str) or not isinstance(expected_sha256, str):
            raise Goal5838SealError(f"{label} identity missing")
        if sha256_path(relative) != expected_sha256:
            raise Goal5838SealError(f"{label} drift")
    preregistration = seal.get("preregistration")
    if not isinstance(preregistration, dict):
        raise Goal5838SealError("preregistration identity missing")
    if sha256_path(preregistration["path"]) != preregistration.get("file_sha256"):
        raise Goal5838SealError("preregistration file drift")
    _verify_file_rows(seal.get("frozen_core_files"), current=True)
    _verify_file_rows(seal.get("stage_b_evidence_files_at_seal"), current=False)
    return {
        "status": "PASS__GOAL5838_GENERIC_CORE_AND_CHALLENGE_TABLE_SEAL",
        "seal_sha256": seal["seal_sha256"],
        "challenge_table_sha256": table["challenge_table_sha256"],
        "frozen_core_file_count": len(seal["frozen_core_files"]),
        "eligible_candidate_count": table["eligible_candidate_count"],
        "selected_candidate_count": 0,
    }


def write_outputs() -> dict[str, Any]:
    if _git("status", "--porcelain"):
        raise Goal5838SealError("generation requires a clean worktree")
    table = build_challenge_table()
    seal = build_core_seal(table)
    TABLE_PATH.write_bytes(pretty_json_bytes(table))
    SEAL_PATH.write_bytes(pretty_json_bytes(seal))
    return verify_stored()


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    result = write_outputs() if args.write else verify_stored()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
