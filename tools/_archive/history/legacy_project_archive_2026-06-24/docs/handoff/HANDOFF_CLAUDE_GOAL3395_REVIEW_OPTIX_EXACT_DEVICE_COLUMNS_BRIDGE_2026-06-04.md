# Handoff: Claude Review Goal3394 OptiX Exact Device Columns Bridge

Please perform a read-only external review of Goal3394.

## Context

Your Goal3393 review accepted with boundary the Goal3390 negative probe and the
Goal3391/3392 Python/CuPy exact-row bridge. It agreed that the next primitive
direction is a generic native exact relation stream or richer relation-witness
stream, not another tolerance parameter or app-shaped special case.

Codex then implemented the first native bridge step:

- Native ABI:
  `rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d`
- Release ABI:
  `rtdl_optix_release_point_closed_shape_membership_exact_device_columns_2d`
- Python method:
  `PreparedOptixPointClosedShapeMembership2D.exact_device_columns(points)`

This bridge calls the existing exact host-refined membership implementation
inside the OptiX backend and uploads the exact `(point_id, shape_id)` pairs into
native-owned CUDA device columns. It is intentionally *not* a device-only exact
predicate and does *not* authorize true-zero-copy claims.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3394_optix_exact_membership_device_columns_live_probe.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md`
- `tests/goal3394_optix_exact_membership_device_columns_bridge_test.py`

## Validation Already Run By Codex

Pod build at commit `97297f6c`:

```bash
make build-optix
```

Result: passed, produced `build/librtdl_optix.so`.

Pod live probe after metadata correction at commit `87a2acbb`:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
  python3 scripts/goal3394_optix_exact_membership_device_columns_live_probe.py \
  --output docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json
```

Result summary:

- exact host rows: 11316
- exact device-column rows: 11316
- pairs match exact: true
- missing: 0
- extra: 0
- device resident: true
- overflow: false

Focused pod tests at commit `389dafbd`:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python3 -m unittest \
  tests.goal3394_optix_exact_membership_device_columns_bridge_test \
  tests.goal3392_exact_membership_bridge_live_probe_test \
  tests.goal3391_host_refined_exact_membership_partner_columns_bridge_test \
  tests.goal3390_boundary_event_signal_4096_negative_probe_test
```

Result: `Ran 11 tests ... OK`.

## Review Questions

1. Is the native ABI app-agnostic and correctly named as a generic
   point/closed-shape membership exact device-column bridge?
2. Is the implementation boundary honest: host-refined exact rows are used
   inside the native bridge, exact pair columns are native-owned/device-resident,
   and device-only exact predicate production remains false?
3. Does the Python method and metadata correctly avoid candidate-stream drift
   after the metadata correction?
4. Does the live 4096-chain probe prove exact pair identity and device residency?
5. Are all release/public-speedup/RayJoin/RT-core/true-zero-copy/default-route
   claims blocked correctly?
6. What remains before this can graduate from bridge to final primitive:
   device-only exact predicate, robust double/GEOS parity, relation witnesses,
   other datasets, overflow handling, or something else?

## Output

Write the review to:

`docs/reviews/goal3395_claude_review_optix_exact_device_columns_bridge_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
