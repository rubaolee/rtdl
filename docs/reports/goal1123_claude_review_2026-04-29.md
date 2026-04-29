# Goal1123 Claude Review — 2026-04-29

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-29

## Verdict: ACCEPT

---

## Scope check: facility and Barnes-Hut wording

Both candidate wording lines pass the narrowness test.

**facility_knn_assignment / coverage_threshold_prepared_recentered**

The public wording is scoped to "prepared facility coverage-threshold RTX query sub-path" only. The boundary statement explicitly excludes ranked nearest-facility assignment, KNN fallback output, facility-location optimization, Python-side setup, and whole-app speedup. No default-mode or whole-app claim is present.

The script uses the CPU oracle as the baseline because it is the fastest same-contract non-OptiX reference (87.24x). Embree is recorded as a secondary ratio but not used in the public wording line. This ordering is correct: the public claim must survive comparison against the toughest available non-OptiX baseline.

**barnes_hut_force_app / node_coverage_prepared_rich**

The public wording is scoped to "prepared depth-8 node-coverage threshold traversal" only. The boundary statement explicitly excludes Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup. No default-mode or whole-app claim is present.

The script uses the same-contract chunked Embree node-coverage baseline (222.19x), which is the correct same-contract comparator for this sub-path. The ratio is plausible given that RT-core hardware acceleration is doing BVH traversal that Embree does in software.

Both wording lines are narrowly scoped and do not overreach into whole-app, default-mode, or pipeline-level claims. No issue.

---

## Robot block check

**robot_collision_screening / prepared_pose_flags** is correctly kept blocked.

The core problem is a scale mismatch: the RTX timing was measured at 64M rays and the available Embree aggregate is 36M chunked work. These are not the same contract. The script does compute a per-pose normalized ratio (`robot_normalized_embree_per_pose / robot_normalized_rtx_per_pose`) and stores it under the field name `diagnostic_normalized_ratio_not_public`, which is never surfaced in the public wording line. That quarantine is correct.

Timing-floor evidence (the 64M run crossed the floor) is noted, but floor-crossing alone does not authorize a public ratio. A ratio requires a same-scale baseline or an explicitly reviewed normalized baseline comparison. Neither exists yet. The block is appropriate and the wording "No public RTX speedup wording is authorized for robot_collision_screening yet" is the right output.

---

## Script methodology

- Source files are loaded from fixed artifact paths; no dynamic path construction that could silently swap baselines.
- `fastest_baseline_ratio` for facility is correctly the CPU oracle. Embree is `secondary_baseline_ratio`, not the headline number.
- `fastest_baseline_ratio` for robot is `None`, which is what causes `n/a` to appear in the table. The diagnostic ratio is stored but isolated.
- `public_speedup_claim_authorized` is hardcoded `False` at the packet level. The packet is a wording-review artifact only; it does not write to `rtdsl.rtx_public_wording_matrix()` or any user-facing doc.
- The `to_markdown` renderer only surfaces `fastest_baseline_ratio`, so the robot diagnostic ratio cannot leak into the markdown output by accident.

No methodological issues found.

---

## Answers to reviewer questions

1. **Are the facility and Barnes-Hut wording lines narrow enough?** Yes. Both are sub-path only, with explicit boundary lists. No whole-app or default-mode claims.
2. **Is robot correctly kept blocked?** Yes. The scale mismatch (36M Embree vs 64M RTX) means no valid same-contract ratio exists. The diagnostic normalized ratio is correctly withheld. Block stands until a same-scale or explicitly accepted normalized baseline review is completed.
3. **Are the evidence sources sufficient to update `rtdsl.rtx_public_wording_matrix()` and user-facing docs in a follow-up goal?** The sources listed (Goal1121 intake, Goal1101 CPU/Embree baselines, Goal1086 robot Embree baseline) are sufficient to support the two candidate rows. A follow-up goal that writes to the wording matrix and user-facing docs may proceed for facility and Barnes-Hut only. Robot must remain blocked there as well.

---

## Summary

ACCEPT. The packet is internally consistent, the facility and Barnes-Hut wording is narrowly bounded, the robot block is correctly maintained on valid grounds (scale mismatch, no accepted normalized review), and `public_speedup_claim_authorized` is false. No public docs should be modified by this packet; a follow-up goal may apply the two reviewed rows to `rtdsl.rtx_public_wording_matrix()`.
