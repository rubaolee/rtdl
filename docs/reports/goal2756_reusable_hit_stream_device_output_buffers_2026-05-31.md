# Goal2756: Reusable Hit-Stream Device Output Buffers

Date: 2026-05-31

Status: implemented and pod-smoked

## Purpose

Goal2754 showed that the current generic OptiX hit-stream plus Triton
continuation path is correct but far slower than the fused prepared grouped
primitive for low-hit-count scalar grouped reductions. One avoidable cost was
that the native hit-stream device-column API allocated and released its output
columns on every run.

Goal2756 adds a generic caller-owned output-buffer path:

- Python creates reusable CUDA `int64` tensors for `ray_ids` and
  `primitive_ids`.
- The OptiX native path writes directly into those caller-owned device columns.
- The returned `RtdlHitStreamColumnHandoff` borrows the same tensors and records
  the caller-owned lifetime model.

This is generic runtime work. It does not add app-specific native hooks.

## Implementation

Native OptiX:

- Added `rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns`.
- Refactored the existing native-owned output path through a shared
  `run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix`.
- Preserved the existing native-owned allocation/release API for callers that
  need it.
- Added fail-closed validation: caller-owned nonzero capacity requires nonzero
  `ray_ids` and `primitive_ids` device pointers.

Python RTDSL:

- Added `PreparedOptixHitStreamDeviceColumnBuffers`, a caller-owned CUDA tensor
  carrier for reusable `ray_ids:int64` and `primitive_ids:int64` output columns.
- Added
  `PreparedOptixStaticTriangleScene3D.prepare_ray_triangle_hit_stream_device_column_buffers`.
- Added
  `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_into_device_columns`.
- Extended hit-stream handoff metadata with:
  - `caller_owned_output_buffers`
  - `reusable_output_buffers_used`
- Kept `producer_consumer_stream_ordering="host_synchronized_before_consumer"`.
- Kept `true_zero_copy_authorized=False`.

## Pod Evidence

Artifact:

- `docs/reports/goal2756_pod_artifacts/goal2756_reusable_hit_stream_device_output_buffers_69_30_85_171_2026-05-31.json`

Environment:

- Host: `69.30.85.171`
- GPU: NVIDIA RTX A5000
- OptiX library: `/root/rtdl/build/librtdl_optix.so`

Observed smoke result:

- `row_count`: `1`
- `overflow`: `false`
- `ray_ids`: `[7]`
- `primitive_ids`: `[0]`
- handoff `ray_ids.data_ptr()` equals reusable buffer `ray_ids.data_ptr()`
- handoff `primitive_ids.data_ptr()` equals reusable buffer
  `primitive_ids.data_ptr()`
- `pointer_identity_preserved`: `true`
- neutral-buffer seam lifetime: `caller_retained`
- nested neutral-buffer `native_producer`: `false`, because the native path
  writes into caller-owned memory rather than owning the buffers
- `host_synchronization_used`: `true`
- `true_zero_copy_authorized`: `false`

## Validation

Local Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/hit_stream_handoff.py src/rtdsl/__init__.py tests/goal2756_reusable_hit_stream_device_output_buffers_test.py tests/goal2746_optix_hit_stream_host_sync_ordering_test.py
OK

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2706_native_optix_hit_stream_device_columns_test tests.goal2746_optix_hit_stream_host_sync_ordering_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test
Ran 14 tests in 0.174s
OK (skipped=1)

$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2756_reusable_hit_stream_device_output_buffers_test tests.goal2752_hit_stream_zero_copy_ordering_metadata_test tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 14 tests in 0.052s
OK (skipped=1)
```

Pod:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
build/librtdl_optix.so rebuilt successfully

PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python3 -m unittest \
  tests.goal2756_reusable_hit_stream_device_output_buffers_test \
  tests.goal2706_native_optix_hit_stream_device_columns_test \
  tests.goal2746_optix_hit_stream_host_sync_ordering_test \
  tests.goal2752_hit_stream_zero_copy_ordering_metadata_test
Ran 14 tests in 2.064s
OK

PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
python3 -m unittest \
  tests.goal2756_reusable_hit_stream_device_output_buffers_test \
  tests.goal2752_hit_stream_zero_copy_ordering_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 14 tests in 1.903s
OK
```

## Boundary

This goal proves a reusable caller-owned output-column path for one generic
OptiX hit-stream primitive on real hardware. It reduces one runtime overhead
source: per-run native output allocation and release.

This goal does not authorize:

- true zero-copy wording;
- no-sync producer/consumer wording;
- public speedup claims;
- a claim that generic hit-stream continuation is faster than fused primitives;
- v2.5 release promotion.

The next generic hit-stream work remains:

- event/same-stream ordering evidence;
- fused gather plus continuation;
- device-resident row-count/overflow handling;
- scale/performance probes that measure the reusable-buffer path against the
  Goal2754 baseline.
