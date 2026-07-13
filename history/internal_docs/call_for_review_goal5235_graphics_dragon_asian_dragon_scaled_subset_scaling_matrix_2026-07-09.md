# Call For Review: Goal5235 Graphics Dragon -> AsianDragon Scaled Subset Scaling Matrix

Please strictly review Goal5235.

## Files To Review

```text
history/internal_docs/goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_graphics_dragon_asian_dragon_scaled_1e-3_subset16_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_1e-3_subset64_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_1e-3_subset256_numpy_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_2026-07-09.json
```

Context:

```text
history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_author_dragon_asian_scaled_1e-3_public_gate_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5234_priority_input_bridge_graphics_dragon_asian_dragon_scaled_1e-3_2026-07-09.json
```

## Review Questions

1. Do all three source limits (16, 64, 256) use the same scaled
   Dragon -> AsianDragon input contract from Goal5234?
2. Does each case match an exact subset oracle with `route_abs_diff=0.0`?
3. Are exact pair-evaluation counts bounded and clearly not full all-source
   materialization?
4. Are the route/exact timings presented only as local exact-oracle diagnostics
   rather than author-vs-RTDL performance claims?
5. Is the capacity extrapolation clearly labeled diagnostic and not an
   all-source result?
6. Does the report correctly identify all-source frontier materialization as a
   capacity/streaming blocker?
7. Does the POD note correctly avoid mixing current scripts with an old RTDL
   remote snapshot as current evidence?
8. Does the report correctly avoid claiming all-source HDResult reproduction,
   Figure 6 reproduction, exact paper identity, or author parity?
9. Are the matrix artifact and per-case artifacts sufficient for this bounded
   scaling goal?
10. Should Goal5235 close as
    `completed_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix__bounded_only`?

## Expected Answer Shape

```text
Verdict:
  approve_goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix
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
The scaled Dragon -> AsianDragon candidate has bounded RTDL subset evidence at
source limits 16, 64, and 256, each matching an exact subset oracle.
```

Forbidden:

```text
RTDL all-source Dragon -> AsianDragon HDResult is reproduced.
Figure 6 is reproduced.
Exact paper input byte identity is proved.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```
