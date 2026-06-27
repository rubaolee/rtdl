# V4 Goal4667 - Hausdorff Adaptive Argmax Focused Gate

Date: 2026-06-25

Status: focused gate passed, no release authorization

Decision label:
`hausdorff_focused_gate_passes_after_generic_adaptive_argmax__not_release_yet`

## Bottom Line

Goal4667 turns Goal4666's mixed Hausdorff result into a focused pass by fixing a
generic runtime bottleneck, not by changing the app or weakening the bar.

The optimization is generic:

`global_argmax_u32_f64_partner_columns`

now supports:

- deferred partner synchronization with `synchronize=False`, so the app hot
  window synchronizes once at the end instead of once inside the continuation
  and once outside it;
- adaptive CuPy reduction:
  - single-block RawKernel for rows `<= 131072`;
  - multi-block RawKernel for larger rows.

No Hausdorff-specific native kernel was added.

## Evidence

Machine summary:

`future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/summary.json`

Raw POD evidence:

- `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/v4_official_cupy_multiblock_copies16384_rerun_warmup5.json`
- `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/v4_official_cupy_multiblock_copies65536_rerun_warmup5.json`
- `future/v4/evidence/v4_goal4667_hausdorff_multiblock_argmax_20260625/v4_official_cupy_multiblock_copies262144_normspan1000000.json`

Baseline:

`future/v4/evidence/v4_goal4665_hausdorff_focused_20260625/summary.json`

Hardware:

- POD: `root@194.68.245.170:22089`
- GPU: NVIDIA RTX A5000
- Driver: `570.195.03`
- CuPy: `14.1.1`

## Focused Rows

Frozen bars:

- correctness required;
- V4/V3 hot speedup must be at least `1.20x`;
- prepare must be at least `0.80x` versus V3 where comparable.

| Points/side | Correct | Strategy | V4 hot | V3 hot | V4/V3 hot | Prepare V4/V3 | Directed-summary V4/V3 | Result |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 65,536 | yes | `cupy_rawkernel_single_block_reduce` | `0.002262s` | `0.003029s` | `1.339x` | `0.942x` | `1.078x` | pass |
| 262,144 | yes | `cupy_rawkernel_multiblock_reduce` | `0.002251s` | `0.004123s` | `1.832x` | `1.201x` | `1.179x` | pass |

The 1,048,576 points/side coordinate-normalized correctness-boundary probe also
passes with the new reducer:

- hot: `0.006921s`;
- prepare: `10.978008s`;
- directed-summary: `34.217822s`;
- strategy: `cupy_rawkernel_multiblock_reduce`.

This large row is still a correctness-boundary probe, not a speed claim.

## What Changed

Code-level changes:

- `src/rtdsl/partner_adapters.py`
  - added `synchronize` control to `global_argmax_u32_f64_partner_columns`;
  - added CuPy RawKernel single-block and multi-block implementations;
  - records `reduction_strategy`, `partner_synchronized_before_return`, and
    `rawkernel_row_threshold` in metadata.
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
  - calls the generic continuation with `synchronize=False`;
  - keeps the final hot-window synchronization outside the continuation.

Local validation:

`py -m unittest tests.v4_goal4666_hausdorff_cupy_official_route_test tests.v4_goal4665_hausdorff_focused_candidate_test tests.v4_goal4652_app_route_binding_test tests.v4_frontdoor_test tests.v4_scope_gate_test`

Result before the final report update:

`27 tests OK`

## Claim Boundary

This authorizes the next protocol step: request or prepare the next app-level
benchmark decision using the updated Hausdorff route.

It does not authorize:

- V4 release;
- formal high-performance V4;
- broad V4 speedup wording;
- whole-app speedup wording;
- public true-zero-copy wording;
- app-specific native Hausdorff kernels;
- arbitrary callback support;
- all-app rerun without protocol refresh and external review/debt record.

## Next Step

Goal4668 should refresh the app-level protocol with this changed Hausdorff
truth, then decide whether a full app-level rerun is now justified. The
Hausdorff focused row can contribute as one candidate row; it is not enough by
itself to finish V4.
