# Goal 93 Report: RayJoin Reproduction Release Matrix

Date: 2026-04-05
Status: complete

## Objective

Freeze the accepted RayJoin-style RTDL evidence into one release-facing
reproduction closure package.

This report does not introduce new experimental claims. It reconciles the
current accepted package and the strongest current long exact-source backend
closure into one release-facing matrix.

## Trust anchor

The bounded v0.1 package remains the trust anchor:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

## Strongest current performance surface

The strongest current performance surface is:

- long exact-source `county_zipcode`
- positive-hit `pip`

Accepted timing boundaries on that surface:

- prepared
- repeated raw-input

## Release-facing matrix

### Long exact-source `county_zipcode` positive-hit `pip`

Prepared boundary:

- PostGIS:
  - accepted indexed baseline
- OptiX:
  - parity-clean
  - warmed prepared win accepted
- Embree:
  - parity-clean
  - prepared win accepted
- Vulkan:
  - parity-clean
  - slower than PostGIS

Repeated raw-input boundary:

- PostGIS:
  - accepted indexed baseline
- OptiX:
  - parity-clean
  - repeated raw-input win accepted
- Embree:
  - parity-clean
  - repeated raw-input win accepted
- Vulkan:
  - parity-clean
  - repeated run improves materially
  - remains slower than PostGIS

### Bounded accepted package

`County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`:

- accepted across:
  - PostGIS
  - native C oracle
  - Embree
  - OptiX
  - Vulkan on the accepted bounded Linux surface

`BlockGroup ⊲⊳ WaterBodies` `county2300_s10`:

- accepted bounded package support row

bounded `LKAU ⊲⊳ PKAU`:

- accepted bounded package support row

bounded `overlay-seed analogue`:

- accepted bounded support row
- seed-generation analogue only, not full polygon materialization

## Skipped / unavailable / non-release surfaces

Not part of the v0.1 release claim surface:

- unstable or unavailable continent-scale dataset families
- paper-identical reproduction claims for every RayJoin dataset family
- full polygon overlay materialization
- oracle performance rows as peer backend-performance evidence
- any merged leaderboard that blurs prepared, raw-input, and bounded timings

## Source evidence

Primary source reports:

- `/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal79_linux_performance_reproduction_matrix_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal84_exact_source_long_backend_summary_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/architecture_api_performance_overview.md`

Primary machine-readable artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_artifacts_2026-04-04/optix/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal82_optix_pre_embree_audit_artifacts_2026-04-04/prepared/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/raw/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_artifacts_2026-04-04/prepared/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal87_vulkan_long_exact_source_artifacts_2026-04-05/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal88_vulkan_long_exact_raw_input_artifacts_2026-04-05/summary.json`

## Honest claim surface

Safe release claims:

- RTDL v0.1 is a bounded, reviewed RayJoin-style reproduction package
- OptiX and Embree are the mature performance backends on the accepted long
  exact-source `county_zipcode` positive-hit `pip` surface
- Vulkan is a real supported backend on that same surface, but slower
- the bounded package remains the main trust anchor for the broader v0.1 slice

Non-claims:

- this is not a full RayJoin paper-identical reproduction package
- this is not a claim that every backend/workload/boundary combination is
  equally mature
- this is not a claim that Vulkan is performance-competitive on the accepted
  long exact-source surface

## Outcome

Goal 93 has frozen the intended release-facing reproduction surface.

The package now includes:

- this closure report
- a machine-readable closure summary
- a short reproduction runbook

The remaining step is external review and consensus before publish.
