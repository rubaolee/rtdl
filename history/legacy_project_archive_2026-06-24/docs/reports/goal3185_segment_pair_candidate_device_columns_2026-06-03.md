# Goal3185: Segment-Pair Candidate Device Columns

Date: 2026-06-03

## Purpose

Goal3183 removed host row materialization for the Spatial RayJoin overlay
active-count subpath. Goal3185 starts the harder resident-output path for the
same generic geometry family: prepared segment-pair traversal can now emit
device-resident candidate ID columns:

- `left_id`
- `right_id`

This is the next primitive-level building block for device-side continuations
over relation candidates.

## Code Changes

- Added generic native ABI:
  `rtdl_optix_prepared_segment_pair_candidate_device_columns`.
- Added release ABI:
  `rtdl_optix_release_segment_pair_candidate_device_columns`.
- Added `RtdlNativeDevicePairColumns` with native-owned CUDA pointers for
  `left_id` and `right_id` columns plus row-count, event-count, overflow,
  capacity, device, owner, and traversal metadata.
- Added an OptiX candidate-column pipeline derived from the existing
  segment-pair conservative candidate any-hit logic.
- Added Python RAII output:
  `OptixNativeDevicePairColumnOutput`.
- Added Python method:
  `PreparedOptixSegmentPairIntersection.candidate_device_columns(...)`.
- Extended v2.8 geometry-relation typed metadata with the generic
  `segment_pair_candidate_2d_device_columns` schema.

## Boundary

This produces device-resident candidate ID columns. It is not exact
intersection witness row materialization; in shorter terms, these are
not exact intersection witness rows.

It does:

- keep native terminology generic,
- reuse the generic segment-pair conservative candidate any-hit logic,
- keep `left_id` and `right_id` columns resident in native-owned CUDA memory,
- return typed stream metadata without forcing a host copy,
- fail closed on overflow.

It does not:

- produce exact `intersection_point_x` / `intersection_point_y` witnesses,
- validate final line-segment intersection predicates,
- provide grouped/reduction continuation over the pair columns yet,
- prove true zero-copy with partner-owned memory,
- prove a public speedup,
- reproduce RayJoin paper results,
- authorize a v2.8 release.

Implementation scope:

- This is a single-launch first slice.
- `left_count * right_count` must fit the uint32 OptiX launch/candidate space.
- chunked append remains future work.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3185_segment_pair_candidate_device_columns_test tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test tests.goal3183_shape_pair_relation_active_count_test
```

Result:

```text
Ran 16 tests in 0.050s

OK
```

Pod validation:

- Host: `root@69.30.85.131 -p 22063`
- Repo: `/root/rtdl_goal3151`
- Commit: `32ab41a0`
- Python: `/root/venvs/rtdl_goal3154/bin/python`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Focused pod suite:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3151/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3185_segment_pair_candidate_device_columns_test \
  tests.goal3183_shape_pair_relation_active_count_test \
  tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test
```

Result:

```text
Ran 16 tests in 0.007s

OK
```

Live pod smoke artifact:

`docs/reports/goal3185_pod_segment_pair_candidate_device_columns_2026-06-03.json`

The authored crossing-segment smoke compared the new device-column candidate
output against the existing exact row path:

| Dataset | Exact Rows | Candidate Column Rows | Candidate Events | Device Columns | Overflow |
| --- | ---: | ---: | ---: | ---: | --- |
| `authored_16_horizontal_by_4_vertical_crossing_segments` | 64 | 64 | 64 | 2 | `False` |

The live smoke also verified:

- `left_id` and `right_id` device pointers were nonzero,
- the typed producer primitive was `segment_pair_candidate_2d`,
- the schema was `segment_pair_candidate_2d_device_columns`,
- `release_authorized` stayed `False`,
- `true_zero_copy_claim_authorized` stayed `False`.
