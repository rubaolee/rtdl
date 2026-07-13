# Call For Review: Goal5247 Scalar Global-Bound Native-Grid Route

Please strictly review Goal5247.

## Files Under Review

Result report:

```text
history/internal_docs/goal5247_scalar_global_bound_native_grid_route_result_2026-07-09.md
```

Evidence JSON:

```text
history/internal_docs/goal5247_native_grid_global_bound_repeat1_2026-07-09.json
history/internal_docs/goal5247_native_grid_global_bound_repeat2_2026-07-09.json
history/internal_docs/goal5247_native_grid_global_bound_repeat3_2026-07-09.json
```

Related prior reports:

```text
history/internal_docs/goal5246_native_grid_cell_mbr_builder_result_2026-07-09.md
history/internal_docs/goal5211_global_bound_early_break_result_2026-07-09.md
history/internal_docs/review_xhd_midterm_after_goal5216_2026-07-09.md
```

## Review Questions

1. Do the three POD JSON files prove scalar `HDResult` correctness against the
   author rerun for Dragon -> scaled AsianDragon?
2. Does the report clearly state that `per_source_witness_exact=false` and
   avoid claiming exact per-source witnesses?
3. Is the global-bound shortcut correctly framed as a generic max-nearest scalar
   optimization, not an X-HD-specific primitive?
4. Is it fair to call Goal5247 the current best scalar route for this one
   Level-B workload?
5. Are the author denominator comparisons fair and separated:
   process wall vs internal `Running.AvgTime`?
6. Does the report avoid claiming full paper reproduction, paper-log exactness,
   Figure reproduction, or author internal timing parity?
7. Is the recommendation correct: use this route for scalar HDResult, but carry
   the approximate-witness caveat?
8. What should be the next required proof before broadening the claim:
   second Level-B workload, prepared/reuse study, or author-internal algorithm
   gap analysis?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 8 review questions:
```

Suggested verdict if approved:

```text
approve_goal5247_scalar_global_bound_native_grid_route_with_witness_caveat
```
