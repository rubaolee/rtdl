# Goal 34 Linux Embree Performance Characterization

Date: 2026-04-02

## Scope

Goal 34 used `192.168.1.20` as the serious Linux Embree performance host for the first exact-source family that is fully staged and parity-clean today:

- `County ⊲⊳ Zipcode`

The purpose of this round was to measure the current local Embree backend on exact-source slices that remained parity-clean after Goal 31 and Goal 32.

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Method

Inputs:

- full staged `USCounty` ArcGIS pages
- full staged `Zipcode` ArcGIS pages

Selection policy:

- reuse the Goal 28D face-overlap selection rule
- choose one county face and `N` overlapping zipcode faces
- keep the lowest estimated segment-cost slice for each requested `1xN` point

Measured workloads:

- `lsi`
- `pip`

Backends:

- `rt.run_cpu(...)`
- `rt.run_embree(...)`

Measurement policy:

- warmup: `1`
- measured iterations: `3`
- accepted point = parity-clean for both `lsi` and `pip`

Planned ladder:

- `1x4`
- `1x5`
- `1x6`
- `1x8`
- stretch: `1x10`, `1x12`

## Harness

The round added a dedicated reproducible harness:

- [goal34_linux_embree_performance.py](../../scripts/goal34_linux_embree_performance.py)

and test coverage:

- [goal34_performance_test.py](../../tests/goal34_performance_test.py)

## Results

All attempted points were accepted in this round.

| Slice | Estimated Segments | `lsi` CPU Median (s) | `lsi` Embree Median (s) | `lsi` Speedup | `pip` CPU Median (s) | `pip` Embree Median (s) | `pip` Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1x4` | `631` | `0.018810398` | `0.001951754` | `9.64x` | `0.000607311` | `0.000478698` | `1.27x` |
| `1x5` | `772` | `0.039446919` | `0.002359525` | `16.72x` | `0.000662559` | `0.000476208` | `1.39x` |
| `1x6` | `921` | `0.062070701` | `0.002815368` | `22.05x` | `0.000748862` | `0.000483146` | `1.55x` |
| `1x8` | `1530` | `0.169970314` | `0.004655572` | `36.51x` | `0.001392166` | `0.000732959` | `1.90x` |
| `1x10` | `1880` | `0.172933934` | `0.005615700` | `30.79x` | `0.003049136` | `0.001310584` | `2.33x` |
| `1x12` | `2080` | `0.259253125` | `0.006209437` | `41.75x` | `0.003330779` | `0.001340347` | `2.48x` |

Rejected points:

- none

## Interpretation

### `lsi`

The current local Embree path is now clearly faster than the Python reference path on Linux exact-source county/zipcode slices.

The measured Linux speedup is already material at the smallest accepted slice and grows strongly as the segment workload grows:

- `1x4`: about `9.64x`
- `1x12`: about `41.75x`

That is consistent with the current architecture:

- CPU path = Python reference oracle
- Embree path = native local `native_loop` sort-sweep candidate pass plus native refine/emit path

So this round shows that the post-Goal-32 local Embree path is now a serious execution backend for exact-source `lsi` on Linux.

### `pip`

`pip` also benefits from Embree, but the speedup is much smaller than `lsi` on this ladder:

- `1x4`: about `1.27x`
- `1x12`: about `2.48x`

That is still useful, but it means:

- current Linux Embree value is much more dramatic for `lsi`
- `pip` remains comparatively close to the Python reference cost on these bounded slices

## What Goal 34 Closed

Goal 34 closed:

- a reproducible Linux Embree performance harness for the first full exact-source family
- accepted parity-clean Linux exact-source performance points through `1x12`
- the first serious Linux performance characterization for the current local Embree backend

## Boundary

Goal 34 does **not** claim:

- full RayJoin paper reproduction at original scale
- that `County ⊲⊳ Zipcode` is fully solved at whole-dataset execution scale
- that the current local `lsi` path is BVH-backed
- that these Linux results generalize automatically to future OptiX / GPU backends

The honest closure statement is:

- the current local Embree backend is now parity-clean and materially faster than the Python oracle on Linux exact-source `County ⊲⊳ Zipcode` slices
- this is the first serious Linux Embree performance baseline for RTDL v0.1
