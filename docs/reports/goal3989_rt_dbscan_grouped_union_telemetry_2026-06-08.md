# Goal3989 RT-DBSCAN Grouped-Union Telemetry

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3988 confirmed that RTDL/OptiX grouped stream remains the fastest current RT-DBSCAN route. Goal3989 collects telemetry to understand what kind of generic runtime improvement would matter next.

## Pod Setup

- Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source checkout: `accc84daf76846d29d91fa8a145187851e941f04`
- Dataset: `clustered3d`
- Point count: `65536`
- Radius/min-neighbor defaults from the RT-DBSCAN benchmark app

## Atomic Telemetry

Artifact: `docs/reports/goal3989_rt_dbscan_grouped_union_atomic_telemetry_2026-06-08.json`

| Metric | Value |
| --- | ---: |
| baseline native sec | 0.0794 |
| telemetry native sec | 0.0791 |
| parent atomic attempts | 81,231.5 |
| parent atomic successes | 65,532 |
| parent success rate | 0.807 |
| attempts per point | 1.239 |

The parent-atomic count is not large enough to explain the entire 80-90ms grouped-stream runtime by itself. In short, atomics are not the sole bottleneck. The expensive work is broader: RT candidate traversal plus same-root root-read culling plus the remaining atomic unions.

## Same-Root A/B

Artifact: `docs/reports/goal3989_rt_dbscan_same_root_ab_2026-06-08/`

| Variant | Median elapsed sec | Native elapsed sec | Signature |
| --- | ---: | ---: | --- |
| same-root culling enabled | 0.0900 | 0.0795 | four clusters of 16,384; all core |
| same-root culling disabled | 0.1067 | 0.1003 | same |

Same-root culling is already the right default. Turning it off slows this profile by roughly 18.5% at the wrapper-median level and roughly 26.2% at native elapsed.

## Interpretation

The next generic primitive should not merely toggle direct side effects, split query ranges, or disable root culling. Those have now been tested.

The next design target is a generic dense fixed-radius grouped-union continuation that reduces candidate/root-read work before or during traversal while keeping the native vocabulary app-agnostic. Possible directions include:

- component-aware root-cache snapshots with explicit staleness policy,
- multi-pass contraction with fewer repeated same-root reads,
- candidate compaction before union for dense self-query clusters,
- or a generic cell/partition assisted grouped-union contract when the prepared search structure exposes safe spatial partitions.

Each option needs a separate design/review step before native ABI changes.

## Boundary

This is telemetry and negative/diagnostic evidence. It does not authorize release, public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic.
