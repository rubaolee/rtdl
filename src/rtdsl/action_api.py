from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from typing import Iterable, Mapping, NoReturn, Sequence

from .action_frontend import RestrictedActionFrontendContract, compile_restricted_action_source
from .action_embree_lowering import (
    ActionEmbreePlacementError,
    compile_embree_aabb_filter_bounded_emit_reference_2d,
)
from .action_interpreter import ActionExecutionResult, execute_action_reference
from .action_host_continuation import (
    compile_host_grouped_i64x2_count_sum,
    prepare_host_grouped_i64x2_count_sum_execution,
)
from .action_ir import (
    ActionScalarKind,
    ActionScalarType,
    ActionTupleType,
    ActionSpec,
    DeliveryEnforcement,
    ExtentKind,
    verify_action_spec,
)
from .action_numba_continuation import (
    ActionPlacementError,
    EagerSpecializedGroupedI64x2PreparedExecution,
    compile_numba_action_continuation,
    compile_numba_certified_query_min_state,
    compile_numba_grouped_i64x2_count_sum,
    compile_numba_order_indexed_grouped_i64x2_count_sum,
    eager_specialize_numba_grouped_i64x2_count_sum,
    prepare_numba_action_columns,
    prepare_numba_grouped_i64x2_count_sum_compiler_snapshot,
    prepare_numba_grouped_i64x2_count_sum_device_columns,
    prepare_numba_grouped_i64x2_count_sum_columns,
)
from .action_native_ordering import probe_grouped_i64x2_native_order
from .action_nearest_state_lowering import compile_certified_nearest_state_3d
from .action_cell_mbr_exact_witness_lowering import (
    CELL_MBR_EXACT_WITNESS_3D_BACKEND,
    CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE,
)
from .action_composition import (
    ActionConsumerCompositionCertificate,
    ActionConsumerCompositionKind,
    ActionConsumerCompositionResources,
    action_template_identity_digest,
    certified_nearest_global_argmax_resources,
    issue_certified_nearest_global_argmax_composition,
    validate_certified_nearest_global_argmax_composition,
)
from .action_native_identity import (
    ActionNativeLibraryIdentity,
    probe_certified_nearest_global_witness_3d,
    probe_certified_nearest_optix_traversal_3d,
    probe_cell_mbr_exact_witness_optix_traversal_3d,
)
from .action_optix_lowering import (
    ActionOptixPlacementError,
    compile_optix_aabb_filter_bounded_emit_2d,
    compile_optix_bounded_selection_3d,
    compile_optix_keyed_i64_sum_3d,
)
from .action_ranked_window_lowering import compile_ranked_distance_window_qk_3d
from .action_candidate_pruned_lowering import (
    compile_candidate_pruned_exact_bounded_selection_3d,
)
from .action_placement import (
    ActionBackendCapability,
    ActionPlacementKind,
    ActionPlacementPlan,
    ActionStateStorage,
    plan_action_placement,
)


ACTION_API_CANDIDATE_VERSION = "rtdl.action_api.private_candidate.v1"
_ACTION_BINDING_SECRET = secrets.token_bytes(32)
_ACTION_PLAN_SECRET = secrets.token_bytes(32)


class ActionProducerKind(str, Enum):
    """Closed compiler-known event sources with no application identity."""

    VERIFIED_LOGICAL_EVENT_COLUMNS = "verified_logical_event_columns.v1"
    PREPARED_POINT_CANDIDATES_3D = "prepared_point_candidates_3d.v1"
    PREPARED_AABB_OVERLAP_CANDIDATES_2D = "prepared_aabb_overlap_candidates_2d.v1"
    STABLE_RAY_TRIANGLE_CANDIDATES_3D = "stable_ray_triangle_candidates_3d.v1"
    COMPLETE_QUERY_GROUPED_DISTANCE_ROWS = "complete_query_grouped_distance_rows.v1"
    CERTIFIED_NEAREST_STATE_3D = "certified_nearest_state_3d.v1"


class ActionProducerEventRegionKind(str, Enum):
    """Compiler-visible producer-region facts, never backend selections."""

    COMPILER_OWNED_DEVICE_WRITE_LEASE = (
        "compiler_owned_device_write_lease.v1"
    )


_SINGLE_DELIVERY_PROOF = "prepared-index-single-delivery-contract-v1"
_STABLE_PRIMITIVE_DEDUP_PROOF = "ray-triangle-stable-primitive-keyed-dedup-v1"
_QUERY_MIN_TERMINATION = "query-local-lower-bound-certificate-v1"
_QUERY_MIN_ORDERING = "query-grouped-canonical-f32-candidate-order-v1"


@dataclass(frozen=True)
class _ProducerContract:
    delivery_proofs: frozenset[str]
    termination_certificates: frozenset[str] = frozenset()
    ordering_certificates: frozenset[str] = frozenset()
    allowed_templates: tuple[tuple[str, str], ...] = ()


_PRODUCER_CONTRACTS = {
    ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS: _ProducerContract(
        frozenset({_SINGLE_DELIVERY_PROOF}),
        allowed_templates=(
            ("host", "sorted_host_i64x2_count_sum"),
            ("numba", "filter_bounded_emit"),
            ("numba", "grouped_i64x2_count_sum"),
        ),
    ),
    ActionProducerKind.PREPARED_POINT_CANDIDATES_3D: _ProducerContract(
        frozenset({_SINGLE_DELIVERY_PROOF}),
        allowed_templates=(
            ("optix", "point_candidate_bounded_selection_3d"),
            ("ranked_window_qk", "prepared_ranked_distance_window_qk_3d"),
            (
                "candidate_pruned_grid",
                "candidate_pruned_exact_bounded_selection_3d",
            ),
        ),
    ),
    ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D: _ProducerContract(
        frozenset({_SINGLE_DELIVERY_PROOF}),
        allowed_templates=(
            ("optix", "aabb_filter_bounded_emit_2d"),
            ("embree", "aabb_filter_bounded_emit_reference_2d"),
        ),
    ),
    ActionProducerKind.STABLE_RAY_TRIANGLE_CANDIDATES_3D: _ProducerContract(
        frozenset({_STABLE_PRIMITIVE_DEDUP_PROOF}),
        allowed_templates=(("optix", "keyed_i64_sum_3d"),),
    ),
    ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS: _ProducerContract(
        frozenset({_SINGLE_DELIVERY_PROOF}),
        frozenset({_QUERY_MIN_TERMINATION}),
        frozenset({_QUERY_MIN_ORDERING}),
        (("numba", "certified_query_min_state"),),
    ),
    ActionProducerKind.CERTIFIED_NEAREST_STATE_3D: _ProducerContract(
        frozenset({_SINGLE_DELIVERY_PROOF}),
        frozenset({_QUERY_MIN_TERMINATION}),
        allowed_templates=(
            ("cuda_grid", "certified_nearest_state_3d"),
            (
                "optix_traversal",
                "certified_nearest_state_3d_optix_traversal",
            ),
            (
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE,
            ),
            # Private migration alias only; it is not advertised as a compiler
            # capability after Goal5661.
            ("optix", "certified_nearest_state_3d"),
        ),
    ),
}


@dataclass(frozen=True)
class CompiledAction:
    spec: ActionSpec
    source_digest: str
    frontend: str = "restricted_python_ast"
    publication_status: str = "private_research_embargo"

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": ACTION_API_CANDIDATE_VERSION,
            "semantic_digest": self.spec.semantic_digest,
            "source_digest": self.source_digest,
            "frontend": self.frontend,
            "publication_status": self.publication_status,
            "raw_callback_accepted": False,
            "arbitrary_numba_cuda_or_ptx_accepted": False,
            "action_name_used_for_lowering_dispatch": False,
            "raw_proof_sets_accepted_by_private_facade": False,
        }

    def execute_reference(
        self,
        events: Sequence[Mapping[str, object]],
        parameters: Mapping[str, object],
        *,
        extents: Mapping[ExtentKind | str, int] | None = None,
    ) -> ActionExecutionResult:
        if self.spec.termination_proofs:
            _fail(
                "producer_binding_required",
                "compiled",
                "termination-bearing Actions execute through BoundAction",
            )
        return execute_action_reference(
            self.spec,
            events,
            parameters,
            extents=extents,
        )

    def plan(
        self,
        capabilities: tuple[ActionBackendCapability, ...],
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, int] | None = None,
    ) -> ActionPlacementPlan:
        del capabilities, extents, parameters
        _fail(
            "producer_binding_required",
            "compiled",
            "placement planning requires a compiler-issued producer binding",
        )


@dataclass(frozen=True)
class VerifiedEventColumnBatchCertificate:
    """Compiler-issued identity and ordering proof for one host column batch."""

    row_count: int
    schema_digest: str
    batch_digest: str
    logical_event_key_digest: str
    ordering_fields: tuple[str, ...]
    ordering_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.verified_event_column_batch.private_candidate.v1",
            "row_count": self.row_count,
            "schema_digest": self.schema_digest,
            "batch_digest": self.batch_digest,
            "logical_event_key_digest": self.logical_event_key_digest,
            "ordering_fields": list(self.ordering_fields),
            "ordering_digest": self.ordering_digest,
            "typed_column_digest": True,
            "duplicate_logical_keys_rejected_vectorized": True,
            "lexicographic_order_validated_vectorized": True,
            "full_payload_and_row_order_bound": True,
            "python_row_objects_materialized": False,
            "device_to_host_copy_used": False,
        }


@dataclass(frozen=True)
class BoundAction:
    """A compiled Action tied to one compiler-known event producer contract."""

    compiled: CompiledAction
    producer_kind: ActionProducerKind
    delivery_proofs: frozenset[str]
    termination_certificates: frozenset[str]
    ordering_certificates: frozenset[str]
    logical_event_key_digest: str | None
    event_column_certificate: VerifiedEventColumnBatchCertificate | None
    binding_digest: str
    _signature: str

    def to_metadata(self) -> dict[str, object]:
        return self.compiled.to_metadata() | {
            "producer_kind": self.producer_kind.value,
            "producer_binding_digest": self.binding_digest,
            "producer_binding_compiler_issued": True,
            "producer_binding_integrity_checked": True,
            "logical_event_key_digest": self.logical_event_key_digest,
            "event_column_certificate": (
                self.event_column_certificate.to_metadata()
                if self.event_column_certificate is not None
                else None
            ),
            "raw_proof_sets_accepted": False,
        }

    def execute_reference(
        self,
        events: Sequence[Mapping[str, object]],
        parameters: Mapping[str, object],
        *,
        extents: Mapping[ExtentKind | str, int] | None = None,
    ) -> ActionExecutionResult:
        _validate_binding(self)
        proof_names = frozenset(
            proof.name
            for proof in self.compiled.spec.termination_proofs
            if proof.certificate in self.termination_certificates
        )
        return execute_action_reference(
            self.compiled.spec,
            events,
            parameters,
            extents=extents,
            discharged_termination_proofs=proof_names,
        )

    def plan(
        self,
        capabilities: tuple[ActionBackendCapability, ...],
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, int] | None = None,
    ) -> ActionPlacementPlan:
        _validate_binding(self)
        return plan_action_placement(
            self.compiled.spec,
            capabilities,
            extents=extents,
            parameters=parameters,
            discharged_delivery_proofs=self.delivery_proofs,
            discharged_termination_certificates=self.termination_certificates,
            producer_kind=self.producer_kind.value,
        )


@dataclass(frozen=True)
class LoweredAction:
    compiled: CompiledAction
    producer_kind: ActionProducerKind
    producer_binding_digest: str
    logical_event_key_digest: str | None
    event_column_certificate: VerifiedEventColumnBatchCertificate | None
    backend: str
    placement: str
    template_kind: str
    program: object
    rejected_templates: tuple[tuple[str, str], ...]
    compiler_execution_trace: Mapping[str, object] | None = None
    consumer_composition: ActionConsumerCompositionCertificate | None = None

    def to_metadata(self) -> dict[str, object]:
        program_metadata = (
            self.program.to_metadata() if hasattr(self.program, "to_metadata") else {}
        )
        metadata = self.compiled.to_metadata() | {
            "backend": self.backend,
            "producer_kind": self.producer_kind.value,
            "producer_binding_digest": self.producer_binding_digest,
            "producer_binding_integrity_checked": True,
            "logical_event_key_digest": self.logical_event_key_digest,
            "event_column_certificate": (
                self.event_column_certificate.to_metadata()
                if self.event_column_certificate is not None
                else None
            ),
            "placement": self.placement,
            "template_kind": self.template_kind,
            "rejected_templates": [
                {"template": template, "reason": reason}
                for template, reason in self.rejected_templates
            ],
            "program": program_metadata,
            "feature_driven_template_selection": True,
        }
        if self.compiler_execution_trace is not None:
            metadata["compiler_execution_trace"] = dict(
                self.compiler_execution_trace
            )
        metadata["consumer_composition"] = (
            self.consumer_composition.to_metadata()
            if self.consumer_composition is not None
            else None
        )
        return metadata


@dataclass(frozen=True)
class ActionTargetProfile:
    """Compiler-owned target facts; applications never select a backend name."""

    optix_available: bool = False
    numba_available: bool = False
    embree_available: bool = False
    cpu_reference_available: bool = True
    optix_max_inline_state_bytes: int | None = None
    numba_max_device_state_bytes: int | None = None
    embree_max_host_state_bytes: int | None = None
    max_output_bytes: int | None = None
    profile_source: str = "explicit_compiler_target_facts"
    device_memory_limit_bytes: int | None = None
    production_selection_policy: str = "legacy_explicit_target_validation"

    def __post_init__(self) -> None:
        if self.profile_source not in {
            "explicit_compiler_target_facts",
            "runtime_capability_probe",
            "fork_clean_runtime_capability_probe",
        }:
            raise ValueError("profile_source is not a compiler-owned target source")
        if self.production_selection_policy not in {
            "legacy_explicit_target_validation",
            "compiler_owned_default",
        }:
            raise ValueError("production_selection_policy is invalid")
        for name in (
            "optix_max_inline_state_bytes",
            "numba_max_device_state_bytes",
            "embree_max_host_state_bytes",
            "max_output_bytes",
            "device_memory_limit_bytes",
        ):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, int) or value < 0):
                raise ValueError(f"{name} must be a nonnegative integer or None")

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.action_target_profile.private_candidate.v1",
            "optix_available": self.optix_available,
            "numba_available": self.numba_available,
            "embree_available": self.embree_available,
            "cpu_reference_available": self.cpu_reference_available,
            "optix_max_inline_state_bytes": self.optix_max_inline_state_bytes,
            "numba_max_device_state_bytes": self.numba_max_device_state_bytes,
            "embree_max_host_state_bytes": self.embree_max_host_state_bytes,
            "max_output_bytes": self.max_output_bytes,
            "profile_source": self.profile_source,
            "device_memory_limit_bytes": self.device_memory_limit_bytes,
            "production_selection_policy": self.production_selection_policy,
            "application_selected_backend": False,
        }


def _probe_device_memory_limit_bytes() -> int | None:
    """Return compiler-probed total device bytes, never an app-supplied guess."""

    try:
        from numba import cuda

        if cuda.is_available():
            _free_bytes, total_bytes = cuda.current_context().get_memory_info()
            total = int(total_bytes)
            if total > 0:
                return total
    except Exception:
        pass
    try:
        import cupy

        _free_bytes, total_bytes = cupy.cuda.runtime.memGetInfo()
        total = int(total_bytes)
        if total > 0:
            return total
    except Exception:
        pass
    return None


_FORK_CLEAN_TARGET_PROBE_REQUEST = "rtdl.fork_clean_action_target_probe_request.v1"
_FORK_CLEAN_TARGET_PROBE_RESPONSE = "rtdl.fork_clean_action_target_probe_response.v1"
_FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_REQUEST = (
    "rtdl.fast_fork_clean_optix_target_probe_request.v1"
)
_FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE = (
    "rtdl.fast_fork_clean_optix_target_probe_response.v1"
)
_TARGET_PROFILE_CONSTRUCTOR_FIELDS = (
    "optix_available",
    "numba_available",
    "embree_available",
    "cpu_reference_available",
    "optix_max_inline_state_bytes",
    "numba_max_device_state_bytes",
    "embree_max_host_state_bytes",
    "max_output_bytes",
    "profile_source",
    "device_memory_limit_bytes",
    "production_selection_policy",
)


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _fork_clean_action_target_probe_response(request: Mapping[str, object]) -> dict[str, object]:
    """Run the ordinary dynamic target probe inside a disposable process."""

    if set(request) != {
        "schema",
        "nonce",
        "required_backends",
        "certified_nearest",
        "cpu_reference_available",
        "optix_max_inline_state_bytes",
        "numba_max_device_state_bytes",
        "embree_max_host_state_bytes",
        "max_output_bytes",
        "action_api_sha256",
        "provider_library_path",
        "provider_library_sha256",
    }:
        raise ValueError("FORK_CLEAN_TARGET_PROBE_REQUEST_FIELDS_INVALID")
    nonce = request["nonce"]
    if (
        request["schema"] != _FORK_CLEAN_TARGET_PROBE_REQUEST
        or not isinstance(nonce, str)
        or len(nonce) != 64
        or any(character not in "0123456789abcdef" for character in nonce)
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_REQUEST_IDENTITY_INVALID")
    module_path = Path(__file__).resolve(strict=True)
    if request["action_api_sha256"] != _sha256_file(module_path):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_SOURCE_MISMATCH")
    backends_value = request["required_backends"]
    if (
        not isinstance(backends_value, list)
        or not backends_value
        or any(not isinstance(item, str) or not item for item in backends_value)
        or backends_value != sorted(set(backends_value))
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_BACKENDS_INVALID")
    if not isinstance(request["certified_nearest"], bool) or not isinstance(
        request["cpu_reference_available"], bool
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_BOOLEAN_FACT_INVALID")
    for field_name in (
        "optix_max_inline_state_bytes",
        "numba_max_device_state_bytes",
        "embree_max_host_state_bytes",
        "max_output_bytes",
    ):
        field_value = request[field_name]
        if field_value is not None and (
            isinstance(field_value, bool)
            or not isinstance(field_value, int)
            or field_value < 0
        ):
            raise ValueError("FORK_CLEAN_TARGET_PROBE_LIMIT_FACT_INVALID:" + field_name)
    provider_path_value = request["provider_library_path"]
    provider_sha_value = request["provider_library_sha256"]
    if "optix" in backends_value:
        if (
            not isinstance(provider_path_value, str)
            or not provider_path_value
            or not isinstance(provider_sha_value, str)
            or len(provider_sha_value) != 64
        ):
            raise ValueError("FORK_CLEAN_TARGET_PROBE_PROVIDER_IDENTITY_REQUIRED")
        provider_path = Path(provider_path_value).resolve(strict=True)
        if _sha256_file(provider_path) != provider_sha_value:
            raise ValueError("FORK_CLEAN_TARGET_PROBE_PROVIDER_MISMATCH")
        if Path(os.environ.get("RTDL_OPTIX_LIB", "")).resolve() != provider_path:
            raise ValueError("FORK_CLEAN_TARGET_PROBE_PROVIDER_ENVIRONMENT_MISMATCH")
    elif provider_path_value is not None or provider_sha_value is not None:
        raise ValueError("FORK_CLEAN_TARGET_PROBE_UNEXPECTED_PROVIDER_IDENTITY")

    target = _detect_action_target_profile_for_required_backends(
        required_backends=tuple(backends_value),
        certified_nearest=request["certified_nearest"],
        cpu_reference_available=request["cpu_reference_available"],
        optix_max_inline_state_bytes=request["optix_max_inline_state_bytes"],
        numba_max_device_state_bytes=request["numba_max_device_state_bytes"],
        embree_max_host_state_bytes=request["embree_max_host_state_bytes"],
        max_output_bytes=request["max_output_bytes"],
    )
    target_payload = {
        field_name: getattr(target, field_name)
        for field_name in _TARGET_PROFILE_CONSTRUCTOR_FIELDS
    }
    body: dict[str, object] = {
        "schema": _FORK_CLEAN_TARGET_PROBE_RESPONSE,
        "nonce": nonce,
        "required_backends": list(backends_value),
        "action_api_sha256": request["action_api_sha256"],
        "provider_library_sha256": provider_sha_value,
        "target_profile": target_payload,
        "probe_process_pid": os.getpid(),
        "parent_process_pid": os.getppid(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "nvidia_visible_devices": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
    }
    body["response_sha256"] = _canonical_sha256(body)
    return body


def _fork_clean_action_target_probe_child_main() -> int:
    """Private subprocess entry point; stdout is exactly one JSON receipt."""

    request = json.loads(sys.stdin.read())
    response = _fork_clean_action_target_probe_response(request)
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


def _detect_optix_target_profile_fork_clean_fast(
    *,
    cpu_reference_available: bool,
    optix_max_inline_state_bytes: int | None,
    numba_max_device_state_bytes: int | None,
    embree_max_host_state_bytes: int | None,
    max_output_bytes: int | None,
    _runner=None,
) -> ActionTargetProfile:
    """Probe one already-required OptiX provider without importing RTDL in child.

    The ordinary fork-clean helper imports :mod:`rtdsl.action_api` in the
    disposable process, which recursively imports the complete compiler and
    runtime graph.  For the exact OptiX-only case, the dynamic facts are only
    provider load/version and visible-device total memory.  A path-executed,
    source-bound child obtains those facts through ``ctypes`` while preserving
    the same fail-closed source/native/GPU-environment receipt boundary.
    """

    provider_value = os.environ.get("RTDL_OPTIX_LIB")
    if not provider_value:
        raise ValueError("FORK_CLEAN_TARGET_PROBE_REQUIRES_EXPLICIT_OPTIX_LIBRARY")
    provider_path = Path(provider_value).resolve(strict=True)
    provider_sha = _sha256_file(provider_path)
    child_path = Path(__file__).with_name(
        "_fork_clean_optix_target_probe_child.py"
    ).resolve(strict=True)
    child_sha = _sha256_file(child_path)
    request: dict[str, object] = {
        "schema": _FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_REQUEST,
        "nonce": secrets.token_hex(32),
        "required_backends": ["optix"],
        "certified_nearest": False,
        "cpu_reference_available": bool(cpu_reference_available),
        "optix_max_inline_state_bytes": optix_max_inline_state_bytes,
        "numba_max_device_state_bytes": numba_max_device_state_bytes,
        "embree_max_host_state_bytes": embree_max_host_state_bytes,
        "max_output_bytes": max_output_bytes,
        "action_api_sha256": _sha256_file(Path(__file__).resolve(strict=True)),
        "probe_child_sha256": child_sha,
        "provider_library_path": str(provider_path),
        "provider_library_sha256": provider_sha,
    }
    environment = os.environ.copy()
    runner = subprocess.run if _runner is None else _runner
    completed = runner(
        [sys.executable, str(child_path)],
        input=json.dumps(request, sort_keys=True, separators=(",", ":")),
        text=True,
        capture_output=True,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_PROCESS_FAILED:"
            + json.dumps(
                {
                    "returncode": completed.returncode,
                    "stderr": completed.stderr[-2000:],
                },
                sort_keys=True,
            )
        )
    try:
        response = json.loads(completed.stdout)
    except Exception as error:
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE_NOT_JSON") from error
    expected_response_fields = {
        "schema",
        "nonce",
        "required_backends",
        "action_api_sha256",
        "probe_child_sha256",
        "provider_library_sha256",
        "provider_version",
        "target_profile",
        "probe_process_pid",
        "parent_process_pid",
        "cuda_visible_devices",
        "nvidia_visible_devices",
        "response_sha256",
    }
    if not isinstance(response, dict) or set(response) != expected_response_fields:
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE_FIELDS_INVALID")
    response_sha = response.pop("response_sha256")
    provider_version = response["provider_version"]
    if (
        not isinstance(response_sha, str)
        or response_sha != _canonical_sha256(response)
        or response["schema"] != _FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE
        or response["nonce"] != request["nonce"]
        or response["required_backends"] != ["optix"]
        or response["action_api_sha256"] != request["action_api_sha256"]
        or response["probe_child_sha256"] != child_sha
        or response["provider_library_sha256"] != provider_sha
        or not isinstance(provider_version, list)
        or len(provider_version) != 3
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in provider_version
        )
        or provider_version[0] <= 0
        or not isinstance(response["probe_process_pid"], int)
        or response["probe_process_pid"] <= 0
        or not isinstance(response["parent_process_pid"], int)
        or response["parent_process_pid"] != os.getpid()
        or response["probe_process_pid"] == os.getpid()
        or response["cuda_visible_devices"]
        != environment.get("CUDA_VISIBLE_DEVICES")
        or response["nvidia_visible_devices"]
        != environment.get("NVIDIA_VISIBLE_DEVICES")
    ):
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE_BINDING_INVALID")
    target_payload = response["target_profile"]
    if not isinstance(target_payload, dict) or set(target_payload) != set(
        _TARGET_PROFILE_CONSTRUCTOR_FIELDS
    ):
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_TARGET_FIELDS_INVALID")
    if (
        target_payload["optix_available"] is not True
        or target_payload["numba_available"] is not False
        or target_payload["embree_available"] is not False
        or target_payload["cpu_reference_available"]
        != bool(cpu_reference_available)
        or target_payload["profile_source"] != "runtime_capability_probe"
        or target_payload["production_selection_policy"]
        != "compiler_owned_default"
        or not isinstance(target_payload["device_memory_limit_bytes"], int)
        or isinstance(target_payload["device_memory_limit_bytes"], bool)
        or target_payload["device_memory_limit_bytes"] <= 0
    ):
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_TARGET_INVALID")
    expected_limits = {
        "optix_max_inline_state_bytes": optix_max_inline_state_bytes,
        "numba_max_device_state_bytes": numba_max_device_state_bytes,
        "embree_max_host_state_bytes": embree_max_host_state_bytes,
        "max_output_bytes": max_output_bytes,
    }
    if any(target_payload[field] != value for field, value in expected_limits.items()):
        raise ValueError("FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_LIMIT_BINDING_INVALID")
    target_payload = dict(target_payload)
    target_payload["profile_source"] = "fork_clean_runtime_capability_probe"
    return ActionTargetProfile(**target_payload)


def _detect_action_target_profile_for_required_backends_fork_clean(
    *,
    required_backends: Iterable[str],
    certified_nearest: bool = False,
    cpu_reference_available: bool = True,
    optix_max_inline_state_bytes: int | None = None,
    numba_max_device_state_bytes: int | None = None,
    embree_max_host_state_bytes: int | None = None,
    max_output_bytes: int | None = None,
    _runner=None,
) -> ActionTargetProfile:
    """Probe dynamic GPU facts in a disposable process, leaving this parent clean.

    Prepared programs that are inherited across POSIX fork must not initialize
    CUDA in their long-lived parent.  This function is the compiler-owned seam
    for that lifecycle.  It returns only strictly validated target facts; it
    never returns a device handle or context.
    """

    backends = tuple(sorted(frozenset(str(item) for item in required_backends)))
    if not backends or any(not item for item in backends):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_BACKENDS_INVALID")
    if backends == ("optix",) and certified_nearest is False and _runner is None:
        return _detect_optix_target_profile_fork_clean_fast(
            cpu_reference_available=cpu_reference_available,
            optix_max_inline_state_bytes=optix_max_inline_state_bytes,
            numba_max_device_state_bytes=numba_max_device_state_bytes,
            embree_max_host_state_bytes=embree_max_host_state_bytes,
            max_output_bytes=max_output_bytes,
        )
    provider_path: Path | None = None
    provider_sha: str | None = None
    if "optix" in backends:
        provider_value = os.environ.get("RTDL_OPTIX_LIB")
        if not provider_value:
            raise ValueError("FORK_CLEAN_TARGET_PROBE_REQUIRES_EXPLICIT_OPTIX_LIBRARY")
        provider_path = Path(provider_value).resolve(strict=True)
        provider_sha = _sha256_file(provider_path)
    request: dict[str, object] = {
        "schema": _FORK_CLEAN_TARGET_PROBE_REQUEST,
        "nonce": secrets.token_hex(32),
        "required_backends": list(backends),
        "certified_nearest": bool(certified_nearest),
        "cpu_reference_available": bool(cpu_reference_available),
        "optix_max_inline_state_bytes": optix_max_inline_state_bytes,
        "numba_max_device_state_bytes": numba_max_device_state_bytes,
        "embree_max_host_state_bytes": embree_max_host_state_bytes,
        "max_output_bytes": max_output_bytes,
        "action_api_sha256": _sha256_file(Path(__file__).resolve(strict=True)),
        "provider_library_path": str(provider_path) if provider_path is not None else None,
        "provider_library_sha256": provider_sha,
    }
    environment = os.environ.copy()
    python_paths = [item for item in sys.path if item]
    if environment.get("PYTHONPATH"):
        python_paths.extend(environment["PYTHONPATH"].split(os.pathsep))
    environment["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(python_paths))
    runner = subprocess.run if _runner is None else _runner
    completed = runner(
        [
            sys.executable,
            "-c",
            (
                "from rtdsl.action_api import "
                "_fork_clean_action_target_probe_child_main as main; "
                "raise SystemExit(main())"
            ),
        ],
        input=json.dumps(request, sort_keys=True, separators=(",", ":")),
        text=True,
        capture_output=True,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "FORK_CLEAN_TARGET_PROBE_PROCESS_FAILED:"
            + json.dumps(
                {
                    "returncode": completed.returncode,
                    "stderr": completed.stderr[-2000:],
                },
                sort_keys=True,
            )
        )
    try:
        response = json.loads(completed.stdout)
    except Exception as error:
        raise ValueError("FORK_CLEAN_TARGET_PROBE_RESPONSE_NOT_JSON") from error
    if not isinstance(response, dict) or set(response) != {
        "schema",
        "nonce",
        "required_backends",
        "action_api_sha256",
        "provider_library_sha256",
        "target_profile",
        "probe_process_pid",
        "parent_process_pid",
        "cuda_visible_devices",
        "nvidia_visible_devices",
        "response_sha256",
    }:
        raise ValueError("FORK_CLEAN_TARGET_PROBE_RESPONSE_FIELDS_INVALID")
    response_sha = response.pop("response_sha256")
    if (
        not isinstance(response_sha, str)
        or response_sha != _canonical_sha256(response)
        or response["schema"] != _FORK_CLEAN_TARGET_PROBE_RESPONSE
        or response["nonce"] != request["nonce"]
        or response["required_backends"] != request["required_backends"]
        or response["action_api_sha256"] != request["action_api_sha256"]
        or response["provider_library_sha256"] != provider_sha
        or not isinstance(response["probe_process_pid"], int)
        or response["probe_process_pid"] <= 0
        or not isinstance(response["parent_process_pid"], int)
        or response["parent_process_pid"] != os.getpid()
        or response["probe_process_pid"] == os.getpid()
        or response["cuda_visible_devices"]
        != environment.get("CUDA_VISIBLE_DEVICES")
        or response["nvidia_visible_devices"]
        != environment.get("NVIDIA_VISIBLE_DEVICES")
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_RESPONSE_BINDING_INVALID")
    target_payload = response["target_profile"]
    if not isinstance(target_payload, dict) or set(target_payload) != set(
        _TARGET_PROFILE_CONSTRUCTOR_FIELDS
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_TARGET_FIELDS_INVALID")
    if (
        target_payload["profile_source"] != "runtime_capability_probe"
        or target_payload["production_selection_policy"] != "compiler_owned_default"
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_TARGET_AUTHORITY_INVALID")
    for backend in backends:
        availability_field = f"{backend}_available"
        if availability_field not in target_payload or target_payload[availability_field] is not True:
            raise ValueError(f"FORK_CLEAN_TARGET_PROBE_REQUIRED_BACKEND_UNAVAILABLE:{backend}")
    if "optix" in backends and (
        not isinstance(target_payload["device_memory_limit_bytes"], int)
        or target_payload["device_memory_limit_bytes"] <= 0
    ):
        raise ValueError("FORK_CLEAN_TARGET_PROBE_DEVICE_MEMORY_REQUIRED")
    target_payload = dict(target_payload)
    target_payload["profile_source"] = "fork_clean_runtime_capability_probe"
    return ActionTargetProfile(**target_payload)


def _detect_action_target_profile_for_required_backends(
    *,
    required_backends: Iterable[str],
    certified_nearest: bool = False,
    cpu_reference_available: bool = True,
    optix_max_inline_state_bytes: int | None = None,
    numba_max_device_state_bytes: int | None = None,
    embree_max_host_state_bytes: int | None = None,
    max_output_bytes: int | None = None,
) -> ActionTargetProfile:
    """Probe exactly the provider set already derived by compiler policy.

    This is an internal compiler seam, not an application backend override.
    Callers must derive the set from a verified producer contract or physical
    registry before entering this function.
    """

    required_backends = frozenset(str(item) for item in required_backends)
    if not required_backends or any(not item for item in required_backends):
        _fail(
            "compiler_required_backend_set_invalid",
            "required_backends",
            ",".join(sorted(required_backends)),
        )

    if certified_nearest:
        try:
            optix_available = bool(
                probe_certified_nearest_global_witness_3d().available
                or probe_certified_nearest_optix_traversal_3d().available
            )
        except Exception:
            optix_available = False
    elif "optix" in required_backends:
        try:
            from .optix_runtime import optix_version

            optix_version()
            optix_available = True
        except Exception:
            optix_available = False
    else:
        optix_available = False

    if "numba" in required_backends:
        try:
            from .numba_partner_continuation import numba_partner_available

            numba_available = bool(numba_partner_available())
        except Exception:
            numba_available = False
    else:
        numba_available = False

    if "embree" in required_backends:
        try:
            from .embree_runtime import embree_aabb_index_2d_available

            embree_available = bool(embree_aabb_index_2d_available())
        except Exception:
            embree_available = False
    else:
        embree_available = False

    return ActionTargetProfile(
        optix_available=optix_available,
        numba_available=numba_available,
        embree_available=embree_available,
        cpu_reference_available=cpu_reference_available,
        optix_max_inline_state_bytes=optix_max_inline_state_bytes,
        numba_max_device_state_bytes=numba_max_device_state_bytes,
        embree_max_host_state_bytes=embree_max_host_state_bytes,
        max_output_bytes=max_output_bytes,
        profile_source="runtime_capability_probe",
        device_memory_limit_bytes=_probe_device_memory_limit_bytes(),
        production_selection_policy="compiler_owned_default",
    )


def detect_action_target_profile(
    *,
    producer_kind: ActionProducerKind | None = None,
    _compiler_required_backends: Iterable[str] | None = None,
    cpu_reference_available: bool = True,
    optix_max_inline_state_bytes: int | None = None,
    numba_max_device_state_bytes: int | None = None,
    embree_max_host_state_bytes: int | None = None,
    max_output_bytes: int | None = None,
) -> ActionTargetProfile:
    """Probe compiler-owned runtime capabilities without accepting a backend choice."""

    if producer_kind is not None and not isinstance(producer_kind, ActionProducerKind):
        _fail("producer_kind_required", "producer_kind", type(producer_kind).__name__)
    if producer_kind is not None and _compiler_required_backends is not None:
        _fail(
            "ambiguous_compiler_backend_requirements",
            "producer_kind/_compiler_required_backends",
        )
    required_backends = (
        frozenset(str(item) for item in _compiler_required_backends)
        if _compiler_required_backends is not None
        else
        frozenset(
            backend
            for backend, _ in _PRODUCER_CONTRACTS[producer_kind].allowed_templates
        )
        if producer_kind is not None
        else frozenset({"optix", "numba", "embree"})
    )
    return _detect_action_target_profile_for_required_backends(
        required_backends=required_backends,
        certified_nearest=(
            producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
        ),
        cpu_reference_available=cpu_reference_available,
        optix_max_inline_state_bytes=optix_max_inline_state_bytes,
        numba_max_device_state_bytes=numba_max_device_state_bytes,
        embree_max_host_state_bytes=embree_max_host_state_bytes,
        max_output_bytes=max_output_bytes,
    )


@dataclass(frozen=True)
class PlannedLoweredAction:
    """One verified plan bound to the exact lowering selected by that plan."""

    plan: ActionPlacementPlan
    lowered: LoweredAction
    target_profile: ActionTargetProfile
    template_preflight_rejections: tuple[tuple[str, str], ...]
    compiler_native_library_identity: ActionNativeLibraryIdentity | None = None
    _compiler_native_library_object_id: int | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    _compiler_native_library_ref: object | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    compiler_prepared_input_digest: str | None = None
    compiler_prepared_input_digest_kind: str | None = None
    _compiler_prepared_input_object_id: int | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    _compiler_prepared_input_ref: object | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    compiler_first_query_input_digest: str | None = None
    compiler_first_query_input_digest_kind: str | None = None
    _compiler_first_query_input_object_id: int | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    _compiler_first_query_input_ref: object | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    consumer_composition: ActionConsumerCompositionCertificate | None = None
    _compiler_seal: str = field(default="", repr=False, compare=False)

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.action_planned_lowering.private_candidate.v1",
            "plan": self.plan.to_dict(),
            "lowered": self.lowered.to_metadata(),
            "target_profile": self.target_profile.to_metadata(),
            "template_preflight_rejections": [
                {"backend": backend, "reason": reason}
                for backend, reason in self.template_preflight_rejections
            ],
            "plan_lowering_backend_match": self.plan.selected_backend
            == self.lowered.backend,
            "plan_lowering_placement_match": self.plan.selected_placement.value
            == self.lowered.placement,
            "application_selected_backend": False,
            "template_legality_checked_before_cost_selection": True,
            "compiler_native_library_identity": (
                self.compiler_native_library_identity.to_metadata()
                if self.compiler_native_library_identity is not None
                else None
            ),
            "compiler_native_library_identity_digest": (
                self.compiler_native_library_identity.identity_digest
                if self.compiler_native_library_identity is not None
                else None
            ),
            "compiler_native_library_object_bound": (
                self.compiler_native_library_identity is not None
                and self._compiler_native_library_object_id is not None
                and self._compiler_native_library_ref is not None
                and id(self._compiler_native_library_ref)
                == self._compiler_native_library_object_id
            ),
            "compiler_native_library_runtime_revalidation_required": (
                self.compiler_native_library_identity is not None
            ),
            "consumer_composition": (
                self.consumer_composition.to_metadata()
                if self.consumer_composition is not None
                else None
            ),
            "consumer_composition_explicitly_requested": (
                self.consumer_composition is not None
            ),
            "consumer_composition_resources_priced_before_final_placement": (
                self.consumer_composition is not None
            ),
            "consumer_composition_resource_scope": (
                "action_semantic_state_only__native_target_index_and_scratch_separate"
                if self.consumer_composition is not None
                else None
            ),
            "compiler_plan_seal_valid": _planned_lowering_seal_valid(self),
            "compiler_prepared_input_object_bound": (
                self.compiler_prepared_input_digest is not None
                and self._compiler_prepared_input_object_id is not None
                and self._compiler_prepared_input_ref is not None
                and id(self._compiler_prepared_input_ref)
                == self._compiler_prepared_input_object_id
            ),
            "compiler_prepared_input_identity_bound": (
                self.compiler_prepared_input_digest is not None
                and self.compiler_prepared_input_digest_kind
                == "packed_point_full_v1"
            ),
            "compiler_prepared_input_digest": self.compiler_prepared_input_digest,
            "compiler_prepared_input_digest_kind": (
                self.compiler_prepared_input_digest_kind
            ),
            "compiler_prepared_input_runtime_content_revalidated": False,
            "compiler_prepared_input_runtime_content_revalidation_required_at_prepare": (
                self.compiler_prepared_input_digest is not None
                and self.compiler_prepared_input_digest_kind
                == "packed_point_full_v1"
            ),
            "compiler_first_query_input_identity_bound": (
                self.compiler_first_query_input_digest is not None
                and self.compiler_first_query_input_digest_kind
                == "packed_point_full_v1"
                and self._compiler_first_query_input_object_id is not None
                and self._compiler_first_query_input_ref is not None
                and id(self._compiler_first_query_input_ref)
                == self._compiler_first_query_input_object_id
            ),
            "compiler_first_query_input_digest": (
                self.compiler_first_query_input_digest
            ),
            "compiler_first_query_input_digest_kind": (
                self.compiler_first_query_input_digest_kind
            ),
            "compiler_first_query_runtime_content_revalidated_once": False,
            "compiler_first_query_runtime_content_revalidation_required_once": (
                self.compiler_first_query_input_digest is not None
                and self.compiler_first_query_input_digest_kind
                == "packed_point_full_v1"
            ),
            "compiler_repeated_query_input_identity_bound": False,
        }


@dataclass(frozen=True)
class ActionCompilerIssue:
    code: str
    path: str
    message: str


class ActionCompilerError(ValueError):
    def __init__(self, issue: ActionCompilerIssue) -> None:
        self.issue = issue
        super().__init__(f"Action compiler failed: {issue.code}@{issue.path}: {issue.message}")


def compile_action_source(
    source: str,
    contract: RestrictedActionFrontendContract,
) -> CompiledAction:
    """Compile the closed frontend; this private candidate never executes user code."""

    spec = compile_restricted_action_source(source, contract)
    return CompiledAction(
        spec=spec,
        source_digest=hashlib.sha256(source.encode("utf-8")).hexdigest(),
    )


def bind_action_producer(
    compiled: CompiledAction,
    producer_kind: ActionProducerKind,
) -> BoundAction:
    """Bind verified IR to a closed producer contract; raw proof names are not accepted."""

    if not isinstance(compiled, CompiledAction):
        _fail("compiled_action_required", "compiled", type(compiled).__name__)
    if not isinstance(producer_kind, ActionProducerKind):
        _fail("producer_kind_required", "producer_kind", type(producer_kind).__name__)
    if producer_kind is ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS:
        _fail(
            "validated_event_rows_required",
            "producer_kind",
            "columnar single-delivery evidence is issued by bind_action_event_rows",
        )
    contract = _PRODUCER_CONTRACTS[producer_kind]
    proof_reference = compiled.spec.logical_event.proof_reference
    if (
        compiled.spec.logical_event.enforcement is DeliveryEnforcement.PROVEN_SINGLE
        and proof_reference not in contract.delivery_proofs
    ):
        _fail(
            "producer_delivery_contract_mismatch",
            "logical_event.proof_reference",
            f"{proof_reference!r} is not discharged by {producer_kind.value}",
        )
    if (
        compiled.spec.logical_event.enforcement is DeliveryEnforcement.KEYED_DEDUP
        and producer_kind is not ActionProducerKind.STABLE_RAY_TRIANGLE_CANDIDATES_3D
    ):
        _fail(
            "producer_delivery_contract_mismatch",
            "logical_event.enforcement",
            f"keyed dedup is not enforced by {producer_kind.value}",
        )
    required_termination = frozenset(
        proof.certificate for proof in compiled.spec.termination_proofs
    )
    if required_termination != contract.termination_certificates:
        _fail(
            "producer_termination_contract_mismatch",
            "termination_proofs",
            f"required={sorted(required_termination)!r}; producer={sorted(contract.termination_certificates)!r}",
        )
    payload = _binding_payload(
        compiled,
        producer_kind,
        contract.delivery_proofs,
        contract.termination_certificates,
        contract.ordering_certificates,
        None,
        None,
    )
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(_ACTION_BINDING_SECRET, payload, hashlib.sha256).hexdigest()
    return BoundAction(
        compiled=compiled,
        producer_kind=producer_kind,
        delivery_proofs=contract.delivery_proofs,
        termination_certificates=contract.termination_certificates,
        ordering_certificates=contract.ordering_certificates,
        logical_event_key_digest=None,
        event_column_certificate=None,
        binding_digest=digest,
        _signature=signature,
    )


def bind_action_event_rows(
    compiled: CompiledAction,
    events: Sequence[Mapping[str, object]],
) -> BoundAction:
    """Verify one concrete logical-event batch and bind its key digest to lowering."""

    if not isinstance(compiled, CompiledAction):
        _fail("compiled_action_required", "compiled", type(compiled).__name__)
    producer_kind = ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS
    contract = _PRODUCER_CONTRACTS[producer_kind]
    proof_reference = compiled.spec.logical_event.proof_reference
    if proof_reference not in contract.delivery_proofs:
        _fail(
            "producer_delivery_contract_mismatch",
            "logical_event.proof_reference",
            str(proof_reference),
        )
    key_digest = _logical_event_key_digest(
        compiled.spec.logical_event.key_fields,
        events,
    )
    payload = _binding_payload(
        compiled,
        producer_kind,
        contract.delivery_proofs,
        contract.termination_certificates,
        contract.ordering_certificates,
        key_digest,
        None,
    )
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(_ACTION_BINDING_SECRET, payload, hashlib.sha256).hexdigest()
    return BoundAction(
        compiled=compiled,
        producer_kind=producer_kind,
        delivery_proofs=contract.delivery_proofs,
        termination_certificates=contract.termination_certificates,
        ordering_certificates=contract.ordering_certificates,
        logical_event_key_digest=key_digest,
        event_column_certificate=None,
        binding_digest=digest,
        _signature=signature,
    )


def bind_action_event_columns(
    compiled: CompiledAction,
    event_columns: Mapping[str, object],
    *,
    ordering_fields: tuple[str, ...],
    producer_kind: ActionProducerKind = ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS,
) -> BoundAction:
    """Bind a complete typed host-column batch without materializing row objects."""

    if not isinstance(compiled, CompiledAction):
        _fail("compiled_action_required", "compiled", type(compiled).__name__)
    if not isinstance(producer_kind, ActionProducerKind):
        _fail("producer_kind_required", "producer_kind", type(producer_kind).__name__)
    if producer_kind not in {
        ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS,
        ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS,
    }:
        _fail(
            "column_binding_producer_unsupported",
            "producer_kind",
            producer_kind.value,
        )
    if compiled.spec.logical_event.enforcement is not DeliveryEnforcement.PROVEN_SINGLE:
        _fail(
            "column_binding_requires_proven_single_delivery",
            "logical_event.enforcement",
            compiled.spec.logical_event.enforcement.value,
        )
    contract = _PRODUCER_CONTRACTS[producer_kind]
    proof_reference = compiled.spec.logical_event.proof_reference
    if proof_reference not in contract.delivery_proofs:
        _fail(
            "producer_delivery_contract_mismatch",
            "logical_event.proof_reference",
            str(proof_reference),
        )
    required_termination = frozenset(
        proof.certificate for proof in compiled.spec.termination_proofs
    )
    if required_termination != contract.termination_certificates:
        _fail(
            "producer_termination_contract_mismatch",
            "termination_proofs",
            f"required={sorted(required_termination)!r}; producer={sorted(contract.termination_certificates)!r}",
        )
    certificate = _verify_event_column_batch(
        compiled,
        event_columns,
        ordering_fields=ordering_fields,
    )
    payload = _binding_payload(
        compiled,
        producer_kind,
        contract.delivery_proofs,
        contract.termination_certificates,
        contract.ordering_certificates,
        certificate.logical_event_key_digest,
        certificate,
    )
    digest = hashlib.sha256(payload).hexdigest()
    signature = hmac.new(_ACTION_BINDING_SECRET, payload, hashlib.sha256).hexdigest()
    return BoundAction(
        compiled=compiled,
        producer_kind=producer_kind,
        delivery_proofs=contract.delivery_proofs,
        termination_certificates=contract.termination_certificates,
        ordering_certificates=contract.ordering_certificates,
        logical_event_key_digest=certificate.logical_event_key_digest,
        event_column_certificate=certificate,
        binding_digest=digest,
        _signature=signature,
    )


def lower_action(
    bound: BoundAction,
    *,
    backend: str,
) -> LoweredAction:
    """Select one legal template using verified IR and compiler-issued producer evidence."""

    if not isinstance(bound, BoundAction):
        _fail("producer_binding_required", "bound", type(bound).__name__)
    _validate_binding(bound)
    compiled = bound.compiled
    producer_contract = _PRODUCER_CONTRACTS[bound.producer_kind]
    allowed_templates = {
        template
        for producer_backend, template in producer_contract.allowed_templates
        if producer_backend == backend
    }
    if not allowed_templates:
        _fail(
            "producer_backend_incompatible",
            "backend",
            f"{bound.producer_kind.value} cannot feed {backend}",
        )
    attempts: list[tuple[str, object]] = []
    if backend == "numba":
        attempts = [
            (
                "filter_bounded_emit",
                lambda: compile_numba_action_continuation(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
            (
                "certified_query_min_state",
                lambda: compile_numba_certified_query_min_state(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                    discharged_termination_certificates=bound.termination_certificates,
                    discharged_ordering_certificates=bound.ordering_certificates,
                ),
            ),
            (
                "grouped_i64x2_count_sum",
                lambda: compile_numba_order_indexed_grouped_i64x2_count_sum(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
        ]
        placement = "device_continuation"
        expected_error = ActionPlacementError
    elif backend == "host":
        attempts = [
            (
                "sorted_host_i64x2_count_sum",
                lambda: compile_host_grouped_i64x2_count_sum(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
        ]
        placement = "host_continuation"
        expected_error = ActionPlacementError
    elif backend == "embree":
        attempts = [
            (
                "aabb_filter_bounded_emit_reference_2d",
                lambda: compile_embree_aabb_filter_bounded_emit_reference_2d(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
        ]
        placement = "host_continuation"
        expected_error = ActionEmbreePlacementError
    elif backend in {
        "optix",
        "cuda_grid",
        "optix_traversal",
        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
    }:
        attempts = [
            *(
                [
                    (
                        (
                            (
                                CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE
                                if backend
                                == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                                else (
                                    "certified_nearest_state_3d_optix_traversal"
                                    if backend == "optix_traversal"
                                    else "certified_nearest_state_3d"
                                )
                            )
                        ),
                        lambda: compile_certified_nearest_state_3d(
                            compiled.spec,
                            discharged_delivery_proofs=bound.delivery_proofs,
                            discharged_termination_certificates=bound.termination_certificates,
                        ),
                    ),
                ]
                if backend
                in {
                    "cuda_grid",
                    "optix_traversal",
                    CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                }
                or bound.producer_kind
                is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
                else [
                    (
                        "point_candidate_bounded_selection_3d",
                        lambda: compile_optix_bounded_selection_3d(
                            compiled.spec,
                            discharged_delivery_proofs=bound.delivery_proofs,
                        ),
                    ),
                    (
                        "aabb_filter_bounded_emit_2d",
                        lambda: compile_optix_aabb_filter_bounded_emit_2d(
                            compiled.spec,
                            discharged_delivery_proofs=bound.delivery_proofs,
                        ),
                    ),
                    (
                        "keyed_i64_sum_3d",
                        lambda: compile_optix_keyed_i64_sum_3d(
                            compiled.spec,
                            discharged_delivery_proofs=bound.delivery_proofs,
                        ),
                    ),
                ]
            ),
        ]
        placement = (
            "device_continuation"
            if backend in {"optix", "cuda_grid"}
            and bound.producer_kind
            is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
            else (
                "traversal_device_continuation"
                if backend
                in {
                    "optix_traversal",
                    CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                }
                else "traversal_fused"
            )
        )
        expected_error = ActionOptixPlacementError
    elif backend == "ranked_window_qk":
        attempts = [
            (
                "prepared_ranked_distance_window_qk_3d",
                lambda: compile_ranked_distance_window_qk_3d(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
        ]
        placement = "device_continuation"
        expected_error = ActionOptixPlacementError
    elif backend == "candidate_pruned_grid":
        attempts = [
            (
                "candidate_pruned_exact_bounded_selection_3d",
                lambda: compile_candidate_pruned_exact_bounded_selection_3d(
                    compiled.spec,
                    discharged_delivery_proofs=bound.delivery_proofs,
                ),
            ),
        ]
        placement = "device_continuation"
        expected_error = ActionOptixPlacementError
    else:
        _fail("unsupported_backend", "backend", backend)

    accepted: list[tuple[str, object]] = []
    rejected: list[tuple[str, str]] = []
    for template, factory in attempts:
        if template not in allowed_templates:
            rejected.append((template, "producer_template_incompatible"))
            continue
        try:
            accepted.append((template, factory()))  # type: ignore[operator]
        except expected_error as exc:
            rejected.append((template, exc.issue.code))
    if not accepted:
        _fail(
            "no_legal_template",
            "spec",
            "; ".join(f"{template}:{reason}" for template, reason in rejected),
        )
    if len(accepted) != 1:
        _fail(
            "ambiguous_legal_templates",
            "spec",
            ",".join(template for template, _ in accepted),
        )
    template, program = accepted[0]
    if template == "certified_nearest_state_3d":
        # The current implementation is a native CUDA grid branch-bound
        # continuation shipped in the OptiX runtime library. It does not launch
        # an OptiX traversal and therefore must not inherit traversal_fused.
        placement = "device_continuation"
    _validate_template_column_ordering(bound, template, program)
    return LoweredAction(
        compiled=compiled,
        producer_kind=bound.producer_kind,
        producer_binding_digest=bound.binding_digest,
        logical_event_key_digest=bound.logical_event_key_digest,
        event_column_certificate=bound.event_column_certificate,
        backend=backend,
        placement=placement,
        template_kind=template,
        program=program,
        rejected_templates=tuple(rejected),
    )


def _validate_template_column_ordering(
    bound: BoundAction,
    template: str,
    program: object,
) -> None:
    certificate = bound.event_column_certificate
    if certificate is None:
        return
    if template == "certified_query_min_state":
        required = (
            str(getattr(program, "query_field")),
            str(getattr(program, "distance_field")),
            str(getattr(program, "candidate_field")),
        )
        if certificate.ordering_fields != required:
            _fail(
                "template_column_ordering_certificate_mismatch",
                "event_column_certificate.ordering_fields",
                f"required {required!r}; got {certificate.ordering_fields!r}",
            )
    elif template in {
        "grouped_i64x2_count_sum",
        "sorted_host_i64x2_count_sum",
    }:
        required_prefix = tuple(getattr(program, "key_fields"))
        if certificate.ordering_fields[: len(required_prefix)] != required_prefix:
            _fail(
                "template_column_ordering_certificate_mismatch",
                "event_column_certificate.ordering_fields",
                f"required prefix {required_prefix!r}; got {certificate.ordering_fields!r}",
            )


def compiler_action_capabilities(
    bound: BoundAction,
    target: ActionTargetProfile,
    *,
    producer_event_region: ActionProducerEventRegionKind | None = None,
) -> tuple[ActionBackendCapability, ...]:
    """Build a closed capability set from producer, verified effects, and target facts."""

    if not isinstance(bound, BoundAction):
        _fail("producer_binding_required", "bound", type(bound).__name__)
    if not isinstance(target, ActionTargetProfile):
        _fail("target_profile_required", "target", type(target).__name__)
    _validate_binding(bound)
    effects = frozenset(verify_action_spec(bound.compiled.spec).inferred_effects)
    producer_contract = _PRODUCER_CONTRACTS[bound.producer_kind]
    allowed_backends = {backend for backend, _ in producer_contract.allowed_templates}
    grouped_host_shape = False
    if bound.producer_kind is ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS:
        try:
            compile_host_grouped_i64x2_count_sum(
                bound.compiled.spec,
                discharged_delivery_proofs=bound.delivery_proofs,
            )
            grouped_host_shape = True
        except ActionPlacementError:
            pass
    grouped_order_shape = False
    grouped_numba_available = target.numba_available
    if bound.producer_kind is ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS:
        try:
            compile_numba_order_indexed_grouped_i64x2_count_sum(
                bound.compiled.spec,
                discharged_delivery_proofs=bound.delivery_proofs,
            )
            grouped_order_shape = True
            if target.numba_available:
                grouped_probe = probe_grouped_i64x2_native_order()
                grouped_numba_available = bool(grouped_probe.available)
        except ActionPlacementError:
            pass
    if producer_event_region is not None and (
        producer_event_region
        is not ActionProducerEventRegionKind.COMPILER_OWNED_DEVICE_WRITE_LEASE
        or bound.producer_kind
        is not ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS
        or not grouped_host_shape
        or not grouped_order_shape
    ):
        _fail(
            "producer_event_region_shape_unsupported",
            "producer_event_region",
            repr(producer_event_region),
        )
    device_region = (
        producer_event_region
        is ActionProducerEventRegionKind.COMPILER_OWNED_DEVICE_WRITE_LEASE
    )
    capabilities: list[ActionBackendCapability] = []
    # A compiler-owned device write region makes the existing checked device
    # continuation the first legal placement and retains the checked host
    # continuation as fallback.  This is a semantic residency fact, not an
    # Action/app name, row-count, or locked-workload branch.  It does not claim
    # that every GPU makes device placement faster; that remains a measured
    # physical question for the target machine.
    if bound.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        definitions = (
            (
                "cuda_grid",
                ActionPlacementKind.DEVICE_CONTINUATION,
                ActionStateStorage.DEVICE_GLOBAL,
                target.optix_available,
                target.optix_max_inline_state_bytes,
                0,
            ),
            (
                "optix_traversal",
                ActionPlacementKind.TRAVERSAL_DEVICE_CONTINUATION,
                ActionStateStorage.DEVICE_GLOBAL,
                target.optix_available,
                target.optix_max_inline_state_bytes,
                1,
            ),
            (
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
                ActionPlacementKind.TRAVERSAL_DEVICE_CONTINUATION,
                ActionStateStorage.DEVICE_GLOBAL,
                target.optix_available,
                target.optix_max_inline_state_bytes,
                2,
            ),
        )
    else:
        definitions = (
            (
                "optix",
                ActionPlacementKind.TRAVERSAL_FUSED,
                ActionStateStorage.INLINE_PER_SCOPE,
                target.optix_available,
                target.optix_max_inline_state_bytes,
                0,
            ),
            (
                "host",
                ActionPlacementKind.HOST_CONTINUATION,
                ActionStateStorage.HOST,
                grouped_host_shape,
                None,
                1 if device_region else 0,
            ),
            (
                "numba",
                ActionPlacementKind.DEVICE_CONTINUATION,
                ActionStateStorage.DEVICE_GLOBAL,
                grouped_numba_available if grouped_order_shape else target.numba_available,
                target.numba_max_device_state_bytes,
                0 if device_region else 1,
            ),
            (
                "embree",
                ActionPlacementKind.HOST_CONTINUATION,
                ActionStateStorage.HOST,
                target.embree_available,
                target.embree_max_host_state_bytes,
                2,
            ),
        )
    for backend, placement, storage, available, state_limit, priority in definitions:
        if backend not in allowed_backends:
            continue
        capabilities.append(
            ActionBackendCapability(
                backend=backend,
                placement=placement,
                supported_effect_sets=(effects,),
                state_storage=storage,
                max_state_bytes=state_limit,
                max_output_bytes=target.max_output_bytes,
                supports_proven_single=True,
                supports_keyed_dedup=(backend == "optix"),
                available=available,
                priority=priority,
            )
        )
    if target.cpu_reference_available:
        capabilities.append(
            ActionBackendCapability(
                backend="cpu_reference",
                placement=ActionPlacementKind.CPU_REFERENCE,
                supported_effect_sets=(effects,),
                state_storage=ActionStateStorage.HOST,
                max_state_bytes=None,
                max_output_bytes=target.max_output_bytes,
                supports_proven_single=True,
                supports_keyed_dedup=True,
                available=True,
                priority=100,
            )
        )
    return tuple(capabilities)


def plan_and_lower_action(
    bound: BoundAction,
    capabilities: tuple[ActionBackendCapability, ...],
    *,
    target_profile: ActionTargetProfile,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None = None,
    consumer_composition: ActionConsumerCompositionKind | None = None,
    producer_event_region: ActionProducerEventRegionKind | None = None,
) -> PlannedLoweredAction:
    """Preflight real templates, plan by proofs/resources, and bind the selected lowering."""

    if not isinstance(bound, BoundAction):
        _fail("producer_binding_required", "bound", type(bound).__name__)
    _validate_binding(bound)
    if producer_event_region is not None and (
        producer_event_region
        is not ActionProducerEventRegionKind.COMPILER_OWNED_DEVICE_WRITE_LEASE
    ):
        _fail(
            "producer_event_region_unsupported",
            "producer_event_region",
            repr(producer_event_region),
        )
    composition_program = None
    composition_resources: ActionConsumerCompositionResources | None = None
    if consumer_composition is not None:
        if (
            consumer_composition
            is not ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        ):
            _fail(
                "consumer_composition_unsupported",
                "consumer_composition",
                repr(consumer_composition),
            )
        if bound.producer_kind is not ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
            _fail(
                "consumer_composition_producer_mismatch",
                "consumer_composition",
                bound.producer_kind.value,
            )
        query_count = _normalized_extent_value(extents, ExtentKind.QUERY_COUNT)
        composition_program = compile_certified_nearest_state_3d(
            bound.compiled.spec,
            discharged_delivery_proofs=bound.delivery_proofs,
            discharged_termination_certificates=bound.termination_certificates,
        )
        composition_resources = certified_nearest_global_argmax_resources(
            bound.compiled.spec,
            query_field=composition_program.query_field,
            candidate_field=composition_program.candidate_field,
            distance_field=composition_program.distance_field,
            distance_state_name=composition_program.distance_state_name,
            candidate_state_name=composition_program.candidate_state_name,
            query_count=query_count,
        )

    nearest_cuda_probe = None
    nearest_optix_probe = None
    nearest_cell_mbr_probe = None
    if bound.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        if any(
            capability.backend == "cuda_grid" and capability.available
            for capability in capabilities
        ):
            nearest_cuda_probe = probe_certified_nearest_global_witness_3d()
        if any(
            capability.backend == "optix_traversal" and capability.available
            for capability in capabilities
        ):
            nearest_optix_probe = (
                probe_certified_nearest_optix_traversal_3d()
            )
        if any(
            capability.backend == CELL_MBR_EXACT_WITNESS_3D_BACKEND
            and capability.available
            for capability in capabilities
        ):
            nearest_cell_mbr_probe = (
                probe_cell_mbr_exact_witness_optix_traversal_3d()
            )
    grouped_native_probe = None
    grouped_order_shape = False
    if bound.producer_kind is ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS:
        try:
            compile_numba_order_indexed_grouped_i64x2_count_sum(
                bound.compiled.spec,
                discharged_delivery_proofs=bound.delivery_proofs,
            )
            grouped_order_shape = True
            grouped_native_probe = probe_grouped_i64x2_native_order()
        except ActionPlacementError:
            pass
    lowered_by_backend: dict[str, LoweredAction] = {}
    preflight_rejections: list[tuple[str, str]] = []
    effective: list[ActionBackendCapability] = []
    for capability in capabilities:
        if not capability.available:
            effective.append(capability)
            continue
        selected_nearest_probe = (
            nearest_cuda_probe
            if capability.backend == "cuda_grid"
            else (
                nearest_optix_probe
                if capability.backend == "optix_traversal"
                else (
                    nearest_cell_mbr_probe
                    if capability.backend
                    == CELL_MBR_EXACT_WITNESS_3D_BACKEND
                    else None
                )
            )
        )
        if (
            bound.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
            and capability.backend
            in {
                "cuda_grid",
                "optix_traversal",
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            }
            and (
                selected_nearest_probe is None
                or not selected_nearest_probe.available
                or selected_nearest_probe.library_identity is None
                or selected_nearest_probe.library_ref is None
            )
        ):
            preflight_rejections.append(
                (
                    capability.backend,
                    "certified_nearest_native_abi_unavailable",
                )
            )
            effective.append(replace(capability, available=False))
            continue
        if (
            capability.backend == "numba"
            and grouped_order_shape
            and (
                grouped_native_probe is None
                or not grouped_native_probe.available
                or grouped_native_probe.library_identity is None
                or grouped_native_probe.library_ref is None
            )
        ):
            preflight_rejections.append(
                (capability.backend, "grouped_native_order_abi_unavailable")
            )
            effective.append(replace(capability, available=False))
            continue
        if capability.backend == "cpu_reference":
            if capability.placement is not ActionPlacementKind.CPU_REFERENCE:
                preflight_rejections.append(
                    (capability.backend, "placement_contract_mismatch")
                )
                effective.append(replace(capability, available=False))
            else:
                effective.append(capability)
            continue
        try:
            lowered = lower_action(bound, backend=capability.backend)
        except ActionCompilerError as exc:
            preflight_rejections.append((capability.backend, exc.issue.code))
            effective.append(replace(capability, available=False))
            continue
        if lowered.placement != capability.placement.value:
            preflight_rejections.append(
                (capability.backend, "placement_contract_mismatch")
            )
            effective.append(replace(capability, available=False))
            continue
        lowered_by_backend[capability.backend] = lowered
        effective.append(capability)

    if not any(capability.available for capability in effective):
        _fail(
            "no_executable_placement",
            "capabilities",
            "; ".join(
                f"{backend}:{reason}" for backend, reason in preflight_rejections
            )
            or "all target capabilities are unavailable",
        )
    plan = bound.plan(
        tuple(effective),
        extents=extents,
        parameters=parameters,
    )
    if composition_resources is not None:
        plan = _bind_composition_resources_before_selection(
            plan,
            tuple(effective),
            composition_resources,
        )
    if plan.selected_backend == "cpu_reference":
        lowered = LoweredAction(
            compiled=bound.compiled,
            producer_kind=bound.producer_kind,
            producer_binding_digest=bound.binding_digest,
            logical_event_key_digest=bound.logical_event_key_digest,
            event_column_certificate=bound.event_column_certificate,
            backend="cpu_reference",
            placement=ActionPlacementKind.CPU_REFERENCE.value,
            template_kind="cpu_reference_interpreter",
            program=bound,
            rejected_templates=(),
        )
    else:
        lowered = lowered_by_backend.get(plan.selected_backend)
        if lowered is None:
            _fail(
                "planned_lowering_missing",
                "plan.selected_backend",
                plan.selected_backend,
            )
    if plan.selected_placement.value != lowered.placement:
        _fail(
            "plan_lowering_placement_mismatch",
            "plan.selected_placement",
            f"{plan.selected_placement.value}!={lowered.placement}",
        )
    composition_certificate = None
    if composition_resources is not None:
        if composition_program is None:
            _fail(
                "consumer_composition_program_missing",
                "consumer_composition",
                "verified producer program was not retained through placement",
            )
        composition_certificate = issue_certified_nearest_global_argmax_composition(
            bound.compiled.spec,
            action_source_digest=bound.compiled.source_digest,
            producer_kind=bound.producer_kind.value,
            producer_binding_digest=bound.binding_digest,
            selected_backend=lowered.backend,
            selected_placement=lowered.placement,
            selected_template=lowered.template_kind,
            template_identity_digest=action_template_identity_digest(
                lowered.program.to_metadata()
                if hasattr(lowered.program, "to_metadata")
                else {"template": lowered.template_kind}
            ),
            query_field=composition_program.query_field,
            candidate_field=composition_program.candidate_field,
            distance_field=composition_program.distance_field,
            distance_state_name=composition_program.distance_state_name,
            candidate_state_name=composition_program.candidate_state_name,
            query_count=composition_resources.query_count,
        )
        if (
            plan.resources.total_state_bytes
            != composition_certificate.total_state_byte_bound
            or plan.resources.bounded_output_rows
            != composition_certificate.output_row_bound
            or plan.resources.bounded_output_bytes
            != composition_certificate.output_byte_bound
        ):
            _fail(
                "consumer_composition_resource_binding_mismatch",
                "plan.resources",
                "pre-placement resources differ from the final certificate",
            )
        lowered = replace(lowered, consumer_composition=composition_certificate)
    elif bound.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        # Planning the producer alone remains useful for diagnostics, but its
        # prepared execution cannot silently append a global reducer.
        composition_certificate = None

    native_library_identity = None
    native_library_ref = None
    if (
        lowered.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
        and lowered.backend
        in {
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        }
        and lowered.template_kind
        in {
            "certified_nearest_state_3d",
            "certified_nearest_state_3d_optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE,
        }
    ):
        selected_nearest_probe = (
            nearest_cuda_probe
            if lowered.backend == "cuda_grid"
            else (
                nearest_optix_probe
                if lowered.backend == "optix_traversal"
                else nearest_cell_mbr_probe
            )
        )
        if (
            selected_nearest_probe is None
            or not selected_nearest_probe.available
            or selected_nearest_probe.library_identity is None
            or selected_nearest_probe.library_ref is None
        ):
            _fail(
                "selected_native_template_identity_missing",
                "nearest_native_probe",
                "the selected certified-nearest route lacks an exact native ABI identity",
            )
        native_library_identity = selected_nearest_probe.library_identity
        native_library_ref = selected_nearest_probe.library_ref
    elif (
        lowered.backend == "numba"
        and lowered.template_kind == "grouped_i64x2_count_sum"
    ):
        if (
            grouped_native_probe is None
            or not grouped_native_probe.available
            or grouped_native_probe.library_identity is None
            or grouped_native_probe.library_ref is None
        ):
            _fail(
                "selected_native_template_identity_missing",
                "grouped_native_order_probe",
                "the selected grouped device route lacks its exact native ordering ABI identity",
            )
        native_library_identity = grouped_native_probe.library_identity
        native_library_ref = grouped_native_probe.library_ref

    execution_trace = {
        "contract": "rtdl.action_compiler_execution_trace.private_candidate.v1",
        "semantic_digest": bound.compiled.spec.semantic_digest,
        "producer_kind": bound.producer_kind.value,
        "producer_binding_digest": bound.binding_digest,
        "target_profile": target_profile.to_metadata(),
        "plan": plan.to_dict(),
        "selected_backend": lowered.backend,
        "selected_placement": lowered.placement,
        "selected_template": lowered.template_kind,
        "consumer_composition": (
            composition_certificate.to_metadata()
            if composition_certificate is not None
            else None
        ),
        "consumer_composition_explicitly_requested": (
            composition_certificate is not None
        ),
        "consumer_composition_resources_priced_before_final_placement": (
            composition_resources is not None
        ),
        "producer_event_region": (
            producer_event_region.value
            if producer_event_region is not None
            else None
        ),
        "producer_event_region_is_backend_selection": False,
        "producer_event_region_preserved_without_host_materialization": (
            producer_event_region
            is ActionProducerEventRegionKind.COMPILER_OWNED_DEVICE_WRITE_LEASE
            and plan.selected_placement
            is ActionPlacementKind.DEVICE_CONTINUATION
        ),
        "native_template_symbol_probe": (
            (
                nearest_cuda_probe
                if lowered.backend == "cuda_grid"
                else (
                    nearest_optix_probe
                    if lowered.backend == "optix_traversal"
                    else nearest_cell_mbr_probe
                )
            ).to_metadata()
            if lowered.backend
            in {
                "cuda_grid",
                "optix_traversal",
                CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            }
            and (
                nearest_cuda_probe
                if lowered.backend == "cuda_grid"
                else (
                    nearest_optix_probe
                    if lowered.backend == "optix_traversal"
                    else nearest_cell_mbr_probe
                )
            )
            is not None
            else None
        ),
        "grouped_native_order_symbol_probe": (
            grouped_native_probe.to_metadata()
            if grouped_native_probe is not None
            else None
        ),
        "selected_native_library_identity": (
            native_library_identity.to_metadata()
            if native_library_identity is not None
            else None
        ),
        "template_preflight_rejections": [
            {"backend": backend, "reason": reason}
            for backend, reason in preflight_rejections
        ],
        "plan_lowering_backend_match": plan.selected_backend == lowered.backend,
        "plan_lowering_placement_match": (
            plan.selected_placement.value == lowered.placement
        ),
        "application_selected_backend": False,
        "raw_callback_accepted": False,
        "user_kernel_accepted": False,
        "arbitrary_ptx_accepted": False,
    }
    lowered = replace(lowered, compiler_execution_trace=execution_trace)
    planned = PlannedLoweredAction(
        plan=plan,
        lowered=lowered,
        target_profile=target_profile,
        template_preflight_rejections=tuple(preflight_rejections),
        compiler_native_library_identity=native_library_identity,
        _compiler_native_library_object_id=(
            id(native_library_ref) if native_library_ref is not None else None
        ),
        _compiler_native_library_ref=native_library_ref,
        consumer_composition=composition_certificate,
    )
    return _seal_planned_lowered_action(planned)


def compile_bound_action_for_target(
    bound: BoundAction,
    target: ActionTargetProfile,
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None = None,
    consumer_composition: ActionConsumerCompositionKind | None = None,
    producer_event_region: ActionProducerEventRegionKind | None = None,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> PlannedLoweredAction:
    """Compile without an application-selected backend or callback escape hatch.

    When a semantic statement is supplied, the application has already chosen
    its algorithm.  The compiler resolves the unique canonical provider for
    that statement/backend contract and makes the existing DEFAULT planner a
    compatibility materializer only.  A materialized provider mismatch fails
    before execution.
    """

    if (semantic_statement_stable_id is None) != (backend_contract_id is None):
        _fail(
            "incomplete_canonical_semantic_authority",
            "semantic_statement_stable_id/backend_contract_id",
            "both fields are required together",
        )

    capabilities = compiler_action_capabilities(
        bound,
        target,
        producer_event_region=producer_event_region,
    )
    if target.production_selection_policy == "compiler_owned_default":
        return _compile_bound_action_with_production_default(
            bound,
            target,
            capabilities=capabilities,
            extents=extents,
            parameters=parameters,
            consumer_composition=consumer_composition,
            producer_event_region=producer_event_region,
            semantic_statement_stable_id=semantic_statement_stable_id,
            backend_contract_id=backend_contract_id,
        )
    if semantic_statement_stable_id is not None:
        _fail(
            "canonical_semantic_authority_requires_production_default",
            "target.production_selection_policy",
            target.production_selection_policy,
        )
    return plan_and_lower_action(
        bound,
        capabilities,
        target_profile=target,
        extents=extents,
        parameters=parameters,
        consumer_composition=consumer_composition,
        producer_event_region=producer_event_region,
    )


def _production_default_value_width(value_type: object) -> int:
    if isinstance(value_type, ActionTupleType):
        return sum(_production_default_value_width(item) for item in value_type.items)
    if not isinstance(value_type, ActionScalarType):
        _fail(
            "production_default_unsupported_value_type",
            "ActionSpec",
            type(value_type).__name__,
        )
    return {
        ActionScalarKind.BOOL: 1,
        ActionScalarKind.I32: 4,
        ActionScalarKind.I64: 8,
        ActionScalarKind.U32: 4,
        ActionScalarKind.U64: 8,
        ActionScalarKind.F32: 4,
        ActionScalarKind.F64: 8,
    }[value_type.kind]


def _production_default_record_width(record_type: object) -> int:
    fields = getattr(record_type, "fields", None)
    if not isinstance(fields, tuple):
        _fail(
            "production_default_record_type_required",
            "ActionSpec",
            type(record_type).__name__,
        )
    return sum(
        _production_default_value_width(field.value_type) for field in fields
    )


def _production_default_contract_class(bound: BoundAction) -> str:
    if bound.producer_kind is ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS:
        effects = set(verify_action_spec(bound.compiled.spec).inferred_effects)
        if any(effect.value == "keyed_reduce" for effect in effects):
            return "grouped_i64x2_count_sum"
        if any(effect.value == "filter" for effect in effects):
            return "filter_bounded_emit"
        _fail(
            "production_default_verified_columns_shape_unknown",
            "bound.compiled.spec",
            bound.compiled.spec.semantic_digest,
        )
    return {
        ActionProducerKind.PREPARED_POINT_CANDIDATES_3D: "bounded_selection_3d",
        ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D: "filter_bounded_emit",
        ActionProducerKind.STABLE_RAY_TRIANGLE_CANDIDATES_3D: "keyed_i64_sum",
        ActionProducerKind.COMPLETE_QUERY_GROUPED_DISTANCE_ROWS: (
            "certified_query_min_state"
        ),
        ActionProducerKind.CERTIFIED_NEAREST_STATE_3D: "exact_witness",
    }[bound.producer_kind]


def _normalized_production_extents(
    extents: Mapping[ExtentKind | str, int],
) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key, raw in extents.items():
        name = key.value if isinstance(key, ExtentKind) else str(key)
        if name in normalized:
            _fail("duplicate_extent", f"extents.{name}", "duplicate normalized key")
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            _fail("invalid_extent", f"extents.{name}", repr(raw))
        normalized[name] = raw
    return dict(sorted(normalized.items()))


def _compile_bound_action_with_production_default(
    bound: BoundAction,
    target: ActionTargetProfile,
    *,
    capabilities: tuple[ActionBackendCapability, ...],
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None,
    consumer_composition: ActionConsumerCompositionKind | None,
    producer_event_region: ActionProducerEventRegionKind | None,
    semantic_statement_stable_id: str | None,
    backend_contract_id: str | None,
) -> PlannedLoweredAction:
    """Bind the real common-Action production path to DEFAULT."""

    from .default_physical_selection import (
        OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
        current_registry_snapshot,
    )
    from .production_default_integration import (
        ProductionDefaultIntegrationError,
        _compile_canonical_production_plan,
        bind_default_plan_to_lowering,
        compile_production_default_plan,
        make_production_action_descriptor,
        make_production_target_descriptor,
    )
    from .canonical_physical_resolution import (
        CanonicalPhysicalResolutionError,
        bind_canonical_provider_to_materialized_plan,
        registered_backend_contract,
        registered_semantic_statement,
        resolve_canonical_provider,
    )

    if target.profile_source not in {
        "runtime_capability_probe",
        "fork_clean_runtime_capability_probe",
    }:
        _fail(
            "production_default_requires_runtime_target_probe",
            "target.profile_source",
            target.profile_source,
        )
    if target.device_memory_limit_bytes is None:
        _fail(
            "production_default_device_memory_fact_missing",
            "target.device_memory_limit_bytes",
            "runtime probe did not produce a device-memory limit",
        )
    normalized_extents = _normalized_production_extents(extents)
    normalized_parameters = dict(sorted((parameters or {}).items()))
    if bound.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        nearest_query_count = normalized_extents.get(
            ExtentKind.QUERY_COUNT.value, 0
        )
        nearest_primitive_count = normalized_extents.get(
            ExtentKind.PRIMITIVE_COUNT.value, 0
        )
        if nearest_query_count <= 0 or nearest_primitive_count <= 0:
            _fail(
                "production_default_nearest_extents_incomplete",
                "extents",
                "certified-nearest DEFAULT requires positive query_count and primitive_count",
            )
    resource_probe = bound.plan(
        capabilities,
        extents=extents,
        parameters=parameters,
    )
    logical_count = max([1, *normalized_extents.values()])
    query_count = normalized_extents.get(ExtentKind.QUERY_COUNT.value, 0)
    primitive_count = normalized_extents.get(ExtentKind.PRIMITIVE_COUNT.value, 0)
    pair_count = (
        query_count * primitive_count
        if query_count and primitive_count
        else logical_count * logical_count
    )
    event_width = max(1, _production_default_record_width(bound.compiled.spec.event_type))
    parameter_width = _production_default_record_width(
        bound.compiled.spec.parameter_type
    )
    contract_class = _production_default_contract_class(bound)
    registry = current_registry_snapshot()
    family_rows = tuple(
        row
        for row in registry.declarations
        if row.semantic_kind == bound.producer_kind.value
        and contract_class in row.accepted_action_contract_classes
    )
    mandatory_nvidia_rt = any(
        OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in row.physical_capabilities
        for row in family_rows
    )
    providers: set[str] = set()
    if target.optix_available:
        providers.update(("cuda", "cupy", "optix"))
    if target.numba_available:
        providers.add("numba")
    if target.embree_available:
        providers.add("embree")
    if target.cpu_reference_available:
        providers.add("python")
    action_descriptor = make_production_action_descriptor(
        semantic_kind=bound.producer_kind.value,
        action_contract_class=contract_class,
        action_semantic_digest=bound.compiled.spec.semantic_digest,
        output_contract={
            "emits": [emit.to_dict() for emit in bound.compiled.spec.emits],
            "logical_event": bound.compiled.spec.logical_event.to_dict(),
            "numeric_contract": bound.compiled.spec.numeric_contract.to_dict(),
            "overflow_policy": bound.compiled.spec.overflow_policy.value,
        },
        work_domain={
            "producer_kind": bound.producer_kind.value,
            "producer_binding_digest": bound.binding_digest,
            "extents": normalized_extents,
            "parameters": normalized_parameters,
            "consumer_composition": (
                consumer_composition.value
                if consumer_composition is not None
                else None
            ),
            "producer_event_region": (
                producer_event_region.value
                if producer_event_region is not None
                else None
            ),
        },
        input_bytes=(pair_count if pair_count else logical_count) * event_width
        + parameter_width,
        output_bytes=resource_probe.resources.bounded_output_bytes,
        prepared_bytes=resource_probe.resources.total_state_bytes,
        logical_cardinality_bound=logical_count,
        pair_cardinality_bound=pair_count,
        logical_item_bytes_bound=event_width,
        pair_item_bytes_bound=event_width,
    )
    target_descriptor = make_production_target_descriptor(
        target_identity={
            "target_profile": target.to_metadata(),
            "producer_kind": bound.producer_kind.value,
            "mandatory_nvidia_rt": mandatory_nvidia_rt,
        },
        available_providers=providers,
        memory_limit_bytes=target.device_memory_limit_bytes,
        mandatory_nvidia_rt=mandatory_nvidia_rt,
    )
    canonical_resolution: Mapping[str, object] | None = None
    if semantic_statement_stable_id is not None:
        assert backend_contract_id is not None
        try:
            statement = registered_semantic_statement(
                semantic_statement_stable_id
            )
            backend_contract = registered_backend_contract(backend_contract_id)
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
        except CanonicalPhysicalResolutionError as exc:
            _fail(
                "canonical_physical_resolution_failed",
                "semantic_statement/backend_contract",
                str(exc),
            )
    try:
        if canonical_resolution is None:
            production_plan = compile_production_default_plan(
                action_descriptor,
                target_descriptor,
                mandatory_nvidia_rt=mandatory_nvidia_rt,
                repository_root=Path(__file__).resolve().parents[2],
            )
        else:
            production_plan = _compile_canonical_production_plan(
                action_descriptor,
                target_descriptor,
                mandatory_nvidia_rt=mandatory_nvidia_rt,
                canonical_provider_stable_id=str(
                    canonical_resolution["provider_candidate_stable_id"]
                ),
                repository_root=Path(__file__).resolve().parents[2],
            )
    except ProductionDefaultIntegrationError as exc:
        _fail("production_default_selection_failed", "DEFAULT", str(exc))
    winner_id = production_plan["selected_candidate_stable_id"]
    declaration = next(
        row for row in registry.declarations if row.stable_id == winner_id
    )
    available_by_backend = {
        capability.backend: capability for capability in capabilities
    }
    selected_capability = available_by_backend.get(declaration.backend)
    if selected_capability is None or not selected_capability.available:
        _fail(
            "production_default_selected_unavailable_backend",
            "DEFAULT.selected_candidate",
            declaration.backend,
        )
    forced_capabilities = tuple(
        replace(
            capability,
            priority=(0 if capability.backend == declaration.backend else 1000 + capability.priority),
        )
        for capability in capabilities
    )
    planned = plan_and_lower_action(
        bound,
        forced_capabilities,
        target_profile=target,
        extents=extents,
        parameters=parameters,
        consumer_composition=consumer_composition,
        producer_event_region=producer_event_region,
    )
    try:
        binding = bind_default_plan_to_lowering(
            production_plan,
            actual_backend=planned.lowered.backend,
            actual_template=planned.lowered.template_kind,
            repository_root=Path(__file__).resolve().parents[2],
        )
    except ProductionDefaultIntegrationError as exc:
        _fail("production_default_lowering_binding_failed", "DEFAULT", str(exc))
    canonical_authority: Mapping[str, object] | None = None
    if canonical_resolution is not None:
        try:
            canonical_authority = bind_canonical_provider_to_materialized_plan(
                canonical_resolution,
                materialized_provider_stable_id=winner_id,
                materialized_plan_sha256=production_plan["production_plan_sha256"],
                materialized_binding_sha256=binding["binding_sha256"],
            )
        except CanonicalPhysicalResolutionError as exc:
            _fail(
                "canonical_provider_materialization_mismatch",
                "production_plan.selected_candidate_stable_id",
                str(exc),
            )
    trace = dict(planned.lowered.compiler_execution_trace or {})
    trace["production_default"] = {
        "policy": "rtdl.production_default.goal5697.v1",
        "plan": production_plan,
        "binding": binding,
        "normal_caller_candidate_override_accepted": False,
        "mandatory_optix_behavior_requires_post_execution_receipt": (
            mandatory_nvidia_rt
        ),
        "partner_stage_can_satisfy_rt_claim": False,
        "production_default_changed": True,
        "canonical_resolution_is_selection_authority": (
            canonical_authority is not None
        ),
        "legacy_default_is_compatibility_materializer_only": (
            False
        ),
        "legacy_default_is_selection_authority": (
            canonical_authority is None
        ),
        "canonical_provider_materializer_used": (
            canonical_authority is not None
        ),
        "default_optimizer_selected_provider": (
            canonical_authority is None
        ),
        "canonical_resolution": canonical_resolution,
        "canonical_production_authority": canonical_authority,
    }
    resealed = replace(
        planned,
        lowered=replace(planned.lowered, compiler_execution_trace=trace),
    )
    return _seal_planned_lowered_action(resealed)


def compile_bound_certified_nearest_candidate_for_functional_validation(
    bound: BoundAction,
    target: ActionTargetProfile,
    *,
    physical_candidate: str,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, int] | None = None,
    consumer_composition: ActionConsumerCompositionKind,
) -> PlannedLoweredAction:
    """Materialize one compiler-registered nearest candidate for validation.

    This private compiler/review front door is intentionally narrower than the
    application API.  It cannot introduce a candidate, change semantic
    extents, or establish normal target priority.  Its only purpose is to
    execute every already legal physical candidate before performance
    calibration exists.
    """

    if (
        not isinstance(bound, BoundAction)
        or bound.producer_kind
        is not ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
    ):
        _fail(
            "certified_nearest_validation_binding_required",
            "bound",
            type(bound).__name__,
        )
    allowed = {
        "cuda_grid",
        "optix_traversal",
        CELL_MBR_EXACT_WITNESS_3D_BACKEND,
    }
    if physical_candidate not in allowed:
        _fail(
            "certified_nearest_validation_candidate_invalid",
            "physical_candidate",
            repr(physical_candidate),
        )
    capabilities = compiler_action_capabilities(bound, target)
    registered = {
        capability.backend: capability for capability in capabilities
    }
    capability = registered.get(physical_candidate)
    if capability is None or not capability.available:
        _fail(
            "certified_nearest_validation_candidate_unavailable",
            "physical_candidate",
            physical_candidate,
        )
    validation_capabilities = tuple(
        replace(
            candidate,
            priority=(
                0
                if candidate.backend == physical_candidate
                else 50 + candidate.priority
            ),
        )
        for candidate in capabilities
    )
    planned = plan_and_lower_action(
        bound,
        validation_capabilities,
        target_profile=target,
        extents=extents,
        parameters=parameters,
        consumer_composition=consumer_composition,
    )
    if planned.lowered.backend != physical_candidate:
        _fail(
            "certified_nearest_validation_candidate_not_selected",
            "planned.lowered.backend",
            planned.lowered.backend,
        )
    return planned


def _normalized_extent_value(
    extents: Mapping[ExtentKind | str, int],
    kind: ExtentKind,
) -> int:
    values = [
        value
        for key, value in extents.items()
        if (key.value if isinstance(key, ExtentKind) else str(key)) == kind.value
    ]
    if len(values) != 1:
        _fail(
            "consumer_composition_extent_required",
            f"extents.{kind.value}",
            repr(values),
        )
    value = values[0]
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail(
            "consumer_composition_extent_invalid",
            f"extents.{kind.value}",
            repr(value),
        )
    return value


def _bind_composition_resources_before_selection(
    plan: ActionPlacementPlan,
    capabilities: tuple[ActionBackendCapability, ...],
    resources_contract: ActionConsumerCompositionResources,
) -> ActionPlacementPlan:
    """Price semantic Action state for every candidate, then choose placement."""

    if plan.cost_predictions:
        _fail(
            "consumer_composition_cost_model_requires_composed_calibration",
            "plan.cost_predictions",
            "uncomposed cost evidence cannot price the explicit reducer",
        )
    resources = replace(
        plan.resources,
        total_state_bytes=resources_contract.total_state_byte_bound,
        bounded_output_rows=resources_contract.output_row_bound,
        bounded_output_bytes=resources_contract.output_byte_bound,
    )
    capability_by_backend = {
        capability.backend: capability for capability in capabilities
    }
    composed_candidates = []
    for candidate in plan.candidates:
        capability = capability_by_backend[candidate.backend]
        state_charge = (
            candidate.state_bytes_charged + resources_contract.reducer_state_bytes
        )
        reasons = list(candidate.reasons)
        composition_reasons = []
        if (
            capability.max_state_bytes is not None
            and state_charge > capability.max_state_bytes
            and "consumer_composition_state_resource_limit_exceeded" not in reasons
        ):
            composition_reasons.append(
                "consumer_composition_state_resource_limit_exceeded"
            )
        if (
            capability.max_output_bytes is not None
            and resources_contract.output_byte_bound > capability.max_output_bytes
            and "consumer_composition_output_resource_limit_exceeded" not in reasons
        ):
            composition_reasons.append(
                "consumer_composition_output_resource_limit_exceeded"
            )
        reasons.extend(composition_reasons)
        composed_candidates.append(
            replace(
                candidate,
                legal=candidate.legal and not composition_reasons,
                reasons=tuple(reasons),
                state_bytes_charged=state_charge,
                output_bytes_charged=resources_contract.output_byte_bound,
            )
        )
    candidates = tuple(composed_candidates)
    legal = tuple(candidate for candidate in candidates if candidate.legal)
    if not legal:
        _fail(
            "consumer_composition_no_legal_placement",
            "capabilities",
            "; ".join(
                f"{candidate.backend}:{','.join(candidate.reasons)}"
                for candidate in candidates
            ),
        )
    selected = min(legal, key=lambda candidate: (candidate.priority, candidate.backend))
    rejected_preferred = [
        candidate
        for candidate in candidates
        if candidate.priority < selected.priority and not candidate.legal
    ]
    selection_reason = "lowest_priority_legal_placement"
    if rejected_preferred:
        selection_reason = "fallback_after_" + "+".join(
            sorted(
                {
                    reason
                    for candidate in rejected_preferred
                    for reason in candidate.reasons
                }
            )
        )
    if plan.cost_model_status.value == "unavailable_or_out_of_domain":
        selection_reason = "cost_model_fallback_to_" + selection_reason
    return replace(
        plan,
        resources=resources,
        selected_backend=selected.backend,
        selected_placement=selected.placement,
        selection_reason=selection_reason,
        candidates=candidates,
    )


def _planned_lowering_seal_payload(planned: PlannedLoweredAction) -> bytes:
    composition = planned.consumer_composition
    payload = {
        "contract": "rtdl.action_planned_lowering.compiler_seal.v1",
        "plan": planned.plan.to_dict(),
        "lowered": planned.lowered.to_metadata(),
        "target_profile": planned.target_profile.to_metadata(),
        "template_preflight_rejections": [
            [backend, reason]
            for backend, reason in planned.template_preflight_rejections
        ],
        "consumer_composition": (
            composition.to_metadata() if composition is not None else None
        ),
        "native_library_binding": {
            "identity": (
                planned.compiler_native_library_identity.to_metadata()
                if planned.compiler_native_library_identity is not None
                else None
            ),
            "object_id": planned._compiler_native_library_object_id,
            "strong_ref_object_id": (
                id(planned._compiler_native_library_ref)
                if planned._compiler_native_library_ref is not None
                else None
            ),
        },
        "runtime_input_binding": {
            "prepared_digest": planned.compiler_prepared_input_digest,
            "prepared_digest_kind": planned.compiler_prepared_input_digest_kind,
            "prepared_object_id": planned._compiler_prepared_input_object_id,
            "prepared_strong_ref_object_id": (
                id(planned._compiler_prepared_input_ref)
                if planned._compiler_prepared_input_ref is not None
                else None
            ),
            "first_query_digest": planned.compiler_first_query_input_digest,
            "first_query_digest_kind": planned.compiler_first_query_input_digest_kind,
            "first_query_object_id": planned._compiler_first_query_input_object_id,
            "first_query_strong_ref_object_id": (
                id(planned._compiler_first_query_input_ref)
                if planned._compiler_first_query_input_ref is not None
                else None
            ),
        },
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _seal_planned_lowered_action(
    planned: PlannedLoweredAction,
) -> PlannedLoweredAction:
    unsigned = replace(planned, _compiler_seal="")
    signature = hmac.new(
        _ACTION_PLAN_SECRET,
        _planned_lowering_seal_payload(unsigned),
        hashlib.sha256,
    ).hexdigest()
    return replace(unsigned, _compiler_seal=signature)


def _planned_lowering_seal_valid(planned: PlannedLoweredAction) -> bool:
    if not isinstance(planned._compiler_seal, str) or not planned._compiler_seal:
        return False
    try:
        payload = _planned_lowering_seal_payload(
            replace(planned, _compiler_seal="")
        )
    except (AttributeError, TypeError, ValueError):
        return False
    expected = hmac.new(_ACTION_PLAN_SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(planned._compiler_seal, expected)


def validate_planned_lowered_action(planned: PlannedLoweredAction) -> None:
    """Verify compiler provenance and every plan/runtime/composition binding."""

    if not isinstance(planned, PlannedLoweredAction):
        _fail(
            "planned_lowered_action_required",
            "planned",
            type(planned).__name__,
        )
    if not _planned_lowering_seal_valid(planned):
        _fail(
            "planned_lowering_compiler_seal_invalid",
            "planned._compiler_seal",
            "plan or runtime binding changed after compiler issuance",
        )
    prepared_binding_present = planned.compiler_prepared_input_digest is not None
    if prepared_binding_present != (
        planned.compiler_prepared_input_digest_kind is not None
        and planned._compiler_prepared_input_object_id is not None
        and planned._compiler_prepared_input_ref is not None
        and id(planned._compiler_prepared_input_ref)
        == planned._compiler_prepared_input_object_id
    ):
        _fail(
            "planned_prepared_input_binding_invalid",
            "planned.compiler_prepared_input_digest",
            "digest, kind, object ID, and strong reference must agree",
        )
    first_query_binding_present = planned.compiler_first_query_input_digest is not None
    if first_query_binding_present != (
        planned.compiler_first_query_input_digest_kind is not None
        and planned._compiler_first_query_input_object_id is not None
        and planned._compiler_first_query_input_ref is not None
        and id(planned._compiler_first_query_input_ref)
        == planned._compiler_first_query_input_object_id
    ):
        _fail(
            "planned_first_query_input_binding_invalid",
            "planned.compiler_first_query_input_digest",
            "digest, kind, object ID, and strong reference must agree",
        )
    native_binding_present = planned.compiler_native_library_identity is not None
    if native_binding_present != (
        planned._compiler_native_library_object_id is not None
        and planned._compiler_native_library_ref is not None
        and id(planned._compiler_native_library_ref)
        == planned._compiler_native_library_object_id
    ):
        _fail(
            "planned_native_library_binding_invalid",
            "planned.compiler_native_library_identity",
            "identity, object ID, and strong reference must agree",
        )
    if planned.plan.selected_backend != planned.lowered.backend:
        _fail(
            "planned_lowering_backend_mismatch",
            "planned.lowered.backend",
            planned.lowered.backend,
        )
    if planned.plan.selected_placement.value != planned.lowered.placement:
        _fail(
            "planned_lowering_placement_mismatch",
            "planned.lowered.placement",
            planned.lowered.placement,
        )
    if planned.consumer_composition != planned.lowered.consumer_composition:
        _fail(
            "planned_lowering_composition_mismatch",
            "planned.consumer_composition",
            "planned and lowered composition certificates differ",
        )
    requires_certified_nearest_native = (
        planned.lowered.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
        and planned.lowered.backend
        in {
            "cuda_grid",
            "optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_BACKEND,
        }
        and planned.lowered.template_kind
        in {
            "certified_nearest_state_3d",
            "certified_nearest_state_3d_optix_traversal",
            CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE,
        }
    )
    trace = planned.lowered.compiler_execution_trace
    physical_registry = (
        trace.get("physical_registry") if isinstance(trace, Mapping) else None
    )
    requires_registered_point_native = (
        planned.lowered.producer_kind
        is ActionProducerKind.PREPARED_POINT_CANDIDATES_3D
        and planned.lowered.template_kind
        in {
            "point_candidate_bounded_selection_3d",
            "prepared_ranked_distance_window_qk_3d",
            "candidate_pruned_exact_bounded_selection_3d",
        }
        and isinstance(physical_registry, Mapping)
        and physical_registry.get("contract")
        == "rtdl.action_physical_registry.private_candidate.v5"
    )
    requires_grouped_native_order = (
        planned.lowered.backend == "numba"
        and planned.lowered.template_kind == "grouped_i64x2_count_sum"
    )
    requires_exact_native = (
        requires_certified_nearest_native
        or requires_registered_point_native
        or requires_grouped_native_order
    )
    if requires_exact_native != native_binding_present:
        _fail(
            "planned_native_library_binding_route_mismatch",
            "planned.compiler_native_library_identity",
            "the exact native library binding must exist for every selected registered native route and no nonnative route",
        )
    if planned.lowered.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        if planned.consumer_composition is not None:
            validate_certified_nearest_global_argmax_composition(
                planned.consumer_composition,
                spec=planned.lowered.compiled.spec,
                action_source_digest=planned.lowered.compiled.source_digest,
                producer_kind=planned.lowered.producer_kind.value,
                producer_binding_digest=planned.lowered.producer_binding_digest,
                selected_backend=planned.lowered.backend,
                selected_placement=planned.lowered.placement,
                selected_template=planned.lowered.template_kind,
                template_identity_digest=action_template_identity_digest(
                    planned.lowered.program.to_metadata()
                    if hasattr(planned.lowered.program, "to_metadata")
                    else {"template": planned.lowered.template_kind}
                ),
                query_count=planned.consumer_composition.query_count,
            )


def _reseal_planned_lowered_action(
    planned: PlannedLoweredAction,
) -> PlannedLoweredAction:
    """Compiler-internal hook for trusted registries that add runtime bindings."""

    return _seal_planned_lowered_action(planned)


def _binding_payload(
    compiled: CompiledAction,
    producer_kind: ActionProducerKind,
    delivery_proofs: frozenset[str],
    termination_certificates: frozenset[str],
    ordering_certificates: frozenset[str],
    logical_event_key_digest: str | None,
    event_column_certificate: VerifiedEventColumnBatchCertificate | None,
) -> bytes:
    fields = (
        ACTION_API_CANDIDATE_VERSION,
        compiled.spec.semantic_digest,
        compiled.source_digest,
        producer_kind.value,
        ",".join(sorted(delivery_proofs)),
        ",".join(sorted(termination_certificates)),
        ",".join(sorted(ordering_certificates)),
        logical_event_key_digest or "",
        (
            json.dumps(
                event_column_certificate.to_metadata(),
                sort_keys=True,
                separators=(",", ":"),
            )
            if event_column_certificate is not None
            else ""
        ),
    )
    return "\x1f".join(fields).encode("utf-8")


def _validate_binding(bound: BoundAction) -> None:
    if not isinstance(bound.producer_kind, ActionProducerKind):
        _fail("producer_binding_forged", "producer_kind", type(bound.producer_kind).__name__)
    contract = _PRODUCER_CONTRACTS[bound.producer_kind]
    if (
        bound.delivery_proofs != contract.delivery_proofs
        or bound.termination_certificates != contract.termination_certificates
        or bound.ordering_certificates != contract.ordering_certificates
    ):
        _fail("producer_binding_forged", "certificates", bound.producer_kind.value)
    payload = _binding_payload(
        bound.compiled,
        bound.producer_kind,
        bound.delivery_proofs,
        bound.termination_certificates,
        bound.ordering_certificates,
        bound.logical_event_key_digest,
        bound.event_column_certificate,
    )
    expected_digest = hashlib.sha256(payload).hexdigest()
    expected_signature = hmac.new(_ACTION_BINDING_SECRET, payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(bound.binding_digest, expected_digest) or not hmac.compare_digest(
        bound._signature, expected_signature
    ):
        _fail("producer_binding_forged", "signature", bound.producer_kind.value)


def validate_bound_action_event_columns(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
) -> VerifiedEventColumnBatchCertificate:
    """Revalidate the exact typed batch bound to a lowered Action."""

    if not isinstance(lowered, LoweredAction):
        _fail("lowered_action_required", "lowered", type(lowered).__name__)
    expected = lowered.event_column_certificate
    if expected is None:
        _fail(
            "direct_column_certificate_required",
            "lowered.event_column_certificate",
            "the lowered Action was not bound through direct verified columns",
        )
    actual = _verify_event_column_batch(
        lowered.compiled,
        event_columns,
        ordering_fields=expected.ordering_fields,
    )
    if actual != expected:
        _fail(
            "event_column_batch_mismatch",
            "event_columns",
            f"expected {expected.batch_digest}; got {actual.batch_digest}",
        )
    return actual


def rebind_lowered_action_event_columns(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
    *,
    max_row_count: int | None = None,
) -> LoweredAction:
    """Issue a fresh batch certificate without recompiling the legal template.

    The default preserves the original exact-row-count prepared contract. A
    compiler-owned prepared stream may instead supply a positive maximum row
    count; every rebound batch is still fully schema, ordering, duplicate-key,
    and template verified before execution.
    """

    if not isinstance(lowered, LoweredAction):
        _fail("lowered_action_required", "lowered", type(lowered).__name__)
    expected = lowered.event_column_certificate
    if expected is None:
        _fail(
            "direct_column_certificate_required",
            "lowered.event_column_certificate",
            "prepared column rebinding requires an initial direct-column certificate",
        )
    rebound = bind_action_event_columns(
        lowered.compiled,
        event_columns,
        ordering_fields=expected.ordering_fields,
        producer_kind=lowered.producer_kind,
    )
    actual = rebound.event_column_certificate
    if actual is None:
        _fail("direct_column_certificate_required", "rebound", "certificate missing")
    if max_row_count is not None:
        if not isinstance(max_row_count, int) or isinstance(max_row_count, bool) or max_row_count < 0:
            _fail(
                "invalid_prepared_event_batch_capacity",
                "max_row_count",
                repr(max_row_count),
            )
        row_count_mismatch = actual.row_count > max_row_count
    else:
        row_count_mismatch = actual.row_count != expected.row_count
    if (
        actual.schema_digest != expected.schema_digest
        or actual.ordering_fields != expected.ordering_fields
        or row_count_mismatch
    ):
        row_contract = (
            f"row count must be <= {max_row_count}"
            if max_row_count is not None
            else f"row count must equal {expected.row_count}"
        )
        _fail(
            "prepared_event_batch_contract_mismatch",
            "event_columns",
            f"schema and ordering must match the prepared identity; {row_contract}",
        )
    _validate_template_column_ordering(rebound, lowered.template_kind, lowered.program)
    return replace(
        lowered,
        producer_binding_digest=rebound.binding_digest,
        logical_event_key_digest=rebound.logical_event_key_digest,
        event_column_certificate=actual,
    )


def prepare_bound_numba_action_columns(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
    parameters: Mapping[str, object],
):
    """Prepare the exact host column batch whose logical keys were compiler-verified."""

    if not isinstance(lowered, LoweredAction):
        _fail("lowered_action_required", "lowered", type(lowered).__name__)
    if (
        lowered.backend != "numba"
        or lowered.template_kind not in {"filter_bounded_emit", "grouped_i64x2_count_sum"}
        or lowered.producer_kind is not ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS
        or lowered.logical_event_key_digest is None
    ):
        _fail("verified_column_binding_required", "lowered", lowered.template_kind)
    if lowered.event_column_certificate is not None:
        validate_bound_action_event_columns(lowered, event_columns)
    else:
        rows = _host_key_rows(
            lowered.compiled.spec.logical_event.key_fields,
            event_columns,
        )
        actual_digest = _logical_event_key_digest(
            lowered.compiled.spec.logical_event.key_fields,
            rows,
        )
        if actual_digest != lowered.logical_event_key_digest:
            _fail(
                "logical_event_batch_mismatch",
                "event_columns",
                f"expected {lowered.logical_event_key_digest}; got {actual_digest}",
            )
    if lowered.template_kind == "filter_bounded_emit":
        return prepare_numba_action_columns(lowered.program, event_columns, parameters)
    if parameters:
        _fail("unexpected_parameters", "parameters", "grouped reduction accepts no parameters")
    return prepare_numba_grouped_i64x2_count_sum_columns(lowered.program, event_columns)


def prepare_grouped_i64x2_count_sum_execution(
    planned: PlannedLoweredAction,
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
    max_event_rows: int,
):
    """Prepare the compiler-selected grouped reduction physical template.

    The application supplies only the verified plan and semantic capacity. It
    cannot request the host or device implementation by name.  For the exact
    generic grouped-i64x2 semantic shape, both host and order-indexed device
    continuations remain legal when available.  Without an in-domain
    compiler-owned cost calibration, the fixed-priority fallback selects the
    lower-overhead checked host continuation; applications still name neither.
    """

    validate_planned_lowered_action(planned)
    lowered = planned.lowered
    if (
        lowered.backend == "host"
        and lowered.template_kind == "sorted_host_i64x2_count_sum"
    ):
        if extents or parameters:
            _fail(
                "grouped_host_query_contract_mismatch",
                "extents_or_parameters",
                "grouped host reduction accepts empty extents and parameters",
            )
        return prepare_host_grouped_i64x2_count_sum_execution(
            planned,
            max_event_rows=max_event_rows,
        )
    if (
        lowered.backend == "numba"
        and lowered.template_kind == "grouped_i64x2_count_sum"
    ):
        from .action_prepared import prepare_action_execution

        native_order_context = _validated_grouped_native_order_context(
            expected_identity=planned.compiler_native_library_identity,
            expected_library_ref=planned._compiler_native_library_ref,
        )
        specialization = (
            eager_specialize_numba_grouped_i64x2_count_sum(
                lowered.program,
                native_order_context=native_order_context,
            )
            if max_event_rows > 0
            else {
                "contract": "rtdl.grouped_i64x2_eager_device_specialization.v1",
                "elapsed_seconds": 0.0,
                "synthetic_row_count": 0,
                "complete_physical_route_executed": False,
                "registered_query_count": 0,
                "kernel_launch_delta": 0,
                "reason": "zero_capacity",
                "runtime_speedup_claimed": False,
            }
        )
        prepared = prepare_action_execution(
            planned,
            extents=extents,
            parameters=parameters,
            max_event_rows=max_event_rows,
        )
        return EagerSpecializedGroupedI64x2PreparedExecution(
            prepared,
            specialization,
        )
    _fail(
        "grouped_i64x2_compiler_plan_required",
        "planned.lowered",
        f"{lowered.backend}:{lowered.template_kind}",
    )


def _validated_grouped_native_order_context(
    *,
    expected_identity: ActionNativeLibraryIdentity | None,
    expected_library_ref: object | None = None,
):
    probe = probe_grouped_i64x2_native_order()
    if not probe.available or probe.context is None:
        _fail(
            "grouped_native_order_prerequisite_unavailable",
            "grouped_native_order_probe",
            probe.error or "native grouped ordering context is unavailable",
        )
    context = probe.context
    if (
        expected_identity is None
        or context.library_identity != expected_identity
        or (
            expected_library_ref is not None
            and context.library_ref is not expected_library_ref
        )
    ):
        _fail(
            "grouped_native_order_identity_mismatch",
            "grouped_native_order_context",
            "the live native ordering context differs from the compiler-bound identity",
        )
    context.validate_full_identity()
    return context


def prepare_bound_numba_action_device_columns(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
    parameters: Mapping[str, object],
    *,
    max_row_count: int,
):
    """Prepare a compiler-owned device batch for the closed grouped template.

    Applications provide typed device columns only.  The compiler derives the
    logical single-delivery key, orders the batch, copies it into private
    device allocations, and verifies the resulting permutation and order
    before the Action kernel can observe it.
    """

    if not isinstance(lowered, LoweredAction):
        _fail("lowered_action_required", "lowered", type(lowered).__name__)
    if (
        lowered.backend != "numba"
        or lowered.template_kind != "grouped_i64x2_count_sum"
        or lowered.producer_kind is not ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS
        or lowered.event_column_certificate is None
    ):
        _fail("verified_device_column_binding_required", "lowered", lowered.template_kind)
    if parameters:
        _fail("unexpected_parameters", "parameters", "grouped reduction accepts no parameters")
    expected_order = (
        *tuple(lowered.program.key_fields),
        *tuple(lowered.compiled.spec.logical_event.key_fields),
    )
    if tuple(lowered.event_column_certificate.ordering_fields) != expected_order:
        _fail(
            "device_column_ordering_contract_mismatch",
            "lowered.event_column_certificate.ordering_fields",
            repr(lowered.event_column_certificate.ordering_fields),
        )
    trace = lowered.compiler_execution_trace
    identity_payload = (
        trace.get("selected_native_library_identity")
        if isinstance(trace, Mapping)
        else None
    )
    if not isinstance(identity_payload, Mapping):
        _fail(
            "grouped_native_order_identity_missing",
            "lowered.compiler_execution_trace",
            "selected grouped device lowering lacks its native ordering identity",
        )
    probe = probe_grouped_i64x2_native_order()
    expected_digest = identity_payload.get("identity_digest")
    if (
        not probe.available
        or probe.context is None
        or probe.context.library_identity.identity_digest != expected_digest
    ):
        _fail(
            "grouped_native_order_identity_mismatch",
            "lowered.compiler_execution_trace.selected_native_library_identity",
            "the live grouped ordering context differs from the planned ABI identity",
        )
    probe.context.validate_hot_binding()
    return prepare_numba_grouped_i64x2_count_sum_device_columns(
        lowered.program,
        event_columns,
        max_row_count=max_row_count,
        native_order_context=probe.context,
    )


def prepare_bound_numba_action_compiler_snapshot(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
    parameters: Mapping[str, object],
    *,
    max_row_count: int,
    private_workspace=None,
    workspace_generation_digest: str | None = None,
):
    """Prepare a sealed producer-completion device snapshot for reduction."""

    if not isinstance(lowered, LoweredAction):
        _fail("lowered_action_required", "lowered", type(lowered).__name__)
    if (
        lowered.backend != "numba"
        or lowered.template_kind != "grouped_i64x2_count_sum"
        or lowered.producer_kind
        is not ActionProducerKind.VERIFIED_LOGICAL_EVENT_COLUMNS
        or lowered.event_column_certificate is None
    ):
        _fail(
            "verified_device_column_binding_required",
            "lowered",
            lowered.template_kind,
        )
    if parameters:
        _fail(
            "unexpected_parameters",
            "parameters",
            "grouped reduction accepts no parameters",
        )
    trace = lowered.compiler_execution_trace
    identity_payload = (
        trace.get("selected_native_library_identity")
        if isinstance(trace, Mapping)
        else None
    )
    if not isinstance(identity_payload, Mapping):
        _fail(
            "grouped_native_order_identity_missing",
            "lowered.compiler_execution_trace",
            "selected grouped device lowering lacks its native ordering identity",
        )
    probe = probe_grouped_i64x2_native_order()
    if (
        not probe.available
        or probe.context is None
        or probe.context.library_identity.identity_digest
        != identity_payload.get("identity_digest")
    ):
        _fail(
            "grouped_native_order_identity_mismatch",
            "lowered.compiler_execution_trace.selected_native_library_identity",
            "the live grouped ordering context differs from the planned ABI identity",
        )
    probe.context.validate_hot_binding()
    return prepare_numba_grouped_i64x2_count_sum_compiler_snapshot(
        lowered.program,
        event_columns,
        max_row_count=max_row_count,
        native_order_context=probe.context,
        private_workspace=private_workspace,
        workspace_generation_digest=workspace_generation_digest,
    )


def _verify_event_column_batch(
    compiled: CompiledAction,
    event_columns: Mapping[str, object],
    *,
    ordering_fields: tuple[str, ...],
) -> VerifiedEventColumnBatchCertificate:
    import numpy as np

    if not isinstance(event_columns, Mapping):
        _fail("event_columns_mapping_required", "event_columns", type(event_columns).__name__)
    if not isinstance(ordering_fields, tuple) or not ordering_fields:
        _fail(
            "explicit_column_ordering_required",
            "ordering_fields",
            "direct column binding requires a nonempty lexicographic ordering",
        )
    if len(set(ordering_fields)) != len(ordering_fields) or not all(
        isinstance(field, str) and field for field in ordering_fields
    ):
        _fail("invalid_column_ordering_fields", "ordering_fields", repr(ordering_fields))

    fields = compiled.spec.event_type.fields
    expected_names = tuple(field.name for field in fields)
    if set(event_columns) != set(expected_names):
        _fail(
            "event_column_schema_mismatch",
            "event_columns",
            f"expected {sorted(expected_names)}",
        )
    if not set(compiled.spec.logical_event.key_fields).issubset(ordering_fields):
        _fail(
            "logical_key_missing_from_ordering_certificate",
            "ordering_fields",
            repr(compiled.spec.logical_event.key_fields),
        )
    if not set(ordering_fields).issubset(expected_names):
        _fail("unknown_column_ordering_field", "ordering_fields", repr(ordering_fields))

    arrays: dict[str, object] = {}
    row_count: int | None = None
    for field in fields:
        if not isinstance(field.value_type, ActionScalarType):
            _fail(
                "scalar_event_columns_required",
                f"event_columns.{field.name}",
                type(field.value_type).__name__,
            )
        value = event_columns[field.name]
        if hasattr(value, "__cuda_array_interface__") or hasattr(value, "copy_to_host"):
            _fail(
                "host_verified_columns_required",
                f"event_columns.{field.name}",
                "direct host verification must not hide a device-to-host copy",
            )
        array = np.asarray(value)
        expected_dtype = _event_column_numpy_dtype(field.value_type.kind, np)
        if array.ndim != 1 or array.dtype != expected_dtype or not array.flags.c_contiguous:
            _fail(
                "event_column_layout_mismatch",
                f"event_columns.{field.name}",
                f"expected contiguous 1-D {expected_dtype}",
            )
        if row_count is None:
            row_count = int(array.shape[0])
        elif row_count != int(array.shape[0]):
            _fail(
                "event_column_length_mismatch",
                f"event_columns.{field.name}",
                str(array.shape[0]),
            )
        if field.nonnegative and bool(np.any(array < 0)):
            _fail("nonnegative_field_violation", f"event_columns.{field.name}", field.name)
        if field.value_type.is_float:
            if compiled.spec.numeric_contract.reject_nan and bool(np.any(np.isnan(array))):
                _fail("nan_rejected", f"event_columns.{field.name}", "NaN is not admitted")
            if not compiled.spec.numeric_contract.allow_infinity and bool(
                np.any(np.isinf(array))
            ):
                _fail(
                    "infinity_not_admitted",
                    f"event_columns.{field.name}",
                    "infinity is not admitted",
                )
        arrays[field.name] = array
    resolved_count = row_count or 0

    key_fields = compiled.spec.logical_event.key_fields
    _reject_duplicate_logical_key_columns(arrays, key_fields, resolved_count, np)
    _validate_lexicographic_column_order(arrays, ordering_fields, resolved_count, np)

    schema_payload = {
        "contract": "rtdl.verified_event_column_schema.private_candidate.v1",
        "semantic_digest": compiled.spec.semantic_digest,
        "event_type": compiled.spec.event_type.to_dict(),
    }
    schema_digest = hashlib.sha256(
        json.dumps(schema_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    batch_digest = _typed_column_digest(
        compiled,
        arrays,
        expected_names,
        label="full_event_batch",
    )
    key_digest = _typed_column_digest(
        compiled,
        arrays,
        key_fields,
        label="logical_event_keys",
    )
    ordering_digest = _typed_column_digest(
        compiled,
        arrays,
        ordering_fields,
        label="lexicographic_order",
    )
    return VerifiedEventColumnBatchCertificate(
        row_count=resolved_count,
        schema_digest=schema_digest,
        batch_digest=batch_digest,
        logical_event_key_digest=key_digest,
        ordering_fields=ordering_fields,
        ordering_digest=ordering_digest,
    )


def _event_column_numpy_dtype(kind: ActionScalarKind, np):
    mapping = {
        ActionScalarKind.BOOL: np.dtype(np.bool_),
        ActionScalarKind.I32: np.dtype(np.int32),
        ActionScalarKind.I64: np.dtype(np.int64),
        ActionScalarKind.U32: np.dtype(np.uint32),
        ActionScalarKind.U64: np.dtype(np.uint64),
        ActionScalarKind.F32: np.dtype(np.float32),
        ActionScalarKind.F64: np.dtype(np.float64),
    }
    return mapping[kind]


def _typed_column_digest(
    compiled: CompiledAction,
    arrays: Mapping[str, object],
    field_names: tuple[str, ...],
    *,
    label: str,
) -> str:
    import numpy as np

    digest = hashlib.sha256()
    digest.update(b"rtdl.typed_event_columns.private_candidate.v1\x00")
    digest.update(compiled.spec.semantic_digest.encode("ascii"))
    digest.update(b"\x00")
    digest.update(label.encode("ascii"))
    for name in field_names:
        array = np.asarray(arrays[name])
        canonical = array
        if (
            array.dtype.kind == "f"
            and compiled.spec.numeric_contract.normalize_signed_zero
            and bool(np.any(array == 0))
        ):
            canonical = array.copy()
            canonical[canonical == 0] = 0.0
        canonical = canonical.astype(canonical.dtype.newbyteorder("<"), copy=False)
        digest.update(b"\x1f")
        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(canonical.dtype.str.encode("ascii"))
        digest.update(b"\x00")
        digest.update(str(int(canonical.shape[0])).encode("ascii"))
        digest.update(b"\x00")
        digest.update(canonical.tobytes(order="C"))
    return digest.hexdigest()


def _reject_duplicate_logical_key_columns(
    arrays: Mapping[str, object],
    key_fields: tuple[str, ...],
    row_count: int,
    np,
) -> None:
    if row_count < 2:
        return
    key_arrays = tuple(np.asarray(arrays[field]) for field in key_fields)
    order = np.lexsort(tuple(reversed(key_arrays)))
    duplicate = np.ones(row_count - 1, dtype=np.bool_)
    for array in key_arrays:
        ordered = array[order]
        duplicate &= ordered[1:] == ordered[:-1]
    if bool(np.any(duplicate)):
        offset = int(np.flatnonzero(duplicate)[0]) + 1
        source_index = int(order[offset])
        _fail(
            "duplicate_logical_event_key",
            f"event_columns[{source_index}]",
            "duplicate key rejected by vectorized column validation",
        )


def _validate_lexicographic_column_order(
    arrays: Mapping[str, object],
    ordering_fields: tuple[str, ...],
    row_count: int,
    np,
) -> None:
    if row_count < 2:
        return
    equal_prefix = np.ones(row_count - 1, dtype=np.bool_)
    descending = np.zeros(row_count - 1, dtype=np.bool_)
    for field in ordering_fields:
        array = np.asarray(arrays[field])
        descending |= equal_prefix & (array[1:] < array[:-1])
        equal_prefix &= array[1:] == array[:-1]
    if bool(np.any(descending)):
        index = int(np.flatnonzero(descending)[0]) + 1
        _fail(
            "event_column_order_certificate_violated",
            f"event_columns[{index}]",
            f"expected lexicographic nondecreasing order by {ordering_fields!r}",
        )


def _host_key_rows(
    key_fields: tuple[str, ...],
    columns: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    import numpy as np

    arrays = []
    for field in key_fields:
        if field not in columns:
            _fail("missing_logical_event_key_column", "event_columns", field)
        value = columns[field]
        if hasattr(value, "__cuda_array_interface__"):
            _fail(
                "host_verified_columns_required",
                f"event_columns.{field}",
                "this binding must not hide a device-to-host verification copy",
            )
        arrays.append(np.asarray(value))
    if any(array.ndim != 1 for array in arrays):
        _fail("logical_event_key_column_not_1d", "event_columns", "key columns must be 1-D")
    row_counts = {int(array.shape[0]) for array in arrays}
    if len(row_counts) != 1:
        _fail("logical_event_key_column_length_mismatch", "event_columns", str(sorted(row_counts)))
    row_count = next(iter(row_counts), 0)
    return tuple(
        {
            field: (array[index].item() if hasattr(array[index], "item") else array[index])
            for field, array in zip(key_fields, arrays)
        }
        for index in range(row_count)
    )


def _logical_event_key_digest(
    key_fields: tuple[str, ...],
    events: Sequence[Mapping[str, object]],
) -> str:
    keys: list[tuple[object, ...]] = []
    seen: set[tuple[object, ...]] = set()
    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            _fail("event_not_mapping", f"events[{index}]", type(event).__name__)
        try:
            key = tuple(event[field] for field in key_fields)
        except KeyError as exc:
            _fail("missing_logical_event_key_field", f"events[{index}]", str(exc.args[0]))
        if key in seen:
            _fail("duplicate_logical_event_key", f"events[{index}]", repr(key))
        seen.add(key)
        keys.append(key)
    try:
        encoded = json.dumps(keys, allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _fail("logical_event_key_not_canonical", "events", str(exc))
    return hashlib.sha256(encoded).hexdigest()


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionCompilerError(ActionCompilerIssue(code, path, message))
