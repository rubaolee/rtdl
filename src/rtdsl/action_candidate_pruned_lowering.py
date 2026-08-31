from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np

from .action_ir import ActionSpec
from .action_optix_lowering import compile_optix_bounded_selection_3d
from .embree_runtime import PackedPoints


CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_VERSION = (
    "rtdl.candidate_pruned_exact_bounded_selection_3d.v1"
)


@dataclass(frozen=True)
class CandidatePrunedExactBoundedSelectionProgram3D:
    spec: ActionSpec
    scope_output_field: str
    item_output_field: str
    distance_output_field: str
    minimum_parameter: str
    maximum_parameter: str
    limit_parameter: str
    minimum_boundary: str
    maximum_boundary: str
    delivery_proof_reference: str
    template_digest: str
    max_per_scope_limit: int

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_VERSION,
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": "candidate_pruned_exact_bounded_selection_3d",
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "bounded_emit"],
            "selection_scope": [self.scope_output_field],
            "selection_order": [
                self.distance_output_field,
                self.item_output_field,
            ],
            "scope_output_field": self.scope_output_field,
            "item_output_field": self.item_output_field,
            "distance_output_field": self.distance_output_field,
            "minimum_parameter": self.minimum_parameter,
            "maximum_parameter": self.maximum_parameter,
            "limit_parameter": self.limit_parameter,
            "minimum_boundary": self.minimum_boundary,
            "maximum_boundary": self.maximum_boundary,
            "delivery_proof_reference": self.delivery_proof_reference,
            "max_per_scope_limit": self.max_per_scope_limit,
            "physical_executor": (
                "prepared_grid_cell_lower_bound_exact_bounded_topk.v1"
            ),
            "unbounded_candidate_relation_materialized": False,
            "candidate_pruning_uses_verified_cell_lower_bounds": True,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "user_kernel_accepted": False,
            "user_ptx_accepted": False,
            "backend_program_name_accepted": False,
        }


def compile_candidate_pruned_exact_bounded_selection_3d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> CandidatePrunedExactBoundedSelectionProgram3D:
    verified = compile_optix_bounded_selection_3d(
        spec,
        discharged_delivery_proofs=discharged_delivery_proofs,
    )
    return CandidatePrunedExactBoundedSelectionProgram3D(
        spec=verified.spec,
        scope_output_field=verified.scope_output_field,
        item_output_field=verified.item_output_field,
        distance_output_field=verified.distance_output_field,
        minimum_parameter=verified.minimum_parameter,
        maximum_parameter=verified.maximum_parameter,
        limit_parameter=verified.limit_parameter,
        minimum_boundary=verified.minimum_boundary,
        maximum_boundary=verified.maximum_boundary,
        delivery_proof_reference=verified.delivery_proof_reference,
        template_digest=verified.template_digest,
        max_per_scope_limit=verified.max_per_scope_limit,
    )


def candidate_pruned_grid_shape(target_count: int) -> tuple[int, int, int]:
    """Compiler physical rule frozen before the formal Goal5653 endpoint."""

    if (
        not isinstance(target_count, int)
        or isinstance(target_count, bool)
        or target_count <= 0
        or target_count > (1 << 32) - 1
    ):
        raise ValueError("candidate-pruned target_count must fit positive U32")
    edge = 64 if target_count >= 1_000_000 else 32
    return (edge, edge, edge)


def _packed_point_columns(
    packed: PackedPoints,
) -> tuple[np.ndarray, np.ndarray]:
    if type(packed) is not PackedPoints or packed.dimension != 3:
        raise TypeError(
            "candidate-pruned preparation requires exact PackedPoints[3D]"
        )
    owner = packed.owner
    if (
        owner is not None
        and getattr(owner, "dtype", None) is not None
        and owner.dtype.names is not None
        and {"id", "x", "y", "z"}.issubset(owner.dtype.names)
    ):
        points = np.empty((packed.count, 3), dtype=np.float64)
        points[:, 0] = owner["x"]
        points[:, 1] = owner["y"]
        points[:, 2] = owner["z"]
        ids = np.ascontiguousarray(owner["id"], dtype=np.int64)
    else:
        points = np.empty((packed.count, 3), dtype=np.float64)
        ids = np.empty(packed.count, dtype=np.int64)
        for index in range(packed.count):
            record = packed.records[index]
            points[index] = (record.x, record.y, record.z)
            ids[index] = int(record.id)
    return points, ids


class PreparedCandidatePrunedExactBoundedSelection3D:
    prepared_producer_kind = "candidate_pruned_exact_bounded_selection_3d.v1"

    def __init__(
        self,
        program: CandidatePrunedExactBoundedSelectionProgram3D,
        search_points: PackedPoints,
        *,
        expected_native_library_identity=None,
        expected_native_library_ref=None,
    ) -> None:
        from .action_nearest_state_lowering import (
            certify_immutable_point_column_domain_3d,
        )
        from .optix_runtime import (
            PreparedCertifiedNearestGlobalWitness3DCuda,
        )

        started = time.perf_counter()
        points, ids = _packed_point_columns(search_points)
        certificate = certify_immutable_point_column_domain_3d(
            points,
            ids,
        )
        self._certificate_seconds = time.perf_counter() - started
        self._program = program
        self._certificate = certificate
        self._grid_shape = candidate_pruned_grid_shape(search_points.count)
        self._native_owner = PreparedCertifiedNearestGlobalWitness3DCuda(
            certificate.target_points,
            target_ids=certificate.target_ids,
            column_domain_certificate=certificate,
            grid_shape=self._grid_shape,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
        )
        self._closed = False

    def run(
        self,
        query_points,
        parameters: dict[str, object],
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("candidate-pruned prepared owner is closed")
        program = self._program
        result = self._native_owner.run_exact_bounded_selection(
            query_points,
            minimum_distance=float(parameters[program.minimum_parameter]),
            maximum_distance=float(parameters[program.maximum_parameter]),
            limit=int(parameters[program.limit_parameter]),
            minimum_boundary=program.minimum_boundary,
            maximum_boundary=program.maximum_boundary,
        )
        columns = result["columns"]
        # The admitted Action template requires the selected distance field to
        # be F32 (compile_optix_bounded_selection_3d rejects every other
        # type).  The reusable CUDA owner evaluates/prunes in F64 internally,
        # but its generic native ABI returns an F64 host column.  Materialize
        # the verified IR type here at the compiler boundary; returning the
        # owner column directly would violate the typed Action result ABI and
        # makes strict application front doors fail closed.
        distance_column = np.ascontiguousarray(
            columns["distance"],
            dtype=np.float32,
        )
        return {
            "columns": {
                program.scope_output_field: columns["scope_id"],
                program.item_output_field: columns["item_id"],
                program.distance_output_field: distance_column,
            },
            "metadata": dict(result["metadata"])
            | {
                "compiler_template": (
                    "candidate_pruned_exact_bounded_selection_3d"
                ),
                "semantic_digest": program.spec.semantic_digest,
                "template_digest": program.template_digest,
                "rank_certificate_validated": True,
                "column_fields_derived_from_verified_ir": True,
                "distance_output_type": "f32",
                "distance_output_materialized_from_verified_ir": True,
                "certificate_seconds": self._certificate_seconds,
                "grid_shape_rule": (
                    "edge_64_when_target_count_ge_1m_else_edge_32"
                ),
            },
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": (
                "rtdl.prepared_candidate_pruned_exact_bounded_selection_3d.v1"
            ),
            "program": self._program.to_metadata(),
            "grid_shape": self._grid_shape,
            "grid_shape_rule": "edge_64_when_target_count_ge_1m_else_edge_32",
            "certificate_seconds": self._certificate_seconds,
            "native_owner": self._native_owner.to_metadata(),
            "closed": self._closed,
        }

    def close(self) -> None:
        if self._closed:
            return
        self._native_owner.close()
        self._closed = True


def prepare_candidate_pruned_exact_bounded_selection_3d(
    program: CandidatePrunedExactBoundedSelectionProgram3D,
    search_points: PackedPoints,
    *,
    expected_native_library_identity=None,
    expected_native_library_ref=None,
) -> PreparedCandidatePrunedExactBoundedSelection3D:
    return PreparedCandidatePrunedExactBoundedSelection3D(
        program,
        search_points,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
    )


__all__ = (
    "CANDIDATE_PRUNED_EXACT_BOUNDED_SELECTION_3D_VERSION",
    "CandidatePrunedExactBoundedSelectionProgram3D",
    "PreparedCandidatePrunedExactBoundedSelection3D",
    "candidate_pruned_grid_shape",
    "compile_candidate_pruned_exact_bounded_selection_3d",
    "prepare_candidate_pruned_exact_bounded_selection_3d",
)
