# Phoenix V3 AABB Native Query-Handle Runner Route M2

Date: 2026-06-22
Status: `m2_aabb_native_query_handle_runner_contract_validated_not_release`

## Summary

Phoenix V3 Gap 1 requires the productized prepared execution/session path to
actually execute on more than one Set-A primitive family before another
all-app pod run. This M2 step routes the generic
`aabb_index_query_2d_native_query_handle` family through the same runner used
by the earlier fixed-radius self-query route.

This is local contract evidence only. It is not pod performance evidence and
does not authorize V3 release, public speedup wording, broad V3-over-V2
wording, or another full all-app rerun.

## M2.1 Route Wiring Update

Status: `m2_1_aabb_runner_backed_contact_route_validated_not_release`

The helper is now wired into a real AABB-bearing benchmark route:

- `examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
  - `aabb_broadphase_witness_rows` uses
    `run_aabb_index_query_2d_range_intersection_prepared_session` for
    Embree/OptiX prepared repeat paths.
  - repeated measured runs reuse one explicit `ExplicitPreparedSessionCache`;
    the first call is the cold prepare path, later calls are cache-hit runner
    executions.
  - the benchmark payload now records
    `prepared_execution_session_runner_used: true`,
    `productized_execution_path: prepared_execution_session_runner`, and
    `prepared_execution_session_runner_metadata`.
- `scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py`
  - the AABB prepare-reuse summary now checks
    `productized_runner_visible_for_prepared_backends` for Embree/OptiX
    payloads.

This closes the M2 "helper not wired into a real benchmark route" gap. It does
not create pod performance evidence by itself. The existing 2026-06-21 AABB
pod rows predate this route binding and must not be reinterpreted as
runner-backed evidence without a focused rerun.

## Code

- `src/rtdsl/prepared_execution.py`
  - added `run_aabb_index_query_2d_range_intersection_prepared_session`
  - uses `run_prepared_execution_session`
  - records `runtime_executed: true`
  - records `primitive_family: aabb_index_query_2d_native_query_handle`
  - records `productized_execution_path: prepared_execution_session_runner`
  - keeps release/public/broad/true-zero-copy/automatic-selection flags false
- `src/rtdsl/__init__.py`
  - exports the helper for stable runtime use

## Validation

Focused tests:

```text
py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 8 tests
OK

py -3 -m unittest tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test tests.v3_phoenix_prepared_execution_session_runner_test
Ran 13 tests
OK
```

The new AABB contract test verifies:

- one prepare call across first and second runner calls;
- the second call is a prepared-session cache hit;
- `runtime_executed` is true;
- explicit backend is `optix`;
- explicit partner is `none`;
- row contract is `generic_prepared_aabb_index_query_2d_native_query_handle`;
- output rows and validation oracle are preserved;
- all release/public/broad/true-zero-copy/automatic-selection flags remain false.

The route-wiring test verifies:

- the Contact Manifold AABB route calls the productized prepared-session
  runner in repeat mode;
- the fake native handle prepares once, executes warmup plus three measured
  runner calls, and closes through `ExplicitPreparedSessionCache.clear`;
- runner metadata records `runtime_executed_count: 3` and `cache_hit_count: 2`;
- the payload keeps `productized_execution_path: prepared_execution_session_runner`;
- correctness against the benchmark CPU oracle is preserved;
- release/public/broad flags remain false.

## Boundaries

This M2 step does not claim:

- material speedup;
- whole LibRTS/contact-manifold acceleration;
- public AABB speedup;
- public Spatial/RayJoin speedup;
- true zero-copy;
- automatic backend or partner selection;
- package/install readiness;
- V3 release readiness.

It also does not count as a full Set-A performance win yet. The helper proves
runner-path breadth at contract level, and M2.1 proves the route is observable
inside a real benchmark harness. Focused same-pod A/B evidence through this
new runner-backed route is still required before it can be treated as runtime
performance progress.

## Next Step

Run focused same-pod A/B for the now runner-backed AABB route. Do not reuse the
older AABB pod result as runner-backed evidence unless it is rerun through the
updated route. Do not run the full all-app suite until at least two Set-A probes
have `runtime_executed: true` and focused material evidence.

## Goal-Level Decision Self-Audit

Decision: route AABB native query-handle through the prepared execution/session
runner as Phoenix M2.

1. Was I foolish? No for this decision.
2. If yes, what actions made the decision foolish? The foolish action would
   have been adding another app-specific LibRTS or contact-manifold shortcut
   instead of a generic AABB runner helper.
3. Was there another path? Yes. I could have made more grouped-stream variants
   or rerun all-app immediately, but that would repeat the previous failure:
   local rows without a reusable runtime path.
4. Can I now try a different path? Yes. The current path is to keep release
   blocked, prove runner execution across reusable Set-A families, and only
   spend pod time on focused route A/B once the benchmark route actually uses
   the productized helper.
