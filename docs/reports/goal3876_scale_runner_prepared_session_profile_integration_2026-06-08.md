# Goal3876 Scale Runner Prepared-Session Profile Integration

## Purpose

Goal3874 made prepared-session residency profiles queryable from Python. Goal3876
wires those profiles into the current scale-profile runner so future dry-run
and live benchmark packets carry the relevant cold prepare vs hot query context
without changing any benchmark command.

## What Changed

Updated `scripts/goal3828_current_benchmark_scale_profile_runner.py`.

The runner now:

- imports the current prepared-session residency profile registry;
- attaches `prepared_session_residency_profile` to any selected scale row that
  has a profile;
- marks each row with `prepared_session_residency_profiled`;
- emits top-level `prepared_session_residency_summary`;
- emits top-level `prepared_session_residency_validation`;
- records `selected_prepared_session_residency_profile_count`.

The command execution path is unchanged. This is metadata integration only.

## Boundary

The runner still does not authorize release action, public speedup wording,
broad RT-core wording, true-zero-copy wording, automatic partner/backend
selection, or app-specific native-engine logic.

Guardrail phrase: automatic partner/backend selection remains unauthorized.

Prepared-session profile attachment is not a hidden cache. It records the
explicit prepared-session cache key, lifetime, invalidation policy, and
cold/hot timing profile for rows that already have Goal3872 evidence.

## Validation

Added `tests/goal3876_scale_runner_prepared_session_profile_integration_test.py`.

The test checks:

- dry-run JSON includes the prepared-session summary and validation;
- the full dry-run selects four profiled rows;
- a single selected profiled row carries the profile payload;
- an unprofiled selected row explicitly records `prepared_session_residency_profiled = false`;
- claim-boundary flags remain false.

## A5000 Evidence

Ran the full current scale-profile runner on an RTX A5000 from a fresh clone at
commit `6531d666`.

Artifact:

`docs/reports/goal3876_scale_runner_profile_integration_a5000/summary.json`

Result:

- `all_pass`: `true`
- `json_pass_count`: `10`
- `selected_prepared_session_residency_profile_count`: `4`
- prepared-session profile geomean prepare/hot-query ratio: `425.192605508771`

Profiled rows:

- `hausdorff_xhd_scale_default_optix_threshold`
- `librts_spatial_index_optix_scale_default_32768`
- `rtnn_prepared_optix_scale_default_65536`
- `triangle_counting_optix_rt_graph_2a1_scale_default_2048`

Unprofiled rows remain explicit with
`prepared_session_residency_profiled = false`.
