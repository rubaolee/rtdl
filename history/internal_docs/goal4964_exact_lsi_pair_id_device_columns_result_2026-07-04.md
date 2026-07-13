# Goal4964 Exact LSI Pair-Id Device Columns Result

Date: 2026-07-04

## Exit Label

`completed_exact_lsi_pair_id_device_columns_correctness_passed__performance_no_go`

## Purpose

Implement and test the Goal4963 design: an exact planar-map LSI pair-id
device-column route that returns generic `{left_id,right_id}` columns without
using the bundled RayJoin overlay helper.

This goal was intentionally allowed to fail as a performance idea. The key
question was whether host row materialization/host row bridge dominated the
fresh writer-free binary route's LSI phase.

## Implementation Summary

Files changed:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal4964_exact_lsi_pair_id_device_columns_test.py
tests/goal4956_columnar_xsect_pipeline_test.py
```

Native symbol added:

```text
rtdl_optix_run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode
```

Python API added:

```python
PreparedOptixPlanarMapLsi2DQuery.run_pair_id_device_columns()
PreparedOptixPlanarMapLsi2D.run_pair_id_device_columns(query)
```

App measurement flag added:

```bash
--exact-lsi-device-columns
```

The native route:

1. Uses the same exact grouped-range direct-intersection predicate as
   `run_pair_id_rows()`.
2. Counts exact accepted pairs.
3. Emits packed exact pair ids on device.
4. Splits packed pair ids into generic device `left_id/right_id` columns.
5. Returns an `OptixNativeDevicePairColumnOutput`.

The public app currently copies those device columns back to NumPy for the
existing downstream reprojection/sort/group path. That copy is explicitly timed
as:

```text
lsi_exact_pair_id_device_columns_to_numpy_sec
```

This is not an end-to-end zero-copy claim.

## POD Build

```text
host: root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
command: make build-optix
result: success
```

## Local Structural Tests

Command:

```bash
py -m unittest \
  tests.goal4964_exact_lsi_pair_id_device_columns_test \
  tests.goal4955_projected_descriptor_pipeline_test \
  tests.goal4956_columnar_xsect_pipeline_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test
```

Result:

```text
Ran 13 tests in 0.160s
OK (skipped=2)
```

Public app/README leak scan:

```bash
rg -n "Goal[0-9]+|goal[0-9]+|history/internal_docs|call_for_review|verdict" \
  Paper-reproduction-apps/rayjoin-paper/README.md \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

Result: no matches.

## POD Measurement Artifacts

```text
history/internal_docs/goal4955_artifacts/goal4964_host_pair_rows_baseline_run1.json
history/internal_docs/goal4955_artifacts/goal4964_host_pair_rows_baseline_run2.json
history/internal_docs/goal4955_artifacts/goal4964_host_pair_rows_baseline_run3.json
history/internal_docs/goal4955_artifacts/goal4964_exact_lsi_device_columns_run1.json
history/internal_docs/goal4955_artifacts/goal4964_exact_lsi_device_columns_run2.json
history/internal_docs/goal4955_artifacts/goal4964_exact_lsi_device_columns_run3.json
history/internal_docs/goal4955_artifacts/goal4964_exact_lsi_pair_id_device_columns_summary.json
```

## Results

Same input as Goal4960:

```text
left:  br_county_clean_25_odyssey_final.txt
right: br_soil_ascii_odyssey_final.txt
author_overlay_compute_sec: 0.0421
```

Median results:

| Route | writer_free_hot_sec | Ratio vs 0.0421s | LSI phase | Device-to-NumPy copy | Fingerprint |
|---|---:|---:|---:|---:|---|
| host exact pair-id rows | 0.893045s | 21.21x | 0.806946s | n/a | stable |
| exact pair-id device columns | 0.987424s | 23.45x | 0.895913s | 0.000526s | stable |

Stable fingerprint in all six runs:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

## Interpretation

Correctness/route result:

```text
pass
```

The exact device-column route produces the same downstream semantic
fingerprint as the host exact pair-id rows route.

Performance result:

```text
no-go for speedup
```

The route is slower than the existing host exact pair-id row route on the public
sample:

```text
0.987424s vs 0.893045s median writer_free_hot_sec
```

The critical observation is:

```text
device-to-NumPy copy median: ~0.000526s
exact LSI device-column phase median: ~0.895913s
```

So the host row materialization/copy is not the meaningful bottleneck. The
fresh LSI cost is dominated by exact traversal/predicate work and by this
prototype's count+emit two-pass structure.

## Decision

Do not promote `--exact-lsi-device-columns` as the v2.14.3 performance route.

It can remain as an internal measurement/prototype route if reviewers accept
the genericity, but it does not solve the fresh-overlay performance gap.

The next performance direction should not be "move the same exact pair ids to
device columns." It should be one of:

1. make exact LSI pair-id production single-pass while still exact and generic,
2. optimize the exact planar-map LSI predicate/traversal itself,
3. or acknowledge that closing the remaining gap requires the later Layer 4
   fusion/pushdown work.

## Not Authorized

- No claim that exact LSI device columns speed up RayJoin.
- No claim that RTDL is near AuthorPatch performance on fresh overlay.
- No claim that this is end-to-end zero-copy.
- No claim that candidate device columns are correctness-equivalent.
