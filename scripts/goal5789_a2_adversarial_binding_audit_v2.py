"""Append-only exact-reason successor to the Goal5789-A2 hostile matrix.

The externally reviewed v1 matrix reruns 159 attacks, but its 126
``certificate_only`` rows accept any reason containing ``callback_contract``.
This successor leaves every reviewed byte untouched, reruns the exact v1
matrix, and independently grades those 126 rows against a mutation-derived,
exact normalized reason-set oracle.

This is a local audit repair only.  It does not modify the checker, any
certificate or authority, authorize Goal5793, use a GPU, or authorize a POD.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from scripts import goal5789_a2_adversarial_binding_audit as predecessor
from scripts import goal5789_a2_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
OUTPUT = (
    ROOT
    / "history/internal_docs/goal5789_a2_callback_binding_adversarial_matrix_v2_20260821.json"
)

PREDECESSOR_IDENTITIES: tuple[tuple[str, str, int, str], ...] = (
    (
        "checker",
        "scripts/goal5789_a2_independent_compatibility_checker.py",
        55_535,
        "6dea6a474b8225a99e96508ef1cf56d3f1147cbaa3adb8acf8124c845597e210",
    ),
    (
        "hostile_matrix_v1_generator",
        "scripts/goal5789_a2_adversarial_binding_audit.py",
        21_318,
        "a24867a2236f0d1e67d4c49f55ca723ce4a20bca03ebbc0893f6d909b277ebb8",
    ),
    (
        "hostile_matrix_v1_regression",
        "tests/goal5789_a2_callback_ir_authority_test.py",
        35_518,
        "3f28cb2784590edb926066f6820b4587cf0d8f3e406060305f493571defa13f3",
    ),
    (
        "hostile_matrix_v1",
        "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
        "CALLBACK_BINDING_ADVERSARIAL_MATRIX.json",
        90_589,
        "ec3de9782d5587f944d0872d25cfc8a8703b0963ad2e2109de1455b742c340ea",
    ),
    (
        "owner_returned_external_review",
        "history/internal_docs/"
        "review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md",
        27_657,
        "88e0aff9fcc0579c4721a8a3422517beff9146acfcef7862f9dd7e880da1bd3a",
    ),
    (
        "postreview_absorption_work_authority",
        "history/internal_docs/"
        "goal5789_a2_postreview_absorption_work_authority_20260821.json",
        4_249,
        "96be56ab7f450664fa2d2c27f3df3e9be667eacf9cc45ee0d45725924520e3a0",
    ),
)

V1_INTERNAL_MATRIX_SHA256 = (
    "098ec342c6a0ed406b83787c480c678cdd4ad8b7ef5d3ecddaf82f3b042635f5"
)
WORK_AUTHORITY_INTERNAL_SHA256 = (
    "d37051d04ff5b3ed99abd11f7469de5fc79bbbac59301ad6fd7b210946961e25"
)
V1_SCHEMA = "rtdl.goal5789_a2.callback_binding_adversarial_matrix.v1"
CERTIFICATE_ONLY_PREFIX = "certificate_only::"
RESOURCE_FIELDS = frozenset(
    {
        "payload_u32_slots",
        "attribute_u32_slots",
        "trace_depth",
        "callable_depth",
        "total_static_iterations",
        "helper_call_depth",
    }
)
ALIASES = frozenset({"bool_alias", "float_alias"})


def _pretty(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _verify_predecessor_files() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for role, relative, expected_size, expected_sha256 in PREDECESSOR_IDENTITIES:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"required predecessor missing: {relative}")
        payload = path.read_bytes()
        actual_size = len(payload)
        actual_sha256 = _sha256_bytes(payload)
        if actual_size != expected_size or actual_sha256 != expected_sha256:
            raise RuntimeError(
                "predecessor identity mismatch: "
                f"{relative}: expected {expected_size}/{expected_sha256}, "
                f"observed {actual_size}/{actual_sha256}"
            )
        rows.append(
            {
                "role": role,
                "path": relative,
                "size_bytes": actual_size,
                "file_sha256": actual_sha256,
            }
        )
    work_authority = _load_object(
        ROOT
        / "history/internal_docs/"
        "goal5789_a2_postreview_absorption_work_authority_20260821.json"
    )
    observed_internal = checker.digest(
        {
            key: value
            for key, value in work_authority.items()
            if key != "work_authority_sha256"
        }
    )
    if (
        work_authority.get("work_authority_sha256")
        != WORK_AUTHORITY_INTERNAL_SHA256
        or observed_internal != WORK_AUTHORITY_INTERNAL_SHA256
    ):
        raise RuntimeError("postreview work-authority internal seal mismatch")
    return rows


def _normalized_reason_set(reasons: Iterable[object]) -> list[str]:
    values = list(reasons)
    if any(type(reason) is not str or not reason for reason in values):
        raise RuntimeError("semantic reasons must be nonempty strings")
    return sorted(set(values))


def _certificate_only_oracle(attack_id: str) -> tuple[str, list[str]]:
    """Derive the exact expected boundary and reason set from the mutation."""

    parts = attack_id.split("::")
    if len(parts) < 3 or parts[0] != "certificate_only" or not parts[1]:
        raise RuntimeError(f"not a certificate-only attack id: {attack_id}")
    mutation = parts[2:]
    authority_mismatch = "callback_contract_authority_mismatch"

    if mutation == ["empty_effects"]:
        return authority_mismatch, [authority_mismatch]
    if len(mutation) == 2 and mutation[0] == "digest" and mutation[1] in {
        "ir_sha256",
        "effect_digest",
    }:
        return authority_mismatch, [authority_mismatch]
    if (
        len(mutation) == 3
        and mutation[0] == "resource"
        and mutation[1] in RESOURCE_FIELDS
        and mutation[2] == "different_int"
    ):
        return authority_mismatch, [authority_mismatch]
    if (
        len(mutation) == 3
        and mutation[0] == "resource"
        and mutation[1] in RESOURCE_FIELDS
        and mutation[2] in ALIASES
    ):
        field = mutation[1]
        strict_type_reason = (
            "callback_authority_invalid_nonnegative_integer:callback_contract."
            f"{field}"
        )
        expected = [strict_type_reason, authority_mismatch]
        if field != "helper_call_depth":
            expected.append(f"invalid_callback_budget:{field}")
        return strict_type_reason, sorted(expected)
    raise RuntimeError(f"unregistered certificate-only mutation: {attack_id}")


def _strengthen_certificate_only_row(
    predecessor_row: Mapping[str, object],
) -> dict[str, object]:
    row = deepcopy(dict(predecessor_row))
    attack_id = row.get("attack_id")
    if type(attack_id) is not str:
        raise RuntimeError("attack_id must be a string")
    boundary_id, expected_reasons = _certificate_only_oracle(attack_id)
    actual_reasons = _normalized_reason_set(row.get("reasons", []))
    expected_reasons = _normalized_reason_set(expected_reasons)
    predecessor_fragment = row.pop("required_reason_fragment", None)
    predecessor_passed = row.get("passed") is True
    exact_verdict = row.get("actual_semantic_verdict") == checker.INCOMPATIBLE
    exact_reference = row.get("actual_reference_admission_complete") is False
    exact_reason_set = actual_reasons == expected_reasons
    expected_fields_exact = (
        row.get("expected_semantic_verdict") == checker.INCOMPATIBLE
        and row.get("expected_reference_admission_complete") is False
    )
    row.update(
        {
            "expected_boundary_id": boundary_id,
            "expected_normalized_reason_set": expected_reasons,
            "actual_normalized_reason_set": actual_reasons,
            "reason_normalization": "sorted_unique_exact_string_set",
            "reason_set_exact": exact_reason_set,
            "predecessor_v1_required_reason_fragment": predecessor_fragment,
            "predecessor_v1_passed": predecessor_passed,
            "passed": bool(
                predecessor_passed
                and expected_fields_exact
                and exact_verdict
                and exact_reference
                and exact_reason_set
            ),
        }
    )
    return row


def strengthen(predecessor_matrix: Mapping[str, object]) -> dict[str, object]:
    if predecessor_matrix.get("schema") != V1_SCHEMA:
        raise RuntimeError("hostile matrix v1 schema mismatch")
    if predecessor_matrix.get("matrix_sha256") != V1_INTERNAL_MATRIX_SHA256:
        raise RuntimeError("hostile matrix v1 internal seal mismatch")
    source_cases = predecessor_matrix.get("cases")
    if not isinstance(source_cases, list) or len(source_cases) != 159:
        raise RuntimeError("hostile matrix v1 must contain exactly 159 cases")

    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    certificate_only_count = 0
    for source_row in source_cases:
        if not isinstance(source_row, dict):
            raise RuntimeError("hostile matrix case must be an object")
        attack_id = source_row.get("attack_id")
        if type(attack_id) is not str or attack_id in seen:
            raise RuntimeError(f"invalid or duplicate attack id: {attack_id!r}")
        seen.add(attack_id)
        if attack_id.startswith(CERTIFICATE_ONLY_PREFIX):
            row = _strengthen_certificate_only_row(source_row)
            certificate_only_count += 1
        else:
            row = deepcopy(source_row)
            row["reason_oracle_scope"] = "inherited_v1__outside_external_review_p2_1"
        rows.append(row)

    if certificate_only_count != 126:
        raise RuntimeError(
            f"expected 126 certificate-only attacks, observed {certificate_only_count}"
        )
    failed = [row["attack_id"] for row in rows if row.get("passed") is not True]
    if failed:
        raise RuntimeError(f"hostile matrix v2 failed cases: {failed}")
    exact_rows = [
        row
        for row in rows
        if str(row["attack_id"]).startswith(CERTIFICATE_ONLY_PREFIX)
        and row.get("reason_set_exact") is True
    ]
    reason_shapes = {
        tuple(row["expected_normalized_reason_set"])
        for row in exact_rows
    }
    if len(exact_rows) != 126 or len(reason_shapes) != 7:
        raise RuntimeError("certificate-only exact reason coverage drift")

    output: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.callback_binding_adversarial_matrix.v2",
        "matrix_sha256": "",
        "status": (
            "PASS__159_V1_ATTACKS_REPLAYED__126_CERTIFICATE_ONLY_CASES_"
            "EXACT_NORMALIZED_REASON_SETS_MATCH"
        ),
        "case_count": len(rows),
        "passed_count": len(rows),
        "failed_count": 0,
        "case_accounting": {
            "predecessor_case_count": 159,
            "certificate_only_case_count": certificate_only_count,
            "certificate_only_exact_reason_set_count": len(exact_rows),
            "certificate_only_generic_substring_oracle_count_in_v2": 0,
            "certificate_only_exact_reason_set_shape_count": len(reason_shapes),
            "cases_outside_external_review_p2_1_scope": len(rows) - len(exact_rows),
            "attack_id_set_preserved_from_v1": True,
        },
        "predecessor_lineage": {
            "external_review_p2_1_repaired": True,
            "v1_internal_matrix_sha256": V1_INTERNAL_MATRIX_SHA256,
            "postreview_work_authority_internal_sha256": (
                WORK_AUTHORITY_INTERNAL_SHA256
            ),
            "v1_rerun_byte_identical_to_frozen_matrix": True,
            "files": _verify_predecessor_files(),
        },
        "claim_boundary": {
            "repairs_external_review_p2_1_reason_oracle_specificity_only": True,
            "reruns_original_159_cases": True,
            "certificate_only_exact_normalized_reason_sets_asserted": True,
            "certificate_only_reason_oracle_derived_from_mutation_kind": True,
            "checker_changed": False,
            "authority_or_certificate_changed": False,
            "scientific_result_changed": False,
            "external_review_disposition_reopened": False,
            "semantic_soundness_claimed": False,
            "completeness_claimed": False,
            "generalization_claimed": False,
        },
        "authorization": {
            "authorizes_goal5793": False,
            "authorizes_entropy_draw": False,
            "authorizes_candidate_selection": False,
            "authorizes_product_change": False,
            "authorizes_gpu": False,
            "authorizes_home": False,
            "authorizes_pod": False,
            "authorizes_worker": False,
            "authorizes_performance_timing": False,
            "authorizes_publication": False,
        },
        "cases": rows,
    }
    output["matrix_sha256"] = checker.digest(
        {key: value for key, value in output.items() if key != "matrix_sha256"}
    )
    return output


def audit(a2_dir: Path = A2) -> dict[str, object]:
    _verify_predecessor_files()
    frozen_v1_path = A2 / "CALLBACK_BINDING_ADVERSARIAL_MATRIX.json"
    frozen_v1 = _load_object(frozen_v1_path)
    internal = checker.digest(
        {key: value for key, value in frozen_v1.items() if key != "matrix_sha256"}
    )
    if internal != V1_INTERNAL_MATRIX_SHA256:
        raise RuntimeError("frozen hostile matrix v1 body digest mismatch")
    rerun_v1 = predecessor.audit(a2_dir)
    if _pretty(rerun_v1) != frozen_v1_path.read_bytes():
        raise RuntimeError("hostile matrix v1 rerun is not byte-identical to frozen v1")
    return strengthen(rerun_v1)


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError("Goal5789-A2 hostile matrix v2 is create-only")
    result = audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("xb") as handle:
        handle.write(_pretty(result))
    print(
        json.dumps(
            {
                "file_sha256": _sha256_bytes(OUTPUT.read_bytes()),
                "matrix_sha256": result["matrix_sha256"],
                "case_count": result["case_count"],
                "certificate_only_exact_reason_set_count": result["case_accounting"][
                    "certificate_only_exact_reason_set_count"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
