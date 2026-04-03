# Goal 45 Report: OptiX County/Zipcode Real-Data Validation

Date: 2026-04-02

## Scope

Goal 45 moved the OptiX backend from tiny/synthetic validation into the first
real exact-source RayJoin family already exercised on Embree:

- `County ⊲⊳ Zipcode`

This round intentionally reused the bounded co-located exact-source slice policy
from Goal 34 instead of attempting state-scale GPU execution immediately.

## Host and runtime boundary

- host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- PTX compiler path:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

The runtime used the trusted `nvcc` fallback path, not the default NVRTC path.

## Inputs

This round used the staged Goal 38 state-filtered exact-source subset:

- county input: `build/goal38/top4_tx_ca_ny_pa/county`
- zipcode input: `build/goal38/top4_tx_ca_ny_pa/zipcode`

Converted input counts:

- county pages: `1`
- county features: `441`
- county chains: `1612`
- zipcode pages: `15`
- zipcode features: `7035`
- zipcode chains: `10144`

## Method

Selection policy:

- reuse the Goal 28D / Goal 34 face-overlap rule
- choose one county face and `N` overlapping zipcode faces
- keep the lowest estimated segment-cost slice for each requested `1xN` point

Requested ladder:

- `1x4`
- `1x5`
- `1x6`
- `1x8`
- `1x10`
- `1x12`

Workloads:

- `lsi`
- `pip`

Backends compared:

- `rt.run_cpu(...)` as the native C/C++ oracle
- `rt.run_optix(...)` as the GPU path

Measurement policy:

- warmup: `1`
- measured iterations: `3`
- OptiX records both:
  - first-call JIT time
  - warm-call median time

Acceptance rule:

- exact-row parity must hold for both `lsi` and `pip`

## Results

### Accepted points

| Slice | County Face | Estimated Segments | `lsi` CPU Median (s) | `lsi` OptiX JIT (s) | `lsi` OptiX Warm Median (s) | `lsi` Speedup | `pip` CPU Median (s) | `pip` OptiX JIT (s) | `pip` OptiX Warm Median (s) | `pip` Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1x8` | `2300` | `1735` | `0.005212429` | `0.006302653` | `0.006061570` | `0.86x` | `0.001291558` | `0.002533343` | `0.002484003` | `0.52x` |
| `1x10` | `2300` | `1880` | `0.005765107` | `0.006711563` | `0.006589364` | `0.87x` | `0.001314003` | `0.002543507` | `0.002480663` | `0.53x` |

Both accepted points were exact-row parity-clean for both workloads.

Observed row counts:

- `1x8`
  - `lsi`: CPU `0`, OptiX `0`
  - `pip`: CPU `8`, OptiX `8`
- `1x10`
  - `lsi`: CPU `5`, OptiX `5`
  - `pip`: CPU `10`, OptiX `10`

Important nuance:

- `1x8` is still a valid exact-row parity point, but the `lsi` side is a
  zero-row case (`0 == 0`). So it is a weaker `lsi` signal than `1x10`, which
  has non-zero `lsi` rows on both backends.

### Rejected points

| Slice | County Face | Estimated Segments | `lsi` Exact-Row Parity | `pip` Exact-Row Parity | Notes |
| --- | ---: | ---: | --- | --- | --- |
| `1x4` | `2677` | `867` | `false` | `false` | OptiX returned more `lsi` rows and mismatched `pip` rows. |
| `1x5` | `2677` | `1083` | `false` | `false` | Same county family as `1x4`; still not parity-clean. |
| `1x6` | `2677` | `1320` | `false` | `false` | Same county family as `1x4`; still not parity-clean. |
| `1x12` | `2300` | `2080` | `false` | `true` | `pip` remains clean, but `lsi` diverges beyond `1x10`. |

## Interpretation

Goal 45 proves that the OptiX backend can now execute the first real exact-source
RayJoin family on the GPU host, but it does **not** yet prove that the current
OptiX path is uniformly parity-clean across the whole bounded County/Zipcode
ladder.

The current truthful OptiX position on this family is:

- exact-row parity is clean at `1x8`
- exact-row parity is clean at `1x10`
- a different county family (`2677`) fails at `1x4`, `1x5`, and `1x6`
- the `2300` family stays clean through `1x10` but fails at `1x12` for `lsi`

That means the current GPU path is **usable but not yet closure-ready** for
this real-data family.

## Performance reading

Within the accepted parity-clean points, warm OptiX is still slightly slower
than the native C oracle:

- `lsi`: about `0.86x` to `0.87x`
- `pip`: about `0.52x` to `0.53x`

This is not a failure of the goal. The purpose of Goal 45 was to establish:

- real-data GPU execution
- real-data correctness boundaries
- first bounded performance evidence on that real data

The result is that correctness boundary discovery mattered more than raw speed
in this round.

## What Goal 45 Closed

Goal 45 closed:

- the first real exact-source RayJoin-family OptiX run on `192.168.1.20`
- a reproducible bounded GPU harness for County/Zipcode slices
- exact-row correctness classification for the bounded `1xN` ladder
- first real-data OptiX timing evidence on that family

## Boundary

Goal 45 does **not** claim:

- full County/Zipcode OptiX correctness
- whole-dataset or state-scale County/Zipcode GPU closure
- parity across the full bounded ladder
- that OptiX is already faster than the native C oracle on these small exact-source slices

The honest closure statement is:

- RTDL OptiX now runs real exact-source County/Zipcode slices on the GPU host
- exact-row parity is proven on accepted bounded points `1x8` and `1x10`
- the current OptiX backend still has unresolved real-data correctness gaps on
  other County/Zipcode slices, especially `1x4`, `1x5`, `1x6`, and `1x12`

## Next goal

The next correct OptiX goal is:

- diagnose why County face `2677` fails at `1x4` / `1x5` / `1x6`
- diagnose why the `2300` family fails at `1x12` for `lsi`
- restore parity on this bounded real-data County/Zipcode ladder before moving
  to broader real-data GPU testing
