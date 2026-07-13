# Call For Review: Goal4963 Exact LSI Pair-Id Device Columns Design Gate

Please review:

`history/internal_docs/goal4963_exact_lsi_pair_id_device_columns_design_gate_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4963_authorize_goal4964_exact_lsi_pair_id_device_columns`
- `approve_with_required_amendments`
- `block_goal4964_until_design_genericity_or_measurement_gate_is_fixed`

## Review Questions

1. Does Goal4963 correctly distinguish existing exact host pair-id rows from
   candidate device columns and left-id-count device columns?
2. Is the proposed primitive generic planar-map LSI rather than a RayJoin
   overlay shortcut?
3. Are the native/API naming red lines sufficient to prevent app identity from
   entering RTDL core?
4. Is the measurement gate honest that exact device columns may not eliminate
   the whole ~0.8s LSI phase if traversal/predicate dominates?
5. Are the correctness gates sufficient before any performance claim?
6. Is reusing `OptixNativeDevicePairColumnOutput` acceptable, or should the
   exact route use a stricter sibling output type?
7. Should Goal4964 be authorized under this design?
