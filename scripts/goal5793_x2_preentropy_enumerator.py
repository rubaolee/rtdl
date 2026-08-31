#!/usr/bin/env python3
"""Validate synthetic X2 science rows and deterministically enumerate triplets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts.goal5793_x2_offline_core import (
    STRUCTURAL_AXES,
    STRUCTURAL_VOCABULARY,
    X2Error,
    enumerate_ordered_triplets,
    validate_science_row,
)


ROOT = Path(__file__).resolve().parents[1]
POSITIVE_AUTHORITY = ROOT / "history/internal_docs/goal5793_x1_positive_vector_freeze_20260822.json"
POSITIVE_AUTHORITY_FILE_SHA256 = "07be9926d986c807651dd39f28310ffb905d3bfc1869690839ab29e3ab96e152"
POSITIVE_AUTHORITY_INTERNAL_SHA256 = "88f82869d58b2916207fa26832c4ffa4405b7efcee4340e3354d9d43de90017f"


POSITIVE_CATEGORICAL_VECTORS: Mapping[str, Mapping[str, str]] = {
    "77c251dbb920fb45cc88e90e61be7c5270d19e9fa61b3c63ad824cc213ba4710": {
        "geometry_family": "CUSTOM_AABB",
        "primitive_type": "CUSTOM_AABB_BOX_OR_INTERVAL",
        "ray_construction": "AXIS_ALIGNED_INTERVAL",
        "hit_policy": "ANY_HIT_ACCEPT_CONTINUE",
        "multiplicity": "SET",
        "boundary_convention": "INCLUSIVE_AABB",
        "tie_break": "LEXICOGRAPHIC_IDS",
        "numeric_domain": "BINARY32_PINNED_GEOMETRY",
        "overflow_domain": "FAIL_CLOSED_CAPACITY",
        "decode": "SET",
        "continuation": "SINGLE_TRACE",
        "composition": "GRAPH_OR_RELATION_CONSTRUCTION",
        "ownership_epoch": "STATIC_IMMUTABLE",
    },
    "a08f2876ff805876b07e09609243f934b9792dcfe389ae3256d2ae041bda17eb": {
        "geometry_family": "BUILTIN_TRIANGLE",
        "primitive_type": "TRIANGLE",
        "ray_construction": "QUERY_EMBEDDED_RANK_OR_KEY",
        "hit_policy": "CLOSEST_HIT_OR_MISS",
        "multiplicity": "EXACTLY_ONE",
        "boundary_convention": "INTERIOR_CELL",
        "tie_break": "LEFTMOST_INDEX",
        "numeric_domain": "MIXED_INTEGER_BINARY32",
        "overflow_domain": "FAIL_CLOSED_CAPACITY",
        "decode": "PER_QUERY_VALUE",
        "continuation": "SINGLE_TRACE",
        "composition": "INDEPENDENT_PER_QUERY",
        "ownership_epoch": "STATIC_IMMUTABLE",
    },
    "d66c3a021be8a90cb25a11bdb9a1a31c17878c24c16ccb43c772bddab244ab60": {
        "geometry_family": "BUILTIN_TRIANGLE",
        "primitive_type": "TRIANGLE",
        "ray_construction": "MESH_ORIENTATION_QUERY",
        "hit_policy": "CLOSEST_HIT_OR_MISS",
        "multiplicity": "ZERO_OR_ONE",
        "boundary_convention": "ORIENTED_TRIANGLE",
        "tie_break": "MIN_PRIMITIVE_ID",
        "numeric_domain": "BINARY32_PINNED_GEOMETRY",
        "overflow_domain": "FAIL_CLOSED_STATUS_BEFORE_OUTPUT",
        "decode": "ORDERED_VECTOR",
        "continuation": "SINGLE_TRACE",
        "composition": "INDEPENDENT_PER_QUERY",
        "ownership_epoch": "STATIC_IMMUTABLE",
    },
    "d9cc889e38d176dd76437782534b6c9c091f20475931e399a5846800facd342f": {
        "geometry_family": "BUILTIN_TRIANGLE",
        "primitive_type": "TRIANGLE",
        "ray_construction": "FINITE_SEGMENT",
        "hit_policy": "ANY_HIT_ACCEPT_CONTINUE",
        "multiplicity": "CHECKED_SCALAR_REDUCTION",
        "boundary_convention": "EXACT_INTEGER",
        "tie_break": "NOT_APPLICABLE",
        "numeric_domain": "CHECKED_U32_TO_U64",
        "overflow_domain": "FAIL_CLOSED_CHECKED_INTEGER",
        "decode": "SCALAR",
        "continuation": "SINGLE_TRACE",
        "composition": "COMMUTATIVE_CHECKED_REDUCTION",
        "ownership_epoch": "STATIC_IMMUTABLE",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_positive_vectors() -> tuple[list[Mapping[str, str]], dict[str, Any]]:
    if not POSITIVE_AUTHORITY.is_file() or _sha256(POSITIVE_AUTHORITY) != POSITIVE_AUTHORITY_FILE_SHA256:
        raise X2Error("X1_POSITIVE_AUTHORITY_IDENTITY_MISMATCH")
    document = json.loads(POSITIVE_AUTHORITY.read_text(encoding="utf-8", errors="strict"))
    if document.get("authority_sha256") != POSITIVE_AUTHORITY_INTERNAL_SHA256:
        raise X2Error("X1_POSITIVE_AUTHORITY_INTERNAL_SEAL_MISMATCH")
    observed = document.get("unique_structural_vectors")
    if not isinstance(observed, list) or len(observed) != 4:
        raise X2Error("X1_POSITIVE_VECTOR_COUNT_MISMATCH")
    observed_hashes = {row.get("structural_vector_sha256") for row in observed if isinstance(row, Mapping)}
    if observed_hashes != set(POSITIVE_CATEGORICAL_VECTORS):
        raise X2Error("X1_POSITIVE_VECTOR_IDENTITY_SET_MISMATCH")
    vectors = [dict(POSITIVE_CATEGORICAL_VECTORS[digest]) for digest in sorted(POSITIVE_CATEGORICAL_VECTORS)]
    for vector in vectors:
        if set(vector) != set(STRUCTURAL_AXES):
            raise X2Error("X2_CATEGORICAL_POSITIVE_VECTOR_SCHEMA_MISMATCH")
        for axis, value in vector.items():
            if value not in STRUCTURAL_VOCABULARY[axis]:
                raise X2Error("X2_CATEGORICAL_POSITIVE_VALUE_OUTSIDE_TAXONOMY")
    return vectors, {
        "path": POSITIVE_AUTHORITY.relative_to(ROOT).as_posix(),
        "bytes": POSITIVE_AUTHORITY.stat().st_size,
        "file_sha256": _sha256(POSITIVE_AUTHORITY),
        "internal_authority_sha256": POSITIVE_AUTHORITY_INTERNAL_SHA256,
        "unique_nested_vector_count": 4,
        "categorical_projection_count": 4,
    }


def build_fixture_result(science_fixture: Mapping[str, Any]) -> dict[str, Any]:
    if set(science_fixture) != {
        "schema",
        "mode",
        "synthetic_fixture",
        "network_call_count",
        "examiner_invocation_count",
        "candidate_implementation_count",
        "rows",
    }:
        raise X2Error("SCIENCE_FIXTURE_SCHEMA_MISMATCH")
    if science_fixture["schema"] != "rtdl.goal5793.x2.preentropy_science_fixture.v1":
        raise X2Error("SCIENCE_FIXTURE_SCHEMA_MISMATCH")
    if science_fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or science_fixture["synthetic_fixture"] is not True:
        raise X2Error("SCIENCE_FIXTURE_MODE_INVALID")
    for zero_field in ("network_call_count", "examiner_invocation_count", "candidate_implementation_count"):
        if science_fixture[zero_field] != 0:
            raise X2Error("PRESELECTION_OUTCOME_LEAKAGE")
    rows = science_fixture["rows"]
    if not isinstance(rows, list):
        raise X2Error("SCIENCE_FIXTURE_ROWS_INVALID")
    positives, positive_authority = load_positive_vectors()
    validated = [validate_science_row(row, positives) for row in rows]
    validated.sort(key=lambda row: row["candidate_id"].encode("utf-8"))
    triplets = enumerate_ordered_triplets(validated)
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.preentropy_enumerator_fixture_result.v1",
        "status": "OFFLINE_SYNTHETIC_ROLE_AND_TRIPLET_ENUMERATION__NOT_X3_SCIENCE_OR_SELECTION",
        "positive_vector_authority": positive_authority,
        "taxonomy": {
            "structural_axes": list(STRUCTURAL_AXES),
            "allowed_values": {axis: list(STRUCTURAL_VOCABULARY[axis]) for axis in STRUCTURAL_AXES},
            "post_live_extension_allowed": False,
            "unmapped_or_disputed_value": "SELECTION_INELIGIBLE__NO_POSTSEARCH_VOCABULARY_EXTENSION",
        },
        "validated_rows": validated,
        "ordered_triplets": triplets,
        "counts": {
            "input_rows": len(rows),
            "role_A_rows": sum(row["role_A"] for row in validated),
            "role_B_rows": sum(row["role_B"] for row in validated),
            "role_C_rows": sum(row["role_C"] for row in validated),
            "ordered_triplets": len(triplets),
            "network_calls": 0,
            "examiner_invocations": 0,
            "candidate_implementations": 0,
            "candidate_executions": 0,
        },
        "authorization": {
            "live_search": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
        },
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(
        result,
        seal_field="result_sha256",
        domain="rtdl.goal5793.x2.preentropy_enumerator_fixture_result",
        version=1,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--science-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(args.science_fixture.read_text(encoding="utf-8", errors="strict"))
    result = build_fixture_result(fixture)
    payload = canonical_json_bytes(result) + b"\n"
    if not args.write_create_only:
        print(json.dumps({"status": "DRY_RUN_NO_HISTORY_WRITE", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}))
        return 0
    if args.output is None:
        raise SystemExit("OUTPUT_REQUIRED_FOR_WRITE")
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps({"path": args.output.as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

