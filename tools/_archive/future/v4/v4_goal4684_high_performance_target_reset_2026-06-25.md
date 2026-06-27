# V4 Goal4684 High-Performance Target Reset

Date: 2026-06-25

Status: `goal4684_no_clean_existing_tier2_app_target_select_tier3_wrapper_spike_protocol`

## Decision

No clean existing Tier-2/app target remains for a near-term formal high-performance V4 release.

The next legitimate V4 architecture track is the Tier-3 wrapper/direct-callable ABI spike. This is selected because it is genuinely absent from V2.14, app-name-free, and directly addresses the user problem that Tier-2 cannot solve: custom scalar callback logic that does not fit recognized push-down operators.

This does not authorize Tier-3 support, raw OptiX callbacks, POD, public speedup wording, or V4 release.

## Candidate Disposition

| Target | Disposition | Reason |
| --- | --- | --- |
| Existing benchmark app route selection | `no_clean_target` | Goal4672 found V2.14 already had a primitive or explicit mixed partner route for every promoted benchmark app. |
| RTDBSCAN fixed-radius/grouped-union | `no_go` | Goals4670/4671 found only modest gains; the best true grouped-union probe stayed below the 1.20x second-win bar and V2.14 already had the core route. |
| Ranked fixed-radius summary / RTNN | `deferred` | Goal4678 deferred the candidate after serious-scale parity or below-parity evidence. |
| Shape-pair relation active count | `no_promotion` | Goal4681 passed correctness but failed speed bars: V4/V2.14 hot `0.963x` and wall `0.605x`. |
| Contact/witness device columns | `no_go` | Goal4683 found the target reuses V2.14 bounded collect-k and current exact-witness partner-column plumbing. |
| Aggregate-frontier device columns | `measured_productization_win_not_second_v4_over_v3_win` | Goal4676 removed a V2.14 host-frontier bottleneck but was parity with V3.0.2 hot path at `0.998x`. |
| Tier-3 wrapper/direct-callable ABI | `selected_as_spike_only_next_track` | It is the remaining V4 design path that is genuinely absent from V2.14, app-name-free, and directly addresses custom scalar callback logic. |

## Why This Is The Correct Reset

Continuing to search the already-audited app list would repeat the V3/V4 failure mode: wrapping known routes, measuring parity/productization, then trying to describe that as high-performance progress.

The three-tier design says the real V4 levers are:

- Tier-2 fused primitives for recognized operators;
- Tier-3 constrained callback injection for scalar per-hit reduce logic.

Current Tier-2 candidates are either measured/productized, deferred for parity, blocked as app-specific, or already present in V2.14. Tier-3 is the only remaining architecture lever that is both new and central to the V4 design.

## Goal-Level Decision Audit

1. Was I being stupid?

Partly. The stupid path would be to keep trying more existing app wrappers after Goal4672, Goal4681, and Goal4683 already showed that those routes are mostly V2.14/productization territory.

2. If yes, what action made it stupid?

The risky action was treating each new wrapper-shaped target as if it might become a V4 speed source without first proving it was absent from V2.14.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. Stop selecting existing app targets unless they have a proven absent lever, and move to a different V4 architecture lever: Tier-3 wrapper/direct-callable ABI.

4. Can I now try the different path that actually solves the problem?

Yes. Goal4685 must create the real wrapper/direct-callable ABI protocol gate. It must not repeat the failed bare-PTX `optixModuleCreate` probe.

## Goal4685 Boundary

Goal4685 is authorized only as protocol/local gate work.

It must:

- define the real OptiX traversal shell or direct-callable ABI composition target;
- reuse the existing Tier-3 protocol rather than weakening it;
- require Numba PTX to enter a semantic OptiX module, not a bare helper module;
- preserve planner fail-closed behavior;
- keep action-shaped callbacks rejected/deferred;
- block all release/support/speed claims.

It must not:

- run POD before the protocol is frozen;
- expose raw OptiX callbacks as public API;
- turn Tier-3 into a V4.0 support claim;
- use app-specific native kernels;
- repeat the old bare-PTX `optixModuleCreate` probe.

## Non-Authorization

Goal4684 does not authorize formal high-performance V4 release, POD spending, implementation, Tier-3 public support, raw OptiX callback support, public speedup wording, whole-app speedup wording, or app-specific native kernels.
