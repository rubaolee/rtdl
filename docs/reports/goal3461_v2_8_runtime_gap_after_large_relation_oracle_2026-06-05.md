# Goal3461 - v2.8 Runtime Gap Refresh After Large Relation Oracle

## Status

Implemented locally.

Goal3461 refreshes the v2.8 Spatial RayJoin runtime gap map after Goals3459-3460.

## What Changed

The Spatial RayJoin row now records two new evidence points:

- Goal3459: public-CDB scale evidence for the generic CuPy bounds-overlap area continuation over resident relation ids, ordinals, and geometry payload columns.
- Goal3460: public-CDB relation id/flag/ordinal content matched a native-fidelity float32 host oracle exactly.

This narrows the active gap. Large relation content is no longer merely fixture-proven; it is public-data-proven under the native OptiX float32 relation contract.

## Remaining Gap

The remaining RayJoin gap is now more precise:

- exact polygon relation witnesses
- exact overlay-area continuation for non-integer, non-orthogonal polygons
- boundary-witness ownership at serious scale

The public CDB audit found non-integer coordinates and diagonal edges, so the older integer-grid exact-area helper cannot be used as the exact overlay oracle for this dataset.

## Boundary

Goal3461 does not authorize:

- v2.8 release
- public speedup wording
- broad RT-core speedup wording
- true-zero-copy wording
- RayJoin paper reproduction claims
- RTDL-beats-RayJoin claims
- full exact overlay-area completion claims

## Validation

- `py -3 -m unittest tests.goal3461_v2_8_runtime_gap_after_large_relation_oracle_test tests.goal3460_shape_pair_relation_large_content_oracle_test tests.goal3459_shape_pair_bounds_overlap_area_large_probe_test`
