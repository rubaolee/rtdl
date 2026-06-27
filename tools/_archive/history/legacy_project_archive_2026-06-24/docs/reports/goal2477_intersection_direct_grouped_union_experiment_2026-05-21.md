# Goal2477: Default-Off Intersection-Direct Grouped-Union Experiment

Date: 2026-05-21

## Summary

Goal2477 adds a controlled OptiX experiment for the generic prepared fixed-radius grouped-union primitive. The experiment lets the intersection program apply the grouped-union side effect directly after the exact radius and existing culling checks, then return without calling `optixReportIntersection`. This removes the anyhit callback from the opt-in path.

The existing anyhit path remains the default and stable path. This change keeps no DBSCAN-native ABI, no DBSCAN vocabulary, and no app-specific engine semantics in the native engine.

## Motivation

Goal2476 showed that same-root culling was useful but did not remove the remaining traversal callback overhead:

- 32768 points, RTX A5000, same build: grouped native median improved from 0.0327394316 s to 0.0249137636 s.
- 65536 points, RTX A5000, same build: grouped native median improved from 0.0831496613 s to 0.0680980021 s.

Those results indicate that many candidate intersections still pay the anyhit-report path. A direct side-effect path is the next app-agnostic experiment because grouped union and fallback candidate updates are idempotent or monotonic atomic operations.

## Implemented Surface

- Native launch parameter: `direct_side_effect`.
- Native side-effect helper: generic fixed-radius grouped-union union/fallback update after exact-radius filtering.
- New C ABI symbols with execution options:
  - `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_execution_options`
  - `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options`
  - `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options`
  - `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_execution_options`
- Python runtime option: `direct_side_effect=False`.
- Partner adapter option: `grouped_union_direct_side_effect=False`.
- Benchmark flag: `--enable-grouped-union-direct-side-effect`.

## Safety Boundary

The experiment is default-off. It must not replace the anyhit default until pod A/B evidence and external review confirm correctness and performance.

The direct path is allowed to apply side effects only after:

- Predicate or all-items connectivity culling.
- Exact fixed-radius distance check.
- Optional same-root culling for parent-union candidates.

For predicated non-parent candidates, the direct path only updates the monotonic fallback candidate by `atomicMin`. For parent-union candidates, it uses the same monotonic union helper used by the anyhit path.

## Claim Boundary

This is an internal app-agnostic grouped-union experiment. Public performance claims remain blocked. Any future promotion requires:

- Same-build on/off pod artifacts.
- Signature equality against the existing default path.
- Focused OptiX runtime tests.
- External review and consensus.

## Pod Evidence

Environment:

- Pod SSH: `root@69.30.85.177 -p 22181 -i ~/.ssh/id_ed25519_rtdl_codex`
- Hostname: `ecdc0a16bb30`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- CUDA compiler: `Build cuda_12.8.r12.8/compiler.35583870_0`
- Source identity: synced dirty working tree; pod copy is not a git checkout.

Focused pod source tests:

```text
PYTHONPATH=src:. /root/rtdl_venv/bin/python -m unittest \
  tests.goal2477_intersection_direct_grouped_union_experiment_test \
  tests.goal2476_grouped_union_same_root_toggle_test \
  tests.goal2475_same_root_grouped_union_intersection_culling_test \
  tests.goal2474_predicate_aware_grouped_union_intersection_culling_test
19 tests OK
```

Tiny direct-side-effect runtime smoke:

- Mode: `optix_rt_core_grouped_stream_cupy_column_signature_3d`
- Dataset: `tiny`
- Direct side effect: enabled
- `matches_reference`: true
- Native symbol: `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options`

Same-build column-signature A/B artifacts:

- Default anyhit path: `docs/reports/goal2477_direct_side_effect_ab_off/summary.json`
- Direct side-effect path: `docs/reports/goal2477_direct_side_effect_ab_on/summary.json`
- 131k default anyhit scale probe: `docs/reports/goal2477_direct_side_effect_scale_131k_off/summary.json`
- 131k direct side-effect scale probe: `docs/reports/goal2477_direct_side_effect_scale_131k_on/summary.json`

Results:

| Point count | Total median off | Total median direct | Total speedup | Grouped native off | Grouped native direct | Native speedup | Signature status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 32768 | 0.0449019494 s | 0.0455493266 s | 0.986x | 0.0249677366 s | 0.0252259923 s | 0.990x | match |
| 65536 | 0.1091199862 s | 0.1088011730 s | 1.003x | 0.0691061830 s | 0.0679963250 s | 1.016x | match |
| 131072 | 0.3323279414 s | 0.3347260887 s | 0.993x | 0.2503216779 s | 0.2511681039 s | 0.997x | match |

Conclusion: the direct-side-effect path is correct on this pod smoke/A-B sample, but performance is mixed to negative. It is slightly slower at 32768 points, slightly faster at 65536 points, and slightly slower again at 131072 points. Keep the experiment default-off and do not promote it or use it for public performance wording.
