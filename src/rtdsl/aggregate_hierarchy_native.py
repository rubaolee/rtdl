from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

from .aggregate_hierarchy import (
    AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
    AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS,
    AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
    AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS,
    AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
    AggregateFrontierReduceSpec3D,
    ContinuationPayloadOpening,
    aggregate_frontier_reduce_execution_contract_3d,
    aggregate_frontier_reduce_numba_3d,
    aggregate_frontier_reduce_numba_available,
    aggregate_frontier_reduce_reference_3d,
)


AGGREGATE_HIERARCHY_NATIVE_LOWERING_CONTRACT = (
    "rtdl.compiler.aggregate_hierarchy_native_lowering.private_candidate.v1"
)
AGGREGATE_HIERARCHY_NATIVE_TEMPLATE = (
    "precompiled_cuda_aggregate_hierarchy_continuation_reduce_3d"
)
AGGREGATE_HIERARCHY_OPTIX_TEMPLATE = (
    "true_optix_aggregate_hierarchy_continuation_reduce_3d"
)
AGGREGATE_HIERARCHY_NUMBA_FALLBACK_TEMPLATE = (
    "numba_cpu_aggregate_hierarchy_reduce_3d"
)
AGGREGATE_HIERARCHY_REFERENCE_FALLBACK_TEMPLATE = (
    "reference_cpu_aggregate_hierarchy_reduce_3d"
)
AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS = (
    "rtdl_cuda_prepare_aggregate_hierarchy_continuation_3d",
    "rtdl_cuda_execute_prepared_aggregate_hierarchy_continuation_3d",
    "rtdl_cuda_close_prepared_aggregate_hierarchy_continuation_3d",
)
AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS = (
    "rtdl_optix_prepare_aggregate_hierarchy_continuation_3d",
    "rtdl_optix_execute_prepared_aggregate_hierarchy_continuation_3d",
    "rtdl_optix_close_prepared_aggregate_hierarchy_continuation_3d",
)
AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS = (
    AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM,
)

_DOUBLE_PTR = ctypes.POINTER(ctypes.c_double)
_I64_PTR = ctypes.POINTER(ctypes.c_int64)


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_native_symbol(library: Any, name: str) -> Any:
    try:
        return getattr(library, name)
    except AttributeError as exc:
        raise RuntimeError(
            f"native aggregate-hierarchy lowering requires symbol {name!r}; "
            "rebuild librtdl_optix from the current source tree"
        ) from exc


def _register_native_aggregate_hierarchy_candidate_abi(
    library: Any,
    required_symbols: tuple[str, str, str],
) -> None:
    prepare = _require_native_symbol(library, required_symbols[0])
    prepare.argtypes = [
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        ctypes.c_uint64,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        _DOUBLE_PTR,
        ctypes.c_uint64,
        _I64_PTR,
        _I64_PTR,
        ctypes.c_uint64,
        _I64_PTR,
        _I64_PTR,
        ctypes.c_uint64,
        _I64_PTR,
        _I64_PTR,
        ctypes.c_int64,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_char_p,
        ctypes.c_uint64,
    ]
    prepare.restype = ctypes.c_int

    execute = _require_native_symbol(library, required_symbols[1])
    execute.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_uint64,
        _DOUBLE_PTR,
        _I64_PTR,
        _I64_PTR,
        _I64_PTR,
        _I64_PTR,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_char_p,
        ctypes.c_uint64,
    ]
    execute.restype = ctypes.c_int

    close = _require_native_symbol(library, required_symbols[2])
    close.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint64]
    close.restype = ctypes.c_int


def _raise_native_error(status: int, error: ctypes.Array[ctypes.c_char]) -> None:
    if int(status) == 0:
        return
    message = bytes(error.value).decode("utf-8", errors="replace")
    raise RuntimeError(message or f"native aggregate-hierarchy call failed with status {status}")


def _native_library_and_capability(
    required_symbols: tuple[str, str, str] = AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS,
) -> tuple[Any | None, dict[str, Any]]:
    started = time.perf_counter()
    try:
        from .optix_runtime import _load_optix_library

        library = _load_optix_library()
        _register_native_aggregate_hierarchy_candidate_abi(
            library, required_symbols
        )
        library_path = Path(str(library._rtdl_library_path)).resolve()
        identity = {
            "path": str(library_path),
            "sha256": _sha256_path(library_path),
        }
        return library, {
            "available": True,
            "reason": "all_required_precompiled_symbols_present",
            "required_symbols": required_symbols,
            "library_identity": identity,
            "probe_seconds": time.perf_counter() - started,
        }
    except (FileNotFoundError, OSError, RuntimeError, AttributeError) as exc:
        return None, {
            "available": False,
            "reason": f"{type(exc).__name__}: {exc}",
            "required_symbols": required_symbols,
            "library_identity": None,
            "probe_seconds": time.perf_counter() - started,
        }


def _root_nodes(spec: AggregateFrontierReduceSpec3D) -> tuple[int, ...]:
    hierarchy = spec.prepared_hierarchy.hierarchy
    child_nodes = set(hierarchy.child_indices)
    return tuple(
        node_index
        for node_index in range(hierarchy.node_count)
        if node_index not in child_nodes
    )


@dataclass(frozen=True)
class AggregateHierarchyCompilerPlan3D:
    spec: AggregateFrontierReduceSpec3D
    selected_template: str
    selected_backend: str
    max_output_rows: int
    capability: dict[str, Any]
    fallback_reason: str | None
    planning_seconds: float
    selection_owner: str = "compiler"
    production_default_plan: dict[str, Any] | None = None
    production_default_binding: dict[str, Any] | None = None
    canonical_resolution: dict[str, Any] | None = None
    canonical_production_authority: dict[str, Any] | None = None
    _native_library: Any | None = field(default=None, repr=False, compare=False)

    def to_metadata(self) -> dict[str, Any]:
        application_selected_backend = self.selection_owner == "application"
        return {
            "contract": AGGREGATE_HIERARCHY_NATIVE_LOWERING_CONTRACT,
            "selected_template": self.selected_template,
            "selected_backend": self.selected_backend,
            "max_output_rows": self.max_output_rows,
            "capability": self.capability,
            "fallback_reason": self.fallback_reason,
            "planning_seconds": self.planning_seconds,
            "selection_owner": self.selection_owner,
            "production_default_plan": self.production_default_plan,
            "production_default_binding": self.production_default_binding,
            "canonical_resolution": self.canonical_resolution,
            "canonical_production_authority": self.canonical_production_authority,
            "application_selected_backend": application_selected_backend,
            "app_identity_used_for_selection": False,
            "fixed_speed_target_used_for_selection": False,
            "complete_output_required": True,
            "spec": self.spec.to_metadata(),
        }


def _explicit_native_plan_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    backend: str,
    max_output_rows: int | None,
) -> AggregateHierarchyCompilerPlan3D:
    """Bind one native executor under the legacy explicit-backend model.

    This is deliberately not a compiler entrypoint.  It exists so a V2-style
    application can select a reviewed generic physical executor directly while
    sharing the exact native implementation used by compiler-selected routes.
    """

    if not isinstance(spec, AggregateFrontierReduceSpec3D):
        raise ValueError("spec must be an AggregateFrontierReduceSpec3D")
    candidates = {
        "cuda": (
            AGGREGATE_HIERARCHY_NATIVE_TEMPLATE,
            AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS,
        ),
        "optix_traversal": (
            AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
            AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS,
        ),
    }
    if backend not in candidates:
        raise ValueError("backend must be 'cuda' or 'optix_traversal'")
    roots = _root_nodes(spec)
    if (
        not isinstance(spec.opening, ContinuationPayloadOpening)
        or len(roots) != 1
        or spec.reducer not in AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS
    ):
        raise RuntimeError(
            "explicit native aggregate-hierarchy backend is not legal for the verified spec"
        )
    point_count = spec.prepared_hierarchy.hierarchy.point_count
    capacity = point_count if max_output_rows is None else int(max_output_rows)
    if capacity < point_count:
        raise ValueError("max_output_rows would truncate complete aggregate output")
    selected_template, required_symbols = candidates[backend]
    library, capability = _native_library_and_capability(required_symbols)
    if library is None:
        raise RuntimeError(
            "explicit native aggregate-hierarchy backend is unavailable: "
            f"{capability['reason']}"
        )
    return AggregateHierarchyCompilerPlan3D(
        spec=spec,
        selected_template=selected_template,
        selected_backend=backend,
        max_output_rows=capacity,
        capability=dict(capability),
        fallback_reason=None,
        planning_seconds=0.0,
        selection_owner="application",
        _native_library=library,
    )


def prepare_aggregate_frontier_reduce_explicit_native_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    backend: str,
    max_output_rows: int | None = None,
) -> PreparedNativeAggregateHierarchy3D:
    """Prepare a generic native executor selected explicitly by a V2 app."""

    return PreparedNativeAggregateHierarchy3D(
        _explicit_native_plan_3d(
            spec,
            backend=backend,
            max_output_rows=max_output_rows,
        )
    )


def compile_aggregate_frontier_reduce_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    max_output_rows: int | None = None,
) -> AggregateHierarchyCompilerPlan3D:
    """Select a legal generic executor outside the mandatory NVIDIA profile.

    This remains the portable compiler surface.  It can select CUDA, Numba, or
    the reference implementation, and therefore cannot establish an RT claim.
    NVIDIA-RT production applications use the separate mandatory DEFAULT
    front door below.
    """

    planning_started = time.perf_counter()
    if not isinstance(spec, AggregateFrontierReduceSpec3D):
        raise ValueError("spec must be an AggregateFrontierReduceSpec3D")
    point_count = spec.prepared_hierarchy.hierarchy.point_count
    capacity = point_count if max_output_rows is None else int(max_output_rows)
    if capacity < point_count:
        raise ValueError("max_output_rows would truncate complete aggregate output")
    roots = _root_nodes(spec)
    native_semantics_legal = (
        isinstance(spec.opening, ContinuationPayloadOpening)
        and len(roots) == 1
        and spec.reducer in AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS
    )
    library: Any | None = None
    if native_semantics_legal:
        library, capability = _native_library_and_capability()
    else:
        capability = {
            "available": False,
            "reason": "native_template_semantics_not_legal_for_verified_spec",
            "required_symbols": AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS,
            "library_identity": None,
            "probe_seconds": 0.0,
        }
    if native_semantics_legal and library is not None:
        selected_template = AGGREGATE_HIERARCHY_NATIVE_TEMPLATE
        selected_backend = "cuda"
        fallback_reason = None
    elif (
        spec.reducer in AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS
        and aggregate_frontier_reduce_numba_available()
    ):
        selected_template = AGGREGATE_HIERARCHY_NUMBA_FALLBACK_TEMPLATE
        selected_backend = "numba"
        fallback_reason = str(capability["reason"])
    elif spec.reducer in AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS:
        selected_template = AGGREGATE_HIERARCHY_REFERENCE_FALLBACK_TEMPLATE
        selected_backend = "reference"
        fallback_reason = str(capability["reason"])
    else:
        raise RuntimeError("no legal aggregate-hierarchy executor supports the verified spec")
    return AggregateHierarchyCompilerPlan3D(
        spec=spec,
        selected_template=selected_template,
        selected_backend=selected_backend,
        max_output_rows=capacity,
        capability=capability,
        fallback_reason=fallback_reason,
        planning_seconds=time.perf_counter() - planning_started,
        selection_owner="compiler_portable_unprofiled",
        _native_library=library,
    )


def compile_aggregate_frontier_reduce_default_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    max_output_rows: int | None = None,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> AggregateHierarchyCompilerPlan3D:
    """Select through the mandatory NVIDIA-RT production DEFAULT.

    No candidate/backend/template argument exists.  Failure to prove and bind
    the registered true-OptiX route is a hard failure, not a CPU/CUDA fallback.
    """

    planning_started = time.perf_counter()
    if not isinstance(spec, AggregateFrontierReduceSpec3D):
        raise ValueError("spec must be an AggregateFrontierReduceSpec3D")
    point_count = spec.prepared_hierarchy.hierarchy.point_count
    capacity = point_count if max_output_rows is None else int(max_output_rows)
    if capacity < point_count:
        raise ValueError("max_output_rows would truncate complete aggregate output")

    roots = _root_nodes(spec)
    native_semantics_legal = (
        isinstance(spec.opening, ContinuationPayloadOpening)
        and len(roots) == 1
        and spec.reducer in AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS
    )
    if not native_semantics_legal:
        raise RuntimeError(
            "production DEFAULT requires the verified aggregate-hierarchy "
            "OptiX semantic shape"
        )
    library, capability = _native_library_and_capability(
        AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS
    )
    if library is None:
        raise RuntimeError(
            "production DEFAULT requires the registered true-OptiX aggregate "
            f"candidate: {capability['reason']}"
        )

    from .production_default_integration import (
        ProductionDefaultIntegrationError,
        bind_default_plan_to_lowering,
        compile_production_default_plan,
        make_production_action_descriptor,
        make_production_target_descriptor,
        probe_device_memory_limit_bytes,
    )

    hierarchy = spec.prepared_hierarchy.hierarchy
    float_columns = (
        hierarchy.point_x,
        hierarchy.point_y,
        hierarchy.point_z,
        hierarchy.point_weight,
        hierarchy.node_cx,
        hierarchy.node_cy,
        hierarchy.node_cz,
        hierarchy.node_half_size,
        hierarchy.node_weight,
    )
    int_columns = (
        hierarchy.member_offsets,
        hierarchy.member_indices,
        hierarchy.child_offsets,
        hierarchy.child_indices,
        hierarchy.node_next_index or (),
        hierarchy.node_resume_index or (),
        hierarchy.node_rope_index or (),
        hierarchy.source_leaf_node_index or (),
        hierarchy.node_subtree_end_index or (),
    )
    prepared_bytes = 8 * sum(len(column) for column in (*float_columns, *int_columns))
    memory_limit = probe_device_memory_limit_bytes()
    if memory_limit is None:
        raise RuntimeError(
            "production DEFAULT could not establish the actual device-memory limit"
        )
    spec_metadata = spec.to_metadata()
    semantic_digest = hashlib.sha256(
        json.dumps(
            spec_metadata,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()
    try:
        action_descriptor = make_production_action_descriptor(
            semantic_kind="aggregate_hierarchy_continuation_reduce_3d",
            action_contract_class="frontier_reduce",
            action_semantic_digest=semantic_digest,
            output_contract={
                "schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
                "reducer": spec.reducer,
                "max_output_rows": capacity,
                "complete_output_required": True,
            },
            work_domain={
                "point_count": hierarchy.point_count,
                "node_count": hierarchy.node_count,
                "root_nodes": list(roots),
                "opening": spec.opening.to_metadata(),
            },
            input_bytes=prepared_bytes,
            output_bytes=capacity * 64,
            prepared_bytes=prepared_bytes,
            logical_cardinality_bound=max(
                hierarchy.point_count, hierarchy.node_count
            ),
            pair_cardinality_bound=0,
            logical_item_bytes_bound=64,
            pair_item_bytes_bound=0,
        )
        target_descriptor = make_production_target_descriptor(
            target_identity={
                "kind": "runtime_probed_nvidia_aggregate_hierarchy_target",
                "provider_library": capability["library_identity"],
                "mandatory_nvidia_rt": True,
            },
            available_providers=("optix",),
            memory_limit_bytes=memory_limit,
            mandatory_nvidia_rt=True,
        )
        if (semantic_statement_stable_id is None) != (
            backend_contract_id is None
        ):
            raise ValueError(
                "canonical semantic statement and backend contract are required together"
            )
        canonical_resolution = None
        canonical_authority = None
        if semantic_statement_stable_id is not None:
            from .canonical_physical_resolution import (
                CanonicalPhysicalResolutionError,
                registered_backend_contract,
                registered_semantic_statement,
                resolve_canonical_provider,
            )

            statement = registered_semantic_statement(
                semantic_statement_stable_id
            )
            backend_contract = registered_backend_contract(backend_contract_id)
            canonical_resolution = resolve_canonical_provider(
                statement_stable_id=statement.stable_id,
                expected_statement_sha256=statement.digest,
                backend_contract_id=backend_contract.stable_id,
                expected_backend_contract_sha256=backend_contract.digest,
                action=action_descriptor,
                target=target_descriptor,
            )
            if canonical_resolution.get("status") != "RESOLVED":
                raise CanonicalPhysicalResolutionError(
                    str(canonical_resolution.get("error_code", "FAIL_CLOSED")),
                    str(canonical_resolution.get("error_detail", "")),
                )
        production_default_plan = compile_production_default_plan(
            action_descriptor,
            target_descriptor,
            mandatory_nvidia_rt=True,
            repository_root=Path(__file__).resolve().parents[2],
        )
        production_default_binding = bind_default_plan_to_lowering(
            production_default_plan,
            actual_backend="optix_traversal",
            actual_template=AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
            repository_root=Path(__file__).resolve().parents[2],
        )
        if canonical_resolution is not None:
            from .canonical_physical_resolution import (
                bind_canonical_provider_to_materialized_plan,
            )

            canonical_authority = bind_canonical_provider_to_materialized_plan(
                canonical_resolution,
                materialized_provider_stable_id=str(
                    production_default_plan["selected_candidate_stable_id"]
                ),
                materialized_plan_sha256=str(
                    production_default_plan["production_plan_sha256"]
                ),
                materialized_binding_sha256=str(
                    production_default_binding["binding_sha256"]
                ),
            )
    except ProductionDefaultIntegrationError as exc:
        raise RuntimeError(f"production DEFAULT failed closed: {exc}") from exc

    selected_template = AGGREGATE_HIERARCHY_OPTIX_TEMPLATE
    selected_backend = "optix_traversal"
    fallback_reason = None

    return AggregateHierarchyCompilerPlan3D(
        spec=spec,
        selected_template=selected_template,
        selected_backend=selected_backend,
        max_output_rows=capacity,
        capability=capability,
        fallback_reason=fallback_reason,
        planning_seconds=time.perf_counter() - planning_started,
        selection_owner="compiler_default",
        production_default_plan=production_default_plan,
        production_default_binding=production_default_binding,
        canonical_resolution=canonical_resolution,
        canonical_production_authority=canonical_authority,
        _native_library=library,
    )


def compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    physical_candidate: str,
    max_output_rows: int | None = None,
) -> AggregateHierarchyCompilerPlan3D:
    """Materialize one compiler-registered physical candidate for validation.

    This compiler/review front door cannot add a candidate, change the verified
    semantics, or establish normal placement priority.  Production compilation
    continues to select the pre-existing CUDA route until modern-RTX evidence
    and a separate placement review exist.
    """

    planning_started = time.perf_counter()
    if not isinstance(spec, AggregateFrontierReduceSpec3D):
        raise ValueError("spec must be an AggregateFrontierReduceSpec3D")
    candidates = {
        "cuda": (
            AGGREGATE_HIERARCHY_NATIVE_TEMPLATE,
            AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS,
        ),
        "optix_traversal": (
            AGGREGATE_HIERARCHY_OPTIX_TEMPLATE,
            AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS,
        ),
    }
    if physical_candidate not in candidates:
        raise ValueError(
            "physical_candidate must name a compiler-registered aggregate "
            "hierarchy candidate"
        )
    roots = _root_nodes(spec)
    if (
        not isinstance(spec.opening, ContinuationPayloadOpening)
        or len(roots) != 1
        or spec.reducer not in AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS
    ):
        raise RuntimeError(
            "physical aggregate-hierarchy candidate is not legal for the verified spec"
        )
    point_count = spec.prepared_hierarchy.hierarchy.point_count
    capacity = point_count if max_output_rows is None else int(max_output_rows)
    if capacity < point_count:
        raise ValueError("max_output_rows would truncate complete aggregate output")

    selected_template, required_symbols = candidates[physical_candidate]
    library, capability = _native_library_and_capability(required_symbols)
    if library is None:
        raise RuntimeError(
            "compiler-registered aggregate-hierarchy candidate is unavailable: "
            f"{capability['reason']}"
        )
    capability = dict(capability)
    capability.update(
        {
            "functional_validation_only": True,
            "candidate_pre_registered_by_compiler": True,
            "candidate_changes_semantics": False,
            "candidate_establishes_production_priority": False,
        }
    )
    return AggregateHierarchyCompilerPlan3D(
        spec=spec,
        selected_template=selected_template,
        selected_backend=physical_candidate,
        max_output_rows=capacity,
        capability=capability,
        fallback_reason=None,
        planning_seconds=time.perf_counter() - planning_started,
        _native_library=library,
    )


class PreparedNativeAggregateHierarchy3D:
    """Closed owner for compiler-selected resident aggregate hierarchy columns."""

    def __init__(self, plan: AggregateHierarchyCompilerPlan3D) -> None:
        if not isinstance(plan, AggregateHierarchyCompilerPlan3D):
            raise ValueError("plan must be an AggregateHierarchyCompilerPlan3D")
        candidate_symbols = {
            AGGREGATE_HIERARCHY_NATIVE_TEMPLATE:
                AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS,
            AGGREGATE_HIERARCHY_OPTIX_TEMPLATE:
                AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS,
        }
        if plan.selected_template not in candidate_symbols:
            raise ValueError(
                "native preparation requires a compiler-selected native template"
            )
        if plan._native_library is None:
            raise RuntimeError("compiler plan has no bound native library")

        import numpy as np

        self._plan = plan
        self._library = plan._native_library
        self._candidate_symbols = candidate_symbols[plan.selected_template]
        self._handle = ctypes.c_void_p()
        self._closed = False
        hierarchy = plan.spec.prepared_hierarchy.hierarchy
        roots = _root_nodes(plan.spec)
        if len(roots) != 1:
            raise ValueError("native continuation lowering requires one root node")
        if hierarchy.node_next_index is None or hierarchy.node_rope_index is None:
            raise ValueError(
                "native continuation lowering requires node_next_index and node_rope_index"
            )

        def f64(values: Any) -> Any:
            return np.ascontiguousarray(values, dtype=np.float64)

        def i64(values: Any) -> Any:
            return np.ascontiguousarray(values, dtype=np.int64)

        arrays = {
            "point_x": f64(hierarchy.point_x),
            "point_y": f64(hierarchy.point_y),
            "point_z": f64(hierarchy.point_z),
            "point_weight": f64(hierarchy.point_weight),
            "node_cx": f64(hierarchy.node_cx),
            "node_cy": f64(hierarchy.node_cy),
            "node_cz": f64(hierarchy.node_cz),
            "node_half_size": f64(hierarchy.node_half_size),
            "node_weight": f64(hierarchy.node_weight),
            "member_offsets": i64(hierarchy.member_offsets),
            "member_indices": i64(hierarchy.member_indices),
            "child_offsets": i64(hierarchy.child_offsets),
            "child_indices": i64(hierarchy.child_indices),
            "node_next_index": i64(hierarchy.node_next_index),
            "node_rope_index": i64(hierarchy.node_rope_index),
        }
        error = ctypes.create_string_buffer(4096)
        prepare_seconds = ctypes.c_double()
        prepare = _require_native_symbol(
            self._library, self._candidate_symbols[0]
        )
        status = prepare(
            arrays["point_x"].ctypes.data_as(_DOUBLE_PTR),
            arrays["point_y"].ctypes.data_as(_DOUBLE_PTR),
            arrays["point_z"].ctypes.data_as(_DOUBLE_PTR),
            arrays["point_weight"].ctypes.data_as(_DOUBLE_PTR),
            ctypes.c_uint64(hierarchy.point_count),
            arrays["node_cx"].ctypes.data_as(_DOUBLE_PTR),
            arrays["node_cy"].ctypes.data_as(_DOUBLE_PTR),
            arrays["node_cz"].ctypes.data_as(_DOUBLE_PTR),
            arrays["node_half_size"].ctypes.data_as(_DOUBLE_PTR),
            arrays["node_weight"].ctypes.data_as(_DOUBLE_PTR),
            ctypes.c_uint64(hierarchy.node_count),
            arrays["member_offsets"].ctypes.data_as(_I64_PTR),
            arrays["member_indices"].ctypes.data_as(_I64_PTR),
            ctypes.c_uint64(len(hierarchy.member_indices)),
            arrays["child_offsets"].ctypes.data_as(_I64_PTR),
            arrays["child_indices"].ctypes.data_as(_I64_PTR),
            ctypes.c_uint64(len(hierarchy.child_indices)),
            arrays["node_next_index"].ctypes.data_as(_I64_PTR),
            arrays["node_rope_index"].ctypes.data_as(_I64_PTR),
            ctypes.c_int64(roots[0]),
            ctypes.byref(self._handle),
            ctypes.byref(prepare_seconds),
            error,
            ctypes.c_uint64(len(error)),
        )
        _raise_native_error(status, error)
        if not self._handle.value:
            raise RuntimeError("native aggregate-hierarchy prepare returned a null handle")
        self.prepare_seconds = float(prepare_seconds.value)

    @property
    def closed(self) -> bool:
        return self._closed

    def execute(self, *, softening: float = 0.0) -> dict[str, Any]:
        if self._closed or not self._handle.value:
            raise RuntimeError("prepared native aggregate hierarchy is closed")
        softening = float(softening)
        if not math.isfinite(softening) or softening < 0.0:
            raise ValueError("softening must be finite and non-negative")
        opening = self._plan.spec.opening
        if not isinstance(opening, ContinuationPayloadOpening):
            raise RuntimeError("prepared native plan no longer has continuation semantics")

        reducer_kind = {
            AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT: 0,
            AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM: 1,
        }.get(self._plan.spec.reducer)
        if reducer_kind is None:
            raise RuntimeError("prepared native plan no longer has a supported reducer")

        import numpy as np

        point_count = self._plan.spec.prepared_hierarchy.hierarchy.point_count
        reducer_value_0 = np.empty(point_count, dtype=np.float64)
        visited = np.empty(point_count, dtype=np.int64)
        aggregate = np.empty(point_count, dtype=np.int64)
        exact = np.empty(point_count, dtype=np.int64)
        status_codes = np.empty(point_count, dtype=np.int64)
        kernel_seconds = ctypes.c_double()
        download_seconds = ctypes.c_double()
        native_total_seconds = ctypes.c_double()
        error = ctypes.create_string_buffer(4096)
        execute = _require_native_symbol(
            self._library, self._candidate_symbols[1]
        )
        status = execute(
            self._handle,
            ctypes.c_uint32(reducer_kind),
            ctypes.c_double(opening.max_ratio),
            ctypes.c_double(softening),
            ctypes.c_uint64(self._plan.max_output_rows),
            reducer_value_0.ctypes.data_as(_DOUBLE_PTR),
            visited.ctypes.data_as(_I64_PTR),
            aggregate.ctypes.data_as(_I64_PTR),
            exact.ctypes.data_as(_I64_PTR),
            status_codes.ctypes.data_as(_I64_PTR),
            ctypes.byref(kernel_seconds),
            ctypes.byref(download_seconds),
            ctypes.byref(native_total_seconds),
            error,
            ctypes.c_uint64(len(error)),
        )
        _raise_native_error(status, error)
        bad_status = np.flatnonzero(status_codes)
        if bad_status.size:
            first = int(bad_status[0])
            raise RuntimeError(
                "native aggregate-hierarchy traversal failed closed: "
                f"source_id={first}, status_code={int(status_codes[first])}"
            )

        rows = tuple(
            {
                "source_id": index,
                "reducer_value_0": float(reducer_value_0[index]),
                "reducer_value_1": 0.0,
                "reducer_value_2": 0.0,
                "visited_node_count": int(visited[index]),
                "aggregate_contribution_count": int(aggregate[index]),
                "exact_contribution_count": int(exact[index]),
                "status_code": int(status_codes[index]),
            }
            for index in range(point_count)
        )
        return {
            "contract_version": AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
            "backend": (
                "explicit_native"
                if self._plan.selection_owner == "application"
                else "compiler"
            ),
            "selected_backend": self._plan.selected_backend,
            "selected_template": self._plan.selected_template,
            "output_schema": AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA,
            "row_count": len(rows),
            "partial_result_returned": False,
            "rows": rows,
            "metadata": {
                "compiler_plan": self._plan.to_metadata(),
                "native_prepare_seconds": self.prepare_seconds,
                "native_kernel_seconds": float(kernel_seconds.value),
                "native_physical_execute_seconds": float(kernel_seconds.value),
                "native_download_seconds": float(download_seconds.value),
                "native_execute_total_seconds": float(native_total_seconds.value),
                "native_numeric_policy": "float64",
                "physical_executor_kind": (
                    "true_optix_triangle_traversal_with_exact_f64_opening"
                    if self._plan.selected_backend == "optix_traversal"
                    else "precompiled_cuda_continuation_kernel"
                ),
                "optix_traversal_candidate_selected": (
                    self._plan.selected_backend == "optix_traversal"
                ),
                "application_selected_backend": (
                    self._plan.selection_owner == "application"
                ),
                "selection_owner": self._plan.selection_owner,
                "app_identity_used_for_selection": False,
            },
        }

    def close(self) -> None:
        if self._closed:
            return
        error = ctypes.create_string_buffer(4096)
        close = _require_native_symbol(
            self._library, self._candidate_symbols[2]
        )
        status = close(self._handle, error, ctypes.c_uint64(len(error)))
        _raise_native_error(status, error)
        self._handle = ctypes.c_void_p()
        self._closed = True

    def __enter__(self) -> PreparedNativeAggregateHierarchy3D:
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True):
            return
        try:
            self.close()
        except Exception:
            pass


def run_aggregate_frontier_reduce_compiler_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    softening: float = 0.0,
    max_output_rows: int | None = None,
) -> dict[str, Any]:
    """Compile and execute one complete aggregate-hierarchy endpoint."""

    endpoint_started = time.perf_counter()
    plan = compile_aggregate_frontier_reduce_3d(
        spec, max_output_rows=max_output_rows
    )
    if plan.selected_backend == "cuda":
        with PreparedNativeAggregateHierarchy3D(plan) as prepared:
            result = prepared.execute(softening=softening)
    elif plan.selected_backend == "numba":
        execution = aggregate_frontier_reduce_execution_contract_3d(
            spec, backend="numba", max_output_rows=plan.max_output_rows
        )
        result = aggregate_frontier_reduce_numba_3d(
            execution, softening=softening
        )
    else:
        execution = aggregate_frontier_reduce_execution_contract_3d(
            spec, backend="reference", max_output_rows=plan.max_output_rows
        )
        result = aggregate_frontier_reduce_reference_3d(
            execution, softening=softening
        )

    completed = dict(result)
    metadata = dict(completed.get("metadata", {}))
    metadata.update(
        {
            "compiler_plan": plan.to_metadata(),
            "compiler_complete_endpoint_seconds": time.perf_counter()
            - endpoint_started,
            "application_selected_backend": False,
            "app_identity_used_for_selection": False,
            "fixed_speed_target_used_for_selection": False,
        }
    )
    completed["metadata"] = metadata
    completed["backend"] = "compiler"
    completed["selected_backend"] = plan.selected_backend
    completed["selected_template"] = plan.selected_template
    return completed


def run_aggregate_frontier_reduce_default_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    softening: float = 0.0,
    max_output_rows: int | None = None,
    semantic_statement_stable_id: str | None = None,
    backend_contract_id: str | None = None,
) -> dict[str, Any]:
    """Execute the mandatory NVIDIA-RT compiler DEFAULT endpoint."""

    endpoint_started = time.perf_counter()
    plan = compile_aggregate_frontier_reduce_default_3d(
        spec,
        max_output_rows=max_output_rows,
        semantic_statement_stable_id=semantic_statement_stable_id,
        backend_contract_id=backend_contract_id,
    )
    with PreparedNativeAggregateHierarchy3D(plan) as prepared:
        completed = dict(prepared.execute(softening=softening))
    metadata = dict(completed.get("metadata", {}))
    metadata.update(
        {
            "compiler_plan": plan.to_metadata(),
            "compiler_complete_endpoint_seconds": time.perf_counter()
            - endpoint_started,
            "production_default_selected": True,
            "behavioral_optix_claim_requires_post_execution_admission": True,
            "application_selected_backend": False,
            "app_identity_used_for_selection": False,
            "fixed_speed_target_used_for_selection": False,
        }
    )
    completed["metadata"] = metadata
    completed["backend"] = "compiler_default"
    completed["selected_backend"] = plan.selected_backend
    completed["selected_template"] = plan.selected_template
    return completed


def run_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
    spec: AggregateFrontierReduceSpec3D,
    *,
    physical_candidate: str,
    softening: float = 0.0,
    max_output_rows: int | None = None,
) -> dict[str, Any]:
    """Execute one already registered candidate at the complete endpoint."""

    endpoint_started = time.perf_counter()
    plan = compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d(
        spec,
        physical_candidate=physical_candidate,
        max_output_rows=max_output_rows,
    )
    with PreparedNativeAggregateHierarchy3D(plan) as prepared:
        completed = dict(prepared.execute(softening=softening))
    metadata = dict(completed.get("metadata", {}))
    metadata.update(
        {
            "compiler_plan": plan.to_metadata(),
            "compiler_complete_endpoint_seconds": time.perf_counter()
            - endpoint_started,
            "functional_validation_only": True,
            "candidate_establishes_production_priority": False,
            "application_selected_backend": False,
            "app_identity_used_for_selection": False,
        }
    )
    completed["metadata"] = metadata
    return completed


__all__ = (
    "AGGREGATE_HIERARCHY_NATIVE_LOWERING_CONTRACT",
    "AGGREGATE_HIERARCHY_NATIVE_REQUIRED_SYMBOLS",
    "AGGREGATE_HIERARCHY_NATIVE_SUPPORTED_REDUCERS",
    "AGGREGATE_HIERARCHY_NATIVE_TEMPLATE",
    "AGGREGATE_HIERARCHY_OPTIX_REQUIRED_SYMBOLS",
    "AGGREGATE_HIERARCHY_OPTIX_TEMPLATE",
    "AggregateHierarchyCompilerPlan3D",
    "PreparedNativeAggregateHierarchy3D",
    "compile_aggregate_frontier_reduce_3d",
    "compile_aggregate_frontier_reduce_default_3d",
    "compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d",
    "prepare_aggregate_frontier_reduce_explicit_native_3d",
    "run_aggregate_frontier_reduce_compiler_3d",
    "run_aggregate_frontier_reduce_default_3d",
    "run_aggregate_frontier_reduce_candidate_for_functional_validation_3d",
)
