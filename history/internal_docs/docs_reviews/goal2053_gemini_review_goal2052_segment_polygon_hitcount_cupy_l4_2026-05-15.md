# Review: Goal2052 Segment/Polygon Hitcount CuPy L4 Runner Repair

**Reviewer:** Gemini CLI (Autonomous Reviewer)  
**Date:** 2026-05-15  
**Verdict:** `accept-with-boundary`

## Executive Summary

This independent review confirms the technical correctness and artifact validity of the Goal2052 runner repair. The repair addressed a dtype mismatch in the `goal1863` performance script, where OptiX ray columns were incorrectly initialized as `float64` instead of the required `float32`. 

The review validates that:
1. The runner repair is surgically scoped and technically accurate.
2. The addition of the `--output-capacity` knob correctly handles scaling limitations discovered during the pod run.
3. The L4 artifacts (2048 and 4096 rows) demonstrate strict parity and performance advantages for the v2 CuPy prepared path.
4. The report maintains rigorous claim boundaries, explicitly denying release readiness or broad architectural speedup claims.

## Technical Analysis

### 1. Runner Repair Correctness
The script `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py` has been correctly updated to use `float32` for OptiX ray columns (`ox`, `oy`, `dx`, `dy`, `tmax`). This change aligns with the OptiX ABI requirements for the bounded all-witness path. Crucially, the triangle vertices remain `float64`, preserving the precision of the input geometry.

### 2. Output Capacity Scaling
The introduction of the `--output-capacity` argument is a significant improvement for benchmark stability. The review notes the "fail-closed" finding at 4096 rows with default capacity:
- **Finding:** The runner correctly identifies and reports a "partner segment/polygon column adapter overflow" when witness storage is insufficient.
- **Resolution:** The explicit `--output-capacity 32768` parameter allowed the 4096-row run to complete successfully on the NVIDIA L4.

### 3. Artifact Validation (NVIDIA L4)
The review examined two primary artifacts:
- **2048-Row Artifact (`goal2052_segment_polygon_hitcount_cupy_l4_2048.json`):**
  - Result: `pass`.
  - Parity: `strict_counts_match: true`.
  - Performance: The v2 prepared CuPy path achieved a 0.370x ratio (approx. 2.7x speedup) against the v1.8 prepared native OptiX baseline.
- **4096-Row Artifact (`goal2052_segment_polygon_hitcount_cupy_l4_4096_capacity32768.json`):**
  - Result: `pass` (with explicit capacity 32768).
  - Parity: `strict_counts_match: true`.
  - Performance: The v2 prepared CuPy path achieved a 0.268x ratio (approx. 3.7x speedup) against the v1.8 prepared native OptiX baseline.

### 4. Warmup and JIT Transparency
The report `docs/reports/goal2052_segment_polygon_hitcount_cupy_l4_runner_repair_2026-05-15.md` correctly identifies the high latency of the first unprepared sample (e.g., 3.68s for 2048 rows) as setup/JIT/cache cost. This transparency ensures that the benchmark results are not misleadingly "sanitized" by hiding initial overheads.

## Claim Boundaries

The review confirms that the following boundaries are strictly enforced in both the JSON artifacts and the final report:
- **AUTHORIZED:** Same-contract timing row evidence for partner-owned device count columns.
- **UNAUTHORIZED:**
  - v2.0 release readiness.
  - Whole-app speedup claims across the RTDL suite.
  - Broad RT-core speedup claims.
  - Package installation or deployment readiness.

## Conclusion

The Goal2052 repair is successful. It restores functionality to the v2 partner performance runner on modern NVIDIA hardware (L4) and provides a necessary control knob for scaling tests. The evidence supports the performance claims for this specific hitcount workload under the defined "same-contract" conditions.

**Verdict:** `accept-with-boundary`
