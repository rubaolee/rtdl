#!/usr/bin/env python3
"""Independently rederive the Goal5814 full-mesh Particle Tracking oracle.

The verifier imports neither RTDL nor PyOptiX.  It parses the pinned public VTU,
rebuilds the complete tetrahedral shared-face topology using an orientation-
parity implementation distinct from the producer, reconstructs the 5,000
deterministic strict-interior queries, and independently computes every exact
``(selected_cell, neighbor_cell, exit_face)`` row before comparing the frozen
NumPy product.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


POLICY_SHA256 = (
    "79f0d56f8765894666eaaec363f7e149c92de68e85d35ce43d3aa765132e625e"
)
DURABLE_SCHEMA = "rtdl.goal5814.particle_tracking_durable_scientific_input.v1"
UPSTREAM_MANIFEST_SHA256 = (
    "7f21844610c4c9ad8ccdf6ec6961de28d6f1099af8b1bf0e37e41bf53fb55743"
)
AUTHOR_VTU_SHA256 = (
    "b6be6c692256e73ea9f93d71dc81ad99478b49ec3866a9ab0109da35f72c57b8"
)
EXPECTED_NPY_SHA256 = (
    "84535828b61be745df5cdc1faee5c343b810df504b8f57404921c1d2d8b9130d"
)
EXPECTED_ARRAY_DOMAIN_SHA256 = (
    "7302ef33da0a88960b1b98d1c5377b6b5931340e5aeae123b2f9712cc0f6acc9"
)
U32_MAX = np.uint32(0xFFFFFFFF)
QUERY_COUNT = 5_000
SEED_LO = np.asarray(
    (73.9 + 1.0e-5, -0.4 + 1.0e-5, -655.95 + 1.0e-5),
    dtype=np.float64)
SEED_HI = np.asarray(
    (77.7 - 1.0e-5, 0.0 - 1.0e-5, -655.45 - 1.0e-5),
    dtype=np.float64)
FROZEN_DIRECTION_F32 = np.asarray(
    (1.0, 1.0e-10, 1.0e-10), dtype=np.float32)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _array_domain_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(
        list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def _canonical_json_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _require_file(path: Path, *, size: int, sha256: str) -> None:
    if not path.is_file() or path.stat().st_size != size or _sha256(path) != sha256:
        raise RuntimeError({
            "scientific_input_member_invalid": str(path),
            "expected_bytes": size,
            "expected_sha256": sha256,
        })


def _load_custody(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = root / "SCIENTIFIC_INPUT_MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    durable = json.loads(manifest_path.read_text(encoding="utf-8"))
    if durable.get("schema") != DURABLE_SCHEMA \
            or durable.get("superseded_goal5776_v1_accepted") is not False \
            or durable.get("temporary_source_root_required_after_materialization") is not False:
        raise RuntimeError("durable Goal5814 custody declaration differs")
    policy = durable.get("controlling_policy", {})
    if policy.get("sha256") != POLICY_SHA256:
        raise RuntimeError("Goal5814 controlling policy identity differs")
    payloads = durable.get("payloads")
    if not isinstance(payloads, list) or len(payloads) != 9:
        raise RuntimeError("durable Goal5814 payload set differs")
    names: set[str] = set()
    for row in payloads:
        name = str(row["name"])
        if name in names or Path(name).name != name:
            raise RuntimeError("durable Goal5814 payload name is unsafe or duplicate")
        names.add(name)
        _require_file(
            root / name, size=int(row["bytes"]), sha256=str(row["sha256"]))
    required = {
        "GOAL5776_MANIFEST.json", "solution_4.vtu", "vertices_f32.npy",
        "triangles_u32.npy", "front_values_u32.npy", "back_values_u32.npy",
        "queries_f32.npy", "expected_u32.npy", "query_cells_u32.npy",
    }
    if names != required:
        raise RuntimeError("durable Goal5814 payload name set differs")
    upstream_path = root / "GOAL5776_MANIFEST.json"
    if _sha256(upstream_path) != UPSTREAM_MANIFEST_SHA256:
        raise RuntimeError("controlling Goal5776 v2 manifest identity differs")
    upstream = json.loads(upstream_path.read_text(encoding="utf-8"))
    if upstream.get("schema") != "rtdl.goal5776.particle_real_scale_input.v1" \
            or upstream.get("source", {}).get("sha256") != AUTHOR_VTU_SHA256:
        raise RuntimeError("controlling Goal5776 v2 manifest content differs")
    return durable, upstream


def _read_vtu(path: Path) -> tuple[np.ndarray, np.ndarray, str]:
    # meshio is an offline file-format dependency, not an execution route.
    # It is imported only after custody has pinned the exact VTU bytes.
    import meshio  # type: ignore

    mesh = meshio.read(path)
    tetra_blocks = [block.data for block in mesh.cells if block.type == "tetra"]
    other_nonempty = [
        (block.type, tuple(block.data.shape)) for block in mesh.cells
        if block.type != "tetra" and len(block.data)
    ]
    if len(tetra_blocks) != 1 or other_nonempty:
        raise RuntimeError({
            "tetra_block_count": len(tetra_blocks),
            "other_nonempty_cell_blocks": other_nonempty,
        })
    points = np.asarray(mesh.points)
    cells = np.asarray(tetra_blocks[0])
    if points.shape != (314_587, 3) or cells.shape != (1_659_240, 4):
        raise RuntimeError({
            "unexpected_points_shape": list(points.shape),
            "unexpected_tetra_shape": list(cells.shape),
        })
    return points, cells, str(getattr(meshio, "__version__", "UNKNOWN"))


def _orient_cells(vertices_f32: np.ndarray, cells: np.ndarray) -> tuple[np.ndarray, int]:
    oriented = np.ascontiguousarray(cells, dtype=np.uint32).copy()
    if oriented.min(initial=0) < 0 or oriented.max(initial=0) >= len(vertices_f32):
        raise RuntimeError("VTU tetra index is outside the point domain")
    sorted_vertices = np.sort(oriented, axis=1)
    if np.any(sorted_vertices[:, 1:] == sorted_vertices[:, :-1]):
        raise RuntimeError("VTU tetra repeats a point index")
    a = vertices_f32[oriented[:, 0]]
    b = vertices_f32[oriented[:, 1]]
    c = vertices_f32[oriented[:, 2]]
    d = vertices_f32[oriented[:, 3]]
    signed_six_volume = np.einsum(
        "ij,ij->i", d - a, np.cross(b - a, c - a))
    if np.any(signed_six_volume == np.float32(0.0)):
        raise RuntimeError("VTU contains a tetra degenerate in consumed f32")
    negative = signed_six_volume < np.float32(0.0)
    negative_count = int(np.count_nonzero(negative))
    temporary = oriented[negative, 0].copy()
    oriented[negative, 0] = oriented[negative, 1]
    oriented[negative, 1] = temporary
    return oriented, negative_count


def _rederive_topology(
    oriented: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, int]]:
    """Build lexicographic faces using inversion parity, not producer swaps."""

    tetra_count = len(oriented)
    incidences = np.empty((tetra_count * 4, 3), dtype=np.uint32)
    incidences[0 * tetra_count:1 * tetra_count] = oriented[:, (1, 2, 3)]
    incidences[1 * tetra_count:2 * tetra_count] = oriented[:, (2, 0, 3)]
    incidences[2 * tetra_count:3 * tetra_count] = oriented[:, (0, 1, 3)]
    incidences[3 * tetra_count:4 * tetra_count] = oriented[:, (0, 2, 1)]
    owners = np.tile(np.arange(tetra_count, dtype=np.uint32), 4)

    inversion_count = (
        (incidences[:, 0] > incidences[:, 1]).astype(np.uint8)
        + (incidences[:, 0] > incidences[:, 2]).astype(np.uint8)
        + (incidences[:, 1] > incidences[:, 2]).astype(np.uint8)
    )
    front_incidence = (inversion_count & np.uint8(1)).astype(bool)
    canonical = np.sort(incidences, axis=1)
    unique_faces, inverse, counts = np.unique(
        canonical, axis=0, return_inverse=True, return_counts=True)
    del canonical, incidences, inversion_count
    if np.any((counts < 1) | (counts > 2)):
        raise RuntimeError("VTU shared-face topology is non-manifold")

    face_count = len(unique_faces)
    front_count = np.bincount(
        inverse[front_incidence], minlength=face_count)
    back_count = np.bincount(
        inverse[~front_incidence], minlength=face_count)
    if np.any(front_count > 1) or np.any(back_count > 1) \
            or not np.array_equal(front_count + back_count, counts):
        raise RuntimeError("VTU face orientation does not define two-sided ownership")

    front = np.full(face_count, U32_MAX, dtype=np.uint32)
    back = np.full(face_count, U32_MAX, dtype=np.uint32)
    front[inverse[front_incidence]] = owners[front_incidence]
    back[inverse[~front_incidence]] = owners[~front_incidence]
    if np.any((front != U32_MAX) & (back != U32_MAX) & (front == back)):
        raise RuntimeError("VTU shared face has identical owners")
    cell_faces = inverse.reshape(4, tetra_count).T.astype(np.uint32, copy=False)
    summary = {
        "face_incidence_count": int(len(inverse)),
        "unique_face_count": int(face_count),
        "boundary_face_count": int(np.count_nonzero(counts == 1)),
        "shared_face_count": int(np.count_nonzero(counts == 2)),
        "front_owned_face_count": int(np.count_nonzero(front != U32_MAX)),
        "back_owned_face_count": int(np.count_nonzero(back != U32_MAX)),
    }
    return unique_faces, front, back, cell_faces, summary


def _maximum_edge_f32(vertices: np.ndarray, cells: np.ndarray) -> np.float32:
    maximum = np.float32(0.0)
    for left, right in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        delta = vertices[cells[:, left]] - vertices[cells[:, right]]
        squared = np.einsum("ij,ij->i", delta, delta)
        maximum = max(maximum, np.float32(np.sqrt(squared).max(initial=0.0)))
    if not np.isfinite(maximum) or maximum <= 0:
        raise RuntimeError("VTU maximum f32 edge length is invalid")
    return maximum


def _reconstruct_query_cells_and_bytes(
    vertices_f64: np.ndarray,
    oriented: np.ndarray,
    queries: np.ndarray,
    query_cells: np.ndarray,
    tmax_f32: np.float32,
) -> tuple[np.ndarray, dict[str, object]]:
    centroids = vertices_f64[oriented].mean(axis=1)
    eligible = np.flatnonzero(np.all(
        (centroids >= SEED_LO) & (centroids <= SEED_HI), axis=1))
    if len(eligible) != 3_636:
        raise RuntimeError(f"eligible tetra count differs: {len(eligible)}")
    chosen = np.resize(eligible, QUERY_COUNT).astype(np.uint32)
    if not np.array_equal(chosen, query_cells):
        raise RuntimeError("query_cells payload is not rederived from pinned VTU")

    local_repeat = np.arange(QUERY_COUNT) // len(eligible)
    weights = np.full((QUERY_COUNT, 4), 0.2, dtype=np.float64)
    weights[np.arange(QUERY_COUNT), local_repeat % 4] = 0.4
    reconstructed_origins = np.einsum(
        "ij,ijk->ik", weights, vertices_f64[oriented[chosen]])
    reconstructed_origins_f32 = np.ascontiguousarray(
        reconstructed_origins, dtype=np.float32)
    if not np.array_equal(reconstructed_origins_f32, queries[:, :3]):
        mismatch = np.argwhere(reconstructed_origins_f32 != queries[:, :3])[0]
        raise RuntimeError({
            "query_origin_bytes_not_reconstructed": [
                int(mismatch[0]), int(mismatch[1])],
        })
    if not np.array_equal(
            queries[:, 3:6], np.broadcast_to(FROZEN_DIRECTION_F32, (QUERY_COUNT, 3))):
        raise RuntimeError("query direction bytes differ")
    if not np.array_equal(
            queries[:, 6], np.full(QUERY_COUNT, tmax_f32, dtype=np.float32)):
        raise RuntimeError("query tmax bytes differ")
    return chosen, {
        "eligible_tetra_count": int(len(eligible)),
        "reconstructed_query_origin_count": QUERY_COUNT,
        "minimum_declared_convex_weight": 0.2,
        "maximum_declared_convex_weight": 0.4,
        "direction_f32": [float(value) for value in FROZEN_DIRECTION_F32],
        "tmax_f32": float(tmax_f32),
    }


def _rederive_expected(
    vertices_f64: np.ndarray,
    triangles: np.ndarray,
    front: np.ndarray,
    back: np.ndarray,
    cell_faces: np.ndarray,
    chosen: np.ndarray,
    queries: np.ndarray,
) -> tuple[np.ndarray, dict[str, object]]:
    face_ids = cell_faces[chosen]
    candidate_triangles = triangles[face_ids]
    a = vertices_f64[candidate_triangles[:, :, 0]]
    b = vertices_f64[candidate_triangles[:, :, 1]]
    c = vertices_f64[candidate_triangles[:, :, 2]]
    normals = np.cross(b - a, c - a)
    directions = queries[:, 3:6].astype(np.float64)
    origins = queries[:, :3].astype(np.float64)
    denominator = np.einsum("qfi,qi->qf", normals, directions)
    numerator = np.einsum("qfi,qfi->qf", normals, a - origins[:, None, :])
    distance = np.divide(
        numerator, denominator,
        out=np.full_like(numerator, np.inf), where=denominator != 0.0)
    distance[distance <= 0.0] = np.inf
    exit_slot = np.argmin(distance, axis=1)
    row = np.arange(QUERY_COUNT)
    exit_distance = distance[row, exit_slot]
    if not np.all(np.isfinite(exit_distance)) \
            or np.any(exit_distance > queries[:, 6].astype(np.float64)):
        raise RuntimeError("a reconstructed query lacks an in-range positive exit")
    exit_face = face_ids[row, exit_slot]
    exit_denominator = denominator[row, exit_slot]
    selected = np.where(exit_denominator < 0.0, front[exit_face], back[exit_face])
    neighbor = np.where(exit_denominator < 0.0, back[exit_face], front[exit_face])
    if not np.array_equal(selected.astype(np.uint32), chosen):
        mismatch = int(np.flatnonzero(selected.astype(np.uint32) != chosen)[0])
        raise RuntimeError({
            "selected_cell_not_rederived": mismatch,
            "expected_from_query_construction": int(chosen[mismatch]),
            "observed_from_face_orientation": int(selected[mismatch]),
        })

    # A strict face-interior check rules out an edge/vertex-tie explanation.
    exit_triangles = triangles[exit_face]
    ta = vertices_f64[exit_triangles[:, 0]]
    tb = vertices_f64[exit_triangles[:, 1]]
    tc = vertices_f64[exit_triangles[:, 2]]
    hit = origins + exit_distance[:, None] * directions
    v0 = tb - ta
    v1 = tc - ta
    v2 = hit - ta
    d00 = np.einsum("ij,ij->i", v0, v0)
    d01 = np.einsum("ij,ij->i", v0, v1)
    d11 = np.einsum("ij,ij->i", v1, v1)
    d20 = np.einsum("ij,ij->i", v2, v0)
    d21 = np.einsum("ij,ij->i", v2, v1)
    bary_denominator = d00 * d11 - d01 * d01
    bary_v = (d11 * d20 - d01 * d21) / bary_denominator
    bary_w = (d00 * d21 - d01 * d20) / bary_denominator
    bary_u = 1.0 - bary_v - bary_w
    minimum_face_barycentric = float(np.min(np.column_stack(
        (bary_u, bary_v, bary_w))))
    if not np.isfinite(minimum_face_barycentric) or minimum_face_barycentric <= 0.0:
        raise RuntimeError({
            "edge_or_vertex_tie_detected": True,
            "minimum_exit_face_barycentric": minimum_face_barycentric,
        })

    expected = np.column_stack((selected, neighbor, exit_face)).astype(np.uint32)
    return expected, {
        "positive_finite_exit_count": int(np.count_nonzero(
            np.isfinite(exit_distance) & (exit_distance > 0.0))),
        "minimum_exit_distance": float(exit_distance.min()),
        "maximum_exit_distance": float(exit_distance.max()),
        "minimum_exit_face_barycentric": minimum_face_barycentric,
        "edge_or_vertex_tie_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.input_root.resolve()
    output_path = args.output.resolve()
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(output_path)

    durable, upstream = _load_custody(root)
    points, raw_cells, meshio_version = _read_vtu(root / "solution_4.vtu")
    forbidden_loaded = sorted(
        name for name in sys.modules
        if name == "rtdsl" or name.startswith("rtdsl.")
        or name == "optix" or name.startswith("optix.")
        or name == "pyoptix" or name.startswith("pyoptix."))
    if forbidden_loaded:
        raise RuntimeError({"forbidden_execution_modules_loaded": forbidden_loaded})

    vertices = np.ascontiguousarray(points, dtype=np.float32)
    frozen_vertices = np.load(root / "vertices_f32.npy", allow_pickle=False, mmap_mode="r")
    if not np.array_equal(vertices, frozen_vertices):
        raise RuntimeError("vertices_f32.npy does not derive from pinned VTU")
    oriented, negative_orientation_count = _orient_cells(vertices, raw_cells)
    triangles, front, back, cell_faces, topology = _rederive_topology(oriented)
    frozen_triangles = np.load(
        root / "triangles_u32.npy", allow_pickle=False, mmap_mode="r")
    frozen_front = np.load(
        root / "front_values_u32.npy", allow_pickle=False, mmap_mode="r")
    frozen_back = np.load(
        root / "back_values_u32.npy", allow_pickle=False, mmap_mode="r")
    if not np.array_equal(triangles, frozen_triangles) \
            or not np.array_equal(front, frozen_front) \
            or not np.array_equal(back, frozen_back):
        raise RuntimeError("frozen face topology does not derive from pinned VTU")

    queries = np.load(root / "queries_f32.npy", allow_pickle=False)
    query_cells = np.load(root / "query_cells_u32.npy", allow_pickle=False)
    frozen_expected = np.load(root / "expected_u32.npy", allow_pickle=False)
    if queries.shape != (QUERY_COUNT, 7) or queries.dtype != np.dtype("float32") \
            or query_cells.shape != (QUERY_COUNT,) \
            or query_cells.dtype != np.dtype("uint32") \
            or frozen_expected.shape != (QUERY_COUNT, 3) \
            or frozen_expected.dtype != np.dtype("uint32"):
        raise RuntimeError("frozen query/oracle array schema differs")
    if _sha256(root / "expected_u32.npy") != EXPECTED_NPY_SHA256:
        raise RuntimeError("frozen expected NumPy bytes differ")

    tmax_f32 = _maximum_edge_f32(vertices, oriented)
    vertices_f64 = vertices.astype(np.float64)
    chosen, query_summary = _reconstruct_query_cells_and_bytes(
        vertices_f64, oriented, queries, query_cells, tmax_f32)
    rederived, geometric_summary = _rederive_expected(
        vertices_f64, triangles, front, back, cell_faces,
        chosen, queries)
    if not np.array_equal(rederived, frozen_expected):
        mismatches = np.flatnonzero(np.any(rederived != frozen_expected, axis=1))
        first = int(mismatches[0])
        raise RuntimeError({
            "oracle_mismatch_count": int(len(mismatches)),
            "first_oracle_mismatch": first,
            "rederived": [int(value) for value in rederived[first]],
            "frozen": [int(value) for value in frozen_expected[first]],
        })
    array_digest = _array_domain_sha256(rederived)
    if array_digest != EXPECTED_ARRAY_DOMAIN_SHA256:
        raise RuntimeError("rederived expected array-domain digest differs")

    result = {
        "schema": "rtdl.goal5814.particle_tracking_independent_oracle_result.v1",
        "status": "PASS__ALL_5000_ROWS_INDEPENDENTLY_REDERIVED",
        "controlling_policy_sha256": POLICY_SHA256,
        "durable_manifest_sha256": _sha256(
            root / "SCIENTIFIC_INPUT_MANIFEST.json"),
        "goal5776_v2_manifest_sha256": _sha256(
            root / "GOAL5776_MANIFEST.json"),
        "author_vtu_sha256": _sha256(root / "solution_4.vtu"),
        "verifier_source_sha256": _sha256(Path(__file__).resolve()),
        "dependencies": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "meshio": meshio_version,
            "rtdl_imported": False,
            "optix_or_pyoptix_imported": False,
        },
        "custody": {
            "durable_payload_count": int(durable["payload_count"]),
            "durable_payload_bytes": int(durable["payload_bytes"]),
            "superseded_goal5776_v1_accepted": False,
            "temporary_root_used": False,
            "expected_npy_bytes": int((root / "expected_u32.npy").stat().st_size),
            "expected_npy_sha256": EXPECTED_NPY_SHA256,
        },
        "mesh": {
            "vertex_count": int(len(vertices)),
            "tetrahedron_count": int(len(oriented)),
            "negative_tetra_orientation_repairs": negative_orientation_count,
            **topology,
        },
        "queries": query_summary,
        "geometry": geometric_summary,
        "oracle": {
            "row_count": int(len(rederived)),
            "column_order": ["selected_cell", "neighbor_cell", "exit_face"],
            "exact_row_match_count": int(np.count_nonzero(
                np.all(rederived == frozen_expected, axis=1))),
            "mismatch_count": 0,
            "unique_selected_cell_count": int(len(np.unique(rederived[:, 0]))),
            "unique_neighbor_cell_count": int(len(np.unique(rederived[:, 1]))),
            "unique_exit_face_count": int(len(np.unique(rederived[:, 2]))),
            "boundary_neighbor_row_count": int(np.count_nonzero(
                rederived[:, 1] == U32_MAX)),
            "selected_cell_equals_rederived_query_cell_count": int(
                np.count_nonzero(rederived[:, 0] == chosen)),
            "first_five_rows": [
                [int(value) for value in row] for row in rederived[:5]],
            "array_digest_framing": "dtype_ascii || compact_shape_json || raw_c_bytes",
            "array_domain_sha256": array_digest,
            "canonical_json_rows_sha256": _canonical_json_sha256(
                rederived.tolist()),
        },
        "method": {
            "product_or_execution_route_imported": False,
            "precomputed_matched_flag_read": False,
            "topology_rederived_from_pinned_vtu": True,
            "face_orientation_method": "INVERSION_PARITY_NOT_PRODUCER_SWAP_SEQUENCE",
            "all_5000_rows_rederived": True,
            "frozen_expected_used_only_after_rederivation": True,
        },
        "claim_boundary": {
            "scientific_input_and_oracle_prerequisite_closed": True,
            "executable_bytes_frozen": False,
            "performance_worker_authorized": False,
            "generalization_exam": False,
        },
        "upstream_claim_boundary": upstream["claim_boundary"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({
        "status": result["status"],
        "result_path": str(output_path),
        "result_bytes": output_path.stat().st_size,
        "result_sha256": _sha256(output_path),
        "oracle_rows": result["oracle"]["row_count"],
        "oracle_sha256": result["oracle"]["array_domain_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
