from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np


SCHEMA = "rtdl.paper_reproduction.librts.goal5504_range_intersects_semantics_fixtures.v1"
F32 = np.float32
F32_MAX = F32(np.finfo(np.float32).max)
F32_EPS = F32(np.finfo(np.float32).eps)
GAMMA3 = F32((F32(3) * F32_EPS) / (F32(1) - F32(3) * F32_EPS))
T1 = F32(np.nextafter(F32(1.0), F32_MAX))
TFAR_MULTIPLIER = F32(F32(1.0) + F32(2.0) * GAMMA3)


Box = tuple[float, float, float, float]


def _f32(value: float | np.floating) -> np.float32:
    return F32(value)


def cpu_inclusive_intersects(box: Box, query: Box) -> bool:
    return bool(
        _f32(query[0]) <= _f32(box[2])
        and _f32(query[2]) >= _f32(box[0])
        and _f32(query[1]) <= _f32(box[3])
        and _f32(query[3]) >= _f32(box[1])
    )


def _slab_hit(origin: tuple[np.float32, np.float32], direction: tuple[np.float32, np.float32], box: Box) -> bool:
    t0 = F32(0.0)
    t1 = T1
    for index in range(2):
        ray_dir = direction[index]
        with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
            inv_ray_dir = F32(1.0) / ray_dir
            t_near = (_f32(box[index]) - origin[index]) * inv_ray_dir
            t_far = (_f32(box[index + 2]) - origin[index]) * inv_ray_dir
            if t_near > t_far:
                t_near, t_far = t_far, t_near
            t_far = F32(t_far * TFAR_MULTIPLIER)
            t0 = t_near if t_near > t0 else t0
            t1 = t_far if t_far < t1 else t1
        if t0 > t1:
            return False
    return True


def author_gpu_style_intersects(box: Box, query: Box) -> bool:
    # Mirrors the pinned author's forward shader: query diagonal, then the
    # reverse envelope diagonal, both consumed by RayParams<float, 2>::IsHit.
    query_origin = (_f32(query[2]), _f32(query[1]))
    query_direction = (_f32(query[0]) - query_origin[0], _f32(query[3]) - query_origin[1])
    query_hit = _slab_hit(query_origin, query_direction, box)

    box_origin = (_f32(box[0]), _f32(box[1]))
    box_direction = (_f32(box[2]) - box_origin[0], _f32(box[3]) - box_origin[1])
    # The pinned forward shader reports the pair only when the reverse test
    # does *not* hit: `if (!box_hit)`. This is the author's directional
    # diagonal-ray construction, not a symmetric two-hit overlap test.
    box_hit = _slab_hit(box_origin, box_direction, query)
    forward_hit = query_hit and not box_hit

    # SpatialIndex::Query runs a second backward pass. Its shader casts the
    # envelope diagonal against the query AABB and reports a hit directly.
    backward_hit = box_hit
    return forward_hit or backward_hit


def _case(case_id: str, category: str, box: Box, query: Box, note: str) -> dict[str, object]:
    cpu = cpu_inclusive_intersects(box, query)
    gpu = author_gpu_style_intersects(box, query)
    return {
        "case_id": case_id,
        "category": category,
        "box": list(box),
        "query": list(query),
        "cpu_inclusive_intersects": cpu,
        "author_gpu_style_intersects": gpu,
        "discriminates": cpu != gpu,
        "note": note,
    }


def build_cases() -> list[dict[str, object]]:
    one_ulp_above = float(np.nextafter(F32(1.0), F32_MAX))
    one_ulp_below = float(np.nextafter(F32(1.0), F32(0.0)))
    return [
        _case(
            "interior_overlap",
            "ordinary_overlap",
            (0.0, 0.0, 1.0, 1.0),
            (0.25, 0.25, 0.75, 0.75),
            "Both contracts must accept an interior overlap.",
        ),
        _case(
            "edge_touch",
            "inclusive_boundary",
            (0.0, 0.0, 1.0, 1.0),
            (1.0, 0.25, 2.0, 0.75),
            "The CPU contract accepts a shared boundary; the GPU emulation is checked explicitly.",
        ),
        _case(
            "one_ulp_gap_after_box_max",
            "float32_ulp_boundary",
            (0.0, 0.0, 1.0, 1.0),
            (one_ulp_above, 0.25, 2.0, 0.75),
            "The query starts one float32 ULP beyond the box max; gamma expansion may distinguish the GPU path.",
        ),
        _case(
            "one_ulp_overlap_before_box_max",
            "float32_ulp_boundary",
            (0.0, 0.0, 1.0, 1.0),
            (one_ulp_below, 0.25, 2.0, 0.75),
            "The query starts one float32 ULP below the box max.",
        ),
        _case(
            "corner_touch",
            "inclusive_corner_boundary",
            (0.0, 0.0, 1.0, 1.0),
            (1.0, 1.0, 2.0, 2.0),
            "Both dimensions meet at one corner; this probes diagonal handling.",
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = build_cases()
    payload = {
        "schema": SCHEMA,
        "status": "semantics_fixture_diagnostic_completed",
        "contract_inputs": {
            "coordinate_type": "float32",
            "cpu_contract": "inclusive_aabb_intersects_float32",
            "gpu_contract_emulation": "rayparams_float32_slab_nextafter_t1_tfar_gamma",
            "gamma3": float(GAMMA3),
            "t1": float(T1),
            "tfar_multiplier": float(TFAR_MULTIPLIER),
        },
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "discriminating_case_count": sum(bool(case["discriminates"]) for case in cases),
            "cpu_gpu_emulation_equivalent_on_all_cases": all(
                not case["discriminates"] for case in cases
            ),
        },
        "claim_boundary": {
            "author_gpu_runtime_executed": False,
            "cpu_oracle_is_author_truth": False,
            "cpu_gpu_equivalence_proven": False,
            "full_input_adjudication": False,
            "rtdl_core_change_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
