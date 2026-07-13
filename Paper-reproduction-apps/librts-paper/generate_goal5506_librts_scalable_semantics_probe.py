from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
APP = Path(__file__).resolve().parent
SOURCE_SCRIPT = APP / "run_goal5504_librts_range_intersects_semantics_fixtures.py"
SPEC = importlib.util.spec_from_file_location("goal5504_semantics", SOURCE_SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _wkt(box: np.ndarray) -> str:
    min_x, min_y, max_x, max_y = (repr(float(value)) for value in box)
    return f"POLYGON(({min_x} {min_y},{max_x} {min_y},{max_x} {max_y},{min_x} {max_y},{min_x} {min_y}))"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rng = np.random.default_rng(5506)
    boxes_min = rng.uniform(-100.0, 100.0, size=(128, 2)).astype(np.float32)
    boxes_size = rng.uniform(0.1, 10.0, size=(128, 2)).astype(np.float32)
    boxes_max = (boxes_min + boxes_size).astype(np.float32)
    queries_min = rng.uniform(-100.0, 100.0, size=(64, 2)).astype(np.float32)
    queries_size = rng.uniform(0.1, 10.0, size=(64, 2)).astype(np.float32)
    queries_max = (queries_min + queries_size).astype(np.float32)

    # Force a stable mix of ordinary, touching, ULP-gap, and corner cases.
    queries_min[0] = boxes_min[0]
    queries_max[0] = boxes_max[0]
    queries_min[1] = (boxes_max[1, 0], boxes_min[1, 1])
    queries_max[1] = (boxes_max[1, 0] + 2.0, boxes_max[1, 1])
    queries_min[2] = (
        np.nextafter(boxes_max[2, 0], np.float32(np.inf)),
        boxes_min[2, 1],
    )
    queries_max[2] = (queries_min[2, 0] + 2.0, boxes_max[2, 1])
    queries_min[3] = boxes_max[3]
    queries_max[3] = boxes_max[3] + np.float32(2.0)

    boxes = np.concatenate((boxes_min, boxes_max), axis=1)
    queries = np.concatenate((queries_min, queries_max), axis=1)
    cpu_count = 0
    source_count = 0
    for box in boxes:
        for query in queries:
            cpu_count += int(MODULE.cpu_inclusive_intersects(tuple(box), tuple(query)))
            source_count += int(MODULE.author_gpu_style_intersects(tuple(box), tuple(query)))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    geometry_path = args.output_dir / "goal5506_geometry.wkt"
    query_path = args.output_dir / "goal5506_queries.wkt"
    geometry_path.write_text("\n".join(_wkt(box) for box in boxes) + "\n", encoding="utf-8")
    query_path.write_text("\n".join(_wkt(query) for query in queries) + "\n", encoding="utf-8")
    oracle = {
        "schema": "rtdl.paper_reproduction.librts.goal5506_scalable_semantics_oracle.v1",
        "status": "deterministic_scalable_probe_generated",
        "seed": 5506,
        "geometry_count": int(len(boxes)),
        "query_count": int(len(queries)),
        "pair_count": int(len(boxes) * len(queries)),
        "cpu_inclusive_count": int(cpu_count),
        "source_rayparams_model_count": int(source_count),
        "boundary_cases": ["exact_box", "shared_edge", "one_ulp_gap", "shared_corner"],
        "geometry_path": str(geometry_path),
        "query_path": str(query_path),
        "claim_boundary": {
            "author_gpu_runtime_executed": False,
            "rtdl_runtime_executed": False,
            "full_input_adjudication": False,
            "rtdl_core_change_authorized": False,
            "performance_ratio_authorized": False,
        },
    }
    (args.output_dir / "goal5506_scalable_semantics_oracle.json").write_text(
        json.dumps(oracle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(oracle, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
