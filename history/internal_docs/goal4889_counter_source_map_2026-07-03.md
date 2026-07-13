# Goal4889 Counter Source Map

Date: 2026-07-03

Status: `source_map_complete__instrumentation_gap_identified`

## Boundary

This source map is read-only. No RTDL product code or AuthorPatch comparator was
modified for Goal4889.

## RTDL Public Overlay Route

The user/application script is:

```text
history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py
```

It imports public RTDL primitives:

```python
from rtdsl import prepare_planar_map_lsi_2d_optix
from rtdsl import prepare_planar_map_point_location_2d_optix
```

It does not import `rtdsl.rayjoin_overlay`.

The Goal4886 Numba wrapper:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

keeps the Goal4880 RTDL primitive path intact and only accelerates selected
application-layer continuation/writer helpers.

## RTDL LSI Counter Path

Public API:

```text
src/rtdsl/optix_runtime.py
PreparedOptixPlanarMapLsi2D.run_raw()
```

Execution path:

```text
PreparedOptixPlanarMapLsi2D.run_raw()
-> PreparedOptixSegmentPairIntersection.run_prepared_left_grouped_range_direct_intersection()
-> rtdl_optix_run_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode()
```

Native implementation:

```text
src/native/optix/rtdl_optix_workloads.cpp
run_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode_optix()
```

Key source fact:

```text
count_segment_pair_intersection_grouped_range_direct_is_exact_one_pass_optix(..., record_group_candidate_events=false)
```

The native helper can count group-candidate events when
`record_group_candidate_events=true`, but the current public row-producing path
sets it to `false`.

Python timing getter:

```text
src/rtdsl/optix_runtime.py
_get_last_segment_pair_phase_timings_from_library()
```

It can return:

- `raw_candidate_count`;
- `emitted_count`;
- candidate pass time;
- write pass time;
- exact-refine time.

But for the actual public LSI row route, `raw_candidate_count` is not populated.
The Goal4889 probe confirmed this:

```json
"mode": "none",
"raw_candidate_count": 0,
"emitted_count": 13452
```

This is a missing instrumentation issue, not a zero-work result.

## RTDL PIP / Point-Location Counter Path

Public API:

```text
src/rtdsl/optix_runtime.py
prepare_planar_map_point_location_2d_optix()
```

This wraps:

```text
prepare_rayjoin_cdb_point_location_2d_optix()
```

Native timing getter:

```text
src/native/optix/rtdl_optix_workloads.cpp
rtdl_optix_rayjoin_cdb_point_location_get_last_phase_timings()
```

It currently returns only:

- point upload seconds;
- traversal seconds;
- row download seconds;
- point count;
- positive face count;
- mode.

It does not return:

- number of AABB/range candidate hits;
- number of segment loop iterations inside `__intersection__rayjoin_cdb_point_location`;
- rejected candidate count;
- per-query distribution.

The native intersection shader:

```text
src/native/optix/rtdl_optix_core.cpp
__intersection__rayjoin_cdb_point_location()
```

loops:

```cpp
for (unsigned int segment_index = range.begin; segment_index < range.end; ++segment_index) {
    ...
}
```

That loop is exactly the work denominator Goal4889 needs, but no counter is
currently accumulated or exposed.

## AuthorPatch Counter Sources

Existing AuthorPatch logs expose:

- map chains/points/edges;
- compressed AABB primitive counts;
- launch dimensions;
- phase times.

They do not expose:

- actual AABB candidate hit count;
- actual per-ray segment tests;
- rejected candidates;
- per-query candidate distributions.

Useful log lines already captured:

```text
lsi_rt.h:50] queries: 14430155
optixLaunch, [w,h,d] = 14430155,1,1
optixLaunch, [w,h,d] = 14788065,1,1
optixLaunch, [w,h,d] = 992505,1,1
optixLaunch, [w,h,d] = 1707,1,1
optixLaunch, [w,h,d] = 2752,1,1
primitive.h:256] ... ne: 14430155 aabbs: 2640424
primitive.h:256] ... ne: 941375 aabbs: 194026
```

These prove comparable launch/query sizes, but not comparable work count.

## Minimal Counter Probe Needed

To finish Claude's AM1, the next measurement must add temporary
instrumentation, not product features.

RTDL temporary measurement build:

1. LSI: enable or expose `record_group_candidate_events=true` for the same
   grouped-range direct-intersection path used by public LSI rows.
2. PIP: add a measurement-only counter for total
   `range.end - range.begin` iterations executed by
   `__intersection__rayjoin_cdb_point_location`.

AuthorPatch temporary measurement build:

1. LSI: count candidate/intersection tests in the Section 5.7 LSI shader.
2. PIP: count candidate edge/range tests in the point-location shader.

Both probes should report:

- total candidate/test count;
- accepted hit count;
- query count;
- time;
- candidate/test per query.

## Source Map Label

`source_map_identifies_counter_gap__temporary_instrumentation_required`
