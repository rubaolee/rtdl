# Goal3218: RayJoin Public LSI Dense Count Probe

Date: 2026-06-03

## Purpose

Goal3218 moves the fused dense left-id count route beyond authored all-crossing
fixtures and onto bounded public RayJoin-style Brazil county/soil CDB slices.

The probe compares two RTDL OptiX app routes under the same prepared-right and
packed-left setup:

- `compact`: emit segment-pair device columns, then compact grouped-count by
  pair-column `left_id`.
- `dense`: count by left-id directly during traversal with the generic
  `rtdl_optix_prepared_segment_pair_left_id_count_device_columns` primitive.

This is an internal route comparison, not a RayJoin paper reproduction and not a
public speedup claim.

Artifact:

- `docs/reports/goal3218_rayjoin_public_lsi_dense_count_probe_2026-06-03.json`

## Environment

- Commit: `34cd58f4b99d66ef1d4f491612633be83328eb19`
- GPU: `NVIDIA A40`
- Driver: `570.211.01`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Warmups: `1`
- Repeats: `5`
- Measured repetitions: `include_rows=False`
- Validation: one `include_rows=True` pass for dense and compact routes.

## Results

| Case | Left Segments | Right Segments | Intersections | Dense Median (s) | Compact Median (s) | Dense / Compact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lsi_county256_soil256_count48` | 3506 | 815 | 34 | 0.00014243647456169128 | 0.0018130503594875336 | 0.07856178611715538 |
| `lsi_county256_soil256_count128` | 6064 | 2034 | 56 | 0.000667918473482132 | 0.005484350025653839 | 0.12178625914791122 |
| `lsi_county256_soil256_count192` | 9216 | 2823 | 85 | 0.0010464414954185486 | 0.008431775495409966 | 0.12410689729443147 |
| `lsi_county256_soil256_count256` | 12295 | 3655 | 88 | 0.0010501518845558167 | 0.00745728611946106 | 0.14082225996603057 |
| `lsi_county256_soil256_count384` | 15763 | 5286 | 116 | 0.0010411553084850311 | 0.008542101830244064 | 0.121885143630427 |
| `lsi_county256_soil256_count512` | 19987 | 6825 | 269 | 0.0010526198893785477 | 0.008508497849106789 | 0.12371395139848926 |

All six rows have `counts_match: true`: the dense route and compact route agree
on the intersection count after validation copies.

## Interpretation

This closes one important weakness in the fused-count chain: the improvement is
not only visible on synthetic all-crossing fixtures. On bounded public
county/soil LSI slices, direct dense counting during traversal remains much
cheaper than producing a pair-column stream and reducing it afterward.

The app-specific parts still stay outside native code:

- dataset selection and RayJoin workload meaning stay in Python,
- original left IDs are remapped in Python,
- route selection stays in Python,
- native code sees only a generic segment-pair left-id count device-column primitive.

## Boundary

This artifact does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin paper
reproduction claims.
