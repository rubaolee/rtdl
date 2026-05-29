# Goal2685 Typed-Column RT Hit-Stream Handoff Contract

Date: 2026-05-29

Status: experimental host-bridge contract and app-wiring slice complete; native device-column output, ownership/lifetime enforcement, and pod validation still required.

## Purpose

Goal2684 proved the clean architectural split:

`Python app lowering -> RTDL native ray/triangle hit stream -> Triton continuation`

The measured bottleneck was not OptiX traversal. It was the host-side hit-stream materialization and Python mapping from `primitive_id` rows into continuation input columns. Goal2685 starts the next layer: a generic typed-column handoff contract and host-row compatibility bridge. It does not yet deliver device-resident native columns; that remains the Goal2686 native/pod slice.

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

Imported the experimental Python surface through `src/rtdsl/__init__.py` for direct `rt.name` use by the RayDB research path, but kept these names out of `rtdsl.__all__` after Goal2687 review so star-import does not imply stable public API promotion.

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

- `api_maturity = "experimental_host_bridge_contract"`
- `materializes_host_rows_for_bridge = True` for the compatibility bridge
- `host_hit_rows_materialized_before_handoff = True` for the compatibility bridge
- `removes_host_materialization_bottleneck = False` for the compatibility bridge
- `native_device_hit_stream_columns_ready = False` for the bridge
- `native_device_column_output_proven_on_hardware = False`
- `true_zero_copy_authorized = False`
- `public_speedup_claim_authorized = False`

The next hardware-backed slice must make the OptiX native output itself populate/own `ray_ids` and `primitive_ids` device columns and hand those columns to Triton without first forming Python host rows.

Goal2687 fresh Claude review correctly rejected any framing that Goal2685 had already delivered device-resident handoff. Goal2688 hardening accepted that critique and changed the contract/tests accordingly:

- native-device-column constructor metadata is exercised even on CPU/mock columns;
- overflow remains fail-closed in native-device-column mode;
- payload group-id validation can avoid a full host scan only with an explicit `caller_asserted` or deferred device-validation mode;
- gather now checks `primitive_id` against `primitive_count` and fails closed on mismatch;
- count, sum, min, and max reference continuations are covered;
- Torch/CUDA gather has a capable-hardware optional test, skipped on unavailable or `sm_61` hardware;
- `native_rt_core_lowering_ready` is no longer true for the experimental RayDB path; the metadata now uses `native_rt_core_lowering_path_present=True` and keeps readiness false.

## Validation

Focused local suite:

```text
py -3 -m unittest ^
  tests.goal2685_device_resident_hit_stream_handoff_test ^
  tests.goal2684_generic_rt_hit_stream_handoff_test ^
  tests.goal2662_v2_5_partner_continuation_contract_test ^
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test ^
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
```

Result:

```text
Ran 41 tests in 0.634s
OK (skipped=5)
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
- `docs/handoff/HANDOFF_CLAUDE_GOAL2688_HIT_STREAM_CONTRACT_REREVIEW_2026-05-29.md`

Gemini Flash was attempted twice from this Windows shell, once with `auto_edit` and once with read-only `plan` mode. Both invocations stalled after terminal capability warnings and did not produce `docs/reviews/goal2686_gemini_review_goal2685_device_hit_stream_handoff_2026-05-29.md`. No Gemini review is claimed for Goal2685/2688 yet.

Fresh Claude review did complete at `docs/reviews/goal2687_claude_fresh_critical_v2_5_design_roadmap_perf_risk_review_2026-05-29.md`; Goal2688 is the implemented response to that critique. The follow-up Claude review target is `docs/reviews/goal2689_claude_rereview_goal2688_hit_stream_contract_hardening_2026-05-29.md`.

## Recommended Native Goal

After Goal2688 re-review, the next implementation slice should be the native/pod device-column path:

1. Add or expose an OptiX native output path that writes bounded `ray_ids:int64` and `primitive_ids:int64` columns into CUDA-resident buffers.
2. Preserve fail-closed overflow metadata: row count, capacity, attempted rows, overflow flag.
3. Attach ownership/lifetime metadata so the native producer keeps buffers alive through Triton continuation.
4. Reuse `RtdlHitStreamColumnHandoff` with `source_mode="native_device_columns"`.
5. Run the pod comparison between Goal2684 host-row hit stream and Goal2685/2686 device-column handoff for `count`, `sum`, `min`, `max`, and `avg_as_sum_count`.
6. Keep the claim boundary blocked until external review confirms correctness, timings, and no app-specific native vocabulary.
