# Call For Review: Goal5206 Frontier First-Use vs Warm Diagnostic

Date: 2026-07-08

Please strictly review Goal5206.

Files under review:

```text
history/internal_docs/goal5206_frontier_first_use_vs_warm_diagnostic_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_current_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_all_then_minus1_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_minus1_then_all_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_numba_serial_seed_one_shot_control_graphics_dragon_happy_buddha_2026-07-08.json
```

## Reviewer Questions

1. Do all diagnostic artifacts still match the Goal5186 author HDResult?
2. Does the current single-case phase timing correctly show:

```text
route_wall ~= 1.169s
frontier_rows ~= 0.740s
native_total ~= 0.600s
optix_launch ~= 0.379s
```

3. Does the same-process two-case diagnostic fairly separate first-use overhead
   from steady route work using near-identical `all` and `437644` source
   limits?
4. Do both two-case orderings support the same conclusion:

```text
first case route ~= 1.17s
second case route ~= 0.61s
first-use seed ~= 0.23s -> warm seed ~= 0.02-0.03s
first-use native total ~= 0.60s -> warm native total ~= 0.39s
```

5. Does the result correctly keep the fresh/one-shot headline at Goal5205
   (`route ~=1.16-1.17s`, total `~=2.06s`) rather than replacing it with the
   warm diagnostic `~=0.61s`?
6. Does the result correctly state that steady OptiX launch / inline scan
   remains about `0.37-0.38s`, so a real route optimization must target that
   execution floor or expose an explicit prepared/warm API?
7. Does the explicit seed-executor control fail to justify replacing the
   current default?
8. Does the result avoid claiming exact paper dataset reproduction, full paper
   reproduction, author performance parity, or author-vs-RTDL performance
   ratio?
9. Is this appropriately classified as a diagnostic/no-go for executor flag
   swapping, not as a new performance optimization?
10. Should Goal5206 close as:

```text
completed_frontier_first_use_vs_warm_diagnostic__fresh_headline_unchanged
```

Expected answer shape:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 questions:
```
