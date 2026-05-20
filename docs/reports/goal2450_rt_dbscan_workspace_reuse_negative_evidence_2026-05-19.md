# Goal2450 RT-DBSCAN Workspace Reuse Negative Evidence

Date: 2026-05-19

Status: pod-smoked, negative for performance.

## Purpose

Goal2444/2445 left one plausible small optimization open: avoid allocating the
`neighbor_indices` output buffer once per chunk in the chunked OptiX adjacency
path. Goal2447 tested a single reused workspace; Goal2449 tested a bounded
workspace pool.

This report closes that small path for performance purposes.

## Pod Setup

Pod command used by the user:

```text
ssh root@69.30.85.177 -p 22055 -i ~/.ssh/id_ed25519
```

Codex connected with the project working key:

```text
C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Recorded hardware:

```text
NVIDIA RTX A5000, driver 570.211.01
```

The pod checkout was reset to `origin/main` at:

```text
76c8306a270c44173a26c8befa6c92a840fba674
```

and then the local Goal2447/2449 files were copied in for smoke testing.

## Evidence

Artifacts:

- `docs/reports/goal2447_rt_dbscan_neighbor_workspace_reuse_pod_smoke/summary.json`
- `docs/reports/goal2449_rt_dbscan_neighbor_workspace_pool_pod_smoke/summary.json`

Dataset:

```text
clustered3d, 32,768 points, chunk_adjacency_edge_budget=8,000,000
```

All compared paths produced matching component signatures:

```text
4 clusters of 8192, core_count 32767, noise_count 0
```

## Results

Single-workspace reuse:

| Policy | Steady-State Mean (s) | Ratio vs Default |
| --- | ---: | ---: |
| Default per-chunk allocation | 0.41097885742783546 | 1.000x |
| Single reused workspace | 0.42906372901052237 | 1.044x |

Bounded workspace pool:

| Policy | Steady-State Mean (s) | Ratio vs Default |
| --- | ---: | ---: |
| Default per-chunk allocation | 0.38809293260176975 | 1.000x |
| Pool size 4 | 0.4262925287087758 | 1.098x |
| Pool size 8 | 0.4073486079772313 | 1.050x |
| Pool size 18 | 0.3900656445572774 | 1.005x |

## Interpretation

The workspace variants are correct, but they are not useful as the next
performance path:

- pool size 1 loses to per-chunk allocation because it synchronizes too often;
- pool sizes 4 and 8 still lose because reuse synchronization is visible;
- pool size 18 nearly matches default, but it retains one buffer per chunk and
  therefore does not improve the memory-bounded story enough to justify a
  performance claim.

The default per-chunk allocation path should remain the performance default.

## Next Direction

The next real RT-DBSCAN improvement should be the larger generic primitive
already identified in the future-version list:

```text
lower-overhead generic grouped stream continuation
```

That means reducing launch count and intermediate storage in the generic
fixed-radius graph/component continuation, not adding a DBSCAN-specific native
kernel.

## Claim Boundary

This is pod smoke evidence for one controlled row. It is not a paper
reproduction claim, whole-app speedup claim, release claim, or broad RT-core
claim.

## Verdict

`accept-with-boundary`: correct implementation and useful negative evidence,
but no performance improvement.
