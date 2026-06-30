# External Review Request: Goal4215 Current Benchmark Packet After RT-DBSCAN Policy Cleanup

Please perform an independent review of Goal4215.

## Files To Inspect

- `docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md`
- `docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/current_scale_profile_packet.json`
- `docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/rayjoin_fixture_materialization.json`
- `tests/goal4215_current_benchmark_scale_profile_after_policy_test.py`
- Context: Goal4205-4212 reports/tests for RT-DBSCAN boundary policy canonicalization.

## Review Questions

1. Does the Goal4215 packet genuinely prove that all ten current benchmark front doors pass on the RTX 4000 Ada pod at source commit `63289bbc`?
2. Is the RayJoin fixture repair correctly classified as an environment/data-materialization repair rather than a code or performance result?
3. Does the packet verify that RT-DBSCAN now reports the canonical `single_pass_candidate_root_rebased` boundary policy in the broad all-app packet?
4. Are all release/public-claim boundaries still closed, including release, public speedup, broad RT-core, whole-app, true-zero-copy, automatic partner selection, AMD performance, and app-specific native-engine logic?
5. Does the report avoid overclaiming the packet as a final release/performance table?

## Expected Output

Write your review to:

- Claude: `docs/reviews/goal4216_claude_review_goal4215_current_benchmark_packet_2026-06-09.md`
- Gemini: `docs/reviews/goal4217_gemini_review_goal4215_current_benchmark_packet_2026-06-09.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is an internal engineering review only. It must not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, or app-specific native-engine logic.
