# Goal5032 N-Run Default Decision Matrix Result

Date: 2026-07-05

## Purpose

Goal5031 brought the device-resident carrier route to parity / candidate-default territory for the prepared LSI base-session query-batch regime. A single artifact was not enough to switch defaults.

Goal5032 runs a same-POD N-run matrix:

- CPU carrier: 3 runs
- Device-resident carrier: 3 runs
- Same top4 input
- Same code
- Same prepared LSI base-session query-batch regime
- Same writer-free binary descriptor route

## Regime Boundary

This is not:

- cold CLI one-shot;
- paper-text output;
- author-performance comparison;
- 10x evidence.

It is:

- same-process prepared LSI base-session;
- six distinct chain-contiguous top4 County x Zipcode query batches;
- writer-free binary descriptor route.

## Artifacts

CPU carrier:

- `history/internal_docs/rtdl_goal5032_nrun_cpu_1_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_cpu_2_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_cpu_3_top4.json`

Device-resident carrier:

- `history/internal_docs/rtdl_goal5032_nrun_device_1_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_device_2_top4.json`
- `history/internal_docs/rtdl_goal5032_nrun_device_3_top4.json`

## Structural Anchors

Every run kept:

- total LSI rows across six batches: `428322`;
- first-batch descriptor pair count: `6316`.

## Matrix

| Route | Run | Six-batch sum | First batch | Later-batch sum | Per-batch median |
|---|---:|---:|---:|---:|---:|
| CPU carrier | 1 | 0.971153s | 0.199328s | 0.771825s | 0.159153s |
| CPU carrier | 2 | 0.971880s | 0.199882s | 0.771998s | 0.159596s |
| CPU carrier | 3 | 0.972112s | 0.202511s | 0.769601s | 0.157159s |
| Device carrier | 1 | 1.063056s | 0.414189s | 0.648867s | 0.130454s |
| Device carrier | 2 | 1.049279s | 0.386033s | 0.663246s | 0.136414s |
| Device carrier | 3 | 1.072188s | 0.378895s | 0.693293s | 0.140194s |

## Median Summary

| Route | Median six-batch sum | Median first batch | Median later-batch sum |
|---|---:|---:|---:|
| CPU carrier | 0.971880s | 0.199882s | 0.771825s |
| Device carrier | 1.063056s | 0.386033s | 0.663246s |

## Decision

CPU carrier remains the default for v2.14.3.

Reason:

- CPU wins full six-batch total: `0.971880s` vs device `1.063056s`.
- Device wins later-batch sum: `0.663246s` vs CPU `0.771825s`.
- Device still loses first batch: `0.386033s` vs CPU `0.199882s`.

So device-carrier has a real steady-state advantage, but its first-batch penalty is still large enough to lose the full six-batch session.

## What Changed Since Goal4998

Device carrier started as a fresh-route regression and later as a replay-only curiosity. Goals5028-5031 changed that:

- prepared carrier arrays removed repeated per-batch carrier dataset copies;
- host run tables were skipped when the device route only needs device run bounds;
- device-carrier kernels, midpoint query-point kernel, and run-bound kernel were warmed with dummy arrays;
- device route now reliably beats CPU on later batches.

But Goal5032 proves that is not enough for a default switch.

## Next Mountain

The remaining blocker is not carrier steady-state. It is first-batch cost.

Options:

1. Accept CPU carrier as v2.14.3 default and stop this track.
2. Continue only if the next goal directly targets device first-batch cost and reports another N-run default matrix.

If continuing, candidate targets are:

- remaining first-batch device prefix/reduction cost;
- descriptor consumer first-batch sort/reduce cost;
- replacing single-block prefix/reduction kernels with a stronger generic device scan/reduce primitive.

## Exit Label

`completed_nrun_default_matrix__cpu_carrier_remains_default_device_wins_steady_state_only`
