# Call For Review: Goal5383 Active-Initial-Best Status Probe

Date: 2026-07-10

Please strictly review Goal5383.

## Files To Review

Result report:

```text
history/internal_docs/goal5383_active_initial_best_status_probe_result_2026-07-10.md
```

Native/runtime changes:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
```

App-owned runner:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_active_query_frontier_bridge_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py
```

Tests:

```text
tests/goal5383_active_initial_best_status_probe_test.py
```

POD artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_source64_active_initial_best_probe_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_source64_seeded_active_initial_best_probe_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5383_full_seeded_active_initial_best_probe_pod.json
```

Related prior evidence:

```text
history/internal_docs/goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md
history/internal_docs/goal5381_active_query_frontier_bridge_probe_result_2026-07-10.md
history/internal_docs/goal5382_xhd_native_status_machine_stream_design_result_2026-07-10.md
```

## Review Questions

1. Is `active-initial-best-prune` implemented as a generic status probe rather
   than an X-HD-specific native primitive?
2. Does the new mode correctly test the hypothesis that active-query entry
   current-best, rather than traversal-updated payload best, explains the
   offload denominator gap?
3. Are the tests sufficient to prove Python runtime mapping, metadata, v6 use,
   runner support, and app-neutral native naming?
4. Does the app runner's new `--initial-state local-grid-cell` option preserve
   generic boundaries and avoid changing the old Goal5381 default?
5. Are the POD artifacts sufficient to classify this probe as a no-go?
6. Does the full seeded probe correctly show:

```text
RTDL offload rows = 2188225
author rows       = 27133990
row parity        = false
```

7. Is the conclusion correct that bridge/vectorization work remains secondary
   and that the remaining path is either real multi-round status-stream
   semantics or fail-closed `-lb` closeout?
8. Does Goal5383 avoid overclaiming explicit `-lb`, Figure 7/11, performance
   parity, or full paper reproduction?
9. Should this close with:

```text
active_initial_best_probe_no_go__offload_denominator_still_mismatch
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
  approve_goal5383_active_initial_best_probe_no_go
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers:
  1. ...
  ...
  9. ...
```
