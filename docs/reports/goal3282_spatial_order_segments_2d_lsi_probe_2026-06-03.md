# Goal3282 Spatial Order Segments 2D LSI Probe

Date: 2026-06-03

## Summary

Goal3282 extends the generic spatial-ordering helper from point records to
2-D segment records:

```python
rtdsl.spatial_order_segments_2d(segments, mode="morton_xy")
```

Supported modes are `natural`, `x_then_y`, `y_then_x`, and `morton_xy`.
Ordering is based on segment centroid and preserves caller segment IDs.

The RayJoin LSI prepared-OptiX benchmark route now accepts
`segment_order_mode`, and the repeated-count runner exposes
`--rtdl-lsi-segment-order` for source-clean pod sweeps.

## Boundary

This is a generic preparation/layout hint. It reorders caller-owned 2-D
segments before packing/preparation. It does not add RayJoin, LSI, overlay, or
paper-specific semantics to the native engine.

No new native ABI was added. The goal is diagnostic: find whether query/static
segment locality changes prepared-query timing enough to justify a later packed
or native-side ordering primitive.

## Pod Evidence

Source-clean pod artifacts are saved under:

`docs/reports/goal3282_lsi_segment_order_pod/`

Hardware/checkout: current pod checkout at commit `b39a796e`.

Command shape:

```bash
python3 scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py \
  --rtdl-lsi-segment-order <mode> \
  --rayjoin-warmup 2 --rayjoin-repeat 10 --rayjoin-process-repeats 3 \
  --rtdl-warmup 2 --rtdl-repeat 7
```

All artifacts record `source_dirty: []` and preserve the LSI count `269`.

| Segment order | RTDL LSI query ms | RayJoin query ms | RTDL/RayJoin | Query order ms | Static order ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| `natural` | 0.472847 | 0.233817 | 2.022x | 0.003524 | 0.001123 |
| `x_then_y` | 0.383597 | 0.233221 | 1.645x | 50.829295 | 17.307818 |
| `y_then_x` | 0.464939 | 0.235200 | 1.977x | 76.129805 | 26.294753 |
| `morton_xy` | 0.473972 | 0.229406 | 2.066x | 122.119104 | 42.844543 |

## Interpretation

`x_then_y` improves the measured prepared-query lane by about `1.23x` versus
natural order (`0.472847 / 0.383597`). That means segment locality is a real
knob for the LSI path.

However, Python-level sorting dominates end-to-end cost at this scale: even the
best query-only mode pays about `50.8 ms` for query ordering and `17.3 ms` for
static ordering. Therefore this is not promoted as a benchmark speedup path.

The useful engineering lesson is narrower and clearer: if RTDL wants this
locality benefit in a serious path, ordering must happen earlier, in a packed
preparation step, cached prepared handle, partner preprocessor, or native-side
layout builder. Ad-hoc Python sorting is acceptable as a user-facing diagnostic
and correctness-preserving layout hint, but not a high-performance continuation
strategy.

## Validation

Local and pod focused tests passed:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3282_spatial_order_segments_2d_lsi_probe_test `
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test
```

Pod result: `36` tests passed.

## Claim Boundary

- Release authorized: `false`
- RayJoin reproduction claim authorized: `false`
- RTDL beats RayJoin claim authorized: `false`
- Broad RT-core speedup claim authorized: `false`
- True zero-copy claim authorized: `false`

The accepted claim is narrow: RTDL now exposes a reusable, app-agnostic
segment-ordering helper and has measured that segment locality can improve the
LSI prepared-query lane, but Python sorting cost blocks promotion as an
end-to-end performance win.
