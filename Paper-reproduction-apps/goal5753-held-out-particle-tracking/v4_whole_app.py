"""Application-owned V4 complete endpoint for tetrahedral particle location.

The input is the held-out two-tetrahedron mesh, not a pre-expanded list of
expected hits.  The application builds unique triangle faces and adjacency;
RTDL verifies/compiles the closed built-in-triangle callback and OptiX chooses
the closest face.  A route-independent rational oracle supplies the expected
cell/neighbor/face rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
import json
import numpy as np
from pathlib import Path
import time

from rtdsl.v4_builtin_triangle_standard_library import (
    BACK_HIT_KIND,
    FRONT_HIT_KIND,
    compile_standard_builtin_triangle_program,
)
from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
from rtdsl.v4_triangle_prepared_runtime import prepare_builtin_triangle_callback


APP_DIR = Path(__file__).resolve().parent
ORACLE_PATH = APP_DIR / "independent_oracle.py"
AUTHOR_SOURCE_SHA256 = (
    "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7"
)
U32_MAX = 0xFFFFFFFF
PAPER_DIRECTION = (
    Fraction(1), Fraction(1, 10_000_000_000),
    Fraction(1, 10_000_000_000),
)


def _oracle():
    spec = importlib.util.spec_from_file_location(
        "rtdl_v4_particle_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load route-independent particle oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_real_scale_v4_input(root: str | Path):
    """Load one frozen Goal5776 full-mesh, 5,000-query input.

    This loader is outside the registered prepared execution timer.  It
    rehashes every array and returns contiguous columns; neither V2 nor V4 may
    expand the 3.39M faces into Python tuples merely to enter a native ABI.
    """

    import numpy as np

    root = Path(root).resolve()
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.particle_real_scale_input.v1":
        raise ValueError("unexpected particle real-scale manifest")
    arrays = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or _file_sha256(path) != row["sha256"]:
            raise RuntimeError(f"particle real-scale member mismatch: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"particle real-scale array contract mismatch: {name}")
        arrays[name] = value
    expected = arrays["expected_u32.npy"]
    return {
        "vertices": arrays["vertices_f32.npy"],
        "triangles": arrays["triangles_u32.npy"],
        "front_values": arrays["front_values_u32.npy"],
        "back_values": arrays["back_values_u32.npy"],
        "queries": arrays["queries_f32.npy"],
        "expected": expected,
        "input_sha256": _file_sha256(manifest_path),
        "independent_oracle_sha256": hashlib.sha256(
            json.dumps({
                "construction": manifest["queries"]["construction"],
                "query_cells_sha256": manifest["members"]["query_cells_u32.npy"]["sha256"],
                "expected_sha256": manifest["members"]["expected_u32.npy"]["sha256"],
                "source_sha256": manifest["source"]["sha256"],
            }, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "real_scale_manifest": manifest,
        "route_independent_expected": True,
    }


def _sub(left, right):
    return tuple(left[index] - right[index] for index in range(3))


def _cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _dot(left, right):
    return sum(left[index] * right[index] for index in range(3))


def _unique_oriented_faces(vertices, cells):
    incidences: dict[tuple[int, int, int], list[tuple[int, tuple[int, ...], int]]] = {}
    for cell_id, cell in enumerate(cells):
        for opposite_index in range(4):
            triangle = tuple(
                cell[index] for index in range(4) if index != opposite_index)
            incidences.setdefault(tuple(sorted(triangle)), []).append((
                cell_id, triangle, cell[opposite_index]))
    rows = []
    for _, adjacent in sorted(incidences.items()):
        triangle = adjacent[0][1]
        a, b, c = (vertices[index] for index in triangle)
        normal = _cross(_sub(b, a), _sub(c, a))
        front = U32_MAX
        back = U32_MAX
        for cell_id, _, opposite_vertex in adjacent:
            side = _dot(normal, _sub(vertices[opposite_vertex], a))
            if side == 0:
                raise ValueError("degenerate tetrahedral face")
            if side > 0:
                if front != U32_MAX:
                    raise ValueError("non-manifold front adjacency")
                front = cell_id
            else:
                if back != U32_MAX:
                    raise ValueError("non-manifold back adjacency")
                back = cell_id
        rows.append((triangle, front, back))
    return tuple(rows)


def _ray_triangle_expected(query, vertices, face_rows):
    best = None
    for face_id, (triangle, front, back) in enumerate(face_rows):
        a, b, c = (vertices[index] for index in triangle)
        edge0 = _sub(b, a)
        edge1 = _sub(c, a)
        normal = _cross(edge0, edge1)
        denominator = _dot(normal, PAPER_DIRECTION)
        if denominator == 0:
            continue
        distance = _dot(normal, _sub(a, query)) / denominator
        if distance < 0:
            continue
        point = tuple(
            query[index] + distance * PAPER_DIRECTION[index]
            for index in range(3)
        )
        offset = _sub(point, a)
        d00 = _dot(edge0, edge0)
        d01 = _dot(edge0, edge1)
        d11 = _dot(edge1, edge1)
        d20 = _dot(offset, edge0)
        d21 = _dot(offset, edge1)
        bary_denominator = d00 * d11 - d01 * d01
        v = (d11 * d20 - d01 * d21) / bary_denominator
        w = (d00 * d21 - d01 * d20) / bary_denominator
        u = Fraction(1) - v - w
        if min(u, v, w) < 0:
            continue
        is_front = denominator < 0
        selected = front if is_front else back
        neighbor = back if is_front else front
        candidate = (distance, face_id, selected, neighbor)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        return (U32_MAX, U32_MAX, U32_MAX)
    return int(best[2]), int(best[3]), int(best[1])


def build_v4_input():
    oracle = _oracle()
    vertices, cells = oracle.two_tetra_fixture()
    queries = (
        oracle.point(Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)),
        oracle.point(Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)),
    )
    expected_cells = tuple(
        oracle.locate_cell(query, vertices, cells) for query in queries)
    face_rows = _unique_oriented_faces(vertices, cells)
    expected_rows = tuple(
        _ray_triangle_expected(query, vertices, face_rows) for query in queries)
    if tuple(row[0] for row in expected_rows) != expected_cells:
        raise RuntimeError("face-orientation projection disagrees with exact cell oracle")
    vertices_f32 = tuple(tuple(float(value) for value in row) for row in vertices)
    triangles = tuple(row[0] for row in face_rows)
    front_values = tuple(int(row[1]) for row in face_rows)
    back_values = tuple(int(row[2]) for row in face_rows)
    query_rows = tuple((
        tuple(float(value) for value in query),
        tuple(float(value) for value in PAPER_DIRECTION),
        2.0,
    ) for query in queries)
    semantic = {
        "vertices": vertices_f32,
        "cells": cells,
        "triangles": triangles,
        "front_values": front_values,
        "back_values": back_values,
        "queries": query_rows,
        "expected": expected_rows,
        "paper_direction": [str(value) for value in PAPER_DIRECTION],
    }
    return {
        **semantic,
        "input_sha256": _digest(semantic),
        "independent_oracle_sha256": hashlib.sha256(
            ORACLE_PATH.read_bytes()).hexdigest(),
    }


def run_v4_complete(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
):
    started = time.perf_counter()
    data = build_v4_input()
    program = compile_standard_builtin_triangle_program(
        target,
        source_semantics_sha256=AUTHOR_SOURCE_SHA256,
        independent_oracle_sha256=data["independent_oracle_sha256"],
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    executed = run_builtin_triangle_callback(
        program.authority,
        program.plan,
        program.abi,
        program.executable,
        vertices=data["vertices"],
        triangles=data["triangles"],
        front_values=data["front_values"],
        back_values=data["back_values"],
        queries=data["queries"],
        expected_output=data["expected"],
        native_library_path=native_library_path,
    )
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.particle_tracking.v4.v1",
        "input_sha256": data["input_sha256"],
        "output": executed.output,
        "expected": data["expected"],
        "matched": executed.output == data["expected"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "tetrahedral_mesh_input",
            "unique_oriented_face_and_adjacency_lowering",
            "restricted_callback_parse_verify",
            "abi_and_wrapper_compile",
            "builtin_triangle_gas_pipeline_sbt_prepare",
            "optix_closest_face_execute",
            "cell_neighbor_face_materialization",
        ),
        "traversal_receipt": executed.traversal_receipt,
        "native_library_sha256": executed.native_library_sha256,
        "default_selected_between_paper_algorithms": False,
    }


@dataclass
class PreparedParticleTrackingV4:
    owner: object
    prepared_input: dict[str, object]
    total_prepare_seconds: float

    def execute(self, *, queries=None):
        query_values = self.prepared_input["queries"] if queries is None else tuple(queries)
        if queries is None:
            expected = tuple(
                tuple(map(int, row)) for row in self.prepared_input["expected"])
        else:
            exact_queries = tuple(
                tuple(Fraction(str(value)) for value in row[0])
                for row in query_values
            )
            face_rows = tuple(zip(
                self.prepared_input["triangles"],
                self.prepared_input["front_values"],
                self.prepared_input["back_values"],
            ))
            exact_vertices = tuple(
                tuple(Fraction(str(value)) for value in row)
                for row in self.prepared_input["vertices"])
            expected = tuple(
                _ray_triangle_expected(
                    query, exact_vertices, face_rows)
                for query in exact_queries
            )
        started = time.perf_counter()
        executed = self.owner.execute(
            query_values, expected_output=expected,
            partner_column_output=hasattr(query_values, "dtype"))
        elapsed = time.perf_counter() - started
        if hasattr(executed.output, "dtype"):
            matched = bool(np.array_equal(
                executed.output, np.asarray(expected, dtype=np.uint32)))
        else:
            matched = executed.output == expected
        return {
            "schema": "rtdl.paper_reproduction.particle_tracking.v4.prepared.v1",
            "output": executed.output,
            "expected": expected,
            "matched": matched,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": executed.traversal_receipt,
            "native_library_sha256": executed.native_library_sha256,
        }

    def close(self):
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_v4(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path, prepared_input=None,
) -> PreparedParticleTrackingV4:
    started = time.perf_counter()
    data = build_v4_input() if prepared_input is None else prepared_input
    program = compile_standard_builtin_triangle_program(
        target, source_semantics_sha256=AUTHOR_SOURCE_SHA256,
        independent_oracle_sha256=data["independent_oracle_sha256"],
        compute_capability=compute_capability, optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    owner = prepare_builtin_triangle_callback(
        authority=program.authority, plan=program.plan, abi=program.abi,
        executable=program.executable, vertices=data["vertices"],
        triangles=data["triangles"], front_values=data["front_values"],
        back_values=data["back_values"],
        native_library_path=native_library_path)
    return PreparedParticleTrackingV4(
        owner, data, time.perf_counter() - started)


__all__ = [
    "PreparedParticleTrackingV4", "build_v4_input", "load_real_scale_v4_input",
    "prepare_v4", "run_v4_complete",
]
