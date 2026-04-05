# Goal 102 Report: Full Honest RayJoin Reproduction

Date: 2026-04-05
Status: complete

## Objective

Freeze the fullest honest RTDL reproduction of the RayJoin paper experiment
surface that is currently supportable with:

- RTDL + Embree
- RTDL + OptiX
- PostGIS where it is a valid comparison baseline

This is intentionally not a paper-identical reproduction claim.

## Strict classification rule

This final package uses the stricter external-audit rule:

- `exact` means paper-identical dataset coverage
- `bounded_analogue` means the row is real and accepted, but its dataset or
  reproduction boundary is narrower than the paper's original surface
- `unavailable` means the row was considered and explicitly could not be staged
  honestly
- `not_applicable` is reserved for paper surfaces that do not exist in the
  current RTDL execution model

Under that rule, **no current row qualifies as `exact`**.

## Final matrix

### Table 3 style workload families

| Paper row | Workload | Goal 102 class | Current RTDL evidence |
| --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi` | `bounded_analogue` | bounded-package closure only; no long paper-scale LSI row |
| County ⊲⊳ Zipcode | `pip` | `bounded_analogue` | strongest current row; long exact-source path plus bounded support package |
| Block ⊲⊳ Water | `lsi` | `bounded_analogue` | closest stable analogue is `BlockGroup ⊲⊳ WaterBodies` |
| Block ⊲⊳ Water | `pip` | `bounded_analogue` | same analogue family; bounded support only |
| LKAU ⊲⊳ PKAU | `lsi`, `pip` | `bounded_analogue` | accepted bounded Australia analogue |
| LKAF ⊲⊳ PKAF | `lsi`, `pip` | `unavailable` | unstable acquisition path |
| LKAS ⊲⊳ PKAS | `lsi`, `pip` | `unavailable` | unstaged |
| LKEU ⊲⊳ PKEU | `lsi`, `pip` | `unavailable` | unstaged |
| LKNA ⊲⊳ PKNA | `lsi`, `pip` | `unavailable` | unstaged |
| LKSA ⊲⊳ PKSA | `lsi`, `pip` | `unavailable` | unstaged |

### Figure 13 style scalability

All accepted Figure 13 LSI scalability rows are classified as:

- `bounded_analogue`

Reason:

- deterministic synthetic generator
- accepted structure match
- not the paper's original dataset surface

### Figure 14 style scalability

All accepted Figure 14 PIP scalability rows are classified as:

- `bounded_analogue`

Reason:

- deterministic synthetic generator
- accepted structure match
- not the paper's original dataset surface

### Table 4 / Figure 15 overlay

Overlay is classified as:

- `bounded_analogue`

Reason:

- current RTDL closure is an overlay-seed analogue
- it is not full polygon overlay materialization

The paper's full overlay materialization surface is:

- `not_applicable`

for the current RTDL code path.

## Strongest current flagship row

The strongest current RTDL reproduction row is still:

- `county_zipcode`
- positive-hit `pip`
- long exact-source execution path

That row remains a `bounded_analogue` for Goal 102 because it is not the
paper-identical full dataset package.

Still, it is the best current evidence for RTDL's mature Embree/OptiX story.

Carried-forward accepted exact-source anchors:

Prepared boundary:

- OptiX:
  - `2.5369022019876866 s`
  - PostGIS `3.39459279399307 s`
  - parity `true`
- Embree:
  - `1.7738651990002836 s`
  - PostGIS `3.40269520500442 s`
  - parity `true`

Repeated raw-input boundary:

- OptiX:
  - first `4.49759002099745 s`
  - best repeated `2.124993502991856 s`
  - PostGIS best comparison about `2.986209955997765 s`
  - parity `true`
- Embree:
  - first `1.959970190000604 s`
  - best repeated `1.0921905469949706 s`
  - PostGIS best comparison about `3.1886126509998576 s`
  - parity `true`

## Fresh bounded top4 support reruns

Goal 102 added fresh Linux reruns on the accepted bounded
`top4_tx_ca_ny_pa` package for both backends and both important timing
boundaries.

Bounded package row count:

- `7863`

### Repeated raw-input boundary

OptiX:

- first `1.0346060559968464 s`
- best repeated `0.17935199600469787 s`
- PostGIS about `0.3755` to `0.3769 s`
- parity `true`

Embree:

- first `0.20209797599818558 s`
- best repeated `0.1451086979941465 s`
- PostGIS about `0.3719` to `0.3768 s`
- parity `true`

### Prepared / prepacked boundary

OptiX:

- `0.18207618700398598 s`
- `0.1791208380018361 s`
- PostGIS `0.4167834419931751 s`, `0.3849254340020707 s`
- parity `true`

Embree:

- `0.1821604330034461 s`
- `0.14840258299955167 s`
- PostGIS `0.37199256900930777 s`, `0.36855210599605925 s`
- parity `true`

These fresh support rows do not change the strict classification. They
strengthen the bounded-package evidence.

## Carry-forward evidence used in this package

Primary reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal54_lkau_pkau_four_system_2026-04-03.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal56_overlay_four_system_closure_2026-04-03.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal79_linux_performance_reproduction_matrix_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal84_exact_source_long_backend_summary_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal89_backend_comparison_refresh_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal93_rayjoin_reproduction_release_matrix_2026-04-05.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal99_optix_cold_prepared_run1_win_2026-04-05.md`

Fresh Goal 102 artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_artifacts_2026-04-05/optix_raw_top4/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_artifacts_2026-04-05/embree_raw_top4/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_artifacts_2026-04-05/optix_prepared_top4/summary.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal102_full_honest_rayjoin_reproduction_artifacts_2026-04-05/embree_prepared_top4/summary.json`

## Honest outcome

Goal 102 succeeds as a **full honest reproduction package**, not as a
paper-identical reproduction package.

What is honestly true now:

- the RayJoin-facing experiment surface is frozen explicitly
- no row is silently omitted
- Embree and OptiX are the only primary execution backends in the package
- the strongest current RTDL row is `county_zipcode` positive-hit `pip`
- bounded support rows for `top4_tx_ca_ny_pa`, `BlockGroup ⊲⊳ WaterBodies`,
  bounded `LKAU ⊲⊳ PKAU`, scalability, and overlay-seed are all carried
  forward honestly
- unavailable continent `LK* ⊲⊳ PK*` rows remain explicit non-results

What this report does not claim:

- that RTDL reproduced every RayJoin dataset family paper-identically
- that any current row qualifies as `exact` under the strict dataset-identity
  rule
- that RTDL currently supports full polygon overlay materialization

## Conclusion

Goal 102 closes the RayJoin-facing reproduction story in the strictest honest
way currently supportable.

The result is a reviewed bounded-analogue package with:

- one strong flagship `county_zipcode` row
- fresh bounded top4 support reruns
- carried-forward bounded families and scalability rows
- explicit unavailable rows

That is the strongest defensible RayJoin reproduction package currently
available in this repository.
