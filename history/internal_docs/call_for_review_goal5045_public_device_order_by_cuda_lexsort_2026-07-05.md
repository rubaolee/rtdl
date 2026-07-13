# Call For Review - Goal5045 Public device_order_by

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5045_public_device_order_by_cuda_lexsort_2026-07-05.md
```

Code/test changes:

```text
src/rtdsl/device_ordering.py
src/rtdsl/__init__.py
tests/goal5045_public_device_order_by_contract_test.py
```

Requested verdict labels:

```text
approve_goal5045_public_device_order_by_contract_with_pod_smoke_debt
approve_goal5045_public_device_order_by_after_pod_smoke_required
revise_goal5045_before_goal5046
fail_goal5045_app_specific_or_device_group_by_leak
```

## Context

Goal5045 is part of v2.14.4's system/API consolidation.  It should promote the already-proven generic CUDA/Thrust lexsort helper into a public RTDL `device_order_by` primitive.

It must not publish `device_group_by`.  Goal5046 is the separate decision point for grouped reduce, and the current plan says it remains internal unless a true device-resident reduce passes verification.

## Review Questions

1. Does `device_order_by` expose a generic RTDL ordering contract rather than RayJoin descriptor/carrier/output-chain semantics?
2. Is the current public dtype signature correctly limited to:

```text
i64_f64_i64_i64_lex
```

3. Are stability/determinism semantics honest, i.e. deterministic ordering depends on an explicit final tie/order key rather than a blanket stable-sort claim?
4. Does the CPU reference route correctly match `numpy.lexsort` over `(key0, key1, key2, order_key)`?
5. Does the native CUDA route wrap the existing generic helper and fail closed unless it receives a device-resident `DeviceColumnBuffer`?
6. Does the implementation avoid self-declared device residency and reject host-materialized buffers?
7. Is `device_group_by` correctly kept non-public?
8. Are public claim-boundary flags still false for speedup, true zero-copy, app-specific schema, and public grouped reduce?
9. Are local tests sufficient for API/contract shape, while acknowledging that they do not prove live POD native CUDA execution?
10. Given POD authentication failure, should Goal5045 close with explicit POD-smoke debt, or must it remain open until a reachable POD run is supplied?

## Non-Authorization Boundary

Approval of this goal does not authorize:

- public speedup wording;
- true-zero-copy wording;
- public `device_group_by`;
- RayJoin app-specific ordering semantics in core;
- claiming live POD native CUDA smoke passed unless it is rerun on an accessible POD.
