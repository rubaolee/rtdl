# Goal 84: Exact-Source Long Backend Summary

## Objective

Summarize the accepted long exact-source `county_zipcode` positive-hit `pip`
results after the OptiX and Embree repair/optimization goals.

This report does not introduce new measurements. It consolidates the already
accepted exact-source Linux artifacts into a single backend-status summary.

## Scope

- workload: long exact-source `county_zipcode`
- query shape: positive-hit `pip`
- compared systems:
  - PostGIS
  - RTDL + OptiX
  - RTDL + Embree
- accepted boundaries:
  - prepared exact-source
  - repeated raw-input exact-source

## Source packages

OptiX package:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_2026-04-04.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal82_optix_pre_embree_audit_2026-04-04.md`

Embree package:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal83_embree_long_exact_source_repair_2026-04-04.md`

## Consolidated results

### Prepared exact-source boundary

OptiX:

- backend: `1.147425041 s`
- PostGIS: `3.142702609 s`
- parity: `true`

Embree:

- backend: `1.773865199 s`
- PostGIS: `3.402695205 s`
- parity: `true`

### Repeated raw-input exact-source boundary

OptiX:

- first run: `3.573603315 s`
- repeated run: `1.090809764 s`
- PostGIS:
  - `3.235889516 s`
  - `3.224879186 s`
- parity: `true`

Embree:

- first run: `1.959970190 s`
- repeated run: `1.092190547 s`
- PostGIS:
  - `3.583030458 s`
  - `3.188612651 s`
- parity: `true`

## Interpretation

Current exact-source long-workload picture:

1. Both mature RTDL backends now have accepted exact-source long-workload wins
   against PostGIS on at least one honest boundary.
2. OptiX and Embree are both parity-clean on the long exact-source
   `county_zipcode` positive-hit `pip` surface.
3. OptiX and Embree are now very close to each other on the warmed repeated
   raw-input boundary:
   - OptiX repeated: `1.090809764 s`
   - Embree repeated: `1.092190547 s`
4. Embree currently has the stronger cold repeated raw-input first-run number on
   this surface:
   - Embree first: `1.959970190 s`
   - OptiX first: `3.573603315 s`

## Honest claim surface

Safe claims:

- RTDL + OptiX beats PostGIS on the accepted long exact-source `county_zipcode`
  positive-hit `pip` surface for repeated raw-input calls, with exact parity.
- RTDL + Embree also beats PostGIS on that same accepted surface, with exact
  parity.
- Both backends also beat PostGIS on the accepted prepared exact-source
  boundary.

Non-claims:

- this is not a blanket claim for all RTDL workloads
- this is not a Vulkan claim
- this is not a full end-to-end cold first-call win claim for every backend

## Conclusion

The RTDL backend story is now materially stronger than it was before Goals 80-83.

For the accepted long exact-source RayJoin-style `county_zipcode` positive-hit
`pip` surface:

- OptiX is parity-clean and fast
- Embree is parity-clean and fast
- PostGIS remains the comparison baseline, but no longer the unquestioned winner
  on the accepted exact-source long-workload boundaries
