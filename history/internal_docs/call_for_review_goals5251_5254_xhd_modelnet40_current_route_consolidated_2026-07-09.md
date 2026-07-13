# Consolidated Call For Review - Goals5251-5254 X-HD ModelNet40 Current Routes

Please strictly review the X-HD ModelNet40 current-route packet:

```text
history/internal_docs/goal5251_global_bound_publish_safety_and_modelnet40_batch40_result_2026-07-09.md
history/internal_docs/goal5252_modelnet40_all400_scalar_route_result_2026-07-09.md
history/internal_docs/goal5253_modelnet40_all400_exact_seed_witness_route_result_2026-07-09.md
history/internal_docs/goal5254_modelnet40_route_label_performance_matrix_2026-07-09.md
```

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_chair_global_bound_fixed_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_artifacts_2026-07-09.tar.gz

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_full_artifacts_2026-07-09.tar.gz

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5253_modelnet40_all400_exact_seed_artifacts_2026-07-09.tar.gz

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5254_modelnet40_route_label_performance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/scripts/summarize_modelnet40_route_matrix.py
```

## What This Packet Claims

### Goal5251

The generic global-bound early-break route had an unsafe publish path:

```text
queries with deferred frontier rows could publish an upper bound as if exact
```

Fix:

```text
src/native/optix/rtdl_optix_workloads.cpp
if (kind == 2) {
    optixSetPayload_6(2u);
}
```

Post-fix evidence:

```text
chair_0162.off -> chair_0131.off fixed
batch40 fixed = 40 / 40 matched
largest selected ModelNet40 pair still matched
```

### Goal5252

Fast scalar `HDResult` route:

```text
ModelNet40 all 400 unique pair identities matched author reruns
max author_abs_diff = 6.59728109919655e-08
per_source_witness_exact = false
```

This route has a missing-nearest fallback tail:

```text
fallback cases = 5 / 400
worst fallback = tent_0112.off -> tent_0183.off
worst fallback route_wall_sec = 78.96278008818626
```

### Goal5253

Exact-seed witness route:

```text
ModelNet40 all 400 unique pair identities matched author reruns
per_source_witness_exact = true for 400 / 400
missing_nearest_fallback_count = 0 for 400 / 400
```

This route is functionally stronger but slower:

```text
route_wall_sec sum = 424.56292333453894
route_wall_sec median = 0.6934860087931156
```

### Goal5254

Denominator-explicit performance matrix over identical 400-case sets:

```text
fast scalar route / author process wall sum = 0.571x
exact route / author process wall sum = 1.664x slower

fast scalar route / author internal AvgTime sum = 53.39x slower
exact route / author internal AvgTime sum = 155.51x slower
```

This is not an author-parity claim. It is a route-label performance matrix.

## Critical Boundaries

Allowed:

```text
ModelNet40 all-400 unique-pair scalar HDResult coverage is proven for the fast route.
ModelNet40 all-400 unique-pair exact-witness coverage is proven for the exact route.
Performance comparisons are denominator-separated and route-label-specific.
```

Forbidden:

```text
full X-HD paper reproduction complete
exact paper byte-input identity
Figure 5-11 reproduction
author internal Running.AvgTime parity
author RT-core algorithm equivalence
single unqualified RTDL performance number
```

## Review Questions

1. Is Goal5251's root-cause analysis of unsafe global-bound publication correct?
2. Does `optixSetPayload_6(2u)` on deferred frontier row emission actually
   prevent unsafe bound publication under the existing raygen publish guard?
3. Does Goal5251 sufficiently prove the chair failure was repaired and batch40
   remains matched?
4. Does Goal5252 prove all 400 unique ModelNet40 pair identities match author
   reruns for scalar `HDResult`?
5. Is the Goal5252 missing-nearest fallback generic and acceptable as a
   correctness safety net, while not a performance route?
6. Does Goal5252 correctly preserve the caveat `per_source_witness_exact=false`?
7. Does Goal5253 prove the exact-seed route is exact-witness for all 400 cases?
8. Is Goal5253 correctly framed as functionally stronger but slower, not as a
   performance win?
9. Does Goal5254 correctly require identical case sets and distinguish route
   labels?
10. Are author process wall and author internal `Running.AvgTime` kept as
    separate denominators?
11. Are the ratio interpretations fair, or do any still risk misleading readers?
12. Should future X-HD summaries be required to name either:

```text
fast scalar route
exact-witness route
```

13. Can Goals5251-5254 become the current ModelNet40 correctness/performance
    anchor for X-HD, with the stated boundaries?
14. What, if anything, must be amended before this packet is used in the final
    X-HD reproduction status report?

## Expected Answer Shape

```text
Verdict:
  approve_goals5251_5254_xhd_modelnet40_current_route_packet
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
  14. ...
```
