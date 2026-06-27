# Goal 65 Vulkan OptiX Linux Comparison

Date: 2026-04-04

## Scope

This round brings the Vulkan backend onto the validated Linux GPU host
`192.168.1.20` and compares it directly with OptiX on already accepted RTDL
workload packages.

Compared backends:

- native C oracle
- Embree
- OptiX
- Vulkan

Host:

- GPU: `NVIDIA GeForce GTX 1070`
- driver: `580.126.09`
- OptiX runtime: `9.0.0`
- Vulkan runtime: `0.1.0`

## Execution Boundary

This was not a new PostGIS closure round. Correctness in this goal is judged
against the native C oracle.

The comparison surface had to be bounded for Vulkan:

- whole `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa` `lsi`
  - not runnable on Vulkan under the current `uint32` output-capacity contract
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s06` and larger `lsi`
  - not runnable on Vulkan under the current `512 MiB` output guardrail

So the accepted execution surface for this goal was:

- bounded County/Zipcode ladder:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`
- bounded BlockGroup/WaterBodies ladder:
  - `county2300_s04`
  - `county2300_s05`
- bounded `LKAU ⊲⊳ PKAU` `sunshine_tiny` overlay-seed analogue

## Method

For OptiX and Vulkan, the harness recorded:

- `prepare`
- one explicit `cold` run
- one explicit `warm` run

The warm run is the performance number that should be compared between the two
GPU backends.

## Preflight

Remote preflight succeeded in the fresh Linux workspace:

- `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev`
- `make build-vulkan`
- `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test`
- `PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc python3 scripts/goal51_vulkan_validation.py`

So the Goal 65 result is based on a working Vulkan/OptiX runtime surface, not a
partial build.

## Results

### 1. County ⊲⊳ Zipcode bounded `1xN` ladder

| Slice | LSI Vulkan parity | LSI OptiX warm (s) | LSI Vulkan warm (s) | PIP Vulkan parity | PIP OptiX warm (s) | PIP Vulkan warm (s) |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `1x4`  | `false` | `0.000930833` | `0.005809129` | `true`  | `0.000726618` | `0.005979543` |
| `1x5`  | `false` | `0.000892708` | `0.005805939` | `true`  | `0.000611246` | `0.005976502` |
| `1x6`  | `false` | `0.000927019` | `0.006035639` | `true`  | `0.000617870` | `0.005841251` |
| `1x8`  | `true`  | `0.001059584` | `0.006101319` | `false` | `0.002209153` | `0.006875637` |
| `1x10` | `true`  | `0.001121010` | `0.006181103` | `false` | `0.002209614` | `0.006437628` |
| `1x12` | `false` | `0.001222988` | `0.006165551` | `false` | `0.002223369` | `0.006297578` |

County/Zipcode conclusion:

- Vulkan does not fully close any accepted County/Zipcode slice in this ladder.
- Where Vulkan *is* parity-clean:
  - `pip` on `1x4`, `1x5`, `1x6`
  - `lsi` on `1x8`, `1x10`
- On those parity-clean subsets, OptiX warm runtime is consistently faster than
  Vulkan warm runtime.

### 2. BlockGroup ⊲⊳ WaterBodies bounded ladder

| Slice | LSI Vulkan parity | LSI OptiX warm (s) | LSI Vulkan warm (s) | PIP Vulkan parity | PIP OptiX warm (s) | PIP Vulkan warm (s) |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `county2300_s04` | `true`  | `0.006040863` | `0.010001875` | `false` | `0.007592129` | `0.010334869` |
| `county2300_s05` | `true`  | `0.010950862` | `0.014589073` | `false` | `0.013551100` | `0.014783905` |

BlockGroup/WaterBodies conclusion:

- Vulkan is parity-clean for `lsi` on `county2300_s04` and `county2300_s05`.
- Vulkan is not parity-clean for `pip` on either accepted block/water slice.
- On the parity-clean `lsi` rows, OptiX remains faster than Vulkan.

### 3. LKAU ⊲⊳ PKAU overlay-seed analogue

| Workload | Vulkan parity | OptiX warm (s) | Vulkan warm (s) |
| --- | --- | ---: | ---: |
| `overlay-seed` | `false` | `0.083965907` | `0.067124664` |

Overlay conclusion:

- Vulkan is faster than OptiX on this bounded overlay-seed analogue.
- That speed result is not currently acceptable as a correctness-backed win,
  because Vulkan is not parity-clean on this workload.

## Overall Conclusion

Goal 65 succeeds as a Linux validation/comparison round, but not as a Vulkan
closure round.

What is now proven:

- Vulkan is built and runnable on `192.168.1.20`.
- Vulkan can execute accepted bounded RTDL packages on that host.
- OptiX remains parity-clean against the native C oracle across the tested Goal
  65 surface.
- Vulkan is only partially parity-clean:
  - some County/Zipcode `pip`
  - some County/Zipcode `lsi`
  - bounded BlockGroup/WaterBodies `lsi`
- Vulkan is not yet parity-clean for:
  - all County/Zipcode bounded slices
  - BlockGroup/WaterBodies `pip`
  - bounded `LKAU ⊲⊳ PKAU` overlay-seed

Performance conclusion under the correctness boundary:

- On the workloads where both GPU backends are parity-clean, OptiX warm runtime
  is consistently better than Vulkan warm runtime on this GTX 1070 host.
- Vulkan only appears faster on the bounded overlay-seed analogue, but that
  result is not yet correctness-acceptable.

## Next Technical Implications

The Vulkan backend is still **provisional** after this round.

Concrete remaining Vulkan issues exposed by Goal 65:

1. `lsi` capacity design does not scale to the larger accepted package tiers.
2. `pip` semantics still diverge from the native C oracle on multiple accepted
   bounded packages.
3. `overlay-seed` semantics still diverge from the native C oracle on the
   bounded Australia package.

So the current project position after Goal 65 is:

- OptiX remains the accepted GPU backend.
- Vulkan is now tested on the Linux GPU host with exact evidence.
- Vulkan is not yet ready to join the accepted bounded four-system closure set.
