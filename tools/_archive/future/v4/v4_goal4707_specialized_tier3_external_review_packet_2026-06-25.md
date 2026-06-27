# V4 Goal4707 Specialized Tier-3 External Review Packet

Date: 2026-06-25

Status: `complete_pending_external_3ai_review`

## Purpose

Consolidate Goals4696-4706 into one reviewer-friendly packet. This packet is
intended to reduce review churn: reviewers should inspect this single chain
instead of chasing eleven separate micro-goal debts.

## Candidate Under Review

Candidate label:

`specialized_numba_scalar_callback_support_candidate`

Candidate scope:

Module-specialized Numba C-ABI scalar device callback called as a direct device
function from an RTDL-generated OptiX hit-program route.

This is a constrained Tier-3 support candidate. It is not public support, not
arbitrary callback support, not raw OptiX callback support, and not a performance
claim.

## Goal Chain Summary

| goal | result | primary file |
|---|---|---|
| Goal4696 | productize constrained candidate; reject arbitrary/action/external-memory/SBT hot-path shapes | `future/v4/v4_goal4696_tier3_productization_decision_2026-06-25.md` |
| Goal4697 | internal API contract scaffold; accepted scalar shapes and fail-closed rejected shapes | `future/v4/v4_goal4697_specialized_tier3_api_contract_2026-06-25.md` |
| Goal4698 | compile/cache/error-reporting scaffold with deterministic key and stage errors | `future/v4/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.md` |
| Goal4699 | app-route protocol frozen against Tier-2 built-in denominator, not slow host only | `future/v4/v4_goal4699_specialized_tier3_app_route_protocol_2026-06-25.md` |
| Goal4700 | POD app-route passed: callback/Tier-2 ratios 0.745x, 0.851x, 0.891x at 32768/131072/262144 rays | `future/v4/v4_goal4700_specialized_tier3_app_route_pod_2026-06-25.md` |
| Goal4701 | support-candidate packet assembled; public support remains false | `future/v4/v4_goal4701_specialized_tier3_support_candidate_2026-06-25.md` |
| Goal4702 | reliability matrix protocol frozen: 20 attempts, 4 variants, dense/sparse/no-hit datasets | `future/v4/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md` |
| Goal4703 | POD reliability matrix passed: 20/20 compile/link/launch, correctness true, cache checks true | `future/v4/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.md` |
| Goal4704 | wording gate: only support-candidate wording allowed, public support/perf/release false | `future/v4/v4_goal4704_specialized_tier3_support_wording_2026-06-25.md` |
| Goal4705 | source-level PTX cache stability fixed and POD-validated across 4 variants | `future/v4/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.md` |
| Goal4706 | negative validation and bounded candidate example passed | `future/v4/v4_goal4706_negative_validation_docs_gate_2026-06-25.md` |

## Key Evidence

POD app-route evidence:

- `future/v4/evidence/v4_goal4700_specialized_tier3_app_route_pod_2026-06-25.json`
- classification: `pass_app_route_gate_not_public_support`
- correctness: true for all measured rows.
- callback/Tier-2 median ratios:
  - 32768 rays: `0.7445223616221324x`
  - 131072 rays: `0.8513881142887039x`
  - 262144 rays: `0.89139416400604x`

POD reliability evidence:

- `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.json`
- classification: `pass_reliability_gate_not_public_support`
- attempts: `20/20`
- correctness: true
- cache checks: true

POD cache-stability evidence:

- `future/v4/evidence/v4_goal4705_source_ptx_cache_stability_pod_2026-06-25.json`
- classification: `pass_source_level_cache_stability_gate_not_public_support`
- rows checked: 4 callback variants.
- raw PTX hash drift observed: true.
- canonical PTX hash stable: true.
- changed PTX/toolchain still changes key: true.

Negative validation evidence:

- `future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.json`
- rejected before compile:
  - arbitrary Python callback
  - action/side-effect callback
  - external memory mutation callback
  - dynamic SBT direct-callable hot path
  - non-scalar variable-length output

## Review Questions

1. Does the chain justify keeping `specialized_numba_scalar_callback_support_candidate` as a constrained support candidate?
2. Is the boundary strong enough: support candidate yes, public support no?
3. Is the app-route denominator in Goal4700 acceptable, especially because it compares against the existing Tier-2 built-in route rather than only a slow host route?
4. Is the Goal4703 reliability matrix sufficient for the next authorization gate?
5. Is the Goal4705 NumbaEnv `B2vN` PTX cache canonicalization safe and narrow?
6. Are the Goal4706 rejected-shape diagnostics adequate, or does the non-scalar case need a more precise error code before public support?
7. What exact remaining gates are required before any public Tier-3 support wording?

## Requested Verdict Labels

- `accept_candidate_continue_public_support_hardening`
- `accept_candidate_with_required_amendments`
- `reject_candidate_keep_spike_only`

## Explicit Non-Authorization

This packet does not authorize:

- V4 release;
- public Tier-3 support;
- arbitrary callbacks;
- raw OptiX callbacks;
- action/side-effect callbacks;
- external memory mutation callbacks;
- broad V4 speedup claims;
- app-level speed claims;
- whole-app high-performance V4 claims.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal intentionally consolidates review debt instead of multiplying
small reviewer asks.

2. If yes, what actions made the decision stupid?

Not applicable. The risk would be turning consolidation into another process
loop. The packet therefore asks for one bounded verdict and preserves exact
non-authorization.

3. Is there another path that avoids being stupid on one idea?

Yes. If reviewers are unavailable, keep the debt open and proceed only with
engineering gates that do not require public support authorization.

4. Can I start a different path that actually solves the problem?

Yes. After this packet, the next engineering path is to address reviewer
amendments or proceed to the next bounded hardening gate without claiming
release/public support.
