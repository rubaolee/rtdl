# Goal1206 Gemini Review: Live Pod Merged Evidence

Date: 2026-05-01
Reviewer: Gemini CLI

## Review Summary

This review covers the merged evidence from the Goal1204 RTX 4090 live pod run and the subsequent Goal1204 Embree4 recovery run. The primary objective was to validate the technical acceptability of the merged data and its suitability for future public wording decisions.

## Evaluation

### 1. Technical Acceptability of Merged Evidence
The merge of the original Goal1204 artifacts with the Embree4 recovery artifacts is **technically acceptable**. 
- The original run successfully completed all OptiX and Jaccard workloads but failed on Embree controls due to a host environment mismatch (Ubuntu's default Embree 3 vs. RTDL's requirement for Embree 4).
- The recovery run specifically targeted these failed controls after a manual installation of Embree 4.4.0.
- The merge process is transparently documented in the intake reports, preserving the original failure context while providing the necessary repaired data points.
- SHA256 hashes for both source artifacts are provided for auditability.

### 2. Validation of DB and Road-Hazard Ratios
The reported ratios are valid for same-scale comparison:
- **DB compact-summary (100k/300k):** Ratios of ~1.12x and ~1.16x demonstrate near-parity with a slight OptiX advantage. These are solid baseline candidates.
- **Road Hazard (40k):** The ratio of **3.53x** (Embree 0.81s vs. OptiX 0.23s) is a strong candidate for positive public wording. It significantly exceeds the 0.1s timing floor and demonstrates a clear hardware acceleration benefit on the RTX 4090.

### 3. Jaccard Evidence Scope
The Jaccard results are correctly categorized:
- **Chunk 512:** Marked as `public_safe` and `parity_vs_cpu: true`. This serves as correctness/readiness evidence.
- **Chunk 64:** Correctly marked as `diagnostic_only` with `parity: false`. 
- The decision to limit Jaccard to "public-safe chunk ready" rather than speedup wording is appropriate given the current sensitivity of Jaccard to chunk sizes on certain GPU architectures.

### 4. Documentation of Environment Issues
The report clearly and accurately documents:
- The conflict between Ubuntu's `libembree-dev` (Embree 3) and RTDL's Embree 4 requirement.
- The specific recovery steps taken (manual install of 4.4.0 and symlinking to `/usr` to satisfy current Linux runtime constraints).
- The recommendation for a follow-up fix to support `RTDL_EMBREE_PREFIX` on Linux to match Windows behavior.

## Verdict: `ACCEPT`

The evidence is technically sound, the recovery process was surgical and well-documented, and the resulting data points provide a valid foundation for subsequent public wording reviews.

### Required Follow-up (Non-Blocking)
- Implement the proposed fix for `RTDL_EMBREE_PREFIX` on Linux to prevent similar environment-related failures in future pod deployments.
