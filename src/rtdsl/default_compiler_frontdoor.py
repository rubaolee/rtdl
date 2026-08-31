"""Compiler-owned DEFAULT planning and behavioral OptiX admission.

The caller supplies an authenticated Action, target, and the identity of the
complete current registry.  It cannot name a backend, template, candidate, or
program bundle.  The selected physical declaration comes only from
``default_physical_selection``.

An OptiX name is deliberately insufficient.  A traversal-capable selection is
only a *plan* until a nonce-bound execution receipt proves a completely bound
``optixLaunch`` through the source-pinned program bundle selected here.  This
module does not execute a candidate and does not claim silicon utilization.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
from typing import Mapping

from .default_physical_selection import (
    ANNOTATION_NONE,
    DEFAULT_RECEIPT_SCHEMA,
    OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
    ActionSelectionDescriptor,
    TargetSelectionDescriptor,
    candidate_descriptor_sha256,
    candidate_legality_reasons,
    current_registry_snapshot,
    materialize_candidates,
    select_default,
)
from .physical_execution_provenance import physical_program_bundle_id


DEFAULT_FRONTDOOR_POLICY_VERSION = "rtdl.default_compiler_frontdoor.goal5696.v1"
DEFAULT_PLAN_SCHEMA = "rtdl.default_compiler_frontdoor.plan.v1"
CANONICAL_PROVIDER_MATERIALIZATION_RECEIPT_SCHEMA = (
    "rtdl.default_compiler_frontdoor.canonical_provider_materialization.v1"
)
DEFAULT_EXECUTION_ADMISSION_SCHEMA = (
    "rtdl.default_compiler_frontdoor.execution_admission.v1"
)
TRAVERSAL_RECEIPT_SCHEMA = "rtdl.physical_execution.traversal_receipt.v1"
PREPARED_DEFAULT_PROOF_AUTHORITY_SCHEMA = (
    "rtdl.default_compiler_frontdoor.prepared_proof_authority.v1"
)
DEFAULT_PROGRAM_PROOF_CAPSULE_SCHEMA = (
    "rtdl.default_compiler_frontdoor.program_proof_capsule.v2"
)
COMPOSED_STATIC_PROOF_SCHEMA = (
    "rtdl.default_compiler_frontdoor.composed_static_proof.v1"
)
_PREPARED_AUTHORITY_TOKEN = object()
_PREPARED_AUTHORITY_SECRET = secrets.token_bytes(32)


class DefaultCompilerFrontdoorError(RuntimeError):
    """A typed fail-closed front-door error."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = str(code)
        self.detail = str(detail)


class PreparedDefaultProofAuthority:
    """Process-local proof that static DEFAULT program sources were verified.

    Dynamic Action/target/resource legality and winner selection are not stored
    here.  The object only owns immutable candidate program contracts and the
    exact source bytes/anchors verified while the compiler context was prepared.
    """

    __slots__ = (
        "_registry",
        "_registry_digest",
        "_repository_root",
        "_contract_json_by_candidate",
        "_source_proof_binding_json",
        "_candidate_ids",
        "_process_id",
        "_nonce",
        "_identity_digest",
        "_signature",
        "_closed",
    )

    def __init__(
        self,
        *,
        registry,
        repository_root: Path,
        contract_json_by_candidate: Mapping[str, str],
        source_proof_binding: Mapping[str, object],
        _constructor_token: object,
    ) -> None:
        if _constructor_token is not _PREPARED_AUTHORITY_TOKEN:
            raise TypeError("prepared DEFAULT proof authorities are compiler-owned")
        self._registry = registry
        self._registry_digest = str(registry.digest)
        self._repository_root = repository_root.resolve()
        self._contract_json_by_candidate = dict(contract_json_by_candidate)
        self._source_proof_binding_json = json.dumps(
            dict(source_proof_binding),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        self._candidate_ids = tuple(sorted(self._contract_json_by_candidate))
        self._process_id = os.getpid()
        self._nonce = secrets.token_hex(32)
        public = {
            "schema": PREPARED_DEFAULT_PROOF_AUTHORITY_SCHEMA,
            "registry_sha256": self._registry_digest,
            "repository_root": str(self._repository_root),
            "candidate_ids": list(self._candidate_ids),
            "program_contract_sha256_by_candidate": {
                candidate_id: json.loads(contract_json)["program_contract_sha256"]
                for candidate_id, contract_json in self._contract_json_by_candidate.items()
            },
            "source_proof_binding": json.loads(self._source_proof_binding_json),
            "process_id": self._process_id,
            "nonce": self._nonce,
        }
        self._identity_digest = _digest(public)
        self._signature = hmac.new(
            _PREPARED_AUTHORITY_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()
        self._closed = False

    def _seal_payload(self) -> bytes:
        return _canonical_bytes(
            {
                "schema": PREPARED_DEFAULT_PROOF_AUTHORITY_SCHEMA,
                "identity_digest": self._identity_digest,
                "registry_object_id": id(self._registry),
                "registry_sha256": self._registry_digest,
                "repository_root": str(self._repository_root),
                "candidate_ids": list(self._candidate_ids),
                "source_proof_binding_sha256": hashlib.sha256(
                    self._source_proof_binding_json.encode("ascii")
                ).hexdigest(),
                "process_id": self._process_id,
                "nonce": self._nonce,
            }
        )

    @property
    def identity_digest(self) -> str:
        return self._identity_digest

    @property
    def closed(self) -> bool:
        return self._closed

    def require_live(
        self,
        *,
        registry,
        repository_root: Path,
    ) -> None:
        if self._closed:
            raise DefaultCompilerFrontdoorError("PREPARED_AUTHORITY_CLOSED")
        if os.getpid() != self._process_id:
            raise DefaultCompilerFrontdoorError(
                "PREPARED_AUTHORITY_CROSSED_PROCESS_BOUNDARY"
            )
        if registry is not self._registry or registry.digest != self._registry_digest:
            raise DefaultCompilerFrontdoorError("PREPARED_AUTHORITY_REGISTRY_DRIFT")
        if repository_root.resolve() != self._repository_root:
            raise DefaultCompilerFrontdoorError(
                "PREPARED_AUTHORITY_REPOSITORY_ROOT_DRIFT"
            )
        expected = hmac.new(
            _PREPARED_AUTHORITY_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(self._signature, expected):
            raise DefaultCompilerFrontdoorError("PREPARED_AUTHORITY_SEAL_INVALID")

    def verified_program_contract(
        self,
        candidate_stable_id: str,
        *,
        registry,
        repository_root: Path,
    ) -> dict[str, object]:
        self.require_live(registry=registry, repository_root=repository_root)
        raw = self._contract_json_by_candidate.get(candidate_stable_id)
        if raw is None:
            raise DefaultCompilerFrontdoorError(
                "PREPARED_AUTHORITY_CANDIDATE_NOT_COVERED",
                candidate_stable_id,
            )
        value = json.loads(raw)
        if value.get("candidate_stable_id") != candidate_stable_id:
            raise DefaultCompilerFrontdoorError(
                "PREPARED_AUTHORITY_CONTRACT_IDENTITY_DRIFT",
                candidate_stable_id,
            )
        return value

    def to_metadata(self) -> dict[str, object]:
        return {
            "schema": PREPARED_DEFAULT_PROOF_AUTHORITY_SCHEMA,
            "identity_digest": self._identity_digest,
            "registry_sha256": self._registry_digest,
            "repository_root": str(self._repository_root),
            "candidate_ids": list(self._candidate_ids),
            "source_proof_binding": json.loads(self._source_proof_binding_json),
            "process_local": True,
            "serialization_allowed": False,
            "dynamic_action_or_target_cached": False,
            "dynamic_legality_or_winner_cached": False,
            "closed": self._closed,
        }

    def require_live_source_seal(
        self,
        *,
        registry,
        repository_root: Path,
    ) -> dict[str, object]:
        """Return a live whole-tree seal, never untrusted authority metadata."""

        self.require_live(registry=registry, repository_root=repository_root)
        binding = json.loads(self._source_proof_binding_json)
        required = {
            "mode",
            "capsule_sha256",
            "source_archive_sha256",
            "source_tree_digest",
            "native_library_sha256",
            "native_source_tree_digest",
            "composed_static_proofs",
            "static_source_bytes_verified_in_this_process",
        }
        if (
            set(binding) != required
            or binding.get("mode") != "source_sealed_program_proof_capsule"
            or binding.get("static_source_bytes_verified_in_this_process") is not False
        ):
            raise DefaultCompilerFrontdoorError(
                "PREPARED_AUTHORITY_WHOLE_SOURCE_SEAL_UNAVAILABLE"
            )
        for field in required - {
            "mode",
            "composed_static_proofs",
            "static_source_bytes_verified_in_this_process",
        }:
            _validate_sha256(binding.get(field), field=f"source_seal_{field}")
        return binding

    def require_composed_static_proof(
        self,
        *,
        registry,
        repository_root: Path,
        proof_id: str,
        consumer_capsule_sha256: str,
    ) -> dict[str, object]:
        binding = self.require_live_source_seal(
            registry=registry,
            repository_root=repository_root,
        )
        if not isinstance(proof_id, str) or not proof_id:
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_ID_INVALID")
        consumer_digest = _validate_sha256(
            consumer_capsule_sha256,
            field="composed_static_proof_consumer_capsule_sha256",
        )
        rows = binding.get("composed_static_proofs")
        if not isinstance(rows, list):
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_SET_INVALID")
        matches = [row for row in rows if isinstance(row, Mapping) and row.get("proof_id") == proof_id]
        if len(matches) != 1:
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_NOT_UNIQUE")
        row = dict(matches[0])
        if row.get("consumer_capsule_sha256") != consumer_digest:
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_CONSUMER_MISMATCH")
        return row

    def close(self) -> None:
        self._closed = True

    def __reduce__(self):
        raise TypeError("prepared DEFAULT proof authorities cannot be serialized")

    def __copy__(self):
        raise TypeError("prepared DEFAULT proof authorities cannot be copied")

    def __deepcopy__(self, memo):
        del memo
        raise TypeError("prepared DEFAULT proof authorities cannot be copied")


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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise DefaultCompilerFrontdoorError("INVALID_SHA256", field)
    try:
        int(value, 16)
    except ValueError as exc:
        raise DefaultCompilerFrontdoorError("INVALID_SHA256", field) from exc
    if value != value.lower():
        raise DefaultCompilerFrontdoorError("NONCANONICAL_SHA256", field)
    return value


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise DefaultCompilerFrontdoorError("EXPECTED_MAPPING", field)
    return value


def _source_evidence(
    path: str,
    sha256: str,
    *,
    source_role: str,
    required_anchors: tuple[str, ...],
) -> dict[str, object]:
    return {
        "path": path,
        "sha256": sha256,
        "source_role": source_role,
        "required_anchors": list(required_anchors),
    }


# These are generic physical-candidate contracts, never application identities.
# Each contract binds the Python-side selected candidate to exact native source
# bytes, a concrete NVRTC program source, the corresponding optixLaunch call,
# and the physical program-bundle identifier recorded by the native audit ABI.
# Exact current native source identity.  Goal5727 added the reviewed generic
# These are source-authority pins, not historical identities.  Goal5745 added
# the generic metric-kNN OptiX family to the same native translation units.
# Every canonical DEFAULT contract that cites either unit must therefore bind
# the current unified bytes; retaining the older Goal5740 pins makes all
# pre-existing applications fail closed even though the target native was
# built from the successor source.
_WORKLOADS_SHA = "9315dc3a1782c4e5289b75407662f2943909c0a3616cd3022f3a4898694a22b9"
_CORE_SHA = "3a2838cd124ce2cc6c03972b3cde1497c8f59437cb7dea12d296f9b069afc15b"
_WORKLOADS = "src/native/optix/rtdl_optix_workloads.cpp"
_CORE = "src/native/optix/rtdl_optix_core.cpp"


_OPTIX_PROGRAM_CONTRACT_INPUTS: dict[str, dict[str, object]] = {
    "aggregate_hierarchy_registry/aggregate_hierarchy_continuation_reduce_3d/optix_traversal/true_optix_aggregate_hierarchy_continuation_reduce_3d": {
        "program_bundles": ("aggregate_hierarchy_continuation_reduce_3d",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "kAggregateHierarchyContinuation3DRtKernelSrc",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "aggregate_hierarchy_continuation_reduce_3d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/certified_nearest_state_3d.v1/optix_cell_mbr_exact_witness/cell_mbr_exact_witness_3d_optix_traversal": {
        "program_bundles": ("cell_mbr_nearest_frontier_f64_3d.v1",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "kCellMbrFrontier3DKernelSrc",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "cell_mbr_nearest_frontier_f64_3d.v1"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/certified_nearest_state_3d.v1/optix_traversal/certified_nearest_state_3d_optix_traversal": {
        "program_bundles": ("certified_nearest_state_f64_cell_mbr_3d.v1",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "kCellMbrFrontier3DKernelSrc",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "certified_nearest_state_f64_cell_mbr_3d.v1"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/prepared_aabb_overlap_candidates_2d.v1/optix/aabb_filter_bounded_emit_2d": {
        "program_bundles": ("aabb_index_count_2d",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "kAabbIndexCountKernelSrc",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "aabb_index_count_2d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/prepared_aabb_index_queries_2d.v1/optix/prepared_optix_aabb_index_query_2d": {
        "program_bundles": ("aabb_index_count_2d",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "kAabbIndexCountKernelSrc",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "aabb_index_count_2d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/prepared_point_candidates_3d.v1/optix/point_candidate_bounded_selection_3d": {
        "program_bundles": ("action_bounded_selection_3d",),
        "source_evidence": (
            _source_evidence(
                _CORE,
                _CORE_SHA,
                source_role="device_program_with_optix_trace",
                required_anchors=(
                    "kFixedRadiusNeighbors3DRtKernelSrc",
                    "__raygen__frn3d_probe",
                    "optixTrace(",
                ),
            ),
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="bound_launch",
                required_anchors=(
                    'rtdl_optix_bind_traversal_audit_context(\n        "action_bounded_selection_3d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "common_action_api/stable_ray_triangle_candidates_3d.v1/optix/keyed_i64_sum_3d": {
        "program_bundles": ("ray_triangle_primitive_grouped_i64_reduction_3d",),
        "source_evidence": (
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="device_program_and_bound_launch",
                required_anchors=(
                    "ray_primitive_grouped_i64_reduction_kernel_source_3d",
                    "optixTrace(",
                    'rtdl_optix_bind_traversal_audit_context(\n        "ray_triangle_primitive_grouped_i64_reduction_3d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
    "fixed_radius_graph_registry/prepared_spatial_radius_producer.v1/optix_prepared_radius_components/prepared_optix_radius_graph_plus_numba_components": {
        "program_bundles": (
            "fixed_radius_count_threshold_3d",
            "fixed_radius_grouped_union_3d",
        ),
        "source_evidence": (
            _source_evidence(
                _CORE,
                _CORE_SHA,
                source_role="device_program_with_optix_trace",
                required_anchors=(
                    "kFixedRadiusCountThreshold3DRtKernelSrc",
                    "__raygen__frn3d_count_threshold_probe",
                    "optixTrace(",
                ),
            ),
            _source_evidence(
                _CORE,
                _CORE_SHA,
                source_role="device_program_with_optix_trace",
                required_anchors=(
                    "kFixedRadiusGroupedUnion3DRtKernelSrc",
                    "__raygen__frn3d_grouped_union_probe",
                    "optixTrace(",
                ),
            ),
            _source_evidence(
                _WORKLOADS,
                _WORKLOADS_SHA,
                source_role="bound_launch",
                required_anchors=(
                    'rtdl_optix_bind_traversal_audit_context(\n        "fixed_radius_count_threshold_3d"',
                    'rtdl_optix_bind_traversal_audit_context(\n        "fixed_radius_grouped_union_3d"',
                    "OPTIX_CHECK(optixLaunch(",
                ),
            ),
        ),
    },
}


def _program_contract(candidate_stable_id: str) -> dict[str, object]:
    raw = _OPTIX_PROGRAM_CONTRACT_INPUTS.get(candidate_stable_id)
    if raw is None:
        raise DefaultCompilerFrontdoorError(
            "OPTIX_PROGRAM_CONTRACT_MISSING", candidate_stable_id
        )
    bundles = tuple(raw["program_bundles"])
    evidence = tuple(dict(item) for item in raw["source_evidence"])
    body: dict[str, object] = {
        "schema": "rtdl.default_compiler_frontdoor.optix_program_contract.v1",
        "candidate_stable_id": candidate_stable_id,
        "program_bundles": list(bundles),
        "program_bundle_ids": [physical_program_bundle_id(name) for name in bundles],
        "source_evidence": list(evidence),
        "static_capability_is_behavioral_proof": False,
        "behavioral_receipt_required": True,
    }
    body["program_contract_sha256"] = _digest(body)
    return body


def _verify_program_sources(
    contract: Mapping[str, object], *, repository_root: Path
) -> None:
    evidence_rows = contract.get("source_evidence")
    if not isinstance(evidence_rows, list) or not evidence_rows:
        raise DefaultCompilerFrontdoorError("EMPTY_OPTIX_SOURCE_EVIDENCE")
    for index, raw in enumerate(evidence_rows):
        row = _require_mapping(raw, field=f"source_evidence[{index}]")
        relative = row.get("path")
        if not isinstance(relative, str) or not relative:
            raise DefaultCompilerFrontdoorError(
                "INVALID_OPTIX_SOURCE_PATH", str(index)
            )
        path = (repository_root / relative).resolve()
        try:
            path.relative_to(repository_root.resolve())
        except ValueError as exc:
            raise DefaultCompilerFrontdoorError(
                "OPTIX_SOURCE_OUTSIDE_REPOSITORY", relative
            ) from exc
        if not path.is_file():
            raise DefaultCompilerFrontdoorError("OPTIX_SOURCE_MISSING", relative)
        expected_sha = _validate_sha256(
            row.get("sha256"), field=f"source_evidence[{index}].sha256"
        )
        if _sha256_file(path) != expected_sha:
            raise DefaultCompilerFrontdoorError("OPTIX_SOURCE_SHA_MISMATCH", relative)
        source = path.read_text(encoding="utf-8")
        role = row.get("source_role")
        if role not in {
            "device_program_and_bound_launch",
            "device_program_with_optix_trace",
            "bound_launch",
        }:
            raise DefaultCompilerFrontdoorError(
                "INVALID_OPTIX_SOURCE_ROLE", f"{relative}:{role}"
            )
        anchors = row.get("required_anchors")
        if not isinstance(anchors, list) or not anchors:
            raise DefaultCompilerFrontdoorError(
                "EMPTY_OPTIX_SOURCE_ANCHORS", relative
            )
        for anchor_index, anchor in enumerate(anchors):
            if not isinstance(anchor, str) or not anchor or anchor not in source:
                raise DefaultCompilerFrontdoorError(
                    "OPTIX_SOURCE_ANCHOR_MISSING",
                    f"{relative}:required_anchors[{anchor_index}]",
                )
    roles = {str(row.get("source_role")) for row in evidence_rows}
    if not roles.intersection(
        {"device_program_and_bound_launch", "device_program_with_optix_trace"}
    ):
        raise DefaultCompilerFrontdoorError("OPTIX_DEVICE_PROGRAM_SOURCE_MISSING")
    if not roles.intersection({"device_program_and_bound_launch", "bound_launch"}):
        raise DefaultCompilerFrontdoorError("OPTIX_BOUND_LAUNCH_SOURCE_MISSING")


def prepare_default_proof_authority(
    *,
    repository_root: Path,
    candidate_stable_ids: tuple[str, ...] | None = None,
) -> PreparedDefaultProofAuthority:
    """Verify immutable program/source proof once for a compiler lifetime.

    The candidate subset must be compiler-derived.  This function never sees
    an Action instance, target resources, legality result, or winner.
    """

    registry = current_registry_snapshot()
    root = Path(repository_root).resolve(strict=True)
    traversal_ids = tuple(
        row.stable_id
        for row in registry.declarations
        if OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in row.physical_capabilities
    )
    requested = traversal_ids if candidate_stable_ids is None else candidate_stable_ids
    if requested != tuple(sorted(set(requested))):
        raise DefaultCompilerFrontdoorError(
            "PREPARED_AUTHORITY_NONCANONICAL_CANDIDATE_SET"
        )
    if not requested:
        raise DefaultCompilerFrontdoorError("PREPARED_AUTHORITY_EMPTY_CANDIDATE_SET")
    unknown = set(requested) - set(traversal_ids)
    if unknown:
        raise DefaultCompilerFrontdoorError(
            "PREPARED_AUTHORITY_UNKNOWN_OR_NONTRAVERSAL_CANDIDATE",
            ",".join(sorted(unknown)),
        )
    contracts: dict[str, str] = {}
    for candidate_id in requested:
        contract = _program_contract(candidate_id)
        _verify_program_sources(contract, repository_root=root)
        contracts[candidate_id] = json.dumps(
            contract,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    authority = PreparedDefaultProofAuthority(
        registry=registry,
        repository_root=root,
        contract_json_by_candidate=contracts,
        source_proof_binding={
            "mode": "runtime_source_byte_verification",
            "static_source_bytes_verified_in_this_process": True,
            "capsule_used": False,
        },
        _constructor_token=_PREPARED_AUTHORITY_TOKEN,
    )
    authority.require_live(registry=registry, repository_root=root)
    return authority


def build_default_program_proof_capsule(
    *,
    repository_root: Path,
    source_archive_sha256: str,
    source_tree_digest: str,
    native_library_sha256: str,
    native_source_tree_digest: str,
    candidate_stable_ids: tuple[str, ...] | None = None,
    composed_static_proofs: tuple[Mapping[str, object], ...] = (),
) -> dict[str, object]:
    """Build a content-addressed install-time static program proof capsule."""

    registry = current_registry_snapshot()
    root = Path(repository_root).resolve(strict=True)
    traversal_ids = tuple(
        row.stable_id
        for row in registry.declarations
        if OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in row.physical_capabilities
    )
    requested = traversal_ids if candidate_stable_ids is None else candidate_stable_ids
    if requested != tuple(sorted(set(requested))):
        raise DefaultCompilerFrontdoorError(
            "PROGRAM_PROOF_CAPSULE_NONCANONICAL_CANDIDATE_SET"
        )
    if not requested or set(requested) - set(traversal_ids):
        raise DefaultCompilerFrontdoorError(
            "PROGRAM_PROOF_CAPSULE_UNKNOWN_OR_NONTRAVERSAL_CANDIDATE"
        )
    contracts = []
    for candidate_id in requested:
        contract = _program_contract(candidate_id)
        _verify_program_sources(contract, repository_root=root)
        contracts.append(contract)
    normalized_composed: list[dict[str, object]] = []
    seen_proof_ids: set[str] = set()
    for raw in composed_static_proofs:
        if not isinstance(raw, Mapping):
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_INVALID")
        proof_id = raw.get("proof_id")
        source_digests = raw.get("dependency_source_sha256")
        if (
            raw.get("schema") != COMPOSED_STATIC_PROOF_SCHEMA
            or not isinstance(proof_id, str)
            or not proof_id
            or proof_id in seen_proof_ids
            or not isinstance(source_digests, Mapping)
            or not source_digests
        ):
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_INVALID")
        consumer_digest = _validate_sha256(
            raw.get("consumer_capsule_sha256"),
            field="composed_static_proof_consumer_capsule_sha256",
        )
        normalized_sources: dict[str, str] = {}
        for relative, digest in sorted(source_digests.items()):
            if not isinstance(relative, str) or not relative:
                raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_SOURCE_INVALID")
            path = (root / relative).resolve(strict=True)
            try:
                path.relative_to(root)
            except ValueError as exc:
                raise DefaultCompilerFrontdoorError(
                    "COMPOSED_STATIC_PROOF_SOURCE_OUTSIDE_ROOT"
                ) from exc
            expected = _validate_sha256(
                digest,
                field=f"composed_static_proof_source_{relative}",
            )
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise DefaultCompilerFrontdoorError(
                    "COMPOSED_STATIC_PROOF_SOURCE_MISMATCH", relative
                )
            normalized_sources[relative] = expected
        seen_proof_ids.add(proof_id)
        proof_body: dict[str, object] = {
            "schema": COMPOSED_STATIC_PROOF_SCHEMA,
            "proof_id": proof_id,
            "consumer_capsule_sha256": consumer_digest,
            "dependency_source_sha256": normalized_sources,
            "dependency_source_set_sha256": _digest(normalized_sources),
        }
        proof_body["proof_sha256"] = _digest(proof_body)
        normalized_composed.append(proof_body)
    normalized_composed.sort(key=lambda row: str(row["proof_id"]))
    body: dict[str, object] = {
        "schema": DEFAULT_PROGRAM_PROOF_CAPSULE_SCHEMA,
        "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
        "source_archive_sha256": _validate_sha256(
            source_archive_sha256, field="source_archive_sha256"
        ),
        "source_tree_digest": _validate_sha256(
            source_tree_digest, field="source_tree_digest"
        ),
        "registry_sha256": registry.digest,
        "native_library_sha256": _validate_sha256(
            native_library_sha256, field="native_library_sha256"
        ),
        "native_source_tree_digest": _validate_sha256(
            native_source_tree_digest, field="native_source_tree_digest"
        ),
        "candidate_ids": list(requested),
        "program_contracts": contracts,
        "composed_static_proofs": normalized_composed,
        "static_source_bytes_verified_at_capsule_build": True,
        "dynamic_action_or_target_cached": False,
        "dynamic_legality_or_winner_cached": False,
        "behavioral_optix_proven": False,
        "silicon_rt_core_utilization_proven": False,
        "capsule_is_external_to_named_source_archive": True,
    }
    body["capsule_sha256"] = _digest(body)
    return body


def install_default_program_proof_capsule(
    capsule: Mapping[str, object],
    *,
    repository_root: Path,
    expected_source_archive_sha256: str,
    expected_source_tree_digest: str,
    expected_native_library_sha256: str,
    expected_native_source_tree_digest: str,
    candidate_stable_ids: tuple[str, ...] | None = None,
) -> PreparedDefaultProofAuthority:
    """Validate a plan-pinned capsule without rereading large source files."""

    if capsule.get("schema") != DEFAULT_PROGRAM_PROOF_CAPSULE_SCHEMA:
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_SCHEMA_MISMATCH")
    claimed = _validate_sha256(capsule.get("capsule_sha256"), field="capsule_sha256")
    capsule_body = dict(capsule)
    capsule_body.pop("capsule_sha256", None)
    if _digest(capsule_body) != claimed:
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_DIGEST_MISMATCH")
    expected_bindings = {
        "source_archive_sha256": expected_source_archive_sha256,
        "source_tree_digest": expected_source_tree_digest,
        "native_library_sha256": expected_native_library_sha256,
        "native_source_tree_digest": expected_native_source_tree_digest,
    }
    for field, expected in expected_bindings.items():
        canonical = _validate_sha256(expected, field=f"expected_{field}")
        if capsule.get(field) != canonical:
            raise DefaultCompilerFrontdoorError(
                "PROGRAM_PROOF_CAPSULE_IDENTITY_MISMATCH", field
            )
    if capsule.get("policy_version") != DEFAULT_FRONTDOOR_POLICY_VERSION:
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_POLICY_MISMATCH")
    if (
        capsule.get("static_source_bytes_verified_at_capsule_build") is not True
        or capsule.get("dynamic_action_or_target_cached") is not False
        or capsule.get("dynamic_legality_or_winner_cached") is not False
        or capsule.get("behavioral_optix_proven") is not False
        or capsule.get("silicon_rt_core_utilization_proven") is not False
        or capsule.get("capsule_is_external_to_named_source_archive") is not True
    ):
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_CLAIM_BOUNDARY_INVALID")
    registry = current_registry_snapshot()
    if capsule.get("registry_sha256") != registry.digest:
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_REGISTRY_MISMATCH")
    candidate_ids = capsule.get("candidate_ids")
    if not isinstance(candidate_ids, list) or candidate_ids != sorted(set(candidate_ids)):
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_CANDIDATE_SET_INVALID")
    requested = tuple(candidate_ids) if candidate_stable_ids is None else candidate_stable_ids
    if (
        requested != tuple(sorted(set(requested)))
        or not requested
        or not set(requested).issubset(set(candidate_ids))
    ):
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_CANDIDATE_SET_MISMATCH")
    raw_contracts = capsule.get("program_contracts")
    if not isinstance(raw_contracts, list) or len(raw_contracts) != len(candidate_ids):
        raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_CONTRACT_SET_INVALID")
    all_contract_json: dict[str, str] = {}
    for candidate_id, raw_contract in zip(candidate_ids, raw_contracts):
        if not isinstance(raw_contract, Mapping):
            raise DefaultCompilerFrontdoorError("PROGRAM_PROOF_CAPSULE_CONTRACT_INVALID")
        expected_contract = _program_contract(candidate_id)
        if _canonical_bytes(raw_contract) != _canonical_bytes(expected_contract):
            raise DefaultCompilerFrontdoorError(
                "PROGRAM_PROOF_CAPSULE_CONTRACT_MISMATCH", candidate_id
            )
        all_contract_json[candidate_id] = json.dumps(
            expected_contract,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    contract_json = {
        candidate_id: all_contract_json[candidate_id] for candidate_id in requested
    }
    raw_composed = capsule.get("composed_static_proofs")
    if not isinstance(raw_composed, list):
        raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_SET_INVALID")
    composed: list[dict[str, object]] = []
    proof_ids: list[str] = []
    for raw in raw_composed:
        if not isinstance(raw, Mapping):
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_INVALID")
        row = dict(raw)
        claimed_proof = _validate_sha256(
            row.pop("proof_sha256", None), field="composed_static_proof_sha256"
        )
        if _digest(row) != claimed_proof:
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_DIGEST_MISMATCH")
        if row.get("schema") != COMPOSED_STATIC_PROOF_SCHEMA:
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_SCHEMA_MISMATCH")
        proof_id = row.get("proof_id")
        source_digests = row.get("dependency_source_sha256")
        if (
            not isinstance(proof_id, str)
            or not proof_id
            or not isinstance(source_digests, Mapping)
            or not source_digests
            or row.get("dependency_source_set_sha256")
            != _digest(dict(source_digests))
        ):
            raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_INVALID")
        _validate_sha256(
            row.get("consumer_capsule_sha256"),
            field="composed_static_proof_consumer_capsule_sha256",
        )
        normalized_sources = {
            str(path): _validate_sha256(
                digest, field=f"composed_static_proof_source_{path}"
            )
            for path, digest in source_digests.items()
        }
        if normalized_sources != dict(source_digests):
            raise DefaultCompilerFrontdoorError(
                "COMPOSED_STATIC_PROOF_SOURCE_SET_INVALID"
            )
        proof_ids.append(proof_id)
        composed.append({**row, "proof_sha256": claimed_proof})
    if proof_ids != sorted(set(proof_ids)):
        raise DefaultCompilerFrontdoorError("COMPOSED_STATIC_PROOF_SET_NONCANONICAL")
    authority = PreparedDefaultProofAuthority(
        registry=registry,
        repository_root=Path(repository_root).resolve(strict=True),
        contract_json_by_candidate=contract_json,
        source_proof_binding={
            "mode": "source_sealed_program_proof_capsule",
            "capsule_sha256": claimed,
            **expected_bindings,
            "composed_static_proofs": composed,
            "static_source_bytes_verified_in_this_process": False,
        },
        _constructor_token=_PREPARED_AUTHORITY_TOKEN,
    )
    authority.require_live(
        registry=registry,
        repository_root=Path(repository_root).resolve(strict=True),
    )
    return authority


def _frontdoor_failure(
    *,
    error: DefaultCompilerFrontdoorError,
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    registry_sha256: object,
) -> dict[str, object]:
    body: dict[str, object] = {
        "schema": DEFAULT_PLAN_SCHEMA,
        "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
        "status": "FAIL_CLOSED",
        "error_code": error.code,
        "error_detail": error.detail,
        "action": action.as_dict(),
        "target": target.as_dict(),
        "supplied_registry_sha256": registry_sha256,
        "candidate_override_accepted": False,
        "candidate_executed": False,
        "behavioral_optix_claimed": False,
        "silicon_rt_core_utilization_claimed": False,
        "production_default_changed": False,
    }
    body["plan_sha256"] = _digest(body)
    return body


def _compile_default_plan_impl(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry_sha256: str,
    annotation_mode: str = ANNOTATION_NONE,
    repository_root: Path | None = None,
    prepared_proof_authority: PreparedDefaultProofAuthority | None = None,
    canonical_provider_stable_id: str | None = None,
) -> dict[str, object]:
    """Return one compiler-owned plan; no candidate override exists.

    ``registry_sha256`` is an identity assertion, not a caller-provided
    registry.  The complete registry is always materialized internally.
    """

    try:
        supplied_registry_sha256 = _validate_sha256(
            registry_sha256, field="registry_sha256"
        )
        if (
            canonical_provider_stable_id is None
            and OPTIX_TRAVERSAL_PROGRAM_CAPABILITY
            not in target.required_physical_capabilities
        ):
            raise DefaultCompilerFrontdoorError(
                "MANDATORY_NVIDIA_RT_PROFILE_REQUIRED"
            )
        registry = current_registry_snapshot()
        if supplied_registry_sha256 != registry.digest:
            raise DefaultCompilerFrontdoorError(
                "CURRENT_REGISTRY_IDENTITY_MISMATCH"
            )
        if canonical_provider_stable_id is None:
            selection = select_default(
                action,
                target,
                registry=registry,
                annotation_mode=annotation_mode,
            )
            if selection.get("schema") != DEFAULT_RECEIPT_SCHEMA:
                raise DefaultCompilerFrontdoorError("UNSUPPORTED_SELECTION_RECEIPT")
            if selection.get("status") != "SELECTED":
                selection_code = str(selection.get("error_code", "UNKNOWN"))
                selection_detail = str(selection.get("error_detail", ""))
                raise DefaultCompilerFrontdoorError(
                    "DEFAULT_SELECTION_FAILED",
                    (
                        f"{selection_code}:{selection_detail}"
                        if selection_detail
                        else selection_code
                    ),
                )
            winner_id = selection.get("winner_stable_id")
            selected_candidate_sha256 = selection["winner_candidate_sha256"]
        else:
            if (
                not isinstance(canonical_provider_stable_id, str)
                or not canonical_provider_stable_id
            ):
                raise DefaultCompilerFrontdoorError(
                    "INVALID_CANONICAL_PROVIDER_IDENTITY"
                )
            materialized = materialize_candidates(action, registry)
            exact = tuple(
                row
                for row in materialized
                if row.declaration.stable_id == canonical_provider_stable_id
            )
            if len(exact) != 1:
                raise DefaultCompilerFrontdoorError(
                    "CANONICAL_PROVIDER_NOT_EXACTLY_ONCE_IN_ACTION_DOMAIN",
                    canonical_provider_stable_id,
                )
            canonical_candidate = exact[0]
            rejection_reasons = candidate_legality_reasons(
                canonical_candidate,
                action,
                target,
            )
            if rejection_reasons:
                raise DefaultCompilerFrontdoorError(
                    "CANONICAL_PROVIDER_ILLEGAL_FOR_ACTION_OR_TARGET",
                    ",".join(rejection_reasons),
                )
            selected_candidate_sha256 = candidate_descriptor_sha256(
                canonical_candidate
            )
            materialization_body: dict[str, object] = {
                "schema": CANONICAL_PROVIDER_MATERIALIZATION_RECEIPT_SCHEMA,
                "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
                "status": "MATERIALIZED",
                "action": action.as_dict(),
                "action_descriptor_sha256": _digest(action.as_dict()),
                "target": target.as_dict(),
                "target_descriptor_sha256": _digest(target.as_dict()),
                "registry_sha256": registry.digest,
                "complete_action_candidate_domain_sha256": _digest(
                    [row.as_dict() for row in materialized]
                ),
                "canonical_provider_stable_id": canonical_provider_stable_id,
                "canonical_candidate": canonical_candidate.as_dict(),
                "canonical_candidate_sha256": selected_candidate_sha256,
                "legality_rejection_reasons": [],
                "candidate_comparison_started": False,
                "default_optimizer_selected_provider": False,
                "caller_candidate_override_used": False,
                "application_identity_used": False,
                "candidate_executed": False,
                "timing_or_learned_input_used": False,
            }
            materialization_body["receipt_sha256"] = _digest(
                materialization_body
            )
            selection = materialization_body
            winner_id = canonical_provider_stable_id
        if (
            canonical_provider_stable_id is not None
            and winner_id != canonical_provider_stable_id
        ):
            raise DefaultCompilerFrontdoorError(
                "CANONICAL_PROVIDER_MATERIALIZATION_MISMATCH",
                f"{winner_id}!={canonical_provider_stable_id}",
            )
        declaration = next(
            (row for row in registry.declarations if row.stable_id == winner_id),
            None,
        )
        if declaration is None:
            raise DefaultCompilerFrontdoorError("SELECTED_CANDIDATE_NOT_IN_REGISTRY")
        has_traversal_capability = (
            OPTIX_TRAVERSAL_PROGRAM_CAPABILITY
            in declaration.physical_capabilities
        )
        mandatory_traversal = (
            OPTIX_TRAVERSAL_PROGRAM_CAPABILITY
            in target.required_physical_capabilities
        )
        if mandatory_traversal and not has_traversal_capability:
            raise DefaultCompilerFrontdoorError(
                "MANDATORY_OPTIX_SELECTED_NONTRAVERSAL_CANDIDATE",
                declaration.stable_id,
            )
        program_contract: dict[str, object] | None = None
        if has_traversal_capability:
            root = (
                Path(__file__).resolve().parents[2]
                if repository_root is None
                else Path(repository_root).resolve()
            )
            if prepared_proof_authority is None:
                program_contract = _program_contract(declaration.stable_id)
                _verify_program_sources(program_contract, repository_root=root)
            else:
                if not isinstance(
                    prepared_proof_authority, PreparedDefaultProofAuthority
                ):
                    raise DefaultCompilerFrontdoorError(
                        "INVALID_PREPARED_PROOF_AUTHORITY"
                    )
                program_contract = (
                    prepared_proof_authority.verified_program_contract(
                        declaration.stable_id,
                        registry=registry,
                        repository_root=root,
                    )
                )

        physical_configuration_policy = declaration.as_dict().get(
            "physical_configuration_policy"
        )
        physical_configuration_policy_sha256 = (
            None
            if physical_configuration_policy is None
            else _digest(physical_configuration_policy)
        )

        selection_sha = selection["receipt_sha256"]
        route_identity = "rtdl.default/" + _digest(
            {
                "selection_receipt_sha256": selection_sha,
                "winner_stable_id": declaration.stable_id,
                "program_contract_sha256": (
                    None
                    if program_contract is None
                    else program_contract["program_contract_sha256"]
                ),
                "physical_configuration_policy_sha256": (
                    physical_configuration_policy_sha256
                ),
            }
        )
        body: dict[str, object] = {
            "schema": DEFAULT_PLAN_SCHEMA,
            "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
            "status": "PLANNED",
            "action": action.as_dict(),
            "action_descriptor_sha256": _digest(action.as_dict()),
            "target": target.as_dict(),
            "target_descriptor_sha256": _digest(target.as_dict()),
            "registry_sha256": registry.digest,
            "selection_receipt": selection,
            "selection_receipt_sha256": selection_sha,
            "selected_candidate_stable_id": declaration.stable_id,
            "selected_candidate_sha256": selected_candidate_sha256,
            "selected_execution_class": declaration.execution_class,
            "selected_physical_capabilities": list(
                declaration.physical_capabilities
            ),
            "selected_physical_configuration_policy": (
                physical_configuration_policy
            ),
            "selected_physical_configuration_policy_sha256": (
                physical_configuration_policy_sha256
            ),
            "optix_program_contract": program_contract,
            "prescribed_route_identity": route_identity,
            "behavioral_optix_receipt_required": has_traversal_capability,
            "mandatory_optix_target": mandatory_traversal,
            "partner_stages_permitted": declaration.execution_class
            == "mixed_optix_numba",
            "candidate_override_accepted": False,
            "application_identity_used": False,
            "candidate_executed": False,
            "static_capability_is_behavioral_proof": False,
            "behavioral_optix_claimed": False,
            "silicon_rt_core_utilization_claimed": False,
            "production_default_changed": False,
            "candidate_domain_restricted_by_canonical_resolution": (
                canonical_provider_stable_id is not None
            ),
            "canonical_provider_materialization_only": (
                canonical_provider_stable_id is not None
            ),
            "default_optimizer_selected_provider": (
                canonical_provider_stable_id is None
            ),
        }
        if prepared_proof_authority is not None:
            body["prepared_static_proof_authority_used"] = True
            body["prepared_static_proof_authority_identity"] = (
                prepared_proof_authority.identity_digest
            )
        body["plan_sha256"] = _digest(body)
        return body
    except DefaultCompilerFrontdoorError as error:
        return _frontdoor_failure(
            error=error,
            action=action,
            target=target,
            registry_sha256=registry_sha256,
        )


def compile_default_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry_sha256: str,
    annotation_mode: str = ANNOTATION_NONE,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Public DEFAULT front door; its override-free interface is immutable."""

    return _compile_default_plan_impl(
        action,
        target,
        registry_sha256=registry_sha256,
        annotation_mode=annotation_mode,
        repository_root=repository_root,
        prepared_proof_authority=None,
        canonical_provider_stable_id=None,
    )


def _compile_canonical_provider_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry_sha256: str,
    canonical_provider_stable_id: str,
    annotation_mode: str = ANNOTATION_NONE,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Compiler-internal materialization of an already resolved provider.

    This is not a candidate override or optimizer.  The canonical resolver has
    already selected exactly one provider for an application-owned semantic
    statement/backend contract.  This helper reruns all ordinary legality,
    resource and program-source checks on that singleton before constructing
    the existing plan schema.
    """

    return _compile_default_plan_impl(
        action,
        target,
        registry_sha256=registry_sha256,
        annotation_mode=annotation_mode,
        repository_root=repository_root,
        prepared_proof_authority=None,
        canonical_provider_stable_id=canonical_provider_stable_id,
    )


def _compile_prepared_default_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    registry_sha256: str,
    prepared_proof_authority: PreparedDefaultProofAuthority,
    annotation_mode: str = ANNOTATION_NONE,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Compiler-internal prepared path; never a caller selection override."""

    if not isinstance(prepared_proof_authority, PreparedDefaultProofAuthority):
        raise TypeError("prepared_proof_authority must be compiler-owned")
    return _compile_default_plan_impl(
        action,
        target,
        registry_sha256=registry_sha256,
        annotation_mode=annotation_mode,
        repository_root=repository_root,
        prepared_proof_authority=prepared_proof_authority,
        canonical_provider_stable_id=None,
    )


def _admission_failure(
    *,
    plan: Mapping[str, object],
    receipt: object,
    code: str,
    detail: str = "",
) -> dict[str, object]:
    body: dict[str, object] = {
        "schema": DEFAULT_EXECUTION_ADMISSION_SCHEMA,
        "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
        "status": "FAIL_CLOSED",
        "error_code": code,
        "error_detail": detail,
        "plan_sha256": plan.get("plan_sha256"),
        "traversal_receipt_sha256": (
            receipt.get("receipt_sha256")
            if isinstance(receipt, Mapping)
            else None
        ),
        "behavioral_optix_proven": False,
        "silicon_rt_core_utilization_proven": False,
        "whole_endpoint_rt_only_proven": False,
        "partner_stages_rejected": False,
    }
    body["admission_sha256"] = _digest(body)
    return body


def admit_default_execution(
    plan: Mapping[str, object],
    traversal_receipt: Mapping[str, object],
    *,
    verified_output_digest: str,
    expected_provider_library_sha256: str,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Validate the post-execution traversal receipt or fail closed.

    This validates OptiX traversal-route behavior.  It intentionally does not
    claim that partner stages ran on RT cores or estimate RT-core utilization.
    """

    try:
        # Reconstruct the complete selection and source contract before
        # accepting any runtime observation.  A caller cannot make a forged
        # plan trustworthy merely by recomputing its unkeyed JSON digest.
        from .default_compiler_frontdoor_reconstruct import (
            DefaultFrontdoorReconstructionError,
            reconstruct_default_plan,
        )

        try:
            reconstruct_default_plan(plan, repository_root=repository_root)
        except DefaultFrontdoorReconstructionError as exc:
            raise DefaultCompilerFrontdoorError(
                "DEFAULT_PLAN_RECONSTRUCTION_FAILED", str(exc)
            ) from exc
        if plan.get("schema") != DEFAULT_PLAN_SCHEMA or plan.get("status") != "PLANNED":
            raise DefaultCompilerFrontdoorError("INVALID_OR_FAILED_DEFAULT_PLAN")
        plan_sha = _validate_sha256(plan.get("plan_sha256"), field="plan_sha256")
        plan_body = dict(plan)
        plan_body.pop("plan_sha256", None)
        if _digest(plan_body) != plan_sha:
            raise DefaultCompilerFrontdoorError("DEFAULT_PLAN_DIGEST_MISMATCH")
        if plan.get("behavioral_optix_receipt_required") is not True:
            raise DefaultCompilerFrontdoorError(
                "PLAN_DOES_NOT_AUTHORIZE_OPTIX_BEHAVIORAL_CLAIM"
            )
        expected_output = _validate_sha256(
            verified_output_digest, field="verified_output_digest"
        )
        expected_native = _validate_sha256(
            expected_provider_library_sha256,
            field="expected_provider_library_sha256",
        )
        if traversal_receipt.get("schema") != TRAVERSAL_RECEIPT_SCHEMA:
            raise DefaultCompilerFrontdoorError("UNSUPPORTED_TRAVERSAL_RECEIPT")
        receipt_sha = _validate_sha256(
            traversal_receipt.get("receipt_sha256"), field="receipt_sha256"
        )
        receipt_body = dict(traversal_receipt)
        receipt_body.pop("receipt_sha256", None)
        if _digest(receipt_body) != receipt_sha:
            raise DefaultCompilerFrontdoorError("TRAVERSAL_RECEIPT_DIGEST_MISMATCH")
        if (
            traversal_receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
        ):
            raise DefaultCompilerFrontdoorError(
                "OPTIX_TRAVERSAL_NOT_BEHAVIORALLY_OBSERVED"
            )
        if traversal_receipt.get("provider_library") != "librtdl_optix":
            raise DefaultCompilerFrontdoorError("UNEXPECTED_PROVIDER_LIBRARY")
        if traversal_receipt.get("provider_library_sha256") != expected_native:
            raise DefaultCompilerFrontdoorError("PROVIDER_LIBRARY_SHA_MISMATCH")
        if traversal_receipt.get("route_identity") != plan.get(
            "prescribed_route_identity"
        ):
            raise DefaultCompilerFrontdoorError("PLAN_ROUTE_IDENTITY_MISMATCH")
        action = _require_mapping(plan.get("action"), field="plan.action")
        if traversal_receipt.get("semantic_digest") != action.get("action_digest"):
            raise DefaultCompilerFrontdoorError("ACTION_SEMANTIC_DIGEST_MISMATCH")
        if traversal_receipt.get("output_digest") != expected_output:
            raise DefaultCompilerFrontdoorError("VERIFIED_OUTPUT_DIGEST_MISMATCH")

        program = _require_mapping(
            plan.get("optix_program_contract"), field="optix_program_contract"
        )
        expected_names = program.get("program_bundles")
        expected_ids = program.get("program_bundle_ids")
        if not isinstance(expected_names, list) or not expected_names:
            raise DefaultCompilerFrontdoorError("EMPTY_EXPECTED_PROGRAM_SET")
        if not isinstance(expected_ids, list) or expected_ids != [
            physical_program_bundle_id(name) for name in expected_names
        ]:
            raise DefaultCompilerFrontdoorError("PROGRAM_BUNDLE_ID_CONTRACT_MISMATCH")
        if traversal_receipt.get("expected_program_bundles") != expected_names:
            raise DefaultCompilerFrontdoorError("EXPECTED_PROGRAM_NAMES_MISMATCH")
        if traversal_receipt.get("expected_program_bundle_ids") != expected_ids:
            raise DefaultCompilerFrontdoorError("EXPECTED_PROGRAM_IDS_MISMATCH")
        if traversal_receipt.get("expected_program_observed_at_receipt_edge") is not True:
            raise DefaultCompilerFrontdoorError("EXPECTED_PROGRAM_NOT_OBSERVED")

        nonce = _require_mapping(traversal_receipt.get("nonce"), field="nonce")
        snapshot = _require_mapping(
            traversal_receipt.get("native_snapshot"), field="native_snapshot"
        )
        nonce_hi = nonce.get("hi")
        nonce_lo = nonce.get("lo")
        if (
            not isinstance(nonce_hi, int)
            or isinstance(nonce_hi, bool)
            or not isinstance(nonce_lo, int)
            or isinstance(nonce_lo, bool)
            or nonce_hi < 0
            or nonce_lo < 0
            or nonce_hi >= 1 << 64
            or nonce_lo >= 1 << 64
            or (nonce_hi == 0 and nonce_lo == 0)
            or snapshot.get("nonce_hi") != nonce_hi
            or snapshot.get("nonce_lo") != nonce_lo
        ):
            raise DefaultCompilerFrontdoorError("TRAVERSAL_NONCE_BINDING_INVALID")

        def count(name: str) -> int:
            value = snapshot.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise DefaultCompilerFrontdoorError(
                    "INVALID_NATIVE_SNAPSHOT_COUNT", name
                )
            return value

        attempted = count("attempted_launch_count")
        successful = count("successful_launch_count")
        failed = count("failed_launch_count")
        complete = count("complete_context_launch_count")
        incomplete = count("incomplete_context_launch_count")
        context_bind = count("context_bind_count")
        if successful <= 0 or attempted != successful or failed != 0:
            raise DefaultCompilerFrontdoorError("OPTIX_LAUNCH_COUNTS_INVALID")
        if complete != successful or incomplete != 0 or context_bind != successful:
            raise DefaultCompilerFrontdoorError("OPTIX_CONTEXT_BINDING_INCOMPLETE")
        if (
            count("pending_context_at_finish") != 0
            or count("session_error") != 0
            or count("incomplete_callsite_record_count") != 0
        ):
            raise DefaultCompilerFrontdoorError("OPTIX_AUDIT_SESSION_NOT_CLEAN")
        if count("raygen_invocation_count") <= 0:
            raise DefaultCompilerFrontdoorError("ZERO_RAYGEN_INVOCATIONS")
        if count("first_traversable") == 0 or count("last_traversable") == 0:
            raise DefaultCompilerFrontdoorError("ZERO_TRAVERSABLE_BINDING")
        for field in (
            "program_bundle_mix",
            "traversable_mix",
            "pipeline_mix",
            "sbt_mix",
            "stream_mix",
            "params_mix",
            "callsite_mix",
        ):
            if count(field) == 0:
                raise DefaultCompilerFrontdoorError(
                    "MISSING_OPTIX_BINDING_EVIDENCE", field
                )
        observed_edges = {
            count("first_program_bundle_id"),
            count("last_program_bundle_id"),
        } - {0}
        if not set(expected_ids).issubset(observed_edges):
            raise DefaultCompilerFrontdoorError(
                "EXPECTED_PROGRAM_SET_NOT_BOUND_AT_RECEIPT_EDGES"
            )
        rules = _require_mapping(
            traversal_receipt.get("claim_rules"), field="claim_rules"
        )
        required_rules = {
            "provider_name_alone_proves_traversal": False,
            "selected_template_alone_proves_traversal": False,
            "successful_optix_launch_required": True,
            "nonzero_traversable_binding_required": True,
            "program_bundle_binding_required": True,
            "output_digest_bound": True,
        }
        if any(rules.get(key) is not value for key, value in required_rules.items()):
            raise DefaultCompilerFrontdoorError("TRAVERSAL_CLAIM_RULES_WEAKENED")

        body: dict[str, object] = {
            "schema": DEFAULT_EXECUTION_ADMISSION_SCHEMA,
            "policy_version": DEFAULT_FRONTDOOR_POLICY_VERSION,
            "status": "PASS",
            "plan_sha256": plan_sha,
            "selection_receipt_sha256": plan.get("selection_receipt_sha256"),
            "selected_candidate_stable_id": plan.get(
                "selected_candidate_stable_id"
            ),
            "program_contract_sha256": program.get("program_contract_sha256"),
            "traversal_receipt_sha256": receipt_sha,
            "verified_output_digest": expected_output,
            "provider_library_sha256": expected_native,
            "behavioral_optix_proven": True,
            "silicon_rt_core_utilization_proven": False,
            "whole_endpoint_rt_only_proven": False,
            "partner_stages_rejected": False,
            "partner_stages_permitted": plan.get("partner_stages_permitted") is True,
        }
        body["admission_sha256"] = _digest(body)
        return body
    except DefaultCompilerFrontdoorError as error:
        return _admission_failure(
            plan=plan,
            receipt=traversal_receipt,
            code=error.code,
            detail=error.detail,
        )


__all__ = [
    "DEFAULT_PROGRAM_PROOF_CAPSULE_SCHEMA",
    "DEFAULT_EXECUTION_ADMISSION_SCHEMA",
    "DEFAULT_FRONTDOOR_POLICY_VERSION",
    "DEFAULT_PLAN_SCHEMA",
    "PREPARED_DEFAULT_PROOF_AUTHORITY_SCHEMA",
    "DefaultCompilerFrontdoorError",
    "PreparedDefaultProofAuthority",
    "admit_default_execution",
    "build_default_program_proof_capsule",
    "compile_default_plan",
    "install_default_program_proof_capsule",
    "prepare_default_proof_authority",
]
