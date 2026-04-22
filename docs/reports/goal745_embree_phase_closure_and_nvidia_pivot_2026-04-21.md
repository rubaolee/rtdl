# Goal 745: Embree Phase Closure And NVIDIA Pivot

## Verdict

The Embree app-performance phase is closed enough to pivot. It should remain open only for maintenance, bug fixes, and targeted regressions found by later tests.

The next top-priority backend is NVIDIA/OptiX on real RTX hardware.

## What Is Done For Embree

| Area | Status | Evidence |
|---|---|---|
| App coverage | Done | Goal741 all-app compact harness covers macOS, Linux, and Windows. |
| Automatic threading | Done | Embree auto-thread config and native probe-range dispatch are active. |
| Compact app modes | Done for key apps | DB, graph, KNN, Hausdorff, ANN, outlier, DBSCAN, road hazard, robot collision, polygon overlap, and Barnes-Hut have compact/scaled modes where practical. |
| LSI root primitive | Done | Goal742 switched LSI to Embree segment user-geometry traversal. |
| PIP root primitive | Done | Goal742/743 document positive-hit PIP as native Embree BVH/point-query candidate discovery. |
| Cross-machine large LSI/PIP evidence | Done | Goal743 macOS, Linux, and Windows parity/performance JSON. |
| Optimization doctrine | Done | Goal744 lessons report for OptiX, Vulkan, HIPRT, and Apple RT. |

## Main Embree Performance Reading

Embree works best when the app asks RTDL for compact outputs:

- sparse spatial joins,
- positive-hit rows,
- counts,
- flags,
- summaries,
- prepared raw rows.

Embree is much less useful when the app asks for massive Python-visible row tables. Dense LSI proves this clearly: one million hit rows are found quickly in prepared raw mode, but full Python dict materialization dominates wall time.

## Important Numbers To Carry Forward

From Goal743:

| Workload | macOS | Linux | Windows | Meaning |
|---|---:|---:|---:|---|
| Sparse LSI auto-vs-1T | `3.72x` | `4.07x` | `48.63x` | Threads help independent probe traversal. |
| PIP positive auto-vs-1T | `2.26x` | `2.81x` | `3.10x` | Threads help independent point-query traversal. |
| Dense LSI auto-vs-1T | `0.96x` | `1.06x` | `0.97x` | Threads cannot fix huge output materialization. |
| Dense LSI raw-vs-dict | `77.90x` | `53.85x` | `32.10x` | Interface/output design dominates dense row workloads. |

## Boundaries

This phase does not claim NVIDIA RT-core acceleration. Embree is a CPU ray-tracing backend.

This phase does not mean every app is performance-leading against every specialized library. It means the RTDL/Embree backend now has:

- correct app coverage,
- cross-machine evidence,
- useful automatic threading,
- compact output patterns,
- and clear honesty boundaries.

## Remaining Embree Maintenance Items

| Item | Priority | Reason |
|---|---|---|
| Keep dense row outputs available but not performance-promoted | High | Dense pair rows are audit/debug outputs, not the fast path. |
| Remove known Windows clang warnings later | Low | Current warnings are noisy but not blocking. |
| Add external GIS comparisons only when user-facing docs need them | Medium | PostGIS/GEOS comparisons are valuable but not needed to close this Embree phase. |
| Re-run Goal741/743 after major native changes | High | Prevent regressions in app coverage and root primitives. |

## NVIDIA/OptiX Pivot

The top priority now is NVIDIA GPUs with real RT cores.

The Embree lesson directly defines the OptiX plan:

1. Do not benchmark only full Python row outputs.
2. Build native OptiX traversal paths for app-relevant kernels.
3. Add compact outputs before performance claims.
4. Separate GPU traversal time, output compaction, host copy, and Python materialization.
5. Use RTX-class hardware before saying “RT-core accelerated.”

## Recommended Next OptiX Work Order

| Order | Work | Why |
|---:|---|---|
| 1 | Robot collision / visibility any-hit compact modes | Best current OptiX flagship candidate because it maps naturally to ray/triangle RT traversal. |
| 2 | LSI/PIP root primitive parity and compact outputs on OptiX | Historical roots plus direct spatial-app relevance. |
| 3 | Fixed-radius count-threshold summary for outlier/DBSCAN | Already has prototype work; needs RTX hardware validation and phase timing. |
| 4 | DB app prepared dataset phase profiling | Important, but less clearly RT-core-natural than ray/geometry workloads. |
| 5 | Graph app review | Must avoid overclaiming unless traversal really maps to OptiX acceleration. |

## Closure Statement

Embree has now done its job for this phase: it proves the RTDL app model can use a mature CPU ray-tracing backend with automatic multithreading, compact outputs, and cross-machine evidence.

The next serious performance credibility step is OptiX on NVIDIA RTX hardware.
