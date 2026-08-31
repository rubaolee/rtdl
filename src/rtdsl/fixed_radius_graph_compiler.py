from __future__ import annotations

from dataclasses import dataclass, field, replace
import functools
import hashlib
import hmac
import inspect
import json
import math
import os
from pathlib import Path
import secrets
from types import MappingProxyType
from typing import Mapping

import numpy as np

from .action_api import (
    ActionTargetProfile,
    CompiledAction,
    bind_action_event_columns,
    compile_bound_action_for_target,
    prepare_bound_numba_action_columns,
)
from .action_numba_continuation import execute_numba_action_continuation
from .action_native_identity import (
    ActionNativeLibraryIdentity,
    ActionNativeTemplateSymbolProbe,
    FIXED_RADIUS_GRAPH_COMPONENTS_3D_REQUIRED_SYMBOLS,
    native_library_identity,
    probe_native_template_symbols,
    validate_native_library_identity,
    validate_native_library_identity_metadata,
)
from .action_phase_trace import ActionPhaseTrace, action_phase
from .action_placement import (
    ActionPhysicalRefinementCertificate,
    issue_action_physical_refinement_certificate,
)
from .component_partition import canonical_partition_labels
from .partner_adapters import (
    PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D,
    prepare_optix_numba_radius_graph_grouped_stream_continuation_3d,
    probe_numba_radius_graph_continuation_3d,
    radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns,
)
from .optix_runtime import (
    PreparedOptixFixedRadiusCountThreshold3D,
    probe_optix_fixed_radius_graph_components_3d,
)
from .predicate_aware_boundary_union import predicate_aware_boundary_union_reference
from .reference import Point3D


FIXED_RADIUS_GRAPH_COMPILER_VERSION = (
    "rtdl.fixed_radius_graph_components.compiler.private_candidate.v3"
)
FIXED_RADIUS_GRAPH_STRUCTURAL_COST_MODEL = (
    "rtdl.fixed_radius_graph_components.structural_work.v2"
)
FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT = (
    "fixed_radius_graph_components.closed_f32_distance_sq.self_inclusive_"
    "min_neighbors.nx2_or_nx3.core_flags_and_canonical_partition.v2"
)
FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE = (
    "closed_f32_squared_radius_implementations_with_locked_rn_operation_order_"
    "and_attested_successor_differential_cases__not_exhaustive_all_f32_proof.v3"
)
FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC = (
    "f32_sub_rn__f32_mul_rn_each_axis__f32_add_rn_xy_then_z__"
    "radius_f32_mul_rn_radius_f32__closed_lte"
)

# This digest is the verified, name-independent semantic identity of the
# restricted closed-radius edge Action.  A source using `<`, a different
# delivery proof, or a different emitted relation does not enter this registry.
_CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST = (
    "dc2a0b80d103f77317944156d39d77df27852e96f8e8d5e7a07e1b87fe017c6f"
)

# The exact evidence digest lives in a separate compiler-owned registry module.
# Keeping the trust pin out of this executable source file avoids a circular
# identity: evidence binds this compiler's SHA-256, while installing that
# evidence must not change the compiler SHA-256 it already attests.
_REFINEMENT_EVIDENCE_ENV = "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"
_REFINEMENT_EVIDENCE_SCHEMA = "rtdl.fixed_radius_graph.refinement_evidence.v4"
_REFINEMENT_EVIDENCE_CAPSULE_SCHEMA = (
    "rtdl.fixed_radius_graph.refinement_evidence_capsule.v1"
)
_REFINEMENT_COMPOSED_SOURCE_PROOF_ID = (
    "fixed_radius_graph_refinement_evidence_capsule.v1"
)
_REFINEMENT_EVIDENCE_CASE_COUNT = 17
_REFINEMENT_EXECUTION_RECEIPT_SCHEMA = (
    "rtdl.fixed_radius_graph.route_execution_receipt.v2"
)
_INDEPENDENT_REFERENCE_SYMBOL = "_standalone_bruteforce_partition"
_INDEPENDENT_REFERENCE_DIGEST = (
    "7e52b42d1b2235110a9925540bbf59bea016261fc8bf64142a5a6d22b2ca53ea"
)

_COMPLETE_PAIR_PRODUCER = "complete_pair_candidate_enumeration.v1"
_SPATIAL_PRODUCER = "prepared_spatial_radius_producer.v1"
_COMPLETE_PAIR_BACKEND = "numba_complete_candidate_action"
_SPATIAL_BACKEND = "optix_prepared_radius_components"

# The complete-pair route remains a legal tiny-input alternative.  It is not a
# scalable fallback: beyond this compiler-owned materialization budget the
# compiler either selects the prepared spatial route or fails closed.
_MAX_COMPLETE_PAIR_EVENT_ROWS = 1_000_000
# The current grouped-union native root walk has a fixed 4096-iteration guard.
# Until the native ABI reports non-convergence explicitly, the compiler must
# keep this exact route inside the largest point count whose worst-case parent
# chain can be fully resolved by that guard.
_MAX_SPATIAL_COMPONENT_POINTS = 4_096
_EDGE_ROW_BYTES = 8
_SPATIAL_RESULT_BYTES_PER_POINT = 20
_SPATIAL_FIXED_SETUP_WORK = 64
_PLAN_SECRET = secrets.token_bytes(32)
_PREPARED_CONTEXT_SECRET = secrets.token_bytes(32)
_PREPARED_CONTEXT_CONSTRUCTOR_TOKEN = object()
_EVIDENCE_EXECUTION_ATTESTATION_SECRET = secrets.token_bytes(32)
_LIVE_ISSUED_EVIDENCE_RECEIPTS: set[tuple[str, str]] = set()


class FixedRadiusGraphPlanningError(ValueError):
    pass


def _freeze_json_value(value: object) -> object:
    """Return a recursively immutable snapshot of JSON-compatible facts."""

    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                str(key): _freeze_json_value(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"unsupported static JSON fact type: {type(value).__name__}")


def _thaw_json_value(value: object) -> object:
    """Return a detached JSON-compatible copy of frozen static facts."""

    if isinstance(value, Mapping):
        return {
            str(key): _thaw_json_value(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_thaw_json_value(item) for item in value]
    return value


def _validate_loaded_fixed_radius_native_binding(
    library,
    expected: ActionNativeLibraryIdentity,
) -> ActionNativeLibraryIdentity:
    """Recheck an already-attested fixed-radius library without file hashing.

    Full binary-byte attestation belongs to prepared-context construction.  A
    hot plan or execution rechecks the exact retained object, resolved path,
    process handle, required ABI symbols, and reported OptiX version.  A new
    object must establish a new prepared context and therefore pay the full
    ``native_library_identity`` check first.
    """

    if not isinstance(expected, ActionNativeLibraryIdentity):
        raise TypeError("expected must be an ActionNativeLibraryIdentity")
    from .optix_runtime import _find_optional_backend_symbol

    raw_path = getattr(library, "_rtdl_library_path", None)
    if not isinstance(raw_path, str) or not raw_path:
        raise RuntimeError("loaded native library has no resolved path identity")
    path = Path(raw_path).expanduser().resolve(strict=True)
    if not path.is_file() or path.is_symlink() or str(path) != expected.resolved_path:
        raise RuntimeError("loaded fixed-radius library path changed after attestation")
    handle = getattr(library, "_handle", None)
    if (
        not isinstance(handle, int)
        or isinstance(handle, bool)
        or handle <= 0
        or str(handle) != expected.process_handle_token
    ):
        raise RuntimeError("loaded fixed-radius library handle changed after attestation")
    missing = tuple(
        symbol
        for symbol in expected.required_symbols
        if _find_optional_backend_symbol(library, symbol) is None
    )
    if missing:
        raise RuntimeError(
            "loaded fixed-radius library lost required symbols: "
            + ", ".join(missing)
        )
    version_symbol = _find_optional_backend_symbol(
        library, "rtdl_optix_get_version"
    )
    if version_symbol is None:
        raise RuntimeError("loaded fixed-radius library lost its version symbol")
    import ctypes

    major = ctypes.c_int()
    minor = ctypes.c_int()
    patch = ctypes.c_int()
    status = int(
        version_symbol(
            ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)
        )
    )
    if status != 0 or (
        int(major.value), int(minor.value), int(patch.value)
    ) != expected.optix_version:
        raise RuntimeError("loaded fixed-radius library version changed after attestation")
    return expected


@dataclass(frozen=True)
class VerifiedFixedRadiusGraphRefinementEvidence:
    artifact_sha256: str
    schema: str
    verified_case_count: int
    independent_reference_digest: str
    executable_identity_digests: Mapping[str, str]
    native_library_binary_sha256: str
    native_optix_version: tuple[int, int, int]
    native_required_symbols_digest: str
    artifact_path: str | None = None
    dependency_source_verification_mode: str = "runtime_dependency_file_hashes"
    source_seal_tree_digest: str | None = None

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": self.schema,
            "artifact_sha256": self.artifact_sha256,
            "verified_case_count": self.verified_case_count,
            "all_cases_exact": True,
            "explicit_case_inputs_and_outputs": True,
            "rounding_counterexample_covered": True,
            "nx2_zero_z_lift_covered": True,
            "recorded_worker_timings_discarded": True,
            "runtime_calibration_authorized": False,
            "executable_identity_digests": dict(
                self.executable_identity_digests
            ),
            "native_evidence_identity": {
                "binary_sha256": self.native_library_binary_sha256,
                "optix_version": list(self.native_optix_version),
                "required_symbols_digest": (
                    self.native_required_symbols_digest
                ),
            },
            "dependency_source_verification_mode": (
                self.dependency_source_verification_mode
            ),
            "source_seal_tree_digest": self.source_seal_tree_digest,
            "independent_oracle": {
                "symbol": _INDEPENDENT_REFERENCE_SYMBOL,
                "normalized_source_sha256": self.independent_reference_digest,
                "normalization": "inspect.getsource_crlf_to_lf_utf8",
            },
        }

    def to_source_receipt(self) -> dict[str, object]:
        """Return the already-verified static artifact identity without I/O."""

        return {
            "status": (
                "successor_evidence_installed"
                if self.artifact_path is not None
                else "validated_evidence_without_installed_path"
            ),
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "artifact_schema": self.schema,
            "old_functional_artifact_accepted": False,
            "source_receipt_created_without_artifact_reread": True,
        }


@dataclass(frozen=True)
class _FixedRadiusGraphRefinementExecutionContext:
    compiled: CompiledAction
    target_profile: ActionTargetProfile
    point_count: int
    input_dimension: int
    spatial_zero_z_lift_required: bool
    native_library_identity: ActionNativeLibraryIdentity
    _native_library_ref: object = field(repr=False, compare=False)


@dataclass(frozen=True)
class _FixedRadiusGraphRuntimeCapabilityProbe:
    metadata: Mapping[str, object]
    native_library_identity: ActionNativeLibraryIdentity | None
    _native_library_ref: object | None = field(
        default=None, repr=False, compare=False
    )


class PreparedFixedRadiusGraphContext:
    """Process-local trust and capability lifetime for fixed-radius plans.

    Refinement evidence, executable identities, the runtime capability probe,
    and the full native-library byte attestation are input-independent.  This
    compiler-owned object establishes them once and keeps their exact live
    objects bound while distinct input batches receive fresh dynamic plans.
    """

    CONTRACT = "rtdl.fixed_radius_graph.prepared_compiler_context.v1"

    def __init__(
        self,
        *,
        compiled: CompiledAction,
        target_profile: ActionTargetProfile,
        refinement_evidence: VerifiedFixedRadiusGraphRefinementEvidence,
        refinement_certificates: tuple[ActionPhysicalRefinementCertificate, ...],
        runtime_capability: Mapping[str, object],
        native_library_identity: ActionNativeLibraryIdentity | None,
        native_library_ref: object | None,
        default_proof_authority: object,
        _constructor_token: object,
    ) -> None:
        if _constructor_token is not _PREPARED_CONTEXT_CONSTRUCTOR_TOKEN:
            raise TypeError("prepared fixed-radius contexts are compiler-owned")
        self._compiled = compiled
        self._target_profile = target_profile
        self._refinement_evidence = refinement_evidence
        self._refinement_evidence_source = _freeze_json_value(
            refinement_evidence.to_source_receipt()
        )
        self._refinement_certificates = tuple(refinement_certificates)
        self._runtime_capability = _freeze_json_value(
            json.loads(json.dumps(runtime_capability))
        )
        self._native_library_identity = native_library_identity
        self._native_library_ref = native_library_ref
        self._default_proof_authority = default_proof_authority
        self._compiled_object_id = id(compiled)
        self._target_profile_object_id = id(target_profile)
        self._native_library_object_id = (
            id(native_library_ref) if native_library_ref is not None else None
        )
        self._default_proof_authority_object_id = id(default_proof_authority)
        self._process_id = os.getpid()
        self._nonce = secrets.token_hex(32)
        self._closed = False
        public = {
            "contract": self.CONTRACT,
            "semantic_digest": self._compiled.spec.semantic_digest,
            "target_profile": self._target_profile.to_metadata(),
            "refinement_evidence": self._refinement_evidence.to_metadata(),
            "refinement_evidence_source": _thaw_json_value(
                self._refinement_evidence_source
            ),
            "refinement_certificates": [
                item.to_dict() for item in self._refinement_certificates
            ],
            "runtime_capability": _thaw_json_value(self._runtime_capability),
            "native_library_identity": (
                self._native_library_identity.to_metadata()
                if self._native_library_identity is not None
                else None
            ),
            "compiled_object_id": self._compiled_object_id,
            "target_profile_object_id": self._target_profile_object_id,
            "native_library_object_id": self._native_library_object_id,
            "default_proof_authority": default_proof_authority.to_metadata(),
            "default_proof_authority_object_id": (
                self._default_proof_authority_object_id
            ),
            "process_id": self._process_id,
            "nonce": self._nonce,
        }
        self._static_metadata_json = json.dumps(
            public, sort_keys=True, separators=(",", ":")
        )
        self._identity_digest = hashlib.sha256(
            self._static_metadata_json.encode("utf-8")
        ).hexdigest()
        self._signature = hmac.new(
            _PREPARED_CONTEXT_SECRET,
            json.dumps(
                self._live_seal_payload(), sort_keys=True, separators=(",", ":")
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @property
    def compiled(self) -> CompiledAction:
        return self._compiled

    @property
    def target_profile(self) -> ActionTargetProfile:
        return self._target_profile

    @property
    def refinement_evidence(self) -> VerifiedFixedRadiusGraphRefinementEvidence:
        return self._refinement_evidence

    @property
    def refinement_evidence_source(self) -> Mapping[str, object]:
        return self._refinement_evidence_source

    @property
    def refinement_certificates(
        self,
    ) -> tuple[ActionPhysicalRefinementCertificate, ...]:
        return self._refinement_certificates

    @property
    def runtime_capability(self) -> Mapping[str, object]:
        return self._runtime_capability

    @property
    def native_library_identity(self) -> ActionNativeLibraryIdentity | None:
        return self._native_library_identity

    @property
    def native_library_ref(self) -> object | None:
        return self._native_library_ref

    @property
    def default_proof_authority(self) -> object:
        return self._default_proof_authority

    @property
    def identity_digest(self) -> str:
        return self._identity_digest

    @property
    def closed(self) -> bool:
        return self._closed

    def _live_seal_payload(self) -> dict[str, object]:
        return {
            "contract": self.CONTRACT,
            "semantic_digest": self._compiled.spec.semantic_digest,
            "identity_digest": self._identity_digest,
            "compiled_object_id": self._compiled_object_id,
            "target_profile_object_id": self._target_profile_object_id,
            "native_library_object_id": self._native_library_object_id,
            "default_proof_authority_object_id": (
                self._default_proof_authority_object_id
            ),
            "default_proof_authority_identity": (
                self._default_proof_authority.identity_digest
            ),
            "process_id": self._process_id,
            "nonce": self._nonce,
        }

    def _require_live(self) -> None:
        if self._closed:
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context is closed"
            )
        if os.getpid() != self._process_id:
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context crossed a process boundary"
            )
        if (
            id(self._compiled) != self._compiled_object_id
            or id(self._target_profile) != self._target_profile_object_id
            or self._compiled.spec.semantic_digest
            != _CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST
        ):
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context identity drifted"
            )
        if id(self._default_proof_authority) != self._default_proof_authority_object_id:
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context proof authority drifted"
            )
        try:
            from .default_physical_selection import current_registry_snapshot

            self._default_proof_authority.require_live(
                registry=current_registry_snapshot(),
                repository_root=Path(__file__).resolve().parents[2],
            )
        except Exception as exc:
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context proof authority failed"
            ) from exc
        expected_signature = hmac.new(
            _PREPARED_CONTEXT_SECRET,
            json.dumps(
                self._live_seal_payload(), sort_keys=True, separators=(",", ":")
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(self._signature, expected_signature):
            raise FixedRadiusGraphPlanningError(
                "prepared fixed-radius compiler context seal is invalid"
            )
        if self._native_library_identity is None:
            if self._native_library_ref is not None or self._native_library_object_id is not None:
                raise FixedRadiusGraphPlanningError(
                    "prepared fixed-radius compiler context native binding drifted"
                )
        else:
            if (
                self._native_library_ref is None
                or id(self._native_library_ref) != self._native_library_object_id
            ):
                raise FixedRadiusGraphPlanningError(
                    "prepared fixed-radius compiler context native object changed"
                )
            try:
                _validate_loaded_fixed_radius_native_binding(
                    self._native_library_ref,
                    self._native_library_identity,
                )
            except Exception as exc:
                raise FixedRadiusGraphPlanningError(
                    "prepared fixed-radius compiler context native binding failed"
                ) from exc

    def to_metadata(self) -> dict[str, object]:
        self._require_live()
        public = json.loads(self._static_metadata_json)
        return {
            **public,
            "identity_digest": self._identity_digest,
            "closed": False,
            "full_evidence_validation_per_batch": False,
            "full_native_binary_hash_per_batch": False,
            "full_static_metadata_serialization_per_batch": False,
            "dynamic_input_plan_per_batch": True,
        }

    def close(self) -> None:
        self._default_proof_authority.close()
        self._closed = True


@dataclass(frozen=True)
class FixedRadiusGraphCandidate:
    producer_kind: str
    backend: str
    legal: bool
    rejection_reasons: tuple[str, ...]
    structural_work_units: int
    structural_work_terms: Mapping[str, int]
    predicted_output_bytes: int
    priority: int

    def to_metadata(self) -> dict[str, object]:
        return {
            "producer_kind": self.producer_kind,
            "backend": self.backend,
            "legal": self.legal,
            "rejection_reasons": list(self.rejection_reasons),
            "structural_work_units": self.structural_work_units,
            "structural_work_terms": dict(self.structural_work_terms),
            "predicted_output_bytes": self.predicted_output_bytes,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class RegisteredFixedRadiusGraphPlan:
    compiled: CompiledAction = field(repr=False)
    target_profile: ActionTargetProfile = field(repr=False)
    semantic_digest: str
    point_count: int
    input_dimension: int
    spatial_execution_dimension: int
    spatial_zero_z_lift_required: bool
    input_digest: str
    parameter_digest: str
    radius_f32: float
    radius_sq_f32: float
    min_neighbors: int
    candidate_density_upper_bound: float
    predicted_candidate_count: int
    candidates: tuple[FixedRadiusGraphCandidate, ...]
    selected_producer_kind: str
    selected_backend: str
    selection_reason: str
    runtime_capability: Mapping[str, object]
    refinement_evidence: VerifiedFixedRadiusGraphRefinementEvidence
    refinement_certificates: tuple[ActionPhysicalRefinementCertificate, ...]
    native_library_identity: ActionNativeLibraryIdentity | None
    native_library_object_id: int | None
    prepared_context_identity_digest: str
    prepared_context_object_id: int
    production_default_plan: Mapping[str, object] | None
    production_default_binding: Mapping[str, object] | None
    canonical_resolution: Mapping[str, object] | None
    canonical_production_authority: Mapping[str, object] | None
    _prepared_context_ref: PreparedFixedRadiusGraphContext = field(
        repr=False, compare=False
    )
    _native_library_ref: object | None = field(repr=False, compare=False)
    _signature: str = field(repr=False)

    def to_invocation_receipt(self) -> dict[str, object]:
        """Return the constant-size dynamic plan receipt for one batch.

        Static evidence, target, capability, and certificate trees are exposed
        once through ``PreparedFixedRadiusGraphContext.to_metadata()``.  The
        hot result path binds them by the sealed context digest instead of
        reconstructing them with per-batch multiplicity.
        """

        return {
            "contract": FIXED_RADIUS_GRAPH_COMPILER_VERSION,
            "metadata_scope": "compact_dynamic_invocation_receipt.v1",
            "semantic_digest": self.semantic_digest,
            "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
            "point_count": self.point_count,
            "input_dimension": self.input_dimension,
            "spatial_execution_dimension": self.spatial_execution_dimension,
            "spatial_zero_z_lift_required": self.spatial_zero_z_lift_required,
            "input_digest": self.input_digest,
            "parameter_digest": self.parameter_digest,
            "radius_f32": self.radius_f32,
            "radius_sq_f32": self.radius_sq_f32,
            "min_neighbors": self.min_neighbors,
            "candidate_density_upper_bound": self.candidate_density_upper_bound,
            "predicted_candidate_count": self.predicted_candidate_count,
            "spatial_component_point_bound": _MAX_SPATIAL_COMPONENT_POINTS,
            "structural_cost_model": {
                "candidate_density_feature_acquired": False,
                "candidate_upper_bound_policy": (
                    "worst_case_all_ordered_pairs_without_input_scan"
                ),
                "structural_work_used_for_selection": False,
                "runtime_calibration_used": False,
            },
            "candidates": [candidate.to_metadata() for candidate in self.candidates],
            "selected_producer_kind": self.selected_producer_kind,
            "selected_backend": self.selected_backend,
            "selection_reason": self.selection_reason,
            "production_default_plan": _thaw_json_value(
                self.production_default_plan
            ),
            "production_default_binding": _thaw_json_value(
                self.production_default_binding
            ),
            "canonical_resolution": _thaw_json_value(self.canonical_resolution),
            "canonical_production_authority": _thaw_json_value(
                self.canonical_production_authority
            ),
            "prepared_context_identity_digest": (
                self.prepared_context_identity_digest
            ),
            "prepared_context_object_id": self.prepared_context_object_id,
            "refinement_evidence_digest": (
                self.refinement_evidence.artifact_sha256
            ),
            "native_library_identity_digest": (
                self.native_library_identity.identity_digest
                if self.native_library_identity is not None
                else None
            ),
            "native_library_object_id": self.native_library_object_id,
            "plan_signature_sha256": hashlib.sha256(
                self._signature.encode("ascii")
            ).hexdigest(),
            "dynamic_input_and_parameters_hmac_bound": True,
            "dynamic_legality_and_selection_hmac_bound": True,
            "static_provenance_bound_by_context_digest": True,
            "expanded_static_provenance_available_on_prepared_context": True,
            "application_supplied_backend": False,
            "application_supplied_cost": False,
            "action_name_used_for_dispatch": False,
            "raw_callback_accepted": False,
            "user_kernel_accepted": False,
            "arbitrary_ptx_accepted": False,
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": FIXED_RADIUS_GRAPH_COMPILER_VERSION,
            "semantic_digest": self.semantic_digest,
            "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
            "boundary_policy": "closed_float32_squared_euclidean_radius",
            "predicate": "float32_distance_sq_lte_float32_radius_sq",
            "distance_arithmetic": FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC,
            "cross_backend_rounding_rule_locked": True,
            "differential_cases_are_not_exhaustive_all_f32_proof": True,
            "neighbor_count_policy": "self_inclusive_min_neighbors",
            "duplicate_coordinate_policy": "distinct_point_ids_preserved",
            "border_assignment_policy": "canonical_lowest_component_label",
            "point_count": self.point_count,
            "input_dimension": self.input_dimension,
            "spatial_execution_dimension": self.spatial_execution_dimension,
            "spatial_zero_z_lift_required": self.spatial_zero_z_lift_required,
            "spatial_zero_z_lift_policy": (
                "compiler_owned_append_exact_float32_positive_zero"
                if self.spatial_zero_z_lift_required
                else "not_required"
            ),
            "input_digest": self.input_digest,
            "parameter_digest": self.parameter_digest,
            "radius_f32": self.radius_f32,
            "radius_sq_f32": self.radius_sq_f32,
            "min_neighbors": self.min_neighbors,
            "candidate_density_upper_bound": self.candidate_density_upper_bound,
            "predicted_candidate_count": self.predicted_candidate_count,
            "structural_cost_model": {
                "contract": FIXED_RADIUS_GRAPH_STRUCTURAL_COST_MODEL,
                "unit": "dimensionless_structural_work",
                "runtime_seconds_predicted": False,
                "runtime_calibration_used": False,
                "hardware_timing_extrapolated": False,
                "complete_pair_event_row_budget": _MAX_COMPLETE_PAIR_EVENT_ROWS,
                "spatial_component_point_bound": (
                    _MAX_SPATIAL_COMPONENT_POINTS
                ),
                "spatial_component_point_bound_reason": (
                    "native_root_resolution_guard_requires_fail_closed_bound"
                ),
                "structural_work_used_for_selection": False,
                "selection_policy": (
                    "compiler_owned_fixed_priority_legal_order_without_"
                    "runtime_calibration"
                ),
                "legal_priority_order": [
                    _SPATIAL_PRODUCER,
                    _COMPLETE_PAIR_PRODUCER,
                ],
                "candidate_density_feature_acquired": False,
                "candidate_upper_bound_policy": (
                    "worst_case_all_ordered_pairs_without_input_scan"
                ),
            },
            "candidates": [candidate.to_metadata() for candidate in self.candidates],
            "selected_producer_kind": self.selected_producer_kind,
            "selected_backend": self.selected_backend,
            "selection_reason": self.selection_reason,
            "runtime_capability": _thaw_json_value(self.runtime_capability),
            "compiler_native_library_identity": (
                self.native_library_identity.to_metadata()
                if self.native_library_identity is not None
                else None
            ),
            "compiler_native_library_object_id": self.native_library_object_id,
            "prepared_compiler_context": {
                "contract": PreparedFixedRadiusGraphContext.CONTRACT,
                "identity_digest": self.prepared_context_identity_digest,
                "process_local": True,
                "full_evidence_validation_per_batch": False,
                "full_native_binary_hash_per_batch": False,
                "dynamic_input_plan_per_batch": True,
            },
            "prepared_context_identity_digest": (
                self.prepared_context_identity_digest
            ),
            "prepared_context_object_id": self.prepared_context_object_id,
            "refinement_certificates": [
                certificate.to_dict() for certificate in self.refinement_certificates
            ],
            "refinement_evidence": self.refinement_evidence.to_metadata(),
            "target_profile": self.target_profile.to_metadata(),
            "legality_checked_before_cost": True,
            "input_and_parameters_bound_to_plan": True,
            "application_supplied_backend": False,
            "application_supplied_cost": False,
            "action_name_used_for_dispatch": False,
            "raw_callback_accepted": False,
            "user_kernel_accepted": False,
            "arbitrary_ptx_accepted": False,
        }


def plan_registered_fixed_radius_graph_components_3d(
    compiled: CompiledAction,
    target_profile: ActionTargetProfile,
    *,
    points,
    radius: float,
    min_neighbors: int,
    prepared_context: PreparedFixedRadiusGraphContext | None = None,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> RegisteredFixedRadiusGraphPlan:
    """Plan a certified fixed-radius graph/component composition.

    Applications provide semantic inputs only.  Backend identities, the
    structural work model, materialization budget, and refinement evidence are
    compiler-owned.
    """

    if not isinstance(compiled, CompiledAction):
        raise TypeError("compiled must be a CompiledAction")
    if not isinstance(target_profile, ActionTargetProfile):
        raise TypeError("target_profile must be compiler-owned ActionTargetProfile facts")
    if compiled.spec.semantic_digest != _CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph registry rejected an unverified Action semantic digest"
        )
    context = (
        prepare_registered_fixed_radius_graph_context(compiled, target_profile)
        if prepared_context is None
        else prepared_context
    )
    if not isinstance(context, PreparedFixedRadiusGraphContext):
        raise TypeError(
            "prepared_context must be a compiler-owned PreparedFixedRadiusGraphContext"
        )
    context._require_live()
    if context.compiled is not compiled or context.target_profile is not target_profile:
        raise FixedRadiusGraphPlanningError(
            "prepared fixed-radius context does not own the supplied compiler facts"
        )
    evidence = context.refinement_evidence
    resolved, radius_f32, radius_sq_f32, resolved_min_neighbors = _normalize_inputs(
        points, radius=radius, min_neighbors=min_neighbors
    )
    point_count = int(resolved.shape[0])
    input_dimension = int(resolved.shape[1])
    # Spatial is the compiler-owned preferred legal route; complete-pair is a
    # fail-closed fallback.  Neither choice needs a data-dependent density
    # estimate.  If fallback output resources must be bounded, all ordered
    # pairs are the only proof-safe upper bound because every pair can satisfy
    # the radius predicate.  Avoid an O(N log N) input scan that has no effect
    # on the selected route or its legality.
    density = 1.0
    predicted_candidates = point_count * point_count
    runtime_capability = context.runtime_capability
    candidates = _build_candidates(
        target_profile,
        runtime_capability=runtime_capability,
        point_count=point_count,
        predicted_candidate_count=predicted_candidates,
    )
    legal = tuple(candidate for candidate in candidates if candidate.legal)
    if not legal:
        details = "; ".join(
            f"{candidate.producer_kind}:{','.join(candidate.rejection_reasons)}"
            for candidate in candidates
        )
        raise FixedRadiusGraphPlanningError(
            f"no legal fixed-radius graph physical producer: {details}"
        )
    production_default_plan: Mapping[str, object] | None = None
    production_default_binding: Mapping[str, object] | None = None
    canonical_resolution: Mapping[str, object] | None = None
    canonical_authority: Mapping[str, object] | None = None
    if target_profile.production_selection_policy == "compiler_owned_default":
        from .default_physical_selection import current_registry_snapshot
        from .production_default_integration import (
            ProductionDefaultIntegrationError,
            _compile_prepared_production_default_plan,
            bind_default_plan_to_lowering,
            make_production_action_descriptor,
            make_production_target_descriptor,
        )

        if target_profile.profile_source != "runtime_capability_probe":
            raise FixedRadiusGraphPlanningError(
                "production DEFAULT requires compiler-probed target facts"
            )
        if target_profile.device_memory_limit_bytes is None:
            raise FixedRadiusGraphPlanningError(
                "production DEFAULT requires an actual device-memory limit"
            )
        providers: set[str] = {"python"}
        if target_profile.optix_available:
            providers.update(("cuda", "cupy", "optix"))
        if target_profile.numba_available:
            providers.add("numba")
        if target_profile.embree_available:
            providers.add("embree")
        try:
            action_descriptor = make_production_action_descriptor(
                semantic_kind="fixed_radius_graph_components_3d.v1",
                action_contract_class="radius_components",
                action_semantic_digest=compiled.spec.semantic_digest,
                output_contract={
                    "logical_output_contract": (
                        FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT
                    ),
                    "point_count": point_count,
                    "canonical_partition_required": True,
                },
                work_domain={
                    "point_count": point_count,
                    "input_dimension": input_dimension,
                    "radius_f32_hex": radius_f32.hex(),
                    "min_neighbors": resolved_min_neighbors,
                    "predicted_candidate_count": predicted_candidates,
                },
                input_bytes=int(resolved.nbytes),
                output_bytes=point_count * _SPATIAL_RESULT_BYTES_PER_POINT,
                prepared_bytes=int(resolved.nbytes),
                logical_cardinality_bound=point_count,
                pair_cardinality_bound=predicted_candidates,
                logical_item_bytes_bound=max(1, input_dimension * 4),
                pair_item_bytes_bound=_EDGE_ROW_BYTES,
            )
            target_descriptor = make_production_target_descriptor(
                target_identity={
                    "target_profile": target_profile.to_metadata(),
                    "semantic_kind": "fixed_radius_graph_components_3d.v1",
                },
                available_providers=providers,
                memory_limit_bytes=target_profile.device_memory_limit_bytes,
                mandatory_nvidia_rt=True,
            )
            if (semantic_statement_stable_id is None) != (
                backend_contract_id is None
            ):
                raise FixedRadiusGraphPlanningError(
                    "canonical semantic statement and backend contract are required together"
                )
            if semantic_statement_stable_id is not None:
                from .canonical_physical_resolution import (
                    CanonicalPhysicalResolutionError,
                    registered_backend_contract,
                    registered_semantic_statement,
                    resolve_canonical_provider,
                )

                statement = registered_semantic_statement(
                    semantic_statement_stable_id
                )
                backend_contract = registered_backend_contract(
                    backend_contract_id
                )
                canonical_resolution = resolve_canonical_provider(
                    statement_stable_id=statement.stable_id,
                    expected_statement_sha256=statement.digest,
                    backend_contract_id=backend_contract.stable_id,
                    expected_backend_contract_sha256=backend_contract.digest,
                    action=action_descriptor,
                    target=target_descriptor,
                )
                if canonical_resolution.get("status") != "RESOLVED":
                    raise CanonicalPhysicalResolutionError(
                        str(canonical_resolution.get("error_code", "FAIL_CLOSED")),
                        str(canonical_resolution.get("error_detail", "")),
                    )
            production_default_plan = _compile_prepared_production_default_plan(
                action_descriptor,
                target_descriptor,
                mandatory_nvidia_rt=True,
                repository_root=Path(__file__).resolve().parents[2],
                prepared_proof_authority=context.default_proof_authority,
            )
        except ProductionDefaultIntegrationError as exc:
            raise FixedRadiusGraphPlanningError(
                f"production DEFAULT failed closed: {exc}"
            ) from exc
        selected_id = production_default_plan["selected_candidate_stable_id"]
        declaration = next(
            row
            for row in current_registry_snapshot().declarations
            if row.stable_id == selected_id
        )
        selected = next(
            (
                candidate
                for candidate in legal
                if candidate.backend == declaration.backend
            ),
            None,
        )
        if selected is None:
            raise FixedRadiusGraphPlanningError(
                "production DEFAULT selected a fixed-radius backend absent "
                "from the live legal candidate set"
            )
        try:
            production_default_binding = bind_default_plan_to_lowering(
                production_default_plan,
                actual_backend=selected.backend,
                actual_template=declaration.template,
                repository_root=Path(__file__).resolve().parents[2],
            )
            if canonical_resolution is not None:
                from .canonical_physical_resolution import (
                    bind_canonical_provider_to_materialized_plan,
                )

                canonical_authority = bind_canonical_provider_to_materialized_plan(
                    canonical_resolution,
                    materialized_provider_stable_id=str(
                        production_default_plan["selected_candidate_stable_id"]
                    ),
                    materialized_plan_sha256=str(
                        production_default_plan["production_plan_sha256"]
                    ),
                    materialized_binding_sha256=str(
                        production_default_binding["binding_sha256"]
                    ),
                )
        except ProductionDefaultIntegrationError as exc:
            raise FixedRadiusGraphPlanningError(
                f"production DEFAULT lowering binding failed: {exc}"
            ) from exc
    else:
        # Legacy validation-only profiles preserve the old fixed priority.
        selected = min(
            legal,
            key=lambda candidate: (
                candidate.priority,
                candidate.structural_work_units,
                candidate.producer_kind,
            ),
        )
    selected_native_identity = (
        context.native_library_identity
        if selected.producer_kind == _SPATIAL_PRODUCER
        else None
    )
    selected_native_ref = (
        context.native_library_ref
        if selected_native_identity is not None
        else None
    )
    if selected.producer_kind == _SPATIAL_PRODUCER and (
        selected_native_identity is None
        or context.native_library_ref is None
    ):
        raise FixedRadiusGraphPlanningError(
            "selected spatial fixed-radius route lacks an exact native library identity"
        )
    certificates = context.refinement_certificates
    input_digest = _point_input_digest(resolved)
    parameter_digest = _parameter_digest(
        radius_f32, radius_sq_f32, resolved_min_neighbors
    )
    unsigned = {
        "semantic_digest": compiled.spec.semantic_digest,
        "point_count": point_count,
        "input_dimension": input_dimension,
        "spatial_execution_dimension": 3,
        "spatial_zero_z_lift_required": input_dimension == 2,
        "input_digest": input_digest,
        "parameter_digest": parameter_digest,
        "radius_f32": radius_f32,
        "radius_sq_f32": radius_sq_f32,
        "min_neighbors": resolved_min_neighbors,
        "candidate_density_upper_bound": density,
        "predicted_candidate_count": predicted_candidates,
        "candidates": [candidate.to_metadata() for candidate in candidates],
        "selected_producer_kind": selected.producer_kind,
        "selected_backend": selected.backend,
        "native_library_identity_digest": (
            selected_native_identity.identity_digest
            if selected_native_identity is not None
            else None
        ),
        "native_library_object_id": (
            id(selected_native_ref) if selected_native_ref is not None else None
        ),
        "prepared_context_identity_digest": context.identity_digest,
        "prepared_context_object_id": id(context),
        "production_default_plan": production_default_plan,
        "production_default_binding": production_default_binding,
        "canonical_resolution": canonical_resolution,
        "canonical_production_authority": canonical_authority,
    }
    signature = hmac.new(
        _PLAN_SECRET,
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return RegisteredFixedRadiusGraphPlan(
        compiled=compiled,
        target_profile=target_profile,
        semantic_digest=compiled.spec.semantic_digest,
        point_count=point_count,
        input_dimension=input_dimension,
        spatial_execution_dimension=3,
        spatial_zero_z_lift_required=input_dimension == 2,
        input_digest=input_digest,
        parameter_digest=parameter_digest,
        radius_f32=radius_f32,
        radius_sq_f32=radius_sq_f32,
        min_neighbors=resolved_min_neighbors,
        candidate_density_upper_bound=density,
        predicted_candidate_count=predicted_candidates,
        candidates=candidates,
        selected_producer_kind=selected.producer_kind,
        selected_backend=selected.backend,
        selection_reason=(
            "compiler_owned_deterministic_default_after_semantic_target_"
            "resource_and_mandatory_optix_legality"
            if production_default_plan is not None
            else "legacy_validation_fixed_priority_after_semantic_target_and_"
            "resource_legality__prepared_spatial_then_complete_pair"
        ),
        runtime_capability=runtime_capability,
        refinement_evidence=evidence,
        refinement_certificates=certificates,
        native_library_identity=selected_native_identity,
        native_library_object_id=(
            id(selected_native_ref) if selected_native_ref is not None else None
        ),
        prepared_context_identity_digest=context.identity_digest,
        prepared_context_object_id=id(context),
        production_default_plan=production_default_plan,
        production_default_binding=production_default_binding,
        canonical_resolution=canonical_resolution,
        canonical_production_authority=canonical_authority,
        _prepared_context_ref=context,
        _native_library_ref=selected_native_ref,
        _signature=signature,
    )


def execute_registered_fixed_radius_graph_components_3d(
    plan: RegisteredFixedRadiusGraphPlan,
    *,
    points,
    radius: float,
    min_neighbors: int,
    trace: ActionPhaseTrace | None = None,
) -> dict[str, object]:
    """Execute exactly the compiler-selected producer after identity recheck."""

    with action_phase(
        trace,
        "binding_certificate",
        label="plan_input_parameter_and_target_identity_recheck",
    ):
        _validate_plan_signature(plan)
        resolved, radius_f32, radius_sq_f32, resolved_min_neighbors = _normalize_inputs(
            points, radius=radius, min_neighbors=min_neighbors
        )
        if int(resolved.shape[0]) != plan.point_count:
            raise FixedRadiusGraphPlanningError(
                "fixed-radius graph point count drifted after planning"
            )
        if _point_input_digest(resolved) != plan.input_digest:
            raise FixedRadiusGraphPlanningError("fixed-radius graph input drifted after planning")
        if int(resolved.shape[1]) != plan.input_dimension:
            raise FixedRadiusGraphPlanningError(
                "fixed-radius graph input dimension drifted after planning"
            )
        if (
            _parameter_digest(
                radius_f32, radius_sq_f32, resolved_min_neighbors
            )
            != plan.parameter_digest
        ):
            raise FixedRadiusGraphPlanningError(
                "fixed-radius graph parameters drifted after planning"
            )
        if plan.selected_producer_kind == _SPATIAL_PRODUCER:
            _revalidate_plan_native_library(plan)
    if plan.selected_producer_kind == _COMPLETE_PAIR_PRODUCER:
        route = _execute_complete_pair_route(
            plan,
            resolved,
            radius_f32=radius_f32,
            radius_sq_f32=radius_sq_f32,
            min_neighbors=resolved_min_neighbors,
            trace=trace,
        )
    elif plan.selected_producer_kind == _SPATIAL_PRODUCER:
        route = _execute_prepared_spatial_route(
            plan,
            resolved,
            radius_f32=radius_f32,
            min_neighbors=resolved_min_neighbors,
            trace=trace,
        )
    else:  # A forged/stale plan never falls back to a different producer.
        raise FixedRadiusGraphPlanningError("fixed-radius graph plan selected an unknown producer")
    plan_receipt = plan.to_invocation_receipt()
    normalized_output = _normalized_evidence_output(route["actual"])
    output_digest = _canonical_json_sha256(normalized_output)
    unsigned_result_receipt = {
        "schema": "rtdl.fixed_radius_graph.dynamic_result_receipt.v1",
        "prepared_context_identity_digest": (
            plan.prepared_context_identity_digest
        ),
        "plan_signature_sha256": plan_receipt["plan_signature_sha256"],
        "input_digest": plan.input_digest,
        "parameter_digest": plan.parameter_digest,
        "selected_producer_kind": plan.selected_producer_kind,
        "selected_backend": plan.selected_backend,
        "point_count": plan.point_count,
        "output_sha256": output_digest,
        "output_complete": True,
    }
    result_signature = hmac.new(
        _PLAN_SECRET,
        json.dumps(
            unsigned_result_receipt, sort_keys=True, separators=(",", ":")
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "contract": FIXED_RADIUS_GRAPH_COMPILER_VERSION,
        "actual": route["actual"],
        "selected_producer_kind": plan.selected_producer_kind,
        "selected_backend": plan.selected_backend,
        "compiler_plan": plan_receipt,
        "invocation_receipt": {
            **unsigned_result_receipt,
            "result_hmac": result_signature,
        },
        "route_metadata": route["metadata"],
        "application_selected_backend": False,
        "application_supplied_cost": False,
    }


def execute_fixed_radius_graph_refinement_evidence_routes(
    compiled: CompiledAction,
    target_profile: ActionTargetProfile,
    *,
    points,
    radius: float,
    min_neighbors: int,
    evidence_case_id: str,
    evidence_source_identity: Mapping[str, str],
) -> dict[str, object]:
    """Execute both exact registered implementations for evidence creation.

    This is not a placement front door and issues no plan or certificate.  It
    exists only to break the legitimate bootstrap cycle: successor evidence
    must execute both implementations before the compiler can trust that
    evidence and start selecting between them.
    """

    if not isinstance(compiled, CompiledAction):
        raise TypeError("compiled must be a CompiledAction")
    if not isinstance(target_profile, ActionTargetProfile):
        raise TypeError("target_profile must be compiler-owned ActionTargetProfile facts")
    if compiled.spec.semantic_digest != _CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius evidence bootstrap rejected an unverified Action semantic digest"
        )
    if (
        not isinstance(evidence_case_id, str)
        or not evidence_case_id
        or any(char.isspace() for char in evidence_case_id)
    ):
        raise ValueError("evidence_case_id must be a nonempty identifier")
    source_identity = _validated_evidence_source_identity(
        evidence_source_identity
    )
    resolved, radius_f32, radius_sq_f32, resolved_min_neighbors = _normalize_inputs(
        points, radius=radius, min_neighbors=min_neighbors
    )
    capability_probe = _probe_fixed_radius_graph_runtime_capability(target_profile)
    capability = capability_probe.metadata
    candidates = _build_candidates(
        target_profile,
        runtime_capability=capability,
        point_count=int(resolved.shape[0]),
        predicted_candidate_count=int(resolved.shape[0]) ** 2,
    )
    by_kind = {candidate.producer_kind: candidate for candidate in candidates}
    required = (_COMPLETE_PAIR_PRODUCER, _SPATIAL_PRODUCER)
    unavailable = {
        kind: by_kind[kind].rejection_reasons
        for kind in required
        if not by_kind[kind].legal
    }
    if unavailable:
        raise FixedRadiusGraphPlanningError(
            "both exact fixed-radius evidence routes are required: "
            + json.dumps(unavailable, sort_keys=True)
        )
    if (
        capability_probe.native_library_identity is None
        or capability_probe._native_library_ref is None
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius evidence execution lacks an exact native library identity"
        )
    context = _FixedRadiusGraphRefinementExecutionContext(
        compiled=compiled,
        target_profile=target_profile,
        point_count=int(resolved.shape[0]),
        input_dimension=int(resolved.shape[1]),
        spatial_zero_z_lift_required=int(resolved.shape[1]) == 2,
        native_library_identity=capability_probe.native_library_identity,
        _native_library_ref=capability_probe._native_library_ref,
    )
    complete = _execute_complete_pair_route(
        context,
        resolved,
        radius_f32=radius_f32,
        radius_sq_f32=radius_sq_f32,
        min_neighbors=resolved_min_neighbors,
        trace=None,
    )
    spatial = _execute_prepared_spatial_route(
        context,
        resolved,
        radius_f32=radius_f32,
        min_neighbors=resolved_min_neighbors,
        trace=None,
    )
    input_digest = _point_input_digest(resolved)
    parameter_digest = _parameter_digest(
        radius_f32,
        radius_sq_f32,
        resolved_min_neighbors,
    )
    execution_nonce = secrets.token_hex(32)
    compiler_source_sha256 = _sha256_file(Path(__file__).resolve())
    capability_digest = _canonical_json_sha256(capability)
    executable_identities = fixed_radius_graph_executable_identity_digests()
    execution_receipts = {
        _COMPLETE_PAIR_PRODUCER: _route_execution_receipt(
            evidence_case_id=evidence_case_id,
            execution_nonce=execution_nonce,
            route_name=_COMPLETE_PAIR_PRODUCER,
            route=complete,
            semantic_digest=compiled.spec.semantic_digest,
            input_digest=input_digest,
            parameter_digest=parameter_digest,
            executable_identity_digest=(
                executable_identities[_COMPLETE_PAIR_PRODUCER]
            ),
            compiler_source_sha256=compiler_source_sha256,
            evidence_source_identity=source_identity,
            runtime_capability_digest=capability_digest,
            native_library_identity=None,
        ),
        _SPATIAL_PRODUCER: _route_execution_receipt(
            evidence_case_id=evidence_case_id,
            execution_nonce=execution_nonce,
            route_name=_SPATIAL_PRODUCER,
            route=spatial,
            semantic_digest=compiled.spec.semantic_digest,
            input_digest=input_digest,
            parameter_digest=parameter_digest,
            executable_identity_digest=executable_identities[_SPATIAL_PRODUCER],
            compiler_source_sha256=compiler_source_sha256,
            evidence_source_identity=source_identity,
            runtime_capability_digest=capability_digest,
            native_library_identity=capability_probe.native_library_identity,
        ),
    }
    return {
        "contract": "rtdl.fixed_radius_graph.refinement_evidence_execution.v2",
        "semantic_digest": compiled.spec.semantic_digest,
        "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
        "input_dimension": int(resolved.shape[1]),
        "complete_pair": complete,
        "prepared_spatial": spatial,
        "runtime_capability": capability,
        "runtime_capability_digest": capability_digest,
        "native_library_identity": (
            capability_probe.native_library_identity.to_metadata()
        ),
        "compiler_source_sha256": compiler_source_sha256,
        "evidence_source_identity": source_identity,
        "executable_identity_digests": executable_identities,
        "execution_receipts": execution_receipts,
        "placement_plan_issued": False,
        "runtime_claim_authorized": False,
    }


def _probe_fixed_radius_graph_runtime_capability(
    target_profile: ActionTargetProfile,
) -> _FixedRadiusGraphRuntimeCapabilityProbe:
    native_probe: ActionNativeTemplateSymbolProbe | None = None
    if target_profile.optix_available:
        optix = probe_optix_fixed_radius_graph_components_3d()
        native_probe = probe_native_template_symbols(
            FIXED_RADIUS_GRAPH_COMPONENTS_3D_REQUIRED_SYMBOLS
        )
        optix = dict(optix)
        optix["native_template_probe"] = native_probe.to_metadata()
        optix["native_library_identity"] = (
            native_probe.library_identity.to_metadata()
            if native_probe.library_identity is not None
            else None
        )
        optix["available"] = bool(optix.get("available")) and bool(
            native_probe.available
        )
        if (
            native_probe.library_identity is not None
            and str(Path(str(optix.get("library_path", ""))).resolve())
            != native_probe.library_identity.resolved_path
        ):
            optix["available"] = False
            optix["error"] = "native_capability_probe_resolved_different_library"
        if not native_probe.available:
            optix["missing_symbols"] = list(native_probe.missing_symbols)
            optix["error"] = native_probe.error
    else:
        optix = {
            "contract": "rtdl.optix.fixed_radius_graph_components_3d.capability.v1",
            "available": False,
            "required_symbols": [],
            "present_symbols": [],
            "missing_symbols": [],
            "library_loaded": False,
            "error": "coarse target profile reports optix unavailable",
        }
    if target_profile.numba_available:
        numba = probe_numba_radius_graph_continuation_3d()
    else:
        numba = {
            "contract": "rtdl.numba.radius_graph_continuation_3d.capability.v1",
            "available": False,
            "cuda_is_available": False,
            "current_context_established": False,
            "required_dtypes_allocated": [],
            "error": "coarse target profile reports numba unavailable",
        }
    metadata = {
        "contract": "rtdl.fixed_radius_graph.runtime_capability_preflight.v1",
        "optix_fixed_radius_graph": json.loads(json.dumps(optix)),
        "numba_radius_graph_continuation": json.loads(json.dumps(numba)),
        "coarse_target_profile_only": False,
        "exact_native_symbols_checked": True,
        "actual_numba_cuda_stack_checked": True,
        "exact_native_binary_identity_checked": bool(
            native_probe is not None and native_probe.library_identity is not None
        ),
    }
    return _FixedRadiusGraphRuntimeCapabilityProbe(
        metadata=metadata,
        native_library_identity=(
            native_probe.library_identity if native_probe is not None else None
        ),
        _native_library_ref=(
            native_probe.library_ref if native_probe is not None else None
        ),
    )


def _build_candidates(
    target_profile: ActionTargetProfile,
    *,
    runtime_capability: Mapping[str, object],
    point_count: int,
    predicted_candidate_count: int,
) -> tuple[FixedRadiusGraphCandidate, ...]:
    pair_rows = point_count * point_count
    complete_output_bytes = predicted_candidate_count * _EDGE_ROW_BYTES
    spatial_output_bytes = point_count * _SPATIAL_RESULT_BYTES_PER_POINT

    complete_rejections = []
    if not target_profile.numba_available:
        complete_rejections.append("numba_unavailable")
    numba_capability = runtime_capability["numba_radius_graph_continuation"]
    if not bool(numba_capability["available"]):
        complete_rejections.append("numba_cuda_stack_unavailable")
    if pair_rows > _MAX_COMPLETE_PAIR_EVENT_ROWS:
        complete_rejections.append("complete_pair_event_row_budget_exceeded")
    if (
        target_profile.max_output_bytes is not None
        and complete_output_bytes > target_profile.max_output_bytes
    ):
        complete_rejections.append("bounded_edge_output_resource_exceeded")
    complete_terms = {
        "distance_evaluations": pair_rows,
        "event_column_materializations": pair_rows,
        "predicted_edge_projection_rows": predicted_candidate_count,
    }

    spatial_rejections = []
    if not target_profile.optix_available:
        spatial_rejections.append("optix_unavailable")
    if not target_profile.numba_available:
        spatial_rejections.append("numba_continuation_unavailable")
    optix_capability = runtime_capability["optix_fixed_radius_graph"]
    if not bool(optix_capability["available"]):
        missing = tuple(optix_capability.get("missing_symbols", ()))
        spatial_rejections.append(
            "optix_fixed_radius_graph_symbols_missing"
            + (":" + ",".join(str(item) for item in missing) if missing else "")
        )
    if not bool(numba_capability["available"]):
        spatial_rejections.append("numba_radius_graph_continuation_unavailable")
    if point_count > _MAX_SPATIAL_COMPONENT_POINTS:
        spatial_rejections.append(
            "spatial_component_root_resolution_bound_exceeded"
        )
    if (
        target_profile.max_output_bytes is not None
        and spatial_output_bytes > target_profile.max_output_bytes
    ):
        spatial_rejections.append("component_column_output_resource_exceeded")
    spatial_terms = {
        "fixed_prepared_setup": _SPATIAL_FIXED_SETUP_WORK,
        "point_index_build": 4 * point_count,
        "candidate_traversal_upper_bound": predicted_candidate_count,
        "component_state_and_projection": 3 * point_count,
    }
    return (
        FixedRadiusGraphCandidate(
            producer_kind=_COMPLETE_PAIR_PRODUCER,
            backend=_COMPLETE_PAIR_BACKEND,
            legal=not complete_rejections,
            rejection_reasons=tuple(complete_rejections),
            structural_work_units=sum(complete_terms.values()),
            structural_work_terms=complete_terms,
            predicted_output_bytes=complete_output_bytes,
            priority=1,
        ),
        FixedRadiusGraphCandidate(
            producer_kind=_SPATIAL_PRODUCER,
            backend=_SPATIAL_BACKEND,
            legal=not spatial_rejections,
            rejection_reasons=tuple(spatial_rejections),
            structural_work_units=sum(spatial_terms.values()),
            structural_work_terms=spatial_terms,
            predicted_output_bytes=spatial_output_bytes,
            priority=0,
        ),
    )


def _refinement_certificates(
    compiled: CompiledAction,
    evidence: VerifiedFixedRadiusGraphRefinementEvidence,
    *,
    native_library_identity: ActionNativeLibraryIdentity | None,
) -> tuple[ActionPhysicalRefinementCertificate, ...]:
    # Fresh runtime processes have already re-hashed every complete source file
    # represented by the executable dependency inventory before constructing
    # ``evidence`` from the materializer-issued capsule.  Re-running
    # ``inspect.getsource`` here would replay a second, weaker spelling of the
    # same static proof inside every complete endpoint.  Consume the immutable
    # identities carried by that verified evidence instead.  Materialization
    # remains the only place that derives these identities from function
    # source, and any source-file drift still fails closed in
    # ``_verified_refinement_evidence_from_capsule``.
    identities = dict(evidence.executable_identity_digests)
    complete_identity = identities[_COMPLETE_PAIR_PRODUCER]
    spatial_identity = identities[_SPATIAL_PRODUCER]
    return (
        issue_action_physical_refinement_certificate(
            compiled.spec,
            logical_output_contract=FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
            refinement_scope=FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE,
            producer_kind=_COMPLETE_PAIR_PRODUCER,
            backend=_COMPLETE_PAIR_BACKEND,
            executable_identity_digest=complete_identity,
            differential_evidence_digest=evidence.artifact_sha256,
            independent_reference_digest=evidence.independent_reference_digest,
            verified_case_count=evidence.verified_case_count,
            native_library_identity_digest=None,
        ),
        issue_action_physical_refinement_certificate(
            compiled.spec,
            logical_output_contract=FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
            refinement_scope=FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE,
            producer_kind=_SPATIAL_PRODUCER,
            backend=_SPATIAL_BACKEND,
            executable_identity_digest=spatial_identity,
            differential_evidence_digest=evidence.artifact_sha256,
            independent_reference_digest=evidence.independent_reference_digest,
            verified_case_count=evidence.verified_case_count,
            native_library_identity_digest=(
                native_library_identity.identity_digest
                if native_library_identity is not None
                else None
            ),
        ),
    )


def prepare_registered_fixed_radius_graph_context(
    compiled: CompiledAction,
    target_profile: ActionTargetProfile,
) -> PreparedFixedRadiusGraphContext:
    """Establish input-independent fixed-radius trust and capability once."""

    if not isinstance(compiled, CompiledAction):
        raise TypeError("compiled must be a CompiledAction")
    if not isinstance(target_profile, ActionTargetProfile):
        raise TypeError("target_profile must be compiler-owned ActionTargetProfile facts")
    if compiled.spec.semantic_digest != _CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph registry rejected an unverified Action semantic digest"
        )
    capability_probe = _probe_fixed_radius_graph_runtime_capability(target_profile)
    current_native = capability_probe.native_library_identity
    from .default_compiler_frontdoor import (
        install_default_program_proof_capsule,
        prepare_default_proof_authority,
    )
    from .default_physical_selection import (
        OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
        current_registry_snapshot,
    )

    registry = current_registry_snapshot()
    default_candidate_ids = tuple(
        row.stable_id
        for row in registry.declarations
        if row.semantic_kind == "fixed_radius_graph_components_3d.v1"
        and "radius_components" in row.accepted_action_contract_classes
        and OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in row.physical_capabilities
    )
    repository_root = Path(__file__).resolve().parents[2]
    capsule_fields = {
        "path": os.environ.get("RTDL_DEFAULT_PROGRAM_PROOF_CAPSULE"),
        "capsule_sha256": os.environ.get(
            "RTDL_DEFAULT_PROGRAM_PROOF_CAPSULE_SHA256"
        ),
        "source_archive_sha256": os.environ.get(
            "RTDL_EXECUTION_SOURCE_ARCHIVE_SHA256"
        ),
        "source_tree_digest": os.environ.get("RTDL_EXECUTION_SOURCE_TREE_DIGEST"),
        "native_source_tree_digest": os.environ.get(
            "RTDL_NATIVE_SOURCE_TREE_DIGEST"
        ),
    }
    if any(value is not None for value in capsule_fields.values()):
        if any(not isinstance(value, str) or not value for value in capsule_fields.values()):
            raise FixedRadiusGraphPlanningError(
                "DEFAULT program proof capsule environment is incomplete"
            )
        capsule_path = Path(str(capsule_fields["path"])).resolve(strict=True)
        capsule = json.loads(capsule_path.read_text(encoding="utf-8"))
        if capsule.get("capsule_sha256") != capsule_fields["capsule_sha256"]:
            raise FixedRadiusGraphPlanningError(
                "DEFAULT program proof capsule plan binding mismatched"
            )
        if current_native is None:
            raise FixedRadiusGraphPlanningError(
                "DEFAULT program proof capsule requires a loaded native identity"
            )
        try:
            default_proof_authority = install_default_program_proof_capsule(
                capsule,
                repository_root=repository_root,
                expected_source_archive_sha256=str(
                    capsule_fields["source_archive_sha256"]
                ),
                expected_source_tree_digest=str(capsule_fields["source_tree_digest"]),
                expected_native_library_sha256=current_native.binary_sha256,
                expected_native_source_tree_digest=str(
                    capsule_fields["native_source_tree_digest"]
                ),
                candidate_stable_ids=default_candidate_ids,
            )
        except Exception as exc:
            raise FixedRadiusGraphPlanningError(
                "DEFAULT program proof capsule failed closed"
            ) from exc
        composed_source_authority = default_proof_authority
    else:
        default_proof_authority = prepare_default_proof_authority(
            repository_root=repository_root,
            candidate_stable_ids=default_candidate_ids,
        )
        composed_source_authority = None
    evidence = _require_installed_refinement_evidence(
        source_seal_authority=composed_source_authority,
    )
    if current_native is not None and (
        current_native.binary_sha256
        != evidence.native_library_binary_sha256
        or current_native.optix_version != evidence.native_optix_version
        or current_native.required_symbols_digest
        != evidence.native_required_symbols_digest
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence native library changed"
        )
    certificates = _refinement_certificates(
        compiled,
        evidence,
        native_library_identity=capability_probe.native_library_identity,
    )
    context = PreparedFixedRadiusGraphContext(
        compiled=compiled,
        target_profile=target_profile,
        refinement_evidence=evidence,
        refinement_certificates=certificates,
        runtime_capability=capability_probe.metadata,
        native_library_identity=capability_probe.native_library_identity,
        native_library_ref=capability_probe._native_library_ref,
        default_proof_authority=default_proof_authority,
        _constructor_token=_PREPARED_CONTEXT_CONSTRUCTOR_TOKEN,
    )
    context._require_live()
    return context


def _execute_complete_pair_route(
    plan: RegisteredFixedRadiusGraphPlan,
    points: np.ndarray,
    *,
    radius_f32: float,
    radius_sq_f32: float,
    min_neighbors: int,
    trace: ActionPhaseTrace | None,
) -> dict[str, object]:
    with action_phase(trace, "event_producer", label="complete_pair_distance_columns"):
        columns = _complete_pair_event_columns(points)
    with action_phase(
        trace,
        "binding_certificate",
        label="verified_complete_pair_columns_and_compiler_lowering",
    ):
        bound = bind_action_event_columns(
            plan.compiled,
            columns,
            ordering_fields=("source_id", "target_id"),
        )
        planned = compile_bound_action_for_target(
            bound,
            plan.target_profile,
            extents={
                "query_count": plan.point_count,
                "primitive_count": plan.point_count,
            },
            parameters={},
        )
        if planned.lowered.backend != "numba" or planned.lowered.template_kind != "filter_bounded_emit":
            raise FixedRadiusGraphPlanningError(
                "complete-pair producer lowering no longer matches its registered implementation"
            )
    prepared = None
    result = None
    relation_metadata: dict[str, object] = {}
    try:
        with action_phase(trace, "backend_prepare", label="prepare_complete_pair_action_columns"):
            prepared = prepare_bound_numba_action_columns(
                planned.lowered,
                columns,
                {"radius_sq": np.float32(radius_sq_f32)},
            )
        if trace is not None:
            trace.fold_device_operation(
                name="complete_pair_columns_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="Numba preparation owns the upload without an independent timer",
            )
        with action_phase(trace, "execute", label="closed_radius_edge_filter"):
            result = execute_numba_action_continuation(
                prepared,
                extents={
                    "query_count": plan.point_count,
                    "primitive_count": plan.point_count,
                },
            )
        with action_phase(trace, "projection", label="edge_download_and_canonical_components"):
            relation = result.to_host_relation()
            relation_metadata = result.to_metadata()
            actual, component_metadata = _compose_partition(
                relation.rows,
                point_count=plan.point_count,
                min_neighbors=min_neighbors,
            )
    finally:
        with action_phase(trace, "backend_prepare", label="release_complete_pair_action_state"):
            try:
                if result is not None:
                    result.close()
            finally:
                if prepared is not None:
                    prepared.close()
    if trace is not None:
        trace.fold_device_operation(
            name="complete_pair_edges_download",
            kind="device_to_host_transfer",
            folded_into="projection",
            reason="to_host_relation owns the download without an independent timer",
        )
        trace.fold_device_operation(
            name="complete_pair_completion_wait",
            kind="device_synchronization_wait",
            folded_into="projection",
            reason="to_host_relation synchronizes output visibility",
        )
    return {
        "actual": actual,
        "metadata": {
            "producer_kind": _COMPLETE_PAIR_PRODUCER,
            "backend": _COMPLETE_PAIR_BACKEND,
            "candidate_row_count": plan.point_count * plan.point_count,
            "relation": relation_metadata,
            "component_composition": component_metadata,
            "closed_radius": True,
            "predicate": "float32_distance_sq_lte_float32_radius_sq",
            "input_dimension": plan.input_dimension,
        },
    }


def _execute_prepared_spatial_route(
    plan: RegisteredFixedRadiusGraphPlan,
    points: np.ndarray,
    *,
    radius_f32: float,
    min_neighbors: int,
    trace: ActionPhaseTrace | None,
) -> dict[str, object]:
    if plan.native_library_identity is None or plan._native_library_ref is None:
        raise FixedRadiusGraphPlanningError(
            "spatial fixed-radius route lacks its compiler-bound native owner"
        )
    try:
        _validate_loaded_fixed_radius_native_binding(
            plan._native_library_ref,
            plan.native_library_identity,
        )
    except Exception as exc:
        raise FixedRadiusGraphPlanningError(
            "spatial fixed-radius native identity failed prepare-time revalidation"
        ) from exc
    with action_phase(
        trace,
        "event_producer",
        label="compiler_owned_spatial_zero_z_lift_or_identity",
    ):
        spatial_points = _lift_points_to_spatial_3d(points)
    point_rows = tuple(
        Point3D(id=index, x=float(row[0]), y=float(row[1]), z=float(row[2]))
        for index, row in enumerate(spatial_points)
    )
    prepared = None
    try:
        with action_phase(trace, "backend_prepare", label="prepare_spatial_radius_index"):
            prepared = prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
                point_rows,
                radius=radius_f32,
                partner="numba",
                boundary_assignment_policy="single_pass_candidate_root_rebased",
                expected_native_library_identity=plan.native_library_identity,
                expected_native_library_ref=plan._native_library_ref,
            )
        if trace is not None:
            trace.fold_device_operation(
                name="spatial_points_and_index_upload",
                kind="host_to_device_transfer",
                folded_into="backend_prepare",
                reason="prepared spatial construction exposes no independent transfer timer",
            )
        with action_phase(trace, "execute", label="prepared_radius_components"):
            result = radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=min_neighbors,
                return_metadata=True,
            )
        with action_phase(trace, "projection", label="download_and_canonicalize_partition"):
            columns = result["columns"]
            point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
            raw_labels = np.asarray(
                columns["component_labels"].copy_to_host(), dtype=np.int64
            )
            raw_core_flags = np.asarray(
                columns["is_core"].copy_to_host(), dtype=np.int64
            )
            _validate_spatial_columns(
                point_ids,
                raw_labels,
                raw_core_flags,
                point_count=plan.point_count,
            )
            labels = [-1] * plan.point_count
            core_flags = [False] * plan.point_count
            for row_index, point_id in enumerate(point_ids.tolist()):
                labels[int(point_id)] = int(raw_labels[row_index])
                core_flags[int(point_id)] = bool(raw_core_flags[row_index])
            actual = {
                "core_flags": tuple(core_flags),
                "canonical_component_labels": canonical_partition_labels(labels),
            }
            route_metadata = dict(result["metadata"])
    finally:
        with action_phase(trace, "backend_prepare", label="release_spatial_radius_index"):
            if prepared is not None:
                prepared.close()
    if trace is not None:
        trace.fold_device_operation(
            name="spatial_component_columns_download",
            kind="device_to_host_transfer",
            folded_into="projection",
            reason="device component columns expose no independent transfer timer",
        )
        trace.fold_device_operation(
            name="spatial_component_completion_wait",
            kind="device_synchronization_wait",
            folded_into="projection",
            reason="copy_to_host synchronizes component output visibility",
        )
    return {
        "actual": actual,
        "metadata": {
            "producer_kind": _SPATIAL_PRODUCER,
            "backend": _SPATIAL_BACKEND,
            "candidate_rows_materialized": 0,
            "route": route_metadata,
            "closed_radius": True,
            "predicate": "float32_distance_sq_lte_float32_radius_sq",
            "boundary_assignment_policy": "single_pass_candidate_root_rebased",
            "original_input_dimension": plan.input_dimension,
            "spatial_execution_dimension": 3,
            "compiler_owned_zero_z_lift": plan.spatial_zero_z_lift_required,
            "native_library_identity": plan.native_library_identity.to_metadata(),
            "zero_z_lift_semantics": (
                "append_exact_float32_positive_zero_preserves_squared_euclidean_distance"
                if plan.spatial_zero_z_lift_required
                else "identity"
            ),
        },
    }


def _complete_pair_event_columns(points: np.ndarray) -> dict[str, np.ndarray]:
    count = int(points.shape[0])
    source_ids = np.repeat(np.arange(count, dtype=np.uint32), count)
    target_ids = np.tile(np.arange(count, dtype=np.uint32), count)
    delta = np.subtract(
        points[:, None, :], points[None, :, :], dtype=np.float32
    )
    squared = np.multiply(delta, delta, dtype=np.float32)
    distance_sq = np.add(
        squared[:, :, 0], squared[:, :, 1], dtype=np.float32
    )
    if points.shape[1] == 3:
        distance_sq = np.add(
            distance_sq, squared[:, :, 2], dtype=np.float32
        )
    return {
        "source_id": source_ids,
        "target_id": target_ids,
        "distance_sq": np.ascontiguousarray(
            distance_sq.reshape(-1), dtype=np.float32
        ),
    }


def _compose_partition(
    edge_rows,
    *,
    point_count: int,
    min_neighbors: int,
) -> tuple[dict[str, object], dict[str, object]]:
    pairs = tuple((int(row[0]), int(row[1])) for row in edge_rows)
    neighbor_counts = [0] * point_count
    for source_id, target_id in pairs:
        if not (0 <= source_id < point_count and 0 <= target_id < point_count):
            raise FixedRadiusGraphPlanningError("edge producer returned an out-of-range point id")
        neighbor_counts[source_id] += 1
    core_flags = tuple(count >= min_neighbors for count in neighbor_counts)
    partition = predicate_aware_boundary_union_reference(
        point_count=point_count,
        candidate_pairs=pairs,
        predicate_flags=core_flags,
    )
    actual = {
        "core_flags": core_flags,
        "canonical_component_labels": canonical_partition_labels(
            partition["component_labels"]
        ),
    }
    return actual, {
        "edge_count": len(pairs),
        "neighbor_counts": neighbor_counts,
        "partition": partition,
    }


def _validate_spatial_columns(
    point_ids: np.ndarray,
    labels: np.ndarray,
    core_flags: np.ndarray,
    *,
    point_count: int,
) -> None:
    if any(array.ndim != 1 for array in (point_ids, labels, core_flags)):
        raise FixedRadiusGraphPlanningError("spatial producer returned non-vector columns")
    if any(int(array.shape[0]) != point_count for array in (point_ids, labels, core_flags)):
        raise FixedRadiusGraphPlanningError("spatial producer returned incomplete component columns")
    if not np.array_equal(np.sort(point_ids), np.arange(point_count, dtype=np.int64)):
        raise FixedRadiusGraphPlanningError(
            "spatial producer point ids are not one exact permutation"
        )
    if np.any((core_flags != 0) & (core_flags != 1)):
        raise FixedRadiusGraphPlanningError("spatial producer core flags are not boolean")


def _normalize_inputs(
    points,
    *,
    radius: float,
    min_neighbors: int,
) -> tuple[np.ndarray, float, float, int]:
    resolved = np.ascontiguousarray(points, dtype=np.float32)
    if (
        resolved.ndim != 2
        or resolved.shape[0] == 0
        or resolved.shape[1] not in {2, 3}
    ):
        raise ValueError(
            "fixed-radius graph compiler requires a nonempty Nx2 or Nx3 point matrix"
        )
    if not np.all(np.isfinite(resolved)):
        raise ValueError("fixed-radius graph point coordinates must be finite")
    if isinstance(radius, (bool, np.bool_)) or not isinstance(
        radius, (int, float, np.integer, np.floating)
    ):
        raise TypeError("radius must be a finite positive scalar")
    radius_f32 = float(np.float32(radius))
    if not math.isfinite(radius_f32) or radius_f32 <= 0.0:
        raise ValueError("radius must remain finite and positive in float32")
    radius_sq_f32 = float(
        np.multiply(
            np.float32(radius_f32), np.float32(radius_f32), dtype=np.float32
        )
    )
    if not math.isfinite(radius_sq_f32) or radius_sq_f32 <= 0.0:
        raise ValueError(
            "squared radius must remain finite and positive in float32"
        )
    if not isinstance(min_neighbors, (int, np.integer)) or isinstance(
        min_neighbors, (bool, np.bool_)
    ):
        raise TypeError("min_neighbors must be an integer")
    resolved_min_neighbors = int(min_neighbors)
    if resolved_min_neighbors < 1:
        raise ValueError("min_neighbors must be positive")
    return resolved, radius_f32, radius_sq_f32, resolved_min_neighbors


def _lift_points_to_spatial_3d(points: np.ndarray) -> np.ndarray:
    """Return the exact compiler-owned 3-D representation for a 2-D input."""

    resolved = np.ascontiguousarray(points, dtype=np.float32)
    if resolved.ndim != 2 or resolved.shape[1] not in {2, 3}:
        raise ValueError("spatial zero-z lift requires an Nx2 or Nx3 matrix")
    if resolved.shape[1] == 3:
        return resolved
    lifted = np.empty((resolved.shape[0], 3), dtype=np.float32)
    lifted[:, :2] = resolved
    lifted[:, 2] = np.float32(0.0)
    return lifted


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _validated_evidence_source_identity(
    value: Mapping[str, str] | object,
) -> dict[str, str]:
    required = {
        "fixed_radius_graph_compiler_sha256",
        "evidence_generator_sha256",
        "crossover_oracle_module_sha256",
    }
    if not isinstance(value, Mapping) or set(value) != required:
        raise TypeError("evidence source identity must contain the exact source set")
    normalized: dict[str, str] = {}
    for name in sorted(required):
        digest = value[name]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"evidence source identity {name} is not SHA-256")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise ValueError(
                f"evidence source identity {name} is not SHA-256"
            ) from exc
        normalized[name] = digest
    if normalized["fixed_radius_graph_compiler_sha256"] != _sha256_file(
        Path(__file__).resolve()
    ):
        raise ValueError("evidence compiler source identity is not current")
    return normalized


def _normalized_evidence_output(value: Mapping[str, object]) -> dict[str, object]:
    return {
        "canonical_component_labels": [
            int(item) for item in value["canonical_component_labels"]
        ],
        "core_flags": [bool(item) for item in value["core_flags"]],
    }


def _route_execution_receipt(
    *,
    evidence_case_id: str,
    execution_nonce: str,
    route_name: str,
    route: Mapping[str, object],
    semantic_digest: str,
    input_digest: str,
    parameter_digest: str,
    executable_identity_digest: str,
    compiler_source_sha256: str,
    evidence_source_identity: Mapping[str, str],
    runtime_capability_digest: str,
    native_library_identity: ActionNativeLibraryIdentity | None,
) -> dict[str, object]:
    output = _normalized_evidence_output(route["actual"])
    metadata = json.loads(json.dumps(route["metadata"]))
    unsigned = {
        "schema": _REFINEMENT_EXECUTION_RECEIPT_SCHEMA,
        "evidence_case_id": evidence_case_id,
        "execution_nonce": execution_nonce,
        "route_name": route_name,
        "semantic_digest": semantic_digest,
        "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
        "input_digest": input_digest,
        "parameter_digest": parameter_digest,
        "executable_identity_digest": executable_identity_digest,
        "compiler_source_sha256": compiler_source_sha256,
        "evidence_source_identity": dict(evidence_source_identity),
        "evidence_source_identity_sha256": _canonical_json_sha256(
            evidence_source_identity
        ),
        "runtime_capability_digest": runtime_capability_digest,
        "native_library_identity": (
            native_library_identity.to_metadata()
            if native_library_identity is not None
            else None
        ),
        "route_metadata": metadata,
        "route_metadata_sha256": _canonical_json_sha256(metadata),
        "output": output,
        "output_sha256": _canonical_json_sha256(output),
    }
    receipt_sha256 = _canonical_json_sha256(unsigned)
    execution_attestation_hmac = hmac.new(
        _EVIDENCE_EXECUTION_ATTESTATION_SECRET,
        receipt_sha256.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    _LIVE_ISSUED_EVIDENCE_RECEIPTS.add(
        (receipt_sha256, execution_attestation_hmac)
    )
    return {
        **unsigned,
        "receipt_sha256": receipt_sha256,
        "execution_attestation_hmac": execution_attestation_hmac,
    }


def _evidence_reference_output(
    points: np.ndarray,
    *,
    radius_f32: np.float32,
    min_neighbors: int,
) -> dict[str, object]:
    """Recompute the evidence oracle without trusting stored output flags."""

    point_count = int(points.shape[0])
    radius_sq = np.multiply(radius_f32, radius_f32, dtype=np.float32)
    delta = np.subtract(
        points[:, None, :], points[None, :, :], dtype=np.float32
    )
    squared = np.multiply(delta, delta, dtype=np.float32)
    distance_sq = np.add(
        squared[:, :, 0], squared[:, :, 1], dtype=np.float32
    )
    if points.shape[1] == 3:
        distance_sq = np.add(
            distance_sq, squared[:, :, 2], dtype=np.float32
        )
    neighbors = [
        np.flatnonzero(distance_sq[source_id] <= radius_sq)
        .astype(np.int64)
        .tolist()
        for source_id in range(point_count)
    ]
    core_flags = [len(row) >= min_neighbors for row in neighbors]
    parent = list(range(point_count))

    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            following = parent[item]
            parent[item] = root
            item = following
        return root

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for source_id, targets in enumerate(neighbors):
        if not core_flags[source_id]:
            continue
        for target_id in targets:
            if core_flags[target_id]:
                union(source_id, target_id)
    labels = [-1] * point_count
    for point_id, is_core in enumerate(core_flags):
        if is_core:
            labels[point_id] = find(point_id)
        else:
            candidate_roots = {
                find(target_id)
                for target_id in neighbors[point_id]
                if core_flags[target_id]
            }
            if candidate_roots:
                labels[point_id] = min(candidate_roots)
    canonical_map: dict[int, int] = {}
    canonical_labels: list[int] = []
    for label in labels:
        if label < 0:
            canonical_labels.append(-1)
        else:
            canonical_map.setdefault(label, len(canonical_map))
            canonical_labels.append(canonical_map[label])
    return {
        "canonical_component_labels": canonical_labels,
        "core_flags": [bool(value) for value in core_flags],
    }


def _validate_route_execution_receipt(
    receipt: Mapping[str, object],
    *,
    evidence_case_id: str,
    execution_nonce: str,
    route_name: str,
    expected_output: Mapping[str, object],
    route_metadata: Mapping[str, object],
    semantic_digest: str,
    input_digest: str,
    parameter_digest: str,
    executable_identity_digest: str,
    compiler_source_sha256: str,
    evidence_source_identity: Mapping[str, str],
    runtime_capability_digest: str,
    native_library_identity: Mapping[str, object] | None,
    allow_pinned_persisted_evidence: bool,
) -> None:
    if not isinstance(receipt, Mapping):
        raise FixedRadiusGraphPlanningError(
            f"fixed-radius refinement case {evidence_case_id} lacks a raw {route_name} receipt"
        )
    unsigned = dict(receipt)
    execution_attestation_hmac = unsigned.pop(
        "execution_attestation_hmac", None
    )
    receipt_digest = unsigned.pop("receipt_sha256", None)
    # Receipt issuance crosses a JSON evidence boundary.  Recreate that exact
    # boundary here as well: live route metadata may legitimately contain
    # tuples, while the signed receipt contains their JSON list form.
    normalized_route_metadata = json.loads(json.dumps(route_metadata))
    expected = {
        "schema": _REFINEMENT_EXECUTION_RECEIPT_SCHEMA,
        "evidence_case_id": evidence_case_id,
        "execution_nonce": execution_nonce,
        "route_name": route_name,
        "semantic_digest": semantic_digest,
        "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
        "input_digest": input_digest,
        "parameter_digest": parameter_digest,
        "executable_identity_digest": executable_identity_digest,
        "compiler_source_sha256": compiler_source_sha256,
        "evidence_source_identity": dict(evidence_source_identity),
        "evidence_source_identity_sha256": _canonical_json_sha256(
            evidence_source_identity
        ),
        "runtime_capability_digest": runtime_capability_digest,
        "native_library_identity": (
            dict(native_library_identity)
            if native_library_identity is not None
            else None
        ),
        "route_metadata": normalized_route_metadata,
        "route_metadata_sha256": _canonical_json_sha256(
            normalized_route_metadata
        ),
        "output": dict(expected_output),
        "output_sha256": _canonical_json_sha256(expected_output),
    }
    expected_receipt_digest = _canonical_json_sha256(expected)
    if (
        unsigned != expected
        or receipt_digest != expected_receipt_digest
        or not isinstance(execution_attestation_hmac, str)
        or len(execution_attestation_hmac) != 64
    ):
        raise FixedRadiusGraphPlanningError(
            f"fixed-radius refinement case {evidence_case_id} has an invalid {route_name} execution receipt"
        )
    try:
        int(execution_attestation_hmac, 16)
    except ValueError as exc:
        raise FixedRadiusGraphPlanningError(
            f"fixed-radius refinement case {evidence_case_id} has an invalid {route_name} execution attestation"
        ) from exc
    if not allow_pinned_persisted_evidence:
        expected_attestation = hmac.new(
            _EVIDENCE_EXECUTION_ATTESTATION_SECRET,
            expected_receipt_digest.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if (
            not hmac.compare_digest(
                execution_attestation_hmac, expected_attestation
            )
            or (
                expected_receipt_digest,
                execution_attestation_hmac,
            )
            not in _LIVE_ISSUED_EVIDENCE_RECEIPTS
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement case {evidence_case_id} {route_name} receipt was not issued by a live route execution"
            )


def _point_input_digest(points: np.ndarray) -> str:
    if points.dtype != np.dtype(np.float32) or not points.flags.c_contiguous:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph input digest requires C-contiguous float32 points"
        )
    digest = hashlib.sha256(b"rtdl.fixed_radius_graph.points.f32.v1\x00")
    digest.update(int(points.shape[0]).to_bytes(8, "little", signed=False))
    digest.update(int(points.shape[1]).to_bytes(4, "little", signed=False))
    # ``_normalize_inputs`` already owns the C-contiguous float32 contract.
    # Hash that exact buffer directly so the mandatory full-input TOCTOU seal
    # does not allocate a second full-size byte string on every plan/execute.
    byte_view = memoryview(points).cast("B")
    try:
        digest.update(byte_view)
    finally:
        byte_view.release()
    return digest.hexdigest()


def _parameter_digest(
    radius_f32: float,
    radius_sq_f32: float,
    min_neighbors: int,
) -> str:
    digest = hashlib.sha256(b"rtdl.fixed_radius_graph.parameters.v2\x00")
    digest.update(np.float32(radius_f32).tobytes())
    digest.update(np.float32(radius_sq_f32).tobytes())
    digest.update(int(min_neighbors).to_bytes(8, "little", signed=False))
    return digest.hexdigest()


def _implementation_identity(function, *dependencies) -> str:
    digest = hashlib.sha256(b"rtdl.fixed_radius_graph.executable_identity.v2\x00")
    for dependency in (function, *dependencies):
        digest.update(
            inspect.getsource(dependency).replace("\r\n", "\n").encode("utf-8")
        )
        digest.update(b"\x00")
    digest.update(FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT.encode("ascii"))
    return digest.hexdigest()


def _fixed_radius_graph_executable_dependencies(
) -> dict[str, tuple[object, ...]]:
    """Return the single inventory used by proof construction and replay.

    Keeping the dependency objects in one compiler-owned inventory prevents a
    static evidence capsule from omitting executable code that contributes to
    the established per-route identity.
    """

    return {
        _COMPLETE_PAIR_PRODUCER: (
            _execute_complete_pair_route,
            _complete_pair_event_columns,
            _compose_partition,
            bind_action_event_columns,
            compile_bound_action_for_target,
            predicate_aware_boundary_union_reference,
        ),
        _SPATIAL_PRODUCER: (
            _execute_prepared_spatial_route,
            _lift_points_to_spatial_3d,
            prepare_optix_numba_radius_graph_grouped_stream_continuation_3d,
            PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D,
            PreparedOptixFixedRadiusCountThreshold3D,
            radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns,
            native_library_identity,
            _validate_loaded_fixed_radius_native_binding,
            canonical_partition_labels,
        ),
    }


@functools.lru_cache(maxsize=1)
def fixed_radius_graph_executable_identity_digests() -> dict[str, str]:
    """Return the two exact executable identities required by evidence v2."""

    return {
        producer: _implementation_identity(*dependencies)
        for producer, dependencies in (
            _fixed_radius_graph_executable_dependencies().items()
        )
    }


def fixed_radius_graph_executable_dependency_source_sha256(
) -> dict[str, str]:
    """Hash every source file represented by an executable dependency.

    This intentionally hashes complete files.  It is a conservative runtime
    check: an unrelated edit may invalidate a capsule, but no edit in a file
    that contributes executable identity can be silently omitted.
    """

    source_root = Path(__file__).resolve(strict=True).parents[2]
    source_files: set[Path] = set()
    for dependencies in _fixed_radius_graph_executable_dependencies().values():
        for dependency in dependencies:
            source_name = inspect.getsourcefile(dependency)
            if not isinstance(source_name, str) or not source_name:
                raise FixedRadiusGraphPlanningError(
                    "fixed-radius executable dependency has no source file"
                )
            source_path = Path(source_name).resolve(strict=True)
            try:
                source_path.relative_to(source_root)
            except ValueError as exc:
                raise FixedRadiusGraphPlanningError(
                    "fixed-radius executable dependency escaped the source tree"
                ) from exc
            if not source_path.is_file() or source_path.is_symlink():
                raise FixedRadiusGraphPlanningError(
                    "fixed-radius executable dependency source is unsafe"
                )
            source_files.add(source_path)
    return {
        path.relative_to(source_root).as_posix(): _sha256_file(path)
        for path in sorted(source_files, key=lambda item: item.as_posix())
    }


def _require_hex_sha256(value: object, *, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise FixedRadiusGraphPlanningError(f"{label} is not one SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise FixedRadiusGraphPlanningError(
            f"{label} is not one SHA-256"
        ) from exc
    if value != value.lower():
        raise FixedRadiusGraphPlanningError(f"{label} is not canonical")
    return value


def build_fixed_radius_graph_refinement_evidence_capsule(
    evidence: VerifiedFixedRadiusGraphRefinementEvidence,
) -> dict[str, object]:
    """Carry a completed materialization proof into fresh runtime processes."""

    if not isinstance(evidence, VerifiedFixedRadiusGraphRefinementEvidence):
        raise TypeError("evidence must be fully validated refinement evidence")
    expected_identities = fixed_radius_graph_executable_identity_digests()
    if (
        evidence.schema != _REFINEMENT_EVIDENCE_SCHEMA
        or evidence.verified_case_count != _REFINEMENT_EVIDENCE_CASE_COUNT
        or evidence.independent_reference_digest != _INDEPENDENT_REFERENCE_DIGEST
        or dict(evidence.executable_identity_digests) != expected_identities
    ):
        raise FixedRadiusGraphPlanningError(
            "refinement evidence cannot issue the installed static capsule"
        )
    return {
        "schema": _REFINEMENT_EVIDENCE_CAPSULE_SCHEMA,
        "artifact_schema": _REFINEMENT_EVIDENCE_SCHEMA,
        "artifact_sha256": _require_hex_sha256(
            evidence.artifact_sha256,
            label="refinement evidence artifact digest",
        ),
        "verified_case_count": _REFINEMENT_EVIDENCE_CASE_COUNT,
        "independent_reference_digest": _INDEPENDENT_REFERENCE_DIGEST,
        "executable_identity_digests": dict(expected_identities),
        "native_evidence_identity": {
            "binary_sha256": _require_hex_sha256(
                evidence.native_library_binary_sha256,
                label="refinement evidence native binary digest",
            ),
            "optix_version": list(evidence.native_optix_version),
            "required_symbols_digest": _require_hex_sha256(
                evidence.native_required_symbols_digest,
                label="refinement evidence native symbol digest",
            ),
        },
        "dependency_source_sha256": (
            fixed_radius_graph_executable_dependency_source_sha256()
        ),
    }


def _verified_refinement_evidence_from_capsule(
    capsule: object,
    *,
    artifact_sha256: str,
    artifact_path: Path,
    source_seal_authority: object | None = None,
) -> VerifiedFixedRadiusGraphRefinementEvidence:
    if not isinstance(capsule, Mapping):
        raise FixedRadiusGraphPlanningError(
            "installed fixed-radius refinement capsule is missing"
        )
    expected_keys = {
        "schema",
        "artifact_schema",
        "artifact_sha256",
        "verified_case_count",
        "independent_reference_digest",
        "executable_identity_digests",
        "native_evidence_identity",
        "dependency_source_sha256",
    }
    if set(capsule) != expected_keys:
        raise FixedRadiusGraphPlanningError(
            "installed fixed-radius refinement capsule fields differ"
        )
    capsule_artifact_sha256 = _require_hex_sha256(
        capsule.get("artifact_sha256"),
        label="installed refinement capsule artifact digest",
    )
    if (
        capsule.get("schema") != _REFINEMENT_EVIDENCE_CAPSULE_SCHEMA
        or capsule.get("artifact_schema") != _REFINEMENT_EVIDENCE_SCHEMA
        or capsule.get("verified_case_count")
        != _REFINEMENT_EVIDENCE_CASE_COUNT
        or capsule.get("independent_reference_digest")
        != _INDEPENDENT_REFERENCE_DIGEST
        or not hmac.compare_digest(
            capsule_artifact_sha256, artifact_sha256
        )
    ):
        raise FixedRadiusGraphPlanningError(
            "installed fixed-radius refinement capsule identity differs"
        )
    identities = capsule.get("executable_identity_digests")
    if not isinstance(identities, Mapping) or set(identities) != {
        _COMPLETE_PAIR_PRODUCER,
        _SPATIAL_PRODUCER,
    }:
        raise FixedRadiusGraphPlanningError(
            "installed refinement capsule route identities differ"
        )
    normalized_identities = {
        str(producer): _require_hex_sha256(
            digest,
            label=f"installed refinement capsule {producer} identity",
        )
        for producer, digest in identities.items()
    }
    native_evidence = capsule.get("native_evidence_identity")
    if not isinstance(native_evidence, Mapping) or set(native_evidence) != {
        "binary_sha256",
        "optix_version",
        "required_symbols_digest",
    }:
        raise FixedRadiusGraphPlanningError(
            "installed refinement capsule native identity differs"
        )
    native_binary_sha256 = _require_hex_sha256(
        native_evidence.get("binary_sha256"),
        label="installed refinement capsule native binary digest",
    )
    native_symbols_digest = _require_hex_sha256(
        native_evidence.get("required_symbols_digest"),
        label="installed refinement capsule native symbol digest",
    )
    native_version = native_evidence.get("optix_version")
    if (
        not isinstance(native_version, (list, tuple))
        or len(native_version) != 3
        or any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            for value in native_version
        )
    ):
        raise FixedRadiusGraphPlanningError(
            "installed refinement capsule native version differs"
        )
    source_digests = capsule.get("dependency_source_sha256")
    if not isinstance(source_digests, Mapping) or not source_digests:
        raise FixedRadiusGraphPlanningError(
            "installed refinement capsule source identities are missing"
        )
    normalized_source_digests = {
        str(path): _require_hex_sha256(
            digest,
            label=f"installed refinement capsule source {path}",
        )
        for path, digest in source_digests.items()
    }
    source_verification_mode = "runtime_dependency_file_hashes"
    source_seal_tree_digest = None
    if source_seal_authority is None:
        current_source_digests = (
            fixed_radius_graph_executable_dependency_source_sha256()
        )
        if normalized_source_digests != current_source_digests:
            raise FixedRadiusGraphPlanningError(
                "installed refinement capsule executable source changed"
            )
    else:
        from .default_compiler_frontdoor import PreparedDefaultProofAuthority
        from .default_physical_selection import current_registry_snapshot

        if not isinstance(source_seal_authority, PreparedDefaultProofAuthority):
            raise FixedRadiusGraphPlanningError(
                "installed refinement capsule source-seal authority type differs"
            )
        repository_root = Path(__file__).resolve().parents[2]
        consumer_capsule_sha256 = hashlib.sha256(
            json.dumps(
                capsule,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        try:
            composed_proof = source_seal_authority.require_composed_static_proof(
                registry=current_registry_snapshot(),
                repository_root=repository_root,
                proof_id=_REFINEMENT_COMPOSED_SOURCE_PROOF_ID,
                consumer_capsule_sha256=consumer_capsule_sha256,
            )
        except Exception as exc:
            raise FixedRadiusGraphPlanningError(
                "installed refinement capsule source-seal authority failed closed"
            ) from exc
        composed_sources = composed_proof.get("dependency_source_sha256")
        if not isinstance(composed_sources, Mapping) or dict(composed_sources) != normalized_source_digests:
            raise FixedRadiusGraphPlanningError(
                "installed refinement capsule composed source identities differ"
            )
        source_binding = source_seal_authority.require_live_source_seal(
            registry=current_registry_snapshot(),
            repository_root=repository_root,
        )
        source_seal_tree_digest = _require_hex_sha256(
            source_binding.get("source_tree_digest"),
            label="installed refinement capsule source-seal tree digest",
        )
        source_verification_mode = "composed_exact_execution_source_tree_seal"
    return VerifiedFixedRadiusGraphRefinementEvidence(
        artifact_sha256=artifact_sha256,
        schema=_REFINEMENT_EVIDENCE_SCHEMA,
        verified_case_count=_REFINEMENT_EVIDENCE_CASE_COUNT,
        independent_reference_digest=_INDEPENDENT_REFERENCE_DIGEST,
        executable_identity_digests=MappingProxyType(normalized_identities),
        native_library_binary_sha256=native_binary_sha256,
        native_optix_version=tuple(native_version),
        native_required_symbols_digest=native_symbols_digest,
        artifact_path=str(artifact_path.resolve()),
        dependency_source_verification_mode=source_verification_mode,
        source_seal_tree_digest=source_seal_tree_digest,
    )


def _validate_fixed_radius_graph_refinement_evidence_manifest(
    payload: Mapping[str, object],
    *,
    artifact_sha256: str,
    allow_pinned_persisted_evidence: bool,
) -> VerifiedFixedRadiusGraphRefinementEvidence:
    """Validate a successor evidence manifest without trusting prose flags."""

    if not isinstance(artifact_sha256, str) or len(artifact_sha256) != 64:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence artifact digest is invalid"
        )
    try:
        int(artifact_sha256, 16)
    except ValueError as exc:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence artifact digest is invalid"
        ) from exc
    if not isinstance(payload, Mapping):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence payload must be a mapping"
        )
    if payload.get("schema") != _REFINEMENT_EVIDENCE_SCHEMA:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence schema is not installed v4"
        )
    if payload.get("semantic_digest") != _CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence semantic digest mismatch"
        )
    if payload.get("logical_output_contract") != FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence logical contract mismatch"
        )
    if payload.get("distance_arithmetic") != FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence arithmetic contract mismatch"
        )
    if payload.get("refinement_scope") != FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence refinement scope mismatch"
        )
    identities = fixed_radius_graph_executable_identity_digests()
    if payload.get("executable_identity_digests") != identities:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence executable identity mismatch"
        )
    compiler_source_sha256 = _sha256_file(Path(__file__).resolve())
    source_identity = payload.get("source_identity")
    try:
        source_identity = _validated_evidence_source_identity(source_identity)
    except (TypeError, ValueError) as exc:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence source identity mismatch"
        ) from exc
    try:
        native_identity = validate_native_library_identity_metadata(
            payload.get("native_library_identity")
        )
    except (TypeError, ValueError) as exc:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence native library identity is invalid"
        ) from exc
    if tuple(native_identity["required_symbols"]) != (
        FIXED_RADIUS_GRAPH_COMPONENTS_3D_REQUIRED_SYMBOLS
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence native ABI identity differs"
        )
    oracle = payload.get("independent_oracle")
    if not isinstance(oracle, Mapping) or (
        oracle.get("symbol") != _INDEPENDENT_REFERENCE_SYMBOL
        or oracle.get("normalized_source_sha256") != _INDEPENDENT_REFERENCE_DIGEST
        or oracle.get("normalization") != "inspect.getsource_crlf_to_lf_utf8"
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence oracle identity mismatch"
        )
    environment = payload.get("functional_environment")
    capability = (
        environment.get("runtime_capability")
        if isinstance(environment, Mapping)
        else None
    )
    optix_capability = (
        capability.get("optix_fixed_radius_graph")
        if isinstance(capability, Mapping)
        else None
    )
    if not isinstance(capability, Mapping) or (
        capability.get("exact_native_symbols_checked") is not True
        or capability.get("exact_native_binary_identity_checked") is not True
        or capability.get("actual_numba_cuda_stack_checked") is not True
        or not isinstance(optix_capability, Mapping)
        or optix_capability.get("available") is not True
        or optix_capability.get("native_library_identity") != native_identity
        or not isinstance(
            capability.get("numba_radius_graph_continuation"), Mapping
        )
        or capability["numba_radius_graph_continuation"].get("available")
        is not True
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence lacks exact runtime capability proof"
        )
    runtime_capability_digest = _canonical_json_sha256(capability)
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence has no explicit cases"
        )
    seen: set[str] = set()
    dimensions: set[int] = set()
    tags: set[str] = set()
    exact_rounding_counterexample_present = False
    explicit_nx2_zero_z_lift_present = False
    for index, case in enumerate(cases):
        if not isinstance(case, Mapping):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {index} is not a mapping"
            )
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise FixedRadiusGraphPlanningError(
                "fixed-radius refinement evidence case ids must be unique"
            )
        seen.add(case_id)
        case_tags = case.get("tags")
        if not isinstance(case_tags, list) or not all(
            isinstance(item, str) and item for item in case_tags
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks tags"
            )
        tags.update(case_tags)
        case_input = case.get("input")
        if not isinstance(case_input, Mapping):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks input"
            )
        dimension = case_input.get("dimension")
        if dimension not in {2, 3}:
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} has invalid dimension"
            )
        dimensions.add(int(dimension))
        point_bits = case_input.get("points_f32_hex")
        if not isinstance(point_bits, list) or not point_bits:
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks point bits"
            )
        for row in point_bits:
            if not isinstance(row, list) or len(row) != dimension:
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} point shape mismatch"
                )
            for value in row:
                if not isinstance(value, str) or len(value) != 8:
                    raise FixedRadiusGraphPlanningError(
                        f"fixed-radius refinement evidence case {case_id} has invalid float bits"
                    )
                try:
                    int(value, 16)
                except ValueError as exc:
                    raise FixedRadiusGraphPlanningError(
                        f"fixed-radius refinement evidence case {case_id} has invalid float bits"
                    ) from exc
                resolved_value = np.asarray(
                    (int(value, 16),), dtype=np.uint32
                ).view(np.float32)[0]
                if not np.isfinite(resolved_value):
                    raise FixedRadiusGraphPlanningError(
                        f"fixed-radius refinement evidence case {case_id} has non-finite point bits"
                    )
        for name in ("radius_f32_hex", "radius_sq_f32_hex"):
            value = case_input.get(name)
            if not isinstance(value, str) or len(value) != 8:
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} lacks {name}"
                )
            try:
                int(value, 16)
            except ValueError as exc:
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} has invalid {name}"
                ) from exc
        radius_bits = int(str(case_input["radius_f32_hex"]), 16)
        radius_sq_bits = int(str(case_input["radius_sq_f32_hex"]), 16)
        radius_f32 = np.asarray((radius_bits,), dtype=np.uint32).view(np.float32)[0]
        radius_sq_f32 = np.asarray(
            (radius_sq_bits,), dtype=np.uint32
        ).view(np.float32)[0]
        computed_radius_sq = np.multiply(
            radius_f32, radius_f32, dtype=np.float32
        )
        computed_radius_sq_bits = int(
            np.asarray((computed_radius_sq,), dtype=np.float32).view(np.uint32)[0]
        )
        if (
            not np.isfinite(radius_f32)
            or radius_f32 <= np.float32(0.0)
            or not np.isfinite(radius_sq_f32)
            or radius_sq_f32 <= np.float32(0.0)
            or radius_sq_bits != computed_radius_sq_bits
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} has inconsistent radius bits"
            )
        min_neighbors = case_input.get("min_neighbors")
        if (
            not isinstance(min_neighbors, int)
            or isinstance(min_neighbors, bool)
            or min_neighbors < 1
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks min_neighbors"
            )
        point_uints = np.asarray(
            [[int(value, 16) for value in row] for row in point_bits],
            dtype=np.uint32,
        )
        resolved_points = np.ascontiguousarray(
            point_uints.view(np.float32), dtype=np.float32
        )
        input_digest = _point_input_digest(resolved_points)
        parameter_digest = _parameter_digest(
            float(radius_f32),
            float(radius_sq_f32),
            min_neighbors,
        )
        recomputed_reference = _evidence_reference_output(
            resolved_points,
            radius_f32=radius_f32,
            min_neighbors=min_neighbors,
        )
        outputs = case.get("outputs")
        if not isinstance(outputs, Mapping) or set(outputs) != {
            "independent_oracle",
            _COMPLETE_PAIR_PRODUCER,
            _SPATIAL_PRODUCER,
        }:
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks all outputs"
            )
        for route_name, output in outputs.items():
            if not isinstance(output, Mapping) or set(output) != {
                "canonical_component_labels",
                "core_flags",
            }:
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} has invalid {route_name} output"
                )
            labels = output["canonical_component_labels"]
            core_flags = output["core_flags"]
            if (
                not isinstance(labels, list)
                or not isinstance(core_flags, list)
                or len(labels) != len(point_bits)
                or len(core_flags) != len(point_bits)
                or not all(
                    isinstance(value, int) and not isinstance(value, bool)
                    for value in labels
                )
                or not all(isinstance(value, bool) for value in core_flags)
                or not all(-1 <= value < len(point_bits) for value in labels)
            ):
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} has malformed {route_name} output columns"
                )
        normalized_outputs = {
            name: _normalized_evidence_output(value)
            for name, value in outputs.items()
        }
        if (
            any(value != recomputed_reference for value in normalized_outputs.values())
            or case.get("all_exact") is not True
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} is not exact under independent recomputation"
            )
        route_metadata = case.get("route_execution_metadata")
        receipts = case.get("execution_receipts")
        if (
            not isinstance(route_metadata, Mapping)
            or set(route_metadata) != {_COMPLETE_PAIR_PRODUCER, _SPATIAL_PRODUCER}
            or not isinstance(receipts, Mapping)
            or set(receipts) != {_COMPLETE_PAIR_PRODUCER, _SPATIAL_PRODUCER}
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} lacks raw route execution receipts"
            )
        complete_receipt = receipts[_COMPLETE_PAIR_PRODUCER]
        spatial_receipt = receipts[_SPATIAL_PRODUCER]
        nonces = {
            receipt.get("execution_nonce")
            for receipt in (complete_receipt, spatial_receipt)
            if isinstance(receipt, Mapping)
        }
        if (
            len(nonces) != 1
            or not isinstance(next(iter(nonces), None), str)
            or len(next(iter(nonces), "")) != 64
        ):
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} has no shared execution nonce"
            )
        execution_nonce = next(iter(nonces))
        try:
            int(execution_nonce, 16)
        except ValueError as exc:
            raise FixedRadiusGraphPlanningError(
                f"fixed-radius refinement evidence case {case_id} has an invalid execution nonce"
            ) from exc
        for route_name in (_COMPLETE_PAIR_PRODUCER, _SPATIAL_PRODUCER):
            metadata = route_metadata[route_name]
            if not isinstance(metadata, Mapping):
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} has invalid route metadata"
                )
            expected_backend = (
                _COMPLETE_PAIR_BACKEND
                if route_name == _COMPLETE_PAIR_PRODUCER
                else _SPATIAL_BACKEND
            )
            if (
                metadata.get("producer_kind") != route_name
                or metadata.get("backend") != expected_backend
                or metadata.get("predicate")
                != "float32_distance_sq_lte_float32_radius_sq"
                or (
                    route_name == _SPATIAL_PRODUCER
                    and metadata.get("native_library_identity")
                    != native_identity
                )
            ):
                raise FixedRadiusGraphPlanningError(
                    f"fixed-radius refinement evidence case {case_id} route identity is invalid"
                )
            _validate_route_execution_receipt(
                receipts[route_name],
                evidence_case_id=case_id,
                execution_nonce=execution_nonce,
                route_name=route_name,
                expected_output=normalized_outputs[route_name],
                route_metadata=metadata,
                semantic_digest=_CLOSED_RADIUS_EDGE_ACTION_SEMANTIC_DIGEST,
                input_digest=input_digest,
                parameter_digest=parameter_digest,
                executable_identity_digest=identities[route_name],
                compiler_source_sha256=compiler_source_sha256,
                evidence_source_identity=source_identity,
                runtime_capability_digest=runtime_capability_digest,
                native_library_identity=(
                    native_identity if route_name == _SPATIAL_PRODUCER else None
                ),
                allow_pinned_persisted_evidence=(
                    allow_pinned_persisted_evidence
                ),
            )
        if "rounding_counterexample" in case_tags:
            expected_rounding_points = [
                ["00000000", "00000000", "00000000"],
                ["bcb4b2ea", "bc3a8c06", "3c455585"],
            ]
            exact_rounding_counterexample_present = (
                dimension == 3
                and [
                    [str(value).lower() for value in row]
                    for row in point_bits
                ]
                == expected_rounding_points
                and str(case_input["radius_f32_hex"]).lower() == "3ce20659"
                and str(case_input["radius_sq_f32_hex"]).lower() == "3a478f35"
                and min_neighbors == 2
                and outputs["independent_oracle"]
                == {
                    "canonical_component_labels": [-1, -1],
                    "core_flags": [False, False],
                }
            ) or exact_rounding_counterexample_present
        if (
            dimension == 2
            and "nx2" in case_tags
            and "zero_z_lift" in case_tags
        ):
            explicit_nx2_zero_z_lift_present = True
    if (
        dimensions != {2, 3}
        or "rounding_counterexample" not in tags
        or not exact_rounding_counterexample_present
        or not explicit_nx2_zero_z_lift_present
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence lacks exact Nx2/Nx3 or rounding coverage"
        )
    if payload.get("case_count") != len(cases):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence case count mismatch"
        )
    if payload.get("all_cases_exact") is not True:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence is not all exact"
        )
    claim = payload.get("claim_boundary")
    if not isinstance(claim, Mapping) or (
        claim.get("functional_only") is not True
        or claim.get("real_gpu_routes_executed") is not True
        or claim.get("exclusive_gpu_claimed") is not False
        or claim.get("runtime_calibration_authorized") is not False
        or claim.get("recorded_worker_timings_discarded") is not True
        or claim.get("runtime_speedup_claimed") is not False
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius refinement evidence claim boundary is invalid"
        )
    return VerifiedFixedRadiusGraphRefinementEvidence(
        artifact_sha256=artifact_sha256,
        schema=_REFINEMENT_EVIDENCE_SCHEMA,
        verified_case_count=len(cases),
        independent_reference_digest=_INDEPENDENT_REFERENCE_DIGEST,
        executable_identity_digests=identities,
        native_library_binary_sha256=str(native_identity["binary_sha256"]),
        native_optix_version=tuple(native_identity["optix_version"]),
        native_required_symbols_digest=str(
            native_identity["required_symbols_digest"]
        ),
    )


def validate_fixed_radius_graph_refinement_evidence_manifest(
    payload: Mapping[str, object],
    *,
    artifact_sha256: str,
) -> VerifiedFixedRadiusGraphRefinementEvidence:
    """Validate newly generated evidence and require live route attestations."""

    return _validate_fixed_radius_graph_refinement_evidence_manifest(
        payload,
        artifact_sha256=artifact_sha256,
        allow_pinned_persisted_evidence=False,
    )


def _require_installed_refinement_evidence(
    *,
    source_seal_authority: object | None = None,
) -> VerifiedFixedRadiusGraphRefinementEvidence:
    from .fixed_radius_graph_refinement_registry import (
        TRUSTED_REFINEMENT_EVIDENCE_CAPSULE,
        TRUSTED_REFINEMENT_EVIDENCE_DIGEST,
    )

    if TRUSTED_REFINEMENT_EVIDENCE_DIGEST is None:
        raise FixedRadiusGraphPlanningError(
            "successor fixed-radius refinement evidence is not installed; "
            "run and review both exact physical routes before planning"
        )
    path_text = os.environ.get(_REFINEMENT_EVIDENCE_ENV)
    if not path_text:
        raise FixedRadiusGraphPlanningError(
            f"installed fixed-radius refinement evidence requires {_REFINEMENT_EVIDENCE_ENV}"
        )
    path = Path(path_text)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise FixedRadiusGraphPlanningError(
            "installed fixed-radius refinement evidence cannot be read"
        ) from exc
    artifact_sha256 = hashlib.sha256(raw).hexdigest()
    if not hmac.compare_digest(
        artifact_sha256, TRUSTED_REFINEMENT_EVIDENCE_DIGEST
    ):
        raise FixedRadiusGraphPlanningError(
            "installed fixed-radius refinement evidence digest mismatch"
        )
    return _verified_refinement_evidence_from_capsule(
        TRUSTED_REFINEMENT_EVIDENCE_CAPSULE,
        artifact_sha256=artifact_sha256,
        artifact_path=path,
        source_seal_authority=source_seal_authority,
    )


def _validate_plan_signature(plan: RegisteredFixedRadiusGraphPlan) -> None:
    if not isinstance(plan, RegisteredFixedRadiusGraphPlan):
        raise TypeError("plan must be a RegisteredFixedRadiusGraphPlan")
    unsigned = {
        "semantic_digest": plan.semantic_digest,
        "point_count": plan.point_count,
        "input_dimension": plan.input_dimension,
        "spatial_execution_dimension": plan.spatial_execution_dimension,
        "spatial_zero_z_lift_required": plan.spatial_zero_z_lift_required,
        "input_digest": plan.input_digest,
        "parameter_digest": plan.parameter_digest,
        "radius_f32": plan.radius_f32,
        "radius_sq_f32": plan.radius_sq_f32,
        "min_neighbors": plan.min_neighbors,
        "candidate_density_upper_bound": plan.candidate_density_upper_bound,
        "predicted_candidate_count": plan.predicted_candidate_count,
        "candidates": [candidate.to_metadata() for candidate in plan.candidates],
        "selected_producer_kind": plan.selected_producer_kind,
        "selected_backend": plan.selected_backend,
        "native_library_identity_digest": (
            plan.native_library_identity.identity_digest
            if plan.native_library_identity is not None
            else None
        ),
        "native_library_object_id": plan.native_library_object_id,
        "prepared_context_identity_digest": (
            plan.prepared_context_identity_digest
        ),
        "prepared_context_object_id": plan.prepared_context_object_id,
        "production_default_plan": plan.production_default_plan,
        "production_default_binding": plan.production_default_binding,
        "canonical_resolution": plan.canonical_resolution,
        "canonical_production_authority": plan.canonical_production_authority,
    }
    expected = hmac.new(
        _PLAN_SECRET,
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(plan._signature, expected):
        raise FixedRadiusGraphPlanningError("fixed-radius graph compiler plan was forged")
    if plan.compiled.spec.semantic_digest != plan.semantic_digest:
        raise FixedRadiusGraphPlanningError("fixed-radius graph Action semantic identity drifted")
    if (
        not isinstance(plan._prepared_context_ref, PreparedFixedRadiusGraphContext)
        or id(plan._prepared_context_ref) != plan.prepared_context_object_id
        or plan._prepared_context_ref.identity_digest
        != plan.prepared_context_identity_digest
        or plan._prepared_context_ref.compiled is not plan.compiled
        or plan._prepared_context_ref.target_profile is not plan.target_profile
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph prepared compiler context changed after planning"
        )
    context = plan._prepared_context_ref
    if (
        plan.runtime_capability is not context.runtime_capability
        or plan.refinement_evidence is not context.refinement_evidence
        or plan.refinement_certificates is not context.refinement_certificates
        or (
            plan.selected_producer_kind == _SPATIAL_PRODUCER
            and plan.native_library_identity is not context.native_library_identity
        )
        or (
            plan.selected_producer_kind != _SPATIAL_PRODUCER
            and plan.native_library_identity is not None
        )
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph static context facts changed after planning"
        )
    context._require_live()


def _revalidate_plan_native_library(plan: RegisteredFixedRadiusGraphPlan) -> None:
    if plan.native_library_identity is None or plan._native_library_ref is None:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph plan lacks its compiler-bound native owner"
        )
    if (
        plan.native_library_object_id is None
        or id(plan._native_library_ref) != plan.native_library_object_id
    ):
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph compiler-bound native object changed after planning"
        )
    try:
        _validate_loaded_fixed_radius_native_binding(
            plan._native_library_ref,
            plan.native_library_identity,
        )
    except Exception as exc:
        raise FixedRadiusGraphPlanningError(
            "fixed-radius graph native library identity drifted after planning"
        ) from exc


__all__ = (
    "FIXED_RADIUS_GRAPH_COMPILER_VERSION",
    "FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC",
    "FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT",
    "FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE",
    "FIXED_RADIUS_GRAPH_STRUCTURAL_COST_MODEL",
    "FixedRadiusGraphCandidate",
    "FixedRadiusGraphPlanningError",
    "PreparedFixedRadiusGraphContext",
    "RegisteredFixedRadiusGraphPlan",
    "VerifiedFixedRadiusGraphRefinementEvidence",
    "build_fixed_radius_graph_refinement_evidence_capsule",
    "execute_fixed_radius_graph_refinement_evidence_routes",
    "execute_registered_fixed_radius_graph_components_3d",
    "fixed_radius_graph_executable_identity_digests",
    "fixed_radius_graph_executable_dependency_source_sha256",
    "plan_registered_fixed_radius_graph_components_3d",
    "prepare_registered_fixed_radius_graph_context",
    "validate_fixed_radius_graph_refinement_evidence_manifest",
)
