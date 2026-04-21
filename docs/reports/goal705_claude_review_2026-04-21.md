# Goal705 OptiX App Benchmark Readiness — Claude Review

Date: 2026-04-21  
Reviewer: Claude Sonnet 4.6  
Verdict: **ACCEPT**

## Summary

The gate is conservative and structurally sound. No app is marked
`ready_for_rtx_claim_review`. The three closest candidates
(`robot_collision_screening`, `outlier_detection`, `dbscan_clustering`) are
correctly blocked behind `needs_phase_contract` or `needs_postprocess_split`.
All CUDA-through-OptiX apps (`hausdorff_distance`, `ann_candidate_search`,
`barnes_hut_force_app`) are correctly excluded from RT-core claims. The four
findings below are honesty boundary gaps — none causes a permissive
classification today, but each is a latent risk for silent drift.

## Findings

### F1: `segment_polygon_anyhit_rows` — performance class contradicts blocker text

- Performance class: `host_indexed_fallback`
- Readiness: `needs_interface_tuning`
- Blocker text: "pair-row output volume can dominate timing **even when native
  traversal exists**"

`host_indexed_fallback` implies native traversal is not yet available; the
blocker implies it is. If native traversal is already an option for this app,
the performance class should be `python_interface_dominated` (rows dominate
even when native traversal runs), which would also align it with the
`needs_interface_tuning` readiness status. As written, a reader who trusts the
performance class concludes native traversal does not exist; a reader who trusts
the blocker concludes it does. The two claims cannot both be accurate.

Recommended fix: if native traversal is reachable for this app today, change the
performance class to `python_interface_dominated` and update the note
accordingly. If it is not yet reachable, remove "even when native traversal
exists" from the blocker and change the readiness to `needs_native_kernel_tuning`
(consistent with the other two host-indexed segment/polygon apps).

### F2: `outlier_detection` — `cuda_through_optix` + `needs_phase_contract` combination lacks structural enforcement

- Performance class: `cuda_through_optix`
- Readiness: `needs_phase_contract`

`needs_phase_contract` is defined as "a credible RTX candidate." The rationale
for pairing it with `cuda_through_optix` is that the optional `rt_count_threshold`
sub-path uses real OptiX traversal. This is valid, but nothing in the taxonomy
or test suite enforces that a `cuda_through_optix` app may only receive
`needs_phase_contract` if a documented traversal sub-path exists. A future
maintainer could silently promote any `cuda_through_optix` app to
`needs_phase_contract` without triggering a test failure.

Recommended fix (low priority, can live in Goal710): add a test that explicitly
enumerates every `cuda_through_optix` app that holds a non-exclude readiness
status and documents the justification for each exception.

### F3: Goal705 API symbols absent from `__all__`

The `__init__.py` imports `OPTIX_APP_BENCHMARK_READINESS_STATUSES`,
`optix_app_benchmark_readiness`, and `optix_app_benchmark_readiness_matrix` at
module level but does not list them in `__all__`. The tests pass because Python
attribute access does not require `__all__` membership. However, the Goal705
report explicitly lists these as the machine-readable public API. The `__all__`
omission means `from rtdsl import *` does not export them, and static analysis
tools may not surface them as public.

Recommended fix: add the three symbols to `__all__` alongside the existing
`OPTIX_APP_PERFORMANCE_CLASSES`, `optix_app_performance_matrix`, and
`optix_app_performance_support` entries.

### F4: No test cross-checks performance class against readiness status

The test suite exhaustively verifies readiness statuses and checks that the
public doc contains required phrases, but no test verifies the OptiX performance
class values. Specifically:

- No test confirms `robot_collision_screening` is the only `optix_traversal`
  app. A future incorrect reclassification would go undetected.
- No test confirms `outlier_detection` and `dbscan_clustering` remain
  `cuda_through_optix`. If either were changed to `optix_traversal` without a
  corresponding phase-contract cleanup, no test would catch it.

Recommended fix: add a test in the Goal705 suite that pins the performance class
of all 18 apps, similar to how `test_closest_candidates_are_still_gated_by_phase_or_postprocess_contracts`
pins readiness statuses.

## Coverage Verification

| Check | Result |
| --- | --- |
| All 18 public apps have a benchmark readiness row | Pass |
| No app is `ready_for_rtx_claim_review` | Pass |
| Closest candidates are `needs_phase_contract` / `needs_postprocess_split` | Pass |
| CUDA-through-OptiX apps are `exclude_from_rtx_app_benchmark` | Pass (hausdorff, ann, barnes_hut) |
| Host-indexed fallback apps are not promoted to benchmark candidates | Pass |
| `outlier_detection` rt_count_threshold traversal sub-path is scoped correctly | Pass (allowed claim is phase-contract scoped) |
| `dbscan_clustering` core-flag claim is scoped to summary only | Pass |
| Public doc records cloud benchmark policy | Pass |
| Goal report records Goal706–712 follow-up sequence | Pass |
| Goal705 API symbols are importable at module level | Pass (but see F3 re `__all__`) |

## Recommendation

Accept Goal705 as-is. F1 is the highest-priority finding and should be resolved
during Goal708 (segment/polygon native/compact-path tuning) when the actual
native traversal availability for `segment_polygon_anyhit_rows` is confirmed. F3
(`__all__` gap) is a one-line fix that can be included in any nearby PR. F2 and
F4 are low-risk and can be addressed within Goal710–712 when those apps complete
their phase contracts.

Do not advance any app to `ready_for_rtx_claim_review` until its respective
follow-up goal closes. Do not rent a paid RTX cloud instance for broad app
benchmarking until that policy condition is met.
