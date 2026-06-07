# Gemini Review: Goals3822-3823 Current Benchmark Adequacy And Front-Door Registry

**Date:** 2026-06-07

**Reviewer:** Gemini

## Scope

Review current `main` after:

- `fe3ae8f2 Goal3822 refresh benchmark adequacy front doors`
- `456d9c0c Goal3823 add benchmark front-door registry`
- `56cdc3e0 Goal3823 add A5000 front-door registry artifact`

## Files Inspected

- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `src/rtdsl/current_benchmark_front_doors.py`
- `src/rtdsl/__init__.py`
- `scripts/goal3823_current_benchmark_front_door_runner.py`
- `docs/reports/goal3822_current_benchmark_adequacy_after_front_door_hardening_2026-06-07.md`
- `docs/reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md`
- `docs/reports/goal3823_current_benchmark_front_door_registry_a5000/summary.json`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md`
- `tests/goal3822_current_benchmark_adequacy_after_front_door_hardening_test.py`
- `tests/goal3823_current_benchmark_front_door_registry_test.py`
- `tests/goal3786_current_benchmark_adequacy_after_hiprt_closeout_test.py`
- `tests/goal3812_current_benchmark_docs_and_adequacy_aliases_test.py`

## Questions & Answers

### 1. Does Goal3822 correctly update the current benchmark adequacy source of truth after Goals3818-3820 without changing it into a release packet or performance leaderboard?

**Answer:** Yes. `src/rtdsl/v2_9_benchmark_adequacy.py` explicitly states that `V2_9_BENCHMARK_ADEQUACY_STATUS` is `"internal_perf_triage_not_release_authorization"` and the `V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY` disallows any release action, public speedup wording, whole-app acceleration, broad RT-core, RayJoin paper reproduction, true-zero-copy, automatic partner selection, AMD performance wording, or app-specific native-engine logic. This is further validated by `tests/goal3822_current_benchmark_adequacy_after_front_door_hardening_test.py` and reiterated in `docs/reports/goal3822_current_benchmark_adequacy_after_front_door_hardening_2026-06-07.md`.

### 2. Are the RTNN and triangle-counting adequacy rows now precise: RTNN points to the executable `prepared_optix_ranked_summary` app mode, and triangle counting points to explicit `--optix-graph-mode native` while preserving no RT-core triangle-count claim?

**Answer:** Yes.
*   **RTNN:** `src/rtdsl/v2_9_benchmark_adequacy.py` shows the `rtnn` app's `current_recommended_path` points to the `prepared_optix_ranked_summary` app mode. The `current_performance_reading` notes that "Goal3820 adds an executable prepared OptiX ranked-summary app mode" and clarifies it's "not an RTNN paper-reproduction claim". This is confirmed by `tests/goal3822_current_benchmark_adequacy_after_front_door_hardening_test.py`.
*   **Triangle-counting:** The `triangle_counting` app's `current_recommended_path` in `src/rtdsl/v2_9_benchmark_adequacy.py` specifies explicit `--optix-graph-mode native`. The `current_performance_reading` attributes this to Goal3819 and explicitly states "no RT-core triangle-count claim". The relevant test also verifies that `broad_rt_core_claim_authorized` remains false.

### 3. Does Goal3823 provide a single current command registry and bounded runner for all ten promoted benchmark app front doors?

**Answer:** Yes. `src/rtdsl/current_benchmark_front_doors.py` defines `CURRENT_BENCHMARK_FRONT_DOORS`, which includes all ten promoted benchmark apps. The `scripts/goal3823_current_benchmark_front_door_runner.py` serves as the bounded runner, executing these registered commands. `tests/goal3823_current_benchmark_front_door_registry_test.py` confirms that the registry covers all ten apps with unique `row_id` values.

### 4. Does the A5000 artifact fairly record all ten registered rows passing, and is it scoped as command-front-door evidence rather than public speedup evidence?

**Answer:** Yes. `docs/reports/goal3823_current_benchmark_front_door_registry_a5000/summary.json` shows `"all_pass": true` for all ten rows. Both the JSON artifact and `docs/reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md` clearly state the `claim_boundary` indicates it "does not authorize release action, package-install wording, public speedup wording..." and that it is "command-front-door evidence, not a performance leaderboard."

### 5. Does the runner avoid hidden partner selection and app-specific native-engine logic?

**Answer:** Yes. The `scripts/goal3823_current_benchmark_front_door_runner.py` executes commands explicitly defined in `src/rtdsl/current_benchmark_front_doors.py` without implicit partner selection. The `CurrentBenchmarkFrontDoor` dataclass explicitly sets `automatic_partner_selection_authorized` and `app_specific_native_engine_logic_allowed` to `False`. Documentation like `docs/learn/partner_choice_for_custom_logic.md` emphasizes explicit partner choice and explicitly states "RTDL is not an automatic optimizer for arbitrary partner code."

### 6. Do all touched files preserve claim boundaries: no release, package-install, public speedup, whole-app acceleration, broad RT-core, paper-reproduction, true-zero-copy, AMD performance, automatic partner selection, or app-specific native-engine claims?

**Answer:** Yes. All relevant files, including `src/rtdsl/v2_9_benchmark_adequacy.py`, `src/rtdsl/current_benchmark_front_doors.py`, the various `docs/reports` files, and the `docs/learn` documents, consistently define and enforce claim boundaries that explicitly disallow all the listed claims. Unit tests like `tests/goal3822_current_benchmark_adequacy_after_front_door_hardening_test.py` and `tests/goal3823_current_benchmark_front_door_registry_test.py` contain explicit assertions to confirm that these authorization flags remain `False`.

## Verdict

accept
