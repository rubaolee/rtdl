# Goal883 Claude External Review

Date: 2026-04-24

## Verdict

**ACCEPT** — with one recommended fix (non-blocking).

---

## What Was Reviewed

The uncommitted diff to `docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md`
makes three classes of change:

1. **Tier 2 additions** — four apps gain new rows for their prepared threshold-decision
   sub-paths: `hausdorff_distance`, `ann_candidate_search`, `facility_knn_assignment`,
   `barnes_hut_force_app`.

2. **Tier 3 refinements** — three apps' existing rows are narrowed to name only the
   sub-path that still needs native redesign (`hausdorff_distance exact distance`,
   `ann_candidate_search ranking`, `barnes_hut_force_app force path`).

3. **Tier 4 removal** — `facility_knn_assignment` is removed from Tier 4 entirely
   (its old row read: "design real RT-assisted nearest/ranking path; do not substitute
   fixed-radius threshold").

---

## Consistency With Goals 879–882

Each of the four Tier 2 additions maps directly to a Goal that received a two-AI
ACCEPT consensus on 2026-04-24:

| Goal | App | Consensus |
| --- | --- | --- |
| Goal879 | hausdorff threshold decision | ACCEPT |
| Goal880 | ANN candidate-coverage decision | ACCEPT |
| Goal881 | facility service-coverage decision | ACCEPT |
| Goal882 | Barnes-Hut node-coverage decision | ACCEPT |

The Tier 2 descriptions in the diff reproduce the exact claim boundary from each
accepted goal report: threshold/coverage decision only; exact distance / ranking /
force-vector paths explicitly kept outside the claim. This is consistent.

The Tier 3 refinements for Hausdorff, ANN, and Barnes-Hut correctly narrow the
"redesign needed" rows to sub-paths that are still CUDA-through-OptiX or
Python-dominated, matching the boundaries agreed in the consensus reports.

---

## RT-Core Readiness Assessment

The diff does **not** overstate RT-core readiness:

- All four Tier 2 entries are labeled "prepared OptiX … decision" and the "Required
  action" column explicitly requires phase-profiler evidence before cloud promotion.
- None of the new Tier 2 rows is an active RTX cloud job; that requires future phase
  profiler runs, same-semantics baselines, a real RTX artifact, and independent review
  (stated in Goal879–882 and enforced by the Goal759/Goal824 manifest gate).
- The Tier 3 residuals for exact distance, ranking, and force paths all carry "design
  native … before any … RT-core claim" directives.

No new speedup claim is created by this plan-doc change.

---

## One Gap: facility_knn ranked assignment has no Tier 3 residual row

**Hausdorff, ANN, and Barnes-Hut** each split into two rows after Goals 879–882:
a Tier 2 row for the prepared decision sub-path, and a Tier 3 row for the full
path that still needs native OptiX redesign.

**Facility KNN does not follow this pattern.** Its Tier 2 row covers the coverage
decision, and the old Tier 4 row is removed, but no Tier 3 row is added to track
that ranked nearest-depot assignment, K=3 fallback, and facility-location
optimization still need native OptiX redesign (the "design real RT-assisted
nearest/ranking path" concern from the old Tier 4 row).

The risk is low because:

- The Tier 2 description already says "keep ranked KNN assignment outside the claim."
- The Goal Sequence section (Goal830+) explicitly names "facility KNN design" as a
  future design-report item.
- Goal881's ACCEPT consensus boundary is explicit about what is not claimed.

But the omission creates a documentation inconsistency: a reader of the tier table
cannot determine whether ranked facility KNN assignment is in Tier 3 (redesign
needed) or Tier 4 (no OptiX surface yet). The other three apps make this explicit.

**Recommended fix** (not a blocker — do not re-spin Goals 879–882):

Add a Tier 3 row for the facility KNN ranked assignment sub-path, parallel to the
other three apps:

```
| `facility_knn_assignment` ranked assignment | KNN rows still used for ordered/ranked depot selection | design native ranking/proximity-reduction before any ranked-assignment RT-core claim |
```

If the ranked assignment path is genuinely Tier 4 (no OptiX surface exists at
all for it), move it there instead with a "Required action" column entry.
Either is consistent; the current state (no row at all) is not.

---

## Summary

The tier promotions are technically sound, correctly scoped, consistent with
Goals 879–882 two-AI accepted consensus, and do not overstate NVIDIA RT-core
readiness. The Tier 3 refinements are more precise than the rows they replace.

The only issue is a documentation gap: `facility_knn_assignment`'s ranked
assignment sub-path has no residual Tier 3 or Tier 4 tracking row, unlike the
three analogous apps. This should be fixed in the next plan-doc commit before
it accumulates more confusion, but it does not block acceptance of the current
structural change.

**ACCEPT** — add the facility KNN ranked assignment residual row at the next
opportunity.
