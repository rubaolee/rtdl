# Goal 47 Report: OptiX Large Checks Matching Goal 41

Date: 2026-04-02

## Scope

Goal 47 extends the Goal 41 large-check pattern from:

- native C/C++ oracle vs Embree

to:

- native C/C++ oracle vs OptiX

using the same Linux host and the same two larger real-data families:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

## Host and runtime boundary

- host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- PTX compiler path:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

## Inputs

### County/Zipcode

- county input: `build/goal38/top4_tx_ca_ny_pa/county`
- zipcode input: `build/goal38/top4_tx_ca_ny_pa/zipcode`

Converted counts:

- county features: `441`
- zipcode features: `7035`
- county chains: `1612`
- zipcode chains: `10144`

### BlockGroup/WaterBodies

- blockgroup input:
  `build/goal36_linux_blockgroup_waterbodies_performance/county2300_s10/blockgroup_feature_layer`
- waterbodies input:
  `build/goal36_linux_blockgroup_waterbodies_performance/county2300_s10/waterbodies_feature_layer`

Converted counts:

- blockgroup features: `279`
- waterbodies features: `172`
- blockgroup chains: `287`
- waterbodies chains: `248`

## Results

## County/Zipcode `top4_tx_ca_ny_pa`

### `lsi`

- pair parity: `true`
- C oracle: `88.599141448 s`
- OptiX: `49.997142295 s`
- row count: `107513`
- OptiX speedup vs C oracle: about `1.77x`

For comparison with the published Goal 41 Embree result:

- Embree: `82.733328274 s`
- OptiX is about `1.65x` faster than Embree on this check

### `pip`

- row parity: `true`
- C oracle: `152.125731922 s`
- OptiX: `81.557032659 s`
- row count: `16352128`
- OptiX speedup vs C oracle: about `1.87x`

For comparison with the published Goal 41 Embree result:

- Embree: `158.767087551 s`
- OptiX is about `1.95x` faster than Embree on this check

## BlockGroup/WaterBodies `county2300_s10`

### `lsi`

- pair parity: `true`
- C oracle: `0.509446987 s`
- OptiX: `0.238977900 s`
- row count: `216`
- OptiX speedup vs C oracle: about `2.13x`

For comparison with the published Goal 41 Embree result:

- Embree: `0.198707218 s`
- OptiX is slower than Embree here by about `0.83x`

### `pip`

- row parity: `true`
- C oracle: `0.236069220 s`
- OptiX: `0.168598965 s`
- row count: `71176`
- OptiX speedup vs C oracle: about `1.40x`

For comparison with the published Goal 41 Embree result:

- Embree: `0.192549768 s`
- OptiX is about `1.14x` faster than Embree here

## Interpretation

Goal 47 closes the exact comparison you asked for:

- the same larger real-data checks published in Goal 41
- but with OptiX instead of Embree

Current result:

- both larger families are parity-clean against the native C oracle on
  `192.168.1.20`
- OptiX is clearly faster than the C oracle on all four workload/family pairs
- relative to Embree:
  - OptiX is faster on the larger County/Zipcode checks
  - OptiX is mixed on `county2300_s10`:
    - slower on `lsi`
    - faster on `pip`

## Boundary

Goal 47 does **not** claim:

- full paper-scale OptiX reproduction
- that OptiX is uniformly faster than Embree on every real-data workload
- that the current OptiX backend is pure GPU refine

The honest closure statement is:

- the Goal 41 larger-check pattern now exists for OptiX as well
- both `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa` and
  `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  are parity-clean against the native C oracle on the GPU host
- the current large-check OptiX path is already competitive and sometimes
  faster than Embree, but the results remain workload-dependent
