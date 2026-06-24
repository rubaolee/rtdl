# Goal3547 - v2.3 Measurement Overlay Repeat Hooks

Status: internal measurement infrastructure; not timing evidence.

## Purpose

Goal3547 converts the Goal3546 prerequisite audit into an executable overlay patch for the historical v2.3 evidence checkout. The patch adds the same measurement-only repeat protocol needed by Goal3542 while preserving the historical v2.3 implementation semantics.

Patch artifact:

`docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch`

Base commit:

`2a28365d0246d51f3e3322b546f8a68c58632db4`

## What The Overlay Does

The overlay updates only benchmark/app measurement surfaces:

- Hausdorff threshold path repeats prepared threshold queries after one-time scene preparation.
- Barnes-Hut node coverage repeats prepared node/body threshold queries after one-time scene preparation.
- LibRTS AABB index reports resident query median/summed-median timing instead of total wall time.
- RayJoin prepared OptiX route repeats the existing v2.3 prepared query calls and validates stable row counts for raw-view repeats.
- Goal2626 registry commands expose `--repeat`/`--warmup` and use resident query metrics where needed.

The overlay deliberately does not backport later app features such as Numba compact-mask planning, point/segment ordering modes, newer PIP count modes, or v2.8/v2.9 primitive changes.

## Local Validation

A disposable overlay worktree was created at:

`C:\Users\Lestat\Desktop\work\rtdl_goal3547_v23_overlay`

Validation performed:

```text
git apply --check docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch
```

This apply check passed on a fresh disposable worktree at commit `2a28365d0246d51f3e3322b546f8a68c58632db4`.

```text
py -3 -m py_compile \
  examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py \
  examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py \
  examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
  scripts/goal2626_benchmark_embree_optix_baseline.py
```

The current Goal3536 dry planner was then run with:

```text
--v23-root C:\Users\Lestat\Desktop\work\rtdl_goal3547_v23_overlay
--v28-root C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
--seed-artifact docs\reports\goal3536_v2_8_vs_v2_3_10s_steady_state_a5000\summary_final.json
```

Result: all five formerly partial rows plan as `internal_repeat_knob` for both `v23` and `v28` lanes:

```text
hausdorff_optix_threshold: internal_repeat_knob / internal_repeat_knob
spatial_rayjoin_optix_prepared_full_route: internal_repeat_knob / internal_repeat_knob
robot_collision_optix_prepared_device_buffers: internal_repeat_knob / internal_repeat_knob
barnes_hut_optix_node_coverage: internal_repeat_knob / internal_repeat_knob
librts_optix_aabb_index: internal_repeat_knob / internal_repeat_knob
```

## Boundary

This goal is still not pod timing evidence. It only supplies the historical-lane measurement overlay needed for a fair 10-second steady-state rerun.

The overlay may change how v2.3 timing is measured, but it must not be used to claim v2.3 had these measurement controls originally. It also must not be described as a v2.3 feature change. It is a measurement adapter.

No release, public speedup, whole-app speedup, broad RT-core speedup, true-zero-copy, or paper-reproduction claim is authorized.
