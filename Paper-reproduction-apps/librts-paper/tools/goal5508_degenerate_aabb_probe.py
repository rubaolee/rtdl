from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

REMOTE_ROOT = Path("/workspace/rtdl-goal5481")
ROOT = (
    REMOTE_ROOT
    if (REMOTE_ROOT / "src" / "rtdsl").is_dir()
    else next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "src" / "rtdsl").is_dir()
    )
)
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "librts-paper"))

import rtdsl as rt
from run_exact_point_contains_count_gate import load_geometry_mbr_columns


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_box_wkts(path: Path, values: np.ndarray) -> None:
    with path.open("w", encoding="utf-8") as output:
        for min_x, min_y, max_x, max_y in values:
            output.write(
                "POLYGON (("
                f"{float(min_x):.9g} {float(min_y):.9g}, "
                f"{float(max_x):.9g} {float(min_y):.9g}, "
                f"{float(max_x):.9g} {float(max_y):.9g}, "
                f"{float(min_x):.9g} {float(max_y):.9g}, "
                f"{float(min_x):.9g} {float(min_y):.9g}))\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("geometry", type=Path)
    parser.add_argument("query", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("subset_wkt", type=Path)
    args = parser.parse_args()

    geometry = load_geometry_mbr_columns(args.geometry)
    query = load_geometry_mbr_columns(args.query)
    values = np.stack(
        (geometry.min_x, geometry.min_y, geometry.max_x, geometry.max_y), axis=1
    ).astype(np.float32)
    invalid_after_float32 = (values[:, 0] >= values[:, 2]) | (values[:, 1] >= values[:, 3])
    indices = np.flatnonzero(invalid_after_float32)
    subset = values[indices]
    _write_box_wkts(args.subset_wkt, subset)

    indexed = rt.Aabb2DColumns(
        ids=np.asarray(indices, dtype=np.uint32),
        min_x=subset[:, 0],
        min_y=subset[:, 1],
        max_x=subset[:, 2],
        max_y=subset[:, 3],
    )
    backend = os.environ.get("RTDL_OPTIX_LIB", "")
    prepared = rt.prepare_aabb_index_2d_columns(indexed, backend="optix")
    try:
        query_result = prepared.count(
            box_queries=query,
            operation="range_intersects",
        )
        rtdl_count = int(query_result["counts"]["range_intersects"])
    finally:
        prepared.close()

    result = {
        "schema": "rtdl.paper_reproduction.librts.goal5508_degenerate_aabb_probe.v1",
        "geometry_sha256": _sha256(args.geometry),
        "query_sha256": _sha256(args.query),
        "subset_wkt_sha256": _sha256(args.subset_wkt),
        "geometry_count": len(geometry),
        "query_count": len(query),
        "invalid_after_float32_count": int(indices.size),
        "invalid_geometry_indices": [int(value) for value in indices],
        "invalid_float32_boxes": subset.tolist(),
        "rtdl_count": rtdl_count,
        "rtdl_query_result": query_result,
        "rtdl_backend": "optix",
        "rtdl_library": backend,
        "same_input_files": True,
        "author_comparison_required": True,
        "claim_boundary": {
            "generic_semantic_diagnosis_only": True,
            "full_input_adjudication": False,
            "paper_reproduction_claimed": False,
            "performance_ratio_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
