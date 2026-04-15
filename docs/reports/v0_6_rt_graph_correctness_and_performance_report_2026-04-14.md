# v0.6 RT Graph Correctness and Performance Report

Date: 2026-04-14
Scope: corrected RT `v0.6` graph line
Platforms:

- Linux `lestat-lx1`
- Windows `lestat-win` (Embree only)

## Purpose

This report consolidates the current correctness and performance position for
the corrected RT graph line:

- workloads:
  - `bfs`
  - `triangle_count`
- Linux backends:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- Windows backend:
  - Embree

This report keeps correctness and performance separate.

## Correctness Summary

### Linux: bounded PostgreSQL-backed all-engine correctness

The bounded correctness gate is closed on Linux for:

- Python
- native/oracle
- Embree
- OptiX
- Vulkan
- PostgreSQL

Verification:

```bash
RTDL_POSTGRESQL_DSN="dbname=postgres" PYTHONPATH=src:. python3 -m unittest \
  tests.goal389_v0_6_rt_graph_bfs_truth_path_test \
  tests.goal390_v0_6_rt_graph_triangle_truth_path_test \
  tests.goal391_v0_6_rt_graph_bfs_oracle_test \
  tests.goal392_v0_6_rt_graph_triangle_oracle_test \
  tests.goal393_v0_6_rt_graph_bfs_embree_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal395_v0_6_rt_graph_bfs_vulkan_test \
  tests.goal396_v0_6_rt_graph_triangle_embree_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal398_v0_6_rt_graph_triangle_vulkan_test \
  tests.goal400_v0_6_postgresql_graph_correctness_test
# Ran 51 tests — OK
```

### Large-batch cross-platform correctness checks

Additional large-batch parity checks were run for the same corrected RT-kernel
graph forms.

#### BFS

Windows Embree and Linux PostgreSQL match exactly on the large batch:

- Windows Embree:
  - row count: `2251703`
  - SHA-256: `e494761bce5b9ea561ea29f605cef8779aa8edb48de0a413bf4f6dfd2c6a07ae`
- Linux PostgreSQL:
  - row count: `2251703`
  - SHA-256: `e494761bce5b9ea561ea29f605cef8779aa8edb48de0a413bf4f6dfd2c6a07ae`

Verdict:

- `bfs` is consistent across:
  - Windows Embree
  - Linux PostgreSQL

#### Triangle Count

Large-batch triangle results are **not** yet consistent.

Observed outputs:

- Windows Embree:
  - row count: `1938`
  - SHA-256: `1112c342267382b12eadcf5db3b6e11aa10a3528a9e3b832a557b67df4fb9779`
- Linux PostgreSQL:
  - row count: `2250`
  - SHA-256: `17c12026dd9af23b12d979f41c77bc5fa406cc5c4bc2641bf423d72094693ff8`

Localization:

- Windows CPU/oracle-style truth:
  - row count: `2250`
  - SHA-256: `17c12026dd9af23b12d979f41c77bc5fa406cc5c4bc2641bf423d72094693ff8`
- Linux Embree:
  - row count: `1938`
  - SHA-256: `1112c342267382b12eadcf5db3b6e11aa10a3528a9e3b832a557b67df4fb9779`

Verdict:

- `triangle_count` large-batch correctness is **not closed** for Embree
- the mismatch is not Windows-specific
- the mismatch is in the Embree triangle path itself

## Performance Summary

### Linux: bounded large-data performance gate

#### BFS step performance

Dataset:

- `snap_wiki_talk`
- first `1,000,000` directed edges loaded
- actual frontier batch: `1,884`

```json
{
  "dataset": "snap_wiki_talk",
  "edge_count": 1000000,
  "embree_prepare_seconds": 0.43921319500077516,
  "embree_seconds": 0.6687887600855902,
  "optix_prepare_seconds": 0.43626449001021683,
  "optix_seconds": 0.47295012103859335,
  "vulkan_prepare_seconds": 0.4364068900467828,
  "vulkan_seconds": 0.47580938693135977,
  "postgresql_setup_seconds": 36.560594053938985,
  "postgresql_seconds": 1.2444212369155139
}
```

#### Triangle probe performance

Dataset:

- `graphalytics_cit_patents`
- first `100,000` canonical undirected edges loaded
- actual seed batch: `8,192`

```json
{
  "dataset": "graphalytics_cit_patents",
  "edge_count": 200000,
  "embree_prepare_seconds": 0.6451302459463477,
  "embree_seconds": 0.052159475977532566,
  "optix_prepare_seconds": 0.6372530059888959,
  "optix_seconds": 0.004164474899880588,
  "vulkan_prepare_seconds": 0.6507506290217862,
  "vulkan_seconds": 0.004779421957209706,
  "postgresql_setup_seconds": 8.719684956944548,
  "postgresql_seconds": 0.004445821978151798
}
```

### Linux: longer-running large-work comparisons

To get the RT engines into a more stable multi-second band, additional direct
large-work runs were performed using repeated prepared-step execution.

#### BFS longer run

Dataset:

- `snap_wiki_talk`
- `5.0M` directed edges loaded
- frontier batch: `132,703`
- `execution_iterations = 5`

Measured:

- Embree prepare: `1.455032638 s`
- Embree run: `17.226615265 s`
- OptiX prepare: `1.495103395 s`
- OptiX run: `11.090026237 s`
- Vulkan prepare: `1.439433480 s`
- Vulkan run: `11.061863374 s`
- PostgreSQL setup: `221.175805129 s`
- PostgreSQL query: `5.507832295 s`

#### Triangle longer run

Dataset:

- `graphalytics_cit_patents`
- `500,000` canonical undirected edges loaded
- seed batch: `500,000`
- `execution_iterations = 140`

Measured:

- Embree prepare: `2.313741725 s`
- Embree run: `130.655804546 s`
- OptiX prepare: `2.619573815 s`
- OptiX run: `8.209053610 s`
- Vulkan prepare: `2.692694399 s`
- Vulkan run: `8.410447048 s`
- PostgreSQL setup: `66.532431962 s`
- PostgreSQL query: `0.634484485 s`

## PostgreSQL Baseline Notes

PostgreSQL is used as the correctness anchor and indexed external baseline.

Indexing used:

- edge table:
  - `(src)`
  - `(dst)`
  - `(src, dst)`
- BFS temp tables:
  - frontier `(vertex_id)`
  - visited `(vertex_id)`
- triangle temp table:
  - seed edges `(u, v)`

The query/setup split remains necessary because setup dominates the PostgreSQL
side on the large graph slices.

## Current Conclusion

### Correctness

- Linux bounded correctness gate:
  - closed
- Windows Embree vs Linux PostgreSQL `bfs`:
  - closed
- Windows Embree vs Linux PostgreSQL `triangle_count` on the large batch:
  - **not closed**

### Performance

- Linux large-data performance evidence exists for:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL
- OptiX and Vulkan are both in a stable multi-second band on the direct
  large-work runs.

## Honesty Boundary

What this report supports:

- bounded RT-kernel correctness on Linux across all intended engines
- cross-host `bfs` parity between Windows Embree and Linux PostgreSQL
- Linux performance comparison across:
  - Embree
  - OptiX
  - Vulkan
  - PostgreSQL

What this report does **not** support:

- a claim that large-batch `triangle_count` correctness is closed for Embree
- a claim that all large-work runs are already correctness-clean
- a final release claim

## Next Required Fix

Before the corrected RT `v0.6` line can claim large-batch correctness and
fully trusted large-batch performance comparison for `triangle_count`, the
Embree triangle path must be fixed and revalidated against PostgreSQL truth.
