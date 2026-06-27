# Goal3183: Shape-Pair Relation Active Count

Date: 2026-06-03

## Purpose

Goal3181 identified that Spatial RayJoin's current prepared OptiX route exposes
generic 2-D relation-row typed producer metadata, but the actual relation rows
are still host materialized.

Goal3183 takes the first performance-bearing step for the overlay-seed path:
add a generic prepared shape-pair relation active-count route. It counts rows
whose generic flags are active:

- `requires_segment_intersection != 0`
- `requires_point_containment != 0`

This lets scalar count mode avoid the final host row-table allocation and Python
row decoding that were previously required just to obtain the active seed count.

## Code Changes

- Added native ABI:
  `rtdl_optix_count_prepared_shape_pair_relation_flags`.
- Split the existing OptiX shape-pair relation implementation into:
  - `compute_shape_pair_relation_flags_with_prepared_right_optix(...)`
  - `run_shape_pair_relation_flags_with_prepared_right_optix(...)`
  - `count_shape_pair_relation_flags_with_prepared_right_optix(...)`
- Added Python method:
  `PreparedOptixShapePairRelation.count_active(...)`.
- Updated the Spatial RayJoin prepared `overlay_seed` count route so it reports
  `overlay_active_pair_dependency_count` and `active_seed_count`.
- Left row mode unchanged. Users who need full pair-dependency rows still call
  the row path and receive `overlay_pair_dependency_rows_with_lsi_pip_flags`.

## Boundary

This is a materialization-reduction step, not the full resident-row stream.
It does not produce device-resident relation-row columns.

It does:

- reuse the generic shape-pair relation flag computation,
- skips final host row allocation for active relation-row count mode,
- keep RayJoin interpretation in Python/app code,
- preserve app-agnostic native terminology.

It does not:

- produce device-resident relation-row columns,
- prove zero-copy,
- prove a public speedup,
- reproduce RayJoin paper results,
- authorize a v2.8 release.

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Local validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3183_shape_pair_relation_active_count_test tests.goal2327_rayjoin_prepared_route_contract_test
```

Result:

```text
Ran 14 tests in 0.038s

OK
```

Pod validation:

- Host: `root@69.30.85.131 -p 22063`
- Repo: `/root/rtdl_goal3151`
- Commit: `b3e3077f`
- Python: `/root/venvs/rtdl_goal3154/bin/python`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`

Focused pod suite:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3151/build/librtdl_optix.so \
  /root/venvs/rtdl_goal3154/bin/python -m unittest \
  tests.goal3183_shape_pair_relation_active_count_test \
  tests.goal2327_rayjoin_prepared_route_contract_test \
  tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test
```

Result:

```text
Ran 14 tests in 0.005s

OK
```

Live pod measurement artifact:

`docs/reports/goal3183_pod_overlay_active_count_2026-06-03.json`

| Dataset | Active Count Median (s) | Old Row + Scan Median (s) | Row+Scan / Count |
| --- | ---: | ---: | ---: |
| `derived/authored_overlay_squares_tiled_x64` | 0.000328 | 0.002347 | 7.15x |
| `derived/authored_overlay_squares_tiled_x512` | 0.015492 | 0.146596 | 9.46x |
| `derived/authored_overlay_squares_tiled_x2048` | 0.227629 | 2.285913 | 10.04x |

All active counts matched the active rows obtained by the old row-production
plus flag-scan method.

Interpretation:

- This is a measured improvement for the exact overlay active-count subpath.
- The comparison is not a whole RayJoin paper reproduction.
- The comparison is not a public RT-core speedup claim.
- The comparison does not prove device-resident relation-row columns; it proves
  that active-count mode avoids the final host row allocation and Python row
  flag scan.
