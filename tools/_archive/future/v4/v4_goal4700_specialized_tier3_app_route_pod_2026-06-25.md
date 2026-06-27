# V4 Goal4700: Specialized Tier-3 App-Route POD Result

Date: 2026-06-25
Status: `specialized_tier3_app_route_measured_not_public_support`
Classification: `pass_app_route_gate_not_public_support`

## Result

Goal4700 implemented and ran the frozen Goal4699 app-route validation on the
current RTX A5000 POD.

Selected route:

- route: `ray_triangle_any_hit_weighted_sum_scalar_reduce`
- surface denominator: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- callback contract: Goal4697 specialized Numba C-ABI scalar callback
- cache/error scaffold: Goal4698

The specialized callback route passed the frozen app-route gate:

- exact parity passed at every size
- callback route was faster than the existing Tier-2 built-in fused route at
  every size
- callback route stayed faster than the legacy host-scalar/materialized context
  route at every size

Evidence:

- `future/v4/evidence/v4_goal4700_specialized_tier3_app_route_pod_2026-06-25.json`
- `future/v4/evidence/v4_goal4700_specialized_tier3_app_route_pod_2026-06-25.md`
- `future/v4/evidence/v4_goal4700_pod_run_2026-06-25.log`

## Measured Rows

Frozen protocol: `32768`, `131072`, `262144` rays; warmup `3`; repeat `10`.

| rays | parity | callback median s | Tier-2 built-in median s | legacy host median s | callback / Tier-2 | legacy host / callback |
|---:|---|---:|---:|---:|---:|---:|
| 32,768 | true | 0.000056944 | 0.000076484 | 0.000169979 | 0.745x | 2.985x |
| 131,072 | true | 0.000126096 | 0.000148106 | 0.000239816 | 0.851x | 1.902x |
| 262,144 | true | 0.000218816 | 0.000245476 | 0.000331175 | 0.891x | 1.513x |

Frozen bars:

- pass: `callback / Tier-2 <= 1.20x` at every size
- hard kill: any size `> 1.50x` versus Tier-2
- context: callback at least `1.20x` faster than legacy host/materialized route

## Interpretation

This is the first app-route evidence that the specialized Tier-3 path can be
useful beyond a microprobe. The route is still deliberately narrow:

- Numba C-ABI scalar callback only
- generated OptiX module specialization only
- no dynamic SBT direct-callable hot path
- no arbitrary Python callback
- no action/side-effect callback
- no external memory mutation callback

The result does not prove general callback support. It authorizes a support
candidate review packet, not public support.

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- raw OptiX callback support
- broad V4 speedup wording
- whole-application speedup wording
- V4 release or tag claims

Goal4701 should package this as a support-candidate review decision. Public
support remains blocked until external review closes the open review debt and
approves the exact wording.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The decisive comparison was against the existing Tier-2 built-in fused
   route, not only against a slow host-materialized route.

2. If yes, what action made it stupid?
   The bad action would have been to claim broad callback support from this
   narrow weighted-sum route. This report keeps public support false.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Treat this as a narrow support candidate and require review before
   public claims.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4701 should move from engineering proof to reviewed support
   candidate, with exact limitations and non-authorization boundaries.
