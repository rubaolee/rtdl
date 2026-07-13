# Call For Review - Goals5357-5362 X-HD Radius / tune_radius Semantics Packet

Please strictly review the complete X-HD radius / `tune_radius` semantics
packet covering Goals5357-5362.

This is a major claim-boundary node. The packet moves from a negative control
that proves the old route was **not** author queue aligned, through an
author-like queue reference/route/wrapper, to a narrow option-surface mapping
for explicit `-tune_radius adaptive`.

## Files To Review

### Reports

```text
history/internal_docs/goal5357_xhd_author_rtdl_radius_trace_comparison_result_2026-07-09.md
history/internal_docs/goal5358_xhd_author_like_radius_queue_reference_result_2026-07-09.md
history/internal_docs/goal5359_xhd_cell_mbr_author_like_queue_route_result_2026-07-09.md
history/internal_docs/goal5360_xhd_hd_exec_author_queue_wrapper_gate_result_2026-07-09.md
history/internal_docs/goal5361_xhd_res4full_nonterminal_author_queue_gate_result_2026-07-09.md
history/internal_docs/goal5362_xhd_tune_radius_option_surface_gate_result_2026-07-09.md
```

### Individual call-for-review files

```text
history/internal_docs/call_for_review_goal5357_xhd_author_rtdl_radius_trace_comparison_2026-07-09.md
history/internal_docs/call_for_review_goal5358_xhd_author_like_radius_queue_reference_2026-07-09.md
history/internal_docs/call_for_review_goal5359_xhd_cell_mbr_author_like_queue_route_2026-07-09.md
history/internal_docs/call_for_review_goal5360_xhd_hd_exec_author_queue_wrapper_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5361_xhd_res4full_nonterminal_author_queue_gate_2026-07-09.md
history/internal_docs/call_for_review_goal5362_xhd_tune_radius_option_surface_gate_2026-07-09.md
```

### Implementation

```text
src/rtdsl/radius_schedule.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5358_author_like_radius_queue_reference.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5359_cell_mbr_author_like_queue_route.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5360_hd_exec_author_queue_wrapper_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5361_res4full_nonterminal_author_queue_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5362_tune_radius_option_surface_gate.py
```

### Evidence artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5357_author_rtdl_radius_trace_comparison.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5358_author_like_radius_queue_reference.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5359_cell_mbr_author_like_queue_route.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5360_hd_exec_author_queue_wrapper_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5360_hd_exec_author_queue_wrapper_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5360_hd_exec_author_queue_explicit_tune_radius_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_wrapper_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_option_surface_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_adaptive_supported_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_double_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_terminal_trace_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_other_author_rt_option_fail_closed.json
```

### Tests

```text
tests/goal5357_author_rtdl_radius_trace_comparison_test.py
tests/goal5358_author_like_radius_queue_reference_test.py
tests/goal5359_cell_mbr_author_like_queue_route_test.py
tests/goal5360_hd_exec_author_queue_wrapper_gate_test.py
tests/goal5361_res4full_nonterminal_author_queue_gate_test.py
tests/goal5362_tune_radius_option_surface_gate_test.py
tests/goal5354_radius_growth_schedule_test.py
tests/goal5355_radius_trace_mapping_test.py
tests/goal5356_route_radius_trace_metadata_test.py
tests/goal5149_cell_mbr_frontier_nearest_continuation_test.py
```

## Packet Narrative To Verify

1. **Goal5357 negative control**: the old single-pass RTDL route matched
   HDResult but did not match author radius queue semantics, so explicit
   `-tune_radius` had to remain fail-closed.
2. **Goal5358 reference**: an app-owned author-like queue reference could
   reproduce the bounded3d author queue row using generic nearest/witness
   primitives.
3. **Goal5359 route**: the cell-MBR route could emit author-like queue rows
   for bounded3d through default-off nearest-column emission.
4. **Goal5360 wrapper**: the `hd_exec`-compatible wrapper exposed that bounded
   queue route under `cell-mbr-author-queue-diagnostic`, while explicit
   `-tune_radius adaptive` still failed closed for the terminal bounded trace.
5. **Goal5361 nonterminal trace**: the wrapper diagnostic route matched a
   res4full nonterminal author queue trace:

   ```text
   5205 -> 4 -> 0
   uses_radius_growth_step = true
   HDResult abs diff ~= 4.44e-09
   ```

6. **Goal5362 narrow option mapping**: explicit `-tune_radius adaptive` is now
   accepted only for the internal diagnostic route with a nonterminal author
   trace. `double`, terminal traces, and other explicit author RT options still
   fail closed.

## Current Authorized Claim If Approved

If and only if this packet is approved, the allowed statement should be:

```text
RTDL's X-HD app-owned hd_exec-compatible wrapper has a narrow internal
diagnostic mapping for -tune_radius adaptive under
cell-mbr-author-queue-diagnostic when a nonterminal author trace is supplied.
The route can reproduce the available bounded terminal and res4full
nonterminal author-like radius queue traces.
```

## Forbidden Claims

Even if this packet is approved, do **not** claim:

```text
general author tune_radius support
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
exact paper dataset reproduction
full X-HD paper reproduction
support for tune_radius double/add
support for lb/prune/eb/tune_grid/n_points_cell/fast_build_bvh/rebuild_bvh
```

## Review Questions

1. Does Goal5357 correctly prove that the old single-pass route was not author
   queue aligned, despite matching HDResult?
2. Does Goal5358's reference derive author-like queue fields from generic
   nearest/witness primitives without turning X-HD semantics into RTDL core?
3. Does Goal5359 genuinely route through cell-MBR internals and emitted nearest
   columns rather than only reusing the reference?
4. Does Goal5360 correctly expose the bounded route through
   `run_xhd_rtdl_hd_exec.py` while keeping explicit `-tune_radius` fail-closed
   on the terminal trace?
5. Does Goal5361 truly exercise a nonterminal trace where `NumOutputPoints > 0`
   and `radius_growth_step` updates Radius?
6. Is Goal5361's required preprocessing (`translate_each_input_to_min_bound`)
   justified by the author JSON MBR and clearly bounded?
7. Does Goal5362 keep `-tune_radius adaptive` support narrow to the internal
   route plus nonterminal author trace?
8. Do Goal5362's fail-closed controls prove unsupported modes/options are not
   accidentally accepted?
9. Are all metadata fields and JSON statuses self-consistent
   (`supported_explicit_author_rt_options`, `unsupported_explicit_author_rt_options`,
   `author_tune_radius_supported`, `uses_radius_growth_step`)?
10. Does the packet preserve app/core boundaries and avoid X-HD-specific
    semantics in RTDL core?
11. Are the tests sufficient for both the positive trace match and the negative
    fail-closed controls?
12. Should this packet close the current radius / `tune_radius` semantics line
    under the narrow internal-diagnostic claim boundary?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve / approve_with_required_amendments / block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
12. ...
```

Suggested approve label if accepted:

```text
approve_goals5357_5362_xhd_radius_tune_radius_semantics_packet
```
