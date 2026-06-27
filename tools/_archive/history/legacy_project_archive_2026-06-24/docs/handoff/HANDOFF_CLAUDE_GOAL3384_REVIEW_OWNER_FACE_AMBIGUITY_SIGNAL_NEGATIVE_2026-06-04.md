# Handoff: Claude Review Goal3383 Owner-Face Ambiguity Signal Negative Probe

Please perform a read-only external review of Goal3383.

## Context

Goal3381 showed full-slice exact parity when the caller supplies the correct
seven-point ambiguity set and owner-face priorities. Your Goal3382 review
accepted that with the boundary that ambiguity-set discovery and independent
priority derivation remain the primary blockers.

Goal3383 tests the first obvious discovery family: simple topology/candidate
signals over live OptiX candidate rows and CDB-derived incident/topology rows.

## Files To Inspect

- `scripts/goal3383_owner_face_ambiguity_signal_negative_probe.py`
- `docs/reports/goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.json`
- `docs/reports/goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.md`
- `tests/goal3383_owner_face_ambiguity_signal_negative_probe_test.py`
- Supporting context:
  - `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.md`
  - `docs/reviews/goal3382_claude_review_selective_live_owner_face_route_probe_2026-06-04.md`

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test `
  tests.goal3381_owner_face_selective_live_route_probe_test
```

Result: `Ran 10 tests ... OK`.

Pod at commit `80292b5f`:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test \
  tests.goal3381_owner_face_selective_live_route_probe_test \
  tests.goal3380_selective_owner_face_cupy_pipeline_test \
  tests.goal3378_owner_face_all_point_priority_negative_probe_test
```

Result: `Ran 14 tests ... OK`.

Owner-face chain on the same pod commit:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3365_owner_face_cupy_selection_continuation_test \
  tests.goal3367_owner_face_cupy_pipeline_composition_test \
  tests.goal3368_owner_face_cupy_selection_review_gap_closure_test \
  tests.goal3369_owner_face_cupy_real_fixture_pipeline_test \
  tests.goal3372_owner_face_cupy_route_fixture_probe_test \
  tests.goal3374_owner_face_cupy_runtime_cdb_route_probe_test \
  tests.goal3376_owner_face_cupy_optix_candidate_route_probe_test \
  tests.goal3378_owner_face_all_point_priority_negative_probe_test \
  tests.goal3380_selective_owner_face_cupy_pipeline_test \
  tests.goal3381_owner_face_selective_live_route_probe_test \
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test
```

Result: `Ran 41 tests ... OK`.

## Review Questions

1. Does Goal3383 correctly keep exact OptiX output out of the signal inputs and
   use it only as an evaluation oracle?
2. Are the tested simple signals represented fairly?
3. Is the negative conclusion justified: no tested signal can be promoted as a
   default route because the best signal selects false-positive points 651 and
   652?
4. Does the report correctly avoid overclaiming and keep all release/default
   route/public speedup/RayJoin reproduction/true-zero-copy boundaries blocked?
5. What should the next engineering target be: a richer generic boundary-event
   primitive, a stronger topology policy, larger-scale characterization, or a
   different route?

## Output

Write the review to:

`docs/reviews/goal3384_claude_review_owner_face_ambiguity_signal_negative_probe_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
