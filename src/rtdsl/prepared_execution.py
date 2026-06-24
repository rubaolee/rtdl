from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import hashlib
import statistics
import time
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Sequence

from .prepared_session_residency import ExplicitPreparedSessionCache
from .prepared_session_residency import RtdlPreparedSessionResidencyPolicy
from .prepared_session_residency import make_prepared_session_cache_key


PREPARED_EXECUTION_REPORT_VERSION = "rtdl.v2_8.prepared_execution_report.v1"
PREPARED_EXECUTION_SESSION_RUNNER_VERSION = "rtdl.v3.phoenix.prepared_execution_session_runner.m3_3"
PREPARED_EXECUTION_SESSION_RUNNER_STATUS = "executed_not_release_authorization"
PREPARED_EXECUTION_SESSION_AUDIT_VERSION = "rtdl.v3.phoenix.prepared_execution_session_audit.v1"
PREPARED_EXECUTION_CONTINUATION_AUDIT_VERSION = (
    "rtdl.v3.phoenix.prepared_execution_continuation_audit.v1"
)
PREPARED_EXECUTION_WORKFLOW = (
    "prepare",
    "pack_or_cache",
    "warm",
    "run_steady_state",
    "explain_timings",
)
PREPARED_EXECUTION_REQUIRED_PHASES = (
    "prepare",
    "cache_load",
    "warmup",
    "steady_state_stream",
    "planner",
    "executor",
    "validation",
)
PREPARED_EXECUTION_CLAIM_BOUNDARY = (
    "Prepared execution separates setup, cache/load, warmup, steady-state "
    "streaming, planner, executor, and validation timings. It does not "
    "authorize release, public speedup wording, broad RT-core speedup wording, "
    "true zero-copy wording, RayJoin paper-reproduction wording, `rtdl beats "
    "RayJoin` wording, full overlay wording, hidden partner selection, or "
    "app-specific native-engine behavior."
)


@dataclass(frozen=True)
class PreparedExecutionPhaseTiming:
    phase: str
    seconds: float
    role: str
    source_keys: tuple[str, ...] = ()
    repeat_seconds: tuple[float, ...] = ()
    best_repeat_seconds: float | None = None
    steady_state_candidate: bool = False
    setup_candidate: bool = False
    validation_candidate: bool = False

    def __post_init__(self) -> None:
        if not self.phase:
            raise ValueError("prepared execution phase must have a name")
        if self.seconds < 0.0:
            raise ValueError(f"prepared execution phase {self.phase} has negative seconds")
        for value in self.repeat_seconds:
            if value < 0.0:
                raise ValueError(f"prepared execution phase {self.phase} has negative repeat seconds")
        if self.best_repeat_seconds is not None and self.best_repeat_seconds < 0.0:
            raise ValueError(f"prepared execution phase {self.phase} has negative best repeat seconds")

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "seconds": self.seconds,
            "role": self.role,
            "source_keys": list(self.source_keys),
            "repeat_seconds": list(self.repeat_seconds),
            "best_repeat_seconds": self.best_repeat_seconds,
            "steady_state_candidate": self.steady_state_candidate,
            "setup_candidate": self.setup_candidate,
            "validation_candidate": self.validation_candidate,
        }


@dataclass(frozen=True)
class PreparedExecutionReport:
    workflow_name: str
    explicit_backend: str
    explicit_partner: str
    phases: tuple[PreparedExecutionPhaseTiming, ...]
    warmup_count: int
    claim_boundary: Mapping[str, bool]
    source_schema: str | None = None
    source_goal: int | None = None
    source_commit: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)
    app_specific_engine_logic_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.workflow_name:
            raise ValueError("prepared execution report must name its workflow")
        if not self.explicit_backend:
            raise ValueError("prepared execution report must record an explicit backend")
        if not self.explicit_partner:
            raise ValueError("prepared execution report must record an explicit partner")
        if self.warmup_count < 0:
            raise ValueError("prepared execution warmup_count must be non-negative")
        phase_names = tuple(phase.phase for phase in self.phases)
        missing = tuple(phase for phase in PREPARED_EXECUTION_REQUIRED_PHASES if phase not in phase_names)
        if missing:
            raise ValueError("prepared execution report is missing required phases: " + ", ".join(missing))
        for field_name in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if getattr(self, field_name):
                raise ValueError(f"prepared execution report must not authorize {field_name}")
        for key, value in self.claim_boundary.items():
            if bool(value):
                raise ValueError(f"prepared execution source claim boundary authorizes {key}")

    @property
    def setup_seconds(self) -> float:
        return sum(phase.seconds for phase in self.phases if phase.setup_candidate)

    @property
    def warmup_seconds(self) -> float:
        return sum(phase.seconds for phase in self.phases if phase.phase == "warmup")

    @property
    def validation_seconds(self) -> float:
        return sum(phase.seconds for phase in self.phases if phase.validation_candidate)

    @property
    def steady_state_seconds(self) -> float:
        return sum(phase.seconds for phase in self.phases if phase.steady_state_candidate)

    def to_dict(self) -> dict[str, Any]:
        phase_payloads: list[dict[str, Any]] = []
        setup_seconds = 0.0
        warmup_seconds = 0.0
        steady_state_seconds = 0.0
        validation_seconds = 0.0
        for phase in self.phases:
            phase_payloads.append(phase.to_dict())
            if phase.setup_candidate:
                setup_seconds += phase.seconds
            if phase.phase == "warmup":
                warmup_seconds += phase.seconds
            if phase.steady_state_candidate:
                steady_state_seconds += phase.seconds
            if phase.validation_candidate:
                validation_seconds += phase.seconds
        return {
            "schema": PREPARED_EXECUTION_REPORT_VERSION,
            "workflow": list(PREPARED_EXECUTION_WORKFLOW),
            "workflow_name": self.workflow_name,
            "explicit_backend": self.explicit_backend,
            "explicit_partner": self.explicit_partner,
            "explicit_partner_choice_required": True,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "warmup_count": self.warmup_count,
            "phase_timings": phase_payloads,
            "summary_sec": {
                "setup": setup_seconds,
                "warmup": warmup_seconds,
                "steady_state": steady_state_seconds,
                "validation": validation_seconds,
            },
            "source_schema": self.source_schema,
            "source_goal": self.source_goal,
            "source_commit": self.source_commit,
            "notes": list(self.notes),
            "claim_boundary": dict(self.claim_boundary),
            "prepared_execution_claim_boundary": PREPARED_EXECUTION_CLAIM_BOUNDARY,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
        }


@dataclass(frozen=True)
class PreparedExecutionSessionTask:
    workflow_name: str
    primitive: str
    backend: str
    partner: str
    input_fingerprints: Mapping[str, Any]
    run_prepared: Callable[[Any], Any]
    prepare_session: Callable[[], Any]
    cache: ExplicitPreparedSessionCache
    parameters: Mapping[str, Any] | None = None
    device: str = "unknown"
    warmup_count: int = 0
    warmup_prepared: Callable[[Any], Any] | None = None
    measured_run_prepared: Callable[[Any], Any] | None = None
    finalize_output: Callable[[Any, Any], Any] | None = None
    validate_output: Callable[[Any], Any] | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not str(self.workflow_name):
            raise ValueError("prepared execution session task requires workflow_name")
        if not callable(self.prepare_session):
            raise TypeError("prepare_session must be callable")
        if not callable(self.run_prepared):
            raise TypeError("run_prepared must be callable")
        if self.warmup_prepared is not None and not callable(self.warmup_prepared):
            raise TypeError("warmup_prepared must be callable when provided")
        if self.measured_run_prepared is not None and not callable(self.measured_run_prepared):
            raise TypeError("measured_run_prepared must be callable when provided")
        if self.finalize_output is not None and not callable(self.finalize_output):
            raise TypeError("finalize_output must be callable when provided")
        if self.validate_output is not None and not callable(self.validate_output):
            raise TypeError("validate_output must be callable when provided")
        if not isinstance(self.cache, ExplicitPreparedSessionCache):
            raise TypeError("cache must be an ExplicitPreparedSessionCache")
        if int(self.warmup_count) < 0:
            raise ValueError("warmup_count must be non-negative")
        if str(self.partner).strip().lower() in {"", "auto", "automatic"}:
            raise ValueError("prepared execution session runner requires explicit partner")


@dataclass(frozen=True)
class PreparedExecutionSessionResult:
    prepared_value: Any = field(compare=False, repr=False)
    output: Any = field(compare=False, repr=False)
    validation_output: Any = field(compare=False, repr=False)
    metadata: Mapping[str, Any]

    @property
    def cache_hit(self) -> bool:
        return bool(self.metadata["prepared_session"]["cache_hit"])

    @property
    def runtime_executed(self) -> bool:
        return bool(self.metadata["runtime_executed"])

    def to_metadata(self) -> dict[str, Any]:
        return dict(self.metadata)

    def runtime_audit(self) -> dict[str, Any]:
        return audit_prepared_execution_session_metadata(self.metadata)


def run_prepared_execution_session(task: PreparedExecutionSessionTask) -> PreparedExecutionSessionResult:
    """Execute one explicit prepared-session task and report V3 claim boundaries.

    The runner is deliberately small: callers still choose the primitive,
    backend, partner, cache, prepare function, and run function. The runner only
    makes that execution path visible and repeatable.
    """

    return _execute_prepared_execution_session(task, measured_repeat_count=1)


def run_repeated_prepared_execution_session(
    task: PreparedExecutionSessionTask,
    *,
    measured_repeat_count: int,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Execute warmup plus N measured prepared runs inside one runner call.

    This is the productized repeat-session shape Phoenix V3 needs before a
    route can claim that prepared reuse is a runtime feature instead of an
    app-local loop. It performs one cache lookup, one prepare/cache phase, N
    measured executions, and one report payload.
    """

    return _execute_prepared_execution_session(
        task,
        measured_repeat_count=measured_repeat_count,
        validate_each_repeat=validate_each_repeat,
        retain_repeat_outputs=retain_repeat_outputs,
    )


def _execute_prepared_execution_session(
    task: PreparedExecutionSessionTask,
    *,
    measured_repeat_count: int,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    repeat_count = int(measured_repeat_count)
    if repeat_count <= 0:
        raise ValueError("measured_repeat_count must be positive")
    cache_key = make_prepared_session_cache_key(
        primitive=task.primitive,
        backend=task.backend,
        input_fingerprints=task.input_fingerprints,
        parameters=task.parameters,
        partner=task.partner,
        device=task.device,
    )
    policy = RtdlPreparedSessionResidencyPolicy(cache_key=cache_key, cache_enabled=True)

    prepare_start = time.perf_counter()
    reuse = _get_or_prepare_with_elapsed(task.cache, cache_key, task.prepare_session, policy=policy)
    prepare_or_cache_sec = time.perf_counter() - prepare_start
    prepare_sec = 0.0 if reuse.cache_hit else prepare_or_cache_sec
    cache_load_sec = prepare_or_cache_sec if reuse.cache_hit else 0.0
    native_prepare = _extract_native_prepare_seconds(reuse.value)
    native_prepare_sec = native_prepare[0]
    native_prepare_source = native_prepare[1]
    legacy_aligned_prepare_sec = (
        native_prepare_sec
        if native_prepare_sec is not None and not reuse.cache_hit
        else prepare_sec
    )

    warmup_runner = task.warmup_prepared or task.run_prepared
    warmup_repeats: list[float] = []
    for _ in range(int(task.warmup_count)):
        start = time.perf_counter()
        warmup_runner(reuse.value)
        warmup_repeats.append(time.perf_counter() - start)
    warmup_sec = sum(warmup_repeats)

    if task.finalize_output is not None and (validate_each_repeat or retain_repeat_outputs):
        raise ValueError(
            "finalize_output is supported only when validate_each_repeat and "
            "retain_repeat_outputs are false"
        )

    measured_repeat_seconds: list[float] = []
    retained_outputs: list[Any] = []
    measured_output: Any = None
    measured_runner = task.measured_run_prepared or task.run_prepared
    for _ in range(repeat_count):
        run_start = time.perf_counter()
        measured_output = measured_runner(reuse.value)
        measured_repeat_seconds.append(time.perf_counter() - run_start)
        if retain_repeat_outputs or validate_each_repeat:
            retained_outputs.append(measured_output)
    executor_sec = float(statistics.median(measured_repeat_seconds))
    output_finalize_sec = 0.0
    if task.finalize_output is not None:
        finalize_start = time.perf_counter()
        final_output = task.finalize_output(reuse.value, measured_output)
        output_finalize_sec = time.perf_counter() - finalize_start
    else:
        final_output = measured_output
    output = tuple(retained_outputs) if retain_repeat_outputs else final_output

    validation_output = None
    validation_sec = 0.0
    if task.validate_output is not None:
        validation_start = time.perf_counter()
        if validate_each_repeat:
            validation_output = tuple(task.validate_output(item) for item in retained_outputs)
        else:
            validation_output = task.validate_output(final_output)
        validation_sec = time.perf_counter() - validation_start

    phases = (
        PreparedExecutionPhaseTiming(
            phase="prepare",
            seconds=prepare_sec,
            role="prepare_explicit_session_on_cache_miss",
            setup_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="cache_load",
            seconds=cache_load_sec,
            role="load_explicit_prepared_session_from_cache_on_hit",
        ),
        PreparedExecutionPhaseTiming(
            phase="warmup",
            seconds=warmup_sec,
            role="caller_requested_prepared_session_warmup",
            repeat_seconds=tuple(warmup_repeats),
            best_repeat_seconds=min(warmup_repeats) if warmup_repeats else None,
        ),
        PreparedExecutionPhaseTiming(
            phase="steady_state_stream",
            seconds=0.0,
            role="no_separate_stream_phase_recorded_by_minimal_runner",
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="planner",
            seconds=0.0,
            role="caller_preplanned_single_prepared_operation",
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="executor",
            seconds=executor_sec,
            role=(
                "execute_explicit_prepared_operation"
                if repeat_count == 1
                else "median_of_repeated_explicit_prepared_operations"
            ),
            repeat_seconds=tuple(measured_repeat_seconds),
            best_repeat_seconds=min(measured_repeat_seconds),
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="validation",
            seconds=validation_sec,
            role="caller_supplied_validation_after_execution",
            validation_candidate=True,
        ),
    )
    report = PreparedExecutionReport(
        workflow_name=task.workflow_name,
        explicit_backend=task.backend,
        explicit_partner=task.partner,
        phases=phases,
        warmup_count=int(task.warmup_count),
        claim_boundary={},
        notes=task.notes,
    )
    report_payload = report.to_dict()
    validation = validate_prepared_execution_report(report_payload)
    metadata = {
        "schema": PREPARED_EXECUTION_SESSION_RUNNER_VERSION,
        "status": PREPARED_EXECUTION_SESSION_RUNNER_STATUS,
        "productized_execution_path": "prepared_execution_session_runner",
        "runtime_executed": True,
        "workflow_name": task.workflow_name,
        "primitive": task.primitive,
        "explicit_backend": task.backend,
        "explicit_partner": task.partner,
        "explicit_partner_choice_required": True,
        "prepared_session": reuse.to_metadata(),
        "outer_prepare_or_cache_sec": prepare_or_cache_sec,
        "outer_prepare_sec": prepare_sec,
        "outer_cache_load_sec": cache_load_sec,
        "native_prepare_sec": native_prepare_sec,
        "native_prepare_seconds_source": native_prepare_source,
        "legacy_aligned_prepare_sec": legacy_aligned_prepare_sec,
        "legacy_aligned_prepare_metric_available": native_prepare_sec is not None and not reuse.cache_hit,
        "prepared_execution_report": report_payload,
        "prepared_execution_report_validation": validation,
        "repeated_prepared_session_execution": repeat_count > 1,
        "measured_repeat_count": repeat_count,
        "measured_repeat_seconds": tuple(measured_repeat_seconds),
        "measured_total_sec": sum(measured_repeat_seconds),
        "measured_median_sec": executor_sec,
        "measured_best_sec": min(measured_repeat_seconds),
        "output_finalize_sec": output_finalize_sec,
        "measured_run_prepared_override_used": task.measured_run_prepared is not None,
        "measured_output_finalized_once": task.finalize_output is not None,
        "per_repeat_output_finalization_avoided": task.finalize_output is not None,
        "single_cache_lookup_for_measured_repeats": True,
        "single_report_after_measured_repeats": True,
        "per_iteration_task_reconstruction_avoided": True,
        "per_iteration_fingerprint_recompute_avoided": True,
        "repeat_outputs_retained": bool(retain_repeat_outputs),
        "validate_each_repeat": bool(validate_each_repeat),
        "output_type": type(output).__name__,
        "validation_output_type": type(validation_output).__name__,
        "validation_passed": _validation_passed(validation_output),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
        "claim_boundary": PREPARED_EXECUTION_CLAIM_BOUNDARY,
    }
    return PreparedExecutionSessionResult(
        prepared_value=reuse.value,
        output=output,
        validation_output=validation_output,
        metadata=metadata,
    )


def run_fixed_radius_count_threshold_3d_self_query_prepared_session(
    *,
    search_points: Any,
    radius: float,
    threshold: int,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    output_columns: dict[str, object] | None = None,
    prepare_session: Callable[[], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run the generic 3-D fixed-radius self-query primitive through the V3 runner."""

    radius = float(radius)
    threshold = int(threshold)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    if prepare_session is None:
        from .optix_runtime import prepare_optix_fixed_radius_count_threshold_3d

        def prepare_session() -> Any:
            return prepare_optix_fixed_radius_count_threshold_3d(
                search_points,
                max_radius=radius,
            )

    def run_prepared(prepared: Any) -> Any:
        from .partner_adapters import (
            fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns,
        )

        return fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns(
            prepared,
            radius=radius,
            threshold=threshold,
            partner=partner,
            output_columns=output_columns,
            return_metadata=True,
        )

    task = PreparedExecutionSessionTask(
        workflow_name="fixed_radius_count_threshold_3d_self_query_prepared_session",
        primitive="fixed_radius_count_threshold_self_query",
        backend="optix",
        partner=partner,
        input_fingerprints={
            "search_points": _stable_input_fingerprint(search_points),
        },
        parameters={
            "radius": radius,
            "threshold": threshold,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_prepared,
        validate_output=validate_output,
        notes=(
            "generic fixed-radius self-query primitive routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "fixed_radius_count_threshold_self_query"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_fixed_radius_threshold_reached_count_2d_prepared_session(
    *,
    search_points: Any,
    query_points: Any,
    radius: float,
    threshold: int,
    backend: str,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    max_radius: float | None = None,
    search_fingerprint: Any | None = None,
    query_fingerprint: Any | None = None,
    prepare_session: Callable[[], Any] | None = None,
    run_threshold_count: Callable[[Any], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    require_repeat5_material_probe: bool = False,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run generic 2-D fixed-radius threshold-summary through the V3 runner."""

    radius = float(radius)
    threshold = int(threshold)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    resolved_backend = str(backend).strip().lower()
    if resolved_backend not in {"embree", "optix"}:
        raise ValueError("backend must be 'embree' or 'optix'")
    resolved_partner = str(partner).strip().lower()
    if not resolved_partner:
        raise ValueError("partner must be explicit, or 'none'")
    repeat_count = int(measured_repeat_count)
    if repeat_count <= 0:
        raise ValueError("measured_repeat_count must be positive")
    if bool(require_repeat5_material_probe) and repeat_count < 5:
        raise ValueError("repeat5 material-probe config requires measured_repeat_count >= 5")
    resolved_max_radius = radius if max_radius is None else float(max_radius)
    if resolved_max_radius < radius:
        raise ValueError("max_radius must be greater than or equal to radius")

    search_count = _prepared_input_count(search_points)
    query_count = _prepared_input_count(query_points)
    resolved_search_fingerprint = (
        make_prepared_input_fingerprint(search_points)
        if search_fingerprint is None
        else search_fingerprint
    )
    resolved_query_fingerprint = (
        make_prepared_input_fingerprint(query_points)
        if query_fingerprint is None
        else query_fingerprint
    )

    if prepare_session is None:
        from .generic_primitives import prepare_generic_fixed_radius_count_threshold_2d

        def prepare_session() -> Any:
            kwargs: dict[str, Any] = {
                "search_points": search_points,
                "backend": resolved_backend,
            }
            if resolved_backend == "optix":
                kwargs["max_radius"] = resolved_max_radius
            return prepare_generic_fixed_radius_count_threshold_2d(**kwargs)

    if run_threshold_count is None:

        def run_threshold_count(prepared: Any) -> Any:
            if hasattr(prepared, "count_threshold_reached"):
                return prepared.count_threshold_reached(
                    query_points,
                    radius=radius,
                    threshold=threshold,
                )
            raise TypeError("prepared threshold-summary session must expose count_threshold_reached")

    task = PreparedExecutionSessionTask(
        workflow_name="fixed_radius_threshold_reached_count_2d_prepared_session",
        primitive="fixed_radius_threshold_reached_count_2d",
        backend=resolved_backend,
        partner=resolved_partner,
        input_fingerprints={
            "search_points": resolved_search_fingerprint,
            "query_points": resolved_query_fingerprint,
        },
        parameters={
            "radius": radius,
            "threshold": threshold,
            "max_radius": resolved_max_radius,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_threshold_count,
        validate_output=validate_output,
        notes=(
            "generic 2-D fixed-radius threshold-summary scalar count routed "
            "through Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if repeat_count != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_mapping = dict(output_payload) if isinstance(output_payload, Mapping) else {}
    threshold_count_present = "threshold_reached_count" in output_mapping
    output_threshold_count = (
        int(output_mapping["threshold_reached_count"])
        if threshold_count_present
        else None
    )
    output_count_within_requested_bounds = bool(
        output_threshold_count is not None
        and output_threshold_count >= 0
        and (query_count is None or output_threshold_count <= int(query_count))
    )
    native_scalar_count_used = bool(output_mapping.get("native_scalar_count_used", False))
    threshold_rows_materialized = bool(
        output_mapping.get(
            "threshold_summary_rows_materialized_on_host",
            "scalar_reduction" in output_mapping,
        )
    )
    hot_path_host_materialization = bool(
        output_mapping.get("hot_path_host_materialization", threshold_rows_materialized)
    )
    prepared_search_resident = bool(
        output_mapping.get("prepared_search_structure_resident_between_rtdl_phases", False)
    )
    query_points_resident = bool(
        output_mapping.get("query_points_device_resident_between_rtdl_phases", False)
    )
    internal_device_residency = bool(
        output_mapping.get(
            "internal_device_residency_between_rtdl_phases",
            prepared_search_resident,
        )
    )
    material_repeat_met = repeat_count >= 5

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "fixed_radius_threshold_reached_count_2d"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = "generic_fixed_radius_threshold_reached_count_2d"
    metadata["continuation_contract"] = "threshold_reached_count_scalar_2d"
    metadata["phoenix_v3_redesign_step"] = "step2_runtime_trunk_third_family_generalization_probe"
    metadata["runtime_trunk_family"] = "fixed_radius_threshold_reached_count_2d_prepared_scene"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and threshold_count_present
        and output_count_within_requested_bounds
        and not threshold_rows_materialized
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_fixed_radius_search_structure_2d",
        "execute_threshold_reached_scalar_count",
        "return_threshold_count",
    )
    metadata["search_count"] = search_count
    metadata["query_count"] = query_count
    metadata["output_threshold_reached_count"] = output_threshold_count
    metadata["output_count_within_requested_bounds"] = output_count_within_requested_bounds
    metadata["native_scalar_count_used"] = native_scalar_count_used
    metadata["threshold_summary_rows_materialized_on_host"] = threshold_rows_materialized
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["prepared_search_structure_resident_between_rtdl_phases"] = prepared_search_resident
    metadata["query_points_device_resident_between_rtdl_phases"] = query_points_resident
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["internal_residency_scope"] = output_mapping.get(
        "internal_residency_scope",
        "not_reported_by_backend",
    )
    metadata["material_probe_repeat_requirement"] = 5
    metadata["material_probe_repeat_requirement_met"] = material_repeat_met
    metadata["repeat5_material_probe_candidate"] = bool(
        material_repeat_met
        and resolved_backend == "optix"
        and metadata["runtime_trunk_executes_end_to_end"]
        and internal_device_residency
    )
    metadata["repeat5_scope_required_for_material_claim"] = True
    metadata["hot_cold_runner_wall_must_travel_together"] = True
    metadata["legacy_app_front_door_parity_required"] = True
    metadata["same_contract_embree_baseline_required"] = True
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned prepared structures and intermediates between RTDL phases "
        "are V3; exposing caller-owned device buffers to an external host "
        "remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    metadata["input_fingerprint_source"] = {
        "search_points": "computed_in_helper" if search_fingerprint is None else "caller_supplied",
        "query_points": "computed_in_helper" if query_fingerprint is None else "caller_supplied",
    }
    metadata["large_input_fingerprint_hot_path_avoided"] = bool(
        search_fingerprint is not None and query_fingerprint is not None
    )
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


class _FixedRadiusRankedSummary3DPreparedSession:
    def __init__(self, search_handle: Any, *, backend: str, query_handle: Any | None = None) -> None:
        self.search_handle = search_handle
        self.query_handle = query_handle
        self.backend = backend

    def run_ranked_summary(
        self,
        query_points: Any,
        *,
        radius: float,
        k_max: int,
        precision: str,
    ) -> Any:
        if self.backend == "optix" and self.query_handle is not None:
            aggregates = self.search_handle.aggregate_ranked_summary_prepared_queries_batch(
                self.query_handle,
                ({"radius": radius, "k_max": k_max},),
                precision=precision,
            )
            if len(aggregates) != 1:
                raise RuntimeError("fixed-radius ranked-summary prepared query batch returned multiple aggregates")
            return aggregates[0]
        if self.backend == "optix":
            return self.search_handle.aggregate_ranked_summary(
                query_points,
                radius=radius,
                k_max=k_max,
                precision=precision,
            )
        return self.search_handle.aggregate_ranked_summary(
            query_points,
            radius=radius,
            k_max=k_max,
        )

    def close(self) -> None:
        for handle in (self.query_handle, self.search_handle):
            close = getattr(handle, "close", None)
            if callable(close):
                close()


def run_fixed_radius_ranked_summary_3d_prepared_session(
    *,
    search_points: Any,
    query_points: Any,
    radius: float,
    k_max: int,
    backend: str,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    search_fingerprint: Any | None = None,
    query_fingerprint: Any | None = None,
    prepared_query_points: bool = True,
    precision: str = "float32",
    prepare_session: Callable[[], Any] | None = None,
    run_ranked_summary: Callable[[Any], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    require_repeat50_material_probe: bool = False,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run generic 3-D fixed-radius ranked-summary aggregate through the V3 runner."""

    radius = float(radius)
    k_max = int(k_max)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if k_max <= 0:
        raise ValueError("k_max must be positive")
    resolved_backend = str(backend).strip().lower()
    if resolved_backend not in {"embree", "optix"}:
        raise ValueError("backend must be 'embree' or 'optix'")
    resolved_partner = str(partner).strip().lower()
    if not resolved_partner:
        raise ValueError("partner must be explicit, or 'none'")
    resolved_precision = str(precision).strip().lower()
    if not resolved_precision:
        raise ValueError("precision must be explicit")
    if resolved_backend == "optix" and prepared_query_points and resolved_precision != "float32":
        raise ValueError("optix prepared query ranked-summary currently requires precision='float32'")
    repeat_count = int(measured_repeat_count)
    if repeat_count <= 0:
        raise ValueError("measured_repeat_count must be positive")
    if bool(require_repeat50_material_probe) and repeat_count < 50:
        raise ValueError("repeat50 material-probe config requires measured_repeat_count >= 50")

    search_count = _prepared_input_count(search_points)
    query_count = _prepared_input_count(query_points)
    resolved_search_fingerprint = (
        make_prepared_input_fingerprint(search_points)
        if search_fingerprint is None
        else search_fingerprint
    )
    resolved_query_fingerprint = (
        make_prepared_input_fingerprint(query_points)
        if query_fingerprint is None
        else query_fingerprint
    )

    if prepare_session is None:
        if resolved_backend == "optix":
            from .optix_runtime import prepare_optix_fixed_radius_neighbors_3d

            def prepare_session() -> _FixedRadiusRankedSummary3DPreparedSession:
                search_handle = prepare_optix_fixed_radius_neighbors_3d(
                    search_points,
                    max_radius=radius,
                )
                query_handle = (
                    search_handle.prepare_query_points(query_points)
                    if bool(prepared_query_points)
                    else None
                )
                return _FixedRadiusRankedSummary3DPreparedSession(
                    search_handle,
                    backend=resolved_backend,
                    query_handle=query_handle,
                )

        else:
            from .embree_runtime import prepare_embree_fixed_radius_neighbors_3d

            def prepare_session() -> _FixedRadiusRankedSummary3DPreparedSession:
                return _FixedRadiusRankedSummary3DPreparedSession(
                    prepare_embree_fixed_radius_neighbors_3d(search_points),
                    backend=resolved_backend,
                )

    if run_ranked_summary is None:

        def run_ranked_summary(prepared: Any) -> Any:
            if isinstance(prepared, _FixedRadiusRankedSummary3DPreparedSession):
                return prepared.run_ranked_summary(
                    query_points,
                    radius=radius,
                    k_max=k_max,
                    precision=resolved_precision,
                )
            if hasattr(prepared, "run_ranked_summary"):
                return prepared.run_ranked_summary(
                    query_points,
                    radius=radius,
                    k_max=k_max,
                    precision=resolved_precision,
                )
            return prepared.aggregate_ranked_summary(
                query_points,
                radius=radius,
                k_max=k_max,
            )

    task = PreparedExecutionSessionTask(
        workflow_name="fixed_radius_ranked_summary_3d_prepared_session",
        primitive="fixed_radius_ranked_summary_3d",
        backend=resolved_backend,
        partner=resolved_partner,
        input_fingerprints={
            "search_points": resolved_search_fingerprint,
            "query_points": resolved_query_fingerprint,
        },
        parameters={
            "radius": radius,
            "k_max": k_max,
            "prepared_query_points": bool(prepared_query_points),
            "precision": resolved_precision,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_ranked_summary,
        validate_output=validate_output,
        notes=(
            "generic 3-D fixed-radius ranked-summary aggregate routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if repeat_count != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_mapping = dict(output_payload) if isinstance(output_payload, Mapping) else {}
    integer_signature_keys = (
        "query_count",
        "bounded_neighbor_count",
        "nearest_id_checksum",
        "kth_id_checksum",
    )
    integer_signatures_present = all(key in output_mapping for key in integer_signature_keys)
    distance_summary_present = "sum_distance" in output_mapping
    output_query_count = output_mapping.get("query_count")
    output_query_count_matches_requested = (
        query_count is None
        or output_query_count is not None
        and int(output_query_count) == int(query_count)
    )
    prepared_queries_resident = bool(output_mapping.get("query_resident"))
    ranked_summary_rows_materialized = bool(output_mapping.get("summary_rows_materialized_on_host", False))
    hot_path_host_materialization = ranked_summary_rows_materialized
    internal_device_residency = bool(
        resolved_backend == "optix"
        and prepared_queries_resident
        and integer_signatures_present
        and not hot_path_host_materialization
    )
    material_repeat_met = repeat_count >= 50

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "fixed_radius_ranked_summary_3d"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = "generic_fixed_radius_ranked_summary_3d_aggregate"
    metadata["continuation_contract"] = "fixed_radius_ranked_summary_aggregate_3d"
    metadata["phoenix_v3_redesign_step"] = "step2_runtime_trunk_generalization_probe"
    metadata["runtime_trunk_family"] = "fixed_radius_ranked_summary_3d_prepared_query_aggregate"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and integer_signatures_present
        and distance_summary_present
        and output_query_count_matches_requested
        and internal_device_residency
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_fixed_radius_search_structure_3d",
        "prepare_query_points_when_supported",
        "execute_ranked_summary_aggregate",
        "return_integer_and_distance_signatures",
    )
    metadata["search_count"] = search_count
    metadata["query_count"] = query_count
    metadata["output_query_count"] = output_query_count
    metadata["output_query_count_matches_requested"] = output_query_count_matches_requested
    metadata["integer_signatures_present"] = integer_signatures_present
    metadata["distance_summary_present"] = distance_summary_present
    metadata["prepared_query_points"] = bool(prepared_query_points)
    metadata["prepared_queries_resident"] = prepared_queries_resident
    metadata["ranked_summary_rows_materialized_on_host"] = ranked_summary_rows_materialized
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["precision"] = resolved_precision
    metadata["material_probe_repeat_requirement"] = 50
    metadata["material_probe_repeat_requirement_met"] = material_repeat_met
    metadata["repeat50_material_probe_candidate"] = bool(
        material_repeat_met
        and resolved_backend == "optix"
        and prepared_query_points
        and resolved_precision == "float32"
        and metadata["runtime_trunk_executes_end_to_end"]
    )
    metadata["repeat50_scope_required_for_material_claim"] = True
    metadata["hot_cold_runner_wall_must_travel_together"] = True
    metadata["baseline_asymmetry_must_be_disclosed"] = True
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    metadata["input_fingerprint_source"] = {
        "search_points": "computed_in_helper" if search_fingerprint is None else "caller_supplied",
        "query_points": "computed_in_helper" if query_fingerprint is None else "caller_supplied",
    }
    metadata["large_input_fingerprint_hot_path_avoided"] = bool(
        search_fingerprint is not None and query_fingerprint is not None
    )
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_aabb_index_query_2d_range_intersection_prepared_session(
    *,
    indexed_boxes: Any,
    query_boxes: Any,
    backend: str,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    indexed_ids: Any | None = None,
    query_ids: Any | None = None,
    row_capacity: int | None = None,
    resolution: int = 32,
    prepare_session: Callable[[], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run generic 2-D AABB range-intersection rows through the V3 runner."""

    normalized_backend = str(backend).strip().lower().replace("-", "_")
    if normalized_backend not in {"embree", "optix"}:
        raise ValueError("AABB native query-handle runner requires backend 'embree' or 'optix'")
    resolved_resolution = int(resolution)
    if resolved_resolution < 1:
        raise ValueError("resolution must be positive")
    indexed_tuple = tuple(indexed_boxes)
    query_tuple = tuple(query_boxes)
    if not indexed_tuple:
        raise ValueError("AABB native query-handle runner requires indexed_boxes")
    if not query_tuple:
        raise ValueError("AABB native query-handle runner requires query_boxes")
    indexed_id_tuple = (
        tuple(int(value) for value in indexed_ids)
        if indexed_ids is not None
        else tuple(range(len(indexed_tuple)))
    )
    query_id_tuple = (
        tuple(int(value) for value in query_ids)
        if query_ids is not None
        else tuple(range(len(query_tuple)))
    )
    if len(indexed_id_tuple) != len(indexed_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")
    if len(query_id_tuple) != len(query_tuple):
        raise ValueError("query_ids length must match query_boxes length")
    resolved_row_capacity = int(row_capacity) if row_capacity is not None else None
    if normalized_backend == "optix" and resolved_row_capacity is None:
        raise ValueError("OptiX AABB native query-handle runner requires row_capacity")
    if resolved_row_capacity is not None and resolved_row_capacity < 0:
        raise ValueError("row_capacity must be non-negative")

    if prepare_session is None:
        from .aabb_index import prepare_aabb_index_2d

        def prepare_session() -> Any:
            return prepare_aabb_index_2d(
                indexed_tuple,
                box_queries=query_tuple,
                indexed_ids=indexed_id_tuple,
                resolution=resolved_resolution,
                backend=normalized_backend,
            )

    def run_prepared(prepared: Any) -> dict[str, Any]:
        if normalized_backend == "optix":
            rows = prepared.intersection_rows(
                query_tuple,
                query_id_tuple,
                row_capacity=resolved_row_capacity,
            )
        else:
            rows = prepared.intersection_rows(query_tuple, query_id_tuple)
        cache_stats = getattr(prepared, "prepared_query_cache_stats", None)
        prepared_query_cache_stats = dict(cache_stats()) if callable(cache_stats) else None
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d_native_query_handle",
            "backend": normalized_backend,
            "prepared": True,
            "operation": "range_intersection_rows",
            "row_schema": ("query_id", "indexed_id"),
            "candidate_id_rows": tuple(sorted((int(query_id), int(indexed_id)) for query_id, indexed_id in rows)),
            "valid_count": len(rows),
            "indexed_box_count": len(indexed_tuple),
            "query_box_count": len(query_tuple),
            "row_capacity": resolved_row_capacity,
            "resolution": resolved_resolution,
            "prepared_query_cache_stats": prepared_query_cache_stats,
            "metadata": {
                "adapter": "aabb_index_query_2d_range_intersection_prepared_session",
                "input_contract": "prepared_native_aabb_index_2d_with_query_boxes",
                "native_engine_row_contract": "generic_prepared_aabb_index_query_2d_native_query_handle",
                "partner": partner,
                "backend": normalized_backend,
                "native_query_handle_reuse": True,
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
            },
        }

    task = PreparedExecutionSessionTask(
        workflow_name="aabb_index_query_2d_range_intersection_prepared_session",
        primitive="aabb_index_query_2d_native_query_handle",
        backend=normalized_backend,
        partner=partner,
        input_fingerprints={
            "indexed_boxes": _stable_input_fingerprint(indexed_tuple),
            "query_boxes": _stable_input_fingerprint(query_tuple),
        },
        parameters={
            "operation": "range_intersection_rows",
            "indexed_ids": _stable_input_fingerprint(indexed_id_tuple),
            "query_ids": _stable_input_fingerprint(query_id_tuple),
            "row_capacity": resolved_row_capacity,
            "resolution": resolved_resolution,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_prepared,
        validate_output=validate_output,
        notes=(
            "generic AABB native query-handle primitive routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    metadata["set_a_probe_candidate"] = False
    metadata["set_b_control_candidate"] = True
    metadata["primitive_family"] = "aabb_index_query_2d_native_query_handle"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = "generic_prepared_aabb_index_query_2d_native_query_handle"
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_aabb_index_query_2d_count_prepared_session(
    *,
    indexed_boxes: Any,
    backend: str,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    point_queries: Any = (),
    box_queries: Any = (),
    indexed_ids: Any | None = None,
    operation: str = "all",
    resolution: int = 32,
    prepare_session: Callable[[], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run generic 2-D AABB count queries through the V3 runner."""

    normalized_backend = str(backend).strip().lower().replace("-", "_")
    if normalized_backend not in {"embree", "optix"}:
        raise ValueError("AABB count runner requires backend 'embree' or 'optix'")
    normalized_operation = str(operation).strip()
    supported_operations = {"all", "point_contains", "range_contains", "range_intersects"}
    if normalized_operation not in supported_operations:
        raise ValueError("unsupported AABB count operation")
    resolved_resolution = int(resolution)
    if resolved_resolution < 1:
        raise ValueError("resolution must be positive")
    indexed_tuple = tuple(indexed_boxes)
    point_query_tuple = tuple(point_queries)
    box_query_tuple = tuple(box_queries)
    if not indexed_tuple:
        raise ValueError("AABB count runner requires indexed_boxes")
    if normalized_operation in {"all", "point_contains"} and not point_query_tuple:
        raise ValueError("AABB point_contains count requires point_queries")
    if normalized_operation in {"all", "range_contains", "range_intersects"} and not box_query_tuple:
        raise ValueError("AABB range count requires box_queries")
    indexed_id_tuple = (
        tuple(int(value) for value in indexed_ids)
        if indexed_ids is not None
        else tuple(range(len(indexed_tuple)))
    )
    if len(indexed_id_tuple) != len(indexed_tuple):
        raise ValueError("indexed_ids length must match indexed_boxes length")

    if prepare_session is None:
        from .aabb_index import prepare_aabb_index_2d

        def prepare_session() -> Any:
            return prepare_aabb_index_2d(
                indexed_tuple,
                point_queries=point_query_tuple,
                box_queries=box_query_tuple,
                indexed_ids=indexed_id_tuple,
                resolution=resolved_resolution,
                backend=normalized_backend,
            )

    def run_prepared(prepared: Any) -> dict[str, Any]:
        count_result = prepared.count(
            point_queries=point_query_tuple,
            box_queries=box_query_tuple,
            operation=normalized_operation,
        )
        counts = dict(count_result.get("counts", {}))
        candidate_checks = count_result.get("candidate_checks")
        cache_stats = getattr(prepared, "prepared_query_cache_stats", None)
        prepared_query_cache_stats = dict(cache_stats()) if callable(cache_stats) else None
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d_count",
            "backend": normalized_backend,
            "prepared": True,
            "operation": normalized_operation,
            "counts": {str(key): int(value) for key, value in counts.items()},
            "candidate_checks": candidate_checks,
            "query_counts": {
                "point_queries": len(point_query_tuple),
                "box_queries": len(box_query_tuple),
            },
            "index": count_result.get(
                "index",
                {
                    "indexed_boxes": len(indexed_tuple),
                    "resolution": resolved_resolution,
                    "backend": normalized_backend,
                },
            ),
            "indexed_box_count": len(indexed_tuple),
            "indexed_ids_fingerprint": make_prepared_input_fingerprint(indexed_id_tuple),
            "resolution": resolved_resolution,
            "prepared_query_cache_stats": prepared_query_cache_stats,
            "source_run_phases": dict(count_result.get("run_phases", {})),
            "metadata": {
                "adapter": "aabb_index_query_2d_count_prepared_session",
                "input_contract": "prepared_native_aabb_index_2d_with_point_and_box_queries",
                "native_engine_count_contract": "generic_prepared_aabb_index_query_2d_count",
                "partner": partner,
                "backend": normalized_backend,
                "native_query_handle_reuse": True,
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
            },
        }

    task = PreparedExecutionSessionTask(
        workflow_name="aabb_index_query_2d_count_prepared_session",
        primitive="aabb_index_query_2d_native_query_handle",
        backend=normalized_backend,
        partner=partner,
        input_fingerprints={
            "indexed_boxes": _stable_input_fingerprint(indexed_tuple),
            "point_queries": _stable_input_fingerprint(point_query_tuple),
            "box_queries": _stable_input_fingerprint(box_query_tuple),
        },
        parameters={
            "operation": normalized_operation,
            "indexed_ids": _stable_input_fingerprint(indexed_id_tuple),
            "resolution": resolved_resolution,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_prepared,
        validate_output=validate_output,
        notes=(
            "generic AABB count primitive routed through Phoenix V3 "
            "prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    metadata["set_a_probe_candidate"] = False
    metadata["set_b_control_candidate"] = True
    metadata["primitive_family"] = "aabb_index_query_2d_native_query_handle"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = "generic_prepared_aabb_index_query_2d_count"
    metadata["count_contract"] = "generic_prepared_aabb_index_query_2d_count"
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


class _OptixAabbPreparedQuerySetCountSession:
    def __init__(self, *, index: Any, point_queries: Any | None, box_queries: Any | None) -> None:
        self.index = index
        self.point_queries = point_queries
        self.box_queries = box_queries
        self.closed = False

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        for value in (self.point_queries, self.box_queries, self.index):
            close = getattr(value, "close", None)
            if callable(close):
                close()


def run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session(
    *,
    indexed_boxes: Any,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    point_queries: Any = (),
    box_queries: Any = (),
    operation: str = "all",
    prepare_session: Callable[[], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "cuda:0",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run OptiX AABB count queries with prepared query handles through the V3 runner."""

    normalized_operation = str(operation).strip()
    supported_operations = {"all", "point_contains", "range_contains", "range_intersects"}
    if normalized_operation not in supported_operations:
        raise ValueError("unsupported AABB count operation")
    indexed_tuple = tuple(indexed_boxes)
    point_query_tuple = tuple(point_queries)
    box_query_tuple = tuple(box_queries)
    if not indexed_tuple:
        raise ValueError("OptiX AABB prepared-query-set runner requires indexed_boxes")
    if normalized_operation in {"all", "point_contains"} and not point_query_tuple:
        raise ValueError("OptiX AABB point_contains count requires point_queries")
    if normalized_operation in {"all", "range_contains", "range_intersects"} and not box_query_tuple:
        raise ValueError("OptiX AABB range count requires box_queries")
    operations = (
        ("point_contains", "range_contains", "range_intersects")
        if normalized_operation == "all"
        else (normalized_operation,)
    )

    if prepare_session is None:
        from .optix_runtime import prepare_optix_aabb_box_queries_2d
        from .optix_runtime import prepare_optix_aabb_index_2d
        from .optix_runtime import prepare_optix_aabb_point_queries_2d

        def prepare_session() -> _OptixAabbPreparedQuerySetCountSession:
            index = prepare_optix_aabb_index_2d(indexed_tuple)
            point_handle = (
                prepare_optix_aabb_point_queries_2d(point_query_tuple)
                if "point_contains" in operations
                else None
            )
            box_handle = (
                prepare_optix_aabb_box_queries_2d(box_query_tuple)
                if any(name in {"range_contains", "range_intersects"} for name in operations)
                else None
            )
            return _OptixAabbPreparedQuerySetCountSession(
                index=index,
                point_queries=point_handle,
                box_queries=box_handle,
            )

    def run_prepared(session: Any) -> dict[str, Any]:
        index = getattr(session, "index", session)
        point_handle = getattr(session, "point_queries", None)
        box_handle = getattr(session, "box_queries", None)
        if normalized_operation == "all":
            count_set = index.count_prepared_query_set(
                point_queries=point_handle,
                box_queries=box_handle,
            )
            counts = {name: int(count_set[name]) for name in operations}
            native_call = "count_prepared_query_set"
        else:
            handle = point_handle if normalized_operation == "point_contains" else box_handle
            count = index.count_prepared_queries(handle, operation=normalized_operation)
            counts = {normalized_operation: int(count)}
            native_call = "count_prepared_queries"
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            "backend": "optix",
            "prepared": True,
            "operation": normalized_operation,
            "operations": tuple(operations),
            "counts": counts,
            "query_counts": {
                "point_queries": len(point_query_tuple),
                "box_queries": len(box_query_tuple),
            },
            "indexed_box_count": len(indexed_tuple),
            "prepared_query_set_native_call": native_call,
            "prepared_query_handles": {
                "point": point_handle is not None,
                "box": box_handle is not None,
            },
            "metadata": {
                "adapter": "aabb_index_query_2d_optix_prepared_query_set_count_prepared_session",
                "input_contract": "prepared_optix_aabb_index_2d_with_prepared_query_handles",
                "native_engine_count_contract": (
                    "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count"
                ),
                "partner": partner,
                "backend": "optix",
                "native_query_handle_reuse": True,
                "prepared_query_set_reuse": True,
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
            },
        }

    task = PreparedExecutionSessionTask(
        workflow_name="aabb_index_query_2d_optix_prepared_query_set_count_prepared_session",
        primitive="aabb_index_query_2d_native_query_handle",
        backend="optix",
        partner=partner,
        input_fingerprints={
            "indexed_boxes": _stable_input_fingerprint(indexed_tuple),
            "point_queries": _stable_input_fingerprint(point_query_tuple),
            "box_queries": _stable_input_fingerprint(box_query_tuple),
        },
        parameters={
            "operation": normalized_operation,
            "prepared_query_mode": "optix_prepared_query_set",
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_prepared,
        validate_output=validate_output,
        notes=(
            "generic OptiX AABB prepared-query-set count primitive routed "
            "through Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    metadata["set_a_probe_candidate"] = False
    metadata["set_b_control_candidate"] = True
    metadata["primitive_family"] = "aabb_index_query_2d_native_query_handle"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count"
    metadata["count_contract"] = "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count"
    metadata["prepared_query_mode"] = "optix_prepared_query_set"
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_radius_graph_component_signature_3d_prepared_session(
    *,
    point_rows: Any,
    point_rows_fingerprint: Any | None = None,
    radius: float,
    min_neighbors: int,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
    boundary_assignment_policy: str = "single_pass_candidate_root_rebased",
    prepare_session: Callable[[], Any] | None = None,
    run_component_signature: Callable[[Any], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run a generic 3-D fixed-radius component-signature continuation through the V3 runner."""

    radius = float(radius)
    min_neighbors = int(min_neighbors)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if min_neighbors < 0:
        raise ValueError("min_neighbors must be non-negative")
    if not isinstance(grouped_union_same_root_culling, bool):
        raise TypeError("grouped_union_same_root_culling must be a bool")
    if not isinstance(grouped_union_direct_side_effect, bool):
        raise TypeError("grouped_union_direct_side_effect must be a bool")
    resolved_block_size = (
        int(grouped_union_query_block_size)
        if grouped_union_query_block_size is not None
        else None
    )
    if resolved_block_size is not None and resolved_block_size <= 0:
        raise ValueError("grouped_union_query_block_size must be positive when provided")
    point_rows_tuple = tuple(point_rows)
    if not point_rows_tuple:
        raise ValueError("radius graph component-signature runner requires point_rows")
    resolved_point_rows_fingerprint = (
        make_prepared_input_fingerprint(point_rows_tuple)
        if point_rows_fingerprint is None
        else point_rows_fingerprint
    )

    if prepare_session is None:
        if str(partner).strip().lower() != "numba":
            raise ValueError(
                "default component-signature runner currently requires partner='numba'; "
                "provide prepare_session and run_component_signature for another explicit partner"
            )
        from .partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d

        def prepare_session() -> Any:
            return prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
                point_rows_tuple,
                radius=radius,
                partner=partner,
                grouped_union_query_block_size=resolved_block_size,
                grouped_union_same_root_culling=grouped_union_same_root_culling,
                grouped_union_direct_side_effect=grouped_union_direct_side_effect,
                boundary_assignment_policy=boundary_assignment_policy,
            )

    if run_component_signature is None:
        from .partner_adapters import (
            radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns,
        )

        def run_component_signature(prepared: Any) -> Any:
            return radius_graph_component_signature_3d_optix_numba_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=min_neighbors,
                return_metadata=True,
            )

    task = PreparedExecutionSessionTask(
        workflow_name="radius_graph_component_signature_3d_prepared_session",
        primitive="fixed_radius_graph_component_signature_3d",
        backend="optix",
        partner=partner,
        input_fingerprints={
            "point_rows": resolved_point_rows_fingerprint,
        },
        parameters={
            "radius": radius,
            "min_neighbors": min_neighbors,
            "grouped_union_query_block_size": resolved_block_size,
            "grouped_union_same_root_culling": grouped_union_same_root_culling,
            "grouped_union_direct_side_effect": grouped_union_direct_side_effect,
            "boundary_assignment_policy": boundary_assignment_policy,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_component_signature,
        validate_output=validate_output,
        notes=(
            "generic fixed-radius graph component-signature continuation routed "
            "through Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    hot_path_host_materialization = any(
        bool(output_metadata.get(key))
        for key in (
            "materializes_neighbor_rows",
            "materializes_directed_adjacency_stream",
            "materializes_bounded_directed_adjacency_chunks",
            "materializes_component_labels",
        )
    )
    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "fixed_radius_graph_component_signature"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = "grouped_stream_component_size_signature_3d"
    metadata["row_contract"] = "generic_fixed_radius_graph_component_signature_3d"
    metadata["phoenix_v3_redesign_step"] = "step1_runtime_trunk_probe"
    metadata["runtime_trunk_family"] = "fixed_radius_self_query_to_grouped_stream_component_signature_3d"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and output_metadata.get("internal_device_residency_between_rtdl_phases")
        and not hot_path_host_materialization
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_fixed_radius_self_query",
        "rt_core_threshold_flags_device_columns",
        "rt_core_grouped_union_device_workspaces",
        "numba_component_signature_device_workspaces",
    )
    metadata["internal_device_residency_between_rtdl_phases"] = bool(
        output_metadata.get("internal_device_residency_between_rtdl_phases")
    )
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["input_fingerprint_source"] = (
        "computed_in_helper" if point_rows_fingerprint is None else "caller_supplied"
    )
    metadata["large_input_fingerprint_hot_path_avoided"] = point_rows_fingerprint is not None
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_radius_graph_component_union_3d_prepared_session(
    *,
    point_rows: Any,
    point_rows_fingerprint: Any | None = None,
    radius: float,
    min_neighbors: int,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
    boundary_assignment_policy: str = "single_pass_candidate_root_rebased",
    output_contract: str = "generic_prepared_optix_numba_grouped_stream_component_labels_3d",
    prepare_session: Callable[[], Any] | None = None,
    run_component_union: Callable[[Any], Any] | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run the fixed-radius component-union pass as its own V3 core node."""

    radius = float(radius)
    min_neighbors = int(min_neighbors)
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if min_neighbors < 1:
        raise ValueError("min_neighbors must be at least 1")
    if not isinstance(grouped_union_same_root_culling, bool):
        raise TypeError("grouped_union_same_root_culling must be a bool")
    if not isinstance(grouped_union_direct_side_effect, bool):
        raise TypeError("grouped_union_direct_side_effect must be a bool")
    resolved_block_size = (
        int(grouped_union_query_block_size)
        if grouped_union_query_block_size is not None
        else None
    )
    if resolved_block_size is not None and resolved_block_size <= 0:
        raise ValueError("grouped_union_query_block_size must be positive when provided")
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    point_rows_tuple = tuple(point_rows)
    if not point_rows_tuple:
        raise ValueError("radius graph component-union runner requires point_rows")
    resolved_point_rows_fingerprint = (
        make_prepared_input_fingerprint(point_rows_tuple)
        if point_rows_fingerprint is None
        else point_rows_fingerprint
    )

    if prepare_session is None:
        if str(partner).strip().lower() != "numba":
            raise ValueError(
                "default component-union runner currently requires partner='numba'; "
                "provide prepare_session and run_component_union for another explicit partner"
            )
        from .partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d

        def prepare_session() -> Any:
            return prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
                point_rows_tuple,
                radius=radius,
                partner=partner,
                grouped_union_query_block_size=resolved_block_size,
                grouped_union_same_root_culling=grouped_union_same_root_culling,
                grouped_union_direct_side_effect=grouped_union_direct_side_effect,
                boundary_assignment_policy=boundary_assignment_policy,
            )

    if run_component_union is None:
        from .partner_adapters import (
            radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns,
        )

        def run_component_union(prepared: Any) -> Any:
            return radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                prepared,
                min_neighbors=min_neighbors,
                return_metadata=True,
            )
    elif not callable(run_component_union):
        raise TypeError("run_component_union must be callable when provided")

    task = PreparedExecutionSessionTask(
        workflow_name="radius_graph_component_union_3d_prepared_session",
        primitive="fixed_radius_graph_component_union_3d",
        backend="optix",
        partner=partner,
        input_fingerprints={
            "point_rows": resolved_point_rows_fingerprint,
        },
        parameters={
            "radius": radius,
            "min_neighbors": min_neighbors,
            "grouped_union_query_block_size": resolved_block_size,
            "grouped_union_same_root_culling": grouped_union_same_root_culling,
            "grouped_union_direct_side_effect": grouped_union_direct_side_effect,
            "boundary_assignment_policy": boundary_assignment_policy,
            "output_contract": resolved_output_contract,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_component_union,
        validate_output=validate_output,
        notes=(
            "generic fixed-radius graph component-union pass routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )

    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    output_columns = (
        dict(output_payload.get("columns", {}))
        if isinstance(output_payload, Mapping) and isinstance(output_payload.get("columns"), Mapping)
        else {}
    )
    native_grouped_stream_metadata = output_metadata.get("native_grouped_stream_metadata")
    if not isinstance(native_grouped_stream_metadata, Mapping):
        native_grouped_stream_metadata = {}
    actual_output_contract = str(
        output_metadata.get("contract")
        or output_metadata.get("partner_reference_contract")
        or ""
    )
    actual_output_partner = str(output_metadata.get("partner") or "").strip().lower().replace("-", "_")
    output_contract_matches_requested = actual_output_contract == resolved_output_contract
    output_partner_matches_requested = actual_output_partner == str(partner).strip().lower().replace("-", "_")
    component_union_pass_count = output_metadata.get(
        "grouped_stream_continuation_pass_count",
        output_metadata.get("grouped_union_query_block_count"),
    )
    component_union_phase_accounting_visible = bool(
        output_metadata.get("component_union_policy")
        and component_union_pass_count is not None
        and native_grouped_stream_metadata
    )
    component_signature_pass_executed = bool(output_metadata.get("component_signature_policy"))
    component_label_columns_present = "component_labels" in output_columns
    component_label_pass_accounted = bool(
        output_metadata.get("component_label_policy")
        and component_label_columns_present
    )
    hot_path_host_materialization = any(
        bool(output_metadata.get(key))
        for key in (
            "hot_path_host_materialization",
            "materializes_neighbor_rows",
            "materializes_directed_adjacency_stream",
            "materializes_bounded_directed_adjacency_chunks",
            "host_rows_materialized",
            "host_output_materialized",
        )
    )
    internal_device_residency = bool(
        output_metadata.get("internal_device_residency_between_rtdl_phases")
    )
    runtime_trunk_executes = bool(
        metadata.get("runtime_executed")
        and output_contract_matches_requested
        and output_partner_matches_requested
        and component_union_phase_accounting_visible
        and component_label_pass_accounted
        and not component_signature_pass_executed
        and internal_device_residency
        and not hot_path_host_materialization
    )

    metadata["set_a_probe_candidate"] = True
    metadata["set_b_control_candidate"] = False
    metadata["primitive_family"] = "fixed_radius_graph_component_union"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = resolved_output_contract
    metadata["row_contract"] = "generic_fixed_radius_graph_component_union_3d"
    metadata["phoenix_v3_redesign_step"] = "m37_component_union_core_node_split"
    metadata["runtime_trunk_family"] = "fixed_radius_self_query_to_grouped_stream_component_union_3d"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = runtime_trunk_executes
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_fixed_radius_self_query",
        "rt_core_threshold_flags_device_columns",
        "rt_core_grouped_union_device_workspaces",
        "numba_component_label_device_columns",
        "component_union_summary_return",
    )
    metadata["input_fingerprint_source"] = (
        "computed_in_helper" if point_rows_fingerprint is None else "caller_supplied"
    )
    metadata["large_input_fingerprint_hot_path_avoided"] = point_rows_fingerprint is not None
    metadata["output_contract"] = resolved_output_contract
    metadata["actual_output_contract"] = actual_output_contract or None
    metadata["output_contract_matches_requested"] = output_contract_matches_requested
    metadata["actual_output_partner"] = actual_output_partner or None
    metadata["output_partner_matches_requested"] = output_partner_matches_requested
    metadata["component_union_phase_accounting_visible"] = component_union_phase_accounting_visible
    metadata["component_union_policy"] = output_metadata.get("component_union_policy")
    metadata["component_union_native_execution_path"] = native_grouped_stream_metadata.get("native_execution_path")
    metadata["component_union_native_elapsed_sec"] = native_grouped_stream_metadata.get("native_elapsed_sec")
    metadata["component_union_pass_count"] = component_union_pass_count
    metadata["grouped_union_query_block_size"] = output_metadata.get("grouped_union_query_block_size")
    metadata["grouped_union_query_block_count"] = output_metadata.get("grouped_union_query_block_count")
    metadata["boundary_assignment_policy"] = output_metadata.get("boundary_assignment_policy")
    metadata["boundary_assignment_canonical_policy"] = output_metadata.get("boundary_assignment_canonical_policy")
    metadata["boundary_assignment_pass_count"] = native_grouped_stream_metadata.get("boundary_assignment_pass_count")
    metadata["component_label_pass_accounted"] = component_label_pass_accounted
    metadata["component_label_columns_present"] = component_label_columns_present
    metadata["component_label_policy"] = output_metadata.get("component_label_policy")
    metadata["component_signature_accounting_split"] = True
    metadata["component_signature_pass_executed"] = component_signature_pass_executed
    metadata["component_signature_policy"] = output_metadata.get("component_signature_policy")
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["native_engine_row_contract"] = output_metadata.get("native_engine_row_contract")
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def _topology_stream_m3_bridge_metadata(
    *,
    backend: str,
    generic_capability: str,
    output_contract: str,
    query_count: int,
    warmup_count: int,
    measured_repeat_count: int,
    output_payload: Any,
    prepared_handle: Mapping[str, Any],
    native_phase_timings: Mapping[str, Any],
    query_stream_residency: str,
    internal_device_residency: bool,
) -> dict[str, Any]:
    from .v3_0_topology_stream_accounting import (
        TOPOLOGY_STREAM_M3_PHASES,
        build_topology_stream_m3_phase_table,
        build_topology_stream_prepared_handle_metadata,
        validate_topology_stream_m3_phase_table,
    )

    payload_mapping = output_payload if isinstance(output_payload, Mapping) else {}
    provided_table = payload_mapping.get("topology_stream_m3_phase_table", {})
    if isinstance(provided_table, Mapping) and isinstance(
        provided_table.get("phase_seconds"), Mapping
    ):
        m3_phase_table = dict(provided_table)
        validate_topology_stream_m3_phase_table(m3_phase_table)
    else:
        phases_sec = payload_mapping.get("phases_sec", {})
        if not isinstance(phases_sec, Mapping):
            phases_sec = {}
        m3_phase_table = build_topology_stream_m3_phase_table(
            phases_sec=phases_sec,
            native_phase_timings=native_phase_timings,
            output_contract=output_contract,
            query_count=query_count,
            repeat=measured_repeat_count,
            warmup=warmup_count,
            query_stream_resident=internal_device_residency,
            table_basis="prepared_execution_topology_stream_m3_bridge_v1",
        )

    handle_metadata = build_topology_stream_prepared_handle_metadata(
        backend=backend,
        generic_capability=generic_capability,
        output_contract=output_contract,
        query_count=query_count,
        static_scene_prepared=bool(prepared_handle.get("static_scene_prepared", True)),
        query_stream_prepared=prepared_handle.get("query_stream_prepared") is True,
        query_stream_residency=query_stream_residency or "unknown",
        m3_phase_table=m3_phase_table,
    )
    full_m3 = bool(m3_phase_table["full_m3_phase_table_complete"])
    return {
        "prepared_execution_to_topology_stream_m3_bridge_contract": (
            "prepared_execution_to_topology_stream_m3_bridge_v1"
        ),
        "prepared_execution_to_topology_stream_m3_bridge_required": True,
        "prepared_execution_to_topology_stream_m3_bridge_status": (
            "complete_non_authorizing_m3_bridge"
            if full_m3
            else "partial_non_authorizing_m3_bridge"
        ),
        "prepared_execution_required_phases": tuple(PREPARED_EXECUTION_REQUIRED_PHASES),
        "topology_stream_m3_required_phases": tuple(TOPOLOGY_STREAM_M3_PHASES),
        "topology_stream_m3_phase_table": m3_phase_table,
        "topology_stream_m3_phase_table_contract": m3_phase_table["contract"],
        "topology_stream_m3_phase_table_complete": full_m3,
        "topology_stream_m3_phase_seconds": dict(m3_phase_table["phase_seconds"]),
        "topology_stream_m3_missing_phases_for_public_row": tuple(
            m3_phase_table["missing_m3_phases_for_public_row"]
        ),
        "topology_stream_prepared_handle": handle_metadata,
        "topology_stream_prepared_handle_contract": handle_metadata["contract"],
        "topology_stream_prepared_handle_full_m3_phase_table_complete": bool(
            handle_metadata["full_m3_phase_table_complete"]
        ),
        "topology_stream_m3_bridge_public_row_authorized": False,
        "topology_stream_m3_bridge_m7_promotion_authorized": False,
    }


def run_point_location_topology_stream_prepared_session(
    *,
    query_stream_fingerprint: Any,
    static_scene_fingerprint: Any,
    output_contract: str,
    query_count: int,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    prepare_session: Callable[[], Any],
    run_topology_stream: Callable[[Any], Any],
    backend: str = "optix",
    shape_count: int | None = None,
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run a generic point-location topology stream through the V3 runner."""

    resolved_backend = str(backend).strip().lower().replace("-", "_")
    if resolved_backend not in {"optix", "embree"}:
        raise ValueError("point-location topology-stream runner requires backend 'optix' or 'embree'")
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    resolved_query_count = int(query_count)
    if resolved_query_count <= 0:
        raise ValueError("query_count must be positive")
    resolved_shape_count = int(shape_count) if shape_count is not None else None
    if resolved_shape_count is not None and resolved_shape_count < 0:
        raise ValueError("shape_count must be non-negative")
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable")
    if not callable(run_topology_stream):
        raise TypeError("run_topology_stream must be callable")

    task = PreparedExecutionSessionTask(
        workflow_name="point_location_topology_stream_prepared_session",
        primitive="point_location_topology_stream",
        backend=resolved_backend,
        partner=partner,
        input_fingerprints={
            "query_stream": query_stream_fingerprint,
            "static_scene": static_scene_fingerprint,
        },
        parameters={
            "output_contract": resolved_output_contract,
            "query_count": resolved_query_count,
            "shape_count": resolved_shape_count,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_topology_stream,
        validate_output=validate_output,
        notes=(
            "generic point-location topology stream routed through Phoenix V3 "
            "prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    prepared_handle = (
        dict(output_payload.get("topology_stream_prepared_handle", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    native_phase_timings = (
        dict(output_payload.get("native_phase_timings", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    query_stream_residency = str(prepared_handle.get("query_stream_residency") or "")
    row_stream_materialized = any(
        bool(native_phase_timings.get(key) or output_metadata.get(key))
        for key in (
            "row_stream_materialized",
            "boundary_candidate_row_stream_materialized",
            "materializes_python_rows",
            "hot_path_host_materialization",
        )
    )
    host_download_seconds = sum(
        float(native_phase_timings.get(key) or 0.0)
        for key in (
            "candidate_download",
            "flag_download",
            "count_download",
            "row_download",
        )
    )
    internal_device_residency = bool(
        output_metadata.get("internal_device_residency_between_rtdl_phases")
        or (
            prepared_handle.get("query_stream_prepared") is True
            and "device_resident" in query_stream_residency
            and not row_stream_materialized
            and host_download_seconds == 0.0
        )
    )
    hot_path_host_materialization = bool(row_stream_materialized or host_download_seconds > 0.0)

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "point_location_topology_stream"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = resolved_output_contract
    metadata["row_contract"] = resolved_output_contract
    metadata["phoenix_v3_redesign_step"] = "step2_runtime_trunk_generalization_probe"
    metadata["runtime_trunk_family"] = "point_location_topology_stream_relation_status_scalar_count"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and internal_device_residency
        and not hot_path_host_materialization
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_point_location_static_scene",
        "prepare_device_resident_query_stream",
        "rt_core_point_location_traversal",
        "device_resident_topology_stream_continuation",
        "scalar_or_summary_return",
    )
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["native_phase_host_download_seconds"] = host_download_seconds
    metadata["query_stream_residency"] = query_stream_residency or None
    metadata.update(
        _topology_stream_m3_bridge_metadata(
            backend=resolved_backend,
            generic_capability="point_location_topology_stream",
            output_contract=resolved_output_contract,
            query_count=resolved_query_count,
            warmup_count=warmup_count,
            measured_repeat_count=int(metadata.get("measured_repeat_count") or measured_repeat_count),
            output_payload=output_payload,
            prepared_handle=prepared_handle,
            native_phase_timings=native_phase_timings,
            query_stream_residency=query_stream_residency,
            internal_device_residency=internal_device_residency,
        )
    )
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_segment_intersection_topology_stream_prepared_session(
    *,
    query_stream_fingerprint: Any,
    static_scene_fingerprint: Any,
    output_contract: str,
    query_count: int,
    right_segment_count: int | None,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    prepare_session: Callable[[], Any],
    run_topology_stream: Callable[[Any], Any],
    measured_run_prepared: Callable[[Any], Any] | None = None,
    finalize_output: Callable[[Any, Any], Any] | None = None,
    backend: str = "optix",
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run a generic segment-intersection topology stream through the V3 runner."""

    resolved_backend = str(backend).strip().lower().replace("-", "_")
    if resolved_backend not in {"optix", "embree"}:
        raise ValueError("segment-intersection topology-stream runner requires backend 'optix' or 'embree'")
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    resolved_query_count = int(query_count)
    if resolved_query_count <= 0:
        raise ValueError("query_count must be positive")
    resolved_right_segment_count = (
        int(right_segment_count) if right_segment_count is not None else None
    )
    if resolved_right_segment_count is not None and resolved_right_segment_count < 0:
        raise ValueError("right_segment_count must be non-negative")
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable")
    if not callable(run_topology_stream):
        raise TypeError("run_topology_stream must be callable")
    if measured_run_prepared is not None and not callable(measured_run_prepared):
        raise TypeError("measured_run_prepared must be callable when provided")
    if finalize_output is not None and not callable(finalize_output):
        raise TypeError("finalize_output must be callable when provided")

    task = PreparedExecutionSessionTask(
        workflow_name="segment_intersection_topology_stream_prepared_session",
        primitive="segment_intersection_topology_stream",
        backend=resolved_backend,
        partner=partner,
        input_fingerprints={
            "query_stream": query_stream_fingerprint,
            "static_scene": static_scene_fingerprint,
        },
        parameters={
            "output_contract": resolved_output_contract,
            "query_count": resolved_query_count,
            "right_segment_count": resolved_right_segment_count,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_topology_stream,
        measured_run_prepared=measured_run_prepared,
        finalize_output=finalize_output,
        validate_output=validate_output,
        notes=(
            "generic segment-intersection topology stream routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    prepared_handle = (
        dict(output_payload.get("topology_stream_prepared_handle", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    native_phase_timings = (
        dict(output_payload.get("native_phase_timings", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    query_stream_residency = str(prepared_handle.get("query_stream_residency") or "")
    row_stream_materialized = any(
        bool(native_phase_timings.get(key) or output_metadata.get(key))
        for key in (
            "row_stream_materialized",
            "candidate_row_stream_materialized",
            "materializes_python_rows",
            "hot_path_host_materialization",
            "count_column_materialized_on_host",
            "group_key_column_materialized_on_host",
        )
    )
    host_download_seconds = sum(
        float(native_phase_timings.get(key) or 0.0)
        for key in (
            "candidate_download",
            "flag_download",
            "count_download",
            "row_download",
        )
    )
    internal_device_residency = bool(
        output_metadata.get("internal_device_residency_between_rtdl_phases")
        or (
            prepared_handle.get("query_stream_prepared") is True
            and "device_resident" in query_stream_residency
            and not row_stream_materialized
            and host_download_seconds == 0.0
        )
    )
    hot_path_host_materialization = bool(row_stream_materialized or host_download_seconds > 0.0)

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "segment_intersection_topology_stream"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = resolved_output_contract
    metadata["row_contract"] = resolved_output_contract
    metadata["phoenix_v3_redesign_step"] = "step2_runtime_trunk_generalization_probe"
    metadata["runtime_trunk_family"] = "segment_intersection_topology_stream_left_id_dense_count"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and internal_device_residency
        and not hot_path_host_materialization
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_segment_intersection_static_scene",
        "prepare_device_resident_left_segment_query_stream",
        "rt_core_segment_intersection_traversal",
        "device_resident_left_id_count_continuation",
        "scalar_or_summary_return",
    )
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["native_phase_host_download_seconds"] = host_download_seconds
    metadata["query_stream_residency"] = query_stream_residency or None
    metadata.update(
        _topology_stream_m3_bridge_metadata(
            backend=resolved_backend,
            generic_capability="segment_intersection_topology_stream",
            output_contract=resolved_output_contract,
            query_count=resolved_query_count,
            warmup_count=warmup_count,
            measured_repeat_count=int(metadata.get("measured_repeat_count") or measured_repeat_count),
            output_payload=output_payload,
            prepared_handle=prepared_handle,
            native_phase_timings=native_phase_timings,
            query_stream_residency=query_stream_residency,
            internal_device_residency=internal_device_residency,
        )
    )
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_grouped_vector_sum_2d_prepared_session(
    *,
    vector_columns_fingerprint: Any,
    row_offsets_fingerprint: Any,
    row_count: int,
    group_count: int,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    prepare_session: Callable[[], Any],
    run_grouped_vector_sum: Callable[[Any], Any] | None = None,
    backend: str = "partner",
    output_contract: str = "generic_grouped_vector_sum_f64x2",
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run a generic grouped vector-sum continuation through the V3 runner."""

    resolved_backend = str(backend).strip().lower().replace("-", "_")
    if not resolved_backend:
        raise ValueError("backend is required")
    resolved_partner = str(partner).strip().lower().replace("-", "_")
    if resolved_partner not in {"numba", "cupy"}:
        raise ValueError("grouped vector-sum prepared session currently requires partner='numba' or partner='cupy'")
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    resolved_row_count = int(row_count)
    resolved_group_count = int(group_count)
    if resolved_row_count <= 0:
        raise ValueError("row_count must be positive")
    if resolved_group_count <= 0:
        raise ValueError("group_count must be positive")
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable")

    if run_grouped_vector_sum is None:
        from .partner_adapters import run_grouped_vector_sum_2d_partner_columns_session

        def run_grouped_vector_sum(prepared: Any) -> Any:
            return run_grouped_vector_sum_2d_partner_columns_session(
                prepared,
                return_metadata=True,
            )
    elif not callable(run_grouped_vector_sum):
        raise TypeError("run_grouped_vector_sum must be callable when provided")

    task = PreparedExecutionSessionTask(
        workflow_name="grouped_vector_sum_2d_prepared_session",
        primitive="grouped_vector_sum_2d",
        backend=resolved_backend,
        partner=resolved_partner,
        input_fingerprints={
            "vector_columns": vector_columns_fingerprint,
            "row_offsets": row_offsets_fingerprint,
        },
        parameters={
            "output_contract": resolved_output_contract,
            "row_count": resolved_row_count,
            "group_count": resolved_group_count,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_grouped_vector_sum,
        validate_output=validate_output,
        notes=(
            "generic grouped vector-sum continuation routed through Phoenix V3 "
            "prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )

    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    actual_output_contract = str(
        output_metadata.get("contract")
        or output_metadata.get("partner_reference_contract")
        or ""
    )
    actual_output_partner = str(output_metadata.get("partner") or "").strip().lower().replace("-", "_")
    output_contract_matches_requested = actual_output_contract == resolved_output_contract
    output_partner_matches_requested = actual_output_partner == resolved_partner
    output_row_count = output_metadata.get("row_count")
    output_group_count = output_metadata.get("group_count")
    output_counts_present = bool(output_row_count is not None and output_group_count is not None)
    output_counts_match_requested = bool(
        output_counts_present
        and int(output_row_count) == resolved_row_count
        and int(output_group_count) == resolved_group_count
    )
    launch_prefix = f"v2_5_{resolved_partner}"
    offset_program_count = output_metadata.get(f"{launch_prefix}_offset_program_count")
    threads_per_block = output_metadata.get(f"{launch_prefix}_threads_per_block")
    groups_per_block = output_metadata.get(f"{launch_prefix}_groups_per_block")
    threads_per_group = output_metadata.get(f"{launch_prefix}_threads_per_group")
    launch_parallelism_axis = output_metadata.get(f"{launch_prefix}_launch_parallelism_axis")
    rows_per_group_mean = output_metadata.get(f"{launch_prefix}_rows_per_group_mean")
    kernel_strategy = output_metadata.get(f"{launch_prefix}_kernel_strategy")
    tiled_row_parallel = output_metadata.get(f"{launch_prefix}_tiled_row_parallel_reduction_used")
    thread_per_group_serial = output_metadata.get(f"{launch_prefix}_thread_per_group_serial_loop_used")
    output_columns_reused = output_metadata.get("output_columns_reused") is True
    per_run_validation = output_metadata.get("per_run_neutral_handoff_validation_used") is True
    host_materialization_flag = any(
        bool(output_metadata.get(key))
        for key in (
            "host_rows_materialized",
            "host_output_materialized",
            "hot_path_host_materialization",
            "per_run_host_validation_materialized",
        )
    )
    hot_path_host_materialization = bool(per_run_validation or host_materialization_flag)
    internal_device_residency = bool(
        output_columns_reused
        and output_contract_matches_requested
        and output_partner_matches_requested
        and output_counts_match_requested
        and not hot_path_host_materialization
    )

    metadata["set_a_probe_candidate"] = True
    metadata["set_b_control_candidate"] = False
    metadata["primitive_family"] = "grouped_vector_sum_2d"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = resolved_output_contract
    metadata["row_contract"] = "generic_presegmented_grouped_vector_sum_2d"
    metadata["phoenix_v3_redesign_step"] = "m36_grouped_reduction_core_node"
    metadata["runtime_trunk_family"] = "grouped_vector_sum_2d_partner_columns_session"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and output_contract_matches_requested
        and output_partner_matches_requested
        and output_counts_match_requested
        and internal_device_residency
        and not hot_path_host_materialization
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_presegmented_grouped_vector_columns",
        "prepare_partner_grouped_vector_sum_session",
        "partner_grouped_vector_sum_replay",
        "device_resident_grouped_sum_columns",
        "summary_return",
    )
    metadata["row_count"] = resolved_row_count
    metadata["group_count"] = resolved_group_count
    metadata["output_contract"] = resolved_output_contract
    metadata["actual_output_contract"] = actual_output_contract or None
    metadata["output_contract_matches_requested"] = output_contract_matches_requested
    metadata["actual_output_partner"] = actual_output_partner or None
    metadata["output_partner_matches_requested"] = output_partner_matches_requested
    metadata["adapter_row_count"] = output_row_count
    metadata["adapter_group_count"] = output_group_count
    metadata["adapter_counts_present"] = output_counts_present
    metadata["output_counts_match_requested"] = output_counts_match_requested
    metadata[f"{launch_prefix}_offset_program_count"] = offset_program_count
    metadata[f"{launch_prefix}_threads_per_block"] = threads_per_block
    metadata[f"{launch_prefix}_groups_per_block"] = groups_per_block
    metadata[f"{launch_prefix}_threads_per_group"] = threads_per_group
    metadata[f"{launch_prefix}_launch_parallelism_axis"] = launch_parallelism_axis
    metadata[f"{launch_prefix}_rows_per_group_mean"] = rows_per_group_mean
    metadata[f"{launch_prefix}_kernel_strategy"] = kernel_strategy
    metadata[f"{launch_prefix}_tiled_row_parallel_reduction_used"] = bool(tiled_row_parallel)
    metadata[f"{launch_prefix}_thread_per_group_serial_loop_used"] = bool(thread_per_group_serial)
    metadata["grouped_reduction_launch_shape"] = {
        "partner": resolved_partner,
        "parallelism_axis": launch_parallelism_axis,
        "kernel_strategy": kernel_strategy,
        "program_count": offset_program_count,
        "threads_per_block": threads_per_block,
        "groups_per_block": groups_per_block,
        "threads_per_group": threads_per_group,
        "row_count": resolved_row_count,
        "group_count": resolved_group_count,
        "rows_per_group_mean": rows_per_group_mean,
        "tiled_row_parallel_reduction_used": bool(tiled_row_parallel),
        "thread_per_group_serial_loop_used": bool(thread_per_group_serial),
    }
    metadata["output_columns_reused"] = output_columns_reused
    metadata["per_run_neutral_handoff_validation_used"] = per_run_validation
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["native_engine_row_contract"] = output_metadata.get("native_engine_row_contract")
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
    *,
    source_fingerprint: Any,
    target_fingerprint: Any,
    aggregate_tree_fingerprint: Any,
    source_count: int,
    target_count: int,
    tree_node_count: int,
    theta: float,
    softening: float,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    prepare_session: Callable[[], Any],
    run_vector_sum: Callable[[Any], Any],
    backend: str = "partner",
    output_contract: str = "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
    scorecard_binding: Mapping[str, Any] | None = None,
    win_source: str = "partner_continuation",
) -> PreparedExecutionSessionResult:
    """Run a generic aggregate-tree fused vector sum through the V3 runner."""

    resolved_backend = str(backend).strip().lower().replace("-", "_")
    if not resolved_backend:
        raise ValueError("backend is required")
    resolved_partner = str(partner).strip().lower().replace("-", "_")
    if resolved_partner not in {"numba_cuda", "native_cuda"}:
        raise ValueError(
            "aggregate-tree fused vector-sum runner currently requires "
            "partner='numba_cuda' or partner='native_cuda'"
        )
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    resolved_source_count = int(source_count)
    resolved_target_count = int(target_count)
    resolved_tree_node_count = int(tree_node_count)
    if resolved_source_count <= 0:
        raise ValueError("source_count must be positive")
    if resolved_target_count <= 0:
        raise ValueError("target_count must be positive")
    if resolved_tree_node_count <= 0:
        raise ValueError("tree_node_count must be positive")
    resolved_theta = float(theta)
    resolved_softening = float(softening)
    if resolved_theta <= 0.0:
        raise ValueError("theta must be positive")
    if resolved_softening < 0.0:
        raise ValueError("softening must be non-negative")
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable")
    if not callable(run_vector_sum):
        raise TypeError("run_vector_sum must be callable")
    resolved_win_source = str(win_source).strip().lower()
    allowed_win_sources = {"residency_wall", "partner_continuation", "kernel"}
    if resolved_win_source not in allowed_win_sources:
        raise ValueError("win_source must be one of residency_wall, partner_continuation, or kernel")
    binding_payload = dict(scorecard_binding or {})
    scorecard_blocker_bound = bool(binding_payload)
    if scorecard_blocker_bound:
        required_binding_fields = (
            "id",
            "set",
            "app",
            "metric",
            "current_value",
            "source",
            "route_kind",
        )
        missing_binding_fields = tuple(
            field for field in required_binding_fields if field not in binding_payload
        )
        if missing_binding_fields:
            raise ValueError(
                "scorecard_binding missing required fields: "
                + ", ".join(missing_binding_fields)
            )
        if str(binding_payload.get("route_kind")).strip() not in {
            "trunk_fix_candidate",
            "severe_regression_repair",
        }:
            raise ValueError("scorecard_binding.route_kind must name trunk_fix_candidate or severe_regression_repair")

    task = PreparedExecutionSessionTask(
        workflow_name="aggregate_tree_fused_weighted_vector_sum_2d_prepared_session",
        primitive="aggregate_tree_fused_weighted_vector_sum_2d",
        backend=resolved_backend,
        partner=resolved_partner,
        input_fingerprints={
            "source_points": source_fingerprint,
            "target_points": target_fingerprint,
            "aggregate_tree": aggregate_tree_fingerprint,
        },
        parameters={
            "output_contract": resolved_output_contract,
            "source_count": resolved_source_count,
            "target_count": resolved_target_count,
            "tree_node_count": resolved_tree_node_count,
            "theta": resolved_theta,
            "softening": resolved_softening,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_vector_sum,
        validate_output=validate_output,
        notes=(
            "generic aggregate-tree fused weighted-vector sum routed through "
            "Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=measured_repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if int(measured_repeat_count) != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_metadata = (
        dict(output_payload.get("metadata", {}))
        if isinstance(output_payload, Mapping)
        else {}
    )
    actual_output_contract = str(output_metadata.get("contract") or "")
    output_contract_matches_requested = actual_output_contract == resolved_output_contract
    actual_output_partner = str(output_metadata.get("partner") or "").strip().lower().replace("-", "_")
    output_partner_matches_requested = actual_output_partner == resolved_partner
    output_source_count = output_metadata.get("source_count")
    output_target_count = output_metadata.get("target_count")
    output_tree_node_count = output_metadata.get("tree_node_count")
    output_counts_match_requested = bool(
        output_source_count is not None
        and output_target_count is not None
        and output_tree_node_count is not None
        and int(output_source_count) == resolved_source_count
        and int(output_target_count) == resolved_target_count
        and int(output_tree_node_count) == resolved_tree_node_count
    )
    frontier_rows_materialized = any(
        bool(output_metadata.get(key))
        for key in (
            "frontier_rows_emitted",
            "frontier_rows_materialized_on_host",
            "materialized_frontier_rows",
        )
    )
    contribution_rows_materialized = any(
        bool(output_metadata.get(key))
        for key in (
            "contribution_rows_materialized_on_host",
            "materialized_contribution_rows",
        )
    )
    output_device_resident = bool(output_metadata.get("device_resident"))
    output_columns_reused = bool(output_metadata.get("output_columns_reused"))
    output_residency_ok = bool(output_columns_reused or output_device_resident)
    internal_device_residency = bool(
        output_metadata.get("prepared_lookup_columns_resident")
        and output_metadata.get("source_columns_reused")
        and output_metadata.get("target_columns_reused")
        and output_metadata.get("aggregate_tree_columns_resident")
        and output_residency_ok
        and not frontier_rows_materialized
        and not contribution_rows_materialized
    )
    hot_path_host_materialization = bool(
        frontier_rows_materialized or contribution_rows_materialized
    )

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "aggregate_tree_fused_weighted_vector_sum_2d"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["continuation_contract"] = resolved_output_contract
    metadata["row_contract"] = resolved_output_contract
    metadata["phoenix_v3_redesign_step"] = "step1_replacement_runtime_trunk_probe"
    metadata["runtime_trunk_family"] = "aggregate_tree_fused_weighted_vector_sum_2d_explicit_partner"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["win_source"] = resolved_win_source
    metadata["win_source_classification_required"] = True
    metadata["win_source_allowed_values"] = tuple(sorted(allowed_win_sources))
    metadata["scorecard_blocker_bound"] = scorecard_blocker_bound
    metadata["scorecard_binding"] = binding_payload
    metadata["scorecard_controlling_row_binding_required_before_release_path"] = True
    metadata["release_path_candidate"] = False
    if scorecard_blocker_bound:
        metadata["scorecard_blocker_set"] = binding_payload.get("set")
        metadata["scorecard_blocker_app"] = binding_payload.get("app")
        metadata["scorecard_blocker_metric"] = binding_payload.get("metric")
        metadata["scorecard_blocker_current_value"] = binding_payload.get("current_value")
        metadata["scorecard_blocker_source"] = binding_payload.get("source")
        metadata["scorecard_blocker_route_kind"] = binding_payload.get("route_kind")
        metadata["scorecard_blocker_target"] = binding_payload.get("target")
        metadata["scorecard_blocker_role"] = binding_payload.get("role")
        metadata["release_path_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and output_contract_matches_requested
        and output_partner_matches_requested
        and output_counts_match_requested
        and internal_device_residency
        and not hot_path_host_materialization
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_weighted_source_target_columns",
        "prepare_aggregate_tree_columns",
        "partner_fused_tree_traversal_and_vector_accumulation",
        "device_resident_vector_and_count_columns",
        "summary_return",
    )
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["frontier_rows_materialized_on_host"] = frontier_rows_materialized
    metadata["contribution_rows_materialized_on_host"] = contribution_rows_materialized
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["output_contract"] = resolved_output_contract
    metadata["actual_output_contract"] = actual_output_contract or None
    metadata["output_contract_matches_requested"] = output_contract_matches_requested
    metadata["actual_output_partner"] = actual_output_partner or None
    metadata["output_partner_matches_requested"] = output_partner_matches_requested
    metadata["output_counts_match_requested"] = output_counts_match_requested
    metadata["output_columns_reused"] = output_columns_reused
    metadata["output_device_resident"] = output_device_resident
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["m72_target_blocker_review_required_before_pod"] = bool(scorecard_blocker_bound)
    metadata["m72_target_blocker"] = binding_payload.get("id")
    if resolved_partner == "numba_cuda":
        metadata["m43_reuse_scope"] = (
            "reuse prepared-runner explicit-partner continuation discipline; "
            "this aggregate-tree path uses numba_cuda, not the M43 CuPy grouped-reduction kernel"
        )
    else:
        metadata["m43_reuse_scope"] = (
            "reuse prepared-runner explicit-partner continuation discipline; "
            "this aggregate-tree path uses a native CUDA device-resident fused kernel, "
            "not the M43 CuPy grouped-reduction kernel"
        )
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
    *,
    triangle_fingerprint: Any,
    ray_batch_fingerprint: Any,
    weight_fingerprint: Any,
    primitive_count: int,
    ray_count: int,
    expected_weighted_hit_sum: int | None,
    partner: str,
    cache: ExplicitPreparedSessionCache,
    prepare_session: Callable[[], Any],
    run_weighted_summary: Callable[[Any], Any] | None = None,
    finalize_weighted_summary: Callable[[Any, Any], Any] | None = None,
    backend: str = "optix",
    output_contract: str = "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1",
    validate_output: Callable[[Any], Any] | None = None,
    device: str = "unknown",
    warmup_count: int = 0,
    measured_repeat_count: int = 1,
    require_repeat5_material_probe: bool = False,
    validate_each_repeat: bool = False,
    retain_repeat_outputs: bool = False,
) -> PreparedExecutionSessionResult:
    """Run generic ray/triangle weighted-summary device-output through V3 runner."""

    resolved_backend = str(backend).strip().lower().replace("-", "_")
    if resolved_backend != "optix":
        raise ValueError("ray-triangle device-output stream runner currently requires backend='optix'")
    resolved_partner = str(partner).strip().lower().replace("-", "_")
    if resolved_partner in {"", "none", "auto", "automatic"}:
        raise ValueError("ray-triangle device-output stream runner requires an explicit partner")
    resolved_output_contract = str(output_contract).strip()
    if not resolved_output_contract:
        raise ValueError("output_contract is required")
    lowered_output_contract = resolved_output_contract.lower()
    for forbidden in ("triangle_counting", "rt_graph", "graph_database"):
        if forbidden in lowered_output_contract:
            raise ValueError("output_contract must stay generic and app-agnostic")
    resolved_primitive_count = int(primitive_count)
    resolved_ray_count = int(ray_count)
    if resolved_primitive_count <= 0:
        raise ValueError("primitive_count must be positive")
    if resolved_ray_count <= 0:
        raise ValueError("ray_count must be positive")
    expected_sum = (
        None
        if expected_weighted_hit_sum is None
        else int(expected_weighted_hit_sum)
    )
    if expected_sum is not None and expected_sum < 0:
        raise ValueError("expected_weighted_hit_sum must be non-negative when provided")
    repeat_count = int(measured_repeat_count)
    if repeat_count <= 0:
        raise ValueError("measured_repeat_count must be positive")
    if bool(require_repeat5_material_probe) and repeat_count < 5:
        raise ValueError("repeat5 material-probe config requires measured_repeat_count >= 5")
    if not callable(prepare_session):
        raise TypeError("prepare_session must be callable")
    if finalize_weighted_summary is not None and not callable(finalize_weighted_summary):
        raise TypeError("finalize_weighted_summary must be callable when provided")

    if run_weighted_summary is None:

        def run_weighted_summary(prepared: Any) -> Any:
            if hasattr(prepared, "run_weighted_summary_device_output_stream"):
                return prepared.run_weighted_summary_device_output_stream()
            if hasattr(prepared, "ray_triangle_weighted_summary_device_output_stream"):
                return prepared.ray_triangle_weighted_summary_device_output_stream()
            raise TypeError(
                "prepared ray-triangle weighted summary session must expose a "
                "device-output stream run method"
            )

    task = PreparedExecutionSessionTask(
        workflow_name="ray_triangle_weighted_summary_device_output_stream_prepared_session",
        primitive="ray_triangle_weighted_summary_device_output_stream",
        backend=resolved_backend,
        partner=resolved_partner,
        input_fingerprints={
            "triangles": triangle_fingerprint,
            "ray_batch": ray_batch_fingerprint,
            "ray_weights": weight_fingerprint,
        },
        parameters={
            "output_contract": resolved_output_contract,
            "primitive_count": resolved_primitive_count,
            "ray_count": resolved_ray_count,
            "expected_weighted_hit_sum": expected_sum,
        },
        device=device,
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=warmup_count,
        run_prepared=run_weighted_summary,
        finalize_output=finalize_weighted_summary,
        validate_output=validate_output,
        notes=(
            "generic ray/triangle weighted-summary device-output stream routed "
            "through Phoenix V3 prepared execution/session runner",
        ),
    )
    result = (
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=repeat_count,
            validate_each_repeat=validate_each_repeat,
            retain_repeat_outputs=retain_repeat_outputs,
        )
        if repeat_count != 1 or validate_each_repeat or retain_repeat_outputs
        else run_prepared_execution_session(task)
    )
    metadata = dict(result.metadata)
    output_payload = result.output[-1] if isinstance(result.output, tuple) and result.output else result.output
    output_mapping = dict(output_payload) if isinstance(output_payload, Mapping) else {}
    output_metadata = (
        dict(output_mapping.get("metadata", {}))
        if isinstance(output_mapping.get("metadata"), Mapping)
        else output_mapping
    )
    actual_output_contract = str(output_metadata.get("contract") or "")
    output_contract_matches_requested = actual_output_contract == resolved_output_contract
    actual_output_partner = str(output_metadata.get("partner") or "").strip().lower().replace("-", "_")
    output_partner_matches_requested = actual_output_partner == resolved_partner
    output_primitive_count = output_metadata.get("primitive_count")
    output_ray_count = output_metadata.get("ray_count")
    output_counts_match_requested = bool(
        output_primitive_count is not None
        and output_ray_count is not None
        and int(output_primitive_count) == resolved_primitive_count
        and int(output_ray_count) == resolved_ray_count
    )
    weighted_hit_sum_present = "weighted_hit_sum" in output_metadata
    weighted_hit_sum = (
        int(output_metadata["weighted_hit_sum"])
        if weighted_hit_sum_present
        else None
    )
    weighted_hit_sum_matches_expected = bool(
        expected_sum is None
        or weighted_hit_sum is not None
        and int(weighted_hit_sum) == expected_sum
    )
    device_output_stream_validated = bool(
        output_metadata.get("device_output_stream_validated")
        or output_metadata.get("caller_owned_device_output_scalar")
    )
    prepared_scene_reused = bool(output_metadata.get("prepared_scene_reused"))
    prepared_ray_batch_reused = bool(output_metadata.get("prepared_ray_batch_reused"))
    ray_weights_device_resident = bool(output_metadata.get("ray_weights_device_resident"))
    output_scalar_device_resident = bool(
        output_metadata.get("output_scalar_device_resident_until_finalize")
        or output_metadata.get("caller_owned_device_output_scalar")
    )
    hot_path_host_materialization = bool(
        output_metadata.get(
            "hot_path_host_materialization",
            output_metadata.get("host_scalar_materialized_during_hot_path", True),
        )
    )
    graph_capture_claim_authorized = bool(
        output_metadata.get("m113_graph_capture_claim_authorized", False)
    )
    internal_device_residency = bool(
        prepared_scene_reused
        and prepared_ray_batch_reused
        and ray_weights_device_resident
        and output_scalar_device_resident
        and device_output_stream_validated
        and not hot_path_host_materialization
    )
    material_repeat_met = repeat_count >= 5

    metadata["set_a_probe_candidate"] = True
    metadata["primitive_family"] = "ray_triangle_weighted_summary_device_output_stream"
    metadata["productized_execution_path"] = "prepared_execution_session_runner"
    metadata["row_contract"] = resolved_output_contract
    metadata["continuation_contract"] = resolved_output_contract
    metadata["phoenix_v3_redesign_step"] = "m16_triangle_candidate_local_runner_wiring"
    metadata["runtime_trunk_family"] = "ray_triangle_weighted_summary_device_output_stream"
    metadata["runtime_trunk_probe_candidate"] = True
    metadata["runtime_trunk_executes_end_to_end"] = bool(
        metadata.get("runtime_executed")
        and output_contract_matches_requested
        and output_partner_matches_requested
        and output_counts_match_requested
        and weighted_hit_sum_present
        and weighted_hit_sum_matches_expected
        and internal_device_residency
        and not graph_capture_claim_authorized
    )
    metadata["runtime_trunk_phase_sequence"] = (
        "prepare_reusable_triangle_scene",
        "prepare_reusable_ray_batch_and_weights",
        "execute_weighted_any_hit_summary_to_device_output",
        "finalize_scalar_summary_after_hot_path",
    )
    metadata["primitive_count"] = resolved_primitive_count
    metadata["ray_count"] = resolved_ray_count
    metadata["expected_weighted_hit_sum"] = expected_sum
    metadata["output_weighted_hit_sum"] = weighted_hit_sum
    metadata["weighted_hit_sum_present"] = weighted_hit_sum_present
    metadata["weighted_hit_sum_matches_expected"] = weighted_hit_sum_matches_expected
    metadata["output_contract"] = resolved_output_contract
    metadata["actual_output_contract"] = actual_output_contract or None
    metadata["output_contract_matches_requested"] = output_contract_matches_requested
    metadata["actual_output_partner"] = actual_output_partner or None
    metadata["output_partner_matches_requested"] = output_partner_matches_requested
    metadata["output_counts_match_requested"] = output_counts_match_requested
    metadata["device_output_stream_validated"] = device_output_stream_validated
    metadata["prepared_scene_reused"] = prepared_scene_reused
    metadata["prepared_ray_batch_reused"] = prepared_ray_batch_reused
    metadata["ray_weights_device_resident"] = ray_weights_device_resident
    metadata["output_scalar_device_resident_until_finalize"] = output_scalar_device_resident
    metadata["internal_device_residency_between_rtdl_phases"] = internal_device_residency
    metadata["hot_path_host_materialization"] = hot_path_host_materialization
    metadata["m113_graph_capture_claim_authorized"] = False
    metadata["m113_cuda_graph_capture_validated"] = False
    metadata["m113_graph_capture_still_blocked_for_triangle"] = True
    metadata["material_probe_repeat_requirement"] = 5
    metadata["material_probe_repeat_requirement_met"] = material_repeat_met
    metadata["repeat5_material_probe_candidate"] = bool(
        material_repeat_met and metadata["runtime_trunk_executes_end_to_end"]
    )
    metadata["hot_cold_runner_wall_must_travel_together"] = True
    metadata["same_contract_embree_baseline_required"] = True
    metadata["old_triangle_row_does_not_count_as_current_third_probe"] = True
    metadata["external_device_buffer_interop_authorized"] = False
    metadata["v4_embedding_or_external_zero_copy_authorized"] = False
    metadata["v3_v4_residency_boundary"] = (
        "RTDL-owned device-resident intermediates between RTDL phases are V3; "
        "exposing device buffers to an external host remains V4 and is not authorized here."
    )
    metadata["focused_material_gain_required_before_all_app"] = True
    metadata["full_all_app_rerun_authorized_by_this_packet"] = False
    metadata["rt_core_speedup_claim_authorized"] = False
    metadata["whole_app_speedup_claim_authorized"] = False
    metadata["public_speedup_claim_authorized"] = False
    metadata["broad_v3_faster_than_v2_claim_authorized"] = False
    metadata["true_zero_copy_claim_authorized"] = False
    metadata["automatic_partner_selection_allowed"] = False
    metadata["automatic_partner_selection_authorized"] = False
    metadata["app_specific_native_engine_logic_allowed"] = False
    return PreparedExecutionSessionResult(
        prepared_value=result.prepared_value,
        output=result.output,
        validation_output=result.validation_output,
        metadata=metadata,
    )


def describe_prepared_execution_user_pattern() -> dict[str, Any]:
    return {
        "schema": PREPARED_EXECUTION_REPORT_VERSION,
        "workflow": list(PREPARED_EXECUTION_WORKFLOW),
        "required_phases": list(PREPARED_EXECUTION_REQUIRED_PHASES),
        "required_user_decisions": [
            "backend",
            "partner",
            "cache mode",
            "warmup repeats",
            "measured repeats",
            "steady-state measurement window",
            "validation oracle",
        ],
        "automatic_partner_selection_allowed": False,
        "app_specific_engine_logic_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": PREPARED_EXECUTION_CLAIM_BOUNDARY,
    }


def prepared_execution_report_from_artifact(
    artifact: Mapping[str, Any],
    *,
    workflow_name: str = "prepared_execution",
    backend: str | None = None,
    partner: str | None = None,
    notes: Sequence[str] = (),
) -> PreparedExecutionReport:
    timing = artifact.get("timing_sec", {})
    if not isinstance(timing, Mapping):
        raise ValueError("prepared execution artifact must contain timing_sec mapping")
    executor_metadata = artifact.get("executor_metadata", {})
    if not isinstance(executor_metadata, Mapping):
        executor_metadata = {}
    selected_partner = partner or str(executor_metadata.get("partner") or artifact.get("partner") or "explicit_partner_not_recorded")
    selected_backend = backend or _infer_backend_from_artifact(artifact)

    warmup_seconds = _float_tuple(timing.get("active_relation_device_columns_warmup_secs", ()))
    planner_repeats = _float_tuple(timing.get("device_tile_task_planning_repeat_secs", ()))
    executor_repeats = _float_tuple(timing.get("cupy_tile_task_executor_repeat_secs", ()))
    phases = (
        PreparedExecutionPhaseTiming(
            phase="prepare",
            seconds=_float_value(timing.get("geometry_plus_payload_prepare")),
            role="one_time_prepare_or_rehydrate_payloads",
            source_keys=("timing_sec.geometry_plus_payload_prepare",),
            setup_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="cache_load",
            seconds=_float_value(timing.get("payload_cache_load")),
            role="load_prepared_payload_cache_when_enabled",
            source_keys=("timing_sec.payload_cache_load",),
        ),
        PreparedExecutionPhaseTiming(
            phase="cache_write",
            seconds=_float_value(timing.get("payload_cache_write")),
            role="write_prepared_payload_cache_when_enabled",
            source_keys=("timing_sec.payload_cache_write",),
        ),
        PreparedExecutionPhaseTiming(
            phase="warmup",
            seconds=min(warmup_seconds) if warmup_seconds else 0.0,
            role="warm_prepared_stream_before_steady_state_measurement",
            source_keys=(
                "timing_sec.active_relation_device_columns_warmup_secs",
                "timing_sec.active_relation_device_columns_best_warmup",
            ),
            repeat_seconds=warmup_seconds,
            best_repeat_seconds=_optional_float(timing.get("active_relation_device_columns_best_warmup")),
        ),
        PreparedExecutionPhaseTiming(
            phase="steady_state_stream",
            seconds=_float_value(timing.get("active_relation_device_columns")),
            role="run_prepared_relation_stream_after_warmup",
            source_keys=("timing_sec.active_relation_device_columns",),
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="candidate_filter",
            seconds=_float_value(timing.get("bounds_positive_filter")),
            role="optional_device_candidate_filter",
            source_keys=("timing_sec.bounds_positive_filter",),
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="planner",
            seconds=_best_or_value(timing, "device_tile_task_planning_best_repeat", "device_tile_task_planning"),
            role="plan_continuation_work_from_prepared_columns",
            source_keys=(
                "timing_sec.device_tile_task_planning_best_repeat",
                "timing_sec.device_tile_task_planning",
            ),
            repeat_seconds=planner_repeats,
            best_repeat_seconds=_optional_float(timing.get("device_tile_task_planning_best_repeat")),
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="executor",
            seconds=_best_or_value(timing, "cupy_tile_task_executor_best_repeat", "cupy_tile_task_executor"),
            role="execute_partner_continuation_with_explicit_partner",
            source_keys=(
                "timing_sec.cupy_tile_task_executor_best_repeat",
                "timing_sec.cupy_tile_task_executor",
            ),
            repeat_seconds=executor_repeats,
            best_repeat_seconds=_optional_float(timing.get("cupy_tile_task_executor_best_repeat")),
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="validation",
            seconds=_float_value(timing.get("exact_oracle")),
            role="external_oracle_validation_not_part_of_steady_state_path",
            source_keys=("timing_sec.exact_oracle",),
            validation_candidate=True,
        ),
    )
    report = PreparedExecutionReport(
        workflow_name=workflow_name,
        explicit_backend=selected_backend,
        explicit_partner=selected_partner,
        phases=phases,
        warmup_count=int(artifact.get("relation_column_warmup_repeats") or len(warmup_seconds)),
        claim_boundary=_source_claim_boundary(artifact),
        source_schema=str(artifact.get("schema")) if artifact.get("schema") is not None else None,
        source_goal=int(artifact["goal"]) if artifact.get("goal") is not None else None,
        source_commit=str(artifact.get("rtdl_commit")) if artifact.get("rtdl_commit") is not None else None,
        notes=tuple(str(note) for note in notes),
    )
    return report


def validate_prepared_execution_report(report: PreparedExecutionReport | Mapping[str, Any]) -> dict[str, Any]:
    payload = report.to_dict() if isinstance(report, PreparedExecutionReport) else dict(report)
    errors: list[str] = []
    if payload.get("schema") != PREPARED_EXECUTION_REPORT_VERSION:
        errors.append("prepared execution report schema mismatch")
    if tuple(payload.get("workflow", ())) != PREPARED_EXECUTION_WORKFLOW:
        errors.append("prepared execution workflow mismatch")
    phase_timings = payload.get("phase_timings", ())
    phase_names = tuple(str(phase.get("phase")) for phase in phase_timings if isinstance(phase, Mapping))
    for phase in PREPARED_EXECUTION_REQUIRED_PHASES:
        if phase not in phase_names:
            errors.append(f"missing required prepared execution phase: {phase}")
    if payload.get("explicit_partner_choice_required") is not True:
        errors.append("prepared execution report must require explicit partner choice")
    for field_name in (
        "automatic_partner_selection_allowed",
        "app_specific_engine_logic_allowed",
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if payload.get(field_name) is not False:
            errors.append(f"prepared execution report authorizes {field_name}")
    for key, value in dict(payload.get("claim_boundary") or {}).items():
        if bool(value):
            errors.append(f"source claim boundary authorizes {key}")
    summary = payload.get("summary_sec", {})
    if not isinstance(summary, Mapping):
        errors.append("prepared execution report missing summary_sec")
    else:
        for key in ("setup", "warmup", "steady_state", "validation"):
            if key not in summary:
                errors.append(f"prepared execution summary missing {key}")
            elif float(summary[key]) < 0.0:
                errors.append(f"prepared execution summary has negative {key}")
    return {
        "schema": PREPARED_EXECUTION_REPORT_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "phase_count": len(phase_names),
        "workflow": PREPARED_EXECUTION_WORKFLOW,
        "claim_boundary": PREPARED_EXECUTION_CLAIM_BOUNDARY,
    }


def audit_prepared_execution_session_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(metadata)
    report = payload.get("prepared_execution_report")
    report_validation = payload.get("prepared_execution_report_validation")
    phase_accounting_present = isinstance(report, Mapping)
    validation_present = isinstance(report_validation, Mapping)
    validation_status = (
        str(report_validation.get("status"))
        if validation_present and report_validation.get("status") is not None
        else "missing"
    )
    phase_accounting_accept = (
        phase_accounting_present
        and validation_present
        and validation_status == "accept"
    )
    productized_runner_used = (
        payload.get("productized_execution_path") == "prepared_execution_session_runner"
        or payload.get("schema") == PREPARED_EXECUTION_SESSION_RUNNER_VERSION
    )
    set_a_probe_candidate = payload.get("set_a_probe_candidate") is True
    set_b_control_candidate = payload.get("set_b_control_candidate") is True
    primitive_family = str(payload.get("primitive_family") or "")
    topology_stream_set_a_candidate = (
        set_a_probe_candidate and "topology_stream" in primitive_family
    )
    runtime_executed = payload.get("runtime_executed") is True
    runtime_trunk_reported = "runtime_trunk_executes_end_to_end" in payload
    runtime_trunk_executes = payload.get("runtime_trunk_executes_end_to_end") is True
    residency_reported = "internal_device_residency_between_rtdl_phases" in payload
    internal_residency = payload.get("internal_device_residency_between_rtdl_phases") is True
    host_materialization_reported = "hot_path_host_materialization" in payload
    hot_path_host_materialization = payload.get("hot_path_host_materialization") is True
    measured_repeats_present = "measured_repeat_seconds" in payload
    output_finalize_measured = "output_finalize_sec" in payload
    topology_stream_m3_bridge_contract_ok = (
        payload.get("prepared_execution_to_topology_stream_m3_bridge_contract")
        == "prepared_execution_to_topology_stream_m3_bridge_v1"
    )
    topology_stream_m3_bridge_complete = (
        payload.get("prepared_execution_to_topology_stream_m3_bridge_status")
        == "complete_non_authorizing_m3_bridge"
        and payload.get("topology_stream_m3_phase_table_complete") is True
        and tuple(payload.get("topology_stream_m3_missing_phases_for_public_row") or ())
        == ()
    )
    topology_stream_m3_bridge_non_authorizing = (
        payload.get("topology_stream_m3_bridge_public_row_authorized") is False
        and payload.get("topology_stream_m3_bridge_m7_promotion_authorized") is False
    )
    topology_stream_m3_bridge_ready = (
        not topology_stream_set_a_candidate
        or (
            topology_stream_m3_bridge_contract_ok
            and topology_stream_m3_bridge_complete
            and topology_stream_m3_bridge_non_authorizing
        )
    )
    claim_boundary_fields = (
        "release_authorized",
        "public_speedup_claim_authorized",
        "broad_v3_faster_than_v2_claim_authorized",
        "true_zero_copy_claim_authorized",
        "automatic_partner_selection_authorized",
    )
    claim_boundaries_closed = all(payload.get(field) is False for field in claim_boundary_fields)
    missing_step3_fields: list[str] = []
    if not phase_accounting_accept:
        missing_step3_fields.append("accepted_phase_accounting")
    if not runtime_trunk_reported:
        missing_step3_fields.append("runtime_trunk_executes_end_to_end")
    if not residency_reported:
        missing_step3_fields.append("internal_device_residency_between_rtdl_phases")
    if not host_materialization_reported:
        missing_step3_fields.append("hot_path_host_materialization")
    if not measured_repeats_present:
        missing_step3_fields.append("measured_repeat_seconds")
    if not output_finalize_measured:
        missing_step3_fields.append("output_finalize_sec")
    if not topology_stream_m3_bridge_ready:
        missing_step3_fields.append("complete_non_authorizing_topology_stream_m3_bridge")
    if not claim_boundaries_closed:
        missing_step3_fields.append("closed_claim_boundaries")
    step3_ready = (
        productized_runner_used
        and runtime_executed
        and phase_accounting_accept
        and runtime_trunk_executes
        and internal_residency
        and host_materialization_reported
        and not hot_path_host_materialization
        and measured_repeats_present
        and output_finalize_measured
        and topology_stream_m3_bridge_ready
        and claim_boundaries_closed
    )
    return {
        "schema": PREPARED_EXECUTION_SESSION_AUDIT_VERSION,
        "status": "accept_step3_ready" if step3_ready else "incomplete_step3_audit",
        "productized_execution_path": payload.get("productized_execution_path"),
        "productized_runner_used": productized_runner_used,
        "set_a_probe_candidate": set_a_probe_candidate,
        "set_b_control_candidate": set_b_control_candidate,
        "topology_stream_set_a_candidate": topology_stream_set_a_candidate,
        "topology_stream_m3_bridge_contract_ok": topology_stream_m3_bridge_contract_ok,
        "topology_stream_m3_bridge_complete": topology_stream_m3_bridge_complete,
        "topology_stream_m3_bridge_non_authorizing": topology_stream_m3_bridge_non_authorizing,
        "topology_stream_m3_bridge_ready": topology_stream_m3_bridge_ready,
        "runtime_executed": runtime_executed,
        "phase_accounting_present": phase_accounting_present,
        "phase_accounting_validation_status": validation_status,
        "phase_accounting_accept": phase_accounting_accept,
        "runtime_trunk_executes_end_to_end_reported": runtime_trunk_reported,
        "runtime_trunk_executes_end_to_end": runtime_trunk_executes,
        "internal_device_residency_reported": residency_reported,
        "internal_device_residency_between_rtdl_phases": internal_residency,
        "hot_path_host_materialization_reported": host_materialization_reported,
        "hot_path_host_materialization": hot_path_host_materialization,
        "measured_repeat_seconds_present": measured_repeats_present,
        "output_finalize_sec_present": output_finalize_measured,
        "claim_boundaries_closed": claim_boundaries_closed,
        "missing_step3_fields": tuple(missing_step3_fields),
        "step3_residency_default_ready": step3_ready,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
    }


def audit_prepared_execution_continuation_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(metadata)
    step3_audit = audit_prepared_execution_session_metadata(payload)
    continuation_contract = payload.get("continuation_contract")
    row_contract = payload.get("row_contract")
    primitive_family = payload.get("primitive_family")
    runtime_trunk_family = payload.get("runtime_trunk_family")
    full_all_app_closed = payload.get("full_all_app_rerun_authorized_by_this_packet") is False
    app_logic_closed = payload.get("app_specific_native_engine_logic_allowed") is False
    automatic_partner_closed = payload.get("automatic_partner_selection_authorized") is False
    focused_gate_present = payload.get("focused_material_gain_required_before_all_app") is True

    missing_step4_fields: list[str] = []
    if step3_audit.get("step3_residency_default_ready") is not True:
        missing_step4_fields.append("step3_residency_default_ready")
    if not primitive_family:
        missing_step4_fields.append("primitive_family")
    if not runtime_trunk_family:
        missing_step4_fields.append("runtime_trunk_family")
    if not continuation_contract:
        missing_step4_fields.append("continuation_contract")
    if not row_contract:
        missing_step4_fields.append("row_contract")
    if not focused_gate_present:
        missing_step4_fields.append("focused_material_gain_required_before_all_app")
    if not full_all_app_closed:
        missing_step4_fields.append("full_all_app_rerun_authorized_by_this_packet_false")
    if not app_logic_closed:
        missing_step4_fields.append("app_specific_native_engine_logic_allowed_false")
    if not automatic_partner_closed:
        missing_step4_fields.append("automatic_partner_selection_authorized_false")

    continuation_core_ready = not missing_step4_fields
    return {
        "schema": PREPARED_EXECUTION_CONTINUATION_AUDIT_VERSION,
        "status": (
            "accept_step4_continuation_core_ready"
            if continuation_core_ready
            else "incomplete_step4_continuation_audit"
        ),
        "step3_audit": step3_audit,
        "step3_residency_default_ready": bool(
            step3_audit.get("step3_residency_default_ready")
        ),
        "primitive_family": primitive_family,
        "runtime_trunk_family": runtime_trunk_family,
        "continuation_contract": continuation_contract,
        "row_contract": row_contract,
        "set_a_probe_candidate": payload.get("set_a_probe_candidate") is True,
        "set_b_control_candidate": payload.get("set_b_control_candidate") is True,
        "focused_material_gain_required_before_all_app": focused_gate_present,
        "full_all_app_rerun_authorized_by_this_packet": False,
        "app_specific_native_engine_logic_allowed": False,
        "automatic_partner_selection_authorized": False,
        "missing_step4_fields": tuple(missing_step4_fields),
        "step4_continuation_core_ready": continuation_core_ready,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_rerun_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
    }


def _source_claim_boundary(artifact: Mapping[str, Any]) -> dict[str, bool]:
    boundary = artifact.get("claim_boundary") or {}
    if not isinstance(boundary, Mapping):
        return {}
    return {str(key): bool(value) for key, value in boundary.items()}


def _validation_passed(validation_output: Any) -> bool | None:
    if validation_output is None:
        return None
    if isinstance(validation_output, bool):
        return validation_output
    if isinstance(validation_output, Sequence) and not isinstance(validation_output, (str, bytes, bytearray)):
        repeat_results = [
            result
            for result in (_validation_passed(item) for item in validation_output)
            if result is not None
        ]
        return all(repeat_results) if repeat_results else None
    if isinstance(validation_output, Mapping):
        bool_values = [bool(value) for value in validation_output.values() if isinstance(value, bool)]
        if bool_values:
            return all(bool_values)
    return None


def make_prepared_input_fingerprint(value: Any) -> Any:
    """Return collision-resistant prepared-session input fingerprint metadata."""

    return _stable_input_fingerprint(value)


def _stable_input_fingerprint(value: Any) -> Any:
    if hasattr(value, "count"):
        count = getattr(value, "count")
        if not callable(count):
            return {"kind": type(value).__name__, "count": int(count)}
    if isinstance(value, Mapping):
        return {str(key): _stable_input_fingerprint(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        digest = hashlib.sha256()
        first_repr: str | None = None
        last_repr: str | None = None
        count = 0
        for item in value:
            item_repr = repr(item)
            if first_repr is None:
                first_repr = item_repr[:128]
            last_repr = item_repr[:128]
            encoded = item_repr.encode("utf-8", "backslashreplace")
            digest.update(str(len(encoded)).encode("ascii"))
            digest.update(b":")
            digest.update(encoded)
            digest.update(b";")
            count += 1
        return {
            "kind": type(value).__name__,
            "count": count,
            "digest_algorithm": "sha256",
            "digest": digest.hexdigest(),
            "fingerprint_shape": "sequence_full_repr_stream_hash",
            "repr_sample": {
                "first": first_repr,
                "last": last_repr,
            },
        }
    value_repr = repr(value)
    encoded = value_repr.encode("utf-8", "backslashreplace")
    return {
        "kind": type(value).__name__,
        "digest_algorithm": "sha256",
        "digest": hashlib.sha256(encoded).hexdigest(),
        "fingerprint_shape": "scalar_repr_hash",
        "repr_sample": value_repr[:256],
    }


def _prepared_input_count(value: Any) -> int | None:
    count = getattr(value, "count", None)
    if count is not None and not callable(count):
        return int(count)
    try:
        return len(value)
    except TypeError:
        return None


def _extract_native_prepare_seconds(value: Any) -> tuple[float | None, str | None]:
    for name in (
        "scene_prepare_sec",
        "native_prepare_sec",
        "prepare_sec",
    ):
        candidate = getattr(value, name, None)
        if isinstance(candidate, (int, float)):
            return float(candidate), f"prepared_value.{name}"
    if isinstance(value, Mapping):
        for name in (
            "scene_prepare_sec",
            "native_prepare_sec",
            "prepare_sec",
        ):
            candidate = value.get(name)
            if isinstance(candidate, (int, float)):
                return float(candidate), f"prepared_value_mapping.{name}"
    return None, None


def _get_or_prepare_with_elapsed(
    cache: ExplicitPreparedSessionCache,
    key: Any,
    prepare_session: Callable[[], Any],
    *,
    policy: RtdlPreparedSessionResidencyPolicy,
):
    from .prepared_session_residency import get_or_prepare_explicit_session

    return get_or_prepare_explicit_session(
        cache,
        key,
        prepare_session,
        policy=policy,
    )


def _infer_backend_from_artifact(artifact: Mapping[str, Any]) -> str:
    schema = str(artifact.get("schema") or "")
    if "optix" in schema:
        return "optix"
    if artifact.get("gpu"):
        return "optix"
    return "explicit_backend_not_recorded"


def _float_value(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _float_tuple(value: Any) -> tuple[float, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)):
        return (float(value),)
    try:
        return tuple(float(item) for item in value)
    except TypeError:
        return (float(value),)


def _best_or_value(timing: Mapping[str, Any], best_key: str, fallback_key: str) -> float:
    if timing.get(best_key) is not None:
        return float(timing[best_key])
    return _float_value(timing.get(fallback_key))


__all__ = [
    "PREPARED_EXECUTION_CLAIM_BOUNDARY",
    "PREPARED_EXECUTION_CONTINUATION_AUDIT_VERSION",
    "PREPARED_EXECUTION_REPORT_VERSION",
    "PREPARED_EXECUTION_REQUIRED_PHASES",
    "PREPARED_EXECUTION_SESSION_AUDIT_VERSION",
    "PREPARED_EXECUTION_SESSION_RUNNER_STATUS",
    "PREPARED_EXECUTION_SESSION_RUNNER_VERSION",
    "PREPARED_EXECUTION_WORKFLOW",
    "PreparedExecutionPhaseTiming",
    "PreparedExecutionReport",
    "PreparedExecutionSessionResult",
    "PreparedExecutionSessionTask",
    "audit_prepared_execution_continuation_metadata",
    "audit_prepared_execution_session_metadata",
    "describe_prepared_execution_user_pattern",
    "make_prepared_input_fingerprint",
    "prepared_execution_report_from_artifact",
    "run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session",
    "run_aabb_index_query_2d_count_prepared_session",
    "run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session",
    "run_aabb_index_query_2d_range_intersection_prepared_session",
    "run_fixed_radius_count_threshold_3d_self_query_prepared_session",
    "run_fixed_radius_ranked_summary_3d_prepared_session",
    "run_fixed_radius_threshold_reached_count_2d_prepared_session",
    "run_grouped_vector_sum_2d_prepared_session",
    "run_point_location_topology_stream_prepared_session",
    "run_prepared_execution_session",
    "run_ray_triangle_weighted_summary_device_output_stream_prepared_session",
    "run_radius_graph_component_union_3d_prepared_session",
    "run_radius_graph_component_signature_3d_prepared_session",
    "run_repeated_prepared_execution_session",
    "run_segment_intersection_topology_stream_prepared_session",
    "validate_prepared_execution_report",
]
