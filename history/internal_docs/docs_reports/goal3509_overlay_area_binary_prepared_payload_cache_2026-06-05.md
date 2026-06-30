# Goal3509 Overlay Area Binary Prepared Payload Cache

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3509 adds an opt-in binary column-cache format for the v2.8 prepared
simple-polygon overlay area route. It keeps the Goal3507 JSON cache as the
default, but lets repeated benchmark runs reload prepared payload columns,
shape-to-component columns, and geometry WKB columns from `.npz` files instead
of parsing large JSON arrays and WKB hex strings.

This is still a host-side cache. It is not true zero-copy or device-resident
payload persistence. The purpose is to make repeat-run benchmark iteration less
dominated by CPU payload preparation while preserving the same generic RTDL
prepared-payload contract.

## Pod Evidence

Artifacts:

- `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_write_pod_2026-06-05.json`
- `docs/reports/goal3509_overlay_area_binary_prepared_payload_cache_read_pod_2026-06-05.json`

Pod hardware/software:

- GPU: NVIDIA RTX A5000
- CuPy: 14.1.1
- Shapely: 2.1.2
- RTDL commit: `d1a9ac191b4362e263876f034eb2083d74011d42`

Both artifacts use the same public-CDB route as Goal3507, adding:

```text
--payload-cache-format binary --payload-cache-evidence
```

The write run uses:

```text
--payload-workers 8 --parallel-payload-prepare-evidence --payload-cache-mode refresh
```

The read run uses:

```text
--payload-cache-mode read
```

## Results

| Route | Geometry+payload prepare | Cache load | Cache write | Device planner best | Executor best | Total abs error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Goal3505 best rebuild, 8 workers | 1.441s | 0.000s | 0.000s | 0.0471s | 0.0146s | 9.228e-09 |
| Goal3507 JSON cache read | 0.355s | 0.355s | 0.000s | 0.0550s | 0.0150s | 9.228e-09 |
| Goal3509 binary cache refresh/write | 1.537s | 0.000s | 0.132s | 0.0552s | 0.0148s | 9.228e-09 |
| Goal3509 binary cache read | 0.171s | 0.171s | 0.000s | 0.0497s | 0.0146s | 9.228e-09 |

Preparation-stage ratios on this pod/dataset:

- Binary read versus best 8-worker rebuild: `1.441s / 0.171s = 8.41x`.
- Binary read versus JSON read: `0.355s / 0.171s = 2.07x`.
- Binary read versus Goal3502 pre-parallel single-triangulation preparation
  (`5.058s`): about `29.51x`.

Correctness and downstream workload shape are unchanged:

- Relation rows: 4,543
- Supported relation rows: 2,149
- Exact positive rows: 1,086
- Observed positive rows: 1,086
- Planned triangle pairs: 4,070,240
- Total absolute area error: `9.227800745748027e-09`
- Max per-relation absolute error: `1.0414231699229504e-09`

## Implementation Notes

The generic payload module now exposes explicit column serialization helpers:

- `prepared_simple_polygon_component_payload_to_numpy_columns(...)`
- `prepared_simple_polygon_component_payload_from_numpy_columns(...)`

The benchmark runner adds:

- `--payload-cache-format json|binary`
- Goal3509 schema: `rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1`
- Binary manifest per side
- Prepared payload column `.npz`
- Shape-to-component column `.npz`
- Geometry WKB byte-column `.npz`

The JSON cache remains the default, so Goal3507 evidence remains stable and
existing scripts do not silently switch storage formats.

## Boundary

This does not add native engine app logic, does not construct polygon payloads
inside the native engine, and does not make the exact overlay executor a full
general overlay engine. It does not authorize release, public speedup, RT-core
speedup, true zero-copy, RayJoin reproduction, `rtdl beats RayJoin`, or full
overlay wording.

The next deeper runtime target remains a device-resident or memory-mapped
prepared-payload lifetime contract. Goal3509 only replaces bulky JSON payload
cache storage with explicit binary column storage.
