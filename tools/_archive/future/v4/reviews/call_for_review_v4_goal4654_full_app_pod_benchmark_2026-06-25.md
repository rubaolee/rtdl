# Call For Review: V4 Goal4654 Full App-Level POD Benchmark

Date: 2026-06-25
Requested verdict: one of

- `accept_goal4654_complete_proceed_goal4655`
- `accept_goal4654_complete_with_blockers_proceed_goal4655`
- `reject_goal4654_rerun_required`
- `blocked_missing_context`

## Files To Review

- Report:
  `future/v4/v4_goal4654_full_app_level_v2_14_v3_v4_pod_benchmark_2026-06-25.md`
- Raw evidence:
  `future/v4/evidence/v4_goal4654_serious_20260625_2/summary.json`
- Generated markdown:
  `future/v4/evidence/v4_goal4654_serious_20260625_2/summary.md`
- Runner:
  `scripts/v4_goal4654_full_app_level_pod_benchmark.py`
- Frozen protocol:
  `future/v4/v4_goal4653_full_app_level_protocol_freeze_2026-06-25.md`

## Core Facts

The serious run executed the four Goal4653 full-route app rows across V2.14,
V3.0.2, and current V4 candidate source trees.

Result table:

| App | V4/V2.14 hot | V4/V3.0.2 hot | V3.0.2/V2.14 hot | RC OK | Parity |
| --- | ---: | ---: | ---: | --- | --- |
| `rt_dbscan` | 1.070x | 1.084x | 0.987x | true | true |
| `raydb_style` | 0.994x | 1.000x | 0.995x | true | true |
| `triangle_counting` | 15.548x | 1.117x | 13.924x | true | true |
| `librts_spatial_index` | 0.999x | 1.001x | 0.997x | true | true |

Known limitations:

- V2.14 and V3.0.2 OptiX libraries could not be built on this POD because
  OptiX SDK headers are absent.
- OptiX-dependent old-version rows used a declared V4 compatibility native
  library. This is not hidden.
- RTDBSCAN large performance rows used `--no-validation`; same-route 2048-point
  parity companion rows were run for each version.
- Goal4654 authorizes no release and no public speedup wording.

## Questions

1. Does the evidence honestly satisfy Goal4654 as an app-level POD benchmark
   input to Goal4655 analysis?
2. Does the V2/V3 OptiX compatibility-native-library limitation block formal
   release authorization from this goal alone?
3. Is the RTDBSCAN split between large `--no-validation` performance rows and
   small same-route parity companion rows acceptable as evidence for analysis,
   or should it force a rerun?
4. Do the measured ratios support a formal high-performance V4 claim?
5. Is the correct next step Goal4655 benchmark analysis with partner-migration
   and native-provenance locks, rather than more raw benchmark running?

## Non-Authorization

This review request does not authorize V4 release, public V4 speedup wording,
whole-app performance claims, CuPy blanket claims, arbitrary Numba callback
claims, C ABI, embedding, or true-zero-copy claims.
