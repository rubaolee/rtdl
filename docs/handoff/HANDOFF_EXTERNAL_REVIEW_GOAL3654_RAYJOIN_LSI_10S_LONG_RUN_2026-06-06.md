# Handoff: External Review for Goal3654 RayJoin LSI 10s Prepared-Left Long Run

Date: 2026-06-06

Please review Goal3654 on current `main` at or after commit `33a2b426`.

## Requested Output

Write one review document:

- Gemini:
  `docs/reviews/goal3655_gemini_review_goal3654_rayjoin_lsi_10s_long_run_2026-06-06.md`
- Claude, if available later:
  `docs/reviews/goal3656_claude_review_goal3654_rayjoin_lsi_10s_long_run_2026-06-06.md`

Use verdicts only from:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Scope To Review

Primary report:

- `docs/reports/goal3654_rayjoin_lsi_10s_prepared_left_long_run_2026-06-06.md`

Primary artifact:

- `docs/reports/goal3654_rayjoin_lsi_10s_prepared_left_a5000/lsi_4096_10s_summary.json`

Related implementation:

- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

Tests:

- `tests.goal3654_rayjoin_lsi_10s_prepared_left_long_run_test`
- `tests.goal3244_rayjoin_same_slice_repeated_count_runner_test`

Recommended validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3654_rayjoin_lsi_10s_prepared_left_long_run_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

## Questions To Answer

1. Does the artifact genuinely show an LSI-only 4096-row same-slice run with
   matching visible count (`4977` RayJoin, `4977` RTDL)?
2. Does the runner's new `--workloads lsi` and
   `--rtdl-internal-query-repeat` telemetry support a 10-second-class RTDL
   hot-loop claim without forcing unrelated PIP work?
3. Does RayJoin process wall timing (`~12.94 s` median) plus RTDL prepared-query
   total timing (`~10.31 s` median) make this stronger evidence than the short
   Goal3650 packet?
4. Is the per-query ratio (`0.284x`, about `3.52x` lower RTDL median) scoped
   correctly to the narrow visible LSI count contract?
5. Are release, public speedup, broad RT-core, true zero-copy, whole-app, and
   full RayJoin reproduction claims still blocked?
6. What should the next performance target be after this: integrate this row
   into the broader v2.9 benchmark table, repeat on a second GPU, or move to
   the next weak app row?

## Expected Boundary

The likely verdict is `accept-with-boundary` if the artifact and wording are
sound. Do not authorize release readiness or public claims from this review
alone.
