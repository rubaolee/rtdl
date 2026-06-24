# Goal3013: Hausdorff Numba Device Score Rows L4 Pod Runner

## Purpose

Goal3013 prepares clean pod evidence for the Goal3012 Hausdorff Numba device
score-row path.

The runner is:

`scripts/goal3013_hausdorff_numba_device_score_rows_pod_runner.py`

It records:

- clean Git commit and dirty status;
- GPU and driver summary;
- a warmup run;
- a larger evidence run;
- oracle parity;
- claim-boundary flags.

## Observed Evidence

The pod artifact is:

`docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json`

It was collected from commit:

`69d4818ad33bf2208014b43dd22d4cbfbcf4c2c4`

on:

`NVIDIA L4, 565.57.01`

The evidence run used `copies=256`, producing `1024 x 1024` points and
`1,048,576` score rows per directed pass.

The artifact shows:

- `backend: partner_numba_witness_exact`;
- `partner: numba`;
- `evidence.matches_oracle: true`;
- `evidence.host_score_row_materialization_used: false`;
- `evidence.score_rows_generated_on_partner_device: true`;
- `evidence.rt_core_accelerated: false`;
- `all_claim_flags_false: true`;
- a clean `source_dirty` list.

The evidence wall time was `1.2707423008978367` seconds. This is phase-timing
evidence only, not a same-contract speedup claim.

## Boundary

This is app-level Numba correctness and phase-timing evidence. It is not v2.6
release evidence, not a speedup claim, and not RT-core evidence. The native
engine remains app-agnostic and is not called by this exact dense path.
