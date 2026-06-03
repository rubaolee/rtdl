# Goal3172 - v2.8 Runtime-Gap Refresh After Direct Compact-Mask Front Door

Date: 2026-06-03

Status: local implementation ready for focused validation.

## Purpose

Goal3171 added `execute_compact_mask_typed_stream_partner_columns(...)` and
migrated RayJoin plus triangle-counting compact-mask preview wrappers to that
direct caller-column helper. Goal3172 updates the v2.8 benchmark runtime-gap
matrix so those rows no longer imply compact-mask continuation itself is
missing.

## Matrix Changes

### Spatial RayJoin

Current best path now records primitive-first scalar count/parity and first-hit
paths plus the direct compact-mask typed-stream front door for explicit
candidate-row filtering.

Remaining bottleneck is not the compact-mask front door. It is native typed hit-stream producer/residency evidence, parity/count grouping over resident
rows, and boundary-witness ownership at serious scale.

### Triangle counting

Current best path now records the native scalar triangle-count primitive plus
the direct compact-mask typed-stream front door for explicit candidate-row
interpretation.

Remaining bottleneck is not the compact-mask front door. It is
segmented/streamed graph lowering, native typed candidate-row producer evidence,
and resident continuation at serious scale.

## Boundary

This refresh does not authorize release packaging, public speedup wording,
broad RT-core claims, true-zero-copy wording, automatic partner selection, or
app-specific native-engine behavior.

The matrix continues to enforce:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

## Validation

Focused local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3172_v2_8_runtime_gap_compact_mask_refresh_test `
  tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```
