# V4 `goal4623` Completion Consensus

Date: 2026-06-24
Status: `complete`
Decision: `development_state_documentation_disclosure_not_release`

## Goal

Run the final V4 catalog/readiness gate, clean release-facing V4 docs/examples
for the current measured/candidate truth, and produce a 3-AI reviewed
release-candidate or development-state decision without broadening claims.

## Final Decision

The current V4 work should be disclosed only as:

- `development_state_documentation_disclosure_not_release`

This means the V4 development front door is coherent enough to document as a
development state with measured/candidate labels. It is not a V4 release and
not a V4 release candidate.

## Current V4 Truth

Measured Torch CUDA Tier-2 surfaces:

1. `v4_fixed_radius_count_threshold_2d_device_arrays`
2. `v4_closest_hit_grouped_argmin_3d_device_arrays`
3. `v4_ray_triangle_any_hit_flags_2d_device_arrays`
4. `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
5. `v4_point_group_nearest_witness_2d_device_arrays`

Candidate Tier-2 surface:

1. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

Tier-3 status:

- protocol-only
- no support claim
- no raw OptiX callback public API

## Verification

Local tests:

```text
py -m unittest tests.v4_scope_gate_test tests.v4_release_candidate_packet_test tests.v4_frontdoor_test tests.v4_operator_catalog_test tests.v4_catalog_regression_gate_test tests.v4_tier3_callback_spike_protocol_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_point_group_nearest_witness_device_outputs_validation_test tests.v4_fixed_radius_docs_and_example_test
Ran 56 tests in 18.988s
OK
```

Poincare third-seat local test readback:

```text
56 tests passed in 19.781s
```

POD scope/frontdoor packet tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.v4_release_candidate_packet_test tests.v4_scope_gate_test tests.v4_frontdoor_test
Ran 11 tests in 1.454s
OK
```

POD final GPU catalog gate:

- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.md`
- status: `passed`
- mode: `gpu`
- measured examples: `5/5` passed
- candidate examples: `1/1` passed as candidate
- release_authorized: `false`

Scope gate:

- `future/v4/v4_0_scope_gate.md`
- `future/v4/evidence/v4_goal4623_scope_gate_current_2026-06-24.json`
- validation status: `passed`
- included measured surfaces: `5`
- candidate surfaces: `1`
- release_authorized: `false`

## Review Seats

### Claude

Record:

- `future/v4/reviews/claude_v4_goal4623_development_state_decision_review_2026-06-24.raw.md`

Verdict:

- `development_state_documentation_disclosure_not_release`

Summary:

- Five measured surfaces and one candidate are consistently represented.
- Final POD GPU catalog gate supports development-state documentation disclosure.
- No overclaims found.
- Stopping at development-state disclosure is appropriate.
- No required amendments.

### Antigravity

Record:

- `future/v4/reviews/antigravity_v4_goal4623_development_state_decision_review_2026-06-24.raw.md`

Verdict:

- `development_state_documentation_disclosure_not_release`

Summary:

- Release authorization remains false.
- Five measured surfaces and one candidate are accurately represented.
- No broad, Tier-3, raw callback, C ABI, CuPy, or app-specific kernel claims are authorized.

### Poincare Internal Third Seat

Verdict:

- `development_state_documentation_disclosure_not_release`

Summary:

- No blocking findings.
- Five measured Torch CUDA Tier-2 surfaces plus one candidate are represented consistently.
- Final POD GPU catalog gate supports disclosure.
- No unauthorized release/RC/broad speedup/whole-app speedup/true-zero/Tier-3/raw callback/CuPy/C ABI/non-Python/app-kernel claims found.

## Non-Authorization

This completion record does not authorize:

- V4 release
- V4 release-candidate status
- broad V4 speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels

## Naming Cleanup

- The development-state packet has been renamed by `goal4624` to
  `future/v4/v4_0_development_state_decision_packet_2026-06-24.md`.
  External raw review files may still mention the old filename as historical
  text and should not be rewritten.
