# Goal3546 - v2.9 v2.3 Same-Contract Repeat Adapter Audit

Status: internal prerequisite audit for the next pod timing packet.

## Purpose

Goal3542 made the current tree repeat-capable for the five Goal3536 partial rows. Goal3546 checks the harder prerequisite for a fair v2.3-vs-current timing packet: can the historical v2.3 evidence checkout expose the same measurement-only repeat protocol without changing v2.3 implementation semantics?

## Evidence

The Goal3536 final artifact identifies the historical v2.3 evidence commit as:

```text
2a28365d0246d51f3e3322b546f8a68c58632db4 Consolidate benchmark RT evidence and v2.4 roadmap
```

That commit is present locally. Static inspection shows:

- `scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py` does not exist in the v2.3 evidence commit.
- `hausdorff_optix_threshold` exists, but its app path uses the one-shot prepared helper rather than a repeatable prepared-handle loop.
- `spatial_rayjoin_optix_prepared_full_route` exists, but its prepared query path uses one-shot `_phase_time` calls.
- `barnes_hut_optix_node_coverage` exists, but its primary metric is still one-shot prepared node coverage.
- `librts_optix_aabb_index` exists, but its registry metric path is `elapsed_sec`, not resident query median time.
- `robot_collision_optix_prepared_device_buffers` already has a compatible `--repeats` control.

## Patch Probe

A direct patch from Goal3542 fails against the v2.3 evidence commit because it includes the current Goal3536 harness and later app-layer context:

```text
error: scripts/goal3536_v2_8_vs_v2_3_10s_steady_state.py: No such file or directory
error: examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py: patch does not apply
error: examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py: patch does not apply
```

A narrower measurement-only patch excluding the Goal3536 harness is much better:

```text
Applied patch to Barnes-Hut app cleanly.
Applied patch to Barnes-Hut benchmark wrapper cleanly.
Applied patch to Hausdorff app cleanly.
Applied patch to LibRTS app cleanly.
Applied patch to Goal2626 registry cleanly.
Applied patch to RayJoin app with conflicts.
```

The remaining conflict is RayJoin-specific. The v2.3 RayJoin app predates later count-mode, ordering-mode, and fallback route additions, so the current-tree patch tries to bring in unrelated app-layer options. The adapter must backport only the measurement protocol, not those later features.

## Required Adapter Work

Before the next authoritative pod timing run, create a disposable v2.3 measurement overlay from commit `2a28365d0246d51f3e3322b546f8a68c58632db4`:

1. Apply the narrow Goal3542 measurement patch to Hausdorff, Barnes-Hut, LibRTS, and `scripts/goal2626_benchmark_embree_optix_baseline.py`.
2. Manually resolve RayJoin by adding only:
   - `statistics` import;
   - `_phase_repeat_time`;
   - `query_repeat` / `warmup` validation and CLI args;
   - repeat wrapping around the existing prepared count/raw query calls;
   - stable row-count checks for repeated raw views.
3. Do not backport unrelated v2.6/v2.8 app-layer options such as Numba compact-mask planning, point/segment ordering modes, or newer PIP count modes.
4. Compile the overlay.
5. Run the current Goal3536 planner with `--v23-root` pointing to the v2.3 overlay and `--v28-root` pointing to current main.
6. Proceed to A5000 timing only if both lanes plan the five formerly partial rows as `internal_repeat_knob`.

## Boundary

This audit is not timing evidence. It does not authorize v2.9 release, public speedup claims, broad RT-core speedup claims, whole-app claims, true zero-copy claims, or paper reproduction claims.

The key design principle is same-contract measurement: the overlay may change timing methodology so the historical implementation can be measured repeatedly, but it must not change the historical v2.3 app/primitive semantics being measured.
