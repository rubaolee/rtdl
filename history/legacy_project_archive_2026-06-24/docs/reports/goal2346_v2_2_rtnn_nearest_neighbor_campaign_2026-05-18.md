# Goal2346: v2.2 RTNN Nearest-Neighbor Campaign

Date: 2026-05-18

Status: campaign opened; implementation and pod performance still pending

## Purpose

Open the first v2.2 benchmark-driven language/runtime improvement campaign.
The selected paper is RTNN, "Accelerating Neighbor Search Using Hardware Ray
Tracing," by Zhehuan Chen, Zherong Pan, Yang Lou, Changqing Zou, and Yuhao Zhu,
published at PPoPP 2022.

This campaign is not a full paper reproduction and not another standalone demo
app. The purpose is to use RTNN as pressure on the RTDL design:

1. identify the generic primitive/runtime contracts that RTDL needs in order to
   express serious nearest-neighbor workloads;
2. compare current RTDL behavior against the paper implementation when RTX pod
   hardware is available;
3. adopt major optimization ideas only when they can be made app-agnostic inside
   RTDL.

## External Sources Found

| Source | Status | Notes |
| --- | --- | --- |
| arXiv paper page | found | `https://arxiv.org/abs/2201.01366` |
| Paper PDF | found | `https://horizon-lab.org/pubs/ppopp22.pdf` |
| Open-source implementation | found | `https://github.com/horizon-research/rtnn` |
| License | found | The GitHub repository states MIT license. |

The RTNN repository README is directly relevant for RTDL because it states the
workload contract as a radius plus a maximum neighbor count `K`, for both
fixed-radius search and KNN. It also exposes the main optimization levers:

- query partitioning;
- automatic batching using an empirical model;
- point/query sorting;
- fixed-radius exact search;
- exact or approximate KNN depending on partitioning/approximation mode;
- GPU helper work outside OptiX, including grid/sort/data-structure steps.

These are language/runtime design signals, not app-specific native entry
points.

## Existing RTDL Memory

RTDL already carried an older v0.5 RTNN planning lane:

| Existing artifact | What it established | v2.2 implication |
| --- | --- | --- |
| `docs/reports/v0_5_rtnn_gap_summary_2026-04-11.md` | RTDL had fixed-radius and KNN rows, but paper-faithful RTNN work needed true 3D, bounded radius+K contracts, datasets, baselines, and ablations. | Still the right warning; v2.2 must not pretend older 2D paths are paper-equivalent. |
| `docs/reports/goal265_v0_5_rtnn_dataset_registry_2026-04-12.md` | Dataset families were named but not acquired/executed. | Reuse this as provenance scaffolding; add executable pod rows only after data acquisition. |
| `docs/reports/goal266_v0_5_rtnn_baseline_registry_2026-04-12.md` | Baselines such as cuNSearch, FRNN, PCLOctree, and FastRNN were registered. | RTNN itself now becomes the first source-code baseline because its repo is available. |
| `docs/reports/goal267_v0_5_rtnn_reproduction_matrix_2026-04-12.md` | Exact reproduction was explicitly blocked pending exact datasets and adapters. | Keep that boundary. v2.2 starts with bounded adoption, not full reproduction. |
| `docs/reports/goal274_v0_5_bounded_fixed_radius_comparison_2026-04-12.md` | Offline fixed-radius comparison harness existed. | Good seed for artifact parsing, but insufficient for live RTNN timing or RTDL-vs-RTNN same-hardware comparison. |

## Current RTDL v2.1 Starting Point

The current RTDL tree already has useful generic nearest-neighbor pieces:

| Area | Current state | Gap against RTNN-style campaign |
| --- | --- | --- |
| Public eDSL predicates | `fixed_radius_neighbors`, `knn_rows`, `bounded_knn_rows` exist. | The public shape is good, but the fast OptiX path is not yet a paper-style 3D radius+K neighbor-search contract. |
| CPU/reference semantics | 3D bounded KNN CPU/oracle tests exist. | Useful correctness anchor. It is not performance evidence. |
| Embree | prepared 2D KNN/fixed-radius count paths exist; older 3D coverage exists in v0.5 tests. | Needs same-contract v2.2 audit before it can be a clean CPU baseline for RTNN-style rows. |
| OptiX fixed-radius | prepared 2D fixed-radius count/threshold, nearest-witness, and partner device-column paths exist. | RTNN is primarily 3D point-cloud/particle neighbor search; v2.2 needs a generic 3D prepared point-cloud path. |
| Partner continuation | CuPy/PyTorch can do GPU reductions and fixed-radius reference work. | Need a reusable bounded-neighbor output contract that lets partner code consume compact rows or columns without host row explosion. |
| Scheduling | RTDL has prepared handles and output reuse in some paths. | RTNN's partitioning, batching, sorting, and approximation policy are not yet first-class execution-plan metadata. |

## Design Finding

RTNN should not push RTDL toward an app-shaped `rtnn(...)` native engine entry.
It points to a missing generic primitive family:

```text
prepared_bounded_neighbor_search_3d
  inputs: build point columns, query point columns, radius, k_max
  outputs: bounded neighbor ids/distances/counts or compact columns
  policy: exact|approximate, partitioning, batching, sorting, overflow behavior
  metadata: selected backend, RT-core path, copy mode, approximation mode,
            overflow count, fallback reason, timing phases
```

The runtime-level lesson is that high-performance nearest-neighbor search needs
more than a hit predicate. It needs:

1. a radius+`K` bounded result contract;
2. compact row/column output with overflow/fail-closed semantics;
3. prepared 3D point-cloud acceleration structures;
4. query partitioning and batching as explicit, explainable execution policy;
5. partner-owned output columns for downstream GPU work;
6. exact-vs-approximate status recorded in metadata rather than hidden inside a
   dispatcher.

These contracts remain app-agnostic: point clouds, radius, `K`, row limits,
partition policy, and output buffers are generic.

## First Performance Plan

The open-source RTNN implementation will be used as the first external target
when an RTX pod is available.

### External RTNN setup

Use a disposable checkout outside tracked files, for example:

```text
git clone --depth 1 https://github.com/horizon-research/rtnn scratch/rtnn_goal2346
cd scratch/rtnn_goal2346/src
mkdir -p build
cd build
cmake -DKNN=5 ..
make -j
```

The repo includes OptiX SDK 7.1 headers and builds `bin/optixNSearch`.

### Initial rows

| Row | Dataset | RTNN mode | RTDL mode | Purpose |
| --- | --- | --- | --- | --- |
| `ppp_2d_radius_k50` | synthetic uniform points projected to z=0 | `radius`, `K=50`, partition on/off | current 2D prepared OptiX fixed-radius count/threshold and partner column path | Immediate smoke comparison against current RTDL surface. |
| `ppp_3d_radius_k50` | synthetic uniform 3D points | `radius`, `K=50` | pending v2.2 generic 3D prepared bounded-neighbor path | First real design gap closure row. |
| `ppp_3d_knn_k5` | synthetic uniform 3D points | `knn`, exact and approximate | pending v2.2 generic bounded KNN path | Tests whether `k_max` and approximation metadata are usable. |
| `stanford_or_mesh_sample` | public point samples once acquired | same as above | same as above | Non-uniform geometry stress row. |

### Measurement rules

- Warmup and steady-state times must be separated.
- Build/prepare time, search time, copy time, and partner continuation time must
  be reported separately.
- RTNN approximate KNN must never be compared against exact RTDL without the
  approximation label and error rate.
- RTDL may claim RT-core acceleration only for rows that call the OptiX backend
  and record the native symbol/execution path.
- No whole-language or broad RT-core speedup claim is authorized by this goal.

## Immediate Implementation Sequence

1. Add a small pod-ready RTNN harness that can:
   - generate deterministic point-cloud text files in RTNN format;
   - build/run RTNN from a source checkout;
   - parse RTNN timing blocks into JSON;
   - run the current RTDL fixed-radius paths where the contract already matches.
2. Add a current-design audit test that marks 3D OptiX bounded-neighbor search
   as the first v2.2 runtime gap, not as an app gap.
3. On the next RTX pod, run RTNN smoke rows and current RTDL 2D rows on the same
   generated inputs.
4. Implement the generic 3D prepared bounded-neighbor runtime path only after the
   first external baseline run confirms the exact measurement contract.
5. Re-run against RTNN and decide which RTNN optimization ideas become RTDL
   execution-policy features.

## Hardware Boundary

This Windows workstation can inspect the source, write harnesses, and run
CPU/reference tests. It cannot produce the accepted RTNN-vs-RTDL RT-core
performance comparison.

The local Linux GTX 1070 machine is useful for build/smoke testing only. It has
no hardware RT cores, so it cannot supply accepted RTNN or RTDL OptiX
performance evidence for this campaign.

Accepted performance evidence requires an RTX pod with CUDA/OptiX available.

## Review-Driven Risk Additions

Goal2347 Gemini review accepted the campaign with boundary and asked that the
first pod attempt explicitly track these risks:

| Risk | Mitigation for first pod attempt |
| --- | --- |
| RTNN dependency drift | Record RTNN commit, CMake version, CUDA version, compiler, and exact build command in every artifact. |
| Pod performance variability | Run warmup plus repeated steady-state rows; record GPU, driver, clock/power hints when available, and avoid mixing other GPU jobs. |
| Real dataset preparation | Start with synthetic PPP rows, then add one public non-uniform point-sample row only after acquisition and normalization are scripted. |
| Harness integration complexity | Keep RTNN build/run, timing parsing, RTDL run, and summary aggregation as separate JSON-producing steps. |
| Non-uniform scalability | Treat uniform PPP as a smoke row; do not generalize until mesh/scan and particle-style rows exist. |

## Verdict

The paper and source are suitable for a v2.2 nearest-neighbor campaign.

Initial verdict: `accept-with-boundary`.

Boundary:

- no full RTNN reproduction claim;
- no speedup claim yet;
- no release claim;
- no app-specific native RTDL entry point;
- next work must turn RTNN's lessons into generic bounded-neighbor runtime
  contracts and pod-measured evidence.

## External Review

Goal2347 Gemini review was received with verdict `accept-with-boundary`.
Gemini verified that the paper/source identification is correct, the campaign
is bounded as optimization adoption rather than full reproduction, the proposed
runtime pressure is generic and app-agnostic, and no speedup/release claim is
made before pod evidence. Gemini's risk additions are incorporated above.
