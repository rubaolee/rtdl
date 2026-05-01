# Goal885 Claude External Review

Date: 2026-04-24
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Review Questions

**1. Does the runbook correctly separate the active evidence batch from the deferred exploration batch?**

Yes. The runbook distinguishes the two batches by ordering ("Run the active one-shot command first"), labeling ("release-grade active evidence first; exploratory/deferred gates second"), and by using separate commands — the active batch has no `--include-deferred` flag, the deferred batch uses `--include-deferred` plus explicit `--only` flags for each target.

**2. Does the deferred batch list all current deferred RTX targets without overstating them as promotion-ready?**

Yes. All 10 targets (service_coverage_gaps, event_hotspot_screening, segment_polygon_hitcount, segment_polygon_anyhit_rows, hausdorff_distance, ann_candidate_search, facility_knn_assignment, barnes_hut_force_app, polygon_pair_overlap_area_rows, polygon_set_jaccard) are listed. The runbook explicitly states failures must be treated as follow-up work, not claim evidence. The refresh report confirms the batch is "explicitly exploratory." No promotion-ready language is used.

**3. Does the cloud-cost rule remain clear: one pod session, no per-app restarts?**

Yes. The runbook title, opening rationale ("avoid repeated restart/stop cycles"), the "Do not start a pod for one app at a time" gate, the same-pod deferred instruction, and the shutdown rule all enforce a single-session model. The cloud-cost intent is unambiguous.

**4. Are the tests sufficient to prevent the runbook from drifting back to the older service/hotspot-only deferred batch?**

Yes. `test_runbook_has_deferred_batch_controls_and_shutdown_rule` uses subtests to assert `--only {app}` for all 10 deferred targets. Any regression to a narrower list would cause multiple subtest failures. The dry-run result (`only_count: 10`) confirms alignment between the script and the runbook list. The 10-test suite passing adds further confidence.
