# Goal 547 External Review: HIPRT Correctness Harness

Date: 2026-04-18
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Summary

The harness is a complete, honest baseline for v0.9 HIPRT progress tracking. It
covers all 17 target workloads, distinguishes all four states correctly, and
gives later implementation goals a measurable CPU-reference baseline to drive
toward PASS.

## Evidence

**Coverage**: All 17 v0.9 workloads enumerated in `cases()` match the plan
exactly. `test_matrix_covers_all_v09_target_workloads` enforces this as a
structural test.

**Status discrimination**:

- `NOT_IMPLEMENTED` (16 on both platforms): API skeleton recognizes the
  workload but raises `NotImplementedError` with a message citing the tracking
  goal (549 / 550 / 551) and the phrase "No CPU fallback is used". The test
  `test_unimplemented_workloads_are_explicit_not_cpu_fallbacks` enforces that
  phrase.
- `HIPRT_UNAVAILABLE` (1 local, 0 Linux): `ray_triangle_hit_count_3d`
  correctly surfaces as `FileNotFoundError` on macOS where the shared library
  is not built, and as `PASS` on Linux where HIPRT is present. The two states
  are caught in separate `except` branches, so a missing library can never be
  silently misclassified as a real failure.
- `PASS` (1 Linux): `ray_triangle_hit_count_3d` returns 2 rows with full
  tuple-level parity against the CPU Python reference.
- `FAIL` (0 on both): Zero FAILs is correct; no implemented workload is
  returning wrong results.

**Exit code**: `main()` returns 1 only when `summary["fail"] > 0`. NOT_IMPLEMENTED
and HIPRT_UNAVAILABLE do not trip CI, which is the right policy for a skeleton
phase.

**CPU reference baseline**: Every entry records `cpu_reference_row_count`,
giving future goals a concrete row-count target.

## Minor Notes (non-blocking)

- Parity is checked as `tuple(hiprt_rows) == tuple(cpu_rows)`: an exact ordered
  comparison. For workloads that return rows in non-deterministic order this
  would cause false FAILs. Acceptable now because only one workload currently
  reaches PASS and it is deterministic; revisit when more workloads land.
- Test file imports from `scripts.goal547_hiprt_correctness_matrix`, coupling it
  to the `PYTHONPATH=src:.` convention. This is fine given the project's
  existing runner commands.

## Conclusion

The harness satisfies its stated purpose: enumerate every v0.9 target, record
CPU-reference row counts, and honestly report where HIPRT stands today. All
NOT_IMPLEMENTED entries are correctly distinguished from real failures, and the
one available PASS is validated with row-level parity. No blocking issues found.
