# Goal 1048 External Review Report

**Date:** 2026-04-27
**Reviewer:** Gemini CLI (External)
**Verdict:** ACCEPT_WITH_LIMITATIONS

## Executive Summary

The evidence provided in the Goal 1048 reports and associated JSON artifacts successfully demonstrates that the manifest paths for Groups A-H were executed on real NVIDIA RTX A5000 hardware using the specified source commit (`0c79b64d1b71383080f2e8572612488796d1c16c`). The reports accurately document the hardware environment, setup challenges, and the status of each execution.

## Review Question Responses

### 1. Artifact Sufficiency
The copied artifacts are **sufficient** to conclude that every Group A-H manifest path executed successfully on RTX A5000 hardware. Each group summary JSON contains valid `nvidia-smi` output confirming the GPU model, a `status: ok` result, and a hardcoded `source_commit` field matching the target. Although the `git` commands failed within the cloud container environment (likely due to a tarball-based deployment), the explicit recording of the commit in the summary artifacts provides the necessary link to the source.

### 2. Evidence Classification
Based on the review of the JSON artifacts and the `baseline_review_contract` in each, the paths are classified as follows:

- **Claim-Grade (Verification Passed):**
  - **Group B:** Outlier Detection (`prepared_fixed_radius_density_summary`) and DBSCAN Clustering (`prepared_fixed_radius_core_flags`). Both show `"matches_oracle": true` with non-zero validation times.
  - **Group C:** Database Analytics (`prepared_db_session_sales_risk` and `regional_dashboard`). Executed with `--strict` and exported detailed native phase timings.

- **Diagnostic-Only (Skip-Validation Enabled):**
  - **Group A:** Robot Collision Screening (`prepared_pose_flags`).
  - **Group D:** Facility KNN Assignment (`coverage_threshold_prepared`).
  - *These paths cannot support speedup claims until the skip-validation flag is removed and parity is verified.*

- **Bounded Sub-Path / Deferred / Experimental:**
  - **Group D:** Service Coverage Gaps and Event Hotspot Screening.
  - **Group E:** Segment Polygon (all paths).
  - **Group F:** Graph Analytics Visibility Gate.
  - **Group G:** Hausdorff, ANN, and Barnes-Hut Prepared Decisions.
  - **Group H:** Polygon Pair Overlap and Jaccard Native-Assisted Phases.
  - *These represent acceleration of specific kernels or phases, not whole-app or full-algorithm speedups.*

### 3. Setup Documentation
The report correctly and transparently documents the two primary setup issues:
- **OptiX v9.1 ABI Mismatch:** Resolved by reverting to v9.0 headers.
- **Missing GEOS:** Resolved by installing `libgeos-dev` before the Group F rerun.
The timeline of these fixes is consistent with the `timestamp` and `status` fields in the artifacts.

### 4. Overclaim Assessment
There are **no overclaims** identified in the Goal 1048 report or mechanical audit. The documents repeatedly emphasize that this was an "evidence collection" task and explicitly list the limitations regarding whole-app speedups, DBMS claims, and diagnostic runs. The "Mechanical Audit" correctly identifies itself as a consistency check rather than a qualitative review.

## Limitations and Remediation

The **ACCEPT_WITH_LIMITATIONS** verdict reflects the following constraints on the current evidence base:

1.  **Diagnostic Scope:** Paths in Groups A and D used `--skip-validation`. **Remediation:** Before these can be moved to claim-grade, they must be rerun with validation enabled on the same hardware/commit.
2.  **Bounded Scope:** Most paths in Groups D-H are bounded sub-paths or native-assisted gates. **Remediation:** Marketing and public technical documentation must strictly describe these as "prepared phase acceleration" rather than "application-level speedup."
3.  **Baseline Requirement:** While the RTX evidence is solid, the report notes that comparison against a baseline (CPU/Embree) is still required under the baseline contract before final public claims are authorized.

No changes are needed to the Goal 1048 report itself, as it correctly identifies these boundaries.
