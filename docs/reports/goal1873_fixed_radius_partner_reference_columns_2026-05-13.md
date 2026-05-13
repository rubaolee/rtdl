# Goal1873 - Fixed-Radius Partner Reference Columns

Status: pass-with-boundary

Date: 2026-05-13

## Scope

Goal1873 adds the first fixed-radius Python+partner contract surface:

- `fixed_radius_count_threshold_2d_partner_columns(...)`
- `service_coverage_gap_flags_partner_columns(...)`
- `event_hotspot_flags_partner_columns(...)`

These functions operate on caller-supplied PyTorch/CuPy point columns and return
partner-owned output columns. The generic contract is:

`generic_fixed_radius_count_threshold_2d`

## Important Boundary

This is a partner reference/conformance path only. It does **not** call the
native RTDL engine and does **not** prove RT-core acceleration. It is the
protocol-first step needed before a native fixed-radius device-column bridge can
be added.

The metadata therefore says:

- `native_engine_row_contract: not_called_partner_reference_only`
- `direct_device_handoff_authorized: false`
- `rt_core_speedup_claim_authorized: false`
- `v2_0_release_authorized: false`
- `whole_app_speedup_claim_authorized: false`

## App Coverage

This adds partner-reference app columns for:

- `service_coverage_gaps`: household coverage and uncovered flags;
- `event_hotspot_screening`: hotspot flags using the existing app convention
  that the self-neighbor is included, so the fixed-radius threshold is
  `hotspot_threshold + 1`.

## Next Step

The next implementation step is the native bridge:

- caller-owned query/search point CUDA columns;
- prepared fixed-radius device-column scene or direct device-column call;
- partner-owned per-query count or threshold output columns;
- pod smoke and timing artifacts.

Until that bridge exists, the two fixed-radius apps remain blocked for RT-core
v2.0 timing claims.
