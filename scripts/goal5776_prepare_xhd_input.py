"""Create the route-independent full Dragon -> HappyBuddha X-HD packet.

SciPy is used only as an over-inclusive candidate finder.  The frozen nearest
rows are selected again with the float32 arithmetic used by the RTDL contract.
This script imports neither the V2 nor the V4 execution route.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.spatial import cKDTree


DRAGON_SHA256 = "fea87ff48f2aba22fb53e7b67c3ff3f7b8c2a3b3a0653af62c48bba67c6d5744"
HAPPY_SHA256 = "2283371216d748a08376a3c88698e283cc8f18d10ced348d6d133051bcf217ab"
AUTHOR_HD_RESULT = 0.12572988867759705


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_input_helper(path: Path):
    spec = importlib.util.spec_from_file_location(
        "goal5776_xhd_input_format_only", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the app-owned X-HD input-format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _f32_distances(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    delta = np.subtract(candidates, query, dtype=np.float32)
    squared = np.multiply(delta, delta, dtype=np.float32)
    return np.add(
        np.add(squared[:, 0], squared[:, 1], dtype=np.float32),
        squared[:, 2],
        dtype=np.float32,
    )


def _derive_exact_rows(
    sources: np.ndarray,
    targets: np.ndarray,
    *,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Find an over-inclusive neighborhood, then choose in exact f32 order."""

    tree = cKDTree(np.asarray(targets, dtype=np.float64), compact_nodes=True)
    double_distance, _ = tree.query(
        np.asarray(sources, dtype=np.float64), k=1, workers=1)
    if not bool(np.isfinite(double_distance).all()):
        raise RuntimeError("KD candidate finder returned a nonfinite distance")

    candidate_ids = np.empty(sources.shape[0], dtype=np.uint32)
    distance_sq = np.empty(sources.shape[0], dtype=np.float32)
    # Input coordinates are float32 and translated into a sub-unit domain.
    # This bound is deliberately much wider than the maximum accumulated f32
    # subtraction/multiply/add rounding error, while remaining a tiny spatial
    # neighborhood for these meshes.
    error_radius = np.float64(2.0e-6)
    for start in range(0, sources.shape[0], batch_size):
        stop = min(start + batch_size, sources.shape[0])
        neighborhoods = tree.query_ball_point(
            np.asarray(sources[start:stop], dtype=np.float64),
            r=double_distance[start:stop] + error_radius,
            workers=1,
        )
        for offset, raw_ids in enumerate(neighborhoods):
            if not raw_ids:
                raise RuntimeError(f"empty candidate neighborhood at query {start + offset}")
            ids = np.asarray(raw_ids, dtype=np.int64)
            values = _f32_distances(sources[start + offset], targets[ids])
            minimum = np.min(values)
            tied = ids[values == minimum]
            winner = int(np.min(tied))
            candidate_ids[start + offset] = winner
            distance_sq[start + offset] = minimum
        if stop == sources.shape[0] or stop % (16 * batch_size) == 0:
            print(f"exact-f32-nearest {stop}/{sources.shape[0]}", flush=True)
    return candidate_ids, distance_sq


def _member(path: Path, value: np.ndarray) -> dict[str, object]:
    np.save(path, np.ascontiguousarray(value), allow_pickle=False)
    return {
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "dtype": str(value.dtype),
        "shape": list(value.shape),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dragon", type=Path, required=True)
    parser.add_argument("--happy", type=Path, required=True)
    parser.add_argument("--input-helper", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=8192)
    args = parser.parse_args()
    if args.output_root.exists():
        raise FileExistsError(f"create-only output already exists: {args.output_root}")
    if args.batch_size <= 0:
        raise ValueError("batch-size must be positive")
    for path, expected in (
        (args.dragon, DRAGON_SHA256), (args.happy, HAPPY_SHA256)
    ):
        actual = _sha256(path)
        if actual != expected:
            raise RuntimeError(f"frozen X-HD source mismatch: {path}: {actual}")

    helper = _load_input_helper(args.input_helper.resolve())
    sources = helper.load_ply_vertex_matrix(args.dragon, n_dims=3)
    targets = helper.load_ply_vertex_matrix(args.happy, n_dims=3)
    sources = helper.translate_point_matrix_to_min_bound(sources, copy=False)
    targets = helper.translate_point_matrix_to_min_bound(targets, copy=False)
    sources = np.ascontiguousarray(sources, dtype=np.float32)
    targets = np.ascontiguousarray(targets, dtype=np.float32)
    if sources.shape != (437_645, 3) or targets.shape != (543_652, 3):
        raise RuntimeError(
            f"unexpected X-HD matrix shapes: {sources.shape}, {targets.shape}")

    nearest_ids, nearest_d2 = _derive_exact_rows(
        sources, targets, batch_size=args.batch_size)
    maximum = np.max(nearest_d2)
    source_ties = np.flatnonzero(nearest_d2 == maximum)
    source_id = int(source_ties[0])
    target_id = int(nearest_ids[source_id])
    value = math.sqrt(float(maximum))
    if abs(value - AUTHOR_HD_RESULT) > 1.0e-6:
        raise RuntimeError(
            f"route-independent oracle disagrees with author HDResult: {value}")

    args.output_root.mkdir(parents=True, exist_ok=False)
    query_ids = np.arange(sources.shape[0], dtype=np.uint32)
    ranks = np.ones(sources.shape[0], dtype=np.uint32)
    arrays = {
        "sources_f32.npy": sources,
        "targets_f32.npy": targets,
        "expected_query_u32.npy": query_ids,
        "expected_candidate_u32.npy": nearest_ids,
        "expected_rank_u32.npy": ranks,
        "expected_distance_sq_f32.npy": nearest_d2,
    }
    members = {
        name: _member(args.output_root / name, value)
        for name, value in arrays.items()
    }
    manifest = {
        "schema": "rtdl.goal5776.xhd_real_scale_input.v1",
        "source": {
            "dragon_sha256": DRAGON_SHA256,
            "happy_sha256": HAPPY_SHA256,
            "dragon_vertex_count": int(sources.shape[0]),
            "happy_vertex_count": int(targets.shape[0]),
            "provenance": "public Stanford Dragon -> HappyBuddha Level-B representative",
            "exact_paper_byte_identity_claimed": False,
        },
        "contract": {
            "direction": "dragon_to_happy",
            "preprocessing": "translate_each_input_to_min_bound_then_f32",
            "output": "exact_directed_global_max_of_nearest_witness",
            "initial_radius": 0.01,
            "maximum_distance": 0.32,
            "maximum_rounds": 6,
            "boundary_policy": "closed",
            "author_hd_result": AUTHOR_HD_RESULT,
            "oracle_value": value,
            "oracle_source_id": source_id,
            "oracle_target_id": target_id,
            "oracle_abs_diff_from_author": abs(value - AUTHOR_HD_RESULT),
            "candidate_finder": "scipy_ckdtree_overinclusive_radius",
            "candidate_adjudication": "explicit_float32_sub_mul_add_then_distance_id_order",
            "execution_route_imported": False,
        },
        "members": members,
    }
    manifest_path = args.output_root / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest_sha256": _sha256(manifest_path),
        "source_id": source_id,
        "target_id": target_id,
        "value": value,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
