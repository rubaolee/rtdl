# Goal4144 - Direct-Status Workspace Reuse Pod Result

Date: 2026-06-09

Verdict: reject-as-performance-default

## Purpose

Goal4144 measures the Goal4143 prepared-workspace reuse candidate for the
RT-DBSCAN direct-status route at 1M points, factor `0.25`, on the same RTX 4000
Ada pod class and with the same Goal4117 runner protocol used by Goal4138.

## Artifact

`docs/reports/goal4144_direct_status_workspace_reuse_1m_factor025_pod.json`

Setup:

- Source commit: `3909281b`
- Point count: 1,048,576
- Repeat: 2
- Warmup: 1
- Factor: `0.25`

## Result Compared With Goal4138

Ratio below is `Goal4138 baseline / Goal4144 workspace candidate`; values above
`1.0x` mean the workspace candidate is faster.

| Profile | Goal4138 replay (s) | Goal4144 replay (s) | Replay ratio | Goal4138 total (s) | Goal4144 total (s) | Total ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clustered3d | 5.755256 | 5.768758 | 0.998x | 7.001828 | 7.055828 | 0.992x |
| road3d | 5.210240 | 5.207637 | 1.000x | 5.956892 | 5.988466 | 0.995x |
| ngsim_dense | 1.252143 | 1.251273 | 1.001x | 2.176086 | 2.274487 | 0.957x |

All rows preserved component-size signature parity.

## Interpretation

The workspace reuse candidate is not a meaningful performance win. Replay timing
is essentially neutral, while one-shot total timing gets worse because workspace
allocation moves into the prepare phase:

- clustered3d prepare rises from `1.246572s` to `1.287070s`;
- road3d prepare rises from `0.746652s` to `0.780829s`;
- ngsim_dense prepare rises from `0.923943s` to `1.023214s`.

This teaches us that per-replay parent/counter allocation is not the dominant
RT-DBSCAN direct-status bottleneck at 1M. The next useful performance work should
target larger structural costs: direct-status kernel work, convergence/sync
behavior, prepare pipeline cost, or a stronger native/resident partition
producer. Do not promote workspace reuse as the default performance route.

## Boundary

This result does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, automatic dispatch,
automatic partner selection, automatic factor selection, app-specific engine
logic, native ABI additions, AMD claims, or true-zero-copy claims.
