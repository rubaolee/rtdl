# V4 Goal4682 Next Target After Shape-Pair No-Speed Result

Date: 2026-06-25

Status:

```text
goal4682_shape_pair_no_promotion_select_contact_witness_design_gate_no_pod
```

## Decision

Close the shape-pair relation active-count route as a performance target.

Goal4681 proved that the route is correct and device-resident enough for the
focused contract, but it did not beat V2.14:

| Ratio | Value |
| --- | ---: |
| V4/V2.14 hot | 0.963x |
| V4/V2.14 wall | 0.605x |
| V4/V3.0.2 hot | 0.977x |

Therefore:

- do not promote `v4_shape_pair_relation_active_count_2d_prepared_left_executor`
  to the measured V4 catalog;
- do not keep tuning it as the second high-performance V4 route;
- do not use it for public speed wording.

## Next Target

Select only a design/audit gate for Goal4683:

```text
AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D
```

This is not implementation authorization. It is the next target only if the
audit can prove a real new generic runtime lever:

- candidate discovery and exact witness refinement must stay in generic device
  columns;
- it must not be contact-manifold app identity;
- it must not be merely V2.14 bounded collect-k with a new V4 name;
- V2.14 denominator and kill conditions must be frozen before any code or POD.

## Why This Direction

Most obvious existing app candidates are already disqualified as clean V4 wins:

- `robot_collision`, `librts_spatial_index`, `rtnn`, `raydb_style`, and
  `triangle_counting` already had relevant V2.14 primitive-first routes.
- `spatial_rayjoin` shape-pair active count just failed as a same-primitive
  speed target.
- `barnes_hut` only produced a V2.14 host-frontier bottleneck win and is not a
  second V4-over-V3 performance source.

The only remaining plausible V4.0 high-leverage class is a generic full
contact/witness pipeline that removes host candidate/witness materialization
without hardcoding contact-manifold semantics.

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No. Continuing to tune shape-pair active count after a clean no-speed POD result
would be the stupid decision.

2. If yes, what actions made it stupid?

Not applicable. The avoided stupid action was opening another POD loop on a
route that already failed the frozen bars.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes. Record no-promotion, then require the next target to prove a new runtime
lever before implementation or POD.

4. Should I try a different path to solve the real problem?

Yes. Goal4683 should audit `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D`. If it
is just bounded collect-k rebranded, kill it immediately.

## Non-Authorization

This goal does not authorize:

- V4 release.
- public speedup wording.
- whole-app high-performance wording.
- measured-catalog promotion for shape-pair relation active count.
- implementation of the contact/witness target.
- POD spending.
- app-identity native kernels.
- Tier-3 callbacks, C ABI, embedding, or non-Python hosts.

## Next Work

Goal4683: design audit for `AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D`.

Exit condition for Goal4683:

- `go`: the target is generic, absent from V2.14 as a full device-column exact
  witness pipeline, and has a concrete material-speed hypothesis;
- `no-go`: the target is bounded collect-k rebranded, app identity, or lacks a
  credible speed source.
