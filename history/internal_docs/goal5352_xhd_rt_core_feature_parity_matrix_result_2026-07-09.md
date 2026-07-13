# Goal5352 - X-HD RT-Core Feature Parity Matrix

## Status

```text
implemented_review_pending
```

Exit label:

```text
rt_core_feature_parity_matrix_ready__next_target_author_rt_option_surface
```

## Purpose

Goal5351 established that accepting author variant names is only value-surface
compatibility. Goal5352 moves one level deeper: it turns the author `rt` / X-HD
implementation semantics into a concrete same-functionality gap matrix.

This is not a new route and not a performance claim. It is a target-selection
artifact for the remaining work needed before RTDL can plausibly claim the same
functionality as the author C++/CUDA/OptiX implementation.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5352_rt_core_feature_parity_matrix.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5352_rt_core_parity_matrix.py
```

Regression test:

```text
tests/goal5352_xhd_rt_core_feature_parity_matrix_test.py
```

## Evidence Inputs

The matrix reads and cross-references these existing artifacts:

```text
Goal5351 author variant semantics audit
Goal5350 functional parity matrix amendment
Goal5282 author offload mapping
Goal5284 Figure 9 auto-tune semantics matrix
Goal5292 Figure 7 load-balance audit
Goal5288 Figure 5 timing denominator audit
run_xhd_rtdl_hd_exec.py wrapper surface
```

## Main Finding

The current RTDL X-HD app has a strong directed-HD value route and a reviewed
Level-B representative line, but it does not yet reproduce author `rt` core
functionality.

The matrix keeps:

```text
author_rt_core_algorithm_parity_ready = false
full_xhd_paper_reproduction_ready = false
closed_features = []
```

Every listed author RT-core feature remains either partial or not reproduced.

## Feature Gaps

The matrix lists these blocking feature groups:

```text
rt_variant_value_surface
author_rt_option_surface
uniform_grid_and_cell_mbr_target_structure
radius_growth_and_tune_radius
early_break_prune_scalar_contract
load_balance_and_heavy_cell_offload
figure11_memory_fields
figure5_author_variant_performance_matrix
exact_paper_input_identity
```

The most immediate concrete gap is the author RT option surface:

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

`run_xhd_rtdl_hd_exec.py` currently accepts author variant names and RTDL route
controls, but it does not expose those author RT options. `Radius` remains an
author iteration/internal output field and radius-growth semantics remain a
separate algorithm target; it is not an author CLI option at the pinned source.
That means an author `hd_exec -variant rt ...` command using the RT flags above
is not yet functionally equivalent on the RTDL side.

## Recommended Next Targets

The artifact recommends:

1. `author_rt_option_surface_gate`
2. `radius_growth_and_tune_radius_semantics`
3. `load_balance_heavy_offload_denominator_gate`

This intentionally moves the work away from variant-name plumbing and toward
the author X-HD algorithm surface.

## Claim Boundary

Goal5352 does not claim:

```text
author_rt_core_algorithm_parity
author_rt_option_surface_complete
Figure 5 reproduction
Figure 7 reproduction
Figure 8 reproduction
Figure 9 reproduction
Figure 11 reproduction
full X-HD paper reproduction
performance ratio
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5352_rt_core_parity_matrix.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5352_rt_core_feature_parity_matrix.json

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5352_rt_core_feature_parity_matrix.json

py -m unittest tests.goal5352_xhd_rt_core_feature_parity_matrix_test tests.goal5351_xhd_author_variant_semantics_audit_test tests.goal5350_xhd_functional_parity_matrix_amendment_test
```

Result:

```text
Ran 14 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Interpretation

Goal5352 answers the question: after accepting author variant names, what is
still missing for the main author `rt` / X-HD algorithm?

Answer: most RT-core functionality remains unclosed. The next implementable
step is not another value-surface wrapper. It is an app-owned author RT option
surface gate that classifies each author RT option as implemented, mapped to a
generic RTDL control with evidence, or fail-closed unsupported.
