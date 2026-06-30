# Goal729 Road-Hazard Compact App Output

Date: 2026-04-21

## Scope

This goal improves the public `examples/rtdl_road_hazard_screening.py` app
surface for large app-output cases.

The backend computation is unchanged: road segments and hazard polygons still
run through the RTDL `segment_polygon_hitcount` primitive. The new compact
output modes avoid returning full per-road hit-count rows in the app JSON
payload when the user only needs priority road ids or summary counts.

## Changes

- Added `--copies N` to tile the demo roads/hazards for larger app-output
  tests.
- Added `--output-mode rows|priority_segments|summary`.
- Default `rows` mode is unchanged and still includes full per-road rows.
- Compact modes preserve:
  - `priority_segments`
  - `priority_segment_count`
  - `row_count`
- Compact modes omit:
  - `rows`

## Correctness

Verification commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal729_road_hazard_compact_output_test \
  tests.goal692_optix_app_correctness_transparency_test \
  tests.goal686_app_catalog_cleanup_test

python3 -m py_compile \
  examples/rtdl_road_hazard_screening.py \
  scripts/goal729_road_hazard_compact_output_perf.py

PYTHONPATH=src:. python3 examples/rtdl_road_hazard_screening.py \
  --backend embree \
  --copies 4 \
  --output-mode priority_segments
```

Results:

- Local focused tests: `13` tests passed.
- Linux focused tests: `8` tests passed.
- CLI smoke check: passed.

## Performance

This measures app payload generation plus JSON serialization, not backend
kernel traversal alone.

Mac local:

| Copies | Rows sec | Compact sec | Speedup | Rows JSON bytes | Compact JSON bytes | Size reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1024 | 0.0218 | 0.0073 | 2.99x | 127329 | 7788 | 16.35x |
| 4096 | 0.0412 | 0.0788 | 0.52x | 520546 | 32365 | 16.08x |
| 16384 | 0.3395 | 0.2923 | 1.16x | 2118948 | 137055 | 15.46x |

Mac geomean:

- Speedup: `1.22x`
- JSON size reduction: `15.96x`

Linux:

| Copies | Rows sec | Compact sec | Speedup | Rows JSON bytes | Compact JSON bytes | Size reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1024 | 0.0248 | 0.0127 | 1.95x | 127329 | 7788 | 16.35x |
| 4096 | 0.1083 | 0.0592 | 1.83x | 520546 | 32365 | 16.08x |
| 16384 | 0.5027 | 0.2577 | 1.95x | 2118948 | 137055 | 15.46x |

Linux geomean:

- Speedup: `1.91x`
- JSON size reduction: `15.96x`

## Boundary

This is an app-output optimization. It does not claim that the Embree traversal
kernel is faster. It makes the large public app payload cheaper when users do
not need full per-road rows.

Use `--output-mode rows` when full per-road hit-count rows are required.

## Verdict

ACCEPT. The compact output mode preserves priority-road results, reduces large
JSON payloads substantially, and keeps the RTDL/OptiX honesty boundary intact.
