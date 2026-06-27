# Goal3911 External Review: Goal3909/3910 RayJoin Subprobe Timing and Reuse

Date: 2026-06-08

Reviewer: Gemini 2.5 Flash via Gemini CLI, independent external review distinct from Codex.

## Review Questions and Answers

### 1. Does Goal3909 expose useful, machine-checkable nested timing without changing benchmark semantics?

**Answer:** Yes, Goal3909 successfully exposes useful, machine-checkable nested timing without altering benchmark semantics.

The `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` script has been updated to include detailed phase timings within the `wrapper_phase_timing_sec` field of its JSON output. These timings include `numba_load_case_sec`, `numba_prepare_sec`, `numba_hot_total_sec`, `cupy_prepare_sec`, `cupy_hot_total_sec`, `rtdl_optix_prepare_total_sec`, `rtdl_optix_hot_total_sec`, and `case_total_sec`. The `_time_numba_count` function incorporates stability checks to ensure consistent counts across repeated runs, which is crucial for machine-checkability.

The `docs/reports/goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_2026-06-08.md` explicitly clarifies that this change is "instrumentation only" and "does not change native RTDL, OptiX kernels, partner kernels, RayJoin semantics, dispatch policy, or public speedup claims." Furthermore, the `tests/goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_test.py` directly validates the correctness of this new timing contract using mocked backends, confirming its machine-checkability.

### 2. Does Goal3910 keep the engine app-agnostic by limiting shared loaded-case reuse to Python/app benchmark orchestration?

**Answer:** Yes, Goal3910 effectively maintains engine app-agnosticism by confining shared loaded-case reuse to Python/app benchmark orchestration.

The modifications in `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` introduce `run_numba_baseline_loaded_case` and `run_rtdl_optix_loaded_case` functions that accept a pre-loaded case object. The `run_probe` function orchestrates this by invoking `_load_rayjoin_case` once per case and then passing this `loaded_case` to both the Numba and RTDL/OptiX benchmark functions. This clearly indicates that the reuse occurs within the Python benchmark script itself, not within the native engine. The RTDL/OptiX payload also now includes `loaded_case_reuse_enabled: True` and route names suffixed with `_loaded_case_reuse`, reinforcing that this is a benchmark-level change.

The `docs/reports/goal3910_rayjoin_lsi_overlay_shared_loaded_case_reuse_2026-06-08.md` explicitly states: "This is not a native-engine change. It does not add RayJoin-specific engine logic, automatic dispatch, or new public speedup claims. It is an app/benchmark orchestration cleanup over existing generic prepared RTDL/OptiX primitives and existing Numba same-contract baselines." The `tests/goal3910_rayjoin_lsi_overlay_shared_case_reuse_test.py` further validates this approach by asserting that `_load_rayjoin_case` is called only once per case by `run_probe` and that the loaded case is then shared.

### 3. Does the loaded-case path preserve same-contract count validation between Numba and RTDL/OptiX?

**Answer:** Yes, the loaded-case path explicitly preserves same-contract count validation between Numba and RTDL/OptiX.

The `run_probe` function in `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` includes explicit `RuntimeError` checks. These checks compare the `row_count` obtained from `run_numba_baseline_loaded_case` against those from `cupy_row` and `rtdl_optix` (which are derived from `run_cupy_baseline` and `run_rtdl_optix_loaded_case` respectively). If any of these counts do not match, a `RuntimeError` is raised. The `counts_match` field in the final reported summary further confirms that this validation is an integral part of the benchmark output. The unit tests for Goal3909 and Goal3910 also utilize mocked backends that return consistent counts, with assertions verifying the `counts_match` outcome.

### 4. Are the payload/report boundaries honest, especially no release, whole-app speedup, RayJoin reproduction, broad RT-core, or true-zero-copy claim?

**Answer:** Yes, the payload and report boundaries are consistently honest and conservative, explicitly disclaiming unauthorized claims.

All relevant scripts and reports rigorously adhere to a strict boundary policy. The `_claim_boundary()` function, integrated into `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py`, and other contextual scripts like `scripts/goal3866_rayjoin_representative_scale_profile.py`, consistently return `release_authorized: False` and similar restricted claims. The `boundary` field in the `run_probe` output for `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py` clearly states: "This is a RayJoin LSI/overlay partner-coverage probe... It is not automatic dispatch, not a RayJoin paper reproduction, and not release evidence." This restrictive language is echoed in `docs/reports/goal3909_rayjoin_lsi_overlay_subprobe_phase_timing_2026-06-08.md`, `docs/reports/goal3910_rayjoin_lsi_overlay_shared_loaded_case_reuse_2026-06-08.md`, and `docs/reports/goal3908_rayjoin_wrapper_phase_timing_a5000_2026-06-08.md`. These consistent disclaimers ensure that no unauthorized claims regarding release, whole-app speedup, RayJoin reproduction, broad RT-core usage, or true-zero-copy are made.

### 5. Are there any correctness, lifecycle, resource-close, or artifact-shape risks before the next A5000 pod timing run?

**Answer:** There are minimal apparent correctness, lifecycle, resource-close, or artifact-shape risks.

*   **Correctness:** The new unit tests (`goal3909_..._test.py` and `goal3910_..._test.py`) specifically validate the timing capture and loaded-case reuse mechanisms through mocked backends. The `run_probe` function's robust count validation (`RuntimeError` on mismatch) further reduces correctness risks for integrated runs.
*   **Lifecycle/Resource-close:** The `run_rtdl_optix_loaded_case` function demonstrates proper resource management for OptiX objects by utilizing `with` statements and `packed_left.close()` within a `try...finally` block. For Python objects like `SimpleNamespace` used for loaded cases, standard Python garbage collection handles their lifecycle effectively.
*   **Artifact-shape:** The changes are additive and well-structured. Goal3909 introduces new timing fields within the existing `wrapper_phase_timing_sec` dictionary. Goal3910 adds clear boolean flags (e.g., `shared_loaded_case_reuse_enabled`) and descriptive suffixes to route labels. These additions are consistent with an evolving `v1` schema and are validated by unit tests, ensuring the overall artifact shape remains predictable and parsable.

The primary residual risk is inherent to mocked testing: it may not capture every subtle interaction bug that could arise in a full backend execution environment with specific hardware and driver versions. However, this is a general limitation and not indicative of specific flaws in the implemented changes. The overall implementation appears robust for its intended purpose.

## Verdict

**Verdict:** `accept`

## Tests Run

No tests were run as part of this read-only external review.
