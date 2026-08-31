"""Event-derived evidence for closed compiler-owned operation sequences.

This module is deliberately app-neutral.  It records an operation only after
the trusted runtime callable implementing that operation returns successfully.
The resulting receipt proves that the instrumented compiler/runtime path
reported the declared ordered operations.  It is *not* hardware introspection:
it does not independently count opaque partner kernels, driver work, or GPU
instructions.  Those limits are part of the receipt's TCB statement.

The evidence layer is intentionally separate from timing.  It records no
durations and offers no mechanism for choosing a plan from an app, dataset,
result, or observed cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Callable, Mapping, TypeVar


OPERATION_SEQUENCE_SCHEMA = "rtdl.v4.operation_sequence_contract.v1"
OPERATION_RECEIPT_SCHEMA = "rtdl.v4.operation_evidence_receipt.v1"
OPERATION_EVENT_SCHEMA = "rtdl.v4.operation_evidence_event.v1"
OPERATION_EVIDENCE_TCB = (
    "trusted_runtime_records_each_compiler_instrumented_operation_only_after_"
    "its_callable_returns_successfully__not_hardware_or_opaque_partner_kernel_"
    "introspection"
)

_ID = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_NONCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{15,255}")
_U64_MAX = (1 << 64) - 1
_T = TypeVar("_T")
_PREVERIFIED_TRACE_AUTHORITY_ISSUER = object()


class OperationEvidenceError(ValueError):
    """Stable fail-closed diagnostic for operation evidence."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 operation evidence rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise OperationEvidenceError(code, path, message)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _fail("canonical_json", "value", str(exc))


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail("sha256", path, repr(value))
    return value


def _identifier(value: object, path: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        _fail("identifier", path, repr(value))
    return value


def _u64(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= _U64_MAX:
        _fail("u64", path, repr(value))
    return value


class OperationKind(str, Enum):
    """Closed compiler-visible operation classes.

    ``LOGICAL_REDUCTION`` does not assert a count of opaque partner kernels.
    ``COMPILER_KERNEL_INVOCATION`` is reserved for a kernel launched directly
    by the compiler-owned runtime.
    """

    DEVICE_MATERIALIZATION = "device_materialization"
    LOGICAL_REDUCTION = "logical_reduction"
    COMPILER_KERNEL_INVOCATION = "compiler_kernel_invocation"
    HOST_COPY_SYNCHRONIZATION = "host_copy_synchronization"


@dataclass(frozen=True)
class OperationRequirement:
    """One exact position in an operation sequence.

    Runtime extents are affine in ``value_count``.  This is sufficient for the
    current closed U64 reducer while keeping the evidence mechanism generic.
    """

    ordinal: int
    operation_id: str
    kind: OperationKind
    units_per_value: int = 0
    fixed_units: int = 0
    bytes_per_unit: int = 0
    fixed_bytes: int = 0
    host_visibility_boundary: bool = False
    compiler_visible_only: bool = True

    def validate(self, *, path: str) -> None:
        _u64(self.ordinal, path + ".ordinal")
        _identifier(self.operation_id, path + ".operation_id")
        if not isinstance(self.kind, OperationKind):
            _fail("operation_kind", path + ".kind", repr(self.kind))
        for name in (
            "units_per_value", "fixed_units", "bytes_per_unit", "fixed_bytes",
        ):
            _u64(getattr(self, name), path + "." + name)
        if not isinstance(self.host_visibility_boundary, bool):
            _fail("boolean", path + ".host_visibility_boundary", repr(
                self.host_visibility_boundary))
        if not isinstance(self.compiler_visible_only, bool):
            _fail("boolean", path + ".compiler_visible_only", repr(
                self.compiler_visible_only))
        if self.units_per_value == 0 and self.fixed_units == 0:
            _fail("empty_extent", path, "operation must account for at least one unit")
        if self.kind is OperationKind.HOST_COPY_SYNCHRONIZATION \
                and not self.host_visibility_boundary:
            _fail("host_visibility", path, "host copy/sync must expose a boundary")
        if self.kind is not OperationKind.HOST_COPY_SYNCHRONIZATION \
                and self.host_visibility_boundary:
            _fail("host_visibility", path, "only host copy/sync exposes a boundary")

    def resolve(self, value_count: int) -> tuple[int, int]:
        self.validate(path=f"requirements[{self.ordinal}]")
        count = _u64(value_count, "value_count")
        units = self.units_per_value * count + self.fixed_units
        byte_count = self.bytes_per_unit * units + self.fixed_bytes
        _u64(units, f"requirements[{self.ordinal}].resolved_units")
        _u64(byte_count, f"requirements[{self.ordinal}].resolved_bytes")
        return units, byte_count

    def to_dict(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "operation_id": self.operation_id,
            "kind": self.kind.value,
            "units_per_value": self.units_per_value,
            "fixed_units": self.fixed_units,
            "bytes_per_unit": self.bytes_per_unit,
            "fixed_bytes": self.fixed_bytes,
            "host_visibility_boundary": self.host_visibility_boundary,
            "compiler_visible_only": self.compiler_visible_only,
        }


@dataclass(frozen=True)
class OperationSequenceContract:
    plan_sha256: str
    mechanism_id: str
    variant: str
    declared_value_count: int
    requirements: tuple[OperationRequirement, ...]
    schema: str = OPERATION_SEQUENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "plan_sha256": self.plan_sha256,
            "mechanism_id": self.mechanism_id,
            "variant": self.variant,
            "declared_value_count": self.declared_value_count,
            "requirements": [item.to_dict() for item in self.requirements],
            "tcb_statement": OPERATION_EVIDENCE_TCB,
            "timing_or_duration_recorded": False,
            "hardware_introspection_claimed": False,
        }

    @property
    def contract_sha256(self) -> str:
        return _digest(self.payload_without_digest())

    def to_dict(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "contract_sha256": self.contract_sha256}


def verify_operation_sequence_contract(
    contract: OperationSequenceContract,
) -> OperationSequenceContract:
    if not isinstance(contract, OperationSequenceContract):
        _fail("contract_type", "contract", type(contract).__name__)
    if contract.schema != OPERATION_SEQUENCE_SCHEMA:
        _fail("contract_schema", "contract.schema", contract.schema)
    _sha(contract.plan_sha256, "contract.plan_sha256")
    _identifier(contract.mechanism_id, "contract.mechanism_id")
    _identifier(contract.variant, "contract.variant")
    _u64(contract.declared_value_count, "contract.declared_value_count")
    if contract.declared_value_count == 0:
        _fail("value_count", "contract.declared_value_count", "nonempty domain required")
    if not contract.requirements:
        _fail("requirements_empty", "contract.requirements", "at least one required")
    ids: set[str] = set()
    for index, requirement in enumerate(contract.requirements):
        requirement.validate(path=f"contract.requirements[{index}]")
        if requirement.ordinal != index:
            _fail("requirement_order", f"contract.requirements[{index}]", str(
                requirement.ordinal))
        if requirement.operation_id in ids:
            _fail("requirement_duplicate", f"contract.requirements[{index}]",
                  requirement.operation_id)
        ids.add(requirement.operation_id)
    return contract


class _PreverifiedOperationTraceAuthority:
    """Opaque process-local admission for one operation trace.

    Construction performs the full ordered-requirement validation once, before
    a registered execution interval.  The trusted runtime may then construct a
    trace without repeating the variant-dependent two-versus-seven validation
    in that interval.  This is an in-process phase-boundary capability, not a
    serializable receipt or a hostile-same-process security boundary.
    """

    __slots__ = ("_contract", "_execution_nonce", "_value_count")

    def __init__(
        self,
        contract: OperationSequenceContract,
        *,
        execution_nonce: str,
        value_count: int,
        _issuer: object,
    ) -> None:
        if _issuer is not _PREVERIFIED_TRACE_AUTHORITY_ISSUER:
            raise TypeError("preverified operation trace authority is opaque")
        self._contract = contract
        self._execution_nonce = execution_nonce
        self._value_count = value_count

    def __copy__(self):
        raise TypeError("preverified operation trace authority is not copyable")

    def __deepcopy__(self, _memo):
        raise TypeError("preverified operation trace authority is not copyable")

    def __reduce__(self):
        raise TypeError("preverified operation trace authority is not serializable")


def preverify_operation_trace_authority(
    contract: OperationSequenceContract,
    *,
    execution_nonce: str,
    value_count: int,
) -> object:
    """Deep-verify and bind one trace admission outside registered execution."""

    verified = verify_operation_sequence_contract(contract)
    if not isinstance(execution_nonce, str) or _NONCE.fullmatch(execution_nonce) is None:
        _fail("execution_nonce", "execution_nonce", repr(execution_nonce))
    checked_value_count = _u64(value_count, "value_count")
    if checked_value_count == 0:
        _fail("value_count", "value_count", "nonempty reducer domain required")
    if checked_value_count != verified.declared_value_count:
        _fail(
            "value_count_binding", "value_count",
            f"expected {verified.declared_value_count}, got {checked_value_count}",
        )
    return _PreverifiedOperationTraceAuthority(
        verified,
        execution_nonce=execution_nonce,
        value_count=checked_value_count,
        _issuer=_PREVERIFIED_TRACE_AUTHORITY_ISSUER,
    )


@dataclass(frozen=True)
class OperationEvent:
    sequence: int
    operation_id: str
    kind: str
    accounted_units: int
    accounted_bytes: int
    previous_event_sha256: str
    event_sha256: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": OPERATION_EVENT_SCHEMA,
            "sequence": self.sequence,
            "operation_id": self.operation_id,
            "kind": self.kind,
            "accounted_units": self.accounted_units,
            "accounted_bytes": self.accounted_bytes,
            "previous_event_sha256": self.previous_event_sha256,
            "recorded_after_callable_success": True,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "event_sha256": self.event_sha256}


@dataclass(frozen=True)
class _SuccessfulOperation:
    """Unsealed successful event retained without JSON or digest work."""

    sequence: int
    operation_id: str
    kind: str
    accounted_units: int
    accounted_bytes: int


@dataclass(frozen=True)
class OperationEvidenceReceipt:
    contract_sha256: str
    plan_sha256: str
    mechanism_id: str
    variant: str
    execution_nonce: str
    value_count: int
    output_sha256: str
    traversal_receipt_sha256: str
    events: tuple[OperationEvent, ...]
    event_chain_sha256: str
    receipt_sha256: str
    schema: str = OPERATION_RECEIPT_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_sha256": self.contract_sha256,
            "plan_sha256": self.plan_sha256,
            "mechanism_id": self.mechanism_id,
            "variant": self.variant,
            "execution_nonce": self.execution_nonce,
            "value_count": self.value_count,
            "output_sha256": self.output_sha256,
            "traversal_receipt_sha256": self.traversal_receipt_sha256,
            "events": [item.to_dict() for item in self.events],
            "event_chain_sha256": self.event_chain_sha256,
            "successful_event_count": len(self.events),
            "event_evidence_tcb": OPERATION_EVIDENCE_TCB,
            "hardware_introspection_claimed": False,
            "opaque_partner_kernel_count_claimed": False,
            "timing_or_duration_recorded": False,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "receipt_sha256": self.receipt_sha256}


class OperationTrace:
    """Single-use trusted-runtime recorder for one declared sequence."""

    __slots__ = (
        "_contract", "_execution_nonce", "_value_count", "_events", "_state",
    )

    def __init__(
        self,
        contract: OperationSequenceContract,
        *,
        execution_nonce: str,
        value_count: int,
    ) -> None:
        self._contract = verify_operation_sequence_contract(contract)
        if not isinstance(execution_nonce, str) or _NONCE.fullmatch(execution_nonce) is None:
            _fail("execution_nonce", "execution_nonce", repr(execution_nonce))
        self._execution_nonce = execution_nonce
        self._value_count = _u64(value_count, "value_count")
        if self._value_count == 0:
            _fail("value_count", "value_count", "nonempty reducer domain required")
        if self._value_count != self._contract.declared_value_count:
            _fail(
                "value_count_binding", "value_count",
                f"expected {self._contract.declared_value_count}, got {self._value_count}",
            )
        self._events: list[_SuccessfulOperation] = []
        self._state = "open"

    @classmethod
    def from_preverified_authority(cls, authority: object) -> "OperationTrace":
        """Construct from an opaque admission without revalidating its sequence."""

        if type(authority) is not _PreverifiedOperationTraceAuthority:
            _fail(
                "preverified_authority_type",
                "authority",
                type(authority).__name__,
            )
        trace = cls.__new__(cls)
        trace._contract = authority._contract
        trace._execution_nonce = authority._execution_nonce
        trace._value_count = authority._value_count
        trace._events = []
        trace._state = "open"
        return trace

    @property
    def state(self) -> str:
        return self._state

    def successful_event_counts(self) -> dict[str, int]:
        """Return counts reconstructed from the events actually recorded.

        This accessor is intentionally available only after the complete
        declared sequence has executed successfully and before/following
        finalization.  It is not a second source of evidence: the finalized
        receipt remains authoritative, while callers that expose a compact
        diagnostic summary can derive it from the same successful events
        instead of restating plan constants.
        """

        if self._state not in {"open", "completed_unsealed", "finalized"}:
            _fail("trace_state", "trace", self._state)
        if len(self._events) != len(self._contract.requirements):
            _fail(
                "operation_sequence_incomplete",
                "events",
                f"{len(self._events)}/{len(self._contract.requirements)}",
            )
        counts = {kind.value: 0 for kind in OperationKind}
        for event in self._events:
            counts[event.kind] += 1
        return counts

    def abort(self) -> None:
        if self._state in {"open", "completed_unsealed"}:
            self._state = "aborted"

    def execute(self, operation_id: str, action: Callable[[], _T]) -> _T:
        """Run the next trusted operation and record it only after success."""

        if self._state != "open":
            _fail("trace_state", "trace", self._state)
        if not callable(action):
            self.abort()
            _fail("operation_callable", "action", type(action).__name__)
        index = len(self._events)
        if index >= len(self._contract.requirements):
            self.abort()
            _fail("unexpected_operation", "operation_id", operation_id)
        requirement = self._contract.requirements[index]
        if operation_id != requirement.operation_id:
            self.abort()
            _fail(
                "operation_order",
                f"events[{index}]",
                f"expected {requirement.operation_id!r}, got {operation_id!r}",
            )
        try:
            result = action()
            # Evidence construction is part of the single fail-closed
            # transaction.  A successful side effect followed by an extent or
            # canonicalization failure must not leave a reusable open trace.
            units, byte_count = requirement.resolve(self._value_count)
            self._events.append(_SuccessfulOperation(
                sequence=index,
                operation_id=requirement.operation_id,
                kind=requirement.kind.value,
                accounted_units=units,
                accounted_bytes=byte_count,
            ))
        except BaseException:
            self.abort()
            raise
        return result

    def complete(self) -> "OperationTrace":
        """Freeze a complete successful sequence without hashing receipts."""

        if self._state != "open":
            _fail("trace_state", "trace", self._state)
        if len(self._events) != len(self._contract.requirements):
            self.abort()
            _fail(
                "operation_sequence_incomplete",
                "events",
                f"{len(self._events)}/{len(self._contract.requirements)}",
            )
        self._state = "completed_unsealed"
        return self

    def seal(
        self,
        *,
        output_sha256: str,
        traversal_receipt_sha256: str,
    ) -> OperationEvidenceReceipt:
        """Build the digest chain and receipt after the measured device path."""

        if self._state != "completed_unsealed":
            _fail("trace_state", "trace", self._state)
        output = _sha(output_sha256, "output_sha256")
        traversal = _sha(traversal_receipt_sha256, "traversal_receipt_sha256")
        finalized_events: list[OperationEvent] = []
        previous = self._contract.contract_sha256
        for raw in self._events:
            body = {
                "schema": OPERATION_EVENT_SCHEMA,
                "sequence": raw.sequence,
                "operation_id": raw.operation_id,
                "kind": raw.kind,
                "accounted_units": raw.accounted_units,
                "accounted_bytes": raw.accounted_bytes,
                "previous_event_sha256": previous,
                "recorded_after_callable_success": True,
            }
            event_sha = _digest(body)
            finalized_events.append(OperationEvent(
                sequence=raw.sequence,
                operation_id=raw.operation_id,
                kind=raw.kind,
                accounted_units=raw.accounted_units,
                accounted_bytes=raw.accounted_bytes,
                previous_event_sha256=previous,
                event_sha256=event_sha,
            ))
            previous = event_sha
        chain = previous
        unsigned = {
            "schema": OPERATION_RECEIPT_SCHEMA,
            "contract_sha256": self._contract.contract_sha256,
            "plan_sha256": self._contract.plan_sha256,
            "mechanism_id": self._contract.mechanism_id,
            "variant": self._contract.variant,
            "execution_nonce": self._execution_nonce,
            "value_count": self._value_count,
            "output_sha256": output,
            "traversal_receipt_sha256": traversal,
            "events": [item.to_dict() for item in finalized_events],
            "event_chain_sha256": chain,
            "successful_event_count": len(self._events),
            "event_evidence_tcb": OPERATION_EVIDENCE_TCB,
            "hardware_introspection_claimed": False,
            "opaque_partner_kernel_count_claimed": False,
            "timing_or_duration_recorded": False,
        }
        receipt = OperationEvidenceReceipt(
            contract_sha256=self._contract.contract_sha256,
            plan_sha256=self._contract.plan_sha256,
            mechanism_id=self._contract.mechanism_id,
            variant=self._contract.variant,
            execution_nonce=self._execution_nonce,
            value_count=self._value_count,
            output_sha256=output,
            traversal_receipt_sha256=traversal,
            events=tuple(finalized_events),
            event_chain_sha256=chain,
            receipt_sha256=_digest(unsigned),
        )
        self._state = "finalized"
        return receipt

    def finalize(
        self,
        *,
        output_sha256: str,
        traversal_receipt_sha256: str,
    ) -> OperationEvidenceReceipt:
        """Backward-compatible immediate complete-and-seal wrapper."""

        if self._state == "open":
            self.complete()
        return self.seal(
            output_sha256=output_sha256,
            traversal_receipt_sha256=traversal_receipt_sha256,
        )


def verify_operation_evidence_receipt(
    receipt: OperationEvidenceReceipt,
    contract: OperationSequenceContract,
    *,
    expected_execution_nonce: str | None = None,
) -> OperationEvidenceReceipt:
    """Reconstruct a receipt without trusting its summary counters."""

    contract = verify_operation_sequence_contract(contract)
    if not isinstance(receipt, OperationEvidenceReceipt):
        _fail("receipt_type", "receipt", type(receipt).__name__)
    if receipt.schema != OPERATION_RECEIPT_SCHEMA:
        _fail("receipt_schema", "receipt.schema", receipt.schema)
    if receipt.contract_sha256 != contract.contract_sha256 \
            or receipt.plan_sha256 != contract.plan_sha256 \
            or receipt.mechanism_id != contract.mechanism_id \
            or receipt.variant != contract.variant:
        _fail("receipt_contract_binding", "receipt", "contract identity mismatch")
    if expected_execution_nonce is not None \
            and receipt.execution_nonce != expected_execution_nonce:
        _fail("receipt_replay", "receipt.execution_nonce", receipt.execution_nonce)
    if _NONCE.fullmatch(receipt.execution_nonce) is None:
        _fail("execution_nonce", "receipt.execution_nonce", receipt.execution_nonce)
    value_count = _u64(receipt.value_count, "receipt.value_count")
    if value_count == 0:
        _fail("value_count", "receipt.value_count", "nonempty reducer domain required")
    if value_count != contract.declared_value_count:
        _fail("value_count_binding", "receipt.value_count", str(value_count))
    _sha(receipt.output_sha256, "receipt.output_sha256")
    _sha(receipt.traversal_receipt_sha256, "receipt.traversal_receipt_sha256")
    if len(receipt.events) != len(contract.requirements):
        _fail("event_count", "receipt.events", str(len(receipt.events)))
    previous = contract.contract_sha256
    for index, (event, requirement) in enumerate(zip(
            receipt.events, contract.requirements, strict=True)):
        if not isinstance(event, OperationEvent):
            _fail("event_type", f"receipt.events[{index}]", type(event).__name__)
        units, byte_count = requirement.resolve(value_count)
        expected = {
            "schema": OPERATION_EVENT_SCHEMA,
            "sequence": index,
            "operation_id": requirement.operation_id,
            "kind": requirement.kind.value,
            "accounted_units": units,
            "accounted_bytes": byte_count,
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        if event.payload_without_digest() != expected:
            _fail("event_content", f"receipt.events[{index}]", "unexpected event")
        expected_digest = _digest(expected)
        if event.event_sha256 != expected_digest:
            _fail("event_digest", f"receipt.events[{index}]", event.event_sha256)
        previous = expected_digest
    if receipt.event_chain_sha256 != previous:
        _fail("event_chain", "receipt.event_chain_sha256", receipt.event_chain_sha256)
    if receipt.receipt_sha256 != _digest(receipt.payload_without_digest()):
        _fail("receipt_digest", "receipt.receipt_sha256", receipt.receipt_sha256)
    return receipt


def receipt_from_mapping(value: Mapping[str, object]) -> OperationEvidenceReceipt:
    """Strictly parse one portable receipt mapping for independent recounts."""

    if not isinstance(value, Mapping):
        _fail("receipt_mapping", "receipt", type(value).__name__)
    expected = {
        "schema", "contract_sha256", "plan_sha256", "mechanism_id", "variant",
        "execution_nonce", "value_count", "output_sha256",
        "traversal_receipt_sha256", "events", "event_chain_sha256",
        "successful_event_count", "event_evidence_tcb",
        "hardware_introspection_claimed", "opaque_partner_kernel_count_claimed",
        "timing_or_duration_recorded", "receipt_sha256",
    }
    if set(value) != expected:
        _fail("receipt_fields", "receipt", repr(sorted(set(value) ^ expected)))
    raw_events = value["events"]
    if not isinstance(raw_events, list):
        _fail("events_type", "receipt.events", type(raw_events).__name__)
    events: list[OperationEvent] = []
    event_fields = {
        "schema", "sequence", "operation_id", "kind", "accounted_units",
        "accounted_bytes", "previous_event_sha256",
        "recorded_after_callable_success", "event_sha256",
    }
    for index, row in enumerate(raw_events):
        if not isinstance(row, Mapping) or set(row) != event_fields:
            _fail("event_fields", f"receipt.events[{index}]", repr(row))
        if row["schema"] != OPERATION_EVENT_SCHEMA \
                or row["recorded_after_callable_success"] is not True:
            _fail("event_schema", f"receipt.events[{index}]", repr(row))
        events.append(OperationEvent(
            sequence=_u64(row["sequence"], f"receipt.events[{index}].sequence"),
            operation_id=_identifier(
                row["operation_id"], f"receipt.events[{index}].operation_id"),
            kind=_identifier(row["kind"], f"receipt.events[{index}].kind"),
            accounted_units=_u64(
                row["accounted_units"], f"receipt.events[{index}].accounted_units"),
            accounted_bytes=_u64(
                row["accounted_bytes"], f"receipt.events[{index}].accounted_bytes"),
            previous_event_sha256=_sha(
                row["previous_event_sha256"],
                f"receipt.events[{index}].previous_event_sha256"),
            event_sha256=_sha(
                row["event_sha256"], f"receipt.events[{index}].event_sha256"),
        ))
    if value["successful_event_count"] != len(events) \
            or value["event_evidence_tcb"] != OPERATION_EVIDENCE_TCB \
            or value["hardware_introspection_claimed"] is not False \
            or value["opaque_partner_kernel_count_claimed"] is not False \
            or value["timing_or_duration_recorded"] is not False:
        _fail("receipt_boundary", "receipt", "claim-boundary fields changed")
    return OperationEvidenceReceipt(
        contract_sha256=_sha(value["contract_sha256"], "receipt.contract_sha256"),
        plan_sha256=_sha(value["plan_sha256"], "receipt.plan_sha256"),
        mechanism_id=_identifier(value["mechanism_id"], "receipt.mechanism_id"),
        variant=_identifier(value["variant"], "receipt.variant"),
        execution_nonce=str(value["execution_nonce"]),
        value_count=_u64(value["value_count"], "receipt.value_count"),
        output_sha256=_sha(value["output_sha256"], "receipt.output_sha256"),
        traversal_receipt_sha256=_sha(
            value["traversal_receipt_sha256"], "receipt.traversal_receipt_sha256"),
        events=tuple(events),
        event_chain_sha256=_sha(
            value["event_chain_sha256"], "receipt.event_chain_sha256"),
        receipt_sha256=_sha(value["receipt_sha256"], "receipt.receipt_sha256"),
    )


__all__ = (
    "OPERATION_EVIDENCE_TCB",
    "OperationEvidenceError",
    "OperationEvidenceReceipt",
    "OperationEvent",
    "OperationKind",
    "OperationRequirement",
    "OperationSequenceContract",
    "OperationTrace",
    "preverify_operation_trace_authority",
    "receipt_from_mapping",
    "verify_operation_evidence_receipt",
    "verify_operation_sequence_contract",
)
