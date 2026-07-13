# Call For Review: Goal5234 Graphics Dragon -> AsianDragon Scaled Author Gate

Please strictly review Goal5234.

## Files To Review

```text
history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/prepare_xhd_scaled_ply_candidate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
tests/goal5234_xhd_scaled_ply_candidate_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_asian_dragon_scaled_1e-3_candidate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_priority_input_bridge_graphics_dragon_asian_dragon_scaled_1e-3_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_raw_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_scaled_1e-3_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_graphics_dragon_asian_dragon_scaled_1e-3_subset16_numpy_2026-07-09.json
```

Context:

```text
history/internal_docs/goal5232_graphics_dragon_asian_dragon_input_bridge_result_2026-07-09.md
history/internal_docs/goal5233_graphics_dragon_asian_dragon_subset_route_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json
```

## Review Questions

1. Does the evidence correctly identify the raw public AsianDragon scale
   mismatch against the paper-log MBR?
2. Is the deterministic `scale=0.001` transform justified by MBR evidence?
3. Does the scaled candidate author POD run match the paper-log HDResult within
   `1e-6`?
4. Does the raw candidate author POD run correctly remain a negative control?
5. Is the scaled PLY preparation script app-owned input preprocessing rather
   than RTDL core behavior?
6. Does the scaled 16-source RTDL subset route match the exact subset oracle?
7. Does the report correctly avoid claiming exact paper byte identity or
   Figure 6 reproduction?
8. Does the report correctly avoid claiming RTDL all-source HDResult
   reproduction or performance parity?
9. Are the tests and validations sufficient for this input-contract gate?
10. Should Goal5234 close as
    `completed_graphics_dragon_asian_dragon_scaled_public_candidate_author_gate__level_b_only`?

## Expected Answer Shape

```text
Verdict:
  approve_goal5234_graphics_dragon_asian_dragon_scaled_author_gate
  or approve_with_required_amendments
  or block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to the 10 review questions:
  ...
```

## Claim Boundary To Enforce

Allowed:

```text
For Dragon -> AsianDragon, the public Stanford AsianDragon file needs a
deterministic 1e-3 scale transform to match the paper-log coordinate scale.
With that app-owned transform, author hd_exec matches the paper-log HDResult
within 1e-6, and RTDL matches an exact 16-source subset oracle.
```

Forbidden:

```text
Exact paper input byte identity is proved.
Figure 6 is reproduced.
RTDL all-source Dragon -> AsianDragon HDResult is reproduced.
RTDL is faster than author or exact code.
Author-vs-RTDL performance parity is established.
Full X-HD paper reproduction is complete.
```
