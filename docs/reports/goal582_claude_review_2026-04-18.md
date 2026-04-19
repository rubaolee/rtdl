# Goal582 External Review — Apple RT Full-Surface Compatibility Dispatch

Date: 2026-04-18

Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Findings

### Implementation correctness

`run_apple_rt` dispatch logic is correct end-to-end:

1. Always loads the Apple RT library first — compatibility-path calls still require `make build-apple-rt`, consistent with stated scope.
2. Rejects any predicate not in `APPLE_RT_COMPATIBILITY_PREDICATES` with `NotImplementedError`.
3. Routes `ray_triangle_closest_hit` with 3D types to the native MPS path via `ray_triangle_closest_hit_apple_rt`.
4. For all other predicates (and non-3D closest-hit), falls back to `_run_cpu_python_reference_from_normalized` — and raises `NotImplementedError` first if `native_only=True`.

The membership of `ray_triangle_closest_hit` in both `APPLE_RT_NATIVE_PREDICATES` and `APPLE_RT_COMPATIBILITY_PREDICATES` is intentional and harmless: `apple_rt_predicate_mode()` checks native first and returns `native_mps_rt` correctly; the support matrix (built from the compat set) then shows it as `native_mps_rt` for 18 total entries — all correct.

### Test coverage

- 18 kernels defined, 18 cases exercised in `test_all_current_predicates_are_callable_through_run_apple_rt`. Count matches predicate list.
- Correctness verified by parity with `run_cpu_python_reference` per kernel — a sound oracle strategy.
- `test_support_matrix_marks_native_and_compatibility_modes` asserts both mode labels and the count of 18.
- `test_native_only_rejects_compatibility_paths` correctly uses a 2D ray-hit-count input that cannot satisfy the 3D native branch, confirming the rejection fires.
- All tests gated with `@unittest.skipUnless(apple_rt_available(), ...)`, appropriate for hardware-dependent tests.

### Honesty boundary

`capability_boundaries.md` correctly states only `ray_triangle_closest_hit` is `native_mps_rt` and all others are `cpu_reference_compat`. No overclaim is present in the reviewed docs. The report's list of incorrect-post-582 statements (no full native parity, no measured speedup beyond closest-hit, no non-macOS support) is accurate and those claims do not appear in the code or docs.

### No blocking issues found

No logic errors, no false advertising, no missing predicate coverage, no unsafe dispatch paths.
