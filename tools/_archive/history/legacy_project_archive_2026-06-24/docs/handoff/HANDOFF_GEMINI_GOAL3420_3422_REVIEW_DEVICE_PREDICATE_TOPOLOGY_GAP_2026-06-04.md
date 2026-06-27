# Handoff: Gemini Review for Goals3420-3422

Please perform an independent read-only review of the v2.8 device-predicate /
closed-shape topology gap chain.

## Files To Inspect

- `docs/reports/goal3420_device_predicate_page_equivalence_2026-06-04.md`
- `docs/reports/goal3420_device_predicate_page_equivalence_probe_2026-06-04.json`
- `tests/goal3420_device_predicate_page_equivalence_test.py`
- `scripts/goal3420_device_predicate_page_equivalence_probe.py`
- `docs/reports/goal3421_cupy_refined_device_predicate_page_probe_2026-06-04.md`
- `docs/reports/goal3421_cupy_refined_device_predicate_page_probe_2026-06-04.json`
- `tests/goal3421_cupy_refined_device_predicate_page_probe_test.py`
- `scripts/goal3421_cupy_refined_device_predicate_page_probe.py`
- `src/rtdsl/closed_shape_topology.py`
- `docs/reports/goal3422_closed_shape_topology_refinement_gap_2026-06-04.md`
- `tests/goal3422_closed_shape_topology_refinement_gap_test.py`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Do Goals3420-3422 correctly preserve the app-agnostic engine boundary while testing the v2.8 device-resident exact stream direction?
2. Is the Goal3420 conclusion valid: native RT device predicate columns are a strong superset on the public CDB, but not exact (`47,570` vs `47,262`, `0 missing`, `308 extra`)?
3. Is the Goal3421 conclusion valid: the CuPy simple-ring refinement removes false positives but misses GEOS/topology boundary pairs (`47,045`, `217 missing`, `0 extra`, `97` mismatched groups at `point_eps=1e-9`)?
4. Does Goal3422 correctly identify the next primitive as a generic topology-aware closed-boundary refinement contract, with topology rows supplied by the caller and no RayJoin/CDB policy embedded into native engine code?
5. Do all reports and artifacts preserve claim boundaries: no release authorization, no public speedup claim, no RT-core speedup claim, no true-zero-copy claim, no native default-route claim?

## Expected Output

Write your review to:

`docs/reviews/goal3423_gemini_review_goals3420_3422_device_predicate_topology_gap_2026-06-04.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

If your environment can run tests, run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3422_closed_shape_topology_refinement_gap_test tests.goal3421_cupy_refined_device_predicate_page_probe_test tests.goal3420_device_predicate_page_equivalence_test
```

If you cannot run tests, say that explicitly and base the review on source/report/artifact inspection.
