# Goal808 Segment/Polygon Native OptiX Mode App Propagation

## Result

Goal808 propagates the explicit segment/polygon OptiX mode surface beyond the raw hit-count example.

The road-hazard app and compact segment/polygon any-hit app outputs can now request the same experimental native hit-count path through public CLI/API arguments.

## What Changed

- `/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py` now accepts `--optix-mode auto|host_indexed|native`.
- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_anyhit_rows.py` now accepts `--optix-mode auto|host_indexed|native`.
- `segment_polygon_anyhit_rows` allows `native` only for compact `segment_flags` and `segment_counts` outputs, because the existing native OptiX candidate is a hit-count path, not a pair-row emitter.
- `rows` mode rejects `--optix-mode native` explicitly rather than silently making a false native row-output claim.

## Boundary

This is app-surface propagation only. It does not promote road hazard or segment/polygon any-hit rows to NVIDIA RT-core claim status.

The native hit-count path must still pass Goal807 strict RTX gating before any readiness matrix promotion or public speedup statement.

## Local Verification

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal808_segment_polygon_app_native_mode_propagation_test tests.goal807_segment_polygon_optix_mode_gate_test tests.goal806_segment_polygon_optix_mode_surface_test tests.goal692_optix_app_correctness_transparency_test -v
python3 -m py_compile examples/rtdl_road_hazard_screening.py examples/rtdl_segment_polygon_anyhit_rows.py tests/goal808_segment_polygon_app_native_mode_propagation_test.py
git diff --check
```

Result: 17 tests OK, `py_compile` OK, and `git diff --check` OK.

Portable CLI smoke checks also passed:

```bash
PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference --output-mode summary --copies 2
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --output-mode segment_counts --copies 2
```
