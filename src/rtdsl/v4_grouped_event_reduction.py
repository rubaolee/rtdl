"""Verified global grouped-event reduction for V4.

This module closes the M5 semantic gap without accepting an application
reducer, an opaque callback, or an application identity.  A behaviorally
observed OptiX producer first supplies a bounded canonical U32-pair relation.
The compiler then applies one closed field-projection algebra and lowers the
result to the existing checked Numba/CUDA grouped-I64x2 COUNT+SUM partner.

The physical split is intentional:

* OptiX owns spatial candidate/event production;
* the compiler owns the exact row-to-event projection and its lifetime;
* the Numba partner owns canonical grouping plus checked signed-I64 addition;
* only canonical immutable result rows cross back to a consumer.

No raw device order is semantic.  Capacity, receipt binding, missing lookup
keys, duplicate lookup keys, and signed overflow all fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from types import MappingProxyType
from typing import Iterable, Mapping, Sequence

import numpy as np

from .action_frontend import (
    RestrictedActionFrontendContract,
    compile_restricted_action_source,
)
from .action_ir import (
    I64,
    U64,
    ActionField,
    ActionRecordType,
    ActionReductionSpec,
    ActionScalarLiteral,
    DeliveryEnforcement,
    LogicalEventContract,
    PhysicalDelivery,
    ReductionOperator,
)
from .action_numba_continuation import (
    NumbaGroupedI64x2CountSumProgram,
    PreparedGroupedI64x2DeviceWorkspace,
    _prepare_numba_grouped_i64x2_count_sum_canonical_host_workspace_verified,
    compile_numba_grouped_i64x2_count_sum,
    eager_specialize_numba_grouped_i64x2_count_sum,
    execute_numba_grouped_i64x2_count_sum,
    prepare_numba_grouped_i64x2_count_sum_columns,
)


GROUPED_EVENT_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-grouped-event-reduction-v1.json"
)
GROUPED_EVENT_SCHEMA_VERSION = "v1"
U32_MAX = (1 << 32) - 1
I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1
U64_MAX = (1 << 64) - 1
_BATCH_SEAL_KEY = secrets.token_bytes(32)
_PRODUCER_SEAL_KEY = secrets.token_bytes(32)
_PREPARED_OWNER_KEY = secrets.token_bytes(32)


class GroupedEventReductionError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 grouped-event reduction rejected: {code}@{path}: {message}"
        )


def _fail(code: str, path: str, message: str) -> None:
    raise GroupedEventReductionError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _sha(value: str, path: str) -> str:
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _fail("identity", path, "lower-case SHA-256 identity required")
    return value


def _i64(value: object, path: str) -> int:
    if isinstance(value, bool):
        _fail("i64_domain", path, "boolean is not an i64")
    result = int(value)
    if result != value or not I64_MIN <= result <= I64_MAX:
        _fail("i64_domain", path, repr(value))
    return result


def _u32(value: object, path: str) -> int:
    if isinstance(value, bool):
        _fail("u32_domain", path, "boolean is not a u32")
    result = int(value)
    if result != value or not 0 <= result <= U32_MAX:
        _fail("u32_domain", path, repr(value))
    return result


class EventFieldSource(str, Enum):
    SOURCE_ID = "source_id_i64"
    ITEM_ID = "item_id_i64"
    SOURCE_LOOKUP = "source_lookup_i64"
    ITEM_LOOKUP = "item_lookup_i64"
    CONSTANT = "constant_i64"


class EventProducerCompletionKind(str, Enum):
    DIRECT_CANONICAL_RELATION = "direct_canonical_relation_v1"
    VERIFIED_EXACT_PARTNER_COMPLETION = "verified_exact_partner_completion_v1"


@dataclass(frozen=True)
class I64LookupTable:
    rows: tuple[tuple[int, int], ...]
    table_sha256: str

    @classmethod
    def from_rows(cls, rows: Iterable[Sequence[object]]) -> "I64LookupTable":
        materialized: list[tuple[int, int]] = []
        for index, row in enumerate(rows):
            if len(row) != 2:
                _fail("lookup_shape", f"rows[{index}]", "u32 key and i64 value required")
            materialized.append((
                _u32(row[0], f"rows[{index}][0]"),
                _i64(row[1], f"rows[{index}][1]"),
            ))
        materialized.sort()
        if len({key for key, _ in materialized}) != len(materialized):
            _fail("duplicate_lookup_key", "rows", "lookup keys must be unique")
        frozen = tuple(materialized)
        return cls(frozen, _digest(frozen))

    def as_mapping(self) -> Mapping[int, int]:
        if self.table_sha256 != _digest(self.rows):
            _fail("lookup_digest", "lookup", "lookup content changed")
        return dict(self.rows)


@dataclass(frozen=True)
class EventFieldProjection:
    source: EventFieldSource
    lookup_sha256: str | None = None
    constant_i64: int | None = None

    def semantic_dict(self) -> dict[str, object]:
        return {
            "source": self.source.value,
            "lookup_sha256": self.lookup_sha256,
            "constant_i64": self.constant_i64,
        }


@dataclass(frozen=True)
class GroupedEventReductionSchema:
    producer_contract_sha256: str
    maximum_event_rows: int
    key0: EventFieldProjection
    key1: EventFieldProjection
    signed_value: EventFieldProjection
    schema_id: str = GROUPED_EVENT_SCHEMA_ID
    schema_version: str = GROUPED_EVENT_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "producer_contract_sha256": self.producer_contract_sha256,
            "maximum_event_rows": self.maximum_event_rows,
            "key0": self.key0.semantic_dict(),
            "key1": self.key1.semantic_dict(),
            "signed_value": self.signed_value.semantic_dict(),
            "logical_event_delivery": "verified_single",
            "canonical_group_order": "lexicographic_i64x2",
            "reductions": ["count_u64", "checked_sum_i64"],
            "signed_overflow_policy": "device_fail_closed",
            "raw_device_order_is_semantic": False,
            "application_owned_grouping_allowed": False,
            "arbitrary_user_projection_or_reducer_allowed": False,
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedEventProducerEvidence:
    producer_contract_sha256: str
    producer_semantic_rows: tuple[tuple[int, int], ...]
    producer_output_sha256: str
    traversal_receipt_sha256: str
    native_library_sha256: str
    maximum_event_rows: int
    completion_kind: EventProducerCompletionKind
    semantic_completion_authority_sha256: str | None
    authority_nonce: str
    compiler_seal: str


@dataclass(frozen=True)
class VerifiedGroupedEventBatch:
    schema: GroupedEventReductionSchema
    producer: VerifiedEventProducerEvidence
    event_id: tuple[int, ...]
    key0: tuple[int, ...]
    key1: tuple[int, ...]
    signed_value: tuple[int, ...]
    content_sha256: str
    compiler_seal: str

    @property
    def row_count(self) -> int:
        return len(self.event_id)


@dataclass(frozen=True)
class CompiledGroupedEventReduction:
    schema: GroupedEventReductionSchema
    producer_authority_nonce: str
    delivery_proof_reference: str
    action_program: NumbaGroupedI64x2CountSumProgram
    contract_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "template_contract_sha256": GROUPED_EVENT_TEMPLATE_SHA256,
            "schema_sha256": self.schema.schema_sha256,
            "producer_authority_nonce": self.producer_authority_nonce,
            "delivery_proof_reference": self.delivery_proof_reference,
            "action_semantic_digest": self.action_program.spec.semantic_digest,
            "action_program": self.action_program.to_metadata(),
            "contract_sha256": self.contract_sha256,
            "physical_stages": [
                "behaviorally_verified_optix_event_producer",
                "compiler_owned_closed_event_projection",
                "numba_cuda_checked_grouped_i64x2_count_sum",
            ],
            "application_or_publication_identity_used": False,
        }


@dataclass(frozen=True)
class GroupedEventReductionResult:
    rows: tuple[tuple[int, int, int, int], ...]
    output_sha256: str
    program_contract_sha256: str
    producer_output_sha256: str
    traversal_receipt_sha256: str
    device_metadata: dict[str, object]


def _verify_traversal_receipt(receipt: Mapping[str, object]) -> str:
    if type(receipt) is not dict:
        _fail("traversal_receipt", "receipt", "exact dict required")
    claimed = receipt.get("receipt_sha256")
    body = dict(receipt)
    body.pop("receipt_sha256", None)
    if claimed != _digest(body):
        _fail("traversal_receipt_digest", "receipt", "receipt digest mismatch")
    snapshot = receipt.get("native_snapshot")
    if type(snapshot) is not dict:
        _fail("traversal_receipt", "receipt.native_snapshot", "exact dict required")
    successful = snapshot.get("successful_launch_count")
    complete = snapshot.get("complete_context_launch_count")
    if (
        receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or not isinstance(successful, int)
        or successful <= 0
        or complete != successful
        or snapshot.get("failed_launch_count") != 0
        or snapshot.get("incomplete_context_launch_count") != 0
        or snapshot.get("pending_context_at_finish") != 0
        or snapshot.get("session_error") != 0
        or not snapshot.get("first_traversable")
        or not snapshot.get("last_traversable")
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
    ):
        _fail(
            "behavioral_optix_receipt",
            "receipt",
            "complete bound OptiX traversal is required",
        )
    _sha(str(receipt.get("provider_library_sha256")), "receipt.provider_library_sha256")
    _sha(str(receipt.get("output_digest")), "receipt.output_digest")
    return str(claimed)


def verify_event_producer_evidence(
    rows: Iterable[Sequence[object]],
    *,
    producer_contract_sha256: str,
    maximum_event_rows: int,
    traversal_receipt: Mapping[str, object],
    completion_kind: EventProducerCompletionKind = (
        EventProducerCompletionKind.DIRECT_CANONICAL_RELATION),
    semantic_completion_authority_sha256: str | None = None,
) -> VerifiedEventProducerEvidence:
    """Bind semantic event rows to one complete behavioral OptiX producer.

    The semantic rows may be a verified exact-predicate completion of the
    broad-phase output; therefore their digest is distinct from the physical
    receipt output digest and both are preserved.
    """

    contract = _sha(producer_contract_sha256, "producer_contract_sha256")
    if not isinstance(maximum_event_rows, int) or isinstance(maximum_event_rows, bool) \
            or maximum_event_rows <= 0 or maximum_event_rows > U32_MAX:
        _fail("capacity", "maximum_event_rows", "positive u32 capacity required")
    materialized: list[tuple[int, int]] = []
    for index, row in enumerate(rows):
        if len(row) != 2:
            _fail("producer_row_shape", f"rows[{index}]", "u32 pair required")
        materialized.append((
            _u32(row[0], f"rows[{index}][0]"),
            _u32(row[1], f"rows[{index}][1]"),
        ))
    if len(materialized) > maximum_event_rows:
        _fail("capacity_overflow", "rows", f"capacity={maximum_event_rows}")
    if len(set(materialized)) != len(materialized):
        _fail("duplicate_logical_event", "rows", "producer rows must be unique")
    frozen = tuple(sorted(materialized))
    receipt_sha = _verify_traversal_receipt(traversal_receipt)
    output_sha = _sha(
        str(traversal_receipt["output_digest"]), "receipt.output_digest")
    native_sha = _sha(
        str(traversal_receipt["provider_library_sha256"]),
        "receipt.provider_library_sha256",
    )
    if not isinstance(completion_kind, EventProducerCompletionKind):
        _fail("completion_kind", "completion_kind", "closed completion enum required")
    semantic_rows_sha = _digest(frozen)
    if completion_kind is EventProducerCompletionKind.DIRECT_CANONICAL_RELATION:
        if semantic_completion_authority_sha256 is not None:
            _fail(
                "completion_authority",
                "semantic_completion_authority_sha256",
                "direct relation cannot carry an exact-partner authority",
            )
        if semantic_rows_sha != output_sha:
            _fail(
                "direct_relation_output_binding",
                "rows",
                "direct semantic rows must equal the receipt-bound output",
            )
    else:
        if semantic_completion_authority_sha256 is None:
            _fail(
                "completion_authority",
                "semantic_completion_authority_sha256",
                "exact partner completion requires a frozen authority digest",
            )
        _sha(
            semantic_completion_authority_sha256,
            "semantic_completion_authority_sha256",
        )
    nonce = _digest({
        "kind": "verified_v4_event_producer_evidence_v1",
        "contract": contract,
        "semantic_rows": semantic_rows_sha,
        "physical_output": output_sha,
        "receipt": receipt_sha,
        "native": native_sha,
        "capacity": maximum_event_rows,
        "completion_kind": completion_kind.value,
        "semantic_completion_authority": semantic_completion_authority_sha256,
    })
    unsealed = VerifiedEventProducerEvidence(
        contract, frozen, output_sha, receipt_sha, native_sha,
        maximum_event_rows, completion_kind,
        semantic_completion_authority_sha256, nonce, "",
    )
    seal = hmac.new(
        _PRODUCER_SEAL_KEY,
        repr((
            "rtdl.v4.event_producer_evidence.seal.v1",
            unsealed.producer_contract_sha256,
            unsealed.producer_semantic_rows,
            unsealed.producer_output_sha256,
            unsealed.traversal_receipt_sha256,
            unsealed.native_library_sha256,
            unsealed.maximum_event_rows,
            unsealed.completion_kind.value,
            unsealed.semantic_completion_authority_sha256,
            unsealed.authority_nonce,
        )).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return VerifiedEventProducerEvidence(
        contract, frozen, output_sha, receipt_sha, native_sha,
        maximum_event_rows, completion_kind,
        semantic_completion_authority_sha256, nonce, seal,
    )


def _validate_producer_evidence(producer: VerifiedEventProducerEvidence) -> None:
    if type(producer) is not VerifiedEventProducerEvidence:
        _fail("producer_exact_type", "producer", type(producer).__name__)
    expected = hmac.new(
        _PRODUCER_SEAL_KEY,
        repr((
            "rtdl.v4.event_producer_evidence.seal.v1",
            producer.producer_contract_sha256,
            producer.producer_semantic_rows,
            producer.producer_output_sha256,
            producer.traversal_receipt_sha256,
            producer.native_library_sha256,
            producer.maximum_event_rows,
            producer.completion_kind.value,
            producer.semantic_completion_authority_sha256,
            producer.authority_nonce,
        )).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(producer.compiler_seal, expected):
        _fail("producer_seal", "producer", "compiler producer seal is invalid")


def _verify_projection(
    projection: EventFieldProjection,
    *,
    label: str,
    lookups: Mapping[str, I64LookupTable],
) -> None:
    if not isinstance(projection, EventFieldProjection) \
            or not isinstance(projection.source, EventFieldSource):
        _fail("projection", label, "closed field projection required")
    if projection.source in {EventFieldSource.SOURCE_LOOKUP, EventFieldSource.ITEM_LOOKUP}:
        if projection.lookup_sha256 not in lookups:
            _fail("projection_lookup", label, "exact lookup digest is unavailable")
        if projection.constant_i64 is not None:
            _fail("projection_shape", label, "lookup projection cannot carry a constant")
    elif projection.source is EventFieldSource.CONSTANT:
        if projection.lookup_sha256 is not None or projection.constant_i64 is None:
            _fail("projection_shape", label, "constant projection is malformed")
        _i64(projection.constant_i64, f"{label}.constant_i64")
    elif projection.lookup_sha256 is not None or projection.constant_i64 is not None:
        _fail("projection_shape", label, "direct-ID projection carries extra authority")


def verify_grouped_event_schema(
    schema: GroupedEventReductionSchema,
    producer: VerifiedEventProducerEvidence,
    *,
    lookup_tables: Sequence[I64LookupTable] = (),
) -> dict[str, I64LookupTable]:
    _validate_producer_evidence(producer)
    if not isinstance(schema, GroupedEventReductionSchema):
        _fail("schema", "schema", type(schema).__name__)
    if schema.schema_id != GROUPED_EVENT_SCHEMA_ID \
            or schema.schema_version != GROUPED_EVENT_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported schema")
    if schema.producer_contract_sha256 != producer.producer_contract_sha256:
        _fail("producer_binding", "schema", "producer contract differs")
    if schema.maximum_event_rows != producer.maximum_event_rows:
        _fail("capacity_binding", "schema", "producer capacity differs")
    by_digest: dict[str, I64LookupTable] = {}
    for index, table in enumerate(lookup_tables):
        if not isinstance(table, I64LookupTable):
            _fail("lookup", f"lookup_tables[{index}]", type(table).__name__)
        table.as_mapping()
        if table.table_sha256 in by_digest:
            _fail("duplicate_lookup_digest", "lookup_tables", table.table_sha256)
        by_digest[table.table_sha256] = table
    _verify_projection(schema.key0, label="schema.key0", lookups=by_digest)
    _verify_projection(schema.key1, label="schema.key1", lookups=by_digest)
    _verify_projection(
        schema.signed_value, label="schema.signed_value", lookups=by_digest)
    return by_digest


def _project(
    projection: EventFieldProjection,
    source_id: int,
    item_id: int,
    lookups: Mapping[str, I64LookupTable],
    path: str,
) -> int:
    if projection.source is EventFieldSource.SOURCE_ID:
        return source_id
    if projection.source is EventFieldSource.ITEM_ID:
        return item_id
    if projection.source is EventFieldSource.CONSTANT:
        return _i64(projection.constant_i64, path)
    table = lookups[str(projection.lookup_sha256)].as_mapping()
    identity = (
        source_id
        if projection.source is EventFieldSource.SOURCE_LOOKUP
        else item_id
    )
    if identity not in table:
        _fail("missing_projection_key", path, repr(identity))
    return table[identity]


def _batch_payload(batch: VerifiedGroupedEventBatch) -> object:
    return (
        "rtdl.v4.verified_grouped_event_batch.v1",
        batch.schema.schema_sha256,
        batch.producer.authority_nonce,
        batch.event_id,
        batch.key0,
        batch.key1,
        batch.signed_value,
        batch.content_sha256,
    )


def _batch_seal(payload: object) -> str:
    return hmac.new(
        _BATCH_SEAL_KEY, repr(payload).encode("utf-8"), hashlib.sha256,
    ).hexdigest()


def materialize_verified_grouped_event_batch(
    schema: GroupedEventReductionSchema,
    producer: VerifiedEventProducerEvidence,
    *,
    lookup_tables: Sequence[I64LookupTable] = (),
) -> VerifiedGroupedEventBatch:
    lookups = verify_grouped_event_schema(
        schema, producer, lookup_tables=lookup_tables)
    rows: list[tuple[int, int, int, int]] = []
    for ordinal, (source_id, item_id) in enumerate(producer.producer_semantic_rows):
        rows.append((
            ordinal,
            _project(schema.key0, source_id, item_id, lookups, f"rows[{ordinal}].key0"),
            _project(schema.key1, source_id, item_id, lookups, f"rows[{ordinal}].key1"),
            _project(
                schema.signed_value, source_id, item_id, lookups,
                f"rows[{ordinal}].signed_value"),
        ))
    rows.sort(key=lambda row: (row[1], row[2], row[0]))
    columns = tuple(tuple(row[index] for row in rows) for index in range(4))
    content_sha = _digest(columns)
    unsealed = VerifiedGroupedEventBatch(
        schema, producer, columns[0], columns[1], columns[2], columns[3],
        content_sha, "",
    )
    return VerifiedGroupedEventBatch(
        schema, producer, columns[0], columns[1], columns[2], columns[3],
        content_sha, _batch_seal(_batch_payload(unsealed)),
    )


def _materialize_prepared_grouped_event_batch(
    schema: GroupedEventReductionSchema,
    producer: VerifiedEventProducerEvidence,
    *,
    lookup_mappings: Mapping[str, Mapping[int, int]],
) -> VerifiedGroupedEventBatch:
    """Materialize after an enclosing prepared owner sealed static lookups."""

    _validate_producer_evidence(producer)
    if (
        schema.producer_contract_sha256 != producer.producer_contract_sha256
        or schema.maximum_event_rows != producer.maximum_event_rows
    ):
        _fail(
            "execution_binding",
            "producer",
            "prepared schema and live producer differ",
        )

    def project(
        projection: EventFieldProjection,
        source_id: int,
        item_id: int,
        path: str,
    ) -> int:
        if projection.source is EventFieldSource.SOURCE_ID:
            return source_id
        if projection.source is EventFieldSource.ITEM_ID:
            return item_id
        if projection.source is EventFieldSource.CONSTANT:
            return _i64(projection.constant_i64, path)
        table = lookup_mappings[str(projection.lookup_sha256)]
        identity = (
            source_id
            if projection.source is EventFieldSource.SOURCE_LOOKUP
            else item_id
        )
        if identity not in table:
            _fail("missing_projection_key", path, repr(identity))
        return table[identity]

    rows: list[tuple[int, int, int, int]] = []
    for ordinal, (source_id, item_id) in enumerate(
        producer.producer_semantic_rows
    ):
        rows.append((
            ordinal,
            project(schema.key0, source_id, item_id, f"rows[{ordinal}].key0"),
            project(schema.key1, source_id, item_id, f"rows[{ordinal}].key1"),
            project(
                schema.signed_value,
                source_id,
                item_id,
                f"rows[{ordinal}].signed_value",
            ),
        ))
    rows.sort(key=lambda row: (row[1], row[2], row[0]))
    columns = tuple(tuple(row[index] for row in rows) for index in range(4))
    content_sha = _digest(columns)
    unsealed = VerifiedGroupedEventBatch(
        schema,
        producer,
        columns[0],
        columns[1],
        columns[2],
        columns[3],
        content_sha,
        "",
    )
    return VerifiedGroupedEventBatch(
        schema,
        producer,
        columns[0],
        columns[1],
        columns[2],
        columns[3],
        content_sha,
        _batch_seal(_batch_payload(unsealed)),
    )


def _validate_batch(batch: VerifiedGroupedEventBatch) -> None:
    if type(batch) is not VerifiedGroupedEventBatch:
        _fail("batch_exact_type", "batch", type(batch).__name__)
    if not hmac.compare_digest(
        batch.compiler_seal,
        _batch_seal(_batch_payload(VerifiedGroupedEventBatch(
            batch.schema, batch.producer, batch.event_id, batch.key0,
            batch.key1, batch.signed_value, batch.content_sha256, ""))),
    ):
        _fail("batch_seal", "batch", "compiler batch seal is invalid")
    columns = (batch.event_id, batch.key0, batch.key1, batch.signed_value)
    if len({len(column) for column in columns}) != 1 \
            or len(batch.event_id) > batch.schema.maximum_event_rows \
            or batch.content_sha256 != _digest(columns):
        _fail("batch_content", "batch", "column identity or capacity changed")
    if tuple(zip(batch.key0, batch.key1, batch.event_id)) != tuple(sorted(
            zip(batch.key0, batch.key1, batch.event_id))):
        _fail("batch_order", "batch", "canonical key/event order required")


_ACTION_SOURCE = """
def action(event, params):
    value = event.signed_value
    reduce("event_count")
    reduce("signed_sum", value)
"""


# This digest names the app-neutral physical template, not one compiled
# instance.  Instance semantic digests intentionally include producer and
# delivery-proof identity and therefore differ across legitimate consumers.
GROUPED_EVENT_TEMPLATE_SHA256 = _digest({
    "kind": "v4_grouped_event_reduction_template_v1",
    "action_source": _ACTION_SOURCE,
    "event_fields": ("event_id", "key0", "key1", "signed_value"),
    "logical_event_key": ("event_id",),
    "group_keys": ("key0", "key1"),
    "reductions": ("count_u64", "checked_sum_i64"),
    "physical_partner": "numba_cuda_checked_grouped_i64x2_count_sum",
})


def _compile_action_program_for_proof(
    proof: str,
) -> NumbaGroupedI64x2CountSumProgram:
    event_type = ActionRecordType("verified_grouped_event", (
        ActionField("event_id", I64, nonnegative=True),
        ActionField("key0", I64),
        ActionField("key1", I64),
        ActionField("signed_value", I64),
    ))
    contract = RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=ActionRecordType("parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("event_id",),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference=proof,
        ),
        reductions=(
            ActionReductionSpec(
                "event_count", ("key0", "key1"), U64,
                ReductionOperator.COUNT,
                ActionScalarLiteral.from_python(U64, 0),
            ),
            ActionReductionSpec(
                "signed_sum", ("key0", "key1"), I64,
                ReductionOperator.SUM,
                ActionScalarLiteral.from_python(I64, 0),
            ),
        ),
    )
    spec = compile_restricted_action_source(_ACTION_SOURCE, contract)
    return compile_numba_grouped_i64x2_count_sum(
        spec, discharged_delivery_proofs=frozenset({proof}))


def _compile_action_program(
    producer: VerifiedEventProducerEvidence,
) -> tuple[str, NumbaGroupedI64x2CountSumProgram]:
    proof = f"v4-grouped-event-single-delivery:{producer.authority_nonce}"
    return proof, _compile_action_program_for_proof(proof)


def compile_grouped_event_reduction(
    schema: GroupedEventReductionSchema,
    producer: VerifiedEventProducerEvidence,
    *,
    lookup_tables: Sequence[I64LookupTable] = (),
) -> CompiledGroupedEventReduction:
    verify_grouped_event_schema(schema, producer, lookup_tables=lookup_tables)
    proof, program = _compile_action_program(producer)
    contract_sha = _compiled_contract_digest(schema, producer, program)
    return CompiledGroupedEventReduction(
        schema, producer.authority_nonce, proof, program, contract_sha)


def _compiled_contract_digest(
    schema: GroupedEventReductionSchema,
    producer: VerifiedEventProducerEvidence,
    program: NumbaGroupedI64x2CountSumProgram,
) -> str:
    return _digest({
        "kind": "compiled_v4_grouped_event_reduction_v1",
        "schema": schema.schema_sha256,
        "producer": producer.authority_nonce,
        "action": program.spec.semantic_digest,
        "program": program.to_metadata(),
    })


def execute_grouped_event_reduction(
    compiled: CompiledGroupedEventReduction,
    batch: VerifiedGroupedEventBatch,
) -> GroupedEventReductionResult:
    _validate_batch(batch)
    if compiled.schema != batch.schema \
            or compiled.producer_authority_nonce != batch.producer.authority_nonce:
        _fail("execution_binding", "compiled", "compiled plan and event batch differ")
    proof, canonical_program = _compile_action_program(batch.producer)
    if (
        compiled.action_program.spec.semantic_digest
        != canonical_program.spec.semantic_digest
        or compiled.action_program != canonical_program
        or compiled.delivery_proof_reference != proof
        or compiled.contract_sha256 != _compiled_contract_digest(
            batch.schema, batch.producer, canonical_program)
    ):
        _fail("compiled_plan_drift", "compiled", "grouped plan changed")
    return _execute_grouped_action_program(
        compiled.action_program, batch,
        contract_sha256=compiled.contract_sha256)


def _execute_grouped_action_program(
    program: NumbaGroupedI64x2CountSumProgram,
    batch: VerifiedGroupedEventBatch,
    *,
    contract_sha256: str,
) -> GroupedEventReductionResult:
    arrays = {
        "event_id": np.ascontiguousarray(batch.event_id, dtype=np.int64),
        "key0": np.ascontiguousarray(batch.key0, dtype=np.int64),
        "key1": np.ascontiguousarray(batch.key1, dtype=np.int64),
        "signed_value": np.ascontiguousarray(batch.signed_value, dtype=np.int64),
    }
    prepared = prepare_numba_grouped_i64x2_count_sum_columns(
        program, arrays)
    device = execute_numba_grouped_i64x2_count_sum(prepared)
    try:
        reductions = device.to_host_reductions()
        metadata = device.to_metadata()
    finally:
        device.close()
        prepared.close()
    by_name = {row.name: row for row in reductions}
    count_rows = dict(by_name["event_count"].rows)
    sum_rows = dict(by_name["signed_sum"].rows)
    keys = tuple(sorted(set(count_rows) | set(sum_rows)))
    rows = tuple(
        (int(key[0]), int(key[1]), int(count_rows[key]), int(sum_rows[key]))
        for key in keys
    )
    return GroupedEventReductionResult(
        rows, _digest(rows), contract_sha256,
        batch.producer.producer_output_sha256,
        batch.producer.traversal_receipt_sha256,
        dict(metadata),
    )


def _execute_grouped_action_program_prepared(
    program: NumbaGroupedI64x2CountSumProgram,
    batch: VerifiedGroupedEventBatch,
    *,
    contract_sha256: str,
    workspace: PreparedGroupedI64x2DeviceWorkspace,
    owner_identity_digest: str,
    query_ordinal: int,
) -> GroupedEventReductionResult:
    arrays = {
        "event_id": np.ascontiguousarray(batch.event_id, dtype=np.int64),
        "key0": np.ascontiguousarray(batch.key0, dtype=np.int64),
        "key1": np.ascontiguousarray(batch.key1, dtype=np.int64),
        "signed_value": np.ascontiguousarray(batch.signed_value, dtype=np.int64),
    }
    prepared = None
    device = None
    generation_digest = None
    try:
        try:
            prepared, generation = (
                _prepare_numba_grouped_i64x2_count_sum_canonical_host_workspace_verified(
                    program,
                    arrays,
                    private_workspace=workspace,
                    owner_identity_digest=owner_identity_digest,
                    query_ordinal=query_ordinal,
                )
            )
            generation_digest = str(generation["workspace_generation_digest"])
            device = execute_numba_grouped_i64x2_count_sum(prepared)
            reductions = device.to_host_reductions()
            metadata = device.to_metadata()
        finally:
            if device is not None:
                device.close()
            if prepared is not None:
                prepared.close()
        assert generation_digest is not None
        workspace.finish_query(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
            generation_digest=generation_digest,
        )
    except Exception:
        workspace.abort_query(
            owner_identity_digest=owner_identity_digest,
            query_ordinal=query_ordinal,
        )
        raise
    by_name = {row.name: row for row in reductions}
    count_rows = dict(by_name["event_count"].rows)
    sum_rows = dict(by_name["signed_sum"].rows)
    keys = tuple(sorted(set(count_rows) | set(sum_rows)))
    rows = tuple(
        (int(key[0]), int(key[1]), int(count_rows[key]), int(sum_rows[key]))
        for key in keys
    )
    return GroupedEventReductionResult(
        rows, _digest(rows), contract_sha256,
        batch.producer.producer_output_sha256,
        batch.producer.traversal_receipt_sha256,
        dict(metadata),
    )


class PreparedGroupedEventReductionOwner:
    """Compile one schema-owned partner and verify each live producer at execute."""

    def __init__(self, schema: GroupedEventReductionSchema, *, lookup_tables=()):
        started = time.perf_counter()
        if not isinstance(schema, GroupedEventReductionSchema) \
                or schema.schema_id != GROUPED_EVENT_SCHEMA_ID \
                or schema.schema_version != GROUPED_EVENT_SCHEMA_VERSION \
                or not isinstance(schema.maximum_event_rows, int) \
                or not 0 < schema.maximum_event_rows <= U32_MAX:
            _fail("prepared_schema", "schema", "valid closed schema required")
        by_digest: dict[str, I64LookupTable] = {}
        for index, table in enumerate(lookup_tables):
            if not isinstance(table, I64LookupTable):
                _fail("lookup", f"lookup_tables[{index}]", type(table).__name__)
            table.as_mapping()
            if table.table_sha256 in by_digest:
                _fail("duplicate_lookup_digest", "lookup_tables", table.table_sha256)
            by_digest[table.table_sha256] = table
        _verify_projection(schema.key0, label="schema.key0", lookups=by_digest)
        _verify_projection(schema.key1, label="schema.key1", lookups=by_digest)
        _verify_projection(
            schema.signed_value, label="schema.signed_value", lookups=by_digest)
        proof = f"v4-grouped-event-prepared-schema:{schema.schema_sha256}"
        program = _compile_action_program_for_proof(proof)
        specialization = eager_specialize_numba_grouped_i64x2_count_sum(program)
        self._schema = schema
        self._lookups = tuple(lookup_tables)
        self._lookup_mappings = MappingProxyType({
            digest: MappingProxyType(table.as_mapping())
            for digest, table in by_digest.items()
        })
        self._proof = proof
        self._program = program
        self._eager_specialization = dict(specialization)
        self._contract_sha256 = _digest({
            "kind": "prepared_v4_grouped_event_reduction_v1",
            "schema": schema.schema_sha256,
            "proof": proof,
            "action": program.spec.semantic_digest,
            "program": program.to_metadata(),
        })
        self._pid = os.getpid()
        self._thread = threading.get_ident()
        self._active = threading.Lock()
        self._closed = False
        self._execution_count = 0
        self.prepare_seconds = time.perf_counter() - started
        self._session_identity = _digest({
            "schema": "rtdl.v4.prepared_grouped_event_owner.v1",
            "grouped_schema": schema.schema_sha256,
            "contract": self._contract_sha256,
            "pid": self._pid,
            "thread": self._thread,
        })
        self._static_payload = (
            "rtdl.v4.prepared_grouped_event_owner.static.v1",
            id(self._schema),
            self._schema.schema_sha256,
            tuple((id(item), item.table_sha256) for item in self._lookups),
            id(self._lookup_mappings),
            tuple(
                (digest, id(mapping))
                for digest, mapping in sorted(self._lookup_mappings.items())
            ),
            id(self._program),
            self._program.spec.semantic_digest,
            self._program.event_fields,
            self._program.key_fields,
            self._program.sum_field,
            self._program.count_reduction_name,
            self._program.sum_reduction_name,
            self._program.delivery_proof_reference,
            self._contract_sha256,
            self._session_identity,
        )
        self._static_seal = hmac.new(
            _PREPARED_OWNER_KEY,
            repr(self._static_payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self._workspace = PreparedGroupedI64x2DeviceWorkspace(
            owner_identity_digest=self._session_identity,
            max_row_count=schema.maximum_event_rows,
        )

    def __getstate__(self):
        raise RuntimeError("prepared grouped-event owner cannot be serialized")

    def _check(self):
        if self._closed:
            raise RuntimeError("prepared grouped-event owner is closed")
        if os.getpid() != self._pid:
            raise RuntimeError("prepared grouped-event owner crossed process boundary")
        if threading.get_ident() != self._thread:
            raise RuntimeError("prepared grouped-event owner crossed thread boundary")

    def _check_static_authority(self):
        current = (
            "rtdl.v4.prepared_grouped_event_owner.static.v1",
            id(self._schema),
            self._schema.schema_sha256,
            tuple((id(item), item.table_sha256) for item in self._lookups),
            id(self._lookup_mappings),
            tuple(
                (digest, id(mapping))
                for digest, mapping in sorted(self._lookup_mappings.items())
            ),
            id(self._program),
            self._program.spec.semantic_digest,
            self._program.event_fields,
            self._program.key_fields,
            self._program.sum_field,
            self._program.count_reduction_name,
            self._program.sum_reduction_name,
            self._program.delivery_proof_reference,
            self._contract_sha256,
            self._session_identity,
        )
        if (
            current != self._static_payload
            or not hmac.compare_digest(
                self._static_seal,
                hmac.new(
                    _PREPARED_OWNER_KEY,
                    repr(current).encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest(),
            )
        ):
            _fail(
                "prepared_static_authority",
                "prepared",
                "schema, lookup, program, or contract changed after prepare",
            )

    @property
    def lifecycle_receipt(self):
        self._check()
        self._check_static_authority()
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "session_identity": self._session_identity,
            "process_bound": True, "thread_bound": True,
            "nonserializable": True, "nonreentrant": True,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
            "execution_count": self._execution_count,
            "grouped_schema_sha256": self._schema.schema_sha256,
            "program_contract_sha256": self._contract_sha256,
            "eager_specialization": dict(self._eager_specialization),
            "first_execute_may_trigger_numba_jit": False,
        }

    def execute(self, producer: VerifiedEventProducerEvidence):
        self._check()
        self._check_static_authority()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("prepared grouped-event owner is already executing")
        try:
            batch = _materialize_prepared_grouped_event_batch(
                self._schema,
                producer,
                lookup_mappings=self._lookup_mappings,
            )
            result = _execute_grouped_action_program_prepared(
                self._program,
                batch,
                contract_sha256=self._contract_sha256,
                workspace=self._workspace,
                owner_identity_digest=self._session_identity,
                query_ordinal=self._execution_count,
            )
            self._execution_count += 1
            return result, batch
        finally:
            self._active.release()

    def close(self):
        self._check()
        if not self._active.acquire(blocking=False):
            raise RuntimeError("cannot close prepared grouped-event owner during execution")
        try:
            workspace = getattr(self, "_workspace", None)
            if workspace is not None:
                workspace.close()
            self._closed = True
        finally:
            self._active.release()

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def reference_grouped_i64x2_count_sum(
    batch: VerifiedGroupedEventBatch,
) -> tuple[tuple[int, int, int, int], ...]:
    """Route-independent exact CPU oracle over a sealed event batch."""

    _validate_batch(batch)
    grouped: dict[tuple[int, int], tuple[int, int]] = {}
    for index, (key0, key1, value) in enumerate(zip(
            batch.key0, batch.key1, batch.signed_value, strict=True)):
        key = (key0, key1)
        count, total = grouped.get(key, (0, 0))
        count += 1
        total += value
        if count > U64_MAX:
            _fail("count_overflow", f"rows[{index}]", repr(key))
        if not I64_MIN <= total <= I64_MAX:
            _fail("signed_reduction_overflow", f"rows[{index}]", repr(key))
        grouped[key] = (count, total)
    return tuple(
        (key0, key1, grouped[(key0, key1)][0], grouped[(key0, key1)][1])
        for key0, key1 in sorted(grouped)
    )


def product_source_has_forbidden_identity_dispatch(source: str) -> bool:
    return bool(re.search(
        r"\b(rayjoin|paper|publication|application_id|app_id)\b\s*(?:==|in\s*[\{\[])",
        source.lower(),
    ))


__all__ = [
    "CompiledGroupedEventReduction", "EventFieldProjection",
    "EventFieldSource", "EventProducerCompletionKind", "GROUPED_EVENT_SCHEMA_ID",
    "GROUPED_EVENT_SCHEMA_VERSION", "GROUPED_EVENT_TEMPLATE_SHA256",
    "GroupedEventReductionError",
    "GroupedEventReductionResult", "GroupedEventReductionSchema",
    "I64LookupTable", "VerifiedEventProducerEvidence",
    "PreparedGroupedEventReductionOwner", "VerifiedGroupedEventBatch",
    "compile_grouped_event_reduction",
    "execute_grouped_event_reduction", "materialize_verified_grouped_event_batch",
    "product_source_has_forbidden_identity_dispatch",
    "reference_grouped_i64x2_count_sum", "verify_event_producer_evidence",
    "verify_grouped_event_schema",
]
