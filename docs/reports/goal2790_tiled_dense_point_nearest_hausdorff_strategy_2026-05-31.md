# Goal2790 - Tiled Dense Point-Nearest Hausdorff Strategy

Date: 2026-05-31

## Purpose

Goal2788 showed that one-block dense point-nearest improves over dense
score-row materialization but still loses to Torch dense at the measured 128 to
4,096 point shapes. Goal2790 tests the next design: tile the candidate points,
produce per-query per-tile nearest witnesses, then reduce those tile witnesses
with generic `grouped_argmin_f64` before the final `grouped_argmax_f64`
directed-Hausdorff witness.

The explicit route is:

```python
directed_hausdorff_2d_partner_columns(
    source,
    target,
    partner="triton",
    triton_strategy="dense_point_nearest_tiled",
    triton_candidate_block_size=1024,
)
```

## What Changed

Updated:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`

Added:

- `run_triton_dense_point_nearest_2d_tiled(...)`
- `dense_point_nearest_2d_tiled_adapter_kernel`
- `triton_strategy="dense_point_nearest_tiled"` for
  `directed_hausdorff_2d_partner_columns(...)`
- `tests/goal2790_hausdorff_tiled_dense_point_nearest_test.py`

The Triton continuation file remains app-name-free: it exposes a generic tiled
dense point-nearest adapter, not a Hausdorff/X-HD primitive.

## Pod Timing

Pod artifact:

`docs/reports/goal2790_pod_artifacts/goal2790_tiled_dense_point_nearest_hausdorff_pod_69_30_85_171_2026-05-31.json`

Host:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
```

| Points x points | Pairs | Torch sec | One-block sec | Best tiled block | Best tiled sec | Tiled / Torch | Correctness |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2,048 x 2,048 | 4,194,304 | 0.000779 | 0.010634 | 1,024 | 0.015275 | 19.608x | pass |
| 4,096 x 4,096 | 16,777,216 | 0.002372 | 0.009841 | 2,048 | 0.016434 | 6.928x | pass |
| 8,192 x 8,192 | 67,108,864 | 0.009176 | n/a | 512 | 0.018804 | 2.049x | pass |
| 16,384 x 16,384 | 268,435,456 | 0.034499 | n/a | 1,024 | 0.025710 | 0.745x | pass |

The result is thresholded:

- Small and mid dense shapes should still select Torch.
- The tiled Triton route becomes competitive at larger shapes; on the measured
  16,384 x 16,384 shape it is faster than Torch (`0.745x` tiled/Torch).
- This is not yet a public speedup claim or a release path. It is internal
  v2.5 preview evidence that the fused/tiled direction is worth continuing.

## Boundary

This goal authorizes:

- a generic tiled dense point-nearest Triton adapter;
- an explicit Hausdorff Python-wrapper strategy using that adapter;
- internal evidence for a large-shape crossover hypothesis.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- a Hausdorff-specific native or Triton continuation primitive;
- automatic partner selection without a future conditional-selection policy.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2790_hausdorff_tiled_dense_point_nearest_test

Ran 4 tests in 0.030s
OK (skipped=1)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2790_local
OK
```

Pod validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2790_hausdorff_tiled_dense_point_nearest_test

Ran 4 tests in 2.053s
OK
```

## Decision

`accept-with-boundary`

Goal2790 is accepted as internal v2.5 preview evidence. The tiled strategy
does not replace the explicit partner-selection rule yet, but it gives a real
large-shape performance direction that Goal2788 did not have.
