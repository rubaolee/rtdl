# Goal3884 Prepared-Session Reuse Tutorial

## Purpose

Goals 3872-3882 moved prepared-session residency from timing evidence into a
generic runtime contract and live benchmark metadata. Goal3884 adds the learner
page for that surface so users can understand the pattern without reading
internal reports. This responds to the Goal3881/Goal3883 review gap by showing
the explicit cache hit/miss mechanics, while avoiding any statement that the
pattern is a default recommendation or a speedup claim.

## What Changed

Added `docs/learn/prepared_session_reuse.md`.

Updated:

- `docs/tutorials/README.md`
- `docs/learn/README.md`

The new page teaches:

- explicit prepare-once/query-many reuse;
- `make_prepared_session_cache_key`;
- `ExplicitPreparedSessionCache`;
- `get_or_prepare_explicit_session`;
- `prepared_session_residency` app metadata;
- visible invalidation;
- current measured generic primitive shapes.

## Boundary

The tutorial is current v2.10 learner guidance, not a release action, and not a new performance claim.

It explicitly says prepared-session reuse does not authorize:

- release action;
- public speedup wording;
- broad RT-core speedup wording;
- true-zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

The code example keeps backend and partner selection in user code and uses a
generic primitive name rather than an app-shaped native-engine handle.

## Validation

Added `tests/goal3884_prepared_session_reuse_tutorial_test.py`.

The test checks that:

- both learner indexes link to the new page;
- the page names the live API helpers and the `prepared_session_residency`
  metadata field;
- the page documents explicit invalidation and the claim boundary;
- the page avoids forbidden public-claim wording;
- a minimal explicit prepared-session cache example executes against the live
  `rtdsl` API and records miss/put/hit events.
