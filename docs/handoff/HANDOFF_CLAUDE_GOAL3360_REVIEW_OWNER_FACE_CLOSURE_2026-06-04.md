# Handoff: Claude Follow-Up Review Goal3358-3359 Owner-Face Closure

Please review whether Goals3358-3359 close the boundaries from your Goal3357 review.

Expected output:

- `docs/reviews/goal3360_claude_review_owner_face_columnar_closure_2026-06-04.md`

## Context

Your Goal3357 review of Goals3349-3356 returned `accept-with-boundary` and identified four pre-lowering gaps:

1. Missing end-to-end columnar fixture over the seven known mismatch points.
2. Silent topology-missing drop was undocumented.
3. Optional topology presence columns were not tested in the columnar filter.
4. Conflicting owner-face selection rows should be covered explicitly.

## New Work To Review

Commit `6a47e36a`:

- `docs/reports/goal3358_owner_face_columnar_known_mismatch_fixture_2026-06-04.md`
- `tests/goal3358_owner_face_columnar_known_mismatch_fixture_test.py`

Commit `174deb39`:

- `src/rtdsl/closed_shape_topology.py`
- `docs/reports/goal3359_owner_face_columnar_review_gap_closure_2026-06-04.md`
- `tests/goal3359_owner_face_review_gap_closure_test.py`

## Validation Already Run

- Goal3358 fixture alone: `Ran 3 tests in 0.004s OK`
- Goal3358 plus columnar stack: `Ran 29 tests in 0.018s OK`
- Broad owner-face chain with Goal3358: `Ran 80 tests in 0.035s OK`
- Goal3359 focused/gap set: `Ran 20 tests in 0.019s OK`
- Full owner-face chain with Goal3359: `Ran 85 tests in 0.036s OK`

## Review Questions

1. Does Goal3358 close the real-artifact columnar fixture gap?
2. Does Goal3359 adequately document and test `missing_topology = drop_candidate`?
3. Are topology face-presence columns now tested adequately?
4. Is conflicting owner-face selection fail-closed coverage sufficient?
5. What remains blocked before native/device lowering?

## Required Boundaries

- Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
- Do not authorize release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy claims.
- Native engine must not infer ownership policy.
