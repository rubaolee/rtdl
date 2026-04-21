# Goal 732: Polygon Pair Summary Output

Date: 2026-04-21

## Scope

Goal 732 adds bounded app-level scalability controls to
`examples/rtdl_polygon_pair_overlap_area_rows.py`:

- `--copies N` creates a tiled repeated fixture
- `--output-mode rows|summary`

The default remains unchanged:

- `--copies 1`
- `--output-mode rows`
- full per-pair overlap area rows

The new `summary` mode returns:

- `overlap_pair_count`
- `total_intersection_area`
- `total_union_area`

and omits the full `rows` payload.

## Correctness

Focused tests verify:

- CPU reference summary equals aggregation over full rows
- Embree summary equals CPU reference summary
- default mode still returns rows
- invalid copy counts and output modes are rejected

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal732_polygon_pair_summary_output_test
```

Results:

- macOS: 4 tests passed
- Linux: 4 tests passed

## Performance Evidence

Measurement:

- `run_case(...)` plus `json.dumps(...)`
- Embree backend
- copies 64, 256, 1024
- 3 repeats

macOS:

| Copies | Rows median | Summary median | Summary speedup | JSON reduction |
| ---: | ---: | ---: | ---: | ---: |
| 64 | 0.0194s | 0.0183s | 1.06x | 31.72x |
| 256 | 0.2597s | 0.2465s | 1.05x | 124.57x |
| 1024 | 4.7390s | 4.5589s | 1.04x | 491.51x |

Linux:

| Copies | Rows median | Summary median | Summary speedup | JSON reduction |
| ---: | ---: | ---: | ---: | ---: |
| 64 | 0.0439s | 0.0349s | 1.26x | 31.72x |
| 256 | 0.5458s | 0.5088s | 1.07x | 124.57x |
| 1024 | 8.3666s | 7.9858s | 1.05x | 491.51x |

Raw evidence:

- `docs/reports/goal732_polygon_pair_summary_output_perf_local_2026-04-21.json`
- `docs/reports/goal732_polygon_pair_summary_output_perf_linux_2026-04-21.json`

## Boundary

This is primarily a compact-output improvement. It greatly reduces JSON payload
size, but whole-app timing improves only modestly because exact grid-cell area
refinement is still CPU/Python-owned after Embree native-assisted candidate
discovery.

Do not claim this is a fully native Embree polygon-overlay kernel.
