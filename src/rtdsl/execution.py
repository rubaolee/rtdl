from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping

from .api import compile_kernel
from .ir import CompiledKernel


_SUPPORTED_BACKENDS = (
    "auto",
    "cpu_python_reference",
    "cpu",
    "embree",
    "optix",
    "vulkan",
    "hiprt",
    "apple_rt",
)


@dataclass(frozen=True)
class ExecutionPolicy:
    """Explicit execution request for the contract-first RTDL runner."""

    backend: str = "cpu_python_reference"
    partner: str | None = None
    allow_fallback: bool = False
    require_rt_core: bool = False
    explain: bool = True
    result_mode: str = "dict"

    def __post_init__(self) -> None:
        if self.backend not in _SUPPORTED_BACKENDS:
            raise ValueError(
                "backend must be one of: " + ", ".join(_SUPPORTED_BACKENDS)
            )
        if self.partner is not None and self.partner not in {"numpy", "cupy", "torch"}:
            raise ValueError("partner must be one of: numpy, cupy, torch")
        if self.require_rt_core and self.backend not in {"auto", "optix"}:
            raise ValueError("require_rt_core is only supported with backend='auto' or backend='optix'")


@dataclass(frozen=True)
class ExecutionReport:
    """Reproducible explanation of one RTDL execution decision."""

    requested_backend: str
    selected_backend: str
    requested_partner: str | None
    selected_partner: str | None
    fallback_backend: str | None
    fallback_reason: str | None
    primitive_family: str
    predicate: str | None
    output_schema: tuple[str, ...]
    exact_mode: str
    memory_status: str
    copy_status: str
    rt_core_status: str
    cuda_core_partner_status: str
    cpu_status: str
    claim_boundary: Mapping[str, bool]
    reproducibility: Mapping[str, str]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["output_schema"] = list(self.output_schema)
        payload["notes"] = list(self.notes)
        payload["claim_boundary"] = dict(self.claim_boundary)
        payload["reproducibility"] = dict(self.reproducibility)
        return payload


@dataclass(frozen=True)
class ExecutionResult:
    """Rows plus the report that explains how they were produced."""

    rows: tuple[dict[str, object], ...]
    execution_report: ExecutionReport

    def to_dict(self) -> dict[str, object]:
        return {
            "rows": list(self.rows),
            "execution_report": self.execution_report.to_dict(),
        }


def run(
    kernel_fn_or_compiled,
    inputs: Mapping[str, object] | None = None,
    *,
    execution: ExecutionPolicy | None = None,
    **input_kwargs,
) -> ExecutionResult:
    """Run a kernel through an explicit, explainable execution policy.

    This is a contract-first facade over the existing backend-specific runners.
    It intentionally returns an execution report instead of silently hiding
    backend, partner, fallback, and claim-boundary decisions.
    """

    policy = execution or ExecutionPolicy()
    merged_inputs = dict(inputs or {})
    merged_inputs.update(input_kwargs)
    compiled = _resolve_kernel_for_report(kernel_fn_or_compiled)
    selected_backend = _select_backend(policy)
    fallback_backend = None
    fallback_reason = None
    notes: list[str] = []

    try:
        rows = _run_selected_backend(
            selected_backend,
            kernel_fn_or_compiled,
            policy=policy,
            inputs=merged_inputs,
        )
    except Exception as exc:
        if not policy.allow_fallback or selected_backend == "cpu_python_reference":
            raise
        fallback_backend = "cpu_python_reference"
        fallback_reason = f"{selected_backend} failed: {type(exc).__name__}: {exc}"
        notes.append("Execution used the portable CPU Python reference fallback.")
        rows = _run_selected_backend(
            fallback_backend,
            kernel_fn_or_compiled,
            policy=policy,
            inputs=merged_inputs,
        )

    report_backend = fallback_backend or selected_backend
    report = _build_report(
        policy=policy,
        compiled=compiled,
        selected_backend=selected_backend,
        report_backend=report_backend,
        fallback_backend=fallback_backend,
        fallback_reason=fallback_reason,
        notes=tuple(notes),
    )
    return ExecutionResult(rows=tuple(rows), execution_report=report)


def _resolve_kernel_for_report(kernel_fn_or_compiled) -> CompiledKernel | None:
    try:
        if isinstance(kernel_fn_or_compiled, CompiledKernel):
            return kernel_fn_or_compiled
        return compile_kernel(kernel_fn_or_compiled)
    except Exception:
        return None


def _select_backend(policy: ExecutionPolicy) -> str:
    if policy.backend == "auto":
        if policy.require_rt_core:
            return "optix"
        return "cpu_python_reference"
    return policy.backend


def _run_selected_backend(
    backend: str,
    kernel_fn_or_compiled,
    *,
    policy: ExecutionPolicy,
    inputs: Mapping[str, object],
):
    if backend == "cpu_python_reference":
        from .runtime import run_cpu_python_reference

        return run_cpu_python_reference(kernel_fn_or_compiled, **dict(inputs))
    if backend == "cpu":
        from .runtime import run_cpu

        return run_cpu(kernel_fn_or_compiled, **dict(inputs))
    if backend == "embree":
        from .embree_runtime import run_embree

        return run_embree(kernel_fn_or_compiled, result_mode=policy.result_mode, **dict(inputs))
    if backend == "optix":
        from .optix_runtime import run_optix

        return run_optix(kernel_fn_or_compiled, result_mode=policy.result_mode, **dict(inputs))
    if backend == "vulkan":
        from .vulkan_runtime import run_vulkan

        return run_vulkan(kernel_fn_or_compiled, result_mode=policy.result_mode, **dict(inputs))
    if backend == "hiprt":
        from .hiprt_runtime import run_hiprt

        return run_hiprt(kernel_fn_or_compiled, result_mode=policy.result_mode, **dict(inputs))
    if backend == "apple_rt":
        from .apple_rt_runtime import run_apple_rt

        return run_apple_rt(kernel_fn_or_compiled, result_mode=policy.result_mode, **dict(inputs))
    raise ValueError(f"unsupported backend: {backend}")


def _build_report(
    *,
    policy: ExecutionPolicy,
    compiled: CompiledKernel | None,
    selected_backend: str,
    report_backend: str,
    fallback_backend: str | None,
    fallback_reason: str | None,
    notes: tuple[str, ...],
) -> ExecutionReport:
    predicate = None
    output_schema: tuple[str, ...] = ()
    exact_mode = "unknown"
    primitive_family = "unknown"
    if compiled is not None and compiled.refine_op is not None:
        predicate = compiled.refine_op.predicate.name
        primitive_family = _primitive_family(predicate, compiled.candidates.mode if compiled.candidates else None)
        exact_mode = _exact_mode(compiled.refine_op.predicate.options)
    if compiled is not None and compiled.emit_op is not None:
        output_schema = tuple(compiled.emit_op.fields)

    rt_core_status = "not_used"
    if report_backend == "optix":
        rt_core_status = "optix_selected_requires_hardware_evidence"
    if policy.require_rt_core and report_backend != "optix":
        rt_core_status = "required_but_fell_back"

    selected_partner = policy.partner
    cuda_core_partner_status = "not_requested"
    if selected_partner in {"cupy", "torch"}:
        cuda_core_partner_status = f"{selected_partner}_requested_not_proven_by_runner"
    elif selected_partner == "numpy":
        cuda_core_partner_status = "numpy_cpu_partner_requested"

    cpu_status = "selected" if report_backend in {"cpu", "cpu_python_reference", "embree"} else "not_selected"
    claim_boundary = {
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "zero_copy_claim_authorized": False,
        "fallback_used": fallback_backend is not None,
    }
    return ExecutionReport(
        requested_backend=policy.backend,
        selected_backend=report_backend,
        requested_partner=policy.partner,
        selected_partner=selected_partner,
        fallback_backend=fallback_backend,
        fallback_reason=fallback_reason,
        primitive_family=primitive_family,
        predicate=predicate,
        output_schema=output_schema,
        exact_mode=exact_mode,
        memory_status="not_reported_by_runtime",
        copy_status="not_reported_by_runtime",
        rt_core_status=rt_core_status,
        cuda_core_partner_status=cuda_core_partner_status,
        cpu_status=cpu_status,
        claim_boundary=claim_boundary,
        reproducibility=_reproducibility_summary(),
        notes=notes,
    )


def _primitive_family(predicate: str, mode: str | None) -> str:
    if mode in {"graph_expand", "graph_intersect"}:
        return "graph_traversal"
    if mode in {"db_scan", "db_group"}:
        return "columnar_payload"
    if predicate in {"ray_triangle_any_hit", "ray_triangle_hit_count", "ray_triangle_closest_hit"}:
        return "traversal"
    if predicate in {"fixed_radius_neighbors", "knn_rows", "bounded_knn_rows", "point_nearest_segment"}:
        return "nearest_neighbor"
    if predicate in {"conjunctive_scan", "grouped_count", "grouped_sum"}:
        return "columnar_payload"
    if predicate in {"segment_intersection", "point_in_polygon", "overlay_compose", "segment_polygon_hitcount", "segment_polygon_anyhit_rows", "polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
        return "spatial_relation"
    return "generic_refine"


def _exact_mode(options: Mapping[str, object]) -> str:
    if "exact" in options:
        return "exact" if bool(options["exact"]) else "float_approx"
    return "contract_defined"


def _reproducibility_summary() -> dict[str, str]:
    commit = "unknown"
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        pass
    return {
        "git_commit": commit,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY", ""),
        "RTDL_EMBREE_THREADS": os.environ.get("RTDL_EMBREE_THREADS", ""),
    }


__all__ = [
    "ExecutionPolicy",
    "ExecutionReport",
    "ExecutionResult",
    "run",
]
