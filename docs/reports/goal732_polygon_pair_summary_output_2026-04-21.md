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

Follow-up optimization in this same goal changed Embree native-assisted
candidate discovery from full `overlay_compose` matrix materialization to
positive-only Embree `segment_intersection` plus positive-hit
`point_in_polygon` helper kernels. This preserves the public overlay contract
while avoiding all-pairs row output inside this app.

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
| 64 | 0.0067s | 0.0062s | 1.07x | 31.32x |
| 256 | 0.0382s | 0.0236s | 1.62x | 123.20x |
| 1024 | 0.3286s | 0.0896s | 3.67x | 486.12x |

Linux:

| Copies | Rows median | Summary median | Summary speedup | JSON reduction |
| ---: | ---: | ---: | ---: | ---: |
| 64 | 0.0162s | 0.0123s | 1.32x | 31.32x |
| 256 | 0.0783s | 0.0510s | 1.54x | 123.20x |
| 1024 | 0.6539s | 0.2055s | 3.18x | 486.12x |

Raw evidence:

- `docs/reports/goal732_polygon_pair_summary_output_perf_local_2026-04-21.json`
- `docs/reports/goal732_polygon_pair_summary_output_perf_linux_2026-04-21.json`

## Boundary

This is an app-level Embree native-assisted candidate/materialization
optimization plus a compact-output improvement. It greatly reduces JSON payload
size and avoids full overlay-matrix row materialization in this app, but exact
grid-cell area refinement remains CPU/Python-owned.

Do not claim this is a fully native Embree polygon-overlay kernel.
