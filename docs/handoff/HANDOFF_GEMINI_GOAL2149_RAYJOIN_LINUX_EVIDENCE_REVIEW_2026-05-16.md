# Gemini Handoff: Goal2149 RayJoin Linux Evidence Addendum Review

Please perform a narrow independent Gemini review of the post-Goal2148 Linux evidence addendum for the RayJoin v2 scale harness.

## Context

Goal2147 added the RayJoin v2 deterministic scale/perf harness and received an independent Gemini `accept` review in `docs/reviews/goal2148_gemini_review_goal2147_rayjoin_scale_harness_2026-05-16.md`.

After that review, Codex ran a separate clean Linux validation clone at `/home/lestat/work/rtdl_rayjoin_goal2147_check` on `192.168.1.20` because the usual Linux checkout had unrelated dirty work. Codex added the Linux artifacts and a short addendum to the Goal2147 report.

## Files To Review

- `docs/reports/goal2147_rayjoin_v2_scale_perf_harness_2026-05-16.md`
- `docs/reports/goal2147_rayjoin_v2_scale_perf_quick_linux_2026-05-16.json`
- `docs/reports/goal2147_rayjoin_v2_scale_perf_medium_pip_lsi_linux_2026-05-16.json`
- `tests/goal2147_rayjoin_v2_scale_perf_test.py`

## Specific Questions

1. Does the addendum clearly state that the primary Linux checkout was dirty and that a separate clean validation clone was used?
2. Do the Linux artifacts preserve claim boundaries, especially `rt_core_speedup_claim_authorized: false`?
3. Is the cold-start outlier interpretation reasonable: zero-warmup quick timing is useful only to prove future pod tables must use warmups/min/median/max?
4. Does the medium PIP/LSI Linux evidence support local harness stability without overclaiming RayJoin paper-scale performance or RT-core speedup?

## Validation Already Run By Codex

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2147_rayjoin_v2_scale_perf_test tests.goal2148_gemini_review_goal2147_rayjoin_scale_harness_test
```

## Required Output

Write your review to:

`docs/reviews/goal2149_gemini_review_goal2147_linux_evidence_addendum_2026-05-16.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. State explicitly that this is an independent Gemini review distinct from Codex.
