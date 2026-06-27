# Antigravity Completion Review: V4 Goal4649 CuPy Front-Door Certification Gate

Date: 2026-06-25
Reviewer: Antigravity (Gemini 3.5 Flash)
Verdict: `accept_goal4649_complete`

---

## Scope

This review covers the following target files and resources:
- Call For Review: [call_for_review_v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/reviews/call_for_review_v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md)
- Goal4649 Report: [v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4649_cupy_frontdoor_certification_gate_2026-06-25.md)
- Target Code: [v4_cupy_certification.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_cupy_certification.py)
- Gate Script: [v4_goal4649_cupy_grouped_reduction_certification_gate.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/scripts/v4_goal4649_cupy_grouped_reduction_certification_gate.py)
- POD Live Evidence JSON: [pod_live_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json)
- POD Live Evidence Markdown: [pod_live_summary.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.md)
- Test Files:
  - [v4_goal4649_cupy_certification_gate_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4649_cupy_certification_gate_test.py)
  - [v4_goal4649_cupy_certification_pod_evidence_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4649_cupy_certification_pod_evidence_test.py)
- Predecessor Consensus: [goal4648_completion_consensus_2026-06-25.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/reviews/goal4648_completion_consensus_2026-06-25.md)

---

## 1. Verification of Key Areas

### A. Narrow CuPy `grouped_vector_sum_f64x2` Certification
Goal4649 strictly certifies a very narrow subset of CuPy capabilities:
* Certified ready targets (2 passed): `cupy_grouped_reduction_device_columns_262144` and `cupy_grouped_reduction_device_columns_524288` using the `grouped_vector_sum_f64x2` operator.
* Non-certified mapping debt (correctly isolated): `cupy_segment_polygon_hitcount_prepared_scaling` and `cupy_hausdorff_witness_continuation` are explicitly set to status `requires_v4_adapter_mapping_before_pod`. They were excluded from live gate executions and are flagged as mapping debt, avoiding premature CuPy certification inflation.

### B. Denominator Honesty
The CPU denominator was successfully corrected from a simplified group-level calculation to a complete Python CPU loop iterating over all input rows (row-by-row CPU loop):
* This correction ensures a direct, same-contract comparison.
* The synthetic nature of the resulting speedup is explicitly called out as an internal certification floor check (clearing the pre-frozen `>=1.20x` floor), rather than serving as public release speedup wording.

### C. Sufficiency of Evidence Fields
The live POD evidence file `pod_live_summary.json` records all necessary telemetry:
* **Correctness**: confirmed with `correctness_parity = true`, and zero error (`max_err_x = 0.0`, `max_err_y = 0.0`).
* **Scale**: rows and groups are documented (e.g. 262144 rows / 1024 groups and 524288 rows / 2048 groups).
* **Denominator**: `cpu_row_loop_seconds` is explicitly recorded.
* **Environment**: GPU (`NVIDIA RTX A5000`), driver (`570.195.03`), Python (`3.12.3`), and CuPy (`14.1.1`) are fully captured.
* **Hot host-materialization flag**: `host_materialization_in_hot_path = false`.
* **Claim Boundaries**: `public_claim_authorized`, `rt_core_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, and `true_zero_copy_claim_authorized` are all set to `false`.

### D. Non-Authorization Boundaries
All eight required non-authorization boundaries are fully preserved and explicitly set to `false` in code and evidence. This review does not authorize:
* public V4 release/tag wording;
* broad V4 speedup language;
* app-level V4-vs-V2.14/V3 claims;
* blanket CuPy support;
* CuPy RT-core Tier-2 claims;
* Hausdorff CuPy claims;
* hitcount CuPy claims;
* arbitrary Numba callback claims;
* C ABI / embedding claims;
* true-zero-copy claims;
* treating partner migration or partner parity as V4 speed evidence.

---

## 2. Answers to Call for Review Questions

1. **Is Goal4649 complete enough to start Goal4650?**
   * **Yes**. The certification gate infrastructure is complete, unit tests pass locally, and live POD evidence has been gathered and validated. This establishes the necessary protocol foundation to proceed to Goal4650.
2. **Do the two passed rows legitimately certify a narrow CuPy `grouped_vector_sum_f64x2` partner front-door surface?**
   * **Yes**. Both rows cleared correctness parity with zero error, did not trigger hot-path host materialization, and cleared the frozen `>=1.20x` performance speedup floor.
3. **Is it correct that Hausdorff/hitcount CuPy remain mapping debt, not support?**
   * **Yes**. They are explicitly flagged as `requires_v4_adapter_mapping_before_pod`, and excluded from active catalog support.
4. **Is the denominator honest enough for a certification floor check after the correction from group formula to full Python row loop?**
   * **Yes**. It uses a true row-scoped CPU loop, verifying the performance baseline without overclaiming or distorting the comparison.
5. **Are the evidence fields sufficient: correctness, scale, denominator, environment, hot host-materialization flag, claim boundaries?**
   * **Yes**. All requested fields are completely populated and asserted in tests.
6. **Does this preserve AM1: partner migration/parity cannot become V4 speed evidence?**
   * **Yes**. `partner_migration_counts_as_v4_speed_win` and `partner_parity_counts_as_v4_speed_win` are strictly `False` across all targets.
7. **Should any public catalog/docs be updated now, or should promotion wait for Goal4651 catalog gate?**
   * **Promotion must wait**. No public documents or catalog entries are modified as part of this goal. Promotion is strictly deferred to the Goal4651 gate.

---

## Verdict Summary

The completion criteria for Goal4649 have been successfully satisfied. The narrow CuPy certification gate has been executed, telemetry has been recorded honestly, and non-authorization boundaries are well-contained.

**Verdict**: `accept_goal4649_complete`
