#!/usr/bin/env python3
"""Standalone target-side checker for Goal5840's three bounded V4 routes.

This file intentionally imports only the Python standard library.  It does not
read RTDL's stored compiler projection and does not issue an executable
capability.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Callable


BUNDLE_SCHEMA = "rtdl.v4.target_evidence_bundle.v2"
BUNDLE_DOMAIN = b"rtdl.v4.target_evidence_bundle.v2\0"
CONTROL_FLOW_SCHEMA = "rtdl.v4.target_control_flow_evidence.v1"
CONTROL_FLOW_DOMAIN = b"rtdl.v4.target_control_flow_evidence.v1\0"
REPORT_SCHEMA = "rtdl.goal5840.independent_target_check.v1"
REPORT_DOMAIN = b"rtdl.goal5840.independent_target_check.v1\0"
FAMILY_PLAN_DOMAIN = b"rtdl.family_compilation_plan.v1\0"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
EFFECT_TAGS = {
    1: "aabb",
    2: "trace_request",
    3: "hit",
    4: "no_hit",
    5: "accept_continue",
    6: "ignore",
    7: "terminate",
    8: "payload",
    9: "output",
}
PROPERTIES = (
    "CP001_ROLE_EFFECT_CLOSURE",
    "CP002_SEMANTIC_ABI_OWNERSHIP",
    "CP003_PHYSICAL_BINDING",
    "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS",
    "CP005_EXECUTABLE_IDENTITY_CHAIN",
)
ROUTE_RULES = {
    "stable::bounded_relation::canonical_bounded_pair_collection": {
        "executable_schema": "rtdl.v4.verified_bounded_relation_executable.v1",
        "composition_mode": "inline_cuda_wrapper",
        "primitive_kind": "custom_primitive",
        "operator_id": "rtdl.result.canonical_bounded_pair_collection.v1",
        "operator_field": ("capacity", "fail_closed_no_partial_result"),
        "nominal_output": "result.canonical_pair_rows",
        "channel": ("primitive.item_id", "verified_intersection.attribute0"),
        "source_anchors": (
            "optixReportIntersection",
            ".item_id",
            "optixGetAttribute_0()",
        ),
        "status_anchors": ("params.overflowed", "atomicExch(params.overflowed"),
        "native_names": (
            "custom_primitive",
            "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES",
        ),
        "sbt_record_count_relation": "primitive_count_or_provider_defined",
        "control_flow_paths": (
            "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
            "src/rtdsl/v4_bounded_relation.py",
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
            "src/native/optix/rtdl_optix_core.cpp",
        ),
    },
    "stable::triangle_reduction::checked_u64_reduction": {
        "executable_schema": "rtdl.v4.verified_triangle_reduction_executable.v1",
        "composition_mode": "linked_leaf_ptx",
        "primitive_kind": "builtin_triangle",
        "operator_id": "rtdl.result.checked_u64_reduction.v1",
        "operator_field": ("overflow", "fail_closed"),
        "nominal_output": "result.checked_u64_scalar",
        "channel": ("primitive.index", "provider.builtin_primitive_index"),
        "source_anchors": ("optixGetPrimitiveIndex()",),
        "status_anchors": (
            "first_error_claimed != 0u",
            "const unsigned long long result",
        ),
        "native_names": (
            "builtin_triangle",
            "OPTIX_BUILD_INPUT_TYPE_TRIANGLES",
            "OPTIX_PRIMITIVE_TYPE_TRIANGLE",
        ),
        "sbt_record_count_relation": "primitive_count_or_provider_defined",
        "control_flow_paths": (
            "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        ),
    },
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": {
        "executable_schema": "rtdl.v4.verified_sphere_any_hit_count_executable.v1",
        "composition_mode": "linked_leaf_ptx",
        "primitive_kind": "builtin_sphere",
        "operator_id": "rtdl.result.per_query_u64.v1",
        "operator_field": ("overflow", "fail_closed_before_output"),
        "nominal_output": "result.per_query_u64",
        "channel": None,
        "source_anchors": (
            "optixGetPrimitiveIndex()",
            "params.output_0[query]",
            "params.output_1[query]",
        ),
        "status_anchors": (
            "first_error_claimed != 0u",
            "const unsigned long long result",
        ),
        "native_names": (
            "builtin_sphere",
            "OPTIX_BUILD_INPUT_TYPE_SPHERES",
            "OPTIX_PRIMITIVE_TYPE_SPHERE",
        ),
        "sbt_record_count_relation": "constant_one",
        "control_flow_paths": (
            "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py",
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        ),
    },
}
FIXED_MODE_BY_ROUTE = {
    "stable::bounded_relation::canonical_bounded_pair_collection": (
        "capacity_fail_closed_collection"
    ),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        "accept_every_hit_and_continue"
    ),
}
TRIANGLE_MODE_BY_REDUCER = {
    "checked_u64_sum": "all_hit_count",
    "checked_u64_product_sum": "weighted_hit_count",
}


class IndependentTargetCheckError(ValueError):
    """One fail-closed target extraction or comparison error."""

    def __init__(self, reason_id: str, path: str, detail: object) -> None:
        self.reason_id = reason_id
        self.path = path
        self.detail = str(detail)
        super().__init__(f"{reason_id}@{path}: {detail}")


def _fail(reason_id: str, path: str, detail: object) -> None:
    raise IndependentTargetCheckError(reason_id, path, detail)


def _require(condition: bool, reason_id: str, path: str, detail: object) -> None:
    if not condition:
        _fail(reason_id, path, detail)


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError) as error:
        _fail("TC000_NONCANONICAL_JSON", "value", str(error))
        raise AssertionError


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest(value: object) -> str:
    return _sha256(_canonical_bytes(value))


def _sha(value: object, path: str) -> str:
    _require(
        isinstance(value, str) and SHA256_RE.fullmatch(value) is not None,
        "TC000_SHA256_REQUIRED",
        path,
        value,
    )
    return str(value)


def _mapping(value: object, path: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), "TC000_MAPPING_REQUIRED", path, type(value).__name__)
    return value  # type: ignore[return-value]


def _sequence(value: object, path: str) -> Sequence[Any]:
    _require(
        isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)),
        "TC000_SEQUENCE_REQUIRED",
        path,
        type(value).__name__,
    )
    return value  # type: ignore[return-value]


def _text_blob(record: object, path: str, *, allow_binary: bool = False) -> str:
    row = _mapping(record, path)
    _require(
        set(row) == {"schema", "encoding", "bytes", "sha256", "base64"}
        and row.get("schema") == "rtdl.v4.target_evidence_blob.v1",
        "TC000_BLOB_SCHEMA",
        path,
        sorted(row),
    )
    try:
        payload = base64.b64decode(str(row["base64"]), validate=True)
    except Exception as error:
        _fail("TC000_BLOB_BASE64", path, str(error))
    _require(row.get("bytes") == len(payload), "TC000_BLOB_SIZE", path, row.get("bytes"))
    _require(row.get("sha256") == _sha256(payload), "TC000_BLOB_DIGEST", path, row.get("sha256"))
    _require(
        row.get("encoding") == "utf-8"
        or (allow_binary and row.get("encoding") == "binary"),
        "TC000_TEXT_BLOB_REQUIRED",
        path,
        row.get("encoding"),
    )
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as error:
        _fail("TC000_TEXT_BLOB_UTF8", path, str(error))
        raise AssertionError


def _json_artifact(bundle: Mapping[str, Any], artifact_id: str) -> Mapping[str, Any]:
    rows = _sequence(bundle.get("program_artifacts"), "bundle.program_artifacts")
    matches = [
        _mapping(row, f"bundle.program_artifacts[{index}]")
        for index, row in enumerate(rows)
        if isinstance(row, Mapping) and row.get("artifact_id") == artifact_id
    ]
    _require(len(matches) == 1, "TC000_ARTIFACT_CARDINALITY", artifact_id, len(matches))
    text = _text_blob(
        matches[0].get("payload"),
        f"artifact.{artifact_id}.payload",
        allow_binary=True,
    )
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        _fail("TC000_ARTIFACT_JSON", artifact_id, str(error))
    return _mapping(value, f"artifact.{artifact_id}.json")


def _verify_bundle_envelope(bundle: object) -> Mapping[str, Any]:
    document = _mapping(bundle, "bundle")
    expected = {
        "schema", "route_id", "declaration_authority_sha256", "declaration",
        "program_artifacts", "generated_target_artifacts", "physical_evidence",
        "execution_receipt", "claim_boundary", "bundle_sha256",
    }
    _require(set(document) == expected, "TC000_BUNDLE_SCHEMA", "bundle", sorted(document))
    _require(document.get("schema") == BUNDLE_SCHEMA, "TC000_BUNDLE_SCHEMA", "bundle.schema", document.get("schema"))
    _require(document.get("route_id") in ROUTE_RULES, "TC000_ROUTE_UNSUPPORTED", "bundle.route_id", document.get("route_id"))
    for path, value in _walk_keys(document):
        _require(path.split(".")[-1] != "compiler_projection", "TC000_COMPILER_PROJECTION_FORBIDDEN", path, value)
    body = dict(document)
    observed = body.pop("bundle_sha256", None)
    body["bundle_sha256"] = ""
    _require(observed == _sha256(BUNDLE_DOMAIN + _canonical_bytes(body)), "TC000_BUNDLE_SEAL", "bundle.bundle_sha256", observed)
    return document


def _walk_keys(value: object, path: str = "bundle"):
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{path}.{key}"
            yield child, item
            yield from _walk_keys(item, child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            yield from _walk_keys(item, f"{path}[{index}]")


def _declaration(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    declaration = _mapping(bundle.get("declaration"), "bundle.declaration")
    body = dict(declaration)
    observed = body.pop("declaration_sha256", None)
    _require(observed == _digest(body), "TC005_DECLARATION_SEAL_MISMATCH", "declaration.declaration_sha256", observed)
    _require(declaration.get("route_id") == bundle.get("route_id"), "TC003_DECLARATION_ROUTE_MISMATCH", "declaration.route_id", declaration.get("route_id"))
    return declaration


def _family_shape(declaration: Mapping[str, Any]) -> Mapping[str, Any]:
    plan = _mapping(declaration.get("family_plan"), "declaration.family_plan")
    return _mapping(plan.get("family_shape"), "declaration.family_plan.family_shape")


def _abi(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    return _json_artifact(bundle, "rtdl.callback.abi")


def _generated(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(bundle.get("generated_target_artifacts"), "bundle.generated_target_artifacts")


def _control_flow_sources(
    bundle: Mapping[str, Any],
    *,
    trusted_manifest_sha256: str,
) -> tuple[dict[str, str], str]:
    route_id = str(bundle["route_id"])
    physical = _mapping(bundle.get("physical_evidence"), "bundle.physical_evidence")
    evidence = _mapping(
        physical.get("target_control_flow_evidence"),
        "physical.target_control_flow_evidence",
    )
    _require(
        set(evidence) == {"schema", "route_id", "sources", "manifest_sha256"}
        and evidence.get("schema") == CONTROL_FLOW_SCHEMA
        and evidence.get("route_id") == route_id,
        "TC004_CONTROL_FLOW_SCHEMA",
        "physical.target_control_flow_evidence",
        sorted(evidence),
    )
    expected_paths = tuple(ROUTE_RULES[route_id]["control_flow_paths"])
    observed: dict[str, str] = {}
    for index, raw in enumerate(
        _sequence(evidence.get("sources"), "control_flow.sources")
    ):
        row = _mapping(raw, f"control_flow.sources[{index}]")
        _require(
            set(row) == {"repository_path", "payload"},
            "TC004_CONTROL_FLOW_SOURCE_SCHEMA",
            f"control_flow.sources[{index}]",
            sorted(row),
        )
        path = str(row.get("repository_path"))
        _require(
            path not in observed,
            "TC004_CONTROL_FLOW_SOURCE_DUPLICATE",
            path,
            path,
        )
        observed[path] = _text_blob(
            row.get("payload"),
            f"control_flow.sources[{index}].payload",
            allow_binary=True,
        )
    _require(
        tuple(observed) == expected_paths,
        "TC004_CONTROL_FLOW_SOURCE_SET",
        route_id,
        {"expected": expected_paths, "observed": tuple(observed)},
    )
    body = dict(evidence)
    manifest_sha256 = body.pop("manifest_sha256", None)
    computed = _sha256(CONTROL_FLOW_DOMAIN + _canonical_bytes(body))
    _require(
        manifest_sha256 == computed,
        "TC004_CONTROL_FLOW_MANIFEST_SEAL",
        "control_flow.manifest_sha256",
        manifest_sha256,
    )
    _require(
        computed == _sha(trusted_manifest_sha256, "trusted_control_flow_manifest_sha256"),
        "TC004_CONTROL_FLOW_TRUST_MISMATCH",
        "control_flow.manifest_sha256",
        computed,
    )
    receipt = _mapping(bundle.get("execution_receipt"), "bundle.execution_receipt")
    _require(
        receipt.get("control_flow_manifest_sha256") == computed,
        "TC004_CONTROL_FLOW_RECEIPT_MISMATCH",
        "execution_receipt.control_flow_manifest_sha256",
        receipt.get("control_flow_manifest_sha256"),
    )
    return observed, computed


def _leaf_effect_tags(source: str, path: str) -> frozenset[int]:
    try:
        tree = ast.parse(source, filename=path, mode="exec")
    except SyntaxError as error:
        _fail("TC001_GENERATED_SOURCE_SYNTAX", path, str(error))
    tags: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not isinstance(value, ast.Constant) or type(value.value) is not int:
            continue
        for target in targets:
            if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name):
                continue
            if target.value.id == "out_effect_tag" and value.value != 0:
                tags.add(int(value.value))
    _require(bool(tags), "TC001_NO_EFFECT_TAG", path, "no nonzero out_effect_tag assignment")
    unknown = sorted(tags - set(EFFECT_TAGS))
    _require(not unknown, "TC001_UNKNOWN_EFFECT_TAG", path, unknown)
    return frozenset(tags)


def _check_cp001(bundle: Mapping[str, Any], declaration: Mapping[str, Any]) -> dict[str, Any]:
    shape = _family_shape(declaration)
    roles = _sequence(_mapping(shape.get("callback"), "family_shape.callback").get("roles"), "family_shape.callback.roles")
    declared = {}
    for index, raw in enumerate(roles):
        row = _mapping(raw, f"family_shape.callback.roles[{index}]")
        role = str(row.get("role"))
        allowed = tuple(sorted(str(item) for item in _sequence(row.get("allowed_effects"), f"roles.{role}.allowed_effects")))
        required = tuple(sorted(str(item) for item in _sequence(row.get("required_effects"), f"roles.{role}.required_effects")))
        _require(allowed == required, "TC001_DECLARED_OPTIONAL_EFFECT_UNSUPPORTED", role, (allowed, required))
        declared[role] = allowed

    abi = _abi(bundle)
    abi_roles = {}
    abi_symbols = {}
    for index, raw in enumerate(_sequence(abi.get("roles"), "abi.roles")):
        row = _mapping(raw, f"abi.roles[{index}]")
        role = str(row.get("role"))
        effects = tuple(sorted(
            str(_mapping(effect, f"abi.roles.{role}.effect").get("kind"))
            for effect in _sequence(row.get("effects"), f"abi.roles.{role}.effects")
        ))
        abi_roles[role] = effects
        abi_symbols[role] = str(row.get("symbol"))

    generated = _generated(bundle)
    wrapper = _mapping(generated.get("wrapper"), "generated.wrapper")
    wrapper_source = _text_blob(wrapper.get("source"), "generated.wrapper.source")
    wrapper_metadata = _mapping(wrapper.get("metadata"), "generated.wrapper.metadata")
    role_symbols = {
        str(pair[0]): str(pair[1])
        for pair in _sequence(wrapper_metadata.get("role_symbols"), "wrapper.role_symbols")
        if isinstance(pair, Sequence) and len(pair) == 2
    }
    composed_ptx = _text_blob(generated.get("composed_ptx"), "generated.composed_ptx")
    target = {}
    leaf_roles = set()
    for index, raw in enumerate(_sequence(generated.get("leaves"), "generated.leaves")):
        row = _mapping(raw, f"generated.leaves[{index}]")
        role = str(row.get("role"))
        leaf_roles.add(role)
        source = _text_blob(row.get("generated_source"), f"generated.leaves.{role}.source")
        tags = _leaf_effect_tags(source, f"generated.leaves.{role}.source")
        target[role] = tuple(sorted(EFFECT_TAGS[tag] for tag in tags))
        generated_metadata = _mapping(row.get("generated_metadata"), f"generated.leaves.{role}.generated_metadata")
        compiled_metadata = _mapping(row.get("compiled_metadata"), f"generated.leaves.{role}.compiled_metadata")
        symbol = str(generated_metadata.get("abi_name"))
        _require(symbol == compiled_metadata.get("abi_name"), "TC001_LEAF_SYMBOL_MISMATCH", role, symbol)
        _require(symbol == abi_symbols.get(role), "TC001_ABI_SYMBOL_MISMATCH", role, symbol)
        _require(symbol == role_symbols.get(role), "TC001_WRAPPER_SYMBOL_MISMATCH", role, symbol)
        compiled_ptx = _text_blob(row.get("compiled_ptx"), f"generated.leaves.{role}.ptx")
        _require(symbol in wrapper_source, "TC001_WRAPPER_SYMBOL_ABSENT", role, symbol)
        _require(symbol in compiled_ptx, "TC001_LEAF_PTX_SYMBOL_ABSENT", role, symbol)
        _require(symbol in composed_ptx, "TC001_COMPOSED_PTX_SYMBOL_ABSENT", role, symbol)
    _require(set(declared) == set(abi_roles) == leaf_roles, "TC001_ROLE_SET_MISMATCH", "roles", (sorted(declared), sorted(abi_roles), sorted(leaf_roles)))
    _require(declared == abi_roles == target, "TC001_ROLE_EFFECT_MISMATCH", "roles", {"declared": declared, "abi": abi_roles, "target": target})
    return {
        "declared_facts_sha256": _digest(declared),
        "target_facts_sha256": _digest(target),
        "evidence": [
            "declaration.family_plan.family_shape.callback.roles",
            "artifact.rtdl.callback.abi.roles",
            "generated.leaves[*].generated_source AST out_effect_tag assignments",
            "generated.wrapper.metadata.role_symbols",
            "generated.wrapper.source and generated/composed PTX symbols",
        ],
    }


def _find_role(abi: Mapping[str, Any], role: str) -> Mapping[str, Any]:
    matches = [
        _mapping(row, f"abi.roles.{role}")
        for row in _sequence(abi.get("roles"), "abi.roles")
        if isinstance(row, Mapping) and row.get("role") == role
    ]
    _require(len(matches) == 1, "TC002_ABI_ROLE_CARDINALITY", role, len(matches))
    return matches[0]


def _field_paths(rows: object, path: str) -> dict[str, Mapping[str, Any]]:
    result = {}
    for index, raw in enumerate(_sequence(rows, path)):
        row = _mapping(raw, f"{path}[{index}]")
        result[str(row.get("path"))] = row
    return result


def _check_cp002(bundle: Mapping[str, Any], declaration: Mapping[str, Any]) -> dict[str, Any]:
    route_id = str(bundle["route_id"])
    rule = ROUTE_RULES[route_id]
    shape = _family_shape(declaration)
    plan = _mapping(declaration.get("family_plan"), "declaration.family_plan")
    instance = _mapping(plan.get("protocol_instance"), "declaration.family_plan.protocol_instance")
    nominal = _mapping(instance.get("nominal_semantics"), "protocol_instance.nominal_semantics")
    _require(nominal.get("output") == rule["nominal_output"], "TC002_NOMINAL_OUTPUT_MISMATCH", "protocol_instance.nominal_semantics.output", nominal.get("output"))
    abi = _abi(bundle)
    wrapper_source = _text_blob(
        _mapping(_generated(bundle).get("wrapper"), "generated.wrapper").get("source"),
        "generated.wrapper.source",
    )
    for anchor in rule["source_anchors"]:
        _require(anchor in wrapper_source, "TC002_RAW_SOURCE_ANCHOR_MISSING", route_id, anchor)

    channel_rule = rule["channel"]
    if channel_rule is not None:
        channels = _sequence(shape.get("channels"), "family_shape.channels")
        matches = [
            _mapping(row, "family_shape.channel")
            for row in channels
            if isinstance(row, Mapping)
            and row.get("semantic") == channel_rule[0]
            and row.get("ownership") == channel_rule[1]
        ]
        _require(len(matches) == 1, "TC002_CHANNEL_OWNERSHIP_MISMATCH", route_id, len(matches))
        if route_id.startswith("stable::bounded_relation"):
            intersection = _find_role(abi, "intersection")
            effect_fields = {}
            for effect in _sequence(intersection.get("effects"), "abi.intersection.effects"):
                effect_row = _mapping(effect, "abi.intersection.effect")
                effect_fields.update(_field_paths(effect_row.get("fields"), "abi.intersection.effect.fields"))
            _require("out.hit.attributes.0" in effect_fields, "TC002_ATTRIBUTE0_PRODUCER_MISSING", route_id, sorted(effect_fields))
        else:
            any_hit = _find_role(abi, "any_hit")
            inputs = _field_paths(any_hit.get("inputs"), "abi.any_hit.inputs")
            _require("in.hit.primitive_index" in inputs, "TC002_PRIMITIVE_INDEX_CONSUMER_MISSING", route_id, sorted(inputs))
    else:
        _require(not _sequence(shape.get("channels"), "family_shape.channels"), "TC002_UNEXPECTED_CHANNEL", route_id, shape.get("channels"))
        finalize = _find_role(abi, "finalize")
        output_fields = {}
        for effect in _sequence(finalize.get("effects"), "abi.finalize.effects"):
            effect_row = _mapping(effect, "abi.finalize.effect")
            output_fields.update(_field_paths(effect_row.get("fields"), "abi.finalize.effect.fields"))
        u64_outputs = [
            path for path, row in output_fields.items()
            if row.get("scalar") == "u64" and path.startswith("out.output.value.")
        ]
        _require(len(u64_outputs) == 1, "TC002_U64_OUTPUT_OWNERSHIP_MISMATCH", route_id, u64_outputs)

    target = {
        "nominal_output": rule["nominal_output"],
        "channel": channel_rule,
    }
    declared = {
        "nominal_output": nominal.get("output"),
        "channel": channel_rule if channel_rule is None else (
            matches[0].get("semantic"), matches[0].get("ownership")
        ),
    }
    return {
        "declared_facts_sha256": _digest(declared),
        "target_facts_sha256": _digest(target),
        "evidence": [
            "declaration family channels and protocol-instance nominal semantics",
            "compiled ABI producer/consumer fields",
            "raw wrapper source provider intrinsic and output anchors",
        ],
    }


def _native_name_values(value: object) -> set[str]:
    names = set()
    for _path, item in _walk_keys(value, "native"):
        if isinstance(item, str):
            names.add(item)
    return names


def _derive_plan_requirements(shape: Mapping[str, Any]) -> dict[str, Any]:
    graph_nodes = [
        _mapping(row, f"family_shape.graph_nodes[{index}]")
        for index, row in enumerate(
            _sequence(shape.get("graph_nodes"), "family_shape.graph_nodes")
        )
    ]
    callback = _mapping(shape.get("callback"), "family_shape.callback")
    roles = [
        _mapping(row, f"family_shape.callback.roles[{index}]")
        for index, row in enumerate(
            _sequence(callback.get("roles"), "family_shape.callback.roles")
        )
    ]
    channels = [
        _mapping(row, f"family_shape.channels[{index}]")
        for index, row in enumerate(
            _sequence(shape.get("channels"), "family_shape.channels")
        )
    ]
    events = [
        _mapping(row, f"family_shape.events[{index}]")
        for index, row in enumerate(
            _sequence(shape.get("events"), "family_shape.events")
        )
    ]
    pipeline = [
        _mapping(row, f"family_shape.result_pipeline[{index}]")
        for index, row in enumerate(
            _sequence(shape.get("result_pipeline"), "family_shape.result_pipeline")
        )
    ]
    provider_builtins = {
        str(producer.get("builtin"))
        for row in channels
        for producer in [_mapping(row.get("producer"), "family_shape.channel.producer")]
        if producer.get("kind") == "provider_builtin"
    } | {
        str(row.get("provider_builtin"))
        for row in events
        if row.get("source") == "provider_builtin"
    }
    operator_contracts = []
    for row in pipeline:
        _require(
            row.get("operator") == "provider_operator",
            "TC003_UNSUPPORTED_RESULT_OPERATOR",
            "family_shape.result_pipeline",
            row.get("operator"),
        )
        operator_contracts.append({
            "operator_id": str(row.get("operator_id")),
            "operator_contract_sha256": _sha(
                row.get("operator_contract_sha256"),
                "family_shape.result_pipeline.operator_contract_sha256",
            ),
        })
    body = {
        "schema": "rtdl.family_plan_requirements.v1",
        "graph_kinds": sorted({str(row.get("kind")) for row in graph_nodes}),
        "primitive_kinds": sorted({
            str(row.get("primitive_kind"))
            for row in graph_nodes
            if row.get("primitive_kind") != "none"
        }),
        "callback_roles": sorted(str(row.get("role")) for row in roles),
        "provider_builtins": sorted(provider_builtins),
        "operator_contracts": sorted(
            operator_contracts, key=lambda row: (
                row["operator_id"], row["operator_contract_sha256"]
            )
        ),
        "capabilities": sorted(str(item) for item in _sequence(
            shape.get("capabilities"), "family_shape.capabilities"
        )),
    }
    return {**body, "requirements_sha256": _digest(body)}


def _cpp_function_window(source: str, function_name: str, path: str) -> str:
    for match in re.finditer(
        r"\b" + re.escape(function_name) + r"\s*\(", source
    ):
        parentheses = 0
        closing = -1
        for index in range(match.end() - 1, len(source)):
            character = source[index]
            if character == "(":
                parentheses += 1
            elif character == ")":
                parentheses -= 1
                if parentheses == 0:
                    closing = index
                    break
        if closing < 0:
            continue
        opening = closing + 1
        while opening < len(source) and source[opening].isspace():
            opening += 1
        if opening >= len(source) or source[opening] != "{":
            continue
        depth = 0
        in_string: str | None = None
        escaped = False
        for index in range(opening, len(source)):
            character = source[index]
            if in_string is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == in_string:
                    in_string = None
                continue
            if character in {'"', "'"}:
                in_string = character
            elif character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return source[match.start():index + 1]
    _fail("TC003_NATIVE_FUNCTION_UNPARSEABLE", path, function_name)
    raise AssertionError


def _check_native_producer_source(
    route_id: str, sources: Mapping[str, str]
) -> dict[str, str]:
    callback_source = sources[
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
    ]
    if route_id.startswith("stable::bounded_relation"):
        prepare = _cpp_function_window(
            callback_source,
            "prepare_v4_bounded_relation_callback",
            "native.callback_poc",
        )
        relation = _cpp_function_window(
            callback_source, "v4_relation_accel", "native.callback_poc"
        )
        core_source = sources["src/native/optix/rtdl_optix_core.cpp"]
        build = _cpp_function_window(
            core_source, "build_custom_accel", "native.optix_core"
        )
        build_with_flags = _cpp_function_window(
            core_source, "build_custom_accel_with_flags", "native.optix_core"
        )
        _require(
            "v4_relation_accel" in prepare
            and "build_custom_accel" in relation
            and "build_custom_accel_with_flags" in build
            and "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES" in build_with_flags,
            "TC003_NATIVE_PRODUCER_CHAIN_MISMATCH",
            route_id,
            "bounded relation prepare -> relation accel -> custom primitive build",
        )
        return {
            "prepare_symbol": "prepare_v4_bounded_relation_callback",
            "build_symbol": "build_custom_accel_with_flags",
            "build_input_type": "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES",
        }
    if route_id.startswith("stable::triangle_reduction"):
        prepare = _cpp_function_window(
            callback_source,
            "prepare_v4_triangle_reduction_callback",
            "native.callback_poc",
        )
        build = _cpp_function_window(
            callback_source,
            "build_v4_triangle_anyhit_accel",
            "native.callback_poc",
        )
        _require(
            "build_v4_triangle_anyhit_accel" in prepare
            and "OPTIX_BUILD_INPUT_TYPE_TRIANGLES" in build,
            "TC003_NATIVE_PRODUCER_CHAIN_MISMATCH",
            route_id,
            "triangle prepare -> built-in triangle build",
        )
        return {
            "prepare_symbol": "prepare_v4_triangle_reduction_callback",
            "build_symbol": "build_v4_triangle_anyhit_accel",
            "build_input_type": "OPTIX_BUILD_INPUT_TYPE_TRIANGLES",
        }
    prepare = _cpp_function_window(
        callback_source,
        "prepare_v4_builtin_sphere_callback",
        "native.callback_poc",
    )
    build = _cpp_function_window(
        callback_source, "build_v4_builtin_sphere_accel", "native.callback_poc"
    )
    _require(
        "build_v4_builtin_sphere_accel" in prepare
        and "OPTIX_BUILD_INPUT_TYPE_SPHERES" in build,
        "TC003_NATIVE_PRODUCER_CHAIN_MISMATCH",
        route_id,
        "sphere prepare -> built-in sphere build",
    )
    return {
        "prepare_symbol": "prepare_v4_builtin_sphere_callback",
        "build_symbol": "build_v4_builtin_sphere_accel",
        "build_input_type": "OPTIX_BUILD_INPUT_TYPE_SPHERES",
    }


def _check_cp003(
    bundle: Mapping[str, Any],
    declaration: Mapping[str, Any],
    control_sources: Mapping[str, str],
) -> dict[str, Any]:
    route_id = str(bundle["route_id"])
    rule = ROUTE_RULES[route_id]
    shape = _family_shape(declaration)
    graph_nodes = _sequence(shape.get("graph_nodes"), "family_shape.graph_nodes")
    primitive_kinds = sorted({
        str(_mapping(row, "family_shape.graph_node").get("primitive_kind"))
        for row in graph_nodes
        if _mapping(row, "family_shape.graph_node").get("primitive_kind") != "none"
    })
    _require(primitive_kinds == [rule["primitive_kind"]], "TC003_DECLARED_PRIMITIVE_MISMATCH", route_id, primitive_kinds)
    physical = _mapping(bundle.get("physical_evidence"), "bundle.physical_evidence")
    descriptor = _mapping(
        physical.get("provider_descriptor"), "physical.provider_descriptor")
    requirements = _derive_plan_requirements(shape)
    for field in (
        "graph_kinds",
        "primitive_kinds",
        "callback_roles",
        "provider_builtins",
        "operator_contracts",
        "capabilities",
    ):
        _require(
            descriptor.get(field) == requirements[field],
            "TC003_PROVIDER_REQUIREMENT_MISMATCH",
            f"provider_descriptor.{field}",
            {"declared": requirements[field], "provider": descriptor.get(field)},
        )
    descriptor_primitives = sorted(str(item) for item in _sequence(
        descriptor.get("primitive_kinds"), "provider_descriptor.primitive_kinds"))
    _require(
        descriptor_primitives == [rule["primitive_kind"]],
        "TC003_PROVIDER_PRIMITIVE_MISMATCH",
        route_id,
        descriptor_primitives,
    )
    declared_roles = sorted(
        str(_mapping(row, "family_shape.callback.role").get("role"))
        for row in _sequence(
            _mapping(shape.get("callback"), "family_shape.callback").get("roles"),
            "family_shape.callback.roles",
        )
    )
    descriptor_roles = sorted(str(item) for item in _sequence(
        descriptor.get("callback_roles"), "provider_descriptor.callback_roles"))
    _require(
        descriptor_roles == declared_roles,
        "TC003_PROVIDER_ROLE_SET_MISMATCH",
        route_id,
        {"declared": declared_roles, "provider": descriptor_roles},
    )
    descriptor_contracts = {
        str(row.get("operator_id")): row.get("operator_contract_sha256")
        for row in (
            _mapping(item, "provider_descriptor.operator_contract")
            for item in _sequence(
                descriptor.get("operator_contracts"),
                "provider_descriptor.operator_contracts",
            )
        )
    }
    declared_contracts = {
        str(row.get("operator_id")): _digest(row)
        for row in (
            _mapping(item, "declaration.operator_contract")
            for item in _sequence(
                declaration.get("operator_contracts"),
                "declaration.operator_contracts",
            )
        )
    }
    _require(
        descriptor_contracts == declared_contracts,
        "TC003_PROVIDER_OPERATOR_CONTRACT_MISMATCH",
        route_id,
        {"declared": declared_contracts, "provider": descriptor_contracts},
    )
    native = _mapping(physical.get("native_producer_descriptor"), "physical.native_producer_descriptor")
    native_names = _native_name_values(native)
    _require(any(name in native_names for name in rule["native_names"]), "TC003_NATIVE_PRIMITIVE_EVIDENCE_MISSING", route_id, sorted(native_names))
    native_source_facts = _check_native_producer_source(route_id, control_sources)
    _require(
        native_source_facts["build_input_type"] in native_names,
        "TC003_NATIVE_DESCRIPTOR_SOURCE_MISMATCH",
        route_id,
        {"descriptor": sorted(native_names), "source": native_source_facts},
    )
    bindings = _mapping(physical.get("sbt_buffer_bindings"), "physical.sbt_buffer_bindings")
    _require(bindings.get("primitive_kind") == rule["primitive_kind"], "TC003_SBT_PRIMITIVE_MISMATCH", route_id, bindings.get("primitive_kind"))
    declared_buffers = sorted(
        (row.get("ordinal"), row.get("semantic"), row.get("value_type"))
        for row in (_mapping(item, "family_shape.buffer") for item in _sequence(shape.get("buffers"), "family_shape.buffers"))
    )
    target_buffers = sorted(
        (row.get("ordinal"), row.get("semantic"), row.get("value_type"))
        for row in (_mapping(item, "physical.binding.buffer") for item in _sequence(bindings.get("buffers"), "physical.sbt_buffer_bindings.buffers"))
    )
    _require(declared_buffers == target_buffers, "TC003_BUFFER_BINDING_MISMATCH", route_id, {"declared": declared_buffers, "target": target_buffers})
    physical_shape = _mapping(shape.get("physical"), "family_shape.physical")
    declared_sbt = _mapping(physical_shape.get("sbt"), "family_shape.physical.sbt")
    _require(bindings.get("record_stride") == declared_sbt.get("record_stride"), "TC003_SBT_STRIDE_MISMATCH", route_id, bindings.get("record_stride"))
    if rule["sbt_record_count_relation"] == "constant_one":
        _require(declared_sbt.get("record_count_relation") == "constant_one", "TC003_SBT_COUNT_RELATION_MISMATCH", route_id, declared_sbt.get("record_count_relation"))
        _require(bindings.get("record_count_relation") == "constant_one", "TC003_SBT_COUNT_RELATION_MISMATCH", route_id, bindings.get("record_count_relation"))
    wrapper_source = _text_blob(
        _mapping(_generated(bundle).get("wrapper"), "generated.wrapper").get("source"),
        "generated.wrapper.source",
    )
    for anchor in rule["source_anchors"]:
        _require(anchor in wrapper_source, "TC003_RAW_PHYSICAL_ANCHOR_MISSING", route_id, anchor)
    declared = {
        "primitive_kind": primitive_kinds[0],
        "roles": declared_roles,
        "operator_contracts": declared_contracts,
        "requirements_sha256": requirements["requirements_sha256"],
        "buffers": declared_buffers,
        "sbt": dict(declared_sbt),
    }
    target = {"primitive_kind": bindings.get("primitive_kind"), "buffers": target_buffers, "sbt": {
        "record_stride": bindings.get("record_stride"),
        "record_count_relation": bindings.get("record_count_relation"),
    }, "provider_requirements_sha256": requirements["requirements_sha256"],
        "native_source_facts": native_source_facts}
    return {
        "declared_facts_sha256": _digest(declared),
        "target_facts_sha256": _digest(target),
        "evidence": [
            "declaration graph/buffer/SBT shape",
            "native producer descriptor primitive names",
            "trusted native producer source call chain and OptiX build-input enum",
            "SBT/buffer binding receipt",
            "raw wrapper provider-intrinsic anchors",
        ],
    }


def _python_function(
    source: str, qualified_name: str, path: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as error:
        _fail("TC004_CONTROL_FLOW_PYTHON_SYNTAX", path, str(error))
    parts = qualified_name.split(".")
    body: Sequence[ast.stmt] = tree.body
    node: ast.AST | None = None
    for index, part in enumerate(parts):
        candidates = [
            item
            for item in body
            if getattr(item, "name", None) == part
            and (
                isinstance(item, ast.ClassDef)
                if index < len(parts) - 1
                else isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
        ]
        _require(
            len(candidates) == 1,
            "TC004_CONTROL_FLOW_SYMBOL_CARDINALITY",
            path,
            {"symbol": qualified_name, "matches": len(candidates)},
        )
        node = candidates[0]
        body = getattr(node, "body", ())
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    return node


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _require_nested_call(
    function: ast.AST, outer: str, inner: str, path: str
) -> int:
    matches = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or _call_name(node) != outer:
            continue
        if any(
            isinstance(child, ast.Call) and _call_name(child) == inner
            for child in ast.walk(node)
            if child is not node
        ):
            matches.append(node.lineno)
    _require(
        len(matches) == 1,
        "TC004_CONTROL_FLOW_CALL_NESTING",
        path,
        {"outer": outer, "inner": inner, "lines": matches},
    )
    return matches[0]


def _call_lines(function: ast.AST, name: str) -> list[int]:
    return sorted(
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and _call_name(node) == name
    )


def _return_constructor_lines(function: ast.AST, name: str) -> list[int]:
    return sorted(
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.Return)
        and isinstance(node.value, ast.Call)
        and _call_name(node.value) == name
    )


def _check_declared_continuation(shape: Mapping[str, Any], route_id: str) -> None:
    continuation = _mapping(
        shape.get("continuation"), "family_shape.continuation"
    )
    states = {
        str(row.get("state_id")): str(row.get("kind"))
        for row in (
            _mapping(item, "family_shape.continuation.state")
            for item in _sequence(
                continuation.get("states"), "family_shape.continuation.states"
            )
        )
    }
    transitions = {
        (
            states.get(str(row.get("from_state"))),
            str(row.get("event")),
            states.get(str(row.get("to_state"))),
        )
        for row in (
            _mapping(item, "family_shape.continuation.transition")
            for item in _sequence(
                continuation.get("transitions"),
                "family_shape.continuation.transitions",
            )
        )
    }
    required = {
        ("launched", "observe_status_failure", "status_failed"),
        ("launched", "observe_status_ok", "status_ok"),
        ("status_ok", "copy_output", "committed"),
    }
    _require(
        required <= transitions
        and not any(
            source == "status_failed" and event == "copy_output"
            for source, event, _target in transitions
        ),
        "TC004_DECLARED_CONTINUATION_MISMATCH",
        route_id,
        sorted(transitions),
    )
    invariants = set(
        str(item)
        for item in _sequence(
            continuation.get("invariants"),
            "family_shape.continuation.invariants",
        )
    )
    _require(
        {
            "copy_output_requires_status_ok",
            "status_failure_forbids_output_copy",
        }
        <= invariants,
        "TC004_DECLARED_CONTINUATION_MISMATCH",
        route_id,
        sorted(invariants),
    )


def _check_host_status_flow(
    route_id: str, sources: Mapping[str, str]
) -> dict[str, object]:
    if route_id.startswith("stable::bounded_relation"):
        runtime_path = "src/rtdsl/v4_bounded_relation_prepared_runtime.py"
        runtime = _python_function(
            sources[runtime_path], "PreparedBoundedRelationOwner.execute", runtime_path
        )
        launch_line = _require_nested_call(
            runtime, "_raise", "_execute", runtime_path
        )
        verify_lines = _call_lines(runtime, "verify_precanonical_bounded_relation")
        return_lines = _return_constructor_lines(runtime, "V4BoundedRelationResult")
        _require(
            len(verify_lines) == 1
            and len(return_lines) == 1
            and launch_line < verify_lines[0] < return_lines[0],
            "TC004_HOST_PUBLICATION_ORDER",
            runtime_path,
            {
                "launch_status": launch_line,
                "fail_closed_verify": verify_lines,
                "publish": return_lines,
            },
        )
        verifier_path = "src/rtdsl/v4_bounded_relation.py"
        verifier = _python_function(
            sources[verifier_path],
            "verify_precanonical_bounded_relation",
            verifier_path,
        )
        guarded = []
        for node in ast.walk(verifier):
            if not isinstance(node, ast.If):
                continue
            names = {
                item.id for item in ast.walk(node.test) if isinstance(item, ast.Name)
            }
            has_fail = any(
                isinstance(item, ast.Call) and _call_name(item) == "_fail"
                for statement in node.body
                for item in ast.walk(statement)
            )
            if has_fail and {
                "overflowed", "observed_unique_count", "capacity", "materialized"
            } <= names:
                guarded.append(node.lineno)
        returns = sorted(
            node.lineno for node in ast.walk(verifier) if isinstance(node, ast.Return)
        )
        _require(
            len(guarded) == 1
            and len(returns) == 1
            and guarded[0] < returns[0],
            "TC004_FAIL_CLOSED_VERIFIER_ORDER",
            verifier_path,
            {"overflow_guard": guarded, "return": returns},
        )
        return {
            "runtime_symbol": "PreparedBoundedRelationOwner.execute",
            "status_line": launch_line,
            "verification_line": verify_lines[0],
            "publication_line": return_lines[0],
            "overflow_guard_line": guarded[0],
        }
    if route_id.startswith("stable::triangle_reduction"):
        runtime_path = "src/rtdsl/v4_triangle_reduction_prepared_runtime.py"
        runtime = _python_function(
            sources[runtime_path], "PreparedTriangleReductionOwner.execute", runtime_path
        )
        launch_line = _require_nested_call(
            runtime, "_raise", "_execute", runtime_path
        )
        reduction_lines = _call_lines(runtime, "_reduce_u64")
        return_lines = _return_constructor_lines(runtime, "V4TriangleReductionResult")
        _require(
            len(reduction_lines) == 1
            and len(return_lines) == 1
            and launch_line < reduction_lines[0] < return_lines[0],
            "TC004_HOST_PUBLICATION_ORDER",
            runtime_path,
            {
                "launch_status": launch_line,
                "checked_reduction": reduction_lines,
                "publish": return_lines,
            },
        )
        return {
            "runtime_symbol": "PreparedTriangleReductionOwner.execute",
            "status_line": launch_line,
            "verification_line": reduction_lines[0],
            "publication_line": return_lines[0],
        }
    runtime_path = "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py"
    source = sources[runtime_path]
    runtime = _python_function(
        source, "PreparedSphereAnyHitCountOwner.execute", runtime_path
    )
    segment = ast.get_source_segment(source, runtime)
    _require(
        isinstance(segment, str),
        "TC004_CONTROL_FLOW_SOURCE_SEGMENT",
        runtime_path,
        "execute",
    )
    assert isinstance(segment, str)
    anchors = (
        "native_status = int(",
        "if native_status:",
        "_raise(native_status, error, \"selected sphere execute\")",
        "if any(",
        "raw_outputs = tuple(",
        "return V4SphereAnyHitCountResult(",
    )
    positions = [segment.find(anchor) for anchor in anchors]
    _require(
        all(position >= 0 for position in positions)
        and positions == sorted(positions)
        and len(set(positions)) == len(positions),
        "TC004_HOST_PUBLICATION_ORDER",
        runtime_path,
        dict(zip(anchors, positions, strict=True)),
    )
    return {
        "runtime_symbol": "PreparedSphereAnyHitCountOwner.execute",
        "ordered_anchor_offsets": positions,
    }


def _check_cp004(
    bundle: Mapping[str, Any],
    declaration: Mapping[str, Any],
    control_sources: Mapping[str, str],
    control_flow_manifest_sha256: str,
) -> dict[str, Any]:
    route_id = str(bundle["route_id"])
    rule = ROUTE_RULES[route_id]
    contracts = _sequence(declaration.get("operator_contracts"), "declaration.operator_contracts")
    matches = [
        _mapping(row, "declaration.operator_contract")
        for row in contracts
        if isinstance(row, Mapping) and row.get("operator_id") == rule["operator_id"]
    ]
    _require(len(matches) == 1, "TC004_OPERATOR_CONTRACT_MISSING", route_id, len(matches))
    field, expected = rule["operator_field"]
    _require(matches[0].get(field) == expected, "TC004_FAIL_CLOSED_CONTRACT_MISMATCH", route_id, matches[0].get(field))
    shape = _family_shape(declaration)
    _check_declared_continuation(shape, route_id)
    wrapper_source = _text_blob(
        _mapping(_generated(bundle).get("wrapper"), "generated.wrapper").get("source"),
        "generated.wrapper.source",
    )
    first_anchor, second_anchor = rule["status_anchors"]
    first_index = wrapper_source.find(first_anchor)
    second_index = wrapper_source.find(second_anchor)
    _require(first_index >= 0 and second_index >= 0, "TC004_STATUS_SOURCE_ANCHOR_MISSING", route_id, (first_anchor, second_anchor))
    if route_id != "stable::bounded_relation::canonical_bounded_pair_collection":
        _require(first_index < second_index, "TC004_STATUS_AFTER_OUTPUT", route_id, (first_index, second_index))
    host_flow = _check_host_status_flow(route_id, control_sources)
    receipt = _mapping(bundle.get("execution_receipt"), "bundle.execution_receipt")
    if route_id in FIXED_MODE_BY_ROUTE:
        expected_mode = FIXED_MODE_BY_ROUTE[route_id]
    else:
        plan = _mapping(
            declaration.get("family_plan"), "declaration.family_plan"
        )
        protocol = _mapping(
            plan.get("protocol_instance"),
            "declaration.family_plan.protocol_instance",
        )
        values = _sequence(
            protocol.get("parameter_values"),
            "declaration.family_plan.protocol_instance.parameter_values",
        )
        reducers = [
            row.get("value")
            for row in values
            if isinstance(row, Mapping)
            and row.get("value_type") == "namespaced_identifier"
        ]
        _require(
            len(reducers) == 1 and reducers[0] in TRIANGLE_MODE_BY_REDUCER,
            "TC004_MODE_PLAN_MISMATCH",
            "declaration.family_plan.protocol_instance.parameter_values",
            reducers,
        )
        expected_mode = TRIANGLE_MODE_BY_REDUCER[str(reducers[0])]
    _require(
        receipt.get("schema") == "rtdl.v4.goal5840_execution_receipt.v1"
        and receipt.get("route_id") == route_id
        and receipt.get("mode") == expected_mode
        and receipt.get("plan_sha256") == declaration.get("plan_sha256"),
        "TC004_MODE_PLAN_MISMATCH",
        "execution_receipt",
        {
            "expected_route": route_id,
            "expected_mode": expected_mode,
            "observed_route": receipt.get("route_id"),
            "observed_mode": receipt.get("mode"),
        },
    )
    _require(receipt.get("status") == "OK" and receipt.get("status_code") == 0, "TC004_EXECUTION_STATUS_NOT_OK", route_id, (receipt.get("status"), receipt.get("status_code")))
    _require(receipt.get("status_before_output") is True, "TC004_STATUS_BEFORE_OUTPUT_MISSING", route_id, receipt.get("status_before_output"))
    _require(receipt.get("complete") is True, "TC004_COMPLETENESS_MISSING", route_id, receipt.get("complete"))
    _require(receipt.get("partial_result_exposed") is False, "TC004_PARTIAL_RESULT_EXPOSED", route_id, receipt.get("partial_result_exposed"))
    facts = {
        "operator_id": rule["operator_id"],
        field: expected,
        "status_before_output": True,
        "complete": True,
        "partial_result_exposed": False,
        "execution_mode": expected_mode,
        "control_flow_manifest_sha256": control_flow_manifest_sha256,
        "host_flow": host_flow,
    }
    return {
        "declared_facts_sha256": _digest({"operator_id": rule["operator_id"], field: matches[0].get(field)}),
        "target_facts_sha256": _digest(facts),
        "evidence": [
            "raw operator contract bound by plan hash",
            "raw wrapper status/control-flow anchors",
            "externally trusted host continuation source AST and native source manifest",
            "execution receipt status/completeness/exposure fields",
        ],
    }


def _ptx_directives(ptx: str, path: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in ptx.splitlines():
        match = re.match(r"^\s*\.(version|target|address_size)\s+(.+?)\s*$", line)
        if match is None:
            continue
        key, value = match.groups()
        _require(key not in result, "TC005_PTX_DIRECTIVE_DUPLICATE", path, key)
        result[key] = value
    _require(
        set(result) == {"version", "target", "address_size"},
        "TC005_PTX_DIRECTIVE_SET",
        path,
        sorted(result),
    )
    return result


def _generated_identity_facts(
    bundle: Mapping[str, Any], plan: Mapping[str, Any]
) -> dict[str, Any]:
    route_id = str(bundle["route_id"])
    rule = ROUTE_RULES[route_id]
    generated = _generated(bundle)
    wrapper = _mapping(generated.get("wrapper"), "generated.wrapper")
    wrapper_metadata = _mapping(wrapper.get("metadata"), "generated.wrapper.metadata")
    wrapper_source = _text_blob(wrapper.get("source"), "generated.wrapper.source")
    wrapper_ptx = _text_blob(wrapper.get("ptx"), "generated.wrapper.ptx")
    wrapper_source_sha = _sha256(wrapper_source.encode("utf-8"))
    wrapper_ptx_sha = _sha256(wrapper_ptx.encode("utf-8"))
    _require(
        wrapper_metadata.get("source_sha256") == wrapper_source_sha,
        "TC005_WRAPPER_SOURCE_DIGEST_MISMATCH",
        "generated.wrapper.metadata.source_sha256",
        wrapper_metadata.get("source_sha256"),
    )
    for field, plan_field in (
        ("callback_ir_sha256", "callback_ir_sha256"),
        ("callback_abi_sha256", "abi_sha256"),
    ):
        _require(
            wrapper_metadata.get(field) == plan.get(plan_field),
            "TC005_WRAPPER_PLAN_IDENTITY_MISMATCH",
            f"generated.wrapper.metadata.{field}",
            {"wrapper": wrapper_metadata.get(field), "plan": plan.get(plan_field)},
        )

    leaf_rows: dict[str, Mapping[str, Any]] = {}
    source_sha_by_role: dict[str, str] = {}
    ptx_sha_by_role: dict[str, str] = {}
    symbol_by_role: dict[str, str] = {}
    for index, raw in enumerate(_sequence(generated.get("leaves"), "generated.leaves")):
        row = _mapping(raw, f"generated.leaves[{index}]")
        role = str(row.get("role"))
        _require(role not in leaf_rows, "TC005_LEAF_ROLE_DUPLICATE", role, role)
        leaf_rows[role] = row
        source = _text_blob(row.get("generated_source"), f"generated.leaves.{role}.source")
        ptx = _text_blob(row.get("compiled_ptx"), f"generated.leaves.{role}.ptx")
        source_sha = _sha256(source.encode("utf-8"))
        ptx_sha = _sha256(ptx.encode("utf-8"))
        source_sha_by_role[role] = source_sha
        ptx_sha_by_role[role] = ptx_sha
        generated_metadata = _mapping(
            row.get("generated_metadata"), f"generated.leaves.{role}.generated_metadata"
        )
        compiled_metadata = _mapping(
            row.get("compiled_metadata"), f"generated.leaves.{role}.compiled_metadata"
        )
        symbol = str(generated_metadata.get("abi_name"))
        symbol_by_role[role] = symbol
        checks = (
            (
                generated_metadata.get("generated_source_sha256"),
                source_sha,
                "generated_source_sha256",
            ),
            (
                generated_metadata.get("callback_ir_sha256"),
                plan.get("callback_ir_sha256"),
                "generated.callback_ir_sha256",
            ),
            (
                generated_metadata.get("callback_effect_digest"),
                plan.get("effect_digest"),
                "generated.callback_effect_digest",
            ),
            (
                generated_metadata.get("callback_abi_sha256"),
                plan.get("abi_sha256"),
                "generated.callback_abi_sha256",
            ),
            (
                compiled_metadata.get("generated_source_sha256"),
                source_sha,
                "compiled.generated_source_sha256",
            ),
            (
                compiled_metadata.get("ir_sha256"),
                plan.get("callback_ir_sha256"),
                "compiled.ir_sha256",
            ),
            (compiled_metadata.get("ptx_sha256"), ptx_sha, "compiled.ptx_sha256"),
            (compiled_metadata.get("abi_name"), symbol, "compiled.abi_name"),
            (compiled_metadata.get("role"), role, "compiled.role"),
        )
        for observed, expected, label in checks:
            _require(
                observed == expected,
                "TC005_LEAF_IDENTITY_MISMATCH",
                f"generated.leaves.{role}.{label}",
                {"observed": observed, "expected": expected},
            )
        _ptx_directives(ptx, f"generated.leaves.{role}.ptx")

    executable_metadata = _mapping(
        generated.get("executable_metadata"), "generated.executable_metadata"
    )
    _require(
        set(executable_metadata) == {
            "schema", "executable_sha256", "composed_ptx_sha256",
            "composition", "identity_preimage",
        },
        "TC005_EXECUTABLE_METADATA_SCHEMA",
        "generated.executable_metadata",
        sorted(executable_metadata),
    )
    _require(
        executable_metadata.get("schema") == rule["executable_schema"],
        "TC005_EXECUTABLE_SCHEMA_MISMATCH",
        "generated.executable_metadata.schema",
        executable_metadata.get("schema"),
    )
    composed_ptx = _text_blob(generated.get("composed_ptx"), "generated.composed_ptx")
    composed_sha = _sha256(composed_ptx.encode("utf-8"))
    _require(
        executable_metadata.get("composed_ptx_sha256") == composed_sha,
        "TC005_COMPOSED_PTX_MISMATCH",
        "generated.executable_metadata.composed_ptx_sha256",
        composed_sha,
    )
    composition = _mapping(
        executable_metadata.get("composition"),
        "generated.executable_metadata.composition",
    )
    _require(
        composition.get("schema") == "rtdl.v4.composed_callback_ptx_evidence.v1"
        and composition.get("mode") == rule["composition_mode"],
        "TC005_COMPOSITION_MODE_MISMATCH",
        "generated.executable_metadata.composition",
        {"schema": composition.get("schema"), "mode": composition.get("mode")},
    )
    _require(
        composition.get("wrapper_ptx_sha256") == wrapper_ptx_sha,
        "TC005_WRAPPER_PTX_MISMATCH",
        "generated.executable_metadata.composition.wrapper_ptx_sha256",
        composition.get("wrapper_ptx_sha256"),
    )
    composed_directives = _ptx_directives(composed_ptx, "generated.composed_ptx")
    wrapper_directives = _ptx_directives(wrapper_ptx, "generated.wrapper.ptx")
    _require(
        composed_directives == wrapper_directives
        and composition.get("ptx_version") == composed_directives["version"]
        and composition.get("ptx_target") == composed_directives["target"]
        and composition.get("address_size") == composed_directives["address_size"],
        "TC005_COMPOSITION_TARGET_MISMATCH",
        "generated.executable_metadata.composition",
        {"composed": composed_directives, "wrapper": wrapper_directives},
    )
    leaf_order = [str(item) for item in _sequence(
        composition.get("leaf_order"), "composition.leaf_order"
    )]
    _require(
        len(leaf_order) == len(set(leaf_order)) and set(leaf_order) == set(leaf_rows),
        "TC005_COMPOSITION_LEAF_ORDER_MISMATCH",
        "composition.leaf_order",
        leaf_order,
    )
    bindings: dict[str, str] = {}
    for index, raw in enumerate(_sequence(
        composition.get("leaf_bindings"), "composition.leaf_bindings"
    )):
        row = _mapping(raw, f"composition.leaf_bindings[{index}]")
        _require(
            set(row) == {"role", "symbol"},
            "TC005_COMPOSITION_BINDING_SCHEMA",
            f"composition.leaf_bindings[{index}]",
            sorted(row),
        )
        role = str(row.get("role"))
        _require(role not in bindings, "TC005_COMPOSITION_BINDING_DUPLICATE", role, role)
        bindings[role] = str(row.get("symbol"))
    _require(
        bindings == symbol_by_role,
        "TC005_COMPOSITION_BINDING_MISMATCH",
        "composition.leaf_bindings",
        {"bindings": bindings, "leaves": symbol_by_role},
    )
    if rule["composition_mode"] == "inline_cuda_wrapper":
        _require(
            composed_ptx == wrapper_ptx,
            "TC005_INLINE_COMPOSITION_MISMATCH",
            "generated.composed_ptx",
            "inline composition must equal wrapper PTX",
        )

    preimage = _mapping(
        executable_metadata.get("identity_preimage"),
        "generated.executable_metadata.identity_preimage",
    )
    _require(
        preimage.get("schema") == rule["executable_schema"],
        "TC005_EXECUTABLE_PREIMAGE_SCHEMA",
        "generated.executable_metadata.identity_preimage.schema",
        preimage.get("schema"),
    )
    sphere = route_id.startswith("prospective::builtin_sphere")
    generated_key = "generated_leaf_sha256" if sphere else "generated"
    compiled_key = "compiled_leaf_sha256" if sphere else "compiled"
    wrapper_source_key = "wrapper_source_sha256" if sphere else "wrapper_source"
    wrapper_ptx_key = "wrapper_ptx_sha256" if sphere else "wrapper_ptx"
    composed_key = "composed_ptx_sha256" if sphere else "composed"
    abi_key = "abi_sha256" if sphere else "abi"
    _require(
        preimage.get(wrapper_source_key) == wrapper_source_sha
        and preimage.get(wrapper_ptx_key) == wrapper_ptx_sha
        and preimage.get(composed_key) == composed_sha
        and preimage.get(generated_key)
        == [source_sha_by_role[role] for role in leaf_order]
        and preimage.get(compiled_key)
        == [ptx_sha_by_role[role] for role in leaf_order]
        and preimage.get(abi_key) == plan.get("abi_sha256"),
        "TC005_EXECUTABLE_PREIMAGE_ARTIFACT_MISMATCH",
        "generated.executable_metadata.identity_preimage",
        preimage,
    )
    if sphere:
        _require(
            preimage.get("plan_sha256")
            == _sha256(FAMILY_PLAN_DOMAIN + _canonical_bytes(plan)),
            "TC005_EXECUTABLE_PREIMAGE_PLAN_MISMATCH",
            "generated.executable_metadata.identity_preimage.plan_sha256",
            preimage.get("plan_sha256"),
        )
    executable_sha = _digest(preimage)
    _require(
        executable_metadata.get("executable_sha256") == executable_sha,
        "TC005_EXECUTABLE_PREIMAGE_DIGEST_MISMATCH",
        "generated.executable_metadata.executable_sha256",
        executable_metadata.get("executable_sha256"),
    )
    return {
        "executable_sha256": executable_sha,
        "composed_ptx_sha256": composed_sha,
        "wrapper_source_sha256": wrapper_source_sha,
        "wrapper_ptx_sha256": wrapper_ptx_sha,
        "leaf_source_sha256_by_role": source_sha_by_role,
        "leaf_ptx_sha256_by_role": ptx_sha_by_role,
        "composition_mode": rule["composition_mode"],
    }


def _verify_digest_field(value: Mapping[str, Any], field: str, reason: str, path: str) -> str:
    body = dict(value)
    observed = body.pop(field, None)
    _require(observed == _digest(body), reason, path, observed)
    return str(observed)


def _program_artifact_identity(
    bundle: Mapping[str, Any], plan: Mapping[str, Any], plan_sha256: str
) -> tuple[str, list[dict[str, object]]]:
    rows = []
    formats = []
    for index, raw in enumerate(_sequence(
        bundle.get("program_artifacts"), "bundle.program_artifacts"
    )):
        row = _mapping(raw, f"bundle.program_artifacts[{index}]")
        artifact_id = str(row.get("artifact_id"))
        format_id = str(row.get("format_id"))
        payload_record = _mapping(
            row.get("payload"), f"bundle.program_artifacts[{index}].payload"
        )
        _text_blob(
            payload_record,
            f"bundle.program_artifacts[{index}].payload",
            allow_binary=True,
        )
        rows.append({
            "artifact_id": artifact_id,
            "format_id": format_id,
            "payload_bytes": payload_record.get("bytes"),
            "payload_sha256": payload_record.get("sha256"),
        })
        formats.append({"artifact_id": artifact_id, "format_id": format_id})
    rows.sort(key=lambda row: str(row["artifact_id"]))
    formats.sort(key=lambda row: (str(row["artifact_id"]), str(row["format_id"])))
    _require(
        len(rows) == len({str(row["artifact_id"]) for row in rows}),
        "TC005_PROGRAM_ARTIFACT_DUPLICATE",
        "bundle.program_artifacts",
        rows,
    )
    identity = {
        "schema": "rtdl.family_program_artifacts.v1",
        "plan_sha256": plan_sha256,
        "callback_source_sha256": plan.get("callback_source_sha256"),
        "callback_ir_sha256": plan.get("callback_ir_sha256"),
        "effect_digest": plan.get("effect_digest"),
        "abi_sha256": plan.get("abi_sha256"),
        "behavior_schema_sha256": plan.get("behavior_schema_sha256"),
        "artifacts": rows,
    }
    return _digest(identity), formats


def _check_cp005(
    bundle: Mapping[str, Any],
    declaration: Mapping[str, Any],
    trusted_declaration_sha256: str,
    trusted_executable_identity_sha256: str,
) -> dict[str, Any]:
    _require(
        declaration.get("declaration_sha256")
        == _sha(trusted_declaration_sha256, "trusted_declaration_sha256"),
        "TC005_DECLARATION_TRUST_MISMATCH",
        "declaration.declaration_sha256",
        declaration.get("declaration_sha256"),
    )
    plan = _mapping(declaration.get("family_plan"), "declaration.family_plan")
    generated_facts = _generated_identity_facts(bundle, plan)
    executable_sha = str(generated_facts["executable_sha256"])
    composed_sha = str(generated_facts["composed_ptx_sha256"])
    physical = _mapping(bundle.get("physical_evidence"), "bundle.physical_evidence")
    descriptor = _mapping(physical.get("provider_descriptor"), "physical.provider_descriptor")
    projection = _mapping(physical.get("provider_projection"), "physical.provider_projection")
    identity = _mapping(physical.get("executable_identity"), "physical.executable_identity")
    descriptor_sha = _verify_digest_field(descriptor, "descriptor_sha256", "TC005_PROVIDER_DESCRIPTOR_SEAL", "physical.provider_descriptor")
    projection_sha = _verify_digest_field(projection, "projection_sha256", "TC005_PROVIDER_PROJECTION_SEAL", "physical.provider_projection")
    identity_sha = _verify_digest_field(identity, "identity_sha256", "TC005_EXECUTABLE_IDENTITY_SEAL", "physical.executable_identity")
    _require(identity_sha == _sha(trusted_executable_identity_sha256, "trusted_executable_identity_sha256"), "TC005_EXECUTABLE_IDENTITY_TRUST_MISMATCH", "physical.executable_identity.identity_sha256", identity_sha)
    _require(identity.get("provider_descriptor_sha256") == descriptor_sha, "TC005_PROVIDER_DESCRIPTOR_CHAIN", "physical.executable_identity", identity.get("provider_descriptor_sha256"))
    _require(identity.get("provider_projection_sha256") == projection_sha, "TC005_PROVIDER_PROJECTION_CHAIN", "physical.executable_identity", identity.get("provider_projection_sha256"))
    _require(identity.get("plan_sha256") == declaration.get("plan_sha256"), "TC005_PLAN_CHAIN", "physical.executable_identity", identity.get("plan_sha256"))
    _require(identity.get("executable_sha256") == executable_sha, "TC005_EXECUTABLE_CHAIN", "physical.executable_identity", identity.get("executable_sha256"))
    _require(identity.get("generated_artifact_sha256") == composed_sha, "TC005_GENERATED_ARTIFACT_CHAIN", "physical.executable_identity", identity.get("generated_artifact_sha256"))
    target = _mapping(physical.get("target_binding"), "physical.target_binding")
    _require(identity.get("target_sha256") == target.get("target_sha256"), "TC005_TARGET_CHAIN", "physical.target_binding", target.get("target_sha256"))
    _require(identity.get("provider_artifact_sha256") == target.get("native_library_sha256"), "TC005_NATIVE_LIBRARY_CHAIN", "physical.target_binding", target.get("native_library_sha256"))
    receipt = _mapping(bundle.get("execution_receipt"), "bundle.execution_receipt")
    _require(receipt.get("plan_sha256") == declaration.get("plan_sha256"), "TC005_RECEIPT_PLAN_CHAIN", "execution_receipt.plan_sha256", receipt.get("plan_sha256"))
    _require(receipt.get("executable_identity_sha256") == identity_sha, "TC005_RECEIPT_EXECUTABLE_CHAIN", "execution_receipt.executable_identity_sha256", receipt.get("executable_identity_sha256"))
    _require(receipt.get("target_sha256") == identity.get("target_sha256"), "TC005_RECEIPT_TARGET_CHAIN", "execution_receipt.target_sha256", receipt.get("target_sha256"))
    _require(receipt.get("native_library_sha256") == identity.get("provider_artifact_sha256"), "TC005_RECEIPT_NATIVE_CHAIN", "execution_receipt.native_library_sha256", receipt.get("native_library_sha256"))
    _require(
        receipt.get("output_sha256")
        == _mapping(
            receipt.get("traversal_receipt"),
            "execution_receipt.traversal_receipt",
        ).get("output_digest"),
        "TC005_RECEIPT_OUTPUT_CHAIN",
        "execution_receipt.output_sha256",
        receipt.get("output_sha256"),
    )
    computed_plan_sha = _sha256(FAMILY_PLAN_DOMAIN + _canonical_bytes(plan))
    _require(
        declaration.get("plan_sha256") == computed_plan_sha,
        "TC005_PLAN_SEAL_MISMATCH",
        "declaration.plan_sha256",
        declaration.get("plan_sha256"),
    )
    for field in (
        "family_shape_sha256",
        "protocol_instance_sha256",
        "callback_source_sha256",
        "callback_ir_sha256",
        "effect_digest",
        "abi_sha256",
        "behavior_schema_sha256",
        "canonical_template_id",
    ):
        _require(
            projection.get(field) == plan.get(field),
            "TC005_PROVIDER_PROJECTION_FIELD_MISMATCH",
            f"physical.provider_projection.{field}",
            {"plan": plan.get(field), "projection": projection.get(field)},
        )
    artifact_bundle_sha, artifact_formats = _program_artifact_identity(
        bundle, plan, computed_plan_sha
    )
    requirements = _derive_plan_requirements(_family_shape(declaration))
    _require(
        projection.get("requirements_sha256") == requirements["requirements_sha256"],
        "TC005_PROVIDER_REQUIREMENTS_CHAIN_MISMATCH",
        "physical.provider_projection.requirements_sha256",
        projection.get("requirements_sha256"),
    )
    _require(
        projection.get("artifact_bundle_sha256") == artifact_bundle_sha,
        "TC005_PROGRAM_ARTIFACT_BUNDLE_CHAIN_MISMATCH",
        "physical.provider_projection.artifact_bundle_sha256",
        projection.get("artifact_bundle_sha256"),
    )
    _require(
        descriptor.get("artifact_formats") == artifact_formats,
        "TC005_PROVIDER_ARTIFACT_FORMAT_MISMATCH",
        "physical.provider_descriptor.artifact_formats",
        {"provider": descriptor.get("artifact_formats"), "bundle": artifact_formats},
    )
    _require(
        projection.get("provider_descriptor_sha256") == descriptor_sha
        and projection.get("plan_sha256") == declaration.get("plan_sha256"),
        "TC005_PROVIDER_PROJECTION_CHAIN_MISMATCH",
        "physical.provider_projection",
        {
            "descriptor": projection.get("provider_descriptor_sha256"),
            "plan": projection.get("plan_sha256"),
        },
    )
    abi = _abi(bundle)
    _require(plan.get("abi_sha256") == abi.get("abi_sha256"), "TC005_ABI_CHAIN", "artifact.rtdl.callback.abi", abi.get("abi_sha256"))
    _require(plan.get("callback_ir_sha256") == abi.get("callback_ir_sha256"), "TC005_CALLBACK_IR_CHAIN", "artifact.rtdl.callback.abi", abi.get("callback_ir_sha256"))
    facts = {
        "declaration_sha256": declaration.get("declaration_sha256"),
        "descriptor_sha256": descriptor_sha,
        "projection_sha256": projection_sha,
        "identity_sha256": identity_sha,
        "composed_ptx_sha256": composed_sha,
        "target_sha256": identity.get("target_sha256"),
        "native_library_sha256": identity.get("provider_artifact_sha256"),
        "generated_identity_facts_sha256": _digest(generated_facts),
        "program_artifact_bundle_sha256": artifact_bundle_sha,
        "requirements_sha256": requirements["requirements_sha256"],
    }
    return {
        "declared_facts_sha256": _digest({
            "declaration_sha256": declaration.get("declaration_sha256"),
            "trusted_executable_identity_sha256": trusted_executable_identity_sha256,
        }),
        "target_facts_sha256": _digest(facts),
        "evidence": [
            "independently supplied declaration and executable identity trust anchors",
            "provider descriptor/projection/executable identity canonical records",
            "raw wrapper/leaf/composed source and PTX identity preimage",
            "target/native binding and exact execution receipt",
            "family-plan to Callback ABI identity chain",
        ],
    }


def check_target_evidence(
    bundle: object,
    *,
    trusted_declaration_sha256: str,
    trusted_executable_identity_sha256: str,
    trusted_control_flow_manifest_sha256: str,
) -> dict[str, Any]:
    """Return all five bounded checks; never raise for a property mismatch."""

    try:
        document = _verify_bundle_envelope(bundle)
        declaration = _declaration(document)
        control_sources, control_flow_manifest_sha256 = _control_flow_sources(
            document,
            trusted_manifest_sha256=trusted_control_flow_manifest_sha256,
        )
    except IndependentTargetCheckError as error:
        rows = [{
            "property_id": property_id,
            "verdict": "REJECT",
            "reason_id": error.reason_id,
            "path": error.path,
            "detail": error.detail,
            "evidence": [],
        } for property_id in PROPERTIES]
        return _report("UNRESOLVED", rows, None)

    checks: tuple[tuple[str, Callable[[], dict[str, Any]]], ...] = (
        (PROPERTIES[0], lambda: _check_cp001(document, declaration)),
        (PROPERTIES[1], lambda: _check_cp002(document, declaration)),
        (PROPERTIES[2], lambda: _check_cp003(
            document, declaration, control_sources)),
        (PROPERTIES[3], lambda: _check_cp004(
            document, declaration, control_sources,
            control_flow_manifest_sha256)),
        (PROPERTIES[4], lambda: _check_cp005(
            document, declaration, trusted_declaration_sha256,
            trusted_executable_identity_sha256)),
    )
    rows = []
    for property_id, check in checks:
        try:
            facts = check()
            rows.append({
                "property_id": property_id,
                "verdict": "PASS",
                "reason_id": "PASS__BOUNDED_TARGET_FACTS_MATCH",
                **facts,
            })
        except IndependentTargetCheckError as error:
            rows.append({
                "property_id": property_id,
                "verdict": "REJECT",
                "reason_id": error.reason_id,
                "path": error.path,
                "detail": error.detail,
                "evidence": [],
            })
    verdict = "ACCEPT" if all(row["verdict"] == "PASS" for row in rows) else "REJECT"
    return _report(verdict, rows, str(document["route_id"]))


def _report(verdict: str, rows: list[dict[str, Any]], route_id: str | None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "route_id": route_id,
        "verdict": verdict,
        "property_checks": rows,
        "pass_count": sum(row["verdict"] == "PASS" for row in rows),
        "reject_count": sum(row["verdict"] == "REJECT" for row in rows),
        "claim_boundary": {
            "bounded_three_route_target_check_only": True,
            "executable_capability_issued": False,
            "general_compiler_soundness": False,
            "application_correctness": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "report_sha256": "",
    }
    report["report_sha256"] = _sha256(REPORT_DOMAIN + _canonical_bytes(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--trusted-declaration-sha256", required=True)
    parser.add_argument("--trusted-executable-identity-sha256", required=True)
    parser.add_argument("--trusted-control-flow-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = json.loads(args.bundle.read_text(encoding="ascii"))
    report = check_target_evidence(
        bundle,
        trusted_declaration_sha256=args.trusted_declaration_sha256,
        trusted_executable_identity_sha256=args.trusted_executable_identity_sha256,
        trusted_control_flow_manifest_sha256=(
            args.trusted_control_flow_manifest_sha256
        ),
    )
    payload = json.dumps(
        report, indent=2, sort_keys=True, ensure_ascii=True
    ) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="ascii")
    raise SystemExit(0 if report["verdict"] == "ACCEPT" else 1)


if __name__ == "__main__":
    main()
