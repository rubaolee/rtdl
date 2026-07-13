# Call For Review - Goal4993 Prepared Vertex Query Points

Date: 2026-07-04

Reviewer requested: Claude and Antigravity

## Documents To Review

- `history/internal_docs/goal4993_prepared_vertex_points_result_2026-07-04.md`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4993_prepared_vertex_points_repeat_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4990_binary_repeat_protocol_test.py`

## Context

Goal4992 removed the LSI setup bottleneck in the prepared/query-many route. A downstream decomposition then showed that vertex PIP still spent hot time preparing the same vertex query points every measured run, especially for top4 zipcode vertices.

Goal4993 moves repeated vertex query-point preparation into the prepared operator session while leaving midpoint query points per-run.

## Key Evidence

Top4 County x Zipcode:

```text
Goal4991 no prepared operator session median = 2.41712380386889s
Goal4992 prepared LSI/PIP sessions median    = 0.9024808872491121s
Goal4993 prepared vertex points median       = 0.5531838703900576s

Goal4993 median LSI phase                    = 0.0033676400780677795s
Goal4993 median downstream floor             = 0.5494433902204037s
lsi_row_count                                = 428322
descriptor_pair_count                        = 15014
```

Session preparation now includes:

```text
session_prepare_vertex_points_map0_in_map1_sec = 0.053136
session_prepare_vertex_points_map1_in_map0_sec = 0.329662
```

## Review Questions

1. Does Goal4993 correctly identify repeated vertex query-point preparation as a removable prepared-session cost?
2. Is the implementation correctly scoped to the app-level prepared/query-many route?
3. Does it avoid moving RayJoin-specific semantics into RTDL core?
4. Does the result preserve structural consistency across measured repeats?
5. Is it valid to report top4 prepared/query-many writer-free median as `0.553s`, while rejecting one-shot and paper-text claims?
6. Is it valid to say LSI is no longer the steady-state bottleneck after Goal4992/4993?
7. Is the next target correctly identified as the remaining downstream columnar floor?

## Requested Verdict Label

```text
approve_goal4993_prepared_vertex_points__downstream_floor_next
```
