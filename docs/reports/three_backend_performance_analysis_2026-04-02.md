# Three-Backend Performance Analysis on `192.168.1.20`

Date: 2026-04-02

## Purpose

This note consolidates the currently published larger real-data performance
results across all three execution paths now available on the Linux host:

- native C/C++ oracle
- Embree backend
- OptiX backend

It focuses on the two larger real-data checks that now exist for all required
paths:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

## Source reports

- C oracle vs Embree:
  - [/Users/rl2025/rtdl_python_only/docs/reports/goal41_cross_host_oracle_correctness_2026-04-02.md](goal41_cross_host_oracle_correctness_2026-04-02.md)
- C oracle vs OptiX:
  - [/Users/rl2025/rtdl_python_only/docs/reports/goal47_optix_goal41_large_checks_2026-04-02.md](goal47_optix_goal41_large_checks_2026-04-02.md)

## Important comparison boundary

These are the best currently published numbers, but they do **not** all come
from one single unified back-to-back harness run.

That means:

- correctness comparisons are strong
- performance comparisons are useful
- but some timing differences, especially on the smaller `county2300_s10` case,
  should still be treated as provisional until we run one single 3-way harness
  in one round

The biggest reason for caution is that the published C-oracle timing for
`county2300_s10` differs materially between Goal 41 and Goal 47, even though
the row counts remain parity-clean.

## Consolidated results

## 1. `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`

### `lsi`

| Backend | Time (s) | Relative to C Oracle |
| --- | ---: | ---: |
| C oracle | `88.391632435` | `1.00x` |
| Embree | `82.733328274` | `1.07x faster` |
| OptiX | `49.997142295` | `1.77x faster` |

Additional comparison:

- OptiX vs Embree: about `1.65x` faster

### `pip`

| Backend | Time (s) | Relative to C Oracle |
| --- | ---: | ---: |
| C oracle | `151.869952414` | `1.00x` |
| Embree | `158.767087551` | `0.96x` (`~4.5%` slower) |
| OptiX | `81.557032659` | `1.86x faster` |

Additional comparison:

- OptiX vs Embree: about `1.95x` faster

### Main insight

On the large County/Zipcode exact-source package:

- OptiX is the fastest of the three
- Embree is close to the C oracle on `lsi`
- Embree is slightly slower than the C oracle on `pip`
- the GPU path already shows clear value on this family

## 2. `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

### `lsi`

| Backend | Time (s) | Relative to C Oracle |
| --- | ---: | ---: |
| C oracle | `0.509446987` | `1.00x` |
| Embree | `0.198707218` | `2.56x faster` |
| OptiX | `0.238977900` | `2.13x faster` |

Additional comparison:

- Embree vs OptiX: Embree is about `1.20x` faster

### `pip`

| Backend | Time (s) | Relative to C Oracle |
| --- | ---: | ---: |
| C oracle | `0.236069220` | `1.00x` |
| Embree | `0.192549768` | `1.23x faster` |
| OptiX | `0.168598965` | `1.40x faster` |

Additional comparison:

- OptiX vs Embree: OptiX is about `1.14x` faster

### Main insight

On the current bounded `county2300_s10` slice:

- OptiX is **not uniformly better**
- Embree wins on `lsi`
- OptiX wins on `pip`

This is the clearest current example that backend advantage is
workload-dependent.

## Why OptiX is faster or slower

## Why OptiX is faster on large County/Zipcode

### 1. More available parallelism

The `top4_tx_ca_ny_pa` package is large:

- `lsi` rows: `107513`
- `pip` rows: `16352128`

That gives the GPU enough work to amortize:

- kernel launch overhead
- OptiX pipeline overhead
- PTX/JIT setup cost

The workload is large enough that GPU candidate generation and parallel output
handling matter.

### 2. OptiX benefits from broad parallel candidate traversal

Even with the current exact host-side refine boundary, the GPU still does the
front-end candidate work in parallel. On the larger County/Zipcode package,
that is already enough to beat the CPU-side paths materially.

### 3. The C oracle is still a general semantic oracle, not a throughput engine

The native oracle is much faster than the old Python simulator, but it is still
designed first for correctness and parity. It is not specialized as aggressively
as a production GPU traversal path.

## Why OptiX is mixed on `county2300_s10`

### 1. The workload is much smaller

`county2300_s10` is tiny compared with `top4_tx_ca_ny_pa`:

- `lsi` rows: `216`
- `pip` rows: `71176`

That means:

- GPU setup and transfer overhead matters much more
- backend constant factors dominate more than raw throughput

### 2. Goal 46 shifted OptiX toward correctness-first design

The current OptiX real-data path uses:

- GPU candidate generation
- exact native host-side refine

That design is good for correctness, but it reduces the chance that OptiX will
win on smaller slices where the host-side refine becomes a larger fraction of
the total cost.

This is especially visible for `lsi`.

### 3. `pip` still benefits from GPU-side front-end structure

Even on the smaller slice, `pip` remains slightly favorable for OptiX relative
to Embree. That suggests the current GPU path still helps on containment-style
work, even when the overall package is not large.

## Practical interpretation

Current evidence suggests:

### Embree

- stronger today as the general CPU backend
- more mature across families
- highly competitive on smaller or mid-size real-data checks
- especially strong on bounded `lsi`

### OptiX

- already worthwhile on large real-data packages
- clearly beneficial on the large County/Zipcode package
- not yet uniformly superior on every tested real-data family
- still influenced by the current correctness-first host-refine design

### C oracle

- trustworthy ground truth
- not the final throughput target
- best used as the correctness reference and a baseline for backend efficiency

## Bottom line

If we compare all three currently published larger Linux results:

- **largest package (`County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`)**
  - OptiX is best
  - Embree is second
  - C oracle is slowest

- **smaller bounded package (`BlockGroup ⊲⊳ WaterBodies` `county2300_s10`)**
  - `lsi`: Embree is best
  - `pip`: OptiX is best
  - C oracle is slowest

So the current insight is:

- OptiX advantage is real, but **size- and workload-dependent**
- Embree remains a very strong backend and is not simply dominated by OptiX
- the current OptiX correctness-first implementation likely underestimates the
  long-term GPU upside for some smaller real-data workloads

## Next measurement that would improve confidence

The best next experiment is a single unified 3-way harness that runs:

- C oracle
- Embree
- OptiX

back-to-back in one round on:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

That would remove cross-round timing drift and give the cleanest possible
three-backend comparison.
