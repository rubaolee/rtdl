# Gemini Review For Goal3715 Original-RayJoin Current Probe

Date: 2026-06-07

## Review of Goal3715 Original-RayJoin Current Probe

### Review Questions & Answers:

1.  **Does Goal3715 correctly show that the LSI correctness gap is fixed: RayJoin LSI `20860`, RayJoin `-check=true` LSI `20860`, RTDL LSI `20860`, delta `0`?**
    *   **Answer:** Yes, the report (`docs/reports/goal3715_rayjoin_original_same_source_current_probe_2026-06-07.md`) and the associated `summary.json` artifact clearly show that the LSI correctness gap is fixed. All LSI counts (RayJoin, RayJoin `-check=true`, and RTDL) are reported as `20860`, resulting in a delta of `0`. This is also verified by the `test_lsi_correctness_gap_is_fixed_but_perf_gap_remains` in `tests/goal3715_rayjoin_original_same_source_current_probe_test.py`.

2.  **Does it correctly report the current timings: RayJoin PIP `0.000872374s`, RTDL PIP `0.000469153s`, RayJoin LSI `0.000873963s`, RTDL LSI `0.001100961s`?**
    *   **Answer:** Yes, the report's "Result" table and the `summary.json` artifact accurately reflect these timings. The corresponding assertions in `tests/goal3715_rayjoin_original_same_source_current_probe_test.py` also confirm these values.

3.  **Is the interpretation honest: PIP query time is promising but lacks RayJoin count comparability, while LSI is correct but still slower at `0.794x`?**
    *   **Answer:** Yes, the interpretation is honest. The "Interpretation" section of the report explicitly states that RTDL's PIP query time is faster but lacks comparability due to RayJoin not printing the PIP count. It also correctly notes that RTDL's LSI is correct but still slower at `0.794x` (approximately `1.26x` longer latency). This aligns with the data in `summary.json` and the test assertions.

4.  **Does the report keep original-RayJoin executable evidence separate from all-CuPy same-contract evidence such as Goal3713?**
    *   **Answer:** Yes, the report maintains this separation. The "Next Work" section explicitly states, "Preserve Goal3713 as the all-CuPy same-contract comparison packet; keep Goal3715 separate as original-RayJoin executable evidence." The entire report consistently focuses on comparing with the original RayJoin executable.

5.  **Are all claim boundaries preserved: no release, public speedup, RTDL-beats-RayJoin, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, or native default-route authorization?**
    *   **Answer:** Yes, all specified claim boundaries are strictly preserved. The report's "Status" and "Boundary" sections, as well as the `claim_boundary` field in `summary.json` (all set to `false`), confirm that none of these claims are authorized. The `test_claim_boundary_flags_remain_false` in the test file further validates this.

### Verdict:

`accept`
