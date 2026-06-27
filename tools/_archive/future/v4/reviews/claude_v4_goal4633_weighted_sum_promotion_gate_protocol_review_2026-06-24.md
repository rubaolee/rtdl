# Claude Review: V4 Goal4633 Weighted-Sum Promotion Gate Protocol

Date: 2026-06-24

Verdict: `approve_with_required_amendments`

Primary reviewed files:

- `future/v4/v4_goal4633_weighted_sum_promotion_gate_protocol_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_goal4633_weighted_sum_promotion_gate_protocol_2026-06-24.md`

## Required Amendment

Claude accepted the goal sequencing and promotion gate, but required one wording
fix before execution:

- rename "Same-Contract Comparison" to "Same-Operator Comparable-Route
  Comparison";
- clarify that the measured ratio captures the cost of the host-materialization
  path versus the device-resident output path, not a pure kernel-vs-kernel
  speedup figure.

Rationale:

- `device_output_frontdoor` returns a Torch CUDA `uint64[1]` scalar that remains
  device-resident until an explicit consumer/verification read;
- `host_scalar_route` returns a Python host scalar and therefore embeds a device
  to host scalar transfer;
- the comparison is valid as a V4 value measurement, but should not be labeled
  as a pure same-contract kernel comparison.

## Accepted Points

Claude accepted:

- weighted-sum as the correct next engineering goal after Goal4632;
- frozen thresholds before execution;
- the four-shape matrix;
- 5 warmups and 30 repeats;
- per-shape floor `>= 1.20x`;
- geomean floor `>= 1.50x`;
- parity at every shape;
- no V4 release authorization;
- no whole-app, CuPy, true-zero-copy, or Tier-3 authorization.

## Authorization

After applying the amendment, Claude authorized proceeding to the Goal4633 POD
gate run.

Claude did not authorize:

- V4 release;
- V4 release-candidate status;
- broad speedup wording;
- whole-application speedup wording;
- CuPy performance claims;
- Tier-3 callback support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python host scope.
