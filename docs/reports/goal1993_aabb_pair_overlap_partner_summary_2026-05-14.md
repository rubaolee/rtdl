# Goal1993 AABB Pair-Overlap Partner Summary

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

The two polygon control rows were much better after the compact identity-payload
work, but their continuation still selected an app-local CuPy RawKernel named
for polygon pair summaries. That was acceptable as user continuation evidence,
but it was not the cleanest v2.0 teaching surface.

Goal1993 moves the reusable part into the partner adapter as a generic 2D AABB
pair-overlap summary.

## What Changed

The partner adapter now exposes:

```text
aabb_pair_overlap_summary_2d_partner_columns(...)
```

The helper accepts caller-supplied partner columns:

```text
left_index, right_index,
left_min_x, left_min_y, left_max_x, left_max_y, left_area,
right_min_x, right_min_y, right_max_x, right_max_y, right_area
```

It returns:

```text
overlap_pair_count,
total_intersection_area,
total_union_area,
set_intersection_area
```

The polygon control examples now prepare those generic pair columns and call the
partner helper. The old app-local `POLYGON_EXTENT_RAWKERNEL_SOURCE` and
`rtdl_user_pair_extent_summary` path are gone from the example.

## Boundary

This does not customize the RTDL native engine. It is also not arbitrary polygon
overlay, polygon clipping, point-in-polygon, GIS topology, or an RT-core polygon
claim. It is a generic partner continuation for axis-aligned 2D boxes and
candidate pair identities.

Existing Goal1969 pod timing remains the performance evidence for the authored
axis-aligned polygon control rows. Goal1993 narrows the design debt by replacing
the app-local extent kernel with a reusable partner primitive.

## Validation

Local validation passed:

```text
py -3 -m unittest tests.goal1993_aabb_pair_overlap_partner_summary_test \
  tests.goal1953_control_apps_cupy_rawkernel_v2_test \
  tests.goal1969_cupy_extent_polygon_candidate_backend_test \
  tests.goal1931_current_all_app_v18_v2_perf_analysis_test

py -3 -m unittest tests.goal1957_partner_identity_payload_contract_test \
  tests.goal1993_aabb_pair_overlap_partner_summary_test \
  tests.goal1953_control_apps_cupy_rawkernel_v2_test

py -3 scripts\goal1908_v2_local_preflight.py
```

The preflight now includes the Goal1993 regression test and passed. The pod
remains reserved for larger performance measurements; Goal1993 itself is a
structural partner-adapter cleanup and does not create new release performance
evidence.
