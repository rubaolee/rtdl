"""Independent Goal5789 semantic-to-physical compatibility checker.

This module is deliberately evidence-side code.  It imports neither RTDL's
lowering selector nor an application execution route.  It checks a closed,
machine-readable certificate and produces four separate judgments:

* target capability;
* semantic/physical compatibility for a declared domain;
* concrete-instance admissibility; and
* performance, which is always outside this checker.

The checker never grants executable authority.  A compatible certificate is a
replayable *reference-admission* result; a family compiler and runtime must
still bind executable target resources, and an application oracle and a
behavioral receipt remain separate evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping


CERTIFICATE_SCHEMA = "rtdl.goal5789.semantic_physical_certificate.v1"
AUTHORITY_SCHEMA = "rtdl.goal5789.compatibility_authority_bundle.v1"
SEMANTIC_AUTHORITY_SCHEMA = "rtdl.goal5789.semantic_requirement_authority.v1"
PHYSICAL_AUTHORITY_SCHEMA = "rtdl.goal5789.physical_guarantee_authority.v1"
TARGET_AUTHORITY_SCHEMA = "rtdl.goal5789.target_capability_authority.v1"
INSTANCE_AUTHORITY_SCHEMA = "rtdl.goal5789.instance_fact_authority.v1"
EVIDENCE_AUTHORITY_SCHEMA = "rtdl.goal5789.evidence_identity_authority.v1"
RESULT_SCHEMA = "rtdl.goal5789.compatibility_check_result.v1"

COMPATIBLE = "COMPATIBLE_FOR_DECLARED_DOMAIN"
INCOMPATIBLE = "INCOMPATIBLE"
UNKNOWN = "UNKNOWN"
CAPABLE = "TARGET_CAPABLE"
INCAPABLE = "TARGET_INCAPABLE"
ADMISSIBLE = "INSTANCE_ADMISSIBLE"
INADMISSIBLE = "INSTANCE_INADMISSIBLE"
NOT_EVALUATED = "NOT_EVALUATED"

_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_POLICY_KEYS = {
    "input_type",
    "output_type",
    "exactness",
    "tie_policy",
    "order_policy",
    "multiplicity",
    "numeric_precision",
    "overflow_policy",
}

_MAP_GRAPH = {
    "encode": (("semantic_input",), ("geometry", "query_state")),
    "ray": (("query_state",), ("ray",)),
    "trace": (("geometry", "ray"), ("hit_stream",)),
    "continuation": (("hit_stream",), ("candidate_output",)),
    "decode": (("candidate_output",), ("semantic_output",)),
}

_ROLE_EFFECTS = {
    "bounds": {"aabb"},
    "make_ray": {"trace_request"},
    "intersection": {"hit", "no_hit"},
    "any_hit": {"accept_continue", "ignore", "terminate"},
    "closest_hit": {"payload"},
    "miss": {"payload"},
    "finalize": {"output"},
}

_GEOMETRY_RULES = {
    "custom_aabb": {
        "required_roles": {"bounds", "make_ray", "intersection", "miss", "finalize"},
        "forbidden_roles": set(),
        "required_capability": "optix_custom_aabb",
        "required_hit_channels": {
            "custom_hit_kind": "verified_intersection_effect",
        },
    },
    "builtin_triangle": {
        "required_roles": {"make_ray", "miss", "finalize"},
        "forbidden_roles": {"bounds", "intersection"},
        "required_capability": "optix_builtin_triangle",
        "required_hit_channels": {
            "primitive_index_u32": "optix_builtin",
            "triangle_front_back_hit_kind_u32": "optix_builtin",
            "triangle_barycentrics_f32x2": "optix_builtin",
            "primitive_metadata_lookup": "compiler_metadata_lookup",
        },
    },
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def certificate_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("certificate_sha256", None)
    return digest(body)


def authority_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("authority_sha256", None)
    return digest(body)


def nested_authority_digest(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body.pop("authority_sha256", None)
    return digest(body)


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and bool(_SHA256.fullmatch(value))


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _mapping(value: object) -> Mapping[str, object] | None:
    return value if isinstance(value, Mapping) else None


def _list(value: object) -> list[object] | None:
    return value if isinstance(value, list) else None


def _key_delta(value: Mapping[str, object], expected: set[str]) -> tuple[list[str], list[str]]:
    return sorted(expected - set(value)), sorted(set(value) - expected)


def _judgment(verdict: str, reasons: Iterable[str]) -> dict[str, object]:
    unique = tuple(dict.fromkeys(reasons))
    return {"verdict": verdict, "reasons": list(unique)}


def _verdict(unknown: list[str], incompatible: list[str], *, yes: str, no: str) -> dict[str, object]:
    if unknown:
        return _judgment(UNKNOWN, unknown + incompatible)
    if incompatible:
        return _judgment(no, incompatible)
    return _judgment(yes, ())


def _check_exact_keys(
    value: Mapping[str, object] | None,
    expected: set[str],
    label: str,
    unknown: list[str],
    incompatible: list[str],
) -> bool:
    if value is None:
        unknown.append(f"missing_or_nonobject:{label}")
        return False
    missing, extra = _key_delta(value, expected)
    unknown.extend(f"missing:{label}.{item}" for item in missing)
    incompatible.extend(f"unexpected:{label}.{item}" for item in extra)
    return not missing and not extra


def _check_sha(value: object, label: str, incompatible: list[str]) -> None:
    if not _is_sha(value):
        incompatible.append(f"invalid_sha256:{label}")


def _check_policy(
    semantic: Mapping[str, object],
    physical: Mapping[str, object],
    unknown: list[str],
    incompatible: list[str],
) -> None:
    semantic_policy = _mapping(semantic.get("policy"))
    physical_policy = _mapping(physical.get("guarantees"))
    left_ok = _check_exact_keys(
        semantic_policy, _POLICY_KEYS, "semantic_request.policy", unknown, incompatible
    )
    right_ok = _check_exact_keys(
        physical_policy, _POLICY_KEYS, "physical_encoding.guarantees", unknown, incompatible
    )
    if not (left_ok and right_ok):
        return
    for key in sorted(_POLICY_KEYS):
        left = semantic_policy[key]
        right = physical_policy[key]
        if not isinstance(left, str) or not left:
            incompatible.append(f"invalid_policy_value:semantic_request.policy.{key}")
        if not isinstance(right, str) or not right:
            incompatible.append(f"invalid_policy_value:physical_encoding.guarantees.{key}")
        if left != right:
            incompatible.append(f"semantic_guarantee_mismatch:{key}:{left!r}!={right!r}")


def _check_map_graph(
    physical: Mapping[str, object],
    authority_sources: Mapping[str, object],
    unknown: list[str],
    incompatible: list[str],
) -> None:
    maps = _list(physical.get("maps"))
    if maps is None:
        unknown.append("missing_or_nonlist:physical_encoding.maps")
        return
    by_kind: dict[str, Mapping[str, object]] = {}
    for index, raw in enumerate(maps):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"kind", "source_pin", "source_sha256", "consumes", "produces"},
            f"physical_encoding.maps[{index}]",
            unknown,
            incompatible,
        ):
            continue
        kind = item["kind"]
        if not isinstance(kind, str) or kind not in _MAP_GRAPH:
            incompatible.append(f"unknown_map_kind:{kind!r}")
            continue
        if kind in by_kind:
            incompatible.append(f"duplicate_map_kind:{kind}")
            continue
        by_kind[kind] = item
        expected_in, expected_out = _MAP_GRAPH[kind]
        if item["consumes"] != list(expected_in):
            incompatible.append(f"map_input_mismatch:{kind}")
        if item["produces"] != list(expected_out):
            incompatible.append(f"map_output_mismatch:{kind}")
        source_pin = item["source_pin"]
        source_sha = item["source_sha256"]
        if not isinstance(source_pin, str) or source_pin not in authority_sources:
            unknown.append(f"source_pin_not_in_authority:{source_pin!r}")
        elif authority_sources[source_pin] != source_sha:
            incompatible.append(f"source_identity_mismatch:{source_pin}")
        _check_sha(source_sha, f"physical_encoding.maps[{index}].source_sha256", incompatible)
    for kind in _MAP_GRAPH:
        if kind not in by_kind:
            unknown.append(f"missing_map_kind:{kind}")


def _check_roles(
    callback: Mapping[str, object],
    geometry_family: object,
    unknown: list[str],
    incompatible: list[str],
) -> None:
    roles = _list(callback.get("roles"))
    if roles is None:
        unknown.append("missing_or_nonlist:callback_contract.roles")
        return
    present: set[str] = set()
    for index, raw in enumerate(roles):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"role", "effects"},
            f"callback_contract.roles[{index}]",
            unknown,
            incompatible,
        ):
            continue
        role = item["role"]
        effects = item["effects"]
        if not isinstance(role, str) or role not in _ROLE_EFFECTS:
            incompatible.append(f"unknown_callback_role:{role!r}")
            continue
        if role in present:
            incompatible.append(f"duplicate_callback_role:{role}")
        present.add(role)
        if not isinstance(effects, list) or any(not isinstance(effect, str) for effect in effects):
            incompatible.append(f"invalid_role_effects:{role}")
            continue
        unexpected = set(effects) - _ROLE_EFFECTS[role]
        if unexpected:
            incompatible.append(f"role_effect_violation:{role}:{','.join(sorted(unexpected))}")
    rule = _GEOMETRY_RULES.get(geometry_family)
    if rule is None:
        incompatible.append(f"unknown_geometry_family:{geometry_family!r}")
        return
    missing = rule["required_roles"] - present
    forbidden = rule["forbidden_roles"] & present
    if not ({"any_hit", "closest_hit"} & present):
        missing.add("any_hit_or_closest_hit")
    incompatible.extend(f"missing_geometry_role:{item}" for item in sorted(missing))
    incompatible.extend(f"forbidden_geometry_role:{item}" for item in sorted(forbidden))


def _check_hit_channels(
    semantic: Mapping[str, object],
    physical: Mapping[str, object],
    callback: Mapping[str, object] | None,
    geometry_family: object,
    unknown: list[str],
    incompatible: list[str],
) -> None:
    required = semantic.get("required_hit_semantics")
    channels = _list(physical.get("hit_channels"))
    if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
        unknown.append("missing_or_invalid:semantic_request.required_hit_semantics")
        return
    if channels is None:
        unknown.append("missing_or_nonlist:physical_encoding.hit_channels")
        return
    by_semantic: dict[str, Mapping[str, object]] = {}
    callback_roles: set[str] = set()
    if callback is not None:
        for raw_role in _list(callback.get("roles")) or []:
            role = _mapping(raw_role)
            if role is not None and isinstance(role.get("role"), str):
                callback_roles.add(role["role"])
    for index, raw in enumerate(channels):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"semantic", "producer", "read_roles"},
            f"physical_encoding.hit_channels[{index}]",
            unknown,
            incompatible,
        ):
            continue
        semantic_name = item["semantic"]
        producer = item["producer"]
        readers = item["read_roles"]
        if not isinstance(semantic_name, str) or semantic_name in by_semantic:
            incompatible.append(f"invalid_or_duplicate_hit_channel:{semantic_name!r}")
            continue
        if not isinstance(producer, str) or not isinstance(readers, list) or not readers:
            incompatible.append(f"invalid_hit_channel_contract:{semantic_name}")
            continue
        if any(reader not in _ROLE_EFFECTS for reader in readers):
            incompatible.append(f"invalid_hit_channel_reader:{semantic_name}")
        elif not (set(readers) & callback_roles):
            incompatible.append(f"hit_channel_has_no_present_reader:{semantic_name}")
        by_semantic[semantic_name] = item
    for name in required:
        if name not in by_semantic:
            incompatible.append(f"required_hit_semantic_missing:{name}")
    rule = _GEOMETRY_RULES.get(geometry_family)
    if rule is None:
        return
    for name, producer in rule["required_hit_channels"].items():
        item = by_semantic.get(name)
        if item is None:
            incompatible.append(f"geometry_hit_channel_missing:{name}")
        elif item["producer"] != producer:
            incompatible.append(f"hit_producer_mismatch:{name}")


def _check_buffers_and_bindings(
    physical: Mapping[str, object],
    instance: Mapping[str, object],
    unknown: list[str],
    incompatible: list[str],
) -> None:
    buffers = _list(physical.get("buffers"))
    bindings = _list(instance.get("bindings"))
    if buffers is None:
        unknown.append("missing_or_nonlist:physical_encoding.buffers")
        return
    if bindings is None:
        unknown.append("missing_or_nonlist:instance_contract.bindings")
        return
    static: dict[str, Mapping[str, object]] = {}
    for index, raw in enumerate(buffers):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"semantic", "access", "residency", "count_relation"},
            f"physical_encoding.buffers[{index}]",
            unknown,
            incompatible,
        ):
            continue
        name = item["semantic"]
        if not isinstance(name, str) or name in static:
            incompatible.append(f"invalid_or_duplicate_buffer:{name!r}")
            continue
        if item["access"] not in {"read_only", "write_only", "internal_status"}:
            incompatible.append(f"invalid_buffer_access:{name}")
        if item["residency"] != "device":
            incompatible.append(f"invalid_buffer_residency:{name}")
        if item["count_relation"] not in {
            "bound_to_declared_input",
            "bounded_by_declared_capacity",
            "one_per_launch",
        }:
            incompatible.append(f"invalid_buffer_count_relation:{name}")
        static[name] = item
    dynamic: dict[str, Mapping[str, object]] = {}
    owners: set[object] = set()
    devices: set[object] = set()
    streams: set[object] = set()
    epochs: set[object] = set()
    for index, raw in enumerate(bindings):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"semantic", "element_count", "writable", "owner_nonce", "device_id", "stream_id", "mutation_epoch"},
            f"instance_contract.bindings[{index}]",
            unknown,
            incompatible,
        ):
            continue
        name = item["semantic"]
        if not isinstance(name, str) or name in dynamic:
            incompatible.append(f"invalid_or_duplicate_binding:{name!r}")
            continue
        for key in ("element_count", "device_id", "stream_id", "mutation_epoch"):
            if not _is_plain_int(item[key]) or item[key] < 0:
                incompatible.append(f"invalid_binding_integer:{name}.{key}")
        if not isinstance(item["writable"], bool):
            incompatible.append(f"invalid_binding_writable:{name}")
        if not isinstance(item["owner_nonce"], str) or not item["owner_nonce"]:
            incompatible.append(f"invalid_binding_owner:{name}")
        dynamic[name] = item
        owners.add(item["owner_nonce"])
        devices.add(item["device_id"])
        streams.add(item["stream_id"])
        epochs.add(item["mutation_epoch"])
    if set(static) != set(dynamic):
        incompatible.append("buffer_binding_membership_mismatch")
    if len(owners) != 1 or len(devices) != 1 or len(streams) != 1 or len(epochs) != 1:
        incompatible.append("buffer_binding_owner_device_stream_epoch_mismatch")
    for name in set(static) & set(dynamic):
        expected_writable = static[name]["access"] != "read_only"
        if dynamic[name]["writable"] is not expected_writable:
            incompatible.append(f"buffer_mutability_mismatch:{name}")
        relation = static[name]["count_relation"]
        count = dynamic[name]["element_count"]
        if relation == "bound_to_declared_input" and count != instance.get("element_count"):
            incompatible.append(f"buffer_input_count_mismatch:{name}")
        elif relation == "bounded_by_declared_capacity":
            capacity = instance.get("capacity")
            if _is_plain_int(count) and _is_plain_int(capacity) and count > capacity:
                incompatible.append(f"buffer_capacity_relation_violated:{name}")
        elif relation == "one_per_launch" and count != 1:
            incompatible.append(f"buffer_status_count_mismatch:{name}")


def _check_source_evidence(
    evidence: Mapping[str, object],
    source_manifest: Mapping[str, object],
    evidence_authority: Mapping[str, object],
    unknown: list[str],
    incompatible: list[str],
) -> None:
    source_pins = _mapping(evidence.get("source_pins"))
    authority_sources = source_manifest
    if source_pins is None:
        unknown.append("missing_or_nonobject:evidence_contract.source_pins")
        return
    if authority_sources is None:
        unknown.append("missing_or_nonobject:authority.source_manifest")
        return
    if not source_pins:
        incompatible.append("empty_source_pins")
    for path, claimed_sha in sorted(source_pins.items()):
        if not isinstance(path, str) or not _is_sha(claimed_sha):
            incompatible.append(f"invalid_source_pin:{path!r}")
        elif path not in authority_sources:
            unknown.append(f"source_pin_not_in_authority:{path}")
        elif authority_sources[path] != claimed_sha:
            incompatible.append(f"source_identity_mismatch:{path}")
    for key, authority_key in (
        ("independent_oracle_sha256", "oracle_sha256_allowlist"),
        ("behavioral_receipt_sha256", "receipt_sha256_allowlist"),
    ):
        value = evidence.get(key)
        allowlist = evidence_authority.get(authority_key)
        if not _is_sha(value):
            incompatible.append(f"invalid_sha256:evidence_contract.{key}")
        elif not isinstance(allowlist, list):
            unknown.append(f"missing_or_nonlist:authority.{authority_key}")
        elif value not in allowlist:
            unknown.append(f"unrecognized_evidence:{key}")
    expected = evidence.get("oracle_output_sha256")
    observed = evidence.get("physical_output_sha256")
    _check_sha(expected, "evidence_contract.oracle_output_sha256", incompatible)
    _check_sha(observed, "evidence_contract.physical_output_sha256", incompatible)
    if expected != observed:
        incompatible.append("oracle_physical_output_mismatch")


def _check_canonical_candidates(
    certificate: Mapping[str, object],
    semantic: Mapping[str, object],
    physical: Mapping[str, object],
    unknown: list[str],
    incompatible: list[str],
) -> dict[str, object]:
    candidates = _list(certificate.get("canonical_candidates"))
    if candidates is None:
        unknown.append("missing_or_nonlist:canonical_candidates")
        return {"verdict": UNKNOWN, "candidate_count": None, "template_id": None}
    matches: list[str] = []
    semantic_policy = semantic.get("policy")
    for index, raw in enumerate(candidates):
        item = _mapping(raw)
        if not _check_exact_keys(
            item,
            {"template_id", "canonical", "algorithm_identity", "geometry_family", "schema_sha256", "guarantees"},
            f"canonical_candidates[{index}]",
            unknown,
            incompatible,
        ):
            continue
        if not isinstance(item["template_id"], str) or not item["template_id"]:
            incompatible.append(f"invalid_template_id:{index}")
            continue
        if not isinstance(item["canonical"], bool):
            incompatible.append(f"invalid_canonical_flag:{index}")
            continue
        if (
            item["canonical"]
            and item["algorithm_identity"] == semantic.get("algorithm_identity")
            and item["geometry_family"] == physical.get("geometry_family")
            and item["schema_sha256"] == physical.get("schema_sha256")
            and item["guarantees"] == semantic_policy
        ):
            matches.append(item["template_id"])
    if len(matches) == 0:
        incompatible.append("unsupported_physical_schema:no_canonical_match")
        return {"verdict": "UNSUPPORTED", "candidate_count": 0, "template_id": None}
    if len(matches) > 1:
        incompatible.append("compiler_configuration_defect:ambiguous_canonical_match")
        return {"verdict": "AMBIGUOUS", "candidate_count": len(matches), "template_id": None}
    return {"verdict": "SOLE_CANONICAL_REFERENCE", "candidate_count": 1, "template_id": matches[0]}


def evaluate_certificate(
    certificate: Mapping[str, object],
    authority: Mapping[str, object],
) -> dict[str, object]:
    """Evaluate a closed Goal5789 certificate without executable authority."""

    semantic_unknown: list[str] = []
    semantic_bad: list[str] = []
    target_unknown: list[str] = []
    target_bad: list[str] = []
    instance_unknown: list[str] = []
    instance_bad: list[str] = []

    top_keys = {
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
    _check_exact_keys(certificate, top_keys, "certificate", semantic_unknown, semantic_bad)
    if certificate.get("schema") != CERTIFICATE_SCHEMA:
        semantic_bad.append("certificate_schema_identity")
    claimed_certificate_sha = certificate.get("certificate_sha256")
    if not _is_sha(claimed_certificate_sha):
        semantic_unknown.append("missing_or_invalid:certificate_sha256")
    elif certificate_digest(certificate) != claimed_certificate_sha:
        semantic_bad.append("certificate_digest_mismatch")

    authority_keys = {
        "schema",
        "authority_sha256",
        "semantic_authority",
        "physical_authority",
        "target_authority",
        "instance_authority",
        "evidence_authority",
    }
    _check_exact_keys(authority, authority_keys, "authority", semantic_unknown, semantic_bad)
    if authority.get("schema") != AUTHORITY_SCHEMA:
        semantic_bad.append("authority_schema_identity")
    claimed_authority_sha = authority.get("authority_sha256")
    if not _is_sha(claimed_authority_sha):
        semantic_unknown.append("missing_or_invalid:authority_sha256")
    elif authority_digest(authority) != claimed_authority_sha:
        semantic_bad.append("authority_digest_mismatch")

    semantic_authority = _mapping(authority.get("semantic_authority"))
    physical_authority = _mapping(authority.get("physical_authority"))
    target_authority = _mapping(authority.get("target_authority"))
    instance_authority = _mapping(authority.get("instance_authority"))
    evidence_authority = _mapping(authority.get("evidence_authority"))
    authority_specs = (
        (
            "semantic_authority",
            semantic_authority,
            SEMANTIC_AUTHORITY_SCHEMA,
            {"schema", "authority_sha256", "contracts"},
            semantic_unknown,
            semantic_bad,
        ),
        (
            "physical_authority",
            physical_authority,
            PHYSICAL_AUTHORITY_SCHEMA,
            {"schema", "authority_sha256", "encodings", "source_manifest"},
            semantic_unknown,
            semantic_bad,
        ),
        (
            "target_authority",
            target_authority,
            TARGET_AUTHORITY_SCHEMA,
            {"schema", "authority_sha256", "target_profiles"},
            target_unknown,
            target_bad,
        ),
        (
            "instance_authority",
            instance_authority,
            INSTANCE_AUTHORITY_SCHEMA,
            {"schema", "authority_sha256", "instances"},
            instance_unknown,
            instance_bad,
        ),
        (
            "evidence_authority",
            evidence_authority,
            EVIDENCE_AUTHORITY_SCHEMA,
            {
                "schema",
                "authority_sha256",
                "oracle_sha256_allowlist",
                "receipt_sha256_allowlist",
            },
            semantic_unknown,
            semantic_bad,
        ),
    )
    for label, section, expected_schema, expected_keys, section_unknown, section_bad in authority_specs:
        if not _check_exact_keys(
            section, expected_keys, f"authority.{label}", section_unknown, section_bad
        ):
            continue
        if section["schema"] != expected_schema:
            section_bad.append(f"authority_section_schema_identity:{label}")
        claimed = section["authority_sha256"]
        if not _is_sha(claimed):
            section_unknown.append(f"missing_or_invalid:authority.{label}.authority_sha256")
        elif nested_authority_digest(section) != claimed:
            section_bad.append(f"authority_section_digest_mismatch:{label}")

    semantic = _mapping(certificate.get("semantic_request"))
    physical = _mapping(certificate.get("physical_encoding"))
    callback = _mapping(certificate.get("callback_contract"))
    target = _mapping(certificate.get("target_contract"))
    instance = _mapping(certificate.get("instance_contract"))
    evidence = _mapping(certificate.get("evidence_contract"))

    semantic_keys = {
        "contract_id",
        "algorithm_identity",
        "declared_domain_sha256",
        "policy",
        "required_hit_semantics",
        "specification_source_pin",
    }
    physical_keys = {
        "encoding_id",
        "geometry_family",
        "schema_sha256",
        "maps",
        "guarantees",
        "hit_channels",
        "gas",
        "buffers",
        "provider_source_pin",
    }
    callback_keys = {
        "ir_sha256",
        "effect_digest",
        "roles",
        "payload_u32_slots",
        "attribute_u32_slots",
        "trace_depth",
        "callable_depth",
        "total_static_iterations",
    }
    target_keys = {
        "target_sha256",
        "provider",
        "native_sha256",
        "capabilities",
        "max_payload_u32_slots",
        "max_attribute_u32_slots",
        "max_trace_depth",
        "max_callable_depth",
    }
    instance_keys = {
        "input_sha256",
        "element_count",
        "capacity",
        "numeric_inputs_finite",
        "overflow_observed",
        "bindings",
    }
    evidence_keys = {
        "source_pins",
        "independent_oracle_sha256",
        "behavioral_receipt_sha256",
        "oracle_output_sha256",
        "physical_output_sha256",
    }
    semantic_ok = _check_exact_keys(semantic, semantic_keys, "semantic_request", semantic_unknown, semantic_bad)
    physical_ok = _check_exact_keys(physical, physical_keys, "physical_encoding", semantic_unknown, semantic_bad)
    callback_ok = _check_exact_keys(callback, callback_keys, "callback_contract", semantic_unknown, semantic_bad)
    target_ok = _check_exact_keys(target, target_keys, "target_contract", target_unknown, target_bad)
    instance_ok = _check_exact_keys(instance, instance_keys, "instance_contract", instance_unknown, instance_bad)
    evidence_ok = _check_exact_keys(evidence, evidence_keys, "evidence_contract", semantic_unknown, semantic_bad)

    # The certificate cannot create its own semantic or physical truth.  It
    # must exactly replay independently pinned requirement/guarantee/fact
    # authorities.  This is the anti-circularity gate for Goal5789.
    if semantic_ok:
        contracts = None if semantic_authority is None else _mapping(semantic_authority.get("contracts"))
        authoritative = None if contracts is None else _mapping(contracts.get(semantic["contract_id"]))
        if authoritative is None:
            semantic_unknown.append("semantic_contract_not_in_independent_authority")
        elif dict(authoritative) != dict(semantic):
            semantic_bad.append("semantic_requirement_authority_mismatch")
    if physical_ok:
        encodings = None if physical_authority is None else _mapping(physical_authority.get("encodings"))
        authoritative = None if encodings is None else _mapping(encodings.get(physical["encoding_id"]))
        if authoritative is None:
            semantic_unknown.append("physical_encoding_not_in_independent_authority")
        elif dict(authoritative) != dict(physical):
            semantic_bad.append("physical_guarantee_authority_mismatch")
    if target_ok:
        profiles = None if target_authority is None else _mapping(target_authority.get("target_profiles"))
        authoritative = None if profiles is None else _mapping(profiles.get(target["target_sha256"]))
        if authoritative is None:
            target_unknown.append("target_profile_not_in_independent_authority")
        elif dict(authoritative) != dict(target):
            target_bad.append("target_capability_authority_mismatch")
    if instance_ok:
        instances = None if instance_authority is None else _mapping(instance_authority.get("instances"))
        authoritative = None if instances is None else _mapping(instances.get(instance["input_sha256"]))
        if authoritative is None:
            instance_unknown.append("instance_not_in_independent_authority")
        elif dict(authoritative) != dict(instance):
            instance_bad.append("instance_fact_authority_mismatch")

    canonical = {"verdict": UNKNOWN, "candidate_count": None, "template_id": None}
    if semantic_ok and physical_ok:
        for key in ("contract_id", "algorithm_identity", "specification_source_pin"):
            if not isinstance(semantic[key], str) or not semantic[key]:
                semantic_bad.append(f"invalid_semantic_identity:{key}")
        _check_sha(semantic["declared_domain_sha256"], "semantic_request.declared_domain_sha256", semantic_bad)
        _check_sha(physical["schema_sha256"], "physical_encoding.schema_sha256", semantic_bad)
        _check_policy(semantic, physical, semantic_unknown, semantic_bad)
        authority_sources = (
            {} if physical_authority is None
            else (_mapping(physical_authority.get("source_manifest")) or {})
        )
        _check_map_graph(physical, authority_sources, semantic_unknown, semantic_bad)
        _check_hit_channels(
            semantic,
            physical,
            callback,
            physical.get("geometry_family"),
            semantic_unknown,
            semantic_bad,
        )
        gas = _mapping(physical.get("gas"))
        if not _check_exact_keys(
            gas,
            {"geometry_family", "graph_depth", "sbt_record_stride", "update_policy"},
            "physical_encoding.gas",
            semantic_unknown,
            semantic_bad,
        ):
            pass
        else:
            if gas["geometry_family"] != physical["geometry_family"]:
                semantic_bad.append("gas_geometry_family_mismatch")
            if gas["graph_depth"] != 1 or gas["sbt_record_stride"] != 1:
                semantic_bad.append("unsupported_gas_topology")
            if gas["update_policy"] not in {"static", "declared_refit"}:
                semantic_bad.append("unsupported_gas_update_policy")
        canonical = _check_canonical_candidates(
            certificate, semantic, physical, semantic_unknown, semantic_bad
        )
        for key in ("specification_source_pin",):
            pin = semantic[key]
            if pin not in authority_sources:
                semantic_unknown.append(f"source_pin_not_in_authority:{pin}")
        for key in ("provider_source_pin",):
            pin = physical[key]
            if pin not in authority_sources:
                semantic_unknown.append(f"source_pin_not_in_authority:{pin}")

    if callback_ok and physical_ok:
        _check_sha(callback["ir_sha256"], "callback_contract.ir_sha256", semantic_bad)
        _check_sha(callback["effect_digest"], "callback_contract.effect_digest", semantic_bad)
        _check_roles(
            callback,
            physical.get("geometry_family"),
            semantic_unknown,
            semantic_bad,
        )
        for key in (
            "payload_u32_slots",
            "attribute_u32_slots",
            "trace_depth",
            "callable_depth",
            "total_static_iterations",
        ):
            if not _is_plain_int(callback[key]) or callback[key] < 0:
                semantic_bad.append(f"invalid_callback_budget:{key}")

    if target_ok and physical_ok:
        _check_sha(target["target_sha256"], "target_contract.target_sha256", target_bad)
        _check_sha(target["native_sha256"], "target_contract.native_sha256", target_bad)
        capabilities = target["capabilities"]
        profiles = None if target_authority is None else _mapping(target_authority.get("target_profiles"))
        profile = None if profiles is None else _mapping(profiles.get(target["target_sha256"]))
        if target["provider"] != "optix":
            target_bad.append("target_provider_not_optix")
        if not isinstance(capabilities, list) or any(not isinstance(item, str) for item in capabilities):
            target_bad.append("invalid_target_capabilities")
            capabilities = []
        required_cap = _GEOMETRY_RULES.get(
            physical.get("geometry_family"), {}
        ).get("required_capability")
        for capability in ("optix", "bound_program_bundle", required_cap):
            if capability and capability not in capabilities:
                target_bad.append(f"target_capability_absent:{capability}")
        if profile is None:
            target_unknown.append("target_profile_not_in_authority")
        elif dict(profile) != dict(target):
            target_bad.append("target_profile_identity_mismatch")

    if callback_ok and target_ok:
        budget_pairs = (
            ("payload_u32_slots", "max_payload_u32_slots"),
            ("attribute_u32_slots", "max_attribute_u32_slots"),
            ("trace_depth", "max_trace_depth"),
            ("callable_depth", "max_callable_depth"),
        )
        for used, maximum in budget_pairs:
            if _is_plain_int(callback[used]) and _is_plain_int(target[maximum]):
                if callback[used] > target[maximum]:
                    target_bad.append(f"target_resource_exceeded:{used}")

    if instance_ok:
        _check_sha(instance["input_sha256"], "instance_contract.input_sha256", instance_bad)
        if not _is_plain_int(instance["element_count"]) or instance["element_count"] < 0:
            instance_bad.append("invalid_instance_element_count")
        if not _is_plain_int(instance["capacity"]) or instance["capacity"] < 0:
            instance_bad.append("invalid_instance_capacity")
        if _is_plain_int(instance["element_count"]) and _is_plain_int(instance["capacity"]):
            if instance["element_count"] > instance["capacity"]:
                instance_bad.append("instance_capacity_exceeded")
        if instance["numeric_inputs_finite"] is not True:
            instance_bad.append("instance_nonfinite_input")
        if instance["overflow_observed"] is not False:
            instance_bad.append("instance_overflow")
    if instance_ok and physical_ok:
        _check_buffers_and_bindings(physical, instance, instance_unknown, instance_bad)

    if evidence_ok:
        source_manifest = (
            {} if physical_authority is None
            else (_mapping(physical_authority.get("source_manifest")) or {})
        )
        _check_source_evidence(
            evidence,
            source_manifest,
            {} if evidence_authority is None else evidence_authority,
            semantic_unknown,
            semantic_bad,
        )

    target_judgment = _verdict(
        target_unknown, target_bad, yes=CAPABLE, no=INCAPABLE
    )
    semantic_judgment = _verdict(
        semantic_unknown, semantic_bad, yes=COMPATIBLE, no=INCOMPATIBLE
    )
    instance_judgment = _verdict(
        instance_unknown, instance_bad, yes=ADMISSIBLE, no=INADMISSIBLE
    )
    reference_admitted = (
        target_judgment["verdict"] == CAPABLE
        and semantic_judgment["verdict"] == COMPATIBLE
        and instance_judgment["verdict"] == ADMISSIBLE
        and canonical["verdict"] == "SOLE_CANONICAL_REFERENCE"
    )
    body = {
        "schema": RESULT_SCHEMA,
        "certificate_sha256": certificate.get("certificate_sha256"),
        "authority_sha256": authority.get("authority_sha256"),
        "target_capable": target_judgment,
        "semantic_compatible": semantic_judgment,
        "instance_admissible": instance_judgment,
        "performance": _judgment(NOT_EVALUATED, ("performance_is_outside_goal5789",)),
        "canonical_resolution": canonical,
        "reference_admission_complete": reference_admitted,
        "executable": False,
        "execution_authorized": False,
        "authority_boundary": (
            "independent reference-admission replay only; family compiler, runtime binding, "
            "application oracle, and behavioral execution remain separate authorities"
        ),
    }
    body["result_sha256"] = digest(body)
    return body


def _load_json(path: Path) -> Mapping[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: JSON object required")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_certificate(
        _load_json(args.certificate),
        _load_json(args.authority),
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
