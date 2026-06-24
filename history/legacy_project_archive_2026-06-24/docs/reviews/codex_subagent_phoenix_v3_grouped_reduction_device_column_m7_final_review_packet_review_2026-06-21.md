# Codex Subagent Review: Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Reviewer: Goodall (`019ee93f-5780-7c32-a9ed-d407c09e8958`)

Date: 2026-06-21

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

Note: the subagent did not write this file directly because it was instructed
not to modify files. This file records the completed review result.

```text
verdict: approve-with-required-fixes

row decision: promote_both_rows
```

## P0 Issues

None.

## P1 Issues

1. Tighten the draft public wording for both rows so the Embree comparison
   explicitly says: Embree remains host-packed while the OptiX candidate uses
   `cupy_device_columns`; therefore the Embree/device-column ratios are
   same-contract context, not pure backend-only ratios.
2. In the final 2-AI consensus, keep the `218.248x` number out of
   headline/public row wording except as a labeled cold-prepare phase ratio,
   adjacent to the workload-build/input-path-collapse attribution.

## Review Questions

1. Yes. This is a V3 generic-engine optimization. The app constructs a
   RayDB-shaped workload, but the runtime path is generic prepared ray batch
   plus generic primitive grouped i64 reduction, with no app-specific native
   engine logic.
2. Both exact rows can be promoted as supplemental row-scoped M7 claims after
   the P1 wording fixes:
   `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
   and
   `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`.
3. Yes. The host-packed OptiX/device-column OptiX comparisons are honest and
   phase-attributed. The packet correctly separates cold+loop, workload build,
   ray-batch prepare, and the 524k workload-build collapse.
4. Yes, but only with the P1 wording fix. The Embree/device-column ratios are
   safe as same-contract context, not pure backend-only ratios.
5. The missing git HEAD is not a P0 blocker. The packet acknowledges it and
   binds the evidence to `source_manifest.sha256`, which is sufficient for this
   review packet.
6. Mostly yes. The forbidden wording is strong on whole-app, whole-database,
   true-zero-copy, broad V3-over-V2, and 218x headline misuse. The one gap is
   that the publishable row wording itself should also carry the
   pure-backend-only guard.
7. Required before final Codex consensus: apply the P1 public-wording fix, then
   state that promotion is row-scoped only, release remains unauthorized,
   true-zero-copy remains unauthorized, and the existing scalar-broadcast M7 row
   is retained.

## Final Recommendation

Approve both rows for supplemental M7 row-scoped promotion after the P1 wording
cleanup. Do not authorize release-wide, whole-RayDB, whole-database,
true-zero-copy, pure backend-only, or broad V3-over-V2 claims.
