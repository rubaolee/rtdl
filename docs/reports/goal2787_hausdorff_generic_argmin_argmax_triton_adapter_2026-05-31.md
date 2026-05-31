# Goal2787 - Hausdorff Generic Argmin/Argmax Triton Adapter

Date: 2026-05-31

## Purpose

Goal2787 wires the existing Hausdorff partner wrapper through generic v2.5
continuation primitives instead of leaving it as only a Torch/CuPy dense
min/max implementation.

The core reusable adapter is:

`group_argmin_then_global_argmax_partner_columns(...)`

It computes a generic pattern:

1. per-group lowest score with lowest-item-id tie break;
2. global highest per-group score with lowest-group-id tie break;
3. winner group/item/score witness metadata.

This is the generic witness-reduction shape needed by directed Hausdorff, but
the primitive does not contain Hausdorff, X-HD, geometry, or app vocabulary.

## What Changed

Updated:

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/adapters/reductions.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`

Added:

- `group_argmin_then_global_argmax_partner_columns(...)`
- Triton route for `directed_hausdorff_2d_partner_columns(...)`
- Goal2787 CUDA correctness tests

The Triton route composes:

- `grouped_argmin_f64`
- `grouped_argmax_f64`

The native engine and Triton continuation files remain app-name-free; the
Hausdorff wrapper is Python-side app/recipe logic over generic continuation
contracts.

## Pod Timing

Pod artifact:

`docs/reports/goal2787_pod_artifacts/goal2787_hausdorff_generic_argmin_argmax_pod_69_30_85_171_2026-05-31.json`

Host:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
```

| Source points | Target points | Pairs | Torch sec | Triton sec | Triton / Torch | Correctness |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 128 | 16,384 | 0.000255 | 0.010252 | 40.241x | pass |
| 512 | 512 | 262,144 | 0.000263 | 0.011862 | 45.145x | pass |
| 1,024 | 1,024 | 1,048,576 | 0.000375 | 0.011955 | 31.880x | pass |

The generic Triton route is correct but not competitive for dense exact
Hausdorff-style reductions. The two-kernel argmin+argmax preview is slower than
the dense Torch same-contract branch on all measured shapes.

## Guidance Refresh

Goal2787 adds a measured negative guidance row for:

- operation: `grouped_argmin_f64`
- workload shape: `dense_exact_hausdorff_argmin_argmax`
- evidence: Goal2787 pod artifact

The v2.5 app migration plan now records Hausdorff/X-HD as wired but blocked
from automatic Triton selection for this dense exact witness-reduction shape.
The recommended performance path remains an explicitly selected same-contract
partner such as optimized Torch/CuPy/CUDA until a fused/tiled generic Triton
witness-reduction design wins timing.

## Boundary

This goal authorizes:

- a generic argmin-then-argmax witness adapter;
- a Hausdorff Python wrapper route through that generic adapter;
- measured negative guidance for dense exact Hausdorff-style reductions.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- Hausdorff-specific native or Triton primitive code;
- auto-selecting Triton for dense exact Hausdorff-style witness reduction.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2787_hausdorff_generic_argmin_argmax_triton_adapter_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test

Ran 28 tests in 0.050s
OK (skipped=4)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2787_final2
OK
```

Pod validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2787_hausdorff_generic_argmin_argmax_triton_adapter_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test

Ran 28 tests in 2.371s
OK
```

## Decision

`accept-with-boundary`

Goal2787 is accepted as a correctness and wiring step for v2.5 generic
witness-reduction composition. It is also accepted as negative performance
evidence: the current generic Triton two-kernel route is not the selected dense
Hausdorff performance path.
