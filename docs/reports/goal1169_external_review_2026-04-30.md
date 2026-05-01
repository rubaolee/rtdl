# Goal1169 External Review — Clean-Source RTX Claim-Grade Batch Plan

Date: 2026-04-30
Reviewer: external (Claude, goal1169 review request)
Document reviewed: `docs/reports/goal1169_clean_source_rtx_claim_grade_batch_plan_2026-04-30.md`

---

## VERDICT: ACCEPT

The plan is correct and conservative as the next clean-source RTX pod plan after Goal1166.

---

## Check-by-check findings

### 1. The plan prioritizes the six NVIDIA RT-core-ready apps without reviewed public wording

PASS. Priorities 1–6 are exactly the six apps that carry `public_wording_not_reviewed`:

| Priority | App | State |
| ---: | --- | --- |
| 1 | `database_analytics / compact_summary` | `public_wording_not_reviewed` |
| 2 | `graph_analytics / visibility_edges` | `public_wording_not_reviewed` |
| 3 | `road_hazard_screening / native compact summary` | `public_wording_not_reviewed` |
| 4 | `polygon_pair_overlap_area_rows / candidate discovery` | `public_wording_not_reviewed` |
| 5 | `polygon_set_jaccard / candidate discovery` | `public_wording_not_reviewed` |
| 6 | `hausdorff_distance / directed_threshold_prepared` | `public_wording_not_reviewed` |

No `public_wording_reviewed` app appears in positions 1–6. The ordering is correct.

### 2. The plan includes clean-source replacement rows for ANN and robot dirty Goal1166 artifacts

PASS. Both dirty artifacts are addressed at Priorities 7 and 8:

- **Priority 7** (`ann_candidate_search / candidate_threshold_prepared`, `public_wording_reviewed`): explicitly labeled "Clean-source replacement for the dirty Goal1166 large-timing artifact" and requires pairing with a correctness row.
- **Priority 8** (`robot_collision_screening / prepared pose-count`, `public_wording_reviewed`): explicitly labeled "Clean-source replacement for the dirty Goal1166 robot validation and large timing artifacts" and preserves the normalized per-pose wording boundary.

Both replacements are correctly scoped and do not attempt to expand the wording already in the reviewed state.

### 3. The source policy is strict enough to prevent dirty-source public claims

PASS. The Source Policy section:

- Restricts runs to clean git checkout of a pushed commit **or** a staged archive with manifest, exact digest, and no dirty ambiguity — no middle option is permitted.
- Mandates recording of git commit or archive digest, `git status --short`, GPU model, driver, CUDA version, OptiX header version, native build log, exact command lines, and artifact paths. The evidence chain is complete.
- Contains an unambiguous prohibition: "If the source is dirty or manually patched on the pod, the run is engineering evidence only and must not be used for public speedup wording."

There is no gap that would allow a dirty-source run to satisfy the policy by omitting a required field.

### 4. The non-goals preserve the project's wording boundaries

PASS. The five non-goals are correctly scoped:

- No whole-app speedup wording — preserves the phase-boundary discipline.
- No `--backend optix` as standalone evidence — prevents backend-flag laundering.
- No timing-only versus correctness-baseline comparisons — prevents cherry-picking.
- No claim that polygon exact area/Jaccard refinement is fully RT-core native — preserves the candidate-discovery vs. exact-continuation boundary.
- No claim that graph BFS, triangle counting, or shortest path is whole-app RT acceleration when only bounded graph-ray candidate generation is measured — preserves the graph wording boundary established in prior review.

None of the non-goals inadvertently block collection of the evidence listed in the Priority Rows.

### 5. The pod-efficiency rule avoids repeated start/stop cycles

PASS. The Pod Efficiency Rule requires:

- A single runner script or manifest for **all** rows must exist before a pod is started.
- Expected output filenames, per-row timeout, and validation policy must be ready before start.
- An intake script capable of rejecting dirty-source or missing-artifact runs must be ready before start.
- Once the pod is started, all rows run in the batch; artifacts are copied back; only then is a second session considered.

This rule structurally prevents the ad hoc restart pattern that produced the Goal1166 dirty-source artifact.

---

## Summary

Every check passes. The plan is correctly sequenced after Goal1166, handles the dirty-source remediation at Priorities 7–8, enforces a strict source policy, preserves all project wording boundaries in the non-goals, and eliminates repeated pod start/stop cycles via the pre-flight manifest requirement.

No fixes required.
