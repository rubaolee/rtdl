# Goal1921 - v2 Post-Pod Performance Report

Status: evidence-report-release-still-blocked

Date: 2026-05-13

## Summary

This report summarizes the accepted Goal1913 RTX pod performance artifacts for
the current v2.0 Python+partner+RTDL work. The evidence was collected on:

- Commit: `c4aebb2a29744a3a78af9d3b2d4b8be957c7cd68`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- Driver: `550.127.05`
- OptiX SDK: `v8.0.0`
- Goal1905 post-pod acceptance: `pass`
- Goal1916 post-pod manifest: `pass`

Main result:

- Fixed-radius workloads show strong v2 partner speedups versus v1.8 prepared
  and v1.8 reused-prepared OptiX rows.
- Segment/polygon hitcount shows mixed tiny-row behavior at 512 rows and clear
  positive prepared comparisons at 2048 rows.
- Road-hazard shows mixed tiny-row behavior at 512 rows and clear positive
  prepared-reuse comparisons at 2048 rows.
- The artifacts support exact scoped claims only. They do not authorize v2.0
  release, broad RT-core speedup, whole-app acceleration, arbitrary partner
  acceleration, package-install support, or fixed-radius true-zero-copy wording.

## Method

All rows below use median query time from the pod artifacts. Lower ratio is
better. A `0.500x` ratio means the v2 row took half the comparison time.

Important comparison contracts:

- `v1.8 one-shot`: legacy/native row that includes heavier per-query setup.
  Ratios against this row are useful for showing amortization, but they are not
  enough by themselves for same-contract speedup claims.
- `v1.8 prepared`: prepared native OptiX baseline.
- `v1.8 reused-prepared`: fixed-radius retained prepared-object baseline where
  available.
- `v2 native partner`: v2 Python+partner+RTDL row with partner-owned columns.
- `v2 prepared partner`: v2 row with prepared native/partner reuse where the
  artifact exposes that path.

## Fixed-Radius

Artifact: `docs/reports/goal1903_fixed_radius_batch_pod.json`

Fixed-radius is the strongest current v2 result. The v2 prepared partner path
is consistently faster than both v1.8 prepared and v1.8 reused-prepared rows.
For size `16384`, dense partner references were intentionally skipped by the
Goal1918 OOM guard because they would materialize `134217728` to `268435456`
pairs. The v1.8 and v2 native timing rows still ran.

| Workload | Size | Partner | v1.8 prepared | v1.8 reused | v2 native | v2 native / v1.8 prepared | v2 prepared | v2 prepared / v1.8 prepared | v2 prepared / v1.8 reused |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| service coverage gaps | 4096 | torch | 0.009101 | 0.006355 | 0.000563 | 0.062x | 0.000250 | 0.027x | 0.039x |
| event hotspot screening | 4096 | torch | 0.008084 | 0.005629 | 0.000494 | 0.061x | 0.000169 | 0.021x | 0.030x |
| service coverage gaps | 16384 | torch | 0.040027 | 0.024426 | 0.000564 | 0.014x | 0.000267 | 0.007x | 0.011x |
| event hotspot screening | 16384 | torch | 0.087541 | 0.027471 | 0.000888 | 0.010x | 0.000202 | 0.002x | 0.007x |
| service coverage gaps | 4096 | cupy | 0.007820 | 0.005606 | 0.000538 | 0.069x | 0.000218 | 0.028x | 0.039x |
| event hotspot screening | 4096 | cupy | 0.009557 | 0.005386 | 0.000505 | 0.053x | 0.000180 | 0.019x | 0.034x |
| service coverage gaps | 16384 | cupy | 0.038096 | 0.027483 | 0.000569 | 0.015x | 0.000228 | 0.006x | 0.008x |
| event hotspot screening | 16384 | cupy | 0.094140 | 0.028904 | 0.000959 | 0.010x | 0.000188 | 0.002x | 0.007x |

Interpretation:

- The v2 prepared fixed-radius path is roughly `25x` to `500x` faster than
  v1.8 prepared in these measured rows.
- Speedup improves at the larger size because the v1.8 prepared rows scale with
  more host/native work while the v2 prepared partner row stays near
  sub-millisecond.
- The fixed-radius artifact does not contain
  `partner_output_columns_true_zero_copy_authorized: true`, so it must not be
  used for fixed-radius true-zero-copy public wording.

## Segment/Polygon Hitcount

Artifacts:

- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`

Segment/polygon has accepted parity and same-contract artifact shape. It also
has `partner_output_columns_true_zero_copy_authorized: true` and
`same_contract_timing_row: true`, but only for these exact artifacts and rows.

| Count | Partner | v1.8 one-shot | v1.8 prepared | v2 native | v2 native / one-shot | v2 native / prepared | v2 prepared reuse | v2 prepared reuse / prepared |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 | cupy | 0.243843 | 0.000784 | 0.001359 | 0.006x | 1.733x | 0.000900 | 1.148x |
| 512 | torch | 0.243843 | 0.000784 | 0.001046 | 0.004x | 1.334x | 0.000798 | 1.017x |
| 2048 | cupy | 16.166940 | 0.002544 | 0.001624 | 0.000x | 0.638x | 0.000928 | 0.365x |
| 2048 | torch | 16.166940 | 0.002544 | 0.001231 | 0.000x | 0.484x | 0.000878 | 0.345x |

Interpretation:

- At 512 rows, v2 is much faster than v1.8 one-shot but not meaningfully faster
  than v1.8 prepared. Torch prepared reuse is essentially neutral at `1.017x`;
  CuPy is slower at `1.148x`.
- At 2048 rows, both partners beat v1.8 prepared. Prepared reuse reaches
  `0.365x` for CuPy and `0.345x` for Torch.
- The accepted claim should be scoped as: segment/polygon partner-owned output
  columns and same-contract timing are validated for these rows, with positive
  prepared comparisons at 2048 rows. Do not make a broad segment/polygon
  speedup claim from the 512-row data.

## Road-Hazard

Artifacts:

- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`

Road-hazard has accepted parity and same-contract artifact shape. It also has
`partner_output_columns_true_zero_copy_authorized: true` and
`same_contract_timing_row: true`, scoped to these artifacts.

| Count | Partner | v1.8 one-shot | v1.8 prepared | v2 native | v2 native / one-shot | v2 native / prepared | v2 prepared reuse | v2 prepared reuse / prepared |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 | cupy | 0.266958 | 0.000687 | 0.001267 | 0.005x | 1.845x | 0.000883 | 1.287x |
| 512 | torch | 0.266958 | 0.000687 | 0.001189 | 0.004x | 1.731x | 0.000609 | 0.886x |
| 2048 | cupy | 18.459379 | 0.004491 | 0.001773 | 0.000x | 0.395x | 0.001108 | 0.247x |
| 2048 | torch | 18.459379 | 0.004491 | 0.002016 | 0.000x | 0.449x | 0.001210 | 0.270x |

Interpretation:

- At 512 rows, v2 is much faster than one-shot, but the prepared comparison is
  mixed. Torch prepared reuse is positive at `0.886x`; CuPy prepared reuse is
  slower at `1.287x`.
- At 2048 rows, both partners are clearly positive. Prepared reuse is `0.247x`
  for CuPy and `0.270x` for Torch versus v1.8 prepared.
- The strongest current road-hazard statement is therefore scoped to larger
  rows and prepared reuse, not a broad all-size whole-app speedup claim.

## Supported Claims

The current artifacts support these narrow statements:

- RTX pod evidence exists for fixed-radius, segment/polygon, and road-hazard
  partner rows on `NVIDIA RTX 2000 Ada Generation`.
- Goal1905 strict post-pod acceptance passed.
- Goal1916 post-pod manifest passed with no missing artifacts.
- Fixed-radius v2 prepared partner rows are faster than v1.8 prepared and v1.8
  reused-prepared rows in all measured Torch/CuPy rows.
- Segment/polygon v2 prepared reuse beats v1.8 prepared at 2048 rows for Torch
  and CuPy.
- Road-hazard v2 prepared reuse beats v1.8 prepared at 2048 rows for Torch and
  CuPy.
- Segment/polygon and road-hazard artifacts support exact
  `partner_output_columns_true_zero_copy_authorized: true` and
  `same_contract_timing_row: true` claims for their measured rows.

## Unsupported Claims

These claims remain blocked:

- v2.0 release readiness.
- Package-install support.
- Whole-application speedup.
- Broad RT-core speedup.
- Arbitrary PyTorch/CuPy acceleration.
- Fixed-radius true-zero-copy support.
- A claim that every small row improves versus v1.8 prepared.
- Any claim that OptiX creates no native acceleration state.

## Release Implication

This is a meaningful v2.0 performance milestone, not a release authorization.
The pod evidence is now real and positive in important rows, but final v2.0
still needs a Claude or Pro-class review of the actual pod artifacts, final
source-tree/package decision consensus, final release consensus, and explicit
release action.
