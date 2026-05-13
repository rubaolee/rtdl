# Goal1935 Gemini Review - Goal1933/1934 Large-Scale v2 Pod Performance

Date: 2026-05-13

Review of `docs/reports/goal1933_goal1934_large_scale_all_app_v2_pod_perf_2026-05-13.md` and associated data.

## Review Questions and Verdicts

1.  **Do the fixed-radius family rows support the report's narrow statement that v2 prepared partner rows are strongly positive versus v1.8 prepared at `524288 x 524288` scale?**
    *   **Verdict:** `accept`
    *   **Justification:** The `fixed_radius_524288.json` artifact confirms that at the `524288 x 524288` scale, v1.8 prepared OptiX times are consistently in the seconds range (1.1s - 1.8s), while v2 prepared partner times are in the sub-millisecond to low-millisecond range (0.0004s - 0.0021s). The resulting `v2_vs_v1_8_prepared_ratio` values are all extremely small (~0.0004x to 0.0011x), unequivocally supporting the claim of strongly positive performance.

2.  **Does the report correctly avoid overclaiming robot collision and segment/polygon any-hit rows, given they remain sub-second despite positive ratios?**
    *   **Verdict:** `accept`
    *   **Justification:** For robot collision (`robot_collision_16384x1024.json`), both v1.8 and v2 prepared times are in the millisecond range (~0.001s and ~0.0006s respectively), confirming they are sub-second. The `claim_boundary` within the JSON explicitly disallows a "whole_app_speedup_claim_authorized". Similarly, for segment/polygon any-hit (`segment_anyhit_rows_4096.json`), v1.8 and v2 times are also well within the sub-second range (~0.014s and ~0.004-0.006s), and the JSON artifact's `claim_boundary` aligns with avoiding overclaiming. The report's interpretations for these sections accurately reflect the sub-second nature and the specific, bounded scope of the performance wins.

3.  **Does the report correctly classify polygon exact metrics, DB analytics, and graph analytics as seconds-scale control/fallback evidence rather than v2 partner speedup rows?**
    *   **Verdict:** `accept`
    *   **Justification:**
        *   **Polygon Exact Metrics (`control_polygon_pair_overlap_8192.json`, `control_polygon_jaccard_8192.json`):** Both artifacts show `optix_candidate_discovery_sec` and `native_exact_continuation_sec` times in the seconds range. The `boundary` and `cloud_claim_contract.non_claim` fields explicitly state that these are not "full polygon-overlap RTX speedup claims" and reinforce their control nature.
        *   **DB Analytics (`control_database_analytics_100000.json`):** The `one_shot_total_sec`, `prepared_session_prepare_total_sec`, and `prepared_session_warm_query_sec.median_sec` are all in the seconds range. The JSON's `cloud_claim_contract.non_claim` explicitly states it is "not a v2 partner columnar scan/grouped-reduction implementation," supporting its classification as control evidence.
        *   **Graph Analytics (`control_graph_analytics_100000.json`):** The `phase_seconds.native_query` is 13.35s (seconds-scale). The `public_speedup_claim_authorized` field being `false` in the JSON reinforces its role as control evidence rather than a v2 speedup claim.

4.  **Are the release boundaries clear: no v2.0 release authorization, no broad RT-core speedup, no whole-app speedup, no arbitrary PyTorch/CuPy acceleration, no package-install claim?**
    *   **Verdict:** `accept`
    *   **Justification:** The "What We Learned" section of the main report explicitly states: "This packet improves the evidence quality, but it does not authorize v2.0 release, whole-app speedup wording, arbitrary PyTorch/CuPy acceleration, or package-install claims." This boundary statement is consistently reinforced across all analyzed JSON artifacts, where `claim_boundary.v2_0_release_authorized`, `whole_app_speedup_claim_authorized`, `broad_rt_core_speedup_claim_authorized`, and `package_install_claim_authorized` are explicitly set to `false`. Additionally, `rt_core_speedup_claim_authorized` is `false` in the robot collision metadata, and various `_non_claim` and `boundary` fields in the control JSONs further clarify these limits. The documentation of these boundaries is clear and consistent.
