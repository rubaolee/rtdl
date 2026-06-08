# Goal3877 Explicit Prepared-Session Reuse Helper

## Purpose

Goal3873 added the prepared-session residency contract, and Goal3874/3876 made
current benchmark residency profiles visible. Goal3877 adds the small user
ergonomics step: a caller-owned `get_or_prepare_explicit_session(...)` helper.

This lets a user write the intended pattern directly:

1. Build an explicit prepared-session cache key.
2. Provide an explicit cache.
3. Provide the prepare function.
4. Reuse the prepared session on later calls.

The helper never chooses a backend, partner, primitive, or device.

## What Changed

Updated `src/rtdsl/prepared_session_residency.py`:

- added `RtdlPreparedSessionReuseResult`;
- added `get_or_prepare_explicit_session(cache, key, prepare_session, policy=None)`.

The helper:

- checks the caller-owned cache for the caller-provided key;
- calls the caller-provided prepare function only on a miss;
- stores the prepared value in the explicit cache;
- returns the prepared value plus cache-hit/miss metadata;
- rejects mismatched policy/key pairs;
- records cache event-log metadata.

The helper is exported through `rtdsl.__init__`.

## Boundary

This is still explicit prepared-session reuse, not hidden dispatch.

Guardrails:

- no hidden automatic partner/backend selection;
- not a true-zero-copy or public speedup claim;
- app-specific native-engine logic remains forbidden;
- no automatic cache construction;
- no automatic backend, partner, primitive, or device choice.

## Validation

Added `tests/goal3877_explicit_prepared_session_reuse_helper_test.py`.

The test checks:

- first lookup misses and calls the prepare function once;
- second lookup hits and does not call prepare again;
- metadata records `explicit_cache_lookup = true`;
- all claim-authorization flags remain false;
- policy/key mismatch fails closed.
