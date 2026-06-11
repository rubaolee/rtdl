# Goal4299: Numba Top-K Partner Reference for the v2.11 Embree CPU Packet

Date: 2026-06-11

Status: implementation support for Goal4298.

## Problem

Goal4298 exposed a current partner gap while running the v2.11 Embree CPU packet on
local Linux. The RTNN row intentionally uses `partner=numba` because the current RTNN
benchmark app has no Embree front door. The generic adapter
`top_k_nearest_points_2d_partner_columns(...)`, however, still accepted only Triton,
Torch, and CuPy.

That made RTNN fail with:

```text
ValueError: partner must be 'triton', 'torch', or 'cupy'
```

## Change

The generic top-k adapter now accepts `partner="numba"` through the existing Numba
device-column runtime. The path is intentionally conservative:

1. Use the generic Numba `pairwise_l2_sq_score_rows_2d` device operation to produce
   grouped squared-distance score rows.
2. Copy score rows to host for deterministic distance-then-candidate-id ranking.
3. Return Numba device arrays for `query_ids`, `neighbor_ids`, `distances`, and
   `neighbor_rank`.

This is a correctness/reference path for v2.11. It is not the final high-performance
Numba grouped-topk kernel.

## Boundary

This path does not call native RT traversal, does not add app-specific engine logic,
does not authorize release action, does not authorize public speedup wording, does not
authorize broad RT-core wording, and does not authorize true-zero-copy wording.

The metadata explicitly records:

- `v2_11_numba_preview_kernel_status: reference_host_rank_after_device_score_rows`
- `numba_score_rows_generated_on_partner_device: True`
- `host_rank_materialization_used: True`

## Why This Is Still Useful

The v2.11 goal is a CPU/Embree compatibility and current-partner reference packet, not
a new performance milestone. This Numba path lets users and reviewers run the same
RTNN top-k contract without falling back to CuPy or Torch, while making the remaining
performance debt visible.

The future high-performance target is a generic Numba `grouped_topk_f64` device
kernel, not an RTNN-specific shortcut.

## Post-Review Cleanup

Claude's Goal4300 review noted that the ANN candidate app's direct CLI still listed
only Torch and CuPy even though the app helper could now read Numba device columns.
The CLI now accepts `--partner numba` for `--backend partner_exact_quality`; the
default remains CuPy. This closes the small reachability inconsistency without
changing the benchmark packet boundary.

Local Linux confirmation artifact:

`docs/reports/goal4299_ann_candidate_numba_cli_local_linux.json`

It records `backend: partner_exact_quality`, `partner: numba`, and
`v2_11_numba_preview_kernel_status: reference_host_rank_after_device_score_rows`.
