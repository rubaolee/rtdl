# Call For Review: Goal5211 Global-Bound Early-Break

Please strictly review Goal5211.

## Files To Review

```text
history/internal_docs/goal5211_global_bound_early_break_result_2026-07-09.md
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5211_global_bound_early_break_contract_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat1_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat2_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5211_global_bound_repeat3_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

## Review Questions

1. Is the new native v5 ABI compatibility-preserving for v1-v4 callers?
2. Is `global_bound_early_break` app-neutral, or does it smuggle X-HD-specific
   semantics into RTDL core?
3. Is the global-bound early-break correctness argument valid for
   max-nearest / directed-Hausdorff reductions?
4. Does the report correctly disclose that per-source witnesses may be
   approximate for early-aborted sources?
5. Do the POD artifacts prove the Level-B Dragon/HappyBuddha route still matches
   the Goal5186 author HDResult?
6. Are the fresh and explicit-warm regimes reported separately, without using a
   warm result as the fresh headline?
7. Is the performance improvement real relative to the relevant recent
   baselines, or is it a measurement-boundary artifact?
8. Are the early-break counts and native timings sufficient to explain the
   speedup mechanism?
9. Should this remain explicit pending review, or is it safe to make the X-HD
   Level-B route default after review?
10. Are there missing tests or safety checks before closing Goal5211?

## Expected Verdict Labels

Use one:

```text
approve_goal5211_global_bound_early_break_route_win
approve_with_required_amendments
block_due_to_incorrect_max_nearest_contract
block_due_to_xhd_specific_core_leak
block_due_to_regime_or_measurement_boundary_error
```

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```
