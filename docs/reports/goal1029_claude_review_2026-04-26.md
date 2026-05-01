# Goal1029 Claude Review

Reviewer: Claude (claude-sonnet-4-6)
Date: 2026-04-26
Source plan: `docs/reports/goal1029_rtx_baseline_promotion_plan_2026-04-26.md`
Input evidence: Goal1028 batch report, Claude review, and Gemini review (all 2026-04-26)

---

## Verdict

**ACCEPT**

The promotion plan is honest, correctly scoped, and complete enough to guide baseline comparison work. It does not authorize any public speedup claims. All 16 app subpaths are listed with explicit baseline requirements and local-feasibility flags. No app is pre-promoted. The plan may be used as the working document for the next phase.

---

## Checks Passed

### 1. No public speedup claims — explicitly blocked at two levels

The Purpose section states: "This plan does not authorize speedup claims." The Promotion Rule then lists five conditions that must all hold before any subpath can move to `speedup_claim_candidate`. No app meets all five conditions today. The plan is correctly positioned as a gate, not a release.

### 2. App coverage is complete

Goal1028 produced evidence for 17 data points across 16 apps (database_analytics has two subpaths). The matrix lists all 16 apps. No app with a collected artifact is omitted.

### 3. Claim scopes are accurate and conservative

Each "Required baseline work before claim" cell preserves or tightens the claim boundary from the Goal1028 evidence:

- Prepared/threshold subpaths correctly exclude the full solver (DBSCAN expansion, exact Hausdorff, ranked KNN, force-vector, ANN ranking).
- Native/experimental subpaths (Groups E and F) correctly scope to the compact-summary gate, not whole-app acceleration.
- Graph analytics correctly separates visibility-edge any-hit from BFS/triangle continuation.

No cell weakens a boundary that Goal1028 or the Goal762 analyzers established.

### 4. Group H postprocess cost is preserved in the plan

The Goal1028 Claude review (F3) flagged that polygon_pair_overlap_area_rows and polygon_set_jaccard have large postprocess medians (3.32 s and 5.40 s respectively) that the main evidence table omitted. The promotion plan addresses this directly: both apps require "full phase accounting: candidate discovery plus exact refinement/continuation" before any claim, and baselines must cover "whole bounded unit-cell semantics." This is the correct response to F3.

### 5. PostGIS work correctly flagged as Linux-preferred

Apps that need PostGIS baselines (database_analytics, road_hazard_screening, segment_polygon_hitcount, segment_polygon_anyhit_rows, polygon_pair_overlap_area_rows, polygon_set_jaccard) mark local feasibility as "Linux preferred" rather than "Yes." This is consistent with Goal1028's environment and avoids blocking local CPU/Embree work on a PostGIS dependency.

### 6. Immediate Local Work and Cloud Efficiency sections are actionable

The batch-before-pod rule and per-app status taxonomy (`baseline_ready`, `baseline_partial`, `needs_linux_or_cloud`) give the next implementer clear stopping conditions. This avoids the per-app pod waste that Goal1028 explicitly discouraged.

### 7. Priority assignments are reasonable

P0 apps (robot_collision_screening, outlier_detection, dbscan_clustering, database_analytics) are the subpaths most likely to yield clean baselines with local tooling and the simplest semantics. P2 apps (hausdorff_distance, ann_candidate_search, barnes_hut_force_app, polygon_pair_overlap_area_rows, polygon_set_jaccard) either have bounded postprocess complexity or require more careful phase accounting. The ordering is defensible.

---

## Follow-Up Items (not blocking ACCEPT)

### F1. database_analytics: two subpaths merged into one matrix row

Goal1028 produced separate evidence for `sales_risk` and `regional_dashboard` (0.085 s and 0.119 s median query times respectively). The matrix collapses both into one row with shared baseline work. This is acceptable if both subpaths will be tested against the same compact-summary baseline, but the next baseline runner should explicitly emit results for both named subpaths so that coverage is unambiguous.

### F2. graph_analytics: GEOS dependency not noted in the matrix

Goal1028's dependency repair event showed that the CPU oracle for graph_analytics requires `libgeos_c` / `libgeos-dev`. The "Local before next pod?" column says "Yes" but does not note this dependency. A baseline runner that tries to compare CPU graph-ray semantics on this Mac will fail silently or with a confusing error if GEOS is not installed. The next runner script should check for GEOS availability and emit `needs_linux_or_cloud` for the CPU oracle path if it is absent.

### F3. Promotion Rule condition 4 references rtdsl.rtx_public_wording_matrix()

The condition reads: "The claim text follows `rtdsl.rtx_public_wording_matrix()`." If this function does not yet exist in the codebase, condition 4 cannot be verified and no app can complete the promotion gate even after baselines are established. This function (or a documented substitute) should be created or pointed to before any app reaches the claim-candidate review step. This is not a blocker for baseline work but is a blocker for the promotion gate itself.

---

## Summary

The Goal1029 promotion plan is accurate, honest, and workable. It correctly continues from the Goal1028 `evidence_collected_no_public_speedup_claim` state without pre-promoting any app. The three follow-up items are operational notes, not evidence of inflated claims or suppressed gaps. Goal1029 is acceptable as the governing document for baseline comparison work.
