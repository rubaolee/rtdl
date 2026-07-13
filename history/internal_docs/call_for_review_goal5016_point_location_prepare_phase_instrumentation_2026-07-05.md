# Call For Review - Goal5016 Point-Location Prepare Phase Instrumentation

Please review:

- `history/internal_docs/goal5016_point_location_prepare_phase_instrumentation_result_2026-07-05.md`
- `history/internal_docs/goal5016_prepare_timing_top4_fastpack_v2.json`
- `history/internal_docs/goal5016_prepare_timing_top4_fastpack_v2.log`

## Requested Verdict

`approve_goal5016_prepare_phase_instrumentation_and_authorize_prepared_base_locator_reuse_measurement`

## Context

The owner asked to continue attacking the v2.14.3 performance problem without
regime sleight-of-hand. Prior review established that:

- fresh one-shot must remain honest;
- prepared replay cannot be relabeled as query-many;
- device-resident-carrier is stopped until payoff is demonstrated;
- the real prepared/query-many path needs distinct-input evidence.

Goal5016 does not optimize yet. It adds native/Python timing visibility for the
generic directed point-location prepare path so the next optimization targets
the real floor.

## Review Questions

1. Does Goal5016 add measurement instrumentation only, without changing
   point-location semantics?
2. Is the extended timing API generic directed point-location / planar-map
   infrastructure rather than a RayJoin overlay kernel?
3. Does the Python wrapper correctly capture prepare timing per prepared handle,
   avoiding the thread-local "last prepare wins" bug?
4. Does the POD evidence show that point-location traversal is tiny and prepare
   workspace construction is the real cost?
5. Is the top4 result correctly interpreted as a fast-pack writer-free route,
   not a stopped device-resident-carrier result?
6. Is the OptiX 9.1 vs 8.1 POD build note handled honestly as a toolchain
   issue rather than a performance result?
7. Does the result avoid 10x, author parity, fresh speedup, and true-zero-copy
   claims?
8. Is the proposed next goal correct: measure prepared-base locator reuse across
   distinct same-domain query batches?
