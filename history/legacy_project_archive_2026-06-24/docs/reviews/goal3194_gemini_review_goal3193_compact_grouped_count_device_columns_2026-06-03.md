# Independent Gemini Review for Goal3193 Compact Grouped-Count Device Columns

**Date:** 2026-06-03

## Context

Goal3191 added dense direct-address grouped-count device columns. Goal3193 builds on that with compact grouped-count device columns:

- native ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity`
- release ABI:
  `rtdl_optix_release_device_grouped_count_i64_compact_columns`
- Python front door:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id_compact_device_columns(...)`
- Python output:
  `OptixNativeDeviceGroupedCountI64CompactOutput`

The compact output keeps two SoA columns resident on CUDA:

- `group_key[]`
- `count[]`

It materializes only the row-count scalar on host so Python can know the valid prefix length. It does not materialize the compact columns on host except in the pod validation script, where CuPy copies are used only to compare against the exact-row oracle.

## Questions Answered

### 1. Does Goal3193 remain app-agnostic in the native layer, with no RayJoin or app-specific native logic?

**Answer:** Yes.
The `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md` report explicitly states in its "Boundary" section that "This is a generic compact grouped-count continuation. It does not add app-specific native logic and it does not add a new RayJoin path." This is further confirmed by the `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json` pod artifact, which lists `claim_boundary.rayjoin_specific_native_logic_added: false`. Additionally, the Python test `tests/goal3193_compact_grouped_count_device_columns_test.py` includes assertions to ensure that "rayjoin" and "intersection_point" are not present in the Python front door code, validating the app-agnostic nature.

### 2. Does it reuse the existing grouped-count kernel and add only a generic compact-count-columns kernel?

**Answer:** Yes.
The `src/native/optix/rtdl_optix_workloads.cpp` file contains both the existing `device_column_grouped_i64_kernel` and the newly added `device_column_grouped_i64_compact_count_columns_kernel`. The `ensure_device_column_grouped_i64_pipeline` function in this file demonstrates that the existing kernel is loaded for general grouped operations, while the new compact-count-columns kernel is specifically loaded for compaction. The `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md` report explicitly confirms this by stating: "Reused the existing grouped-count kernel. Added only a generic compact-count-columns kernel that converts dense `count[group_id]` into compact SoA columns."

### 3. Is the compact output boundary correct: native-owned CUDA `group_key[]` and `count[]` columns, host row-count scalar only, direct-address `group_capacity` before compaction, and no exact intersection witness rows?

**Answer:** Yes.
The `src/native/optix/rtdl_optix_prelude.h` defines `RtdlNativeDeviceGroupedCountI64CompactColumns` to include `group_keys_device_ptr` and `counts_device_ptr` (both `ctypes.c_uint64`, indicating CUDA device pointers), along with a `row_count` member for the host-side scalar. The Python `OptixNativeDeviceGroupedCountI64CompactOutput` class in `src/rtdsl/optix_runtime.py` corroborates this by exposing these attributes and explicitly setting `row_count_materialized_on_host: True` and `group_key_column_materialized_on_host: False`, `count_column_materialized_on_host: False` in its metadata. It also specifies `group_capacity_semantics: "direct-address key capacity before compaction"`. The `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md` report and the `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json` pod artifact consistently confirm these details, including the absence of exact intersection witness rows.

### 4. Does Python provide safe ownership/release and bounded CuPy views for both compact columns?

**Answer:** Yes.
The `src/rtdsl/optix_runtime.py` file demonstrates safe ownership and release through the `_OptixNativeDeviceGroupedCountI64CompactColumnsOwner` class, which implements `__enter__`, `__exit__`, and `close` methods to manage the lifetime of the native CUDA resources. This class utilizes the `rtdl_optix_release_device_grouped_count_i64_compact_columns` native ABI for releasing resources. For bounded CuPy views, the `OptixNativeDeviceGroupedCountI64CompactOutput` class provides `as_cupy_group_keys` and `as_cupy_counts` methods. These methods leverage `cupy.cuda.UnownedMemory` and `cupy.cuda.MemoryPointer`, which create CuPy arrays directly from the device pointers without copying data to the host. The `_OptixNativeDeviceGroupedCountI64CompactColumnsOwner` instance is passed to `UnownedMemory`, ensuring that the underlying CUDA memory is managed and released appropriately only when the CuPy arrays are no longer in use, thus providing safe and bounded views.

### 5. Is the direct-address key-capacity limitation documented and tested, including the pod negative probe where `group_capacity=64` overflows for IDs `200..215`?

**Answer:** Yes.
The direct-address key-capacity limitation is thoroughly documented and tested. The `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md` report explicitly states that the implementation "fail closed when keys exceed the caller's direct-address capacity" and provides a detailed description of the negative probe: "Negative probe: `group_capacity=64` overflowed and returned no resident compact output because left IDs `200..215` exceed the direct-address capacity." The `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json` pod artifact further confirms this by showing `negative_probe.group_capacity_64_overflow: true` and `negative_probe.reason: "left_id values 200..215 exceed direct-address capacity 64"`. The `tests/goal3193_compact_grouped_count_device_columns_test.py` unit test also includes an assertion specifically checking for this negative probe behavior.

### 6. Does the pod artifact support only bounded claims: live authored smoke, compact device column residency, CuPy validation copy only, no true zero-copy claim, no release authorization, no public speedup claim, and no RayJoin-specific native logic?

**Answer:** Yes.
The `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md` report explicitly lists the bounded claims: `release_authorized: False`, `public_speedup_claim_authorized: False`, `rt_core_speedup_claim_authorized: False`, `true_zero_copy_claim_authorized: False`. It also clarifies that compact group/count columns are not materialized on the host except for validation purposes, and no app-specific (e.g., RayJoin) native logic is added. The `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json` pod artifact confirms all these points: `claim_boundary.release_authorized: false`, `claim_boundary.public_speedup_claim_authorized: false`, `claim_boundary.rt_core_speedup_claim_authorized: false`, `claim_boundary.true_zero_copy_claim_authorized: false`, and `claim_boundary.rayjoin_specific_native_logic_added: false`. The `live_smoke` section of the pod artifact indicates `all_match_exact_rows: true`, `compact_count_result_device_resident: true`, and `compact_columns_materialized_for_validation_only: true`, verifying the live authored smoke and CuPy validation copy aspects.

## Verdict

**`accept-with-boundary`**

The implementation is real and pod-proven for bounded compact columns. Broader downstream device-to-device continuations, public speedup claims, true zero-copy claims, and release authorization remain explicitly out of scope, as confirmed by the claim boundaries in the report and pod artifact. The design adheres to the specified constraints, reuses existing components where appropriate, and introduces new generic functionality responsibly with proper validation and error handling for capacity limitations.