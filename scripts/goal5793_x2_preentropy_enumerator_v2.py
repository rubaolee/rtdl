#!/usr/bin/env python3
"""Append-only X2 enumerator successor that records every unmapped row.

The reviewed v1 bytes remain immutable.  This successor implements the
pre-corpus disposition already declared by v1: a well-formed row containing a
string value outside the frozen vocabulary remains visible, receives no role,
is selection-ineligible, and contributes to a sealed denominator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core_v1
from scripts import goal5793_x2_preentropy_enumerator as enumerator_v1


RESULT_DOMAIN = "rtdl.goal5793.x2.preentropy_enumerator_fixture_result.v2"
UNMAPPED_STATUS = "UNMAPPED_IN_FROZEN_VOCABULARY__SELECTION_INELIGIBLE"
CLAIM_LANGUAGE = {
    "role_diversity_predicate": (
        "NON_IDENTITY_CHECK_ONLY__HAMMING_DISTANCE_AT_LEAST_ONE_FROM_EACH_OF_FOUR_FROZEN_POSITIVE_VECTORS"
    ),
    "role_diversity_supports_structural_novelty_or_coverage_claim": False,
    "role_A_interpretation": (
        "PREREGISTERED_PREDICTION_CALIBRATION_ON_ENTROPY_SELECTED_INSTANCES_NOT_CHOSEN_BY_AUTHORS"
    ),
    "role_A_supports_arbitrary_literature_capability_claim": False,
    "allowed_sampling_frame_wording": (
        "RANDOMLY_SELECTED_FROM_WORKS_EXPRESSIBLE_IN_THE_PRE_FROZEN_STRUCTURAL_VOCABULARY"
    ),
    "required_companion_denominator": "UNMAPPED_ROW_COUNT_AND_PER_AXIS_BREAKDOWN",
    "randomly_selected_from_the_literature_without_qualification_allowed": False,
}


def _validate_fixture_envelope(science_fixture: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    expected = {
        "schema", "mode", "synthetic_fixture", "network_call_count",
        "examiner_invocation_count", "candidate_implementation_count", "rows",
    }
    if not isinstance(science_fixture, Mapping) or set(science_fixture) != expected:
        raise core_v1.X2Error("SCIENCE_FIXTURE_SCHEMA_MISMATCH")
    if science_fixture["schema"] != "rtdl.goal5793.x2.preentropy_science_fixture.v1":
        raise core_v1.X2Error("SCIENCE_FIXTURE_SCHEMA_MISMATCH")
    if science_fixture["mode"] != "OFFLINE_SYNTHETIC_FIXTURES_ONLY" or science_fixture["synthetic_fixture"] is not True:
        raise core_v1.X2Error("SCIENCE_FIXTURE_MODE_INVALID")
    for field in ("network_call_count", "examiner_invocation_count", "candidate_implementation_count"):
        if science_fixture[field] != 0:
            raise core_v1.X2Error("PRESELECTION_OUTCOME_LEAKAGE")
    rows = science_fixture["rows"]
    if not isinstance(rows, list) or any(not isinstance(row, Mapping) for row in rows):
        raise core_v1.X2Error("SCIENCE_FIXTURE_ROWS_INVALID")
    return rows


def _validate_or_record(
    row: Mapping[str, Any], positive_vectors: list[Mapping[str, Any]]
) -> dict[str, Any]:
    try:
        mapped = core_v1.validate_science_row(row, positive_vectors)
    except core_v1.X2Error as exc:
        if exc.reason_id != "SCIENCE_ROW_UNMAPPED_STRUCTURAL_VALUE":
            raise
        vector = row.get("structural_vector")
        if not isinstance(vector, Mapping) or set(vector) != set(core_v1.STRUCTURAL_AXES):
            raise
        unmapped = []
        sanitized = dict(row)
        sanitized_vector = dict(vector)
        for axis in core_v1.STRUCTURAL_AXES:
            value = vector[axis]
            if value not in core_v1.STRUCTURAL_VOCABULARY[axis]:
                if not isinstance(value, str) or not value:
                    raise core_v1.X2Error("SCIENCE_ROW_UNMAPPED_STRUCTURAL_VALUE_NOT_RECORDABLE", axis)
                unmapped.append({"axis": axis, "value": value})
                sanitized_vector[axis] = core_v1.STRUCTURAL_VOCABULARY[axis][0]
        if not unmapped:
            raise
        sanitized["structural_vector"] = sanitized_vector
        # Reuse the reviewed validator to reject every non-taxonomy defect.
        core_v1.validate_science_row(sanitized, positive_vectors)
        return {
            "candidate_id": row["candidate_id"],
            "canonical_work_identity": row["canonical_work_identity"],
            "normalized_problem_family": row["normalized_problem_family"],
            "role_A": False,
            "role_B": False,
            "role_C": False,
            "expected_disposition": row["expected_disposition"],
            "structural_vector": dict(vector),
            "risk_flags": dict(row["risk_flags"]),
            "structural_mapping_status": UNMAPPED_STATUS,
            "unmapped_structural_values": unmapped,
            "selection_eligible": False,
            "exclusion_reason": "FROZEN_STRUCTURAL_VOCABULARY_CANNOT_EXPRESS_ROW__NO_MANUAL_DELETION__NO_EXTENSION",
        }
    return {
        **mapped,
        "structural_mapping_status": "MAPPED_IN_FROZEN_VOCABULARY",
        "unmapped_structural_values": [],
        "selection_eligible": bool(mapped["role_A"] or mapped["role_B"] or mapped["role_C"]),
        "exclusion_reason": None,
    }


def build_fixture_result(science_fixture: Mapping[str, Any]) -> dict[str, Any]:
    rows = _validate_fixture_envelope(science_fixture)
    positives, positive_authority = enumerator_v1.load_positive_vectors()
    validated = [_validate_or_record(row, positives) for row in rows]
    candidate_ids = [row["candidate_id"] for row in validated]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise core_v1.X2Error("TRIPLET_CANDIDATE_ID_DUPLICATE")
    validated.sort(key=lambda row: row["candidate_id"].encode("utf-8"))
    mapped_rows = [row for row in validated if row["structural_mapping_status"] == "MAPPED_IN_FROZEN_VOCABULARY"]
    triplets = core_v1.enumerate_ordered_triplets(mapped_rows)
    per_axis = {axis: 0 for axis in core_v1.STRUCTURAL_AXES}
    per_axis_values: dict[str, list[str]] = {axis: [] for axis in core_v1.STRUCTURAL_AXES}
    for row in validated:
        for item in row["unmapped_structural_values"]:
            per_axis[item["axis"]] += 1
            per_axis_values[item["axis"]].append(item["value"])
    per_axis_values = {
        axis: sorted(set(values), key=lambda value: value.encode("utf-8"))
        for axis, values in per_axis_values.items()
    }
    unmapped_count = len(validated) - len(mapped_rows)
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.preentropy_enumerator_fixture_result.v2",
        "status": "OFFLINE_SYNTHETIC_ENUMERATION_WITH_SEALED_UNMAPPED_DENOMINATOR__NOT_X3_SCIENCE_OR_SELECTION",
        "successor_of": {
            "path": "scripts/goal5793_x2_preentropy_enumerator.py",
            "review_finding": "P1_1_UNMAPPED_ROW_BATCH_ABORT",
            "reviewed_bytes_edited": False,
        },
        "positive_vector_authority": positive_authority,
        "taxonomy": {
            "structural_axes": list(core_v1.STRUCTURAL_AXES),
            "allowed_values": {axis: list(core_v1.STRUCTURAL_VOCABULARY[axis]) for axis in core_v1.STRUCTURAL_AXES},
            "post_live_extension_allowed": False,
            "unmapped_or_disputed_value": UNMAPPED_STATUS,
            "manual_row_deletion_or_unrecorded_prefilter_allowed": False,
            "unmapped_row_preserved_in_validated_rows": True,
        },
        "claim_language": CLAIM_LANGUAGE,
        "validated_rows": validated,
        "ordered_triplets": triplets,
        "counts": {
            "input_rows": len(rows),
            "mapped_rows": len(mapped_rows),
            "unmapped_rows": unmapped_count,
            "unmapped_by_axis": per_axis,
            "unmapped_values_by_axis": per_axis_values,
            "role_A_rows": sum(row["role_A"] for row in mapped_rows),
            "role_B_rows": sum(row["role_B"] for row in mapped_rows),
            "role_C_rows": sum(row["role_C"] for row in mapped_rows),
            "ordered_triplets": len(triplets),
            "network_calls": 0,
            "examiner_invocations": 0,
            "candidate_implementations": 0,
            "candidate_executions": 0,
        },
        "authorization": {
            "live_search": False, "entropy": False, "selection": False,
            "candidate_work": False, "gpu_ssh_pod": False, "timing": False,
        },
        "result_sha256": "",
    }
    if result["counts"]["input_rows"] != result["counts"]["mapped_rows"] + result["counts"]["unmapped_rows"]:
        raise core_v1.X2Error("UNMAPPED_DENOMINATOR_ACCOUNTING_MISMATCH")
    result["result_sha256"] = seal_document(result, seal_field="result_sha256", domain=RESULT_DOMAIN, version=2)
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
    if args.write_create_only:
        if args.output is None or args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_INVALID_OR_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(json.dumps({"status": "PASS", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
