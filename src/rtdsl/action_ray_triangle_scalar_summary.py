"""Compiler-owned Action lowering for generic ray/triangle scalar summaries.

This module deliberately does not know any paper/application identity.  An
application first selects its semantic algorithm.  That algorithm binds one
of two generic producer contracts:

* one logical value per ray is its all-hit count; or
* one logical value per ray is its weight when any hit exists.

Both contracts feed the same verified scalar-sum Action.  There is no
cross-producer selection and no application-selected backend/template escape.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import secrets
from typing import Iterable, Mapping, Sequence

from .action_api import (
    ActionTargetProfile,
    CompiledAction,
    _detect_action_target_profile_for_required_backends,
    _detect_action_target_profile_for_required_backends_fork_clean,
)
from .action_ir import (
    ActionScalarKind,
    DeliveryEnforcement,
    PhysicalDelivery,
    ReductionOperator,
)
from .generic_primitives import run_generic_ray_triangle_any_hit
from .optix_runtime import (
    prepare_optix_static_triangle_scene_3d,
    prepare_optix_static_triangle_scene_3d_device_triangles,
)
from .reference import ray_triangle_hit_count_cpu


class RayTriangleScalarSummaryError(ValueError):
    pass


class RayTriangleScalarProducerKind(str, Enum):
    RAY_ANY_HIT_WEIGHTED_VALUE_3D = "ray_any_hit_weighted_value_3d.v1"
    RAY_ALL_HIT_COUNT_VALUE_3D = "ray_all_hit_count_value_3d.v1"


_TEMPLATE_BY_PRODUCER = {
    RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D: (
        "prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d"
    ),
    RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D: (
        "prepared_optix_triangle_scene_ray_hit_count_sum_3d"
    ),
}

_DIRECT_PROVIDER_BY_PRODUCER = {
    RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D: (
        "canonical_standalone/ray_triangle_any_hit_weighted_value_3d/optix/"
        "prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d"
    ),
    RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D: (
        "canonical_standalone/ray_triangle_all_hit_count_value_3d/optix/"
        "prepared_optix_triangle_scene_ray_hit_count_sum_3d"
    ),
}

_PREPARED_PROGRAM_SECRET = secrets.token_bytes(32)


def _stable_digest(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_scalar_sum_action(compiled: CompiledAction) -> None:
    if not isinstance(compiled, CompiledAction):
        raise RayTriangleScalarSummaryError("COMPILED_ACTION_REQUIRED")
    spec = compiled.spec
    fields = {field.name: field.value_type for field in spec.event_type.fields}
    if set(fields) != {"ray_id", "value"}:
        raise RayTriangleScalarSummaryError("RAY_VALUE_EVENT_SCHEMA_REQUIRED")
    if fields["ray_id"].kind is not ActionScalarKind.U64:
        raise RayTriangleScalarSummaryError("RAY_ID_U64_REQUIRED")
    if fields["value"].kind is not ActionScalarKind.U64:
        raise RayTriangleScalarSummaryError("VALUE_U64_REQUIRED")
    if (
        spec.logical_event.key_fields != ("ray_id",)
        or spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        raise RayTriangleScalarSummaryError("PROVEN_SINGLE_RAY_EVENT_REQUIRED")
    if spec.states or spec.emits or spec.termination_proofs:
        raise RayTriangleScalarSummaryError("PURE_SCALAR_REDUCTION_REQUIRED")
    if len(spec.reductions) != 1:
        raise RayTriangleScalarSummaryError("ONE_REDUCTION_REQUIRED")
    reduction = spec.reductions[0]
    if (
        reduction.key_fields
        or reduction.operator is not ReductionOperator.SUM
        or reduction.value_type.kind is not ActionScalarKind.U64
        or reduction.identity.to_python() != 0
    ):
        raise RayTriangleScalarSummaryError("UNKEYED_U64_SUM_REQUIRED")


def _action_sum(compiled: CompiledAction, values: Sequence[int]) -> int:
    events = tuple(
        {"ray_id": index, "value": int(value)}
        for index, value in enumerate(values)
    )
    result = compiled.execute_reference(events, {})
    rows = result.reductions[0].rows
    if len(rows) != 1 or rows[0][0] != ():
        raise RayTriangleScalarSummaryError("SCALAR_REDUCTION_RESULT_REQUIRED")
    return int(rows[0][1])


def _column_count(columns: Mapping[str, object], *, label: str) -> int:
    if not columns:
        raise RayTriangleScalarSummaryError(f"{label}_DEVICE_COLUMNS_REQUIRED")
    counts = set()
    for value in columns.values():
        size = getattr(value, "size", None)
        counts.add(int(size) if size is not None else len(value))
    if len(counts) != 1:
        raise RayTriangleScalarSummaryError(f"{label}_DEVICE_COLUMN_LENGTH_MISMATCH")
    return counts.pop()


@dataclass(frozen=True)
class CompiledRayTriangleScalarSummary:
    compiled: CompiledAction
    producer_kind: RayTriangleScalarProducerKind
    backend: str
    template: str
    target_profile: ActionTargetProfile
    canonical_resolution: Mapping[str, object] | None = None
    canonical_production_authority: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        _validate_scalar_sum_action(self.compiled)
        expected = _TEMPLATE_BY_PRODUCER[self.producer_kind]
        if self.backend == "optix":
            if self.template != expected or not self.target_profile.optix_available:
                raise RayTriangleScalarSummaryError("OPTIX_TEMPLATE_BINDING_INVALID")
        elif self.backend == "cpu_reference":
            if self.template != "cpu_reference_interpreter":
                raise RayTriangleScalarSummaryError("CPU_TEMPLATE_BINDING_INVALID")
        else:
            raise RayTriangleScalarSummaryError("UNSUPPORTED_COMPILER_BACKEND")
        if (self.canonical_resolution is None) != (
            self.canonical_production_authority is None
        ):
            raise RayTriangleScalarSummaryError(
                "CANONICAL_RESOLUTION_AND_AUTHORITY_REQUIRED_TOGETHER"
            )

    def to_metadata(self) -> dict[str, object]:
        payload = {
            "contract": "rtdl.v3.ray_triangle_scalar_summary_plan.v1",
            "action_semantic_digest": self.compiled.spec.semantic_digest,
            "action_source_digest": self.compiled.source_digest,
            "producer_kind": self.producer_kind.value,
            "backend": self.backend,
            "template": self.template,
            "target_profile": self.target_profile.to_metadata(),
            "application_selected_backend": False,
            "application_selected_template": False,
            "cross_producer_or_algorithm_selection_performed": False,
            "canonical_resolution": (
                None
                if self.canonical_resolution is None
                else dict(self.canonical_resolution)
            ),
            "canonical_production_authority": (
                None
                if self.canonical_production_authority is None
                else dict(self.canonical_production_authority)
            ),
            "selection_rule": (
                "selected algorithm binds one generic producer contract; "
                "compiler selects the sole legal provider template for that contract"
            ),
        }
        payload["plan_sha256"] = _stable_digest(payload)
        return payload

    def execute(
        self,
        *,
        triangles,
        rays,
        ray_weights: Sequence[int] | None = None,
    ) -> dict[str, object]:
        (
            scalar,
            ray_count,
            primitive_count,
            ray_columns,
            native,
        ) = self._execute_scalar_core(
            triangles=triangles,
            rays=rays,
            ray_weights=ray_weights,
        )
        return {
            "scalar_sum": scalar,
            "ray_count": ray_count,
            "primitive_count": primitive_count,
            "device_column_execution": ray_columns,
            "plan": self.to_metadata(),
            "native_summary": native,
        }

    def _execute_scalar_core(
        self,
        *,
        triangles,
        rays,
        ray_weights: Sequence[int] | None = None,
    ) -> tuple[int, int, int, bool, Mapping[str, object] | None]:
        """Execute one segment without materializing discarded plan metadata.

        ``execute_segments`` previously called :meth:`execute`, which rebuilt
        the complete canonical-plan metadata for every segment and immediately
        discarded it.  This internal core preserves every legality check and
        the exact native route while letting the segmented front door emit the
        plan once, at its actual output boundary.
        """

        triangle_columns = isinstance(triangles, Mapping)
        ray_columns = isinstance(rays, Mapping)
        if triangle_columns != ray_columns:
            raise RayTriangleScalarSummaryError("MATCHED_HOST_OR_DEVICE_GEOMETRY_REQUIRED")
        if ray_columns:
            if self.backend != "optix":
                raise RayTriangleScalarSummaryError("DEVICE_COLUMNS_REQUIRE_OPTIX")
            ray_count = _column_count(rays, label="RAY")
            primitive_count = _column_count(triangles, label="TRIANGLE")
        else:
            ray_count = len(rays)
            primitive_count = len(triangles)
        if self.producer_kind is RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D:
            if ray_weights is None or len(ray_weights) != ray_count:
                raise RayTriangleScalarSummaryError("ONE_WEIGHT_PER_RAY_REQUIRED")
            if ray_columns:
                with prepare_optix_static_triangle_scene_3d_device_triangles(triangles) as scene:
                    native = scene.ray_any_hit_weighted_sum_device_columns(rays, ray_weights)
                scalar = int(native["weighted_hit_sum"])
            else:
                weights = tuple(int(value) for value in ray_weights)
                if any(value < 0 or value >= 1 << 64 for value in weights):
                    raise RayTriangleScalarSummaryError("RAY_WEIGHT_U64_REQUIRED")
            if self.backend == "optix" and not ray_columns:
                with prepare_optix_static_triangle_scene_3d(triangles) as scene:
                    native = scene.ray_any_hit_weighted_sum(rays, weights)
                scalar = int(native["weighted_hit_sum"])
            elif self.backend != "optix":
                rows = run_generic_ray_triangle_any_hit(rays, triangles, backend="cpu")
                values = tuple(
                    weights[int(row["ray_id"])] if int(row["any_hit"]) else 0
                    for row in rows
                )
                scalar = _action_sum(self.compiled, values)
                native = None
        else:
            if ray_weights is not None:
                raise RayTriangleScalarSummaryError("HIT_COUNT_PRODUCER_REJECTS_RAY_WEIGHTS")
            if ray_columns:
                with prepare_optix_static_triangle_scene_3d_device_triangles(triangles) as scene:
                    native = scene.ray_hit_count_sum_device_columns(rays)
                scalar = int(native["hit_count_sum"])
            elif self.backend == "optix":
                with prepare_optix_static_triangle_scene_3d(triangles) as scene:
                    native = scene.ray_hit_count_sum(rays)
                scalar = int(native["hit_count_sum"])
            else:
                rows = ray_triangle_hit_count_cpu(rays, triangles)
                values = tuple(int(row["hit_count"]) for row in rows)
                scalar = _action_sum(self.compiled, values)
                native = None
        return scalar, ray_count, primitive_count, ray_columns, native

    def execute_segments(
        self,
        segments: Iterable[Mapping[str, object]],
    ) -> dict[str, object]:
        """Execute an app-neutral partition of one scalar reduction.

        The caller owns the semantic partition.  This method neither chooses
        an algorithm nor changes a producer kind: it only applies the already
        compiled associative U64 sum to consecutive, nonempty physical
        segments.  Every segment therefore traverses through the same
        compiler-selected provider as :meth:`execute`.
        """

        scalar_sum = 0
        ray_count = 0
        primitive_count = 0
        segment_rows: list[dict[str, object]] = []
        for expected_segment_id, segment in enumerate(segments):
            if not isinstance(segment, Mapping):
                raise RayTriangleScalarSummaryError("SEGMENT_MAPPING_REQUIRED")
            segment_id = segment.get("segment_id")
            if segment_id != expected_segment_id:
                raise RayTriangleScalarSummaryError("CONTIGUOUS_SEGMENT_IDS_REQUIRED")
            if set(segment) - {
                "segment_id",
                "triangles",
                "rays",
                "ray_weights",
                "partition",
                "relation_count",
                "host_geometry_bytes",
            }:
                raise RayTriangleScalarSummaryError("UNKNOWN_SEGMENT_FIELD")
            if "triangles" not in segment or "rays" not in segment:
                raise RayTriangleScalarSummaryError("SEGMENT_GEOMETRY_REQUIRED")
            (
                value,
                segment_ray_count,
                segment_primitive_count,
                device_column_execution,
                native,
            ) = self._execute_scalar_core(
                triangles=segment["triangles"],
                rays=segment["rays"],
                ray_weights=segment.get("ray_weights"),
            )
            if value < 0 or scalar_sum > ((1 << 64) - 1) - value:
                raise RayTriangleScalarSummaryError("SEGMENTED_U64_SUM_OVERFLOW")
            scalar_sum += value
            ray_count += segment_ray_count
            primitive_count += segment_primitive_count
            if device_column_execution is not True:
                raise RayTriangleScalarSummaryError(
                    "SEGMENTED_EXECUTION_REQUIRES_DEVICE_COLUMNS"
                )
            segment_rows.append(
                {
                    "segment_id": expected_segment_id,
                    "scalar_sum": value,
                    "ray_count": segment_ray_count,
                    "primitive_count": segment_primitive_count,
                    "relation_count": int(segment.get("relation_count", 0)),
                    "host_geometry_bytes": int(segment.get("host_geometry_bytes", 0)),
                    "partition": segment.get("partition"),
                    "native_summary_sha256": (
                        None if native is None else _stable_digest(native)
                    ),
                }
            )
        if not segment_rows:
            raise RayTriangleScalarSummaryError("AT_LEAST_ONE_PHYSICAL_SEGMENT_REQUIRED")
        return {
            "scalar_sum": scalar_sum,
            "ray_count": ray_count,
            "primitive_count": primitive_count,
            "device_column_execution": True,
            "segmented_execution": True,
            "segment_count": len(segment_rows),
            "segments": segment_rows,
            "plan": self.to_metadata(),
        }


def _prepared_program_payload(
    compiled: CompiledAction,
    target_profile: ActionTargetProfile,
    plans: Sequence[CompiledRayTriangleScalarSummary],
) -> dict[str, object]:
    return {
        "contract": "rtdl.compiler_prepared_ray_triangle_scalar_summary_program.v1",
        "action_semantic_digest": compiled.spec.semantic_digest,
        "action_source_digest": compiled.source_digest,
        "target_profile": target_profile.to_metadata(),
        "plans": [
            plan.to_metadata()
            for plan in sorted(plans, key=lambda row: row.producer_kind.value)
        ],
        "compiler_owned": True,
        "application_selected_backend": False,
        "application_selected_template": False,
        "cross_producer_selection_performed": False,
        "device_handle_or_context_captured": False,
        "cross_process_serialization_allowed": False,
    }


def _prepared_program_seal(payload: Mapping[str, object]) -> str:
    return hmac.new(
        _PREPARED_PROGRAM_SECRET,
        json.dumps(
            dict(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii"),
        hashlib.sha256,
    ).hexdigest()


@dataclass(frozen=True)
class CompilerPreparedRayTriangleScalarSummaryProgram:
    """Opaque compiler program prepared before repeated endpoint execution.

    The object contains immutable IR, target facts and canonical provider
    authority only.  It deliberately contains no CUDA/OptiX handle and may
    cross a trusted POSIX fork, but it cannot be serialized or reconstructed by
    an application.  Every lookup revalidates the process-private seal.
    """

    compiled: CompiledAction
    target_profile: ActionTargetProfile
    plans: tuple[CompiledRayTriangleScalarSummary, ...]
    _compiler_seal: str

    def __post_init__(self) -> None:
        self._require_live()

    def __reduce__(self):
        raise TypeError("compiler-prepared programs are process-local and non-serializable")

    def _require_live(self) -> None:
        if not isinstance(self.compiled, CompiledAction):
            raise RayTriangleScalarSummaryError("PREPARED_COMPILED_ACTION_REQUIRED")
        _validate_scalar_sum_action(self.compiled)
        if not isinstance(self.target_profile, ActionTargetProfile):
            raise RayTriangleScalarSummaryError("PREPARED_TARGET_PROFILE_REQUIRED")
        if (
            self.target_profile.profile_source
            not in {
                "runtime_capability_probe",
                "fork_clean_runtime_capability_probe",
            }
            or self.target_profile.production_selection_policy
            != "compiler_owned_default"
        ):
            raise RayTriangleScalarSummaryError(
                "COMPILER_OWNED_RUNTIME_TARGET_PROFILE_REQUIRED"
            )
        if not self.plans:
            raise RayTriangleScalarSummaryError("AT_LEAST_ONE_PREPARED_PLAN_REQUIRED")
        producer_kinds: set[RayTriangleScalarProducerKind] = set()
        for plan in self.plans:
            if not isinstance(plan, CompiledRayTriangleScalarSummary):
                raise RayTriangleScalarSummaryError("PREPARED_PLAN_TYPE_INVALID")
            if plan.compiled is not self.compiled:
                raise RayTriangleScalarSummaryError("PREPARED_ACTION_OBJECT_BINDING_INVALID")
            if plan.target_profile != self.target_profile:
                raise RayTriangleScalarSummaryError("PREPARED_TARGET_BINDING_INVALID")
            if plan.producer_kind in producer_kinds:
                raise RayTriangleScalarSummaryError("DUPLICATE_PREPARED_PRODUCER")
            producer_kinds.add(plan.producer_kind)
            if (
                plan.backend != "optix"
                or plan.canonical_resolution is None
                or plan.canonical_production_authority is None
            ):
                raise RayTriangleScalarSummaryError(
                    "PREPARED_CANONICAL_OPTIX_AUTHORITY_REQUIRED"
                )
        expected = _prepared_program_seal(
            _prepared_program_payload(self.compiled, self.target_profile, self.plans)
        )
        if not isinstance(self._compiler_seal, str) or not hmac.compare_digest(
            self._compiler_seal, expected
        ):
            raise RayTriangleScalarSummaryError("PREPARED_PROGRAM_SEAL_INVALID")

    def require_plan(
        self,
        *,
        producer_kind: RayTriangleScalarProducerKind,
        expected_action_source_digest: str,
    ) -> CompiledRayTriangleScalarSummary:
        self._require_live()
        if not isinstance(producer_kind, RayTriangleScalarProducerKind):
            raise RayTriangleScalarSummaryError("PRODUCER_KIND_REQUIRED")
        if (
            not isinstance(expected_action_source_digest, str)
            or len(expected_action_source_digest) != 64
            or self.compiled.source_digest != expected_action_source_digest
        ):
            raise RayTriangleScalarSummaryError("PREPARED_ACTION_SOURCE_MISMATCH")
        matches = tuple(
            plan for plan in self.plans if plan.producer_kind is producer_kind
        )
        if len(matches) != 1:
            raise RayTriangleScalarSummaryError("PREPARED_PRODUCER_PLAN_MISSING")
        return matches[0]

    def to_metadata(self) -> dict[str, object]:
        self._require_live()
        payload = _prepared_program_payload(
            self.compiled, self.target_profile, self.plans
        )
        payload["prepared_program_sha256"] = _stable_digest(payload)
        return payload

    def issue_fork_execution_ticket(
        self,
    ) -> "PreparedRayTriangleScalarSummaryForkTicket":
        """Validate once and issue a one-use-per-fork execution capability."""

        self._require_live()
        fingerprints = tuple(
            _prepared_plan_fingerprint(plan)
            for plan in sorted(self.plans, key=lambda row: row.producer_kind.value)
        )
        payload = {
            "contract": "rtdl.prepared_ray_triangle_scalar_summary_fork_ticket.v1",
            "program_object_id": id(self),
            "program_seal": self._compiler_seal,
            "action_source_digest": self.compiled.source_digest,
            "plan_fingerprints": fingerprints,
        }
        return PreparedRayTriangleScalarSummaryForkTicket(
            _program=self,
            _plan_fingerprints=fingerprints,
            _ticket_seal=_prepared_program_seal(payload),
        )


def _prepared_plan_fingerprint(
    plan: CompiledRayTriangleScalarSummary,
) -> dict[str, object]:
    resolution = plan.canonical_resolution
    authority = plan.canonical_production_authority
    return {
        "plan_object_id": id(plan),
        "compiled_object_id": id(plan.compiled),
        "target_object_id": id(plan.target_profile),
        "action_semantic_digest": plan.compiled.spec.semantic_digest,
        "action_source_digest": plan.compiled.source_digest,
        "producer_kind": plan.producer_kind.value,
        "backend": plan.backend,
        "template": plan.template,
        "target_profile": plan.target_profile.to_metadata(),
        "canonical_resolution_object_id": id(resolution),
        "canonical_resolution_sha256": (
            None if resolution is None else _stable_digest(dict(resolution))
        ),
        "canonical_resolution_receipt_sha256": (
            None if resolution is None else resolution.get("receipt_sha256")
        ),
        "canonical_authority_object_id": id(authority),
        "canonical_authority_sha256": (
            None if authority is None else _stable_digest(dict(authority))
        ),
        "canonical_authority_receipt_sha256": (
            None if authority is None else authority.get("authority_receipt_sha256")
        ),
    }


@dataclass(frozen=True)
class PreparedRayTriangleScalarSummaryForkTicket:
    """Single-use capability copied by POSIX fork, never serialized."""

    _program: CompilerPreparedRayTriangleScalarSummaryProgram
    _plan_fingerprints: tuple[dict[str, object], ...]
    _ticket_seal: str
    _consumed: bool = False

    def __reduce__(self):
        raise TypeError("prepared execution tickets are fork-local and non-serializable")

    def require_plan(
        self,
        *,
        producer_kind: RayTriangleScalarProducerKind,
        expected_action_source_digest: str,
    ) -> CompiledRayTriangleScalarSummary:
        if self._consumed:
            raise RayTriangleScalarSummaryError("PREPARED_FORK_TICKET_ALREADY_CONSUMED")
        if not isinstance(self._program, CompilerPreparedRayTriangleScalarSummaryProgram):
            raise RayTriangleScalarSummaryError("PREPARED_FORK_TICKET_PROGRAM_INVALID")
        current = tuple(
            _prepared_plan_fingerprint(plan)
            for plan in sorted(
                self._program.plans, key=lambda row: row.producer_kind.value
            )
        )
        payload = {
            "contract": "rtdl.prepared_ray_triangle_scalar_summary_fork_ticket.v1",
            "program_object_id": id(self._program),
            "program_seal": self._program._compiler_seal,
            "action_source_digest": self._program.compiled.source_digest,
            "plan_fingerprints": current,
        }
        if (
            current != self._plan_fingerprints
            or not isinstance(self._ticket_seal, str)
            or not hmac.compare_digest(
                self._ticket_seal, _prepared_program_seal(payload)
            )
        ):
            raise RayTriangleScalarSummaryError("PREPARED_FORK_TICKET_SEAL_INVALID")
        if self._program.compiled.source_digest != expected_action_source_digest:
            raise RayTriangleScalarSummaryError("PREPARED_ACTION_SOURCE_MISMATCH")
        matches = tuple(
            plan
            for plan in self._program.plans
            if plan.producer_kind is producer_kind
        )
        if len(matches) != 1:
            raise RayTriangleScalarSummaryError("PREPARED_PRODUCER_PLAN_MISSING")
        object.__setattr__(self, "_consumed", True)
        return matches[0]


def compile_ray_triangle_scalar_summary(
    compiled: CompiledAction,
    *,
    producer_kind: RayTriangleScalarProducerKind,
    target_profile: ActionTargetProfile,
    require_optix: bool,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> CompiledRayTriangleScalarSummary:
    """Compile one already-selected producer contract; never choose an algorithm."""

    _validate_scalar_sum_action(compiled)
    if not isinstance(producer_kind, RayTriangleScalarProducerKind):
        raise RayTriangleScalarSummaryError("PRODUCER_KIND_REQUIRED")
    if not isinstance(target_profile, ActionTargetProfile):
        raise RayTriangleScalarSummaryError("TARGET_PROFILE_REQUIRED")
    if (semantic_statement_stable_id is None) != (backend_contract_id is None):
        raise RayTriangleScalarSummaryError(
            "CANONICAL_SEMANTIC_STATEMENT_AND_BACKEND_REQUIRED_TOGETHER"
        )
    if target_profile.optix_available:
        canonical_resolution = None
        canonical_authority = None
        if semantic_statement_stable_id is not None:
            from .canonical_physical_resolution import (
                bind_canonical_provider_to_direct_provider,
                resolve_canonical_standalone_provider_for_contract,
            )

            memory_limit = target_profile.device_memory_limit_bytes
            if memory_limit is None:
                raise RayTriangleScalarSummaryError(
                    "CANONICAL_PRODUCTION_TARGET_REQUIRES_DEVICE_MEMORY_LIMIT"
                )
            execution_contract = {
                "contract": "rtdl.ray_triangle_scalar_summary.direct_execution.v1",
                "action_semantic_digest": compiled.spec.semantic_digest,
                "action_source_digest": compiled.source_digest,
                "producer_kind": producer_kind.value,
                "backend": "optix",
                "template": _TEMPLATE_BY_PRODUCER[producer_kind],
                "target_profile": target_profile.to_metadata(),
            }
            execution_contract_sha256 = _stable_digest(execution_contract)
            canonical_resolution = resolve_canonical_standalone_provider_for_contract(
                statement_stable_id=semantic_statement_stable_id,
                backend_contract_id=backend_contract_id,
                action_identity={
                    "action_semantic_digest": compiled.spec.semantic_digest,
                    "action_source_digest": compiled.source_digest,
                    "producer_kind": producer_kind.value,
                },
                output_contract={
                    "kind": "exact_unkeyed_u64_scalar_sum",
                    "output_bytes": 8,
                },
                work_domain={
                    "producer_kind": producer_kind.value,
                    "dynamic_geometry_owned_by_direct_provider": True,
                },
                input_bytes=0,
                output_bytes=8,
                prepared_bytes=0,
                logical_cardinality_bound=1,
                pair_cardinality_bound=0,
                logical_item_bytes_bound=8,
                pair_item_bytes_bound=0,
                target_identity={
                    "kind": "runtime_probed_ray_triangle_scalar_summary_target",
                    "target_profile": target_profile.to_metadata(),
                    "mandatory_nvidia_rt": True,
                },
                available_providers=("optix",),
                memory_limit_bytes=memory_limit,
            )
            canonical_authority = bind_canonical_provider_to_direct_provider(
                canonical_resolution,
                direct_provider_stable_id=_DIRECT_PROVIDER_BY_PRODUCER[producer_kind],
                direct_execution_contract_sha256=execution_contract_sha256,
            )
        return CompiledRayTriangleScalarSummary(
            compiled=compiled,
            producer_kind=producer_kind,
            backend="optix",
            template=_TEMPLATE_BY_PRODUCER[producer_kind],
            target_profile=target_profile,
            canonical_resolution=canonical_resolution,
            canonical_production_authority=canonical_authority,
        )
    if semantic_statement_stable_id is not None:
        raise RayTriangleScalarSummaryError(
            "CANONICAL_OPTIX_BACKEND_UNAVAILABLE"
        )
    if require_optix:
        raise RayTriangleScalarSummaryError("TRUE_OPTIX_TARGET_REQUIRED")
    if not target_profile.cpu_reference_available:
        raise RayTriangleScalarSummaryError("NO_LEGAL_PROVIDER")
    return CompiledRayTriangleScalarSummary(
        compiled=compiled,
        producer_kind=producer_kind,
        backend="cpu_reference",
        template="cpu_reference_interpreter",
        target_profile=target_profile,
    )


def prepare_ray_triangle_scalar_summary_program(
    compiled: CompiledAction,
    *,
    producer_contracts: Sequence[
        tuple[RayTriangleScalarProducerKind, str, str]
    ],
    target_profile: ActionTargetProfile,
) -> CompilerPreparedRayTriangleScalarSummaryProgram:
    """Prepare immutable canonical plans for already-selected producers.

    This is a compiler lifecycle operation, not a physical-plan optimizer.  A
    caller supplies semantic producer contracts, never backend/template names;
    each contract must resolve to its unique canonical OptiX provider.  The
    resulting process-local program contains no device handle and may be
    inherited by a trusted fork.
    """

    _validate_scalar_sum_action(compiled)
    if not isinstance(target_profile, ActionTargetProfile):
        raise RayTriangleScalarSummaryError("PREPARED_TARGET_PROFILE_REQUIRED")
    if (
        target_profile.profile_source
        not in {
            "runtime_capability_probe",
            "fork_clean_runtime_capability_probe",
        }
        or target_profile.production_selection_policy != "compiler_owned_default"
        or not target_profile.optix_available
    ):
        raise RayTriangleScalarSummaryError(
            "COMPILER_OWNED_OPTIX_TARGET_PROFILE_REQUIRED"
        )
    contracts = tuple(producer_contracts)
    if not contracts:
        raise RayTriangleScalarSummaryError("AT_LEAST_ONE_PRODUCER_CONTRACT_REQUIRED")
    if len({row[0] for row in contracts}) != len(contracts):
        raise RayTriangleScalarSummaryError("DUPLICATE_PREPARED_PRODUCER")
    plans: list[CompiledRayTriangleScalarSummary] = []
    for producer_kind, statement_id, backend_contract_id in contracts:
        if not isinstance(producer_kind, RayTriangleScalarProducerKind):
            raise RayTriangleScalarSummaryError("PRODUCER_KIND_REQUIRED")
        if not isinstance(statement_id, str) or not statement_id:
            raise RayTriangleScalarSummaryError("SEMANTIC_STATEMENT_ID_REQUIRED")
        if not isinstance(backend_contract_id, str) or not backend_contract_id:
            raise RayTriangleScalarSummaryError("BACKEND_CONTRACT_ID_REQUIRED")
        plans.append(
            compile_ray_triangle_scalar_summary(
                compiled,
                producer_kind=producer_kind,
                target_profile=target_profile,
                require_optix=True,
                semantic_statement_stable_id=statement_id,
                backend_contract_id=backend_contract_id,
            )
        )
    plans_tuple = tuple(plans)
    payload = _prepared_program_payload(compiled, target_profile, plans_tuple)
    return CompilerPreparedRayTriangleScalarSummaryProgram(
        compiled=compiled,
        target_profile=target_profile,
        plans=plans_tuple,
        _compiler_seal=_prepared_program_seal(payload),
    )


def detect_ray_triangle_scalar_summary_target(
    *, fork_clean: bool = False
) -> ActionTargetProfile:
    """Compiler-owned capability probe for this generic producer family."""

    if not isinstance(fork_clean, bool):
        raise TypeError("fork_clean must be bool")
    detector = (
        _detect_action_target_profile_for_required_backends_fork_clean
        if fork_clean
        else _detect_action_target_profile_for_required_backends
    )
    return detector(
        required_backends=("optix",),
        cpu_reference_available=True,
    )


__all__ = [
    "CompiledRayTriangleScalarSummary",
    "CompilerPreparedRayTriangleScalarSummaryProgram",
    "PreparedRayTriangleScalarSummaryForkTicket",
    "RayTriangleScalarProducerKind",
    "RayTriangleScalarSummaryError",
    "compile_ray_triangle_scalar_summary",
    "detect_ray_triangle_scalar_summary_target",
    "prepare_ray_triangle_scalar_summary_program",
]
