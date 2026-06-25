# V4 Claude Design Implementation Status And Next Goals

Date: 2026-06-24
Status: development-state status, not a release authorization

## Bottom Line

Claude's V4 design is **not fully complete as a V4 performance release**.

What is complete:

- a coherent V4 development front door
- five measured Torch CUDA Tier-2 fused/operator surfaces
- one clearly labeled Tier-2 candidate surface
- a conservative operator/callback planner
- a falsifiable Tier-3 callback protocol
- a fixed-radius Section 8 evidence chain through prepared hot path, Route D,
  and Torch device-array front door, with bounded no-release conclusions
- a final POD catalog gate proving the current development-state surface truth

What is not complete:

- the design's performance-release proof across the operator catalog; the
  fixed-radius proof is real but still one primitive, one fixture family, and
  one measured partner
- full operator-library coverage audit
- push-down recognizer beyond current explicit surfaces
- Tier-3 Numba/PTX/OptiX implementation
- release or release-candidate authorization

The current reviewed decision remains:

- `development_state_documentation_disclosure_not_release`

## Evidence Anchors

- V4 design:
  `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`
- Final development-state decision:
  `future/v4/reviews/goal4623_completion_consensus_2026-06-24.md`
- Naming cleanup:
  `future/v4/reviews/goal4624_completion_consensus_and_review_debt_2026-06-24.md`
- Development-state packet:
  `future/v4/v4_0_development_state_decision_packet_2026-06-24.md`
- Final POD catalog gate:
  `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.md`
- Tier-3 callback protocol:
  `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- Section 8 prepared hot-path outcome:
  `future/v4/reviews/claude_v4_section8_prepared_hot_path_review_2026-06-24.md`
- Route D hand-written OptiX ceiling:
  `future/v4/reviews/claude_v4_section8_route_d_handwritten_optix_ceiling_review_2026-06-24.md`
- Fixed-radius device-array front door:
  `future/v4/evidence/v4_section8_device_array_frontdoor_report_2026-06-24.md`
- Fixed-radius wrapper review:
  `future/v4/reviews/claude_v4_section8_fixed_radius_wrapper_surface_review_2026-06-24.md`

## Design-To-Implementation Matrix

| Claude design item | Status | Implemented result | Not complete / reason |
| --- | --- | --- | --- |
| V4 is the Python GPU-array RT-core lane | Partially complete | Unified `import rtdsl.v4` front door; Torch CUDA device-array surfaces are exposed through `src/rtdsl/v4.py`. | Still development-state only; no release/RC authorization. |
| Three-tier model: Tier 1 fallback, Tier 2 fused fast path, Tier 3 extension | Partially complete | Tier 2 has measured surfaces; Tier 3 has a protocol; Tier 1 remains the conceptual fallback/parity layer. | The three-tier system is not fully productized; Tier 3 is not implemented. |
| New rule: allow generic fused continuation operators, forbid app-identity kernels | Complete for current surface | Current catalog uses generic operators only; docs and gates keep app-specific native kernels unauthorized. | Future primitives must continue to be reviewed against this rule. |
| Operator push-down instead of raw OptiX callbacks | Partially complete | Planner routes recognized operators to Tier 2; scalar callback is spike-only; action-shaped callbacks are rejected. | No general expression recognizer or composite operator tree push-down yet. |
| Tier 2 fused native primitives are the main force | Substantially advanced | Five measured Torch CUDA Tier-2 surfaces: fixed-radius count-threshold, closest-hit grouped argmin, ray/triangle any-hit flags, primitive grouped-i64 reduction, point-group nearest witness. | Not all shelved primitives are promoted; coverage of app catalog is not audited. |
| Tier 2 catalog/front door | Complete as development-state | Final POD gate passed: five measured examples plus one candidate; `release_authorized: false`. | Not a release catalog. Weighted-sum remains candidate. |
| Tier 3 Numba JIT -> PTX -> OptiX module linking | Protocol complete only | Falsifiable protocol defines accepted scalar reduce shape, rejected action shapes, compile/link/correctness/overhead gates. | No Tier-3 implementation; bare PTX direct OptiX module link remains blocked. |
| Honest performance ladder | Partially complete | Docs distinguish measured/candidate/protocol-only and do not claim broad performance; fixed-radius now has a reviewed evidence ladder from failed whole-call route to prepared hot path, Route D, and GPU-array front door. | No catalog-wide performance scorecard and no second-primitive release gate yet. |
| Section 8 fixed-radius validation | Complete for one bounded primitive, not release-complete | Original whole-call app route failed; prepared hot path passed narrowly scoped credit; Route D hand-written OptiX ceiling was acquired; Torch device-array front door removed the product-boundary blocker for this fixed-radius contract. | This validates one measured fixed-radius GPU-array route only. It does not authorize broad V4 speedup wording, near-hand-written OptiX wording without caveats, CuPy performance, or a release. |
| App-catalog coverage audit | Not complete | Existing V2 primitive inventory exists as implementation map. | No reviewed percentage of workload coverage by recognized fused operators. |
| Release or release-candidate decision | Complete as No-release decision | Three-review consensus says `development_state_documentation_disclosure_not_release`. | No release approval exists; review debt remains; no public speedup wording authorized. |

## Current Concrete V4 Surface

Measured Torch CUDA Tier-2 surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`

Candidate Tier-2 surface:

1. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

Tier-3 status:

- `tier3_protocol_goal4622_spike_only_not_support`
- no API surface
- no raw OptiX callback public API
- no support claim

## Why The Current Work Is Real But Not Enough

The work is real because the POD gate executed the current catalog on RTX A5000
hardware and passed all five measured examples plus the one candidate example.
The front door, scope gate, catalog, examples, and tests agree on the same
surface truth.

It is not enough for a V4 performance release because Claude's design requires
the fixed-radius result to become a repeatable operator-library pattern rather
than a single successful surface. The current fixed-radius chain is meaningful:
it shows that a Tier-2 fused primitive plus a GPU-array front door can erase the
old Python product-boundary penalty for one contract. The release gap is now
coverage, generality, candidate status, and review-clean public wording.

## Next Goals

### `goal4626` - Section 8 Evidence Reconciliation And Release-Scorecard Protocol

Purpose:

- Reconcile the already completed fixed-radius Section 8 chain and freeze the
  release scorecard that future V4 work must satisfy.

Tasks:

- Record the strict whole-call failure, prepared hot-path credit, Route D
  ceiling, and Torch device-array front-door result in one current scorecard.
- State exactly which fixed-radius claims are authorized and which remain
  forbidden.
- Define what a second Tier-2 primitive must prove before V4 can move toward a
  performance release.
- Keep the scorecard incompatible with broad speedup, CuPy, Tier-3, and release
  claims.

Exit gate:

- Reviewed scorecard protocol exists.
- No fixed-radius experiment is rerun merely because old status wording was
  stale.
- No release claim is made.

### `goal4627` - Tier-2 Operator Coverage Audit

Purpose:

- Determine how much of the benchmark/app catalog maps to recognized generic
  fused continuation operators and choose the next high-value release gate.

Tasks:

- Map benchmark continuations to operator classes: count/threshold, any-hit,
  grouped sum/min/max/count, argmin/argmax, nearest witness, weighted sum,
  unsupported action-shaped, app-identity, or unknown.
- Report actual coverage instead of using the unverified "80%" claim.
- Select the next Tier-2 primitive/family for same-contract POD validation.

Exit gate:

- Reviewed coverage table exists.
- The next gate is tied to a high-value generic operator, not an app-specific
  route.
- No workload coverage percentage is public unless supported by the audit.

### `goal4628` - Second Tier-2 Same-Contract POD Gate

Purpose:

- Prove whether the fixed-radius outcome generalizes to a second generic Tier-2
  operator surface.

Tasks:

- Use the operator/family selected by `goal4627`.
- Freeze same-contract baselines, correctness parity, timing boundary, and pass
  threshold before running.
- Run the selected Tier-2 device-array surface on the same RT hardware.
- Compare against appropriate separated/product-boundary and native-reference
  baselines when available.
- Record whether the win source is generic Tier-2 fusion plus GPU-array
  boundary, or merely a one-off wrapper effect.

Exit gate:

- Second primitive result is validated, inconclusive, or rejected by review.
- If the second primitive fails to show a meaningful route, V4 remains
  development-state and the performance-release path pauses.

### `goal4629` - Weighted-Sum Candidate Promotion Or Rejection Decision

Purpose:

- Decide whether `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` becomes
  measured, remains candidate, or is rejected.

Tasks:

- Define promotion evidence required.
- Run any missing correctness/performance gates.
- Preserve Torch-only and OptiX-8.0 scope unless new evidence expands it.

Exit gate:

- Candidate is either promoted by review, kept candidate with reason, or
  rejected/deferred.

### `goal4630` - Push-Down Recognizer Minimum Slice

Purpose:

- Move from explicit surfaces toward the design's operator push-down model.

Tasks:

- Implement a minimal planner/recognizer for one or two declarative operator
  shapes that map to existing Tier-2 surfaces.
- Keep user model declarative.
- Do not expose raw callbacks.

Exit gate:

- Recognizer routes only recognized generic operators.
- Unsupported or action-shaped logic fails closed.

### `goal4631` - Tier-3 Stage-1/Stage-2 Spike Execution

Purpose:

- Execute the Tier-3 protocol only after the protocol is reviewed and the team
  chooses to spend resources on it.

Tasks:

- Run the compile reliability matrix.
- Attempt wrapper/direct-callable ABI route.
- Stop immediately if kill criteria fail.

Exit gate:

- Tier-3 remains unsupported unless every gate passes and later review
  authorizes a support path.

### `goal4632` - V4 Performance Release Decision

Purpose:

- Decide whether V4 can become a performance release, remains development-state,
  or must be reframed.

Tasks:

- Combine fixed-radius Section 8 evidence, second-primitive evidence, coverage
  audit, candidate status, docs, and review debt.
- Obtain 3-AI review.

Exit gate:

- One of:
  - performance release candidate authorized with exact wording and scope
  - development-state continues
  - performance-release thesis rejected or deferred

## Non-Authorization

This document does not authorize:

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
