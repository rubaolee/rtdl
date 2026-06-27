# Handoff: Gemini Review For Goal3671 Side-Aware Owner-Face Filter

Please perform an independent read-only review of Goal3671 and write the review
to:

`docs/reviews/goal3672_gemini_review_goal3671_side_aware_owner_face_filter_2026-06-06.md`

## Context

The user rejected treating v2.9 as a closeout. Goal3668 is now historical and
superseded: v2.9 remains open for major performance/contract improvements.

Goal3665 showed the tuned RayJoin PIP fast route must fail closed on the full
county CDB sample: `47264 != 47262`. Goal3671 adds a generic side-aware
owner-face filter so caller-supplied `(owner_face_id, owner_side)` columns can
disambiguate closed-shape topology cases where face id alone is not enough.

## Files To Review

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3671_side_aware_owner_face_filter_test.py`
- `docs/reports/goal3671_side_aware_owner_face_filter_2026-06-06.md`
- `docs/reports/goal3671_rayjoin_topology_probe_a5000/full_county_side_aware_route_probe.json`
- `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md`
- `docs/research/future_version_to_do_list.md`

## Validation Already Run

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3671_side_aware_owner_face_filter_test tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test tests.goal3665_rayjoin_pip_fast_domain_preflight_guard_test tests.goal3668_v2_9_closeout_and_next_direction_refresh_test
```

Result: `17 tests OK (skipped=1)`.

Pod A5000:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3671_side_aware_owner_face_filter_test \
  tests.goal3362_owner_face_cupy_filter_continuation_test \
  tests.goal3364_owner_face_cupy_review_gap_closure_test \
  tests.goal3367_owner_face_cupy_pipeline_composition_test \
  tests.goal3380_selective_owner_face_cupy_pipeline_test
```

Result: `21 tests OK`.

Full-county side-aware route probe:

- exact prepared rows: `47262`
- tuned candidate rows before side-aware filter: `47264`
- selected ambiguous points: `[893, 894]`
- selected candidate rows: `4`
- selected filtered rows: `2`
- removed extra rows: `(893, 16312)`, `(894, 16312)`
- final filtered rows: `47262`
- exact multiset parity: `true`

## Review Questions

1. Does the new side-aware owner-face filter stay app-agnostic, with RayJoin/CDB
   policy remaining caller-supplied?
2. Is preserving duplicate candidate row multiplicity in the side-aware filter
   correct for the current RayJoin PIP row-count contract?
3. Does the full-county pod artifact support the bounded claim that side-aware
   topology continuation can repair the Goal3665 `47264 != 47262` mismatch when
   owner-side columns are supplied?
4. Does the report avoid overclaiming automatic/default route selection, release
   readiness, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy?
5. What is the next major engineering step: owner-side derivation, native/device
   lowering of the side-aware filter, fused exact closed-shape count, or
   something else?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Please lead with findings, then verdict and recommendations.
