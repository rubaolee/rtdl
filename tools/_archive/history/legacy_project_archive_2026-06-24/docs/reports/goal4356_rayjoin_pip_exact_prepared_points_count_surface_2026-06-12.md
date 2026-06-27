# Goal4356 RayJoin PIP Exact Prepared-Points Count Surface

Date: 2026-06-12

## What changed

v2.12 now has an explicit RayJoin PIP count mode, `exact_prepared_points`, backed by the new native OptiX ABI:

`rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d`

This route prepares generic point-probe columns once, then runs the exact prepared closed-shape membership count against those resident columns. It removes point repack/reupload from the measured exact query loop while keeping the exact host-refined semantics used by the previous `prepared.count(packed_points)` authority route.

## Why it matters

The Goal4354 RayJoin comparison showed the RTDL exact PIP route was slow for a reason that has little to do with RT cores: each hot query repacked and reuploaded the same point stream, then downloaded candidate rows for exact CPU/GEOS refinement. That made the measurement a mix of RT traversal, memory traffic, and host-side exact predicate work.

This change removes the first avoidable part of that debt. The native timing mode is now `prepared_points_exact_count`, so pod artifacts can verify that point pack/upload are zero in the measured query phase.

## Claim boundary

This is not a public speedup claim. It is a prepared exact-count surface that should make the RayJoin PIP row more explainable and possibly faster.

The route still downloads candidate rows and performs host exact refinement. Therefore it is not yet a fully device-native PIP exact count, not a pure RT-core-only result, and not enough by itself to claim RTDL beats RayJoin on PIP.

## Next required pod check

Run the same RayJoin stream used by Goal4354 with:

`count_mode=exact_prepared_points`

The Goal4354 runner now exposes this as:

`python3 scripts/goal4354_rayjoin_original_vs_rtdl_same_stream_scalar_count.py --artifact-dir docs/reports/goal4354_rayjoin_original_vs_rtdl_pod --workloads pip --pip-rtdl-count-mode exact_prepared_points --include-embree`

Compare against:

1. RayJoin original PIP scalar count.
2. RTDL OptiX `exact`.
3. RTDL OptiX `exact_prepared_points`.
4. RTDL OptiX validated device-filtered modes, kept separate because they are not the exact authority route.

The expected explanation if this improves is simple: query point preparation moves out of the hot loop. The expected explanation if it is still slow is also simple: candidate download plus CPU exact refinement remains in the hot loop.
