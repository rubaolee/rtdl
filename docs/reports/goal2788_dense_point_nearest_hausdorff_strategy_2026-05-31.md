# Goal2788 - Dense Point-Nearest Hausdorff Triton Strategy

Date: 2026-05-31

## Purpose

Goal2787 proved that directed Hausdorff can be wired through generic
`grouped_argmin_f64` plus `grouped_argmax_f64`, but the dense score-row route
was much slower than Torch. Goal2788 tests the next design idea: avoid dense
score-row materialization by using a fused dense point-nearest adapter kernel,
then apply the existing generic grouped argmax for the final directed
Hausdorff witness.

The new route is explicit:

```python
directed_hausdorff_2d_partner_columns(
    source,
    target,
    partner="triton",
    triton_strategy="dense_point_nearest",
)
```

The default Triton strategy remains `generic_score_rows` so Goal2787's reviewed
route stays reproducible. Goal2788 adds a separate, opt-in strategy.

## What Changed

Updated:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`

Added:

- `run_triton_dense_point_nearest_2d(...)`
- `dense_point_nearest_2d_adapter_kernel`
- `triton_strategy="dense_point_nearest"` for
  `directed_hausdorff_2d_partner_columns(...)`
- Goal2788 correctness and claim-boundary tests

The Triton continuation file remains app-name-free: it exposes a generic dense
point nearest-witness adapter, not a Hausdorff/X-HD primitive.

## Pod Timing

Pod artifact:

`docs/reports/goal2788_pod_artifacts/goal2788_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json`

Host:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
```

| Source points | Target points | Pairs | Torch sec | Goal2787 generic sec | Goal2788 dense-nearest sec | Dense / Torch | Dense / Generic | Correctness |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 128 | 128 | 16,384 | 0.000297 | 0.010907 | 0.007820 | 26.320x | 0.717x | pass |
| 512 | 512 | 262,144 | 0.000252 | 0.014573 | 0.007741 | 30.720x | 0.531x | pass |
| 1,024 | 1,024 | 1,048,576 | 0.000345 | 0.014217 | 0.009354 | 27.109x | 0.658x | pass |
| 2,048 | 2,048 | 4,194,304 | 0.000768 | 0.011731 | 0.009572 | 12.466x | 0.816x | pass |
| 4,096 | 4,096 | 16,777,216 | 0.002323 | 0.019159 | 0.008769 | 3.774x | 0.458x | pass |

Goal2788 is an improvement over Goal2787: it removes dense score-row
materialization and is faster than the generic score-row route on every
measured shape. It is still not the selected dense Hausdorff performance path
because it remains 3.77x-30.73x slower than Torch on the same-contract RTX
A5000 measurements.

## Guidance Refresh

Goal2788 adds a measured negative guidance row for:

- operation: `grouped_argmin_f64`
- workload shape: `dense_exact_hausdorff_nearest_then_global_max`
- evidence: Goal2788 pod artifact

The v2.5 app migration plan now records Hausdorff/X-HD as having two measured
negative Triton preview shapes:

- Goal2787: generic grouped argmin then grouped argmax
- Goal2788: fused dense point-nearest then grouped argmax

Both routes are correct. Neither route authorizes automatic Triton selection
for dense exact Hausdorff-style witness reduction.

## Boundary

This goal authorizes:

- a generic dense point-nearest Triton adapter kernel;
- an explicit Hausdorff Python-wrapper strategy using that adapter;
- measured negative guidance for dense Hausdorff-style nearest-witness
  reduction.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- a Hausdorff-specific native or Triton continuation primitive;
- auto-selecting Triton for dense exact Hausdorff-style witness reduction.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2788_hausdorff_dense_point_nearest_triton_strategy_test \
  tests.goal2787_hausdorff_generic_argmin_argmax_triton_adapter_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 22 tests in 0.017s
OK (skipped=4)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2788_final
OK
```

Pod validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2788_hausdorff_dense_point_nearest_triton_strategy_test \
  tests.goal2787_hausdorff_generic_argmin_argmax_triton_adapter_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 22 tests in 2.417s
OK
```

## Decision

`accept-with-boundary`

Goal2788 is accepted as a design improvement over Goal2787 and as negative
selection evidence. The fused dense point-nearest strategy is correct and
better than materializing dense score rows, but it still does not beat Torch for
the tested dense Hausdorff shapes.
