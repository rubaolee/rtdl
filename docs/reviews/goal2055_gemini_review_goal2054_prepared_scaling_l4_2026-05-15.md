# Independent Review: Goal2054 Segment/Polygon Hitcount Prepared Scaling L4

Reviewer: Gemini
Date: 2026-05-15
Subject: Goal2054 Prepared Scaling (8192-65536) on NVIDIA L4

## Overview

This review covers the artifacts for Goal2054, which validates the prepared-only scaling path for the segment/polygon hitcount workload on the NVIDIA L4 pod. The goal introduced a `--skip-one-shot-baseline` flag to the runner to avoid excessive execution time for large scaling rows while maintaining strict parity and same-contract comparisons.

## Artifacts Reviewed

- Runner: `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`
- JSON Reports (8192, 16384, 32768, 65536):
  - `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_8192_prepared_capacity262144.json`
  - `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_16384_prepared_capacity1048576.json`
  - `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_32768_prepared_capacity4194304.json`
  - `docs/reports/goal2054_segment_polygon_hitcount_cupy_l4_65536_prepared_capacity16777216.json`
- Summary Report: `docs/reports/goal2054_segment_polygon_hitcount_prepared_scaling_l4_2026-05-15.md`
- Validation Tests: `tests/goal2054_segment_polygon_hitcount_prepared_scaling_l4_test.py`

## Findings

### 1. Skip Flag Logic
The implementation of `--skip-one-shot-baseline` in `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py` is appropriate. It correctly bypasses the one-shot baseline execution while populating the JSON artifact with a `skipped: true` status and a clear `skip_reason`. It does not attempt to "fake" or estimate the one-shot timing, which is correct given the context that Goal2052 already established the one-shot baseline for lower counts.

### 2. Scaling Artifacts and Timing
All four L4 artifacts (8192, 16384, 32768, and 65536) successfully demonstrate bounded, prepared same-contract timing rows.
- **8192**: v2 prepared is ~8.2x faster than v1.8 prepared.
- **16384**: v2 prepared is ~16.3x faster than v1.8 prepared.
- **32768**: v2 prepared is ~44.7x faster than v1.8 prepared.
- **65536**: v2 prepared is ~78.6x faster than v1.8 prepared.

The data shows that the v2 prepared path remains nearly flat (~2.2ms to ~2.35ms) across the scaling range, while the v1.8 prepared native row path grows with count, confirming the efficiency of the GPU-resident continuation path.

### 3. Strict Parity and Reuse
Strict parity is maintained across all runs (`strict_counts_match: true`). The artifacts confirm that prepared scene reuse and output column reuse are active (`prepared_scene_reused: true`, `witness_output_columns_reused: true`), adhering to the Goal 1886/1850 contracts.

### 4. Claim Boundaries
The summary report and JSON artifacts correctly block overclaims. They explicitly disclaim:
- v2.0 release readiness.
- Broad all-app speedup.
- Broad RT-core speedup.
- Exact polygon overlay/Jaccard acceleration.
- Exact Hausdorff witness bridge.

The allowed claims are correctly restricted to the specific workload and artifact scaling on the L4 pod.

### 5. Validation Consistency
The tests in `tests/goal2054_segment_polygon_hitcount_prepared_scaling_l4_test.py` provide comprehensive coverage, verifying the script logic, artifact integrity, and report content.

## Verdict

The artifacts for Goal2054 are complete, consistent, and strictly follow the established boundaries.

**Verdict: accept-with-boundary**
