I will read the following files to gather the necessary information:
1. `scripts/goal1126_robot_normalized_public_wording_review.py`
2. `tests/goal1126_robot_normalized_public_wording_review_test.py`
3. `docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.md`
4. `docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.json`
5. `docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.md`
6. `docs/reports/goal1123_public_wording_wording_review_after_goal1121_2026-04-29.json`
7. `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json`
8. `docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json`
9. `docs/handoff/REFRESH_LOCAL_2026-04-13.md`

I will then analyze the contents of these files to determine if the normalized per-pose robot public wording is acceptable, considering the pose count difference between RTX and Embree, and provide a verdict (ACCEPT/BLOCK) and any blockers.
The normalized per-pose robot public wording is **ACCEPTABLE**.

**Reasoning:**
The review process explicitly addresses the difference in total pose counts (64M RTX vs. 36M Embree) by normalizing the throughput "per-pose". The candidate wording and its accompanying boundary clearly state this normalization and explicitly disclaim it as a "same-total-work wall-time claim." This directly fulfills the condition set by Goal1123, which blocked public wording until an "explicitly normalized baseline review" was accepted. The `Goal1126` review packet itself indicates `valid: True` and includes checks confirming `pose_counts_differ: true` and `wording_explicitly_normalized: true`.

**Blockers:** None, provided the wording is used as proposed, maintaining the "normalized per-pose" clarification and the specified boundaries.
