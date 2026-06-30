# Goal 46 Report: OptiX County/Zipcode Parity Repair

Date: 2026-04-02

## Scope

Goal 46 repaired the real-data OptiX correctness gap exposed by Goal 45 on the
first exact-source RayJoin family:

- `County ⊲⊳ Zipcode`

Goal 45 had accepted only:

- `1x8`
- `1x10`

and rejected:

- `1x4`
- `1x5`
- `1x6`
- `1x12`

because exact-row parity did not hold across the full bounded ladder.

## Diagnosis

The failing slices separated into two patterns:

- `1x4` / `1x5` / `1x6`
  - impossible `lsi` false-positive rows from the GPU path
  - one `pip` boundary mismatch
- `1x12`
  - one missing `lsi` row

Exact-row delta inspection on `192.168.1.20` showed:

- the `1x4` extra `lsi` rows were not real segment intersections
- the `1x12` missing row disappeared under exact double-precision host refine
  once the candidate path was made more tolerant

The practical conclusion was:

- the previous OptiX device-side refine path was not trustworthy enough on this
  real geographic data
- the parity repair should use OptiX as a GPU candidate generator and the
  native exact host logic as the final oracle refine

## Code changes

File changed:

- [/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp](../../src/native/rtdl_optix.cpp)

Main changes:

- added exact native host-side `segment_intersection` refine for `lsi`
- added exact native host-side point-in-polygon recomputation for `pip`
- widened segment AABB padding for `lsi`
- widened `lsi` trace `tmax` slightly
- changed the OptiX `lsi` intersection program to report AABB-overlap
  candidates and leave truth filtering to exact host refine

## Remote rerun

Goal 46 reran the full Goal 45 bounded ladder on `192.168.1.20` using:

- county input: `build/goal38/top4_tx_ca_ny_pa/county`
- zipcode input: `build/goal38/top4_tx_ca_ny_pa/zipcode`
- sizes:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`

Runtime boundary:

- OptiX runtime: `9.0`
- PTX compiler:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

## Results

### Final status

- accepted points: `6`
- rejected points: `0`

The full bounded County/Zipcode ladder is now exact-row parity-clean.

### Accepted points

| Slice | `lsi` CPU Rows | `lsi` OptiX Rows | `pip` CPU Rows | `pip` OptiX Rows | `lsi` CPU Median (s) | `lsi` OptiX Warm Median (s) | `pip` CPU Median (s) | `pip` OptiX Warm Median (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1x4`  | `3`  | `3`  | `4`  | `4`  | `0.002661481` | `0.003503646` | `0.000446793` | `0.000861384` |
| `1x5`  | `3`  | `3`  | `5`  | `5`  | `0.003289656` | `0.004104529` | `0.000445940` | `0.000850927` |
| `1x6`  | `3`  | `3`  | `6`  | `6`  | `0.003991393` | `0.004852923` | `0.000448727` | `0.000862113` |
| `1x8`  | `0`  | `0`  | `8`  | `8`  | `0.005217926` | `0.006215723` | `0.001293248` | `0.002551167` |
| `1x10` | `5`  | `5`  | `10` | `10` | `0.005767384` | `0.006762578` | `0.001316241` | `0.002530437` |
| `1x12` | `10` | `10` | `12` | `12` | `0.006308146` | `0.007488998` | `0.001351188` | `0.002550176` |

## Interpretation

Goal 46 closes the bounded real-data County/Zipcode correctness gap for OptiX.

The truthful backend position after this round is:

- `County ⊲⊳ Zipcode` bounded ladder is now parity-clean on the GPU host
- this closure was achieved by moving final truth evaluation back into exact
  native host-side refine for `lsi` and `pip`
- therefore Goal 46 is a correctness-restoration round, not a GPU-purity or
  GPU-performance-improvement round

## Performance meaning

Warm OptiX remains slower than the native C oracle on these small bounded
slices. That is expected after the repair because the current OptiX path now
includes exact host-side refine.

So Goal 46 does **not** support stronger GPU performance claims. It supports a
stronger correctness claim:

- bounded real-data County/Zipcode OptiX parity is now closed

## Verification

Local verification:

- `make test` passed
- Goal 45 local unit tests passed

Remote verification:

- full bounded ladder rerun on `192.168.1.20`
- accepted points: `6`
- rejected points: `0`

## Boundary

Goal 46 does **not** claim:

- whole-dataset County/Zipcode GPU closure
- paper-scale OptiX reproduction
- improved OptiX performance
- that the current OptiX path is GPU-only exact refine

The honest closure statement is:

- the first real exact-source RayJoin family is now parity-clean on OptiX
  across the bounded `1x4` through `1x12` ladder
- the current implementation achieves that by combining GPU candidate
  generation with exact native host-side refine

## Next goal

The next correct OptiX goal is:

- move from bounded County/Zipcode parity repair to the next real-data family or
  broader GPU validation, while keeping this exact-refine boundary explicit
