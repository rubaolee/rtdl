# Claude Review: Goals4085-4088 Partition Summary Chain

Date: 2026-06-09

Reviewer: Claude

Provenance note: Claude produced this review in stdout but could not write the
requested file because its local session asked for write approval. This file
transcribes the Claude review content so the review can be tracked in the normal
`docs/reviews/` location.

## Verdict

`accept`

## Summary

All five review questions are answered affirmatively. No correctness bugs, no
forbidden vocabulary, and no unauthorized claims were found.

## Findings

### 1. Goal4088 Boundary

Correctly scoped. The host AABB rebuild
(`cupy.asnumpy(point_partition_ids)` plus Python accumulation loop) is moved
inside the `pair_enumeration == "host"` branch only. Device AABBs already exist
before the branch.

The `V28FixedRadiusGraphComponentPlan.__post_init__` guard still raises
`ValueError` for any truthy authorization flag, unchanged.

### 2. 1.6x-2.3x Improvement Without Count Regression

Supported by cross-validated artifacts.

`tests.goal4088_device_partition_summary_host_aabb_skip_test` asserts that
`pair_count` and `status_counts` match between the `0c1a717f` and `b5cb7968`
artifacts for all three profiles.

The remaining bottleneck is device pair-stream materialization: 10M-30M rows,
not host work. The Goal4088 report states that explicitly.

### 3. Default-Route Policy

Correct and enforced at multiple layers:

- promotion-blocker tuple;
- plan dataclass guard;
- strategy gating in the plan function;
- prepared-handle metadata flags;
- empirical evidence, including road build still at 0.088s versus the 0.036s
  current-route reference after optimization.

### 4. Prepared Reuse Boundary

Accurate. Clustered break-even is about 11 runs before Goal4088 and about 8.5
runs after Goal4088. Road never breaks even because replay, about 0.042s,
exceeds the current-route reference, about 0.036s.

The `_break_even_runs` logic is correct and the tests match the arithmetic.

### 5. Next Direction

Correct. Goal4086 tests prove the native kernel parameter block has no
partition, safe-full, or ambiguous work-stream fields. Wrapper tuning cannot
unblock the candidate. Materialization cost must be avoided on the critical
path.

## Boundary

This review does not authorize release, public speedup wording, broad RT-core
wording, whole-app acceleration wording, paper-reproduction wording,
true-zero-copy wording, hidden dispatch, automatic partner selection, or
app-specific native-engine logic.
