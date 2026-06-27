# Call For Review: V4 `goal4621` Catalog Hardening Completion

Date: 2026-06-24
Author: Codex
Status: completion review request; not a release authorization

## Verdict Requested

Please review whether `goal4621` is complete:

`goal4621` — Tier-2 catalog hardening

Allowed verdict labels:

- `accept_goal4621_complete_not_release`
- `accept_with_required_amendments`
- `reject_goal4621_incomplete`
- `reject_goal4621_scope_violation`

Completion still requires 3-AI consensus or explicit review debt. This packet
asks for review; it does not self-close the goal.

## Intended Scope

`goal4621` was authorized by the reviewed `goal4615`-`goal4623` goal sequence.
Its purpose is to make the V4 front door and operator catalog hard to misread.

The goal does **not** authorize:

- V4 release
- measured-catalog promotion
- broad V4 speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- CuPy performance claims
- Tier-3 callback support
- raw OptiX callback support
- C ABI / embedding / non-Python-host work
- app-specific native kernels

## Implemented Changes

### 1. Programmatic Catalog Rows Are Explicit

Changed:

- `src/rtdsl/v4_operator_catalog.py`

Measured and candidate catalog rows now expose consistent machine-readable
fields:

- `catalog_class`
- `surface_status`
- `partner_claim_status`
- `direct_device_input_columns`
- `direct_device_output_columns`
- `direct_device_output_scalar`
- `host_materialization_in_hot_path`
- `true_zero_copy_authorized`
- `release_claim_authorized`
- `broad_v4_speedup_claim_authorized`
- `whole_app_speedup_claim_authorized`
- `tier3_callback_claim_authorized`
- `raw_optix_callback_claim_authorized`
- `cupy_performance_claim_authorized`
- `embedding_c_abi_claim_authorized`
- `non_python_host_binding_claim_authorized`
- `app_specific_native_kernel_authorized`

The measured rows use:

- `catalog_class: measured`
- `surface_status: tier2_measured_pod_validated_not_release`

The weighted-sum candidate row uses:

- `catalog_class: candidate`
- `surface_status: tier2_candidate_goal4620_not_measured`
- `partner_claim_status: candidate_goal4620_gate_passed_not_measured`

### 2. Front-Door Boundary Is Explicit

Changed:

- `src/rtdsl/v4.py`
- `future/v4/examples/v4_frontdoor_quickstart.py`

The unified front door now exposes:

- `5` measured surfaces
- `1` candidate surface
- `true_zero_copy_authorized: false`
- broad / whole-app / Tier-3 / raw callback / CuPy / embedding / non-Python-host
  / app-kernel authorization flags as false

### 3. Public Metadata Sanitizes True-Zero Authorization Flags

Changed:

- `src/rtdsl/v4_fixed_radius.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4_point_group.py`

The wrappers still preserve direct-device facts such as device pointers,
device-resident outputs, and no host materialization in the hot path. However,
any public metadata field shaped like `*true_zero_copy_authorized` is cleared to
`false` before leaving the V4 wrapper. This prevents native direct-device
evidence from being misread as a public V4 true-zero-copy claim.

This specifically fixed a POD gate failure where fixed-radius and any-hit flags
still emitted nested `true_zero_copy_authorized: true` fields from older native
metadata.

### 4. Catalog Gate Recursively Rejects Forbidden Claims

Changed:

- `scripts/v4_catalog_regression_gate.py`

The gate now recursively rejects:

- `true_zero_copy_authorized: true`
- `raw_optix_callback_claim_authorized: true`

in addition to the pre-existing forbidden flags.

### 5. User-Facing V4 Docs No Longer Point At Old RC State

Changed:

- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

The front-door docs now describe the current V4 development state:

- `5` measured Torch CUDA Tier-2 surfaces
- `1` weighted-sum candidate
- weighted-sum candidate gate and completion consensus closed
- weighted-sum still not measured/promoted
- release authorization still false

Removed stale current-front-door wording that pointed users at the older
release-candidate packet or said the weighted-sum candidate still needed POD
validation and completion review.

### 6. Tests Harden The Boundary

Changed:

- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_ray_triangle_device_array_api_test.py`

New/updated assertions check:

- measured/candidate status fields exist on all catalog rows
- all non-authorization flags remain false
- quickstart reports `5` measured and `1` candidate
- README does not include stale `Current candidate packet` wording
- any-hit flags keep direct device output true while true-zero-copy
  authorization stays false

## Verification

### Local Unit Tests

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_catalog_regression_gate_test tests.v4_fixed_radius_docs_and_example_test tests.v4_point_group_nearest_witness_device_outputs_validation_test
Ran 43 tests ... OK
```

### Local Dry-Run Catalog Gate

```text
py scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16 --include-candidates --json-out future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.json --md-out future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.md
status: passed
examples: 10
```

Evidence:

- `future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.json`
- `future/v4/evidence/v4_goal4621_catalog_dry_run_hardened_include_candidates_2026-06-24.md`

### POD Structure Tests

POD:

- `NVIDIA RTX A5000`
- driver: `570.195.03`

```text
python3 -m unittest tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_ray_triangle_device_array_api_test tests.v4_point_group_device_array_api_test tests.v4_catalog_regression_gate_test
Ran 34 tests ... OK
```

### POD GPU Catalog Gate

```text
python3 scripts/v4_catalog_regression_gate.py --mode gpu --copies 32768 --ray-count 32768 --include-candidates --json-out future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.json --md-out future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.md
status: passed
examples: 10
```

Evidence:

- `future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.json`
- `future/v4/evidence/v4_goal4621_catalog_gpu_hardened_include_candidates_32768_2026-06-24.md`

POD example summary:

| Example | Status | Passed |
| --- | --- | --- |
| `fixed_radius` | `measured` | `true` |
| `closest_hit_grouped_argmin` | `measured` | `true` |
| `ray_triangle_any_hit_flags` | `measured` | `true` |
| `primitive_grouped_i64_reduction` | `measured` | `true` |
| `point_group_nearest_witness` | `measured` | `true` |
| `v4_frontdoor_quickstart` | `ok` | `true` |
| `operator_callback_planning_tier2` | `tier2_measured_ready` | `true` |
| `operator_callback_planning_scalar_callback` | `tier3_spike_only_not_v4_0_release_surface` | `true` |
| `operator_callback_planning_complex_callback` | `rejected_action_shaped_callback_deferred` | `true` |
| `ray_triangle_any_hit_weighted_sum_candidate` | `candidate_gate_passed` | `true` |

The gate recursively found no forbidden true claim flags in current evidence.

## Goal-Level Decision Audit

1. Am I being foolish by asking for completion review now?
   No. `goal4621` is catalog/front-door hardening, and both local and POD gates
   pass after the true-zero metadata leak was fixed.
2. What would make this decision foolish?
   Treating catalog hardening as release authorization or measured promotion.
   This packet explicitly does neither.
3. Is there another path that avoids process churn?
   Yes. Ask for one completion review packet with evidence, then either close
   with 3-AI consensus/debt or patch specific reviewer amendments.
4. Can I solve the problem differently?
   If reviewers reject completion, patch the named catalog/doc/gate gap. Do not
   start a new operator or performance route inside `goal4621`.

## Reviewer Questions

1. Does the implementation stay within `goal4621` scope?
2. Are measured, candidate, and deferred statuses now explicit enough for users
   and reviewers?
3. Is the true-zero metadata sanitizer correct: direct-device facts remain, but
   public true-zero-copy authorization flags are false?
4. Does the updated gate appropriately reject forbidden claim flags?
5. Are README and `tier2_operator_catalog.md` now clean current-front-door docs
   rather than old RC/history pointers?
6. Is the POD evidence sufficient for `goal4621` completion while still
   insufficient for V4 release or measured promotion?
7. May `goal4621` be marked complete pending 3-AI consensus or explicit review
   debt?

## Non-Authorization

This packet does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- public true-zero-copy wording
- OptiX 9.1 claims
- CuPy performance claims
- Tier-3 callback support
- raw OptiX callback support
- C ABI / embedding / non-Python-host work
- app-specific native kernels

