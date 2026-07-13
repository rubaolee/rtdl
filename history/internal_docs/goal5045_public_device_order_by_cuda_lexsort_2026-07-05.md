# Goal5045 - Public device_order_by

Date: 2026-07-05

Status:

```text
implemented_public_device_order_by_cuda_lexsort__pod_smoke_blocked_by_auth
```

## Purpose

Goal5045 promotes the generic native CUDA/Thrust lexsort capability into a public RTDL ordering primitive.  This goal is deliberately narrow:

- expose public `device_order_by`;
- define the currently supported dtype signature;
- define deterministic ordering semantics;
- keep `device_group_by` internal/not public;
- avoid RayJoin, descriptor-carrier, output-chain, or app-specific semantics in the public API.

## Implementation

Modified files:

```text
src/rtdsl/device_ordering.py
src/rtdsl/__init__.py
tests/goal5045_public_device_order_by_contract_test.py
```

New public symbols:

```text
DEVICE_ORDER_BY_CONTRACT_VERSION
DEVICE_ORDER_BY_API_MATURITY
DEVICE_ORDER_BY_SUPPORTED_SIGNATURES
DEVICE_ORDER_BY_BACKENDS
DEVICE_ORDER_BY_CLAIM_BOUNDARY
DeviceOrderByResult
describe_device_order_by_contract
device_order_by
device_order_by_reference_i64_f64_i64_i64
validate_device_order_by_contract
```

Current public signature:

```text
i64_f64_i64_i64_lex
```

Semantics:

- lexicographic ascending over four declared key columns;
- dtype order is `int64, float64, int64, int64`;
- the fourth key is an explicit final tie/order key;
- RTDL does not claim stable sort by backend implementation; deterministic stability is the caller's responsibility via the explicit final tie key.

Backends:

```text
cpu_reference
native_cuda
```

The `native_cuda` route wraps the existing generic helper:

```text
rtdl_cuda_sort_i64_f64_i64_i64_lex
```

via:

```text
optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device(...)
```

The wrapper requires a public `DeviceColumnBuffer`, checks device residency metadata, validates dtype/row-count compatibility, extracts CUDA pointers through `__cuda_array_interface__`, and fails closed for host-materialized buffers.

## Claim Boundary

The contract keeps these false:

```text
release_authorized
public_speedup_claim_authorized
true_zero_copy_claim_authorized
app_specific_schema_allowed
device_group_by_public_claim_authorized
```

This goal does not publish `device_group_by`.  Goal5046 must decide that separately, and only after a true device-resident reduce path passes verification.

## Verification

Local contract and regression run:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5045_public_device_order_by_contract_test tests.goal5043_public_device_column_buffer_contract_test tests.goal5044_public_prepared_geometry_session_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
.................
----------------------------------------------------------------------
Ran 17 tests in 0.092s

OK
```

Existing native lexsort bridge/regression run:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5019_native_lexsort_bridge_test tests.goal5033_descriptor_consumer_native_lexsort_test
```

Result:

```text
Could not find platform independent libraries <prefix>
......
----------------------------------------------------------------------
Ran 6 tests in 0.013s

OK
```

Core API leak scan:

```powershell
rg -n "rayjoin|RayJoin|output_chain|descriptor_pair|carrier|device_group_by" src/rtdsl/device_ordering.py tests/goal5045_public_device_order_by_contract_test.py
```

Only allowed hits:

- `device_group_by` appears as an explicit non-authorization flag and test assertion;
- no RayJoin, output-chain, descriptor-pair, or carrier semantic appears in `src/rtdsl/device_ordering.py`.

POD smoke:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=8 root@157.157.221.29 -p 22051 "echo pod-ok"
ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/id_ed25519 root@157.157.221.29 -p 22051 "echo pod-ok"
```

Result:

```text
root@157.157.221.29: Permission denied (publickey,password).
```

POD correctness/performance smoke was therefore not run in this goal.  This must not be misreported as a native CUDA runtime pass.  The local tests verify the public contract, CPU reference semantics, dtype/device-residency fail-closed behavior, and the native wrapper call boundary through a mocked native helper.

## What This Proves

- RTDL now has a public `device_order_by` contract.
- The public API exposes only the proven `i64,f64,i64,i64` lexicographic signature.
- CPU reference semantics match `numpy.lexsort`.
- The native CUDA wrapper is generic and optional.
- Host-materialized buffers cannot use the `native_cuda` route.
- `device_group_by` is not public.

## What This Does Not Prove

- It does not prove a new POD native CUDA performance number.
- It does not prove public `device_group_by`.
- It does not prove true zero-copy.
- It does not authorize public speedup wording.
- It does not make RayJoin app descriptor/carrier logic part of RTDL core.

## Next

Request external review.  If the reviewer requires POD smoke before closing Goal5045, rerun on a reachable POD and update this report with the native CUDA result.  Otherwise, close Goal5045 as public API/local contract complete with POD smoke debt explicitly recorded.
