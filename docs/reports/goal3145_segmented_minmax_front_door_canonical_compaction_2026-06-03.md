# Goal3145: Segmented Min/Max Front Door With Canonical Compaction

Date: 2026-06-03

Status: implemented and validated on RTX 4000 Ada pod; internal v2.8 preview only.

## Purpose

Goal3111 created the v2.8 segmented typed stream adapter, but left `segmented_min_f64` and `segmented_max_f64` deferred at the partner-consumer front door even though lower-level Numba grouped min/max kernels already existed. Goal3145 closes that gap for the common grouped-reduction shape: callers can now route segmented min/max through the explicit partner-consumer front door without writing a bespoke benchmark-app backend.

This is the "A" path after the Goal3143 Hausdorff front-door cleanup: make existing fast grouped primitives discoverable and usable through canonical app-agnostic adapters.

## Implementation

- `segmented_min_f64` and `segmented_max_f64` are now listed in `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`.
- They are removed from `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS`; `compact_mask_i64` remains deferred.
- The partner front door composes generic operations:
  - `partner_group_count_by_key(...)` to identify present groups.
  - `partner_group_min_by_key(...)` or `partner_group_max_by_key(...)` to compute dense grouped values.
  - `_canonical_segmented_minmax_columns(...)` to compact dense outputs into the public schema.
- Public output schema:
  - min: `group_ids`, `mins`, `missing_group_ids`
  - max: `group_ids`, `maxes`, `missing_group_ids`
- Metadata marks `canonical_output_host_compaction_used: true`.

## Boundary

The canonical compaction is intentionally host-side output shaping for this front door. It does not claim device-resident result streams, true zero-copy, RT-core acceleration, public speedup, automatic partner selection, or release readiness. The caller must still explicitly select `partner="numba"` and supply partner columns; hidden dispatch remains blocked.

This keeps the runtime useful without blurring the v3.0 device-residency roadmap.

## Validation

Local validation:

```text
python -m unittest \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal2995_raydb_numba_segmented_minmax_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 24 tests
OK
```

Combined local validation after Goal3144:

```text
Ran 44 tests
OK (skipped=9)
```

Pod validation on NVIDIA RTX 4000 Ada:

```text
python -m unittest \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test \
  tests.goal2995_raydb_numba_segmented_minmax_test \
  tests.goal3139_numba_kernel_cache_contract_test

Ran 24 tests in 0.008s
OK
```

Pod probe artifact:
`docs/reports/goal3145_pod_artifacts/segmented_minmax_front_door_pod_probe_2026-06-03.json`

| operation | rows | groups | time | output groups | missing groups | match |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `segmented_min_f64` | 65,536 | 1,024 | 0.274269 s | 1,024 | 0 | yes |
| `segmented_max_f64` | 65,536 | 1,024 | 0.050509 s | 1,024 | 0 | yes |
| `segmented_min_f64` | 1,048,576 | 1,024 | 0.043832 s | 1,024 | 0 | yes |
| `segmented_max_f64` | 1,048,576 | 1,024 | 0.043967 s | 1,024 | 0 | yes |

All rows matched the NumPy reference. All public/release/speedup/RT-core/zero-copy flags stayed false.

## Conclusion

The segmented typed stream front door now covers count, sum, min, max, vector sum, argmin, argmax, top-k, and bounded collect using explicit user-selected partners. This reduces benchmark-app-specific wiring pressure while preserving the primitive-first, app-agnostic runtime boundary.

The next useful extension is still `compact_mask_i64`, but that requires separate mask-compaction evidence and should not be folded into this goal.
