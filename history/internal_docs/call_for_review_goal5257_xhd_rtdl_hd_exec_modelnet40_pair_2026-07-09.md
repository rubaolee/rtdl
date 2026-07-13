# Call For Review - Goal5257 X-HD RTDL hd_exec Entrypoint on ModelNet40 Pair

Please strictly review Goal5257.

## Files Under Review

```text
history/internal_docs/goal5257_xhd_rtdl_hd_exec_modelnet40_pair_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json
tests/goal5257_xhd_rtdl_hd_exec_modelnet40_pod_artifact_test.py
```

Prerequisite context:

```text
history/internal_docs/call_for_review_goals5255_5256_xhd_rtdl_hd_exec_entrypoint_consolidated_2026-07-09.md
history/internal_docs/goal5252_modelnet40_all400_scalar_route_result_2026-07-09.md
history/internal_docs/goal5253_modelnet40_all400_exact_seed_witness_route_result_2026-07-09.md
```

## Context

Goals5255-5256 proved the new RTDL `hd_exec`-compatible runner on bounded
fixtures and live GPU route labels. Goal5257 runs the same user-facing entrypoint
on a real public ModelNet40 OFF pair:

```text
airplane_0036.off -> airplane_0515.off
```

Both RTDL route labels match the corresponding author rerun HDResult within
1e-6 tolerance.

## Questions

1. Does Goal5257 prove that the user-facing RTDL `hd_exec` entrypoint can run on
   a real public ModelNet40 OFF pair, not just bounded WKT fixtures?

2. Is the comparison to the author rerun HDResult valid for this same pair and
   preprocessing contract?

3. Are the two route labels interpreted correctly?

```text
cell-mbr-fast-scalar:
  HDResult matched, per_source_witness_exact=false on this pair

cell-mbr-exact-witness:
  HDResult matched, per_source_witness_exact=true on this pair
```

4. Does the report avoid overclaiming from one ModelNet40 pair to all-400 route
   coverage? Should it state even more strongly that Goals5252-5254 remain the
   all-400 evidence?

5. Is `Running.AvgTime` sufficiently labeled as RTDL route wall time in an
   author-shaped JSON field, not author internal `Running.AvgTime` parity?

6. Do the claim boundaries correctly avoid:

```text
exact paper byte-input identity
Figure reproduction
author RT-core algorithm equivalence
performance speedup/parity
```

7. Are the artifact tests sufficient, or should they assert more nested route
   fields such as grid shape / initial-state / seed executor?

8. Should this goal be accepted as the ModelNet40 user-entrypoint bridge, while
   leaving bulk all-400 coverage to Goals5252-5254?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | revise | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
...
8. ...

Recommended verdict label:
...
```

## Proposed Verdict If Accepted

```text
approve_goal5257_xhd_rtdl_hd_exec_modelnet40_pair_bridge
```
