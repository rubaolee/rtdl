# Goal3873 Prepared-Session Residency Contract

## Purpose

Goal3872 showed that several current scale-profile rows are dominated by
one-time scene or payload preparation while hot prepared queries are much
smaller:

- Hausdorff/X-HD threshold: prepare/query ratio about `72x`.
- LibRTS AABB index: prepare/query ratio about `14x`.
- RTNN ranked summary: prepare/query ratio about `12758x`.
- Triangle counting summary: prepare/query ratio about `2606x`.

Goal3873 turns that measurement into a generic runtime contract. The next
engineering target is not another per-row tweak; it is prepared-session
residency with a visible prepared-session cache key, explicit lifetime and
invalidation, and cold prepare vs hot query accounting.

## What Changed

Added `src/rtdsl/prepared_session_residency.py`.

The new module provides:

- `RtdlPreparedSessionCacheKey`: a stable, explicit key over primitive,
  backend, partner, device, input fingerprints, and parameter fingerprints.
- `RtdlPreparedSessionResidencyPolicy`: cache/lifetime/invalidation policy for
  an explicit user session.
- `RtdlPreparedSessionTimingRecord`: cold prepare vs hot query timing metadata.
- `ExplicitPreparedSessionCache`: a small caller-owned cache that records hits,
  misses, evictions, and explicit invalidation events, and closes cached handles
  when invalidated.
- Contract helpers:
  `describe_prepared_session_residency_contract`,
  `validate_prepared_session_residency_contract`,
  `make_prepared_session_cache_key`, and
  `summarize_prepared_session_timing_records`.

The helpers are exported through `rtdsl.__init__` so app authors can use the
same explicit contract from benchmark code or tutorials.

## Boundary

This is not a hidden dispatcher and not a global cache. Callers must provide
the primitive, backend, partner, device, input fingerprints, and parameters.
The cache does not build scenes by itself and does not choose a partner or
backend.

Guardrails:

- no hidden automatic partner/backend selection;
- explicit lifetime and invalidation;
- not a true-zero-copy or public speedup claim;
- app-specific native-engine logic remains forbidden;
- release, public speedup, broad RT-core, true-zero-copy, automatic partner
  selection, and app-specific native-engine authorization flags all remain
  `False`.

The native engine remains app-agnostic. The module rejects app-shaped primitive
names such as old benchmark or domain terms and expects generic primitive names
like fixed-radius threshold summary, AABB index query, ranked neighbor summary,
or ray/triangle weighted sum.

## Effect

The project can now distinguish three things that were easy to mix together:

1. Cold preparation: scene construction, payload import, handle creation, or
   JIT/initialization.
2. Hot query: repeated requests against an explicit prepared session.
3. Cache policy: caller-visible reuse keyed by stable fingerprints with
   explicit invalidation.

This makes the next performance work cleaner. Future benchmark rows can report
prepared-session residency without implying that a cache hit is a public speedup
claim or that RTDL is doing hidden partner/backend selection.

## Validation

Added `tests/goal3873_prepared_session_residency_contract_test.py`.

The test checks:

- the contract requires explicit cache keys, visible invalidation, and cold/hot
  phase split;
- all claim-authorization flags remain false;
- cache keys are stable under input ordering;
- app-shaped primitive names are rejected;
- explicit cache hit/miss/invalidation events are recorded;
- invalidation closes cached handles;
- Goal3872 timing ratios can be summarized without authorizing release,
  speedup, or true-zero-copy claims.
