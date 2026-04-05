# Goal 103 Report: Full Honest RayJoin Reproduction, Vulkan-Only

Date: 2026-04-05
Status: complete

## Objective

Freeze the fullest honest RayJoin-facing reproduction package currently
supported by RTDL when Vulkan is the only RTDL execution backend.

This is intentionally not a paper-identical reproduction claim.

## Strict classification rule

This package uses the same strict rule as Goal 102:

- `exact` means paper-identical dataset coverage
- `bounded_analogue` means the row is real and accepted, but narrower than the
  paper's original dataset or reproduction boundary
- `unavailable` means the row was considered explicitly but no acceptable
  Vulkan artifact exists
- `not_applicable` means the paper surface does not exist in the current RTDL
  Vulkan execution model

Under that rule, **no current Vulkan row qualifies as `exact`**.

## Final Vulkan-only matrix

### Table 3 style workload families

| Paper row | Workload | Goal 103 class | Current Vulkan evidence |
| --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi` | `unavailable` | no accepted Vulkan LSI RayJoin-facing row |
| County ⊲⊳ Zipcode | `pip` | `bounded_analogue` | strongest current Vulkan row; prepared and repeated raw-input both measured |
| Block ⊲⊳ Water | `lsi` | `unavailable` | no accepted Vulkan analogue row |
| Block ⊲⊳ Water | `pip` | `unavailable` | no accepted Vulkan analogue row |
| LKAU ⊲⊳ PKAU | `lsi`, `pip` | `unavailable` | no accepted Vulkan reproduction artifact |
| LKAF ⊲⊳ PKAF | `lsi`, `pip` | `unavailable` | dataset/acquisition absent for Vulkan package |
| LKAS ⊲⊳ PKAS | `lsi`, `pip` | `unavailable` | unstaged |
| LKEU ⊲⊳ PKEU | `lsi`, `pip` | `unavailable` | unstaged |
| LKNA ⊲⊳ PKNA | `lsi`, `pip` | `unavailable` | unstaged |
| LKSA ⊲⊳ PKSA | `lsi`, `pip` | `unavailable` | unstaged |

### Figure 13 style scalability

Figure 13 Vulkan rows are classified as:

- `unavailable`

Reason:

- no accepted Vulkan-only Figure 13 artifact package exists in the current
  repository

### Figure 14 style scalability

Figure 14 Vulkan rows are classified as:

- `unavailable`

Reason:

- no accepted Vulkan-only Figure 14 artifact package exists in the current
  repository

### Table 4 / Figure 15 overlay

Overlay for the current Vulkan-only package is:

- `unavailable`

Reason:

- no accepted Vulkan overlay analogue artifact exists

The paper's full overlay materialization surface remains:

- `not_applicable`

for the current RTDL Vulkan execution model.

## Strongest current Vulkan row

The strongest current Vulkan RayJoin-facing row is:

- `county_zipcode`
- positive-hit `pip`

Prepared long exact-source:

- Vulkan:
  - `6.139390789991012 s`
  - `6.164127523996285 s`
- PostGIS:
  - `3.2591196079883957 s`
  - `3.0466118039912544 s`
- parity:
  - `true`

Repeated raw-input long exact-source:

- Vulkan:
  - first `16.14024098799564 s`
  - best repeated `6.709643080001115 s`
- PostGIS:
  - about `3.0880011199915316 s` to `3.125241542002186 s`
- parity:
  - `true`

This row is still a `bounded_analogue` for Goal 103 because it is not the
paper-identical full dataset package.

It is also still slower than PostGIS on both accepted long boundaries.

## Bounded Vulkan support row

Goal 85 provides the best bounded Vulkan support row:

- `top4_tx_ca_ny_pa`
- `county_zipcode`
- positive-hit `pip`
- prepared / prepacked boundary

Accepted result:

- row count `7863`
- parity `true`
- Vulkan:
  - `0.8581980200033286 s`
  - `0.3335896480057272 s`
- PostGIS:
  - `0.39323220199730713 s`
  - `0.4003148310002871 s`

This bounded row is important because it shows the Vulkan package is not only a
long-row loss story:

- it is parity-clean
- it materially improves on rerun
- it can beat PostGIS on the warmed bounded prepared slice

That still does not promote it beyond `bounded_analogue`.

## Hardware validation anchor

Goal 85 also established the non-performance Vulkan support baseline:

- Vulkan hardware smoke passed
- Goal 51 validation ladder:
  - `8 / 8` parity-clean
- focused Vulkan unit/backend slice:
  - `20` tests
  - `OK`

This does not itself make a RayJoin paper row, but it strengthens the honesty
of the Vulkan-only package by showing that the backend is real, validated, and
not just represented by one hand-picked benchmark.

## Carry-forward evidence used in this package

- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_hardware_validation_and_measurement_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_unblocked_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_measurement_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_2026-04-05.md`

Primary machine-readable artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_prepared_exact_source_artifacts_2026-04-04/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal85_vulkan_smoke_artifacts_2026-04-04/goal51_summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json`

## Honest outcome

Goal 103 closes as a **full honest bounded Vulkan-only reproduction package**.

What is honestly true now:

- the Vulkan-only RayJoin-facing matrix is frozen explicitly
- no row is silently omitted
- the strongest current Vulkan row is `county_zipcode` positive-hit `pip`
- Vulkan is parity-clean on the accepted long exact-source prepared and raw
  boundaries
- Vulkan remains slower than PostGIS on those long boundaries
- Vulkan has one useful bounded top4 prepared support row
- most other RayJoin paper rows remain explicit `unavailable` for a Vulkan-only
  package

What this report does not claim:

- that Vulkan reproduced the RayJoin paper broadly
- that any current Vulkan row is `exact`
- that Vulkan is mature-performance competitive with PostGIS, OptiX, or Embree
- that Vulkan currently supports full overlay materialization

## Conclusion

Goal 103 succeeds because it states the Vulkan story exactly as it is:

- real
- hardware-validated
- parity-clean on the accepted flagship row
- bounded
- incomplete across the broader paper matrix
- slower than PostGIS on the long flagship row

That is still a useful and publishable RTDL result.
