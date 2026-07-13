# Call For Review - Goal5376 Status-Machine Candidate Contract

Please strictly review Goal5376.

## Files To Review

Implementation:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
```

Tests:

```text
tests/goal5376_status_machine_candidate_telemetry_test.py
tests/goal5376_status_machine_candidate_contract_artifact_test.py
```

Artifact builder and result:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5376_status_machine_candidate_contract.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5376_status_machine_candidate_contract.json
```

Report:

```text
history/internal_docs/goal5376_status_machine_candidate_contract_result_2026-07-10.md
```

## Context

Goal5374 created an author `-lb` oracle for Dragon -> AsianDragon:

```text
active_in_queue_size = 437645
OffloadingSize / raw offload rows = 27133990
author-width bytes = 217071920
status_count_init = 437645
status_count_offloading = 27133990
cmax2_mbr_abort = 0
point_loop_early_break = 0
```

Goal5375 showed current RTDL surfaces do not match that oracle. The best
candidate remained:

```text
goal5365_full_cover_lb256_behavior_gate_surface
rows = 24508120
absolute row delta = 2625870
row_count_parity = false
```

Goal5376 does **not** claim to solve `-lb`. It introduces a generic RTDL
status-shaped telemetry surface so the current cell-MBR frontier producer can be
compared against the author oracle without app-specific hooks or overclaiming.

## Review Questions

1. Does `optix_runtime.py` expose a generic, app-neutral
   `status_machine_candidate_telemetry.v1` surface rather than an X-HD-specific
   primitive?
2. Does `partner_continuations.py` correctly pass `status_machine_telemetry` and
   `status_machine_telemetry_collected` through the public columnar front-door?
3. Are the fields correctly labeled as RTDL candidate/analog fields, especially
   `active_in_queue_size`, `point_loop_early_break_count`, and
   `current_best_state_source`?
4. Does the implementation avoid claiming explicit X-HD `-lb` support, row-count
   parity, same-denominator memory parity, Figure 7/11 reproduction, or
   performance parity?
5. Does the artifact preserve the Goal5374 oracle numbers and Goal5375 negative
   parity result?
6. Are the focused tests sufficient for this contract-level goal?
7. Is it acceptable that no full POD route probe is claimed yet, given that this
   goal is contract + local passthrough and the next step must sync/build before
   using the telemetry remotely?
8. Should the next goal be a real RTDL status-machine mode/probe that attempts
   row parity against the Goal5374 author oracle?

## Expected Answer Shape

Please answer with:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
```

Suggested verdict if approved:

```text
approve_goal5376_status_machine_candidate_contract__real_lb_mode_still_required
```
