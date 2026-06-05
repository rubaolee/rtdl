# Handoff: Claude Review Goals3396-3398 Exact Stream Continuation And Full CDB

Please perform a read-only external review of Goals 3396, 3397, and 3398.

## Context

Your Goal3395 review accepted Goal3394 with boundary and flagged one naming
smell: the shared `RtdlNativeDevicePairColumns.candidate_event_count` field is
reused as an exact row count for exact-device-column streams.

Codex then did:

- Goal3396: proved the Goal3394 exact device-column stream feeds the existing
  generic grouped-count compact device continuation on the 4096-chain slice.
- Goal3397: added exact/relation row-count aliases in Python metadata and probe
  artifacts while preserving the shared ABI field as a legacy low-level slot.
- Goal3398: ran the exact stream and grouped-count continuation on the full
  available `br_county.cdb` dataset.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `scripts/goal3394_optix_exact_membership_device_columns_live_probe.py`
- `scripts/goal3396_exact_device_columns_grouped_count_live_probe.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md`
- `tests/goal3394_optix_exact_membership_device_columns_bridge_test.py`
- `docs/reports/goal3396_exact_device_columns_grouped_count_live_probe_2026-06-04.json`
- `docs/reports/goal3396_exact_device_columns_grouped_count_continuation_2026-06-04.md`
- `tests/goal3396_exact_device_columns_grouped_count_continuation_test.py`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_grouped_count_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_stream_and_grouped_count_2026-06-04.md`
- `tests/goal3398_full_br_county_exact_stream_and_grouped_count_test.py`

## Validation Already Run By Codex

Local focused tests:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3398_full_br_county_exact_stream_and_grouped_count_test `
  tests.goal3396_exact_device_columns_grouped_count_continuation_test `
  tests.goal3394_optix_exact_membership_device_columns_bridge_test
```

Result: `Ran 8 tests ... OK`.

Pod focused tests at commit `4a3d00ec`:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so python3 -m unittest \
  tests.goal3398_full_br_county_exact_stream_and_grouped_count_test \
  tests.goal3396_exact_device_columns_grouped_count_continuation_test \
  tests.goal3394_optix_exact_membership_device_columns_bridge_test
```

Result: `Ran 8 tests ... OK`.

Key full-dataset evidence:

- full `br_county`: 16545 points, 15700 shapes
- exact device rows: 47262
- exact relation row-count alias: 47262
- exact pair match: true
- grouped point counts: 16476 host and 16476 device
- grouped counts match host: true
- missing/extra/mismatched groups: 0
- grouped overflow: false

## Review Questions

1. Does Goal3397 adequately resolve the exact-count naming concern at the
   metadata/report/test level without pretending the ABI field was renamed?
2. Does Goal3396 prove useful composition from exact device columns into a
   generic grouped-count continuation?
3. Does Goal3398 close the full `br_county` chain-offset gap for the exact
   stream and grouped-count continuation?
4. Are claim boundaries still correct: no release, no public speedup, no
   RayJoin paper reproduction, no RTDL-beats-RayJoin, no RT-core speedup, no
   true-zero-copy, no native default route?
5. What remains before this bridge can be considered a stable v2.8 primitive:
   actual ABI field rename, overflow streaming fallback, device-only exact
   predicate, multi-dataset coverage, or something else?

## Output

Write the review to:

`docs/reviews/goal3399_claude_review_exact_stream_grouped_and_full_cdb_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
