# Handoff: External Review for Goal3650 RayJoin LSI Large-Slice Prepared-Left Scaling

Date: 2026-06-06

Please review Goal3650 on current `main` at or after commit `ea08fb92`.

## Requested Output

Write one review document:

- Gemini:
  `docs/reviews/goal3651_gemini_review_goal3650_rayjoin_lsi_large_slice_2026-06-06.md`
- Claude, if available later:
  `docs/reviews/goal3652_claude_review_goal3650_rayjoin_lsi_large_slice_2026-06-06.md`

Use verdicts only from:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Scope To Review

Primary report:

- `docs/reports/goal3650_rayjoin_lsi_prepared_left_large_slice_scaling_2026-06-06.md`

Primary artifact:

- `docs/reports/goal3650_rayjoin_lsi_prepared_left_large_slice_a5000/same_slice_4096_summary.json`

Related context:

- `docs/reports/goal3647_rayjoin_lsi_prepared_left_route_adoption_2026-06-06.md`
- `docs/reports/goal3647_rayjoin_prepared_left_app_a5000/same_slice_summary.json`
- `docs/reviews/goal3648_gemini_review_segment_pair_rayjoin_prepared_left_chain_3633_3647_2026-06-06.md`

Test:

- `tests.goal3650_rayjoin_lsi_prepared_left_large_slice_scaling_test`

Recommended validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3650_rayjoin_lsi_prepared_left_large_slice_scaling_test tests.goal3647_rayjoin_lsi_prepared_left_route_adoption_test
```

## Questions To Answer

1. Does the 4096-row artifact genuinely show matching visible LSI counts
   (`4977` RayJoin, `4977` RTDL)?
2. Is the timing comparison scoped correctly to RayJoin's reported query median
   versus RTDL's prepared query median, not full app-wall timing?
3. Does the report avoid claiming full RayJoin reproduction, broad RT-core
   speedup, release readiness, true zero-copy, or whole-app benchmark speedup?
4. Is it reasonable to treat the 4096-row result as stronger evidence than the
   512-row smoke for the narrow LSI visible-count contract?
5. What should be the next engineering step after this packet: larger/synthetic
   LSI slices, prepared-left route integration into broader benchmark tables,
   or a new generic primitive?

## Expected Boundary

The likely verdict is `accept-with-boundary` if the artifact and report are
sound. Do not authorize release readiness or public claims from this review
alone.
