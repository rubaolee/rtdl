# Goal2664: v2.5 Triton Segmented-Count Preview

Status: preview implementation, pod validation required.

Date: 2026-05-27

## Purpose

This goal extends the Goal2663 Triton pilot from generic segmented sum to the
matching generic `segmented_count_i64` continuation. The count/sum pair is the
minimum useful continuation shape for RayDB-style grouped rows and other dense
hit-stream benchmark paths.

This goal still does not promote a performance path. It is a source-level
implementation slice that must be validated on a Linux NVIDIA pod before any
benchmark wording can use it.

## Implemented Surface

Updated module:

- `src/rtdsl/triton_partner_continuation.py`

New exported API:

- `describe_triton_segmented_count_i64()`
- `run_triton_segmented_count_i64()`
- `TRITON_SEGMENTED_COUNT_I64_OPERATION`

Updated test:

- `tests/goal2663_v2_5_triton_segmented_sum_test.py`

The test file now covers both segmented count and segmented sum because the two
operations share the same lazy Triton backend boundary.

## Contract

`run_triton_segmented_count_i64()` accepts a CUDA Torch tensor:

- `group_ids`: `torch.int64`, shape `(row_count,)`
- `group_count`: non-negative integer

The output is a CUDA Torch tensor `counts[group]` with the number of rows whose
`group_ids[row] == group`.

Like the Python reference contract, the wrapper rejects invalid group ids
outside `[0, group_count)`. The Triton kernel then uses `tl.atomic_add` over a
partner-owned device output tensor.

## Boundary

This is a generic post-RT continuation. It has no database, graph, DBSCAN,
Barnes-Hut, collision, RTNN, or LibRTS vocabulary.

The boundary remains:

- `status = preview_not_promoted`
- `raw_kernel_required = False`
- `replaces_rt_traversal = False`
- `promoted_performance_path = False`
- `rt_core_speedup_claim_authorized = False`

Triton does not replace OptiX RT traversal. It only handles a generic grouped
continuation over partner-owned tensors after an RTDL primitive has produced
group ids.

## Validation

Run locally:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2663_v2_5_triton_segmented_sum_test \
  tests.goal2662_v2_5_partner_continuation_contract_test
```

Expected on this Mac:

- descriptor and source-boundary tests pass;
- count and sum CUDA execution tests are skipped if Triton/Torch CUDA are not
  available;
- no public speedup claim is made.

## Pod Gate

Before using this in benchmark evidence, run the same tests on a CUDA pod and
then add scale tests for grouped row streams large enough to measure seconds,
not microbenchmarks. Promotion requires showing that Triton preserves or
improves the existing RTDL benchmark basis instead of trading away RT-core
performance for convenience.
