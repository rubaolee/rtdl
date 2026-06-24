# Phoenix V3 Grouped-Reduction Device-Column Ray-Batch Candidate

Status: `grouped_reduction_device_column_ray_batch_candidate_pending_pod_not_m7`.

This is a candidate for the `grouped_reduction_prepare_amortization`
queue item. It is not release authorization and not an M7 promotion.

Current flags:

- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `whole_app_speedup_claim_authorized: false`
- `m7_promotion_authorized: false`
- `default_route_unchanged: true`

Why this is generic engine work:

The candidate reuses RTDL's generic prepared ray-batch device-column ABI and generic ray/triangle grouped i64 reduction. RayDB remains only the evidence harness that supplies columns and checks the CPU oracle.

## What Changed

- RayDB prepared grouped reduction accepts explicit ray_batch_layout.
- host_packed remains the default and the current M7 evidence path.
- cupy_device_columns can defer Python host ray-record materialization and prepare the OptiX ray batch from partner-owned CUDA columns.
- The M28 runner records prepared_ray_batch_layout, native_device_column_path_used, logical_ray_count, and host_packed_ray_count.
- The generic 3-D triangle packer now accepts scalar fields just like the 3-D ray packer.

## Required Pod Evidence

- same RTX/RT-core host for Embree and OptiX
- same generated_rows/generated_groups/mode/repeat/warmup
- CPU-reference parity for both backends
- prepared_ray_batch_layout=cupy_device_columns on OptiX rows
- native_device_column_path_used=true on OptiX rows
- host_packed_ray_count=0 and logical_ray_count>0 on OptiX candidate rows
- cold_prepare_total_sec, workload_build_sec, prepared_ray_batch_sec, prepared_iteration_total_sec, and native_call_wall_median_sec recorded
- source manifest and 2-AI review before any M7 reopening

## Rerun Command

```powershell
py -3 scripts/v3_0_m28_raydb_prepared_grouped_refresh.py --generated-rows 524288 --generated-groups 2048 --generated-revenue-mod 64 --modes sum --backends embree,optix --warmup 3 --repeat-overrides embree:sum=100,optix:sum=100 --optix-ray-batch-layout cupy_device_columns --output docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_YYYYMMDD/grouped_sum_device_columns_524288_repeat100.json
```

## Forbidden Wording

- Do not claim the device-column candidate is faster before pod evidence exists.
- Do not replace the current grouped_reduction M7 row with this candidate without fresh M7 review.
- Do not call this true zero-copy; it is an explicit V3 partner-device ray-column route, not V4 interop.
- Do not promote whole RayDB or count rows from this code change alone.

## Goal-Level Decision Audit

Decision: add an explicit device-column ray-batch candidate for grouped-reduction prepare amortization, with release flags false

1. Was I foolish?
   No. The current 524,288-row blocker is dominated by host ray-record construction and ray-batch preparation, so the next honest path is to test an existing generic device-column ABI instead of polishing prose.
2. If yes, what actions made the decision foolish?
   It would be foolish to call this a V3 performance win before the pod rerun, or to hide that the current M7 row remains only the 262,144-row host-packed repeat100 case.
3. Was there another path?
   Keep tuning RayDB-specific encoding or rewrite a native database operator. That would violate the Phoenix requirement that apps are evidence harnesses, not V3 products.
4. Can I now try a different path that actually solves the problem?
   Run the explicit cupy_device_columns candidate on the RT hardware pod, compare against the host-packed/current route, and only reopen M7 if wall and cold-plus-loop evidence materially improves.
