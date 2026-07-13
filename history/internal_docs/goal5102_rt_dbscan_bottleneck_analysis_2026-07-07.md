# Goal5102 RT-DBSCAN Bottleneck Analysis

## Status

`completed_bounded_bottleneck_analysis`

## Evidence Base

This analysis uses the representative matrix from Goals5099-5100.

## Cold Bottleneck

Cold one-shot RTDL time is about 1.6-1.7s on the three synthetic representatives, while the author's reported phase total is about 0.02-0.05s.

The first RTDL execution includes:

- Python process startup,
- CUDA context work,
- Numba compilation/setup,
- OptiX/native pipeline setup,
- generic grouped-stream workspace setup.

The medium warm matrix confirms this: the first in-process repeat had `rtdl_wall_sec=1.593s` and `grouped_union_native_elapsed_sec=0.441654s`, while later repeats had `rtdl_wall_sec` around 0.004-0.006s and grouped-union native elapsed around 0.0001s.

## Steady-State Shape

After setup is paid, these tiny synthetic fixtures are not traversal-bound. The recorded native phases are already very small. Remaining wall time is likely dominated by Python/app runner overhead and label materialization/comparison at this scale.

## Next Technical Mountains

1. **Prepared service regime**: define and prove a real long-lived process model for multiple RT-DBSCAN queries, not replay of the exact same input as a headline.
2. **Precompiled / warmed route**: reduce first-use compilation/setup if one-shot use remains important.
3. **Larger exact or representative datasets**: the current fixtures are controlled but small; performance shape may change at paper scale.
4. **Paper dataset provenance**: exact paper reproduction remains blocked until paper inputs and phase boundaries are pinned.

## What Not To Do

Do not market warm 4-6ms diagnostic numbers as paper performance. Do not spend effort on app-level formatting or label-ID parity before the input/provenance and regime problem is solved.
