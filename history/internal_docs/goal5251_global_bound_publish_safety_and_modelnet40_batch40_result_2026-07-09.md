# Goal5251 - Global-Bound Publish Safety And ModelNet40 Batch40 Result

Date: 2026-07-09

## Verdict

```text
completed_global_bound_publish_safety_fix__modelnet40_batch40_40_of_40_matched
```

Goal5251 fixes a correctness bug in the generic native OptiX global-bound
early-break route and reruns the 40-category ModelNet40 scalar batch.

This is a real correction, not just another batch run. The first batch40 attempt
found one failure:

```text
matched_case_count = 39 / 40
failed case = chair_0162.off -> chair_0131.off
pre-fix scalar route distance = 0.22796002964350456
author HDResult              = 0.22701063752174377
pre-fix abs diff             = 0.0009493921217607892
```

The same chair case with `global_bound_early_break=false` matched:

```text
no-global-bound distance = 0.22701063780710734
author abs diff          = 2.8536356611041924e-10
per_source_witness_exact = true
```

That localized the failure to the global-bound early-break path, not to
ModelNet40 provenance, author comparator choice, or input normalization.

## Root Cause

The native OptiX route published a global max-nearest bound for a query as long
as the ray did not terminate through the global-bound abort path:

```text
if (p5 != 0u && p6 == 0u) publish_global_bound_sq(best_sq)
```

But `p6` did not record whether the query had emitted deferred frontier rows.
For a query that hit a large cell, `best_sq` was only the current upper bound,
not an exact nearest distance. Publishing that upper bound as a global scalar
bound allowed later queries to early-break against a value that was not exact.

## Fix

File changed:

```text
src/native/optix/rtdl_optix_workloads.cpp
```

Fix:

```text
if (kind == 2) {
    optixSetPayload_6(2u);
}
```

This marks queries that emit deferred frontier rows as not safe for global-bound
publication. The raygen already publishes the global bound only when `p6 == 0`.

Meaning:

```text
publish global scalar bound only from queries whose nearest distance has no
deferred frontier work remaining
```

This preserves the app-neutral contract. The fix is about generic max-nearest
global-bound safety, not X-HD or ModelNet40-specific behavior.

Test guard added:

```text
tests/goal5211_global_bound_early_break_contract_test.py
```

## Validation

POD rebuild:

```text
cd /tmp/rtdl_goal5236
make build-optix
```

The build completed successfully.

### Chair Failure Recheck

Same chair pair, with global-bound early-break enabled after the fix:

```text
evidence = Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_chair_global_bound_fixed_2026-07-09.json
matched = true
author_hd_result = 0.22701063752174377
rtdl distance    = 0.22701063780710734
author_abs_diff  = 2.8536356611041924e-10
```

### Fixed Batch40

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5251_modelnet40_scalar_batch40_fixed_artifacts_2026-07-09.tar.gz
```

Result:

```text
selected_count = 40
matched_case_count = 40
failed_case_count = 0
all_cases_matched = true
```

Point-count range:

```text
min total points = 2,307
max total points = 747,309
```

Correctness envelope:

```text
max author_abs_diff    = 3.139302651167242e-08
median author_abs_diff = 8.42380862287051e-09
tolerance              = 1e-6
```

Performance envelope:

```text
route_wall_sec sum    = 5.2887017503380775
route_wall_sec median = 0.09036052599549294
route_wall_sec max    = 0.7171685770153999

total_sec sum         = 16.445522889494896
total_sec median      = 0.31650785356760025
total_sec max         = 1.907470129430294
```

Author denominators for the same 40 cases:

```text
author process_wall_sec sum    = 21.012552723288536
author process_wall_sec median = 0.47194377705454826

author Running.AvgTime sum ms  = 249.875
author Running.AvgTime median ms = 5.62
```

### Fixed Largest Pair Recheck

After the native fix, the largest selected ModelNet40 unique pair still matches:

```text
airplane_0396.off -> airplane_0050.off
total points = 2,726,286
matched = true
author_abs_diff = 1.6001468206017222e-09
route_wall_sec = 1.0067468956112862
total_sec = 7.567300736904144
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5250_modelnet40_scalar_largest1_fixed_artifacts_2026-07-09.tar.gz
```

## Claim Boundary

Allowed:

```text
The generic global-bound early-break route had an unsafe publish path for
queries with deferred frontier rows. Goal5251 fixes it and proves the fixed
route on a 40-category ModelNet40 scalar batch, 40/40 matched, plus the largest
selected ModelNet40 unique pair.
```

Forbidden:

```text
all 400 ModelNet40 scalar-route coverage
exact per-source witnesses
exact paper byte-input identity
Figure reproduction
author internal Running.AvgTime parity
speedup/parity claim
full X-HD paper reproduction complete
```

Critical caveat:

```text
per_source_witness_exact = false
```

The fixed global-bound route is scalar `HDResult` exact for the tested author
comparisons. It is still not an exact per-source witness route.

## Next Step

Send Goal5251 for strict review. If accepted, it supersedes the pre-fix
Goal5249 batch10 and pre-fix Goal5250 largest-pair evidence for current-route
correctness. The remaining major X-HD blockers are:

```text
1. all-400 ModelNet40 scalar-route coverage, if desired;
2. exact per-source witness route performance, if required;
3. exact paper byte-input provenance and Figure reproduction;
4. denominator-aligned performance against author internal timing.
```
