# Call For Review - Goal4994 Prepared Reprojection Segment Arrays

Date: 2026-07-04

Reviewer requested: Claude and Antigravity

## Documents To Review

- `history/internal_docs/goal4994_prepared_reprojection_segment_arrays_result_2026-07-04.md`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4994_prepared_reprojection_arrays_repeat_top4.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4990_binary_repeat_protocol_test.py`

## Context

Goal4993 reduced top4 prepared/query-many median to `0.553s` but reprojection remained `~0.19-0.21s`. Inspection showed each measured run uploaded all left/right segment coordinate arrays to the GPU. Goal4994 moves those arrays into the prepared operator session and reuses them.

## Key Evidence

Top4 County x Zipcode:

```text
Goal4991 no prepared operator session median      = 2.41712380386889s
Goal4992 prepared LSI/PIP sessions median         = 0.9024808872491121s
Goal4993 prepared vertex query points median      = 0.5531838703900576s
Goal4994 prepared reprojection arrays median      = 0.3665195722132921s

Goal4994 median LSI phase                         = 0.0033884719014167786s
Goal4994 median downstream floor                  = 0.36127020977437496s
```

Reprojection phase:

```text
before: ~0.19-0.21s
after:  ~0.004-0.014s
```

## Review Questions

1. Does Goal4994 correctly identify repeated segment-coordinate GPU upload as the main reprojection cost?
2. Is the prepared segment device array reuse correctly scoped to the app-level prepared/query-many route?
3. Does it avoid RTDL core changes and RayJoin-specific core primitives?
4. Does the top4 evidence support the claimed reprojection improvement?
5. Is it valid to report top4 prepared/query-many median `0.367s`, while rejecting one-shot and paper-text claims?
6. Is it correct to identify sort/run metadata and carrier construction as the next remaining bottlenecks?

## Requested Verdict Label

```text
approve_goal4994_prepared_reprojection_arrays__sort_carrier_next
```
