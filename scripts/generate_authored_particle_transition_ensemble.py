#!/usr/bin/env python3
"""Generate distinct strict-interior Particle transitions on a real mesh."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from scripts.goal5776_prepare_particle_mesh import (
    AUTHOR_DIRECTION,
    MICROFLUIDICS_SEED_HI,
    MICROFLUIDICS_SEED_LO,
    _faces_like_author,
)


U64_MASK = np.uint64(0xFFFFFFFFFFFFFFFF)
U32_MAX = np.uint32(0xFFFFFFFF)


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _splitmix64(values: np.ndarray, salt: int) -> np.ndarray:
    result = values ^ np.uint64(salt)
    result = (result + np.uint64(0x9E3779B97F4A7C15)) & U64_MASK
    result = ((result ^ (result >> np.uint64(30)))
              * np.uint64(0xBF58476D1CE4E5B9)) & U64_MASK
    result = ((result ^ (result >> np.uint64(27)))
              * np.uint64(0x94D049BB133111EB)) & U64_MASK
    return result ^ (result >> np.uint64(31))


def _uniform53(values: np.ndarray, salt: int) -> np.ndarray:
    return ((_splitmix64(values, salt) >> np.uint64(11)).astype(np.float64)
            * (1.0 / (1 << 53)))


def _strict_barycentric_weights(
    indices: np.ndarray, *, attempt: int = 0,
) -> np.ndarray:
    attempt_salt = (attempt * 0xD1B54A32D192ED03) & 0xFFFFFFFFFFFFFFFF
    weights = np.empty((len(indices), 4), dtype=np.float64)
    weights[:, 0] = 0.1 + 0.15 * _uniform53(
        indices, 0x243F6A8885A308D3 ^ attempt_salt)
    weights[:, 1] = 0.1 + 0.15 * _uniform53(
        indices, 0x13198A2E03707344 ^ attempt_salt)
    weights[:, 2] = 0.1 + 0.15 * _uniform53(
        indices, 0xA4093822299F31D0 ^ attempt_salt)
    weights[:, 3] = 1.0 - weights[:, :3].sum(axis=1)
    if np.any(weights <= 0.0) or not np.allclose(
            weights.sum(axis=1), 1.0, rtol=0.0, atol=2e-16):
        raise RuntimeError("strict barycentric generator failed")
    return weights


def _cell_barycentric_rows(
    cell_vertices: np.ndarray, origins: np.ndarray,
) -> np.ndarray:
    v0, v1, v2, v3 = (cell_vertices[:, index] for index in range(4))
    e0 = v0 - v3
    e1 = v1 - v3
    e2 = v2 - v3
    delta = origins - v3
    denominator = np.einsum("ij,ij->i", e0, np.cross(e1, e2))
    if np.any(denominator == 0.0):
        raise ValueError("selected Particle cell is degenerate")
    l0 = np.einsum("ij,ij->i", delta, np.cross(e1, e2)) / denominator
    l1 = np.einsum("ij,ij->i", e0, np.cross(delta, e2)) / denominator
    l2 = np.einsum("ij,ij->i", e0, np.cross(e1, delta)) / denominator
    l3 = 1.0 - l0 - l1 - l2
    return np.column_stack((l0, l1, l2, l3))


def _triangle_barycentric_minimum_rows(
    a: np.ndarray, b: np.ndarray, c: np.ndarray, points: np.ndarray,
) -> np.ndarray:
    edge_0 = b - a
    edge_1 = c - a
    offset = points - a
    dot_00 = np.einsum("ij,ij->i", edge_0, edge_0)
    dot_01 = np.einsum("ij,ij->i", edge_0, edge_1)
    dot_11 = np.einsum("ij,ij->i", edge_1, edge_1)
    dot_20 = np.einsum("ij,ij->i", offset, edge_0)
    dot_21 = np.einsum("ij,ij->i", offset, edge_1)
    denominator = dot_00 * dot_11 - dot_01 * dot_01
    safe = denominator != 0.0
    first = np.divide(
        dot_11 * dot_20 - dot_01 * dot_21, denominator,
        out=np.full_like(denominator, -np.inf), where=safe)
    second = np.divide(
        dot_00 * dot_21 - dot_01 * dot_20, denominator,
        out=np.full_like(denominator, -np.inf), where=safe)
    return np.minimum(np.minimum(first, second), 1.0 - first - second)


def _verify_static_base(
    base: Path,
    vertices: np.ndarray,
    triangles: np.ndarray,
    front: np.ndarray,
    back: np.ndarray,
) -> dict[str, object]:
    manifest_path = base / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {
        "vertices_f32.npy": vertices,
        "triangles_u32.npy": triangles,
        "front_values_u32.npy": front,
        "back_values_u32.npy": back,
    }
    for name, value in expected.items():
        path = base / name
        row = manifest["members"][name]
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"base Particle member hash differs: {name}")
        observed = np.load(path, mmap_mode="r", allow_pickle=False)
        if observed.shape != value.shape or observed.dtype != value.dtype \
                or not np.array_equal(observed, value):
            raise RuntimeError(f"base Particle static topology differs: {name}")
    return {
        "manifest_sha256": sha256(manifest_path),
        "source_sha256": manifest["source"]["sha256"],
        "maximum_edge_length": manifest["mesh"]["maximum_edge_length"],
    }


def _generate_chunk(
    *, start: int, stop: int, eligible: np.ndarray,
    vertices: np.ndarray, cells: np.ndarray, triangles: np.ndarray,
    front: np.ndarray, back: np.ndarray, cell_faces: np.ndarray,
    tmax: float, exit_barycentric_margin: float = 1.0e-3,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float, int]:
    indices = np.arange(start, stop, dtype=np.uint64)
    chosen = eligible[(indices % np.uint64(len(eligible))).astype(np.int64)]
    queries = np.empty((len(indices), 7), dtype=np.float32)
    queries[:, 3:6] = AUTHOR_DIRECTION.astype(np.float32)
    queries[:, 6] = np.float32(tmax)
    expected = np.empty((len(indices), 3), dtype=np.uint32)
    pending = np.arange(len(indices), dtype=np.int64)
    minimum_cell_barycentric = math.inf
    minimum_exit_barycentric = math.inf
    rejected_candidate_count = 0
    for attempt in range(16):
        if len(pending) == 0:
            break
        current_indices = indices[pending]
        current_chosen = chosen[pending]
        weights = _strict_barycentric_weights(
            current_indices, attempt=attempt)
        cell_vertices = vertices[cells[current_chosen]]
        origins = np.einsum("ij,ijk->ik", weights, cell_vertices)
        origins_f32 = np.ascontiguousarray(origins, dtype=np.float32)
        oracle_origins = origins_f32.astype(np.float64)
        cell_barycentric = _cell_barycentric_rows(
            cell_vertices, oracle_origins)
        cell_minimum = cell_barycentric.min(axis=1)

        face_ids = cell_faces[current_chosen]
        tri = triangles[face_ids]
        a = vertices[tri[:, :, 0]]
        b = vertices[tri[:, :, 1]]
        c = vertices[tri[:, :, 2]]
        normal = np.cross(b - a, c - a)
        denominator = np.einsum("qfi,i->qf", normal, AUTHOR_DIRECTION)
        numerator = np.einsum(
            "qfi,qfi->qf", normal, a - oracle_origins[:, None, :])
        distance = np.divide(
            numerator, denominator,
            out=np.full_like(numerator, np.inf), where=denominator != 0.0)
        distance[distance <= 0.0] = np.inf
        exit_slot = np.argmin(distance, axis=1)
        row = np.arange(len(pending))
        exit_distance = distance[row, exit_slot]
        exit_face = face_ids[row, exit_slot]
        exit_denominator = denominator[row, exit_slot]
        selected = np.where(
            exit_denominator < 0.0, front[exit_face], back[exit_face])
        neighbor = np.where(
            exit_denominator < 0.0, back[exit_face], front[exit_face])
        exit_a = a[row, exit_slot]
        exit_b = b[row, exit_slot]
        exit_c = c[row, exit_slot]
        exit_points = oracle_origins \
            + exit_distance[:, None] * AUTHOR_DIRECTION[None, :]
        exit_minimum = _triangle_barycentric_minimum_rows(
            exit_a, exit_b, exit_c, exit_points)
        valid = np.isfinite(exit_distance) \
            & (cell_minimum > 0.0) \
            & (exit_minimum > exit_barycentric_margin) \
            & (selected != U32_MAX) \
            & (selected.astype(np.uint32) == current_chosen)
        accepted = pending[valid]
        queries[accepted, :3] = origins_f32[valid]
        expected[accepted] = np.column_stack((
            selected[valid], neighbor[valid], exit_face[valid],
        )).astype(np.uint32)
        if np.any(valid):
            minimum_cell_barycentric = min(
                minimum_cell_barycentric, float(cell_minimum[valid].min()))
            minimum_exit_barycentric = min(
                minimum_exit_barycentric, float(exit_minimum[valid].min()))
        rejected_candidate_count += int((~valid).sum())
        pending = pending[~valid]
    if len(pending):
        raise RuntimeError(
            f"Particle strict-exit resampling exhausted: {len(pending)}")
    return (
        queries, expected, chosen.astype(np.uint32),
        minimum_cell_barycentric, minimum_exit_barycentric,
        rejected_candidate_count,
    )


def main() -> int:
    import meshio

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-vtu", type=Path, required=True)
    parser.add_argument("--expected-vtu-sha256", required=True)
    parser.add_argument("--base-particle-dir", type=Path, required=True)
    parser.add_argument("--query-count", type=int, required=True)
    parser.add_argument("--chunk-size", type=int, default=250_000)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.query_count <= 0xFFFFFFFF:
        raise ValueError("query count is outside nonzero U32")
    if args.chunk_size < 1:
        raise ValueError("chunk size must be positive")
    if sha256(args.input_vtu) != args.expected_vtu_sha256:
        raise RuntimeError("Particle VTU identity differs")

    mesh = meshio.read(args.input_vtu)
    tetra_blocks = [block.data for block in mesh.cells if block.type == "tetra"]
    if len(tetra_blocks) != 1:
        raise ValueError("expected exactly one tetrahedral cell block")
    vertices_f32 = np.ascontiguousarray(mesh.points, dtype=np.float32)
    vertices = vertices_f32.astype(np.float64)
    cells = np.ascontiguousarray(tetra_blocks[0], dtype=np.uint32)
    triangles, front, back, cell_faces, oriented_cells = _faces_like_author(
        vertices_f32, cells)
    base = _verify_static_base(
        args.base_particle_dir.resolve(strict=True),
        vertices_f32, triangles, front, back)
    centroids = vertices[oriented_cells].mean(axis=1)
    eligible = np.flatnonzero(np.all(
        (centroids >= MICROFLUIDICS_SEED_LO)
        & (centroids <= MICROFLUIDICS_SEED_HI), axis=1))
    if len(eligible) != 3_636:
        raise RuntimeError(f"Particle eligible-cell count differs: {len(eligible)}")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    query_path = output / "queries_f32.npy"
    expected_path = output / "expected_u32.npy"
    cell_path = output / "query_cells_u32.npy"
    queries = np.lib.format.open_memmap(
        query_path, mode="w+", dtype=np.float32,
        shape=(args.query_count, 7))
    expected = np.lib.format.open_memmap(
        expected_path, mode="w+", dtype=np.uint32,
        shape=(args.query_count, 3))
    query_cells = np.lib.format.open_memmap(
        cell_path, mode="w+", dtype=np.uint32,
        shape=(args.query_count,))
    minimum = math.inf
    exit_minimum = math.inf
    rejected_candidate_count = 0
    for start in range(0, args.query_count, args.chunk_size):
        stop = min(start + args.chunk_size, args.query_count)
        (chunk_queries, chunk_expected, chunk_cells, chunk_minimum,
         chunk_exit_minimum, chunk_rejected) = \
            _generate_chunk(
                start=start, stop=stop, eligible=eligible,
                vertices=vertices, cells=oriented_cells,
                triangles=triangles, front=front, back=back,
                cell_faces=cell_faces,
                tmax=float(base["maximum_edge_length"]),
            )
        queries[start:stop] = chunk_queries
        expected[start:stop] = chunk_expected
        query_cells[start:stop] = chunk_cells
        minimum = min(minimum, chunk_minimum)
        exit_minimum = min(exit_minimum, chunk_exit_minimum)
        rejected_candidate_count += chunk_rejected
    queries.flush()
    expected.flush()
    query_cells.flush()

    origin_bits = np.ascontiguousarray(queries[:, :3]).view(np.dtype([
        ("x", "<u4"), ("y", "<u4"), ("z", "<u4"),
    ])).reshape(-1)
    distinct_count = int(np.unique(origin_bits).size)
    if distinct_count != args.query_count:
        raise RuntimeError(
            f"Particle generated origins are not distinct: {distinct_count}")

    members = {}
    for path, shape, dtype in (
        (query_path, [args.query_count, 7], "float32"),
        (expected_path, [args.query_count, 3], "uint32"),
        (cell_path, [args.query_count], "uint32"),
    ):
        members[path.name] = {
            "bytes": path.stat().st_size,
            "dtype": dtype,
            "sha256": sha256(path),
            "shape": shape,
        }
    manifest = {
        "schema": "rtdl.v4.authored_particle.transition_ensemble.v1",
        "source_vtu": {
            "path": str(args.input_vtu.resolve(strict=True)),
            "sha256": args.expected_vtu_sha256,
        },
        "base_particle": base,
        "mesh": {
            "vertex_count": len(vertices_f32),
            "tetrahedron_count": len(oriented_cells),
            "triangle_count": len(triangles),
            "eligible_cell_count": len(eligible),
        },
        "queries": {
            "count": args.query_count,
            "distinct_origin_count": distinct_count,
            "construction": "splitmix64_strict_origin_and_exit_barycentric_v2",
            "minimum_reconstructed_barycentric_weight": minimum,
            "minimum_exit_triangle_barycentric_weight": exit_minimum,
            "exit_triangle_barycentric_margin": 1.0e-3,
            "rejected_candidate_count": rejected_candidate_count,
            "maximum_resample_attempts_per_row": 16,
            "direction": AUTHOR_DIRECTION.tolist(),
            "maximum_distance": base["maximum_edge_length"],
            "chunk_size": args.chunk_size,
        },
        "members": members,
        "claim_boundary": {
            "real_mesh": True,
            "distinct_strict_interior_queries": True,
            "single_cell_transition_stage": True,
            "temporal_particle_simulation": False,
            "author_random_particle_bytes_reproduced": False,
            "performance_result_created": False,
        },
    }
    manifest_path = output / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "query_count": args.query_count,
        "minimum_reconstructed_barycentric_weight": minimum,
        "minimum_exit_triangle_barycentric_weight": exit_minimum,
        "rejected_candidate_count": rejected_candidate_count,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
