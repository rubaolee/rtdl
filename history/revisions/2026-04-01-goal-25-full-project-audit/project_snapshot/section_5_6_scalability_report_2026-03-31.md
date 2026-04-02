# RTDL Section 5.6 Scalability Analogue Report

- Generated: `2026-03-31T10:35:17`
- Method: `Embree-phase scaled analogue of RayJoin Section 5.6`
- Fixed build-side polygons: `100000`
- Probe-side series: `100000, 200000, 300000, 400000, 500000`
- Iterations: `5`
- Warmup: `1`

## Support Decision

The repository did not previously support Section 5.6 as an executable experiment.
It had the workload surface and planning notes, but it lacked:

- deterministic uniform / gaussian scalability generators,
- a fixed-R / varying-S experiment runner for `lsi` and `pip`,
- Figure 13 / Figure 14 analogue generation, and
- a dedicated report path for the Section 5.6 structure.

This report is therefore a **revised Embree-phase scaled analogue**, not a claim of the original 5M / 1M..5M GPU experiment.

The checked-in 2026-03-31 report is reproducible with:
`PYTHONPATH=src:. python3 -m rtdsl.section_5_6_scalability --build-polygons 100000 --probe-series 100000,200000,300000,400000,500000 --iterations 5 --warmup 1 --workloads lsi --publish-docs`

## Correctness Gate

- `uniform` parity sample: `lsi=True`, `pip=None` on reduced CPU-vs-Embree checks.
- `gaussian` parity sample: `lsi=True`, `pip=None` on reduced CPU-vs-Embree checks.

## Results

| Workload | Distribution | Probe Polygons | Query Time (ms) | Throughput | Output Rows |
| --- | --- | ---: | ---: | ---: | ---: |
| `lsi` | `uniform` | 100000 | 743.293 | 88094.42 `intersections/s` | 65480 |
| `lsi` | `uniform` | 200000 | 1304.533 | 99998.21 `intersections/s` | 130451 |
| `lsi` | `uniform` | 300000 | 1928.766 | 101474.19 `intersections/s` | 195720 |
| `lsi` | `uniform` | 400000 | 2739.473 | 94571.83 `intersections/s` | 259077 |
| `lsi` | `uniform` | 500000 | 3629.051 | 89420.07 `intersections/s` | 324510 |
| `lsi` | `gaussian` | 100000 | 1086.436 | 306206.75 `intersections/s` | 332674 |
| `lsi` | `gaussian` | 200000 | 1943.597 | 340601.47 `intersections/s` | 661992 |
| `lsi` | `gaussian` | 300000 | 3057.244 | 325140.60 `intersections/s` | 994034 |
| `lsi` | `gaussian` | 400000 | 4426.805 | 298831.09 `intersections/s` | 1322867 |
| `lsi` | `gaussian` | 500000 | 5883.610 | 282883.11 `intersections/s` | 1664374 |

## Generated Figures

- `build/goal14_5min_lsi/figures/figure13_lsi_scalability.svg`
- `build/goal14_5min_lsi/figures/figure14_pip_scalability.svg`

## Interpretation

- Figure 13 analogue corresponds to `lsi` only.
- Figure 14 was not executed in this published run; the checked-in Figure 14 SVG for this artifact set is therefore a placeholder.
- Query-time curves and throughput curves follow the structure of RayJoin Section 5.6.
- Scale and hardware are intentionally different from the original paper.
