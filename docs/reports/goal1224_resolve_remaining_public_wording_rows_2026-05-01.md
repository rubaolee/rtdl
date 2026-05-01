# Goal1224 Resolve Remaining Public Wording Rows

Date: 2026-05-01

This packet resolves the remaining not-public-reviewed rows from valid Goal1194/Goal1193 same-contract evidence. It authorizes only source-of-truth status changes after external AI review; it does not move the v0.9.8 release tag and does not authorize whole-app claims.

## Summary

- source intake: `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json`
- minimum positive public ratio: `1.2`
- valid: `True`
- promote to reviewed: `hausdorff_distance`
- mark blocked after review: `graph_analytics, polygon_pair_overlap_area_rows`

## Decisions

| App | Path | Embree phase sec | OptiX phase sec | Ratio | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| `graph_analytics` | `graph_visibility_edges` | `1.000280` | `2.000505` | `0.50x` | `public_wording_blocked` |
| `polygon_pair_overlap_area_rows` | `native_assisted_lsi_pip_candidate_discovery` | `2.896597` | `3.452362` | `0.84x` | `public_wording_blocked` |
| `hausdorff_distance` | `directed_threshold_prepared` | `1.680214` | `0.122389` | `13.73x` | `public_wording_reviewed` |

## Wording And Boundaries

### graph_analytics / graph_visibility_edges

RTDL's graph visibility_edges RTX sub-path has valid same-contract evidence, but measured 2.000505 s versus 1.000280 s for Embree, so the raw Embree-over-OptiX ratio is 0.50x and no positive public RTX speedup wording is authorized.

Boundary: Only the bounded graph visibility_edges any-hit traversal sub-path is covered; BFS frontier bookkeeping, triangle set-intersection, shortest-path logic, graph database behavior, distributed analytics, Python setup, and whole-app graph speedup remain outside this wording.

### polygon_pair_overlap_area_rows / native_assisted_lsi_pip_candidate_discovery

RTDL's polygon-pair candidate-discovery RTX sub-path has valid same-contract evidence, but measured 3.452362 s versus 2.896597 s for Embree, so the raw Embree-over-OptiX ratio is 0.84x and no positive public RTX speedup wording is authorized.

Boundary: Only native-assisted LSI/PIP candidate discovery is covered; exact polygon-area continuation, row materialization, Python setup, arbitrary polygon geometry, and whole-app polygon-overlap speedup remain outside this wording.

### hausdorff_distance / directed_threshold_prepared

RTDL's prepared Hausdorff threshold-decision RTX sub-path measured 0.122389 s and 13.73x versus the reviewed same-contract Embree directed-summary sub-path.

Boundary: Only the prepared Hausdorff <= radius threshold-decision traversal sub-path is covered; exact Hausdorff distance, KNN rows, nearest-neighbor ranking, violating-ID witness output, Python setup, validation, and whole-app speedup remain outside this wording.

