# Antigravity Review — Goal4954-A Binary Overlay Contract and Measurement Plan

Date: 2026-07-04
Reviewer: Antigravity (strict)
Review targets:
- [call_for_review_goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md)
- [goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md)
- [goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md)
- [antigravity_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md)

---

## Verdict

```text
approve_goal4954a_contract_measurement_plan_open_goal4954b
```

### Authorization Boundary

This verdict authorizes opening **only Goal4954-B as measurement-only work**.

It does **not** authorize:
- Implementation of columnar reprojection/sort changes;
- Implementation of binary row construction;
- Native/core changes;
- Layer 4 fusion or raw callbacks;
- Performance claims before measurement.

Goal4954-B must remain restricted to running the writer-free baseline measurement and producing the detailed phase table.

---

## Core Evaluation

### 1. The Owner Invariant: RTDL is Generic; RayJoin is an App

The contract defined in [goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954a_binary_overlay_contract_and_measurement_plan_2026-07-04.md) strictly preserves the owner invariant.
- The schema definitions for the two binary contracts ("Spatial Event Rows" and "Grouped Binary Output Rows") use entirely generic terms (`source_side_id`, `source_group_id`, `source_element_id`, `event_order`, `primary_label`, `secondary_label`, etc.) and prohibit RayJoin-specific nomenclature (`RayJoin`, `AuthorOfficial`, `output_chain`, `Section 5.7`, etc.).
- RayJoin is treated purely as an application layer that adapts its specific dataset models (CDB polygon maps, chain IDs, face IDs) into these generic core carrier schemas.
- The Ownership Table correctly partitions work: RTDL core owns generic columns, generic transforms (map, filter, sort, group, reduce), and generic aggregates. RayJoin owns paper-specific loading, comparison, text writing, output-chain byte equality, and reconstruction.

### 2. Next Authorized Step

The review confirms that the next authorized step is strictly **Goal4954-B writer-free baseline measurement**. No implementation of columnar reprojection, sorting, or new runtime capabilities is permitted during Goal4954-B.

---

## Answers to Review Questions

### 1. Does Goal4954-A define a binary overlay/event contract with generic names and generic semantics?
**Yes.** The schema for both Spatial Event Rows and Grouped Binary Output Rows are defined using generic database/spatial concepts. They are entirely explainable without reference to RayJoin, preserving the architectural boundary.

### 2. Does it keep RayJoin-specific items app-owned?
**Yes.** Under the ownership breakdown, the following remain strictly within the RayJoin application space:
- CDB file loading;
- AuthorOfficial comparator;
- Paper text writer;
- Output-chain byte equality;
- App-specific reconstruction from binary rows to paper output.

### 3. Does the ownership table correctly distinguish RTDL core progress from RayJoin app work?
**Yes.** The table cleanly separates generic mechanisms (buffers, row representations, spatial outputs, standard dataflow ops) owned by RTDL from the app-specific formats, comparisons, and writers owned by RayJoin.

### 4. Is `descriptor_pair_count` a reasonable first downstream consumer for proving binary operator value without parsing paper text?
**Yes.** Grouping the binary output rows by `(label_a, label_b)` and counting occurrences represents a fundamental generic spatial join/overlap aggregation. It is simple, completely independent of RayJoin text formatting or ordering rules, and serves as an excellent proof-of-concept for downstream operator consumption.

### 5. Is the non-RayJoin proof requirement strong enough before any carrier or consumer is counted as RTDL-core progress?
**Yes.** The requirement demands constructing/reusing a non-RayJoin spatial dataset, producing generic rows using the same carrier, running the consumer, and showing zero RayJoin/CDB/AuthorOfficial imports. This is an objective and enforceable gate to prevent core pollution.

### 6. Does the measurement plan preserve the distinction between the paper-output correctness anchor and the writer-free binary operator performance benchmark?
**Yes.** The measurement plan decouples the correctness check (the existing paper text line compared against the public answer) from the performance benchmark (the new binary operator line).

### 7. Does it correctly require comparison against AuthorOfficial overlay compute, not author text dump?
**Yes.** It explicitly requires comparing the writer-free RTDL phases against the AuthorOfficial overlay-compute reference phase. If that compute phase cannot be isolated in the author run, the comparator must be marked as `author_overlay_compute_reference_missing` and competitiveness claims are blocked.

### 8. Does it avoid pretending that removing the writer closes the compute gap?
**Yes.** The plan acknowledges that removing the writer isolates the compute gap (~2.7s for RTDL pre-fusion phases vs. ~0.04s for the author's overlay compute) but does not close it. Gate 2 explicitly fails if the measurement claims otherwise.

### 9. Are the gates sufficient to prevent app-specific RayJoin core logic, paper text semantics in RTDL core, Layer 4 fusion work, and premature performance claims?
**Yes.** The combination of Schema Genericity Rules, the Hard Promotion Gate, and the Gate 1/2/3 Decision Gates provides complete coverage to prevent these leaks.

### 10. Should Goal4954-B open as measurement-only work with no columnar reprojection/sort implementation yet?
**Yes.** Goal4954-B is authorized strictly as a writer-free baseline measurement phase to establish the precise benchmark and phase table breakdown. It is not an implementation phase.
