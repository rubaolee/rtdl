# Call For Review - Goal4992 Prepared Operator Session

Date: 2026-07-04

Reviewer requested: Claude and Antigravity

## Documents To Review

- `history/internal_docs/goal4992_prepared_operator_session_result_2026-07-04.md`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_prepared_session_repeat_public_sample.json`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_prepared_session_repeat_top4.json`
- `history/internal_docs/goal4990_pod_artifacts_2026-07-04/goal4992_lsi_decomposition_top4_full_measured.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4990_binary_repeat_protocol_test.py`

## Context

Goal4991 showed top4 prepared/query-many repeats were still LSI-producer dominated (`~1.57s`). Goal4992 decomposed that LSI producer and found the native launch was only `~0.002s`; the dominant cost was repeated setup/ensure. Goal4992 then introduced an explicit app-level prepared operator session that loads data and prepares reusable LSI/PIP handles once before warmup/measured runs.

This is not a fresh one-shot route and not a RayJoin-specific RTDL core primitive.

## Key Evidence

Public County x Soil:

```text
before prepared operator session median = 0.12284692749381065s
after prepared operator session median  = 0.06634041108191013s
median LSI phase after session          = 0.0013317279517650604s
```

Top4 County x Zipcode:

```text
before prepared operator session median = 2.41712380386889s
after prepared operator session median  = 0.9024808872491121s
median LSI phase after session          = 0.0035249311476945877s
median downstream floor after session   = 0.8986660744994879s
```

Top4 LSI decomposition before prepared operator session:

```text
lsi_phase_sec        = 1.562966462224722
optix_launch         = 0.002200077
grouped_range_ensure = 0.932241326
scaled_cache_ensure  = 0.626564428
```

## Review Questions

1. Does Goal4992 correctly identify repeated LSI setup/ensure, not OptiX traversal, as the prior top4 LSI bottleneck?
2. Is the `--prepared-operator-session` implementation an app-layer prepared/query-many route rather than a RayJoin-specific RTDL core primitive?
3. Does the result correctly keep session prepare phases, warmup row, and measured rows separate?
4. Is it valid to say prepared operator session removes the top4 steady-state LSI bottleneck?
5. Is it valid to say top4 is now downstream-floor dominated, not LSI dominated?
6. Does the report avoid claiming fresh one-shot `0.902s`, author parity, or paper text performance?
7. Should the next goal attack the downstream floor rather than LSI setup?

## Requested Verdict Label

```text
approve_goal4992_prepared_operator_session__downstream_next
```
