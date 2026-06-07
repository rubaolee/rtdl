# Handoff: Gemini Review For Goal3715 Original-RayJoin Current Probe

Please perform a read-only independent review of:

- `docs/reports/goal3715_rayjoin_original_same_source_current_probe_2026-06-07.md`
- `docs/reports/goal3715_rayjoin_original_same_source_current_a5000/summary.json`
- `tests/goal3715_rayjoin_original_same_source_current_probe_test.py`

Context:

- Goal3691 previously found RTDL LSI `20859` vs original RayJoin `20860` on RayJoin's bundled Brazil sample.
- Goals3696-3708 repaired the segment-pair exact-count contract and prepared-left LSI count route.
- Goal3715 reruns the original-RayJoin same-source probe on current `main` at RTDL commit `5951f35853ad09d3873926ad4c2012e0837fa16b`.

Review questions:

1. Does Goal3715 correctly show that the LSI correctness gap is fixed: RayJoin LSI `20860`, RayJoin `-check=true` LSI `20860`, RTDL LSI `20860`, delta `0`?
2. Does it correctly report the current timings: RayJoin PIP `0.000872374s`, RTDL PIP `0.000469153s`, RayJoin LSI `0.000873963s`, RTDL LSI `0.001100961s`?
3. Is the interpretation honest: PIP query time is promising but lacks RayJoin count comparability, while LSI is correct but still slower at `0.794x`?
4. Does the report keep original-RayJoin executable evidence separate from all-CuPy same-contract evidence such as Goal3713?
5. Are all claim boundaries preserved: no release, public speedup, RTDL-beats-RayJoin, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, or native default-route authorization?

Expected verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Write your review to:

- `docs/reviews/goal3716_gemini_review_goal3715_original_rayjoin_current_probe_2026-06-07.md`

Do not edit source files other than the requested review file.
