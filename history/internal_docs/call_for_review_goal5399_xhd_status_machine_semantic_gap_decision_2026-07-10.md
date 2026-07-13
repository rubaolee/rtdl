# Call For Review - Goal5399 X-HD Status-Machine Semantic Gap Decision

Please strictly review Goal5399.

## Files To Review

Decision report:

```text
history/internal_docs/goal5399_xhd_status_machine_semantic_gap_decision_2026-07-10.md
```

Primary evidence:

```text
history/internal_docs/goal5398_xhd_native_v7_status_stream_parity_gate_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5398_native_v7_status_stream_parity_gate_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
```

Relevant source surfaces:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace_v2.py
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/active_query_status.py
```

## Review Questions

1. Does Goal5399 correctly identify the Goal5398 mismatch as semantic rather
   than a simple ABI/hash/remap bug?
2. Does the report correctly characterize the author trace as raw shader
   offload append rows before load-balance reduce?
3. Does the report correctly characterize the current RTDL v7 stream as rows
   emitted at the existing generic frontier emission point?
4. Is it correct to reject hard-coding 62 rows per active query?
5. Is it correct to reject claiming explicit `-lb` support from scalar
   correctness?
6. Is authorizing one more generic status-state-machine spike reasonable, or
   should the line stop now?
7. Does the proposed Goal5400 scope remain generic enough for RTDL core/native?
8. Are the fail-closed exit labels and forbidden summaries strong enough to
   prevent overclaiming Figure 7/11 or full paper reproduction?

## Expected Answer Shape

Please respond with:

```text
Verdict:
  approve_goal5399_authorize_generic_status_state_machine_spike
  OR approve_with_required_amendments
  OR revise_goal5399

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 8 review questions:
  ...
```

## Proposed Verdict

```text
approve_goal5399_authorize_generic_status_state_machine_spike
```
