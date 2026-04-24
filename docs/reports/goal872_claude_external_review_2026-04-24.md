---

## ACCEPT

- **New device-emitter path is correctly isolated**: `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded` is a distinct `extern "C"` symbol that routes to `run_seg_poly_anyhit_rows_optix_native_bounded`; the original `rtdl_optix_run_segment_polygon_anyhit_rows` is untouched and still calls `run_seg_poly_anyhit_rows_optix_host_indexed` (api.cpp:321 vs 347).
- **Any-hit kernel semantics are correct**: `atomicAdd(params.output_count, 1u)` claims a slot; writes the pair only if `slot < output_capacity`; falls through to `atomicExch(params.overflowed, 1u)` on overflow — no silent truncation without a flag (core.cpp:1597–1602).
- **Bounded copy is wired end-to-end**: After `optixLaunch`, the host path does `std::min<size_t>(emitted, output_capacity)` before the device-to-host download, preventing out-of-bounds writes (workloads.cpp:1428).
- **No readiness overclaim**: `recommended_status` is `device_emitter_implemented_pending_real_optix_gate` and the boundary section explicitly forbids RT-core promotion until a real OptiX artifact passes the gate.
- **Evidence checks are heuristic substring matches** (script lines 23–30), which is consistent with this packet series' convention but would not catch a rename or refactor — acceptable at this stage since the gate itself requires a real build.
