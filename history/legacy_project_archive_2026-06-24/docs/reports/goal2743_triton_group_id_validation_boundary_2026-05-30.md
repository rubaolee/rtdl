# Goal2743 - Triton Group-ID Validation Boundary

Date: 2026-05-30

Status: local Codex implementation complete; pod validation pending.

## Purpose

The v2.5 reviews correctly flagged that group-id validation must not be
described as a fully device-resident error-flag path. The current Triton preview
kernels do reject out-of-range group ids before launch, but they do so with a
Torch CUDA predicate followed by a host scalar sync.

Goal2743 makes that boundary visible in the Triton descriptors and runtime
result metadata.

## Change

`src/rtdsl/triton_partner_continuation.py` now records:

- `TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE =
  "torch_cuda_precheck_host_scalar_sync"`
- `TRITON_GROUP_ID_BOUNDS_DEVICE_ERROR_FLAG_AVAILABLE = False`
- `group_id_bounds_validation` metadata in Triton operation descriptors.
- `group_id_bounds_validation` metadata in Triton runtime result records.

For operations that use group ids, the metadata states:

- bounds are checked before kernel launch;
- the check uses a host scalar sync;
- no device-resident error flag is available yet;
- true-zero-copy claims remain unauthorized.

For `compact_mask_i64`, the metadata states group-id validation is not
applicable.

## Why This Matters

This does not add a new kernel. It prevents future documentation, benchmark
summaries, or release reports from silently treating the current correctness
precheck as a zero-copy-compatible device validation path.

The future stronger form is a device-resident validation/error-flag primitive
that can keep the continuation pipeline on-device without a host scalar sync.
That remains future v2.x work.

## Validation

Local Windows validation:

```text
py -3 -m unittest \
  tests.goal2743_triton_group_id_validation_boundary_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2696_v2_5_partner_support_matrix_test
19 tests OK

py -3 -m py_compile src/rtdsl/triton_partner_continuation.py \
  tests/goal2743_triton_group_id_validation_boundary_test.py
clean
```

Pod validation on `root@69.30.85.171:22167` after pulling commit `a5dbe3d5`:

```text
python3 -m unittest \
  tests.goal2743_triton_group_id_validation_boundary_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2696_v2_5_partner_support_matrix_test
19 tests OK
```

## Boundary

- No native ABI changed.
- No performance claim is authorized.
- No true-zero-copy claim is authorized.
- This is metadata honesty around an existing correctness precheck, not a new
  device validation primitive.
