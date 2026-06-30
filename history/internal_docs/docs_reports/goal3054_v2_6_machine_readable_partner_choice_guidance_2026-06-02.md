# Goal3054 v2.6 Machine-Readable Partner Choice Guidance

Date: 2026-06-02

## Purpose

Goal3050 added learner-facing guidance for the user question:

```text
If I need custom logic after the RTDL primitive, should I choose CuPy or Numba?
```

Goal3054 mirrors that guidance in source as advisory metadata so examples and
benchmark apps can explain partner recommendations without inventing their own
wording.

## Implementation

Added `src/rtdsl/v2_6_partner_choice_guidance.py` with:

- `v2_6_partner_choice_guidance()`
- `plan_v2_6_partner_choice(benchmark_app, continuation_shape=None)`
- `explain_v2_6_partner_choice(..., user_preferred_partner=None)`
- `validate_v2_6_partner_choice_guidance(...)`

The helper covers the ten promoted benchmark apps:

```text
hausdorff_xhd, spatial_rayjoin, rt_dbscan, robot_collision,
contact_manifold, raydb_style, barnes_hut, librts_spatial_index,
rtnn, triangle_counting
```

## Design Rules

- Primitive first: use a fused generic RTDL primitive when it exactly expresses
  the answer.
- User choice: the helper explains; it does not auto-select.
- Evidence boundary: each row names the current evidence goal or artifact.
- Honesty: Numba is recommended for selected custom generic continuations, CuPy
  remains the measured reference for selected rows, and some apps have no
  promoted custom partner yet.
- Native engine remains app-agnostic.

## Validation

Planned focused validation:

```bash
PYTHONPATH=src:. python -m unittest tests.goal3054_v2_6_partner_choice_guidance_test
```

## Claim Boundary

Goal3054 does not authorize v2.6 release, broad CuPy or Numba acceleration
claims, RT-core speedup claims, true-zero-copy claims, automatic partner
selection, or app-specific native-engine behavior.
