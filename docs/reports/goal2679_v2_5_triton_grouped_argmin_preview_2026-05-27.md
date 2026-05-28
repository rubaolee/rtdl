# Goal2679: v2.5 Triton Grouped Argmin Preview

Status: local implementation slice; CUDA pod validation still required.

Date: 2026-05-27

## Purpose

`grouped_argmin_f64` is the generic continuation behind nearest-witness and
ranked-summary benchmark paths. This goal moves it from descriptor-only to an
executable Triton preview without adding app-specific semantics to the engine.

The operation contract is:

- inputs: `group_ids:int64`, `item_ids:int64`, `scores:float64`, `group_count`;
- output: one lowest-score item per present group;
- tie-break: lowest score, then lowest item id;
- missing groups are explicit in `missing_group_ids`;
- NaN scores are rejected.

## Implementation

Added to `src/rtdsl/triton_partner_continuation.py`:

- `describe_triton_grouped_argmin_f64()`;
- `run_triton_grouped_argmin_f64()`;
- `_triton_grouped_argmin_score_f64_kernel()`;
- `_triton_grouped_argmin_item_i64_kernel()`;
- generic dispatcher support through `run_triton_partner_continuation()`.

The preview uses Triton atomics to compute per-group minimum score, then a
second Triton pass to select the lowest item id among rows with that minimum
score. Torch is still only the CUDA tensor carrier and compaction helper, not
the v2.5 partner. The metadata remains:

- `partner="triton"`;
- `status="preview_not_promoted"`;
- `cupy_required=False`;
- `pytorch_partner_required=False`;
- `promoted_performance_path=False`;
- `replaces_rt_traversal=False`.

## Benchmark Impact

This unblocks the generic operation needed by Hausdorff/X-HD and RTNN-style
nearest/ranked summaries at the v2.5 preview level. It does not by itself prove
benchmark-app migration or performance. Full app wiring and pod evidence remain
required.

After this goal, the v2.5 preview operation set is:

- `segmented_count_i64`;
- `segmented_sum_f64`;
- `segmented_min_f64`;
- `segmented_max_f64`;
- `compact_mask_i64`;
- `grouped_argmin_f64`.

Goal2680 later adds `bounded_collect_finalize_i64` as a local Triton preview,
so this statement is historical to Goal2679.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test
```

Expected locally on this Mac:

```text
Ran 4 tests
OK (skipped=1)
```

The skipped test requires Triton plus Torch CUDA on a Linux NVIDIA pod.

## Claim Boundary

This is a generic post-RT continuation preview only. It does not replace RTDL
RT traversal, does not authorize public speedup claims, and does not complete
v2.5. Promotion requires CUDA correctness/timing evidence, app integration, and
review.
