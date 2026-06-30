# Handoff: Claude Review Goal3381 Selective Live Owner-Face Route Probe

Please perform a read-only external review of Goal3381.

## Context

RTDL v2.8 is hardening the RayJoin-style owner-face continuation path while
preserving the core rule that the native engine stays app-agnostic.

Recent chain:

- Goal3376: live OptiX candidate device columns for seven known mismatch points;
  stored artifact used only as expected-answer oracle.
- Goal3378: all-point incident-chain-length priority negative probe; rejected as
  a default policy because it drops true exact rows.
- Goal3380: generic selective CuPy owner-face pipeline; caller supplies
  `selected_point_ids`, selected candidates are filtered, non-selected rows pass
  through.
- Goal3381: full 512-chain CDB slice probe using live OptiX candidates for all
  points plus selective CuPy repair only for the caller-supplied known ambiguity
  set.

## Files To Inspect

- `scripts/goal3381_owner_face_selective_live_route_probe.py`
- `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.json`
- `docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.md`
- `tests/goal3381_owner_face_selective_live_route_probe_test.py`
- Supporting implementation:
  - `src/rtdsl/closed_shape_topology.py`
  - `tests/goal3380_selective_owner_face_cupy_pipeline_test.py`
  - `docs/reports/goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.md`
  - `docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.md`

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3381_owner_face_selective_live_route_probe_test `
  tests.goal3380_selective_owner_face_cupy_pipeline_test `
  tests.goal3378_owner_face_all_point_priority_negative_probe_test
```

Result: `Ran 9 tests ... OK (skipped=1)`.

Pod at commit `23e74ab9`:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3381_owner_face_selective_live_route_probe_test \
  tests.goal3380_selective_owner_face_cupy_pipeline_test \
  tests.goal3378_owner_face_all_point_priority_negative_probe_test \
  tests.goal3376_owner_face_cupy_optix_candidate_route_probe_test \
  tests.goal3374_owner_face_cupy_runtime_cdb_route_probe_test
```

Result: `Ran 13 tests ... OK`.

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
  tests.goal3381_owner_face_selective_live_route_probe_test
```

Result: `Ran 36 tests ... OK`.

## Review Questions

1. Does Goal3381 genuinely use live OptiX candidate device columns for the full
   slice rather than replaying stored candidate/topology/incident artifacts?
2. Does the selective CuPy continuation remain app-agnostic at the primitive
   level, with app policy restricted to the caller-provided ambiguity set and
   owner-face ranks?
3. Does the result honestly show full-slice exact-row parity for this fixture:
   1429 candidate rows, 1417 exact rows, 12 extras removed, 0 missing, 0 extra?
4. Are all claim boundaries still correctly blocked: no release, no default
   route, no public speedup, no RayJoin reproduction, no RTDL-beats-RayJoin, no
   true-zero-copy?
5. What is the next highest-risk missing piece before this can become a default
   front door: ambiguity-set discovery, stronger topology policy, larger CDB
   scale, or something else?

## Output

Write the review to:

`docs/reviews/goal3382_claude_review_selective_live_owner_face_route_probe_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
