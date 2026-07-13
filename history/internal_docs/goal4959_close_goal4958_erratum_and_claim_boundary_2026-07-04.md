# Goal4959 Close Goal4958 Erratum And Claim Boundary

Date: 2026-07-04

## Exit Label

`completed_goal4958_erratum_fresh_route_boundary_closed`

## Purpose

Close the Goal4958 correction loop after Claude identified that the
`0.086s / 2.04x` headline used a mismatched denominator.

## What Was Corrected

The incorrect headline was:

```text
RTDL writer-free binary route is about 2.04x slower than AuthorPatch overlay compute.
```

This is now retracted as a same-denominator fresh-overlay claim.

Correct classification:

```text
fresh writer-free binary route: ~0.90s
AuthorPatch overlay compute:    0.0421s
fresh comparison:               ~21x slower

cached/replay body after exact LSI already computed once: ~0.086s
cached/replay arithmetic ratio vs AuthorPatch:            ~2.04x
```

The cached/replay ratio is useful diagnostic evidence, but it is not an
authorized headline because the RTDL numerator excludes first LSI computation
while the author denominator includes overlay compute.

## Files Updated

- `history/internal_docs/goal4958_prepared_hot_lsi_replay_and_exact_device_output_audit_2026-07-04.md`
- `history/internal_docs/v2_14_3_rayjoin_binary_operator_status_problem_solution_progress_plan_2026-07-04.md`
- `history/internal_docs/call_for_review_goal4958_prepared_hot_lsi_replay_2026-07-04.md`
- `history/internal_docs/goal4958_erratum_claude_review_2x_headline_retracted_2026-07-04.md`
- `Paper-reproduction-apps/rayjoin-paper/README.md`

## Allowed Claim

The v2.14.3 RayJoin writer-free binary route has a real fresh-route improvement:

```text
~2.92s -> ~0.90s
```

This is approximately a 3x improvement over the original numeric binary route.
It remains about 21x slower than the patched author overlay compute baseline on
a fresh same-denominator comparison.

The cached/replay body after exact LSI pair ids have already been computed once
is about 0.086s.

## Forbidden Claims

- Fresh overlay runtime is 0.086s.
- Cold-start runtime is 0.086s.
- Paper text-output runtime is 0.086s.
- RTDL is only 2.04x slower than AuthorPatch on a same-denominator fresh
  overlay comparison.
- Candidate device columns are exact LSI pair-id rows.
- Left-id count device columns are sufficient for RayJoin reprojection/sort.
- RTDL core already exposes exact planar-map LSI `{left_id, right_id}` device
  columns.

## Verification

Local tests:

```text
py -m unittest tests.goal4955_projected_descriptor_pipeline_test \
  tests.goal4956_columnar_xsect_pipeline_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test

Ran 8 tests in 0.106s
OK (skipped=2)
```

Public RayJoin app/README leak scan:

```text
rg -n "Goal[0-9]+|goal[0-9]+|history/internal_docs|call_for_review|verdict" \
  Paper-reproduction-apps/rayjoin-paper/README.md \
  Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py

no matches
```

Dangerous-headline scan:

```text
rg -n "2\\.04x slower|2x range|same order of magnitude|remaining gap.*2x|fresh.*0\\.086" \
  history/internal_docs/goal4958_prepared_hot_lsi_replay_and_exact_device_output_audit_2026-07-04.md \
  history/internal_docs/v2_14_3_rayjoin_binary_operator_status_problem_solution_progress_plan_2026-07-04.md \
  history/internal_docs/call_for_review_goal4958_prepared_hot_lsi_replay_2026-07-04.md \
  Paper-reproduction-apps/rayjoin-paper/README.md
```

Only negative/forbidden-claim wording remains.

## Next Goal

Goal4960 should run an explicit same-input fresh vs cached/replay measurement
and report both denominators in one artifact.
