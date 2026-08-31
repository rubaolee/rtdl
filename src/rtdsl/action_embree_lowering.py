from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from typing import Mapping, NoReturn

import numpy as np

from .action_ir import (
    ActionEffect,
    ActionOp,
    ActionSpec,
    ActionStaticLoop,
    CapacityParam,
    DeliveryEnforcement,
    F32,
    OutputOrderKind,
    PhysicalDelivery,
    U32,
    verify_action_spec,
)
from .embree_runtime import prepare_embree_aabb_index_2d


@dataclass(frozen=True)
class ActionEmbreePlacementIssue:
    code: str
    path: str
    message: str


class ActionEmbreePlacementError(ValueError):
    def __init__(self, issue: ActionEmbreePlacementIssue) -> None:
        self.issue = issue
        super().__init__(
            f"Action Embree placement failed: {issue.code}@{issue.path}: {issue.message}"
        )


@dataclass(frozen=True)
class EmbreeAabbFilterBoundedEmitProgram2D:
    spec: ActionSpec
    query_event_field: str
    item_event_field: str
    overlap_event_field: str
    minimum_overlap_parameter: str
    capacity_parameter: str
    delivery_proof_reference: str
    template_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "verified_action_embree_aabb_filter_reference_2d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": "aabb_overlap_candidate_2d_filter_bounded_emit_reference_v1",
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "bounded_emit"],
            "event_source_contract": "aabb_overlap_candidate_2d.v1",
            "filter": {
                "event_field": self.overlap_event_field,
                "predicate": "gt",
                "parameter": self.minimum_overlap_parameter,
            },
            "delivery_proof_reference": self.delivery_proof_reference,
            "placement_kind": "host_continuation_after_native_candidate_collection",
            "traversal_fused": False,
            "candidate_rows_materialized": True,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "backend_program_name_accepted": False,
        }

    def resource_plan(
        self,
        parameters: Mapping[str, object],
        *,
        indexed_count: int,
        query_count: int,
        max_candidate_rows: int,
    ) -> dict[str, object]:
        output_capacity = _require_nonnegative_integer(
            parameters, self.capacity_parameter
        )
        if min(indexed_count, query_count, max_candidate_rows) < 0:
            _fail("negative_resource_extent", "resource_plan", "negative count")
        candidate_capacity = indexed_count * query_count
        if candidate_capacity > max_candidate_rows:
            _fail(
                "embree_candidate_capacity_exceeded",
                "resource_plan.candidate_rows",
                f"required {candidate_capacity}, allowed {max_candidate_rows}",
            )
        return {
            "indexed_count": indexed_count,
            "query_count": query_count,
            "candidate_relation_capacity_rows": candidate_capacity,
            "bounded_output_capacity_rows": output_capacity,
            "candidate_row_bytes": candidate_capacity * 8,
            "bounded_output_capacity_bytes": output_capacity * 8,
            "candidate_rows_materialized": True,
            "unbounded_candidate_relation_materialized": False,
            "overflow_policy": "fail_closed",
        }


def compile_embree_aabb_filter_bounded_emit_reference_2d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> EmbreeAabbFilterBoundedEmitProgram2D:
    """Recognize one read-only AABB filter/emit shape without app-name dispatch."""

    verified = verify_action_spec(spec)
    if set(verified.inferred_effects) != {
        ActionEffect.FILTER,
        ActionEffect.BOUNDED_EMIT,
    }:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "Embree reference template requires filter plus bounded_emit",
        )
    if spec.states or spec.reductions or spec.termination_proofs:
        _fail(
            "effect_subset_not_supported",
            "spec",
            "state, reduce, and terminate are not supported",
        )
    if (
        spec.logical_event.physical_delivery is not PhysicalDelivery.PROVEN_SINGLE
        or spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE
    ):
        _fail(
            "single_delivery_not_discharged",
            "logical_event",
            "the prepared AABB event source requires proven-single delivery",
        )
    proof = spec.logical_event.proof_reference
    if not proof or proof not in discharged_delivery_proofs:
        _fail(
            "delivery_proof_not_discharged",
            "logical_event.proof_reference",
            "an externally discharged placement proof is required",
        )
    if len(spec.blocks) != 1 or any(
        isinstance(statement, ActionStaticLoop)
        for statement in spec.blocks[0].operations
    ):
        _fail("straight_line_block_required", "blocks", "template v1 is straight-line")
    if len(spec.emits) != 1:
        _fail("single_emit_required", "emits", "template v1 requires one emit")
    emit = spec.emits[0]
    if emit.selection is not None:
        _fail("plain_bounded_emit_required", "emits[0].selection", "selection is absent")
    if not isinstance(emit.capacity, CapacityParam):
        _fail(
            "dynamic_capacity_parameter_required",
            "emits[0].capacity",
            "a checked output-capacity parameter is required",
        )
    if emit.order_kind is not OutputOrderKind.CANONICAL_ORDER:
        _fail(
            "canonical_output_order_required",
            "emits[0].order_kind",
            emit.order_kind.value,
        )
    if len(emit.record_type.fields) != 2 or len(emit.order_keys) != 2:
        _fail(
            "canonical_pair_output_required",
            "emits[0]",
            "two canonically ordered identifiers are required",
        )
    if any(field.value_type != U32 for field in emit.record_type.fields):
        _fail("u32_pair_output_required", "emits[0].record_type", "non-u32 field")
    if tuple(key.field for key in emit.order_keys) != tuple(
        field.name for field in emit.record_type.fields
    ):
        _fail(
            "canonical_pair_order_mismatch",
            "emits[0].order_keys",
            "order keys must cover the emitted pair",
        )

    origins: dict[str, tuple[object, ...]] = {}
    emit_inputs: tuple[str, ...] | None = None
    filter_origin: tuple[object, ...] | None = None
    for index, statement in enumerate(spec.blocks[0].operations):
        assert isinstance(statement, ActionOp)
        path = f"blocks[0].operations[{index}]"
        if statement.opcode == "load_event":
            origins[statement.outputs[0].name] = (
                "event",
                str(statement.attribute("field")),
            )
        elif statement.opcode == "load_param":
            origins[statement.outputs[0].name] = (
                "param",
                str(statement.attribute("field")),
            )
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
            _fail("opcode_not_supported_by_embree_template", path, statement.opcode)
    if emit_inputs is None or filter_origin is None:
        _fail("filter_and_emit_required", "blocks[0]", "missing filter or emit")

    output_origins = {
        field.name: origins[input_name]
        for field, input_name in zip(
            emit.record_type.fields, emit_inputs, strict=True
        )
    }
    query_output, item_output = (field.name for field in emit.record_type.fields)
    query_origin = _require_event_origin(output_origins[query_output], query_output)
    item_origin = _require_event_origin(output_origins[item_output], item_output)
    if set(spec.logical_event.key_fields) != {query_origin, item_origin}:
        _fail(
            "logical_event_identity_mismatch",
            "logical_event.key_fields",
            "pair identity must be exactly the emitted identifiers",
        )
    if len(filter_origin) != 4 or filter_origin[0] != "compare":
        _fail("scalar_overlap_compare_required", "filter", repr(filter_origin))
    predicate = str(filter_origin[1])
    left, right = filter_origin[2], filter_origin[3]
    if predicate == "gt" and _is_event_origin(left) and _is_parameter_origin(right):
        overlap_origin, threshold_origin = left, right
    elif predicate == "lt" and _is_parameter_origin(left) and _is_event_origin(right):
        overlap_origin, threshold_origin = right, left
    else:
        _fail(
            "strict_overlap_filter_required",
            "filter",
            "template v1 requires event_f32 > parameter_f32",
        )
    overlap_field = str(overlap_origin[1])
    overlap_type = spec.event_type.field(overlap_field)
    if overlap_type is None or overlap_type.value_type != F32:
        _fail("f32_overlap_event_required", "event_type", overlap_field)
    threshold_parameter = str(threshold_origin[1])
    descriptor = {
        "template_kind": "aabb_overlap_candidate_2d_filter_bounded_emit_reference_v1",
        "semantic_digest": spec.semantic_digest,
        "query_event_field": query_origin,
        "item_event_field": item_origin,
        "overlap_event_field": overlap_field,
        "minimum_overlap_parameter": threshold_parameter,
        "capacity_parameter": emit.capacity.name,
    }
    digest = hashlib.sha256(
        repr(sorted(descriptor.items())).encode("utf-8")
    ).hexdigest()
    return EmbreeAabbFilterBoundedEmitProgram2D(
        spec=spec,
        query_event_field=query_origin,
        item_event_field=item_origin,
        overlap_event_field=overlap_field,
        minimum_overlap_parameter=threshold_parameter,
        capacity_parameter=emit.capacity.name,
        delivery_proof_reference=proof,
        template_digest=digest,
    )


class PreparedEmbreeActionAabbFilterBoundedEmit2D:
    def __init__(
        self,
        program: EmbreeAabbFilterBoundedEmitProgram2D,
        indexed_boxes,
        *,
        max_candidate_rows: int,
    ) -> None:
        indexed = tuple(_normalize_box(box, "indexed_boxes") for box in indexed_boxes)
        if not indexed:
            raise ValueError("Embree Action AABB source requires at least one indexed box")
        if len({box[0] for box in indexed}) != len(indexed):
            raise ValueError("indexed_boxes IDs must be unique")
        if not isinstance(max_candidate_rows, int) or isinstance(max_candidate_rows, bool):
            raise TypeError("max_candidate_rows must be an integer")
        if max_candidate_rows < 0:
            raise ValueError("max_candidate_rows must be non-negative")
        self.program = program
        self._indexed = indexed
        self._indexed_by_id = {box[0]: box for box in indexed}
        self._max_candidate_rows = max_candidate_rows
        self._prepared = prepare_embree_aabb_index_2d(indexed_boxes)
        self._closed = False

    def run(self, query_boxes, parameters: Mapping[str, object]) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared Action Embree handle is closed")
        queries = tuple(_normalize_box(box, "query_boxes") for box in query_boxes)
        if len({box[0] for box in queries}) != len(queries):
            raise ValueError("query_boxes IDs must be unique")
        resource = self.program.resource_plan(
            parameters,
            indexed_count=len(self._indexed),
            query_count=len(queries),
            max_candidate_rows=self._max_candidate_rows,
        )
        threshold = _require_f32(parameters, self.program.minimum_overlap_parameter)
        if threshold < 0.0:
            _fail(
                "negative_overlap_threshold",
                f"parameters.{self.program.minimum_overlap_parameter}",
                str(threshold),
            )
        query_by_id = {box[0]: box for box in queries}
        native = self._prepared.collect_range_intersection_rows(query_boxes)
        rows = []
        for query_id, indexed_id in native["candidate_id_rows"]:
            query = query_by_id[int(query_id)]
            indexed = self._indexed_by_id[int(indexed_id)]
            overlap_x = max(0.0, min(query[3], indexed[3]) - max(query[1], indexed[1]))
            overlap_y = max(0.0, min(query[4], indexed[4]) - max(query[2], indexed[2]))
            overlap_area = float(np.float32(overlap_x * overlap_y))
            if overlap_area > threshold:
                rows.append((int(query_id), int(indexed_id)))
        rows.sort()
        output_capacity = int(resource["bounded_output_capacity_rows"])
        if len(rows) > output_capacity:
            _fail(
                "bounded_emit_capacity_overflow",
                "embree.rows",
                f"observed {len(rows)} rows for capacity {output_capacity}",
            )
        return {
            "rows": tuple(rows),
            "metadata": self.program.to_metadata()
            | resource
            | {
                "native_symbol": native["native_generic_symbol"],
                "native_candidate_row_count": len(native["candidate_id_rows"]),
                "emitted_row_count": len(rows),
                "native_candidate_collection": True,
                "strict_filter_location": "compiler_owned_host_continuation",
                "prepared_index_reused": True,
                "rt_core_accelerated": False,
                "user_callback_executed": False,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        self._prepared.close()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_embree_action_aabb_filter_bounded_emit_2d(
    program: EmbreeAabbFilterBoundedEmitProgram2D,
    indexed_boxes,
    *,
    max_candidate_rows: int,
) -> PreparedEmbreeActionAabbFilterBoundedEmit2D:
    return PreparedEmbreeActionAabbFilterBoundedEmit2D(
        program,
        indexed_boxes,
        max_candidate_rows=max_candidate_rows,
    )


def _normalize_box(box, path: str) -> tuple[int, float, float, float, float]:
    try:
        values = (
            int(getattr(box, "id")),
            float(getattr(box, "min_x")),
            float(getattr(box, "min_y")),
            float(getattr(box, "max_x")),
            float(getattr(box, "max_y")),
        )
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError(f"{path} requires id/min_x/min_y/max_x/max_y fields") from exc
    if values[0] < 0 or values[0] > 0xFFFFFFFF:
        raise ValueError(f"{path} ID must fit uint32")
    if not all(math.isfinite(value) for value in values[1:]):
        raise ValueError(f"{path} coordinates must be finite")
    if values[3] < values[1] or values[4] < values[2]:
        raise ValueError(f"{path} bounds are inverted")
    return values


def _is_parameter_origin(origin: object) -> bool:
    return isinstance(origin, tuple) and len(origin) == 2 and origin[0] == "param"


def _is_event_origin(origin: object) -> bool:
    return isinstance(origin, tuple) and len(origin) == 2 and origin[0] == "event"


def _require_event_origin(origin: tuple[object, ...], path: str) -> str:
    if not _is_event_origin(origin):
        _fail("direct_event_output_required", path, repr(origin))
    return str(origin[1])


def _require_nonnegative_integer(parameters: Mapping[str, object], name: str) -> int:
    value = parameters.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("nonnegative_integer_parameter_required", f"parameters.{name}", repr(value))
    return value


def _require_f32(parameters: Mapping[str, object], name: str) -> float:
    value = parameters.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail("numeric_parameter_required", f"parameters.{name}", repr(value))
    normalized = float(np.float32(value))
    if not math.isfinite(normalized):
        _fail("finite_f32_parameter_required", f"parameters.{name}", repr(value))
    return normalized


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionEmbreePlacementError(ActionEmbreePlacementIssue(code, path, message))


__all__ = [
    "ActionEmbreePlacementError",
    "EmbreeAabbFilterBoundedEmitProgram2D",
    "PreparedEmbreeActionAabbFilterBoundedEmit2D",
    "compile_embree_aabb_filter_bounded_emit_reference_2d",
    "prepare_embree_action_aabb_filter_bounded_emit_2d",
]
