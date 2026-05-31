# Goal2868: Gemini Independent Review of v2.5 Last-Day Work Since Claude Reviews

Reviewer: Gemini (independent external reviewer)
Date: 2026-05-31
Responds to: `docs/handoff/CALL_FOR_REVIEW_GOAL2868_V2_5_LAST_DAY_WORK_SINCE_CLAUDE_REVIEWS_2026-05-31.md`
Audited range: `3f8b1d5b` (Goal2773 intake) through `fbe28476` (Goal2867 bypass audit)

---

## Verdict

**accept-with-boundary.**

### Release-Boundary Statement
The last-day v2.5 internal engineering packet is coherent and accepted with boundaries; final release remains blocked pending an explicit user-requested release packet and fresh 3-AI release consensus.

No public speedup wording, broad RT-core speedup wording, whole-app speedup wording, true zero-copy wording, package-install wording, or automatic Triton preview selection is authorized by this review. The native engine remains strictly app-agnostic.

---

## Findings

### F1 — Large Performance Gap for Triton Preview (High Severity)
The partner selection guidance ([v2_5_partner_selection_guidance.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v2_5_partner_selection_guidance.py)) documents significant performance gaps where Triton is slower than Torch CUDA same-contract reductions (measured on the RTX A5000 pod):
- `segmented_count_i64` is **22.78x–38.04x slower** (Goal2796).
- `segmented_sum_f64` is **38.29x–84.10x slower** (Goal2796).
- `segmented_min_f64` is **44.84x–192.49x slower** (Goal2796).
- `segmented_max_f64` is **36.00x–142.23x slower** (Goal2796).
- `grouped_topk_f64` is **4.91x–10.04x slower** (Goal2784).
- `grouped_vector_sum_f64x2` is **3.76x–16.86x slower** (Goal2786).
- `grouped_argmin_f64` (witness) is **31.88x–45.15x slower** (Goal2787) and **3.77x–30.73x slower** (Goal2788).

While the selection policy is correct and honest (it marks Triton as preview-only, forbids automatic auto-selection, and defaults to primitive-first/fallback paths), this massive performance disparity is a severe blocker for any future production promotion of the Triton backend.

### F2 — Tiled Crossover Thresholds are Highly Unstable (Medium Severity)
Goal2790 ([v2_5_partner_selection_guidance.py:330-356](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v2_5_partner_selection_guidance.py#L330-L356)) documents that Triton is slower than Torch for 2K, 4K, and 8K dense point-nearest Hausdorff witness reductions, but becomes faster (**0.745x ratio**) at 16K x 16K.
This crossover is highly sensitive to workload size, density, and hardware characteristics. Automatic selection of Triton based on simple heuristics would be brittle and error-prone. The code correctly handles this by forcing explicit app/user selection and planning guidance, rather than auto-selecting.

### F3 — Determinism and Tie-Breaks are Aspirational but Untested in Hardware Sweep (Medium Severity)
The witness, argmax, and top-k operators contain potential non-determinism when multiple elements share identical scores or distances. While the determinism policy ([v2_5_determinism_policy.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v2_5_determinism_policy.py)) successfully declares tie-break policies at the API level, these policies have only been validated on a single hardware architecture (RTX A5000 pod) under small inputs. There is a risk that different CUDA compiler optimization paths or register pressure on other GPUs will violate these tie-break assertions in the wild.

### F4 — Compact Child Output Can Mask Subprocess Failures (Low Severity)
Goal2855 ([goal2855_summary.json](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reports/goal2865_current_packet_after_front_doors_pod/goal2855_summary.json)) uses compact child logging to keep harness execution output clean. While useful, this risks hiding diagnostic details of transient CUDA driver crashes, memory allocation failures, or timeout warnings. Downstream processes must strictly check the `returncode_ok` and `artifact_status_ok` fields in the generated JSON summary to verify that passing status isn't falsely assumed.

---

## Review Answers

### 1. Did the work respond to Claude's four main corrections?
**Yes.**
- **Neutral Seam Audit:** Successfully completed. The torch-coercing path (`_maybe_torch_column`) has been cleaned up, and all boundaries are routed through the neutral seam contract.
- **Partner-Set Mismatch:** Reconciled. The role of CuPy is clearly constrained to conformance/descriptors, while Numba is established as the primary fallback, resolving the code-docs mismatch.
- **Deterministic Reductions:** The determinism policy has been formalized and validated.
- **Tier-Label Drift:** Fixed. `librts` is correctly treated as Tier C, and `spatial_rayjoin` count/parity vs rows is properly separated.

### 2. Are the new public front doors generic and app-agnostic?
**Yes.**
The API exposed in [v2_5_triton_app_migration.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v2_5_triton_app_migration.py) covers generic operations (`segmented_count_i64`, `segmented_sum_f64`, etc.) and does not leak any application semantics (no RayDB or DBSCAN vocabularies in the native signature). The front door is complete and clean.

### 3. Does the partner selection policy block blind Triton auto-selection?
**Yes.**
The planner policy is strictly advisory (`planner_policy: "advisory_only_explicit_app_partner_choice"`). It requires explicit user choice and refuses to auto-select Triton, especially given the measured performance gap where Torch CUDA remains significantly faster on smaller sweeps.

### 4. Does the Goal2865 packet prove all 7/7 harnesses pass at the new head?
**Yes.**
The summary artifact ([goal2855_summary.json](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reports/goal2865_current_packet_after_front_doors_pod/goal2855_summary.json)) confirms `all_pass: true` for the 7 canonical harnesses on the RTX A5000 pod under a clean Git state, ensuring no regression occurred during the front-door refactoring.

### 5. Were RTNN batch optimizations and negative probes handled correctly?
**Yes.**
The batch optimizations (Goal2821–2822) are generic. The negative probe (Goal2823) was correctly rejected as the default runtime path because launching a second kernel to reduce partials on the device introduced overhead that offset any download savings.

### 6. Does `validate_v2_5_internal_readiness_packet` block release?
**Yes.**
The validator checks that the internal readiness status is exactly `"internal_evidence_packet_coherent_not_release_ready"` and enforces that all claim authorizations are `False`.

---

## Required Fixes Before a Future Release Review

1. **Performance Parity or Clear Fallback Defaults:** The performance gaps identified in **F1** must either be addressed by optimized Triton custom kernels, or the system must explicitly document Numba/Torch as the promoted performance path while Triton remains marked as a non-default preview.
2. **Multi-Vendor Verification:** Before release, the determinism and tie-break policies (**F3**) must be validated on at least one other NVIDIA architecture (e.g., L4 or H100) to ensure compilation/hardware variances do not break exact-match contracts.
3. **Explicit User Request:** A formal release review request must be initiated by the user, followed by a fresh 3-AI consensus pass.

---

## Optional Future Work

- **CUDA Graph Replay:** Implement CUDA Graph Replay for static/repeated prepared workloads.
- **Cross-Framework Zero-Copy Transports:** Integrate DLPack and `__cuda_array_interface__` directly to allow zero-copy handoffs without framework-specific coercion.
