# Handoff: Claude Review Goal3385/3386 Boundary-Event Signal Route

Please perform a read-only external review of Goals 3385 and 3386.

## Context

Your Goal3384 review accepted Goal3383 and recommended richer generic
boundary-event evidence because topology-only signals could not distinguish the
651/652 false positives from the true ambiguous points.

Codex then implemented:

- Goal3385: generic CuPy continuation
  `run_selective_closed_shape_boundary_event_membership_pipeline_cupy`, which
  filters only caller-selected candidate rows by zero-boundary event pairs and
  passes all other rows through.
- Goal3386: bounded constructive route probe that derives selected points from
  live OptiX candidate device columns + live OptiX boundary-event device columns
  + CDB-derived generic topology/incident features, then uses the Goal3385
  helper to match live exact rows.

## Files To Inspect

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal3385_selective_boundary_event_cupy_filter_2026-06-04.md`
- `tests/goal3385_selective_boundary_event_cupy_filter_test.py`
- `scripts/goal3386_boundary_event_signal_selective_route_probe.py`
- `docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.json`
- `docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.md`
- `tests/goal3386_boundary_event_signal_selective_route_probe_test.py`
- Context:
  - `docs/reviews/goal3384_claude_review_owner_face_ambiguity_signal_negative_probe_2026-06-04.md`

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3386_boundary_event_signal_selective_route_probe_test `
  tests.goal3385_selective_boundary_event_cupy_filter_test `
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test
```

Result: `Ran 12 tests ... OK (skipped=2)`.

Pod at commit `49d2ea1b`:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3386_boundary_event_signal_selective_route_probe_test \
  tests.goal3385_selective_boundary_event_cupy_filter_test \
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test \
  tests.goal3381_owner_face_selective_live_route_probe_test
```

Result: `Ran 17 tests ... OK`.

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
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test \
  tests.goal3385_selective_boundary_event_cupy_filter_test \
  tests.goal3386_boundary_event_signal_selective_route_probe_test
```

Result: `Ran 48 tests ... OK`.

## Review Questions

1. Is the Goal3385 helper genuinely app-agnostic and safe as a generic
   continuation? Does it avoid inferring ambiguous points or app ownership?
2. Does Goal3386 correctly keep live exact output out of the signal inputs and
   use it only for evaluation?
3. Does the bounded signal honestly derive the same seven true candidate-extra
   points without the fixed Goal3328 point list?
4. Does the Goal3385 helper drop exactly 12 selected candidate extras and match
   the 1417-row live exact output on the 512-chain slice?
5. Are the boundaries correct: no release, no public speedup, no RayJoin paper
   reproduction, no RTDL-beats-RayJoin, no true zero-copy, no native default
   route?
6. What remains before this can be proposed as a default route candidate:
   larger CDB slices, other RayJoin datasets, signal simplification,
   deterministic tolerance policy, native lowering, or something else?

## Output

Write the review to:

`docs/reviews/goal3387_claude_review_boundary_event_signal_route_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
