# Goal2688 Hit-Stream Handoff Contract Hardening After Fresh Claude Review

Date: 2026-05-29

Status: implemented locally; external re-review requested next.

## Purpose

Goal2687 fresh Claude review accepted the v2.5 direction but rejected the
over-strong framing that Goal2685 had delivered device-resident hit-stream
handoff. Claude's key point was correct: the current code defines a typed-column
contract and host-row compatibility bridge. It does not yet remove the
host-materialization bottleneck, does not yet prove CUDA-resident native columns,
and does not yet enforce native buffer ownership/lifetime.

Goal2688 turns that critique into executable guardrails before the native
Goal2686-style implementation begins.

## Changes

Code:

- `src/rtdsl/hit_stream_handoff.py`
  - added `GENERIC_HIT_STREAM_HANDOFF_API_MATURITY = "experimental_host_bridge_contract"`;
  - added source-mode and group-id-validation mode constants;
  - added metadata fields:
    - `api_maturity`;
    - `host_hit_rows_materialized_before_handoff`;
    - `removes_host_materialization_bottleneck`;
    - `native_device_column_output_proven_on_hardware`;
    - `ownership_lifetime_model`;
    - payload `group_id_bounds_validation`;
    - payload `host_scan_for_group_id_validation`;
    - payload `device_group_id_validation_pending`;
    - payload `default_primitive_values_used`;
    - gather `primitive_id_bounds_checked`;
  - added fail-closed primitive-id range validation before payload gather;
  - added explicit `group_id_bounds_validation` control so future CUDA paths can avoid a full host group-id scan only by declaring a caller-asserted or deferred device-check contract.

- `src/rtdsl/__init__.py`
  - keeps the experimental names importable as `rt.name` for the RayDB research path;
  - removes the experimental hit-stream handoff names from `rtdsl.__all__` so star-import no longer implies stable public API promotion.

- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
  - changes the experimental RayDB device-hit-stream path from `native_rt_core_lowering_ready=True` to:
    - `native_rt_core_lowering_path_present=True`;
    - `native_rt_core_lowering_ready=False`.

Tests:

- `tests/goal2685_device_resident_hit_stream_handoff_test.py`
  - checks the contract is explicitly experimental and host-bridge-only;
  - exercises the `source_mode="native_device_columns"` constructor as a bounded contract path;
  - checks native-device-column overflow remains fail-closed;
  - verifies payload group-id host-scan skipping requires an explicit bounds contract and `group_count`;
  - records the default count-value convenience in metadata;
  - verifies primitive-id out-of-range gather fails closed;
  - verifies gathered columns feed count, sum, min, and max reference continuation modes;
  - includes an optional Torch/CUDA gather test for capable `sm_70+` hardware;
  - verifies experimental direct attributes are importable but not present in `rtdsl.__all__`.

Docs:

- `docs/reports/goal2685_device_resident_hit_stream_handoff_typed_payload_columns_2026-05-29.md`
  - retitled/reframed as a typed-column RT hit-stream handoff contract;
  - states explicitly that Goal2685 is a host-row bridge only;
  - lists the new machine-readable boundary fields.

- `docs/rtdl_primitive_catalog.md`
  - marks the typed-column handoff layer as experimental;
  - records that native CUDA device-column output, ownership/lifetime enforcement, pod timing, and external review remain required before zero-copy or speedup claims.

## Claude Findings Response

| Goal2687 finding | Goal2688 response | Status |
| --- | --- | --- |
| Goal2685 name/framing overclaimed device residency. | Report and catalog now frame it as an experimental typed-column contract plus host bridge. Metadata says `removes_host_materialization_bottleneck=False` for the bridge. | Addressed |
| Host bridge does not remove the measured host-materialization bottleneck. | Structured metadata now records host hit rows were materialized before handoff and the bottleneck was not removed. | Addressed |
| Native-device-column constructor was untested. | Added CPU/mock constructor test for `source_mode="native_device_columns"` and metadata. | Addressed as contract test; hardware evidence still pending |
| Payload group-id validation forced host sync on CUDA tensors. | Added explicit validation modes. Host scan remains default; future CUDA paths can use `caller_asserted` or deferred device validation without a full host scan. | Partially addressed; device error-flag validation remains future work |
| Gather lacked primitive-id bounds check. | Added fail-closed primitive-id range validation before gather. | Addressed |
| Only sum mode was exercised. | Added reference count, sum, min, and max continuation coverage over gathered columns. | Addressed |
| Torch/CUDA gather branch untested. | Added optional capable-hardware test, skipped unless Torch CUDA and `sm_70+` are available. | Test hook added; pod execution still pending |
| Public exports implied stability. | Experimental names remain direct attributes but are removed from `rtdsl.__all__`. | Addressed |
| Ownership/lifetime was metadata-only. | Metadata now says native owner state machine is required before promotion. Actual state-machine implementation remains the next native goal. | Boundary documented; not implemented |
| "ready" wording could leak into public claims. | Experimental RayDB path now uses `native_rt_core_lowering_path_present=True` and `native_rt_core_lowering_ready=False`. | Addressed for this path |

## Remaining Work Before Native Device-Column Promotion

1. Define the native ownership/lifetime state machine: allocation owner, retention through partner continuation, release point, overflow cleanup, and failure cleanup.
2. Implement OptiX native CUDA-resident `ray_ids:int64` and `primitive_ids:int64` output buffers.
3. Attach those buffers to `RtdlHitStreamColumnHandoff` with `source_mode="native_device_columns"` and a real native owner object.
4. Add a device-side validation/error-flag path for payload group-id bounds so `caller_asserted` is not the only no-host-scan route.
5. Run `sm_70+` pod validation for count, sum, min, max, and average-as-sum-count with phase timings.
6. Request fresh Claude review and Gemini review before any zero-copy, removed-bottleneck, or performance wording is allowed.

## Claim Boundary

Goal2688 does not deliver true zero-copy, device-resident native output, or a new
speedup claim. It makes the current contract honest, stricter, and harder to
misuse before the native device-column implementation starts.
