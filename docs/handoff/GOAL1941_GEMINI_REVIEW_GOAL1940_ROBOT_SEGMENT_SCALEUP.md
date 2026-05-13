# Goal1941 Gemini Review Task

Please perform an independent review of Goal1940 in
`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

Review the committed state at `dbcf6f04` and inspect:

- `docs/reports/goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md`
- `tests/goal1940_robot_segment_scaleup_pod_perf_test.py`
- `docs/reports/goal1940_robot_segment_scaleup_pod/*.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/*.log`
- the Goal1899 board, Goal1908 preflight wiring, and Goal1911 readiness wiring

Questions to answer:

1. Are the Goal1940 numbers transcribed correctly from the pod artifacts?
2. Is the interpretation correct that segment any-hit now has seconds-scale
   same-contract positive v2 partner evidence at 1,048,576 rows?
3. Is the interpretation correct that robot collision has exact parity and
   strong ratios through 8,388,608 poses, but still should not be sold as a
   seconds-scale whole-app claim because the v1.8 baseline remains subsecond?
4. Do the claim boundaries remain intact: no v2.0 release authorization, no
   package-install claim, no broad RT-core speedup claim, no whole-app speedup
   claim, and no arbitrary PyTorch/CuPy acceleration claim?
5. Are the report, test, and gate wiring sufficient, or should any artifact
   provenance, validation, or wording be tightened?

Please save your review as:

`docs/reviews/goal1941_gemini_review_goal1940_robot_segment_scaleup_2026-05-13.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

State clearly that this is an independent Gemini review distinct from Codex.
