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
