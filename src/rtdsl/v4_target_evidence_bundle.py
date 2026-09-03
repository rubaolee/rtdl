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


TARGET_EVIDENCE_BUNDLE_SCHEMA = "rtdl.v4.target_evidence_bundle.v2"
TARGET_EVIDENCE_BUNDLE_DOMAIN = b"rtdl.v4.target_evidence_bundle.v2\0"
FAMILY_DECLARATION_SCHEMA = "rtdl.v4.family_target_declaration.v1"
TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA = (
    "rtdl.v4.target_control_flow_evidence.v1"
)
TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN = (
    b"rtdl.v4.target_control_flow_evidence.v1\0"
)
SUPPORTED_ROUTE_IDS = frozenset({
    "stable::bounded_relation::canonical_bounded_pair_collection",
    "stable::triangle_reduction::checked_u64_reduction",
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query",
})
_SHA256 = re.compile(r"[0-9a-f]{64}")
_MAX_BLOB_BYTES = 64 * 1024 * 1024
_EXECUTABLE_SCHEMA_BY_ROUTE = {
    "stable::bounded_relation::canonical_bounded_pair_collection": (
        "rtdl.v4.verified_bounded_relation_executable.v1"
    ),
    "stable::triangle_reduction::checked_u64_reduction": (
        "rtdl.v4.verified_triangle_reduction_executable.v1"
    ),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        "rtdl.v4.verified_sphere_any_hit_count_executable.v1"
    ),
}
_REQUIRED_MODES_BY_ROUTE = {
    "stable::bounded_relation::canonical_bounded_pair_collection": frozenset({
        "capacity_fail_closed_collection",
    }),
    "stable::triangle_reduction::checked_u64_reduction": frozenset({
        "all_hit_count",
        "weighted_hit_count",
    }),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        frozenset({"accept_every_hit_and_continue"})
    ),
}
_TRIANGLE_MODE_BY_REDUCER = {
    "checked_u64_sum": "all_hit_count",
    "checked_u64_product_sum": "weighted_hit_count",
}


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


def _capture_executable_identity_preimage(
    executable: object,
    *,
    wrapper_source_sha256: str,
    wrapper_ptx_sha256: str,
    generated_source_sha256: list[str],
    compiled_ptx_sha256: list[str],
    composed_ptx_sha256: str,
) -> dict[str, object]:
    """Reconstruct the exact canonical record hashed by each bounded compiler."""

    schema = _string(getattr(executable, "schema", None), "executable.schema")
    options = _json_copy(
        list(getattr(executable, "compiler_options", ())),
        "executable.compiler_options",
    )
    nvrtc_log_sha256 = _sha(
        getattr(executable, "nvrtc_log_sha256", None),
        "executable.nvrtc_log_sha256",
    )
    if schema == _EXECUTABLE_SCHEMA_BY_ROUTE[
        "stable::bounded_relation::canonical_bounded_pair_collection"
    ]:
        inline_leaf_sha256 = [
            [
                _string(
                    getattr(role, "value", role),
                    f"executable.inline_cuda_leaf_sha256[{index}].role",
                ),
                _sha(digest, f"executable.inline_cuda_leaf_sha256[{index}].sha256"),
            ]
            for index, (role, digest) in enumerate(
                getattr(executable, "inline_cuda_leaf_sha256", ())
            )
        ]
        record = {
            "schema": schema,
            "authority": _sha(
                getattr(executable, "authority_sha256", None),
                "executable.authority_sha256",
            ),
            "contract": _sha(
                getattr(executable, "contract_sha256", None),
                "executable.contract_sha256",
            ),
            "abi": _sha(
                getattr(executable, "abi_sha256", None),
                "executable.abi_sha256",
            ),
            "wrapper_source": wrapper_source_sha256,
            "wrapper_ptx": wrapper_ptx_sha256,
            "generated": generated_source_sha256,
            "compiled": compiled_ptx_sha256,
            "inline_cuda": _sha(
                getattr(executable, "inline_cuda_source_sha256", None),
                "executable.inline_cuda_source_sha256",
            ),
            "inline_cuda_leaves": inline_leaf_sha256,
            "composed": composed_ptx_sha256,
            "options": options,
            "nvrtc_log": nvrtc_log_sha256,
        }
    elif schema == _EXECUTABLE_SCHEMA_BY_ROUTE[
        "stable::triangle_reduction::checked_u64_reduction"
    ]:
        record = {
            "schema": schema,
            "authority": _sha(
                getattr(executable, "authority_sha256", None),
                "executable.authority_sha256",
            ),
            "contract": _sha(
                getattr(executable, "contract_sha256", None),
                "executable.contract_sha256",
            ),
            "abi": _sha(
                getattr(executable, "abi_sha256", None),
                "executable.abi_sha256",
            ),
            "wrapper_source": wrapper_source_sha256,
            "wrapper_ptx": wrapper_ptx_sha256,
            "generated": generated_source_sha256,
            "compiled": compiled_ptx_sha256,
            "composed": composed_ptx_sha256,
            "options": options,
            "nvrtc_log": nvrtc_log_sha256,
        }
    elif schema == _EXECUTABLE_SCHEMA_BY_ROUTE[
        "prospective::builtin_sphere::any_hit_count_continue_u64_per_query"
    ]:
        record = {
            "schema": schema,
            "authority_sha256": _sha(
                getattr(executable, "authority_sha256", None),
                "executable.authority_sha256",
            ),
            "plan_sha256": _sha(
                getattr(executable, "plan_sha256", None),
                "executable.plan_sha256",
            ),
            "abi_sha256": _sha(
                getattr(executable, "abi_sha256", None),
                "executable.abi_sha256",
            ),
            "wrapper_source_sha256": wrapper_source_sha256,
            "wrapper_ptx_sha256": wrapper_ptx_sha256,
            "generated_leaf_sha256": generated_source_sha256,
            "compiled_leaf_sha256": compiled_ptx_sha256,
            "composed_ptx_sha256": composed_ptx_sha256,
            "compiler_options": options,
            "nvrtc_log_sha256": nvrtc_log_sha256,
        }
    else:
        _fail("TE044_EXECUTABLE_SCHEMA", "executable.schema", schema)
        raise AssertionError
    executable_sha256 = _sha(
        getattr(executable, "executable_sha256", None),
        "executable.executable_sha256",
    )
    _require(
        _digest(record) == executable_sha256,
        "TE045_EXECUTABLE_PREIMAGE_DRIFT",
        "executable.executable_sha256",
        executable_sha256,
    )
    return record


def capture_generated_target_artifacts(executable: object) -> dict[str, object]:
    """Capture raw codegen bytes without interpreting their semantics."""

    wrapper = getattr(executable, "wrapper", None)
    _require(wrapper is not None, "TE020_WRAPPER_REQUIRED", "executable.wrapper", None)
    generated = tuple(getattr(executable, "generated_leaves", ()))
    compiled = tuple(getattr(executable, "compiled_leaves", ()))
    compiled_roles = [str(getattr(row, "role", "")) for row in compiled]
    _require(
        len(compiled_roles) == len(set(compiled_roles)),
        "TE046_COMPILED_ROLE_DUPLICATE",
        "executable.compiled_leaves",
        compiled_roles,
    )
    compiled_by_role = dict(zip(compiled_roles, compiled, strict=True))
    leaves = []
    generated_order: list[str] = []
    generated_source_sha256: list[str] = []
    compiled_ptx_sha256: list[str] = []
    for index, leaf in enumerate(generated):
        role_object = getattr(leaf, "role", None)
        role = getattr(role_object, "value", role_object)
        role = _string(role, f"generated_leaves[{index}].role")
        generated_order.append(role)
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
        generated_source_sha256.append(
            _sha(
                metadata.get("generated_source_sha256"),
                f"generated.{role}.generated_source_sha256",
            )
        )
        compiled_ptx_sha256.append(
            _sha(compiled_metadata["ptx_sha256"], f"compiled.{role}.ptx_sha256")
        )
        leaves.append({
            "role": role,
            "generated_metadata": _json_copy(metadata, f"generated.{role}"),
            "generated_source": make_blob_record(getattr(leaf, "generated_source", None)),
            "compiled_metadata": compiled_metadata,
            "compiled_ptx": make_blob_record(getattr(compiled_leaf, "ptx", None)),
        })
    _require(
        len(generated_order) == len(set(generated_order))
        and set(generated_order) == set(compiled_roles),
        "TE047_GENERATED_COMPILED_ROLE_SET",
        "executable.leaves",
        {"generated": generated_order, "compiled": compiled_roles},
    )
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
    wrapper_source_sha256 = _sha(
        wrapper_metadata["source_sha256"], "wrapper.source_sha256"
    )
    wrapper_ptx_sha256 = _sha(
        getattr(composed, "wrapper_ptx_sha256", None),
        "executable.composed.wrapper_ptx_sha256",
    )
    composed_ptx_sha256 = _sha(
        getattr(composed, "ptx_sha256", None),
        "executable.composed.ptx_sha256",
    )
    schema = _string(getattr(executable, "schema", None), "executable.schema")
    composition_mode = (
        "inline_cuda_wrapper"
        if schema == _EXECUTABLE_SCHEMA_BY_ROUTE[
            "stable::bounded_relation::canonical_bounded_pair_collection"
        ]
        else "linked_leaf_ptx"
    )
    identity_preimage = _capture_executable_identity_preimage(
        executable,
        wrapper_source_sha256=wrapper_source_sha256,
        wrapper_ptx_sha256=wrapper_ptx_sha256,
        generated_source_sha256=generated_source_sha256,
        compiled_ptx_sha256=compiled_ptx_sha256,
        composed_ptx_sha256=composed_ptx_sha256,
    )
    return {
        "wrapper": {
            "metadata": wrapper_metadata,
            "source": make_blob_record(getattr(wrapper, "source", None)),
            "ptx": make_blob_record(getattr(executable, "wrapper_ptx", None)),
        },
        "leaves": sorted(leaves, key=lambda row: str(row["role"])),
        "composed_ptx": make_blob_record(getattr(composed, "ptx", None)),
        "executable_metadata": {
            "schema": schema,
            "executable_sha256": _sha(
                getattr(executable, "executable_sha256", None),
                "executable.executable_sha256",
            ),
            "composed_ptx_sha256": composed_ptx_sha256,
            "composition": {
                "schema": "rtdl.v4.composed_callback_ptx_evidence.v1",
                "mode": composition_mode,
                "ptx_version": _string(
                    getattr(composed, "ptx_version", None),
                    "executable.composed.ptx_version",
                ),
                "ptx_target": _string(
                    getattr(composed, "ptx_target", None),
                    "executable.composed.ptx_target",
                ),
                "address_size": _string(
                    getattr(composed, "address_size", None),
                    "executable.composed.address_size",
                ),
                "wrapper_ptx_sha256": wrapper_ptx_sha256,
                "leaf_order": generated_order,
                "leaf_bindings": [
                    {
                        "role": _string(role, "composed.leaf_bindings.role"),
                        "symbol": _string(symbol, "composed.leaf_bindings.symbol"),
                    }
                    for role, symbol in getattr(composed, "leaf_bindings", ())
                ],
                "stripped_wrapper_externs": list(
                    getattr(composed, "stripped_wrapper_externs", ())
                ),
                "stripped_numba_environments": list(
                    getattr(composed, "stripped_numba_environments", ())
                ),
            },
            "identity_preimage": identity_preimage,
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
    target_control_flow_evidence: Mapping[str, object],
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
            "target_control_flow_evidence": target_control_flow_evidence,
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


def _execution_mode_from_plan(
    route_id: str, declaration: Mapping[str, object]
) -> str:
    if route_id != "stable::triangle_reduction::checked_u64_reduction":
        return next(iter(_REQUIRED_MODES_BY_ROUTE[route_id]))
    plan = declaration.get("family_plan")
    _require(
        isinstance(plan, Mapping),
        "TE062_EXECUTION_MODE_PLAN",
        "bundle.declaration.family_plan",
        type(plan).__name__,
    )
    assert isinstance(plan, Mapping)
    protocol = plan.get("protocol_instance")
    _require(
        isinstance(protocol, Mapping),
        "TE062_EXECUTION_MODE_PLAN",
        "bundle.declaration.family_plan.protocol_instance",
        type(protocol).__name__,
    )
    assert isinstance(protocol, Mapping)
    values = protocol.get("parameter_values")
    _require(
        isinstance(values, list),
        "TE062_EXECUTION_MODE_PLAN",
        "bundle.declaration.family_plan.protocol_instance.parameter_values",
        values,
    )
    matches = [
        row.get("value")
        for row in values
        if isinstance(row, Mapping)
        and row.get("value_type") == "namespaced_identifier"
    ]
    _require(
        len(matches) == 1 and matches[0] in _TRIANGLE_MODE_BY_REDUCER,
        "TE062_EXECUTION_MODE_PLAN",
        "bundle.declaration.family_plan.protocol_instance.parameter_values",
        matches,
    )
    return _TRIANGLE_MODE_BY_REDUCER[str(matches[0])]


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
    wrapper_ptx = validate_blob_record(wrapper.get("ptx"), "bundle.generated.wrapper.ptx")
    wrapper_metadata = wrapper.get("metadata")
    _require(isinstance(wrapper_metadata, Mapping), "TE033_WRAPPER_METADATA", "bundle.generated.wrapper.metadata", wrapper_metadata)
    assert isinstance(wrapper_metadata, Mapping)
    _require(wrapper_metadata.get("source_sha256") == _sha256(wrapper_source), "TE034_WRAPPER_SOURCE_DRIFT", "bundle.generated.wrapper", wrapper_metadata.get("source_sha256"))
    leaves = generated.get("leaves")
    _require(isinstance(leaves, list) and bool(leaves), "TE035_LEAVES_REQUIRED", "bundle.generated.leaves", leaves)
    roles = []
    generated_source_sha256_by_role: dict[str, str] = {}
    compiled_ptx_sha256_by_role: dict[str, str] = {}
    symbols_by_role: dict[str, str] = {}
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
        _require(
            generated_metadata.get("abi_name") == compiled_metadata.get("abi_name"),
            "TE048_LEAF_SYMBOL_DRIFT",
            role,
            {
                "generated": generated_metadata.get("abi_name"),
                "compiled": compiled_metadata.get("abi_name"),
            },
        )
        generated_source_sha256_by_role[role] = _sha256(source)
        compiled_ptx_sha256_by_role[role] = _sha256(ptx)
        symbols_by_role[role] = _string(
            generated_metadata.get("abi_name"), f"bundle.generated.leaves.{role}.abi_name"
        )
    _require(len(roles) == len(set(roles)), "TE040_LEAF_ROLE_DUPLICATE", "bundle.generated.leaves", roles)
    composed = validate_blob_record(generated.get("composed_ptx"), "bundle.generated.composed_ptx")
    executable_metadata = generated.get("executable_metadata")
    _require(isinstance(executable_metadata, Mapping), "TE041_EXECUTABLE_METADATA", "bundle.generated.executable_metadata", executable_metadata)
    assert isinstance(executable_metadata, Mapping)
    _require(
        set(executable_metadata) == {
            "schema", "executable_sha256", "composed_ptx_sha256",
            "composition", "identity_preimage",
        },
        "TE041_EXECUTABLE_METADATA",
        "bundle.generated.executable_metadata",
        sorted(executable_metadata),
    )
    _require(executable_metadata.get("composed_ptx_sha256") == _sha256(composed), "TE042_COMPOSED_PTX_DRIFT", "bundle.generated.composed_ptx", executable_metadata.get("composed_ptx_sha256"))
    expected_schema = _EXECUTABLE_SCHEMA_BY_ROUTE[str(document["route_id"])]
    _require(
        executable_metadata.get("schema") == expected_schema,
        "TE044_EXECUTABLE_SCHEMA",
        "bundle.generated.executable_metadata.schema",
        executable_metadata.get("schema"),
    )
    composition = executable_metadata.get("composition")
    _require(
        isinstance(composition, Mapping),
        "TE049_COMPOSITION_METADATA",
        "bundle.generated.executable_metadata.composition",
        composition,
    )
    assert isinstance(composition, Mapping)
    _require(
        set(composition) == {
            "schema", "mode", "ptx_version", "ptx_target", "address_size",
            "wrapper_ptx_sha256", "leaf_order", "leaf_bindings",
            "stripped_wrapper_externs", "stripped_numba_environments",
        }
        and composition.get("schema")
        == "rtdl.v4.composed_callback_ptx_evidence.v1",
        "TE049_COMPOSITION_METADATA",
        "bundle.generated.executable_metadata.composition",
        sorted(composition),
    )
    expected_mode = (
        "inline_cuda_wrapper"
        if document.get("route_id")
        == "stable::bounded_relation::canonical_bounded_pair_collection"
        else "linked_leaf_ptx"
    )
    _require(
        composition.get("mode") == expected_mode,
        "TE050_COMPOSITION_MODE",
        "bundle.generated.executable_metadata.composition.mode",
        composition.get("mode"),
    )
    _require(
        composition.get("wrapper_ptx_sha256") == _sha256(wrapper_ptx),
        "TE051_WRAPPER_PTX_DRIFT",
        "bundle.generated.wrapper.ptx",
        composition.get("wrapper_ptx_sha256"),
    )
    leaf_order = [
        _string(item, f"composition.leaf_order[{index}]")
        for index, item in enumerate(
            composition.get("leaf_order", ())
            if isinstance(composition.get("leaf_order"), Sequence)
            else ()
        )
    ]
    _require(
        len(leaf_order) == len(set(leaf_order)) and set(leaf_order) == set(roles),
        "TE052_COMPOSITION_LEAF_ORDER",
        "bundle.generated.executable_metadata.composition.leaf_order",
        leaf_order,
    )
    raw_bindings = composition.get("leaf_bindings")
    _require(
        isinstance(raw_bindings, list),
        "TE053_COMPOSITION_BINDINGS",
        "bundle.generated.executable_metadata.composition.leaf_bindings",
        raw_bindings,
    )
    bindings: dict[str, str] = {}
    for index, raw in enumerate(raw_bindings):
        _require(
            isinstance(raw, Mapping) and set(raw) == {"role", "symbol"},
            "TE053_COMPOSITION_BINDINGS",
            f"bundle.generated.executable_metadata.composition.leaf_bindings[{index}]",
            raw,
        )
        assert isinstance(raw, Mapping)
        role = _string(raw.get("role"), f"composition.leaf_bindings[{index}].role")
        symbol = _string(raw.get("symbol"), f"composition.leaf_bindings[{index}].symbol")
        _require(role not in bindings, "TE053_COMPOSITION_BINDINGS", role, "duplicate")
        bindings[role] = symbol
    _require(
        bindings == symbols_by_role,
        "TE053_COMPOSITION_BINDINGS",
        "bundle.generated.executable_metadata.composition.leaf_bindings",
        {"expected": symbols_by_role, "observed": bindings},
    )
    if expected_mode == "inline_cuda_wrapper":
        _require(
            _sha256(composed) == _sha256(wrapper_ptx),
            "TE054_INLINE_COMPOSITION_DRIFT",
            "bundle.generated.composed_ptx",
            "inline composed PTX must equal wrapper PTX",
        )
    identity_preimage = executable_metadata.get("identity_preimage")
    _require(
        isinstance(identity_preimage, Mapping),
        "TE055_EXECUTABLE_PREIMAGE",
        "bundle.generated.executable_metadata.identity_preimage",
        identity_preimage,
    )
    assert isinstance(identity_preimage, Mapping)
    _require(
        identity_preimage.get("schema") == expected_schema,
        "TE055_EXECUTABLE_PREIMAGE",
        "bundle.generated.executable_metadata.identity_preimage.schema",
        identity_preimage.get("schema"),
    )
    preimage_generated_key = (
        "generated_leaf_sha256"
        if expected_schema
        == _EXECUTABLE_SCHEMA_BY_ROUTE[
            "prospective::builtin_sphere::any_hit_count_continue_u64_per_query"
        ]
        else "generated"
    )
    preimage_compiled_key = (
        "compiled_leaf_sha256"
        if expected_schema
        == _EXECUTABLE_SCHEMA_BY_ROUTE[
            "prospective::builtin_sphere::any_hit_count_continue_u64_per_query"
        ]
        else "compiled"
    )
    preimage_wrapper_source_key = (
        "wrapper_source_sha256"
        if preimage_generated_key == "generated_leaf_sha256"
        else "wrapper_source"
    )
    preimage_wrapper_ptx_key = (
        "wrapper_ptx_sha256"
        if preimage_generated_key == "generated_leaf_sha256"
        else "wrapper_ptx"
    )
    preimage_composed_key = (
        "composed_ptx_sha256"
        if preimage_generated_key == "generated_leaf_sha256"
        else "composed"
    )
    _require(
        identity_preimage.get(preimage_wrapper_source_key) == _sha256(wrapper_source)
        and identity_preimage.get(preimage_wrapper_ptx_key) == _sha256(wrapper_ptx)
        and identity_preimage.get(preimage_composed_key) == _sha256(composed)
        and identity_preimage.get(preimage_generated_key)
        == [generated_source_sha256_by_role[role] for role in leaf_order]
        and identity_preimage.get(preimage_compiled_key)
        == [compiled_ptx_sha256_by_role[role] for role in leaf_order],
        "TE056_EXECUTABLE_PREIMAGE_ARTIFACT_DRIFT",
        "bundle.generated.executable_metadata.identity_preimage",
        identity_preimage,
    )
    _require(
        executable_metadata.get("executable_sha256") == _digest(identity_preimage),
        "TE045_EXECUTABLE_PREIMAGE_DRIFT",
        "bundle.generated.executable_metadata.executable_sha256",
        executable_metadata.get("executable_sha256"),
    )
    physical = document.get("physical_evidence")
    _require(
        isinstance(physical, Mapping)
        and set(physical) == {
            "provider_descriptor", "provider_projection", "executable_identity",
            "target_binding", "native_producer_descriptor", "sbt_buffer_bindings",
            "target_control_flow_evidence",
        },
        "TE057_PHYSICAL_EVIDENCE",
        "bundle.physical_evidence",
        sorted(physical) if isinstance(physical, Mapping) else physical,
    )
    assert isinstance(physical, Mapping)
    control_flow = physical.get("target_control_flow_evidence")
    _require(
        isinstance(control_flow, Mapping)
        and set(control_flow) == {
            "schema", "route_id", "sources", "manifest_sha256",
        }
        and control_flow.get("schema") == TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA
        and control_flow.get("route_id") == document.get("route_id"),
        "TE058_CONTROL_FLOW_EVIDENCE",
        "bundle.physical_evidence.target_control_flow_evidence",
        control_flow,
    )
    assert isinstance(control_flow, Mapping)
    sources = control_flow.get("sources")
    _require(
        isinstance(sources, list) and bool(sources),
        "TE058_CONTROL_FLOW_EVIDENCE",
        "bundle.physical_evidence.target_control_flow_evidence.sources",
        sources,
    )
    source_paths = []
    assert isinstance(sources, list)
    for index, raw_source in enumerate(sources):
        path = (
            "bundle.physical_evidence.target_control_flow_evidence"
            f".sources[{index}]"
        )
        _require(
            isinstance(raw_source, Mapping)
            and set(raw_source) == {"repository_path", "payload"},
            "TE058_CONTROL_FLOW_EVIDENCE",
            path,
            raw_source,
        )
        assert isinstance(raw_source, Mapping)
        source_paths.append(
            _string(raw_source.get("repository_path"), f"{path}.repository_path")
        )
        validate_blob_record(raw_source.get("payload"), f"{path}.payload")
    _require(
        len(source_paths) == len(set(source_paths)),
        "TE059_CONTROL_FLOW_SOURCE_DUPLICATE",
        "bundle.physical_evidence.target_control_flow_evidence.sources",
        source_paths,
    )
    control_body = dict(control_flow)
    control_digest = control_body.pop("manifest_sha256", None)
    _require(
        control_digest
        == _sha256(
            TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN + _canonical_bytes(control_body)
        ),
        "TE060_CONTROL_FLOW_MANIFEST_SEAL",
        "bundle.physical_evidence.target_control_flow_evidence.manifest_sha256",
        control_digest,
    )
    receipt = document.get("execution_receipt")
    _require(
        isinstance(receipt, Mapping),
        "TE061_RECEIPT_CONTROL_FLOW_BINDING",
        "bundle.execution_receipt",
        receipt,
    )
    assert isinstance(receipt, Mapping)
    _require(
        set(receipt) == {
            "schema", "route_id", "mode", "plan_sha256",
            "executable_identity_sha256", "target_sha256",
            "native_library_sha256", "output_sha256", "status",
            "status_code", "status_before_output", "complete",
            "partial_result_exposed", "control_flow_manifest_sha256",
            "traversal_receipt",
        }
        and receipt.get("schema") == "rtdl.v4.goal5840_execution_receipt.v1"
        and receipt.get("route_id") == document.get("route_id")
        and receipt.get("control_flow_manifest_sha256") == control_digest,
        "TE061_RECEIPT_CONTROL_FLOW_BINDING",
        "bundle.execution_receipt",
        receipt,
    )
    expected_mode = _execution_mode_from_plan(str(document["route_id"]), declaration)
    _require(
        receipt.get("mode") == expected_mode,
        "TE062_EXECUTION_MODE_PLAN",
        "bundle.execution_receipt.mode",
        {"expected": expected_mode, "observed": receipt.get("mode")},
    )
    for field in (
        "plan_sha256", "executable_identity_sha256", "target_sha256",
        "native_library_sha256", "output_sha256",
    ):
        _sha(receipt.get(field), f"bundle.execution_receipt.{field}")
    _require(
        receipt.get("plan_sha256") == declaration.get("plan_sha256")
        and receipt.get("status") == "OK"
        and receipt.get("status_code") == 0
        and receipt.get("status_before_output") is True
        and receipt.get("complete") is True
        and receipt.get("partial_result_exposed") is False,
        "TE063_EXECUTION_RECEIPT_STATUS",
        "bundle.execution_receipt",
        receipt,
    )
    traversal = receipt.get("traversal_receipt")
    _require(
        isinstance(traversal, Mapping)
        and traversal.get("physical_executor_classification")
        == "optix_traversal_observed"
        and traversal.get("provider_library_sha256")
        == receipt.get("native_library_sha256")
        and traversal.get("output_digest") == receipt.get("output_sha256"),
        "TE064_TRUE_OPTIX_RECEIPT_BINDING",
        "bundle.execution_receipt.traversal_receipt",
        traversal,
    )
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
    "TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN",
    "TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA",
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
