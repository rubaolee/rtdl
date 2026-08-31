from __future__ import annotations

from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
import time
from typing import Callable, Iterator, NoReturn


ACTION_PHASE_TRACE_VERSION = "rtdl.action_phase_trace.private_candidate.v1"

ACTION_PHASES = (
    "input_adapter",
    "event_producer",
    "action_compile_or_cache_hit",
    "binding_certificate",
    "physical_plan",
    "backend_prepare",
    "host_to_device_transfer",
    "device_to_host_transfer",
    "device_synchronization_wait",
    "execute",
    "projection",
    "app_validation",
)

DEVICE_PHASES = frozenset(
    {
        "host_to_device_transfer",
        "device_to_host_transfer",
        "device_synchronization_wait",
    }
)


@dataclass(frozen=True)
class ActionPhaseTraceIssue:
    code: str
    path: str
    message: str


class ActionPhaseTraceError(ValueError):
    def __init__(self, issue: ActionPhaseTraceIssue) -> None:
        self.issue = issue
        super().__init__(
            f"Action phase trace failed: {issue.code}@{issue.path}: {issue.message}"
        )


class ActionPhaseTrace:
    """Measure one Action route without influencing planning or execution."""

    def __init__(
        self,
        *,
        app: str,
        route: str,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        if not isinstance(app, str) or not app:
            _fail("invalid_trace_identity", "app", repr(app))
        if not isinstance(route, str) or not route:
            _fail("invalid_trace_identity", "route", repr(route))
        self.app = app
        self.route = route
        self._clock = clock
        self._started = float(clock())
        self._active_phase: str | None = None
        self._segments: dict[str, list[float]] = {name: [] for name in ACTION_PHASES}
        self._segment_rows: dict[str, list[dict[str, object]]] = {
            name: [] for name in ACTION_PHASES
        }
        self._segment_labels: dict[str, set[str]] = {
            name: set() for name in ACTION_PHASES
        }
        self._skipped: dict[str, str] = {}
        self._folded_phases: dict[str, dict[str, str]] = {}
        self._device_operations: list[dict[str, object]] = []
        self._device_operation_names: set[str] = set()
        self._finished = False

    @contextmanager
    def measure(self, phase: str, *, label: str | None = None) -> Iterator[None]:
        self._require_open()
        self._require_phase(phase)
        segment_label = phase if label is None else label
        if not isinstance(segment_label, str) or not segment_label:
            _fail("invalid_segment_label", f"phases.{phase}", repr(segment_label))
        if segment_label in self._segment_labels[phase]:
            _fail(
                "duplicate_segment_label",
                f"phases.{phase}.{segment_label}",
                "segment labels must be unique within one phase",
            )
        if phase in DEVICE_PHASES:
            _fail(
                "device_phase_requires_operation",
                f"phases.{phase}",
                "use measure_device_operation so copy and synchronization semantics remain visible",
            )
        if phase in self._skipped:
            _fail("phase_already_skipped", f"phases.{phase}", self._skipped[phase])
        if self._active_phase is not None:
            _fail(
                "nested_phase_measurement",
                f"phases.{phase}",
                f"active={self._active_phase}",
            )
        self._active_phase = phase
        started = float(self._clock())
        try:
            yield
        finally:
            elapsed = float(self._clock()) - started
            self._active_phase = None
            if elapsed < 0.0:
                _fail("negative_phase_time", f"phases.{phase}", str(elapsed))
            self._segments[phase].append(elapsed)
            self._segment_rows[phase].append(
                {"label": segment_label, "elapsed_seconds": elapsed}
            )
            self._segment_labels[phase].add(segment_label)

    @contextmanager
    def measure_device_operation(
        self,
        *,
        name: str,
        kind: str,
        reason: str,
    ) -> Iterator[None]:
        self._require_open()
        self._require_device_operation(name=name, kind=kind, reason=reason)
        if self._active_phase is not None:
            _fail(
                "nested_phase_measurement",
                f"device_operations.{name}",
                f"active={self._active_phase}",
            )
        self._active_phase = kind
        started = float(self._clock())
        try:
            yield
        finally:
            elapsed = float(self._clock()) - started
            self._active_phase = None
            if elapsed < 0.0:
                _fail("negative_phase_time", f"device_operations.{name}", str(elapsed))
            self._segments[kind].append(elapsed)
            self._segment_rows[kind].append(
                {"label": name, "elapsed_seconds": elapsed}
            )
            self._segment_labels[kind].add(name)
            self._device_operations.append(
                {
                    "name": name,
                    "kind": kind,
                    "measured_separately": True,
                    "elapsed_seconds": elapsed,
                    "folded_into": None,
                    "calibration_eligible": True,
                    "reason": reason,
                }
            )

    def fold_device_operation(
        self,
        *,
        name: str,
        kind: str,
        folded_into: str,
        reason: str,
    ) -> None:
        self._require_open()
        self._require_device_operation(name=name, kind=kind, reason=reason)
        self._require_phase(folded_into)
        if folded_into in DEVICE_PHASES:
            _fail(
                "invalid_fold_parent",
                f"device_operations.{name}.folded_into",
                "a folded device operation must name one measured non-device parent",
            )
        self._device_operations.append(
            {
                "name": name,
                "kind": kind,
                "measured_separately": False,
                "elapsed_seconds": None,
                "folded_into": folded_into,
                "calibration_eligible": False,
                "reason": reason,
            }
        )

    def mark_not_applicable(self, phase: str, *, reason: str) -> None:
        self._require_open()
        self._require_phase(phase)
        if not isinstance(reason, str) or not reason:
            _fail("missing_phase_reason", f"phases.{phase}", repr(reason))
        if self._segments[phase]:
            _fail("phase_already_measured", f"phases.{phase}", reason)
        self._skipped[phase] = reason

    def fold_phase(self, phase: str, *, folded_into: str, reason: str) -> None:
        self._require_open()
        self._require_phase(phase)
        self._require_phase(folded_into)
        if phase in DEVICE_PHASES or folded_into in DEVICE_PHASES or phase == folded_into:
            _fail(
                "invalid_phase_fold",
                f"phases.{phase}.folded_into",
                "non-device phases may fold only into a different non-device parent",
            )
        if not isinstance(reason, str) or not reason:
            _fail("missing_phase_reason", f"phases.{phase}", repr(reason))
        if self._segments[phase] or phase in self._skipped or phase in self._folded_phases:
            _fail("phase_already_accounted", f"phases.{phase}", reason)
        self._folded_phases[phase] = {"folded_into": folded_into, "reason": reason}

    def finish(self) -> dict[str, object]:
        self._require_open()
        if self._active_phase is not None:
            _fail("active_phase_at_finish", "trace", self._active_phase)
        finished = float(self._clock())
        route_elapsed = finished - self._started
        if route_elapsed < 0.0:
            _fail("negative_route_time", "trace", str(route_elapsed))

        device_kinds = {str(row["kind"]) for row in self._device_operations}
        phase_rows: dict[str, dict[str, object]] = {}
        measured_total = 0.0
        for phase in ACTION_PHASES:
            segments = self._segments[phase]
            elapsed = float(sum(segments))
            measured_total += elapsed
            if segments:
                status = "measured"
                reason = None
            elif phase in DEVICE_PHASES and phase in device_kinds:
                status = "folded"
                reason = "all recorded operations are folded into named parent phases"
            elif phase in self._folded_phases:
                status = "folded"
                reason = self._folded_phases[phase]["reason"]
            elif phase in self._skipped:
                status = "not_applicable"
                reason = self._skipped[phase]
            else:
                _fail("missing_phase_accounting", f"phases.{phase}", self.route)
            phase_rows[phase] = {
                "status": status,
                "elapsed_seconds": elapsed if segments else None,
                "segment_count": len(segments),
                "segments": list(self._segment_rows[phase]),
                "folded_into": (
                    self._folded_phases[phase]["folded_into"]
                    if phase in self._folded_phases
                    else None
                ),
                "calibration_eligible": bool(segments),
                "reason": reason,
            }

        for phase, row in self._folded_phases.items():
            parent = row["folded_into"]
            if not self._segments[parent]:
                _fail(
                    "unmeasured_fold_parent",
                    f"phases.{phase}.folded_into",
                    parent,
                )

        unaccounted = max(0.0, route_elapsed - measured_total)
        tolerance = max(0.001, route_elapsed * 0.02)
        if measured_total - route_elapsed > tolerance:
            _fail(
                "phase_double_counting",
                "reconciliation",
                f"measured={measured_total}; route={route_elapsed}; tolerance={tolerance}",
            )
        reconciled = unaccounted <= tolerance
        if not reconciled:
            _fail(
                "phase_reconciliation_failed",
                "reconciliation",
                f"unaccounted={unaccounted}; tolerance={tolerance}",
            )
        self._finished = True
        return {
            "contract": ACTION_PHASE_TRACE_VERSION,
            "app": self.app,
            "route": self.route,
            "phases": phase_rows,
            "device_operations": list(self._device_operations),
            "reconciliation": {
                "route_elapsed_seconds": route_elapsed,
                "measured_phase_seconds": measured_total,
                "unaccounted_seconds": unaccounted,
                "tolerance_seconds": tolerance,
                "passed": True,
                "overlap_allowed": False,
            },
            "cost_model_calibration_authorized": False,
            "placement_or_execution_changed_by_trace": False,
        }

    def _require_open(self) -> None:
        if self._finished:
            _fail("trace_already_finished", "trace", self.route)

    @staticmethod
    def _require_phase(phase: str) -> None:
        if phase not in ACTION_PHASES:
            _fail("unknown_phase", "phase", repr(phase))

    def _require_device_operation(self, *, name: str, kind: str, reason: str) -> None:
        if not isinstance(name, str) or not name:
            _fail("invalid_device_operation", "name", repr(name))
        if name in self._device_operation_names:
            _fail("duplicate_device_operation", f"device_operations.{name}", name)
        if kind not in DEVICE_PHASES:
            _fail("invalid_device_operation_kind", f"device_operations.{name}.kind", kind)
        if not isinstance(reason, str) or not reason:
            _fail("missing_device_operation_reason", f"device_operations.{name}", repr(reason))
        self._device_operation_names.add(name)


def action_phase(
    trace: ActionPhaseTrace | None,
    phase: str,
    *,
    label: str | None = None,
):
    if trace is None:
        return nullcontext()
    return trace.measure(phase, label=label)


def _fail(code: str, path: str, message: str) -> NoReturn:
    raise ActionPhaseTraceError(ActionPhaseTraceIssue(code, path, message))


__all__ = [
    "ACTION_PHASE_TRACE_VERSION",
    "ACTION_PHASES",
    "DEVICE_PHASES",
    "ActionPhaseTrace",
    "ActionPhaseTraceError",
    "ActionPhaseTraceIssue",
    "action_phase",
]
