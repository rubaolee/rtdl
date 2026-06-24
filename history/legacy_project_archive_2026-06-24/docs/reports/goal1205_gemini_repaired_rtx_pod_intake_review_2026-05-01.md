# Goal1205 Gemini Repaired RTX Pod Intake Review

Date: 2026-05-01

Verdict: `BLOCK`

The Goal1205 intake tool contains schema mismatches that will cause it to incorrectly classify DB repairs and Jaccard chunk policies when parsing real Goal1204 artifacts. While the decision rules are conceptually conservative and correct, the implementation paths do not align with the actual JSON output of the underlying profilers.

## Findings

### 1. DB Chunked Metadata Mismatch
- **Issue:** `_db_chunked()` in `scripts/goal1205_repaired_rtx_pod_intake.py` looks for `prepared_dataset` or `session` at the top level or directly inside `results[0]`.
- **Reality:** `scripts/goal756_db_prepared_session_perf.py` (via `run_suite`) nests these metadata fields inside `results[0]["prepared_session_output"]["sections"]["sales_risk"]["session"]` or `results[0]["reported_prepare_phases_sec"]["sales_risk"]`.
- **Impact:** `repair_passed` will be `False` even when the repair is successful.

### 2. Jaccard Classification Key Mismatch
- **Issue:** `_jaccard_row()` expects `policy.get("classification") == "diagnostic_only"`.
- **Reality:** `scripts/goal877_polygon_overlap_optix_phase_profiler.py` uses the key `"policy"` for this string (e.g., `policy.get("policy") == "diagnostic_only"`).
- **Impact:** The `diagnostic_only` check will fail for chunk 64, blocking the `public_safe_chunk_ready` decision.

### 3. Test False Positive
- **Issue:** `tests/goal1205_repaired_rtx_pod_intake_test.py` passes because it mocks a simplified JSON structure that matches the intake's expectations but does not reflect the actual output of `goal756` or `goal877`.
- **Recommendation:** Update the test to use a representative snippet of actual `goal756` and `goal877` output.

## Required Fixes

- [ ] **Fix DB Detection:** Update `_db_chunked` to traverse the `prepared_session_output` or `reported_prepare_phases_sec` paths produced by `goal756`.
- [ ] **Fix Jaccard Key:** Update `_jaccard_row` to check the `"policy"` key for the `"diagnostic_only"` value.
- [ ] **Update Tests:** Align test mock data with the actual nested structures found in the profiler outputs.

## Decision Rules Evaluation

- **Conservatism:** The rules for `repair_passed`, `public_safe_chunk_ready`, and `same_scale_public_positive_candidate` are appropriately conservative for public-claim discipline.
- **Boundary:** The boundary wording is excellent and clearly prevents the intake tool from being misinterpreted as a release authorization.
- **Timing Floor:** The 0.1s floor for Road Hazard is correctly implemented and aligned with Goal1204's scale increase.

Once the schema alignments are corrected, the intake tool will be ready for the next paid RTX pod run.
