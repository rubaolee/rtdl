# Call For Review - Goal5253 ModelNet40 All-400 Exact-Seed Witness Route

Please strictly review Goal5253:

```text
history/internal_docs/goal5253_modelnet40_all400_exact_seed_witness_route_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_artifacts_2026-07-09.tar.gz
```

## Context

Goal5252 proved the fast scalar global-bound route on all 400 unique ModelNet40
pair identities, but retained this caveat:

```text
per_source_witness_exact = false
```

Goal5253 runs a slower exact-seed route:

```text
initial_state = grid-branch-bound
grid_branch_bound_seed_executor = native_cuda
skip_frontier_if_exact_seed = true
```

Result:

```text
matched_case_count = 400 / 400
failed_case_count = 0
max author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = true for 400 / 400
missing_nearest_fallback_count = 0 for 400 / 400
```

Performance:

```text
route_wall_sec sum = 424.56292333453894
route_wall_sec median = 0.6934860087931156
route_wall_sec max = 13.780185401439667
```

## Review Questions

1. Does the evidence support 400/400 matched unique ModelNet40 pair identities?
2. Do the route JSONs support `per_source_witness_exact=true` for all 400
   cases?
3. Is it correct to present Goal5253 as functionally stronger than Goal5252,
   while slower overall?
4. Is the batch harness change (`--skip-frontier-if-exact-seed`) a valid
   passthrough of an existing generic route gate capability?
5. Does the tent outlier comparison support the conclusion that exact-seed skip
   is a better functional fallback than pairwise missing-nearest fallback?
6. Are performance denominators separated fairly?
7. Does the report avoid claiming author RT-core algorithm equivalence?
8. Should the project carry two labels:
   - fast scalar route;
   - exact witness route?
9. Does Goal5253 supersede Goal5252 for functional completeness, while not
   superseding it for scalar-route speed?
10. Are any amendments required before this is used as the current ModelNet40
    exact-witness correctness anchor?

## Expected Answer Shape

```text
Verdict:
  approve_goal5253...
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Question answers:
  1. ...
  ...
```
