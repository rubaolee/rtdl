# External Review Handoff: Goal3180/3181 Typed Producer Metadata

Date: 2026-06-03

Please perform a read-only independent review of the recent v2.8 typed producer
metadata work:

- Goal3180 report:
  `docs/reports/goal3180_ray_triangle_hit_stream_typed_producer_metadata_2026-06-03.md`
- Goal3181 report:
  `docs/reports/goal3181_geometry_relation_row_view_typed_producer_metadata_2026-06-03.md`
- Relevant source:
  `src/rtdsl/hit_stream_handoff.py`
  `src/rtdsl/generic_primitives.py`
  `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
  `src/rtdsl/optix_runtime.py`
  `src/rtdsl/v2_8_benchmark_runtime_gap.py`
  `src/rtdsl/__init__.py`
- Relevant tests:
  `tests/goal3180_ray_triangle_hit_stream_typed_producer_metadata_test.py`
  `tests/goal3181_geometry_relation_row_view_typed_producer_metadata_test.py`
  `tests/goal3172_v2_8_runtime_gap_compact_mask_refresh_test.py`
  `tests/goal3105_v2_8_benchmark_runtime_gap_map_test.py`

Review questions:

1. Are Goal3180 and Goal3181 correctly separated? Goal3180 should cover generic
   3-D ray/triangle device hit-stream metadata; Goal3181 should cover current
   Spatial RayJoin generic 2-D relation-row host row-view metadata.
2. Do the new names and schemas stay app-agnostic, or do they smuggle Spatial
   RayJoin, graph, Hausdorff, or other app semantics into the runtime/core?
3. Are the claim boundaries honest? Goal3180 can report the live device-resident
   hit-stream evidence it actually has; Goal3181 must remain
   `host_materialized_row_view` and must not imply device-resident relation rows,
   zero-copy, public speedup, or release readiness.
4. Do the tests actually enforce the intended split and boundary, including the
   corrected Spatial RayJoin runtime-gap wording?
5. What is the next highest-risk engineering step before moving Spatial RayJoin
   from host row-view metadata to real resident relation-row outputs?

Expected output path:

`docs/reviews/goal3182_external_review_goal3180_3181_typed_producer_metadata_2026-06-03.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
