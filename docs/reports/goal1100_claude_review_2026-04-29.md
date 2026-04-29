# Goal1100 Claude Review

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Scope

Review of `scripts/goal1100_post_pod_baseline_gap_audit.py`, its test suite, the generated JSON/MD reports, and the referenced evidence artifacts for facility (Goal1083, Goal1084) and Barnes-Hut (Goal1093), checked against the Goal835 baselines.

## Facility Gap Identification

**Correct.** The audit classifies facility as `partial_cpu_oracle_present_needs_fastest_non_optix_phase_baseline`. This is accurate on two counts:

1. The Goal1083 CPU oracle (`mode: "dry-run"`) exposes only `cpu_reference_total_sec` and `input_build_sec` — no phase separation (no `optix_prepare_sec`, `optix_query_sec`, etc.). It cannot serve as a public-wording baseline.
2. The Goal835 Embree baseline covers `coverage_threshold_prepared` at 80k customers (`customer_count: 80000`, `copies: 20000`, `radius: 1.0`), while the Goal1084 RTX pod artifact uses the recentered contract at 10M queries (`query_count: 10000000`, `coordinate_mapping: copy_local_recentered_queries_canonical_depots`). Scale mismatch (80k vs 10M) and coordinate-mapping difference both render the old baseline non-comparable. The `not_same_current_contract` classification is correct.

The RTX correctness read (`matches_oracle: true` from `goal1084` `scenario.result.matches_oracle`) is correctly extracted and matches the artifact.

## Barnes-Hut Gap Identification

**Correct.** The audit classifies Barnes-Hut as `current_contract_baseline_missing`. Verified:

1. The Goal835 Embree baseline uses `body_count: 4096`, `radius: 10.0`. The current contract uses `depth: 8`, `radius: 0.1`, `hit_threshold: 4`, and a 20M timing repeat. All four parameters differ; this is not a same-contract baseline.
2. The 20M timing run (`goal1093_barnes_hut_depth8_20m_timing.json`) has `skip_validation: true`, so `matches_oracle: null`. The script correctly derives `rtx_timing_has_validation: false` via the `is True` identity check, and this is explicitly tested.
3. RTX correctness is drawn only from the 4096-body validation run (`matches_oracle: true`), not the unvalidated timing run. The two-field split (`rtx_correctness` vs `rtx_timing_has_validation`) is the correct way to represent this.

## Public Speedup Claim Authorization

**No unauthorized claims.** Both rows hardcode `public_speedup_claim_ready: false`. `public_speedup_claim_ready_count: 0` is enforced as a validity condition (`valid` flips to `false` if it is ever non-zero). The boundary statement appears twice in the report (summary header and boundary section) and is independently tested. No speedup ratio, multiplier, or claim language appears anywhere in the script or outputs. This is consistent with the Goal1099 consensus boundary and the `activation_status: deferred_until_real_rtx_phase_run_and_review` in both RTX cloud claim contracts.

## Test Adequacy

**Adequate, one minor gap.** The four tests cover:

- Overall validity and the authorization guard (`public_speedup_claim_ready_count == 0`, boundary string).
- Facility gap status, `rtx_correctness`, `path_name`, and `next_action` content.
- Barnes gap status, `rtx_timing_has_validation: False`, and `next_action` content.
- Markdown rendering of both gap statuses and the boundary wording.

Tests call `build_audit()` live against real artifacts, which is appropriate for an audit report — if evidence files change, tests will catch the drift.

**Minor gap:** No test asserts that `rtx_query_median_sec` or `rtx_validation_query_median_sec` are non-None floats. If the profiler schema changes and the `optix_query_sec.median_sec` key disappears, the audit would silently record `null` timing values without failing. This is low severity because the `valid` flag and authorization guard are unaffected by timing values, but a `assertIsInstance(..., float)` guard would improve future-proofing.

## Additional Observations

- `_median_optix` correctly navigates `scenario.timings_sec.optix_query_sec.median_sec` and returns `None` on structural mismatch. The extracted medians (facility: 0.1351 s, Barnes validation: 0.00758 s, Barnes 20M: 0.2306 s) match the source JSON.
- The `valid` predicate requires exactly `row_count == 2`, `rtx_correct_count == 2`, `public_speedup_claim_ready_count == 0`, and `baseline_missing_or_partial_count == 2`. All four conditions are satisfied by the current evidence. The predicate is tight enough to catch accidental promotion of either app to a complete baseline state.
- Goal835 baseline files referenced by the script exist at the expected paths and have the expected content.

## Summary

Goal1100 correctly identifies baseline gaps for both facility (partial CPU oracle, scale/contract mismatch with Goal835) and Barnes-Hut (no same-contract baseline, unvalidated timing run). It does not authorize any public RTX speedup claims. The test suite is adequate for guarding the authorization boundary. The one minor gap (no assertion on timing median being non-None) does not affect the authorization logic and does not block acceptance.
