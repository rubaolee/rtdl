from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Mapping

import numpy as np


_PRODUCER_EVIDENCE_SECRET = secrets.token_bytes(32)
_VERIFIED_CAPABILITY_SECRET = secrets.token_bytes(32)
_PRODUCER_CONSTRUCTOR_KEY = object()
_CAPABILITY_CONSTRUCTOR_KEY = object()

EXPECTED_FRONTIER_CONTRACT = (
    "generic_cell_mbr_nearest_frontier_native_3d_optix"
)
EXPECTED_FRONTIER_SYMBOL = (
    "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4"
)
PREPARED_TARGET_DOMAIN_FRONTIER_SYMBOL = (
    "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_prepared_domain_v1"
)
EXPECTED_FRONTIER_SYMBOLS = frozenset(
    (
        EXPECTED_FRONTIER_SYMBOL,
        PREPARED_TARGET_DOMAIN_FRONTIER_SYMBOL,
    )
)
EXPECTED_PROGRAM_BUNDLE = "cell_mbr_nearest_frontier_f64_3d.v1"
EXPECTED_LOWERED_TEMPLATE = (
    "cell_mbr_exact_witness_3d_optix_traversal"
)
EXPECTED_COMPOSITION = (
    "certified_nearest_state_3d_to_global_argmax_with_witness"
)


def _array_digest(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        array = np.asarray(value)
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(b"\x00")
        digest.update(repr(tuple(int(item) for item in array.shape)).encode("ascii"))
        digest.update(b"\x00")
        digest.update(np.ascontiguousarray(array).tobytes(order="C"))
        digest.update(b"\x00")
    return digest.hexdigest()


def _column_identity_digest(
    columns: Mapping[str, object],
    *,
    names: tuple[str, ...],
) -> str:
    digest = hashlib.sha256()
    for name in names:
        if name not in columns:
            raise RuntimeError(f"completed-state producer is missing column {name!r}")
        digest.update(name.encode("ascii"))
        digest.update(b"\x00")
        digest.update(bytes.fromhex(_array_digest(np.asarray(columns[name]))))
    return digest.hexdigest()


def _require_i64_vector(value, label: str) -> np.ndarray:
    array = np.asarray(value)
    if array.dtype != np.dtype(np.int64) or array.ndim != 1:
        raise RuntimeError(f"{label} must be an exact I64 vector")
    if not array.flags.c_contiguous:
        raise RuntimeError(f"{label} must be C-contiguous")
    return array


def _require_f64_vector(value, label: str) -> np.ndarray:
    array = np.asarray(value)
    if array.dtype != np.dtype(np.float64) or array.ndim != 1:
        raise RuntimeError(f"{label} must be an exact F64 vector")
    if not array.flags.c_contiguous:
        raise RuntimeError(f"{label} must be C-contiguous")
    return array


def _all_ids_in_sorted_domain(
    item_ids: np.ndarray,
    target_ids: np.ndarray,
) -> bool:
    if target_ids.ndim != 1 or target_ids.size == 0:
        return False
    if bool(np.any(target_ids < 0)) or (
        target_ids.size > 1
        and bool(np.any(target_ids[1:] <= target_ids[:-1]))
    ):
        return False
    positions = np.searchsorted(target_ids, item_ids)
    return bool(
        np.all(positions < target_ids.size)
        and np.array_equal(target_ids[positions], item_ids)
    )


class CompletedNearestStateProducerEvidence3D:
    """Private evidence that one executed frontier returned an exact full state.

    This object is compiler-internal evidence, not a public application
    capability and not a behavioral traversal receipt.  It seals the exact
    returned state and the producer inputs after the native frontier call.
    """

    __slots__ = (
        "_query_ids",
        "_nearest_item_ids",
        "_nearest_distances",
        "_query_ids_object_id",
        "_nearest_item_ids_object_id",
        "_nearest_distances_object_id",
        "_query_content_digest",
        "_target_content_digest",
        "_cell_content_digest",
        "_state_content_digest",
        "_producer_object_ids",
        "_query_count",
        "_target_count",
        "_frontier_native_symbol",
        "_seal",
    )

    contract = "rtdl.completed_nearest_state_producer_evidence_3d.v1"

    def __init__(
        self,
        *,
        query_ids: np.ndarray,
        nearest_item_ids: np.ndarray,
        nearest_distances: np.ndarray,
        query_content_digest: str,
        target_content_digest: str,
        cell_content_digest: str,
        producer_object_ids: tuple[int, ...],
        target_count: int,
        _constructor_key,
        frontier_native_symbol: str = EXPECTED_FRONTIER_SYMBOL,
    ) -> None:
        if _constructor_key is not _PRODUCER_CONSTRUCTOR_KEY:
            raise TypeError(
                "completed nearest-state producer evidence is compiler-private"
            )
        query_ids.setflags(write=False)
        nearest_item_ids.setflags(write=False)
        nearest_distances.setflags(write=False)
        object.__setattr__(self, "_query_ids", query_ids)
        object.__setattr__(self, "_nearest_item_ids", nearest_item_ids)
        object.__setattr__(self, "_nearest_distances", nearest_distances)
        object.__setattr__(self, "_query_ids_object_id", id(query_ids))
        object.__setattr__(self, "_nearest_item_ids_object_id", id(nearest_item_ids))
        object.__setattr__(
            self,
            "_nearest_distances_object_id",
            id(nearest_distances),
        )
        object.__setattr__(self, "_query_content_digest", query_content_digest)
        object.__setattr__(self, "_target_content_digest", target_content_digest)
        object.__setattr__(self, "_cell_content_digest", cell_content_digest)
        object.__setattr__(
            self,
            "_state_content_digest",
            _array_digest(query_ids, nearest_item_ids, nearest_distances),
        )
        object.__setattr__(self, "_producer_object_ids", producer_object_ids)
        object.__setattr__(self, "_query_count", int(query_ids.size))
        object.__setattr__(self, "_target_count", int(target_count))
        if frontier_native_symbol not in EXPECTED_FRONTIER_SYMBOLS:
            raise RuntimeError(
                "completed nearest-state producer symbol is not an approved "
                "generic frontier executor"
            )
        object.__setattr__(
            self,
            "_frontier_native_symbol",
            frontier_native_symbol,
        )
        object.__setattr__(self, "_seal", self._issue_seal())
        self._validate_for_compiler()

    def __setattr__(self, _name, _value) -> None:
        raise AttributeError(
            "completed nearest-state producer evidence cannot be modified"
        )

    def _seal_payload(self) -> bytes:
        return (
            f"{self.contract}\x00{self._query_ids_object_id}\x00"
            f"{self._nearest_item_ids_object_id}\x00"
            f"{self._nearest_distances_object_id}\x00"
            f"{self._query_content_digest}\x00{self._target_content_digest}\x00"
            f"{self._cell_content_digest}\x00{self._state_content_digest}\x00"
            f"{self._producer_object_ids!r}\x00{self._query_count}\x00"
            f"{self._target_count}\x00{EXPECTED_FRONTIER_CONTRACT}\x00"
            f"{self._frontier_native_symbol}"
        ).encode("ascii")

    def _issue_seal(self) -> str:
        return hmac.new(
            _PRODUCER_EVIDENCE_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_for_compiler(self) -> None:
        if (
            id(self._query_ids) != self._query_ids_object_id
            or id(self._nearest_item_ids) != self._nearest_item_ids_object_id
            or id(self._nearest_distances)
            != self._nearest_distances_object_id
            or self._query_ids.flags.writeable
            or self._nearest_item_ids.flags.writeable
            or self._nearest_distances.flags.writeable
            or self._state_content_digest
            != _array_digest(
                self._query_ids,
                self._nearest_item_ids,
                self._nearest_distances,
            )
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            raise RuntimeError(
                "completed nearest-state producer evidence binding changed"
            )

    def to_metadata(self) -> dict[str, object]:
        self._validate_for_compiler()
        return {
            "contract": self.contract,
            "query_count": self._query_count,
            "target_count": self._target_count,
            "query_content_digest": self._query_content_digest,
            "target_content_digest": self._target_content_digest,
            "cell_content_digest": self._cell_content_digest,
            "state_content_digest": self._state_content_digest,
            "frontier_contract": EXPECTED_FRONTIER_CONTRACT,
            "frontier_native_symbol": self._frontier_native_symbol,
            "frontier_row_count": 0,
            "per_source_witness_exact": True,
            "cross_process_serialization_allowed": False,
            "metadata_can_authorize_consumption": False,
        }

    def __reduce__(self):
        raise TypeError(
            "completed nearest-state producer evidence cannot be serialized"
        )

    def __getstate__(self):
        raise TypeError(
            "completed nearest-state producer evidence cannot be serialized"
        )


def _issue_completed_nearest_state_producer_evidence_3d(
    *,
    query_ids,
    query_coordinates,
    target_ids,
    target_coordinates,
    cell_columns: Mapping[str, object],
    nearest_state: Mapping[str, object],
    frontier_columns: Mapping[str, object],
    metadata: Mapping[str, object],
    producer_objects: tuple[object, ...],
) -> CompletedNearestStateProducerEvidence3D | None:
    """Issue private evidence only for an exact, empty, completed frontier."""

    declared_rows = int(metadata.get("row_count", -1))
    row_sizes = {
        name: int(np.asarray(value).size)
        for name, value in frontier_columns.items()
    }
    actual_empty = all(size == 0 for size in row_sizes.values())
    if declared_rows == 0 and not actual_empty:
        raise RuntimeError(
            "frontier declares zero rows but returned nonempty row columns"
        )
    if declared_rows != 0:
        return None
    if not actual_empty:
        return None
    frontier_native_symbol = metadata.get("native_generic_symbol")
    eligible = (
        metadata.get("contract") == EXPECTED_FRONTIER_CONTRACT
        and frontier_native_symbol in EXPECTED_FRONTIER_SYMBOLS
        and metadata.get("inline_nearest") is True
        and metadata.get("inline_nearest_state_available") is True
        and metadata.get("per_source_witness_exact") is True
        and metadata.get("global_bound_early_break") is False
        and metadata.get("overflowed") is False
        and metadata.get("overflow_telemetry_only") is False
    )
    if not eligible:
        return None

    producer_query_ids = _require_i64_vector(query_ids, "producer query IDs")
    state_query_ids = _require_i64_vector(
        nearest_state["query_point_ids"],
        "nearest-state query IDs",
    )
    nearest_item_ids = _require_i64_vector(
        nearest_state["current_best_item_ids"],
        "nearest-state item IDs",
    )
    nearest_distances = _require_f64_vector(
        nearest_state["current_best_distances"],
        "nearest-state distances",
    )
    target_id_values = _require_i64_vector(target_ids, "target IDs")
    if (
        not np.array_equal(state_query_ids, producer_query_ids)
        or nearest_item_ids.shape != producer_query_ids.shape
        or nearest_distances.shape != producer_query_ids.shape
    ):
        raise RuntimeError(
            "completed nearest state does not exactly cover producer queries"
        )
    if (
        bool(np.any(nearest_item_ids < 0))
        or not bool(np.all(np.isfinite(nearest_distances)))
        or bool(np.any(nearest_distances < 0.0))
        or not _all_ids_in_sorted_domain(nearest_item_ids, target_id_values)
    ):
        raise RuntimeError(
            "completed nearest state is outside the exact target domain"
        )

    cell_digest = _column_identity_digest(
        cell_columns,
        names=(
            "cell_ids",
            "point_begin_offsets",
            "point_counts",
            "point_row_indices",
            "min_x",
            "min_y",
            "min_z",
            "max_x",
            "max_y",
            "max_z",
        ),
    )
    return CompletedNearestStateProducerEvidence3D(
        query_ids=state_query_ids,
        nearest_item_ids=nearest_item_ids,
        nearest_distances=nearest_distances,
        query_content_digest=_array_digest(
            producer_query_ids,
            np.asarray(query_coordinates, dtype=np.float64),
        ),
        target_content_digest=_array_digest(
            target_id_values,
            np.asarray(target_coordinates, dtype=np.float64),
        ),
        cell_content_digest=cell_digest,
        producer_object_ids=tuple(id(value) for value in producer_objects),
        target_count=int(target_id_values.size),
        frontier_native_symbol=str(frontier_native_symbol),
        _constructor_key=_PRODUCER_CONSTRUCTOR_KEY,
    )


class VerifiedCompletedNearestState3D:
    """Single-use compiler proof for consuming an exact completed state."""

    __slots__ = (
        "_producer_evidence",
        "_query_matrix",
        "_query_ids",
        "_target_certificate",
        "_native_library_identity",
        "_native_library_ref",
        "_query_matrix_object_id",
        "_query_ids_object_id",
        "_target_certificate_object_id",
        "_native_identity_object_id",
        "_native_library_object_id",
        "_query_content_digest",
        "_target_content_digest",
        "_state_content_digest",
        "_native_identity_digest",
        "_prepared_generation",
        "_execution_generation",
        "_permitted_consumer",
        "_consumed",
        "_seal",
    )

    contract = "rtdl.verified_completed_nearest_state_3d.v1"

    def __init__(
        self,
        *,
        producer_evidence: CompletedNearestStateProducerEvidence3D,
        query_matrix: np.ndarray,
        query_ids: np.ndarray,
        target_certificate,
        native_library_identity,
        native_library_ref,
        prepared_generation: str,
        execution_generation: int,
        permitted_consumer: str,
        _constructor_key,
    ) -> None:
        if _constructor_key is not _CAPABILITY_CONSTRUCTOR_KEY:
            raise TypeError(
                "verified completed nearest-state capability is compiler-private"
            )
        query_matrix.setflags(write=False)
        query_ids.setflags(write=False)
        object.__setattr__(self, "_producer_evidence", producer_evidence)
        object.__setattr__(self, "_query_matrix", query_matrix)
        object.__setattr__(self, "_query_ids", query_ids)
        object.__setattr__(self, "_target_certificate", target_certificate)
        object.__setattr__(
            self,
            "_native_library_identity",
            native_library_identity,
        )
        object.__setattr__(self, "_native_library_ref", native_library_ref)
        object.__setattr__(self, "_query_matrix_object_id", id(query_matrix))
        object.__setattr__(self, "_query_ids_object_id", id(query_ids))
        object.__setattr__(
            self,
            "_target_certificate_object_id",
            id(target_certificate),
        )
        object.__setattr__(
            self,
            "_native_identity_object_id",
            id(native_library_identity),
        )
        object.__setattr__(
            self,
            "_native_library_object_id",
            id(native_library_ref),
        )
        object.__setattr__(
            self,
            "_query_content_digest",
            _array_digest(query_ids, query_matrix),
        )
        object.__setattr__(
            self,
            "_target_content_digest",
            str(target_certificate.target_content_digest),
        )
        object.__setattr__(
            self,
            "_state_content_digest",
            producer_evidence._state_content_digest,
        )
        object.__setattr__(
            self,
            "_native_identity_digest",
            str(native_library_identity.identity_digest),
        )
        object.__setattr__(self, "_prepared_generation", prepared_generation)
        object.__setattr__(self, "_execution_generation", execution_generation)
        object.__setattr__(self, "_permitted_consumer", permitted_consumer)
        object.__setattr__(self, "_consumed", False)
        object.__setattr__(self, "_seal", self._issue_seal())
        self._validate()

    def __setattr__(self, _name, _value) -> None:
        raise AttributeError(
            "verified completed nearest-state capability cannot be modified"
        )

    def _seal_payload(self) -> bytes:
        return (
            f"{self.contract}\x00{id(self._producer_evidence)}\x00"
            f"{self._query_matrix_object_id}\x00{self._query_ids_object_id}\x00"
            f"{self._target_certificate_object_id}\x00"
            f"{self._native_identity_object_id}\x00"
            f"{self._native_library_object_id}\x00"
            f"{self._query_content_digest}\x00{self._target_content_digest}\x00"
            f"{self._state_content_digest}\x00{self._native_identity_digest}\x00"
            f"{EXPECTED_PROGRAM_BUNDLE}\x00{EXPECTED_LOWERED_TEMPLATE}\x00"
            f"{EXPECTED_COMPOSITION}\x00{self._prepared_generation}\x00"
            f"{self._execution_generation}\x00{self._permitted_consumer}"
        ).encode("ascii")

    def _issue_seal(self) -> str:
        return hmac.new(
            _VERIFIED_CAPABILITY_SECRET,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate(self) -> None:
        self._producer_evidence._validate_for_compiler()
        self._target_certificate.validate_exact(
            self._target_certificate.target_points,
            self._target_certificate.target_ids,
        )
        if (
            id(self._query_matrix) != self._query_matrix_object_id
            or id(self._query_ids) != self._query_ids_object_id
            or id(self._target_certificate)
            != self._target_certificate_object_id
            or id(self._native_library_identity)
            != self._native_identity_object_id
            or id(self._native_library_ref) != self._native_library_object_id
            or self._query_matrix.flags.writeable
            or self._query_ids.flags.writeable
            or self._query_content_digest
            != _array_digest(self._query_ids, self._query_matrix)
            or self._target_content_digest
            != self._target_certificate.target_content_digest
            or self._native_identity_digest
            != self._native_library_identity.identity_digest
            or self._state_content_digest
            != self._producer_evidence._state_content_digest
            or not hmac.compare_digest(self._seal, self._issue_seal())
        ):
            raise RuntimeError(
                "verified completed nearest-state capability binding changed"
            )

    def consume_once(self, *, permitted_consumer: str) -> dict[str, np.ndarray]:
        if self._consumed:
            raise RuntimeError(
                "verified completed nearest-state capability was already consumed"
            )
        if permitted_consumer != self._permitted_consumer:
            raise RuntimeError(
                "verified completed nearest-state capability consumer changed"
            )
        self._validate()
        object.__setattr__(self, "_consumed", True)
        return {
            "source_ids": self._producer_evidence._query_ids,
            "nearest_item_ids": self._producer_evidence._nearest_item_ids,
            "nearest_distances": self._producer_evidence._nearest_distances,
        }

    def to_metadata(self) -> dict[str, object]:
        self._validate()
        return {
            "contract": self.contract,
            "producer_evidence_contract": self._producer_evidence.contract,
            "producer_state_content_digest": self._state_content_digest,
            "target_content_digest": self._target_content_digest,
            "query_content_digest": self._query_content_digest,
            "native_library_identity_digest": self._native_identity_digest,
            "program_bundle": EXPECTED_PROGRAM_BUNDLE,
            "lowered_template": EXPECTED_LOWERED_TEMPLATE,
            "composition": EXPECTED_COMPOSITION,
            "prepared_generation": self._prepared_generation,
            "execution_generation": self._execution_generation,
            "permitted_consumer": self._permitted_consumer,
            "single_consumer": True,
            "consumed": self._consumed,
            "cross_process_serialization_allowed": False,
            "metadata_can_authorize_consumption": False,
        }

    def __reduce__(self):
        raise TypeError(
            "verified completed nearest-state capability cannot be serialized"
        )

    def __getstate__(self):
        raise TypeError(
            "verified completed nearest-state capability cannot be serialized"
        )


def verify_completed_nearest_state_3d(
    producer_evidence,
    *,
    query_matrix,
    query_ids,
    target_certificate,
    native_library_identity,
    native_library_ref,
    expected_program_bundle: str,
    expected_lowered_template: str,
    expected_composition: str,
    prepared_generation: str,
    execution_generation: int,
    permitted_consumer: str,
) -> VerifiedCompletedNearestState3D:
    """Verify producer evidence and issue one exact consumer capability."""

    if not isinstance(
        producer_evidence,
        CompletedNearestStateProducerEvidence3D,
    ):
        raise TypeError(
            "completed nearest-state verification requires private producer evidence"
        )
    producer_evidence._validate_for_compiler()
    if (
        expected_program_bundle != EXPECTED_PROGRAM_BUNDLE
        or expected_lowered_template != EXPECTED_LOWERED_TEMPLATE
        or expected_composition != EXPECTED_COMPOSITION
    ):
        raise RuntimeError(
            "completed nearest-state compiler composition binding changed"
        )
    from .action_nearest_state_lowering import (
        ImmutablePointColumnDomain3DCertificate,
    )

    if not isinstance(
        target_certificate,
        ImmutablePointColumnDomain3DCertificate,
    ):
        raise TypeError(
            "completed nearest-state verification requires an immutable target-domain certificate"
        )
    target_certificate.validate_exact(
        target_certificate.target_points,
        target_certificate.target_ids,
    )
    query_matrix_value = np.asarray(query_matrix)
    query_id_values = np.asarray(query_ids)
    if (
        query_matrix_value.dtype != np.dtype(np.float64)
        or query_matrix_value.ndim != 2
        or query_matrix_value.shape[1:] != (3,)
        or not query_matrix_value.flags.c_contiguous
        or query_id_values.dtype != np.dtype(np.int64)
        or query_id_values.ndim != 1
        or not query_id_values.flags.c_contiguous
        or query_matrix_value.shape[0] != query_id_values.size
    ):
        raise RuntimeError(
            "completed nearest-state query binding is not exact F64x3/I64"
        )
    if (
        producer_evidence._query_count != int(query_id_values.size)
        or producer_evidence._query_content_digest
        != _array_digest(query_id_values, query_matrix_value)
        or producer_evidence._target_content_digest
        != _array_digest(
            target_certificate.target_ids,
            target_certificate.target_points,
        )
        or not np.array_equal(
            producer_evidence._query_ids,
            query_id_values,
        )
        or not _all_ids_in_sorted_domain(
            producer_evidence._nearest_item_ids,
            target_certificate.target_ids,
        )
    ):
        raise RuntimeError(
            "completed nearest-state evidence differs from compiler-bound query or target"
        )
    if (
        not isinstance(prepared_generation, str)
        or not prepared_generation
        or not isinstance(execution_generation, int)
        or isinstance(execution_generation, bool)
        or execution_generation <= 0
        or not isinstance(permitted_consumer, str)
        or not permitted_consumer
    ):
        raise ValueError(
            "completed nearest-state generation and consumer bindings are required"
        )
    return VerifiedCompletedNearestState3D(
        producer_evidence=producer_evidence,
        query_matrix=query_matrix_value,
        query_ids=query_id_values,
        target_certificate=target_certificate,
        native_library_identity=native_library_identity,
        native_library_ref=native_library_ref,
        prepared_generation=prepared_generation,
        execution_generation=execution_generation,
        permitted_consumer=permitted_consumer,
        _constructor_key=_CAPABILITY_CONSTRUCTOR_KEY,
    )


__all__ = (
    "CompletedNearestStateProducerEvidence3D",
    "VerifiedCompletedNearestState3D",
    "verify_completed_nearest_state_3d",
)
