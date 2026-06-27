Based on a technical audit of the OptiX prototype in `/Users/rl2025/claude-work/2026-04-02/rtdl`, here is the review memo.

## 1. Confirmed Findings

- **Payload register mismatches**
  - `pip_kernel` uses 4 payload registers in `optixTrace` (around line 721) but the pipeline is initialized with `numPayloadValues=3` (around line 1348).
  - `rayhit_kernel` uses 4 payload registers in `optixTrace` (around line 966) but the pipeline is initialized with `numPayloadValues=2` (around line 1703).
  - `segpoly_kernel` uses 4 payload registers in `optixTrace` (around line 1072) but the pipeline is initialized with `numPayloadValues=2` (around line 1815).
- **Overlay containment flaw**
  - The CPU-side fallback for polygon containment only checks the first vertex of each polygon pair. That is not a correctness-complete containment test for the claimed hybrid overlay strategy.
- **macOS artifact mismatch**
  - The `Makefile` emits `librtdl_optix.so`, while `optix_runtime.py` expects `.dylib` on Darwin. The default build/load path is therefore broken on macOS.

## 2. Disagreements

- The earlier Gemini review overstated architectural quality and implementation readiness.
- The earlier Gemini review's correctness framing for overlay was too strong relative to the actual single-vertex containment check.

## 3. Required Fixes Before Merge

1. Align `numPayloadValues` with the payload registers actually used by each OptiX pipeline.
2. Replace the single-vertex overlay containment supplement with a correctness-complete containment strategy.
3. Make the build artifact naming portable so the runtime loader can discover the built library on macOS without manual overrides.

## 4. Final Verdict

**NO-MERGE**

The earlier Gemini review significantly overclaimed readiness. The external OptiX prototype contains substantial work, but it is not ready to merge into the controlled RTDL repository until the blocking issues above are fixed and re-audited.
