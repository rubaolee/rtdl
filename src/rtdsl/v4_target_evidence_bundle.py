"""Raw target-evidence bundles for bounded V4 refinement checks.

This module records evidence.  It does not decide that lowering is correct and
does not import or serialize the existing compiler protocol projection.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


TARGET_EVIDENCE_BUNDLE_SCHEMA = "rtdl.v4.target_evidence_bundle.v1"
TARGET_EVIDENCE_BUNDLE_DOMAIN = b"rtdl.v4.target_evidence_bundle.v1\0"
FAMILY_DECLARATION_SCHEMA = "rtdl.v4.family_target_declaration.v1"
SUPPORTED_ROUTE_IDS = frozenset({
    "stable::bounded_relation::canonical_bounded_pair_collection",
    "stable::triangle_reduction::checked_u64_reduction",
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query",
})
_SHA256 = re.compile(r"[0-9a-f]{64}")
_MAX_BLOB_BYTES = 64 * 1024 * 1024


class TargetEvidenceBundleError(ValueError):
    """Malformed or internally inconsistent target evidence."""


def _fail(code: str, path: str, detail: object) -> None:
    raise TargetEvidenceBundleError(f"{code}@{path}: {detail}")


def _require(condition: bool, code: str, path: str, detail: object) -> None:
    if not condition:
        _fail(code, path, detail)


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
        _fail("TE001_NOT_CANONICAL_JSON", "value", str(error))
        raise AssertionError


def _json_copy(value: object, path: str) -> object:
    try:
        return json.loads(_canonical_bytes(value).decode("ascii"))
    except TargetEvidenceBundleError:
        raise
    except Exception as error:  # pragma: no cover - canonical encoder owns this path
        _fail("TE001_NOT_CANONICAL_JSON", path, str(error))
        raise AssertionError


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest(value: object) -> str:
    return _sha256(_canonical_bytes(value))


def _sha(value: object, path: str) -> str:
    _require(
        isinstance(value, str) and _SHA256.fullmatch(value) is not None,
        "TE002_SHA256_REQUIRED",
        path,
        value,
    )
    return str(value)


def _string(value: object, path: str) -> str:
    _require(isinstance(value, str) and bool(value), "TE003_STRING_REQUIRED", path, value)
    return str(value)


def _reject_compiler_projection(value: object, path: str = "bundle") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            _require(
                key != "compiler_projection",
                "TE004_COMPILER_PROJECTION_FORBIDDEN",
                f"{path}.{key}",
                "stored compiler projection is not target evidence",
            )
            _reject_compiler_projection(item, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _reject_compiler_projection(item, f"{path}[{index}]")


def make_blob_record(payload: bytes | bytearray | memoryview | str) -> dict[str, object]:
    """Encode exact bytes with a local integrity digest."""

    if isinstance(payload, str):
        raw = payload.encode("utf-8")
        encoding = "utf-8"
    elif isinstance(payload, (bytes, bytearray, memoryview)):
        raw = bytes(payload)
        encoding = "binary"
    else:
        _fail("TE005_BLOB_REQUIRED", "payload", type(payload).__name__)
    _require(bool(raw), "TE006_EMPTY_BLOB", "payload", "empty")
    _require(
        len(raw) <= _MAX_BLOB_BYTES,
        "TE007_BLOB_TOO_LARGE",
        "payload",
        len(raw),
    )
    return {
        "schema": "rtdl.v4.target_evidence_blob.v1",
        "encoding": encoding,
        "bytes": len(raw),
        "sha256": _sha256(raw),
        "base64": base64.b64encode(raw).decode("ascii"),
    }


def validate_blob_record(record: object, path: str) -> bytes:
    _require(isinstance(record, Mapping), "TE008_BLOB_SCHEMA", path, type(record).__name__)
    assert isinstance(record, Mapping)
    _require(
        set(record) == {"schema", "encoding", "bytes", "sha256", "base64"}
        and record.get("schema") == "rtdl.v4.target_evidence_blob.v1",
        "TE008_BLOB_SCHEMA",
        path,
        sorted(record),
    )
    _require(record.get("encoding") in {"utf-8", "binary"}, "TE008_BLOB_SCHEMA", path, record.get("encoding"))
    try:
        raw = base64.b64decode(str(record["base64"]), validate=True)
    except Exception as error:
        _fail("TE009_BLOB_BASE64", path, str(error))
    _require(record.get("bytes") == len(raw), "TE010_BLOB_SIZE", path, record.get("bytes"))
    _require(record.get("sha256") == _sha256(raw), "TE011_BLOB_DIGEST", path, record.get("sha256"))
    if record.get("encoding") == "utf-8":
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as error:
            _fail("TE012_BLOB_UTF8", path, str(error))
    return raw


def registered_operator_contracts(route_id: str) -> tuple[dict[str, object], ...]:
    """Return the exact operator contracts discarded after family-plan hashing."""

    route_id = _string(route_id, "route_id")
    if route_id == "stable::bounded_relation::canonical_bounded_pair_collection":
        return ({
            "schema": "rtdl.provider_operator_contract.v1",
            "operator_id": "rtdl.result.canonical_bounded_pair_collection.v1",
            "input": "accepted_pair_events",
            "duplicate_policy": "keyed_identical_deduplicate",
            "order": "lexicographic",
            "capacity": "fail_closed_no_partial_result",
            "output": "u32_pair_rows",
        },)
    if route_id == "stable::triangle_reduction::checked_u64_reduction":
        return ({
            "schema": "rtdl.provider_operator_contract.v1",
            "operator_id": "rtdl.result.checked_u64_reduction.v1",
            "modes": ["checked_u64_product_sum", "checked_u64_sum"],
            "overflow": "fail_closed",
            "output": "u64_scalar",
        },)
    if route_id == "prospective::builtin_sphere::any_hit_count_continue_u64_per_query":
        return ({
            "schema": "rtdl.provider_operator_contract.v1",
            "operator_id": "rtdl.result.per_query_u64.v1",
            "input": "verified_finalize_output",
            "operation": "commit_per_query_u64",
            "output": "u64_per_query",
            "count_relation": "query_count",
            "overflow": "fail_closed_before_output",
        },)
    _fail("TE013_ROUTE_UNSUPPORTED", "route_id", route_id)
    raise AssertionError


def build_family_target_declaration(
    route_id: str,
    plan: object,
) -> dict[str, object]:
    """Capture one family plan plus the raw contracts its hashes commit to."""

    _require(route_id in SUPPORTED_ROUTE_IDS, "TE013_ROUTE_UNSUPPORTED", "route_id", route_id)
    to_dict = getattr(plan, "to_dict", None)
    plan_mapping = to_dict() if callable(to_dict) else plan
    plan_mapping = _json_copy(plan_mapping, "plan")
    _require(isinstance(plan_mapping, Mapping), "TE014_PLAN_REQUIRED", "plan", type(plan_mapping).__name__)
    plan_sha256 = getattr(plan, "plan_sha256", None)
    if plan_sha256 is None and isinstance(plan_mapping, Mapping):
        plan_sha256 = plan_mapping.get("plan_sha256")
    plan_sha256 = _sha(plan_sha256, "plan.plan_sha256")
    assert isinstance(plan_mapping, Mapping)
    pipeline = plan_mapping.get("family_shape", {}).get("result_pipeline") if isinstance(plan_mapping.get("family_shape"), Mapping) else None
    _require(isinstance(pipeline, list) and bool(pipeline), "TE015_RESULT_PIPELINE_REQUIRED", "plan.family_shape.result_pipeline", pipeline)
    contracts = registered_operator_contracts(route_id)
    contracts_by_id = {str(row["operator_id"]): row for row in contracts}
    for index, row in enumerate(pipeline):
        _require(isinstance(row, Mapping), "TE016_OPERATOR_ROW", f"pipeline[{index}]", row)
        operator_id = row.get("operator_id")
        _require(operator_id in contracts_by_id, "TE017_OPERATOR_CONTRACT_MISSING", f"pipeline[{index}]", operator_id)
        _require(
            row.get("operator_contract_sha256") == _digest(contracts_by_id[str(operator_id)]),
            "TE018_OPERATOR_CONTRACT_DIGEST",
            f"pipeline[{index}].operator_contract_sha256",
            row.get("operator_contract_sha256"),
        )
    declaration = {
        "schema": FAMILY_DECLARATION_SCHEMA,
        "route_id": route_id,
        "plan_sha256": plan_sha256,
        "family_plan": plan_mapping,
        "operator_contracts": list(contracts),
    }
    declaration["declaration_sha256"] = _digest(declaration)
    return declaration


def capture_family_program_artifacts(artifacts: object) -> list[dict[str, object]]:
    rows = getattr(artifacts, "artifacts", None)
    _require(isinstance(rows, tuple), "TE019_PROGRAM_ARTIFACTS_REQUIRED", "artifacts", type(rows).__name__)
    result = []
    for index, row in enumerate(rows):
        artifact_id = _string(getattr(row, "artifact_id", None), f"artifacts[{index}].artifact_id")
        format_id = _string(getattr(row, "format_id", None), f"artifacts[{index}].format_id")
        result.append({
            "artifact_id": artifact_id,
            "format_id": format_id,
            "payload": make_blob_record(getattr(row, "payload", None)),
        })
    return sorted(result, key=lambda row: str(row["artifact_id"]))


def capture_generated_target_artifacts(executable: object) -> dict[str, object]:
    """Capture raw codegen bytes without interpreting their semantics."""

    wrapper = getattr(executable, "wrapper", None)
    _require(wrapper is not None, "TE020_WRAPPER_REQUIRED", "executable.wrapper", None)
    generated = tuple(getattr(executable, "generated_leaves", ()))
    compiled = tuple(getattr(executable, "compiled_leaves", ()))
    compiled_by_role = {str(getattr(row, "role", "")): row for row in compiled}
    leaves = []
    for index, leaf in enumerate(generated):
        role_object = getattr(leaf, "role", None)
        role = getattr(role_object, "value", role_object)
        role = _string(role, f"generated_leaves[{index}].role")
        compiled_leaf = compiled_by_role.get(role)
        _require(compiled_leaf is not None, "TE021_COMPILED_LEAF_MISSING", role, sorted(compiled_by_role))
        metadata = getattr(leaf, "to_dict")(include_source=False)
        compiled_metadata = {
            key: _json_copy(getattr(compiled_leaf, key), f"compiled.{role}.{key}")
            for key in (
                "schema", "role", "abi_name", "compute_capability", "numeric_mode",
                "generated_source_sha256", "ir_sha256", "ptx_sha256", "ptx_version",
                "ptx_target", "external_symbols", "numba_version", "python_version",
                "nonce_word", "compiler_function_count",
            )
        }
        leaves.append({
            "role": role,
            "generated_metadata": _json_copy(metadata, f"generated.{role}"),
            "generated_source": make_blob_record(getattr(leaf, "generated_source", None)),
            "compiled_metadata": compiled_metadata,
            "compiled_ptx": make_blob_record(getattr(compiled_leaf, "ptx", None)),
        })
    wrapper_metadata = {
        key: _json_copy(getattr(wrapper, key), f"wrapper.{key}")
        for key in (
            "schema", "physical_template", "callback_ir_sha256",
            "callback_abi_sha256", "source_sha256", "role_symbols",
            "linked_role_symbols",
        )
    }
    composed = getattr(executable, "composed", None)
    _require(composed is not None, "TE022_COMPOSED_PTX_REQUIRED", "executable.composed", None)
    return {
        "wrapper": {
            "metadata": wrapper_metadata,
            "source": make_blob_record(getattr(wrapper, "source", None)),
            "ptx": make_blob_record(getattr(executable, "wrapper_ptx", None)),
        },
        "leaves": sorted(leaves, key=lambda row: str(row["role"])),
        "composed_ptx": make_blob_record(getattr(composed, "ptx", None)),
        "executable_metadata": {
            "schema": _string(getattr(executable, "schema", None), "executable.schema"),
            "executable_sha256": _sha(
                getattr(executable, "executable_sha256", None),
                "executable.executable_sha256",
            ),
            "composed_ptx_sha256": _sha(
                getattr(composed, "ptx_sha256", None),
                "executable.composed.ptx_sha256",
            ),
        },
    }


def build_target_evidence_bundle(
    *,
    route_id: str,
    declaration: Mapping[str, object],
    declaration_authority_sha256: str,
    program_artifacts: Sequence[Mapping[str, object]],
    generated_target_artifacts: Mapping[str, object],
    provider_descriptor: Mapping[str, object],
    provider_projection: Mapping[str, object],
    executable_identity: Mapping[str, object],
    target_binding: Mapping[str, object],
    native_producer_descriptor: Mapping[str, object],
    sbt_buffer_bindings: Mapping[str, object],
    execution_receipt: Mapping[str, object],
) -> dict[str, object]:
    """Build one sealed but still untrusted target-evidence transport object."""

    _require(route_id in SUPPORTED_ROUTE_IDS, "TE013_ROUTE_UNSUPPORTED", "route_id", route_id)
    components = {
        "declaration": declaration,
        "program_artifacts": program_artifacts,
        "generated_target_artifacts": generated_target_artifacts,
        "physical_evidence": {
            "provider_descriptor": provider_descriptor,
            "provider_projection": provider_projection,
            "executable_identity": executable_identity,
            "target_binding": target_binding,
            "native_producer_descriptor": native_producer_descriptor,
            "sbt_buffer_bindings": sbt_buffer_bindings,
        },
        "execution_receipt": execution_receipt,
    }
    _reject_compiler_projection(components)
    copied = _json_copy(components, "components")
    assert isinstance(copied, Mapping)
    document: dict[str, object] = {
        "schema": TARGET_EVIDENCE_BUNDLE_SCHEMA,
        "route_id": route_id,
        "declaration_authority_sha256": _sha(
            declaration_authority_sha256, "declaration_authority_sha256"),
        **copied,
        "claim_boundary": {
            "raw_target_evidence_transport_only": True,
            "compiler_projection_used_as_evidence": False,
            "refinement_or_correctness_established": False,
            "gpu_execution_established_by_bundle_alone": False,
            "performance_or_speedup": False,
        },
        "bundle_sha256": "",
    }
    document["bundle_sha256"] = _sha256(
        TARGET_EVIDENCE_BUNDLE_DOMAIN + _canonical_bytes(document)
    )
    validate_target_evidence_bundle(document)
    return document


def validate_target_evidence_bundle(document: object) -> None:
    _require(isinstance(document, Mapping), "TE023_BUNDLE_REQUIRED", "bundle", type(document).__name__)
    assert isinstance(document, Mapping)
    expected_keys = {
        "schema", "route_id", "declaration_authority_sha256", "declaration",
        "program_artifacts", "generated_target_artifacts", "physical_evidence",
        "execution_receipt", "claim_boundary", "bundle_sha256",
    }
    _require(set(document) == expected_keys, "TE024_BUNDLE_SCHEMA", "bundle", sorted(document))
    _require(document.get("schema") == TARGET_EVIDENCE_BUNDLE_SCHEMA, "TE024_BUNDLE_SCHEMA", "bundle.schema", document.get("schema"))
    _require(document.get("route_id") in SUPPORTED_ROUTE_IDS, "TE013_ROUTE_UNSUPPORTED", "bundle.route_id", document.get("route_id"))
    _sha(document.get("declaration_authority_sha256"), "bundle.declaration_authority_sha256")
    _reject_compiler_projection(document)
    body = dict(document)
    observed = body.pop("bundle_sha256", None)
    body["bundle_sha256"] = ""
    _require(
        observed == _sha256(TARGET_EVIDENCE_BUNDLE_DOMAIN + _canonical_bytes(body)),
        "TE025_BUNDLE_SEAL",
        "bundle.bundle_sha256",
        observed,
    )
    declaration = document.get("declaration")
    _require(isinstance(declaration, Mapping), "TE026_DECLARATION_REQUIRED", "bundle.declaration", type(declaration).__name__)
    assert isinstance(declaration, Mapping)
    _require(declaration.get("schema") == FAMILY_DECLARATION_SCHEMA, "TE026_DECLARATION_REQUIRED", "bundle.declaration.schema", declaration.get("schema"))
    _require(declaration.get("route_id") == document.get("route_id"), "TE027_ROUTE_DRIFT", "bundle.declaration.route_id", declaration.get("route_id"))
    declaration_body = dict(declaration)
    declaration_digest = declaration_body.pop("declaration_sha256", None)
    _require(declaration_digest == _digest(declaration_body), "TE028_DECLARATION_SEAL", "bundle.declaration.declaration_sha256", declaration_digest)
    artifacts = document.get("program_artifacts")
    _require(isinstance(artifacts, list) and bool(artifacts), "TE029_PROGRAM_ARTIFACTS", "bundle.program_artifacts", artifacts)
    artifact_ids = []
    for index, row in enumerate(artifacts):
        _require(isinstance(row, Mapping), "TE029_PROGRAM_ARTIFACTS", f"bundle.program_artifacts[{index}]", row)
        assert isinstance(row, Mapping)
        _require(set(row) == {"artifact_id", "format_id", "payload"}, "TE029_PROGRAM_ARTIFACTS", f"bundle.program_artifacts[{index}]", sorted(row))
        artifact_ids.append(_string(row.get("artifact_id"), f"bundle.program_artifacts[{index}].artifact_id"))
        _string(row.get("format_id"), f"bundle.program_artifacts[{index}].format_id")
        validate_blob_record(row.get("payload"), f"bundle.program_artifacts[{index}].payload")
    _require(len(artifact_ids) == len(set(artifact_ids)), "TE030_ARTIFACT_DUPLICATE", "bundle.program_artifacts", artifact_ids)
    generated = document.get("generated_target_artifacts")
    _require(isinstance(generated, Mapping), "TE031_GENERATED_REQUIRED", "bundle.generated_target_artifacts", type(generated).__name__)
    assert isinstance(generated, Mapping)
    _require(set(generated) == {"wrapper", "leaves", "composed_ptx", "executable_metadata"}, "TE031_GENERATED_REQUIRED", "bundle.generated_target_artifacts", sorted(generated))
    wrapper = generated.get("wrapper")
    _require(isinstance(wrapper, Mapping), "TE032_WRAPPER_REQUIRED", "bundle.generated.wrapper", wrapper)
    assert isinstance(wrapper, Mapping)
    _require(set(wrapper) == {"metadata", "source", "ptx"}, "TE032_WRAPPER_REQUIRED", "bundle.generated.wrapper", sorted(wrapper))
    wrapper_source = validate_blob_record(wrapper.get("source"), "bundle.generated.wrapper.source")
    validate_blob_record(wrapper.get("ptx"), "bundle.generated.wrapper.ptx")
    wrapper_metadata = wrapper.get("metadata")
    _require(isinstance(wrapper_metadata, Mapping), "TE033_WRAPPER_METADATA", "bundle.generated.wrapper.metadata", wrapper_metadata)
    assert isinstance(wrapper_metadata, Mapping)
    _require(wrapper_metadata.get("source_sha256") == _sha256(wrapper_source), "TE034_WRAPPER_SOURCE_DRIFT", "bundle.generated.wrapper", wrapper_metadata.get("source_sha256"))
    leaves = generated.get("leaves")
    _require(isinstance(leaves, list) and bool(leaves), "TE035_LEAVES_REQUIRED", "bundle.generated.leaves", leaves)
    roles = []
    for index, row in enumerate(leaves):
        _require(isinstance(row, Mapping), "TE035_LEAVES_REQUIRED", f"bundle.generated.leaves[{index}]", row)
        assert isinstance(row, Mapping)
        _require(set(row) == {"role", "generated_metadata", "generated_source", "compiled_metadata", "compiled_ptx"}, "TE035_LEAVES_REQUIRED", f"bundle.generated.leaves[{index}]", sorted(row))
        role = _string(row.get("role"), f"bundle.generated.leaves[{index}].role")
        roles.append(role)
        source = validate_blob_record(row.get("generated_source"), f"bundle.generated.leaves[{index}].generated_source")
        ptx = validate_blob_record(row.get("compiled_ptx"), f"bundle.generated.leaves[{index}].compiled_ptx")
        generated_metadata = row.get("generated_metadata")
        compiled_metadata = row.get("compiled_metadata")
        _require(isinstance(generated_metadata, Mapping) and isinstance(compiled_metadata, Mapping), "TE036_LEAF_METADATA", role, "mappings required")
        assert isinstance(generated_metadata, Mapping) and isinstance(compiled_metadata, Mapping)
        _require(generated_metadata.get("role") == role and compiled_metadata.get("role") == role, "TE037_LEAF_ROLE_DRIFT", role, "metadata")
        _require(generated_metadata.get("generated_source_sha256") == _sha256(source), "TE038_LEAF_SOURCE_DRIFT", role, generated_metadata.get("generated_source_sha256"))
        _require(compiled_metadata.get("ptx_sha256") == _sha256(ptx), "TE039_LEAF_PTX_DRIFT", role, compiled_metadata.get("ptx_sha256"))
    _require(len(roles) == len(set(roles)), "TE040_LEAF_ROLE_DUPLICATE", "bundle.generated.leaves", roles)
    composed = validate_blob_record(generated.get("composed_ptx"), "bundle.generated.composed_ptx")
    executable_metadata = generated.get("executable_metadata")
    _require(isinstance(executable_metadata, Mapping), "TE041_EXECUTABLE_METADATA", "bundle.generated.executable_metadata", executable_metadata)
    assert isinstance(executable_metadata, Mapping)
    _require(executable_metadata.get("composed_ptx_sha256") == _sha256(composed), "TE042_COMPOSED_PTX_DRIFT", "bundle.generated.composed_ptx", executable_metadata.get("composed_ptx_sha256"))
    boundary = document.get("claim_boundary")
    _require(
        isinstance(boundary, Mapping)
        and boundary.get("raw_target_evidence_transport_only") is True
        and boundary.get("compiler_projection_used_as_evidence") is False
        and all(
            value is False
            for key, value in boundary.items()
            if key not in {"raw_target_evidence_transport_only", "compiler_projection_used_as_evidence"}
        ),
        "TE043_CLAIM_BOUNDARY",
        "bundle.claim_boundary",
        boundary,
    )


__all__ = [
    "FAMILY_DECLARATION_SCHEMA",
    "SUPPORTED_ROUTE_IDS",
    "TARGET_EVIDENCE_BUNDLE_SCHEMA",
    "TargetEvidenceBundleError",
    "build_family_target_declaration",
    "build_target_evidence_bundle",
    "capture_family_program_artifacts",
    "capture_generated_target_artifacts",
    "make_blob_record",
    "registered_operator_contracts",
    "validate_blob_record",
    "validate_target_evidence_bundle",
]
