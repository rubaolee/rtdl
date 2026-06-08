# Goal3886 RTNN Prepared-Session Reuse Idiom

## Purpose

Goal3884 added learner-facing mechanics for explicit prepared-session reuse.
Goal3886 adds a small RTNN app mode that actually calls the same helper from an
example app and records a live miss/put/hit cycle.

This responds to the Goal3881/Goal3883 review gap: prior benchmark payloads
emitted `prepared_session_residency` metadata, but no app called
`get_or_prepare_explicit_session`.

## What Changed

Updated:

- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rtnn/README.md`

Added mode:

`prepared_session_reuse_idiom`

The mode:

- builds a generic `fixed_radius_neighbors_3d_ranked_summary` cache key;
- creates a caller-owned `ExplicitPreparedSessionCache`;
- calls `get_or_prepare_explicit_session` twice;
- records `miss`, `put`, and `hit` events;
- returns the prepared descriptor reused on the second lookup;
- marks `native_runner_invoked = false`;
- marks `performance_evidence = false`.

## Boundary

This is an app-level idiom demo, not a new benchmark timing path.

It does not authorize:

- release action;
- public speedup wording;
- broad RT-core speedup wording;
- true-zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

The promoted OptiX RTNN benchmark mode is unchanged. Goal3886 only gives users
and reviewers a concrete example of the explicit helper mechanics.

## Validation

Added `tests/goal3886_rtnn_prepared_session_reuse_idiom_test.py`.

The test checks:

- the CLI exposes `prepared_session_reuse_idiom`;
- the command produces pure JSON;
- the live helper was invoked;
- the native runner was not invoked;
- the cache event log is exactly `miss`, `put`, `hit`;
- the prepare callable runs once;
- all claim-boundary flags stay false;
- the README and this report document the boundary.
