# Gemini Review Task: Goal2315/Goal2316 RayJoin Closure And v2.0 Release Prep

Please perform an independent read-only review and write your review to:

`docs/reviews/goal2317_gemini_review_goal2315_2316_rayjoin_closure_release_prep_2026-05-17.md`

Files to inspect:

- `docs/reports/goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md`
- `docs/reports/goal2316_v2_0_release_prep_pending_final_decision_2026-05-17.md`
- `docs/reports/goal2314_prepared_closed_shape_raw_row_view_2ai_consensus_2026-05-17.md`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json`
- `docs/research/future_version_to_do_list.md`
- `docs/release_reports/v2_0_pre_release_candidate.md`
- `tests/goal2315_rayjoin_v2_0_bounded_closure_test.py`
- `tests/goal2316_v2_0_release_prep_pending_final_decision_test.py`

Review questions:

1. Does Goal2315 correctly close the RayJoin-style v2.0 project as a bounded
   language/runtime milestone while refusing to claim RTDL beats RayJoin or
   reproduces the full paper?
2. Does the report clearly answer both audiences: RTDL users can implement the
   scoped LSI/PIP workloads, and systems researchers should view the remaining
   gap as generic device-resident continuation work rather than app-specific
   engine customization?
3. Are deferred items captured in `docs/research/future_version_to_do_list.md`
   instead of blocking v2.0?
4. Does Goal2316 prepare v2.0 for final release review while explicitly
   waiting for the user's final decision and the strict 3-AI final release
   consensus?
5. Does the clean v2.0 pre-release candidate note mention the RayJoin closure
   briefly without overloading learner docs with historical detail?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This should be read-only except for writing the requested review
file.
