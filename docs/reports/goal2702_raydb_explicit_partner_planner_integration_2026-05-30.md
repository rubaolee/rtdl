# Goal2702 RayDB Explicit Partner Planner Integration

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2698 and Goal2700

## Purpose

Goal2702 wires the new v2.5 planning and explicit gather surfaces into a real
benchmark app path: the RayDB-style paper RT device-hit-stream continuation.

Before this goal, the app used the default gather behavior. After this goal,
the app records whether it requested `python_reference` or `triton`, and it
stores one support-matrix-backed hit-stream partner plan for each generic
continuation operation in the mode.

## What Changed

In
`examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`,
`_run_paper_rt_device_hit_stream_triton_result_mode(...)` now:

1. Computes `continuation_plan = describe_raydb_v2_5_partner_continuation(mode)`.
2. Chooses `requested_gather_partner = "python_reference"` when
   `allow_reference_fallback=True`, otherwise `"triton"`.
3. Builds `v2_5_hit_stream_partner_plans` by calling
   `rt.plan_v2_5_hit_stream_partner_continuation(...)` for each generic
   continuation operation.
4. Calls `rt.gather_typed_payload_columns_for_hit_stream(...)` with the explicit
   `partner=requested_gather_partner` argument.
5. Emits `requested_gather_partner` and `v2_5_hit_stream_partner_plans` in the
   app metadata.

## Validation

Added `tests/goal2702_raydb_explicit_partner_planner_integration_test.py`.

Initial Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2690_post_goal2689_contract_honesty_test
Ran 31 tests in 1.131s
OK (skipped=1)
```

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 83 tests in 7.970s
OK (skipped=5)

py -3 -m py_compile examples\v2_0\research_benchmarks\raydb_style\rtdl_raydb_style_benchmark_app.py \
  tests\goal2702_raydb_explicit_partner_planner_integration_test.py
OK
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`591d6fb273fed1e00e6b6cc6d7b063b998086fce`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 83 tests in 2.601s
OK (skipped=5)

python3 -m py_compile examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py \
  tests/goal2702_raydb_explicit_partner_planner_integration_test.py
OK
```

The new integration test checks the CPU/reference fallback path because that
path is no-pod. It verifies:

- `requested_gather_partner == "python_reference"`;
- handoff metadata records `requested_gather_partner` and
  `selected_gather_partner`;
- the partner plan selects `python_reference`;
- the plan is not fail-closed;
- zero-copy and speedup claims remain false.

## Boundary

Goal2702 does not:

- validate the Triton/Torch carrier path on hardware;
- implement native OptiX CUDA hit-column output;
- claim zero-copy or speedup;
- make RayDB app logic part of the native engine.

## Next Work

1. Run the expanded focused suite on Windows and local Linux.
2. When a pod is available, run the same app path with `allow_reference_fallback=False`
   so the explicit `partner="triton"` gather path is exercised on real CUDA.
