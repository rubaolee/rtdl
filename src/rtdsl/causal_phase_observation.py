from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps
import json
import time
from typing import Any, Callable, Iterator, Mapping, NoReturn


CAUSAL_PHASE_OBSERVATION_VERSION = (
    "rtdl.causal_phase_observation.private_observation_only.v1"
)


@dataclass(frozen=True)
class CausalPhaseObservationIssue:
    code: str
    path: str
    message: str


class CausalPhaseObservationError(ValueError):
    def __init__(self, issue: CausalPhaseObservationIssue) -> None:
        self.issue = issue
        super().__init__(
            "Causal phase observation failed: "
            f"{issue.code}@{issue.path}: {issue.message}"
        )


class CausalPhaseObservation:
    """Record nested call costs without selecting or changing an execution.

    The observer is deliberately independent of Action planning, lowering,
    backend selection, and application identity.  Inclusive durations describe
    call boundaries.  Exclusive durations subtract direct-child inclusive
    durations so nested observations are never presented as additive savings.
    """

    def __init__(
        self,
        *,
        identity: Mapping[str, object],
        clock_ns: Callable[[], int] = time.perf_counter_ns,
    ) -> None:
        self._identity = _json_mapping(identity, path="identity")
        self._clock_ns = clock_ns
        self._started_ns = _clock_value(clock_ns, path="clock.started_ns")
        self._stack: list[dict[str, object]] = []
        self._events: list[dict[str, object]] = []
        self._finished = False
        self._next_event_id = 0

    @contextmanager
    def observe(
        self,
        label: str,
        *,
        category: str,
        metadata: Mapping[str, object] | None = None,
    ) -> Iterator[None]:
        self._require_open()
        clean_label = _nonempty_string(label, path="event.label")
        clean_category = _nonempty_string(category, path="event.category")
        clean_metadata = _json_mapping(
            {} if metadata is None else metadata,
            path=f"events.{clean_label}.metadata",
        )
        event_id = self._next_event_id
        self._next_event_id += 1
        parent_event_id = (
            int(self._stack[-1]["event_id"]) if self._stack else None
        )
        event: dict[str, object] = {
            "event_id": event_id,
            "parent_event_id": parent_event_id,
            "depth": len(self._stack),
            "label": clean_label,
            "category": clean_category,
            "metadata": clean_metadata,
            "started_ns": _clock_value(
                self._clock_ns,
                path=f"events.{event_id}.started_ns",
            ),
            "direct_child_elapsed_ns": 0,
            "completed": False,
            "error_type": None,
        }
        self._stack.append(event)
        try:
            yield
        except BaseException as error:
            event["error_type"] = type(error).__name__
            raise
        finally:
            finished_ns = _clock_value(
                self._clock_ns,
                path=f"events.{event_id}.finished_ns",
            )
            if not self._stack or self._stack[-1] is not event:
                _fail(
                    "observation_stack_corrupt",
                    f"events.{event_id}",
                    clean_label,
                )
            self._stack.pop()
            started_ns = int(event["started_ns"])
            elapsed_ns = finished_ns - started_ns
            child_ns = int(event["direct_child_elapsed_ns"])
            if elapsed_ns < 0:
                _fail(
                    "negative_event_duration",
                    f"events.{event_id}.elapsed_ns",
                    str(elapsed_ns),
                )
            if child_ns > elapsed_ns:
                _fail(
                    "child_duration_exceeds_parent",
                    f"events.{event_id}.direct_child_elapsed_ns",
                    f"children={child_ns}; parent={elapsed_ns}",
                )
            event["finished_ns"] = finished_ns
            event["elapsed_ns"] = elapsed_ns
            event["exclusive_ns"] = elapsed_ns - child_ns
            event["completed"] = True
            self._events.append(event)
            if self._stack:
                self._stack[-1]["direct_child_elapsed_ns"] = (
                    int(self._stack[-1]["direct_child_elapsed_ns"])
                    + elapsed_ns
                )

    def wrap_call(
        self,
        function: Callable[..., Any],
        *,
        label: str,
        category: str,
        metadata_factory: (
            Callable[[tuple[object, ...], dict[str, object]], Mapping[str, object]]
            | None
        ) = None,
    ) -> Callable[..., Any]:
        """Return a transparent timing wrapper for one existing callable."""

        if not callable(function):
            _fail("target_not_callable", "function", repr(function))
        clean_label = _nonempty_string(label, path="wrapper.label")
        clean_category = _nonempty_string(category, path="wrapper.category")

        @wraps(function)
        def observed(*args, **kwargs):
            metadata = (
                {}
                if metadata_factory is None
                else metadata_factory(tuple(args), dict(kwargs))
            )
            with self.observe(
                clean_label,
                category=clean_category,
                metadata=metadata,
            ):
                return function(*args, **kwargs)

        return observed

    def finish(self) -> dict[str, object]:
        self._require_open()
        if self._stack:
            _fail(
                "active_observation_at_finish",
                "observation",
                str(self._stack[-1]["label"]),
            )
        finished_ns = _clock_value(
            self._clock_ns,
            path="clock.finished_ns",
        )
        route_elapsed_ns = finished_ns - self._started_ns
        if route_elapsed_ns < 0:
            _fail(
                "negative_route_duration",
                "reconciliation.route_elapsed_ns",
                str(route_elapsed_ns),
            )
        ordered = sorted(self._events, key=lambda row: int(row["event_id"]))
        roots = [row for row in ordered if row["parent_event_id"] is None]
        root_inclusive_ns = sum(int(row["elapsed_ns"]) for row in roots)
        if root_inclusive_ns > route_elapsed_ns:
            _fail(
                "root_duration_exceeds_route",
                "reconciliation.root_inclusive_ns",
                f"roots={root_inclusive_ns}; route={route_elapsed_ns}",
            )
        event_exclusive_ns = sum(int(row["exclusive_ns"]) for row in ordered)
        if event_exclusive_ns != root_inclusive_ns:
            _fail(
                "exclusive_reconciliation_failed",
                "reconciliation.event_exclusive_ns",
                f"exclusive={event_exclusive_ns}; roots={root_inclusive_ns}",
            )
        self._finished = True
        return {
            "schema": CAUSAL_PHASE_OBSERVATION_VERSION,
            "status": "complete_observation_only",
            "identity": deepcopy(self._identity),
            "clock": {
                "name": "perf_counter_ns",
                "unit": "nanoseconds",
                "monotonic_required": True,
            },
            "events": [_public_event(row) for row in ordered],
            "reconciliation": {
                "route_elapsed_ns": route_elapsed_ns,
                "root_inclusive_ns": root_inclusive_ns,
                "event_exclusive_ns": event_exclusive_ns,
                "unobserved_route_ns": route_elapsed_ns - root_inclusive_ns,
                "nested_inclusive_durations_are_additive": False,
                "exclusive_durations_are_additive_within_observed_roots": True,
                "passed": True,
            },
            "claim_boundary": {
                "observation_only": True,
                "placement_or_execution_changed": False,
                "algorithm_changed": False,
                "timer_boundary_changed": False,
                "performance_result_claimed": False,
                "predicted_saving_claimed": False,
            },
        }

    def _require_open(self) -> None:
        if self._finished:
            _fail(
                "observation_already_finished",
                "observation",
                CAUSAL_PHASE_OBSERVATION_VERSION,
            )


@contextmanager
def patch_observed_call(
    owner: object,
    attribute: str,
    observer: CausalPhaseObservation,
    *,
    label: str,
    category: str,
    metadata_factory: (
        Callable[[tuple[object, ...], dict[str, object]], Mapping[str, object]]
        | None
    ) = None,
) -> Iterator[None]:
    """Temporarily wrap one callable and restore the exact original object."""

    clean_attribute = _nonempty_string(attribute, path="patch.attribute")
    if not hasattr(owner, clean_attribute):
        _fail(
            "patch_attribute_missing",
            f"patch.{clean_attribute}",
            type(owner).__name__,
        )
    original = getattr(owner, clean_attribute)
    wrapped = observer.wrap_call(
        original,
        label=label,
        category=category,
        metadata_factory=metadata_factory,
    )
    setattr(owner, clean_attribute, wrapped)
    try:
        yield
    finally:
        changed = getattr(owner, clean_attribute) is not wrapped
        setattr(owner, clean_attribute, original)
        if changed:
            _fail(
                "patch_target_changed_during_observation",
                f"patch.{clean_attribute}",
                type(owner).__name__,
            )


def _public_event(event: Mapping[str, object]) -> dict[str, object]:
    return {
        "event_id": int(event["event_id"]),
        "parent_event_id": (
            None
            if event["parent_event_id"] is None
            else int(event["parent_event_id"])
        ),
        "depth": int(event["depth"]),
        "label": str(event["label"]),
        "category": str(event["category"]),
        "metadata": deepcopy(event["metadata"]),
        "elapsed_ns": int(event["elapsed_ns"]),
        "direct_child_elapsed_ns": int(event["direct_child_elapsed_ns"]),
        "exclusive_ns": int(event["exclusive_ns"]),
        "completed": bool(event["completed"]),
        "error_type": (
            None if event["error_type"] is None else str(event["error_type"])
        ),
    }


def _json_mapping(value: Mapping[str, object], *, path: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        _fail("mapping_required", path, repr(value))
    if any(not isinstance(key, str) or not key for key in value):
        _fail("string_keys_required", path, repr(value))
    try:
        encoded = json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as error:
        _fail("json_safe_mapping_required", path, str(error))
    if not isinstance(decoded, dict):
        _fail("mapping_required", path, type(decoded).__name__)
    return decoded


def _clock_value(clock_ns: Callable[[], int], *, path: str) -> int:
    value = clock_ns()
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        _fail("invalid_clock_value", path, repr(value))
    return value


def _nonempty_string(value: object, *, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("nonempty_string_required", path, repr(value))
    return value


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise CausalPhaseObservationError(
        CausalPhaseObservationIssue(code=code, path=path, message=message)
    )


__all__ = [
    "CAUSAL_PHASE_OBSERVATION_VERSION",
    "CausalPhaseObservation",
    "CausalPhaseObservationError",
    "CausalPhaseObservationIssue",
    "patch_observed_call",
]
