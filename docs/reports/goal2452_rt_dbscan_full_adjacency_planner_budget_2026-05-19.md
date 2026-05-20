# Goal2452 RT-DBSCAN Full Adjacency Planner Budget

Date: 2026-05-19

Status: implemented and pod-probed.

## Purpose

After Goals2447/2449/2450 ruled out neighbor-workspace reuse as a performance
path, the next question was whether the explicit continuation planner was too
conservative. It was.

The previous default directed-edge budget was `64,000,000`, which forced the
32,768-point `clustered3d` row into chunked adjacency. A pod probe showed that
the full directed adjacency stream fits on the RTX A5000 and is much faster.

## Evidence

Artifact:

```text
docs/reports/goal2452_rt_dbscan_full_vs_chunked_adjacency_probe/summary.json
```

Hardware:

```text
NVIDIA RTX A5000, driver 570.211.01, 24564 MiB
```

Dataset:

```text
clustered3d, 32,768 points
```

Both paths produced matching component signatures:

```text
4 clusters of 8192, core_count 32767, noise_count 0
```

## Result

| Path | Steady-State Mean (s) | Best Steady-State (s) |
| --- | ---: | ---: |
| Full OptiX directed adjacency stream | 0.061457750077048935 | 0.06038908660411835 |
| Chunked OptiX directed adjacency stream | 0.3918370498965184 | 0.3820408321917057 |

The full stream time ratio was:

```text
0.15684517350587324x
```

so full adjacency was about `6.4x` faster than chunking on this row.

## What Changed

`DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET` in the RT-DBSCAN benchmark app is now:

```text
160,000,000
```

This makes `planned_rt_dbscan_continuation` select
`optix_rt_core_adjacency_cupy_components_3d` for the 32,768-point clustered
row, while still selecting chunked adjacency for streams above the explicit
budget.

The user can still force chunking with:

```text
--adjacency-edge-budget 64000000
```

## Boundary

This is an app-level explicit plan/explain policy update, not an invisible
engine dispatcher. It does not add DBSCAN-native ABI and does not place app
logic inside the native engine.

This is not a paper reproduction claim, whole-app speedup claim, release claim,
or broad RT-core claim.

## Verdict

`accept-with-boundary`.
