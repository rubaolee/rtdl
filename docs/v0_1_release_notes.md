# RTDL v0.1 Release Notes

Date: 2026-04-05
Status: released

## What RTDL v0.1 is

RTDL v0.1 is the first bounded, reviewed release slice of the project.

In plain terms, it shows that:

- RTDL can express a real non-graphical ray-tracing workload family
- the same workload can run across multiple serious backends
- correctness can be checked against internal oracles and PostGIS
- performance claims can be made with explicit, honest timing boundaries

The motivating workload family is from:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI `10.1145/3650200.3656610`

## Strongest current claims

The strongest current performance closure is:

- long exact-source `county_zipcode`
- positive-hit `pip`

On that accepted surface:

- RTDL + OptiX beats PostGIS on the published prepared and repeated raw-input
  boundaries
- RTDL + Embree does too
- RTDL + Vulkan is parity-clean on the same surface, but slower

Primary evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal93_rayjoin_reproduction_release_matrix_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`

## Trust anchor

The bounded package remains the v0.1 trust anchor:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

## Backend status

### OptiX

- mature high-performance backend on the accepted long exact-source
  `county_zipcode` positive-hit `pip` surface

### Embree

- mature high-performance CPU backend on the same accepted surface

### Vulkan

- supported and hardware-validated
- parity-clean on the accepted long exact-source surface
- slower than PostGIS, OptiX, and Embree there

## Correctness position

- Python oracle:
  - trusted on deterministic mini envelopes
- native C oracle:
  - trusted on deterministic small envelopes
- PostGIS:
  - external indexed comparison baseline on accepted workload packages

## What v0.1 does not claim

RTDL v0.1 does not claim:

- full paper-identical reproduction of every RayJoin dataset family
- exact computational geometry everywhere
- full polygon overlay materialization
- equal maturity across all backends and workload families
- competitive Vulkan performance on the accepted long exact-source surface

## Known issues / current limits

- current native `pip` lowering supports `boundary_mode='inclusive'`
- Vulkan is a supported backend but not a competitive performance backend on
  the accepted long exact-source surface
- the bounded package is still the main v0.1 trust anchor even though the
  strongest current performance evidence is the long exact-source
  `county_zipcode` row
- `overlay` remains a seed-generation analogue, not full polygon
  materialization

## Canonical reading path

Read these first:

1. `/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md`
2. `/Users/rl2025/rtdl_python_only/docs/architecture_api_performance_overview.md`
3. `/Users/rl2025/rtdl_python_only/docs/current_milestone_qa.md`
4. `/Users/rl2025/rtdl_python_only/docs/v0_1_reproduction_and_verification.md`
5. `/Users/rl2025/rtdl_python_only/docs/v0_1_support_matrix.md`
6. `/Users/rl2025/rtdl_python_only/docs/future_ray_tracing_directions.md`
