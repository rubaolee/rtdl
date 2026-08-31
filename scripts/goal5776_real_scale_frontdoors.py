#!/usr/bin/env python3
"""Real-scale V2-direct/V4 front doors for the Goal5776 formal matrix.

Each adapter exposes the same scientific structure: load immutable application
input, prepare one true-OptiX owner, execute and materialize the canonical
application output plus behavioral receipt, close the owner, and compare only
after all registered phases have stopped.  Application-specific algorithms are
frozen by the execution unit; this module never asks DEFAULT to choose one.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
from typing import Mapping

import numba
import numpy as np

from goal5776_real_scale_formal_contract import COLD, PREPARED, UNIT_BY_ID, V2, V4
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _array_digest(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        array = np.ascontiguousarray(value)
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
        digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def _load(path: Path, name: str):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load application module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _native(runtime: Mapping[str, object]) -> Path:
    path = Path(str(runtime["native_library_path"])).resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(path)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(path)
    return path


def _source(runtime: Mapping[str, object]) -> Path:
    return Path(str(runtime["source_root"])).resolve()


def _input(runtime: Mapping[str, object], unit_id: str) -> Mapping[str, object]:
    inputs = runtime.get("inputs")
    if not isinstance(inputs, Mapping) or not isinstance(inputs.get(unit_id), Mapping):
        raise RuntimeError(f"Goal5776 runtime lacks input identity: {unit_id}")
    return inputs[unit_id]


def _v4_runtime(runtime: Mapping[str, object]) -> dict[str, object]:
    native = _native(runtime)
    capability = tuple(int(value) for value in runtime["compute_capability"])
    capability_text = ".".join(map(str, capability))
    return {
        "target": ReferenceTargetProfile(
            provider="optix",
            optix_sdk=str(runtime["optix_sdk_version"]),
            compute_capability=capability_text,
            native_sha256=_sha(native),
            supports_custom_aabb=True,
            supports_builtin_triangle=True,
        ),
        "compute_capability": capability,
        "optix_include": Path(str(runtime["optix_include"])).resolve(),
        "cuda_include": Path(str(runtime["cuda_include"])).resolve(),
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def _single_result(
    *, unit_id: str, lifecycle: str, input_sha256: str,
    output_sha256: str, traversal_receipt: Mapping[str, object],
    loading_seconds: float, preparation_seconds: float,
    execute_seconds: float, close_seconds: float, matched: bool,
) -> dict[str, object]:
    if not matched:
        raise RuntimeError(f"Goal5776 exact output mismatch: {unit_id}")
    row_id = UNIT_BY_ID[unit_id].statistical_row_ids_for(lifecycle)[0]
    registered = float(execute_seconds)
    if lifecycle == COLD:
        registered += float(loading_seconds + preparation_seconds + close_seconds)
    rows = [{
        "row_id": row_id,
        "input_sha256": str(input_sha256),
        "output_sha256": str(output_sha256),
        "registered_complete_endpoint_seconds": registered,
    }]
    return {
        "matched": True,
        "default_selected_between_application_algorithms": False,
        "comparator_inside_registered_timer": False,
        "close_inside_registered_timer": lifecycle == COLD,
        "loading_seconds_reported_separately": (
            None if lifecycle == COLD else float(loading_seconds)
        ),
        "preparation_seconds_reported_separately": (
            None if lifecycle == COLD else float(preparation_seconds)
        ),
        "traversal_receipt": _bind_receipt_to_registered_rows(
            traversal_receipt, rows),
        "phase_accounting": {
            "loading_seconds": float(loading_seconds),
            "preparation_seconds": float(preparation_seconds),
            "close_seconds": float(close_seconds),
            "row_execute_seconds": {row_id: float(execute_seconds)},
            "same_worker_mutually_exclusive_phases": True,
            "nested_phase_medians_summed": False,
        },
        "rows": rows,
    }


def _bind_receipt_to_registered_rows(
    receipt: Mapping[str, object], rows: list[dict[str, object]],
) -> dict[str, object]:
    """Bind behavioral evidence to the exact registered endpoint rows.

    This wrapper is intentionally produced after the registered timer.  It
    does not pretend that the native traversal receipt itself computed an
    application digest; it makes the evidence-layer relationship explicit and
    independently checkable for both V2-direct and V4, including composite
    receipts whose component digests are narrower than the application row.
    """

    result = dict(receipt)
    if "registered_row_binding" in result:
        raise RuntimeError("traversal receipt already carries a row binding")
    canonical_rows = [{
        "row_id": str(row["row_id"]),
        "input_sha256": str(row["input_sha256"]),
        "output_sha256": str(row["output_sha256"]),
    } for row in rows]
    result["registered_row_binding"] = {
        "schema": "rtdl.goal5776.registered_row_binding.v1",
        "binding_scope": "post_timer_evidence_binding__not_native_claim",
        "row_count": len(canonical_rows),
        "ordered_rows_sha256": _digest(canonical_rows),
        "unbound_traversal_receipt_sha256": _digest(result),
    }
    return result


def _combine_receipts(receipts) -> dict[str, object]:
    values = [dict(item) for item in receipts]
    if not values:
        raise RuntimeError("cannot combine an empty traversal-receipt sequence")
    snapshots = [dict(item["native_snapshot"]) for item in values]
    provider = str(values[0].get("provider_library_sha256", ""))
    if provider and any(
        str(item.get("provider_library_sha256", "")) != provider
        for item in values
    ):
        raise RuntimeError("combined receipts span multiple native providers")
    counts = (
        "successful_launch_count", "complete_context_launch_count",
        "unbound_launch_count", "failed_launch_count",
        "incomplete_context_launch_count", "pending_context_at_finish",
        "session_error",
    )
    snapshot = {
        name: sum(int(item.get(name, 0)) for item in snapshots)
        for name in counts
    }
    snapshot["first_traversable"] = snapshots[0].get("first_traversable")
    snapshot["last_traversable"] = snapshots[-1].get("last_traversable")
    return {
        "schema": "rtdl.goal5776.combined_behavioral_optix_receipt.v1",
        "physical_executor_classification": "optix_traversal_observed",
        "provider_library_sha256": provider,
        "native_snapshot": snapshot,
        "component_receipt_count": len(values),
        "component_receipts_sha256": _digest(values),
        # Carry the component receipts instead of forcing a reviewer to trust
        # a digest over evidence that is absent from the packet.
        "component_receipts": values,
    }


def _multi_result(
    *, unit_id: str, lifecycle: str, input_sha256: str,
    row_outputs: Mapping[str, object], row_execute_seconds: Mapping[str, float],
    traversal_receipt: Mapping[str, object], loading_seconds: float,
    preparation_seconds: float, close_seconds: float, matched: bool,
    prepared_session_complete_wall_seconds: float | None = None,
) -> dict[str, object]:
    """Build an endpoint with directly observed, non-derived row bodies."""

    if not matched:
        raise RuntimeError(f"Goal5776 exact output mismatch: {unit_id}")
    row_ids = UNIT_BY_ID[unit_id].statistical_row_ids_for(lifecycle)
    if set(row_ids) != set(row_outputs) or set(row_ids) != set(row_execute_seconds):
        raise RuntimeError("Goal5776 multi-row endpoint shape mismatch")
    rows = []
    for row_id in row_ids:
        execute = float(row_execute_seconds[row_id])
        registered = execute
        if lifecycle == COLD:
            registered += float(loading_seconds + preparation_seconds + close_seconds)
        rows.append({
            "row_id": row_id,
            "input_sha256": str(input_sha256),
            "output_sha256": _digest(row_outputs[row_id]),
            "registered_complete_endpoint_seconds": registered,
        })
    result = {
        "matched": True,
        "default_selected_between_application_algorithms": False,
        "comparator_inside_registered_timer": False,
        "close_inside_registered_timer": lifecycle == COLD,
        "loading_seconds_reported_separately": (
            None if lifecycle == COLD else float(loading_seconds)
        ),
        "preparation_seconds_reported_separately": (
            None if lifecycle == COLD else float(preparation_seconds)
        ),
        "traversal_receipt": _bind_receipt_to_registered_rows(
            traversal_receipt, rows),
        "phase_accounting": {
            "loading_seconds": float(loading_seconds),
            "preparation_seconds": float(preparation_seconds),
            "close_seconds": float(close_seconds),
            "row_execute_seconds": {
                key: float(value) for key, value in row_execute_seconds.items()
            },
            "same_worker_mutually_exclusive_phases": True,
            "nested_phase_medians_summed": False,
        },
        "rows": rows,
    }
    if prepared_session_complete_wall_seconds is not None:
        result["prepared_session_complete_wall_seconds_reported_separately"] = float(
            prepared_session_complete_wall_seconds
        )
    return result


def _run_particle(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    from rtdsl import optix_runtime

    source = _source(runtime)
    native = _native(runtime)
    app = _load(
        source / "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
        "goal5776_formal_particle_v4",
    )
    input_root = Path(str(_input(runtime, unit_id)["input_root"])).resolve()
    started = time.perf_counter()
    data = app.load_real_scale_v4_input(input_root)
    loading = time.perf_counter() - started
    expected = np.asarray(data["expected"], dtype=np.uint32)
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4(**_v4_runtime(runtime), prepared_input=data)
        preparation = time.perf_counter() - started
        try:
            result = owner.execute()
            execute = float(result["registered_prepared_execution_seconds"])
            output = np.asarray(result["output"], dtype=np.uint32)
            receipt = result["traversal_receipt"]
            started = time.perf_counter()
            owner.close()
            owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        vertices = np.asarray(data["vertices"], dtype=np.float32)
        triangles = np.asarray(data["triangles"], dtype=np.uint32)
        queries = np.asarray(data["queries"], dtype=np.float32)
        started = time.perf_counter()
        packed_triangles = optix_runtime.pack_triangles_3d_from_arrays(
            np.arange(len(triangles), dtype=np.uint32),
            vertices[triangles[:, 0], 0], vertices[triangles[:, 0], 1],
            vertices[triangles[:, 0], 2], vertices[triangles[:, 1], 0],
            vertices[triangles[:, 1], 1], vertices[triangles[:, 1], 2],
            vertices[triangles[:, 2], 0], vertices[triangles[:, 2], 1],
            vertices[triangles[:, 2], 2],
        )
        packed_rays = optix_runtime.pack_rays_3d_from_arrays(
            np.arange(len(queries), dtype=np.uint32),
            queries[:, 0], queries[:, 1], queries[:, 2],
            queries[:, 3], queries[:, 4], queries[:, 5], queries[:, 6],
        )
        owner = optix_runtime.prepare_optix_static_triangle_scene_3d(packed_triangles)
        preparation = time.perf_counter() - started
        library = optix_runtime._load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                hit = owner.ray_closest_hit_row_arrays(packed_rays)
                ray_id = np.asarray(hit["ray_id"], dtype=np.uint32)
                face_id = np.asarray(hit["triangle_id"], dtype=np.uint32)
                distance = np.asarray(hit["t"], dtype=np.float64)
                order = np.argsort(ray_id, kind="stable")
                if not np.array_equal(
                    ray_id[order], np.arange(len(queries), dtype=np.uint32)
                ) or np.any(face_id[order] >= len(triangles)) \
                        or not np.all(np.isfinite(distance[order])):
                    raise RuntimeError("V2 Particle closest-hit rows are invalid")
                face_id = face_id[order]
                selected_triangles = triangles[face_id]
                a = vertices[selected_triangles[:, 0]].astype(np.float64)
                b = vertices[selected_triangles[:, 1]].astype(np.float64)
                c = vertices[selected_triangles[:, 2]].astype(np.float64)
                denominator = np.einsum(
                    "ij,ij->i", np.cross(b - a, c - a),
                    queries[:, 3:6].astype(np.float64),
                )
                front = np.asarray(data["front_values"], dtype=np.uint32)[face_id]
                back = np.asarray(data["back_values"], dtype=np.uint32)[face_id]
                output = np.column_stack((
                    np.where(denominator < 0.0, front, back).astype(np.uint32),
                    np.where(denominator < 0.0, back, front).astype(np.uint32),
                    face_id,
                )).astype(np.uint32)
                output_sha = _array_digest(output)
                receipt = audit.finish(
                    semantic_digest=str(data["input_sha256"]),
                    output_digest=output_sha,
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter()
            owner.close()
            owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    output_sha = _array_digest(output)
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=str(data["input_sha256"]), output_sha256=output_sha,
        traversal_receipt=receipt, loading_seconds=loading,
        preparation_seconds=preparation, execute_seconds=execute,
        close_seconds=close, matched=np.array_equal(output, expected),
    )


def _run_rtnn(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    from rtdsl.direct_optix_physical import prepare_direct_optix_bounded_selection_3d
    from rtdsl.optix_runtime import _load_optix_library

    source = _source(runtime)
    native = _native(runtime)
    app = _load(
        source / "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
        "goal5776_formal_rtnn_v4",
    )
    started = time.perf_counter()
    data = app.load_real_scale_v4_input(
        Path(str(_input(runtime, unit_id)["input_root"])).resolve()
    )
    loading = time.perf_counter() - started
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4(**_v4_runtime(runtime), prepared_input=data)
        preparation = time.perf_counter() - started
        try:
            result = owner.execute(
                data["queries"], k=data["k"],
                minimum_distance=data["minimum_distance"],
                maximum_distance=data["maximum_distance"],
                initial_radius=data["initial_radius"],
                maximum_rounds=data["maximum_rounds"],
            )
            execute = float(result["registered_prepared_execution_seconds"])
            output = result["output"]
            receipt = result["traversal_receipt"]
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        migration = app._load_app()
        started = time.perf_counter()
        packed_search = migration._pack_point_rows(data["search"])
        packed_queries = migration._pack_point_rows(data["queries"])
        owner = prepare_direct_optix_bounded_selection_3d(
            packed_search, max_distance_bound=data["maximum_distance"]
        )
        preparation = time.perf_counter() - started
        library = _load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                physical = owner.run(
                    packed_queries,
                    minimum_distance=data["minimum_distance"],
                    maximum_distance=data["maximum_distance"], k=data["k"],
                    minimum_boundary="open", maximum_boundary="open",
                )
                output = migration._canonical_rows(
                    migration._relation_rows_from_rows(physical["rows"])
                )
                output_sha = _digest(output)
                receipt = audit.finish(
                    semantic_digest=data["input_sha256"],
                    output_digest=output_sha,
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    output_sha = _digest(output)
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=data["input_sha256"], output_sha256=output_sha,
        traversal_receipt=receipt, loading_seconds=loading,
        preparation_seconds=preparation, execute_seconds=execute,
        close_seconds=close,
        matched=bool(app._paper_rows_match(output, data["expected"])),
    )


def _run_rt_barneshut(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    from rtdsl.aggregate_hierarchy_native import (
        prepare_aggregate_frontier_reduce_explicit_native_3d,
    )
    from rtdsl.optix_runtime import _load_optix_library

    source = _source(runtime)
    native = _native(runtime)
    app = _load(
        source / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
        "goal5776_formal_rt_barneshut_v4",
    )
    identity = _input(runtime, unit_id)
    started = time.perf_counter()
    data = app.load_real_scale_v4_input(
        Path(str(identity["prepared_arrays"])).resolve(),
        Path(str(identity["expected_forces"])).resolve(),
        expected_prepared_sha256=str(identity["expected_prepared_sha256"]),
        expected_forces_sha256=str(identity["expected_forces_sha256"]),
    )
    loading = time.perf_counter() - started
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4(prepared_input=data)
        preparation = time.perf_counter() - started
        try:
            result = owner.execute(softening=0.0)
            execute = float(result["registered_prepared_execution_seconds"])
            output = result["output"]
            receipt = result["traversal_receipt"]
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        maximum = data["spec"].prepared_hierarchy.hierarchy.point_count
        started = time.perf_counter()
        owner = prepare_aggregate_frontier_reduce_explicit_native_3d(
            data["spec"], backend="optix_traversal",
            max_output_rows=maximum,
        )
        preparation = time.perf_counter() - started
        library = _load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                physical = owner.execute(softening=0.0)
                output = app._canonical_force_rows(tuple({
                    "source_id": int(row["source_id"]),
                    "scalar_force": (
                        float(row["reducer_value_0"])
                        * float(data["force_scale"])
                    ),
                } for row in physical["rows"]))
                output_sha = _digest(output)
                receipt = audit.finish(
                    semantic_digest=str(data["input_sha256"]),
                    output_digest=output_sha,
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    comparison = app._compare_force_rows(output, data["expected_rows"])
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=str(data["input_sha256"]),
        output_sha256=_digest(output), traversal_receipt=receipt,
        loading_seconds=loading, preparation_seconds=preparation,
        execute_seconds=execute, close_seconds=close,
        matched=bool(comparison["matched"]),
    )


def _run_xhd(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    from rtdsl.optix_runtime import (
        _load_optix_library,
        prepare_certified_nearest_global_witness_3d_optix,
    )

    source = _source(runtime)
    native = _native(runtime)
    app = _load(
        source / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
        "goal5776_formal_xhd_v4",
    )
    started = time.perf_counter()
    data = app.load_real_scale_v4_input(
        Path(str(_input(runtime, unit_id)["input_root"])).resolve()
    )
    loading = time.perf_counter() - started
    sources = np.ascontiguousarray(data["sources"], dtype=np.float32)
    targets = np.ascontiguousarray(data["targets"], dtype=np.float32)
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4(**_v4_runtime(runtime), prepared_input=data)
        preparation = time.perf_counter() - started
        try:
            result = owner.execute(sources)
            execute = float(result["registered_prepared_execution_seconds"])
            output = dict(result["output"])
            receipt = result["traversal_receipt"]
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        started = time.perf_counter()
        owner = prepare_certified_nearest_global_witness_3d_optix(
            targets.astype(np.float64),
            target_ids=np.arange(len(targets), dtype=np.int64),
            grid_shape=(32, 32, 32),
            query_domain_lower_bounds=np.min(sources, axis=0),
            query_domain_upper_bounds=np.max(sources, axis=0),
            max_inline_points=64,
            max_heavy_point_evaluations=len(sources) * len(targets),
            application_selected_backend=True,
        )
        preparation = time.perf_counter() - started
        library = _load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                physical = owner.run(sources.astype(np.float64))
                output = dict(physical["actual"])
                output_sha = _digest(output)
                receipt = audit.finish(
                    semantic_digest=str(data["input_sha256"]),
                    output_digest=output_sha,
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    expected = dict(data["expected"])
    matched = (
        int(output["source_id"]) == int(expected["source_id"])
        and int(output["item_id"]) == int(expected["item_id"])
        and abs(float(output["value"]) - float(expected["value"])) <= 1.0e-6
    )
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=str(data["input_sha256"]),
        output_sha256=_digest(output), traversal_receipt=receipt,
        loading_seconds=loading, preparation_seconds=preparation,
        execute_seconds=execute, close_seconds=close, matched=matched,
    )


def _normalized_partition(value: Mapping[str, object]) -> dict[str, object]:
    return {
        "canonical_component_labels": [
            int(item) for item in value["canonical_component_labels"]
        ],
        "core_flags": [bool(item) for item in value["core_flags"]],
    }


def _rtdbscan_project(columns, point_count: int) -> dict[str, object]:
    import rtdsl as rt

    point_ids = np.asarray(columns["point_ids"].copy_to_host(), dtype=np.int64)
    labels_in = np.asarray(
        columns["component_labels"].copy_to_host(), dtype=np.int64
    )
    core_in = np.asarray(columns["is_core"].copy_to_host(), dtype=np.int64)
    labels = [-1] * point_count
    core = [False] * point_count
    for index, point_id in enumerate(point_ids.tolist()):
        labels[int(point_id)] = int(labels_in[index])
        core[int(point_id)] = bool(core_in[index])
    return {
        "canonical_component_labels": rt.canonical_partition_labels(labels),
        "core_flags": tuple(core),
    }


def _float32_from_hex(value: str) -> float:
    return float(np.asarray((int(value, 16),), dtype=np.uint32).view(np.float32)[0])


def _load_rtdbscan_case(
    *, unit_id: str, identity: Mapping[str, object], app,
) -> dict[str, object]:
    case_id = unit_id.removeprefix("rtdbscan__")
    if case_id == "goal5776_clustered3d_4096":
        return app.load_real_scale_v4_input(
            Path(str(identity["input_root"])).resolve()
        )
    evidence_path = Path(str(identity["refinement_evidence_path"])).resolve()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    selected = [row for row in evidence["cases"] if row["case_id"] == case_id]
    if len(selected) != 1:
        raise RuntimeError(f"missing unique RT-DBSCAN frozen case: {case_id}")
    row = selected[0]
    input_row = row["input"]
    points = np.asarray([
        [_float32_from_hex(item) for item in point]
        for point in input_row["points_f32_hex"]
    ], dtype=np.float32)
    return {
        "points": np.ascontiguousarray(points),
        "epsilon": _float32_from_hex(input_row["radius_f32_hex"]),
        "min_points": int(input_row["min_neighbors"]),
        "expected": _normalized_partition(row["outputs"]["independent_oracle"]),
        "input_sha256": _digest({
            "case_id": case_id,
            "points_f32_hex": input_row["points_f32_hex"],
            "radius_f32_hex": input_row["radius_f32_hex"],
            "min_neighbors": int(input_row["min_neighbors"]),
        }),
        "route_independent_expected": True,
        "frozen_refinement_evidence_sha256": _sha(evidence_path),
    }


def _run_rtdbscan(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    import rtdsl as rt
    from rtdsl import optix_runtime

    source = _source(runtime)
    native = _native(runtime)
    app = _load(
        source / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
        "goal5776_formal_rtdbscan_v4",
    )
    started = time.perf_counter()
    data = _load_rtdbscan_case(
        unit_id=unit_id, identity=_input(runtime, unit_id), app=app,
    )
    loading = time.perf_counter() - started
    points = np.ascontiguousarray(data["points"], dtype=np.float32)
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4(
            **_v4_runtime(runtime), points=points,
            initial_radius=float(data["epsilon"]),
            frozen_expected=_normalized_partition(data["expected"]),
            frozen_input_sha256=str(data["input_sha256"]),
            frozen_epsilon=float(data["epsilon"]),
            frozen_min_points=int(data["min_points"]),
            maximum_event_capacity=int(len(points)) ** 2,
        )
        preparation = time.perf_counter() - started
        try:
            result = owner.execute(
                epsilon=float(data["epsilon"]),
                min_points=int(data["min_points"]),
            )
            execute = float(result["registered_prepared_execution_seconds"])
            output = _normalized_partition(result["output"])
            receipt = result["traversal_receipt"]
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        lifted = points if points.shape[1] == 3 else np.column_stack((
            points, np.zeros((len(points),), dtype=np.float32)
        ))
        point_rows = tuple(rt.Point3D(
            id=index, x=float(row[0]), y=float(row[1]), z=float(row[2])
        ) for index, row in enumerate(lifted))
        started = time.perf_counter()
        owner = rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d(
            point_rows, radius=float(data["epsilon"]), partner="numba"
        )
        preparation = time.perf_counter() - started
        library = optix_runtime._load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                physical = rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns(
                    owner, min_neighbors=int(data["min_points"]),
                    return_metadata=True,
                )
                output = _normalized_partition(
                    _rtdbscan_project(physical["columns"], len(points))
                )
                output_sha = _digest(output)
                receipt = audit.finish(
                    semantic_digest=str(data["input_sha256"]),
                    output_digest=output_sha,
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    expected = _normalized_partition(data["expected"])
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=str(data["input_sha256"]),
        output_sha256=_digest(output), traversal_receipt=receipt,
        loading_seconds=loading, preparation_seconds=preparation,
        execute_seconds=execute, close_seconds=close,
        matched=output == expected,
    )


def _run_triangle(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    from rtdsl import optix_runtime

    source = _source(runtime)
    native = _native(runtime)
    identity = _input(runtime, unit_id)
    algorithm = UNIT_BY_ID[unit_id].paper_algorithm
    edge_file = Path(str(identity["edge_file"])).resolve()
    expected_count = int(identity["expected_triangle_count"])
    maximum_rows = int(identity.get("max_relation_rows", 1_000_000))
    v2_app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v2_14_whole_app.py",
        "goal5776_formal_triangle_v2",
    )
    v4_app = _load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        "goal5776_formal_triangle_v4",
    )
    started = time.perf_counter()
    benchmark = v2_app._load_benchmark()
    graph_contract = benchmark.build_segmented_rt_graph_csr_binary(
        str(edge_file), expected_triangle_count=expected_count,
    )
    input_sha = _sha(edge_file)
    loading = time.perf_counter() - started
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = v4_app.prepare_v4_segmented(
            algorithm, **_v4_runtime(runtime), edge_file=str(edge_file),
            expected_triangle_count=expected_count,
            max_relation_rows=maximum_rows,
            prepared_graph_contract=graph_contract,
        )
        preparation = time.perf_counter() - started
        try:
            result = owner.execute()
            execute = float(result["registered_prepared_execution_seconds"])
            output = {"triangle_count": int(result["output"]["triangle_count"])}
            receipt = _combine_receipts(result["traversal_receipts"])
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        preparation = 0.0
        library = optix_runtime._load_optix_library()
        started = time.perf_counter()
        with OptixTraversalAuditSession.open(
            library=library, library_path=native
        ) as audit:
            source_result = benchmark.run_rt_graph_segmented_optix_scalar_summary(
                graph_contract, paper_method=algorithm,
                max_relation_rows=maximum_rows,
            )
            output = {"triangle_count": int(source_result["scalar_sum"])}
            receipt = audit.finish(
                semantic_digest=input_sha, output_digest=_digest(output),
                route_identity=f"goal5776:{unit_id}:{method}",
            )
        execute = time.perf_counter() - started
        close = 0.0
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle,
        input_sha256=input_sha, output_sha256=_digest(output),
        traversal_receipt=receipt, loading_seconds=loading,
        preparation_seconds=preparation, execute_seconds=execute,
        close_seconds=close,
        matched=int(output["triangle_count"]) == expected_count,
    )


def _run_librts(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    import rtdsl as rt
    from rtdsl.optix_runtime import _load_optix_library

    source = _source(runtime)
    native = _native(runtime)
    identity = _input(runtime, unit_id)
    operation = (
        "point_contains" if unit_id.endswith("point_contains")
        else "range_contains"
    )
    app = _load(
        source / "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
        "goal5776_formal_librts_v4",
    )
    loaders = _load(
        source / "Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py",
        "goal5776_formal_librts_loaders",
    )
    cache_npz = Path(str(identity["cache_npz"])).resolve()
    cache_json = Path(str(identity["cache_json"])).resolve()
    query_path = Path(str(identity[
        "point_queries" if operation == "point_contains" else "range_queries"
    ])).resolve()
    started = time.perf_counter()
    metadata = json.loads(cache_json.read_text(encoding="utf-8"))
    with np.load(cache_npz, allow_pickle=False) as arrays:
        indexed = rt.Aabb2DColumns(
            ids=np.array(arrays["ids"], copy=True),
            min_x=np.array(arrays["min_x"], copy=True),
            min_y=np.array(arrays["min_y"], copy=True),
            max_x=np.array(arrays["max_x"], copy=True),
            max_y=np.array(arrays["max_y"], copy=True),
        )
    if len(indexed) != int(metadata["row_count"]):
        raise RuntimeError("LibRTS cache cardinality mismatch")
    if operation == "point_contains":
        queries = loaders.load_point_queries(query_path)
        execute_kwargs = {"point_queries": queries}
    else:
        queries = tuple(loaders.load_geometry_mbr_columns_fast(query_path))
        execute_kwargs = {"box_queries": queries}
    input_sha = _digest({
        "operation": operation,
        "cache_npz_sha256": _sha(cache_npz),
        "cache_json_sha256": _sha(cache_json),
        "query_sha256": _sha(query_path),
        "indexed_count": len(indexed), "query_count": len(queries),
    })
    loading = time.perf_counter() - started
    owner = None
    if method == V4:
        started = time.perf_counter()
        owner = app.prepare_v4_real_scale_count(
            target=_v4_runtime(runtime)["target"], indexed_columns=indexed,
            operation=operation, native_library_path=native,
        )
        preparation = time.perf_counter() - started
        try:
            started = time.perf_counter()
            observed = owner.execute_count(**execute_kwargs)
            execute = time.perf_counter() - started
            value = int(observed["count"])
            receipt = observed["traversal_receipt"]
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    else:
        started = time.perf_counter()
        owner = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
        preparation = time.perf_counter() - started
        library = _load_optix_library()
        try:
            started = time.perf_counter()
            with OptixTraversalAuditSession.open(
                library=library, library_path=native
            ) as audit:
                observed = owner.count(operation=operation, **execute_kwargs)
                value = int(observed["counts"][operation])
                receipt = audit.finish(
                    semantic_digest=input_sha,
                    output_digest=_digest({"count": value}),
                    route_identity=f"goal5776:{unit_id}:{method}",
                )
            execute = time.perf_counter() - started
            started = time.perf_counter(); owner.close(); owner = None
            close = time.perf_counter() - started
        finally:
            if owner is not None:
                owner.close()
    output = {"count": value}
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle, input_sha256=input_sha,
        output_sha256=_digest(output), traversal_receipt=receipt,
        loading_seconds=loading, preparation_seconds=preparation,
        execute_seconds=execute, close_seconds=close,
        matched=value == int(identity["expected_count"]),
    )


def _run_raydb(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    """Run the authentic 60M-row packet as a cold-only complete endpoint."""

    if lifecycle != COLD:
        raise RuntimeError(
            "RayDB real-scale has no authentic prepared packet owner; fixture substitution is forbidden"
        )
    source = _source(runtime)
    native = _native(runtime)
    identity = _input(runtime, unit_id)
    packet = Path(str(identity["packet_path"])).resolve()
    partition_rows = int(identity["partition_rows"])
    input_sha = _sha(packet)
    if method == V4:
        app = _load(
            source / "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
            "goal5776_formal_raydb_v4",
        )
        started = time.perf_counter()
        observed = app.run_v4_real_scale_packet(
            packet_path=packet, partition_rows=partition_rows,
            **_v4_runtime(runtime),
        )
        complete = time.perf_counter() - started
        output = observed["output"]
        receipt = observed["traversal_receipt"]
        matched = bool(observed["matched"])
    else:
        runner = _load(
            source / "Paper-reproduction-apps/raydb-paper/run_ssb_packet_rtdl.py",
            "goal5776_formal_raydb_v2",
        )
        library = runner._load_optix_library() if hasattr(
            runner, "_load_optix_library"
        ) else None
        if library is None:
            from rtdsl.optix_runtime import _load_optix_library
            library = _load_optix_library()
        started = time.perf_counter()
        audit = OptixTraversalAuditSession.open(
            library=library, library_path=native
        )
        try:
            observed = runner.run_packet(
                packet, partition_rows=partition_rows
            )
            output = {"grouped_rows": observed["rtdl_rows"]}
            receipt = audit.finish(
                semantic_digest=input_sha, output_digest=_digest(output),
                route_identity=f"goal5776:{unit_id}:{method}",
            )
        except Exception:
            audit.abort()
            raise
        complete = time.perf_counter() - started
        matched = bool(observed["rtdl_matches_oracle"])
    return _single_result(
        unit_id=unit_id, lifecycle=lifecycle, input_sha256=input_sha,
        output_sha256=_digest(output), traversal_receipt=receipt,
        loading_seconds=0.0, preparation_seconds=0.0,
        execute_seconds=complete, close_seconds=0.0, matched=matched,
    )


def _rayjoin_output(protocol: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    return tuple({
        "batch_index": index,
        "lsi_row_count": int(row["lsi_row_count"]),
        "descriptor_pair_count": int(row["descriptor_pair_count"]),
        "total_groups": int(row.get("descriptor_total_groups", 0)),
        "total_point_rows": int(row.get("descriptor_total_point_rows", 0)),
        "pair_rows_sha256": row.get("descriptor_pair_rows_sha256"),
    } for index, row in enumerate(protocol["measured_rows"]))


def _run_rayjoin(
    unit_id: str, method: str, lifecycle: str, runtime: Mapping[str, object]
) -> dict[str, object]:
    source = _source(runtime)
    native = _native(runtime)
    identity = _input(runtime, unit_id)
    left = Path(str(identity["left"])).resolve()
    right = Path(str(identity["right"])).resolve()
    capacity = int(identity["lsi_capacity"])
    input_sha = _digest({
        "left_sha256": _sha(left), "right_sha256": _sha(right),
        "lsi_capacity": capacity, "query_chain_batches": 6,
    })
    expected_output_sha = str(identity["expected_output_sha256"])
    app = _load(
        source / "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
        "goal5776_formal_rayjoin_v4",
    )
    legacy = _load(
        source / "Paper-reproduction-apps/rayjoin-paper/rtdl3_whole_app.py",
        "goal5776_formal_rayjoin_v2",
    )
    compile_seconds = 0.0
    compiled = None
    if method == V4 and lifecycle == PREPARED:
        started = time.perf_counter()
        compiled = app.compile_v4_real_scale_six_batch(
            lsi_capacity=capacity,
            **{key: value for key, value in _v4_runtime(runtime).items()
               if key != "native_library_path"},
        )
        compile_seconds = time.perf_counter() - started

    started = time.perf_counter()
    if method == V4:
        observed = app.run_v4_real_scale_six_batch(
            left, right, lsi_capacity=capacity,
            prepared_compiled_relation=compiled, **_v4_runtime(runtime),
        )
        canonical = tuple(observed["output"])
        protocol = observed["source_result"]
        receipt = observed["traversal_receipt"]
    else:
        args = legacy.prepared_six_batch_args(
            left, right, lsi_capacity=capacity,
            pair_name="goal5776_formal_v2_six_batch",
        )
        from rtdsl.optix_runtime import _load_optix_library
        audit = OptixTraversalAuditSession.open(
            library=_load_optix_library(), library_path=native
        )
        try:
            protocol = legacy.run_v2_prepared_six_batch(args)
            canonical = _rayjoin_output(protocol)
            receipt = audit.finish(
                semantic_digest=input_sha, output_digest=_digest(canonical),
                route_identity=f"goal5776:{unit_id}:{method}",
            )
        except Exception:
            audit.abort()
            raise
    complete_wall = time.perf_counter() - started
    if len(canonical) != 6 or _digest(canonical) != expected_output_sha:
        raise RuntimeError("RayJoin six-batch canonical output mismatch")
    if lifecycle == COLD:
        row_id = UNIT_BY_ID[unit_id].statistical_row_ids_for(COLD)[0]
        return _multi_result(
            unit_id=unit_id, lifecycle=lifecycle, input_sha256=input_sha,
            row_outputs={row_id: canonical},
            row_execute_seconds={row_id: complete_wall},
            traversal_receipt=receipt, loading_seconds=0.0,
            preparation_seconds=0.0, close_seconds=0.0, matched=True,
        )

    session = dict(protocol["session_prepare_phase_seconds"])
    loading = sum(float(value) for key, value in session.items()
                  if key.startswith("session_load_pack_"))
    preparation = compile_seconds + sum(
        float(value) for key, value in session.items()
        if not key.startswith("session_load_pack_")
    )
    specialization = protocol.get("descriptor_consumer_specialization")
    if isinstance(specialization, Mapping):
        preparation += float(specialization.get("elapsed_seconds", 0.0))
    row_ids = UNIT_BY_ID[unit_id].statistical_row_ids_for(PREPARED)
    measured = tuple(protocol["measured_rows"])
    if len(measured) != 6:
        raise RuntimeError("RayJoin prepared protocol did not expose six direct rows")
    return _multi_result(
        unit_id=unit_id, lifecycle=lifecycle, input_sha256=input_sha,
        row_outputs={row_id: canonical[index]
                     for index, row_id in enumerate(row_ids)},
        row_execute_seconds={
            row_id: float(measured[index]["writer_free_hot_sec"])
            for index, row_id in enumerate(row_ids)
        },
        traversal_receipt=receipt, loading_seconds=loading,
        preparation_seconds=preparation, close_seconds=0.0, matched=True,
        prepared_session_complete_wall_seconds=complete_wall,
    )


_DISPATCH = {
    "particle_tracking": _run_particle,
    "rtnn": _run_rtnn,
    "rt_barneshut": _run_rt_barneshut,
    "x_hd": _run_xhd,
    "rt_dbscan": _run_rtdbscan,
    "triangle_counting": _run_triangle,
    "librts": _run_librts,
    "raydb": _run_raydb,
    "rayjoin": _run_rayjoin,
}


def run_real_scale_endpoint(
    *, unit_id: str, method: str, lifecycle: str,
    runtime: Mapping[str, object],
) -> dict[str, object]:
    if unit_id not in UNIT_BY_ID or method not in (V2, V4) \
            or lifecycle not in (COLD, PREPARED):
        raise ValueError("unknown Goal5776 endpoint identity")
    unit = UNIT_BY_ID[unit_id]
    if lifecycle not in unit.supported_lifecycles:
        raise RuntimeError(
            f"Goal5776 lifecycle is not supported by authentic route: {unit_id}:{lifecycle}"
        )
    try:
        runner = _DISPATCH[unit.app]
    except KeyError as exc:
        raise RuntimeError(
            f"Goal5776 real-scale adapter is not implemented: {unit.app}"
        ) from exc
    return runner(unit_id, method, lifecycle, runtime)


__all__ = ["run_real_scale_endpoint"]
