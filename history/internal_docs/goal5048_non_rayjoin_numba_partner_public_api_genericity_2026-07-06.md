# Goal5048 - Non-RayJoin Numba PartnerContinuation Public API Genericity

Date: 2026-07-06

Status:

```text
completed_non_rayjoin_public_numba_partner_api_genericity__pod_cuda_smoke_pending
```

## Purpose

Goal5048 verifies that the public `NumbaPartnerContinuation` API added in
Goal5047 is not RayJoin-shaped.  The proof uses a non-RayJoin ray/triangle hit
stream shape and the public `DeviceColumnBuffer` + Numba partner-continuation
contract.

This goal is a genericity/contract gate.  It is not a performance goal.

## Implementation

Added:

```text
tests/goal5048_non_rayjoin_numba_partner_public_api_genericity_test.py
```

No production source files were changed.

## What The Test Proves

The new test covers three boundaries.

### 1. Public API accepts non-RayJoin hit-stream columns

The test builds a `DeviceColumnBuffer` with:

```text
producer = ray_triangle_hit_stream
columns  = ray_ids, primitive_ids
```

It then plans and runs a public Numba continuation:

```text
operation      = uint32_equal_mask
input binding  = values -> primitive_ids
scalar input   = target
```

The mocked runner assertion proves the public wrapper binds:

```text
values = buffer.columns["primitive_ids"]
target = 7
```

This verifies that the public API can consume a non-RayJoin primitive-output
column shape without app-shaped rows, output chains, or overlay structures.

### 2. Legacy grouped/segmented Numba exports remain outside the public contract

The test records the current export-hygiene fact:

- lower-level `NUMBA_GROUPED_*` and `NUMBA_SEGMENTED_*` constants still exist as
  historical lower-level exports;
- none of their operation values appears in
  `NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS`;
- trying to route them through `numba_partner_continuation(...)` fails closed;
- `device_group_by` remains absent from `rt` and `rt.__all__`.

This keeps the Goal5046 decision intact: grouped reduce is not public-ready in
v2.14.4.

### 3. Optional live CUDA smoke is present but skipped locally

The test includes a real OptiX ray/triangle hit-stream -> `DeviceColumnBuffer`
-> public Numba wrapper smoke.  It is skipped unless OptiX + Numba CUDA are
available locally.

Local result:

```text
Could not find platform independent libraries <prefix>
..s......
----------------------------------------------------------------------
Ran 9 tests in 0.009s

OK (skipped=1)
```

The skip is expected in the local environment and remains a POD debt before any
runtime or performance claim.

## Verification Command

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5048_non_rayjoin_numba_partner_public_api_genericity_test tests.goal5047_numba_partner_continuation_public_api_test
```

Result:

```text
Could not find platform independent libraries <prefix>
..s......
----------------------------------------------------------------------
Ran 9 tests in 0.009s

OK (skipped=1)
```

## Claim Boundary

Authorized:

```text
non_rayjoin_public_api_shape_proven
legacy_grouped_exports_not_in_public_partner_contract
device_group_by_still_not_public
local_structural_and_mocked_execution_tests_pass
```

Not authorized:

```text
POD_CUDA_runtime_success
public_speedup_claim
true_zero_copy_claim
device_group_by_public_ready
RayJoin_specific_partner_API
replacement_of_RT_traversal
```

## Next

The next useful step is Goal5049: migrate one RayJoin paper-reproduction app
path to the public `DeviceColumnBuffer` + `device_order_by` +
`NumbaPartnerContinuation` surface, while preserving the existing v2.14.3
performance boundary and not reviving stopped device-resident performance
claims.
