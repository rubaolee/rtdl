# Codex Review: Goal 99 Final Package

### 1. Verdict: APPROVE

### 2. Findings

Goal 99 is technically sound and honestly scoped. The implemented change in
`/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py` moves one-time
OptiX cold-start work into `PreparedOptixKernel.bind(...)` for the
positive-hit `point_in_polygon` path only. That matches the accepted prepared
measurement boundary because `bind_sec` is already reported separately while the
timed backend rows measure `bound.run()` only.

The focused regression test in
`/Users/rl2025/rtdl_python_only/tests/goal99_optix_cold_prepared_run1_win_test.py`
correctly checks the key behavior:

- positive-hit prepared binds warm once before the first timed run
- non-positive-hit prepared binds do not change behavior

The clean Linux result artifact in
`/Users/rl2025/rtdl_python_only/docs/reports/goal99_optix_cold_prepared_run1_win_artifacts_2026-04-05/summary.json`
supports the claim:

- run 1:
  - OptiX `2.5369022019876866 s`
  - PostGIS `3.39459279399307 s`
  - parity `true`
- run 2:
  - OptiX `2.133376205994864 s`
  - PostGIS `3.01533580099931 s`
  - parity `true`

### 3. Agreement and Disagreement

I agree with both the optimization direction and the claim boundary. This is
not presented as a cold raw-input win or a hidden end-to-end change. It is
explicitly a prepared/prepacked boundary improvement, and the report states that
clearly. The implementation also preserves the Goal 98 conservative-candidate
repair because it does not change the native OptiX correctness path.

### 4. Recommended next step

Goal 99 is acceptable for integration. The next clean move is to publish Goal
98 and Goal 99 together and then update the release-validation package so the
pre-release gate reflects the repaired and improved OptiX state.
