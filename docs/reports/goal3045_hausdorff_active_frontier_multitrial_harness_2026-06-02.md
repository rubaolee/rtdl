# Goal3045 Hausdorff Active-Frontier Multitrial Harness

Date: 2026-06-02

Status: harness landed; A4000 run pending.

## Purpose

Goal3042 produced a strong single-run A4000 result for the active-frontier
Hausdorff path, but the Goal3043 Claude review correctly noted that a public
performance claim needs repeated timing with warmup, medians, and dispersion.

Goal3045 adds `scripts/goal3045_hausdorff_active_frontier_multitrial.py` to run
the current CuPy grouped-grid reference and the RTDL/OptiX active-frontier path
inside one Python process with:

- explicit warmup iterations,
- alternating measurement order,
- per-trial exact-distance validation,
- median, quartile, and IQR summaries,
- closed claim-boundary flags.

## Boundary

This harness is for internal v2.6 evidence. It does not authorize release,
public speedup wording, broad RT-core speedup wording, whole-app speedup
wording, or true-zero-copy wording.
