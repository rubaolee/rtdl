# Call For Review: Goal5236 Graphics Dragon -> AsianDragon Scaled OptiX POD Bounded Gate

Please strictly review Goal5236.

## Files To Review

```text
history/internal_docs/goal5236_graphics_dragon_asian_dragon_scaled_optix_pod_bounded_gate_result_2026-07-09.md

Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset256_optix_pod_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5236_graphics_dragon_asian_dragon_scaled_subset1024_optix_pod_2026-07-09.json

history/internal_docs/goal5234_graphics_dragon_asian_dragon_scaled_author_gate_result_2026-07-09.md
history/internal_docs/goal5235_graphics_dragon_asian_dragon_scaled_subset_scaling_matrix_result_2026-07-09.md
```

## Context

Goal5234 found that raw public AsianDragon does not match the paper log, while
an app-owned deterministic `scale=0.001` public candidate matches the paper-log
HDResult within `1e-6`.

Goal5235 ran local bounded NumPy route gates for source limits 16, 64, and 256.
All matched exact subset oracles, but it did not exercise a current rebuilt POD
OptiX backend.

Goal5236 uploads the current source subset to the POD, rebuilds
`librtdl_optix.so`, and runs bounded OptiX gates for the scaled
Dragon -> AsianDragon candidate.

## Claims Under Review

1. Goal5236 uses a current-source rebuilt OptiX library, not the old
   `/tmp/rtdl_goal5144` snapshot.
2. The 256-source and 1024-source bounded OptiX routes match exact subset
   oracles with `route_abs_diff=0.0`.
3. The route consumes the full scaled AsianDragon target (`3,609,600` points)
   with bounded source subsets.
4. Explicit frontier capacity (`400,000`) is sufficient for the two bounded
   POD gates.
5. Goal5236 remains bounded Level-B same-source evidence only.

## Review Questions

1. Does the build/version evidence sufficiently show that Goal5236 did not mix
   current scripts with the old POD OptiX library?
2. Do the JSON artifacts prove exact scalar and final max-witness agreement for
   the 256-source and 1024-source bounded gates?
3. Is the `per_source_witness_exact=false` caveat correctly stated, and does it
   prevent overclaiming exact per-source nearest witnesses?
4. Is it correct to reject timing scale/speedup claims from the 256 vs 1024
   timing difference because of warm/JIT/runtime effects?
5. Is the Level-B same-source boundary maintained? In particular, does Goal5236
   avoid claiming exact paper input identity, all-source HDResult, Figure 6, or
   author-vs-RTDL performance parity?
6. Does the scaled-input contract from Goal5234 remain visible enough?
7. Should the next step be a larger bounded OptiX subset, or a streaming /
   chunked all-source route design before attempting all-source?

## Expected Answer Shape

```text
Verdict:
  approve_goal5236_scaled_optix_pod_bounded_gate
  OR approve_with_required_amendments
  OR block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Answers to review questions:
  1. ...
  2. ...
```

## Forbidden Summaries

Please reject any summary that says:

```text
X-HD full paper reproduction is complete.
RTDL reproduced Figure 6.
RTDL matched author performance.
RTDL ran all-source Dragon -> AsianDragon.
RTDL proved exact paper input byte identity.
The bounded route proves exact per-source witnesses.
```
