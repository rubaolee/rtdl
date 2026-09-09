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


def _strict_barycentric_weights(indices: np.ndarray) -> np.ndarray:
    weights = np.empty((len(indices), 4), dtype=np.float64)
    weights[:, 0] = 0.1 + 0.15 * _uniform53(
        indices, 0x243F6A8885A308D3)
    weights[:, 1] = 0.1 + 0.15 * _uniform53(
        indices, 0x13198A2E03707344)
    weights[:, 2] = 0.1 + 0.15 * _uniform53(
        indices, 0xA4093822299F31D0)
    weights[:, 3] = 1.0 - weights[:, :3].sum(axis=1)
    if np.any(weights <= 0.0) or not np.allclose(
            weights.sum(axis=1), 1.0, rtol=0.0, atol=2e-16):
        raise RuntimeError("strict barycentric generator failed")
    return weights


def _barycentric_minimum(
    cell_vertices: np.ndarray, origins: np.ndarray,
) -> float:
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
    return float(np.min(np.column_stack((l0, l1, l2, l3))))


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
    tmax: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    indices = np.arange(start, stop, dtype=np.uint64)
    chosen = eligible[(indices % np.uint64(len(eligible))).astype(np.int64)]
    weights = _strict_barycentric_weights(indices)
    cell_vertices = vertices[cells[chosen]]
    origins = np.einsum("ij,ijk->ik", weights, cell_vertices)
    origins_f32 = np.ascontiguousarray(origins, dtype=np.float32)
    oracle_origins = origins_f32.astype(np.float64)
    minimum = _barycentric_minimum(cell_vertices, oracle_origins)
    if minimum <= 0.0:
        raise RuntimeError("f32 Particle query is not strictly interior")

    face_ids = cell_faces[chosen]
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
    exit_distance = distance[np.arange(len(indices)), exit_slot]
    if not np.all(np.isfinite(exit_distance)):
        raise RuntimeError("strict-interior Particle query lacks an exit face")
    exit_face = face_ids[np.arange(len(indices)), exit_slot]
    exit_denominator = denominator[np.arange(len(indices)), exit_slot]
    selected = np.where(exit_denominator < 0.0, front[exit_face], back[exit_face])
    neighbor = np.where(exit_denominator < 0.0, back[exit_face], front[exit_face])
    if np.any(selected == U32_MAX) \
            or not np.array_equal(selected.astype(np.uint32), chosen):
        raise RuntimeError("Particle topology oracle rejected containing cell")

    queries = np.empty((len(indices), 7), dtype=np.float32)
    queries[:, :3] = origins_f32
    queries[:, 3:6] = AUTHOR_DIRECTION.astype(np.float32)
    queries[:, 6] = np.float32(tmax)
    expected = np.column_stack((selected, neighbor, exit_face)).astype(np.uint32)
    return queries, expected, chosen.astype(np.uint32), minimum


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
    for start in range(0, args.query_count, args.chunk_size):
        stop = min(start + args.chunk_size, args.query_count)
        chunk_queries, chunk_expected, chunk_cells, chunk_minimum = \
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
            "construction": "splitmix64_strict_barycentric_v1",
            "minimum_reconstructed_barycentric_weight": minimum,
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
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
