from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import hmac
import math
import secrets
import struct
import time
from typing import Mapping, Sequence


_PREPARED_ACTION_KEYED_I64_CONSUMED_OWNER_SECRET = secrets.token_bytes(32)
_PREPARED_ACTION_KEYED_I64_BACKEND_OWNER_SECRET = secrets.token_bytes(32)
_ALL_INCLUDED_PRIMITIVE_MASK_SECRET = secrets.token_bytes(32)

from .action_ir import (
    ActionEffect,
    ActionOp,
    ActionScalarType,
    ActionSpec,
    ActionStaticLoop,
    BoundedSelectionSpec,
    CapacityParam,
    DeliveryEnforcement,
    ExtentKind,
    F32,
    I64,
    OrderKeyRole,
    OutputOrderKind,
    PhysicalDelivery,
    ReductionOperator,
    U32,
    verify_action_spec,
)
from .action_value_validation import _issue_verified_grouped_i64_host_columns
from .embree_runtime import PackedPoints
from .direct_optix_physical import prepare_direct_optix_bounded_selection_3d
from .optix_runtime import (
    OptixRowView,
    PackedAabbs2D,
    _RtdlAabbPairRow,
    _RtdlFixedRadiusNeighborRow,
    _check_status,
    _load_optix_library,
    pack_aabbs_2d,
    pack_points,
)
from .verified_packed_points import (
    issue_verified_unique_u32_packed_points,
)


@dataclass(frozen=True)
class ActionOptixPlacementIssue:
    code: str
    path: str
    message: str


class ActionOptixPlacementError(ValueError):
    def __init__(self, issue: ActionOptixPlacementIssue) -> None:
        self.issue = issue
        super().__init__(
            f"Action OptiX placement failed: {issue.code}@{issue.path}: {issue.message}"
        )


@dataclass(frozen=True)
class OptixBoundedSelectionProgram3D:
    spec: ActionSpec
    template_kind: str
    scope_output_field: str
    item_output_field: str
    distance_output_field: str
    scope_event_field: str
    item_event_field: str
    distance_event_field: str
    minimum_parameter: str
    maximum_parameter: str
    limit_parameter: str
    minimum_boundary: str
    maximum_boundary: str
    delivery_proof_reference: str
    template_digest: str
    max_per_scope_limit: int = 64

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "verified_action_optix_bounded_selection_3d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": self.template_kind,
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "bounded_emit"],
            "selection_scope": [self.scope_output_field],
            "selection_order": [self.distance_output_field, self.item_output_field],
            "scope_output_field": self.scope_output_field,
            "item_output_field": self.item_output_field,
            "distance_output_field": self.distance_output_field,
            "scope_event_field": self.scope_event_field,
            "item_event_field": self.item_event_field,
            "distance_event_field": self.distance_event_field,
            "minimum_parameter": self.minimum_parameter,
            "maximum_parameter": self.maximum_parameter,
            "limit_parameter": self.limit_parameter,
            "minimum_boundary": self.minimum_boundary,
            "maximum_boundary": self.maximum_boundary,
            "delivery_proof_reference": self.delivery_proof_reference,
            "payload_dwords": 1,
            "max_per_scope_limit": self.max_per_scope_limit,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "user_ptx_accepted": False,
            "backend_program_name_accepted": False,
        }

    def resource_plan(
        self,
        *,
        query_count: int,
        parameters: Mapping[str, object],
    ) -> dict[str, object]:
        limit = _require_nonnegative_integer(parameters, self.limit_parameter)
        if limit > self.max_per_scope_limit:
            _fail(
                "selection_limit_exceeds_template_resource_bound",
                f"parameters.{self.limit_parameter}",
                f"limit {limit} exceeds template bound {self.max_per_scope_limit}",
            )
        if query_count < 0:
            _fail("negative_query_count", "query_count", str(query_count))
        capacity = query_count * limit
        if capacity > (1 << 63) - 1:
            _fail("output_capacity_overflow", "resource_plan", str(capacity))
        return {
            "query_count": query_count,
            "per_scope_limit": limit,
            "bounded_output_capacity_rows": capacity,
            "bounded_output_capacity_bytes": capacity
            * ctypes.sizeof(_RtdlFixedRadiusNeighborRow),
            "payload_dwords": 1,
            "global_output_state_required": True,
            "unbounded_candidate_relation_materialized": False,
        }


def compile_optix_bounded_selection_3d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> OptixBoundedSelectionProgram3D:
    """Select a controlled OptiX template from verified IR features only."""

    verify_action_spec(spec)
    if spec.states or spec.reductions or spec.termination_proofs:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "first OptiX template admits filter plus one selected emit only",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "the template has no physical-delivery deduplication",
        )
    proof = spec.logical_event.proof_reference
    if not proof or proof not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "an externally discharged placement proof is required",
        )
    if len(spec.blocks) != 1 or any(
        isinstance(statement, ActionStaticLoop) for statement in spec.blocks[0].operations
    ):
        _fail("straight_line_block_required", "blocks", "template v1 is straight-line")
    if len(spec.emits) != 1:
        _fail("single_emit_required", "emits", "template v1 requires one emit")
    emit = spec.emits[0]
    selection = emit.selection
    if selection is None:
        _fail(
            "bounded_selection_required",
            "emits[0].selection",
            "this template is selected only for explicit per-scope bounded selection",
        )
    assert isinstance(selection, BoundedSelectionSpec)
    if len(selection.scope_key_fields) != 1:
        _fail(
            "single_scope_key_required",
            "emits[0].selection.scope_key_fields",
            "point-candidate template v1 supports one integer scope key",
        )
    if selection.scope_extent is not ExtentKind.QUERY_COUNT:
        _fail(
            "query_scope_extent_required",
            "emits[0].selection.scope_extent",
            selection.scope_extent.value,
        )
    if not isinstance(selection.limit, CapacityParam):
        _fail(
            "dynamic_limit_parameter_required",
            "emits[0].selection.limit",
            "point-candidate template v1 uses a checked integer parameter",
        )
    if len(selection.order_keys) != 2:
        _fail(
            "distance_then_item_order_required",
            "emits[0].selection.order_keys",
            "template v1 requires one f32 distance key and one integer item-id tie-break",
        )
    distance_key, item_key = selection.order_keys
    distance_field = emit.record_type.field(distance_key.field)
    item_field = emit.record_type.field(item_key.field)
    if distance_field is None or distance_field.value_type != F32:
        _fail(
            "f32_distance_order_required",
            "emits[0].selection.order_keys[0]",
            "first selected key must be f32",
        )
    if distance_key.ascending is not True:
        _fail("ascending_distance_required", "emits[0].selection.order_keys[0]", "false")
    if item_key.role is not OrderKeyRole.ITEM_ID or item_field is None:
        _fail(
            "integer_item_id_tiebreak_required",
            "emits[0].selection.order_keys[1]",
            "second key must be the verified item-id tie-break",
        )
    if item_key.ascending is not True:
        _fail("ascending_item_id_required", "emits[0].selection.order_keys[1]", "false")

    origins: dict[str, tuple[object, ...]] = {}
    emit_inputs: tuple[str, ...] | None = None
    filter_origin: tuple[object, ...] | None = None
    for index, statement in enumerate(spec.blocks[0].operations):
        assert isinstance(statement, ActionOp)
        path = f"blocks[0].operations[{index}]"
        if statement.opcode == "load_event":
            origins[statement.outputs[0].name] = ("event", str(statement.attribute("field")))
        elif statement.opcode == "load_param":
            origins[statement.outputs[0].name] = ("param", str(statement.attribute("field")))
        elif statement.opcode == "compare":
            origins[statement.outputs[0].name] = (
                "compare",
                str(statement.attribute("predicate")),
                origins[statement.inputs[0]],
                origins[statement.inputs[1]],
            )
        elif statement.opcode == "bool_and":
            origins[statement.outputs[0].name] = (
                "and",
                origins[statement.inputs[0]],
                origins[statement.inputs[1]],
            )
        elif statement.opcode == "filter":
            if filter_origin is not None:
                _fail("one_filter_required", path, "multiple filter operations")
            filter_origin = origins[statement.inputs[0]]
        elif statement.opcode == "emit":
            if emit_inputs is not None:
                _fail("one_emit_operation_required", path, "multiple emit operations")
            emit_inputs = statement.inputs
        else:
            _fail(
                "opcode_not_supported_by_optix_template",
                path,
                statement.opcode,
            )
    if emit_inputs is None or filter_origin is None:
        _fail("filter_and_emit_required", "blocks[0]", "missing filter or emit")

    output_origins = {
        field.name: origins[input_name]
        for field, input_name in zip(emit.record_type.fields, emit_inputs, strict=True)
    }
    scope_output = selection.scope_key_fields[0]
    scope_origin = _require_event_origin(output_origins[scope_output], scope_output)
    item_origin = _require_event_origin(output_origins[item_key.field], item_key.field)
    distance_origin = _require_event_origin(output_origins[distance_key.field], distance_key.field)
    if not isinstance(spec.event_type.field(distance_origin).value_type, ActionScalarType):
        _fail("scalar_distance_event_required", "event_type", distance_origin)

    minimum, maximum = _extract_distance_window(filter_origin, ("event", distance_origin))
    logical_keys = set(spec.logical_event.key_fields)
    if logical_keys != {scope_origin, item_origin}:
        _fail(
            "logical_event_identity_mismatch",
            "logical_event.key_fields",
            "point-candidate logical identity must be exactly scope-event plus item-event fields",
        )

    descriptor = {
        "template_kind": "point_candidate_3d_filter_bounded_selection_v1",
        "semantic_digest": spec.semantic_digest,
        "scope_event_field": scope_origin,
        "item_event_field": item_origin,
        "distance_event_field": distance_origin,
        "minimum_parameter": minimum[0],
        "minimum_boundary": minimum[1],
        "maximum_parameter": maximum[0],
        "maximum_boundary": maximum[1],
        "limit_parameter": selection.limit.name,
    }
    template_digest = hashlib.sha256(repr(sorted(descriptor.items())).encode("utf-8")).hexdigest()
    return OptixBoundedSelectionProgram3D(
        spec=spec,
        template_kind=str(descriptor["template_kind"]),
        scope_output_field=scope_output,
        item_output_field=item_key.field,
        distance_output_field=distance_key.field,
        scope_event_field=scope_origin,
        item_event_field=item_origin,
        distance_event_field=distance_origin,
        minimum_parameter=minimum[0],
        maximum_parameter=maximum[0],
        limit_parameter=selection.limit.name,
        minimum_boundary=minimum[1],
        maximum_boundary=maximum[1],
        delivery_proof_reference=proof,
        template_digest=template_digest,
    )


@dataclass(frozen=True)
class OptixAabbFilterBoundedEmitProgram2D:
    spec: ActionSpec
    template_kind: str
    query_output_field: str
    item_output_field: str
    query_event_field: str
    item_event_field: str
    overlap_event_field: str
    minimum_overlap_parameter: str
    minimum_overlap_boundary: str
    capacity_parameter: str
    delivery_proof_reference: str
    template_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "verified_action_optix_aabb_filter_bounded_emit_2d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": self.template_kind,
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "bounded_emit"],
            "event_source_contract": "aabb_overlap_candidate_2d.v1",
            "filter": {
                "event_field": self.overlap_event_field,
                "predicate": "gt" if self.minimum_overlap_boundary == "open" else "ge",
                "parameter": self.minimum_overlap_parameter,
                "minimum_boundary": self.minimum_overlap_boundary,
            },
            "delivery_proof_reference": self.delivery_proof_reference,
            "payload_dwords": 1,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "user_ptx_accepted": False,
            "backend_program_name_accepted": False,
        }

    def resource_plan(self, parameters: Mapping[str, object]) -> dict[str, object]:
        capacity = _require_nonnegative_integer(parameters, self.capacity_parameter)
        if capacity > 0xFFFFFFFF:
            _fail(
                "output_capacity_exceeds_template_bound",
                f"parameters.{self.capacity_parameter}",
                str(capacity),
            )
        return {
            "bounded_output_capacity_rows": capacity,
            "bounded_output_capacity_bytes": capacity * ctypes.sizeof(_RtdlAabbPairRow),
            "payload_dwords": 1,
            "global_output_state_required": True,
            "unbounded_candidate_relation_materialized": False,
            "overflow_policy": "fail_closed",
        }


def compile_optix_aabb_filter_bounded_emit_2d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> OptixAabbFilterBoundedEmitProgram2D:
    """Lower a verified scalar overlap filter and bounded pair emit by IR shape."""

    verified = verify_action_spec(spec)
    if set(verified.inferred_effects) != {ActionEffect.FILTER, ActionEffect.BOUNDED_EMIT}:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "AABB template requires exactly filter plus bounded_emit",
        )
    if spec.states or spec.reductions or spec.termination_proofs:
        _fail("effect_subset_not_supported", "spec", "state, reduce, and terminate are absent")
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "the template relies on the prepared AABB pair dedup contract",
        )
    proof = spec.logical_event.proof_reference
    if not proof or proof not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "an externally discharged placement proof is required",
        )
    if len(spec.blocks) != 1 or any(
        isinstance(statement, ActionStaticLoop) for statement in spec.blocks[0].operations
    ):
        _fail("straight_line_block_required", "blocks", "template v1 is straight-line")
    if len(spec.emits) != 1:
        _fail("single_emit_required", "emits", "template v1 requires one emit")
    emit = spec.emits[0]
    if emit.selection is not None:
        _fail("plain_bounded_emit_required", "emits[0].selection", "selection is not used")
    if not isinstance(emit.capacity, CapacityParam):
        _fail(
            "dynamic_capacity_parameter_required",
            "emits[0].capacity",
            "AABB template requires one checked capacity parameter",
        )
    if emit.order_kind is not OutputOrderKind.CANONICAL_ORDER:
        _fail("canonical_output_order_required", "emits[0].order_kind", emit.order_kind.value)
    if len(emit.record_type.fields) != 2 or len(emit.order_keys) != 2:
        _fail(
            "canonical_pair_output_required",
            "emits[0]",
            "template v1 emits two canonically ordered u32 identifiers",
        )
    if any(field.value_type != U32 for field in emit.record_type.fields):
        _fail("u32_pair_output_required", "emits[0].record_type", "non-u32 field")
    if tuple(key.field for key in emit.order_keys) != tuple(
        field.name for field in emit.record_type.fields
    ):
        _fail(
            "canonical_pair_order_mismatch",
            "emits[0].order_keys",
            "order keys must cover the emitted pair in record order",
        )

    origins: dict[str, tuple[object, ...]] = {}
    emit_inputs: tuple[str, ...] | None = None
    filter_origin: tuple[object, ...] | None = None
    for index, statement in enumerate(spec.blocks[0].operations):
        assert isinstance(statement, ActionOp)
        path = f"blocks[0].operations[{index}]"
        if statement.opcode == "load_event":
            origins[statement.outputs[0].name] = ("event", str(statement.attribute("field")))
        elif statement.opcode == "load_param":
            origins[statement.outputs[0].name] = ("param", str(statement.attribute("field")))
        elif statement.opcode == "compare":
            origins[statement.outputs[0].name] = (
                "compare",
                str(statement.attribute("predicate")),
                origins[statement.inputs[0]],
                origins[statement.inputs[1]],
            )
        elif statement.opcode == "filter":
            if filter_origin is not None:
                _fail("one_filter_required", path, "multiple filter operations")
            filter_origin = origins[statement.inputs[0]]
        elif statement.opcode == "emit":
            if emit_inputs is not None:
                _fail("one_emit_operation_required", path, "multiple emit operations")
            emit_inputs = statement.inputs
        else:
            _fail("opcode_not_supported_by_optix_template", path, statement.opcode)
    if emit_inputs is None or filter_origin is None:
        _fail("filter_and_emit_required", "blocks[0]", "missing filter or emit")
    output_origins = {
        field.name: origins[input_name]
        for field, input_name in zip(emit.record_type.fields, emit_inputs, strict=True)
    }
    query_output, item_output = (field.name for field in emit.record_type.fields)
    query_origin = _require_event_origin(output_origins[query_output], query_output)
    item_origin = _require_event_origin(output_origins[item_output], item_output)
    if set(spec.logical_event.key_fields) != {query_origin, item_origin}:
        _fail(
            "logical_event_identity_mismatch",
            "logical_event.key_fields",
            "AABB pair identity must be exactly the two emitted event identifiers",
        )
    if len(filter_origin) != 4 or filter_origin[0] != "compare":
        _fail("scalar_overlap_compare_required", "filter", repr(filter_origin))
    predicate = str(filter_origin[1])
    left, right = filter_origin[2], filter_origin[3]
    if predicate in {"gt", "ge"} and _is_event_origin(left) and _is_parameter_origin(right):
        overlap_origin, threshold_origin = left, right
        minimum_boundary = "open" if predicate == "gt" else "closed"
    elif predicate in {"lt", "le"} and _is_parameter_origin(left) and _is_event_origin(right):
        overlap_origin, threshold_origin = right, left
        minimum_boundary = "open" if predicate == "lt" else "closed"
    else:
        _fail(
            "ordered_overlap_filter_required",
            "filter",
            "template requires event_f32 >/>= parameter_f32",
        )
    overlap_field = str(overlap_origin[1])
    if spec.event_type.field(overlap_field) is None or spec.event_type.field(overlap_field).value_type != F32:
        _fail("f32_overlap_event_required", "event_type", overlap_field)
    threshold_parameter = str(threshold_origin[1])
    descriptor = {
        "template_kind": "aabb_overlap_candidate_2d_filter_bounded_emit_v1",
        "semantic_digest": spec.semantic_digest,
        "query_event_field": query_origin,
        "item_event_field": item_origin,
        "overlap_event_field": overlap_field,
        "minimum_overlap_parameter": threshold_parameter,
        "minimum_overlap_boundary": minimum_boundary,
        "capacity_parameter": emit.capacity.name,
    }
    template_digest = hashlib.sha256(
        repr(sorted(descriptor.items())).encode("utf-8")
    ).hexdigest()
    return OptixAabbFilterBoundedEmitProgram2D(
        spec=spec,
        template_kind=str(descriptor["template_kind"]),
        query_output_field=query_output,
        item_output_field=item_output,
        query_event_field=query_origin,
        item_event_field=item_origin,
        overlap_event_field=overlap_field,
        minimum_overlap_parameter=threshold_parameter,
        minimum_overlap_boundary=minimum_boundary,
        capacity_parameter=emit.capacity.name,
        delivery_proof_reference=proof,
        template_digest=template_digest,
    )


class PreparedOptixActionBoundedSelection3D:
    def __init__(
        self,
        program: OptixBoundedSelectionProgram3D,
        search_points,
        *,
        max_distance_bound: float,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
    ) -> None:
        if not math.isfinite(max_distance_bound) or max_distance_bound <= 0.0:
            raise ValueError("max_distance_bound must be finite and positive")
        packed = (
            search_points
            if isinstance(search_points, PackedPoints)
            else pack_points(records=search_points, dimension=3)
        )
        if packed.dimension != 3:
            raise ValueError("Action point-candidate source requires 3-D search points")
        verified_search = issue_verified_unique_u32_packed_points(
            packed,
            dimension=3,
            path="search_points",
        )
        self.program = program
        self._packed_search = packed
        self._max_distance_bound = float(max_distance_bound)
        self._closed = False
        self._direct_owner = prepare_direct_optix_bounded_selection_3d(
            verified_search,
            max_distance_bound=self._max_distance_bound,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
            _native_library_loader=_load_optix_library,
        )

    @property
    def _native_library_ref(self):
        return self._direct_owner._native_library_ref

    @_native_library_ref.setter
    def _native_library_ref(self, value) -> None:
        self._direct_owner._native_library_ref = value

    @property
    def _native_library_identity(self):
        return self._direct_owner._native_library_identity

    @_native_library_identity.setter
    def _native_library_identity(self, value) -> None:
        self._direct_owner._native_library_identity = value

    def run(
        self,
        query_points,
        parameters: Mapping[str, object],
        *,
        extents: Mapping[ExtentKind | str, int],
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Action OptiX handle is closed")
        packed = (
            query_points
            if isinstance(query_points, PackedPoints)
            else pack_points(records=query_points, dimension=3)
        )
        if packed.dimension != 3:
            raise ValueError("Action point-candidate query requires 3-D points")
        verified_query = issue_verified_unique_u32_packed_points(
            packed,
            dimension=3,
            path="query_points",
        )
        query_extent = extents.get(ExtentKind.QUERY_COUNT, extents.get("query_count"))
        if query_extent != packed.count:
            _fail(
                "query_extent_mismatch",
                "extents.query_count",
                f"declared {query_extent!r}, observed {packed.count}",
            )
        minimum = _require_f32(parameters, self.program.minimum_parameter)
        maximum = _require_f32(parameters, self.program.maximum_parameter)
        if minimum < 0.0 or maximum < minimum:
            _fail("invalid_distance_window", "parameters", f"{minimum}..{maximum}")
        if maximum > self._max_distance_bound:
            _fail(
                "maximum_exceeds_prepared_bound",
                f"parameters.{self.program.maximum_parameter}",
                str(maximum),
            )
        resource = self.program.resource_plan(query_count=packed.count, parameters=parameters)
        limit = int(resource["per_scope_limit"])
        if limit == 0 or packed.count == 0 or self._packed_search.count == 0:
            return {
                "rows": (),
                "metadata": self.program.to_metadata()
                | resource
                | {
                    "native_symbol": None,
                    "native_elapsed_sec": 0.0,
                    "empty_shortcut": True,
                    "rt_core_accelerated": False,
                },
            }

        direct = self._direct_owner.run(
            verified_query,
            minimum_distance=minimum,
            maximum_distance=maximum,
            k=limit,
            minimum_boundary=self.program.minimum_boundary,
            maximum_boundary=self.program.maximum_boundary,
        )
        rows = direct["rows"]
        direct_metadata = direct["metadata"]
        return {
            "rows": rows,
            "metadata": self.program.to_metadata()
            | resource
            | {
                "native_symbol": "rtdl_optix_run_prepared_action_bounded_selection_3d",
                "native_elapsed_sec": direct_metadata["native_elapsed_sec"],
                "emitted_row_count": len(rows),
                "empty_shortcut": False,
                "rt_core_accelerated": True,
                "prepared_search_resident": True,
                "unbounded_candidate_relation_materialized": False,
                "bounded_output_downloaded": True,
                "user_callback_executed": False,
                "direct_physical_owner_contract": direct_metadata["contract"],
                "search_validation_capability": dict(
                    direct_metadata["search_validation_capability"]
                ),
                "query_validation_capability": dict(
                    direct_metadata["query_validation_capability"]
                ),
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        self._direct_owner.close()
        self._closed = True

    def __enter__(self) -> PreparedOptixActionBoundedSelection3D:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_optix_action_bounded_selection_3d(
    program: OptixBoundedSelectionProgram3D,
    search_points,
    *,
    max_distance_bound: float,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
) -> PreparedOptixActionBoundedSelection3D:
    return PreparedOptixActionBoundedSelection3D(
        program,
        search_points,
        max_distance_bound=max_distance_bound,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
    )


class PreparedOptixActionAabbFilterBoundedEmit2D:
    def __init__(
        self,
        program: OptixAabbFilterBoundedEmitProgram2D,
        indexed_boxes,
    ) -> None:
        packed = indexed_boxes if isinstance(indexed_boxes, PackedAabbs2D) else pack_aabbs_2d(indexed_boxes)
        if packed.count == 0:
            raise ValueError("Action AABB event source requires at least one indexed box")
        _require_unique_aabb_u32_ids(packed, "indexed_boxes")
        self.program = program
        self._packed_indexed = packed
        self._handle = ctypes.c_void_p()
        self._closed = False
        lib = _load_optix_library()
        _configure_action_aabb_optix_symbols(lib)
        error = ctypes.create_string_buffer(4096)
        status = lib.rtdl_optix_prepare_action_aabb_candidates_2d(
            packed.records,
            ctypes.c_size_t(packed.count),
            ctypes.byref(self._handle),
            error,
            ctypes.c_size_t(len(error)),
        )
        _check_status(status, error)

    def run(
        self,
        query_boxes,
        parameters: Mapping[str, object],
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Action OptiX handle is closed")
        packed = query_boxes if isinstance(query_boxes, PackedAabbs2D) else pack_aabbs_2d(query_boxes)
        _require_unique_aabb_u32_ids(packed, "query_boxes")
        threshold = _require_f32(parameters, self.program.minimum_overlap_parameter)
        if threshold < 0.0:
            _fail(
                "negative_overlap_threshold",
                f"parameters.{self.program.minimum_overlap_parameter}",
                str(threshold),
            )
        resource = self.program.resource_plan(parameters)
        capacity = int(resource["bounded_output_capacity_rows"])
        row_array = (_RtdlAabbPairRow * capacity)() if capacity else None
        emitted_count = ctypes.c_size_t()
        overflowed = ctypes.c_uint32()
        lib = _load_optix_library()
        _configure_action_aabb_optix_symbols(lib)
        error = ctypes.create_string_buffer(4096)
        started = time.perf_counter()
        run_v2 = getattr(
            lib,
            "rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d_v2",
            None,
        )
        if run_v2 is not None:
            status = run_v2(
                self._handle,
                packed.records,
                ctypes.c_size_t(packed.count),
                ctypes.c_double(threshold),
                ctypes.c_uint32(_boundary_mode(self.program.minimum_overlap_boundary)),
                row_array,
                ctypes.c_size_t(capacity),
                ctypes.byref(emitted_count),
                ctypes.byref(overflowed),
                error,
                ctypes.c_size_t(len(error)),
            )
            native_symbol = "rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d_v2"
        elif self.program.minimum_overlap_boundary == "open":
            status = lib.rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d(
                self._handle,
                packed.records,
                ctypes.c_size_t(packed.count),
                ctypes.c_double(threshold),
                row_array,
                ctypes.c_size_t(capacity),
                ctypes.byref(emitted_count),
                ctypes.byref(overflowed),
                error,
                ctypes.c_size_t(len(error)),
            )
            native_symbol = "rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d"
        else:
            _fail(
                "closed_overlap_boundary_abi_unavailable",
                "native",
                "loaded OptiX backend does not export the v2 AABB Action ABI",
            )
        _check_status(status, error)
        elapsed = time.perf_counter() - started
        if overflowed.value:
            _fail(
                "bounded_emit_capacity_overflow",
                "native.rows",
                f"observed {emitted_count.value} rows for capacity {capacity}",
            )
        rows = tuple(
            (int(row_array[index].query_id), int(row_array[index].indexed_id))
            for index in range(emitted_count.value)
        )
        return {
            "rows": rows,
            "metadata": self.program.to_metadata()
            | resource
            | {
                "native_symbol": native_symbol,
                "native_elapsed_sec": elapsed,
                "emitted_row_count": len(rows),
                "rt_core_accelerated": True,
                "prepared_index_resident": True,
                "unbounded_candidate_relation_materialized": False,
                "bounded_output_downloaded": True,
                "user_callback_executed": False,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        if self._handle.value:
            lib = _load_optix_library()
            _configure_action_aabb_optix_symbols(lib)
            lib.rtdl_optix_destroy_prepared_action_aabb_candidates_2d(self._handle)
        self._handle = ctypes.c_void_p()
        self._closed = True

    def __enter__(self) -> PreparedOptixActionAabbFilterBoundedEmit2D:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_optix_action_aabb_filter_bounded_emit_2d(
    program: OptixAabbFilterBoundedEmitProgram2D,
    indexed_boxes,
) -> PreparedOptixActionAabbFilterBoundedEmit2D:
    return PreparedOptixActionAabbFilterBoundedEmit2D(program, indexed_boxes)


@dataclass(frozen=True)
class OptixKeyedI64SumProgram3D:
    spec: ActionSpec
    template_kind: str
    primitive_event_field: str
    group_event_field: str
    include_event_field: str
    value_event_field: str
    reduction_name: str
    dedup_proof_reference: str
    template_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "verified_action_optix_keyed_i64_sum_3d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": self.template_kind,
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "keyed_reduce"],
            "logical_event_key": [self.primitive_event_field, self.group_event_field],
            "primitive_event_field": self.primitive_event_field,
            "group_event_field": self.group_event_field,
            "include_event_field": self.include_event_field,
            "value_event_field": self.value_event_field,
            "reduction_name": self.reduction_name,
            "reduction_key": [self.group_event_field],
            "reduction_operator": "sum",
            "reduction_value_type": "i64",
            "dedup_proof_reference": self.dedup_proof_reference,
            "excluded_primitive_policy": "private_sink_group_then_drop",
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "user_ptx_accepted": False,
            "backend_program_name_accepted": False,
        }


def compile_optix_keyed_i64_sum_3d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> OptixKeyedI64SumProgram3D:
    """Lower a filtered, keyed exact-i64 sum by verified IR shape."""

    verified = verify_action_spec(spec)
    if set(verified.inferred_effects) != {ActionEffect.FILTER, ActionEffect.KEYED_REDUCE}:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "grouped-i64 template requires exactly filter plus keyed_reduce",
        )
    if spec.states or spec.emits or spec.termination_proofs or len(spec.reductions) != 1:
        _fail(
            "single_reduction_only",
            "spec",
            "grouped-i64 template admits one reduction and no state, emit, or termination",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.MAY_REPEAT
        or spec.logical_event.enforcement is not DeliveryEnforcement.KEYED_DEDUP
    ):
        _fail(
            "keyed_dedup_contract_required",
            "logical_event",
            "ray/primitive delivery may repeat and must be deduplicated",
        )
    dedup_proof = "ray-triangle-stable-primitive-keyed-dedup-v1"
    if dedup_proof not in discharged_delivery_proofs:
        _fail(
            "dedup_proof_not_discharged",
            "logical_event",
            f"placement requires {dedup_proof}",
        )
    reduction = spec.reductions[0]
    if (
        reduction.operator is not ReductionOperator.SUM
        or reduction.value_type != I64
        or reduction.identity.to_python() != 0
        or len(reduction.key_fields) != 1
    ):
        _fail(
            "exact_keyed_i64_sum_required",
            "reductions[0]",
            "template requires one-key signed-i64 SUM with identity zero",
        )
    group_field = reduction.key_fields[0]
    group_type = spec.event_type.field(group_field)
    if group_type is None or group_type.value_type != U32:
        _fail("u32_group_key_required", "reductions[0].key_fields", group_field)
    if len(spec.blocks) != 1 or any(
        isinstance(statement, ActionStaticLoop) for statement in spec.blocks[0].operations
    ):
        _fail("straight_line_block_required", "blocks", "template v1 is straight-line")

    origins: dict[str, tuple[object, ...]] = {}
    filter_origin: tuple[object, ...] | None = None
    reduce_origin: tuple[object, ...] | None = None
    for index, statement in enumerate(spec.blocks[0].operations):
        assert isinstance(statement, ActionOp)
        path = f"blocks[0].operations[{index}]"
        if statement.opcode == "load_event":
            origins[statement.outputs[0].name] = ("event", str(statement.attribute("field")))
        elif statement.opcode == "filter":
            if filter_origin is not None:
                _fail("one_filter_required", path, "multiple filter operations")
            filter_origin = origins[statement.inputs[0]]
        elif statement.opcode == "reduce":
            if reduce_origin is not None or statement.attribute("reduction") != reduction.name:
                _fail("one_matching_reduce_required", path, str(statement.attribute("reduction")))
            reduce_origin = origins[statement.inputs[0]]
        else:
            _fail("opcode_not_supported_by_optix_template", path, statement.opcode)
    if not _is_event_origin(filter_origin) or not _is_event_origin(reduce_origin):
        _fail(
            "direct_event_filter_and_value_required",
            "blocks[0]",
            "filter predicate and reduced value must be direct event fields",
        )
    include_field = str(filter_origin[1])
    value_field = str(reduce_origin[1])
    include_type = spec.event_type.field(include_field)
    value_type = spec.event_type.field(value_field)
    if include_type is None or include_type.value_type.kind.value != "bool":
        _fail("bool_include_event_required", "blocks[0].filter", include_field)
    if value_type is None or value_type.value_type != I64:
        _fail("i64_value_event_required", "blocks[0].reduce", value_field)
    logical_keys = set(spec.logical_event.key_fields)
    primitive_fields = logical_keys.difference({group_field})
    if len(logical_keys) != 2 or len(primitive_fields) != 1:
        _fail(
            "primitive_and_group_logical_key_required",
            "logical_event.key_fields",
            repr(spec.logical_event.key_fields),
        )
    primitive_field = next(iter(primitive_fields))
    primitive_type = spec.event_type.field(primitive_field)
    if primitive_type is None or primitive_type.value_type.kind.value not in {"u32", "u64"}:
        _fail("integer_primitive_id_required", "logical_event.key_fields", primitive_field)

    descriptor = {
        "template_kind": "ray_triangle_filter_keyed_i64_sum_3d_v1",
        "semantic_digest": spec.semantic_digest,
        "primitive_event_field": primitive_field,
        "group_event_field": group_field,
        "include_event_field": include_field,
        "value_event_field": value_field,
        "dedup_proof_reference": dedup_proof,
    }
    template_digest = hashlib.sha256(
        repr(sorted(descriptor.items())).encode("utf-8")
    ).hexdigest()
    return OptixKeyedI64SumProgram3D(
        spec=spec,
        template_kind=str(descriptor["template_kind"]),
        primitive_event_field=primitive_field,
        group_event_field=group_field,
        include_event_field=include_field,
        value_event_field=value_field,
        reduction_name=reduction.name,
        dedup_proof_reference=dedup_proof,
        template_digest=template_digest,
    )


def _validate_canonical_optix_keyed_i64_sum_program_3d(
    program: OptixKeyedI64SumProgram3D,
) -> None:
    """Reject role mutation and metadata-counterfeit programs before execution."""

    if type(program) is not OptixKeyedI64SumProgram3D:
        _fail(
            "optix_keyed_i64_sum_program_exact_type_required",
            "program",
            type(program).__name__,
        )
    canonical = compile_optix_keyed_i64_sum_3d(
        program.spec,
        discharged_delivery_proofs=frozenset(
            {"ray-triangle-stable-primitive-keyed-dedup-v1"}
        ),
    )
    if program != canonical:
        _fail(
            "optix_keyed_i64_sum_program_role_binding_invalid",
            "program",
            "executable roles differ from the canonical verified Action lowering",
        )


class PreparedOptixActionKeyedI64Sum3D:
    def __init__(
        self,
        program: OptixKeyedI64SumProgram3D,
        triangles,
        *,
        primitive_group_ids: Sequence[int],
        primitive_values: Sequence[int],
        primitive_includes: Sequence[bool] | AllIncludedPrimitiveMask,
        group_count: int,
    ) -> None:
        _validate_canonical_optix_keyed_i64_sum_program_3d(program)
        if not isinstance(group_count, int) or isinstance(group_count, bool) or group_count < 0:
            _fail("nonnegative_group_count_required", "group_count", repr(group_count))
        import numpy as np

        try:
            source_groups = np.asarray(primitive_group_ids)
            source_values = np.asarray(primitive_values)
        except (TypeError, ValueError, OverflowError) as exc:
            _fail("primitive_payload_array_invalid", "primitive_payload", str(exc))
        if any(array.ndim != 1 for array in (source_groups, source_values)):
            _fail(
                "primitive_payload_rank_invalid",
                "primitive_payload",
                "group and value payloads must be 1-D",
            )
        if source_groups.dtype.kind not in {"i", "u"}:
            _fail(
                "primitive_group_type_invalid",
                "primitive_group_ids",
                str(source_groups.dtype),
            )
        if source_values.dtype.kind not in {"i", "u"}:
            _fail(
                "primitive_value_type_invalid",
                "primitive_values",
                str(source_values.dtype),
            )
        if source_groups.size != source_values.size:
            _fail(
                "primitive_payload_length_mismatch",
                "primitive_payload",
                f"groups={source_groups.size} values={source_values.size}",
            )
        primitive_count = int(source_groups.size)
        if group_count >= 0xFFFFFFFF:
            _fail("group_count_exceeds_sink_encoding", "group_count", str(group_count))
        if type(primitive_includes) is AllIncludedPrimitiveMask:
            primitive_includes.validate()
            if len(primitive_includes) != primitive_count:
                _fail(
                    "primitive_payload_length_mismatch",
                    "primitive_payload",
                    (
                        f"groups={primitive_count} values={source_values.size} "
                        f"includes={len(primitive_includes)}"
                    ),
                )
            include_mode = primitive_includes.contract
            sink_group = None
            physical_group_count = group_count
            includes_for_certificate = None
        else:
            try:
                includes = np.asarray(primitive_includes)
            except (TypeError, ValueError, OverflowError) as exc:
                _fail("primitive_payload_array_invalid", "primitive_includes", str(exc))
            if includes.ndim != 1:
                _fail(
                    "primitive_payload_rank_invalid",
                    "primitive_includes",
                    "include payload must be 1-D",
                )
            if includes.size != primitive_count:
                _fail(
                    "primitive_payload_length_mismatch",
                    "primitive_payload",
                    (
                        f"groups={primitive_count} values={source_values.size} "
                        f"includes={includes.size}"
                    ),
                )
            include_mode = "per_primitive_bool_mask.v1"
            sink_group = group_count
            physical_group_count = group_count + 1
            includes_for_certificate = primitive_includes
        try:
            verified_host_columns = _issue_verified_grouped_i64_host_columns(
                source_groups,
                source_values,
                primitive_count=primitive_count,
                group_count=int(physical_group_count),
                primitive_includes=includes_for_certificate,
                sink_group=sink_group,
            )
        except OverflowError as exc:
            if "primitive_values entries exceed" in str(exc):
                _fail("primitive_value_i64_overflow", "primitive_values", str(exc))
            if "primitive_group_ids entries exceed" in str(exc):
                _fail("primitive_group_out_of_range", "primitive_group_ids", str(exc))
            raise
        except ValueError as exc:
            if "primitive_group_ids entries" in str(exc):
                _fail("primitive_group_out_of_range", "primitive_group_ids", str(exc))
            _fail("primitive_payload_array_invalid", "primitive_payload", str(exc))
        from .generic_primitives import (
            prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d,
        )

        self.program = program
        self.group_count = group_count
        self.sink_group = sink_group
        self.primitive_include_mode = include_mode
        self._prepared = prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d(
            triangles,
            primitive_group_ids=None,
            primitive_values=None,
            group_count=physical_group_count,
            backend="optix",
            required_reduction="sum",
            verified_host_columns=verified_host_columns,
        )
        self.primitive_count = primitive_count
        self.physical_group_count = int(physical_group_count)
        self._closed = False
        try:
            self._prepared_backend_owner_ref = self._prepared
            self._prepared_backend_owner_object_id = id(self._prepared)
            self._prepared_backend_owner_type = self._qualified_type_name(self._prepared)
            self._prepared_backend_owner_close_method = getattr(
                type(self._prepared),
                "close",
            )
            self._prepared_backend_owner_facts = self._current_prepared_backend_owner_facts()
            self._prepared_backend_owner_seal = self._issue_prepared_backend_owner_seal()
            self._prepared_backend_owner_identity_digest = hashlib.sha256(
                self._prepared_backend_owner_binding_payload()
            ).hexdigest()
            self._close_progress = 0
            self._close_seal = self._issue_close_seal()
        except Exception:
            try:
                type(self._prepared).close(self._prepared)
            except Exception:
                pass
            raise

    @staticmethod
    def _qualified_type_name(value: object) -> str:
        return f"{type(value).__module__}.{type(value).__qualname__}"

    def _current_prepared_backend_owner_facts(self) -> tuple[object, ...]:
        """Snapshot the exact nested generic owner and its live native resources."""

        owner = self._prepared
        metadata_function = getattr(
            type(owner),
            "compiler_backend_owner_metadata",
            None,
        )
        if metadata_function is None:
            _fail(
                "prepared_keyed_i64_backend_owner_metadata_required",
                "prepared.backend_owner",
                self._qualified_type_name(owner),
            )
        native_metadata = metadata_function(owner)
        if not isinstance(native_metadata, Mapping):
            _fail(
                "prepared_keyed_i64_backend_owner_metadata_invalid",
                "prepared.backend_owner",
                type(native_metadata).__name__,
            )
        native_metadata = dict(native_metadata)
        native_identity_digest = native_metadata.get(
            "prepared_resource_identity_digest"
        )
        if not isinstance(native_identity_digest, str):
            _fail(
                "prepared_keyed_i64_backend_owner_metadata_invalid",
                "prepared.backend_owner",
                "prepared resource identity digest is missing",
            )
        return (
            self._qualified_type_name(owner),
            str(getattr(owner, "contract", "unspecified")),
            str(getattr(owner, "backend", "unspecified")),
            getattr(owner, "triangle_count", "unspecified"),
            getattr(owner, "group_count", "unspecified"),
            id(getattr(owner, "_prepared_scene", None)),
            id(getattr(owner, "_prepared_payload", None)),
            id(getattr(owner, "_scene_cm", None)),
            id(getattr(owner, "_payload_cm", None)),
            native_identity_digest,
            id(metadata_function),
            self._qualified_type_name(metadata_function),
            id(getattr(type(owner), "close", None)),
            self._qualified_type_name(getattr(type(owner), "close", None)),
            repr(native_metadata),
        )

    def _issue_close_seal(self) -> str:
        return hmac.new(
            _PREPARED_ACTION_KEYED_I64_BACKEND_OWNER_SECRET,
            (
                "rtdl.prepared_keyed_i64_outer_close.v1\x00"
                + str(id(self._prepared_backend_owner_ref))
                + "\x00"
                + self._prepared_backend_owner_type
                + "\x00"
                + self._prepared_backend_owner_identity_digest
                + "\x00"
                + str(self._close_progress)
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _prepared_backend_owner_binding_payload(self) -> bytes:
        return (
            "rtdl.prepared_optix_action_keyed_i64_nested_owner_binding.v1\x00"
            + str(self._prepared_backend_owner_object_id)
            + "\x00"
            + self._prepared_backend_owner_type
            + "\x00"
            + repr(self._prepared_backend_owner_facts)
        ).encode("utf-8")

    def _issue_prepared_backend_owner_seal(self) -> str:
        return hmac.new(
            _PREPARED_ACTION_KEYED_I64_BACKEND_OWNER_SECRET,
            self._prepared_backend_owner_binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_prepared_backend_owner_binding(self) -> None:
        owner = self._prepared
        if (
            owner is not self._prepared_backend_owner_ref
            or id(owner) != self._prepared_backend_owner_object_id
            or self._qualified_type_name(owner) != self._prepared_backend_owner_type
        ):
            _fail(
                "prepared_keyed_i64_backend_owner_binding_invalid",
                "prepared.backend_owner",
                "nested generic owner object changed",
            )
        if bool(getattr(owner, "closed", False)) or (
            hasattr(owner, "_prepared_scene")
            and (
                getattr(owner, "_prepared_scene", None) is None
                or getattr(owner, "_prepared_payload", None) is None
            )
        ):
            _fail(
                "prepared_keyed_i64_backend_owner_closed",
                "prepared.backend_owner",
                "nested generic owner was closed before the outer owner",
            )
        try:
            current_facts = self._current_prepared_backend_owner_facts()
        except Exception as exc:
            _fail(
                "prepared_keyed_i64_backend_owner_binding_invalid",
                "prepared.backend_owner",
                f"nested resource validation failed: {type(exc).__name__}:{exc}",
            )
        current_identity_digest = hashlib.sha256(
            self._prepared_backend_owner_binding_payload()
        ).hexdigest()
        if (
            current_facts != self._prepared_backend_owner_facts
            or not hmac.compare_digest(
                self._prepared_backend_owner_seal,
                self._issue_prepared_backend_owner_seal(),
            )
            or not hmac.compare_digest(
                self._prepared_backend_owner_identity_digest,
                current_identity_digest,
            )
        ):
            _fail(
                "prepared_keyed_i64_backend_owner_binding_invalid",
                "prepared.backend_owner",
                "nested generic owner or its prepared resources changed",
            )

    def run(self, rays) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Action keyed-i64-sum handle is closed")
        self._validate_prepared_backend_owner_binding()
        return self._project_result(
            type(self._prepared).run(self._prepared, rays, reduction="sum")
        )

    def prepare_query(self, rays):
        """Prepare one compiler-owned ray batch reusable across compatible scenes."""

        if self._closed:
            raise RuntimeError("prepared Action keyed-i64-sum handle is closed")
        self._validate_prepared_backend_owner_binding()
        return type(self._prepared).prepare_ray_batch(self._prepared, rays)

    def run_prepared_query(self, prepared_rays) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Action keyed-i64-sum handle is closed")
        self._validate_prepared_backend_owner_binding()
        return self._project_result(
            type(self._prepared).run_prepared_rays(
                self._prepared,
                prepared_rays,
                reduction="sum",
            )
        )

    def _project_result(self, result) -> dict[str, object]:
        backend_owner_metadata = result.get("prepared_backend_owner_metadata")
        if backend_owner_metadata is None:
            backend_owner_metadata = type(
                self._prepared
            ).compiler_backend_owner_metadata(self._prepared)
        if not isinstance(backend_owner_metadata, Mapping):
            _fail(
                "prepared_keyed_i64_backend_owner_metadata_required",
                "prepared.backend_owner",
                type(backend_owner_metadata).__name__,
            )
        rows = tuple(
            (int(row["group_id"]), int(row["sum"]))
            for row in result["rows"]
            if self.sink_group is None or int(row["group_id"]) != self.sink_group
        )
        return {
            "rows": rows,
            "metadata": {
                **self.program.to_metadata(),
                "group_count": self.group_count,
                "physical_group_count": self.physical_group_count,
                "primitive_include_mode": self.primitive_include_mode,
                "sink_group_reserved": self.sink_group is not None,
                "sink_group_not_exposed": True,
                "hit_event_count_before_dedup": int(result["hit_event_count_before_dedup"]),
                "deduplicated_primitive_hit_count": int(
                    result["deduplicated_primitive_hit_count"]
                ),
                "rt_core_accelerated": bool(result["rt_core_accelerated"]),
                "prepared_scene_used": bool(result.get("prepared_scene_used", False)),
                "prepared_payload_used": bool(
                    result.get("prepared_generic_payload_used", False)
                ),
                "prepared_generic_ray_batch_used": bool(
                    result.get("prepared_generic_ray_batch_used", False)
                ),
                "prepared_backend_owner_metadata": dict(
                    backend_owner_metadata
                ),
                "unbounded_event_rows_downloaded": False,
                "group_rows_downloaded": True,
                "phase_timing_seconds": dict(result.get("phase_timing_seconds", {})),
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        if (
            self._prepared is not self._prepared_backend_owner_ref
            or self._qualified_type_name(self._prepared)
            != self._prepared_backend_owner_type
            or getattr(type(self._prepared), "close", None)
            is not self._prepared_backend_owner_close_method
            or self._close_progress not in {0, 1}
            or not isinstance(self._close_seal, str)
            or not hmac.compare_digest(self._close_seal, self._issue_close_seal())
        ):
            _fail(
                "prepared_keyed_i64_backend_owner_binding_invalid",
                "prepared.backend_owner",
                "outer close owner or progress seal changed",
            )
        if self._close_progress == 0:
            self._validate_prepared_backend_owner_binding()
        try:
            self._prepared_backend_owner_close_method(
                self._prepared_backend_owner_ref
            )
        except Exception:
            owner = self._prepared_backend_owner_ref
            if bool(getattr(owner, "_payload_close_committed", False)) or bool(
                getattr(owner, "_scene_close_committed", False)
            ):
                self._close_progress = 1
                self._close_seal = self._issue_close_seal()
            raise
        self._close_progress = 2
        self._close_seal = self._issue_close_seal()
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed

    def consumed_owner_metadata(self) -> dict[str, object]:
        """Return structural facts for a compiler-owned consumed resource."""

        if self._closed:
            _fail(
                "prepared_keyed_i64_owner_closed",
                "prepared.backend_owner",
                "prepared owner is closed",
            )
        self._validate_prepared_backend_owner_binding()

        return {
            "contract": "rtdl.optix_action_keyed_i64_sum_prepared_owner.v1",
            "semantic_digest": self.program.spec.semantic_digest,
            "template_digest": self.program.template_digest,
            "program_roles": self.program.to_metadata(),
            "primitive_count": self.primitive_count,
            "logical_group_count": self.group_count,
            "physical_group_count": self.physical_group_count,
            "primitive_include_mode": self.primitive_include_mode,
            "sink_group_reserved": self.sink_group is not None,
            "nested_backend_owner_type": self._prepared_backend_owner_type,
            "nested_backend_owner_identity_digest": (
                self._prepared_backend_owner_identity_digest
            ),
        }

    def to_metadata(self) -> dict[str, object]:
        """Expose sealed compiler evidence for the live nested native owner."""

        if self._closed:
            _fail(
                "prepared_keyed_i64_owner_closed",
                "prepared.backend_owner",
                "prepared owner is closed",
            )
        self._validate_prepared_backend_owner_binding()
        nested = type(self._prepared).compiler_backend_owner_metadata(
            self._prepared
        )
        if not isinstance(nested, Mapping):
            _fail(
                "prepared_keyed_i64_backend_owner_metadata_invalid",
                "prepared.backend_owner",
                type(nested).__name__,
            )
        return {
            **self.consumed_owner_metadata(),
            "contract": "rtdl.optix_action_keyed_i64_sum_prepared_owner_metadata.v1",
            "nested_backend_owner_metadata": dict(nested),
            "closed": False,
        }

    def __enter__(self) -> PreparedOptixActionKeyedI64Sum3D:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_optix_action_keyed_i64_sum_3d(
    program: OptixKeyedI64SumProgram3D,
    triangles,
    *,
    primitive_group_ids: Sequence[int],
    primitive_values: Sequence[int],
    primitive_includes: Sequence[bool] | AllIncludedPrimitiveMask,
    group_count: int,
) -> PreparedOptixActionKeyedI64Sum3D:
    return PreparedOptixActionKeyedI64Sum3D(
        program,
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        primitive_includes=primitive_includes,
        group_count=group_count,
    )


class AllIncludedPrimitiveMask:
    """Typed constant-true include certificate without an O(N) boolean array."""

    __slots__ = ("_count", "_seal")
    contract = "all_primitives_included.v1"

    def __init__(self, count: int) -> None:
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            _fail("nonnegative_primitive_count_required", "count", repr(count))
        self._count = count
        self._seal = self._issue_seal()

    def _issue_seal(self) -> str:
        return hmac.new(
            _ALL_INCLUDED_PRIMITIVE_MASK_SECRET,
            (self.contract + "\x00" + str(self._count)).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def validate(self) -> None:
        if (
            type(self) is not AllIncludedPrimitiveMask
            or not isinstance(self._count, int)
            or isinstance(self._count, bool)
            or self._count < 0
            or not isinstance(self._seal, str)
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            _fail(
                "all_included_primitive_mask_binding_invalid",
                "primitive_includes",
                "exact type, primitive count, or compiler seal changed",
            )

    def __len__(self) -> int:
        self.validate()
        return self._count

    def to_metadata(self) -> dict[str, object]:
        self.validate()
        return {
            "contract": self.contract,
            "primitive_count": self._count,
            "constant_value": True,
            "materialized_boolean_column": False,
        }


def all_included_primitive_mask(count: int) -> AllIncludedPrimitiveMask:
    """Issue an app-neutral constant include certificate for one payload."""

    return AllIncludedPrimitiveMask(count)


class ConsumedOptixActionKeyedI64Sum3D:
    """Move-only capability for one synchronously prepared keyed-sum owner.

    Host payload aliases are no longer part of the persistent Action identity:
    preparation has already copied them into a closed compiler-owned backend
    resource.  A private seal binds the exact owner object, program, structural
    facts, and fresh resource generation until one atomic consumption.
    """

    contract = "rtdl.consumed_optix_action_keyed_i64_sum_owner.v1"

    def __init__(self, owner: PreparedOptixActionKeyedI64Sum3D) -> None:
        if type(owner) is not PreparedOptixActionKeyedI64Sum3D:
            _fail("prepared_keyed_i64_owner_required", "owner", type(owner).__name__)
        _validate_canonical_optix_keyed_i64_sum_program_3d(owner.program)
        if owner.closed:
            _fail("prepared_keyed_i64_owner_closed", "owner", "owner is closed")
        self._owner = owner
        self._owner_ref = owner
        self._owner_object_id = id(owner)
        self._owner_type = f"{type(owner).__module__}.{type(owner).__qualname__}"
        self._generation = secrets.token_bytes(32)
        self._generation_sha256 = hashlib.sha256(self._generation).hexdigest()
        self._structural_metadata = owner.consumed_owner_metadata()
        self._consumed = False
        self._seal = self._issue_seal()
        self._identity_digest = self._issue_identity_digest()
        self._owner_close_method = getattr(type(owner), "close")
        self._owner_close_method_object_id = id(self._owner_close_method)
        self._owner_close_method_type = (
            f"{type(self._owner_close_method).__module__}."
            f"{type(self._owner_close_method).__qualname__}"
        )
        self._close_progress = 0
        self._close_seal = self._issue_close_seal()

    def _issue_identity_digest(self) -> str:
        return hashlib.sha256(
            (
                self.contract
                + "\x00"
                + self._generation_sha256
                + "\x00"
                + repr(sorted(self._structural_metadata.items()))
            ).encode("utf-8")
        ).hexdigest()

    @property
    def identity_digest(self) -> str:
        return self._identity_digest

    @property
    def consumed(self) -> bool:
        return self._consumed

    def _issue_seal(self) -> str:
        return hmac.new(
            _PREPARED_ACTION_KEYED_I64_CONSUMED_OWNER_SECRET,
            (
                self.contract
                + "\x00"
                + str(self._owner_object_id)
                + "\x00"
                + self._owner_type
                + "\x00"
                + self._generation.hex()
                + "\x00"
                + repr(sorted(self._structural_metadata.items()))
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _issue_close_seal(self) -> str:
        return hmac.new(
            _PREPARED_ACTION_KEYED_I64_CONSUMED_OWNER_SECRET,
            (
                self.contract
                + "\x00close\x00"
                + str(self._owner_object_id)
                + "\x00"
                + self._owner_type
                + "\x00"
                + self._generation.hex()
                + "\x00"
                + self._generation_sha256
                + "\x00"
                + self._identity_digest
                + "\x00"
                + str(self._owner_close_method_object_id)
                + "\x00"
                + self._owner_close_method_type
                + "\x00"
                + str(self._close_progress)
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _validate_close_binding(
        self,
        owner: PreparedOptixActionKeyedI64Sum3D,
    ) -> None:
        if (
            owner is not self._owner_ref
            or self._owner is not self._owner_ref
            or id(owner) != self._owner_object_id
            or f"{type(owner).__module__}.{type(owner).__qualname__}"
            != self._owner_type
            or getattr(type(owner), "close", None) is not self._owner_close_method
            or id(self._owner_close_method) != self._owner_close_method_object_id
            or (
                f"{type(self._owner_close_method).__module__}."
                f"{type(self._owner_close_method).__qualname__}"
            )
            != self._owner_close_method_type
            or hashlib.sha256(self._generation).hexdigest()
            != self._generation_sha256
            or not hmac.compare_digest(self._seal, self._issue_seal())
            or not hmac.compare_digest(
                self._identity_digest,
                self._issue_identity_digest(),
            )
            or self._close_progress not in {0, 1}
            or not isinstance(self._close_seal, str)
            or not hmac.compare_digest(
                self._close_seal,
                self._issue_close_seal(),
            )
        ):
            _fail(
                "consumed_keyed_i64_owner_binding_invalid",
                "consumed_owner",
                "prepared owner object, generation, close method, or seal changed",
            )

    def _validate_for_program(self, program: OptixKeyedI64SumProgram3D) -> None:
        _validate_canonical_optix_keyed_i64_sum_program_3d(program)
        if self._consumed or self._owner is None:
            _fail(
                "consumed_keyed_i64_owner_already_taken",
                "consumed_owner",
                "owner capability is single-use",
            )
        if (
            self._owner is not self._owner_ref
            or id(self._owner) != self._owner_object_id
            or f"{type(self._owner).__module__}.{type(self._owner).__qualname__}"
            != self._owner_type
            or hashlib.sha256(self._generation).hexdigest()
            != self._generation_sha256
            or not hmac.compare_digest(self._seal, self._issue_seal())
            or not hmac.compare_digest(
                self._identity_digest,
                self._issue_identity_digest(),
            )
            or self._close_progress != 0
            or not isinstance(self._close_seal, str)
            or not hmac.compare_digest(
                self._close_seal,
                self._issue_close_seal(),
            )
        ):
            _fail(
                "consumed_keyed_i64_owner_binding_invalid",
                "consumed_owner",
                "prepared owner object or private seal changed",
            )
        if self._owner.closed:
            _fail(
                "consumed_keyed_i64_owner_closed",
                "consumed_owner",
                "prepared owner was closed before transfer",
            )
        _validate_canonical_optix_keyed_i64_sum_program_3d(self._owner.program)
        if program != self._owner.program:
            _fail(
                "consumed_keyed_i64_owner_program_mismatch",
                "program",
                "prepared owner was created for a different canonical program",
            )
        if (
            program.template_digest
            != self._structural_metadata["template_digest"]
            or program.spec.semantic_digest
            != self._structural_metadata["semantic_digest"]
        ):
            _fail(
                "consumed_keyed_i64_owner_program_mismatch",
                "program",
                "prepared owner was created for a different verified program",
            )
        if self._owner.consumed_owner_metadata() != self._structural_metadata:
            _fail(
                "consumed_keyed_i64_owner_metadata_drift",
                "consumed_owner",
                "prepared owner structural facts changed",
            )

    def validate_for_program(self, program: OptixKeyedI64SumProgram3D) -> None:
        self._validate_for_program(program)

    def take_backend_owner(
        self, program: OptixKeyedI64SumProgram3D
    ) -> PreparedOptixActionKeyedI64Sum3D:
        self._validate_for_program(program)
        owner = self._owner
        assert owner is not None
        self._owner = None
        self._consumed = True
        return owner

    def to_metadata(self) -> dict[str, object]:
        if not self._consumed:
            assert self._owner is not None
            self._validate_for_program(self._owner.program)
        return {
            "contract": self.contract,
            "identity_digest": self._identity_digest,
            "generation_sha256": self._generation_sha256,
            "structural_metadata": dict(self._structural_metadata),
            "compiler_owned": True,
            "single_use": True,
            "consumed": self._consumed,
            "host_payload_content_rehashed_for_persistent_identity": False,
            "backend_resource_prepared_before_issue": True,
        }

    def close(self) -> None:
        owner = self._owner
        if owner is None:
            return
        self._validate_close_binding(owner)
        if self._close_progress == 0:
            self._validate_for_program(owner.program)
        try:
            self._owner_close_method(owner)
        except Exception:
            if (
                getattr(owner, "_close_progress", None) == 1
                and isinstance(getattr(owner, "_close_seal", None), str)
                and hmac.compare_digest(
                    owner._close_seal,
                    PreparedOptixActionKeyedI64Sum3D._issue_close_seal(owner),
                )
            ):
                self._close_progress = 1
                self._close_seal = self._issue_close_seal()
            raise
        self._close_progress = 2
        self._close_seal = self._issue_close_seal()
        self._owner = None
        self._consumed = True

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def prepare_consumed_optix_action_keyed_i64_sum_3d(
    program: OptixKeyedI64SumProgram3D,
    triangles,
    *,
    primitive_group_ids: Sequence[int],
    primitive_values: Sequence[int],
    primitive_includes: Sequence[bool] | AllIncludedPrimitiveMask,
    group_count: int,
) -> ConsumedOptixActionKeyedI64Sum3D:
    """Synchronously prepare and seal one move-only compiler backend owner."""

    _validate_canonical_optix_keyed_i64_sum_program_3d(program)
    owner = prepare_optix_action_keyed_i64_sum_3d(
        program,
        triangles,
        primitive_group_ids=primitive_group_ids,
        primitive_values=primitive_values,
        primitive_includes=primitive_includes,
        group_count=group_count,
    )
    try:
        return ConsumedOptixActionKeyedI64Sum3D(owner)
    except Exception:
        owner.close()
        raise


def _extract_distance_window(
    origin: tuple[object, ...],
    distance_origin: tuple[object, ...],
) -> tuple[tuple[str, str], tuple[str, str]]:
    terms = _flatten_and(origin)
    minimum: tuple[str, str] | None = None
    maximum: tuple[str, str] | None = None
    for term in terms:
        if len(term) != 4 or term[0] != "compare":
            _fail("distance_window_compare_required", "filter", repr(term))
        predicate = str(term[1])
        left = term[2]
        right = term[3]
        if left == distance_origin and _is_parameter_origin(right):
            if predicate in {"gt", "ge"}:
                minimum = (str(right[1]), "open" if predicate == "gt" else "closed")
            elif predicate in {"lt", "le"}:
                maximum = (str(right[1]), "open" if predicate == "lt" else "closed")
            else:
                _fail("ordered_distance_compare_required", "filter", predicate)
        elif right == distance_origin and _is_parameter_origin(left):
            if predicate in {"lt", "le"}:
                minimum = (str(left[1]), "open" if predicate == "lt" else "closed")
            elif predicate in {"gt", "ge"}:
                maximum = (str(left[1]), "open" if predicate == "gt" else "closed")
            else:
                _fail("ordered_distance_compare_required", "filter", predicate)
        else:
            _fail(
                "distance_window_operand_mismatch",
                "filter",
                "each compare must relate the emitted distance to one parameter",
            )
    if minimum is None or maximum is None or len(terms) != 2:
        _fail(
            "two_sided_distance_window_required",
            "filter",
            "template v1 requires exactly one lower and one upper distance bound",
        )
    return minimum, maximum


def _flatten_and(origin: tuple[object, ...]) -> tuple[tuple[object, ...], ...]:
    if origin and origin[0] == "and":
        return _flatten_and(origin[1]) + _flatten_and(origin[2])
    return (origin,)


def _is_parameter_origin(origin: object) -> bool:
    return isinstance(origin, tuple) and len(origin) == 2 and origin[0] == "param"


def _is_event_origin(origin: object) -> bool:
    return isinstance(origin, tuple) and len(origin) == 2 and origin[0] == "event"


def _require_event_origin(origin: tuple[object, ...], path: str) -> str:
    if len(origin) != 2 or origin[0] != "event":
        _fail("direct_event_projection_required", f"emit.{path}", repr(origin))
    return str(origin[1])


def _require_nonnegative_integer(parameters: Mapping[str, object], name: str) -> int:
    value = parameters.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("nonnegative_integer_parameter_required", f"parameters.{name}", repr(value))
    return value


def _require_f32(parameters: Mapping[str, object], name: str) -> float:
    value = parameters.get(name)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        _fail("floating_parameter_required", f"parameters.{name}", repr(value))
    number = float(value)
    if not math.isfinite(number):
        _fail("finite_parameter_required", f"parameters.{name}", repr(value))
    try:
        return struct.unpack(">f", struct.pack(">f", number))[0]
    except OverflowError:
        _fail("f32_parameter_overflow", f"parameters.{name}", repr(value))


def _require_unique_u32_ids(packed: PackedPoints, path: str) -> None:
    ids = [int(packed.records[index].id) for index in range(packed.count)]
    if len(ids) != len(set(ids)):
        _fail("duplicate_stable_id", path, "point IDs must be unique")
    if any(value < 0 or value > 0xFFFFFFFF for value in ids):
        _fail("stable_id_out_of_u32_range", path, "point IDs must fit uint32")


def _require_unique_aabb_u32_ids(packed: PackedAabbs2D, path: str) -> None:
    ids = [int(packed.records[index].id) for index in range(packed.count)]
    if len(ids) != len(set(ids)):
        _fail("duplicate_stable_id", path, "AABB IDs must be unique")
    if any(value < 0 or value > 0xFFFFFFFF for value in ids):
        _fail("stable_id_out_of_u32_range", path, "AABB IDs must fit uint32")


def _boundary_mode(boundary: str) -> int:
    if boundary == "closed":
        return 0
    if boundary == "open":
        return 1
    raise AssertionError(boundary)


def _configure_action_aabb_optix_symbols(lib) -> None:
    prepare = getattr(lib, "rtdl_optix_prepare_action_aabb_candidates_2d", None)
    run = getattr(lib, "rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d", None)
    destroy = getattr(lib, "rtdl_optix_destroy_prepared_action_aabb_candidates_2d", None)
    if prepare is None or run is None or destroy is None:
        raise RuntimeError(
            "loaded OptiX backend does not export the private RTDL 3.0 AABB Action ABI"
        )
    prepare.restype = ctypes.c_int
    run.restype = ctypes.c_int
    run_v2 = getattr(
        lib, "rtdl_optix_run_prepared_action_aabb_filter_bounded_emit_2d_v2", None
    )
    if run_v2 is not None:
        run_v2.restype = ctypes.c_int
    destroy.argtypes = [ctypes.c_void_p]
    destroy.restype = None


def _fail(code: str, path: str, message: str):
    raise ActionOptixPlacementError(ActionOptixPlacementIssue(code, path, message))


__all__ = [
    "ActionOptixPlacementError",
    "ActionOptixPlacementIssue",
    "AllIncludedPrimitiveMask",
    "ConsumedOptixActionKeyedI64Sum3D",
    "OptixAabbFilterBoundedEmitProgram2D",
    "OptixBoundedSelectionProgram3D",
    "OptixKeyedI64SumProgram3D",
    "PreparedOptixActionAabbFilterBoundedEmit2D",
    "PreparedOptixActionBoundedSelection3D",
    "PreparedOptixActionKeyedI64Sum3D",
    "compile_optix_aabb_filter_bounded_emit_2d",
    "compile_optix_bounded_selection_3d",
    "compile_optix_keyed_i64_sum_3d",
    "all_included_primitive_mask",
    "prepare_optix_action_aabb_filter_bounded_emit_2d",
    "prepare_optix_action_bounded_selection_3d",
    "prepare_optix_action_keyed_i64_sum_3d",
    "prepare_consumed_optix_action_keyed_i64_sum_3d",
]
