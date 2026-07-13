# Call For Review — Goal4912 Persistent Planar-Map Workspace Design Gate

Date: 2026-07-03

Please review:

```text
history/internal_docs/goal4912_persistent_workspace_design_plan_2026-07-03.md
```

## Requested Verdict Labels

Choose one:

- `approve_goal4912_productize_in_process_workspace_api`
- `approve_with_required_amendments`
- `block_goal4912_as_packaging_without_product_value`
- `block_goal4912_as_too_broad_or_risky`

## Review Questions

1. Does the plan correctly use Goal4902, Goal4904, Goal4910, and Goal4911 evidence?
2. Is the chosen direction correct: productize an in-process workspace/session API rather than run more group-mode or writer micro-tuning?
3. Is it correct to defer cross-process OptiX GAS/build-artifact caching as a later R&D goal?
4. Is the proposed API generic planar-map RTDL infrastructure rather than a RayJoin-specific hidden route?
5. Does the plan preserve the boundary that app logic and Numba/CuPy continuations stay outside RTDL core?
6. Is the implementation scope for Goal4913 tight enough?
7. Is the acceptance bar honest, especially that it does not require a new speedup and primarily productizes already-proven session reuse?
8. Should Goal4913 be authorized to implement the in-process workspace API?

## Non-Authorization Boundary

Approval of Goal4912 must not authorize:

- raw OptiX callback exposure;
- RayJoin-specific hidden kernels;
- cross-process OptiX GAS serialization;
- broad RTDL/RayJoin performance claims;
- public release wording changes;
- resurrection of V3/V4 claims.
