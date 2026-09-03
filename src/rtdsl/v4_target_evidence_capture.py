"""Assemble Goal5840 evidence from one real generic-family execution.

This module is evidence infrastructure, not a public execution front door.  It
uses an exact, fail-closed bridge to recover the target executable currently
hidden behind the generic lifecycle so the evidence bundle contains the bytes
that were actually materialized.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
import hashlib
import json
from pathlib import Path
from collections.abc import Mapping

from .v4_target_control_flow_evidence import (
    capture_target_control_flow_evidence,
)
from .v4_target_evidence_bundle import (
    build_family_target_declaration,
    build_target_evidence_bundle,
    capture_family_program_artifacts,
    capture_generated_target_artifacts,
)


_BUILD_INPUT_NAME_BY_ROUTE = {
    "stable::bounded_relation::canonical_bounded_pair_collection": (
        "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES"
    ),
    "stable::triangle_reduction::checked_u64_reduction": (
        "OPTIX_BUILD_INPUT_TYPE_TRIANGLES"
    ),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        "OPTIX_BUILD_INPUT_TYPE_SPHERES"
    ),
}


class TargetEvidenceCaptureError(RuntimeError):
    """The live route cannot be represented by the bounded evidence schema."""


def _fail(path: str, detail: object) -> None:
    raise TargetEvidenceCaptureError(f"{path}: {detail}")


def _canonical_copy(value: object, path: str) -> object:
    try:
        return json.loads(
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
        )
    except (TypeError, ValueError) as error:
        _fail(path, error)
        raise AssertionError


def _to_dict(value: object, path: str) -> dict[str, object]:
    method = getattr(value, "to_dict", None)
    if not callable(method):
        _fail(path, "to_dict() required")
    result = _canonical_copy(method(), path)
    if not isinstance(result, dict):
        _fail(path, "mapping required")
    return result


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dataclass_scalars(value: object, path: str) -> dict[str, object]:
    if not is_dataclass(value) or isinstance(value, type):
        _fail(path, "dataclass instance required")
    result: dict[str, object] = {}
    for field in fields(value):
        item = getattr(value, field.name)
        if isinstance(item, Path):
            result[field.name] = str(item.resolve())
        elif isinstance(item, tuple):
            result[field.name] = list(item)
        elif isinstance(item, (str, int, float, bool)) or item is None:
            result[field.name] = item
        else:
            _fail(f"{path}.{field.name}", type(item).__name__)
    return result


def _raw_executable(materialized: object) -> object:
    handle = getattr(materialized, "_handle", None)
    if handle is None or handle.__class__.__name__ != "_MaterializedBridge":
        _fail("materialized._handle", type(handle).__name__)
    raw = getattr(handle, "_materialized", None)
    if raw is None:
        _fail("materialized._handle._materialized", "missing")
    executable = getattr(raw, "executable", None)
    if executable is None:
        backend = getattr(raw, "_backend", None)
        if not isinstance(backend, dict) or "executable" not in backend:
            _fail("materialized.raw", "known executable carrier required")
        executable = backend["executable"]
    observed = getattr(executable, "executable_sha256", None)
    identity = getattr(materialized, "identity", None)
    expected = getattr(identity, "executable_sha256", None)
    if observed != expected:
        _fail(
            "materialized.executable_identity",
            {"expected": expected, "observed": observed},
        )
    return executable


def _sbt_buffer_bindings(plan: object) -> dict[str, object]:
    plan_document = _to_dict(plan, "route.plan")
    shape = plan_document.get("family_shape")
    if not isinstance(shape, dict):
        _fail("route.plan.family_shape", type(shape).__name__)
    graph_nodes = shape.get("graph_nodes")
    if not isinstance(graph_nodes, list) or len(graph_nodes) != 1:
        _fail("route.plan.family_shape.graph_nodes", graph_nodes)
    primitive_kind = graph_nodes[0].get("primitive_kind")
    physical = shape.get("physical")
    if not isinstance(physical, dict) or not isinstance(physical.get("sbt"), dict):
        _fail("route.plan.family_shape.physical.sbt", physical)
    sbt = physical["sbt"]
    buffers = shape.get("buffers")
    if not isinstance(buffers, list) or not buffers:
        _fail("route.plan.family_shape.buffers", buffers)
    return {
        "schema": "rtdl.v4.target_sbt_buffer_bindings.v1",
        "primitive_kind": primitive_kind,
        "record_stride": sbt.get("record_stride"),
        "record_count_relation": sbt.get("record_count_relation"),
        "buffers": [
            {
                "ordinal": row.get("ordinal"),
                "semantic": row.get("semantic"),
                "value_type": row.get("value_type"),
            }
            for row in buffers
            if isinstance(row, dict)
        ],
    }


def _target_binding(target: object, toolchain: object) -> dict[str, object]:
    profile = getattr(target, "profile", None)
    target_sha256 = getattr(profile, "target_sha256", None)
    native_sha256 = getattr(profile, "native_sha256", None)
    native_path = Path(getattr(target, "native_library_path", "")).resolve()
    if not native_path.is_file() or _sha_file(native_path) != native_sha256:
        _fail("target.native_library", "path/profile identity mismatch")
    if not isinstance(target_sha256, str):
        _fail("target.profile.target_sha256", target_sha256)
    return {
        "schema": "rtdl.v4.target_binding.v1",
        "target_sha256": target_sha256,
        "native_library_path": str(native_path),
        "native_library_sha256": native_sha256,
        "target_profile": _dataclass_scalars(profile, "target.profile"),
        "toolchain": _dataclass_scalars(toolchain, "toolchain"),
    }


def _execution_receipt(
    *,
    route_id: str,
    mode: str,
    plan_sha256: str,
    identity: Mapping[str, object],
    result: object,
    target_binding: Mapping[str, object],
    control_flow_manifest_sha256: str,
) -> dict[str, object]:
    traversal = getattr(result, "traversal_receipt", None)
    if not isinstance(traversal, Mapping):
        _fail("result.traversal_receipt", type(traversal).__name__)
    traversal = _canonical_copy(dict(traversal), "result.traversal_receipt")
    assert isinstance(traversal, dict)
    if traversal.get("physical_executor_classification") != "optix_traversal_observed":
        _fail("result.traversal_receipt", "true OptiX traversal required")
    native_sha256 = target_binding["native_library_sha256"]
    if traversal.get("provider_library_sha256") != native_sha256:
        _fail("result.traversal_receipt", "native provider identity mismatch")
    output_sha256 = getattr(result, "output_sha256", None)
    if traversal.get("output_digest") != output_sha256:
        _fail("result.output_sha256", "traversal output identity mismatch")
    return {
        "schema": "rtdl.v4.goal5840_execution_receipt.v1",
        "route_id": route_id,
        "mode": mode,
        "plan_sha256": plan_sha256,
        "executable_identity_sha256": identity["identity_sha256"],
        "target_sha256": target_binding["target_sha256"],
        "native_library_sha256": native_sha256,
        "output_sha256": output_sha256,
        "status": "OK",
        "status_code": 0,
        "status_before_output": True,
        "complete": True,
        "partial_result_exposed": False,
        "control_flow_manifest_sha256": control_flow_manifest_sha256,
        "traversal_receipt": traversal,
    }


def capture_real_target_evidence_bundle(
    *,
    route_id: str,
    mode: str,
    route: object,
    program: object,
    materialized: object,
    result: object,
    target: object,
    toolchain: object,
    declaration_authority_sha256: str,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Capture one successful true-OptiX execution through the public route."""

    if route_id not in _BUILD_INPUT_NAME_BY_ROUTE:
        _fail("route_id", route_id)
    plan = getattr(route, "plan", None)
    artifacts = getattr(route, "artifacts", None)
    provider = getattr(route, "provider", None)
    if getattr(program, "plan", None) != plan \
            or getattr(program, "artifacts", None) != artifacts:
        _fail("program", "route/program plan or artifact mismatch")
    materialized_program = getattr(materialized, "_program", None)
    if materialized_program is not program:
        _fail("materialized._program", "program identity mismatch")
    projection = getattr(program, "provider_projection", None)
    identity_object = getattr(materialized, "identity", None)
    identity = _to_dict(identity_object, "materialized.identity")
    if getattr(result, "executable_identity_sha256", None) != identity.get(
        "identity_sha256"
    ) or getattr(result, "provider_projection_sha256", None) != getattr(
        projection, "projection_sha256", None
    ):
        _fail("result", "generic lifecycle identity mismatch")
    target_binding = _target_binding(target, toolchain)
    if identity.get("target_sha256") != target_binding["target_sha256"] \
            or identity.get("provider_artifact_sha256") != target_binding[
                "native_library_sha256"
            ]:
        _fail("materialized.identity", "target/native binding mismatch")
    control_flow = capture_target_control_flow_evidence(
        route_id, repository_root=repository_root
    )
    execution_receipt = _execution_receipt(
        route_id=route_id,
        mode=mode,
        plan_sha256=getattr(plan, "plan_sha256", ""),
        identity=identity,
        result=result,
        target_binding=target_binding,
        control_flow_manifest_sha256=str(control_flow["manifest_sha256"]),
    )
    traversal = execution_receipt["traversal_receipt"]
    assert isinstance(traversal, dict)
    physical_receipt = traversal.get("physical_receipt")
    native_descriptor: dict[str, object] = {
        "schema": "rtdl.v4.target_native_producer_descriptor.v1",
        "evidence_kind": "trusted_source_chain_plus_executed_native_identity",
        "build_input_type_name": _BUILD_INPUT_NAME_BY_ROUTE[route_id],
        "native_library_sha256": target_binding["native_library_sha256"],
        "control_flow_manifest_sha256": control_flow["manifest_sha256"],
    }
    if isinstance(physical_receipt, dict):
        native_descriptor["runtime_physical_receipt"] = physical_receipt
    declaration = build_family_target_declaration(route_id, plan)
    executable = _raw_executable(materialized)
    return build_target_evidence_bundle(
        route_id=route_id,
        declaration=declaration,
        declaration_authority_sha256=declaration_authority_sha256,
        program_artifacts=capture_family_program_artifacts(artifacts),
        generated_target_artifacts=capture_generated_target_artifacts(executable),
        provider_descriptor=_to_dict(provider.descriptor, "provider.descriptor"),
        provider_projection=_to_dict(projection, "program.provider_projection"),
        executable_identity=identity,
        target_binding=target_binding,
        native_producer_descriptor=native_descriptor,
        sbt_buffer_bindings=_sbt_buffer_bindings(plan),
        target_control_flow_evidence=control_flow,
        execution_receipt=execution_receipt,
    )


__all__ = [
    "TargetEvidenceCaptureError",
    "capture_real_target_evidence_bundle",
]
