from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping
from typing import Sequence


PREPARED_EXECUTION_REPORT_VERSION = "rtdl.v2_8.prepared_execution_report.v1"
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
        payload = asdict(self)
        payload["source_keys"] = list(self.source_keys)
        payload["repeat_seconds"] = list(self.repeat_seconds)
        return payload


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
            "phase_timings": [phase.to_dict() for phase in self.phases],
            "summary_sec": {
                "setup": self.setup_seconds,
                "warmup": self.warmup_seconds,
                "steady_state": self.steady_state_seconds,
                "validation": self.validation_seconds,
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


def _source_claim_boundary(artifact: Mapping[str, Any]) -> dict[str, bool]:
    boundary = artifact.get("claim_boundary") or {}
    if not isinstance(boundary, Mapping):
        return {}
    return {str(key): bool(value) for key, value in boundary.items()}


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
    "PREPARED_EXECUTION_REPORT_VERSION",
    "PREPARED_EXECUTION_REQUIRED_PHASES",
    "PREPARED_EXECUTION_WORKFLOW",
    "PreparedExecutionPhaseTiming",
    "PreparedExecutionReport",
    "describe_prepared_execution_user_pattern",
    "prepared_execution_report_from_artifact",
    "validate_prepared_execution_report",
]
