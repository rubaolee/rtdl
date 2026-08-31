#!/usr/bin/env python3
"""Untimed Home gate for the Goal5776 full-mesh Particle V2/V4 lane.

Both methods consume the same frozen 314k-vertex / 3.39M-face columns and the
same 5,000 queries.  The script creates one V2-direct OptiX prepared scene and
one V4 prepared callback owner, checks the complete application output against
the route-independent frozen oracle, and requires behavioral OptiX receipts.
It emits no registered performance observation and refuses to overwrite its
output.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

import numba
import numpy as np

from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


U32_MAX = np.uint32(0xFFFFFFFF)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _array_digest(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for value in arrays:
        array = np.ascontiguousarray(value)
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
        digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def _load_app(source_root: Path):
    path = (
        source_root
        / "Paper-reproduction-apps"
        / "goal5753-held-out-particle-tracking"
        / "v4_whole_app.py"
    )
    name = "goal5776_particle_v4_whole_app"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Particle V4 front door")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"]
        == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(
            int(snapshot[name]) == 0
            for name in (
                "failed_launch_count",
                "incomplete_context_launch_count",
                "pending_context_at_finish",
                "session_error",
            )
        )
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


def _runtime(native: Path, optix_include: Path, cuda_include: Path):
    return {
        "target": ReferenceTargetProfile(
            provider="optix",
            optix_sdk="9.0.0",
            compute_capability="6.1",
            native_sha256=_sha(native),
            supports_custom_aabb=True,
            supports_builtin_triangle=True,
        ),
        "compute_capability": (6, 1),
        "optix_include": optix_include,
        "cuda_include": cuda_include,
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def _v2_output(data: dict[str, object], native: Path):
    from rtdsl import optix_runtime

    vertices = np.asarray(data["vertices"], dtype=np.float32)
    triangles = np.asarray(data["triangles"], dtype=np.uint32)
    queries = np.asarray(data["queries"], dtype=np.float32)
    expected = np.asarray(data["expected"], dtype=np.uint32)

    # The direct lane deliberately uses the public bulk packers rather than
    # constructing 3.39M Python Triangle3D objects.
    packed_triangles = optix_runtime.pack_triangles_3d_from_arrays(
        np.arange(len(triangles), dtype=np.uint32),
        vertices[triangles[:, 0], 0],
        vertices[triangles[:, 0], 1],
        vertices[triangles[:, 0], 2],
        vertices[triangles[:, 1], 0],
        vertices[triangles[:, 1], 1],
        vertices[triangles[:, 1], 2],
        vertices[triangles[:, 2], 0],
        vertices[triangles[:, 2], 1],
        vertices[triangles[:, 2], 2],
    )
    packed_rays = optix_runtime.pack_rays_3d_from_arrays(
        np.arange(len(queries), dtype=np.uint32),
        queries[:, 0], queries[:, 1], queries[:, 2],
        queries[:, 3], queries[:, 4], queries[:, 5], queries[:, 6],
    )
    library = optix_runtime._load_optix_library()
    started = time.perf_counter()
    with optix_runtime.prepare_optix_static_triangle_scene_3d(
        packed_triangles
    ) as scene:
        prepare_seconds = time.perf_counter() - started
        with OptixTraversalAuditSession.open(
            library=library, library_path=native
        ) as audit:
            execute_started = time.perf_counter()
            hit = scene.ray_closest_hit_row_arrays(packed_rays)
            execute_seconds = time.perf_counter() - execute_started

            ray_id = np.asarray(hit["ray_id"], dtype=np.uint32)
            face_id = np.asarray(hit["triangle_id"], dtype=np.uint32)
            distance = np.asarray(hit["t"], dtype=np.float64)
            if len(ray_id) != len(queries):
                raise RuntimeError("V2 closest-hit row count mismatch")
            order = np.argsort(ray_id, kind="stable")
            if not np.array_equal(ray_id[order], np.arange(len(queries), dtype=np.uint32)):
                raise RuntimeError("V2 closest-hit rows do not cover every query exactly once")
            face_id = face_id[order]
            distance = distance[order]
            if np.any(face_id >= len(triangles)) or not np.all(np.isfinite(distance)):
                raise RuntimeError("V2 returned an invalid closest-hit witness")

            selected_triangles = triangles[face_id]
            a = vertices[selected_triangles[:, 0]].astype(np.float64)
            b = vertices[selected_triangles[:, 1]].astype(np.float64)
            c = vertices[selected_triangles[:, 2]].astype(np.float64)
            direction = queries[:, 3:6].astype(np.float64)
            denominator = np.einsum(
                "ij,ij->i", np.cross(b - a, c - a), direction
            )
            if np.any(denominator == 0.0):
                raise RuntimeError("V2 closest-hit face is parallel to its query")
            front = np.asarray(data["front_values"], dtype=np.uint32)[face_id]
            back = np.asarray(data["back_values"], dtype=np.uint32)[face_id]
            selected = np.where(denominator < 0.0, front, back).astype(np.uint32)
            neighbor = np.where(denominator < 0.0, back, front).astype(np.uint32)
            output = np.column_stack((selected, neighbor, face_id)).astype(np.uint32)
            output_digest = _array_digest(output)
            receipt = audit.finish(
                semantic_digest=str(data["input_sha256"]),
                output_digest=output_digest,
                route_identity="goal5776:particle:v2_direct:true_optix:full_mesh",
            )
    if not np.array_equal(output, expected):
        mismatch = int(np.flatnonzero(np.any(output != expected, axis=1))[0])
        raise RuntimeError(f"V2 Particle output mismatch at query {mismatch}")
    if not _receipt_ok(receipt):
        raise RuntimeError("V2 Particle behavioral OptiX receipt failed")
    return {
        "matched": True,
        "output_sha256": output_digest,
        "prepare_seconds_observed_not_formal": prepare_seconds,
        "execute_seconds_observed_not_formal": execute_seconds,
        "traversal_receipt": receipt,
        "closest_hit_metadata": scene.last_closest_hit_metadata,
    }


def _v4_output(app, data: dict[str, object], runtime: dict[str, object]):
    with app.prepare_v4(**runtime, prepared_input=data) as owner:
        prepared_seconds = owner.total_prepare_seconds
        result = owner.execute()
    if result["matched"] is not True:
        raise RuntimeError("V4 Particle output mismatch")
    receipt = dict(result["traversal_receipt"])
    if not _receipt_ok(receipt):
        raise RuntimeError("V4 Particle behavioral OptiX receipt failed")
    output = np.asarray(result["output"], dtype=np.uint32)
    expected = np.asarray(data["expected"], dtype=np.uint32)
    if not np.array_equal(output, expected):
        raise RuntimeError("V4 Particle returned non-canonical output bytes")
    return {
        "matched": True,
        "output_sha256": _array_digest(output),
        "prepare_seconds_observed_not_formal": prepared_seconds,
        "execute_seconds_observed_not_formal": result[
            "registered_prepared_execution_seconds"
        ],
        "traversal_receipt": receipt,
        "lifecycle_receipt": result["lifecycle_receipt"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)

    app = _load_app(args.source_root.resolve())
    data = app.load_real_scale_v4_input(args.input_root)
    expected_digest = _array_digest(np.asarray(data["expected"], dtype=np.uint32))
    v2 = _v2_output(data, native)
    v4 = _v4_output(
        app,
        data,
        _runtime(native, args.optix_include.resolve(), args.cuda_include.resolve()),
    )
    if v2["output_sha256"] != expected_digest or v4["output_sha256"] != expected_digest:
        raise RuntimeError("V2/V4 Particle output digest disagreement")
    result = {
        "schema": "rtdl.goal5776.particle_real_scale_home_smoke.v1",
        "status": "passed",
        "scope": "untimed_functional_capacity_and_behavioral_optix_only",
        "registered_performance_observation_created": False,
        "host": platform.node(),
        "gpu_scope": "Home GTX1070 CC6.1 behavioral OptiX; no RT-silicon claim",
        "source_root": str(args.source_root.resolve()),
        "input_manifest_sha256": str(data["input_sha256"]),
        "native_library_sha256": _sha(native),
        "mesh": {
            "vertex_count": int(len(data["vertices"])),
            "triangle_count": int(len(data["triangles"])),
            "query_count": int(len(data["queries"])),
        },
        "expected_output_sha256": expected_digest,
        "v2_direct": v2,
        "v4": v4,
        "correct_method_count": 2,
        "behavioral_true_optix_method_count": 2,
        "claim_boundary": {
            "full_mesh": True,
            "full_author_query_count": True,
            "full_50000_step_advection": False,
            "formal_performance_claimed": False,
            "modern_rtx_claimed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": result["status"],
        "mesh": result["mesh"],
        "v2_prepare_seconds": v2["prepare_seconds_observed_not_formal"],
        "v4_prepare_seconds": v4["prepare_seconds_observed_not_formal"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
