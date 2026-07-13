# Goal5206 Frontier First-Use vs Warm Diagnostic Result

Date: 2026-07-08

## Verdict

```text
completed_frontier_first_use_vs_warm_diagnostic__fresh_headline_unchanged
```

## Purpose

After Goal5205, the strongest current full-public Dragon -> HappyBuddha Level-B
one-shot route was:

```text
load_full_inputs ~= 0.68s
route_wall       ~= 1.16-1.17s
total            ~= 2.06s
```

The remaining route-local floor was dominated by:

```text
frontier_rows / native inline-nearest ~= 0.74s
initial_state_seed                   ~= 0.23s
grid_cell_mbrs                       ~= 0.10s
```

Goal5206 does not implement a new optimization. It decomposes whether the
remaining frontier/seed floor is steady computation or first-use runtime cost.
This prevents the next goal from chasing a misleading denominator.

## Evidence

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_current_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_all_then_minus1_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_frontier_phase_minus1_then_all_goal5205_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5206_numba_serial_seed_one_shot_control_graphics_dragon_happy_buddha_2026-07-08.json
```

All successful diagnostic artifacts:

```text
matched = true
author_abs_diff ~= 2.3849e-9
```

## Current Single-Case Phase Timing

Current one-shot all-source run with native frontier phase timings:

```text
load_full_inputs ~= 0.680s
route_wall       ~= 1.169s
frontier_rows    ~= 0.740s
initial_seed     ~= 0.234s
grid_cell_mbrs   ~= 0.099s
```

Native frontier timing:

```text
total_native_sec        ~= 0.600s
optix_launch_sec        ~= 0.379s
query_pack_sec          ~= 0.016s
device_alloc_upload_sec ~= 0.005s
accel_build_sec         ~= 0.0004s
nearest_download_sec    ~= 0.0006s
```

This confirms the Goal5205 route floor: the native frontier phase is real, and
prepared cell-MBR acceleration build is not material.

## Same-Process Warm Diagnostic

The full-public script rejects duplicate `all,all` source limits. Therefore the
diagnostic used near-identical two-case sequences:

```text
all,437644
437644,all
```

The second case differs by at most one source point, so phase movement is a
runtime warmup signal rather than a data-size effect.

### all -> 437644

First case (`all`):

```text
route_wall       ~= 1.170s
frontier_rows    ~= 0.745s
initial_seed     ~= 0.231s
native_total     ~= 0.604s
optix_launch     ~= 0.382s
```

Second case (`437644`):

```text
route_wall       ~= 0.613s
frontier_rows    ~= 0.403s
initial_seed     ~= 0.029s
native_total     ~= 0.394s
optix_launch     ~= 0.371s
```

### 437644 -> all

First case (`437644`):

```text
route_wall       ~= 1.174s
frontier_rows    ~= 0.746s
initial_seed     ~= 0.234s
native_total     ~= 0.603s
optix_launch     ~= 0.382s
```

Second case (`all`):

```text
route_wall       ~= 0.611s
frontier_rows    ~= 0.403s
initial_seed     ~= 0.024s
native_total     ~= 0.393s
optix_launch     ~= 0.371s
```

## Interpretation

The same full `all` route is about:

```text
one-shot route_wall ~= 1.16-1.17s
same-process warm route_wall ~= 0.61s
```

The difference is not driven by source count. It comes mainly from:

```text
initial_state_seed first-use ~= 0.23s -> warm ~= 0.02-0.03s
native total first-use      ~= 0.60s -> warm ~= 0.39s
```

The OptiX launch / inline scan itself remains about:

```text
optix_launch ~= 0.37-0.38s
```

Therefore:

- a large part of the one-shot route wall is first-use runtime overhead;
- the steady native inline-nearest scan is still a real `~0.37s` floor;
- warm-route numbers must not replace one-shot numbers without explicit regime
  labeling.

## Seed Executor Control

An explicit `--local-grid-seed-executor numba` one-shot control did not improve
the route:

```text
matched = true
route_wall ~= 1.171s
initial_state_seed ~= 0.228s
```

The route metadata still reports the effective executor as `numba_parallel`.
There is no evidence here to replace the current default executor.

## Claim Boundary

Goal5206 claims:

- a first-use vs same-process warm decomposition for the current Level-B route;
- the fresh one-shot headline remains the Goal5205 route (`~1.16-1.17s`, total
  `~2.06s`);
- same-process warm route can reach about `~0.61s` on this POD and workload, but
  only as a labeled diagnostic regime.

Goal5206 does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- a new RTDL optimization;
- permission to report warm numbers as the one-shot result.

## Next

The next real optimization choices are:

1. build an explicit generic prepared/warm runtime API and report both
   preparation cost and warm route cost; or
2. attack the steady native inline-nearest scan (`optix_launch ~=0.37s`) through
   a stronger generic spatial execution model / work ordering.

Do not spend the next goal on:

- PLY tuple parsing;
- max-nearest full lexsort;
- prepared cell-MBR accel-build caching;
- swapping seed executor flags without a new executor implementation.
