# Call For Review - Goal5047 Numba PartnerContinuation Public API

Date: 2026-07-06

Review target:

```text
history/internal_docs/goal5047_numba_partner_continuation_public_api_2026-07-06.md
src/rtdsl/numba_partner_api.py
src/rtdsl/__init__.py
tests/goal5047_numba_partner_continuation_public_api_test.py
```

## Requested Verdict Labels

```text
approve_goal5047_numba_partner_continuation_public_api_with_pod_smoke_debt
revise_goal5047_before_goal5048
fail_goal5047_app_specific_or_hidden_host_fallback
```

## Context

Goal5047 promotes the existing Numba continuation assets into a small public RTDL
partner-continuation contract over `DeviceColumnBuffer`.

This is a v2.14.4 system/API consolidation goal. It is not a RayJoin app
optimization and not a public performance claim.

The implementation intentionally keeps `device_group_by` outside the public
surface per Goal5046. Grouped/segmented reduce kernels remain internal until a
device-resident grouped-reduce contract passes POD verification.

## Review Questions

1. Does the public API consume `DeviceColumnBuffer` inputs rather than app-shaped
   Python rows or RayJoin overlay data structures?
2. Is the public operation set generic enough for v2.14.4, and does it correctly
   exclude public `device_group_by` / grouped reduce?
3. Does host-materialized input fail closed unless `allow_host_fallback=True` is
   explicitly provided?
4. Does the runner bind explicit logical inputs, scalar inputs, and options to
   existing Numba continuation runners rather than duplicating kernels or
   introducing a raw-kernel API?
5. Does the local no-CUDA behavior remain explicit (`skipped_cuda_unavailable`)
   and non-authorizing?
6. Are the claim-boundary flags correct and conservative: no RT traversal
   replacement, no raw-kernel requirement, no public speedup claim, no
   true-zero-copy claim, and no app-specific semantics?
7. Do the tests sufficiently cover the API contract, fail-closed behavior,
   CUDA-unavailable skip, and mocked runner binding?
8. Is it correct to leave a POD CUDA smoke as a follow-up debt before using this
   API in a performance or end-to-end claim?

## Non-Authorization

This review must not authorize:

```text
public_speedup_claim
true_zero_copy_claim
raw_numba_kernel_user_api
device_group_by_public_ready
RayJoin_specific_partner_API
replacement_of_RT_traversal
POD_CUDA_runtime_success
```
