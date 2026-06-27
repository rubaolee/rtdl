# Goal 565 External Review

Date: 2026-04-18

Verdict: **ACCEPT**

## Scope Check

This is a valid bounded HIPRT performance-improvement round. The goal is
correctly scoped to a single workload: 3D `ray_triangle_hit_count` with a
prepared HIPRT context on Linux NVIDIA GTX 1070. The honesty boundary is
explicit in both the report and the JSON artifact, and no overreach claims are
present.

## Technical Credibility

The prepared-vs-one-shot split is technically sound:

- The one-shot path (`0.5655s`) pays HIPRT/Orochi context init, geometry
  upload/build, and trace-kernel compilation on every cold call.
- The prepare phase (`0.5238s`) pays those same costs once; subsequent prepared
  queries only pay ray upload + BVH traversal + copy-back.
- The 274.7x speedup is arithmetically consistent: `0.5655 / 0.00206 ≈ 274.5x`.
- Five repeated query timings are tight (`0.00197–0.00213s`), confirming stable
  repeated execution with no warm-up drift.
- All backends report `parity_vs_cpu_reference: true`; no false parity is
  claimed.

## Script Quality

- `measure()` correctly separates timing from correctness comparison.
- `prepared.close()` is called in a `finally` block — no resource leak.
- Speedup is only computed when both `hiprt_one_shot` and `hiprt_prepared` are
  `"PASS"`; unavailable backends are handled gracefully.
- Input validation guards against non-positive argument values.

## Test Coverage

Tests are minimal but appropriate: determinism of `make_case` and a CPU-path
smoke test that exercises the full payload structure without requiring GPU
hardware. The harness tests from goal544 and goal560 are also re-run as
regression guards.

## Disallowed Claims Confirmed Absent

- No claim of AMD GPU validation.
- No claim of RT-core speedup.
- No claim that all 18 v0.9 workloads have prepared coverage.
- No claim that HIPRT is generally performance-leading across workloads.

## Summary

The result is honest, reproducible on the stated hardware, and correctly
interpreted. The prepared-query performance path is a real and useful mitigation
for repeated-query application shapes that reuse built geometry.
