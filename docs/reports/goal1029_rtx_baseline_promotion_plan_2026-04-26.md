# Goal1029 RTX Baseline Promotion Plan

Date: 2026-04-26

Input evidence:

- `docs/reports/goal1028_a5000_rtx_cloud_batch_report_2026-04-26.md`
- `docs/reports/goal1028_claude_review_2026-04-26.md`
- `docs/reports/goal1028_gemini_review_2026-04-26.md`

## Purpose

Goal1028 proved that the current app subpaths can produce RTX/OptiX artifacts on an RTX A5000. Goal1029 defines what is still required before any of those artifacts can become public speedup claims.

This plan does not authorize speedup claims.

## Promotion Rule

An app subpath can move from `rtx_artifact_collected` to `speedup_claim_candidate` only when all conditions hold:

1. Same-semantics CPU/Embree/PostGIS/SciPy or other relevant baseline exists.
2. Timing phases are comparable and exclude unrelated validation/setup unless the claim is explicitly whole-app.
3. Correctness parity is established for the same output semantics.
4. RTX query phase beats the fastest comparable baseline by the current public wording threshold.
5. The claim text follows `rtdsl.rtx_public_wording_matrix()`.

## App Baseline Matrix

| App | RTX evidence status | Main RTX subpath | Required baseline work before claim | Local before next pod? | Priority |
|---|---|---|---|---|---|
| `robot_collision_screening` | artifact collected | prepared pose flags | Re-run same pose/obstacle semantics on CPU and Embree; check timing floor and outlier handling. | Yes | P0 |
| `outlier_detection` | artifact collected | fixed-radius density summary | Compare against CPU, Embree, and SciPy/KDTree for threshold-count summary, not whole clustering. | Yes | P0 |
| `dbscan_clustering` | artifact collected | fixed-radius core flags | Compare against CPU, Embree, and SciPy/KDTree for core-flag summary only; full DBSCAN cluster expansion remains outside claim. | Yes | P0 |
| `database_analytics:sales_risk` | artifact collected | prepared compact DB summary | Compare CPU compact summary, Embree compact summary, and PostgreSQL indexed same-semantics compact outputs for the `sales_risk` scenario. | Linux preferred | P0 |
| `database_analytics:regional_dashboard` | artifact collected | prepared compact DB summary | Compare CPU compact summary, Embree compact summary, and PostgreSQL indexed same-semantics compact outputs for the `regional_dashboard` scenario. | Linux preferred | P0 |
| `service_coverage_gaps` | artifact collected | prepared gap summary | Compare CPU, Embree, and SciPy radius-summary semantics; keep nearest-row behavior out of claim. | Yes | P1 |
| `event_hotspot_screening` | artifact collected | prepared count summary | Compare CPU, Embree, and SciPy same-radius count summary; avoid full app/general GIS claim. | Yes | P1 |
| `facility_knn_assignment` | artifact collected | coverage threshold prepared | Compare only coverage-threshold decisions against CPU/Embree/SciPy; ranked KNN assignment remains outside claim. | Yes | P1 |
| `road_hazard_screening` | artifact collected | native segment/polygon summary gate | Compare CPU, Embree, and PostGIS if available for compact summary semantics. | Local CPU/Embree yes; PostGIS Linux preferred | P1 |
| `segment_polygon_hitcount` | artifact collected | native hit-count gate | Compare CPU, Embree, and PostGIS hit-count semantics. | Local CPU/Embree yes; PostGIS Linux preferred | P1 |
| `segment_polygon_anyhit_rows` | artifact collected | bounded pair-row any-hit | Compare bounded output-capacity row semantics against CPU and PostGIS; capacity/overflow must be part of contract. | Local CPU yes; PostGIS Linux preferred | P1 |
| `graph_analytics` | artifact collected after GEOS repair | visibility any-hit + native graph-ray gate | Separate visibility-edge any-hit from BFS/triangle continuation; compare CPU and Embree graph-ray candidate semantics first. CPU oracle checks require GEOS development libraries (`libgeos-dev`/`pkg-config` on Linux or equivalent). | Yes, if GEOS is available | P1 |
| `hausdorff_distance` | artifact collected | directed threshold prepared | Compare threshold decision only against CPU/Embree/SciPy; exact Hausdorff distance remains outside claim. | Yes | P2 |
| `ann_candidate_search` | artifact collected | candidate threshold prepared | Compare candidate coverage threshold against CPU/Embree/SciPy; ANN ranking/recall remains outside claim. | Yes | P2 |
| `barnes_hut_force_app` | artifact collected | node coverage prepared | Compare node-coverage decision against CPU/Embree; no force-vector solver claim. | Yes | P2 |
| `polygon_pair_overlap_area_rows` | artifact collected | LSI/PIP candidate discovery + exact continuation | Preserve full phase accounting: candidate discovery plus exact refinement. Compare CPU/Embree/PostGIS whole bounded unit-cell semantics before claim. | Local CPU/Embree yes; PostGIS Linux preferred | P2 |
| `polygon_set_jaccard` | artifact collected | LSI/PIP candidate discovery + exact continuation | Preserve full phase accounting: candidate discovery plus exact Jaccard continuation. Compare CPU/Embree/PostGIS whole bounded unit-cell semantics before claim. | Local CPU/Embree yes; PostGIS Linux preferred | P2 |

## Immediate Local Work

The next local work should not use another pod. It should build a baseline runner or baseline audit that:

- Reuses the same scenario parameters from the Goal1028 artifacts.
- Runs CPU and Embree where available on this Mac.
- Marks PostgreSQL/PostGIS and RTX reruns as pending Linux/cloud tasks instead of blocking local progress.
- Emits a per-app status: `baseline_ready`, `baseline_partial`, or `needs_linux_or_cloud`.

## Cloud Efficiency Rule

The next pod should not be launched for one app at a time. It should wait until:

- local baseline extraction is done,
- commands are batched,
- missing Linux/PostGIS dependencies are known,
- and the expected result files are listed before starting the pod.

## Current Conclusion

All app subpaths have RTX evidence, but zero app subpaths should yet be described publicly as RTX speedup wins. The project is ready for baseline comparison work, not release wording promotion.
