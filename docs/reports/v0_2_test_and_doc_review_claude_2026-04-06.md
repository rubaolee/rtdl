# RTDL v0.2 Test and Doc Review

Date: 2026-04-06
Reviewer: Claude
Status: accepted

## Verdict

Accepted. The v0.2 test-and-documentation package is accurate, technically honest, and
internally consistent. No overclaiming found. Platform and backend boundaries are enforced
throughout.

## Findings

### Goal 130 — Test Plan and Execution

The execution report is accurate against the underlying Linux artifact.

- All timing figures and parity results verified against lx1 JSON artifacts.
- The `n/a` fix for missing PostGIS timing entries is real and present in the harness.
- Runner repair is real: 7 `test_matrix_runner_test.py` tests pass locally.
- One transparency gap: the execution report labels PostGIS timings from single-shot
  validation passes, not from the 3-iteration mean used for isolated backend timings.
  This is not an error but is not stated explicitly. It explains the gap between CPU x64
  figures in the report versus the perf artifact (0.010713s vs 0.001937s). Worth noting
  in the runner comments but not a correctness problem.
- Scope note: `v0_2_linux` runner currently contains 2 unittest modules, not a broad
  suite. The report does not overclaim coverage.

### Goal 131 — Linux Stress Audit

The stress audit to x4096 is verified.

- x1024, x2048, x4096 hitcount and anyhit row counts match the artifact JSON exactly.
- All parity flags are `true` in the artifact.
- The artifact timestamp and hostname (lx1, 2026-04-06T21:53:56) are consistent with the
  report.
- No fabricated figures. No rounding inconsistencies.

### v0.2 User Guide

The guide is honest and accurate.

- All four Quick Start file references exist on disk.
- Platform section correctly names Linux as primary and Mac as limited local (Python
  reference, C/oracle, Embree only).
- OptiX wins are attributed to the accepted candidate-index algorithmic redesign, not to
  universal RT-core-native maturity. This matches the actual source of wins.
- Vulkan is described as correctness/portability backend, not flagship. Matches
  implementation status.
- Current Limits section is explicit: no claims of exact computational geometry, full
  overlay materialization, or universal backend maturity.

### SQL Workloads

The SQL file and its companion report are consistent with each other and with the handoff
boundary.

- `segment_polygon_hitcount` uses `LEFT JOIN` — zero-hit segments are preserved. Correct.
- `segment_polygon_anyhit_rows` uses plain `JOIN` — zero-hit segments intentionally
  excluded. Correct.
- GiST indexes created on both `segments.geom` and `polygons.geom` before `ANALYZE`.
  Consistent with handoff note.
- The companion report matches the SQL file exactly: no drift between the explanation and
  the actual query shapes.
- The PostGIS path uses the same representative RTDL datasets as the runtime backends. No
  independent or synthetic geometry.

### Goal 132 — Gemini Doc Draft Review

The corrections applied to the Gemini draft are appropriate and complete.

- Platform honesty: Linux primary / Mac limited — applied correctly.
- Backend honesty: OptiX framed as algorithmic win, Vulkan framed as portability backend —
  applied correctly.
- Scope discipline: guide limited to the two real v0.2 families and narrow generate-only
  line — applied correctly.
- The report accurately describes what corrections were required and why.

## Summary

The package is clean. All artifact figures are traceable to actual lx1 runs. The user
guide is technically accurate and platform-honest. The SQL workload file matches its
companion report exactly. The one transparency gap (PostGIS single-shot vs 3-iteration
mean labeling in Goal 130) is minor and does not affect correctness claims. No overclaiming
found anywhere in the package.
