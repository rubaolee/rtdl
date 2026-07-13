# Call For Review: Goal5237 Graphics Dragon -> AsianDragon Scaled All-Source Route-Only

Please strictly review Goal5237.

## Files To Review

```text
history/internal_docs/goal5237_graphics_dragon_asian_dragon_scaled_all_source_route_only_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_no_translate_pod_2026-07-09.json

history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
history/internal_docs/goal5236_graphics_dragon_asian_dragon_scaled_optix_pod_bounded_gate_result_2026-07-09.md
```

## Context

Goal5234 proved that raw public AsianDragon does not match the paper log, while
an app-owned scaled `0.001` public candidate matches the author paper-log
HDResult within `1e-6`.

Goal5236 proved bounded POD OptiX source subsets for Dragon -> scaled
AsianDragon match exact subset oracles.

Goal5237 attempts the full source set. It uses `--skip-exact-oracle` because
the full exact pair oracle is not practical, and compares the route result to
the author scaled-public HDResult from Goal5234.

## Claims Under Review

1. The successful Goal5237 route is an all-source route over `437,645` source
   points and `3,609,600` target points.
2. The successful route matches the author scaled-public HDResult within
   `1e-6`.
3. The route was run against the current-source rebuilt POD OptiX library from
   Goal5236, not the old POD snapshot.
4. The two diagnostic no-go runs correctly identify required execution-mode
   constraints:
   - independent min-bound translation is required for the author-compatible
     route;
   - global-bound early break must be disabled for exact-value all-source
     reproduction.
5. Goal5237 does not prove exact paper input byte identity, Figure 6, or
   performance parity.

## Review Questions

1. Does the passing JSON prove `full_all_source_route_run=true`, author
   comparator match, and no full pairwise materialization?
2. Is it valid to call the result "all-source route-only HDResult match" while
   still refusing full paper reproduction and exact paper input claims?
3. Does the translated+early-break no-go run justify forbidding
   `global_bound_early_break` in exact-value reproduction mode?
4. Does the no-translate no-go run justify documenting independent min-bound
   translation as part of the current app-owned author-compatible preprocessing
   contract, or does it require deeper author-source provenance before being
   accepted?
5. Is `per_source_witness_exact=true` in the successful route sufficient to
   remove the earlier per-source witness caveat for this exact-mode run?
6. Is the timing evidence usable only as route accounting, not as an
   author-vs-RTDL performance claim?
7. What should be the next required goal: performance matrix, preprocessing
   provenance audit, or another paper workload?

## Expected Answer Shape

```text
Verdict:
  approve_goal5237_scaled_all_source_route_only
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```

## Forbidden Summaries

Reject any summary that says:

```text
X-HD full paper reproduction is complete.
RTDL proved exact paper input byte identity.
RTDL reproduced Figure 6.
RTDL matched author performance.
Global-bound early break is exact for all-source reproduction.
The no-translate route matched author.
```
