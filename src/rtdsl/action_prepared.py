from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
import ctypes
import hashlib
import hmac
import json
import math
import secrets
import time
from typing import Mapping, NoReturn

from .action_api import (
    ActionProducerKind,
    LoweredAction,
    PlannedLoweredAction,
    prepare_bound_numba_action_compiler_snapshot,
    prepare_bound_numba_action_device_columns,
    rebind_lowered_action_event_columns,
    prepare_bound_numba_action_columns,
    validate_planned_lowered_action,
)
from .action_composition import (
    UINT32_MAX,
    ActionConsumerCompositionKind,
    action_template_identity_digest,
    validate_certified_nearest_global_argmax_composition,
)
from .action_ir import ExtentKind
from .action_native_identity import validate_native_library_identity


ACTION_PREPARED_VERSION = "rtdl.action_prepared_execution.private_candidate.v1"
_PACKED_POINT_FULL_DIGEST_KIND = "packed_point_full_v1"
_PACKED_POINT_SAMPLE_DIGEST_KIND = "packed_point_sample_v1"
_PREPARED_IDENTITY_SEAL_SECRET = secrets.token_bytes(32)
_PREPARED_QUERY_BATCH_SEAL_SECRET = secrets.token_bytes(32)


def _detached_json_metadata(value):
    """Return a caller-owned JSON-compatible copy of sealed metadata."""

    if isinstance(value, Mapping):
        detached = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("prepared metadata keys must be strings")
            detached[key] = _detached_json_metadata(item)
        return detached
    if isinstance(value, (tuple, list)):
        return [_detached_json_metadata(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(
        "prepared metadata must contain only JSON-compatible values"
    )


class ActionPreparedStreamOrdering(str, Enum):
    SYNCHRONOUS_DEFAULT_STREAM = "synchronous_default_stream.v1"
    EXPLICIT_SERIAL_STREAM = "explicit_serial_stream.v1"


@dataclass(frozen=True)
class ActionPreparedIssue:
    code: str
    path: str
    message: str


class ActionPreparedError(ValueError):
    def __init__(self, issue: ActionPreparedIssue) -> None:
        self.issue = issue
        super().__init__(
            f"Prepared Action failed: {issue.code}@{issue.path}: {issue.message}"
        )


@dataclass(frozen=True)
class PreparedTriangleGroupedI64Payload3D:
    """Immutable primitive payload for a compiler-owned prepared 3-D index."""

    triangles: object
    primitive_group_ids: object
    primitive_values: object
    primitive_includes: object
    group_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.group_count, int) or isinstance(self.group_count, bool):
            _fail("nonnegative_group_count_required", "group_count", repr(self.group_count))
        if self.group_count < 0:
            _fail("nonnegative_group_count_required", "group_count", repr(self.group_count))
        lengths = (
            len(self.primitive_group_ids),
            len(self.primitive_values),
            len(self.primitive_includes),
        )
        if len(set(lengths)) != 1:
            _fail(
                "primitive_payload_length_mismatch",
                "prepared_input",
                f"groups={lengths[0]} values={lengths[1]} includes={lengths[2]}",
            )


class ConsumedPreparedTriangleGroupedI64Payload3D:
    """Move-only compiler payload for an already prepared grouped index.

    Raw host arrays are validated and synchronously consumed while constructing
    the backend owner. Persistent Action identity then binds only the exact
    sealed owner generation and structural program facts. The legacy raw
    payload remains supported and retains its full-content identity scan.
    """

    contract = "rtdl.consumed_prepared_triangle_grouped_i64_payload_3d.v1"

    def __init__(self, capability, program) -> None:
        from .action_optix_lowering import ConsumedOptixActionKeyedI64Sum3D

        if type(capability) is not ConsumedOptixActionKeyedI64Sum3D:
            _fail(
                "consumed_triangle_grouped_i64_owner_required",
                "capability",
                type(capability).__name__,
            )
        capability.validate_for_program(program)
        metadata = capability.to_metadata()
        if metadata.get("consumed") is not False:
            _fail(
                "consumed_triangle_grouped_i64_owner_already_taken",
                "capability",
                "owner capability must be fresh",
            )
        self._capability = capability
        self._capability_ref = capability
        self._capability_object_id = id(capability)
        self._capability_type = (
            f"{type(capability).__module__}.{type(capability).__qualname__}"
        )
        self._owner_identity_digest = str(metadata["identity_digest"])
        self._generation_sha256 = str(metadata["generation_sha256"])
        self._structural_metadata = dict(metadata["structural_metadata"])
        self._semantic_digest = str(program.spec.semantic_digest)
        self._template_digest = str(program.template_digest)
        self._consumed = False
        self._closed = False
        self._close_progress = 0
        self._seal = self._issue_seal()

    @property
    def consumed(self) -> bool:
        return self._consumed

    @property
    def identity_digest(self) -> str:
        return self._owner_identity_digest

    def _seal_payload(self) -> bytes:
        return json.dumps(
            {
                "contract": self.contract,
                "capability_object_id": self._capability_object_id,
                "capability_type": self._capability_type,
                "owner_identity_digest": self._owner_identity_digest,
                "generation_sha256": self._generation_sha256,
                "structural_metadata": self._structural_metadata,
                "semantic_digest": self._semantic_digest,
                "template_digest": self._template_digest,
                "close_progress": self._close_progress,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _PREPARED_IDENTITY_SEAL_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def validate_for_lowered(self, lowered: LoweredAction) -> None:
        from .action_optix_lowering import ConsumedOptixActionKeyedI64Sum3D

        if self._closed:
            _fail(
                "consumed_triangle_grouped_i64_payload_closed",
                "prepared_input",
                "payload was closed before owner transfer",
            )
        if self._consumed:
            _fail(
                "consumed_triangle_grouped_i64_owner_already_taken",
                "prepared_input",
                "owner capability is single-use",
            )
        capability = self._capability
        if (
            capability is None
            or capability is not self._capability_ref
            or type(capability) is not ConsumedOptixActionKeyedI64Sum3D
            or id(capability) != self._capability_object_id
            or f"{type(capability).__module__}.{type(capability).__qualname__}"
            != self._capability_type
            or self._close_progress != 0
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            _fail(
                "consumed_triangle_grouped_i64_binding_invalid",
                "prepared_input",
                "capability object, generation, structural facts, or seal changed",
            )
        if (
            lowered.backend != "optix"
            or lowered.template_kind != "keyed_i64_sum_3d"
            or lowered.compiled.spec.semantic_digest != self._semantic_digest
            or getattr(lowered.program, "template_digest", None)
            != self._template_digest
        ):
            _fail(
                "consumed_triangle_grouped_i64_plan_mismatch",
                "prepared_input",
                f"{lowered.backend}:{lowered.template_kind}",
            )
        ConsumedOptixActionKeyedI64Sum3D.validate_for_program(
            capability,
            lowered.program,
        )
        current = ConsumedOptixActionKeyedI64Sum3D.to_metadata(capability)
        if (
            current.get("identity_digest") != self._owner_identity_digest
            or current.get("generation_sha256") != self._generation_sha256
            or dict(current.get("structural_metadata", {}))
            != self._structural_metadata
            or current.get("consumed") is not False
        ):
            _fail(
                "consumed_triangle_grouped_i64_metadata_drift",
                "prepared_input",
                "capability metadata differs from the compiler-issued snapshot",
            )

    def _prepared_identity_metadata(self) -> dict[str, object]:
        return {
            "contract": self.contract,
            "owner_identity_digest": self._owner_identity_digest,
            "generation_sha256": self._generation_sha256,
            "structural_metadata": dict(self._structural_metadata),
            "semantic_digest": self._semantic_digest,
            "template_digest": self._template_digest,
            "compiler_owned": True,
            "single_use": True,
            "backend_resource_prepared_before_issue": True,
            "host_payload_content_rehashed_for_persistent_identity": False,
        }

    def take_backend_owner(self, lowered: LoweredAction):
        from .action_optix_lowering import ConsumedOptixActionKeyedI64Sum3D

        self.validate_for_lowered(lowered)
        capability = self._capability
        owner = ConsumedOptixActionKeyedI64Sum3D.take_backend_owner(
            capability,
            lowered.program,
        )
        self._consumed = True
        return owner

    def close(self) -> None:
        if self._closed:
            return
        from .action_optix_lowering import ConsumedOptixActionKeyedI64Sum3D

        capability = self._capability
        if (
            capability is None
            or capability is not self._capability_ref
            or type(capability) is not ConsumedOptixActionKeyedI64Sum3D
            or id(capability) != self._capability_object_id
            or f"{type(capability).__module__}.{type(capability).__qualname__}"
            != self._capability_type
            or self._close_progress not in {0, 1}
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            _fail(
                "consumed_triangle_grouped_i64_binding_invalid",
                "prepared_input",
                "capability object, generation, structural facts, or seal changed",
            )
        if not self._consumed:
            try:
                ConsumedOptixActionKeyedI64Sum3D.close(capability)
            except Exception:
                if getattr(capability, "_close_progress", None) == 1:
                    self._close_progress = 1
                    self._seal = self._issue_seal()
                raise
        self._close_progress = 2
        self._seal = self._issue_seal()
        self._closed = True

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


@dataclass(frozen=True)
class PreparedCertifiedNearestGridPayload3D:
    """Immutable target/grid input for a certified nearest-state lifetime."""

    target_points: object
    target_ids: object | None = None
    grid_shape: tuple[int, int, int] = (32, 32, 32)
    independent_validation_sample_count: int = 64
    query_domain_lower_bounds: tuple[float, float, float] | None = None
    query_domain_upper_bounds: tuple[float, float, float] | None = None
    optix_max_inline_points: int = 64
    optix_max_heavy_point_evaluations: int = 1 << 30
    cell_mbr_point_order: str = "point-id"
    prepared_target_domain: bool = False
    _column_domain_certificate: object = field(
        init=False, repr=False, compare=False
    )
    _column_domain_certificate_object_id: int = field(
        init=False, repr=False, compare=False
    )
    _column_domain_binding_seal: str = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        from .action_nearest_state_lowering import (
            ImmutablePointColumnDomain3DCertificateError,
            certify_immutable_point_column_domain_3d,
        )

        try:
            certificate = certify_immutable_point_column_domain_3d(
                self.target_points,
                self.target_ids,
            )
        except ImmutablePointColumnDomain3DCertificateError as exc:
            code, path = {
                "target_matrix_required": (
                    "prepared_nearest_target_matrix_required",
                    "prepared_input.target_points",
                ),
                "target_count_u32_overflow": (
                    "prepared_nearest_target_count_u32_overflow",
                    "prepared_input.target_points",
                ),
                "target_finite_required": (
                    "prepared_nearest_target_finite_required",
                    "prepared_input.target_points",
                ),
                "target_ids_invalid": (
                    "prepared_nearest_target_ids_invalid",
                    "prepared_input.target_ids",
                ),
            }.get(
                exc.code,
                (
                    "prepared_nearest_column_domain_certificate_invalid",
                    "prepared_input",
                ),
            )
            _fail(code, path, str(exc))
        shape = tuple(int(value) for value in self.grid_shape)
        if len(shape) != 3 or any(value <= 0 for value in shape):
            _fail(
                "prepared_nearest_grid_shape_invalid",
                "prepared_input.grid_shape",
                repr(shape),
            )
        if not isinstance(self.independent_validation_sample_count, int) or isinstance(
            self.independent_validation_sample_count, bool
        ) or self.independent_validation_sample_count < 0:
            _fail(
                "prepared_nearest_validation_sample_count_invalid",
                "prepared_input.independent_validation_sample_count",
                repr(self.independent_validation_sample_count),
            )
        if not isinstance(self.prepared_target_domain, bool):
            _fail(
                "prepared_nearest_target_domain_mode_invalid",
                "prepared_input.prepared_target_domain",
                repr(self.prepared_target_domain),
            )
        query_lower = self.query_domain_lower_bounds
        query_upper = self.query_domain_upper_bounds
        if (query_lower is None) != (query_upper is None):
            _fail(
                "prepared_nearest_query_domain_pair_required",
                "prepared_input.query_domain",
                "lower and upper bounds must be provided together",
            )
        if query_lower is not None:
            try:
                normalized_lower = tuple(float(value) for value in query_lower)
                normalized_upper = tuple(float(value) for value in query_upper)
            except Exception as exc:
                _fail(
                    "prepared_nearest_query_domain_invalid",
                    "prepared_input.query_domain",
                    str(exc),
                )
            if (
                len(normalized_lower) != 3
                or len(normalized_upper) != 3
                or any(
                    not math.isfinite(value)
                    for value in (*normalized_lower, *normalized_upper)
                )
                or any(
                    upper < lower
                    for lower, upper in zip(
                        normalized_lower, normalized_upper
                    )
                )
            ):
                _fail(
                    "prepared_nearest_query_domain_invalid",
                    "prepared_input.query_domain",
                    f"{normalized_lower!r}..{normalized_upper!r}",
                )
            query_lower = normalized_lower
            query_upper = normalized_upper
        for name in (
            "optix_max_inline_points",
            "optix_max_heavy_point_evaluations",
        ):
            value = getattr(self, name)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
                or value > (1 << 64) - 1
            ):
                _fail(
                    "prepared_nearest_optix_capacity_invalid",
                    f"prepared_input.{name}",
                    repr(value),
                )
        if self.cell_mbr_point_order not in {"point-id", "input-stable"}:
            _fail(
                "prepared_nearest_cell_mbr_point_order_invalid",
                "prepared_input.cell_mbr_point_order",
                repr(self.cell_mbr_point_order),
            )
        object.__setattr__(self, "target_points", certificate.target_points)
        object.__setattr__(self, "target_ids", certificate.target_ids)
        object.__setattr__(self, "grid_shape", shape)
        object.__setattr__(
            self, "query_domain_lower_bounds", query_lower
        )
        object.__setattr__(
            self, "query_domain_upper_bounds", query_upper
        )
        object.__setattr__(self, "_column_domain_certificate", certificate)
        object.__setattr__(
            self,
            "_column_domain_certificate_object_id",
            id(certificate),
        )
        object.__setattr__(
            self,
            "_column_domain_binding_seal",
            self._issue_column_domain_binding_seal(),
        )
        self._validated_column_domain_certificate()

    def _column_domain_binding_payload(self) -> bytes:
        certificate = self._column_domain_certificate
        return (
            "rtdl.prepared_nearest_column_domain_binding.v1\x00"
            f"{id(certificate)}\x00{self._column_domain_certificate_object_id}\x00"
            f"{id(self.target_points)}\x00{id(self.target_ids)}\x00"
            f"{certificate.target_content_digest}\x00{self.grid_shape}\x00"
            f"{self.independent_validation_sample_count}\x00"
            f"{self.query_domain_lower_bounds}\x00"
            f"{self.query_domain_upper_bounds}\x00"
            f"{self.optix_max_inline_points}\x00"
            f"{self.optix_max_heavy_point_evaluations}\x00"
            f"{self.cell_mbr_point_order}\x00"
            f"{self.prepared_target_domain}"
        ).encode("ascii")

    def _issue_column_domain_binding_seal(self) -> str:
        return hmac.new(
            _PREPARED_IDENTITY_SEAL_SECRET,
            self._column_domain_binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validated_column_domain_certificate(self):
        try:
            certificate = self._column_domain_certificate
            if id(certificate) != self._column_domain_certificate_object_id:
                raise RuntimeError("certificate object changed")
            expected_seal = self._issue_column_domain_binding_seal()
            if not hmac.compare_digest(
                self._column_domain_binding_seal,
                expected_seal,
            ):
                raise RuntimeError("payload/certificate binding seal changed")
            certificate.validate_exact(self.target_points, self.target_ids)
            return certificate
        except Exception as exc:
            _fail(
                "prepared_nearest_column_domain_certificate_invalid",
                "prepared_input",
                str(exc),
            )

    def _prepared_identity_metadata(self) -> dict[str, object]:
        certificate = self._validated_column_domain_certificate()
        metadata = {
            "contract": "rtdl.prepared_certified_nearest_grid_payload_3d.v3",
            "column_domain_certificate": certificate.identity_metadata(),
            "grid_shape": list(self.grid_shape),
            "independent_validation_sample_count": (
                self.independent_validation_sample_count
            ),
            "query_domain_lower_bounds": (
                list(self.query_domain_lower_bounds)
                if self.query_domain_lower_bounds is not None
                else None
            ),
            "query_domain_upper_bounds": (
                list(self.query_domain_upper_bounds)
                if self.query_domain_upper_bounds is not None
                else None
            ),
            "optix_max_inline_points": self.optix_max_inline_points,
            "optix_max_heavy_point_evaluations": (
                self.optix_max_heavy_point_evaluations
            ),
            "cell_mbr_point_order": self.cell_mbr_point_order,
        }
        if self.prepared_target_domain:
            metadata["prepared_target_domain"] = True
        return metadata


@dataclass(frozen=True)
class ActionPreparedIdentity:
    semantic_digest: str
    source_digest: str
    producer_kind: str
    producer_certificate_digest: str
    producer_schema_digest: str
    target_profile_digest: str
    physical_plan_digest: str
    selected_backend: str
    selected_placement: str
    selected_template: str
    consumer_composition_digest: str
    consumer_composition_kind: str
    native_library_identity_digest: str
    native_library_object_token: str
    module_owner_digest: str
    index_owner_digest: str
    state_owner_digest: str
    extents_digest: str
    parameters_digest: str
    bounded_output_rows: int
    bounded_output_bytes: int
    event_batch_row_count_mode: str
    max_event_rows: int | None
    stream_ordering: str
    identity_digest: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": ACTION_PREPARED_VERSION,
            "semantic_digest": self.semantic_digest,
            "source_digest": self.source_digest,
            "producer_kind": self.producer_kind,
            "producer_certificate_digest": self.producer_certificate_digest,
            "producer_schema_digest": self.producer_schema_digest,
            "target_profile_digest": self.target_profile_digest,
            "physical_plan_digest": self.physical_plan_digest,
            "selected_backend": self.selected_backend,
            "selected_placement": self.selected_placement,
            "selected_template": self.selected_template,
            "consumer_composition_digest": self.consumer_composition_digest,
            "consumer_composition_kind": self.consumer_composition_kind,
            "native_library_identity_digest": self.native_library_identity_digest,
            "native_library_object_token": self.native_library_object_token,
            "module_owner_digest": self.module_owner_digest,
            "index_owner_digest": self.index_owner_digest,
            "state_owner_digest": self.state_owner_digest,
            "extents_digest": self.extents_digest,
            "parameters_digest": self.parameters_digest,
            "bounded_output_rows": self.bounded_output_rows,
            "bounded_output_bytes": self.bounded_output_bytes,
            "event_batch_row_count_mode": self.event_batch_row_count_mode,
            "max_event_rows": self.max_event_rows,
            "stream_ordering": self.stream_ordering,
            "identity_digest": self.identity_digest,
        }


def validate_action_prepared_identity_metadata(
    metadata: Mapping[str, object],
) -> dict[str, object]:
    """Validate one complete persisted prepared identity and public digest."""

    if not isinstance(metadata, Mapping):
        _fail(
            "prepared_identity_metadata_mapping_required",
            "identity",
            type(metadata).__name__,
        )
    value = dict(metadata)
    payload_keys = {
        field.name for field in fields(ActionPreparedIdentity)
    } - {"identity_digest"}
    expected_keys = payload_keys | {"contract", "identity_digest"}
    if set(value) != expected_keys:
        _fail(
            "prepared_identity_metadata_fields_differ",
            "identity",
            repr(sorted(value)),
        )
    if value["contract"] != ACTION_PREPARED_VERSION:
        _fail(
            "prepared_identity_metadata_contract_differ",
            "identity.contract",
            repr(value["contract"]),
        )

    sha_fields = {
        "semantic_digest",
        "source_digest",
        "producer_certificate_digest",
        "producer_schema_digest",
        "target_profile_digest",
        "physical_plan_digest",
        "module_owner_digest",
        "index_owner_digest",
        "state_owner_digest",
        "extents_digest",
        "parameters_digest",
        "identity_digest",
    }
    for name in sha_fields:
        if not _is_sha256_digest(value[name]):
            _fail(
                "prepared_identity_metadata_digest_invalid",
                f"identity.{name}",
                repr(value[name]),
            )
    for name in ("consumer_composition_digest", "native_library_identity_digest"):
        if value[name] != "none" and not _is_sha256_digest(value[name]):
            _fail(
                "prepared_identity_metadata_digest_invalid",
                f"identity.{name}",
                repr(value[name]),
            )
    for name in (
        "producer_kind",
        "selected_backend",
        "selected_placement",
        "selected_template",
        "consumer_composition_kind",
        "native_library_object_token",
        "event_batch_row_count_mode",
        "stream_ordering",
    ):
        if type(value[name]) is not str or not value[name]:
            _fail(
                "prepared_identity_metadata_string_invalid",
                f"identity.{name}",
                repr(value[name]),
            )
    for name in ("bounded_output_rows", "bounded_output_bytes"):
        if (
            not isinstance(value[name], int)
            or isinstance(value[name], bool)
            or value[name] < 0
        ):
            _fail(
                "prepared_identity_metadata_bound_invalid",
                f"identity.{name}",
                repr(value[name]),
            )
    max_rows = value["max_event_rows"]
    if max_rows is not None and (
        not isinstance(max_rows, int)
        or isinstance(max_rows, bool)
        or max_rows < 0
    ):
        _fail(
            "prepared_identity_metadata_bound_invalid",
            "identity.max_event_rows",
            repr(max_rows),
        )
    if value["event_batch_row_count_mode"] not in {
        "bounded_variable",
        "exact_initial_batch",
    } or value["stream_ordering"] not in {
        item.value for item in ActionPreparedStreamOrdering
    }:
        _fail(
            "prepared_identity_metadata_mode_invalid",
            "identity",
            "row-count mode or stream ordering differs",
        )
    payload = {name: value[name] for name in payload_keys}
    expected_digest = _digest(payload, "prepared_identity")
    if not hmac.compare_digest(value["identity_digest"], expected_digest):
        _fail(
            "prepared_identity_metadata_digest_mismatch",
            "identity.identity_digest",
            "public identity digest does not match the complete payload",
        )
    return value


def validate_prepared_backend_owner_metadata_snapshot(
    prepared_metadata: Mapping[str, object],
) -> dict[str, object] | None:
    """Recompute the public digest for a persisted backend-owner snapshot."""

    if not isinstance(prepared_metadata, Mapping):
        _fail(
            "prepared_metadata_mapping_required",
            "prepared_metadata",
            type(prepared_metadata).__name__,
        )
    snapshot = prepared_metadata.get("backend_owner_metadata")
    digest = prepared_metadata.get("backend_owner_metadata_digest")
    if snapshot is None:
        if digest != "none":
            _fail(
                "prepared_backend_owner_metadata_digest_mismatch",
                "backend_owner_metadata_digest",
                repr(digest),
            )
        return None
    if not isinstance(snapshot, Mapping) or not _is_sha256_digest(digest):
        _fail(
            "prepared_backend_owner_metadata_invalid",
            "backend_owner_metadata",
            type(snapshot).__name__,
        )
    value = dict(snapshot)
    expected = _digest(value, "backend_owner_metadata")
    if not hmac.compare_digest(digest, expected):
        _fail(
            "prepared_backend_owner_metadata_digest_mismatch",
            "backend_owner_metadata_digest",
            "public backend-owner digest differs",
        )
    return value


@dataclass(frozen=True)
class PreparedActionQueryResult:
    payload: object
    query_ordinal: int
    timing_regime: str
    elapsed_seconds: float
    prepared_identity_digest: str
    backend_owner_generation: int
    event_batch_certificate: Mapping[str, object] | None = None

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.prepared_action_query_result.private_candidate.v1",
            "query_ordinal": self.query_ordinal,
            "timing_regime": self.timing_regime,
            "elapsed_seconds": self.elapsed_seconds,
            "prepared_identity_digest": self.prepared_identity_digest,
            "backend_owner_generation": self.backend_owner_generation,
            "event_batch_certificate": (
                _detached_json_metadata(self.event_batch_certificate)
                if self.event_batch_certificate is not None
                else None
            ),
            "runtime_speedup_claimed": False,
        }


class PreparedActionQueryBatch:
    """Compiler-owned prepared query input reusable across compatible indices."""

    contract = "rtdl.prepared_action_query_batch.private_candidate.v1"

    def __init__(
        self,
        native_owner,
        *,
        compatibility_digest: str,
        query_input_digest: str,
        query_count: int | None,
        prepare_elapsed_seconds: float,
    ) -> None:
        if native_owner is None:
            _fail("prepared_query_native_owner_required", "native_owner", "none")
        self._native_owner = native_owner
        self._native_owner_ref = native_owner
        self._native_owner_object_id = id(native_owner)
        self._native_owner_type = (
            f"{type(native_owner).__module__}.{type(native_owner).__qualname__}"
        )
        self._compatibility_digest = compatibility_digest
        self._query_input_digest = query_input_digest
        self._query_count = query_count
        self._prepare_elapsed_seconds = float(prepare_elapsed_seconds)
        self.execution_count = 0
        self._closed = False
        self._native_owner_binding_snapshot = self._current_native_owner_binding_snapshot()
        self._native_owner_binding_digest = _digest(
            self._native_owner_binding_snapshot,
            "prepared_query_native_owner_binding",
        )
        self._seal = self._issue_seal()

    @property
    def compatibility_digest(self) -> str:
        return self._compatibility_digest

    @property
    def query_input_digest(self) -> str:
        return self._query_input_digest

    @property
    def query_count(self) -> int | None:
        return self._query_count

    @property
    def prepare_elapsed_seconds(self) -> float:
        return self._prepare_elapsed_seconds

    def _current_native_owner_binding_snapshot(self) -> dict[str, object]:
        owner = self._native_owner
        if owner is None:
            _fail("prepared_query_batch_closed", "prepared_query", "batch is closed")
        metadata_function = getattr(
            type(owner),
            "compiler_native_resource_binding_metadata",
            None,
        )
        if metadata_function is not None:
            try:
                native_metadata = metadata_function(owner)
            except Exception as exc:
                _fail(
                    "prepared_query_native_owner_binding_invalid",
                    "prepared_query.native_owner",
                    f"native owner validation failed: {type(exc).__name__}:{exc}",
                )
            if not isinstance(native_metadata, Mapping):
                _fail(
                    "prepared_query_native_owner_metadata_invalid",
                    "prepared_query.native_owner",
                    type(native_metadata).__name__,
                )
            native_metadata = dict(native_metadata)
        else:
            native_metadata = {
                "contract": "opaque_prepared_query_owner.v1",
                "object_id": id(owner),
                "type": f"{type(owner).__module__}.{type(owner).__qualname__}",
                "ray_count": getattr(owner, "ray_count", None),
                "closed": bool(getattr(owner, "closed", getattr(owner, "_closed", False))),
            }
        return {
            "native_owner_object_id": id(owner),
            "native_owner_type": f"{type(owner).__module__}.{type(owner).__qualname__}",
            "native_owner_metadata_function_id": (
                id(metadata_function) if metadata_function is not None else None
            ),
            "native_owner_metadata_function_type": (
                f"{type(metadata_function).__module__}.{type(metadata_function).__qualname__}"
                if metadata_function is not None
                else "none"
            ),
            "native_owner_metadata": native_metadata,
        }

    def _binding_payload(self) -> bytes:
        return json.dumps(
            {
                "contract": self.contract,
                "native_owner_object_id": self._native_owner_object_id,
                "native_owner_type": self._native_owner_type,
                "native_owner_binding_digest": self._native_owner_binding_digest,
                "compatibility_digest": self._compatibility_digest,
                "query_input_digest": self._query_input_digest,
                "query_count": self._query_count,
                "prepare_elapsed_seconds": self._prepare_elapsed_seconds,
                "execution_count": self.execution_count,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _issue_seal(self) -> str:
        return hmac.new(
            _PREPARED_QUERY_BATCH_SEAL_SECRET,
            self._binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def validate_open(self) -> None:
        if type(self) is not PreparedActionQueryBatch:
            _fail(
                "prepared_query_batch_exact_type_required",
                "prepared_query",
                type(self).__name__,
            )
        if (
            self._closed
            or self._native_owner is None
            or self._native_owner is not self._native_owner_ref
        ):
            _fail("prepared_query_batch_closed", "prepared_query", "batch is closed or replaced")
        current_type = (
            f"{type(self._native_owner).__module__}.{type(self._native_owner).__qualname__}"
        )
        current_snapshot = self._current_native_owner_binding_snapshot()
        if (
            id(self._native_owner) != self._native_owner_object_id
            or current_type != self._native_owner_type
            or current_snapshot != self._native_owner_binding_snapshot
            or not hmac.compare_digest(
                _digest(current_snapshot, "prepared_query_native_owner_binding"),
                self._native_owner_binding_digest,
            )
            or not isinstance(self._compatibility_digest, str)
            or not _is_sha256_digest(self._compatibility_digest)
            or not isinstance(self._query_input_digest, str)
            or not _is_sha256_digest(self._query_input_digest)
            or (
                self._query_count is not None
                and (
                    not isinstance(self._query_count, int)
                    or isinstance(self._query_count, bool)
                    or self._query_count < 0
                )
            )
            or not math.isfinite(self._prepare_elapsed_seconds)
            or self._prepare_elapsed_seconds < 0.0
            or not isinstance(self.execution_count, int)
            or isinstance(self.execution_count, bool)
            or self.execution_count < 0
            or not isinstance(self._seal, str)
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            _fail(
                "prepared_query_batch_binding_invalid",
                "prepared_query",
                "query identity, native owner, or private seal changed",
            )

    def native_owner_for_execution(self):
        self.validate_open()
        return self._native_owner_ref

    def record_execution(self) -> None:
        self.validate_open()
        self.execution_count += 1
        self._seal = self._issue_seal()

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if self._closed:
            return
        self.validate_open()
        owner = self._native_owner_ref
        if owner is not None and hasattr(owner, "close"):
            type(owner).close(owner)
        self._native_owner = None
        self._closed = True

    def to_metadata(self) -> dict[str, object]:
        if not self._closed:
            self.validate_open()
        return {
            "contract": self.contract,
            "compatibility_digest": self._compatibility_digest,
            "query_input_digest": self._query_input_digest,
            "query_count": self._query_count,
            "prepare_elapsed_seconds": self._prepare_elapsed_seconds,
            "execution_count": self.execution_count,
            "closed": self._closed,
            "native_owner_object_bound": True,
            "native_owner_binding_digest": self._native_owner_binding_digest,
            "compiler_owned": True,
            "application_selected_backend": False,
            "runtime_speedup_claimed": False,
        }

    def __enter__(self):
        self.validate_open()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


class PreparedActionExecution:
    """Compiler-owned prepared plan with explicit identity and query lifetime."""

    def __init__(
        self,
        planned: PlannedLoweredAction,
        identity: ActionPreparedIdentity,
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering,
        backend_owner: object | None,
        prepare_elapsed_seconds: float,
        max_event_rows: int | None,
    ) -> None:
        self._planned = planned
        self._identity = identity
        self._identity_seal = hmac.new(
            _PREPARED_IDENTITY_SEAL_SECRET,
            json.dumps(
                identity.to_metadata(),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self._extents = _normalize_extents(extents)
        self._parameters = dict(parameters)
        self._stream_ordering = stream_ordering
        self._backend_owner = backend_owner
        self._backend_owner_object_id = (
            id(backend_owner) if backend_owner is not None else None
        )
        self._backend_owner_type = (
            f"{type(backend_owner).__module__}.{type(backend_owner).__qualname__}"
            if backend_owner is not None
            else "none"
        )
        self._backend_owner_prepared_identity_digest = identity.identity_digest
        self._backend_owner_seal = self._issue_backend_owner_seal()
        self._backend_owner_factory_invocation_count = 1
        self._backend_owner_generation = 1 if backend_owner is not None else 0
        self._backend_owner_replaced_during_open_lifetime = False
        self._backend_owner_metadata_snapshot: dict[str, object] | None = None
        self._prepare_elapsed_seconds = float(prepare_elapsed_seconds)
        self._max_event_rows = max_event_rows
        self._query_elapsed_seconds: list[float] = []
        self._column_rebind_count = 0
        self._first_query_input_content_revalidated = False
        self._validated_query_input_counts: list[int] = []
        self._active_producer_batch = None
        self._grouped_device_private_workspace = None
        self._grouped_device_private_workspace_metadata_snapshot = None
        self._closed = False
        self._invalid_reason: str | None = None

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def identity(self) -> ActionPreparedIdentity:
        return self._identity

    @property
    def query_count(self) -> int:
        return len(self._query_elapsed_seconds)

    def execute_columns(
        self,
        event_columns: Mapping[str, object],
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryResult:
        self._require_query_contract(extents, parameters, stream_ordering)
        if self._active_producer_batch is not None:
            _fail(
                "producer_owned_batch_still_active",
                "prepared",
                "consume or invalidate the active producer batch first",
            )
        lowered = self._planned.lowered
        if lowered.backend != "numba":
            _fail(
                "prepared_column_backend_unsupported",
                "lowered.backend",
                lowered.backend,
            )
        rebound = rebind_lowered_action_event_columns(
            lowered,
            event_columns,
            max_row_count=self._max_event_rows,
        )
        self._column_rebind_count += 1
        started = time.perf_counter()
        payload = _execute_numba_columns(
            rebound,
            event_columns,
            self._parameters,
            self._extents,
        )
        return self._record_query(payload, time.perf_counter() - started)

    def execute_device_columns(
        self,
        event_columns: Mapping[str, object],
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryResult:
        """Execute a private compiler-owned, device-resident event batch."""

        self._require_query_contract(extents, parameters, stream_ordering)
        if self._active_producer_batch is not None:
            _fail(
                "producer_owned_batch_still_active",
                "prepared",
                "consume or invalidate the active producer batch first",
            )
        lowered = self._planned.lowered
        if lowered.backend != "numba" or self._max_event_rows is None:
            _fail(
                "prepared_device_column_backend_unsupported",
                "lowered",
                lowered.template_kind,
            )
        prepared = None
        result = None
        started = time.perf_counter()
        try:
            prepared = prepare_bound_numba_action_device_columns(
                lowered,
                event_columns,
                parameters,
                max_row_count=self._max_event_rows,
            )
            from .action_numba_continuation import (
                execute_numba_grouped_i64x2_count_sum,
            )

            result = execute_numba_grouped_i64x2_count_sum(prepared)
            payload = result.to_host_reductions()
            certificate = dict(prepared.device_certificate_metadata or {})
        finally:
            if result is not None:
                result.close()
            if prepared is not None:
                prepared.close()
        self._column_rebind_count += 1
        return self._record_query(
            payload,
            time.perf_counter() - started,
            event_batch_certificate=certificate,
        )

    def begin_producer_owned_device_batch(self, *, capacity: int):
        """Open one compiler-allocated device producer write lease."""

        self._require_open()
        lowered = self._planned.lowered
        trace = lowered.compiler_execution_trace
        if (
            lowered.backend != "numba"
            or lowered.template_kind != "grouped_i64x2_count_sum"
            or self._max_event_rows is None
            or not isinstance(trace, Mapping)
            or trace.get("producer_event_region")
            != "compiler_owned_device_write_lease.v1"
        ):
            _fail(
                "producer_owned_device_region_plan_required",
                "prepared",
                f"{lowered.backend}:{lowered.template_kind}",
            )
        if self._active_producer_batch is not None:
            _fail(
                "producer_owned_batch_already_active",
                "prepared",
                "one producer batch must be consumed before another begins",
            )
        if (
            not isinstance(capacity, int)
            or isinstance(capacity, bool)
            or capacity < 0
            or capacity > self._max_event_rows
        ):
            _fail(
                "producer_owned_batch_capacity_invalid",
                "capacity",
                f"capacity={capacity}; max_event_rows={self._max_event_rows}",
            )
        try:
            from numba import cuda  # type: ignore
            import numpy as np
            from .action_host_continuation import (
                CompilerOwnedUnorderedI64x2DeviceBatch,
            )
            from .action_numba_continuation import (
                PreparedGroupedI64x2DeviceWorkspace,
            )

            allocation_started = time.perf_counter()
            workspace = self._grouped_device_private_workspace
            if workspace is None:
                workspace = PreparedGroupedI64x2DeviceWorkspace(
                    owner_identity_digest=self.identity.identity_digest,
                    max_row_count=int(self._max_event_rows),
                )
                self._grouped_device_private_workspace = workspace
            workspace.begin_query(
                owner_identity_digest=self.identity.identity_digest,
                query_ordinal=self.query_count,
            )
            allocated_capacity = max(1, capacity)
            group_length_device = cuda.device_array(
                allocated_capacity, dtype=np.int64
            )
            label_a_device = cuda.device_array(
                allocated_capacity, dtype=np.int64
            )
            label_b_device = cuda.device_array(
                allocated_capacity, dtype=np.int64
            )
            counters_device = cuda.to_device(np.zeros(3, dtype=np.int64))
            overflow_device = cuda.to_device(np.zeros(1, dtype=np.int64))
            allocation_seconds = time.perf_counter() - allocation_started
            batch = CompilerOwnedUnorderedI64x2DeviceBatch(
                owner_identity_digest=self.identity.identity_digest,
                batch_ordinal=self.query_count,
                capacity=capacity,
                group_length_device=group_length_device,
                label_a_device=label_a_device,
                label_b_device=label_b_device,
                counters_device=counters_device,
                overflow_device=overflow_device,
                completion_residency="device",
                producer_workspace_allocation_seconds=allocation_seconds,
                private_workspace=workspace,
            )
        except ActionPreparedError:
            workspace = self._grouped_device_private_workspace
            if workspace is not None:
                workspace.abort_query(
                    owner_identity_digest=self.identity.identity_digest,
                    query_ordinal=self.query_count,
                )
            raise
        except Exception as exc:  # pragma: no cover - runtime specific.
            workspace = self._grouped_device_private_workspace
            if workspace is not None:
                workspace.abort_query(
                    owner_identity_digest=self.identity.identity_digest,
                    query_ordinal=self.query_count,
                )
            _fail(
                "producer_owned_batch_allocation_failed",
                "prepared",
                str(exc),
            )
        self._active_producer_batch = batch
        return batch

    def execute_producer_owned_device_batch(
        self,
        batch,
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryResult:
        """Consume one completion snapshot through the existing device reducer."""

        self._require_query_contract(extents, parameters, stream_ordering)
        from .action_host_continuation import (
            CompilerOwnedUnorderedI64x2DeviceBatch,
        )

        if (
            type(batch) is not CompilerOwnedUnorderedI64x2DeviceBatch
            or batch is not self._active_producer_batch
        ):
            _fail(
                "producer_owned_batch_substitution",
                "batch",
                "batch is not the active compiler-owned producer allocation",
            )
        prepared = None
        result = None
        started = time.perf_counter()
        snapshot_bind_seconds = 0.0
        order_prepare_seconds = 0.0
        reducer_launch_seconds = 0.0
        result_download_projection_seconds = 0.0
        certificate_assembly_seconds = 0.0
        resource_close_seconds = 0.0
        workspace = self._grouped_device_private_workspace
        workspace_generation_digest: str | None = None
        query_ordinal = self.query_count
        execution_failed = False
        try:
            phase_started = time.perf_counter()
            snapshot_columns, producer_receipt = batch._consume_device_snapshot(
                owner_identity_digest=self.identity.identity_digest,
                batch_ordinal=self.query_count,
            )
            snapshot_bind_seconds = time.perf_counter() - phase_started
            workspace_generation_digest = producer_receipt.get(
                "workspace_generation_digest"
            )
            if (
                workspace is None
                or not isinstance(workspace_generation_digest, str)
            ):
                _fail(
                    "prepared_private_workspace_generation_missing",
                    "producer_receipt.workspace_generation_digest",
                    repr(workspace_generation_digest),
                )
            phase_started = time.perf_counter()
            prepared = prepare_bound_numba_action_compiler_snapshot(
                self._planned.lowered,
                snapshot_columns,
                parameters,
                max_row_count=int(self._max_event_rows or 0),
                private_workspace=workspace,
                workspace_generation_digest=workspace_generation_digest,
            )
            order_prepare_seconds = time.perf_counter() - phase_started
            from .action_numba_continuation import (
                execute_numba_grouped_i64x2_count_sum,
            )

            phase_started = time.perf_counter()
            result = execute_numba_grouped_i64x2_count_sum(prepared)
            reducer_launch_seconds = time.perf_counter() - phase_started
            reducer_execution_timing = result.to_metadata().get(
                "observation_timing_seconds"
            )
            phase_started = time.perf_counter()
            payload = result.to_host_reductions()
            result_download_projection_seconds = (
                time.perf_counter() - phase_started
            )
            phase_started = time.perf_counter()
            reducer_certificate = dict(
                prepared.device_certificate_metadata or {}
            )
            certificate = {
                **producer_receipt,
                **reducer_certificate,
                "contract": (
                    "rtdl.producer_owned_order_indexed_device_batch.v1"
                ),
                "binding_kind": (
                    "compiler_preallocated_single_consume_device_batch"
                ),
                "source_residency": "device",
                "completion_snapshot_residency": "device",
                "compiler_generated_logical_key": True,
                "full_typed_payload_and_order_bound": True,
                "duplicate_logical_keys_rejected": True,
                "caller_owned_device_columns_retained": False,
                "consumer_reads_completion_host_snapshot": False,
                "consumer_reads_completion_device_snapshot": True,
                "device_storage_post_completion_mutation_can_affect_consumer": False,
                "python_event_rows_materialized": False,
                "sorted_payload_permutation_used": False,
                "order_indexed_checked_scan_used": True,
                "host_grouped_scan_used": False,
                "new_native_symbol_added": False,
                "reducer_execution_observation_timing_seconds": (
                    reducer_execution_timing
                ),
            }
            certificate_assembly_seconds = time.perf_counter() - phase_started
        except BaseException:
            execution_failed = True
            try:
                batch.invalidate()
            finally:
                self._active_producer_batch = None
                self._invalid_reason = (
                    "producer-owned device batch execution failed"
                )
            raise
        finally:
            close_started = time.perf_counter()
            if result is not None:
                result.close()
            if prepared is not None:
                prepared.close()
            resource_close_seconds = time.perf_counter() - close_started
            if execution_failed:
                if workspace is not None:
                    workspace.abort_query(
                        owner_identity_digest=self.identity.identity_digest,
                        query_ordinal=query_ordinal,
                    )
                self.close()
        assert workspace is not None
        assert workspace_generation_digest is not None
        workspace.finish_query(
            owner_identity_digest=self.identity.identity_digest,
            query_ordinal=query_ordinal,
            generation_digest=workspace_generation_digest,
        )
        consumer_phase_timing_seconds = {
            "producer_workspace_allocation_seconds": float(
                producer_receipt.get(
                    "producer_workspace_allocation_seconds",
                    0.0,
                )
            ),
            "completion_snapshot_seconds": float(
                producer_receipt.get(
                    "completion_device_to_device_seconds",
                    0.0,
                )
            ),
            "snapshot_bind_and_receipt_seconds": float(snapshot_bind_seconds),
            "order_prepare_seconds": float(order_prepare_seconds),
            "reducer_launch_seconds": float(reducer_launch_seconds),
            "result_download_and_core_projection_seconds": float(
                result_download_projection_seconds
            ),
            "certificate_assembly_seconds": float(
                certificate_assembly_seconds
            ),
            "resource_close_seconds": float(resource_close_seconds),
            "prepared_query_elapsed_seconds": float(
                time.perf_counter() - started
            ),
        }
        certificate = {
            **certificate,
            "observation_only_phase_trace": True,
            "route_or_synchronization_changed_by_trace": False,
            "consumer_phase_timing_seconds": consumer_phase_timing_seconds,
        }
        self._active_producer_batch = None
        self._column_rebind_count += 1
        return self._record_query(
            payload,
            time.perf_counter() - started,
            event_batch_certificate=certificate,
        )

    def execute_queries(
        self,
        query_input,
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryResult:
        validate_planned_lowered_action(self._planned)
        self._require_query_contract(extents, parameters, stream_ordering)
        self._validate_actual_query_count(query_input)
        self._revalidate_compiler_bound_first_query_input(query_input)
        started = time.perf_counter()
        if self._backend_owner is None:
            _fail(
                "prepared_index_owner_required",
                "backend_owner",
                self._planned.lowered.template_kind,
            )
        template = self._planned.lowered.template_kind
        if template in {
            "certified_nearest_state_3d",
            "certified_nearest_state_3d_optix_traversal",
            "cell_mbr_exact_witness_3d_optix_traversal",
        } or (
            template == "cpu_reference_interpreter"
            and getattr(self._backend_owner, "prepared_producer_kind", None)
            == ActionProducerKind.CERTIFIED_NEAREST_STATE_3D.value
        ):
            payload = self._backend_owner.run(query_input)
        elif template == "point_candidate_bounded_selection_3d":
            payload = self._backend_owner.run(
                query_input,
                self._parameters,
                extents=self._extents,
            )
            # Physical templates may retain their legacy row representation,
            # but the prepared Action contract exposes the IR-named columns in
            # every placement. Applications therefore do not branch on the
            # compiler's fused-versus-continuation choice.
            rows = tuple(payload.get("rows", ()))
            program = self._planned.lowered.program
            import numpy as np

            columns = {
                program.scope_output_field: np.asarray(
                    [row[0] for row in rows], dtype=np.uint32
                ),
                program.item_output_field: np.asarray(
                    [row[1] for row in rows], dtype=np.uint32
                ),
                program.distance_output_field: np.asarray(
                    [row[2] for row in rows], dtype=np.float32
                ),
            }
            payload = dict(payload)
            payload["columns"] = columns
            payload["metadata"] = dict(payload.get("metadata", {})) | {
                "placement_invariant_column_contract": True,
                "column_fields_derived_from_verified_ir": True,
            }
        elif template == "candidate_pruned_exact_bounded_selection_3d":
            payload = self._backend_owner.run(
                query_input,
                self._parameters,
            )
        elif template == "prepared_ranked_distance_window_qk_3d":
            program = self._planned.lowered.program
            view = self._backend_owner.run_ranked_distance_window_raw(
                query_input,
                minimum_distance=float(self._parameters[program.minimum_parameter]),
                radius=float(self._parameters[program.maximum_parameter]),
                k_max=int(self._parameters[program.limit_parameter]),
                minimum_boundary=program.minimum_boundary,
                radius_boundary=program.maximum_boundary,
            )
            try:
                native_columns = view.to_numpy_columns(copy=True)
            finally:
                view.close()
            import numpy as np

            try:
                query_ids = np.asarray(native_columns["query_id"], dtype=np.uint32)
                neighbor_ids = np.asarray(native_columns["neighbor_id"], dtype=np.uint32)
                distances = np.asarray(native_columns["distance"], dtype=np.float32)
                ranks = np.asarray(native_columns["neighbor_rank"], dtype=np.uint32)
            except (KeyError, TypeError, ValueError, OverflowError) as exc:
                _fail(
                    "ranked_window_result_shape_invalid",
                    "backend_owner.result",
                    f"required ranked-result column is malformed: {exc}",
                )
            column_shapes = {
                "query_id": query_ids.shape,
                "neighbor_id": neighbor_ids.shape,
                "distance": distances.shape,
                "neighbor_rank": ranks.shape,
            }
            if any(array.ndim != 1 for array in (query_ids, neighbor_ids, distances, ranks)) or len(
                set(column_shapes.values())
            ) != 1:
                _fail(
                    "ranked_window_result_shape_invalid",
                    "backend_owner.result",
                    "query, neighbor, distance, and rank columns must be equal-length 1-D arrays",
                )
            if ranks.size:
                if bool(np.any(query_ids[1:] < query_ids[:-1])):
                    _fail(
                        "ranked_window_query_group_order_invalid",
                        "backend_owner.result.query_id",
                        "query groups must be contiguous and nondecreasing",
                    )
                group_start = np.empty(ranks.shape, dtype=np.bool_)
                group_start[0] = True
                group_start[1:] = query_ids[1:] != query_ids[:-1]
                starts = np.maximum.accumulate(
                    np.where(group_start, np.arange(ranks.size, dtype=np.uint32), 0)
                )
                expected_ranks = np.arange(ranks.size, dtype=np.uint32) - starts + 1
                if bool(np.any(ranks != expected_ranks)) or bool(
                    np.any(ranks > int(self._parameters[program.limit_parameter]))
                ):
                    _fail(
                        "ranked_window_rank_certificate_invalid",
                        "backend_owner.result.neighbor_rank",
                        "each query must expose contiguous ranks 1..K",
                    )
            payload = {
                "columns": {
                    program.scope_output_field: query_ids,
                    program.item_output_field: neighbor_ids,
                    program.distance_output_field: distances,
                },
                "metadata": {
                    "contract": "rtdl.prepared_ranked_distance_window_qk_result.v1",
                    "row_count": int(native_columns["query_id"].shape[0]),
                    "bounded_qk_output": True,
                    "rank_certificate_validated": True,
                    "unbounded_candidate_relation_materialized": False,
                    "application_selected_backend": False,
                },
            }
        elif template == "keyed_i64_sum_3d":
            payload = self._backend_owner.run(query_input)
        elif template in {
            "aabb_filter_bounded_emit_2d",
            "aabb_filter_bounded_emit_reference_2d",
        }:
            payload = self._backend_owner.run(query_input, self._parameters)
        else:
            _fail("prepared_query_template_unsupported", "template", template)
        return self._record_query(payload, time.perf_counter() - started)

    def prepare_query_batch(
        self,
        query_input,
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryBatch:
        """Prepare a query input without exposing the compiler-selected backend."""

        self._require_query_contract(extents, parameters, stream_ordering)
        template = self._planned.lowered.template_kind
        if (
            template != "keyed_i64_sum_3d"
            or self._backend_owner is None
            or not hasattr(self._backend_owner, "prepare_query")
        ):
            _fail("prepared_query_batch_unsupported", "template", template)
        started = time.perf_counter()
        native_owner = self._backend_owner.prepare_query(query_input)
        try:
            metadata_function = getattr(
                type(native_owner),
                "compiler_native_resource_binding_metadata",
                None,
            )
            if metadata_function is None:
                _fail(
                    "prepared_query_native_owner_metadata_required",
                    "prepared_query.native_owner",
                    type(native_owner).__name__,
                )
            native_metadata = metadata_function(native_owner)
            query_input_digest = (
                native_metadata.get("prepared_query_input_digest")
                if isinstance(native_metadata, Mapping)
                else None
            )
            if not isinstance(query_input_digest, str) or not _is_sha256_digest(
                query_input_digest
            ):
                _fail(
                    "prepared_query_snapshot_digest_required",
                    "prepared_query.native_owner",
                    "native owner must bind the exact compiler-owned query snapshot",
                )
            return PreparedActionQueryBatch(
                native_owner,
                compatibility_digest=_prepared_query_compatibility_digest(self.identity),
                query_input_digest=query_input_digest,
                query_count=(
                    int(native_owner.ray_count)
                    if hasattr(native_owner, "ray_count")
                    else None
                ),
                prepare_elapsed_seconds=time.perf_counter() - started,
            )
        except Exception:
            if hasattr(native_owner, "close"):
                type(native_owner).close(native_owner)
            raise

    def execute_prepared_query_batch(
        self,
        prepared_query: PreparedActionQueryBatch,
        *,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None = None,
    ) -> PreparedActionQueryResult:
        """Execute a compiler-owned prepared query against this compatible index."""

        self._require_query_contract(extents, parameters, stream_ordering)
        if type(prepared_query) is not PreparedActionQueryBatch:
            _fail(
                "prepared_query_batch_exact_type_required",
                "prepared_query",
                type(prepared_query).__name__,
            )
        prepared_query.validate_open()
        expected = _prepared_query_compatibility_digest(self.identity)
        if prepared_query.compatibility_digest != expected:
            _fail(
                "prepared_query_batch_incompatible",
                "prepared_query.compatibility_digest",
                "query batch was prepared for a different Action plan",
            )
        template = self._planned.lowered.template_kind
        if (
            template != "keyed_i64_sum_3d"
            or self._backend_owner is None
            or not hasattr(self._backend_owner, "run_prepared_query")
        ):
            _fail("prepared_query_batch_unsupported", "template", template)
        started = time.perf_counter()
        payload = self._backend_owner.run_prepared_query(
            prepared_query.native_owner_for_execution()
        )
        prepared_query.record_execution()
        return self._record_query(payload, time.perf_counter() - started)

    def invalidate(self, reason: str) -> None:
        if not isinstance(reason, str) or not reason.strip():
            _fail("invalidation_reason_required", "reason", repr(reason))
        if self._closed:
            return
        self._invalid_reason = reason.strip()
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        active_batch = self._active_producer_batch
        if active_batch is not None:
            active_batch.invalidate()
            self._active_producer_batch = None
        self._validate_backend_owner_binding()
        owner = self._backend_owner
        if owner is not None and hasattr(owner, "to_metadata"):
            snapshot = owner.to_metadata()
            if not isinstance(snapshot, Mapping):
                _fail(
                    "prepared_backend_owner_metadata_invalid",
                    "backend_owner.to_metadata",
                    type(snapshot).__name__,
                )
            self._backend_owner_metadata_snapshot = dict(snapshot)
        if owner is not None and hasattr(owner, "close"):
            owner.close()
        self._backend_owner = None
        workspace = self._grouped_device_private_workspace
        if workspace is not None:
            self._grouped_device_private_workspace_metadata_snapshot = (
                workspace.to_metadata()
            )
            workspace.close()
            self._grouped_device_private_workspace = None
        self._closed = True

    def timing_metadata(self) -> dict[str, object]:
        first = self._query_elapsed_seconds[0] if self._query_elapsed_seconds else None
        repeats = self._query_elapsed_seconds[1:]
        return {
            "contract": "rtdl.prepared_action_timing.private_candidate.v1",
            "prepare_seconds": self._prepare_elapsed_seconds,
            "first_query_seconds": first,
            "repeated_query_seconds": list(repeats),
            "query_count": self.query_count,
            "warm_only_headline_authorized": False,
            "runtime_speedup_claimed": False,
        }

    def to_metadata(self) -> dict[str, object]:
        self._validate_identity()
        backend_owner_metadata = self._backend_owner_metadata_snapshot
        if backend_owner_metadata is None and self._backend_owner is not None:
            to_metadata = getattr(self._backend_owner, "to_metadata", None)
            if callable(to_metadata):
                value = to_metadata()
                if not isinstance(value, Mapping):
                    _fail(
                        "prepared_backend_owner_metadata_invalid",
                        "backend_owner.to_metadata",
                        type(value).__name__,
                    )
                backend_owner_metadata = dict(value)
        return {
            "contract": ACTION_PREPARED_VERSION,
            "identity": self.identity.to_metadata(),
            "backend_owner_metadata": backend_owner_metadata,
            "backend_owner_metadata_digest": (
                _digest(backend_owner_metadata, "backend_owner_metadata")
                if backend_owner_metadata is not None
                else "none"
            ),
            "resource_ownership": {
                "module": "compiler_owned_for_prepared_lifetime",
                "index": (
                    "compiler_owned_for_prepared_lifetime"
                    if self.identity.index_owner_digest != "none"
                    else "not_applicable"
                ),
                "state": "compiler_owned_per_query",
                "query_result_closed_before_next_query": True,
            },
            "backend_owner_lifecycle": {
                "factory_invocation_count": self._backend_owner_factory_invocation_count,
                "owner_generation": self._backend_owner_generation,
                "owner_replaced_during_open_lifetime": self._backend_owner_replaced_during_open_lifetime,
                "query_count": self.query_count,
                "compiler_authored": True,
            },
            "event_batch_lifecycle": {
                "row_count_mode": self.identity.event_batch_row_count_mode,
                "max_event_rows": self.identity.max_event_rows,
                "column_rebind_count": self._column_rebind_count,
                "schema_reverified_per_batch": True,
                "ordering_reverified_per_batch": True,
                "duplicate_logical_keys_rejected_per_batch": True,
                "capacity_reverified_per_batch": self._max_event_rows is not None,
                "compiler_authored": True,
                "producer_owned_batch_active": (
                    self._active_producer_batch is not None
                ),
                "prepared_private_workspace": (
                    self._grouped_device_private_workspace.to_metadata()
                    if self._grouped_device_private_workspace is not None
                    else self._grouped_device_private_workspace_metadata_snapshot
                ),
            },
            "backend_runtime_lifecycle": _backend_runtime_lifecycle_metadata(
                self._planned.lowered
            ),
            "runtime_input_binding": {
                "prepared_input_full_content_revalidated_before_owner_prepare": (
                    self._planned.compiler_prepared_input_digest_kind
                    == _PACKED_POINT_FULL_DIGEST_KIND
                ),
                "first_query_full_content_revalidated": (
                    self._first_query_input_content_revalidated
                ),
                "first_query_binding_only": (
                    self._planned.compiler_first_query_input_digest is not None
                ),
                "repeated_query_batches_globally_content_bound": False,
                "actual_query_count_derived_before_native_allocation": bool(
                    self._validated_query_input_counts
                ),
                "validated_query_input_counts": list(
                    self._validated_query_input_counts
                ),
            },
            "timing": self.timing_metadata(),
            "closed": self._closed,
            "invalidated": self._invalid_reason is not None,
            "invalidation_reason": self._invalid_reason,
            "application_selected_backend": False,
            "raw_callback_accepted": False,
            "user_kernel_accepted": False,
            "arbitrary_ptx_accepted": False,
        }

    def __enter__(self) -> PreparedActionExecution:
        self._require_open()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def _record_query(
        self,
        payload: object,
        elapsed: float,
        *,
        event_batch_certificate: Mapping[str, object] | None = None,
    ) -> PreparedActionQueryResult:
        ordinal = len(self._query_elapsed_seconds)
        self._query_elapsed_seconds.append(float(elapsed))
        return PreparedActionQueryResult(
            payload=payload,
            query_ordinal=ordinal,
            timing_regime="first_query" if ordinal == 0 else "repeated_query",
            elapsed_seconds=float(elapsed),
            prepared_identity_digest=self.identity.identity_digest,
            backend_owner_generation=self._backend_owner_generation,
            event_batch_certificate=event_batch_certificate,
        )

    def _revalidate_compiler_bound_first_query_input(self, query_input) -> None:
        planned = self._planned
        expected = planned.compiler_first_query_input_digest
        if expected is None:
            return
        if self.query_count != 0:
            return
        if (
            planned._compiler_first_query_input_object_id is None
            or planned._compiler_first_query_input_object_id != id(query_input)
            or planned._compiler_first_query_input_ref is not query_input
        ):
            _fail(
                "compiler_first_query_input_binding_mismatch",
                "query_input",
                "first query input is not the compiler-bound object",
            )
        if planned.compiler_first_query_input_digest_kind != _PACKED_POINT_FULL_DIGEST_KIND:
            _fail(
                "compiler_first_query_input_digest_kind_unsupported",
                "planned.compiler_first_query_input_digest_kind",
                repr(planned.compiler_first_query_input_digest_kind),
            )
        actual = _packed_point_runtime_identity(query_input)
        if actual != expected:
            _fail(
                "compiler_first_query_input_content_drift",
                "query_input",
                "compiler-bound first query packed content changed after planning",
            )
        self._first_query_input_content_revalidated = True

    def _validate_actual_query_count(self, query_input) -> None:
        """Bind the caller-visible query object to the planned query extent."""

        template = self._planned.lowered.template_kind
        certified_nearest = template in {
            "certified_nearest_state_3d",
            "certified_nearest_state_3d_optix_traversal",
            "cell_mbr_exact_witness_3d_optix_traversal",
        } or (
            template == "cpu_reference_interpreter"
            and self._planned.lowered.producer_kind
            is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
        )
        if certified_nearest:
            import numpy as np

            matrix = np.asarray(query_input)
            if matrix.ndim != 2 or matrix.shape[1:] != (3,):
                _fail(
                    "prepared_query_input_shape_invalid",
                    "query_input",
                    str(matrix.shape),
                )
            actual = int(matrix.shape[0])
        elif template in {
            "point_candidate_bounded_selection_3d",
            "prepared_ranked_distance_window_qk_3d",
            "candidate_pruned_exact_bounded_selection_3d",
        }:
            count = getattr(query_input, "count", None)
            if not isinstance(count, int) or isinstance(count, bool):
                _fail(
                    "prepared_query_input_count_unavailable",
                    "query_input.count",
                    repr(count),
                )
            actual = count
        else:
            return
        if actual <= 0:
            _fail(
                "prepared_query_input_empty",
                "query_input",
                str(actual),
            )
        if actual > UINT32_MAX:
            _fail(
                "prepared_query_input_u32_overflow",
                "query_input",
                str(actual),
            )
        expected = self._extents.get(ExtentKind.QUERY_COUNT.value)
        if expected is None:
            _fail(
                "prepared_query_extent_required",
                "extents.query_count",
                "missing",
            )
        if actual != expected:
            _fail(
                "prepared_query_input_extent_mismatch",
                "query_input",
                f"planned query_count={expected}; actual rows={actual}",
            )
        self._validated_query_input_counts.append(actual)

    def _require_query_contract(
        self,
        extents: Mapping[ExtentKind | str, int],
        parameters: Mapping[str, object],
        stream_ordering: ActionPreparedStreamOrdering | None,
    ) -> None:
        self._require_open()
        if _normalize_extents(extents) != self._extents:
            _fail(
                "prepared_extents_invalidated",
                "extents",
                "query extents differ from the prepared identity",
            )
        if _digest(parameters, "parameters") != self.identity.parameters_digest:
            _fail(
                "prepared_parameters_invalidated",
                "parameters",
                "query parameters differ from the prepared identity",
            )
        actual_stream = stream_ordering or self._stream_ordering
        if actual_stream is not self._stream_ordering:
            _fail(
                "prepared_stream_ordering_invalidated",
                "stream_ordering",
                actual_stream.value,
            )

    def _require_open(self) -> None:
        # Invalidation deliberately closes the physical owner, but it remains a
        # distinct persistent logical state.  Report that state before the
        # generic use-after-close condition so callers cannot lose the reason
        # the prepared execution was invalidated.
        if self._invalid_reason is not None:
            _fail(
                "prepared_action_invalidated",
                "prepared",
                self._invalid_reason,
            )
        if self._closed:
            _fail("prepared_action_closed", "prepared", "prepared owner is closed")
        self._validate_identity()
        self._validate_backend_owner_binding()

    def _validate_identity(self) -> None:
        identity = self._identity
        if not isinstance(identity, ActionPreparedIdentity):
            _fail(
                "prepared_identity_invalid",
                "prepared.identity",
                type(identity).__name__,
            )
        metadata = identity.to_metadata()
        payload = dict(metadata)
        payload.pop("contract", None)
        claimed_digest = payload.pop("identity_digest", None)
        if claimed_digest != _digest(payload, "prepared_identity"):
            _fail(
                "prepared_identity_digest_invalid",
                "prepared.identity.identity_digest",
                "identity fields differ from the issued digest",
            )
        expected_seal = hmac.new(
            _PREPARED_IDENTITY_SEAL_SECRET,
            json.dumps(
                metadata,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(self._identity_seal, expected_seal):
            _fail(
                "prepared_identity_seal_invalid",
                "prepared.identity",
                "prepared identity was replaced after compiler issuance",
            )

    def _issue_backend_owner_seal(self) -> str:
        payload = {
            "prepared_identity_digest": self._backend_owner_prepared_identity_digest,
            "backend_owner_object_id": self._backend_owner_object_id,
            "backend_owner_type": self._backend_owner_type,
        }
        return hmac.new(
            _PREPARED_IDENTITY_SEAL_SECRET,
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).hexdigest()

    def _validate_backend_owner_binding(self) -> None:
        current_object_id = (
            id(self._backend_owner) if self._backend_owner is not None else None
        )
        current_type = (
            f"{type(self._backend_owner).__module__}.{type(self._backend_owner).__qualname__}"
            if self._backend_owner is not None
            else "none"
        )
        if (
            current_object_id != self._backend_owner_object_id
            or current_type != self._backend_owner_type
            or not hmac.compare_digest(
                self._backend_owner_seal, self._issue_backend_owner_seal()
            )
        ):
            _fail(
                "prepared_backend_owner_binding_invalid",
                "prepared.backend_owner",
                "compiler-created backend owner changed during the prepared lifetime",
            )


def _backend_runtime_lifecycle_metadata(lowered: LoweredAction) -> dict[str, object]:
    if lowered.backend == "numba" and lowered.template_kind == "grouped_i64x2_count_sum":
        from .action_numba_continuation import (
            grouped_i64x2_count_sum_kernel_lifecycle_metadata,
        )

        return grouped_i64x2_count_sum_kernel_lifecycle_metadata()
    return {
        "contract": "rtdl.backend_runtime_lifecycle.private_candidate.v1",
        "available": False,
        "reason": "selected backend/template has no runtime lifecycle probe",
        "compiler_owned": True,
    }


def _prepared_query_compatibility_digest(identity: ActionPreparedIdentity) -> str:
    """Bind a reusable query to every plan fact except the prepared index itself."""

    return _digest(
        {
            "semantic_digest": identity.semantic_digest,
            "source_digest": identity.source_digest,
            "producer_kind": identity.producer_kind,
            "producer_certificate_digest": identity.producer_certificate_digest,
            "producer_schema_digest": identity.producer_schema_digest,
            "target_profile_digest": identity.target_profile_digest,
            "physical_plan_digest": identity.physical_plan_digest,
            "selected_backend": identity.selected_backend,
            "selected_placement": identity.selected_placement,
            "selected_template": identity.selected_template,
            "consumer_composition_digest": identity.consumer_composition_digest,
            "consumer_composition_kind": identity.consumer_composition_kind,
            "native_library_identity_digest": identity.native_library_identity_digest,
            "native_library_object_token": identity.native_library_object_token,
            "module_owner_digest": identity.module_owner_digest,
            "state_owner_digest": identity.state_owner_digest,
            "extents_digest": identity.extents_digest,
            "parameters_digest": identity.parameters_digest,
            "stream_ordering": identity.stream_ordering,
        },
        "prepared_query_compatibility",
    )


def _packed_point_runtime_identity(packed) -> str:
    """Recompute the registry's full packed identity at the use boundary."""

    # Imported lazily to keep the generic prepared layer independent unless a
    # trusted point-registry plan explicitly requests this closed digest kind.
    from .action_physical_registry import _packed_point_identity

    try:
        return _packed_point_identity(packed)
    except (TypeError, ValueError, OverflowError) as exc:
        _fail(
            "compiler_bound_packed_point_input_invalid",
            "packed_input",
            str(exc),
        )


def _packed_point_runtime_sample_fingerprint(packed) -> str:
    """Recompute the registry's bounded sample at the prepare boundary."""

    from .action_physical_registry import _packed_point_sample_fingerprint

    try:
        return _packed_point_sample_fingerprint(packed)
    except (TypeError, ValueError, OverflowError) as exc:
        _fail(
            "compiler_bound_packed_point_input_invalid",
            "packed_input",
            str(exc),
        )


def _packed_point_runtime_storage_binding(packed) -> dict[str, object]:
    """Recompute exact native storage identity without scanning its payload."""

    from .action_physical_registry import _packed_point_storage_binding

    try:
        return _packed_point_storage_binding(packed)
    except (TypeError, ValueError, OverflowError) as exc:
        _fail(
            "compiler_bound_packed_point_input_invalid",
            "packed_input",
            str(exc),
        )


def prepare_consumed_triangle_grouped_i64_action_execution(
    planned: PlannedLoweredAction,
    *,
    triangles,
    primitive_group_ids,
    primitive_values,
    primitive_includes,
    group_count: int,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
    stream_ordering: ActionPreparedStreamOrdering = (
        ActionPreparedStreamOrdering.SYNCHRONOUS_DEFAULT_STREAM
    ),
) -> PreparedActionExecution:
    """Prepare and atomically transfer one sealed grouped backend owner.

    All raw payload validation and backend upload remain inside the ordinary
    prepare denominator. Once the synchronous backend resource exists, its
    fresh generation and structural seal replace repeated O(payload-bytes)
    host hashing in persistent prepared identity.
    """

    if not isinstance(planned, PlannedLoweredAction):
        _fail("planned_lowered_action_required", "planned", type(planned).__name__)
    validate_planned_lowered_action(planned)
    lowered = planned.lowered
    if lowered.backend != "optix" or lowered.template_kind != "keyed_i64_sum_3d":
        _fail(
            "consumed_triangle_grouped_i64_plan_required",
            "planned.lowered",
            f"{lowered.backend}:{lowered.template_kind}",
        )
    if (
        stream_ordering
        is not ActionPreparedStreamOrdering.SYNCHRONOUS_DEFAULT_STREAM
    ):
        _fail(
            "consumed_triangle_grouped_i64_stream_unsupported",
            "stream_ordering",
            stream_ordering.value,
        )
    from .action_optix_lowering import (
        prepare_consumed_optix_action_keyed_i64_sum_3d,
    )

    capability = None
    payload = None
    try:
        capability = prepare_consumed_optix_action_keyed_i64_sum_3d(
            lowered.program,
            triangles,
            primitive_group_ids=primitive_group_ids,
            primitive_values=primitive_values,
            primitive_includes=primitive_includes,
            group_count=group_count,
        )
        payload = ConsumedPreparedTriangleGroupedI64Payload3D(
            capability,
            lowered.program,
        )
        return prepare_action_execution(
            planned,
            extents=extents,
            parameters=parameters,
            prepared_input=payload,
            stream_ordering=stream_ordering,
        )
    except Exception:
        if payload is not None:
            payload.close()
        elif capability is not None:
            capability.close()
        raise


def prepare_action_execution(
    planned: PlannedLoweredAction,
    *,
    extents: Mapping[ExtentKind | str, int],
    parameters: Mapping[str, object],
    prepared_input=None,
    stream_ordering: ActionPreparedStreamOrdering = (
        ActionPreparedStreamOrdering.SYNCHRONOUS_DEFAULT_STREAM
    ),
    max_distance_bound: float | None = None,
    max_candidate_rows: int | None = None,
    max_event_rows: int | None = None,
) -> PreparedActionExecution:
    """Prepare one closed compiler-selected plan; no backend callback is accepted."""

    if not isinstance(planned, PlannedLoweredAction):
        _fail("planned_lowered_action_required", "planned", type(planned).__name__)
    validate_planned_lowered_action(planned)
    if not isinstance(stream_ordering, ActionPreparedStreamOrdering):
        _fail("stream_ordering_required", "stream_ordering", type(stream_ordering).__name__)
    normalized_extents = _normalize_extents(extents)
    parameters_digest = _digest(parameters, "parameters")
    lowered = planned.lowered
    composition = planned.consumer_composition
    if lowered.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D:
        if composition is None:
            _fail(
                "prepared_certified_nearest_composition_required",
                "planned.consumer_composition",
                "global witness execution must be explicitly composed by the compiler",
            )
        if (
            composition.kind
            is not ActionConsumerCompositionKind.CERTIFIED_NEAREST_TO_GLOBAL_ARGMAX_WITH_WITNESS
        ):
            _fail(
                "prepared_certified_nearest_consumer_mismatch",
                "planned.consumer_composition",
                composition.kind.value,
            )
        query_extent = normalized_extents.get(ExtentKind.QUERY_COUNT.value)
        validate_certified_nearest_global_argmax_composition(
            composition,
            spec=lowered.compiled.spec,
            action_source_digest=lowered.compiled.source_digest,
            producer_kind=lowered.producer_kind.value,
            producer_binding_digest=lowered.producer_binding_digest,
            selected_backend=lowered.backend,
            selected_placement=lowered.placement,
            selected_template=lowered.template_kind,
            template_identity_digest=action_template_identity_digest(
                lowered.program.to_metadata()
                if hasattr(lowered.program, "to_metadata")
                else {"template": lowered.template_kind}
            ),
            query_count=query_extent,
        )
    elif composition is not None:
        _fail(
            "prepared_consumer_composition_producer_mismatch",
            "planned.consumer_composition",
            lowered.producer_kind.value,
        )
    event_certificate = lowered.event_column_certificate
    if max_event_rows is not None:
        if not isinstance(max_event_rows, int) or isinstance(max_event_rows, bool) or max_event_rows < 0:
            _fail(
                "invalid_prepared_event_batch_capacity",
                "max_event_rows",
                repr(max_event_rows),
            )
        if lowered.backend != "numba" or event_certificate is None:
            _fail(
                "variable_prepared_event_batch_requires_numba_columns",
                "max_event_rows",
                lowered.template_kind,
            )
        if event_certificate.row_count > max_event_rows:
            _fail(
                "prepared_event_batch_capacity_too_small",
                "max_event_rows",
                f"initial rows={event_certificate.row_count}; capacity={max_event_rows}",
            )
    if planned.plan.selected_backend != lowered.backend:
        _fail("prepared_plan_backend_mismatch", "planned", lowered.backend)
    if planned.plan.selected_placement.value != lowered.placement:
        _fail("prepared_plan_placement_mismatch", "planned", lowered.placement)

    planned_native_identity = planned.compiler_native_library_identity
    planned_native_library = planned._compiler_native_library_ref
    if planned_native_identity is not None:
        if (
            planned_native_library is None
            or planned._compiler_native_library_object_id != id(planned_native_library)
        ):
            _fail(
                "prepared_native_library_object_binding_mismatch",
                "planned.compiler_native_library_identity",
                "the compiler-bound native library object is unavailable",
            )
        try:
            revalidated_native_identity = validate_native_library_identity(
                planned_native_library,
                planned_native_identity,
            )
        except (RuntimeError, TypeError, ValueError, OSError) as exc:
            _fail(
                "prepared_native_library_identity_drift",
                "planned.compiler_native_library_identity",
                str(exc),
            )
        planned_native_identity_metadata = revalidated_native_identity.to_metadata()
    else:
        if (
            planned._compiler_native_library_object_id is not None
            or planned_native_library is not None
        ):
            _fail(
                "prepared_native_library_binding_incomplete",
                "planned.compiler_native_library_identity",
                "identity, object ID, and strong reference must be present together",
            )
        planned_native_identity_metadata = None

    try:
        from .action_physical_registry import (
            validate_registered_point_prepare_contract,
        )

        max_distance_bound, runtime_native_library_identity = (
            validate_registered_point_prepare_contract(
                planned,
                parameters=parameters,
                max_distance_bound=max_distance_bound,
            )
        )
    except (RuntimeError, TypeError, ValueError) as exc:
        _fail(
            "registered_point_prepare_contract_invalid",
            "planned.lowered.compiler_execution_trace.physical_registry",
            str(exc),
        )

    started = time.perf_counter()
    certificate = lowered.event_column_certificate
    producer_schema_digest = (
        certificate.schema_digest
        if certificate is not None
        else _digest(lowered.compiled.spec.event_type.to_dict(), "event_schema")
    )
    target_digest = _digest(planned.target_profile.to_metadata(), "target_profile")
    plan_digest = _digest(planned.plan.to_dict(), "physical_plan")
    program_metadata = (
        lowered.program.to_metadata()
        if hasattr(lowered.program, "to_metadata")
        else {"template": lowered.template_kind}
    )
    composition_metadata = (
        composition.to_metadata() if composition is not None else None
    )
    module_digest = _digest(
        {
            "program": program_metadata,
            "consumer_composition": composition_metadata,
            "planned_native_library_identity": planned_native_identity_metadata,
            "planned_native_library_object_token": (
                str(id(planned_native_library))
                if planned_native_library is not None
                else "none"
            ),
            "runtime_native_library_identity": runtime_native_library_identity,
            "prepared_max_distance_bound_hex": (
                float(max_distance_bound).hex()
                if max_distance_bound is not None
                else None
            ),
        },
        "module_owner",
    )
    if planned.compiler_prepared_input_digest is not None:
        if (
            prepared_input is None
            or planned._compiler_prepared_input_object_id != id(prepared_input)
            or planned._compiler_prepared_input_ref is not prepared_input
        ):
            _fail(
                "compiler_prepared_input_binding_mismatch",
                "prepared_input",
                "prepared input is not the compiler-bound object",
            )
        digest_kind = planned.compiler_prepared_input_digest_kind
        if digest_kind == _PACKED_POINT_FULL_DIGEST_KIND:
            actual_digest = _packed_point_runtime_identity(prepared_input)
            if actual_digest != planned.compiler_prepared_input_digest:
                _fail(
                    "compiler_prepared_input_content_drift",
                    "prepared_input",
                    "compiler-bound packed content changed after planning",
                )
        elif digest_kind == _PACKED_POINT_SAMPLE_DIGEST_KIND:
            actual_digest = _packed_point_runtime_sample_fingerprint(prepared_input)
            if actual_digest != planned.compiler_prepared_input_digest:
                _fail(
                    "compiler_prepared_input_content_drift",
                    "prepared_input",
                    "compiler-bound packed sample or structure changed after planning",
                )
            trace = lowered.compiler_execution_trace
            registry = trace.get("physical_registry") if isinstance(trace, Mapping) else None
            expected_storage = (
                registry.get("prepared_search_storage_binding")
                if isinstance(registry, Mapping)
                else None
            )
            actual_storage = _packed_point_runtime_storage_binding(prepared_input)
            if not isinstance(expected_storage, Mapping) or (
                dict(expected_storage) != actual_storage
            ):
                _fail(
                    "compiler_prepared_input_storage_drift",
                    "prepared_input.records",
                    "compiler-bound packed storage object, type, or address changed",
                )
        elif digest_kind is not None:
            _fail(
                "compiler_prepared_input_digest_kind_unsupported",
                "planned.compiler_prepared_input_digest_kind",
                repr(digest_kind),
            )
        index_digest = planned.compiler_prepared_input_digest
    elif (
        planned.compiler_prepared_input_digest_kind is not None
        or planned._compiler_prepared_input_object_id is not None
        or planned._compiler_prepared_input_ref is not None
    ):
        _fail(
            "compiler_prepared_input_binding_incomplete",
            "planned.compiler_prepared_input_digest",
            "digest, digest kind, and object binding must be present together",
        )
    else:
        if isinstance(
            prepared_input,
            ConsumedPreparedTriangleGroupedI64Payload3D,
        ):
            prepared_input.validate_for_lowered(lowered)
        index_digest = (
            _digest(prepared_input, "index_owner")
            if prepared_input is not None
            else "none"
        )
    if planned.compiler_first_query_input_digest is None:
        if (
            planned.compiler_first_query_input_digest_kind is not None
            or planned._compiler_first_query_input_object_id is not None
            or planned._compiler_first_query_input_ref is not None
        ):
            _fail(
                "compiler_first_query_input_binding_incomplete",
                "planned.compiler_first_query_input_digest",
                "digest, digest kind, and object binding must be present together",
            )
    elif (
        planned.compiler_first_query_input_digest_kind
        != _PACKED_POINT_FULL_DIGEST_KIND
        or planned._compiler_first_query_input_object_id is None
        or planned._compiler_first_query_input_ref is None
    ):
        _fail(
            "compiler_first_query_input_binding_invalid",
            "planned.compiler_first_query_input_digest",
            "first-query binding requires a full packed digest and object identity",
        )
    state_digest = _digest(
        {
            "template": lowered.template_kind,
            "resources": planned.plan.resources.to_dict(),
            "consumer_composition": composition_metadata,
            "stream_ordering": stream_ordering.value,
        },
        "state_owner",
    )
    extents_digest = _digest(normalized_extents, "extents")
    identity_payload = {
        "semantic_digest": lowered.compiled.spec.semantic_digest,
        "source_digest": lowered.compiled.source_digest,
        "producer_kind": lowered.producer_kind.value,
        "producer_certificate_digest": lowered.producer_binding_digest,
        "producer_schema_digest": producer_schema_digest,
        "target_profile_digest": target_digest,
        "physical_plan_digest": plan_digest,
        "selected_backend": lowered.backend,
        "selected_placement": lowered.placement,
        "selected_template": lowered.template_kind,
        "consumer_composition_digest": (
            composition.composition_digest if composition is not None else "none"
        ),
        "consumer_composition_kind": (
            composition.kind.value if composition is not None else "none"
        ),
        "native_library_identity_digest": (
            planned_native_identity.identity_digest
            if planned_native_identity is not None
            else "none"
        ),
        "native_library_object_token": (
            str(id(planned_native_library))
            if planned_native_library is not None
            else "none"
        ),
        "module_owner_digest": module_digest,
        "index_owner_digest": index_digest,
        "state_owner_digest": state_digest,
        "extents_digest": extents_digest,
        "parameters_digest": parameters_digest,
        "bounded_output_rows": planned.plan.resources.bounded_output_rows,
        "bounded_output_bytes": planned.plan.resources.bounded_output_bytes,
        "event_batch_row_count_mode": (
            "bounded_variable" if max_event_rows is not None else "exact_initial_batch"
        ),
        "max_event_rows": max_event_rows,
        "stream_ordering": stream_ordering.value,
    }
    identity = ActionPreparedIdentity(
        **identity_payload,
        identity_digest=_digest(identity_payload, "prepared_identity"),
    )
    backend_owner = _prepare_backend_owner(
        lowered,
        consumer_composition=composition,
        prepared_input=prepared_input,
        max_distance_bound=max_distance_bound,
        max_candidate_rows=max_candidate_rows,
        stream_ordering=stream_ordering,
        expected_native_library_identity=planned_native_identity,
        expected_native_library_ref=planned_native_library,
    )
    try:
        return PreparedActionExecution(
            planned,
            identity,
            extents=normalized_extents,
            parameters=parameters,
            stream_ordering=stream_ordering,
            backend_owner=backend_owner,
            prepare_elapsed_seconds=time.perf_counter() - started,
            max_event_rows=max_event_rows,
        )
    except Exception:
        if backend_owner is not None and hasattr(backend_owner, "close"):
            backend_owner.close()
        raise


def _production_physical_configuration_policy(lowered):
    trace = getattr(lowered, "compiler_execution_trace", None)
    if not isinstance(trace, Mapping) or "production_default" not in trace:
        return None
    production = trace.get("production_default")
    if not isinstance(production, Mapping):
        _fail(
            "production_physical_configuration_trace_invalid",
            "lowered.compiler_execution_trace.production_default",
            type(production).__name__,
        )
    plan = production.get("plan")
    binding = production.get("binding")
    if not isinstance(plan, Mapping) or not isinstance(binding, Mapping):
        _fail(
            "production_physical_configuration_binding_missing",
            "lowered.compiler_execution_trace.production_default",
            "plan and binding are required",
        )
    nested = plan.get("default_plan")
    if not isinstance(nested, Mapping):
        _fail(
            "production_physical_configuration_default_plan_missing",
            "production_default.plan.default_plan",
            type(nested).__name__,
        )
    policy = plan.get("selected_physical_configuration_policy")
    policy_sha = plan.get("selected_physical_configuration_policy_sha256")
    if (
        nested.get("selected_physical_configuration_policy") != policy
        or nested.get("selected_physical_configuration_policy_sha256") != policy_sha
        or binding.get("selected_physical_configuration_policy") != policy
        or binding.get("selected_physical_configuration_policy_sha256") != policy_sha
    ):
        _fail(
            "production_physical_configuration_policy_rebound",
            "production_default",
            "plan/default_plan/binding disagree",
        )
    if policy is None or policy_sha is None:
        _fail(
            "production_physical_configuration_policy_missing",
            "production_default.plan.selected_physical_configuration_policy",
            "parameter-complete production candidate requires policy",
        )
    return policy


def _prepare_backend_owner(
    lowered: LoweredAction,
    *,
    consumer_composition,
    prepared_input,
    max_distance_bound: float | None,
    max_candidate_rows: int | None,
    stream_ordering: ActionPreparedStreamOrdering,
    expected_native_library_identity,
    expected_native_library_ref,
):
    template = lowered.template_kind
    if template in {
        "certified_nearest_state_3d",
        "certified_nearest_state_3d_optix_traversal",
        "cell_mbr_exact_witness_3d_optix_traversal",
    } or (
        template == "cpu_reference_interpreter"
        and lowered.producer_kind is ActionProducerKind.CERTIFIED_NEAREST_STATE_3D
    ):
        if not isinstance(prepared_input, PreparedCertifiedNearestGridPayload3D):
            _fail(
                "prepared_certified_nearest_grid_payload_required",
                "prepared_input",
                type(prepared_input).__name__,
            )
        if stream_ordering is not ActionPreparedStreamOrdering.SYNCHRONOUS_DEFAULT_STREAM:
            _fail(
                "prepared_certified_nearest_stream_unsupported",
                "stream_ordering",
                stream_ordering.value,
            )
        from .action_nearest_state_lowering import (
            prepare_certified_nearest_state_backend_owner,
        )

        physical_configuration_policy = (
            _production_physical_configuration_policy(lowered)
            if template == "cell_mbr_exact_witness_3d_optix_traversal"
            else None
        )

        return prepare_certified_nearest_state_backend_owner(
            lowered,
            prepared_input.target_points,
            consumer_composition=consumer_composition,
            target_ids=prepared_input.target_ids,
            column_domain_certificate=(
                prepared_input._validated_column_domain_certificate()
            ),
            grid_shape=prepared_input.grid_shape,
            independent_validation_sample_count=(
                prepared_input.independent_validation_sample_count
            ),
            query_domain_lower_bounds=(
                prepared_input.query_domain_lower_bounds
            ),
            query_domain_upper_bounds=(
                prepared_input.query_domain_upper_bounds
            ),
            optix_max_inline_points=(
                prepared_input.optix_max_inline_points
            ),
            optix_max_heavy_point_evaluations=(
                prepared_input.optix_max_heavy_point_evaluations
            ),
            cell_mbr_point_order=(
                prepared_input.cell_mbr_point_order
            ),
            prepared_target_domain=(
                prepared_input.prepared_target_domain
            ),
            physical_configuration_policy=physical_configuration_policy,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
        )
    if lowered.backend == "numba" and template in {
        "filter_bounded_emit",
        "grouped_i64x2_count_sum",
        "certified_query_min_state",
    }:
        if prepared_input is not None:
            _fail("unexpected_prepared_index", "prepared_input", template)
        return None
    if template == "point_candidate_bounded_selection_3d":
        if prepared_input is None or max_distance_bound is None:
            _fail(
                "prepared_index_configuration_required",
                "prepared_input",
                "point candidates require search points and max_distance_bound",
            )
        from .action_optix_lowering import prepare_optix_action_bounded_selection_3d

        return prepare_optix_action_bounded_selection_3d(
            lowered.program,
            prepared_input,
            max_distance_bound=max_distance_bound,
            expected_native_library_identity=(
                expected_native_library_identity
            ),
            expected_native_library_ref=expected_native_library_ref,
        )
    if template == "prepared_ranked_distance_window_qk_3d":
        if prepared_input is None or max_distance_bound is None:
            _fail(
                "prepared_index_configuration_required",
                "prepared_input",
                "ranked distance-window execution requires search points and max_distance_bound",
            )
        from .optix_runtime import prepare_optix_fixed_radius_neighbors_3d

        return prepare_optix_fixed_radius_neighbors_3d(
            prepared_input,
            max_radius=max_distance_bound,
            expected_native_library_identity=(
                expected_native_library_identity
            ),
            expected_native_library_ref=expected_native_library_ref,
        )
    if template == "candidate_pruned_exact_bounded_selection_3d":
        if prepared_input is None or max_distance_bound is None:
            _fail(
                "prepared_index_configuration_required",
                "prepared_input",
                "candidate-pruned exact bounded selection requires search points "
                "and max_distance_bound",
            )
        from .action_candidate_pruned_lowering import (
            prepare_candidate_pruned_exact_bounded_selection_3d,
        )

        return prepare_candidate_pruned_exact_bounded_selection_3d(
            lowered.program,
            prepared_input,
            expected_native_library_identity=expected_native_library_identity,
            expected_native_library_ref=expected_native_library_ref,
        )
    if template == "keyed_i64_sum_3d":
        if isinstance(
            prepared_input,
            ConsumedPreparedTriangleGroupedI64Payload3D,
        ):
            if (
                stream_ordering
                is not ActionPreparedStreamOrdering.SYNCHRONOUS_DEFAULT_STREAM
            ):
                _fail(
                    "consumed_triangle_grouped_i64_stream_unsupported",
                    "stream_ordering",
                    stream_ordering.value,
                )
            return prepared_input.take_backend_owner(lowered)
        if not isinstance(prepared_input, PreparedTriangleGroupedI64Payload3D):
            _fail(
                "prepared_triangle_grouped_i64_payload_required",
                "prepared_input",
                type(prepared_input).__name__,
            )
        from .action_optix_lowering import prepare_optix_action_keyed_i64_sum_3d

        return prepare_optix_action_keyed_i64_sum_3d(
            lowered.program,
            prepared_input.triangles,
            primitive_group_ids=prepared_input.primitive_group_ids,
            primitive_values=prepared_input.primitive_values,
            primitive_includes=prepared_input.primitive_includes,
            group_count=prepared_input.group_count,
        )
    if template == "aabb_filter_bounded_emit_2d":
        if prepared_input is None:
            _fail("prepared_index_configuration_required", "prepared_input", template)
        from .action_optix_lowering import prepare_optix_action_aabb_filter_bounded_emit_2d

        return prepare_optix_action_aabb_filter_bounded_emit_2d(
            lowered.program,
            prepared_input,
        )
    if template == "aabb_filter_bounded_emit_reference_2d":
        if prepared_input is None or max_candidate_rows is None:
            _fail(
                "prepared_index_configuration_required",
                "prepared_input",
                "Embree AABB preparation requires max_candidate_rows",
            )
        from .action_embree_lowering import (
            prepare_embree_action_aabb_filter_bounded_emit_2d,
        )

        return prepare_embree_action_aabb_filter_bounded_emit_2d(
            lowered.program,
            prepared_input,
            max_candidate_rows=max_candidate_rows,
        )
    _fail("prepared_template_unsupported", "lowered.template_kind", template)


def _execute_numba_columns(
    lowered: LoweredAction,
    event_columns: Mapping[str, object],
    parameters: Mapping[str, object],
    extents: Mapping[ExtentKind | str, int],
):
    template = lowered.template_kind
    prepared = None
    result = None
    try:
        if template in {"filter_bounded_emit", "grouped_i64x2_count_sum"}:
            prepared = prepare_bound_numba_action_columns(
                lowered, event_columns, parameters
            )
            if template == "filter_bounded_emit":
                from .action_numba_continuation import execute_numba_action_continuation

                result = execute_numba_action_continuation(prepared, extents=extents)
                project = result.to_host_relation
            else:
                from .action_numba_continuation import (
                    execute_numba_grouped_i64x2_count_sum,
                )

                result = execute_numba_grouped_i64x2_count_sum(prepared)
                project = result.to_host_reductions
        elif template == "certified_query_min_state":
            from .action_numba_continuation import (
                execute_numba_certified_query_min_state,
                prepare_numba_certified_query_min_columns,
            )

            query_count = extents.get(ExtentKind.QUERY_COUNT, extents.get("query_count"))
            if not isinstance(query_count, int):
                _fail(
                    "prepared_query_extent_required",
                    "extents.query_count",
                    repr(query_count),
                )
            prepared = prepare_numba_certified_query_min_columns(
                lowered.program,
                event_columns,
                query_count=query_count,
            )
            result = execute_numba_certified_query_min_state(prepared)
            project = result.to_host_states
        else:
            _fail("prepared_column_template_unsupported", "template", template)
        return project()
    finally:
        if result is not None:
            result.close()
        if prepared is not None:
            prepared.close()


def _normalize_extents(
    extents: Mapping[ExtentKind | str, int],
) -> dict[str, int]:
    if not isinstance(extents, Mapping):
        _fail("prepared_extents_mapping_required", "extents", type(extents).__name__)
    normalized: dict[str, int] = {}
    for key, value in extents.items():
        name = key.value if isinstance(key, ExtentKind) else str(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _fail("invalid_prepared_extent", f"extents.{name}", repr(value))
        normalized[name] = value
    return dict(sorted(normalized.items()))


def _digest(value, label: str) -> str:
    canonical = _canonical_value(value, label)
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(
        ("rtdl.action_prepared_identity.v1\x00" + label + "\x00" + payload).encode(
            "utf-8"
        )
    ).hexdigest()


def _is_sha256_digest(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _canonical_value(value, path: str):
    if isinstance(value, ConsumedPreparedTriangleGroupedI64Payload3D):
        return value._prepared_identity_metadata()
    if isinstance(value, PreparedCertifiedNearestGridPayload3D):
        # The certificate computed the exact full-content digest while issuing
        # immutable bytes-backed columns.  Reuse that proof instead of hashing
        # the same multi-million-row arrays again for prepared identity.
        return value._prepared_identity_metadata()
    if (
        is_dataclass(value)
        and hasattr(value, "records")
        and hasattr(value, "count")
        and hasattr(value, "dimension")
        and isinstance(value.records, ctypes.Array)
    ):
        import numpy as np

        records = np.ctypeslib.as_array(value.records)
        record_fields = {}
        for field_name in records.dtype.names or ():
            field = np.ascontiguousarray(records[field_name])
            record_fields[field_name] = {
                "dtype": field.dtype.str,
                "shape": list(field.shape),
                "sha256": hashlib.sha256(field.tobytes(order="C")).hexdigest(),
            }
        return {
            "packed_record_type": type(value.records)._type_.__name__,
            "packed_record_count": int(value.count),
            "packed_dimension": int(value.dimension),
            "packed_record_fields": record_fields,
            "padding_bytes_excluded_from_identity": True,
        }
    if is_dataclass(value):
        # dataclasses.asdict() deep-copies leaves. Prepared payload leaves can
        # be multi-gigabyte NumPy arrays, so walk fields without copying them.
        return _canonical_value(
            {field.name: getattr(value, field.name) for field in fields(value)},
            path,
        )
    if isinstance(value, Enum):
        return {"enum": value.value}
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(item, f"{path}.{key}")
            for key, item in sorted(value.items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, (tuple, list)):
        return [
            _canonical_value(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    if hasattr(value, "dtype") and hasattr(value, "shape") and hasattr(value, "tobytes"):
        try:
            shape = tuple(int(item) for item in value.shape)
            raw = value.tobytes(order="C")
        except Exception as exc:
            _fail("prepared_identity_value_unsupported", path, str(exc))
        return {
            "array_dtype": str(value.dtype),
            "array_shape": list(shape),
            "array_sha256": hashlib.sha256(raw).hexdigest(),
        }
    if hasattr(value, "item") and callable(value.item):
        try:
            return _canonical_value(value.item(), path)
        except Exception:
            pass
    if isinstance(value, float):
        if not math.isfinite(value):
            _fail("nonfinite_prepared_identity", path, repr(value))
        normalized = 0.0 if value == 0.0 else value
        return {"float_hex": normalized.hex()}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if hasattr(value, "to_metadata") and callable(value.to_metadata):
        return _canonical_value(value.to_metadata(), path)
    _fail("prepared_identity_value_unsupported", path, type(value).__name__)


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionPreparedError(ActionPreparedIssue(code, path, message))


__all__ = (
    "ACTION_PREPARED_VERSION",
    "ActionPreparedError",
    "ActionPreparedIdentity",
    "ActionPreparedIssue",
    "ActionPreparedStreamOrdering",
    "PreparedActionExecution",
    "PreparedActionQueryBatch",
    "PreparedActionQueryResult",
    "PreparedCertifiedNearestGridPayload3D",
    "ConsumedPreparedTriangleGroupedI64Payload3D",
    "PreparedTriangleGroupedI64Payload3D",
    "prepare_consumed_triangle_grouped_i64_action_execution",
    "prepare_action_execution",
    "validate_action_prepared_identity_metadata",
    "validate_prepared_backend_owner_metadata_snapshot",
)
