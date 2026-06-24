# Goal2016 Torch Vectorized Exact Witness Filter

Date: 2026-05-14

Status: pod-pass-with-boundary

## Summary

Goal2016 starts closing the Torch/CuPy asymmetry left by Goal2003 and Goal2009.
CuPy already had a device-side exact segment/triangle filter for generic OptiX
candidate witnesses. Torch previously fell back to host exact filtering for the
same hit-count column path.

This goal adds a vectorized Torch exact filter over partner-owned device
columns. The native OptiX engine remains unchanged and app-agnostic:

`generic_ray_primitive_candidate_witness_pairs`

The app exactness still lives in the partner layer.

## Implementation Shape

- `_torch_exact_segment_triangle_witness_pairs(...)` maps candidate ray and
  primitive IDs to partner-column positions with Torch tensor operations.
- It keeps filtered candidate IDs as Torch `int64` tensors internally because
  CUDA boolean indexing is not implemented for `torch.uint32`.
- It evaluates the same segment/triangle predicates as the CuPy RawKernel path:
  endpoint-in-triangle plus segment/edge intersections with epsilon handling.
- `segment_polygon_hitcount_optix_partner_device_count_columns(..., partner="torch")`
  now exact-filters and counts on the Torch device path.
- `segment_polygon_hitcount_optix_prepared_partner_device_count_columns(..., partner="torch")`
  uses the same prepared-scene retained triangle columns and partner lookup
  cache pattern as CuPy.

Expected metadata:

- `app_exact_filter: torch_vectorized_segment_triangle_filter_from_generic_witness_candidates`
- `app_exact_filter_device_materialization: true`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_torch_exact_filter`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_prepared_torch_exact_filter`
- `whole_app_true_zero_copy_authorized: true`

## Boundary

## Pod Evidence

Artifact:

- `docs/reports/goal2016_pod_smoke/road_hazard_prepared_torch_exact_filter_2048.json`
- `docs/reports/goal2016_pod_smoke/road_hazard_prepared_torch_exact_filter_4096.json`

Pod:

- GPU: `NVIDIA RTX A5000, 570.211.01`
- Source label: `5e89ceaf-plus-goal2016-torch-exact-filter`
- Count: `2048`
- Iterations: `5`

The run passed strict priority-flag parity and recorded:

- `app_exact_filter: torch_vectorized_segment_triangle_filter_from_generic_witness_candidates`
- `app_exact_filter_device_materialization: true`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_torch_exact_filter`
- `app_count_materialization: partner_gpu_unique_pair_counts_from_prepared_torch_exact_filter`
- `whole_app_true_zero_copy_authorized: true`

Timing at count 2048:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 prepared native OptiX road-hazard rows | 0.002813369 | 1.000x |
| v2.0 unprepared Torch exact-filter priority columns | 0.005988153 | 2.128x slower |
| v2.0 prepared Torch exact-filter priority columns | 0.005289506 | 1.880x slower |

Timing at count 4096:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 prepared native OptiX road-hazard rows | 0.007986754 | 1.000x |
| v2.0 unprepared Torch exact-filter priority columns | 0.005732235 | 0.718x |
| v2.0 prepared Torch exact-filter priority columns | 0.004532680 | 0.568x |

The Torch exact-filter path is therefore scale-sensitive. At count 2048 it
closes the device-exactness/parity gap but is slower than v1.8 prepared native.
At count 4096 it becomes positive evidence: the prepared Torch row is about
`1.76x` faster than v1.8 prepared native, with strict priority-flag parity.

## Boundary

This goal primarily closes a partner-parity and correctness gap. It also has
positive scale-sensitive evidence at count 4096, but it is not a v2.0 release
claim and not a broad speedup claim.

Known review boundaries:

- Torch uses vectorized tensor expressions rather than the CuPy RawKernel path,
  so precision and launch behavior may differ slightly even though parity passed
  on the collected pod artifacts.
- Invalid candidate positions are clamped for tensor indexing and then masked
  out by `valid`; this is intentional but should stay covered by tests.
- The perf runner's top-level artifact `goal` field still says `Goal1869`
  because the runner predates Goal2016; use the path and source label for
  provenance.

Claude reviewed this goal in
`docs/reviews/goal2017_claude_review_goal2016_torch_exact_filter_2026-05-14.md`
with verdict `accept-with-boundary`.

After the count-4096 artifact was added, Claude reviewed the updated
scale-sensitive wording in
`docs/reviews/goal2019_claude_addendum_review_goal2016_torch_4096_2026-05-14.md`
with verdict `accept-with-boundary`.
