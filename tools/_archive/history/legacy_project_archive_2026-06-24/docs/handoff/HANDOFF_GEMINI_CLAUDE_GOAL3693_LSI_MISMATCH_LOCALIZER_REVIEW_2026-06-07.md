# External Review Handoff: Goal3693 RayJoin LSI Mismatch Localizer

Please perform a read-only independent review of Goal3693.

## Context

Goal3691 compared RTDL with the original RayJoin repository on the same bundled Brazil sample files. PIP looked promising, but LSI was the live blocker: RayJoin reported `20860` checked intersections and RTDL reported `20859`.

Goal3693 localizes that one-row LSI gap.

## Files To Review

- `docs/reports/goal3693_rayjoin_lsi_mismatch_localizer_2026-06-07.md`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/lsi_pair_set_diff_summary.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/missing_pair_geometry.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/missing_pair_precision_probe.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/rayjoin_lsi_dump.log`
- `tests/goal3693_rayjoin_lsi_mismatch_localizer_test.py`
- `docs/research/future_version_to_do_list.md`

Helpful context:

- `docs/reports/goal3691_rayjoin_original_same_source_probe_2026-06-07.md`
- `docs/reviews/goal3692_gemini_review_goal3691_rayjoin_same_source_probe_2026-06-07.md`
- `src/rtdsl/segment_pair_contracts.py`
- `src/native/optix/rtdl_optix_core.cpp`

## Questions To Answer

1. Does the evidence really localize the LSI mismatch to one normalized pair, with no RTDL extras?
2. Does the missing-pair geometry support the endpoint-near / precision-policy diagnosis?
3. Does the precision probe reasonably explain how exact arithmetic includes the pair while a float32 candidate predicate can drop it?
4. Does the report keep the solution generic and app-agnostic, without proposing RayJoin-specific native engine logic?
5. Are the claim boundaries strict enough: no release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core, or zero-copy claims?
6. What should the next generic segment-pair primitive/policy be: ambiguous candidate emission, high-precision/scaled candidate emission, typed status columns, or a different approach?

## Required Output

Write a review file with verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Preferred Gemini output:

- `docs/reviews/goal3694_gemini_review_goal3693_rayjoin_lsi_mismatch_localizer_2026-06-07.md`

Preferred Claude output:

- `docs/reviews/goal3695_claude_review_goal3693_rayjoin_lsi_mismatch_localizer_2026-06-07.md`

Do not mutate source code. If you run tests, prefer:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3693_rayjoin_lsi_mismatch_localizer_test tests.goal3691_rayjoin_original_same_source_probe_test
```

