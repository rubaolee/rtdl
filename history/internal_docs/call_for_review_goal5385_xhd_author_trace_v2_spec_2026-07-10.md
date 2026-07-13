# Call For Review: Goal5385 X-HD Author Trace V2 Spec

Please strictly review Goal5385.

## Files To Review

Builder and artifact:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5385_author_trace_v2_spec.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5385_author_trace_v2_spec.json
```

Tests:

```text
tests/goal5385_author_trace_v2_spec_test.py
```

Result:

```text
history/internal_docs/goal5385_xhd_author_trace_v2_spec_result_2026-07-10.md
```

Context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb_status_trace_oracle.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5384_multiround_status_requirements.json
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5384_xhd_multiround_active_query_status_result_2026-07-10.md
```

## Review Questions

1. Does Goal5385 correctly identify the limitation of the current Goal5374
   author oracle as count-only and insufficient for multi-round row/state
   parity?
2. Are the proposed author trace v2 fields sufficient to compare RTDL
   multi-round active-query status streams against the author `-lb` behavior?
3. Does the spec include both row-count information and row-identity evidence
   (`raw_offload_row_hash` plus samples or optional full dump)?
4. Does it include per-round cmin2/current-best state evidence before ray,
   after ray, and after load-balance?
5. Does it include loadBalanceProcessing feedback evidence instead of treating
   raw offload append counts as the whole algorithm?
6. Is the dump policy realistic for the observed `27133990` raw offload rows
   and `217071920` author-width bytes?
7. Does the patch scope remain author-app-owned and avoid modifying RTDL core?
8. Does the result avoid claiming that author v2 trace is already implemented
   or executed on POD?
9. Does it preserve the boundary that explicit `-lb`, Figure 7, Figure 11,
   performance ratios, and full X-HD reproduction remain unclaimed?
10. Is the recommended next step correct: implement the author v2 patch or a
    native generic multi-round stream, not more single-pass prune-mode probes?

## Expected Answer Shape

```text
Verdict:
  approve_goal5385_author_trace_v2_spec
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  1. ...
  ...
  10. ...
```

## Requested Verdict If Clean

```text
approve_goal5385_author_trace_v2_spec__next_patch_or_native_stream
```
