# Goal3987 RT-DBSCAN Blocked Grouped-Stream Negative Probe

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3985 made the current-scale timing packet readable enough to choose the next real runtime target. Excluding artificial aggregate totals for RayDB and robot collision, the largest single-call hot-path metric in the ten-app packet is RT-DBSCAN grouped stream:

- current row: `rt_dbscan_optix_numba_scale_default_65536_no_validation`
- representative metric: `metadata.prepared_query_repeat_protocol.elapsed_sec_median`
- Goal3985 value: about 0.0907 sec

Goal3987 tested whether existing blocked grouped-stream or direct-side-effect switches can improve that path without new runtime work.

## Pod Setup

- Pod: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit for probe checkout: `accc84daf76846d29d91fa8a145187851e941f04`
- OptiX build: `make build-optix`
- Dataset: `clustered3d`
- Point count: `65536`
- Repeat/warmup: `--repeat 5 --warmup 1`
- Validation: `--no-validation`; signature stability checked from payloads

## Results

| Variant | Median elapsed sec | Native elapsed sec | Signature |
| --- | ---: | ---: | --- |
| unblocked grouped stream | 0.0901 | 0.0795 | four clusters of 16,384; all core |
| blocked, block size 2,048 | 0.7696 | 0.7594 | same |
| blocked, block size 4,096 | 0.3942 | 0.3866 | same |
| blocked, block size 8,192 | 0.2111 | 0.2041 | same |
| blocked, block size 16,384 | 0.1180 | 0.1118 | same |
| blocked, block size 32,768 | 0.1077 | 0.1013 | same |
| direct side effect enabled | 0.0900 | 0.0792 | same |

## Interpretation

No existing switch wins:

- Smaller blocked ranges are much slower because they multiply grouped-union traversal passes.
- Larger blocked ranges approach the unblocked path but still lose.
- The direct-side-effect flag is effectively neutral for this column-signature case.

This closes the easy-route question. The next improvement requires a stronger generic runtime primitive, not a route flip.

## Next Design Target

The current path is already app-agnostic:

- native contract: `generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace`
- no neighbor-row materialization
- no directed adjacency stream materialization
- Numba only computes the compact column signature

The remaining runtime problem is grouped-union atomic pressure over dense fixed-radius self-queries. The next useful primitive direction is a generic resident fixed-radius component/grouped-union contract that reduces redundant all-items traversal and parent-workspace contention without introducing DBSCAN-specific engine vocabulary.

## Boundary

This is negative performance evidence and does not authorize release, public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic.
