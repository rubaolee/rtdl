"""Candidate-agnostic X1 registry-template and seven-slot derivation.

The concrete X1 authority is reconstructed only from exact Goal5789-A2
postreview packet bytes.  Matching never reads a row id, expected outcome,
role, source index, citation key, or candidate hash.  A receipt is valid only
when one frozen scientific/family template matches and all seven mechanical
identity slots rederive from the submitted declarations.

The concrete authority is a historical positive fixture authority.  A future
expanded-row authority must be separately frozen and reviewed before it can be
pinned by a future controlling runner; callers cannot self-declare one here.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
A2_ROOT = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
PACKET_MANIFEST_PATH = (
    ROOT
    / "history/internal_docs/goal5789_a2_postreview_repair_packet_v1_manifest_20260822.json"
)
EXPECTED_PACKET_MANIFEST_SHA256 = (
    "f33ddfcad448c4f8954751e627d2448bd3070a2ac7f26476f9bd758798762c04"
)
CANONICAL_PATH = ROOT / "scripts/goal5793_x1_canonical.py"
V1_CHECKER_PATH = ROOT / "scripts/goal5789_independent_compatibility_checker.py"
EXPECTED_CANONICAL_SHA256 = (
    "13b22dbae22b0a70763fdf46031c7975ab1eaebe20c37789f397242b7a1c9b3a"
)
EXPECTED_V1_CHECKER_SHA256 = (
    "abb1f1575af824cc37e9d9984aff8679f79cb89f4ad7ed2792ede5a3db75ac2e"
)
REGISTRY_SCHEMA = "rtdl.goal5793.x1.registry_derivation_authority.v1"
RECEIPT_SCHEMA = "rtdl.goal5793.x1.registry_derivation_receipt.v1"
STAGE_PIN_SCHEMA = "rtdl.goal5793.x1.presearch_registry_stage_pin.v1"
EXAM_INPUT_SCHEMA = "rtdl.goal5793.x1.generic_examiner_input.v1"
ALLOWED_IDENTITY_SLOTS = (
    "ir_digest",
    "effect_digest",
    "schema_digest",
    "abi_digest",
    "plan_digest",
    "native_digest",
    "source_digest",
)
POSITIVE_IDS = (
    "particle__microfluidics_5000",
    "triangle__com_dblp__rt_2a1",
    "triangle__cit_patents__rt_2a1",
    "triangle__soc_livejournal1__rt_2a1",
    "librts__parks_point_contains",
    "librts__parks_range_contains",
)
HELD_OUT_ROW = "legacy_held_out__rtxrmq"

class RegistryDerivationError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_exact(path: Path, name: str, expected: str):
    resolved = path.resolve(strict=True)
    if _sha256(resolved) != expected:
        raise RegistryDerivationError(f"dependency_hash_mismatch:{resolved}")
    spec = importlib.util.spec_from_file_location(name, resolved)
    if spec is None or spec.loader is None:
        raise RegistryDerivationError(f"dependency_spec_unavailable:{resolved}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    if Path(module.__file__).resolve(strict=True) != resolved:
        raise RegistryDerivationError(f"dependency_origin_mismatch:{resolved}")
    return module


canonical = _load_exact(
    CANONICAL_PATH, "_goal5793_x1_registry_canonical", EXPECTED_CANONICAL_SHA256
)
v1 = _load_exact(
    V1_CHECKER_PATH, "_goal5793_x1_registry_v1_checker", EXPECTED_V1_CHECKER_SHA256
)


DERIVATION_PROTOCOL = {
    "name": "goal5793_x1_identity_free_scientific_template_seven_slot_v1",
    "canonical_helper_sha256": EXPECTED_CANONICAL_SHA256,
    "reference_overlap_checker_sha256": EXPECTED_V1_CHECKER_SHA256,
    "callback_program_projection": (
        "exact_known_callback_ir_schema__unknown_keys_fail_closed__"
        "normalized_source_source_sha256_and_program_label_omitted"
    ),
    "facade_classifier": (
        "geometry_family_plus_semantic_output_type_and_multiplicity_only"
    ),
    "postfreeze_identity_slot_count": 7,
    "candidate_metadata_or_expected_outcome_used": False,
}

DECLARATION_RULE_REPLAY_SUMMARY = {
    "enum_total": 39,
    "declaration_reached_count": 35,
    "REACHED": [
        "SP000_MALFORMED_INPUT",
        "SP001_SEMANTIC_REQUIREMENT_UNKNOWN",
        "SP002_PHYSICAL_GUARANTEE_UNKNOWN",
        "SP003_LIVE_BINDING_UNKNOWN",
        "SP004_CANONICAL_CANDIDATES_UNKNOWN",
        "SP010_IDENTITY_INVALID",
        "SP011_DIGEST_INVALID",
        "SP020_POLICY_INCOMPLETE",
        "SP021_POLICY_UNSUPPORTED_FIELD",
        "SP023_REQUIRED_HIT_SEMANTIC_MISSING",
        "SP024_EXACTNESS_POLICY_MISMATCH",
        "SP025_TIE_POLICY_MISMATCH",
        "SP026_MULTIPLICITY_POLICY_MISMATCH",
        "SP027_OVERFLOW_POLICY_MISMATCH",
        "SP028_NUMERIC_PRECISION_POLICY_MISMATCH",
        "SP029_ORDER_POLICY_MISMATCH",
        "SP030_MAP_STAGE_UNKNOWN",
        "SP031_MAP_STAGE_DUPLICATE",
        "SP032_MAP_GRAPH_MISMATCH",
        "SP033_MAP_SOURCE_UNKNOWN",
        "SP034_MAP_SOURCE_DIGEST_MISMATCH",
        "SP035_INPUT_TYPE_POLICY_MISMATCH",
        "SP036_OUTPUT_TYPE_POLICY_MISMATCH",
        "SP037_ALGORITHM_IDENTITY_MISMATCH",
        "SP038_DECLARED_DOMAIN_MISMATCH",
        "SP039_ORIENTATION_CONTRACT_MISMATCH",
        "SP040_GAS_CONTRACT_MISMATCH",
        "SP041_MAP_SOURCE_UNUSED",
        "SP050_CALLBACK_BINDING_MISMATCH",
        "SP051_SCHEMA_BINDING_MISMATCH",
        "SP052_TARGET_PROVIDER_MISMATCH",
        "SP053_TARGET_CAPABILITY_MISSING",
        "SP060_CANONICAL_CANDIDATE_UNSUPPORTED",
        "SP061_CANONICAL_CANDIDATE_AMBIGUOUS",
        "SP062_CANONICAL_LIVE_BINDING_MISMATCH",
    ],
    "UNREACHABLE_BY_CURRENT_CODE": [
        "SP022_SEMANTIC_GUARANTEE_MISMATCH",
    ],
    "AUTHORITY_ONLY": [
        "SP063_PHYSICAL_AUTHORITY_NONCANONICAL",
        "SP070_AUTHORITY_NOT_LIVE",
        "SP071_AUTHORITY_BINDING_DRIFT",
    ],
    "claim": (
        "35 declaration rules replayed; SP022 closed-policy fallback is "
        "unreachable; SP063/SP070/SP071 are authority-only; never 39/39 generic"
    ),
}


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RegistryDerivationError(f"expected_object:{path}")
    return value


def _record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _packet_payloads() -> dict[str, Mapping[str, object]]:
    if _sha256(PACKET_MANIFEST_PATH) != EXPECTED_PACKET_MANIFEST_SHA256:
        raise RegistryDerivationError("packet_manifest_hash_mismatch")
    manifest = _json(PACKET_MANIFEST_PATH)
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or len(rows) != manifest.get("payload_count"):
        raise RegistryDerivationError("packet_manifest_count_mismatch")
    indexed: dict[str, Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("path"), str):
            raise RegistryDerivationError("packet_manifest_row_malformed")
        path = str(row["path"])
        if path in indexed:
            raise RegistryDerivationError("packet_manifest_duplicate_path")
        indexed[path] = row
    return indexed


def _packet_record(path: Path, payloads: Mapping[str, Mapping[str, object]]):
    rel = path.relative_to(ROOT).as_posix()
    frozen = payloads.get(rel)
    if frozen is None:
        raise RegistryDerivationError(f"packet_payload_missing:{rel}")
    observed = _record(path)
    if observed["bytes"] != frozen.get("bytes") \
            or observed["sha256"] != frozen.get("sha256"):
        raise RegistryDerivationError(f"packet_payload_drift:{rel}")
    return observed


def _digest(value: object, domain: str, projection: str) -> str:
    return str(canonical.canonical_digest(
        value, domain=domain, version=1, projection=projection
    )["sha256"])


def _normalize_a2_to_v1(
    certificate: Mapping[str, object], authority: Mapping[str, object]
) -> tuple[dict[str, object], dict[str, object]]:
    normalized_certificate = deepcopy(dict(certificate))
    normalized_certificate["schema"] = v1.CERTIFICATE_SCHEMA
    callback = normalized_certificate.get("callback_contract")
    if isinstance(callback, dict):
        for key in (
            "callback_authority_id",
            "authority_program_sha256",
            "helper_call_depth",
        ):
            callback.pop(key, None)
    normalized_certificate["certificate_sha256"] = v1.certificate_digest(
        normalized_certificate
    )
    normalized_authority = deepcopy(dict(authority))
    normalized_authority["schema"] = v1.AUTHORITY_SCHEMA
    normalized_authority.pop("callback_ir_authority_binding", None)
    normalized_authority["authority_sha256"] = v1.authority_digest(
        normalized_authority
    )
    return normalized_certificate, normalized_authority


def _scientific_projection(
    certificate: Mapping[str, object], callback_program: Mapping[str, object]
) -> dict[str, object]:
    semantic = deepcopy(certificate["semantic_request"])
    physical = deepcopy(certificate["physical_encoding"])
    callback = deepcopy(certificate["callback_contract"])
    candidates = deepcopy(certificate["canonical_candidates"])
    target = deepcopy(certificate["target_contract"])
    semantic.pop("specification_source_pin", None)
    physical.pop("schema_sha256", None)
    physical.pop("provider_source_pin", None)
    for edge in physical["maps"]:
        edge.pop("source_pin", None)
        edge.pop("source_sha256", None)
    callback.pop("ir_sha256", None)
    callback.pop("effect_digest", None)
    for candidate in candidates:
        candidate.pop("schema_sha256", None)
    target.pop("target_sha256", None)
    target.pop("native_sha256", None)
    return {
        "semantic_obligation": semantic,
        "physical_guarantee": physical,
        "callback_roles_resources": callback,
        "canonical_registry_template": candidates,
        "target_capability_shape": target,
        "callback_program_structure": _callback_program_structure(callback_program),
    }


def _exact_mapping(
    value: object, expected: set[str], context: str
) -> Mapping[str, object]:
    """Require the frozen Callback-IR schema, including absence of new keys."""

    if not isinstance(value, Mapping) or set(value) != expected:
        observed = sorted(str(key) for key in value) \
            if isinstance(value, Mapping) else type(value).__name__
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}:{observed}"
        )
    if not all(isinstance(key, str) for key in value):
        raise RegistryDerivationError(
            f"callback_program_nonstring_key:{context}"
        )
    return value


def _exact_list(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}:not_list"
        )
    return value


def _project_ir_type(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, Mapping) or not isinstance(value.get("kind"), str):
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}:type"
        )
    kind = value["kind"]
    keys_by_kind = {
        "scalar": {"kind", "scalar"},
        "vector": {"kind", "lanes", "scalar"},
        "builtin": {"kind", "name"},
        "record": {"kind", "name"},
        "tuple": {"kind", "items"},
        "read_only_view": {"kind", "items"},
    }
    if kind not in keys_by_kind:
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}:unknown_type:{kind}"
        )
    row = _exact_mapping(value, keys_by_kind[kind], context)
    projected = deepcopy(dict(row))
    if "items" in row:
        projected["items"] = [
            _project_ir_type(item, f"{context}.items[{index}]")
            for index, item in enumerate(_exact_list(row["items"], context))
        ]
    return projected


def _project_expression(value: object, context: str) -> dict[str, object]:
    row = _exact_mapping(
        value, {"attributes", "opcode", "operands", "type"}, context
    )
    attributes = row["attributes"]
    if not isinstance(attributes, Mapping) or not set(attributes).issubset(
        {"field_names", "name", "value"}
    ):
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}.attributes"
        )
    if not all(isinstance(key, str) for key in attributes):
        raise RegistryDerivationError(
            f"callback_program_nonstring_key:{context}.attributes"
        )
    operands = _exact_list(row["operands"], f"{context}.operands")
    return {
        "attributes": deepcopy(dict(attributes)),
        "opcode": deepcopy(row["opcode"]),
        "operands": [
            _project_expression(child, f"{context}.operands[{index}]")
            for index, child in enumerate(operands)
        ],
        "type": _project_ir_type(row["type"], f"{context}.type"),
    }


_EFFECT_FIELD_NAMES = {
    "attributes", "direction", "hit_kind", "lower", "origin", "payload",
    "t", "tmax", "tmin", "upper", "value",
}


def _project_effect(value: object, context: str) -> dict[str, object]:
    row = _exact_mapping(value, {"fields", "kind"}, context)
    fields = row["fields"]
    if not isinstance(fields, Mapping) or not set(fields).issubset(
        _EFFECT_FIELD_NAMES
    ):
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}.fields"
        )
    return {
        "fields": {
            key: _project_expression(child, f"{context}.fields.{key}")
            for key, child in fields.items()
        },
        "kind": deepcopy(row["kind"]),
    }


def _project_statement(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise RegistryDerivationError(
            f"callback_program_schema_mismatch:{context}:statement"
        )
    kind = value.get("kind")
    if kind == "let":
        row = _exact_mapping(value, {"kind", "name", "value"}, context)
        return {
            "kind": "let",
            "name": deepcopy(row["name"]),
            "value": _project_expression(row["value"], f"{context}.value"),
        }
    if kind == "return_effect":
        row = _exact_mapping(value, {"effect", "kind"}, context)
        return {
            "effect": _project_effect(row["effect"], f"{context}.effect"),
            "kind": "return_effect",
        }
    if kind == "if":
        row = _exact_mapping(
            value, {"condition", "else", "kind", "then"}, context
        )
        return {
            "condition": _project_expression(
                row["condition"], f"{context}.condition"
            ),
            "else": [
                _project_statement(child, f"{context}.else[{index}]")
                for index, child in enumerate(
                    _exact_list(row["else"], f"{context}.else")
                )
            ],
            "kind": "if",
            "then": [
                _project_statement(child, f"{context}.then[{index}]")
                for index, child in enumerate(
                    _exact_list(row["then"], f"{context}.then")
                )
            ],
        }
    raise RegistryDerivationError(
        f"callback_program_schema_mismatch:{context}:unknown_statement:{kind}"
    )


def _project_function(value: object, context: str) -> dict[str, object]:
    row = _exact_mapping(
        value, {"arguments", "body", "name", "return_type", "role"}, context
    )
    arguments = []
    for index, argument in enumerate(
        _exact_list(row["arguments"], f"{context}.arguments")
    ):
        argument_context = f"{context}.arguments[{index}]"
        argument_row = _exact_mapping(
            argument, {"name", "type"}, argument_context
        )
        arguments.append({
            "name": deepcopy(argument_row["name"]),
            "type": _project_ir_type(
                argument_row["type"], f"{argument_context}.type"
            ),
        })
    return_type = row["return_type"]
    if return_type is not None:
        return_type = _project_ir_type(return_type, f"{context}.return_type")
    return {
        "arguments": arguments,
        "body": [
            _project_statement(child, f"{context}.body[{index}]")
            for index, child in enumerate(
                _exact_list(row["body"], f"{context}.body")
            )
        ],
        "name": deepcopy(row["name"]),
        "return_type": return_type,
        "role": deepcopy(row["role"]),
    }


def _project_record(value: object, context: str) -> dict[str, object]:
    row = _exact_mapping(value, {"fields", "name", "purpose"}, context)
    fields = []
    for index, field in enumerate(_exact_list(row["fields"], f"{context}.fields")):
        field_context = f"{context}.fields[{index}]"
        field_row = _exact_mapping(field, {"name", "type"}, field_context)
        fields.append({
            "name": deepcopy(field_row["name"]),
            "type": _project_ir_type(field_row["type"], f"{field_context}.type"),
        })
    return {
        "fields": fields,
        "name": deepcopy(row["name"]),
        "purpose": deepcopy(row["purpose"]),
    }


def _project_manifest(value: object) -> dict[str, object]:
    row = _exact_mapping(value, {
        "any_hit_delivery", "attribute_types", "constants", "geometry",
        "linkage_selection_reason", "name", "numeric", "output_record",
        "payload_record", "resources", "selected_linkage",
    }, "program.manifest")
    geometry = _exact_mapping(row["geometry"], {
        "admission", "contract_name", "proof_sha256",
        "target_f32_outward_rounding",
    }, "program.manifest.geometry")
    # A non-null proof would be an eighth post-freeze identity, so v1 rejects it.
    if geometry["proof_sha256"] is not None:
        raise RegistryDerivationError(
            "callback_program_unregistered_geometry_proof_identity"
        )
    numeric = _exact_mapping(row["numeric"], {
        "implicit_fast_math", "integer_overflow", "nonfinite_effect",
        "nonfinite_input", "strict_f32",
    }, "program.manifest.numeric")
    resources = _exact_mapping(row["resources"], {
        "max_attribute_u32_slots", "max_callable_depth",
        "max_helper_call_depth", "max_payload_u32_slots",
        "max_static_loop_trip_count", "max_total_static_iterations",
        "max_trace_depth",
    }, "program.manifest.resources")
    constants = []
    for index, constant in enumerate(
        _exact_list(row["constants"], "program.manifest.constants")
    ):
        context = f"program.manifest.constants[{index}]"
        constant_row = _exact_mapping(
            constant, {"name", "type", "value"}, context
        )
        constants.append({
            "name": deepcopy(constant_row["name"]),
            "type": _project_ir_type(constant_row["type"], f"{context}.type"),
            "value": deepcopy(constant_row["value"]),
        })
    return {
        "any_hit_delivery": deepcopy(row["any_hit_delivery"]),
        "attribute_types": [
            _project_ir_type(child, f"program.manifest.attribute_types[{index}]")
            for index, child in enumerate(
                _exact_list(row["attribute_types"], "program.manifest.attribute_types")
            )
        ],
        "constants": constants,
        "geometry": {
            "admission": deepcopy(geometry["admission"]),
            "contract_name": deepcopy(geometry["contract_name"]),
            "target_f32_outward_rounding": deepcopy(
                geometry["target_f32_outward_rounding"]
            ),
        },
        "linkage_selection_reason": deepcopy(row["linkage_selection_reason"]),
        # manifest.name is a program label, not a scientific structure field.
        "numeric": deepcopy(dict(numeric)),
        "output_record": deepcopy(row["output_record"]),
        "payload_record": deepcopy(row["payload_record"]),
        "resources": deepcopy(dict(resources)),
        "selected_linkage": deepcopy(row["selected_linkage"]),
    }


def _validate_projected_manifest(value: object) -> dict[str, object]:
    """Validate the exact output schema of :func:`_project_manifest`."""

    row = _exact_mapping(value, {
        "any_hit_delivery", "attribute_types", "constants", "geometry",
        "linkage_selection_reason", "numeric", "output_record",
        "payload_record", "resources", "selected_linkage",
    }, "program.manifest")
    geometry = _exact_mapping(row["geometry"], {
        "admission", "contract_name", "target_f32_outward_rounding",
    }, "program.manifest.geometry")
    numeric = _exact_mapping(row["numeric"], {
        "implicit_fast_math", "integer_overflow", "nonfinite_effect",
        "nonfinite_input", "strict_f32",
    }, "program.manifest.numeric")
    resources = _exact_mapping(row["resources"], {
        "max_attribute_u32_slots", "max_callable_depth",
        "max_helper_call_depth", "max_payload_u32_slots",
        "max_static_loop_trip_count", "max_total_static_iterations",
        "max_trace_depth",
    }, "program.manifest.resources")
    constants = []
    for index, constant in enumerate(
        _exact_list(row["constants"], "program.manifest.constants")
    ):
        context = f"program.manifest.constants[{index}]"
        constant_row = _exact_mapping(
            constant, {"name", "type", "value"}, context
        )
        constants.append({
            "name": deepcopy(constant_row["name"]),
            "type": _project_ir_type(constant_row["type"], f"{context}.type"),
            "value": deepcopy(constant_row["value"]),
        })
    return {
        "any_hit_delivery": deepcopy(row["any_hit_delivery"]),
        "attribute_types": [
            _project_ir_type(child, f"program.manifest.attribute_types[{index}]")
            for index, child in enumerate(
                _exact_list(row["attribute_types"], "program.manifest.attribute_types")
            )
        ],
        "constants": constants,
        "geometry": deepcopy(dict(geometry)),
        "linkage_selection_reason": deepcopy(row["linkage_selection_reason"]),
        "numeric": deepcopy(dict(numeric)),
        "output_record": deepcopy(row["output_record"]),
        "payload_record": deepcopy(row["payload_record"]),
        "resources": deepcopy(dict(resources)),
        "selected_linkage": deepcopy(row["selected_linkage"]),
    }


def _callback_program_structure(value: object) -> object:
    """Project the exact known Callback-IR schema; reject every unknown key.

    Only the explicitly known byte identities ``normalized_source`` and
    ``source_sha256`` and the non-semantic program label ``manifest.name`` are
    omitted.  This is deliberately not a substring-based key filter: a new
    semantic field cannot disappear silently.
    """

    if not isinstance(value, Mapping):
        raise RegistryDerivationError(
            "callback_program_schema_mismatch:program:not_mapping"
        )
    raw_keys = {
        "functions", "manifest", "normalized_source", "records", "schema_id",
        "schema_version", "source_sha256",
    }
    projected_keys = {
        "functions", "manifest", "records", "schema_id", "schema_version",
    }
    if set(value) == projected_keys:
        row = _exact_mapping(value, projected_keys, "program")
        return {
            "functions": [
                _project_function(child, f"program.functions[{index}]")
                for index, child in enumerate(
                    _exact_list(row["functions"], "program.functions")
                )
            ],
            "manifest": _validate_projected_manifest(row["manifest"]),
            "records": [
                _project_record(child, f"program.records[{index}]")
                for index, child in enumerate(
                    _exact_list(row["records"], "program.records")
                )
            ],
            "schema_id": deepcopy(row["schema_id"]),
            "schema_version": deepcopy(row["schema_version"]),
        }
    row = _exact_mapping(value, raw_keys, "program")
    if not isinstance(row["normalized_source"], str) \
            or not isinstance(row["source_sha256"], str):
        raise RegistryDerivationError("callback_program_identity_field_malformed")
    return {
        "functions": [
            _project_function(child, f"program.functions[{index}]")
            for index, child in enumerate(
                _exact_list(row["functions"], "program.functions")
            )
        ],
        "manifest": _project_manifest(row["manifest"]),
        "records": [
            _project_record(child, f"program.records[{index}]")
            for index, child in enumerate(
                _exact_list(row["records"], "program.records")
            )
        ],
        "schema_id": deepcopy(row["schema_id"]),
        "schema_version": deepcopy(row["schema_version"]),
    }


def _classify_facade(projection: Mapping[str, object]) -> dict[str, str]:
    """Select facade from identity-free scientific family fields only."""

    physical = projection["physical_guarantee"]
    semantic = projection["semantic_obligation"]
    geometry = physical.get("geometry_family")
    policy = semantic.get("policy")
    if not isinstance(policy, Mapping):
        raise RegistryDerivationError("semantic_policy_missing_for_facade")
    output_type = policy.get("output_type")
    multiplicity = policy.get("multiplicity")
    if geometry == "custom_aabb":
        family = "bounded_relation"
    elif geometry == "builtin_triangle" and (
        output_type == "checked_u64_triangle_count_scalar"
        and multiplicity == "paper_owned_rt2a1_weighted_hit_multiplicity"
    ):
        family = "triangle_reduction"
    elif geometry == "builtin_triangle":
        family = "builtin_triangle"
    else:
        raise RegistryDerivationError("scientific_family_has_no_frozen_facade")
    names = {
        "builtin_triangle": (
            "admit_builtin_triangle_compilation",
            "compile_semantically_admitted_builtin_triangle_executable",
            "run_semantically_admitted_builtin_triangle_callback",
        ),
        "triangle_reduction": (
            "admit_triangle_reduction_compilation",
            "compile_semantically_admitted_triangle_reduction_executable",
            "run_semantically_admitted_triangle_reduction_callback",
        ),
        "bounded_relation": (
            "admit_bounded_relation_compilation",
            "compile_semantically_admitted_bounded_relation_executable",
            "run_semantically_admitted_bounded_relation_callback",
        ),
    }
    admit, compile_name, run = names[family]
    return {"family": family, "admit": admit, "compile": compile_name, "run": run}


def _identity_slots(
    certificate: Mapping[str, object], template: Mapping[str, object]
) -> dict[str, str]:
    physical = certificate["physical_encoding"]
    callback = certificate["callback_contract"]
    candidates = certificate["canonical_candidates"]
    target = certificate["target_contract"]
    evidence = certificate["evidence_contract"]
    schema_values = {physical["schema_sha256"]} | {
        row["schema_sha256"] for row in candidates
    }
    if len(schema_values) != 1:
        raise RegistryDerivationError("schema_slot_is_not_single_identity")
    values = {
        "ir_digest": callback["ir_sha256"],
        "effect_digest": callback["effect_digest"],
        "schema_digest": next(iter(schema_values)),
        "abi_digest": _digest(
            template["scientific_projection"]["callback_program_structure"],
            "rtdl.goal5793.x1.registry.callback_abi",
            "full_frozen_callback_program",
        ),
        "plan_digest": _digest(
            {
                "maps": [
                    {
                        "kind": edge["kind"],
                        "consumes": edge["consumes"],
                        "produces": edge["produces"],
                    }
                    for edge in physical["maps"]
                ],
                "canonical_candidates": [
                    {key: value for key, value in candidate.items()
                     if key != "schema_sha256"}
                    for candidate in candidates
                ],
                "gas": physical["gas"],
            },
            "rtdl.goal5793.x1.registry.plan",
            "mapping_registry_and_gas",
        ),
        "native_digest": target["native_sha256"],
        "source_digest": _digest(
            evidence["source_pins"],
            "rtdl.goal5793.x1.registry.source",
            "complete_reference_source_pin_map",
        ),
    }
    if tuple(values) != ALLOWED_IDENTITY_SLOTS:
        raise RegistryDerivationError("identity_slot_keyset_or_order_mismatch")
    if not all(isinstance(value, str) and len(value) == 64 for value in values.values()):
        raise RegistryDerivationError("identity_slot_value_invalid")
    return values


def build_registry_authority() -> dict[str, object]:
    payloads = _packet_payloads()
    callback_authority_path = A2_ROOT / "CALLBACK_IR_AUTHORITY.json"
    callback_authority = _json(callback_authority_path)
    programs = callback_authority["programs"]
    authority_path = A2_ROOT / "AUTHORITY_BUNDLE.json"
    held_authority_path = A2_ROOT / "HELD_OUT_AUTHORITY_BUNDLE.json"
    authority = _json(authority_path)
    held_authority = _json(held_authority_path)

    templates_by_digest: dict[str, dict[str, object]] = {}
    normalized_authorities: dict[str, dict[str, object]] = {}
    rows = [(row_id, A2_ROOT / "certificates" / f"{row_id}.json", authority)
            for row_id in POSITIVE_IDS]
    rows.append((
        HELD_OUT_ROW,
        A2_ROOT / "HELD_OUT_RTXRMQ_CERTIFICATE.json",
        held_authority,
    ))
    row_roots = []
    for row_id, certificate_path, row_authority in rows:
        certificate = _json(certificate_path)
        program_sha = certificate["callback_contract"]["authority_program_sha256"]
        if program_sha not in programs:
            raise RegistryDerivationError("callback_program_missing_from_authority")
        normalized_certificate, normalized_authority = _normalize_a2_to_v1(
            certificate, row_authority
        )
        projection = _scientific_projection(
            normalized_certificate, programs[program_sha]["callback_program"]
        )
        facade = _classify_facade(projection)
        fingerprint = _digest(
            {"scientific_projection": projection, "facade": facade},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        if fingerprint not in templates_by_digest:
            templates_by_digest[fingerprint] = {
                "template_sha256": fingerprint,
                "scientific_projection": projection,
                "facade": facade,
                "allowed_postfreeze_slots": list(ALLOWED_IDENTITY_SLOTS),
                "row_provenance": [],
            }
        templates_by_digest[fingerprint]["row_provenance"].append(row_id)
        authority_sha = normalized_authority["authority_sha256"]
        normalized_authorities[authority_sha] = normalized_authority
        row_roots.append({
            "row_provenance": row_id,
            "certificate": _packet_record(certificate_path, payloads),
            "normalized_certificate_sha256": normalized_certificate[
                "certificate_sha256"
            ],
            "normalized_reference_authority_sha256": authority_sha,
            "template_sha256": fingerprint,
        })

    templates = [templates_by_digest[key] for key in sorted(templates_by_digest)]
    if len(templates) != 4:
        raise RegistryDerivationError(
            f"expected four identity-free positive templates, got {len(templates)}"
        )
    result: dict[str, object] = {
        "schema": REGISTRY_SCHEMA,
        "status": "HISTORICAL_FIXTURE_AUTHORITY__FUTURE_X3_AUTHORITY_NOT_YET_ISSUED",
        "authority_sha256": "",
        "canonicalization": canonical.CANONICALIZATION_NAME,
        "derivation_protocol": deepcopy(DERIVATION_PROTOCOL),
        "declaration_rule_replay_summary": deepcopy(
            DECLARATION_RULE_REPLAY_SUMMARY
        ),
        "scope": {
            "candidate_agnostic": True,
            "historical_a2_roots_only": True,
            "future_candidate_authorized": False,
            "candidate_identity_used_for_matching": False,
            "expected_outcome_or_role_used_for_matching": False,
            "search_entropy_implementation_execution_gpu_timing_count": 0,
        },
        "frozen_roots": {
            "postreview_packet_manifest": {
                **_record(PACKET_MANIFEST_PATH),
                "hard_pinned_sha256": EXPECTED_PACKET_MANIFEST_SHA256,
            },
            "callback_ir_authority": _packet_record(
                callback_authority_path, payloads
            ),
            "ordinary_authority": _packet_record(authority_path, payloads),
            "held_out_authority": _packet_record(held_authority_path, payloads),
            "canonical_helper": _record(CANONICAL_PATH),
            "v1_checker": _record(V1_CHECKER_PATH),
        },
        "allowed_postfreeze_slots": list(ALLOWED_IDENTITY_SLOTS),
        "forbidden_postfreeze_changes": [
            "semantic obligation",
            "physical guarantee",
            "geometry family",
            "callback role or opcode",
            "admission rule",
            "canonical registry template",
            "admit/compile/run facade",
        ],
        "templates": templates,
        "row_roots": row_roots,
        "allowed_normalized_reference_authority_sha256": sorted(
            normalized_authorities
        ),
        "template_count": len(templates),
        "row_provenance_count": len(row_roots),
        "future_boundary": (
            "a future candidate-specific registry authority must use this exact "
            "schema/derivation, be frozen in the preentropy science table, receive "
            "separate review, and be pinned as an exact dependency by its runner; "
            "this historical fixture authority cannot authorize it"
        ),
    }
    result["authority_sha256"] = canonical.seal_document(
        result,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.registry_derivation_authority",
        version=1,
    )
    return result


def _plain_sha256(value: object, context: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise RegistryDerivationError(f"invalid_sha256:{context}")
    try:
        int(value, 16)
    except ValueError as exc:
        raise RegistryDerivationError(f"invalid_sha256:{context}") from exc
    return value


def _validate_identity_free_projection(value: object) -> dict[str, object]:
    projection = _exact_mapping(value, {
        "semantic_obligation", "physical_guarantee",
        "callback_roles_resources", "canonical_registry_template",
        "target_capability_shape", "callback_program_structure",
    }, "scientific_projection")
    semantic = _exact_mapping(
        projection["semantic_obligation"],
        set(projection["semantic_obligation"])
        if isinstance(projection["semantic_obligation"], Mapping) else set(),
        "scientific_projection.semantic_obligation",
    )
    physical = _exact_mapping(
        projection["physical_guarantee"],
        set(projection["physical_guarantee"])
        if isinstance(projection["physical_guarantee"], Mapping) else set(),
        "scientific_projection.physical_guarantee",
    )
    callback = _exact_mapping(
        projection["callback_roles_resources"],
        set(projection["callback_roles_resources"])
        if isinstance(projection["callback_roles_resources"], Mapping) else set(),
        "scientific_projection.callback_roles_resources",
    )
    target = _exact_mapping(
        projection["target_capability_shape"],
        set(projection["target_capability_shape"])
        if isinstance(projection["target_capability_shape"], Mapping) else set(),
        "scientific_projection.target_capability_shape",
    )
    candidates = _exact_list(
        projection["canonical_registry_template"],
        "scientific_projection.canonical_registry_template",
    )
    if "specification_source_pin" in semantic:
        raise RegistryDerivationError(
            "identity_field_in_scientific_projection:specification_source_pin"
        )
    for key in ("schema_sha256", "provider_source_pin"):
        if key in physical:
            raise RegistryDerivationError(
                f"identity_field_in_scientific_projection:{key}"
            )
    maps = physical.get("maps")
    if not isinstance(maps, list):
        raise RegistryDerivationError("scientific_projection_maps_not_list")
    for index, edge in enumerate(maps):
        if not isinstance(edge, Mapping):
            raise RegistryDerivationError(
                f"scientific_projection_map_not_object:{index}"
            )
        if "source_pin" in edge or "source_sha256" in edge:
            raise RegistryDerivationError(
                f"identity_field_in_scientific_projection:maps[{index}]"
            )
    for key in ("ir_sha256", "effect_digest"):
        if key in callback:
            raise RegistryDerivationError(
                f"identity_field_in_scientific_projection:{key}"
            )
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            raise RegistryDerivationError(
                f"scientific_projection_candidate_not_object:{index}"
            )
        if "schema_sha256" in candidate:
            raise RegistryDerivationError(
                f"identity_field_in_scientific_projection:candidate[{index}]"
            )
    for key in ("target_sha256", "native_sha256"):
        if key in target:
            raise RegistryDerivationError(
                f"identity_field_in_scientific_projection:{key}"
            )
    program = _callback_program_structure(
        projection["callback_program_structure"]
    )
    result = deepcopy(dict(projection))
    result["callback_program_structure"] = program
    return result


_REGISTRY_AUTHORITY_KEYS = {
    "schema", "status", "authority_sha256", "canonicalization",
    "derivation_protocol", "declaration_rule_replay_summary", "scope",
    "frozen_roots",
    "allowed_postfreeze_slots", "forbidden_postfreeze_changes", "templates",
    "row_roots", "allowed_normalized_reference_authority_sha256",
    "template_count", "row_provenance_count", "future_boundary",
}


def validate_registry_authority(value: object) -> dict[str, object]:
    """Validate an externally supplied, separately pinned registry authority."""

    authority = _exact_mapping(value, _REGISTRY_AUTHORITY_KEYS, "registry_authority")
    if authority["schema"] != REGISTRY_SCHEMA:
        raise RegistryDerivationError("registry_authority_schema_mismatch")
    if authority["canonicalization"] != canonical.CANONICALIZATION_NAME:
        raise RegistryDerivationError("registry_canonicalization_mismatch")
    if canonical.canonical_json_bytes(authority["derivation_protocol"]) \
            != canonical.canonical_json_bytes(DERIVATION_PROTOCOL):
        raise RegistryDerivationError("registry_derivation_protocol_mismatch")
    if canonical.canonical_json_bytes(authority["declaration_rule_replay_summary"]) \
            != canonical.canonical_json_bytes(DECLARATION_RULE_REPLAY_SUMMARY):
        raise RegistryDerivationError("registry_rule_replay_summary_mismatch")
    if tuple(authority["allowed_postfreeze_slots"]) != ALLOWED_IDENTITY_SLOTS:
        raise RegistryDerivationError("registry_allowed_slots_mismatch")
    expected_seal = canonical.seal_document(
        authority,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.registry_derivation_authority",
        version=1,
    )
    if authority["authority_sha256"] != expected_seal:
        raise RegistryDerivationError("registry_authority_seal_mismatch")
    templates = _exact_list(authority["templates"], "registry_authority.templates")
    if type(authority["template_count"]) is not int \
            or authority["template_count"] != len(templates) \
            or not templates:
        raise RegistryDerivationError("registry_template_count_mismatch")
    observed_template_sha: set[str] = set()
    provenance_count = 0
    for index, raw_template in enumerate(templates):
        context = f"registry_authority.templates[{index}]"
        template = _exact_mapping(raw_template, {
            "template_sha256", "scientific_projection", "facade",
            "allowed_postfreeze_slots", "row_provenance",
        }, context)
        projection = _validate_identity_free_projection(
            template["scientific_projection"]
        )
        facade = _classify_facade(projection)
        if canonical.canonical_json_bytes(template["facade"]) \
                != canonical.canonical_json_bytes(facade):
            raise RegistryDerivationError(f"registry_facade_mismatch:{index}")
        expected_template_sha = _digest(
            {"scientific_projection": projection, "facade": facade},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        if template["template_sha256"] != expected_template_sha:
            raise RegistryDerivationError(
                f"registry_template_derivation_mismatch:{index}"
            )
        if expected_template_sha in observed_template_sha:
            raise RegistryDerivationError("registry_duplicate_template")
        observed_template_sha.add(expected_template_sha)
        if tuple(template["allowed_postfreeze_slots"]) != ALLOWED_IDENTITY_SLOTS:
            raise RegistryDerivationError(
                f"registry_template_allowed_slots_mismatch:{index}"
            )
        provenance = _exact_list(
            template["row_provenance"], f"{context}.row_provenance"
        )
        provenance_count += len(provenance)
    if authority["row_provenance_count"] != provenance_count:
        raise RegistryDerivationError("registry_row_provenance_count_mismatch")
    allowed_authorities = _exact_list(
        authority["allowed_normalized_reference_authority_sha256"],
        "registry_authority.allowed_reference_authorities",
    )
    if len(set(allowed_authorities)) != len(allowed_authorities):
        raise RegistryDerivationError("registry_duplicate_reference_authority")
    for index, digest in enumerate(allowed_authorities):
        _plain_sha256(digest, f"allowed_reference_authority[{index}]")
    row_roots = _exact_list(authority["row_roots"], "registry_authority.row_roots")
    for index, row in enumerate(row_roots):
        if not isinstance(row, Mapping) \
                or row.get("template_sha256") not in observed_template_sha:
            raise RegistryDerivationError(f"registry_row_root_invalid:{index}")
    if not isinstance(authority["frozen_roots"], Mapping) \
            or not authority["frozen_roots"]:
        raise RegistryDerivationError("registry_frozen_roots_absent")
    return deepcopy(dict(authority))


def _registry_canonical_identity(authority: Mapping[str, object]) -> dict[str, object]:
    encoded = canonical.canonical_json_bytes(authority)
    return {"bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()}


def _build_stage_pin(
    authority: Mapping[str, object], *, stage_id: str, frozen_stage_root_sha256: str
) -> dict[str, object]:
    validated = validate_registry_authority(authority)
    _plain_sha256(frozen_stage_root_sha256, "frozen_stage_root_sha256")
    identity = _registry_canonical_identity(validated)
    pin: dict[str, object] = {
        "schema": STAGE_PIN_SCHEMA,
        "stage_id": stage_id,
        "stage_kind": "PRESEARCH_REGISTRY_AUTHORITY_FREEZE",
        "registry_authority_sha256": validated["authority_sha256"],
        "registry_authority_canonical_bytes": identity["bytes"],
        "registry_authority_canonical_sha256": identity["sha256"],
        "derivation_protocol_sha256": _digest(
            DERIVATION_PROTOCOL,
            "rtdl.goal5793.x1.registry.derivation_protocol",
            "exact_generic_registry_derivation_protocol",
        ),
        "frozen_stage_root_sha256": frozen_stage_root_sha256,
        "presearch_controls": {
            "search": False,
            "entropy": False,
            "selection": False,
            "candidate_implementation": False,
            "execution": False,
            "gpu": False,
            "pod": False,
            "ssh": False,
            "timing": False,
            "publication": False,
        },
        "stage_pin_sha256": "",
    }
    pin["stage_pin_sha256"] = canonical.seal_document(
        pin,
        seal_field="stage_pin_sha256",
        domain="rtdl.goal5793.x1.presearch_registry_stage_pin",
        version=1,
    )
    return pin


def historical_registry_context() -> tuple[
    dict[str, object], dict[str, object], str
]:
    """Return historical baseline authority plus its out-of-band test pin."""

    authority = build_registry_authority()
    pin = _build_stage_pin(
        authority,
        stage_id="goal5793-x1-historical-a2-positive-baseline",
        frozen_stage_root_sha256=EXPECTED_PACKET_MANIFEST_SHA256,
    )
    return authority, pin, str(pin["stage_pin_sha256"])


_STAGE_PIN_KEYS = {
    "schema", "stage_id", "stage_kind", "registry_authority_sha256",
    "registry_authority_canonical_bytes",
    "registry_authority_canonical_sha256", "derivation_protocol_sha256",
    "frozen_stage_root_sha256", "presearch_controls", "stage_pin_sha256",
}


def _validate_stage_pin(
    authority: Mapping[str, object], pin_value: object, trusted_pin_sha256: object
) -> dict[str, object]:
    pin = _exact_mapping(pin_value, _STAGE_PIN_KEYS, "registry_stage_pin")
    if pin["schema"] != STAGE_PIN_SCHEMA \
            or pin["stage_kind"] != "PRESEARCH_REGISTRY_AUTHORITY_FREEZE":
        raise RegistryDerivationError("registry_stage_pin_schema_or_kind_mismatch")
    expected_seal = canonical.seal_document(
        pin,
        seal_field="stage_pin_sha256",
        domain="rtdl.goal5793.x1.presearch_registry_stage_pin",
        version=1,
    )
    if pin["stage_pin_sha256"] != expected_seal:
        raise RegistryDerivationError("registry_stage_pin_seal_mismatch")
    if trusted_pin_sha256 != expected_seal:
        raise RegistryDerivationError("out_of_band_trusted_stage_pin_mismatch")
    identity = _registry_canonical_identity(authority)
    if pin["registry_authority_sha256"] != authority["authority_sha256"] \
            or pin["registry_authority_canonical_bytes"] != identity["bytes"] \
            or pin["registry_authority_canonical_sha256"] != identity["sha256"]:
        raise RegistryDerivationError("registry_stage_pin_authority_mismatch")
    expected_protocol = _digest(
        DERIVATION_PROTOCOL,
        "rtdl.goal5793.x1.registry.derivation_protocol",
        "exact_generic_registry_derivation_protocol",
    )
    if canonical.canonical_json_bytes(pin["derivation_protocol_sha256"]) \
            != canonical.canonical_json_bytes(expected_protocol):
        raise RegistryDerivationError("registry_stage_pin_protocol_mismatch")
    controls = pin["presearch_controls"]
    expected_controls = {
        "search": False, "entropy": False, "selection": False,
        "candidate_implementation": False, "execution": False, "gpu": False,
        "pod": False, "ssh": False, "timing": False, "publication": False,
    }
    if canonical.canonical_json_bytes(controls) \
            != canonical.canonical_json_bytes(expected_controls):
        raise RegistryDerivationError("registry_stage_pin_controls_mismatch")
    _plain_sha256(pin["frozen_stage_root_sha256"], "frozen_stage_root_sha256")
    return deepcopy(dict(pin))


def _match_template(
    certificate: Mapping[str, object], registry: Mapping[str, object]
) -> Mapping[str, object]:
    callback = certificate["callback_contract"]
    matches = []
    for template in registry["templates"]:
        program = template["scientific_projection"]["callback_program_structure"]
        projection = _scientific_projection(certificate, program)
        facade = _classify_facade(projection)
        fingerprint = _digest(
            {"scientific_projection": projection, "facade": facade},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        if fingerprint == template["template_sha256"]:
            # IR/effect are slots, but the role/resource projection must still be exact.
            if callback.get("roles") == template["scientific_projection"][
                "callback_roles_resources"
            ].get("roles"):
                matches.append(template)
    if len(matches) != 1:
        raise RegistryDerivationError(f"registry_template_match_count:{len(matches)}")
    return matches[0]


def _orientation(certificate: Mapping[str, object]) -> str:
    semantic = certificate["semantic_request"]
    return _digest(
        {
            "contract_id": semantic["contract_id"],
            "declared_domain_sha256": semantic["declared_domain_sha256"],
            "input_type": semantic["policy"]["input_type"],
            "exactness": semantic["policy"]["exactness"],
        },
        "rtdl.goal5793.x1.registry.orientation_contract",
        "normalized_v1_semantic_orientation_obligation",
    )


def _product_sections(
    certificate: Mapping[str, object],
    registry: Mapping[str, object],
    template: Mapping[str, object],
    slots: Mapping[str, str],
) -> dict[str, object]:
    semantic_ref = certificate["semantic_request"]
    physical_ref = certificate["physical_encoding"]
    callback_ref = certificate["callback_contract"]
    target_ref = certificate["target_contract"]
    evidence_ref = certificate["evidence_contract"]
    orientation = _orientation(certificate)
    maps = [{
        "kind": edge["kind"],
        "source_id": edge["source_pin"],
        "source_sha256": edge["source_sha256"],
        "consumes": deepcopy(edge["consumes"]),
        "produces": deepcopy(edge["produces"]),
    } for edge in physical_ref["maps"]]
    source_manifest = {
        edge["source_pin"]: evidence_ref["source_pins"][edge["source_pin"]]
        for edge in physical_ref["maps"]
    }
    candidates = [{
        **deepcopy(candidate),
        "declared_domain_sha256": semantic_ref["declared_domain_sha256"],
        "orientation_contract_sha256": orientation,
    } for candidate in certificate["canonical_candidates"]]
    family_nonce = _digest(
        {
            "registry_authority_sha256": registry["authority_sha256"],
            "template_sha256": template["template_sha256"],
            "identity_slots": slots,
        },
        "rtdl.goal5793.x1.registry.family_authority_nonce",
        "exact_template_and_seven_slots",
    )
    family_authority = _digest(
        {
            "registry_authority_sha256": registry["authority_sha256"],
            "template_sha256": template["template_sha256"],
            "identity_slots": slots,
            "family_authority_nonce": family_nonce,
            "facade": template["facade"],
        },
        "rtdl.goal5793.x1.registry.family_authority",
        "candidate_agnostic_registry_derivation",
    )
    return {
        "semantic_requirement": {
            "contract_id": semantic_ref["contract_id"],
            "algorithm_identity": semantic_ref["algorithm_identity"],
            "declared_domain_sha256": semantic_ref["declared_domain_sha256"],
            "policy": deepcopy(semantic_ref["policy"]),
            "required_hit_semantics": deepcopy(
                semantic_ref["required_hit_semantics"]
            ),
            "orientation_contract_sha256": orientation,
            "specification_source_sha256": evidence_ref["source_pins"][
                semantic_ref["specification_source_pin"]
            ],
        },
        "physical_guarantee": {
            "encoding_id": physical_ref["encoding_id"],
            "supported_algorithm_identity": semantic_ref["algorithm_identity"],
            "supported_domain_sha256": semantic_ref["declared_domain_sha256"],
            "orientation_contract_sha256": orientation,
            "geometry_family": physical_ref["geometry_family"],
            "schema_sha256": slots["schema_digest"],
            "callback_ir_sha256": slots["ir_digest"],
            "effect_digest": slots["effect_digest"],
            "guarantees": deepcopy(physical_ref["guarantees"]),
            "maps": maps,
            "hit_semantics": [row["semantic"] for row in physical_ref["hit_channels"]],
            "gas_graph_depth": physical_ref["gas"]["graph_depth"],
            "gas_sbt_record_stride": physical_ref["gas"]["sbt_record_stride"],
            "gas_update_policy": physical_ref["gas"]["update_policy"],
            "buffer_contract_sha256": _digest(
                physical_ref["buffers"],
                "rtdl.goal5793.x1.reference_buffer_contract",
                "goal5789_v1.physical_encoding.buffers",
            ),
            "required_target_capabilities": [
                "optix", "bound_program_bundle",
                f"optix_{physical_ref['geometry_family']}",
            ],
            "source_manifest": source_manifest,
        },
        "live_binding": {
            "callback_ir_sha256": slots["ir_digest"],
            "effect_digest": slots["effect_digest"],
            "family_schema_sha256": slots["schema_digest"],
            "target_sha256": target_ref["target_sha256"],
            "target_provider": target_ref["provider"],
            "target_capabilities": deepcopy(target_ref["capabilities"]),
            "canonical_artifact_sha256": slots["native_digest"],
            "canonical_template_id": candidates[0]["template_id"],
            "family_authority_sha256": family_authority,
            "family_authority_nonce": family_nonce,
        },
        "canonical_candidates": candidates,
    }


def _receipt(
    payload: Mapping[str, object],
    registry: Mapping[str, object],
    template: Mapping[str, object],
    slots: Mapping[str, str],
) -> dict[str, object]:
    receipt: dict[str, object] = {
        "schema": RECEIPT_SCHEMA,
        "registry_authority_sha256": registry["authority_sha256"],
        "template_sha256": template["template_sha256"],
        "identity_slots": dict(slots),
        "family_authority_sha256": payload["live_binding"][
            "family_authority_sha256"
        ],
        "family_authority_nonce": payload["live_binding"][
            "family_authority_nonce"
        ],
        "exam_projection_sha256": _digest(
            payload,
            "rtdl.goal5793.x1.registry.exam_projection",
            "complete_generic_exam_input",
        ),
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = canonical.seal_document(
        receipt,
        seal_field="receipt_sha256",
        domain="rtdl.goal5793.x1.registry_derivation_receipt",
        version=1,
    )
    return receipt


def historical_registered_fixture(row_id: str) -> tuple[dict[str, object], dict[str, object]]:
    """Build one historical fixture; row_id is test provenance, not matcher input."""

    if row_id not in (*POSITIVE_IDS, HELD_OUT_ROW):
        raise RegistryDerivationError("historical_fixture_id_not_allowed")
    registry = build_registry_authority()
    if row_id == HELD_OUT_ROW:
        certificate_path = A2_ROOT / "HELD_OUT_RTXRMQ_CERTIFICATE.json"
        authority_path = A2_ROOT / "HELD_OUT_AUTHORITY_BUNDLE.json"
    else:
        certificate_path = A2_ROOT / "certificates" / f"{row_id}.json"
        authority_path = A2_ROOT / "AUTHORITY_BUNDLE.json"
    certificate, authority = _normalize_a2_to_v1(
        _json(certificate_path), _json(authority_path)
    )
    template = _match_template(certificate, registry)
    slots = _identity_slots(certificate, template)
    payload: dict[str, object] = {
        "schema": EXAM_INPUT_SCHEMA,
        **_product_sections(certificate, registry, template, slots),
        "reference_certificate": certificate,
        "reference_authority": authority,
    }
    return payload, _receipt(payload, registry, template, slots)


def verify_registered_input(
    payload: Mapping[str, object],
    receipt: Mapping[str, object],
    registry_authority: Mapping[str, object] | None = None,
    registry_stage_pin: Mapping[str, object] | None = None,
    trusted_stage_pin_sha256: str | None = None,
) -> dict[str, object]:
    """Verify against a separately trusted external presearch authority.

    The candidate payload cannot carry the authority, stage pin, or trust-root
    digest.  A controlling runner must pass all three out of band.  Therefore a
    candidate cannot manufacture both the scientific registry and its root of
    trust inside the declaration under examination.
    """

    if not isinstance(payload, Mapping) or not isinstance(receipt, Mapping):
        raise RegistryDerivationError("payload_and_receipt_must_be_objects")
    if registry_authority is None:
        raise RegistryDerivationError("external_registry_authority_required")
    if registry_stage_pin is None:
        raise RegistryDerivationError("external_registry_stage_pin_required")
    if trusted_stage_pin_sha256 is None:
        raise RegistryDerivationError("out_of_band_trusted_stage_pin_required")
    for forbidden in (
        "registry_authority", "registry_stage_pin", "trusted_stage_pin_sha256"
    ):
        if forbidden in payload:
            raise RegistryDerivationError(
                f"trust_root_forbidden_inside_candidate_payload:{forbidden}"
            )
    registry = validate_registry_authority(registry_authority)
    validated_pin = _validate_stage_pin(
        registry, registry_stage_pin, trusted_stage_pin_sha256
    )
    if set(receipt) != {
        "schema", "registry_authority_sha256", "template_sha256",
        "identity_slots", "family_authority_sha256", "family_authority_nonce",
        "exam_projection_sha256", "receipt_sha256",
    }:
        raise RegistryDerivationError("receipt_keyset_mismatch")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise RegistryDerivationError("receipt_schema_mismatch")
    if receipt.get("registry_authority_sha256") != registry["authority_sha256"]:
        raise RegistryDerivationError("registry_receipt_authority_mismatch")
    certificate = payload.get("reference_certificate")
    authority = payload.get("reference_authority")
    if not isinstance(certificate, Mapping) or not isinstance(authority, Mapping):
        raise RegistryDerivationError("reference_certificate_or_authority_absent")
    if authority.get("authority_sha256") not in registry[
        "allowed_normalized_reference_authority_sha256"
    ]:
        raise RegistryDerivationError("reference_authority_not_frozen")
    template = _match_template(certificate, registry)
    slots = _identity_slots(certificate, template)
    expected_sections = _product_sections(certificate, registry, template, slots)
    for key, expected in expected_sections.items():
        if canonical.canonical_json_bytes(payload.get(key)) \
                != canonical.canonical_json_bytes(expected):
            raise RegistryDerivationError(f"registered_projection_mismatch:{key}")
    expected_receipt = _receipt(payload, registry, template, slots)
    if canonical.canonical_json_bytes(receipt) \
            != canonical.canonical_json_bytes(expected_receipt):
        raise RegistryDerivationError("registry_receipt_mismatch")
    return {
        "status": "EXACT_REGISTERED_TEMPLATE_AND_SEVEN_SLOTS",
        "registry_authority_sha256": registry["authority_sha256"],
        "template_sha256": template["template_sha256"],
        "identity_slots": slots,
        "receipt_sha256": receipt["receipt_sha256"],
        "registry_stage_pin_sha256": validated_pin["stage_pin_sha256"],
        "registry_stage_id": validated_pin["stage_id"],
        "registry_authority_source": "OUT_OF_BAND_SEPARATELY_TRUSTED_STAGE_PIN",
        "candidate_identity_used": False,
        "expected_outcome_or_role_used": False,
    }


__all__ = [
    "ALLOWED_IDENTITY_SLOTS",
    "DECLARATION_RULE_REPLAY_SUMMARY",
    "RECEIPT_SCHEMA",
    "REGISTRY_SCHEMA",
    "STAGE_PIN_SCHEMA",
    "RegistryDerivationError",
    "build_registry_authority",
    "historical_registered_fixture",
    "historical_registry_context",
    "validate_registry_authority",
    "verify_registered_input",
]
