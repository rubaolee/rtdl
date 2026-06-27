# V4 Goal4626 Section 8 Evidence Reconciliation And Release Scorecard Protocol

Date: 2026-06-24

Status: `goal4626_protocol_current_not_release`

## Purpose

Goal4626 reconciles the already completed fixed-radius Section 8 chain and
freezes the scorecard that later V4 work must satisfy. It exists to prevent two
bad outcomes:

1. rerunning or re-planning fixed-radius work that is already on record, and
2. treating one fixed-radius success as a broad V4 performance release.

This document is a protocol and scorecard, not a release authorization.

## Fixed-Radius Section 8 Evidence Chain

| Step | Evidence | Result | Scorecard Meaning |
| --- | --- | --- | --- |
| Original whole-call Section 8 route | `future/v4/evidence/v4_section8_fixed_radius_validation_report_2026-06-24.md` | strict gate failed because summary fused route did not clear the predeclared 1.5x whole-call threshold on two serious sizes | Whole-call Python/app route is not a V4 release proof. |
| Prepared hot-path revision | `future/v4/evidence/v4_section8_prepared_hot_path_validation_report_2026-06-24.md` and `future/v4/reviews/claude_v4_section8_prepared_hot_path_review_2026-06-24.md` | prepared summary hot path passed 1.5x on all three serious sizes: 1.655x, 1.772x, 1.970x | The generic fixed-radius count-threshold continuation earns bounded prepared-session credit only. |
| Route D hand-written OptiX ceiling | `future/v4/evidence/v4_section8_route_d_handwritten_optix_ceiling_report_2026-06-24.md` and `future/v4/reviews/claude_v4_section8_route_d_handwritten_optix_ceiling_review_2026-06-24.md` | independent Route D acquired; old RTDL Python-facing paths were 192x-1140x slower than the ceiling | Near-hand-written wording is not authorized for the old product path; the blocker is product boundary, not RT-core feasibility. |
| Torch device-array front door | `future/v4/evidence/v4_section8_device_array_frontdoor_report_2026-06-24.md`, `future/v4/reviews/claude_v4_section8_fixed_radius_wrapper_surface_review_2026-06-24.md`, and `future/v4/reviews/claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md` | fixed-radius Torch CUDA device-array route passed; product-boundary gap to Route D rows reduced by 1022.93x, 3841.66x, and 9699.17x; amendment closure binds `authorized_next_step = external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive` | Fixed-radius is complete for one bounded Torch GPU-array primitive, not release-complete. Second primitive work must not start until the fixed-radius API wrapper is productized. |

## Current Fixed-Radius Claim Boundary

Authorized as internal development evidence:

- Fixed-radius count-threshold has one reviewed V4 Torch CUDA device-array front
  door.
- The device-array route keeps Python point objects and app row materialization
  out of the timed hot path.
- Under the measured boundary, it closes the old Python-facing product-boundary
  gap for this one contract.

Not authorized:

- V4 release
- V4 release-candidate status
- broad V4 speedup wording
- whole-application speedup wording
- "RTDL is near hand-written OptiX" without the fixed-radius/device-array
  boundary caveat
- CuPy performance claims
- Tier-3 callback support
- raw OptiX callback support
- true-zero-copy public wording
- C ABI / embedding / non-Python host claims
- app-specific native kernels

## Release Scorecard Frozen By Goal4626

Future V4 performance-release work must satisfy all rows below.

| Gate | Required Evidence | Current Status |
| --- | --- | --- |
| G1: fixed-radius anchor | Reviewed Section 8 chain from failed whole-call route through Torch device-array front door | `pass_bounded_one_primitive` |
| G2: operator coverage audit | Reviewed mapping from benchmark/app continuations to generic V4 operators, unsupported action shapes, or deferred/app-identity classes | `missing`; this is `goal4627` |
| G3: second Tier-2 same-contract gate | A non-fixed-radius generic Tier-2 operator selected by the coverage audit must pass correctness parity and same-contract performance evaluation on the same RT hardware; before this starts, the fixed-radius device-array API wrapper must be productized per `external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive` | `missing`; this is `goal4628`, gated by the fixed-radius wrapper productization prerequisite |
| G4: candidate status | Weighted-sum candidate must be promoted, kept candidate, or rejected by explicit review | `missing`; this is `goal4629` |
| G5: push-down model | At least one minimal declarative recognizer must route recognized generic operator requests to existing Tier-2 surfaces and fail closed for unsupported/action-shaped logic | `missing`; this is `goal4630` |
| G6: Tier-3 boundary | Tier-3 must remain spike-only unless the protocol gates all pass and a later review authorizes support | `protocol_only`; execution is `goal4631` |
| G7: final release decision | Three-review decision over scorecard, docs, scope, tests, review debt, and exact public wording | `missing`; this is `goal4632` |

## Second Tier-2 Gate Rules

Goal4628 must not be a toy measurement. The second gate must:

- use a generic operator, not an app-identity kernel;
- run at serious sizes on the same RT hardware class;
- include correctness parity;
- keep Python row objects and host result-table materialization out of the
  measured hot path;
- compare against the best available same-contract baseline;
- state whether the win source is generic Tier-2 fusion, GPU-array product
  boundary removal, both, or neither;
- fail closed if the comparison is not strong enough to support V4 performance
  wording.

## Decision Logic

If G2 and G3 pass:

- continue toward candidate resolution, push-down recognizer, and final release
  decision.

If G3 fails or is inconclusive:

- V4 remains a development-state capability surface;
- do not claim a performance release;
- do not keep adding primitives merely to avoid the negative result.

If G2 shows poor coverage:

- release wording must be coverage-limited, or V4 remains development-state.

## Goal-Level Decision Audit

1. Am I being foolish?

Not in the final Goal4626 form. The foolish path would be rerunning fixed-radius
because an older summary said the two-baseline experiment was not complete.

2. What actions would make the decision foolish?

Ignoring the existing Route D and Torch device-array evidence, or allowing a
single fixed-radius route to stand in for a catalog-wide release claim.

3. Is there a different path that avoids that failure?

Yes. Freeze the fixed-radius chain as bounded evidence, then audit coverage and
run a second non-fixed-radius Tier-2 gate.

4. Can the project now try a different path that solves the actual problem?

Yes. Goal4627 and Goal4628 test whether the fixed-radius result generalizes to a
catalog of generic V4 fused operators.

## Non-Authorization

Goal4626 does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
