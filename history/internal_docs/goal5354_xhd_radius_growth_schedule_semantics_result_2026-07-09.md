# Goal5354 - Generic Radius-Growth Schedule Semantics

## Status

```text
implemented_review_pending
```

Exit label:

```text
radius_growth_schedule_helper_ready__next_target_route_trace_mapping
```

## Purpose

Goal5353 made explicit author RT options fail closed. Goal5354 starts mapping
one real semantic family: `tune_radius` / radius-growth.

This goal does not wire `tune_radius` into the X-HD route yet. It extracts the
radius update schedule into a generic RTDL helper and tests the edge cases that
are easy to get wrong. The author source is used as the semantic reference, but
the exported RTDL API is deliberately app-neutral.

## Author Rule Captured

Pinned author source:

```text
repository = https://github.com/pwrliang/X-HD.git
commit     = 7bf41c8442d059c94f4178355c6d5a10571d9658
file       = src/hd_impl/hausdorff_distance_rt.h
lines      = 398-419 in pinned checkout
```

Captured semantics:

```text
last_in_size = in_size
in_size = in_queue.size(stream)

if in_size > 0 and radius < hd_ub:
  adaptive:
    reduced_factor = (last_in_size - in_size) / last_in_size
    for expand_factor in [8,4,2,1]:
      if reduced_factor < 1 / expand_factor:
        radius += expand_factor * cell_diagonal
        break
  double:
    radius *= 2
  add:
    radius += cell_diagonal

  radius = min(radius, hd_ub)
```

Important correction: the adaptive condition is strict less-than. For example,
`reduced_factor == 1/8` does **not** choose `+8 * cell_diagonal`; it falls to
`+4 * cell_diagonal`.

## New Generic API

Added:

```text
src/rtdsl/radius_schedule.py
```

Exported from `rtdsl.__init__`:

```text
RadiusGrowthStep
radius_growth_step
radius_growth_trace
RADIUS_GROWTH_MODES
RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION
```

The helper is app-neutral:

```text
contract = rtdl.radius_growth_schedule.v1
app_semantics = none
core exported names contain no xhd / author token
```

It can be used for any bounded iterative search that expands a radius based on
unresolved item counts. A non-X-HD retry-radius consumer is included in tests.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5354_radius_growth_semantics.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5354_radius_growth_semantics.py
```

Regression test:

```text
tests/goal5354_radius_growth_schedule_test.py
```

## Current X-HD Mapping Status

```text
helper_semantics_available = true
route_uses_helper = false
run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed = true
```

This means Goal5354 is a semantic substrate, not route parity. The next step is
to decide how to wire the helper into the cell-MBR route and compare iteration
traces against author outputs.

## Claim Boundary

Goal5354 does not claim:

```text
author RT-core algorithm equivalence
author tune_radius route mapping
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

It also does not authorize silent acceptance of explicit author `-tune_radius`
flags in `run_xhd_rtdl_hd_exec.py`. Those flags remain fail-closed until a
later route behavior gate maps the schedule to observed author iteration traces.

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5354_radius_growth_semantics.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5354_radius_growth_semantics.json

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5354_radius_growth_semantics.json

py -m unittest tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test tests.goal5352_xhd_rt_core_feature_parity_matrix_test
```

Result:

```text
Ran 18 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Recommended next target:

```text
wire_tune_radius_to_cell_mbr_route_under_explicit_flag
```

But that should remain gated: explicit `-tune_radius` should stay fail-closed
until route trace mapping is verified against author behavior on a bounded or
Level-B input.
