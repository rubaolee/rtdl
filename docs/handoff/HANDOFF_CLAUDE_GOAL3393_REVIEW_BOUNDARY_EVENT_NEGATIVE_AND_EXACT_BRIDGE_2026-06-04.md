# Handoff: Claude Review Goals3390-3392 Boundary-Event Negative And Exact Bridge

Please perform a read-only external review of Goals 3390, 3391, and 3392.

## Context

Goal3388 showed that a first-boundary-event tolerance signal matched exact
membership rows on 512/1024/2048 chain slices. Your Goal3389 review accepted
that with boundary and requested larger/full slices plus more tolerance evidence.

Codex then did:

- Goal3390: 4096-chain negative probe showing the Goal3388 signal fails.
- Goal3391: bounded helper
  `materialize_closed_shape_membership_rows_as_cupy_columns`, which uploads exact
  host-refined membership rows into CuPy columns with explicit no-zero-copy and
  no-native-exact-stream metadata.
- Goal3392: live pod probe on the same 4096 slice proving the Goal3391 bridge
  preserves all exact `(point_id, shape_id)` pairs.

## Files To Inspect

- `docs/reports/goal3390_boundary_event_signal_4096_negative_probe_2026-06-04.json`
- `docs/reports/goal3390_boundary_event_signal_4096_negative_probe_2026-06-04.md`
- `tests/goal3390_boundary_event_signal_4096_negative_probe_test.py`
- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `docs/reports/goal3391_host_refined_exact_membership_partner_columns_bridge_2026-06-04.md`
- `tests/goal3391_host_refined_exact_membership_partner_columns_bridge_test.py`
- `scripts/goal3392_exact_membership_bridge_live_probe.py`
- `docs/reports/goal3392_exact_membership_bridge_live_probe_2026-06-04.json`
- `docs/reports/goal3392_exact_membership_bridge_live_probe_2026-06-04.md`
- `tests/goal3392_exact_membership_bridge_live_probe_test.py`

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3392_exact_membership_bridge_live_probe_test `
  tests.goal3391_host_refined_exact_membership_partner_columns_bridge_test `
  tests.goal3390_boundary_event_signal_4096_negative_probe_test
```

Result: `Ran 8 tests ... OK (skipped=2)`.

Pod at commit `5a1d9ac1`:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3392_exact_membership_bridge_live_probe_test \
  tests.goal3391_host_refined_exact_membership_partner_columns_bridge_test \
  tests.goal3390_boundary_event_signal_4096_negative_probe_test
```

Result: `Ran 8 tests ... OK`.

## Review Questions

1. Does Goal3390 correctly classify the 4096 failure as semantic rather than
   resource/overflow related?
2. Does the failure evidence justify blocking promotion of the Goal3388
   first-boundary-event route?
3. Is Goal3391's bridge genuinely app-agnostic and honestly bounded as
   `partner_device_after_host_refine_upload`, not true zero-copy and not native
   exact device-row production?
4. Does Goal3392 prove the bridge preserves exact pair identity on the 4096
   slice that broke Goal3388?
5. Are all release/public-speedup/RayJoin/RT-core/true-zero-copy/default-route
   claims blocked correctly?
6. Is the next primitive direction correct: a generic native exact closed-shape
   relation stream or richer relation-witness stream, not another app-specific
   special case?

## Output

Write the review to:

`docs/reviews/goal3393_claude_review_boundary_event_negative_and_exact_bridge_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
