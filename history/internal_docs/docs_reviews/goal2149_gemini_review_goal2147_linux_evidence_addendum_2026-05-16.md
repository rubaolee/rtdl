# Goal2149 Gemini Review of Goal2147 Linux Evidence Addendum

This is an independent Gemini review, distinct from Codex, of the post-Goal2148 Linux evidence addendum for the RayJoin v2 scale harness.

## Verdict

`accept`

## Review Findings

1.  **Dirty Primary Linux Checkout:** The addendum in `docs/reports/goal2147_rayjoin_v2_scale_perf_harness_2026-05-16.md` clearly states, "After the Goal2147 commit was pushed, Codex validated a separate clean Linux clone at `/home/lestat/work/rtdl_rayjoin_goal2147_check` on `192.168.1.20` without touching the dirty primary Linux checkout." This provides sufficient clarity on the validation environment.

2.  **Claim Boundaries in Linux Artifacts:** Both `docs/reports/goal2147_rayjoin_v2_scale_perf_quick_linux_2026-05-16.json` and `docs/reports/goal2147_rayjoin_v2_scale_perf_medium_pip_lsi_linux_2026-05-16.json` explicitly contain `"rt_core_speedup_claim_authorized": false`. This confirms that the claim boundaries are preserved within the Linux artifacts. The corresponding test `tests/goal2147_rayjoin_v2_scale_perf_test.py` also validates this.

3.  **Cold-Start Outlier Interpretation:** The report's interpretation of the zero-warmup quick timing is reasonable. It correctly identifies the cold-start outlier and uses this observation to emphasize the necessity of including warmups and reporting min/median/max timings for future pod tables, rather than single-shot measurements. This approach enhances the robustness of future performance analysis.

4.  **Medium PIP/LSI Linux Evidence and Claim Boundaries:** The medium PIP/LSI Linux evidence presented in the report and `docs/reports/goal2147_rayjoin_v2_scale_perf_medium_pip_lsi_linux_2026-05-16.json` supports local harness stability, showing consistent CPU and Embree parity. Crucially, the evidence, in conjunction with the explicit "Claim Boundary" section in the report and the `false` flags for `paper_scale_perf_claim_authorized` and `rt_core_speedup_claim_authorized` in the JSON artifacts, effectively prevents any overclaiming regarding RayJoin paper-scale performance or RT-core speedup.

## Conclusion

The Linux evidence addendum addresses the stated objectives clearly and accurately. The documentation and artifacts maintain appropriate claim boundaries, and the interpretation of the cold-start outlier provides valuable guidance for future performance testing. The medium-scale results demonstrate local harness stability without exceeding the defined claims.
