# Gemini Review: Goal3978-3981 Timing Contract Chain

Date: 2026-06-08
Verdict: `accept-with-boundary`

## Executive Summary

The Goal3978-3981 chain successfully hardens the timing contract for the current ten-app scale-profile packet. It moves the project from relying on subprocess wrapper "wall clock" time to a machine-readable "hot path" metric contract. The chain correctly identifies short-row variance, rejects naive repeat-count calibration, and implements a fail-closed validation mechanism in the scale-profile registry.

## Answers to Review Questions

### 1. Does Goal3978 correctly show repeatability for the current ten-app packet while identifying the short-row variance for robot collision and RayDB?

**Yes.** The repeatability probe in Goal3978 demonstrates that the toolchain and runner are highly stable for 8 out of 10 rows (relative range < 0.03%). It accurately identifies `robot_collision` (18.16% range) and `raydb_style` (11.51% range) as noisy due to their short absolute durations, correctly attributing this to benchmark scale rather than toolchain instability.

### 2. Does Goal3979 correctly reject blind repeat-count calibration for those rows and explain that wrapper/subprocess elapsed is not the hot-path metric?

**Yes.** Goal3979 provides empirical evidence that increasing the internal repeat count (up to 30x) for short rows does not significantly scale the hot-path traversal work. It correctly concludes that the multi-second wall time for these rows is dominated by the Python/subprocess setup envelope and rejects the idea of "blind" calibration.

### 3. Does Goal3980 correctly encode the wrapper-vs-hot-path boundary in the current scale-profile registry without changing app behavior or authorizing claims?

**Yes.** `src/rtdsl/current_benchmark_scale_profiles.py` was updated with a robust metadata contract. The `timing_metric_scope` is explicitly set to `wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric`. The validator and dataclass `__post_init__` enforce that all claim-authorization flags remain `False`, ensuring the project fails closed. No application logic was modified.

### 4. Does Goal3981 correctly replace the placeholder hot-path metric with concrete payload paths, including a composite RayJoin summary path?

**Yes.** Placeholder strings have been replaced with precise dotted-path accessors into the application JSON payloads (e.g., `run_phases.query_median_sec`). The `spatial_rayjoin` row correctly uses a composite object path (`representative_hot_path_summary`) to account for its multi-stage contract.

### 5. Are the tests sufficient to guard the timing contract and keep release, public-speedup, broad RT-core, whole-app acceleration, true-zero-copy, AMD, paper-reproduction, package-install, auto-selection, and app-specific native logic claims blocked?

**Yes.** The tests (specifically `tests/goal3980_current_scale_hot_path_metric_contract_test.py` and `tests/goal3981_current_scale_concrete_hot_path_metric_paths_test.py`) verify both the existence of the concrete metric paths in real artifacts and the strict "fail closed" state of the validator. Any attempt to flip a claim flag or use an unauthorized timing scope will trigger a validation failure.

### 6. What should be the next benchmark-quality step before any claim-grade timing packet?

The next step should be **scale-up calibration for the short rows**. Now that the registry can target specific hot-path metrics (e.g., `benchmark_timing_sec.tail_phase_traversal_sec`), the data size or batch counts for `robot_collision` and `raydb_style` should be increased until the *hot-path metric itself* reaches a stable, claim-grade duration (e.g., 10 seconds), effectively drowning out the subprocess setup noise.

## Boundary Conditions

This review accepts the internal hardening of the timing contract. It **does not authorize**:
- Release actions or package-install wording.
- Public speedup or whole-app acceleration claims.
- Broad RT-core or true-zero-copy claims.
- AMD performance or paper-reproduction wording.
- Automatic partner/backend selection or app-specific native-engine logic.

The "accept-with-boundary" verdict specifically acknowledges that while the contract is now technically sound, the *scales* for the short rows remain non-claim-grade until the next calibration step is completed.
