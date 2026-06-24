# Goal970 A5000 Artifact Review And Claim Boundary

Date: 2026-04-26

## Scope

This report reviews the copied RTX A5000 artifacts from Goal969 and records
what can and cannot be claimed before public documentation is refreshed.

Primary artifact directory:

```text
docs/reports/cloud_2026_04_26/runpod_a5000_0900/
```

The standard `docs/reports/goal759_*`, `goal761_group_*`, `goal811_*`,
`goal877_*`, `goal887_*`, `goal889_*`, `goal933_*`, and `goal934_*` report
paths were refreshed from that directory so existing gates analyze the latest
April 26 A5000 evidence.

## Artifact Report Status

| Group | Status | Entries | Meaning |
| --- | --- | ---: | --- |
| A robot | `ok` | 1 | Prepared pose-flag OptiX artifact is parseable and contract-complete. |
| B fixed-radius | `ok` | 2 | Outlier and DBSCAN compact threshold/core summaries are contract-complete. |
| C database | `ok` | 2 | Sales-risk and regional-dashboard DB compact summaries are contract-complete. |
| D spatial | `ok` | 3 | Service coverage, event hotspot, and facility threshold summaries are contract-complete. |
| E segment/polygon | `ok` | 3 | Road hazard, segment/polygon hitcount, and bounded pair-row gates are contract-complete. |
| F graph | `ok` | 1 | Graph visibility/BFS/triangle gate is contract-complete after GEOS dependency remedy. |
| G prepared decision | `ok` | 3 | Hausdorff threshold, ANN candidate coverage, and Barnes-Hut node coverage are contract-complete. |
| H polygon | `ok` | 2 | Polygon overlap and Jaccard native-assisted phase gates are contract-complete after analyzer fix. |

Generated artifact-review reports:

```text
docs/reports/goal969_artifact_report_group_a_robot_2026-04-26.md
docs/reports/goal969_artifact_report_group_b_fixed_radius_2026-04-26.md
docs/reports/goal969_artifact_report_group_c_database_2026-04-26.md
docs/reports/goal969_artifact_report_group_d_spatial_2026-04-26.md
docs/reports/goal969_artifact_report_group_e_segment_polygon_2026-04-26.md
docs/reports/goal969_artifact_report_group_f_graph_2026-04-26.md
docs/reports/goal969_artifact_report_group_g_prepared_decision_2026-04-26.md
docs/reports/goal969_artifact_report_group_h_polygon_2026-04-26.md
```

## Runtime Conclusions

| App / path | RTDL RTX evidence | Median native/query phase |
| --- | --- | ---: |
| Robot collision / prepared pose flags | OptiX any-hit pose-flag summary ran on RTX A5000; large timing plus smaller validated companion. | `0.000367 s` |
| Outlier detection / density summary | OptiX fixed-radius threshold summary ran; smaller validated companion confirms oracle parity. | `0.005078 s` |
| DBSCAN / core flags | OptiX fixed-radius core summary ran; smaller validated companion confirms oracle parity. | `0.000853 s` |
| DB sales risk | OptiX prepared DB compact summary ran with native phase counters. | `0.100171 s` |
| DB regional dashboard | OptiX prepared DB compact summary ran with native phase counters. | `0.135571 s` |
| Service coverage gaps | OptiX fixed-radius threshold summary ran. | `0.215130 s` |
| Event hotspot screening | OptiX fixed-radius count summary ran. | `0.326126 s` |
| Facility coverage threshold | OptiX fixed-radius threshold decision ran. | `0.000585 s` |
| Road hazard summary | Native OptiX segment/polygon compact summary ran with validation phase. | `0.182339 s` |
| Segment/polygon hitcount | Native OptiX custom-AABB hitcount ran with validation phase. | `0.004443 s` |
| Segment/polygon bounded pair rows | Native OptiX bounded pair-row traversal ran. | `0.003625 s` |
| Graph visibility/BFS/triangle gate | OptiX graph gate ran strict after GEOS dependency remedy. | `1.583060 s` |
| Hausdorff threshold | OptiX fixed-radius threshold decision ran. | `0.001217 s` |
| ANN candidate coverage | OptiX fixed-radius threshold decision ran. | `0.000632 s` |
| Barnes-Hut node coverage | OptiX fixed-radius threshold decision ran. | `0.001540 s` |
| Polygon pair overlap | OptiX native-assisted candidate discovery ran; exact continuation remains separate CPU/native-assisted phase. | `3.513415 s` |
| Polygon set Jaccard | OptiX native-assisted candidate discovery ran; exact continuation remains separate CPU/native-assisted phase. | `3.642833 s` |

## Important Boundaries

- This evidence supports "RTDL can execute the listed RT sub-paths on RTX-class
  NVIDIA hardware through OptiX" after review.
- It does not yet support broad whole-app speedup claims.
- It does not convert timing-only artifacts into correctness evidence; companion
  validation artifacts must be referenced separately where the large run skips
  validation.
- Polygon overlap and Jaccard remain native-assisted phase claims: OptiX does
  candidate discovery, while exact area/Jaccard continuation is still a separate
  refinement phase.
- DB workloads remain prepared compact-summary RTDL workloads, not DBMS or SQL
  engine claims.
- The graph artifact passed after installing `libgeos-dev` and `pkg-config`;
  future cloud runbooks should include those packages before graph gates.

## Tooling Fix

The artifact analyzer initially reported Group H as `needs_attention` because
it failed to pass `native_exact_continuation_sec` from the polygon artifact into
the cloud contract checker. The artifact itself already contained the phase.

Fixed files:

```text
scripts/goal762_rtx_cloud_artifact_report.py
tests/goal762_rtx_cloud_artifact_report_test.py
```

Verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal762_rtx_cloud_artifact_report_test
Ran 11 tests
OK
```

## Verdict

The A5000 artifacts are complete enough for post-cloud review and documentation
refresh. Public claims must stay scoped to the prepared/native RT sub-paths
listed above until baseline comparison, documentation update, and 2-AI
consensus are complete.
