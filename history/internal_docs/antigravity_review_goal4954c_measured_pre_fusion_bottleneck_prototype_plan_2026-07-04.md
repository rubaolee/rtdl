# Antigravity Review — Goal4954-C Measured Pre-Fusion Bottleneck Prototype Plan

Date: 2026-07-04
Reviewer: Antigravity (strict)
Review targets:
- [call_for_review_goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md)
- [goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md)
- [goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md)
- [antigravity_review_goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_review_goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md)

---

## Verdict

```text
approve_goal4954c_grouped_carrier_prototype
```

### Authorization Boundary

This approval authorizes **only** the prototyping of the grouped columnar carrier (Prototype C1) under app-owned reproduction artifacts.

It does **not** authorize:
- Layer 4 fusion;
- Raw callbacks;
- RTDL core/runtime edits;
- Public API exposure;
- Promotion of app-owned RayJoin prototype code into RTDL core;
- Performance claims beyond the measured public sample.

---

## Core Evaluation

### 1. Justification for Targeting Grouped Binary Row Construction First
The empirical timings from [Goal4954-B](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md) clearly show that **binary grouped row construction** is the largest single pre-fusion hot-path bottleneck, taking `1.748347s` (approximately **33%** of the `5.309487s` total). The downstream **descriptor-pair consumer** accounts for another `0.688320s` (approximately **13%**). Together, these two phases make up over **45%** of the pre-fusion runtime.
Optimizing only reprojection/sorting would miss this primary bottleneck. Therefore, targeting grouped binary row construction first in [Goal4954-C C1](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md) is highly justified by the baseline measurement data.

### 2. Genericity of the Grouped Columnar Carrier
The proposed grouped columnar carrier consists of:
- **Group-level columns:** `group_offset`, `group_length`, `label_a`, `label_b`, `alt_label`, `source_side_id`, `source_element_id`
- **Point-level columns:** `x`, `y`

This layout is a standard columnar nested list/jagged array representation (analogous to Apache Arrow's ListArray layout with offset/length buffers). It remains generic because it does not encode any RayJoin paper text formats or output-chain byte layouts. It represents general spatial overlay groupings where group properties are segregated from vertex/point coordinates. Thus, it does not constitute RayJoin-core pollution.

---

## Answers to Review Questions

### 1. Is it correct to target binary grouped row construction first, given it is the largest measured pre-fusion bottleneck?
**Yes.** The baseline measurement from [Goal4954-B](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md) ranks binary grouped row construction (`1.748s`) as the primary bottleneck, ahead of LSI rows (`1.213s`), sort total (`0.836s`), and reprojection (`0.741s`). Targeting the largest contributor is correct engineering discipline.

### 2. Is the grouped columnar carrier generic enough:
- **group offsets/lengths:** Yes. This is a standard way to represent variable-sized list groupings in columnar formats.
- **group-level labels/descriptors:** Yes. These are generic numeric or categoric properties associated with each partition.
- **point-level coordinate columns:** Yes. These are standard spatial primitive attributes (`x`, `y`).
The schema does not leak app-specific text formatting or paper-writing conventions, maintaining genericity.

### 3. Does the plan avoid RTDL core/runtime edits and public API exposure?
**Yes.** Under the **Owner Invariant** and **Forbidden** sections, the plan strictly forbids modifying the RTDL core/runtime and exposing public APIs. The prototype code will live entirely within app-owned reproduction artifacts.

### 4. Does it preserve the RTDL-generic/RayJoin-app invariant?
**Yes.** Because the carrier is generic and the implementation remains in the app-owned reproduction artifacts, the core system boundaries are preserved. Promotion of any generic carrier mechanism to RTDL core is deferred to a future subgoal (Goal4954-D) and will require a non-RayJoin proof.

### 5. Is it correct to hold LSI, reprojection, sort, PIP, midpoint generation, and input data constant for C1, so the effect is isolated?
**Yes.** Isolating the experimental variables is critical to measure the exact performance delta of the grouped columnar carrier and downstream consumer without introducing confounding variables.

### 6. Is the descriptor-pair consumer over group-level labels and `group_length` a fair replacement for the flat repeated-label consumer?
**Yes.** Since group-level labels are constant across all point rows within a group, repeating them per point row is redundant. Emitting aggregates via `point_count_by_descriptor_pair` (accumulating `group_length` rather than physically scanning repeated labels) is mathematically equivalent in output count semantics while avoiding physical data replication.

### 7. Are success/failure labels decision-forcing?
**Yes.** The labels clearly distinguish:
- `grouped_carrier_win_continue` (faster, correct, no core pollution);
- `grouped_carrier_correct_but_not_faster_stop` (correct but insufficient speedup);
- `grouped_carrier_wrong_reject` (incorrect counts/semantics or leaking app details).
These force a clean, objective decision on the next steps.

### 8. Should Goal4954-C C1 open with: `approve_goal4954c_grouped_carrier_prototype`?
**Yes.** The plan is sound, empirically justified, and adheres to the project's strict architectural constraints.
