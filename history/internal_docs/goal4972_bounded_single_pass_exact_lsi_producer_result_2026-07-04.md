# Goal4972 — Bounded Single-Pass Exact LSI Producer Result

Date: 2026-07-04

## Verdict

`bounded_single_pass_exact_lsi_no_go`

The bounded exact LSI device-column producer is correct and generic, but it does not materially
improve the RayJoin large representative route. The deleted count pass is not the bottleneck.

## What Changed

Added a bounded exact planar-map LSI pair-id device-column route:

- native symbol:
  `rtdl_optix_run_prepared_segment_pair_bounded_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode`
- Python wrapper:
  `PreparedOptixPlanarMapLsi2D.run_bounded_pair_id_device_columns(..., max_rows=...)`
- app measurement route:
  `section57_overlay_columnar_binary.py --bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity N`

The output remains generic `{left_id, right_id}` device columns. It does not encode RayJoin output
chains, author text format, faces, or overlay semantics. Overflow fails closed.

## Validation

Local structural tests:

```text
py -m unittest tests.goal4964_exact_lsi_pair_id_device_columns_test tests.goal4956_columnar_xsect_pipeline_test tests.goal4972_bounded_exact_lsi_producer_test
Ran 11 tests in 0.792s
OK (skipped=1)
```

POD smoke:

```text
single crossing segment pair: row_count=1 capacity=4 candidate_event_count=1 overflow=False
overflow smoke: row_count=0 capacity=0 candidate_event_count=1 overflow=True
```

POD matrix environment notes:

- The POD needed `RTDL_OPTIX_PTX_COMPILER=nvcc` because runtime NVRTC failed on host glibc math
  headers.
- The command had to use an explicit PATH/LD_LIBRARY_PATH; earlier `$CUDA_HOME`/`$PATH` expansion
  through PowerShell/SSH produced bad remote values.
- This is an environment/runtime compile-path fix, not an algorithm or app-semantics change.

## Top4 Representative Results

Input:

```text
left:  /root/rtdl_goal4971/Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb
right: /root/rtdl_goal4971/Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb
```

Correctness gates passed for all routes:

| Gate | Value |
|---|---:|
| LSI row count | `428322` |
| xsect rows side0 / side1 | `428322 / 428322` |
| vertex PIP positives | `812721 / 4527305` |
| device sort validation | `true / true` |

Performance:

| Route | Writer-Free Hot Sec | LSI Stage Sec | Notes |
|---|---:|---:|---|
| public rows | `9.387372702360153` | `4.5479182079434395` | baseline in this run |
| exact pair-id device columns | `5.845848858356476` | `2.687378019094467` | Goal4971-style route |
| bounded exact pair-id device columns | `5.277617208659649` | `2.688651569187641` | new route |
| prepared replay | `2.56909366697073` | `0.009015299379825592` | cached diagnostic only; excludes prepare/workspace |

The bounded LSI stage is effectively the same as the exact-device LSI stage:

```text
bounded exact LSI: 2.688651569187641s
exact-device LSI: 2.687378019094467s
delta: +0.001273550093174s
```

The slightly lower full writer-free hot time for bounded (`5.2776s` vs `5.8458s`) does not come from
the LSI producer; the LSI stages are equal within noise. It is mostly downstream variance, especially
compiled carrier construction in this run.

## Key Finding

The count pass is not the bottleneck.

Native LSI timing for bounded exact output:

```json
{
  "candidate_count_pass": 0.0,
  "candidate_write_pass": 0.002294741,
  "native_output_row_count": 428322,
  "native_output_capacity": 1000000,
  "native_output_overflow": false
}
```

Native LSI timing for exact-device output:

```json
{
  "candidate_count_pass": 0.002218429,
  "candidate_write_pass": 0.00226498,
  "native_output_row_count": 428322
}
```

The removable count pass is roughly `0.002s`, while the Python-measured exact LSI stage is roughly
`2.69s`. Therefore, deleting the count pass cannot move the route materially.

## Interpretation

Goal4972 is useful because it closes one hypothesis:

> The exact LSI producer is not slow because it performs a separate count pass.

The remaining LSI cost is elsewhere: native runtime pipeline setup / exact LSI producer computation /
predicate/traversal machinery. The next goal should not keep shaving row-output wrappers. It should
target the exact LSI producer itself, or explicitly pivot to a larger architectural path such as a
resident exact LSI workspace / precompiled pipeline / predicate-level optimization.

## Artifacts

Local artifact directory:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_artifacts_2026-07-04/`

Key file:

`history/internal_docs/goal4972_bounded_single_pass_exact_lsi_producer_artifacts_2026-07-04/goal4970_top4_section57_matrix_summary.json`

## Not Authorized

- No broad RayJoin speedup claim.
- No author-performance headline.
- No claim that bounded single-pass closes the exact LSI bottleneck.
- No Layer 4 or callback/fusion claim.
- No public release wording change from this result alone.
