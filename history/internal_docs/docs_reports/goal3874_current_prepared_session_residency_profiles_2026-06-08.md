# Goal3874 Current Prepared-Session Residency Profiles

## Purpose

Goal3873 added the generic prepared-session residency contract. Goal3874
connects that contract to the current benchmark matrix by recording the
scene-heavy rows measured in Goal3872 as machine-readable profiles.

This keeps the current benchmark story precise:

- cold prepare vs hot query is explicit;
- every profile has a prepared-session cache key;
- every profile has explicit lifetime and invalidation policy;
- no hidden automatic partner/backend selection;
- not a true-zero-copy or public speedup claim;
- app-specific native-engine logic remains forbidden.

## What Changed

Added `src/rtdsl/current_prepared_session_residency_profiles.py`.

The registry covers the four Goal3872 rows:

| App | Generic primitive | Prepare sec | Hot query sec | Ratio |
| --- | --- | ---: | ---: | ---: |
| Hausdorff/X-HD | `fixed_radius_threshold_2d` | 0.743487 | 0.010264 | 72.436x |
| LibRTS spatial index | `aabb_index_query_2d` | 0.402613 | 0.029665 | 13.572x |
| RTNN | `fixed_radius_neighbors_3d_ranked_summary` | 1.702647 | 0.000133 | 12757.870x |
| Triangle counting | `ray_triangle_weighted_any_hit_sum_3d` | 0.391839 | 0.000150 | 2605.920x |

The profiles are exported through `rtdsl.__init__`:

- `current_prepared_session_residency_profiles`;
- `summarize_current_prepared_session_residency_profiles`;
- `validate_current_prepared_session_residency_profiles`;
- `CurrentPreparedSessionResidencyProfile`;
- profile version/status/boundary constants.

## Boundary

This registry is not a benchmark release packet. It is an internal current-row
profile registry. It does not authorize release action, public speedup wording,
broad RT-core wording, true-zero-copy wording, automatic partner/backend
selection, or app-specific native-engine logic.

The app names appear only as benchmark-row identifiers. The prepared primitives
remain generic and app-agnostic.

## Why This Matters

The A5000 evidence says the next important performance direction for these
rows is prepared-session residency and amortization, not local per-query
micro-tuning. A user or benchmark runner should be able to say:

1. This is the cold preparation phase.
2. This is the hot prepared-query phase.
3. This is the explicit key/lifetime/invalidation policy for reuse.
4. This is only internal evidence unless a later release packet authorizes
   public wording.

Goal3874 makes those facts queryable from Python instead of burying them in a
single report table.

## Validation

Added `tests/goal3874_current_prepared_session_residency_profiles_test.py`.

The test checks:

- the profile registry covers all four Goal3872 rows;
- every row validates through the Goal3873 prepared-session contract;
- every row has ratio `>= 10x` and reuse recommendation enabled;
- all claim flags remain false;
- primitive names do not contain app-shaped terms;
- the summary preserves the Goal3872 geomean ratio scale.
