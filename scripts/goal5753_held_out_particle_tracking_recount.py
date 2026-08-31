#!/usr/bin/env python3
"""Independent standard-library recount of the Goal5753 held-out failure.

This file imports neither the primary exam nor RTDL.  It reconstructs the
selection binding, source facts, exact oracle and physical-schema mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


FAILURE_CODE = (
    "unsupported_physical_geometry_family__triangle_mesh_required__"
    "frozen_v4_sphere_only"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def det(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def sub(a, b):
    return tuple(a[index] - b[index] for index in range(3))


def matches(point, vertices, cells):
    found = []
    for cell_id, cell in enumerate(cells):
        a, b, c, d = (vertices[index] for index in cell)
        denominator = det(sub(a, d), sub(b, d), sub(c, d))
        weights = (
            det(sub(point, d), sub(b, d), sub(c, d)) / denominator,
            det(sub(a, d), sub(point, d), sub(c, d)) / denominator,
            det(sub(a, d), sub(b, d), sub(point, d)) / denominator,
        )
        weights += (Fraction(1) - sum(weights),)
        if all(value >= 0 for value in weights):
            found.append(cell_id)
    return tuple(found)


def extract_struct(text: str, name: str) -> str:
    matched = re.search(rf"struct\s+{re.escape(name)}\s*\{{(.*?)\}};", text, re.DOTALL)
    if matched is None:
        raise RuntimeError(f"missing struct: {name}")
    return matched.group(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--author-source", type=Path, required=True)
    parser.add_argument("--primary-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    author = args.author_source.resolve()
    primary = json.loads(args.primary_result.read_text(encoding="utf-8"))

    selection_path = workspace / "history/internal_docs/goal5753_held_out_selection_20260811.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected = selection["selection"]["selected_candidate"]["candidate_id"]
    if selected != "Wang2022AnGP::particle_tracking":
        raise RuntimeError("independent selection mismatch")
    if sha256_file(selection_path) != primary["selected_application"]["selection_sha256"]:
        raise RuntimeError("selection digest mismatch")

    author_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=author, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if author_commit != primary["author_source_audit"]["commit"]:
        raise RuntimeError("author commit mismatch")
    author_hashes = {}
    for relative, evidence in primary["author_source_audit"]["files"].items():
        actual = sha256_file(author / relative)
        if actual != evidence["sha256"]:
            raise RuntimeError(f"author file mismatch: {relative}")
        author_hashes[relative] = actual

    native_source = (workspace / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
        encoding="utf-8"
    )
    sphere = extract_struct(native_source, "V4CallbackSphere")
    params = extract_struct(native_source, "V4FormalParams")
    for token in ("float cx, cy, cz, radius", "uint32_t item_id"):
        if token not in sphere:
            raise RuntimeError(f"frozen sphere ABI token missing: {token}")
    for token in (
        "const V4CallbackSphere* spheres", "const float* query_x",
        "const float* query_y", "const float* query_z", "const float* query_tmax",
        "uint32_t* output_ids", "float* output_distance",
    ):
        if token not in params:
            raise RuntimeError(f"frozen formal parameter token missing: {token}")
    forbidden = ("vertex", "indices", "front_cell", "back_cell", "face_id", "hit_kind")
    if any(token in sphere.lower() or token in params.lower() for token in forbidden):
        raise RuntimeError("frozen formal ABI unexpectedly contains triangle-cell channel")

    missing = {
        "geometry_family": "built_in_triangle_gas",
        "primitive_columns": [
            "vertices_f32x3", "triangle_indices_u32x3", "front_cell_u32",
            "back_cell_u32", "face_id_u32",
        ],
        "hit_channels": ["primitive_index", "triangle_front_back_hit_kind"],
        "query_columns": ["position_f32x3", "direction_f32x3", "tmax_f32"],
        "output_columns": ["cell_id_u32", "face_id_u32"],
    }
    if primary["physical_admission"]["failure"] != {"code": FAILURE_CODE, "missing": missing}:
        raise RuntimeError("primary physical-failure payload does not independently recount")

    f = Fraction
    vertices = (
        (f(0), f(0), f(0)), (f(1), f(0), f(0)), (f(0), f(1), f(0)),
        (f(0), f(0), f(1)), (f(1), f(1), f(1)),
    )
    cells = ((0, 1, 2, 3), (4, 1, 2, 3))
    oracle = {
        "cell_0_interior": matches((f(1, 10), f(1, 10), f(1, 10)), vertices, cells),
        "cell_1_interior": matches((f(1, 2), f(1, 2), f(1, 2)), vertices, cells),
        "shared_face_ambiguous": matches((f(1, 3), f(1, 3), f(1, 3)), vertices, cells),
        "outside_mesh": matches((f(2), f(2), f(2)), vertices, cells),
    }
    expected_oracle = {
        "cell_0_interior": (0,), "cell_1_interior": (1,),
        "shared_face_ambiguous": (0, 1), "outside_mesh": (),
    }
    if oracle != expected_oracle:
        raise RuntimeError(f"independent oracle mismatch: {oracle}")

    if primary["behavioral_execution"]["optix_launch_count"] != 0:
        raise RuntimeError("failed admission cannot carry an OptiX launch")
    result: dict[str, Any] = {
        "schema": "rtdl.v4.goal5753.held_out_particle_tracking_recount.v1",
        "status": "independent_recount_matches_honest_physical_admission_failure",
        "primary_exam_module_imported": False,
        "rtdsl_imported": False,
        "selection_sha256": sha256_file(selection_path),
        "author_commit": author_commit,
        "author_file_sha256": author_hashes,
        "frozen_formal_geometry": "custom_analytic_sphere_aabb_gas",
        "independent_missing_capabilities": missing,
        "independent_oracle_matches": {key: list(value) for key, value in oracle.items()},
        "registered_gpu_workers": 0,
        "optix_launch_count": 0,
        "primary_status": primary["status"],
        "failure_code": FAILURE_CODE,
        "all_checks_passed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
