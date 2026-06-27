# V4 Goal4666 - Hausdorff CuPy Official Route Evidence

Date: 2026-06-25

Status: complete, no release authorization

Decision label:
`official_cupy_route_productized__large_row_passes_hot_prepare__focused_bar_not_reopened`

## Bottom Line

Goal4666 fixes a real V4 route problem, but it does not authorize formal
high-performance V4.

The V4 Hausdorff route now supports `partner="cupy"` through the official V4
point-group nearest-witness front door and the generic
`global_argmax_u32_f64_partner_columns` continuation. It no longer depends on
the app-local CuPy reducer.

This is useful engineering progress:

- correctness passes;
- the producer is `v4_point_group_nearest_witness_2d_device_arrays`;
- the consumer is generic `global_argmax_u32_f64_partner_columns`;
- the 262,144 points/side row now clears the frozen V4/V3 hot-path and prepare
  bars.

But the result is mixed:

- the 65,536 points/side primary row still fails the frozen hot/prepare bars;
- a warm-cache diagnostic rerun reduces that failure to near-parity, but still
  does not clear the `1.20x` hot bar;
- the app-level directed-summary denominator remains parity/slower versus the
  V3 CuPy route.

Therefore this counts as route productization and a focused performance repair,
not as formal V4 high-performance evidence.

## Evidence

Machine summary:

`future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/summary.json`

Raw rows:

- `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/v4_official_cupy_copies1024.json`
- `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/v4_official_cupy_copies16384.json`
- `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/v4_official_cupy_copies16384_rerun_warmup2.json`
- `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/v4_official_cupy_copies65536.json`
- `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/v4_official_cupy_copies262144_normspan1000000.json`

Baseline source:

`future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/summary.json`

Hardware:

- POD: `root@194.68.245.170:22089`
- GPU: NVIDIA RTX A5000
- Driver: `570.195.03`
- CuPy: `14.1.1`

## Primary Rows

| Points/side | Correct | V4 CuPy hot | V3 CuPy hot | V4/V3 hot | Prepare V4/V3 | Directed-summary V4/V3 | Reading |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 65,536 | yes | `0.008496s` | `0.003029s` | `0.357x` | `0.745x` | `0.829x` | Primary row fails. |
| 262,144 | yes | `0.003200s` | `0.004123s` | `1.288x` | `1.031x` | `0.973x` | Hot/prepare pass; app directed-summary remains parity/slower. |

Diagnostic rerun for the 65,536 points/side row:

- `--warmup 2`, same official CuPy route;
- correctness passed;
- hot `0.003151s`, V4/V3 hot `0.961x`;
- prepare `1.812401s`, V4/V3 prepare `0.793x`;
- directed-summary `3.216290s`, near V3 parity.

This shows the original 65,536 row had instability, but the rerun still does not
meet the frozen `1.20x` hot bar and remains just under the `0.80x` prepare floor.

## 1M Correctness Boundary

The coordinate-normalized 1,048,576 points/side CuPy official route passed
correctness:

- copies: `262144`;
- coordinate-normalization span: `1000000.0`;
- hot: `0.023564s`;
- prepare: `10.664132s`;
- directed-summary: `34.609050s`;
- producer: `v4_point_group_nearest_witness_2d_device_arrays`;
- consumer: `global_argmax_u32_f64_partner_columns`, partner `cupy`,
  reduction `cupy_masked_reduce`.

This is a correctness-boundary probe, not a speed claim.

## What Changed

Code-level change:

- `src/rtdsl/v4_point_group.py`: the V4 point-group surface can now allocate and
  prepare CuPy output columns instead of rejecting CuPy as declared-unmeasured.
- `src/rtdsl/partner_adapters.py`: `global_argmax_u32_f64_partner_columns` now
  has a generic CuPy path with deterministic tie-breaking.
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`:
  `partner="cupy"` now uses the official V4 session and generic continuation;
  the app-local CuPy reducer has been removed from the hot path.

Local validation:

`py -m unittest tests.v4_goal4666_hausdorff_cupy_official_route_test tests.v4_goal4665_hausdorff_focused_candidate_test tests.v4_goal4664_next_performance_target_selection_test tests.v4_goal4652_app_route_binding_test tests.v4_frontdoor_test tests.v4_scope_gate_test`

Result:

`28 tests OK`

## Claim Boundary

Not authorized:

- V4 release;
- formal high-performance V4;
- broad V4 speedup wording;
- whole-app speedup wording;
- all-app rerun trigger;
- public true-zero-copy wording;
- app-specific native Hausdorff kernel;
- CuPy performance wording beyond this exact measured route.

## Next Engineering Need

Do not rerun all-app from this mixed result.

The next useful engineering decision is:

1. either reduce the remaining small-scale overhead/stability in the same V4
   official CuPy route and rerun the focused Hausdorff gate;
2. or select a different app-level target where the V4 architecture has a
   stronger V4-specific lever than partner parity.

In both cases the standard remains app-level evidence against V2.14/V3.0.2, not
operator-only or partner-migration evidence.
