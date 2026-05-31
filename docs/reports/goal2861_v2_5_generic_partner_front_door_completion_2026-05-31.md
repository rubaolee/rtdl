# Goal2861: v2.5 Generic Partner Front-Door Completion

Status: implemented and pod-validated for the executable Triton wrappers.

Date: 2026-05-31

## Purpose

Goal2855 made the seven canonical v2.5 harnesses runnable as one packet. The
next usability gap was not another packet artifact: `v2_5_triton_front_door_coverage()`
still reported only 4 of 10 promoted benchmark apps as adapter-front-door
ready, even though the lower-level Triton dispatcher already had the remaining
generic continuation operations.

This goal closes that API gap by exposing the remaining generic continuation
operations as explicit partner-column front doors. A learner or app author can
now call named generic RTDL/partner primitives instead of reaching into raw
dispatcher helper names.

## What Changed

Added four app-agnostic partner-column adapters in `src/rtdsl/partner_adapters.py`:

- `grouped_argmin_f64_partner_columns(...)`
- `grouped_argmax_f64_partner_columns(...)`
- `grouped_topk_f64_partner_columns(...)`
- `bounded_collect_finalize_i64_partner_columns(...)`

The already-existing `grouped_vector_sum_2d_partner_columns(...)` remains the
front door for `grouped_vector_sum_f64x2`.

The new adapters:

- accept caller-supplied generic partner-owned columns;
- route `partner="triton"` through the reviewed v2.5 Triton continuation
  kernels;
- provide Torch CUDA same-contract reference paths where useful;
- preserve deterministic tie-breaking and fail-closed bounded-collect overflow;
- export through `rtdsl.__all__`, `rtdsl.adapters.reductions`, and
  `rtdsl.adapters.collection`;
- do not call native RT traversal and do not embed app semantics.

## Coverage Delta

`V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS` now includes:

- `segmented_count_i64`
- `segmented_sum_f64`
- `segmented_min_f64`
- `segmented_max_f64`
- `compact_mask_i64`
- `bounded_collect_finalize_i64`
- `grouped_argmin_f64`
- `grouped_argmax_f64`
- `grouped_topk_f64`
- `grouped_vector_sum_f64x2`

`v2_5_triton_front_door_coverage()` now reports 10/10 promoted benchmark apps
as front-door-ready:

- benchmark apps covered: 10
- fully front-door-ready apps: 10
- dispatcher-only operations for promoted apps: 0
- missing preview operations for promoted apps: 0

This is API coverage only. It is not a speedup claim, not a public-release
claim, not CUDA pod benchmark completion, and not permission to auto-select
Triton where measured guidance says another same-contract partner is faster.

## Validation

Local Windows structural checks:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test \
  tests.goal2776_v2_5_triton_grouped_argmax_preview_test \
  tests.goal2777_v2_5_triton_grouped_topk_preview_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2781_grouped_vector_sum_adapter_test
```

Result:

```text
Ran 37 tests in 0.032s
OK (skipped=9)
```

Focused Goal2861 local source/coverage checks:

```text
Ran 2 tests in 0.002s
OK
```

Pod executable Triton validation was first run on `69.30.85.171:22167` against
the Goal2861 working tree patch on top of `52898c4d`:

```text
Ran 33 tests in 3.121s
OK (skipped=1)
```

After commit and push, the pod was stashed back to a clean worktree, fast-forwarded
to `d60537e6`, and rerun:

```text
Ran 34 tests in 2.545s
OK (skipped=1)
```

The pod run exercised the new Triton front doors for grouped argmin, grouped
argmax, grouped top-k, and bounded collect/finalize, plus the surrounding
Goal2681/2679/2680/2776/2777 checks.

## Boundary

This goal makes v2.5 easier to write against. It does not make the preview
Triton kernels the selected performance path for every app. Existing selection
guidance still applies:

- dense exact top-k may stay with a faster same-contract partner;
- dense Hausdorff witness reductions may stay with the measured faster path;
- Barnes-Hut grouped vector sums may stay with Torch/CuPy unless Triton wins;
- primitive-first RTDL paths remain preferred where they are already faster.

The native engine remains app-agnostic. The new front doors are generic
partner-column continuations only.
