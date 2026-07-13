# Call For Review: Goal4965 Exact LSI Bottleneck Decision

Please review:

`history/internal_docs/goal4965_exact_lsi_bottleneck_decision_after_device_columns_no_go_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4965_bottleneck_decision_exact_lsi_compute_next`
- `approve_with_required_amendments`
- `block_until_goal4965_decision_reconciles_measurements`

## Review Questions

1. Does the decision correctly interpret Goal4964 as correctness pass but
   performance no-go?
2. Does the evidence justify saying host row materialization/copy is not the
   meaningful bottleneck, given the `~0.000526s` device-to-NumPy copy median?
3. Is it correct to identify fresh exact planar-map LSI computation as the next
   real bottleneck?
4. Does the packet correctly reject cached replay and candidate device columns
   as fresh overlay performance evidence?
5. Is the recommended next goal, exact LSI fresh-cost breakdown and single-pass
   feasibility, the right continuation?
6. Does the packet preserve the generic-system boundary and avoid RayJoin
   overlay-specific core claims?
7. Is it correct to keep larger representative testing blocked until real
   inputs are restored?
