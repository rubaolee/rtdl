# Goal 104 Report: RayJoin Reproduction Performance Report

Date: 2026-04-05
Status: complete

## Purpose

Goals 102 and 103 froze the current honest RayJoin-facing reproduction packages:

- Goal 102:
  - Embree + OptiX package
- Goal 103:
  - Vulkan-only package

Those goals are intentionally matrix-oriented. This report complements them by
explaining the performance evidence in one place with more detail on:

- experiment boundaries
- dataset packages
- measured results
- interpretation

## Experiment Boundaries

The same workload can be measured under more than one honest timing boundary.
Those boundaries must not be merged into one number.

### 1. Prepared / prepacked boundary

This boundary:

- prepares the kernel
- packs points and polygons
- binds execution state
- then measures backend execution through the prepared object

This is the fairest way to compare backend execution once the author or runtime
has already reached an execution-ready state.

### 2. Repeated raw-input boundary

This boundary:

- starts from ordinary raw RTDL inputs
- lets the runtime own any caching or prepared-execution reuse
- measures repeated calls in the same process

This is important because it shows what a user gets without manually calling
prepare or pack APIs.

### 3. Bounded support rows

Some accepted rows use smaller or narrower package surfaces such as:

- `top4_tx_ca_ny_pa`
- `county2300_s10`
- `sunshine_tiny`

These are still real and useful, but they are support rows rather than the
main long flagship row.

## Dataset Packages

### Long exact-source flagship row

The main current flagship workload is:

- `county_zipcode`
- positive-hit `pip`

This is the strongest current row because:

- it uses the accepted long exact-source execution path
- it has mature results for Embree, OptiX, and Vulkan
- it compares directly against PostGIS

In the strict Goal 102 / Goal 103 classification, it is still only a
`bounded_analogue`, because the package is not the paper-identical full dataset
surface.

### Bounded top4 support row

The strongest bounded support row is:

- `county_zipcode`
- positive-hit `pip`
- `top4_tx_ca_ny_pa`

This row is valuable because:

- it is smaller and easier to rerun
- it is parity-clean across the accepted backends
- it shows warmed prepared and repeated raw-input behavior on a real package

### Other bounded support families

The broader bounded package also includes:

- `BlockGroup ⊲⊳ WaterBodies` on `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU` on `sunshine_tiny`
- overlay-seed analogue rows

Those matter to the reproduction matrix, but they are not the main current
performance story.

## Goal 102: Embree and OptiX Package

Goal 102 is the full honest bounded RayJoin reproduction package for:

- Embree
- OptiX

### Long exact-source prepared boundary

#### Embree

- backend:
  - `1.7738651990002836 s`
- PostGIS:
  - `3.40269520500442 s`
- parity:
  - `true`

#### OptiX

- backend:
  - `2.5369022019876866 s`
  - `2.133376205994864 s`
- PostGIS:
  - `3.39459279399307 s`
  - `3.01533580099931 s`
- parity:
  - `true`

Interpretation:

- both mature RTDL backends beat PostGIS on the accepted long prepared row
- Embree is the faster of the two on this row
- OptiX still carries more cold-start structure around bind/warmup, but the
  accepted Goal 99 path moved enough one-time work out of the first timed run
  to close the run-1 gap

### Long exact-source repeated raw-input boundary

#### Embree

- first:
  - `1.959970190000604 s`
- best repeated:
  - `1.0921905469949706 s`
- PostGIS comparison:
  - about `3.1886126509998576 s` to `3.5830304580013035 s`
- parity:
  - `true`

#### OptiX

- first:
  - `4.49759002099745 s`
- best repeated:
  - `2.124993502991856 s`
- PostGIS comparison:
  - about `2.986209955997765 s` to `3.407562541004154 s`
- parity:
  - `true`

Interpretation:

- Embree has the strongest first-call and repeated-call story on the long row
- OptiX is slower on the first raw-input call, but wins once runtime-owned
  reuse takes effect
- the difference matters because repeated raw-input is a user-facing boundary,
  not a manually prepacked benchmark

### Fresh bounded top4 support reruns

Goal 102 also added fresh Linux reruns on:

- `top4_tx_ca_ny_pa`
- row count `7863`

#### Prepared / prepacked

Embree:

- `0.1821604330034461 s`
- `0.14840258299955167 s`

OptiX:

- `0.18207618700398598 s`
- `0.1791208380018361 s`

PostGIS:

- about `0.36855210599605925 s` to `0.4167834419931751 s`

Parity:

- `true`

#### Repeated raw-input

Embree:

- first `0.20209797599818558 s`
- best repeated `0.1451086979941465 s`

OptiX:

- first `1.0346060559968464 s`
- best repeated `0.17935199600469787 s`

PostGIS:

- about `0.37192401199718006 s` to `0.3768596890004119 s`

Parity:

- `true`

Interpretation:

- both mature backends are comfortably inside the PostGIS time range on the
  warmed support rows
- Embree is especially strong on the bounded row
- OptiX still shows a larger first-call gap than Embree, but its repeated
  result is strong

## Goal 103: Vulkan-Only Package

Goal 103 is the Vulkan-only honest RayJoin reproduction package.

Its value is different:

- support
- correctness
- hardware validation

not mature-performance closure.

### Long exact-source prepared boundary

Vulkan:

- `6.139390789991012 s`
- `6.164127523996285 s`

PostGIS:

- `3.2591196079883957 s`
- `3.0466118039912544 s`

Parity:

- `true`

Interpretation:

- Vulkan now runs the same long prepared flagship row as the other backends
- this was not true before the Goal 87 allocation-contract repair
- Vulkan is still materially slower than PostGIS on this row

### Long exact-source repeated raw-input boundary

Vulkan:

- first `16.14024098799564 s`
- best repeated `6.709643080001115 s`

PostGIS:

- about `3.0880011199915316 s` to `3.125241542002186 s`

Parity:

- `true`

Interpretation:

- repeated-call reuse helps Vulkan materially
- but not enough to become competitive with PostGIS on the long flagship row

### Bounded top4 prepared support row

Vulkan:

- `0.8581980200033286 s`
- `0.3335896480057272 s`

PostGIS:

- `0.39323220199730713 s`
- `0.4003148310002871 s`

Parity:

- `true`

Interpretation:

- this row is important because it shows Vulkan is not only a long-row loss
  story
- on the warmed bounded prepared slice, Vulkan can beat PostGIS
- but the broader long-row position is still slower

### Hardware validation context

Goal 85 also established:

- Goal 51 Vulkan ladder:
  - `8 / 8` parity-clean
- focused Vulkan unit/backend slice:
  - `20` tests
  - `OK`

This matters because the Vulkan package is not just one benchmark. It is backed
by hardware validation and parity testing.

## Comparative Reading

### Embree

Embree is currently the best all-around backend on the flagship row:

- strongest prepared result
- strongest repeated raw-input result
- strong first-call behavior

### OptiX

OptiX is a mature performance backend, but more sensitive to first-call setup
costs:

- wins on prepared and repeated-call boundaries
- weaker than Embree on the first raw-input call

### Vulkan

Vulkan is real and supported, but its current role is different:

- parity-clean
- hardware-validated
- slower on the main long row
- useful warmed bounded support row

## What These Results Mean

The main conclusion is not just ``some backend is fast.'' It is:

- RTDL is no longer only a language experiment
- it now has a real backend-performance story on a serious flagship workload
- that story is strongest for Embree and OptiX
- Vulkan is a supported portability backend, not the current performance leader

## What These Results Do Not Mean

- they do not make the package paper-identical to RayJoin
- they do not imply all workload families are equally mature
- they do not imply Vulkan is close to Embree or OptiX on the flagship row
- they do not imply overlay is full polygon materialization

## Source Packages

Main source reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal103_full_honest_rayjoin_reproduction_vulkan_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal84_exact_source_long_backend_summary_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal99_optix_cold_prepared_run1_win_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_hardware_validation_and_measurement_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_unblocked_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_measurement_2026-04-05.md`

## Conclusion

Goals 102 and 103 now provide a clear current performance picture:

- Embree and OptiX are the mature RTDL performance backends on the strongest
  current RayJoin-facing row
- Vulkan is a parity-clean and hardware-validated backend, but slower on that
  row
- the bounded support rows strengthen the story without changing the honest
  classification boundary

This report exists so future contributors do not have to reconstruct the
performance narrative from dozens of goal packages.
