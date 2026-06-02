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

## Expected Evidence

The expected artifact path after pod execution is:

`docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json`

The artifact must show:

- `backend: partner_numba_witness_exact`;
- `partner: numba`;
- `evidence.matches_oracle: true`;
- `evidence.host_score_row_materialization_used: false`;
- `evidence.score_rows_generated_on_partner_device: true`;
- `evidence.rt_core_accelerated: false`;
- `all_claim_flags_false: true`;
- a clean `source_dirty` list.

## Boundary

This is app-level Numba correctness and phase-timing evidence. It is not v2.6
release evidence, not a speedup claim, and not RT-core evidence. The native
engine remains app-agnostic and is not called by this exact dense path.
