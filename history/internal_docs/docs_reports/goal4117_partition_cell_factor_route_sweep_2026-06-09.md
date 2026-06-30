# Goal4117 - RT-DBSCAN Explicit Partition Cell-Factor Route Sweep

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4117 measures the RT-DBSCAN prepared direct-status app route after Goal4116 exposed `partition_cell_factor` as an explicit user-selected parameter.

This is not hidden auto-tuning. The sweep asks whether a user-visible partition granularity choice can remove the `ngsim_dense` regression observed in Goal4114.

## Pod Evidence

Artifact:

`docs/reports/goal4117_partition_cell_factor_route_sweep_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `493bccf5`
- Tracked worktree dirty: `false`
- Point count: 65,536
- Repeat: 4
- Warmup: 1
- Tested partition cell factors: `0.0625`, `0.125`, `0.25`, `0.5`, `1.0`

## Result

| Profile | Current replay (s) | Best factor | Tuned direct-status replay (s) | Replay speedup | Best amortized speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 0.094716 | 0.25 | 0.031992 | 2.961x | 9.284x |
| road3d | 0.039510 | 0.25 | 0.021178 | 1.866x | 2.389x |
| ngsim_dense | 0.014906 | 0.5 | 0.011358 | 1.312x | 2.484x |

All tested factors matched the current route's component-size signature. The important repair is `ngsim_dense`: Goal4114's default `0.125` replay speedup was `0.178x`; Goal4117's explicit `0.5` factor makes it `1.312x`.

## Interpretation

The design problem was not that direct-status was fundamentally bad on dense profiles. The tested default partition size was wrong for that shape.

Small cells (`0.0625` and `0.125`) create many partitions and a large neighbor-offset window. That is bad for `ngsim_dense`, where `0.125` used 60,094 partitions and offset 9. The `0.5` factor reduced this to 6,124 partitions and offset 3 while preserving the same component-size signature.

The route guidance should therefore change from "dense NGSIM-like repeated workloads prefer grouped-stream Numba" to "dense NGSIM-like repeated workloads can use explicit prepared direct-status when the user selects the tested larger partition factor."

## Boundary

This report does not promote automatic tuning. It does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, AMD performance claims, or true-zero-copy claims.
