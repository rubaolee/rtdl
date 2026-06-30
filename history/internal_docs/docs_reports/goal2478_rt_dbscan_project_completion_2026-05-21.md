# Goal2478 RT-DBSCAN Project Completion Report

Date: 2026-05-21

## Decision

The RT-DBSCAN benchmark app is complete for the current v2.x scope. The project now has a working RTDL implementation of the RT-DBSCAN application shape using generic fixed-radius primitives, partner continuations, and OptiX RT traversal where appropriate:

```text
3-D fixed-radius neighbor search -> core-point threshold -> radius-graph components
```

No DBSCAN-specific native ABI, native DBSCAN vocabulary, or app-specific native engine semantics were added. App semantics remain in the Python benchmark app and partner adapter layer.

This is not a paper-reproduction claim and not a public broad DBSCAN speedup claim. The paper authors' exact implementation and datasets were not used in this closeout matrix.

## What Is Implemented

The benchmark app now covers the relevant execution contracts:

| Contract | Status | Notes |
| --- | --- | --- |
| CPU tiny reference | Complete | Exact correctness oracle for the small fixture. |
| Generic RTDL row path | Complete | Same row contract without GPU. |
| Prepared CuPy device-grid baseline | Complete | Fair steady-state CUDA-core baseline for timing comparisons. |
| OptiX RT core flags plus prepared CuPy continuation | Complete | RT traversal writes threshold-capped counts/core flags; CuPy labels components. |
| OptiX RT full adjacency stream plus CuPy continuation | Complete | Preferred exact adjacency branch when the full directed stream fits the edge budget. |
| OptiX RT chunked adjacency stream | Complete as diagnostic | Retained for manual memory-bounded comparison, not the default over-budget branch. |
| OptiX RT grouped-stream continuation | Complete | Preferred over-budget dense continuation branch; avoids full neighbor-index materialization. |
| Grouped-union all-items/self-query path | Complete | Keeps query/search inputs on device and removes avoidable host transfer. |
| Predicate and same-root culling | Complete | Reduces avoidable anyhit work while preserving generic fixed-radius semantics. |
| Intersection-direct side-effect experiment | Not promoted | Correct but mixed-to-negative performance; remains default-off. |

## Final Pod Evidence

Pod command used:

```bash
ssh root@69.30.85.177 -p 22181 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

| Field | Value |
| --- | --- |
| Hostname | `ecdc0a16bb30` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| CUDA | `Build cuda_12.8.r12.8/compiler.35583870_0` |
| OptiX | `/root/vendor/optix-dev-8.0.0` |
| Artifact | `docs/reports/goal2478_rt_dbscan_project_close_pod/summary.json` |
| Source tree on pod | rsync copy, not a git checkout |

Command shape:

```bash
cd /root/rtdl_python_only
export PYTHONPATH=src:.
export PATH=/usr/local/cuda-12.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH:-}
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc
export RTDL_OPTIX_PTX_COMPILER=nvcc
/root/rtdl_venv/bin/python scripts/goal2478_rt_dbscan_project_close_pod_runner.py \
  --output-dir docs/reports/goal2478_rt_dbscan_project_close_pod \
  --repeat-count 3 \
  --point-count 32768 \
  --point-count 65536 \
  --point-count 131072
```

All recorded probes had matching signatures.

## Performance Matrix

Dataset: `clustered3d`. Values are tail medians after dropping the first timing row; with `--repeat-count 3`, each tail median is computed from the two post-warmup runs. The grouped-stream column-signature mode measures the dense continuation path without materializing neighbor rows or a full directed adjacency stream.

| Points | Prepared CuPy grid, sec | OptiX RT-count + prepared CuPy, sec | RT-count speedup vs CuPy | Grouped-stream total, sec | Grouped native kernel, sec | Grouped-stream speedup vs CuPy | High-level plan | Continuation plan |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 32,768 | 0.1597758988 | 0.1429276895 | 1.1179x | 0.0408550138 | 0.0224657068 | 3.9108x | prepared CuPy | full adjacency stream |
| 65,536 | 0.4676661789 | 0.3734569130 | 1.2523x | 0.0990382954 | 0.0674216980 | 4.7221x | RT-count bridge | grouped stream |
| 131,072 | 1.5541055435 | 1.0094030295 | 1.5396x | 0.3172265468 | 0.2537486283 | 4.8990x | RT-count bridge | grouped stream |

Planner interpretation:

- `planned_rt_dbscan` selects the prepared CuPy baseline at 32,768 points because earlier prepared-fairness evidence kept the crossover at the 65k clustered scale.
- `planned_rt_dbscan` selects the RT-count bridge at 65,536 and 131,072 points.
- `planned_rt_dbscan_continuation` selects full adjacency at 32,768 points because the estimated 135,291,470 directed edges fit the 160,000,000 edge budget.
- `planned_rt_dbscan_continuation` selects grouped stream at 65,536 and 131,072 points because estimated directed edge counts are 541,165,879 and 2,164,663,517, which exceed the edge budget.

## Architecture Boundary

The native engine is general for this project scope because the native surfaces operate on fixed-radius geometry and caller-owned generic columns:

- points/search points;
- radius;
- threshold-capped count columns;
- predicate flags;
- parent/union columns;
- fallback-candidate columns;
- adjacency offsets and neighbor-index streams.

The native engine does not know DBSCAN clusters, labels, `min_neighbors` as an app concept, or dataset names. The benchmark app maps DBSCAN semantics onto the generic primitives in Python.

The remaining app-specific behavior is expected and intentional:

- dataset generation and benchmark presets live in the example app;
- planner thresholds live in the example app as evidence-bound plan/explain policy;
- partner choice and output labels live in Python/CuPy adapter code.

## Deferred Work

These items are not blockers for closing the current RT-DBSCAN benchmark app:

| Item | Reason for deferral |
| --- | --- |
| Paper implementation comparison | Blocked unless the authors' implementation and datasets are available and usable. |
| Paper-level public speedup wording | Requires representative datasets, reviewed claim path, and external consensus. |
| Broad DBSCAN acceleration claim | Requires more datasets and public wording review. |
| New native algorithm replacing grouped union | v3-scale only if new evidence shows a generic primitive can outperform grouped stream without app-specific engine knowledge. |
| Vulkan/HIPRT/Apple RT backends | Outside active v2.x priority; Embree and OptiX remain the active backends. |
| Intersection-direct side-effect default promotion | Explicitly not promoted because A/B evidence was mixed to negative. |

## Closeout Position

The project can now be closed as an RTDL benchmark app. The correct next work is cleanup, review, and commit discipline, not another native optimization cycle, unless a new measured regression appears or an external review identifies a correctness gap.
