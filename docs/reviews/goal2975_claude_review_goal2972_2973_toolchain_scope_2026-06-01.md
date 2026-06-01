# Goal2975: Claude Review — Goal2972/2973 Comparison Toolchain Scope

Date: 2026-06-01
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **accept**

## Files Reviewed

- `docs/reports/goal2972_comparison_toolchain_scope_guard_2026-06-01.md`
- `docs/reports/goal2973_current_packet_with_comparison_toolchain_scope_2026-06-01.md`
- `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2972_comparison_toolchain_scope_guard_test.py`
- `tests/goal2973_current_packet_with_comparison_toolchain_scope_test.py`
- `docs/reports/goal2973_current_packet_with_toolchain_scope_pod/goal2855_summary.json`
- `docs/reports/goal2973_current_packet_with_toolchain_scope_pod/goal2973_triage.json`

## Q1: Goal2972 Scope Guard — Machine-Readable and Non-Overclaiming

The `_comparison_toolchain_scope()` function in the runner emits a fully
machine-readable dict under `runner_metadata.toolchain.comparison_toolchain_scope`
with `scope_version: "rtdl.goal2972.comparison_toolchain_scope.v1"`.

Required comparison shape is correctly specified: `same_source_commit_required:
true`, `same_gpu_required: true`, `same_packet_runner_required: true`.

Native OptiX stack observations are complete: `ptx_compiler: "nvcc"`,
`ptx_arch_recorded`, `nvcc_version_recorded`, `optix_header_exists`,
`rtdl_optix_library_exists`. Partner versions for Triton, Torch, CuPy, and
Numba are each recorded with a `_has_text()` boolean.

The `observed_stack_complete_for_current_packet` boolean gates on all four
partner versions plus native OptiX plus host compiler version — conservative and
correct.

The `known_non_equivalence` list is specific: nvcc/PTX AoT, Triton/LLVM JIT,
CuPy/NVRTC, Torch/ATen, Numba CUDA JIT. These are the exact axes where
different optimization choices could occur.

False-authorization flags are all present and set to `False`:
`compiler_flag_alignment_proven`, `cross_compiler_fairness_claim_authorized`,
`public_speedup_wording_authorized`, `paper_reproduction_claim_authorized`,
`release_authorized`.

The Goal2972 report accurately summarizes the change, explicitly states "This is
not a compiler fairness proof. It is a comparison-scope guard," and correctly
excludes second-architecture and multivendor claims.

**Finding: Goal2972 correctly adds a machine-readable scope guard without
claiming compiler fairness.**

## Q2: Goal2973 Packet Integrity

The pod summary (`goal2855_summary.json`) at commit
`63158f6db0a2248d203476633ea9f5171a0b596b` shows:

| Field | Value |
| --- | --- |
| `status` | `pass` |
| `all_pass` | `true` |
| `artifact_count` | `7` |
| `dirty_artifacts` | `{}` |
| `claim_boundary_violations` | `{}` |
| `source_dirty` (runner metadata) | `[]` |
| Source commit consistent | `true` |

All seven app artifacts (`goal2797`–`goal2803`) show `status: "pass"`,
`source_dirty: []`, and the same commit SHA. GPU identity is
`NVIDIA RTX A5000, 570.211.01` consistently.

The triage (`goal2973_triage.json`) shows:

| Field | Value |
| --- | --- |
| `status` | `pass` |
| `apps` | 10 rows |
| `performance_targets` | `[]` |
| `top_priority` | `null` |
| `claim_boundary_violations` | `{}` |

The `comparison_toolchain_scope` fields within the pod summary confirm
`native_optix_stack_observed: true`, `observed_stack_complete_for_current_packet:
true`, and all false-authorization flags are `false`.

**Finding: Goal2973 preserves 7/7 pass, empty dirty artifacts, empty
claim-boundary violations, zero performance targets, and `top_priority: null`.**

## Q3: Readiness Gate Fail-Closed Behavior

`validate_v2_5_internal_readiness_packet()` in `v2_5_internal_readiness.py`
now includes a complete set of identity checks against the scope guard:

- Verifies `scope_version == "rtdl.goal2972.comparison_toolchain_scope.v1"`;
  fails if missing (the `toolchain.get("comparison_toolchain_scope") or {}`
  expression returns `{}` for an absent key, and the version check then fails).
- Verifies `same_source_commit_required is True`, `same_gpu_required is True`,
  `same_packet_runner_required is True`.
- Verifies `native_optix_stack_observed is True`,
  `observed_stack_complete_for_current_packet is True`.
- Verifies `compiler_flag_alignment_proven is not False` triggers an error —
  meaning if this field were accidentally set to `True` or removed, the gate
  fails.
- Verifies `cross_compiler_fairness_claim_authorized is not False`,
  `public_speedup_wording_authorized is not False`,
  `release_authorized is not False` each trigger errors.

The use of strict identity (`is not True` / `is not False`) rather than
truthiness comparisons means no value coercion can silently pass a bad state.
The pre-existing `toolchain.get("claim_boundary", {})` checks for
`compiler_fairness_claim_authorized` and `multivendor_claim_authorized` remain
intact.

The readiness index now points to the Goal2973 pod artifacts:
`goal2973_current_packet_with_toolchain_scope_pod/goal2855_summary.json`
and `goal2973_triage.json`.

Test `test_readiness_index_points_to_goal2973_packet` confirms the full
validation chain returns `status: "accept"` with `errors: ()`.

**Finding: The gate fails closed on scope guard loss and on claim flag flips.**

## Q4: Boundary Honesty

The scope guard accurately characterizes this evidence as same-commit /
same-GPU / same-runner comparison with visible toolchains. It does not imply
compiler equivalence.

The `known_non_equivalence` list names the specific compilation axes that differ
across the native and partner paths, so a reader cannot mistake "stack visible"
for "flags identical."

The Goal2973 report explicitly states that the second-architecture and
multivendor performance check is not closed by this A5000 pod packet. That
residual gap is accurately preserved.

The blocked-action list in `v2_5_internal_readiness.py` includes
`public_speedup_wording`, `broad_rt_core_speedup_wording`,
`whole_app_speedup_wording`, `true_zero_copy_wording`, `package_install_wording`,
`triton_preview_auto_selection`, and `native_app_specific_engine_logic` — all
unchanged and correctly listed.

The `V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY` string retains all required phrases:
"internal readiness", "does not authorize release", "public speedup wording",
"broad RT-core wording", "whole-app speedup wording", "true zero-copy wording",
"package-install wording", "Triton preview auto-selection",
"app-specific native engine logic".

**Finding: The boundary is honest and covers all required out-of-scope items.**

## Q5: Claim, Release, and Partner-Choice Leaks

No leaks introduced:

- All seven artifact `claim_boundary_violations` are `{}`.
- The triage `claim_boundary_violations` is `{}`.
- The triage `claim_boundary` dict has `public_speedup_claim_authorized: false`,
  `release_authorized: false`, `whole_app_speedup_claim_authorized: false`,
  `true_zero_copy_claim_authorized: false`, `paper_reproduction_claim_authorized:
  false`.
- No app row in the triage exposes a public speedup or partner-choice
  authorization; `barnes_hut` records `selected_vector_sum_partner: "cupy"`
  as measured selection evidence, not a claim, and the boundary note
  "Triton vector path not promoted" is preserved.
- The new `allowed_next_actions` entries for Goal2972 and Goal2973 are
  `keep_goal2972_comparison_toolchain_scope_guard_green` and
  `keep_goal2973_current_packet_with_comparison_toolchain_scope_green` — both
  maintenance actions with no release or public-claim scope.

**Minor documentation inconsistency (non-blocking):** The triage JSON carries
`"goal": "Goal2902 v2.5 current packet performance triage"` — a label inherited
from the original triage template, not updated to `Goal2973`. This does not
affect gate logic; the readiness index identifies the triage by file path, not
by the `goal` label field. Worth correcting in a follow-up edit if the triage
is regenerated.

**Finding: No public-claim, release, app-specific-engine, or partner-choice
leaks are introduced.**

## Summary

| Question | Finding |
| --- | --- |
| Q1: Scope guard machine-readable, no compiler-fairness claim | Pass |
| Q2: Goal2973 packet 7/7, clean, zero targets, null priority | Pass |
| Q3: Gate fails closed on guard loss and claim flip | Pass |
| Q4: Boundary honest — same commit/GPU/runner, not compiler-equivalence proof | Pass |
| Q5: No public-claim or release leaks | Pass (one minor doc label note) |

## Verdict: accept

Goal2972 correctly adds a bounded, machine-readable comparison-toolchain scope
guard that is specific about what the evidence proves and what it does not.
Goal2973 confirms that the guard is present and correct in a clean 7/7 pod run
with zero performance targets. The readiness gate is fail-closed on all critical
fields. The second-architecture / multivendor gap is explicitly preserved.

This review does not authorize v2.5 release, public speedup wording, whole-app
speedup wording, broad RT-core wording, true zero-copy wording, package-install
wording, paper reproduction, Triton preview auto-selection, or app-specific
native engine customization.
