# Call For Review: `goal4620` Weighted-Sum Candidate Completion

Date: 2026-06-24
Author: Codex
Status: completion review request; not a release authorization

## Verdict Requested

Please review whether `goal4620` is complete as a candidate implementation:

`v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

Allowed verdict labels:

- `accept_goal4620_complete_candidate_not_promoted`
- `accept_with_required_amendments`
- `reject_goal4620_incomplete`
- `reject_goal4620_scope_violation`

Completion requires 3-AI consensus or explicit review debt. This packet asks
for external review; it does not self-close the goal.

## Prior Authorization

Claude accepted the replacement fallback selection with amendments:

- `future/v4/reviews/claude_v4_goal4620_replacement_fallback_selection_review_2026-06-24.raw.md`

Consensus and Amendment 1 verification:

- `future/v4/reviews/goal4620_replacement_fallback_selection_consensus_2026-06-24.md`

The candidate was authorized only as a candidate surface. Measured-catalog
promotion, release wording, true-zero-copy wording, CuPy performance claims,
OptiX 9.1 scope, Tier-3 callback work, and C ABI / embedding work remain
unauthorized.

## Implemented Scope

Code:

- `src/rtdsl/v4_ray_triangle.py`
  - added
    `V4_RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_DEVICE_ARRAY_SURFACE`
  - added
    `ray_triangle_any_hit_weighted_sum_3d_device_array_claim_boundary_v4`
  - added
    `allocate_ray_triangle_any_hit_weighted_sum_3d_device_array_output_v4`
  - added
    `V4RayTriangleAnyHitWeightedSum3DDeviceArraySession`
  - added
    `prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4`
  - default stream handling creates a nonzero Torch CUDA stream because the
    native graph executor rejects stream pointer `0`
- `src/rtdsl/v4_operator_catalog.py`
  - added weighted-sum as a Tier-2 candidate, not measured
  - planner returns `tier2_fused_operator_candidate` for Torch and no CuPy
    performance surface
- `src/rtdsl/v4.py`
  - exported the candidate front door
  - front-door claim boundary now reports `5` measured surfaces and `1`
    candidate surface

Examples / validation:

- `future/v4/examples/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py`
- `scripts/v4_ray_triangle_weighted_sum_device_output_validation.py`
- `scripts/v4_catalog_regression_gate.py`
  - default gate still runs measured examples
  - `--include-candidates` explicitly includes the weighted-sum candidate

Tests:

- `tests/v4_ray_triangle_device_array_api_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_catalog_regression_gate_test.py`

Docs:

- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`

## Claude Amendments Closure

### Amendment 1: Verify Existing Executor Metadata Before Implementation

Closed in:

- `future/v4/reviews/goal4620_replacement_fallback_selection_consensus_2026-06-24.md`

The existing executor method and metadata were verified before implementation.

### Amendment 2: Scene-Preparation Ownership Metadata

Implemented in the claim boundary and run metadata:

- `scene_preparation_ownership:
  caller_initiated_v4_prepare_static_triangle_scene_from_device_triangle_columns`
- `scene_data_residency:
  rtdl_owned_prepared_optix_scene_from_caller_device_triangle_columns`

### Amendment 3: Output Scalar Allocation Policy

Implemented:

- primary path: RTDL-allocated Torch CUDA `uint64[1]` scalar
- caller override: supported through `run(output_scalar=...)`
- metadata records `output_scalar_allocation` as either
  `rtdl_allocated_default` or `caller_supplied_override`

The POD example and catalog gate exercise the RTDL-allocated default path.
The POD validation script exercises the caller-supplied override path for
repeat measurement stability.

## POD Evidence

Primary candidate gate:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`

Result summary:

| Rays | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Same-Contract Ratio |
|---:|---|---:|---:|---:|
| 32768 | true | 0.000068050 | 0.000139300 | 2.047x |
| 131072 | true | 0.000146613 | 0.000228226 | 1.557x |

Catalog integration gate:

- `future/v4/evidence/v4_goal4620_catalog_gate_gpu_32768_include_weighted_sum_candidate_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_catalog_gate_gpu_32768_include_weighted_sum_candidate_2026-06-24.md`

Gate summary:

- status: `passed`
- examples: `10`
- measured examples: `5`
- candidate examples: `1`
- weighted-sum candidate status: `candidate_gate_passed`
- release authorized: `false`

## Local Verification

Local Windows structure/docs tests:

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_ray_triangle_device_array_api_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
Ran 31 tests ... OK

py -m unittest tests.v4_operator_catalog_test tests.v4_ray_triangle_device_array_api_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test tests.v4_fixed_radius_docs_and_example_test
Ran 39 tests ... OK
```

POD structure tests:

```text
python3 -m unittest tests.v4_operator_catalog_test tests.v4_ray_triangle_device_array_api_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
Ran 31 tests ... OK
```

POD smoke:

- `future/v4/examples/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --ray-count 8192`
- correctness: `true`
- weighted sum: `33558528`
- metadata: `device_output_used: true`,
  `host_scalar_read_before_consumer: false`,
  `cuda_stream_ptr_nonzero: true`

## Goal-Level Decision Audit

1. Am I being foolish by asking for completion review now?
   No. The agreed candidate was implemented, amendment gates were closed, and
   both local and POD evidence exist.
2. What would make this foolish?
   Claiming measured-catalog promotion or V4 release from candidate evidence.
   This packet explicitly does neither.
3. Is there another path that avoids process churn?
   Yes. Ask for one completion review packet with the evidence above, then
   either close with 3-AI consensus/debt or apply specific amendments.
4. Can I solve the problem differently?
   Yes. If reviewers reject completion, keep the surface candidate-only and
   patch the specific missing gate rather than starting another candidate search.

## Reviewer Questions

1. Does the implementation stay within the Claude-authorized Candidate A scope?
2. Are all three Claude amendments closed?
3. Is the POD evidence sufficient for candidate completion, while still
   insufficient for measured-catalog promotion?
4. Are the catalog/front-door/docs updates honest: `5 measured / 1 candidate`,
   no release wording, no broad speedup wording?
5. Is the nonzero stream fix correct and properly bounded?
6. May `goal4620` be marked complete as a candidate implementation, pending
   the required 3-AI completion consensus or explicit review debt?

## Non-Authorization

This packet does not authorize:

- measured-catalog promotion
- V4 release or release-candidate status
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy wording
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- app-specific native kernels
