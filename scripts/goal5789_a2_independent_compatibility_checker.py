"""Goal5789-A2 callback-authority-bound compatibility checker.

This successor leaves the immutable Goal5789 v1 checker untouched.  It adds
one precondition before delegating the original semantic/physical calculus:
the complete callback summary in a certificate must be an exact projection of
a separately materialized, source-backed Callback-IR authority.  The checker
also reconstructs the IR, source, role/effect and static-iteration digests from
the authority's full serialized program without importing RTDL or an app.

The authority and its pin remain trusted inputs.  Coherently replacing every
authority root is intentionally outside this checker's guarantee; A2 records
that jointly-wrong-authority ceiling rather than claiming proof-carrying code
or end-to-end semantic soundness.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from scripts import goal5789_independent_compatibility_checker as v1


CERTIFICATE_SCHEMA = "rtdl.goal5789.semantic_physical_certificate.v2"
AUTHORITY_SCHEMA = "rtdl.goal5789.compatibility_authority_bundle.v2"
CALLBACK_AUTHORITY_SCHEMA = "rtdl.goal5789_a2.callback_ir_authority.v1"
CALLBACK_AUTHORITY_PIN_SCHEMA = "rtdl.goal5789_a2.callback_ir_authority_pin.v1"
CALLBACK_BINDING_SCHEMA = "rtdl.goal5789_a2.callback_ir_authority_binding.v1"
RESULT_SCHEMA = "rtdl.goal5789.compatibility_check_result.v2"

COMPATIBLE = v1.COMPATIBLE
INCOMPATIBLE = v1.INCOMPATIBLE
UNKNOWN = v1.UNKNOWN
CAPABLE = v1.CAPABLE
ADMISSIBLE = v1.ADMISSIBLE

EXPECTED_PROGRAM_SHA256S = {
    "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
    "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
    "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671",
    "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690",
    "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26",
}

EXPECTED_PROGRAM_METADATA_BY_SHA256 = {
    "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476": {
        "alias": "builtin_triangle_adjacency",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "compile_entrypoint": "rtdsl.v4_builtin_triangle_standard_library:compile_adjacency_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_builtin_triangle_standard_library.py",
        ],
    },
    "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30": {
        "alias": "builtin_triangle_count",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.count.v1",
        "compile_entrypoint": "rtdsl.v4_triangle_standard_library:compile_count_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ],
    },
    "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671": {
        "alias": "builtin_triangle_keyed",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.keyed.v1",
        "compile_entrypoint": "rtdsl.v4_triangle_standard_library:compile_keyed_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_triangle_standard_library.py",
        ],
    },
    "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690": {
        "alias": "custom_aabb_box_relation",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.closed_relation.v1",
        "compile_entrypoint": "rtdsl.v4_box_relation_callback:compile_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_box_relation_callback.py",
        ],
    },
    "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26": {
        "alias": "custom_aabb_spatial_candidate",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.spatial_candidate.v1",
        "compile_entrypoint": "rtdsl.v4_spatial_candidate_callback:compile_callback",
        "selected_constructor_source_paths": [
            "src/rtdsl/v4_callback_frontend.py",
            "src/rtdsl/v4_callback_ir.py",
            "src/rtdsl/v4_typed_physical_schema.py",
            "src/rtdsl/v4_spatial_candidate_callback.py",
        ],
    },
}

EXPECTED_ADMITTED_BINDINGS = [
    {
        "semantic_contract_id": "particle.closest_face_projection.v1",
        "physical_encoding_id": "builtin_triangle.closest_face_projection.v1",
        "authority_program_sha256": "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
                "source_sha256": "e2d26dd9a67025066ca77d1c57f358c34a8e4446a679b32f772a228ee52712a4",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ["compile_standard_builtin_triangle_program"],
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_sha256": "71392af802dc5b32a94ed162a79052fa2ac8097e2231bba719eb51dcb0de5868",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ],
            },
        ],
    },
    {
        "semantic_contract_id": "triangle.rt2a1.weighted_count.v1",
        "physical_encoding_id": "builtin_triangle.weighted_count.v1",
        "authority_program_sha256": "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.count.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
                "source_sha256": "8ab4f4ad6c5913483633b06e70035a26637bc2b2a0589ce470623504d86e6210",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": ["compile_count_callback"],
            }
        ],
    },
    {
        "semantic_contract_id": "librts.inclusive_aabb_relation.v1",
        "physical_encoding_id": "custom_aabb.inclusive_relation.v1",
        "authority_program_sha256": "eeb2427e72a1f6b9f242adbf588d89e40616f1176c5bef60705ec716fcd06690",
        "callback_authority_id": "goal5789-a2.callback.custom_aabb.closed_relation.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
                "source_sha256": "2952d38b341525d5b529a4391949df5b1ab59cd463c752f4da4df0823e40b987",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "from rtdsl.v4_box_relation_callback import",
                    "compile_callback()",
                ],
            }
        ],
    },
    {
        "semantic_contract_id": "rtxrmq.leftmost_argmin.v1",
        "physical_encoding_id": "builtin_triangle.rtxrmq_leftmost.v1",
        "authority_program_sha256": "371de8d1816ddb8dbce78db9eb160f08cce3d595784509d5c6400e51b50ad476",
        "callback_authority_id": "goal5789-a2.callback.builtin_triangle.adjacency.v1",
        "consumer_source_witnesses": [
            {
                "source_path": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
                "source_sha256": "0823fdf32e0ade592eebc577b1f43d5c81e4fb1134934f353bbd3e3586a3b0b1",
                "source_root": "goal5789_heldout_certificate_source_pin",
                "required_tokens": ["compile_standard_builtin_triangle_program"],
            },
            {
                "source_path": "src/rtdsl/v4_builtin_triangle_standard_library.py",
                "source_sha256": "71392af802dc5b32a94ed162a79052fa2ac8097e2231bba719eb51dcb0de5868",
                "source_root": "goal5785_execution_source_archive",
                "required_tokens": [
                    "def compile_standard_builtin_triangle_program",
                    "compile_adjacency_callback",
                ],
            },
        ],
    },
]

EXPECTED_CALLBACK_AUTHORITY_CLAIM_BOUNDARY = {
    "source_backed_callback_ir_authority": True,
    "executed_leaf_identity_crossbound": True,
    "controlling_result_source_evidence_crossbound": True,
    "execution_evidence_embeds_exact_source_archive": True,
    "selected_constructor_sources_are_not_claimed_as_complete_import_closure": True,
    "consumer_callsites_exact_hash_and_token_bound": True,
    "callback_authority_bound_inventory_scope": (
        "six_of_fifteen_inventory_rows_plus_legacy_rtxrmq_replay"
    ),
    "authority_producer_is_tcb": True,
    "independently_implemented_product_verifier_claimed": False,
    "jointly_wrong_authorities_detected": False,
    "semantic_soundness_claimed": False,
    "execution_authorized": False,
}

EXPECTED_CALLBACK_PIN_AUTHORIZATION = {
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
}

EXPECTED_CALLBACK_AUTHORITY_PATH = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY.json"
)
EXPECTED_CALLBACK_PIN_PATH = (
    "history/internal_docs/goal5789_a2_contract_evidence_20260821/"
    "CALLBACK_IR_AUTHORITY_PIN.json"
)
EXPECTED_SOURCE_ARCHIVE_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/EXECUTION_SOURCE.tar.gz",
    "size_bytes": 10_836_249,
    "file_sha256": "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
}
EXPECTED_EXECUTION_EVIDENCE_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/GOAL5785_EVIDENCE.tar.gz",
    "size_bytes": 28_674_437,
    "file_sha256": "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a",
}
EXPECTED_CONTROLLING_RESULT_IDENTITY = {
    "path": "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816.json",
    "size_bytes": 4_963,
    "file_sha256": "7f5cd38e625fa62233adfbb9df1f6aa56ebb050999b3154c1604bbc25f4e9064",
}
EXPECTED_EXECUTION_LEAF_MANIFEST_IDENTITY = {
    "member_path": "EXECUTION/FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json",
    "file_sha256": "ecafcfb25190a785ae2cfe704dcb6bc75b137180d23bab4867c1cd40f45ad390",
    "size_bytes": 5_573,
    "entry_count": 26,
    "entries_sha256": "694835a8e5d07afbb935709d424fc9c8abc1afa88c8a1522dbb3859d40594aed",
}

_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_CERTIFICATE_KEYS = {
    "schema",
    "certificate_sha256",
    "semantic_request",
    "physical_encoding",
    "callback_contract",
    "canonical_candidates",
    "target_contract",
    "instance_contract",
    "evidence_contract",
}
_AUTHORITY_KEYS = {
    "schema",
    "authority_sha256",
    "semantic_authority",
    "physical_authority",
    "target_authority",
    "instance_authority",
    "evidence_authority",
    "callback_ir_authority_binding",
}
_CALLBACK_CONTRACT_KEYS = {
    "callback_authority_id",
    "authority_program_sha256",
    "ir_sha256",
    "effect_digest",
    "roles",
    "payload_u32_slots",
    "attribute_u32_slots",
    "trace_depth",
    "callable_depth",
    "total_static_iterations",
    "helper_call_depth",
}
_CALLBACK_AUTHORITY_KEYS = {
    "schema",
    "authority_sha256",
    "source_archive",
    "execution_evidence_archive",
    "controlling_result",
    "execution_leaf_manifest",
    "selected_constructor_source_manifest",
    "consumer_source_manifest",
    "consumer_source_authority_roots",
    "programs",
    "admitted_bindings",
    "claim_boundary",
}
_CALLBACK_PIN_KEYS = {
    "schema",
    "pin_sha256",
    "callback_authority",
    "source_archive",
    "execution_evidence_archive",
    "controlling_result",
    "materializer",
    "authorization",
}
_CALLBACK_BINDING_KEYS = {
    "schema",
    "authority_sha256",
    "callback_authority_path",
    "callback_authority_file_sha256",
    "callback_authority_sha256",
    "callback_authority_pin_path",
    "callback_authority_pin_file_sha256",
    "callback_authority_pin_sha256",
}
_PROGRAM_ROW_KEYS = {
    "callback_authority_id",
    "alias",
    "compile_entrypoint",
    "selected_constructor_source_paths",
    "executed_leaf_evidence",
    "callback_program",
    "callback_program_sha256",
    "verified_summary",
    "callback_contract",
}
_PROGRAM_KEYS = {
    "schema_id",
    "schema_version",
    "manifest",
    "records",
    "functions",
    "normalized_source",
    "source_sha256",
}
_VERIFIED_SUMMARY_KEYS = {
    "ir_sha256",
    "effect_digest",
    "payload_u32_slots",
    "attribute_u32_slots",
    "total_static_iterations",
    "helper_call_depth",
}

_V1_SEMANTIC_UNKNOWN_REASON_PREFIXES = (
    "missing:",
    "missing_or_invalid:",
    "missing_or_nonlist:",
    "missing_or_nonobject:",
    "missing_map_kind:",
    "source_pin_not_in_authority:",
    "unrecognized_evidence:",
)
_V1_SEMANTIC_UNKNOWN_REASONS = {
    "semantic_contract_not_in_independent_authority",
    "physical_encoding_not_in_independent_authority",
}


def _v1_has_proven_semantic_incompatibility(
    reasons: Sequence[object], *, callback_is_unbound: bool
) -> bool:
    """Separate v1's proven contradictions from its UNKNOWN-first presentation.

    The immutable v1 checker intentionally reports UNKNOWN whenever *any*
    authority is missing, even if it simultaneously records contradictions.
    A2 preserves that historical object but must not let its own missing
    Callback-IR authority hide a separately proven contradiction.  Missing
    callback readers are ignored only for an explicitly unbound callback;
    every other non-UNKNOWN reason is decisive.
    """

    for raw_reason in reasons:
        if not isinstance(raw_reason, str):
            return True
        if raw_reason in _V1_SEMANTIC_UNKNOWN_REASONS:
            continue
        if raw_reason.startswith(_V1_SEMANTIC_UNKNOWN_REASON_PREFIXES):
            continue
        if callback_is_unbound and raw_reason.startswith(
            "hit_channel_has_no_present_reader:"
        ):
            continue
        return True
    return False


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest_from_object(value: object) -> str:
    return hashlib.sha256(pretty_json_bytes(value)).hexdigest()


def certificate_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("certificate_sha256", None)
    return digest(body)


def authority_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("authority_sha256", None)
    return digest(body)


def callback_authority_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("authority_sha256", None)
    return digest(body)


def callback_pin_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("pin_sha256", None)
    return digest(body)


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256.fullmatch(value))


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _mapping(value: object) -> Mapping[str, object] | None:
    return value if isinstance(value, Mapping) else None


def _exact_keys(value: object, expected: set[str], label: str, errors: list[str]) -> Mapping[str, object] | None:
    row = _mapping(value)
    if row is None:
        errors.append(f"callback_authority_missing_or_nonobject:{label}")
        return None
    missing = sorted(expected - set(row))
    extra = sorted(set(row) - expected)
    errors.extend(f"callback_authority_missing:{label}.{key}" for key in missing)
    errors.extend(f"callback_authority_unexpected:{label}.{key}" for key in extra)
    return row if not missing and not extra else None


def _plain_nonnegative(value: object, label: str, errors: list[str]) -> int | None:
    if not _is_plain_int(value) or value < 0:
        errors.append(f"callback_authority_invalid_nonnegative_integer:{label}")
        return None
    return value


def _statement_projection(statements: object, label: str, errors: list[str]) -> tuple[int, set[str]]:
    if not isinstance(statements, list):
        errors.append(f"callback_authority_nonlist:{label}")
        return 0, set()
    iterations = 0
    effects: set[str] = set()
    for index, raw in enumerate(statements):
        path = f"{label}[{index}]"
        statement = _mapping(raw)
        if statement is None or not isinstance(statement.get("kind"), str):
            errors.append(f"callback_authority_invalid_statement:{path}")
            continue
        kind = statement["kind"]
        if kind == "let" or kind == "set":
            expected = {"kind", "name", "value"}
        elif kind == "if":
            expected = {"kind", "condition", "then", "else"}
        elif kind == "static_for":
            expected = {"kind", "index", "trip_count", "body"}
        elif kind == "return_effect":
            expected = {"kind", "effect"}
        elif kind == "return_value":
            expected = {"kind", "value"}
        else:
            errors.append(f"callback_authority_unknown_statement_kind:{path}:{kind}")
            continue
        if set(statement) != expected:
            errors.append(f"callback_authority_statement_schema:{path}:{kind}")
            continue
        if kind == "if":
            left_iterations, left_effects = _statement_projection(statement["then"], f"{path}.then", errors)
            right_iterations, right_effects = _statement_projection(statement["else"], f"{path}.else", errors)
            iterations += left_iterations + right_iterations
            effects.update(left_effects)
            effects.update(right_effects)
        elif kind == "static_for":
            trip_count = _plain_nonnegative(statement["trip_count"], f"{path}.trip_count", errors)
            body_iterations, body_effects = _statement_projection(statement["body"], f"{path}.body", errors)
            if trip_count is not None:
                iterations += trip_count * max(1, 1 + body_iterations)
            effects.update(body_effects)
        elif kind == "return_effect":
            effect = _exact_keys(statement["effect"], {"kind", "fields"}, f"{path}.effect", errors)
            if effect is not None:
                effect_kind = effect["kind"]
                if not isinstance(effect_kind, str) or not effect_kind:
                    errors.append(f"callback_authority_invalid_effect_kind:{path}")
                else:
                    effects.add(effect_kind)
                if not isinstance(effect["fields"], Mapping):
                    errors.append(f"callback_authority_invalid_effect_fields:{path}")
    return iterations, effects


def _record_u32_slots(
    type_value: object,
    records: Mapping[str, Mapping[str, object]],
    visiting: frozenset[str],
    label: str,
    errors: list[str],
) -> int | None:
    value = _mapping(type_value)
    if value is None or not isinstance(value.get("kind"), str):
        errors.append(f"callback_authority_invalid_register_type:{label}")
        return None
    kind = value["kind"]
    if kind == "scalar":
        if set(value) != {"kind", "scalar"} or not isinstance(value["scalar"], str):
            errors.append(f"callback_authority_invalid_scalar_type:{label}")
            return None
        return 2 if value["scalar"] in {"i64", "u64", "f64"} else 1
    if kind == "vector":
        if set(value) != {"kind", "lanes", "scalar"}:
            errors.append(f"callback_authority_invalid_vector_type:{label}")
            return None
        lanes = value["lanes"]
        scalar = value["scalar"]
        if not _is_plain_int(lanes) or lanes <= 0 or not isinstance(scalar, str):
            errors.append(f"callback_authority_invalid_vector_layout:{label}")
            return None
        return lanes * (2 if scalar == "f64" else 1)
    if kind == "tuple":
        if set(value) != {"kind", "items"} or not isinstance(value["items"], list):
            errors.append(f"callback_authority_invalid_tuple_type:{label}")
            return None
        total = 0
        for index, item in enumerate(value["items"]):
            slots = _record_u32_slots(item, records, visiting, f"{label}.items[{index}]", errors)
            if slots is None:
                return None
            total += slots
        return total
    if kind == "record":
        if set(value) != {"kind", "name"} or not isinstance(value["name"], str):
            errors.append(f"callback_authority_invalid_record_type:{label}")
            return None
        name = value["name"]
        if name in visiting or name not in records:
            errors.append(f"callback_authority_recursive_or_missing_record:{label}:{name}")
            return None
        total = 0
        fields = records[name].get("fields")
        if not isinstance(fields, list):
            errors.append(f"callback_authority_invalid_record_fields:{name}")
            return None
        for index, field_value in enumerate(fields):
            field = _exact_keys(
                field_value,
                {"name", "type"},
                f"records.{name}.fields[{index}]",
                errors,
            )
            if field is None:
                return None
            slots = _record_u32_slots(
                field["type"], records, visiting | {name}, f"records.{name}.fields[{index}].type", errors
            )
            if slots is None:
                return None
            total += slots
        return total
    errors.append(f"callback_authority_nonregister_layout_type:{label}:{kind}")
    return None


def _walk_expression_values(value: object):
    if isinstance(value, Mapping):
        if isinstance(value.get("opcode"), str):
            yield value
        for nested in value.values():
            yield from _walk_expression_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_expression_values(nested)


def _derive_program_resources(
    program: Mapping[str, object], errors: list[str]
) -> tuple[int | None, int | None, int | None]:
    record_rows = program.get("records")
    manifest = _mapping(program.get("manifest"))
    functions = program.get("functions")
    if not isinstance(record_rows, list) or manifest is None or not isinstance(functions, list):
        errors.append("callback_authority_resource_derivation_inputs_missing")
        return None, None, None
    records: dict[str, Mapping[str, object]] = {}
    for index, raw_record in enumerate(record_rows):
        record = _exact_keys(raw_record, {"name", "purpose", "fields"}, f"records[{index}]", errors)
        if record is None:
            continue
        name = record["name"]
        if not isinstance(name, str) or not name or name in records:
            errors.append(f"callback_authority_invalid_or_duplicate_record:{index}")
            continue
        records[name] = record
    payload_name = manifest.get("payload_record")
    if not isinstance(payload_name, str) or payload_name not in records:
        errors.append("callback_authority_payload_record_missing")
        payload_slots = None
    elif records[payload_name].get("purpose") != "payload":
        errors.append("callback_authority_payload_record_purpose_mismatch")
        payload_slots = None
    else:
        payload_slots = _record_u32_slots(
            {"kind": "record", "name": payload_name}, records, frozenset(), "manifest.payload_record", errors
        )
    attribute_types = manifest.get("attribute_types")
    if not isinstance(attribute_types, list):
        errors.append("callback_authority_attribute_types_nonlist")
        attribute_slots = None
    else:
        attribute_slots = 0
        for index, attribute_type in enumerate(attribute_types):
            slots = _record_u32_slots(
                attribute_type, records, frozenset(), f"manifest.attribute_types[{index}]", errors
            )
            if slots is None:
                attribute_slots = None
                break
            attribute_slots += slots

    function_names: set[str] = set()
    helper_names: set[str] = set()
    function_rows: list[Mapping[str, object]] = []
    for index, raw_function in enumerate(functions):
        function = _mapping(raw_function)
        if function is None or not isinstance(function.get("name"), str):
            errors.append(f"callback_authority_invalid_function_for_call_graph:{index}")
            continue
        name = function["name"]
        if name in function_names:
            errors.append(f"callback_authority_duplicate_function_for_call_graph:{name}")
            continue
        function_names.add(name)
        if function.get("role") is None:
            helper_names.add(name)
        function_rows.append(function)
    graph: dict[str, set[str]] = {name: set() for name in function_names}
    for function in function_rows:
        source = str(function["name"])
        for expression in _walk_expression_values(function.get("body")):
            if expression.get("opcode") != "helper_call":
                continue
            attributes = _mapping(expression.get("attributes"))
            target = None if attributes is None else attributes.get("name")
            if not isinstance(target, str) or target not in helper_names:
                errors.append(f"callback_authority_unknown_helper_call:{source}:{target!r}")
            else:
                graph[source].add(target)
    visiting: set[str] = set()
    memo: dict[str, int] = {}

    def depth(name: str) -> int:
        if name in visiting:
            errors.append(f"callback_authority_recursive_helper:{name}")
            return 0
        if name in memo:
            return memo[name]
        visiting.add(name)
        result = 0 if not graph[name] else 1 + max(depth(target) for target in graph[name])
        visiting.remove(name)
        memo[name] = result
        return result

    helper_depth = max((depth(name) for name in graph), default=0)
    return payload_slots, attribute_slots, helper_depth


def derive_program_projection(
    program_value: object,
    *,
    callback_authority_id: str,
    authority_program_sha256: str,
) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []
    program = _exact_keys(program_value, _PROGRAM_KEYS, "callback_program", errors)
    if program is None:
        return None, errors
    normalized_source = program["normalized_source"]
    if not isinstance(normalized_source, str):
        errors.append("callback_authority_invalid_normalized_source")
    else:
        expected_source_sha = hashlib.sha256(normalized_source.encode("utf-8")).hexdigest()
        if program["source_sha256"] != expected_source_sha:
            errors.append("callback_authority_source_sha256_mismatch")
    ir_body = dict(program)
    ir_body.pop("normalized_source")
    ir_body.pop("source_sha256")
    ir_sha256 = digest(ir_body)
    functions = program["functions"]
    roles: list[dict[str, object]] = []
    effect_rows: list[list[object]] = []
    total_static_iterations = 0
    seen_names: set[str] = set()
    seen_roles: set[str] = set()
    if not isinstance(functions, list):
        errors.append("callback_authority_functions_nonlist")
    else:
        for index, raw_function in enumerate(functions):
            function = _exact_keys(
                raw_function,
                {"name", "role", "arguments", "return_type", "body"},
                f"callback_program.functions[{index}]",
                errors,
            )
            if function is None:
                continue
            name = function["name"]
            role = function["role"]
            if not isinstance(name, str) or not name or name in seen_names:
                errors.append(f"callback_authority_invalid_or_duplicate_function_name:{index}")
                continue
            seen_names.add(name)
            function_iterations, function_effects = _statement_projection(
                function["body"], f"callback_program.functions[{index}].body", errors
            )
            total_static_iterations += function_iterations
            sorted_effects = sorted(function_effects)
            effect_rows.append([name, sorted_effects])
            if role is not None:
                if not isinstance(role, str) or not role or role in seen_roles:
                    errors.append(f"callback_authority_invalid_or_duplicate_role:{index}")
                    continue
                seen_roles.add(role)
                roles.append({"role": role, "effects": sorted_effects})
    manifest = _mapping(program["manifest"])
    resources = None if manifest is None else _mapping(manifest.get("resources"))
    if resources is None:
        errors.append("callback_authority_missing_manifest_resources")
        trace_depth = None
        callable_depth = None
    else:
        trace_depth = _plain_nonnegative(resources.get("max_trace_depth"), "manifest.resources.max_trace_depth", errors)
        callable_depth = _plain_nonnegative(resources.get("max_callable_depth"), "manifest.resources.max_callable_depth", errors)
    projection: dict[str, object] = {
        "callback_authority_id": callback_authority_id,
        "authority_program_sha256": authority_program_sha256,
        "ir_sha256": ir_sha256,
        "effect_digest": digest(effect_rows),
        "roles": roles,
        "trace_depth": trace_depth,
        "callable_depth": callable_depth,
        "total_static_iterations": total_static_iterations,
    }
    payload_slots, attribute_slots, helper_depth = _derive_program_resources(program, errors)
    projection.update(
        {
            "payload_u32_slots": payload_slots,
            "attribute_u32_slots": attribute_slots,
            "helper_call_depth": helper_depth,
        }
    )
    return projection, errors


def _validate_program_row(
    program_sha256: str,
    row_value: object,
    selected_constructor_source_manifest: Mapping[str, object],
    errors: list[str],
) -> tuple[dict[str, object] | None, list[str]]:
    row = _exact_keys(row_value, _PROGRAM_ROW_KEYS, f"programs.{program_sha256}", errors)
    if row is None:
        return None, []
    if not _is_sha(program_sha256) or row["callback_program_sha256"] != program_sha256:
        errors.append(f"callback_authority_program_catalog_key_mismatch:{program_sha256}")
    if not isinstance(row["callback_authority_id"], str) or not row["callback_authority_id"]:
        errors.append(f"callback_authority_invalid_id:{program_sha256}")
    if not isinstance(row["alias"], str) or not row["alias"]:
        errors.append(f"callback_authority_invalid_alias:{program_sha256}")
    producer_paths = row["selected_constructor_source_paths"]
    if not isinstance(producer_paths, list) or not producer_paths or any(
        path not in selected_constructor_source_manifest for path in producer_paths
    ):
        errors.append(f"callback_authority_producer_source_binding_mismatch:{program_sha256}")
    if row["callback_program_sha256"] != digest(row["callback_program"]):
        errors.append(f"callback_authority_program_digest_mismatch:{program_sha256}")
    verified = _exact_keys(row["verified_summary"], _VERIFIED_SUMMARY_KEYS, f"verified_summary.{program_sha256}", errors)
    authoritative_contract = _exact_keys(
        row["callback_contract"],
        _CALLBACK_CONTRACT_KEYS,
        f"authority.callback_contract.{program_sha256}",
        errors,
    )
    derived, derive_errors = derive_program_projection(
        row["callback_program"],
        callback_authority_id=str(row["callback_authority_id"]),
        authority_program_sha256=program_sha256,
    )
    errors.extend(derive_errors)
    leaf_keys: list[str] = []
    if verified is not None and derived is not None:
        for key in (
            "ir_sha256",
            "effect_digest",
            "payload_u32_slots",
            "attribute_u32_slots",
            "total_static_iterations",
            "helper_call_depth",
        ):
            if canonical_bytes(verified[key]) != canonical_bytes(derived[key]):
                errors.append(f"callback_authority_verified_program_mismatch:{program_sha256}:{key}")
        expected_contract = dict(derived)
        for key in ("payload_u32_slots", "attribute_u32_slots", "helper_call_depth"):
            _plain_nonnegative(verified[key], f"verified_summary.{program_sha256}.{key}", errors)
        if authoritative_contract is not None and canonical_bytes(authoritative_contract) != canonical_bytes(expected_contract):
            errors.append(f"callback_authority_contract_not_exact_program_projection:{program_sha256}")
        leaf_rows = row["executed_leaf_evidence"]
        if not isinstance(leaf_rows, list) or not leaf_rows:
            errors.append(f"callback_authority_executed_leaf_evidence_missing:{program_sha256}")
        else:
            leaf_roles: list[str] = []
            expected_leaf_keys = {
                "member_path",
                "file_sha256",
                "size_bytes",
                "key_sha256",
                "role",
                "callback_ir_sha256",
                "callback_effect_digest",
            }
            for index, leaf_value in enumerate(leaf_rows):
                leaf = _exact_keys(
                    leaf_value,
                    expected_leaf_keys,
                    f"executed_leaf_evidence.{program_sha256}[{index}]",
                    errors,
                )
                if leaf is None:
                    continue
                if not _is_sha(leaf["file_sha256"]) or not _is_sha(leaf["key_sha256"]):
                    errors.append(f"callback_authority_executed_leaf_invalid_digest:{program_sha256}:{index}")
                _plain_nonnegative(leaf["size_bytes"], f"executed_leaf_evidence.{program_sha256}[{index}].size_bytes", errors)
                if leaf["callback_ir_sha256"] != derived["ir_sha256"]:
                    errors.append(f"callback_authority_executed_leaf_ir_mismatch:{program_sha256}:{index}")
                if leaf["callback_effect_digest"] != derived["effect_digest"]:
                    errors.append(f"callback_authority_executed_leaf_effect_mismatch:{program_sha256}:{index}")
                if isinstance(leaf["role"], str):
                    leaf_roles.append(leaf["role"])
                else:
                    errors.append(f"callback_authority_executed_leaf_role_invalid:{program_sha256}:{index}")
                if isinstance(leaf["key_sha256"], str):
                    leaf_keys.append(leaf["key_sha256"])
            expected_roles = [item["role"] for item in expected_contract["roles"]]
            if sorted(leaf_roles) != sorted(expected_roles):
                errors.append(f"callback_authority_executed_leaf_role_set_mismatch:{program_sha256}")
        return expected_contract, leaf_keys
    return None, leaf_keys


def _validate_callback_binding(
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    unknowns: list[str] = []
    if set(certificate) != _CERTIFICATE_KEYS:
        errors.append("callback_authority_certificate_top_schema")
    if certificate.get("schema") != CERTIFICATE_SCHEMA:
        errors.append("callback_authority_certificate_schema_identity")
    if certificate_digest(certificate) != certificate.get("certificate_sha256"):
        errors.append("callback_authority_certificate_digest_mismatch")
    if set(authority) != _AUTHORITY_KEYS:
        errors.append("callback_authority_bundle_top_schema")
    if authority.get("schema") != AUTHORITY_SCHEMA:
        errors.append("callback_authority_bundle_schema_identity")
    if authority_digest(authority) != authority.get("authority_sha256"):
        errors.append("callback_authority_bundle_digest_mismatch")

    auth = _exact_keys(callback_authority, _CALLBACK_AUTHORITY_KEYS, "callback_ir_authority", errors)
    pin = _exact_keys(callback_pin, _CALLBACK_PIN_KEYS, "callback_ir_authority_pin", errors)
    binding = _exact_keys(authority.get("callback_ir_authority_binding"), _CALLBACK_BINDING_KEYS, "callback_ir_authority_binding", errors)
    if auth is None or pin is None or binding is None:
        return errors, unknowns
    if auth["schema"] != CALLBACK_AUTHORITY_SCHEMA:
        errors.append("callback_authority_schema_identity")
    if callback_authority_digest(auth) != auth["authority_sha256"]:
        errors.append("callback_authority_digest_mismatch")
    if pin["schema"] != CALLBACK_AUTHORITY_PIN_SCHEMA:
        errors.append("callback_authority_pin_schema_identity")
    if callback_pin_digest(pin) != pin["pin_sha256"]:
        errors.append("callback_authority_pin_digest_mismatch")
    if binding["schema"] != CALLBACK_BINDING_SCHEMA:
        errors.append("callback_authority_binding_schema_identity")
    if v1.nested_authority_digest(binding) != binding["authority_sha256"]:
        errors.append("callback_authority_binding_digest_mismatch")
    if canonical_bytes(auth["claim_boundary"]) != canonical_bytes(
        EXPECTED_CALLBACK_AUTHORITY_CLAIM_BOUNDARY
    ):
        errors.append("callback_authority_claim_boundary_not_exact")
    for field, expected in (
        ("source_archive", EXPECTED_SOURCE_ARCHIVE_IDENTITY),
        ("execution_evidence_archive", EXPECTED_EXECUTION_EVIDENCE_IDENTITY),
        ("controlling_result", EXPECTED_CONTROLLING_RESULT_IDENTITY),
    ):
        if canonical_bytes(auth[field]) != canonical_bytes(expected):
            errors.append(f"callback_authority_reviewed_root_identity_mismatch:{field}")
    if binding["callback_authority_path"] != EXPECTED_CALLBACK_AUTHORITY_PATH:
        errors.append("callback_authority_binding_path_mismatch")
    if binding["callback_authority_pin_path"] != EXPECTED_CALLBACK_PIN_PATH:
        errors.append("callback_authority_binding_pin_path_mismatch")

    expected_binding = {
        "callback_authority_file_sha256": file_digest_from_object(auth),
        "callback_authority_sha256": auth["authority_sha256"],
        "callback_authority_pin_file_sha256": file_digest_from_object(pin),
        "callback_authority_pin_sha256": pin["pin_sha256"],
    }
    for key, expected in expected_binding.items():
        if binding[key] != expected:
            errors.append(f"callback_authority_binding_identity_mismatch:{key}")
    pin_authority = _exact_keys(
        pin["callback_authority"],
        {"path", "size_bytes", "file_sha256", "authority_sha256"},
        "callback_ir_authority_pin.callback_authority",
        errors,
    )
    if pin_authority is None:
        errors.append("callback_authority_pin_missing_authority_identity")
    else:
        if pin_authority["path"] != EXPECTED_CALLBACK_AUTHORITY_PATH:
            errors.append("callback_authority_pin_path_mismatch")
        _plain_nonnegative(
            pin_authority["size_bytes"],
            "callback_ir_authority_pin.callback_authority.size_bytes",
            errors,
        )
        for key, expected in (
            ("file_sha256", expected_binding["callback_authority_file_sha256"]),
            ("authority_sha256", auth["authority_sha256"]),
        ):
            if pin_authority.get(key) != expected:
                errors.append(f"callback_authority_pin_identity_mismatch:{key}")
    if pin["source_archive"] != auth["source_archive"]:
        errors.append("callback_authority_source_archive_pin_mismatch")
    if pin["execution_evidence_archive"] != auth["execution_evidence_archive"]:
        errors.append("callback_authority_execution_evidence_pin_mismatch")
    if pin["controlling_result"] != auth["controlling_result"]:
        errors.append("callback_authority_controlling_result_pin_mismatch")
    authorization = _mapping(pin["authorization"])
    if canonical_bytes(authorization) != canonical_bytes(EXPECTED_CALLBACK_PIN_AUTHORIZATION):
        errors.append("callback_authority_pin_authorization_not_exact_false")

    source_manifest = _mapping(auth["selected_constructor_source_manifest"])
    consumer_source_manifest = _mapping(auth["consumer_source_manifest"])
    consumer_source_roots = _mapping(auth["consumer_source_authority_roots"])
    programs = _mapping(auth["programs"])
    if (
        source_manifest is None
        or consumer_source_manifest is None
        or consumer_source_roots is None
        or programs is None
    ):
        errors.append("callback_authority_catalog_missing")
        return errors, unknowns
    heldout_root = _exact_keys(
        consumer_source_roots.get("goal5789_heldout_certificate")
        if set(consumer_source_roots) == {"goal5789_heldout_certificate"}
        else None,
        {"path", "size_bytes", "file_sha256", "certificate_sha256"},
        "consumer_source_authority_roots.goal5789_heldout_certificate",
        errors,
    )
    if heldout_root is not None:
        if not _is_sha(heldout_root["file_sha256"]) or not _is_sha(heldout_root["certificate_sha256"]):
            errors.append("callback_authority_consumer_source_root_digest_invalid")
        _plain_nonnegative(
            heldout_root["size_bytes"],
            "consumer_source_authority_roots.goal5789_heldout_certificate.size_bytes",
            errors,
        )
        if not isinstance(heldout_root["path"], str) or not heldout_root["path"]:
            errors.append("callback_authority_consumer_source_root_path_invalid")
    for path in set(source_manifest) & set(consumer_source_manifest):
        if source_manifest[path] != consumer_source_manifest[path]:
            errors.append(f"callback_authority_overlapping_source_identity_mismatch:{path}")
    for path, sha256 in {**source_manifest, **consumer_source_manifest}.items():
        if not isinstance(path, str) or not path or not _is_sha(sha256):
            errors.append("callback_authority_invalid_source_manifest_row")

    if set(programs) != EXPECTED_PROGRAM_SHA256S:
        errors.append("callback_authority_program_universe_count_mismatch")
    derived_contracts: dict[str, dict[str, object]] = {}
    all_leaf_keys: list[str] = []
    for program_sha256, row_value in programs.items():
        if not isinstance(program_sha256, str):
            errors.append("callback_authority_nonstring_program_key")
            continue
        if isinstance(row_value, Mapping):
            actual_metadata = {
                key: row_value.get(key)
                for key in (
                    "alias",
                    "callback_authority_id",
                    "compile_entrypoint",
                    "selected_constructor_source_paths",
                )
            }
            expected_metadata = EXPECTED_PROGRAM_METADATA_BY_SHA256.get(program_sha256)
            if expected_metadata is None or canonical_bytes(actual_metadata) != canonical_bytes(
                expected_metadata
            ):
                errors.append(
                    f"callback_authority_program_metadata_exact_identity_mismatch:{program_sha256}"
                )
        contract, leaf_keys = _validate_program_row(program_sha256, row_value, source_manifest, errors)
        all_leaf_keys.extend(leaf_keys)
        if contract is not None:
            derived_contracts[program_sha256] = contract
    leaf_manifest = _exact_keys(
        auth["execution_leaf_manifest"],
        {"member_path", "file_sha256", "size_bytes", "entry_count", "entries_sha256"},
        "execution_leaf_manifest",
        errors,
    )
    if leaf_manifest is not None:
        if canonical_bytes(leaf_manifest) != canonical_bytes(
            EXPECTED_EXECUTION_LEAF_MANIFEST_IDENTITY
        ):
            errors.append("callback_authority_execution_leaf_manifest_identity_mismatch")
        if leaf_manifest["entry_count"] != 26 or len(all_leaf_keys) != 26:
            errors.append("callback_authority_leaf_universe_count_mismatch")
        if len(all_leaf_keys) != len(set(all_leaf_keys)):
            errors.append("callback_authority_leaf_universe_duplicate")

    bindings = auth["admitted_bindings"]
    if not isinstance(bindings, list) or len(bindings) != 4:
        errors.append("callback_authority_admitted_binding_count_mismatch")
        bindings = []
    elif canonical_bytes(bindings) != canonical_bytes(EXPECTED_ADMITTED_BINDINGS):
        errors.append("callback_authority_admitted_binding_exact_mapping_mismatch")
    binding_rows: list[Mapping[str, object]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for index, binding_value in enumerate(bindings):
        admitted = _exact_keys(
            binding_value,
            {
                "semantic_contract_id",
                "physical_encoding_id",
                "authority_program_sha256",
                "callback_authority_id",
                "consumer_source_witnesses",
            },
            f"admitted_bindings[{index}]",
            errors,
        )
        if admitted is None:
            continue
        pair = (str(admitted["semantic_contract_id"]), str(admitted["physical_encoding_id"]))
        if pair in seen_pairs:
            errors.append("callback_authority_duplicate_admitted_binding")
        seen_pairs.add(pair)
        program_sha = admitted["authority_program_sha256"]
        contract = derived_contracts.get(str(program_sha))
        if contract is None:
            errors.append(f"callback_authority_binding_program_missing:{index}")
        elif admitted["callback_authority_id"] != contract["callback_authority_id"]:
            errors.append(f"callback_authority_binding_id_mismatch:{index}")
        witnesses = admitted["consumer_source_witnesses"]
        if not isinstance(witnesses, list) or not witnesses:
            errors.append(f"callback_authority_binding_consumer_witness_missing:{index}")
        else:
            seen_witness_paths: set[str] = set()
            for witness_index, witness_value in enumerate(witnesses):
                witness = _exact_keys(
                    witness_value,
                    {"source_path", "source_sha256", "source_root", "required_tokens"},
                    f"admitted_bindings[{index}].consumer_source_witnesses[{witness_index}]",
                    errors,
                )
                if witness is None:
                    continue
                source_path = witness["source_path"]
                if not isinstance(source_path, str) or source_path in seen_witness_paths:
                    errors.append(f"callback_authority_binding_consumer_path_invalid:{index}:{witness_index}")
                else:
                    seen_witness_paths.add(source_path)
                if consumer_source_manifest.get(source_path) != witness["source_sha256"]:
                    errors.append(f"callback_authority_binding_consumer_hash_mismatch:{index}:{witness_index}")
                if witness["source_root"] not in {
                    "goal5785_execution_source_archive",
                    "goal5789_heldout_certificate_source_pin",
                }:
                    errors.append(f"callback_authority_binding_consumer_root_invalid:{index}:{witness_index}")
                tokens = witness["required_tokens"]
                if (
                    not isinstance(tokens, list)
                    or not tokens
                    or any(not isinstance(token, str) or not token for token in tokens)
                    or len(tokens) != len(set(tokens))
                ):
                    errors.append(f"callback_authority_binding_consumer_tokens_invalid:{index}:{witness_index}")
        binding_rows.append(admitted)

    semantic = _mapping(certificate.get("semantic_request"))
    physical = _mapping(certificate.get("physical_encoding"))
    if semantic is None or physical is None:
        errors.append("callback_authority_certificate_pair_missing")
        return errors, unknowns
    pair = (semantic.get("contract_id"), physical.get("encoding_id"))
    selected = [row for row in binding_rows if (row["semantic_contract_id"], row["physical_encoding_id"]) == pair]
    if len(selected) == 0:
        if certificate.get("callback_contract") is not None:
            errors.append("callback_contract_present_without_admitted_semantic_physical_binding")
        unknowns.append("callback_authority_not_established_for_semantic_physical_pair")
        return errors, unknowns
    if len(selected) != 1:
        errors.append("callback_authority_ambiguous_semantic_physical_binding")
        return errors, unknowns
    callback = _exact_keys(certificate.get("callback_contract"), _CALLBACK_CONTRACT_KEYS, "callback_contract", errors)
    selected_contract = derived_contracts.get(str(selected[0]["authority_program_sha256"]))
    if callback is None or selected_contract is None:
        return errors, unknowns
    for key in (
        "payload_u32_slots",
        "attribute_u32_slots",
        "trace_depth",
        "callable_depth",
        "total_static_iterations",
        "helper_call_depth",
    ):
        _plain_nonnegative(callback[key], f"callback_contract.{key}", errors)
    if canonical_bytes(callback) != canonical_bytes(selected_contract):
        errors.append("callback_contract_authority_mismatch")
    return errors, unknowns


def _translate_to_v1(
    certificate: Mapping[str, object], authority: Mapping[str, object]
) -> tuple[dict[str, object], dict[str, object]]:
    old_certificate = deepcopy(dict(certificate))
    old_certificate["schema"] = v1.CERTIFICATE_SCHEMA
    callback = old_certificate.get("callback_contract")
    if isinstance(callback, dict):
        callback.pop("callback_authority_id", None)
        callback.pop("authority_program_sha256", None)
        callback.pop("helper_call_depth", None)
    old_certificate["certificate_sha256"] = v1.certificate_digest(old_certificate)
    old_authority = deepcopy(dict(authority))
    old_authority["schema"] = v1.AUTHORITY_SCHEMA
    old_authority.pop("callback_ir_authority_binding", None)
    old_authority["authority_sha256"] = v1.authority_digest(old_authority)
    return old_certificate, old_authority


def evaluate_certificate(
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
) -> dict[str, object]:
    callback_errors, callback_unknowns = _validate_callback_binding(
        certificate, authority, callback_authority, callback_pin
    )
    old_certificate, old_authority = _translate_to_v1(certificate, authority)
    result = v1.evaluate_certificate(old_certificate, old_authority)
    result["schema"] = RESULT_SCHEMA
    result["certificate_sha256"] = certificate.get("certificate_sha256")
    result["authority_sha256"] = authority.get("authority_sha256")
    result["callback_authority_sha256"] = callback_authority.get("authority_sha256")
    result["callback_authority_pin_sha256"] = callback_pin.get("pin_sha256")
    if callback_errors:
        existing = list(result["semantic_compatible"]["reasons"])
        result["semantic_compatible"] = {
            "verdict": INCOMPATIBLE,
            "reasons": list(dict.fromkeys(existing + callback_errors)),
        }
        result["reference_admission_complete"] = False
    elif callback_unknowns:
        existing = list(result["semantic_compatible"]["reasons"])
        # A missing Callback-IR binding is an additional reason to remain
        # UNKNOWN only when the predecessor calculus has not already proved
        # the declaration inconsistent.  Never let an unbound callback mask
        # a stronger INCOMPATIBLE verdict.
        inherited_verdict = result["semantic_compatible"]["verdict"]
        proven_incompatible = (
            inherited_verdict == INCOMPATIBLE
            or _v1_has_proven_semantic_incompatibility(
                existing, callback_is_unbound=certificate.get("callback_contract") is None
            )
        )
        result["semantic_compatible"] = {
            "verdict": INCOMPATIBLE if proven_incompatible else UNKNOWN,
            "reasons": list(dict.fromkeys(existing + callback_unknowns)),
        }
        result["reference_admission_complete"] = False
    result["authority_boundary"] = (
        "reference-admission replay with exact source-backed Callback-IR authority binding; "
        "authority producers and external authority roots remain TCB; no executable authority, "
        "soundness, completeness, or jointly-wrong-authority detection is claimed"
    )
    result.pop("result_sha256", None)
    result["result_sha256"] = digest(result)
    return result


def _load_json(path: Path) -> Mapping[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: JSON object required")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--callback-authority", type=Path, required=True)
    parser.add_argument("--callback-authority-pin", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_certificate(
        _load_json(args.certificate),
        _load_json(args.authority),
        _load_json(args.callback_authority),
        _load_json(args.callback_authority_pin),
    )
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    return 0 if result["reference_admission_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
