# Goal4105 - Direct Status Union Versus Current RT-DBSCAN Route

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4104 proved that direct device status consumption is faster than the Goal4100-style materialized unordered partition-pair path when both are already inside the partition-convergence runtime shape.

Goal4105 asks the stricter route question: if a user calls the direct-status preview as an app-level function, does it beat the current recommended RTDL/OptiX grouped-stream plus Numba signature route?

## Fair Timing Boundary

The comparator intentionally includes app-level point generation/setup on both sides. This is a conservative route-level comparison, not a resident-kernel-only comparison.

This matters because Goal4104's direct-status win was a resident/runtime win, while Goal4105 measures a naive app-level call that still has to construct point rows and pack device columns on each run.

## Pod Evidence

Artifact:

`docs/reports/goal4105_direct_status_vs_current_route_pod.json`

Setup:

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source commit: `a6bf5eae465dc1248559dddd15e2933ffedf036b`
- Tracked worktree dirty: `false`
- Point count: 65,536
- Cell factor: 0.125
- Repeat: 3 measured runs after 1 warmup

## Result

| Profile | Direct-status app-level median (s) | Current route median (s) | Current/direct ratio | Direct faster? |
| --- | ---: | ---: | ---: | --- |
| clustered3d | 0.401603 | 0.190724 | 0.475x | no |
| road3d | 0.332069 | 0.126130 | 0.380x | no |
| ngsim_dense | 0.479589 | 0.099025 | 0.206x | no |

The current route remains the recommended route. Goal4104's direct-status kernel is promising, but Goal4105 shows that the direct-status path is not route-promotable as an app-level route while it repacks point rows and rebuilds partition columns for every call.

## Interpretation

The useful design conclusion is sharper now:

- Goal4104 says direct status consumption is the right primitive direction.
- Goal4105 says direct status must be exposed through a prepared/resident column-input path before it can compete with the current route.
- More row-stream cleanup is not the main target.

The next engineering target is therefore a prepared/resident direct-status partition-convergence handle: prepare point columns, partition keys, offsets, and AABBs once; then run direct grouped-union signatures repeatedly without rebuilding those columns or materializing near-pair rows.

## Boundary

This report does not promote `partition_convergence_hybrid` as a default route and does not authorize release, public speedup wording, broad RT-core wording, whole-app benchmark claims, paper-reproduction claims, hidden dispatch, automatic partner selection, app-specific engine logic, native ABI additions, or true-zero-copy claims.
