# External Review Handoff: Goal4190 RT-DBSCAN Counts-Only Mixed-Route Probe

Please perform an independent read-only review of Goal4190.

## Files To Inspect

- `scripts/goal4190_rt_dbscan_counts_only_mixed_route_probe.py`
- `docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada/`
- `tests/goal4190_rt_dbscan_counts_only_mixed_route_probe_test.py`
- `docs/research/future_version_to_do_list.md`
- Related prior context:
  - `docs/reports/goal4165_mixed_policy_variant_probe_2026-06-09.md`
  - `docs/reports/goal4166_policy_aware_rt_dbscan_semantic_signature_2026-06-09.md`
  - `docs/reports/goal4180_current_route_decision_after_goal4177_timing_2026-06-09.md`

## Review Questions

1. Does the probe correctly compare the current grouped-stream route with predicate direct-status routes under both strict component-size and counts-only semantic contracts?
2. Do the artifacts support the conclusion that counts-only signatures match while policy-bound component-size signatures do not?
3. Do the performance results justify the report's conservative conclusion: single-pass direct-status is only a modest/scale-dependent counts-only option, not a promoted default?
4. Does the report correctly identify the next major runtime target as a generic predicate-aware direct-status grouped-union primitive with deterministic border assignment, without encoding DBSCAN logic into the native engine?
5. Are claim/release/route-promotion boundaries preserved?

## Expected Output

Write one review file:

- Claude: `docs/reviews/goal4191_claude_review_goal4190_rtdbscan_counts_only_mixed_route_2026-06-09.md`
- Gemini: `docs/reviews/goal4192_gemini_review_goal4190_rtdbscan_counts_only_mixed_route_2026-06-09.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Suggested validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4190_rt_dbscan_counts_only_mixed_route_probe_test tests.goal4166_policy_aware_rt_dbscan_semantic_signature_test tests.goal4177_declared_all_items_direct_status_rtdbscan_2m_test
```

This is a performance-direction and semantic-contract review, not a release authorization review.
