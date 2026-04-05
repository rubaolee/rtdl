# Goal 98 Plan: OptiX Release Regression Repair

Date: 2026-04-05
Status: planned

## Trigger

Goal 94 release validation found a clean-clone OptiX regression on the accepted
long exact-source prepared `county_zipcode` positive-hit `pip` surface.

Clean-clone failure artifact:

- `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_prepared/summary.json`

Key failing values:

- PostGIS row count:
  - `39073`
- OptiX row count:
  - `38799`
- parity:
  - `false`
- OptiX backend times:
  - `7.817694120996748 s`
  - `5.145167353999568 s`

## Execution order

1. write diagnosis report
2. obtain 3-way review on diagnosis/proposal
3. repair code
4. run focused validation locally
5. run clean Linux rerun on the same exact-source surface
6. obtain 3-way review on:
- code package
- rerun result package
7. only then resume v0.1 closure

## Initial likely focus areas

- OptiX positive-hit prepared path
- packed/prepared input reuse vs exact-source fresh pack path
- candidate generation / materialization correctness
- exact finalize path on the fresh clean-clone route
- any dependency on local build/runtime state that differs from clean clone

## Hard rule

Do not patch around the failure by weakening the accepted OptiX claim unless the
repair attempt fails and the downgrade is explicitly documented as the final
result.
