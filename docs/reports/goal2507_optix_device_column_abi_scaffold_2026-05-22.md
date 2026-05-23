# Goal2507 OptiX Device-Column ABI Scaffold

Date: 2026-05-22

## Summary

Goal2507 adds the first native OptiX C ABI scaffold for partner-resident
columnar payloads. This is not an execution implementation. It is a fail-closed
symbol and struct definition so the next implementation step has a stable native
target without weakening the Goal2505/Goal2506 claim boundary.

native execution remains unauthorized.

## Native Surface Added

Header: `src/native/optix/rtdl_optix_prelude.h`

Added constants:

- `kRtdlDevicePayloadDeviceCuda`
- `kRtdlDevicePayloadDtypeInt64`
- `kRtdlDevicePayloadDtypeUint32`
- `kRtdlDevicePayloadDtypeFloat64`

Added struct:

```c
struct RtdlDevicePayloadField {
    const char* name;
    uint32_t kind;
    uint32_t dtype;
    uint32_t device_type;
    uint32_t device_id;
    size_t element_count;
    size_t stride_bytes;
    uint64_t device_ptr;
};
```

Added C API declaration and definition:

```c
int rtdl_optix_columnar_payload_create_from_device_columns(...);
```

The implementation currently sets `dataset_out` to null and returns through the
normal native error path with a message that includes `fail-closed ABI scaffold`
and `partner-resident columnar native execution is not implemented`.

## Why This Is Safe

The scaffold does not call the existing host-column builder and does not stage a
device-resident table back to host. It exists only to make the ABI name and
descriptor shape explicit.

The Python requirements packet still reports:

```text
blocked_pending_optix_device_column_abi
```

The reason is that an executable ABI requires more than a public symbol. It
still needs device-side AABB/metadata preparation or an equivalent no-hidden-copy
strategy, device-side exact predicate evaluation, and device-side grouped
count/sum reduction.

## Claim Boundary

No speedup, zero-copy, SQL, or DBMS claim is authorized by this scaffold.

Authorized wording:

- RTDL has a fail-closed native ABI scaffold for future OptiX device-column
  payloads.
- Goal2505 partner-resident descriptors remain metadata only.
- Native partner-resident execution remains blocked until the symbol is backed
  by real device-side execution.

Forbidden wording:

- RTDL executes partner-resident RayDB-style columnar payloads natively in OptiX.
- RTDL has true zero-copy columnar DB execution.
- RTDL has a SQL/DBMS engine.
- RTDL has whole-app RayDB speedups.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2507_optix_device_column_abi_scaffold_test
```

Expected result:

```text
4 tests OK
```

Combined RayDB-style local validation through Goal2507:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2497_raydb_style_embree_count_sum_parity_test \
  tests.goal2498_raydb_style_optix_count_sum_parity_test \
  tests.goal2499_raydb_style_lowering_plan_test \
  tests.goal2500_raydb_style_backend_matrix_runner_test \
  tests.goal2501_raydb_style_optix_pod_results_test \
  tests.goal2502_raydb_style_benchmark_slice_closeout_test \
  tests.goal2503_direct_columnar_record_set_preparation_test \
  tests.goal2504_columnar_typed_host_buffer_handoff_test \
  tests.goal2505_partner_resident_columnar_descriptor_contract_test \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test \
  tests.goal2507_optix_device_column_abi_scaffold_test
```

Observed result:

```text
61 tests OK, 4 skipped
```

## Next Implementation Target

The next meaningful target is not more descriptor metadata. It is a real
device-side numeric slice:

- validate `RtdlDevicePayloadField` inputs
- build or encode row metadata without host table staging
- evaluate predicates on device columns
- reduce count and int64 sum by one group key on device
- return compact rows to host only as final API output
