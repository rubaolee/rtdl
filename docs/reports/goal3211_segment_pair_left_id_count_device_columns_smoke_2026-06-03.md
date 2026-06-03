# Goal3211: Segment-Pair Left-ID Count Device Columns Smoke

Date: 2026-06-03

## Purpose

Goal3211 records live pod evidence for the Goal3210 generic fused count
primitive:

`rtdl_optix_prepared_segment_pair_left_id_count_device_columns`

The primitive counts segment-pair hits by the pair-column `left_id` axis during
OptiX traversal and returns a dense device-resident count column. It avoids
materializing `left_ids[]` / `right_ids[]` pair columns when the caller only
needs per-left counts.

This is a generic segment-pair primitive. It is not a RayJoin-specific native
kernel.

## Pod Evidence

Artifact:

- `docs/reports/goal3211_segment_pair_left_id_count_device_columns_smoke_2026-06-03.json`
- Commit under test: `b9b8df8f`
- Symbol: `rtdl_optix_prepared_segment_pair_left_id_count_device_columns`
- Build: pod `make build-optix` completed before the smoke.

Fixture:

- `16` horizontal left segments with IDs `0..15`
- `4` vertical right segments crossing every left segment
- Expected candidate count: `64`

Result:

- Dense count output was device-resident.
- `source_row_count: 64`
- Counts copied with CuPy for validation were `[4, 4, ..., 4]`.
- `all_match_expected_counts: true`

Negative probe:

- `group_capacity: 8`
- `overflow: true`
- `device_resident: false`

## Interpretation

The smoke proves the new ABI builds, loads, executes, and preserves the direct
address group-capacity failure boundary.

The dense output uses implicit group keys: `count[index]` is the count for group
key `index`. The metadata records:

`group_key_semantics: dense output uses direct-address array index as the implicit group key`

## Boundaries

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`

This smoke does not prove:

- final Spatial RayJoin semantics,
- public whole-app speedup,
- RayJoin paper parity,
- true zero-copy,
- release readiness.
