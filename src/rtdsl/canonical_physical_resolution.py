"""App-neutral canonical physical-provider resolution.

The application owns an explicit algorithm statement.  This module does not
choose that algorithm and does not optimize over alternatives.  It authenticates
the statement, backend contract, closed provider table and current candidate
registry, then resolves exactly one provider or fails closed.

An OptiX provider in a successful receipt is a static plan identity.  It is not
evidence that ``optixLaunch`` executed; the separate behavioral traversal
receipt remains authoritative for that fact.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from .default_physical_selection import (
    OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
    ActionSelectionDescriptor,
    CandidateDescriptor,
    RegistrySnapshot,
    TargetSelectionDescriptor,
    candidate_descriptor_sha256,
    candidate_legality_reasons,
    current_registry_snapshot,
    make_action_descriptor,
    make_target_descriptor,
    materialize_candidates,
)


CANONICAL_RESOLUTION_POLICY_VERSION = "rtdl.canonical_physical_resolution.goal5729.v1"
CANONICAL_RESOLUTION_RECEIPT_SCHEMA = "rtdl.canonical_physical_resolution.receipt.v1"
CANONICAL_REGISTRY_VERSION = "rtdl.canonical_physical_provider_registry.goal5729.v1"
CANONICAL_PRODUCTION_AUTHORITY_SCHEMA = (
    "rtdl.canonical_physical_resolution.production_authority.v1"
)


class CanonicalPhysicalResolutionError(RuntimeError):
    """Typed fail-closed canonical-resolution error."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = str(code)
        self.detail = str(detail)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        raise CanonicalPhysicalResolutionError("INVALID_SHA256", field)
    try:
        int(value, 16)
    except ValueError as exc:
        raise CanonicalPhysicalResolutionError("INVALID_SHA256", field) from exc
    return value


@dataclass(frozen=True)
class SemanticAlgorithmStatement:
    stable_id: str
    semantic_kind: str
    action_contract_class: str
    algorithm_contract: str
    typed_effect_contract: str
    output_semantics: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (
                self.stable_id,
                self.semantic_kind,
                self.action_contract_class,
                self.algorithm_contract,
                self.typed_effect_contract,
                self.output_semantics,
            )
        ):
            raise CanonicalPhysicalResolutionError("EMPTY_STATEMENT_FIELD", self.stable_id)
        forbidden = ("paper", "author", "dataset", "benchmark", "rayjoin", "x_hd", "rtnn")
        lowered = _canonical_bytes(self.as_dict()).decode("ascii").lower()
        if any(token in lowered for token in forbidden):
            raise CanonicalPhysicalResolutionError(
                "APPLICATION_OR_PUBLICATION_IDENTITY_IN_STATEMENT", self.stable_id
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "stable_id": self.stable_id,
            "semantic_kind": self.semantic_kind,
            "action_contract_class": self.action_contract_class,
            "algorithm_contract": self.algorithm_contract,
            "typed_effect_contract": self.typed_effect_contract,
            "output_semantics": self.output_semantics,
        }

    @property
    def digest(self) -> str:
        return _digest(self.as_dict())


@dataclass(frozen=True)
class BackendContract:
    stable_id: str
    required_providers: tuple[str, ...]
    allowed_execution_classes: tuple[str, ...]
    required_physical_capabilities: tuple[str, ...]
    behavioral_proof_required_for_execution_claim: bool

    def __post_init__(self) -> None:
        if not self.stable_id:
            raise CanonicalPhysicalResolutionError("EMPTY_BACKEND_CONTRACT_ID")
        for field, values in (
            ("required_providers", self.required_providers),
            ("allowed_execution_classes", self.allowed_execution_classes),
            ("required_physical_capabilities", self.required_physical_capabilities),
        ):
            if tuple(sorted(set(values))) != values:
                raise CanonicalPhysicalResolutionError(
                    "NONCANONICAL_BACKEND_CONTRACT_SET", f"{self.stable_id}.{field}"
                )

    def as_dict(self) -> dict[str, object]:
        return {
            "stable_id": self.stable_id,
            "required_providers": list(self.required_providers),
            "allowed_execution_classes": list(self.allowed_execution_classes),
            "required_physical_capabilities": list(self.required_physical_capabilities),
            "behavioral_proof_required_for_execution_claim": (
                self.behavioral_proof_required_for_execution_claim
            ),
        }

    @property
    def digest(self) -> str:
        return _digest(self.as_dict())


@dataclass(frozen=True)
class CanonicalProviderBinding:
    statement_stable_id: str
    backend_contract_id: str
    candidate_stable_id: str
    algorithm_preserving: bool
    compatibility_fallback: bool
    provider_namespace: str = "legacy_candidate"

    def __post_init__(self) -> None:
        if not self.statement_stable_id or not self.backend_contract_id or not self.candidate_stable_id:
            raise CanonicalPhysicalResolutionError("EMPTY_PROVIDER_BINDING_FIELD")
        if self.provider_namespace not in {"legacy_candidate", "standalone_provider"}:
            raise CanonicalPhysicalResolutionError(
                "UNKNOWN_PROVIDER_NAMESPACE", self.provider_namespace
            )
        if self.compatibility_fallback and self.algorithm_preserving:
            raise CanonicalPhysicalResolutionError(
                "REFERENCE_FALLBACK_CANNOT_CLAIM_ALGORITHM_PRESERVATION",
                self.candidate_stable_id,
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "statement_stable_id": self.statement_stable_id,
            "backend_contract_id": self.backend_contract_id,
            "candidate_stable_id": self.candidate_stable_id,
            "algorithm_preserving": self.algorithm_preserving,
            "compatibility_fallback": self.compatibility_fallback,
            "provider_namespace": self.provider_namespace,
        }


@dataclass(frozen=True)
class StandaloneProviderDeclaration:
    """Source-bound canonical provider outside the retiring legacy registry."""

    stable_id: str
    semantic_kind: str
    accepted_action_contract_class: str
    template: str
    provider_class: str
    required_providers: tuple[str, ...]
    execution_class: str
    physical_capabilities: tuple[str, ...]
    provider_abi_requirement_digest: str
    proof_digest: str
    resource_bound_digest: str
    reuse_contract_digest: str
    template_digest: str
    source_path: str
    source_sha256: str
    source_anchor: str
    memory_base_bytes: int
    memory_output_multiplier: int
    compatibility_fallback: bool

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value
            for value in (
                self.stable_id,
                self.semantic_kind,
                self.accepted_action_contract_class,
                self.template,
                self.provider_class,
                self.source_path,
                self.source_sha256,
                self.source_anchor,
            )
        ):
            raise CanonicalPhysicalResolutionError(
                "EMPTY_STANDALONE_PROVIDER_FIELD", self.stable_id
            )
        for field in (
            "provider_abi_requirement_digest",
            "proof_digest",
            "resource_bound_digest",
            "reuse_contract_digest",
            "template_digest",
            "source_sha256",
        ):
            _require_sha256(getattr(self, field), field=f"{self.stable_id}.{field}")
        for field in ("required_providers", "physical_capabilities"):
            values = getattr(self, field)
            if tuple(sorted(set(values))) != values:
                raise CanonicalPhysicalResolutionError(
                    "NONCANONICAL_STANDALONE_PROVIDER_SET",
                    f"{self.stable_id}.{field}",
                )
        if self.memory_base_bytes < 0 or self.memory_output_multiplier < 0:
            raise CanonicalPhysicalResolutionError(
                "INVALID_STANDALONE_MEMORY_BOUND", self.stable_id
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "stable_id": self.stable_id,
            "semantic_kind": self.semantic_kind,
            "accepted_action_contract_class": self.accepted_action_contract_class,
            "template": self.template,
            "provider_class": self.provider_class,
            "required_providers": list(self.required_providers),
            "execution_class": self.execution_class,
            "physical_capabilities": list(self.physical_capabilities),
            "provider_abi_requirement_digest": self.provider_abi_requirement_digest,
            "proof_digest": self.proof_digest,
            "resource_bound_digest": self.resource_bound_digest,
            "reuse_contract_digest": self.reuse_contract_digest,
            "template_digest": self.template_digest,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_anchor": self.source_anchor,
            "memory_base_bytes": self.memory_base_bytes,
            "memory_output_multiplier": self.memory_output_multiplier,
            "compatibility_fallback": self.compatibility_fallback,
            "exactness_verified": True,
            "determinism_verified": True,
            "ordering_verified": True,
            "normal_default_eligible": True,
        }

    def descriptor(self, action: ActionSelectionDescriptor) -> dict[str, object]:
        result = self.as_dict()
        result.update(
            {
                "action_digest": action.action_digest,
                "output_contract_digest": action.output_contract_digest,
                "work_domain_digest": action.work_domain_digest,
                "conservative_memory_bytes": (
                    self.memory_base_bytes
                    + self.memory_output_multiplier * action.output_bytes
                ),
            }
        )
        return result


@dataclass(frozen=True)
class CanonicalProviderRegistry:
    version: str
    statements: tuple[SemanticAlgorithmStatement, ...]
    backend_contracts: tuple[BackendContract, ...]
    standalone_providers: tuple[StandaloneProviderDeclaration, ...]
    bindings: tuple[CanonicalProviderBinding, ...]
    candidate_registry_sha256: str

    def __post_init__(self) -> None:
        _require_sha256(self.candidate_registry_sha256, field="candidate_registry_sha256")
        for field, values, key in (
            ("statements", self.statements, lambda row: row.stable_id),
            ("backend_contracts", self.backend_contracts, lambda row: row.stable_id),
            ("standalone_providers", self.standalone_providers, lambda row: row.stable_id),
            (
                "bindings",
                self.bindings,
                lambda row: (
                    row.statement_stable_id,
                    row.backend_contract_id,
                    row.candidate_stable_id,
                ),
            ),
        ):
            identities = tuple(key(row) for row in values)
            if identities != tuple(sorted(identities)) or len(identities) != len(set(identities)):
                raise CanonicalPhysicalResolutionError(
                    "NONCANONICAL_OR_DUPLICATE_CANONICAL_REGISTRY", field
                )
        statement_ids = {row.stable_id for row in self.statements}
        backend_ids = {row.stable_id for row in self.backend_contracts}
        for binding in self.bindings:
            if binding.statement_stable_id not in statement_ids:
                raise CanonicalPhysicalResolutionError(
                    "BINDING_REFERENCES_UNKNOWN_STATEMENT", binding.statement_stable_id
                )
            if binding.backend_contract_id not in backend_ids:
                raise CanonicalPhysicalResolutionError(
                    "BINDING_REFERENCES_UNKNOWN_BACKEND", binding.backend_contract_id
                )

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "statements": [row.as_dict() for row in self.statements],
            "backend_contracts": [row.as_dict() for row in self.backend_contracts],
            "standalone_providers": [row.as_dict() for row in self.standalone_providers],
            "bindings": [row.as_dict() for row in self.bindings],
            "candidate_registry_sha256": self.candidate_registry_sha256,
        }

    @property
    def digest(self) -> str:
        return _digest(self.as_dict())


def _statement(
    stable_id: str,
    semantic_kind: str,
    action_contract_class: str,
    algorithm_contract: str,
) -> SemanticAlgorithmStatement:
    return SemanticAlgorithmStatement(
        stable_id=stable_id,
        semantic_kind=semantic_kind,
        action_contract_class=action_contract_class,
        algorithm_contract=algorithm_contract,
        typed_effect_contract="restricted_typed_effect_graph__no_opaque_callback.v1",
        output_semantics=f"{semantic_kind}/{action_contract_class}/exact_canonical_output.v1",
    )


def _current_statements() -> tuple[SemanticAlgorithmStatement, ...]:
    rows = (
        _statement("aggregate_hierarchy.frontier_reduce.v1", "aggregate_hierarchy_continuation_reduce_3d", "frontier_reduce", "bounded_frontier_opening_then_exact_reduction"),
        _statement("aabb_index.prepared_query_2d.v1", "prepared_aabb_index_queries_2d.v1", "bounded_count_or_pair_rows", "prepared_aabb_index_query"),
        _statement("aabb_overlap.filter_bounded_emit_2d.v1", "prepared_aabb_overlap_candidates_2d.v1", "filter_bounded_emit", "prepared_aabb_filter_then_bounded_emit"),
        _statement("fixed_radius.complete_pair_components.v1", "fixed_radius_graph_components_3d.v1", "radius_components", "complete_pair_radius_graph_then_grouped_components"),
        _statement("fixed_radius.prepared_spatial_components.v1", "fixed_radius_graph_components_3d.v1", "radius_components", "prepared_spatial_radius_graph_then_grouped_components"),
        _statement("logical_events.filter_bounded_emit.v1", "verified_logical_event_columns.v1", "filter_bounded_emit", "verified_filter_then_bounded_emit"),
        _statement("logical_events.grouped_i64x2_count_sum.v1", "verified_logical_event_columns.v1", "grouped_i64x2_count_sum", "verified_grouped_i64x2_count_and_sum"),
        _statement("metric_knn.filter_refine_euclidean_3d.v1", "metric_knn_euclidean_filter_refine_3d.v1", "metric_knn_complete_topk_3d", "inclusive_aabb_candidates_then_exact_euclidean_topk_with_bounded_radius_completion"),
        _statement("metric_knn.filter_refine_linf_3d.v1", "metric_knn_linf_filter_refine_3d.v1", "metric_knn_complete_topk_3d", "inclusive_aabb_candidates_then_exact_linf_topk_with_bounded_radius_completion"),
        _statement("metric_knn.monotone_cosine_3d.v1", "metric_knn_cosine_monotone_transform_3d.v1", "metric_knn_complete_topk_3d", "verified_unit_normalization_then_euclidean_aabb_candidates_and_exact_cosine_topk_with_bounded_radius_completion"),
        _statement("nearest_state.cell_mbr_exact_witness.v1", "certified_nearest_state_3d.v1", "exact_witness", "cell_mbr_frontier_then_exact_witness"),
        _statement("nearest_state.frontier_seeded_exact.v1", "certified_nearest_state_3d.v1", "exact_witness", "certified_frontier_seed_then_exact_state"),
        _statement("point_selection.candidate_pruned_grid.v1", "prepared_point_candidates_3d.v1", "bounded_selection_3d", "candidate_pruned_grid_exact_bounded_selection"),
        _statement("point_selection.ranked_window_qk.v1", "prepared_point_candidates_3d.v1", "bounded_selection_3d", "ranked_distance_window_qk"),
        _statement("point_selection.spatial_bounded.v1", "prepared_point_candidates_3d.v1", "bounded_selection_3d", "prepared_spatial_bounded_selection"),
        _statement("planar_map.directed_segment_point_location_2d.v1", "directed_segment_point_location_2d.v1", "verified_planar_map_producer", "directed_segment_point_location"),
        _statement("planar_map.segment_first_hit_2d.v1", "segment_first_hit_2d.v1", "verified_planar_map_producer", "segment_first_hit"),
        _statement("planar_map.segment_pair_grouped_range_exact_count_2d.v1", "segment_pair_grouped_range_direct_intersection_exact_count_2d.v1", "verified_planar_map_producer", "segment_pair_grouped_range_direct_intersection_exact_count"),
        _statement("query_min_state.complete_grouped_distance.v1", "complete_query_grouped_distance_rows.v1", "certified_query_min_state", "complete_grouped_distance_rows_then_exact_min_state"),
        _statement("ray_triangle_scalar.all_hit_count_value.v1", "ray_triangle_all_hit_count_value_3d.v1", "unkeyed_u64_scalar_sum", "one_all_hit_count_value_per_ray_then_u64_sum"),
        _statement("ray_triangle_scalar.any_hit_weighted_value.v1", "ray_triangle_any_hit_weighted_value_3d.v1", "unkeyed_u64_scalar_sum", "one_any_hit_weighted_value_per_ray_then_u64_sum"),
        _statement("ray_triangle.keyed_i64_sum.v1", "stable_ray_triangle_candidates_3d.v1", "keyed_i64_sum", "stable_ray_triangle_candidates_then_keyed_i64_sum"),
    )
    return tuple(sorted(rows, key=lambda row: row.stable_id))


def _current_backend_contracts() -> tuple[BackendContract, ...]:
    optix_cap = (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,)
    rows = (
        BackendContract("compat.embree_traversal.v1", ("embree",), ("embree_cpu",), (), True),
        BackendContract("host.partner.v1", ("python",), ("host",), (), False),
        BackendContract("host.reference.v1", ("python",), ("host",), (), False),
        BackendContract("numba.cpu_partner.v1", ("numba",), ("numba_cpu",), (), False),
        BackendContract("numba.cuda_partner.v1", ("numba",), ("cuda", "numba"), (), False),
        BackendContract("nvidia.cuda_compute.v1", ("cuda",), ("cuda",), (), False),
        BackendContract("nvidia.optix_numba_pipeline.v1", ("numba", "optix"), ("mixed_optix_numba",), optix_cap, True),
        BackendContract("nvidia.optix_traversal.v1", ("optix",), ("optix",), optix_cap, True),
    )
    return tuple(sorted(rows, key=lambda row: row.stable_id))


def _binding(statement: str, backend: str, candidate: str, *, reference: bool = False) -> CanonicalProviderBinding:
    return CanonicalProviderBinding(
        statement_stable_id=statement,
        backend_contract_id=backend,
        candidate_stable_id=candidate,
        algorithm_preserving=not reference,
        compatibility_fallback=reference,
    )


def _standalone_binding(
    statement: str,
    backend: str,
    provider: str,
    *,
    reference: bool = False,
) -> CanonicalProviderBinding:
    return CanonicalProviderBinding(
        statement_stable_id=statement,
        backend_contract_id=backend,
        candidate_stable_id=provider,
        algorithm_preserving=not reference,
        compatibility_fallback=reference,
        provider_namespace="standalone_provider",
    )


_SCALAR_SUMMARY_SOURCE_PATH = "src/rtdsl/action_ray_triangle_scalar_summary.py"
_SCALAR_SUMMARY_SOURCE_SHA256 = "92767727b31d1cfa1d49bd449cfa66964cd1dd1218ed5933c15cd2ef8fac3223"
_PLANAR_MAP_NATIVE_SOURCE_PATH = "src/native/optix/rtdl_optix_workloads.cpp"
_PLANAR_MAP_NATIVE_SOURCE_SHA256 = "961cfa0d3bf78ac9ad19920684722d5f29877de81f236241c04ee9638434743c"
_METRIC_KNN_SOURCE_PATH = "src/rtdsl/metric_knn.py"
_METRIC_KNN_SOURCE_SHA256 = "cbc35bcbf8bcc2d4610e1f1ae9348f03a1a1eda63526e8982b48f902ca0e7447"


def _standalone_contract_digest(
    kind: str, stable_id: str, source_sha256: str
) -> str:
    return _digest(
        {
            "kind": kind,
            "stable_id": stable_id,
            "source_sha256": source_sha256,
            "version": 1,
        }
    )


def _standalone_provider(
    *,
    stable_id: str,
    semantic_kind: str,
    template: str,
    source_anchor: str,
    reference: bool,
    source_path: str = _SCALAR_SUMMARY_SOURCE_PATH,
    source_sha256: str = _SCALAR_SUMMARY_SOURCE_SHA256,
    accepted_action_contract_class: str = "unkeyed_u64_scalar_sum",
) -> StandaloneProviderDeclaration:
    return StandaloneProviderDeclaration(
        stable_id=stable_id,
        semantic_kind=semantic_kind,
        accepted_action_contract_class=accepted_action_contract_class,
        template=("cpu_reference_interpreter" if reference else template),
        provider_class=("python_cpu_reference" if reference else "optix"),
        required_providers=(("python",) if reference else ("optix",)),
        execution_class=("host" if reference else "optix"),
        physical_capabilities=(
            ("HOST_REFERENCE_PROGRAM",)
            if reference
            else (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,)
        ),
        provider_abi_requirement_digest=_standalone_contract_digest(
            "provider_abi", stable_id, source_sha256
        ),
        proof_digest=_standalone_contract_digest("proof", stable_id, source_sha256),
        resource_bound_digest=_standalone_contract_digest("resource", stable_id, source_sha256),
        reuse_contract_digest=_standalone_contract_digest("reuse", stable_id, source_sha256),
        template_digest=_standalone_contract_digest("template", stable_id, source_sha256),
        source_path=source_path,
        source_sha256=source_sha256,
        source_anchor=source_anchor,
        memory_base_bytes=4096,
        memory_output_multiplier=1,
        compatibility_fallback=reference,
    )


def _current_standalone_providers() -> tuple[StandaloneProviderDeclaration, ...]:
    rows = (
        _standalone_provider(
            stable_id="canonical_standalone/metric_knn_euclidean_filter_refine_3d/optix/prepared_metric_knn_3d_optix",
            semantic_kind="metric_knn_euclidean_filter_refine_3d.v1",
            template="prepared_metric_knn_3d_optix",
            source_anchor="prepare_metric_knn_physical_3d",
            reference=False,
            source_path=_METRIC_KNN_SOURCE_PATH,
            source_sha256=_METRIC_KNN_SOURCE_SHA256,
            accepted_action_contract_class="metric_knn_complete_topk_3d",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/metric_knn_linf_filter_refine_3d/optix/prepared_metric_knn_3d_optix",
            semantic_kind="metric_knn_linf_filter_refine_3d.v1",
            template="prepared_metric_knn_3d_optix",
            source_anchor="prepare_metric_knn_physical_3d",
            reference=False,
            source_path=_METRIC_KNN_SOURCE_PATH,
            source_sha256=_METRIC_KNN_SOURCE_SHA256,
            accepted_action_contract_class="metric_knn_complete_topk_3d",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/metric_knn_cosine_monotone_transform_3d/optix/prepared_metric_knn_3d_optix",
            semantic_kind="metric_knn_cosine_monotone_transform_3d.v1",
            template="prepared_metric_knn_3d_optix",
            source_anchor="prepare_metric_knn_physical_3d",
            reference=False,
            source_path=_METRIC_KNN_SOURCE_PATH,
            source_sha256=_METRIC_KNN_SOURCE_SHA256,
            accepted_action_contract_class="metric_knn_complete_topk_3d",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/ray_triangle_all_hit_count_value_3d/host_reference/cpu_reference_interpreter",
            semantic_kind="ray_triangle_all_hit_count_value_3d.v1",
            template="prepared_optix_triangle_scene_ray_hit_count_sum_3d",
            source_anchor="RAY_ALL_HIT_COUNT_VALUE_3D",
            reference=True,
        ),
        _standalone_provider(
            stable_id="canonical_standalone/ray_triangle_all_hit_count_value_3d/optix/prepared_optix_triangle_scene_ray_hit_count_sum_3d",
            semantic_kind="ray_triangle_all_hit_count_value_3d.v1",
            template="prepared_optix_triangle_scene_ray_hit_count_sum_3d",
            source_anchor="prepared_optix_triangle_scene_ray_hit_count_sum_3d",
            reference=False,
        ),
        _standalone_provider(
            stable_id="canonical_standalone/directed_segment_point_location_2d/optix/directed_segment_point_location_2d",
            semantic_kind="directed_segment_point_location_2d.v1",
            template="directed_segment_point_location_2d",
            source_anchor='"directed_segment_point_location_2d"',
            reference=False,
            source_path=_PLANAR_MAP_NATIVE_SOURCE_PATH,
            source_sha256=_PLANAR_MAP_NATIVE_SOURCE_SHA256,
            accepted_action_contract_class="verified_planar_map_producer",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/segment_first_hit_2d/optix/segment_first_hit_2d",
            semantic_kind="segment_first_hit_2d.v1",
            template="segment_first_hit_2d",
            source_anchor='"segment_first_hit_2d"',
            reference=False,
            source_path=_PLANAR_MAP_NATIVE_SOURCE_PATH,
            source_sha256=_PLANAR_MAP_NATIVE_SOURCE_SHA256,
            accepted_action_contract_class="verified_planar_map_producer",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/segment_pair_grouped_range_direct_intersection_exact_count_2d/optix/segment_pair_grouped_range_direct_intersection_exact_count_2d",
            semantic_kind="segment_pair_grouped_range_direct_intersection_exact_count_2d.v1",
            template="segment_pair_grouped_range_direct_intersection_exact_count_2d",
            source_anchor='"segment_pair_grouped_range_direct_intersection_exact_count_2d"',
            reference=False,
            source_path=_PLANAR_MAP_NATIVE_SOURCE_PATH,
            source_sha256=_PLANAR_MAP_NATIVE_SOURCE_SHA256,
            accepted_action_contract_class="verified_planar_map_producer",
        ),
        _standalone_provider(
            stable_id="canonical_standalone/ray_triangle_any_hit_weighted_value_3d/host_reference/cpu_reference_interpreter",
            semantic_kind="ray_triangle_any_hit_weighted_value_3d.v1",
            template="prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d",
            source_anchor="RAY_ANY_HIT_WEIGHTED_VALUE_3D",
            reference=True,
        ),
        _standalone_provider(
            stable_id="canonical_standalone/ray_triangle_any_hit_weighted_value_3d/optix/prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d",
            semantic_kind="ray_triangle_any_hit_weighted_value_3d.v1",
            template="prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d",
            source_anchor="prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d",
            reference=False,
        ),
    )
    return tuple(sorted(rows, key=lambda row: row.stable_id))


def _current_bindings() -> tuple[CanonicalProviderBinding, ...]:
    common = "common_action_api"
    bindings = (
        _binding("aggregate_hierarchy.frontier_reduce.v1", "nvidia.cuda_compute.v1", "aggregate_hierarchy_registry/aggregate_hierarchy_continuation_reduce_3d/cuda/precompiled_cuda_aggregate_hierarchy_continuation_reduce_3d"),
        _binding("aggregate_hierarchy.frontier_reduce.v1", "numba.cpu_partner.v1", "aggregate_hierarchy_registry/aggregate_hierarchy_continuation_reduce_3d/numba/numba_cpu_aggregate_hierarchy_reduce_3d"),
        _binding("aggregate_hierarchy.frontier_reduce.v1", "nvidia.optix_traversal.v1", "aggregate_hierarchy_registry/aggregate_hierarchy_continuation_reduce_3d/optix_traversal/true_optix_aggregate_hierarchy_continuation_reduce_3d"),
        _binding("aggregate_hierarchy.frontier_reduce.v1", "host.reference.v1", "aggregate_hierarchy_registry/aggregate_hierarchy_continuation_reduce_3d/reference/reference_cpu_aggregate_hierarchy_reduce_3d", reference=True),
        _binding("nearest_state.frontier_seeded_exact.v1", "host.reference.v1", f"{common}/certified_nearest_state_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("nearest_state.frontier_seeded_exact.v1", "nvidia.cuda_compute.v1", f"{common}/certified_nearest_state_3d.v1/cuda_grid/certified_nearest_state_3d"),
        _binding("nearest_state.frontier_seeded_exact.v1", "nvidia.optix_traversal.v1", f"{common}/certified_nearest_state_3d.v1/optix_traversal/certified_nearest_state_3d_optix_traversal"),
        _binding("nearest_state.cell_mbr_exact_witness.v1", "host.reference.v1", f"{common}/certified_nearest_state_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("nearest_state.cell_mbr_exact_witness.v1", "nvidia.optix_traversal.v1", f"{common}/certified_nearest_state_3d.v1/optix_cell_mbr_exact_witness/cell_mbr_exact_witness_3d_optix_traversal"),
        _binding("query_min_state.complete_grouped_distance.v1", "host.reference.v1", f"{common}/complete_query_grouped_distance_rows.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("query_min_state.complete_grouped_distance.v1", "numba.cuda_partner.v1", f"{common}/complete_query_grouped_distance_rows.v1/numba/certified_query_min_state"),
        _binding("aabb_index.prepared_query_2d.v1", "nvidia.optix_traversal.v1", f"{common}/prepared_aabb_index_queries_2d.v1/optix/prepared_optix_aabb_index_query_2d"),
        _binding("aabb_overlap.filter_bounded_emit_2d.v1", "host.reference.v1", f"{common}/prepared_aabb_overlap_candidates_2d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("aabb_overlap.filter_bounded_emit_2d.v1", "compat.embree_traversal.v1", f"{common}/prepared_aabb_overlap_candidates_2d.v1/embree/aabb_filter_bounded_emit_reference_2d"),
        _binding("aabb_overlap.filter_bounded_emit_2d.v1", "nvidia.optix_traversal.v1", f"{common}/prepared_aabb_overlap_candidates_2d.v1/optix/aabb_filter_bounded_emit_2d"),
        _binding("point_selection.candidate_pruned_grid.v1", "host.reference.v1", f"{common}/prepared_point_candidates_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("point_selection.candidate_pruned_grid.v1", "nvidia.cuda_compute.v1", f"{common}/prepared_point_candidates_3d.v1/candidate_pruned_grid/candidate_pruned_exact_bounded_selection_3d"),
        _binding("point_selection.ranked_window_qk.v1", "host.reference.v1", f"{common}/prepared_point_candidates_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("point_selection.ranked_window_qk.v1", "nvidia.cuda_compute.v1", f"{common}/prepared_point_candidates_3d.v1/ranked_window_qk/prepared_ranked_distance_window_qk_3d"),
        _binding("point_selection.spatial_bounded.v1", "host.reference.v1", f"{common}/prepared_point_candidates_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("point_selection.spatial_bounded.v1", "nvidia.optix_traversal.v1", f"{common}/prepared_point_candidates_3d.v1/optix/point_candidate_bounded_selection_3d"),
        _binding("ray_triangle.keyed_i64_sum.v1", "host.reference.v1", f"{common}/stable_ray_triangle_candidates_3d.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("ray_triangle.keyed_i64_sum.v1", "nvidia.optix_traversal.v1", f"{common}/stable_ray_triangle_candidates_3d.v1/optix/keyed_i64_sum_3d"),
        _binding("logical_events.filter_bounded_emit.v1", "host.reference.v1", f"{common}/verified_logical_event_columns.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("logical_events.filter_bounded_emit.v1", "numba.cuda_partner.v1", f"{common}/verified_logical_event_columns.v1/numba/filter_bounded_emit"),
        _binding("logical_events.grouped_i64x2_count_sum.v1", "host.reference.v1", f"{common}/verified_logical_event_columns.v1/cpu_reference/cpu_reference_interpreter", reference=True),
        _binding("logical_events.grouped_i64x2_count_sum.v1", "host.partner.v1", f"{common}/verified_logical_event_columns.v1/host/sorted_host_i64x2_count_sum"),
        _binding("logical_events.grouped_i64x2_count_sum.v1", "numba.cuda_partner.v1", f"{common}/verified_logical_event_columns.v1/numba/grouped_i64x2_count_sum"),
        _binding("fixed_radius.complete_pair_components.v1", "numba.cuda_partner.v1", "fixed_radius_graph_registry/complete_pair_candidate_enumeration.v1/numba_complete_candidate_action/complete_pair_grouped_radius_components"),
        _binding("fixed_radius.prepared_spatial_components.v1", "nvidia.optix_numba_pipeline.v1", "fixed_radius_graph_registry/prepared_spatial_radius_producer.v1/optix_prepared_radius_components/prepared_optix_radius_graph_plus_numba_components"),
        _standalone_binding("metric_knn.filter_refine_euclidean_3d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/metric_knn_euclidean_filter_refine_3d/optix/prepared_metric_knn_3d_optix"),
        _standalone_binding("metric_knn.filter_refine_linf_3d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/metric_knn_linf_filter_refine_3d/optix/prepared_metric_knn_3d_optix"),
        _standalone_binding("metric_knn.monotone_cosine_3d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/metric_knn_cosine_monotone_transform_3d/optix/prepared_metric_knn_3d_optix"),
        _standalone_binding("ray_triangle_scalar.all_hit_count_value.v1", "host.reference.v1", "canonical_standalone/ray_triangle_all_hit_count_value_3d/host_reference/cpu_reference_interpreter", reference=True),
        _standalone_binding("ray_triangle_scalar.all_hit_count_value.v1", "nvidia.optix_traversal.v1", "canonical_standalone/ray_triangle_all_hit_count_value_3d/optix/prepared_optix_triangle_scene_ray_hit_count_sum_3d"),
        _standalone_binding("ray_triangle_scalar.any_hit_weighted_value.v1", "host.reference.v1", "canonical_standalone/ray_triangle_any_hit_weighted_value_3d/host_reference/cpu_reference_interpreter", reference=True),
        _standalone_binding("ray_triangle_scalar.any_hit_weighted_value.v1", "nvidia.optix_traversal.v1", "canonical_standalone/ray_triangle_any_hit_weighted_value_3d/optix/prepared_optix_triangle_scene_ray_any_hit_weighted_sum_3d"),
        _standalone_binding("planar_map.directed_segment_point_location_2d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/directed_segment_point_location_2d/optix/directed_segment_point_location_2d"),
        _standalone_binding("planar_map.segment_first_hit_2d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/segment_first_hit_2d/optix/segment_first_hit_2d"),
        _standalone_binding("planar_map.segment_pair_grouped_range_exact_count_2d.v1", "nvidia.optix_traversal.v1", "canonical_standalone/segment_pair_grouped_range_direct_intersection_exact_count_2d/optix/segment_pair_grouped_range_direct_intersection_exact_count_2d"),
    )
    return tuple(
        sorted(
            bindings,
            key=lambda row: (
                row.statement_stable_id,
                row.backend_contract_id,
                row.candidate_stable_id,
            ),
        )
    )


def _validate_against_candidate_registry(
    canonical: CanonicalProviderRegistry,
    candidates: RegistrySnapshot,
) -> None:
    if canonical.candidate_registry_sha256 != candidates.digest:
        raise CanonicalPhysicalResolutionError("CANDIDATE_REGISTRY_IDENTITY_DRIFT")
    declaration_by_id = {row.stable_id: row for row in candidates.declarations}
    standalone_by_id = {row.stable_id: row for row in canonical.standalone_providers}
    statement_by_id = {row.stable_id: row for row in canonical.statements}
    backend_by_id = {row.stable_id: row for row in canonical.backend_contracts}
    covered: set[str] = set()
    exact_keys: set[tuple[str, str]] = set()
    for binding in canonical.bindings:
        key = (binding.statement_stable_id, binding.backend_contract_id)
        if key in exact_keys:
            raise CanonicalPhysicalResolutionError(
                "AMBIGUOUS_CANONICAL_PROVIDER", "/".join(key)
            )
        exact_keys.add(key)
        statement = statement_by_id[binding.statement_stable_id]
        backend = backend_by_id[binding.backend_contract_id]
        if binding.provider_namespace == "legacy_candidate":
            declaration = declaration_by_id.get(binding.candidate_stable_id)
        else:
            declaration = standalone_by_id.get(binding.candidate_stable_id)
        if declaration is None:
            raise CanonicalPhysicalResolutionError(
                "BINDING_REFERENCES_UNKNOWN_CANDIDATE", binding.candidate_stable_id
            )
        if declaration.semantic_kind != statement.semantic_kind:
            raise CanonicalPhysicalResolutionError(
                "BINDING_SEMANTIC_KIND_MISMATCH", binding.candidate_stable_id
            )
        accepted_contracts = getattr(
            declaration,
            "accepted_action_contract_classes",
            (getattr(declaration, "accepted_action_contract_class", ""),),
        )
        if statement.action_contract_class not in accepted_contracts:
            raise CanonicalPhysicalResolutionError(
                "BINDING_ACTION_CONTRACT_MISMATCH", binding.candidate_stable_id
            )
        if declaration.required_providers != backend.required_providers:
            raise CanonicalPhysicalResolutionError(
                "BINDING_PROVIDER_CONTRACT_MISMATCH", binding.candidate_stable_id
            )
        if declaration.execution_class not in backend.allowed_execution_classes:
            raise CanonicalPhysicalResolutionError(
                "BINDING_EXECUTION_CLASS_MISMATCH", binding.candidate_stable_id
            )
        if not set(backend.required_physical_capabilities).issubset(
            declaration.physical_capabilities
        ):
            raise CanonicalPhysicalResolutionError(
                "BINDING_PHYSICAL_CAPABILITY_MISMATCH", binding.candidate_stable_id
            )
        is_reference = (
            declaration.selection_role == "REFERENCE_FALLBACK"
            if binding.provider_namespace == "legacy_candidate"
            else declaration.compatibility_fallback
        )
        if binding.compatibility_fallback != is_reference:
            raise CanonicalPhysicalResolutionError(
                "BINDING_REFERENCE_ROLE_MISMATCH", binding.candidate_stable_id
            )
        if binding.provider_namespace == "legacy_candidate":
            covered.add(binding.candidate_stable_id)
    missing = sorted(set(declaration_by_id) - covered)
    if missing:
        raise CanonicalPhysicalResolutionError(
            "CURRENT_CANDIDATE_NOT_ACCOUNTED", ",".join(missing)
        )
    bound_standalone = {
        row.candidate_stable_id
        for row in canonical.bindings
        if row.provider_namespace == "standalone_provider"
    }
    orphaned = sorted(set(standalone_by_id) - bound_standalone)
    if orphaned:
        raise CanonicalPhysicalResolutionError(
            "STANDALONE_PROVIDER_NOT_ACCOUNTED", ",".join(orphaned)
        )
    root = Path(__file__).resolve().parents[2]
    for provider in canonical.standalone_providers:
        path = root / provider.source_path
        if not path.is_file():
            raise CanonicalPhysicalResolutionError(
                "STANDALONE_PROVIDER_SOURCE_MISSING", provider.source_path
            )
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != provider.source_sha256:
            raise CanonicalPhysicalResolutionError(
                "STANDALONE_PROVIDER_SOURCE_DRIFT", provider.source_path
            )
        if provider.source_anchor not in payload.decode("utf-8"):
            raise CanonicalPhysicalResolutionError(
                "STANDALONE_PROVIDER_SOURCE_ANCHOR_MISSING", provider.stable_id
            )


@lru_cache(maxsize=1)
def current_canonical_provider_registry() -> CanonicalProviderRegistry:
    candidates = current_registry_snapshot()
    result = CanonicalProviderRegistry(
        version=CANONICAL_REGISTRY_VERSION,
        statements=_current_statements(),
        backend_contracts=_current_backend_contracts(),
        standalone_providers=_current_standalone_providers(),
        bindings=_current_bindings(),
        candidate_registry_sha256=candidates.digest,
    )
    _validate_against_candidate_registry(result, candidates)
    return result


def registered_semantic_statement(stable_id: str) -> SemanticAlgorithmStatement:
    rows = tuple(
        row for row in current_canonical_provider_registry().statements if row.stable_id == stable_id
    )
    if len(rows) != 1:
        raise CanonicalPhysicalResolutionError("UNSUPPORTED_SEMANTIC_STATEMENT", stable_id)
    return rows[0]


def registered_backend_contract(stable_id: str) -> BackendContract:
    rows = tuple(
        row for row in current_canonical_provider_registry().backend_contracts if row.stable_id == stable_id
    )
    if len(rows) != 1:
        raise CanonicalPhysicalResolutionError("UNSUPPORTED_BACKEND_CONTRACT", stable_id)
    return rows[0]


def _failure_receipt(
    *,
    statement_stable_id: str,
    expected_statement_sha256: str,
    backend_contract_id: str,
    expected_backend_contract_sha256: str,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    registry: CanonicalProviderRegistry,
    error: CanonicalPhysicalResolutionError,
) -> dict[str, object]:
    body: dict[str, object] = {
        "schema": CANONICAL_RESOLUTION_RECEIPT_SCHEMA,
        "policy_version": CANONICAL_RESOLUTION_POLICY_VERSION,
        "status": "FAIL_CLOSED",
        "error_code": error.code,
        "error_detail": error.detail,
        "statement_stable_id": statement_stable_id,
        "expected_statement_sha256": expected_statement_sha256,
        "backend_contract_id": backend_contract_id,
        "expected_backend_contract_sha256": expected_backend_contract_sha256,
        "action": action.as_dict(),
        "action_descriptor_sha256": _digest(action.as_dict()),
        "target": target.as_dict(),
        "target_contract_sha256": _digest(target.as_dict()),
        "canonical_registry": registry.as_dict(),
        "canonical_registry_sha256": registry.digest,
        "candidate_registry_sha256": registry.candidate_registry_sha256,
        "candidate_executed": False,
        "behavioral_traversal_claimed": False,
        "timing_or_learned_input_used": False,
        "application_or_publication_identity_used": False,
        "dataset_or_batch_identity_used": False,
        "harness_candidate_override_used": False,
        "cost_or_latency_order_used": False,
    }
    body["receipt_sha256"] = _digest(body)
    return body


def _resolve_or_raise(
    *,
    statement_stable_id: str,
    expected_statement_sha256: str,
    backend_contract_id: str,
    expected_backend_contract_sha256: str,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    canonical_registry: CanonicalProviderRegistry,
    candidate_registry: RegistrySnapshot,
) -> dict[str, object]:
    _validate_against_candidate_registry(canonical_registry, candidate_registry)
    statements = tuple(row for row in canonical_registry.statements if row.stable_id == statement_stable_id)
    if len(statements) != 1:
        raise CanonicalPhysicalResolutionError("UNSUPPORTED_SEMANTIC_STATEMENT", statement_stable_id)
    statement = statements[0]
    if statement.digest != _require_sha256(expected_statement_sha256, field="expected_statement_sha256"):
        raise CanonicalPhysicalResolutionError("SEMANTIC_STATEMENT_IDENTITY_MISMATCH", statement_stable_id)
    if action.semantic_kind != statement.semantic_kind or action.action_contract_class != statement.action_contract_class:
        raise CanonicalPhysicalResolutionError("ACTION_DOES_NOT_IMPLEMENT_STATEMENT", statement_stable_id)

    backends = tuple(row for row in canonical_registry.backend_contracts if row.stable_id == backend_contract_id)
    if len(backends) != 1:
        raise CanonicalPhysicalResolutionError("UNSUPPORTED_BACKEND_CONTRACT", backend_contract_id)
    backend = backends[0]
    if backend.digest != _require_sha256(expected_backend_contract_sha256, field="expected_backend_contract_sha256"):
        raise CanonicalPhysicalResolutionError("BACKEND_CONTRACT_IDENTITY_MISMATCH", backend_contract_id)

    bindings = tuple(
        row
        for row in canonical_registry.bindings
        if row.statement_stable_id == statement_stable_id
        and row.backend_contract_id == backend_contract_id
    )
    if not bindings:
        raise CanonicalPhysicalResolutionError(
            "UNSUPPORTED_STATEMENT_BACKEND_PAIR", f"{statement_stable_id}/{backend_contract_id}"
        )
    if len(bindings) != 1:
        raise CanonicalPhysicalResolutionError(
            "AMBIGUOUS_CANONICAL_PROVIDER", f"{statement_stable_id}/{backend_contract_id}"
        )
    binding = bindings[0]
    candidate: CandidateDescriptor | None = None
    standalone: StandaloneProviderDeclaration | None = None
    if binding.provider_namespace == "legacy_candidate":
        candidates = materialize_candidates(action, candidate_registry)
        matches = tuple(row for row in candidates if row.declaration.stable_id == binding.candidate_stable_id)
        if len(matches) != 1:
            raise CanonicalPhysicalResolutionError(
                "MISSING_PROVIDER_IDENTITY_OR_RECEIPT_CONTRACT", binding.candidate_stable_id
            )
        candidate = matches[0]
        reasons = candidate_legality_reasons(candidate, action, target)
        provider_descriptor = candidate.as_dict()
        provider_sha256 = candidate_descriptor_sha256(candidate)
        source_sha256 = candidate.declaration.source_sha256
        template_sha256 = candidate.declaration.template_digest
    else:
        standalone_matches = tuple(
            row
            for row in canonical_registry.standalone_providers
            if row.stable_id == binding.candidate_stable_id
        )
        if len(standalone_matches) != 1:
            raise CanonicalPhysicalResolutionError(
                "MISSING_PROVIDER_IDENTITY_OR_RECEIPT_CONTRACT", binding.candidate_stable_id
            )
        standalone = standalone_matches[0]
        reasons_list: list[str] = []
        if standalone.semantic_kind != action.semantic_kind or standalone.accepted_action_contract_class != action.action_contract_class:
            reasons_list.append("ACTION_CONTRACT_CLASS_NOT_ACCEPTED")
        for provider_digest, admitted in (
            (standalone.proof_digest, action.admitted_proof_digests),
            (standalone.resource_bound_digest, action.admitted_resource_bound_digests),
            (standalone.reuse_contract_digest, action.admitted_reuse_contract_digests),
            (standalone.template_digest, action.admitted_template_digests),
        ):
            if provider_digest not in admitted:
                reasons_list.append("STANDALONE_PROVIDER_PROOF_NOT_ADMITTED")
        if not set(standalone.required_providers).issubset(target.available_providers):
            reasons_list.append("REQUIRED_PROVIDER_UNAVAILABLE")
        if standalone.provider_abi_requirement_digest not in target.available_provider_abi_requirement_digests:
            reasons_list.append("PROVIDER_ABI_REQUIREMENT_UNAVAILABLE")
        if target.allowed_execution_classes and standalone.execution_class not in target.allowed_execution_classes:
            reasons_list.append("EXECUTION_CLASS_NOT_ALLOWED")
        if not set(target.required_physical_capabilities).issubset(standalone.physical_capabilities):
            reasons_list.append("REQUIRED_PHYSICAL_CAPABILITY_MISSING")
        provider_descriptor = standalone.descriptor(action)
        if int(provider_descriptor["conservative_memory_bytes"]) > target.memory_limit_bytes:
            reasons_list.append("CONSERVATIVE_MEMORY_BOUND_EXCEEDED")
        reasons = tuple(reasons_list)
        provider_sha256 = _digest(provider_descriptor)
        source_sha256 = standalone.source_sha256
        template_sha256 = standalone.template_digest
    if reasons:
        raise CanonicalPhysicalResolutionError(
            "ILLEGAL_TARGET_OR_RESOURCE_CONTRACT",
            f"{binding.candidate_stable_id}:{','.join(reasons)}",
        )

    body: dict[str, object] = {
        "schema": CANONICAL_RESOLUTION_RECEIPT_SCHEMA,
        "policy_version": CANONICAL_RESOLUTION_POLICY_VERSION,
        "status": "RESOLVED",
        "statement": statement.as_dict(),
        "statement_sha256": statement.digest,
        "action": action.as_dict(),
        "action_descriptor_sha256": _digest(action.as_dict()),
        "target": target.as_dict(),
        "target_contract_sha256": _digest(target.as_dict()),
        "backend_contract": backend.as_dict(),
        "backend_contract_sha256": backend.digest,
        "canonical_registry": canonical_registry.as_dict(),
        "canonical_registry_sha256": canonical_registry.digest,
        "candidate_registry": candidate_registry.as_dict(),
        "candidate_registry_sha256": candidate_registry.digest,
        "binding": binding.as_dict(),
        "binding_sha256": _digest(binding.as_dict()),
        "provider_candidate_stable_id": binding.candidate_stable_id,
        "provider_namespace": binding.provider_namespace,
        "provider_candidate": provider_descriptor,
        "provider_candidate_sha256": provider_sha256,
        "provider_source_sha256": source_sha256,
        "provider_template_sha256": template_sha256,
        "algorithm_preserving": binding.algorithm_preserving,
        "compatibility_fallback": binding.compatibility_fallback,
        "candidate_executed": False,
        "behavioral_traversal_claimed": False,
        "behavioral_traversal_receipt_still_required": (
            backend.behavioral_proof_required_for_execution_claim
        ),
        "timing_or_learned_input_used": False,
        "application_or_publication_identity_used": False,
        "dataset_or_batch_identity_used": False,
        "harness_candidate_override_used": False,
        "cost_or_latency_order_used": False,
        "complete_legal_order_constructed": False,
    }
    body["receipt_sha256"] = _digest(body)
    return body


def resolve_canonical_provider(
    *,
    statement_stable_id: str,
    expected_statement_sha256: str,
    backend_contract_id: str,
    expected_backend_contract_sha256: str,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
) -> dict[str, object]:
    """Resolve one canonical provider or return a typed fail-closed receipt."""

    canonical = current_canonical_provider_registry()
    candidates = current_registry_snapshot()
    try:
        return _resolve_or_raise(
            statement_stable_id=statement_stable_id,
            expected_statement_sha256=expected_statement_sha256,
            backend_contract_id=backend_contract_id,
            expected_backend_contract_sha256=expected_backend_contract_sha256,
            action=action,
            target=target,
            canonical_registry=canonical,
            candidate_registry=candidates,
        )
    except CanonicalPhysicalResolutionError as error:
        return _failure_receipt(
            statement_stable_id=statement_stable_id,
            expected_statement_sha256=expected_statement_sha256,
            backend_contract_id=backend_contract_id,
            expected_backend_contract_sha256=expected_backend_contract_sha256,
            action=action,
            target=target,
            registry=canonical,
            error=error,
        )


def bind_canonical_provider_to_materialized_plan(
    resolution_receipt: Mapping[str, object],
    *,
    materialized_provider_stable_id: str,
    materialized_plan_sha256: str,
    materialized_binding_sha256: str,
) -> dict[str, object]:
    """Make canonical resolution authoritative over a compatibility plan.

    The compatibility materializer may construct the existing downstream plan
    schema, but it cannot choose or replace the provider.  Any difference from
    the already-resolved canonical provider fails before execution.
    """

    if not isinstance(resolution_receipt, Mapping):
        raise CanonicalPhysicalResolutionError("INVALID_RESOLUTION_RECEIPT")
    receipt = dict(resolution_receipt)
    claimed = _require_sha256(receipt.pop("receipt_sha256", None), field="receipt_sha256")
    if _digest(receipt) != claimed:
        raise CanonicalPhysicalResolutionError("RESOLUTION_RECEIPT_DIGEST_MISMATCH")
    if (
        receipt.get("schema") != CANONICAL_RESOLUTION_RECEIPT_SCHEMA
        or receipt.get("status") != "RESOLVED"
    ):
        raise CanonicalPhysicalResolutionError("RESOLUTION_RECEIPT_NOT_RESOLVED")
    if receipt.get("candidate_executed") is not False:
        raise CanonicalPhysicalResolutionError("STATIC_RESOLUTION_CLAIMS_EXECUTION")
    canonical_provider = receipt.get("provider_candidate_stable_id")
    if not isinstance(canonical_provider, str) or not canonical_provider:
        raise CanonicalPhysicalResolutionError("CANONICAL_PROVIDER_ID_MISSING")
    if materialized_provider_stable_id != canonical_provider:
        raise CanonicalPhysicalResolutionError(
            "MATERIALIZED_PROVIDER_DIFFERS_FROM_CANONICAL_PROVIDER",
            f"{materialized_provider_stable_id}!={canonical_provider}",
        )
    plan_sha = _require_sha256(
        materialized_plan_sha256, field="materialized_plan_sha256"
    )
    binding_sha = _require_sha256(
        materialized_binding_sha256, field="materialized_binding_sha256"
    )
    body: dict[str, object] = {
        "schema": CANONICAL_PRODUCTION_AUTHORITY_SCHEMA,
        "status": "BOUND",
        "canonical_resolution_receipt_sha256": claimed,
        "statement_stable_id": receipt["statement"]["stable_id"],
        "statement_sha256": receipt["statement_sha256"],
        "backend_contract_id": receipt["backend_contract"]["stable_id"],
        "backend_contract_sha256": receipt["backend_contract_sha256"],
        "provider_candidate_stable_id": canonical_provider,
        "provider_candidate_sha256": receipt["provider_candidate_sha256"],
        "provider_namespace": receipt["provider_namespace"],
        "materialized_plan_sha256": plan_sha,
        "materialized_binding_sha256": binding_sha,
        "compatibility_plan_materializer_used": True,
        "compatibility_materializer_is_selection_authority": False,
        "application_selected_algorithm": True,
        "compiler_selected_provider_for_exact_statement": True,
        "algorithm_options_or_cost_input_used": False,
        "candidate_executed": False,
        "behavioral_traversal_claimed": False,
        "behavioral_receipt_still_required": receipt[
            "behavioral_traversal_receipt_still_required"
        ],
    }
    body["authority_receipt_sha256"] = _digest(body)
    return body


def resolve_canonical_standalone_provider_for_contract(
    *,
    statement_stable_id: str,
    backend_contract_id: str,
    action_identity: Mapping[str, object],
    output_contract: Mapping[str, object],
    work_domain: Mapping[str, object],
    input_bytes: int,
    output_bytes: int,
    prepared_bytes: int,
    logical_cardinality_bound: int,
    pair_cardinality_bound: int,
    logical_item_bytes_bound: int,
    pair_item_bytes_bound: int,
    target_identity: Mapping[str, object],
    available_providers: Sequence[str],
    memory_limit_bytes: int,
) -> dict[str, object]:
    """Resolve a source-bound direct provider without inventing candidates.

    The semantic statement and backend contract identify exactly one canonical
    standalone provider.  Its proof, resource, reuse, template and ABI
    digests are admitted from the closed compiler registry, never from the
    application.  Dynamic resource quantities remain caller-observed facts.
    This helper does not execute the provider and does not choose an algorithm.
    """

    statement = registered_semantic_statement(statement_stable_id)
    backend = registered_backend_contract(backend_contract_id)
    registry = current_canonical_provider_registry()
    bindings = tuple(
        row
        for row in registry.bindings
        if row.statement_stable_id == statement.stable_id
        and row.backend_contract_id == backend.stable_id
    )
    if len(bindings) != 1:
        raise CanonicalPhysicalResolutionError(
            "AMBIGUOUS_CANONICAL_PROVIDER",
            f"{statement.stable_id}/{backend.stable_id}",
        )
    binding = bindings[0]
    if binding.provider_namespace != "standalone_provider":
        raise CanonicalPhysicalResolutionError(
            "DIRECT_FRONTDOOR_REQUIRES_STANDALONE_PROVIDER",
            binding.candidate_stable_id,
        )
    providers = tuple(
        row
        for row in registry.standalone_providers
        if row.stable_id == binding.candidate_stable_id
    )
    if len(providers) != 1:
        raise CanonicalPhysicalResolutionError(
            "MISSING_PROVIDER_IDENTITY_OR_RECEIPT_CONTRACT",
            binding.candidate_stable_id,
        )
    provider = providers[0]
    action = make_action_descriptor(
        semantic_kind=statement.semantic_kind,
        action_contract_class=statement.action_contract_class,
        action_identity=dict(action_identity),
        output_contract=dict(output_contract),
        work_domain=dict(work_domain),
        input_bytes=int(input_bytes),
        output_bytes=int(output_bytes),
        prepared_bytes=int(prepared_bytes),
        logical_cardinality_bound=int(logical_cardinality_bound),
        pair_cardinality_bound=int(pair_cardinality_bound),
        logical_item_bytes_bound=int(logical_item_bytes_bound),
        pair_item_bytes_bound=int(pair_item_bytes_bound),
        admitted_proof_digests=(provider.proof_digest,),
        admitted_resource_bound_digests=(provider.resource_bound_digest,),
        admitted_reuse_contract_digests=(provider.reuse_contract_digest,),
        admitted_template_digests=(provider.template_digest,),
    )
    target = make_target_descriptor(
        target_identity=dict(target_identity),
        available_providers=tuple(available_providers),
        allowed_execution_classes=(provider.execution_class,),
        available_provider_abi_requirement_digests=(
            provider.provider_abi_requirement_digest,
        ),
        memory_limit_bytes=int(memory_limit_bytes),
        required_physical_capabilities=backend.required_physical_capabilities,
    )
    receipt = resolve_canonical_provider(
        statement_stable_id=statement.stable_id,
        expected_statement_sha256=statement.digest,
        backend_contract_id=backend.stable_id,
        expected_backend_contract_sha256=backend.digest,
        action=action,
        target=target,
    )
    if receipt.get("status") != "RESOLVED":
        raise CanonicalPhysicalResolutionError(
            str(receipt.get("error_code", "FAIL_CLOSED")),
            str(receipt.get("error_detail", "")),
        )
    return receipt


def bind_canonical_provider_to_direct_provider(
    resolution_receipt: Mapping[str, object],
    *,
    direct_provider_stable_id: str,
    direct_execution_contract_sha256: str,
) -> dict[str, object]:
    """Make canonical resolution authoritative over a direct provider call."""

    if not isinstance(resolution_receipt, Mapping):
        raise CanonicalPhysicalResolutionError("INVALID_RESOLUTION_RECEIPT")
    receipt = dict(resolution_receipt)
    claimed = _require_sha256(receipt.pop("receipt_sha256", None), field="receipt_sha256")
    if _digest(receipt) != claimed:
        raise CanonicalPhysicalResolutionError("RESOLUTION_RECEIPT_DIGEST_MISMATCH")
    if (
        receipt.get("schema") != CANONICAL_RESOLUTION_RECEIPT_SCHEMA
        or receipt.get("status") != "RESOLVED"
    ):
        raise CanonicalPhysicalResolutionError("RESOLUTION_RECEIPT_NOT_RESOLVED")
    if receipt.get("provider_namespace") != "standalone_provider":
        raise CanonicalPhysicalResolutionError(
            "DIRECT_FRONTDOOR_REQUIRES_STANDALONE_PROVIDER"
        )
    if receipt.get("candidate_executed") is not False:
        raise CanonicalPhysicalResolutionError("STATIC_RESOLUTION_CLAIMS_EXECUTION")
    canonical_provider = receipt.get("provider_candidate_stable_id")
    if not isinstance(canonical_provider, str) or not canonical_provider:
        raise CanonicalPhysicalResolutionError("CANONICAL_PROVIDER_ID_MISSING")
    if direct_provider_stable_id != canonical_provider:
        raise CanonicalPhysicalResolutionError(
            "DIRECT_PROVIDER_DIFFERS_FROM_CANONICAL_PROVIDER",
            f"{direct_provider_stable_id}!={canonical_provider}",
        )
    contract_sha = _require_sha256(
        direct_execution_contract_sha256,
        field="direct_execution_contract_sha256",
    )
    body: dict[str, object] = {
        "schema": CANONICAL_PRODUCTION_AUTHORITY_SCHEMA,
        "status": "BOUND",
        "canonical_resolution_receipt_sha256": claimed,
        "statement_stable_id": receipt["statement"]["stable_id"],
        "statement_sha256": receipt["statement_sha256"],
        "backend_contract_id": receipt["backend_contract"]["stable_id"],
        "backend_contract_sha256": receipt["backend_contract_sha256"],
        "provider_candidate_stable_id": canonical_provider,
        "provider_candidate_sha256": receipt["provider_candidate_sha256"],
        "provider_namespace": receipt["provider_namespace"],
        "direct_execution_contract_sha256": contract_sha,
        "direct_provider_frontdoor_used": True,
        "compatibility_plan_materializer_used": False,
        "compatibility_materializer_is_selection_authority": False,
        "application_selected_algorithm": True,
        "compiler_selected_provider_for_exact_statement": True,
        "algorithm_options_or_cost_input_used": False,
        "candidate_executed": False,
        "behavioral_traversal_claimed": False,
        "behavioral_receipt_still_required": receipt[
            "behavioral_traversal_receipt_still_required"
        ],
    }
    body["authority_receipt_sha256"] = _digest(body)
    return body


__all__ = [
    "CANONICAL_REGISTRY_VERSION",
    "CANONICAL_PRODUCTION_AUTHORITY_SCHEMA",
    "CANONICAL_RESOLUTION_POLICY_VERSION",
    "CANONICAL_RESOLUTION_RECEIPT_SCHEMA",
    "BackendContract",
    "CanonicalPhysicalResolutionError",
    "CanonicalProviderBinding",
    "CanonicalProviderRegistry",
    "StandaloneProviderDeclaration",
    "SemanticAlgorithmStatement",
    "current_canonical_provider_registry",
    "registered_backend_contract",
    "registered_semantic_statement",
    "bind_canonical_provider_to_direct_provider",
    "bind_canonical_provider_to_materialized_plan",
    "resolve_canonical_standalone_provider_for_contract",
    "resolve_canonical_provider",
]
