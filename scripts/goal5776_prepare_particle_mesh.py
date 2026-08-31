"""Prepare a deterministic real-scale RTxAdvection point-location input.

The converter is deliberately offline.  It consumes the public author's VTU
mesh, reconstructs the author's shared-face orientation convention, and emits
contiguous NumPy columns.  The formal V2/V4 endpoints consume those same
columns; neither endpoint is allowed to rebuild millions of Python objects.

The 5,000 queries have route-independent answers by construction.  They are
strictly interior convex combinations of tetrahedra whose centroids lie in the
author's frozen microfluidics seeding box.  Hence the expected containing cell
is known without invoking either V2, V4, OptiX, or the application front door.
The closest exit face and neighbor are independently derived from the frozen
topology and the paper ray direction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


U32_MAX = np.uint32(0xFFFFFFFF)
AUTHOR_QUERY_COUNT = 5_000
AUTHOR_DIRECTION = np.asarray((1.0, 1.0e-10, 1.0e-10), dtype=np.float64)
MICROFLUIDICS_SEED_LO = np.asarray((73.9 + 1.0e-5, -0.4 + 1.0e-5,
                                     -655.95 + 1.0e-5), dtype=np.float64)
MICROFLUIDICS_SEED_HI = np.asarray((77.7 - 1.0e-5, 0.0 - 1.0e-5,
                                     -655.45 - 1.0e-5), dtype=np.float64)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _faces_like_author(vertices_f32: np.ndarray, cells: np.ndarray):
    """Vectorized equivalent of RTxAdvection SharedFacesBuilder."""

    if cells.ndim != 2 or cells.shape[1] != 4:
        raise ValueError("particle mesh requires tetrahedral cells")
    if cells.min(initial=0) < 0 or cells.max(initial=0) >= len(vertices_f32):
        raise ValueError("tetrahedral cell index outside vertex domain")
    if np.any(np.sort(cells, axis=1)[:, 1:] == np.sort(cells, axis=1)[:, :-1]):
        raise ValueError("tetrahedral cell repeats a vertex")

    oriented = np.ascontiguousarray(cells, dtype=np.uint32).copy()
    a = vertices_f32[oriented[:, 0]]
    b = vertices_f32[oriented[:, 1]]
    c = vertices_f32[oriented[:, 2]]
    d = vertices_f32[oriented[:, 3]]
    volume = np.einsum("ij,ij->i", d - a, np.cross(b - a, c - a))
    if np.any(volume == np.float32(0.0)):
        raise ValueError("target-f32 degenerate tetrahedron is unsupported")
    negative = volume < np.float32(0.0)
    swapped = oriented[negative, 0].copy()
    oriented[negative, 0] = oriented[negative, 1]
    oriented[negative, 1] = swapped

    # Exact Gmsh face order in the public author's OptixTetQuery.cpp.
    faces = np.concatenate((
        oriented[:, (1, 2, 3)], oriented[:, (2, 0, 3)],
        oriented[:, (0, 1, 3)], oriented[:, (0, 2, 1)],
    ), axis=0)
    owners = np.tile(np.arange(len(oriented), dtype=np.uint32), 4)
    front = np.zeros(len(faces), dtype=np.bool_)
    mask = faces[:, 0] > faces[:, 2]
    tmp = faces[mask, 0].copy(); faces[mask, 0] = faces[mask, 2]; faces[mask, 2] = tmp
    front[mask] = ~front[mask]
    mask = faces[:, 1] > faces[:, 2]
    tmp = faces[mask, 1].copy(); faces[mask, 1] = faces[mask, 2]; faces[mask, 2] = tmp
    front[mask] = ~front[mask]
    mask = faces[:, 0] > faces[:, 1]
    tmp = faces[mask, 0].copy(); faces[mask, 0] = faces[mask, 1]; faces[mask, 1] = tmp
    front[mask] = ~front[mask]
    if not np.all((faces[:, 0] < faces[:, 1]) & (faces[:, 1] < faces[:, 2])):
        raise RuntimeError("author face canonicalization failed")

    unique_faces, inverse, counts = np.unique(
        faces, axis=0, return_inverse=True, return_counts=True)
    if np.any(counts > 2):
        raise ValueError("non-manifold tetrahedral face")
    order = np.argsort(inverse, kind="stable")
    starts = np.empty(len(counts), dtype=np.int64)
    starts[0] = 0
    if len(starts) > 1:
        np.cumsum(counts[:-1], out=starts[1:])
    front_values = np.full(len(counts), U32_MAX, dtype=np.uint32)
    back_values = np.full(len(counts), U32_MAX, dtype=np.uint32)
    cell_face_ids = np.empty((len(oriented), 4), dtype=np.uint32)
    # ``inverse`` follows the four face blocks, matching cell_face_ids.T.
    cell_face_ids.T[:] = inverse.reshape(4, len(oriented)).astype(np.uint32)

    for incidence_index in (0, 1):
        present = counts > incidence_index
        source = order[starts[present] + incidence_index]
        destination = np.flatnonzero(present)
        selected_front = front[source]
        if np.any(selected_front):
            front_values[destination[selected_front]] = owners[source[selected_front]]
        if np.any(~selected_front):
            back_values[destination[~selected_front]] = owners[source[~selected_front]]
    if np.any((front_values != U32_MAX) & (back_values != U32_MAX)
              & (front_values == back_values)):
        raise ValueError("shared face has the same owner on both sides")
    return (np.ascontiguousarray(unique_faces, dtype=np.uint32),
            front_values, back_values, cell_face_ids, oriented)


def _max_tetra_edge(vertices_f32: np.ndarray, cells: np.ndarray) -> float:
    maximum = np.float32(0.0)
    for left, right in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        delta = vertices_f32[cells[:, left]] - vertices_f32[cells[:, right]]
        candidate = np.sqrt(np.einsum("ij,ij->i", delta, delta)).max(initial=0.0)
        maximum = max(maximum, np.float32(candidate))
    if not np.isfinite(maximum) or maximum <= 0:
        raise ValueError("invalid maximum tetrahedral edge length")
    return float(maximum)


def _queries_and_expected(vertices: np.ndarray, cells: np.ndarray,
                          triangles: np.ndarray, front: np.ndarray,
                          back: np.ndarray, cell_faces: np.ndarray,
                          tmax: float):
    centroids = vertices[cells].mean(axis=1)
    eligible = np.flatnonzero(
        np.all((centroids >= MICROFLUIDICS_SEED_LO)
               & (centroids <= MICROFLUIDICS_SEED_HI), axis=1))
    if len(eligible) < AUTHOR_QUERY_COUNT // 2:
        raise ValueError("author seed box does not contain enough tetrahedra")
    chosen = np.resize(eligible, AUTHOR_QUERY_COUNT)
    local_repeat = np.arange(AUTHOR_QUERY_COUNT) // len(eligible)
    # Strictly positive barycentric weights keep every query inside its known
    # cell.  Repeated cells receive a distinct, deterministic interior point.
    weights = np.full((AUTHOR_QUERY_COUNT, 4), 0.2, dtype=np.float64)
    weights[np.arange(AUTHOR_QUERY_COUNT), local_repeat % 4] = 0.4
    origins = np.einsum("ij,ijk->ik", weights, vertices[cells[chosen]])
    # The OptiX contract consumes f32 vertices and origins.  Derive the oracle
    # from those exact consumed values, not from the higher-precision VTU
    # source that is unavailable to either timed route.
    origins_f32 = np.ascontiguousarray(origins, dtype=np.float32)
    oracle_origins = origins_f32.astype(np.float64)
    face_ids = cell_faces[chosen]
    tri = triangles[face_ids]
    a = vertices[tri[:, :, 0]]
    b = vertices[tri[:, :, 1]]
    c = vertices[tri[:, :, 2]]
    normal = np.cross(b - a, c - a)
    denominator = np.einsum("qfi,i->qf", normal, AUTHOR_DIRECTION)
    numerator = np.einsum("qfi,qfi->qf", normal, a - oracle_origins[:, None, :])
    distance = np.divide(
        numerator, denominator,
        out=np.full_like(numerator, np.inf), where=denominator != 0.0)
    distance[distance <= 0.0] = np.inf
    exit_slot = np.argmin(distance, axis=1)
    exit_distance = distance[np.arange(AUTHOR_QUERY_COUNT), exit_slot]
    if not np.all(np.isfinite(exit_distance)):
        raise ValueError("interior query has no positive tetrahedral exit face")
    exit_face = face_ids[np.arange(AUTHOR_QUERY_COUNT), exit_slot]
    exit_denominator = denominator[np.arange(AUTHOR_QUERY_COUNT), exit_slot]
    selected = np.where(exit_denominator < 0.0, front[exit_face], back[exit_face])
    neighbor = np.where(exit_denominator < 0.0, back[exit_face], front[exit_face])
    if not np.array_equal(selected.astype(np.uint32), chosen.astype(np.uint32)):
        raise RuntimeError("independent topology oracle disagrees with containing cell")
    queries = np.empty((AUTHOR_QUERY_COUNT, 7), dtype=np.float32)
    queries[:, :3] = origins_f32
    queries[:, 3:6] = AUTHOR_DIRECTION.astype(np.float32)
    queries[:, 6] = np.float32(tmax)
    expected = np.column_stack((selected, neighbor, exit_face)).astype(np.uint32)
    return queries, expected, chosen.astype(np.uint32), len(eligible)


def main() -> int:
    # Offline author-data conversion dependency; not required by target
    # validation or formal execution of the already frozen NumPy columns.
    import meshio

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-vtu", required=True, type=Path)
    parser.add_argument("--expected-vtu-sha256", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    source_sha = _sha(args.input_vtu)
    if source_sha != args.expected_vtu_sha256:
        raise RuntimeError("particle VTU SHA-256 mismatch")
    mesh = meshio.read(args.input_vtu)
    tetra_blocks = [block.data for block in mesh.cells if block.type == "tetra"]
    if len(tetra_blocks) != 1:
        raise ValueError("expected exactly one tetra cell block")
    vertices_f64 = np.ascontiguousarray(mesh.points, dtype=np.float64)
    vertices_f32 = np.ascontiguousarray(vertices_f64, dtype=np.float32)
    cells = np.ascontiguousarray(tetra_blocks[0], dtype=np.uint32)
    triangles, front, back, cell_faces, oriented_cells = _faces_like_author(
        vertices_f32, cells)
    tmax = _max_tetra_edge(vertices_f32, oriented_cells)
    queries, expected, query_cells, eligible_count = _queries_and_expected(
        vertices_f32.astype(np.float64), oriented_cells, triangles,
        front, back, cell_faces, tmax)

    args.output_dir.mkdir(parents=True, exist_ok=False)
    arrays = {
        "vertices_f32.npy": vertices_f32,
        "triangles_u32.npy": triangles,
        "front_values_u32.npy": front,
        "back_values_u32.npy": back,
        "queries_f32.npy": queries,
        "expected_u32.npy": expected,
        "query_cells_u32.npy": query_cells,
    }
    members = {}
    for name, value in arrays.items():
        path = args.output_dir / name
        np.save(path, value, allow_pickle=False)
        members[name] = {
            "sha256": _sha(path), "size_bytes": path.stat().st_size,
            "shape": list(value.shape), "dtype": str(value.dtype),
        }
    manifest = {
        "schema": "rtdl.goal5776.particle_real_scale_input.v1",
        "source": {
            "path": str(args.input_vtu.resolve()), "sha256": source_sha,
            "public_author_commit": "5cfe63fed227c238905a8f24082b59b5d3160966",
        },
        "mesh": {
            "vertex_count": len(vertices_f32), "tetrahedron_count": len(cells),
            "unique_face_count": len(triangles), "maximum_edge_length": tmax,
        },
        "queries": {
            "count": AUTHOR_QUERY_COUNT,
            "author_default_count": AUTHOR_QUERY_COUNT,
            "seed_box_eligible_tetrahedra": eligible_count,
            "construction": "strict_interior_convex_combinations_v1",
            "direction": AUTHOR_DIRECTION.tolist(),
            "route_independent_expected_cell": True,
        },
        "members": members,
        "claim_boundary": {
            "full_mesh": True, "full_author_query_count": True,
            "full_50000_step_advection": False,
            "author_random_particle_bytes_reproduced": False,
            "performance_result_created": False,
        },
    }
    manifest_path = args.output_dir / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print(json.dumps(manifest["mesh"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
