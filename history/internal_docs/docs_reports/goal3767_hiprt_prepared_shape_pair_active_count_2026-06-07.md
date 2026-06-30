# Goal3767 HIPRT Prepared Shape-Pair Active Count

Date: 2026-06-07

## Purpose

Goal3767 closes the second RayJoin-facing HIPRT generic-contract gap after
Goal3766. The added contract is a generic prepared right-shape payload plus a
scalar active-count query over left shapes. A pair is active when the existing
HIPRT relation flags would require segment intersection or point containment.

The new native symbols are:

- `rtdl_hiprt_prepare_shape_pair_relation_active_count`
- `rtdl_hiprt_count_prepared_shape_pair_relation_active`
- `rtdl_hiprt_destroy_prepared_shape_pair_relation_active_count`

The Python-facing prepared handle is:

- `prepare_hiprt_shape_pair_active_count_2d`
- `PreparedHiprtShapePairActiveCount2D.count(left_polygons)`

## Implementation

- Added `PreparedShapePairActiveCount2D`, retaining right polygon refs, right
  vertices, a HIPRT function table, and a lazily compiled scalar-count kernel.
- Added `RtdlShapePairActiveCount2DKernel`, reusing the same exact polygon
  relation helpers as `RtdlShapePairRelationFlags2DKernel`.
- Added the C ABI prepare/count/destroy trio.
- Added the Python prepared handle and context-manager lifecycle.
- Added `prepared_shape_pair_active_count_2d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix: `spatial_rayjoin` now has no
  missing generic HIPRT contracts and moves to `ready_for_amd_functional_pod`.

## Important Boundary

This is not a full reusable right-geometry scene. The current HIPRT shape-pair
candidate construction uses a left-batch envelope, so each count query still
builds query-specific AABBs and a query-specific HIPRT geometry. The win is that
right polygon payloads and the count kernel are prepared/reused, and the result
is a scalar active count instead of a full `left_count * right_count` relation
row matrix.

The deeper performance target remains a stronger shape-pair candidate geometry
that can reuse more of the prepared right-side structure across arbitrary left
batches.

## Evidence

Artifact:

`docs/reports/goal3767_hiprt_prepared_shape_pair_active_count_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `24055b49`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Clean validation from `/root/rtdl_goal3767_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
python3 -m unittest \
  tests.goal3767_hiprt_prepared_shape_pair_active_count_test \
  tests.goal3766_hiprt_prepared_segment_pair_count_test \
  tests.goal3765_hiprt_prepared_grouped_anyhit_flags_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 28 tests passed.
- The clean source commit was `24055b49`.
- The scoped source status was clean.

Correctness sample:

- HIPRT relation row count: `6`
- Active pair count from relation flags: `2`
- HIPRT prepared scalar active count: `2`
- Match: `true`

## Parity Position

After Goals3766 and 3767, the `spatial_rayjoin` HIPRT row in the v2.10
AMD/HIPRT parity matrix has no missing generic contracts and is marked
`ready_for_amd_functional_pod`.

This is still not AMD hardware evidence. It does not authorize release, AMD
performance, broad RT-core, whole-app speedup, paper reproduction, or public
benchmark claims.

## Next Step

The next required step is an actual AMD HIPRT functional pod run for the two
currently ready lanes:

- `robot_collision`
- `spatial_rayjoin`

If AMD hardware passes functionally, the next engineering target is performance
work on reusable prepared geometry and resident query batching, not
app-specific RayJoin code.
