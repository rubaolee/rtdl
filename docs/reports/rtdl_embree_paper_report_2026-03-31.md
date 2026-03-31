# RTDL Embree Paper-Style Report

## Abstract

This report consolidates the current RTDL Embree-phase evidence into a single paper-style summary. RTDL is a Python-hosted DSL and compiler/runtime stack for non-graphics ray tracing workloads, with RayJoin as the primary target problem. The current audited baseline runs six workload families on a native Embree backend and uses a Python CPU implementation as the semantic reference.

The report combines three layers of evidence: the frozen Embree baseline evaluation matrix, the current RayJoin paper-reproduction plan and dataset provenance mapping, and the implemented Section 5.6 scalability analogue for `lsi` and `pip`. The resulting artifact is intentionally honest about its scope: it is an Embree-phase reproduction effort, not the final NVIDIA/OptiX v0.1 result.

## System and Experiment Scope

- Runtime backends used here: `run_cpu(...)` for semantic reference and `run_embree(...)` for native execution.
- Current audited workloads: `lsi`, `pip`, `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, `point_nearest_segment`.
- Paper-focused reproduction status: Figure 13 and Figure 14 now have implemented scaled analogues; Table 3, Table 4, and Figure 15 remain planned.
- Precision model: `float_approx` only; no robust or exact arithmetic claim is made in this report.

## Embree Baseline Evaluation

- Total benchmark cases: `17`.
- CPU-vs-Embree parity: `True` across the frozen evaluation matrix.
- Best observed Embree speedup vs CPU: `ray_synthetic_large` at `165.14x`.
- Slowest Embree case by mean latency: `ray_synthetic_large` at `0.001822s`.

| Workload | Largest Current Case | Embree Mean (s) |
| --- | --- | ---: |
| `lsi` | `lsi_county_tiled_x8` | 0.000413 |
| `pip` | `pip_county_tiled_x8` | 0.000450 |
| `overlay` | `overlay_county_soil_tiled_x8` | 0.000614 |
| `ray_tri_hitcount` | `ray_synthetic_large` | 0.001822 |
| `segment_polygon_hitcount` | `segment_polygon_county_fixture` | 0.000294 |
| `point_nearest_segment` | `point_nearest_county_fixture` | 0.000249 |

## Section 5.6 Support Decision

The repository did not originally support RayJoin Section 5.6 as an executable experiment. That gap is now closed for an Embree-phase scaled analogue. RTDL implements deterministic synthetic generators, fixed-build-size and varying-probe-size benchmark runners, Figure 13 / Figure 14 analogue generation, and a dedicated reproducible report path.

This remains a scaled analogue rather than a paper-identical result because the current Embree phase uses:

- fixed build-side polygons `R = 800`,
- probe-side series `S = 160, 320, 480, 640, 800`,
- distributions `uniform` and `gaussian`,
- local Embree execution instead of NVIDIA RT cores.

Correctness gate for the analogue: `True` on reduced CPU-vs-Embree parity samples.

## Section 5.6 Quantitative Highlights

| Series | First Point | Final Point |
| --- | --- | --- |
| `Figure 13 Uniform LSI Throughput` | `160 -> 0.00 intersections/s` | `800 -> 1421.33 intersections/s` |
| `Figure 13 Gaussian LSI Throughput` | `160 -> 0.00 intersections/s` | `800 -> 4292.25 intersections/s` |
| `Figure 14 Uniform PIP Throughput` | `160 -> 829.91 probe-points/s` | `800 -> 2182.83 probe-points/s` |
| `Figure 14 Gaussian PIP Throughput` | `160 -> 2729.58 probe-points/s` | `800 -> 1970.94 probe-points/s` |

## Figure Coverage

- Corresponding RayJoin paper figures are included for Figure 13, Figure 14, and Figure 15 when they are available in the local RayJoin working copy.
- RTDL currently provides generated analogues for Figure 13 and Figure 14.
- Figure 15 is included as a paper reference figure only; the matching RTDL overlay-speedup analogue remains open.

## Limitations and Remaining Work

- Table 3 and Table 4 paper-scale dataset pairs are still planned rather than reproduced.
- The current `overlay` workload is an overlay-seed analogue, not full polygon overlay materialization.
- The current report uses Embree and local synthetic or derived inputs where the paper used NVIDIA RT cores and larger prepared datasets.
- The final v0.1 target remains the OptiX/NVIDIA phase after this Embree baseline is complete enough.

## Artifact Pointers

- Baseline evaluation summary: `/Users/rl2025/rtdl_python_only/docs/reports/embree_evaluation_summary_2026-03-30.md`
- Section 5.6 analogue summary: `/Users/rl2025/rtdl_python_only/docs/reports/section_5_6_scalability_report_2026-03-31.md`
- Frozen paper target matrix: `/Users/rl2025/rtdl_python_only/docs/rayjoin_paper_reproduction_matrix.md`
- Dataset provenance note: `/Users/rl2025/rtdl_python_only/docs/rayjoin_paper_dataset_provenance.md`
