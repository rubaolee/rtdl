# Goal1312: v1.5 Jaccard OptiX-Slower Reason

Date: 2026-05-05

## Decision

The vague `optix_still_slower_with_reason` inventory blocker is now resolved as a recorded diagnostic. `polygon_set_jaccard` remains `diagnostic_blocked`, but for the remaining native implementation work, not because the slower-than-Embree behavior is unexplained.

## Evidence

Source artifacts:

- `docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_pod_results/embree_summary_128.json`
- `docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_pod_results/optix_summary_128.json`
- `docs/reports/goal1311_v1_5_jaccard_generic_fail_closed_collection_pod_results/optix_slower_reason.json`

At 128 copies with `COLLECT_K_BOUNDED` capacity 512:

| Metric | Embree | OptiX |
|---|---:|---:|
| Candidate pairs | 384 | 256 |
| Candidate discovery seconds | 0.1197133231908083 | 1.3446430154144764 |
| Native exact continuation seconds | 0.03697788529098034 | 0.06522038020193577 |
| Observed candidate+continuation seconds | 0.15669120848178864 | 1.4098633956164122 |
| Jaccard intersection | 640 | 640 |
| Jaccard union | 2432 | 2432 |
| Jaccard similarity | 0.2631578947368421 | 0.2631578947368421 |

Computed slowdown:

| Metric | Slowdown |
|---|---:|
| Candidate discovery | 11.232191869498777x |
| Native exact continuation | 1.7637671729660633x |
| Observed candidate+continuation pipeline | 8.99771856555866x |

## Explanation

This Jaccard path is not a monolithic GPU Jaccard kernel. It performs multi-pass RT-assisted candidate discovery, transfers and normalizes candidate-pair IDs, then runs native exact set-area scoring. In the recorded pod run, OptiX produced a smaller complete candidate set than Embree, but OptiX spent more time in candidate discovery and exact native continuation. Therefore correctness matched while observed performance remained slower.

This is enough for v1.5 diagnostic closure because it explains the slower result without overclaiming. It is not enough for positive public performance wording.

## Remaining Blockers

- Native device-level fail-closed bounded collection implementation.
- Native score reduction after complete candidate coverage.

## Boundary

Correctness-ready diagnostic only. No positive Jaccard speedup wording, no whole-app GIS claim, and no native device-level Jaccard reduction promotion.
