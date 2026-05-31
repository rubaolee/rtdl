# Goal2696 V2.5 Partner Support Matrix

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2692 and Goal2694

## Purpose

Goal2696 makes the v2.5 partner-choice envelope explicit. The neutral buffer
seam lets an app choose a partner per boundary, but the runtime also needs a
declared `(partner x operation)` matrix so unsupported choices fail closed
instead of becoming undefined behavior.

This goal is a no-pod contract and planning milestone. It does not run or tune
new partner kernels.

## What Changed

Added `src/rtdsl/v2_5_partner_support_matrix.py` with:

| Surface | Purpose |
| --- | --- |
| `V25PartnerSupportCell` | One machine-readable `(operation, partner)` support cell. |
| `v2_5_partner_support_cells()` | Enumerates every current v2.5 operation against every allowed partner. |
| `v2_5_partner_support_matrix()` | Returns the full matrix plus claim boundaries and policy flags. |
| `plan_v2_5_partner_support(operation, partner)` | Returns the exact cell for a requested app boundary choice. |
| `validate_v2_5_partner_support_matrix(...)` | Ensures the matrix covers every required cell and does not authorize public claims. |

The symbols are imported at `rtdsl` module scope for internal/experimental use
but are intentionally not added to `rtdsl.__all__`.

## Matrix Policy

| Partner | Matrix status |
| --- | --- |
| `python_reference` | Universal correctness reference for every continuation operation. |
| `triton` | Preview-not-promoted for every operation in `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`; unsupported cells fail closed; preview rows require CUDA and `sm_70+`. |
| `numba` | Preview-not-promoted only for `segmented_count_i64` and `segmented_sum_f64`; all other operation cells fail closed. |
| `cupy_conformance` | Descriptor/conformance cells for most operations; Goal2774 adds a narrow preview-not-promoted cell for `hit_stream_grouped_ray_id_primitive_i64`. |

Every cell records:

- neutral buffer seam version;
- continuation contract version;
- execution backend label;
- whether CUDA or `sm_70+` is required;
- whether the neutral seam is required;
- same-contract reference requirement;
- `promoted_performance_path=False`;
- `rt_traversal_replacement_allowed=False`;
- `public_speedup_claim_authorized=False`;
- `true_zero_copy_claim_authorized=False`.

## Validation

Added `tests/goal2696_v2_5_partner_support_matrix_test.py`.

Initial Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 15 tests in 0.008s
OK
```

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 72 tests in 7.638s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\v2_5_partner_support_matrix.py \
  src\rtdsl\__init__.py tests\goal2696_v2_5_partner_support_matrix_test.py
OK
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`a3e244648903dc594cd2182a163cd10122afc2f2`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 72 tests in 2.514s
OK (skipped=5)

python3 -m py_compile src/rtdsl/v2_5_partner_support_matrix.py \
  src/rtdsl/__init__.py tests/goal2696_v2_5_partner_support_matrix_test.py
OK
```

The test covers:

- full `(allowed partner x continuation operation)` coverage;
- reference cells are universal; Triton preview cells are operation-specific and claim-bounded;
- Numba preview is intentionally narrow;
- CuPy conformance cells are descriptor-only except the explicit Goal2774 grouped hit-stream preview, not promoted;
- support-matrix symbols are experimental and absent from `rtdsl.__all__`.

## Boundary

Goal2696 does not:

- add new Triton, Numba, or CuPy kernels;
- prove benchmark performance;
- authorize a release claim;
- force any partner;
- replace RTDL/OptiX traversal with partner code;
- authorize zero-copy claims.

## Next Work

1. Use `plan_v2_5_partner_support(...)` inside benchmark planning code so app
   choices are checked against the declared envelope.
2. Add conformance tests for actual runnable cells when a pod is available.
3. Begin the native OptiX CUDA-resident hit-column implementation only after
   the matrix and neutral seam are both reviewed.
