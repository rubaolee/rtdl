# Goal3232: RayJoin Public Row-Continuation Probe

Date: 2026-06-03

## Purpose

Goal3232 moves the public RayJoin evidence beyond scalar/count parity for all
three current row workload families:

- PIP positive-hit rows on `pip_county512`.
- LSI segment-intersection rows on `lsi_county256_soil256_count512`.
- Overlay pair-dependency rows on `overlay_county128_soil128` and
  `overlay_county256_soil256`.

The probe materializes prepared OptiX rows, normalizes generic primitive row
fields at the Python app boundary, and compares compact row sets against the
CPU Python reference. It does not dump the full row arrays into the artifact.

## Artifact

- `docs/reports/goal3232_rayjoin_public_row_continuation_probe_2026-06-03.json`
- `docs/reports/goal3232_rayjoin_public_row_continuation_probe_2026-06-03.stdout`

Pod metadata:

- Commit: `e18d1c2cb59231ea573831c58734bd70e02ddd45`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Repeats: `1`
- Status: `pass`

| Case | Workload | CPU Rows | Prepared OptiX Rows | Symmetric Difference | Prepared Total (s) | Prepared Query (s) | CPU Reference (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pip_county512` | `pip` | 1430 | 1430 | 0 | 1.07393875904381 | 0.00150928646326065 | 0.0976834278553724 |
| `lsi_county256_soil256_count512` | `lsi` | 269 | 269 | 0 | 0.182055670768023 | 0.00135014764964581 | 45.8350778464228 |
| `overlay_county128_soil128` | `overlay_seed` | 14036 | 14036 | 0 | 0.371490608900785 | 0.00620529986917973 | 6.02088607661426 |
| `overlay_county256_soil256` | `overlay_seed` | 56876 | 56876 | 0 | 0.119245840236545 | 0.0222352594137192 | 22.588710911572 |

## Interpretation

For PIP, the native prepared row path emits generic
`point_id`/`shape_id`/`membership` rows. The app-level validator maps
`shape_id` to RayJoin's `polygon_id` and checks the resulting
`(point_id, polygon_id)` set against the CPU positive-assignment rows.
The refreshed harness explicitly rejects any prepared PIP row whose
`membership` value is not `1`.

For LSI, the validator compares `(left_id, right_id)` segment-pair sets and
also records `max_lsi_coordinate_delta`; the refreshed pod artifact reports
`0`.

For overlay, the prepared row path emits generic shape-pair dependency rows
with `left_polygon_id`, `right_polygon_id`, `requires_lsi`, and `requires_pip`.
The app compares those four fields directly against the CPU reference rows.

All four public cases match with symmetric difference `0`, including the
bounded LSI row slice and the larger bounded overlay slice with 56,876
row-continuation records.
The largest base row-continuation case has 56,876 row-continuation records.

The prepared query phase is much smaller than the full wall time. The total
time includes cold preparation, host-side row materialization, and row-set
validation. This goal is therefore correctness/contract evidence for public
row continuation, not a public speedup claim.

The artifact now records
`unattributed_prepared_total_minus_named_phases_sec` per measurement so future
readers can see the materialization/host overhead that is not included in the
named native phase dictionary. CPU summaries are compacted to counts rather than
embedding full positive-assignment or active-seed row lists.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims. No RayJoin paper-reproduction claims are authorized
here. Full paper-scale datasets, cross-system comparison, and stronger
row-stream/device-resident continuation remain future work.
