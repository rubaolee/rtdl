"""Pinned complete-output contract for the public-PyOptiX DBSCAN arm."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .dbscan_owner import PublicPyOptixDbscanOwner


MEMBER_SHA256 = {
    "points_f32.npy": (
        "59fb61b317fcf80ec54a0eb3829956ba9c9220fe7c9a6f9c9180d56a3b567d27"),
    "neighbor_counts_u32.npy": (
        "d3987e1e57b77fc0e8a842333d91660b68386b5ae1c4022e541d535da8ee575d"),
    "core_flags_u8.npy": (
        "922f9df37cf064e34bc4fbc343c8dbda834c1c5d29a0425b8863f9369c191d47"),
    "canonical_component_labels_i32.npy": (
        "e27028d9ba0c751069dbd194a902dc7ef64d6616a2dbc8c2f45bbbdbb505ee53"),
}
CONTRACT = {
    "boundary_assignment": "lowest_component_root",
    "closed_radius": True,
    "dimension": 3,
    "distance_arithmetic": "float32_sub_mul_add_add",
    "epsilon": 0.055,
    "min_points": 12,
    "point_count": 4096,
    "self_neighbor_included": True,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_input(root: str | Path) -> dict[str, object]:
    root = Path(root).resolve(strict=True)
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.rtdbscan_real_scale_input.v1" \
            or manifest.get("contract") != CONTRACT:
        raise ValueError("input is not the fixed 4096-point DBSCAN contract")
    arrays: dict[str, np.ndarray] = {}
    for name, expected_sha256 in MEMBER_SHA256.items():
        path = root / name
        specification = manifest["members"][name]
        if _sha256(path) != expected_sha256 \
                or specification["sha256"] != expected_sha256 \
                or path.stat().st_size != specification["bytes"]:
            raise ValueError(f"pinned DBSCAN member mismatch: {name}")
        value = np.load(path, allow_pickle=False)
        if str(value.dtype) != specification["dtype"] \
                or list(value.shape) != specification["shape"]:
            raise ValueError(f"DBSCAN member shape/dtype mismatch: {name}")
        arrays[name] = np.ascontiguousarray(value)
    points = arrays["points_f32.npy"]
    if points.shape != (4096, 3) or not np.isfinite(points).all():
        raise ValueError("DBSCAN point array violates its frozen contract")
    counts = arrays["neighbor_counts_u32.npy"]
    core = arrays["core_flags_u8.npy"]
    if not np.array_equal(core, (counts >= CONTRACT["min_points"]).astype(np.uint8)):
        raise ValueError("independent count/core oracle files disagree")
    expected = {
        "canonical_component_labels": tuple(map(
            int, arrays["canonical_component_labels_i32.npy"])),
        "core_flags": tuple(bool(value) for value in core),
        "neighbor_counts": tuple(map(int, counts)),
    }
    return {
        "points": points,
        "epsilon": CONTRACT["epsilon"],
        "min_points": CONTRACT["min_points"],
        "expected": expected,
        "manifest_sha256": _sha256(manifest_path),
        "input_identity": "pinned_synthetic_clustered3d_4096__not_paper_data",
    }


def compare_output(
    actual: object, expected: dict[str, tuple[object, ...]],
) -> dict[str, object]:
    if not isinstance(actual, dict) or set(actual) != set(expected):
        return {
            "matched": False,
            "reason": "all three exact DBSCAN output columns are required",
        }
    differences: dict[str, object] = {}
    for name in sorted(expected):
        observed = tuple(actual[name])
        wanted = expected[name]
        if observed != wanted:
            differences[name] = {
                "actual_count": len(observed),
                "expected_count": len(wanted),
                "first_differing_indices": [
                    index for index, (left, right) in enumerate(
                        zip(observed, wanted, strict=False)) if left != right
                ][:32],
            }
    return {
        "matched": not differences,
        "differences": differences,
        "point_count": len(expected["neighbor_counts"]),
        "directed_edge_count": sum(expected["neighbor_counts"]),
    }


def prepare_owner(
    data: dict[str, object],
    *,
    device_ptx_path: str | Path,
    continuation_ptx_path: str | Path,
) -> PublicPyOptixDbscanOwner:
    device_ptx_path = Path(device_ptx_path).resolve(strict=True)
    return PublicPyOptixDbscanOwner.prepare(
        points=data["points"],
        epsilon=data["epsilon"],
        min_points=data["min_points"],
        device_ptx=device_ptx_path.read_bytes(),
        continuation_ptx=Path(continuation_ptx_path).resolve(strict=True),
    )


__all__ = [
    "CONTRACT", "MEMBER_SHA256", "compare_output", "load_input",
    "prepare_owner",
]
