# Goal5353 - X-HD Author RT Option Surface Gate

## Status

```text
implemented_review_pending
```

Exit label:

```text
author_rt_option_surface_gate_ready__next_target_semantic_mapping
```

## Purpose

Goal5352 showed that the RTDL X-HD wrapper accepts author variant names but does
not yet expose the author `rt` option surface. Goal5353 implements the first
user-facing gate for that surface.

This goal does **not** implement author RT-core semantics. It makes the wrapper
honest and explicit:

```text
omitted author RT defaults -> recorded for audit only
explicit author RT option  -> fail closed with JSON status
```

This is better than either argparse rejection or silent ignore, but it does not
claim author algorithm parity.

## Source Finding

Pinned author source defines these RT flags:

```text
fast_build_bvh = false
rebuild_bvh    = false
eb             = true
prune          = true
lb             = 256
n_points_cell  = 15
tune_grid      = false
tune_radius    = adaptive
```

`Radius` is not an author CLI flag at the pinned source. It is an
iteration/internal field and remains part of the radius-growth semantics gap.

## Implemented Changes

Modified:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Added:

```text
AUTHOR_RT_OPTION_SPECS
_author_rt_option_surface(...)
_raise_if_unsupported_author_rt_options(...)
_unsupported_author_rt_options_payload(...)
UnsupportedAuthorRtOptionsError
```

The parser now accepts author-style flags:

```text
-fast_build_bvh / --fast-build-bvh / --fast_build_bvh
-rebuild_bvh    / --rebuild-bvh    / --rebuild_bvh
-eb             / --eb
-prune          / --prune
-lb             / --lb
-n_points_cell  / --n-points-cell  / --n_points_cell
-tune_grid      / --tune-grid      / --tune_grid
-tune_radius    / --tune-radius    / --tune_radius
```

If any of these is explicitly supplied, the run stops before input loading and
writes a fail-closed JSON payload with:

```text
RTDL.status = unsupported_author_rt_options_fail_closed
HDResult = null
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5353_author_rt_option_surface_gate.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5353_author_rt_option_surface_gate.py
```

Regression test:

```text
tests/goal5353_xhd_author_rt_option_surface_gate_test.py
```

## Artifact Summary

The artifact records:

```text
default_surface.status = no_explicit_author_rt_options__author_defaults_recorded_only
explicit_surface.status = unsupported_explicit_author_rt_options
fail_closed_payload_status = unsupported_author_rt_options_fail_closed
radius_cli_flag_present = false
```

Explicit options exercised by the artifact:

```text
fast_build_bvh
rebuild_bvh
eb
prune
lb
n_points_cell
tune_grid
tune_radius
```

## Claim Boundary

Goal5353 does not claim:

```text
author RT option surface complete
author RT-core algorithm equivalence
performance parity
full X-HD paper reproduction
```

It only establishes a fail-closed surface for explicit author RT options.

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5353_author_rt_option_surface_gate.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5353_author_rt_option_surface_gate.json

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5353_author_rt_option_surface_gate.json

py -m unittest tests.goal5353_xhd_author_rt_option_surface_gate_test tests.goal5352_xhd_rt_core_feature_parity_matrix_test tests.goal5351_xhd_author_variant_semantics_audit_test tests.goal5349_xhd_hd_exec_variant_value_surface_test tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test
```

Result:

```text
Ran 24 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Interpretation

Goal5353 moves the X-HD app closer to author user-facing behavior by recognizing
the author RT option surface. It intentionally refuses to silently ignore those
options. The next real implementation work is semantic mapping:

```text
tune_radius -> generic radius schedule, or stay unsupported
lb/heavy offload -> generic worklist denominator, or stay unsupported
eb/prune -> exact scalar vs exact witness contract, or stay unsupported
```
