from __future__ import annotations

from dataclasses import dataclass

from .action_ir import ActionSpec
from .action_optix_lowering import compile_optix_bounded_selection_3d


@dataclass(frozen=True)
class RankedDistanceWindowQkProgram3D:
    """Verified bounded-selection semantics for the prepared Q*K executor."""

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
            "contract": "verified_action_prepared_ranked_distance_window_qk_3d.v1",
            "semantic_digest": self.spec.semantic_digest,
            "template_kind": "prepared_ranked_distance_window_qk_3d",
            "template_digest": self.template_digest,
            "effect_subset": ["filter", "bounded_emit"],
            "selection_scope": [self.scope_output_field],
            "selection_order": [self.distance_output_field, self.item_output_field],
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
            "physical_executor": "prepared_spatial_ranked_distance_window_qk.v1",
            "unbounded_candidate_relation_materialized": False,
            "action_name_used_for_dispatch": False,
            "app_identity_used_for_dispatch": False,
            "user_callback_accepted": False,
            "user_kernel_accepted": False,
            "user_ptx_accepted": False,
            "backend_program_name_accepted": False,
        }


def compile_ranked_distance_window_qk_3d(
    spec: ActionSpec,
    *,
    discharged_delivery_proofs: frozenset[str] = frozenset(),
) -> RankedDistanceWindowQkProgram3D:
    """Reuse the verified filter/top-K shape without exposing a raw kernel."""

    verified = compile_optix_bounded_selection_3d(
        spec,
        discharged_delivery_proofs=discharged_delivery_proofs,
    )
    return RankedDistanceWindowQkProgram3D(
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


__all__ = (
    "RankedDistanceWindowQkProgram3D",
    "compile_ranked_distance_window_qk_3d",
)
