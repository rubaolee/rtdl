# Goal3234: RayJoin Public Overlay Row-Scale Addendum

Date: 2026-06-03

## Purpose

Goal3234 extends the Goal3232 public row-continuation evidence to larger
bounded overlay slices:

- `overlay_county384_soil384`
- `overlay_county512_soil512`

It uses the same generic Goal3232 row-continuation harness with an explicit
Goal3234 artifact schema. The native route remains prepared OptiX
`overlay_seed` row mode, and validation remains a compact set-difference check
against the CPU Python reference.

## Artifact

- `docs/reports/goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.json`
- `docs/reports/goal3234_rayjoin_public_overlay_row_scale_addendum_2026-06-03.stdout`

Pod metadata:

- Commit: `a6b040417875bef9f526e548959ab9b515d128de`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Repeats: `1`
- Status: `pass`

| Case | CPU Rows | Prepared OptiX Rows | Active Rows | Symmetric Difference | Prepared Total (s) | Prepared Query (s) | CPU Reference (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `overlay_county384_soil384` | 130320 | 130320 | 96 | 0 | 0.923723483458161 | 0.048036515712738 | 47.7308861520141 |
| `overlay_county512_soil512` | 233766 | 233766 | 121 | 0 | 0.385483676567674 | 0.084552900865674 | 79.9776256717741 |

## Interpretation

This is the strongest public overlay row-continuation evidence so far. It
validates hundreds of thousands of generic shape-pair dependency rows against
the CPU reference without storing the full row arrays in the repository.
Both rows have symmetric difference `0` against the CPU reference row set.

The prepared query phases remain small (`0.048 s` and `0.085 s`), while the
full totals include cold preparation, host-side row materialization, and
row-set validation. The CPU reference times are reported to show validation
cost and scale, not to authorize a public speedup claim.

The app-level semantics stay outside the native engine. The engine sees generic
shape-pair relation rows; the RayJoin interpretation of active overlay seeds
remains in Python.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims. It strengthens bounded public row-continuation
evidence only. Full paper-scale datasets, cross-system RayJoin comparison, and
device-resident row-stream continuation remain future work.
