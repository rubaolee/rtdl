# Goal2874 Triton Preview Current Pod Conformance Backfill

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2873 separated support labels from conformance evidence and deliberately
left several Triton preview rows as current-pod-indexing gaps. The NVIDIA pod
was available, so Goal2874 reran the older CUDA-gated Triton preview tests on
the current source tree and backfilled the matrix.

## Rows Closed

The following Triton preview operations now have current pod runtime
conformance rows in `v2_5_partner_conformance_matrix()`:

- `segmented_count_i64`
- `segmented_min_f64`
- `segmented_max_f64`
- `compact_mask_i64`
- `bounded_collect_finalize_i64`

Together with Goal2872 and Goal2779, every operation in
`V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS` now has a pod runtime conformance row.

## Remaining Boundary

This is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
and not package-install wording.

The matrix still reports `release_conformance_complete: false` because the
Numba fallback preview rows remain explicit runtime conformance gaps. That is
now the precise partner-conformance blocker rather than a mixed Triton/Numba
uncertainty.

## Pod Validation

Local validation:

```text
py -3 -m unittest \
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test \
  tests.goal2873_v2_5_partner_conformance_matrix_test

Ran 12 tests in 0.635s
OK
```

Expanded local readiness/conformance slice:

```text
Ran 79 tests in 2.491s
OK (skipped=5)
```

Run from pushed `main` on the NVIDIA pod:

```text
scope:
  tests.goal2663_v2_5_triton_segmented_sum_test
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test
  tests.goal2678_v2_5_triton_compact_mask_preview_test
  tests.goal2680_v2_5_triton_bounded_collect_preview_test
  tests.goal2779_v2_5_triton_edge_list_components_preview_test

Ran 25 tests in 2.894s
OK
```

## Codex Verdict

`accept-with-boundary`
