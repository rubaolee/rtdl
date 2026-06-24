# Handoff: Gemini Review Goal3673 Ordinal-Selective Owner-Side Filter

Please perform an independent review of Goal3673 in the RTDL repo.

## Context

The user explicitly rejected v2.9 closeout and asked for major performance
improvements, not minor tuning. Goal3671 proved that side-aware owner-face
filtering can repair the full-county RayJoin PIP mismatch `47264 != 47262` when
two ambiguous point ids are manually supplied. Goal3673 extends that work.

## Files To Inspect

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3673_ordinal_selective_owner_side_filter_test.py`
- `tests/goal3671_side_aware_owner_face_filter_test.py`
- `tests/goal3602_v2_9_benchmark_status_after_resident_evidence_test.py`
- `docs/reports/goal3673_ordinal_selective_owner_side_filter_2026-06-06.md`
- `docs/reports/goal3673_rayjoin_ordinal_owner_side_probe_a5000/full_county_ordinal_owner_side_route_probe.json`
- `docs/reports/goal3673_rayjoin_ordinal_owner_side_probe_a5000/full_county_selective_ordinal_owner_side_route_probe.json`
- `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the new ordinal-aware side filter remain app-agnostic, or does it
   smuggle CDB/RayJoin ownership policy into the engine/runtime?
2. Is the negative all-point probe interpreted correctly: owner-side filtering
   is not a universal replacement for membership?
3. Is the positive selective probe strong enough to claim the immediate
   full-county `47264 != 47262` mismatch is repaired when the caller supplies
   selected ambiguity input ordinals and owner-side columns?
4. Are claim boundaries preserved? In particular, no release, public speedup,
   RTDL-beats-RayJoin, RayJoin reproduction, true-zero-copy, or native default
   route claim should be authorized.
5. Are the tests adequate and are there missing acceptance bars before this
   could become a default route?

## Validation To Run

If practical, run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3673_ordinal_selective_owner_side_filter_test tests.goal3671_side_aware_owner_face_filter_test tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test
```

## Expected Output

Write your review to:

```text
docs/reviews/goal3674_gemini_review_goal3673_ordinal_selective_owner_side_filter_2026-06-06.md
```

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`. Be explicit about any boundary.
