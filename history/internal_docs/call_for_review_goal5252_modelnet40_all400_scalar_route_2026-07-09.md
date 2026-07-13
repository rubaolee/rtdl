# Call For Review - Goal5252 ModelNet40 All-400 Scalar Route

Please strictly review Goal5252:

```text
history/internal_docs/goal5252_modelnet40_all400_scalar_route_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5252_modelnet40_all400_scalar_route_full_artifacts_2026-07-09.tar.gz
```

## Context

Goal5252 extends the current X-HD scalar `HDResult` route to all 400 unique
ModelNet40 pair identities represented in the author paper-branch log index.

Result:

```text
matched_case_count = 400
failed_case_count = 0
all_cases_matched = true
max author_abs_diff = 6.59728109919655e-08
tolerance = 1e-6
```

This result depends on two route repairs:

```text
Goal5251: native global-bound publish safety fix
Goal5252: missing-nearest fallback using generic pairwise + nearest helpers
```

The missing-nearest fallback is a correctness safety net:

```text
fallback cases = 5 / 400
fallback source rows total = 1,988
fallback candidate rows total = 31,961,946
largest fallback case = tent_0112.off -> tent_0183.off
largest fallback route_wall_sec = 78.96278008818626
```

## Review Questions

1. Does the aggregate evidence really support 400/400 matched unique
   ModelNet40 pair identities?
2. Is the claim boundary correct: scalar `HDResult` author-rerun coverage, not
   full paper reproduction?
3. Is the report clear that `per_source_witness_exact=false` remains a critical
   caveat?
4. Is the missing-nearest fallback generic enough, or does it introduce
   X-HD-specific app behavior into RTDL?
5. Does the fallback distribution show a real performance tail that must not be
   hidden by median route time?
6. Are the performance denominators presented fairly:
   - RTDL route wall;
   - RTDL total wall;
   - author process wall;
   - author internal `Running.AvgTime`?
7. Is it acceptable to state that all 400 unique ModelNet40 pair identities are
   covered, while avoiding the broader "all paper records" claim unless the
   Goal5230 duplicate mapping is also accepted?
8. Does Goal5252 supersede the earlier selected ModelNet40 scalar-route
   evidence from Goals5248-5251?
9. Is the tent fallback outlier correctly identified as the next performance
   mountain?
10. Are any further amendments required before this can be used as the current
    ModelNet40 scalar-route correctness anchor?

## Expected Answer Shape

```text
Verdict:
  approve_goal5252...
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
