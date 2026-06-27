# RTDL Section 5.6 Scalability Analogue Report

- Generated: `2026-03-31T06:51:08`
- Method: `Embree-phase scaled analogue of RayJoin Section 5.6`
- Fixed build-side polygons: `800`
- Probe-side series: `160, 320, 480, 640, 800`
- Iterations: `2`
- Warmup: `1`

## Support Decision

The repository did not previously support Section 5.6 as an executable experiment.
It had the workload surface and planning notes, but it lacked:

- deterministic uniform / gaussian scalability generators,
- a fixed-R / varying-S experiment runner for `lsi` and `pip`,
- Figure 13 / Figure 14 analogue generation, and
- a dedicated report path for the Section 5.6 structure.

This report is therefore a **revised Embree-phase scaled analogue**, not a claim of the original 5M / 1M..5M GPU experiment.

## Correctness Gate

- `uniform` parity sample: `lsi=True`, `pip=True` on reduced CPU-vs-Embree checks.
- `gaussian` parity sample: `lsi=True`, `pip=True` on reduced CPU-vs-Embree checks.

## Results

| Workload | Distribution | Probe Polygons | Query Time (ms) | Throughput | Output Rows |
| --- | --- | ---: | ---: | ---: | ---: |
| `lsi` | `uniform` | 160 | 8.295 | 0.00 `intersections/s` | 0 |
| `pip` | `uniform` | 160 | 192.791 | 829.91 `probe-points/s` | 128000 |
| `lsi` | `uniform` | 320 | 10.247 | 195.19 `intersections/s` | 2 |
| `pip` | `uniform` | 320 | 300.873 | 1063.57 `probe-points/s` | 256000 |
| `lsi` | `uniform` | 480 | 12.073 | 0.00 `intersections/s` | 0 |
| `pip` | `uniform` | 480 | 430.850 | 1114.08 `probe-points/s` | 384000 |
| `lsi` | `uniform` | 640 | 9.646 | 414.68 `intersections/s` | 4 |
| `pip` | `uniform` | 640 | 373.850 | 1711.92 `probe-points/s` | 512000 |
| `lsi` | `uniform` | 800 | 7.036 | 1421.33 `intersections/s` | 10 |
| `pip` | `uniform` | 800 | 366.496 | 2182.83 `probe-points/s` | 640000 |
| `lsi` | `gaussian` | 160 | 3.879 | 0.00 `intersections/s` | 0 |
| `pip` | `gaussian` | 160 | 58.617 | 2729.58 `probe-points/s` | 128000 |
| `lsi` | `gaussian` | 320 | 4.139 | 483.17 `intersections/s` | 2 |
| `pip` | `gaussian` | 320 | 128.788 | 2484.71 `probe-points/s` | 256000 |
| `lsi` | `gaussian` | 480 | 4.410 | 2721.27 `intersections/s` | 12 |
| `pip` | `gaussian` | 480 | 195.241 | 2458.50 `probe-points/s` | 384000 |
| `lsi` | `gaussian` | 640 | 5.327 | 3378.99 `intersections/s` | 18 |
| `pip` | `gaussian` | 640 | 326.666 | 1959.19 `probe-points/s` | 512000 |
| `lsi` | `gaussian` | 800 | 6.989 | 4292.25 `intersections/s` | 30 |
| `pip` | `gaussian` | 800 | 405.897 | 1970.94 `probe-points/s` | 640000 |

## Generated Figures

- `/Users/rl2025/rtdl_python_only/build/section_5_6_scalability/figures/figure13_lsi_scalability.svg`
- `/Users/rl2025/rtdl_python_only/build/section_5_6_scalability/figures/figure14_pip_scalability.svg`

## Interpretation

- Figure 13 analogue corresponds to `lsi` only.
- Figure 14 analogue corresponds to `pip` only.
- Query-time curves and throughput curves follow the structure of RayJoin Section 5.6.
- For `pip`, throughput is computed from probe-point count per second; the `Output Rows` column is the emitted RTDL row count and therefore reflects the current point/polygon row schema rather than raw point count.
- Scale and hardware are intentionally different from the original paper.
