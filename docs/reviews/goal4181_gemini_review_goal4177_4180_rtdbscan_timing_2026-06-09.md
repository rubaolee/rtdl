# Review: Goal4177/4180 RTDBSCAN Declared All-Items Timing

**Reviewer:** Gemini (gemini-1.5-flash), independent read-only review
**Date:** 2026-06-09
**Verdict:** `accept-with-boundary`

---

## Files Reviewed

- `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json`
- `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_2026-06-09.md`
- `tests/goal4177_declared_all_items_direct_status_rtdbscan_2m_test.py`
- `docs/reports/goal4180_current_route_decision_after_goal4177_timing_2026-06-09.md`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `tests/goal4179_current_route_decision_after_declared_refactor_test.py`
- Context:
  - `docs/reviews/goal4178_claude_review_goal4176_4177_declared_rtdbscan_refactor_2026-06-09.md`
  - `docs/reports/goal4176_declared_rtdbscan_all_items_direct_status_refactor_2026-06-09.md`

---

## Question 1: Does the Goal4177 artifact support the reported 2M road3d timing result: current grouped-stream `34.321601s`, measured all-true predicate direct-status `25.557633s`, and declared all-items direct-status `20.144741s`?

**Answer:** Yes, the Goal4177 artifact (`docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json` and `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_2026-06-09.md`) fully supports the reported 2M road3d timing results. The JSON artifact contains the raw `elapsed_sec` values that precisely match the reported numbers, and the Markdown report accurately summarizes them. The associated test (`tests/goal4177_declared_all_items_direct_status_rtdbscan_2m_test.py`) further validates these timing values and speedups.

---

## Question 2: Does the declared route preserve the same RT-DBSCAN app signature while materializing no predicate columns and executing no RT count-threshold?

**Answer:** Yes, the declared route preserves the same RT-DBSCAN app signature: `{"cluster_sizes": {"1": 2097152}, "core_count": 2097152, "noise_count": 0}`. The `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_2026-06-09.md` report explicitly states that `predicate_columns_materialized = false` and `rt_count_threshold_executed = false` for the declared route. This is confirmed by the `goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json` artifact (where `predicate_columns_materialized` and `rt_count_threshold_executed` are `false` for the declared route entry), and by `tests/goal4177_declared_all_items_direct_status_rtdbscan_2m_test.py` which asserts these conditions.

---

## Question 3: Does Goal4180 update the route registry honestly, replacing the pending Goal4177 language with accepted evidence while avoiding automatic route promotion or release/public-claim authorization?

**Answer:** Yes, Goal4180 updates the route registry honestly. The `docs/reports/goal4180_current_route_decision_after_goal4177_timing_2026-06-09.md` explicitly notes its status as "accepted registry refresh; no automatic route promotion" and integrates Goal4177 as accepted evidence. The `src/rtdsl/current_benchmark_route_decisions.py` file reflects this update in `CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` and within the `rt_dbscan` route's guidance, incorporating the Goal4177 findings. Importantly, the `CurrentBenchmarkRouteDecision` class and its usage explicitly set and enforce that `automatic_partner_selection_authorized`, `release_authorized`, `public_speedup_claim_authorized`, etc., remain `false`, demonstrating a clear avoidance of automatic route promotion or unauthorized claims. The test `tests/goal4179_current_route_decision_after_declared_refactor_test.py` verifies these aspects.

---

## Question 4: Is the boundary correct that this is an explicit external-proof all-predicate route only, not a mixed-predicate RTDBSCAN promotion and not a broad RT-core speedup claim for the declared subpath?

**Answer:** Yes, the boundary is correctly maintained. All reviewed documents, including `docs/reports/goal4177_declared_all_items_direct_status_rtdbscan_2m_2026-06-09.md` and `docs/reports/goal4180_current_route_decision_after_goal4177_timing_2026-06-09.md`, consistently emphasize that the declared route requires "explicit caller selection and external proof that all predicate flags are true." They explicitly state that "Mixed-predicate RT-DBSCAN rows remain on the grouped-stream Numba route" and that this evidence "does not authorize release, public speedup wording, broad RT-core wording, whole-app claims, paper-reproduction claims..." The `src/rtdsl/current_benchmark_route_decisions.py` further reinforces this by listing "mixed predicate direct-status broad promotion" among `rejected_or_unpromoted_candidates`.

---

## Question 5: Are there metadata, timing-methodology, or machine-checkability issues that must be fixed before this evidence is used as current route guidance?

**Answer:** No significant metadata, timing-methodology, or machine-checkability issues that must be fixed are identified. An earlier Claude review (`docs/reviews/goal4178_claude_review_goal4176_4177_declared_rtdbscan_refactor_2026-06-09.md`) raised concerns about timing asymmetry due to warmups and an outer `neighbor_count_policy` inconsistency. However, further inspection of the `goal4177_declared_all_items_direct_status_rtdbscan_2m_pod.json` artifact and `tests/goal4177_declared_all_items_direct_status_rtdbscan_2m_test.py` shows that:
1. Per-route warmups are indeed performed for all three routes, addressing the timing asymmetry concern.
2. The `neighbor_count_policy` for the declared route in the JSON artifact is correctly set to `"not_materialized_all_items_declared_predicate_true"`, suggesting the inconsistency may have been resolved or does not apply to the generated output.
The acknowledged limitation of single-run measurements is consistent with prior goals and does not block the use of this evidence for guidance.

---

## Summary and Verdict

Goal4177 successfully measures the performance of the refactored caller-declared all-items direct-status RT-DBSCAN route, demonstrating a significant speedup over existing routes while maintaining the expected application signature. Goal4180 honestly integrates this evidence into the route registry, carefully preserving all necessary boundaries against automatic promotion, unauthorized claims, and mixed-predicate application. The potential issues identified in an earlier review appear to have been addressed in the current implementation or do not manifest in the provided artifacts.

This review does not authorize route promotion, default selection, release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, native ABI additions, AMD performance claims, true-zero-copy claims, or mixed-predicate route changes. The route remains explicitly for external-proof all-predicate scenarios.
