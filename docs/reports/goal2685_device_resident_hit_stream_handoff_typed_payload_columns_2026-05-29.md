# Goal2685 Device-Resident RT Hit-Stream Handoff And Typed Payload Columns

Date: 2026-05-29

Status: local contract and app-wiring slice complete; pod/native device-column validation still required.

## Purpose

Goal2684 proved the clean architectural split:

`Python app lowering -> RTDL native ray/triangle hit stream -> Triton continuation`

The measured bottleneck was not OptiX traversal. It was the host-side hit-stream materialization and Python mapping from `primitive_id` rows into continuation input columns. Goal2685 starts the next layer: a generic typed-column handoff that can eventually let the native OptiX producer expose device-resident hit columns directly to Triton without Python rebuilding a large row table.

## What Changed

Added `src/rtdsl/hit_stream_handoff.py` with an app-free v2.5 handoff contract:

- `GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION`
- `GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS = ("ray_ids:int64", "primitive_ids:int64")`
- `GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS = ("primitive_group_ids:int64", "primitive_values:float64")`
- `RtdlHitStreamColumnHandoff`
- `RtdlTypedPrimitivePayloadColumns`
- `describe_generic_device_resident_hit_stream_handoff_3d`
- `prepare_generic_hit_stream_columns_from_rows`
- `prepare_generic_device_resident_hit_stream_columns`
- `prepare_generic_typed_primitive_payload_columns`
- `gather_typed_payload_columns_for_hit_stream`

Exported the new public Python surface through `src/rtdsl/__init__.py`.

Added a RayDB-style v2.5 path:

- backend label: `paper_rt_optix_device_hit_stream_triton`
- implementation: `_run_paper_rt_device_hit_stream_triton_result_mode`
- contract: RTDL still emits only generic ray/primitive hit information; app code supplies typed primitive payload columns; Triton performs generic segmented continuation.

Added pod runner:

- `scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py`

Added focused test:

- `tests/goal2685_device_resident_hit_stream_handoff_test.py`

Linux validation on `192.168.1.20` found that native Embree hit-stream results exposed the canonical schema only inside `claim_boundary`, not as a top-level `row_schema`. The Embree and OptiX Python runtime wrappers were updated to publish top-level `row_schema = ("ray_id", "primitive_id")`, and the Goal2685 test now exercises the Embree wrapper when native Embree is available.

## Boundary

This goal does not claim true zero-copy yet.

The new local bridge can wrap Goal2684 host hit rows into typed columns and then gather payload columns without rebuilding an app-shaped primitive row table. Metadata explicitly records:

- `materializes_host_rows_for_bridge = True` for the compatibility bridge
- `native_device_hit_stream_columns_ready = False` for the bridge
- `true_zero_copy_authorized = False`
- `public_speedup_claim_authorized = False`

The next hardware-backed slice must make the OptiX native output itself populate/own `ray_ids` and `primitive_ids` device columns and hand those columns to Triton without first forming Python host rows.

## Validation

Focused local suite:

```text
py -3 -m unittest ^
  tests.goal2685_device_resident_hit_stream_handoff_test ^
  tests.goal2684_generic_rt_hit_stream_handoff_test ^
  tests.goal2662_v2_5_partner_continuation_contract_test ^
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test
```

Result:

```text
Ran 26 tests in 0.532s
OK (skipped=1)
```

Compile check:

```text
py -3 -m py_compile src\rtdsl\hit_stream_handoff.py src\rtdsl\__init__.py examples\v2_0\research_benchmarks\raydb_style\rtdl_raydb_style_benchmark_app.py scripts\goal2685_raydb_device_hit_stream_handoff_pod_runner.py tests\goal2685_device_resident_hit_stream_handoff_test.py
```

Result: pass.

Runner dry-run:

```text
py -3 scripts\goal2685_raydb_device_hit_stream_handoff_pod_runner.py --dry-run
```

Result: pass, with default comparison backends:

- `paper_rt_optix_hit_stream_triton`
- `paper_rt_optix_device_hit_stream_triton`

Linux CPU/dev validation:

```text
ssh 192.168.1.20
cd ~/work/rtdl_goal2685_linux_check
PYTHONPATH=src:. python3 -m unittest tests.goal2685_device_resident_hit_stream_handoff_test tests.goal2684_generic_rt_hit_stream_handoff_test tests.goal2662_v2_5_partner_continuation_contract_test tests.goal2679_v2_5_triton_grouped_argmin_preview_test
```

Result:

```text
Ran 26 tests in 0.245s
OK (skipped=1)
```

The same Linux run confirmed Embree 4.3.0 and a real native Embree `RAY_TRIANGLE_HIT_STREAM_3D` result can feed the Goal2685 typed-column wrapper.

Local Linux OptiX SDK discovery:

- Host: `192.168.1.20`
- Existing SDK: `/home/lestat/vendor/optix-dev/include/optix.h`
- Build command: `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev`
- Result: `build/librtdl_optix.so` built successfully with CUDA 12.0 / GTX 1070

OptiX smoke:

```text
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so PYTHONPATH=src:. python3 ...
```

Result:

```text
optix_version (9, 0, 0)
backend=optix
primitive=RAY_TRIANGLE_HIT_STREAM_3D
row_schema=('ray_id', 'primitive_id')
row_count=2
rt_core_accelerated=True
native_lowering_ready=True
```

The typed-column wrapper accepted the OptiX hit-stream result and produced continuation inputs without rebuilding an app-shaped primitive row table. The compatibility bridge still records `materializes_host_rows_for_bridge=True`, so true device-column output remains the next native slice.

Local Linux partner probe:

- Torch/Triton installed into isolated target directory `.pydeps_v25_triton_probe` with `python3 -m pip install --target .pydeps_v25_triton_probe --index-url https://download.pytorch.org/whl/cu121 torch`.
- Probe result: `torch 2.5.1+cu121`, `triton 3.1.0`, CUDA visible, device `NVIDIA GeForce GTX 1070`, compute capability `(6, 1)`.
- `rt.triton_partner_available()` returned `True`.
- A small Triton segmented-sum kernel failed during PTX assembly because Triton emitted `.relaxed` instructions that require `sm_70+`.

Therefore `192.168.1.20` is useful for Linux Embree, OptiX SDK, and native wrapper smoke, but it is not accepted v2.5 Triton continuation performance evidence. The next performance run still needs a modern NVIDIA pod.

## External Review Status

Review handoff prepared:

- `docs/handoff/HANDOFF_GEMINI_GOAL2685_DEVICE_HIT_STREAM_REVIEW_2026-05-29.md`

Gemini Flash was attempted twice from this Windows shell, once with `auto_edit` and once with read-only `plan` mode. Both invocations stalled after terminal capability warnings and did not produce `docs/reviews/goal2686_gemini_review_goal2685_device_hit_stream_handoff_2026-05-29.md`. No external review is claimed yet.

## Recommended Next Goal

Goal2686 should be the native/pod slice:

1. Add or expose an OptiX native output path that writes bounded `ray_ids:int64` and `primitive_ids:int64` columns into CUDA-resident buffers.
2. Preserve fail-closed overflow metadata: row count, capacity, attempted rows, overflow flag.
3. Attach ownership/lifetime metadata so the native producer keeps buffers alive through Triton continuation.
4. Reuse `RtdlHitStreamColumnHandoff` with `source_mode="native_device_columns"`.
5. Run the pod comparison between Goal2684 host-row hit stream and Goal2685/2686 device-column handoff for `count`, `sum`, `min`, `max`, and `avg_as_sum_count`.
6. Keep the claim boundary blocked until external review confirms correctness, timings, and no app-specific native vocabulary.
