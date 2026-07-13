# Call For Review: Goal4967 Exact LSI Fresh Cost Breakdown

Please review:

`history/internal_docs/goal4967_exact_lsi_fresh_cost_breakdown_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4967_breakdown_workspace_first_use_is_bottleneck`
- `approve_with_required_amendments`
- `block_until_goal4967_reconciles_native_timings_and_measurement_boundary`

## Review Questions

1. Does the report correctly interpret the new native LSI timings?
2. Is it correct that the `~0.8s` fresh LSI wall time is not explained by the
   measured native count/write launch times?
3. Is it correct to refine the earlier "cached replay" wording into
   "prepared-hot workspace replay" while still forbidding a fresh `0.10s`
   claim?
4. Does the evidence weaken single-pass exact pair-id production as the next
   highest-leverage optimization?
5. Is the proposed next goal, explicit planar-map LSI workspace preparation
   contract and setup breakdown, the right continuation?
6. Does the packet preserve the generic RTDL boundary and avoid RayJoin overlay
   core semantics?
