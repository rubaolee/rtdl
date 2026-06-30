# Goal2039 Embree CPU Partner All-Thread Local Linux Evidence

Date: 2026-05-14

Status: `accept-with-boundary`

## Purpose

Goal2037 defined the plan for testing v2.0 Embree as a CPU RTDL engine with a CPU-side partner continuation. Goal2039 turns that plan into evidence on the local Linux host.

The test answers a narrow v2.0 question: if there is no NVIDIA RT-core pod and no Intel GPU, can the Embree backend still run the v2 architecture as Python + CPU partner + RTDL, using all available CPU threads?

## Environment

- Host: `192.168.1.20`, user `lestat`
- Linux checkout: `/home/lestat/work/rtdl_goal2037_8df10007`
- Source basis: Windows commit `8df10007`, deployed as a git archive; Linux artifact records `git_commit=unknown`
- Repair applied before final large run: `examples/rtdl_robot_collision_screening_app.py` and `scripts/goal2037_embree_cpu_partner_all_thread_runner.py`
- OS: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Python: `3.12.3`
- Logical CPUs: `8`
- NumPy: `2.4.4`
- Torch: not installed
- Numba: not installed

Thread environment recorded by the runner:

| Variable | Value |
| --- | ---: |
| `OMP_NUM_THREADS` | 8 |
| `TBB_NUM_THREADS` | 8 |
| `MKL_NUM_THREADS` | 8 |
| `OPENBLAS_NUM_THREADS` | 8 |
| `NUMEXPR_NUM_THREADS` | 8 |
| `RTDL_EMBREE_THREADS` | 8 |

## Artifact Packets

| Packet | Path | Result |
| --- | --- | --- |
| Smoke | `docs/reports/goal2037_embree_cpu_partner_all_thread_local_linux_smoke_8df10007` | 16 pass |
| Large repaired | `docs/reports/goal2039_embree_cpu_partner_all_thread_local_linux_large_repaired` | 16 pass |

The smoke run used small fixtures and retained normal correctness validation. The large run used order-of-seconds-or-larger fixtures with three repeats per app.

## Important Repair

The first large run exposed a real benchmarking bug in `robot_collision_screening`: the Embree row was doing a full CPU oracle validation inside the timed app path. On the large fixture (`20000` poses, `1024` obstacles), that validation path dominated the wall time and made the row look hung.

The fix keeps correctness validation in smoke-scale runs, but appends `--skip-validation` for the large robot timing row. The large robot result therefore reports:

- `validation_mode`: `skipped`
- `matches_oracle`: `null`
- `pose_count`: `20000`
- `edge_ray_count`: `80000`
- `obstacle_triangle_count`: `2048`

This is the right split: smoke proves the contract, large measures the Embree app path without a second quadratic CPU oracle.

## Large Timing Matrix

Median wall-clock times from three repeats:

| App | Median seconds | Continuation target | Status |
| --- | ---: | --- | --- |
| `database_analytics` | 1.718904 | NumPy columnar predicate/reduction | pass |
| `graph_analytics` | 1.006331 | NumPy-or-Numba graph continuation target | pass |
| `service_coverage_gaps` | 1.030201 | NumPy threshold/count | pass |
| `event_hotspot_screening` | 1.819200 | NumPy threshold/count | pass |
| `facility_knn_assignment` | 72.139829 | NumPy threshold/count | pass |
| `road_hazard_screening` | 0.856886 | NumPy grouped count/flags | pass |
| `segment_polygon_hitcount` | 0.260264 | NumPy grouped count | pass |
| `segment_polygon_anyhit_rows` | 0.281030 | NumPy compact row materialization | pass |
| `polygon_pair_overlap_area_rows` | 20.513456 | NumPy tiled exact continuation | pass |
| `polygon_set_jaccard` | 6.213745 | NumPy tiled exact continuation | pass |
| `hausdorff_distance` | 109.705274 | NumPy threshold/exact distance | pass |
| `ann_candidate_search` | 42.423010 | NumPy threshold/count | pass |
| `outlier_detection` | 1.059823 | NumPy threshold/count | pass |
| `dbscan_clustering` | 1.065992 | NumPy threshold/count | pass |
| `robot_collision_screening` | 0.856429 | NumPy compact flags | pass |
| `barnes_hut_force_app` | 3.375587 | NumPy-or-Numba node coverage target | pass |

## Interpretation

Embree v2.0 CPU-partner execution is real on local Linux: all 16 app rows completed with all-thread settings and NumPy-host continuation available.

The result is not uniformly high performance. The remaining weak rows are precise:

- `facility_knn_assignment`: large threshold candidate workload remains expensive on CPU.
- `polygon_pair_overlap_area_rows`: exact polygon continuation remains expensive, though bounded and stable.
- `hausdorff_distance`: exact distance workload dominates the CPU path.
- `ann_candidate_search`: candidate search remains expensive on CPU at this scale.

The fast rows are also precise:

- grouped count/flag rows (`road_hazard_screening`, `segment_polygon_hitcount`, `segment_polygon_anyhit_rows`)
- density threshold rows (`outlier_detection`, `dbscan_clustering`)
- graph summary row at the authored scale
- robot collision after removing CPU-oracle contamination from the large timing path

## Claim Boundaries

This goal may claim:

- Embree v2 CPU-partner local Linux evidence exists.
- The local Linux all-thread matrix completed 16/16 large rows.
- NumPy is sufficient to exercise the current CPU-partner path when Torch and Numba are unavailable.
- The robot long-run problem was caused by validation-path contamination and has a narrow repair.

This goal must not claim:

- v2.0 release readiness.
- broad all-app v2 speedup.
- true host zero-copy for every row.
- Embree performance equivalence to OptiX/RT cores.
- first-class Numba or Torch-CPU backend readiness, because neither was installed in this run.

## Verdict

`accept-with-boundary`

The CPU Embree partner architecture is executable and testable today, but the evidence points to four rows that still need v2.0 performance work or a more explicit fallback story before release positioning.
