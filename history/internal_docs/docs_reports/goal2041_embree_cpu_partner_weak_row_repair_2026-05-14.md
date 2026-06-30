# Goal2041 Embree CPU Partner Weak-Row Repair

Date: 2026-05-14

Status: `accept-with-boundary`

## Purpose

Goal2039 made the Embree v2 CPU-partner path honest: it ran all 16 app rows on local Linux with 8 threads and exposed several slow rows. Goal2041 repairs the rows where the slow path was caused by the wrong v2 contract or by expensive positive candidate discovery.

This is not a release authorization. It is a performance repair and design clarification.

## Root Cause

The slow rows were not all the same bug.

| Row | Root cause |
| --- | --- |
| `facility_knn_assignment` | The large row used KNN row materialization even though the benchmark question was a coverage decision. |
| `ann_candidate_search` | The large row used KNN rerank rows even though the benchmark question was candidate coverage within a radius. |
| `hausdorff_distance` | Exact directed Hausdorff summary required expensive nearest-neighbor passes; the large v2 test only needed the bounded `Hausdorff <= threshold` decision. |
| `polygon_pair_overlap_area_rows` | Candidate discovery was dominated by multiple positive LSI/PIP probes; exact area continuation was only about 2s. |
| `polygon_set_jaccard` | Same candidate-policy problem as polygon pair overlap; the set-area/Jaccard reduction itself was not the main issue. |

## Repairs

| Row | Old median | New median | Improvement | Repair |
| --- | ---: | ---: | ---: | --- |
| `facility_knn_assignment` | 72.139829s | 0.980785s | 73.55x | Embree generic prepared fixed-radius threshold/count |
| `polygon_pair_overlap_area_rows` | 20.513456s | 3.265121s | 6.28x | CPU-partner bbox candidate broadphase + native exact-area summary |
| `polygon_set_jaccard` | 6.213745s | 0.395822s | 15.70x | CPU-partner bbox candidate broadphase + native Jaccard summary |
| `hausdorff_distance` | 109.705274s | 1.199686s | 91.44x | Embree generic prepared fixed-radius threshold/count |
| `ann_candidate_search` | 42.423010s | 0.758911s | 55.90x | Embree generic prepared fixed-radius threshold/count |

The full repaired 16-row matrix passed on local Linux:

- Artifact: `docs/reports/goal2041_embree_cpu_partner_all_thread_large_repaired_v2`
- Status: 16 pass / 0 fail / 0 timeout
- Host: `192.168.1.20`
- Threads: 8
- NumPy: `2.4.4`
- Torch: not installed
- Numba: not installed

## Design Boundary

This solves the v2 Embree CPU-partner performance problem for the tested summary/decision contracts. It does not solve every richer app requirement.

Still unsatisfied as separate design requirements:

- exact K=3 facility fallback ranking at large scale
- exact ANN ranking or recall/latency optimization
- exact Hausdorff distance and witness extraction at large scale
- broad general polygon overlay

The design lesson is crisp: RTDL should keep the engine app-agnostic, but v2 needs explicit generic partner-side candidate and reduction policies. Fixed-radius threshold/count is already a good generic primitive. Polygon bbox broadphase is a useful partner policy. Exact ranked KNN and exact Hausdorff need a future generic spatial-index partner adapter, not app-custom code inside Embree.

## Claim Boundary

Allowed:

- Embree CPU-partner weak-row repair evidence exists.
- The repaired full 16-row local Linux matrix passes.
- The tested decision/summary contracts are now much faster.

Not allowed:

- v2.0 release readiness.
- broad all-app speedup claims.
- exact ranked KNN solved.
- exact Hausdorff distance solved.
- generic polygon overlay solved.

## Verdict

`accept-with-boundary`
