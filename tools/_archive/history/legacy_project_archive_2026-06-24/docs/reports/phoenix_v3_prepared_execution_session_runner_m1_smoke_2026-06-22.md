# Phoenix V3 Prepared Execution Session Runner M1 Smoke

Date: 2026-06-22
Status: `m1_generic_runner_smoke_validated_not_release`

## Summary

This report records the first concrete Gap-1 implementation step after Claude's
`approve_blocked_not_release` review.

Files changed:

- `src/rtdsl/prepared_execution.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`

The new M1 runner is deliberately small and generic:

- caller supplies the primitive name, backend, partner, cache, prepare
  function, run function, and optional validation function;
- runner builds an explicit prepared-session key using the existing
  `prepared_session_residency` contract;
- runner executes the prepared operation and records prepare/cache/warmup/
  executor/validation phases through the existing prepared-execution report;
- runner reports `runtime_executed: true`;
- runner records conservative `validation_passed` status when validation
  returns a bool or a mapping of bool checks;
- runner records all release/public/broad/zero-copy/automatic-selection flags
  as false;
- runner rejects app-shaped primitive names through the existing generic
  prepared-session primitive-name guard.

This is not a speed result. It does not authorize release or public wording.

## Why This Matters

Claude's review correctly identified Gap 1 as the parent blocker: V3 has many
prepared/session/continuation pieces, but no productized execution path that
actually owns the loop. This runner is the first small runtime surface for that
path.

It is intentionally not an app engine. The benchmark apps remain probes only.

## Validation

New runner tests:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
4 tests OK
```

Combined review/intake/selection/runner tests:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_phoenix_next_dominant_hotpath_selection_test \
  tests.v3_phoenix_prepared_execution_session_runner_test

19 tests OK
```

Release-boundary gates:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_major_performance_mandate_gate_test \
  tests.v3_phoenix_release_readiness_gate_test \
  tests.v3_release_wording_gate_test

9 tests OK
```

Related legacy prepared/session tests also passed during development:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal756_prepared_db_app_session_test \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.v3_phoenix_next_dominant_hotpath_selection_test

26 tests OK, 2 skipped
```

Follow-up binding report:

```text
docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md
status: m1_1_fixed_radius_self_query_runner_binding_validated_not_release
```

## Non-Claims

This packet does not claim:

- V3 is release-ready.
- V3 broadly beats V2.x.
- The new runner improves performance yet.
- The new runner was wired into a real benchmark route by this M1 smoke packet.
- True zero-copy is implemented.
- Automatic backend or partner selection is authorized.
- V4/C ABI/embedding scope belongs in Phoenix V3.

## Next Work

This M1 smoke packet is superseded by the M1.1 fixed-radius self-query binding
packet for the first real generic primitive binding. The next step is not more
local smoke testing. The next step is to make a runner-backed primitive visible
inside one real Set-A probe route and only then prove it on pod:

1. Wire a runner-backed primitive into one reusable Set-A probe route, starting
   with fixed-radius self-query or grouped/component continuation.
2. Record focused same-pod A/B evidence with `runtime_executed: true`.
3. Repeat on a second Set-A probe before another all-app paired run is
   justified.
4. Freeze Set A / Set B classification before any full pod rerun.

## Goal-Level Decision Audit

Decision: land a minimal generic prepared execution/session runner as Gap-1 M1
work, while keeping release blocked.

1. Was I foolish?
   No for this decision. It follows Claude's redirect by moving from cache
   hygiene toward an execution path that actually executes.
2. If yes, what actions made the decision foolish?
   The foolish action would be to call this performance progress before a real
   primitive flows through it and focused pod evidence exists.
3. Was there another path that would have avoided getting stuck on this idea?
   Yes: keep polishing symbol/cache regressions. That path has already been
   measured and mostly reaches parity, not major-version value.
4. Can I now try a different path that actually solves the problem?
   Yes. Use this runner as the runtime spine, route real Set-A primitives
   through it, and require pod evidence before any release or speed claim.
