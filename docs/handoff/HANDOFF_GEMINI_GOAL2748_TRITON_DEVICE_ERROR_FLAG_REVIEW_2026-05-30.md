# Handoff: Gemini Review For Goal2748 Triton Device Error Flag

Please perform an independent read-only review of Goal2748 and write your
review to:

`docs/reviews/goal2749_gemini_review_goal2748_triton_device_error_flag_2026-05-30.md`

## Context

RTDL v2.5 is hardening generic device-resident hit-stream and partner
continuation paths. Goal2743 correctly documented a debt item: Triton grouped
continuations rejected invalid `group_ids` through a Torch CUDA predicate plus a
host scalar sync. That was fail-closed but not a device-resident error flag and
not zero-copy.

Goal2748 adds a Triton device-side invalid-group counter while preserving the
claim boundary:

- new operation: `group_id_bounds_device_flag_i64`;
- new descriptor: `describe_triton_group_id_bounds_device_flag_i64()`;
- new helper: `run_triton_group_id_bounds_device_flag_i64(...)`;
- new strict helper: `assert_triton_group_ids_in_bounds_device_flag_i64(...)`;
- opt-in grouped-operation mode:
  `TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE`;
- default grouped-operation validation remains
  `torch_cuda_precheck_host_scalar_sync`;
- true zero-copy and promoted performance claims remain false.

## Files To Inspect

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/__init__.py`
- `tests/goal2748_triton_group_id_device_error_flag_test.py`
- `tests/goal2743_triton_group_id_validation_boundary_test.py`
- `docs/reports/goal2748_triton_group_id_device_error_flag_2026-05-30.md`
- `docs/research/future_version_to_do_list.md`

## Validation Already Run By Codex

Local Windows:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2748_triton_group_id_device_error_flag_test \
  tests.goal2743_triton_group_id_validation_boundary_test \
  tests.goal2662_v2_5_partner_continuation_contract_test

Ran 18 tests in 0.007s
OK (skipped=2)
```

Pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
timeout 240 python3 -m unittest \
  tests.goal2748_triton_group_id_device_error_flag_test \
  tests.goal2743_triton_group_id_validation_boundary_test \
  tests.goal2662_v2_5_partner_continuation_contract_test

Ran 18 tests in 1.093s
OK
```

Pod broader sweep:

```text
Ran 42 tests in 0.566s
OK
```

Explicit pod smoke showed `invalid_count=2`, no-host-read device-flag metadata,
and host-raise metadata still marking host scalar sync and zero-copy claim false.

## Review Questions

1. Does Goal2748 correctly add a generic device-resident validation primitive
   without making the default Triton grouped continuation path magically
   zero-copy?
2. Are the no-host-read device-flag mode and host-scalar-raise mode clearly
   distinguished?
3. Are the public claim boundaries still conservative enough?
4. Does this close the first Goal2743 debt slice while leaving the right future
   work for event ordering and no-host-read continuation integration?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
