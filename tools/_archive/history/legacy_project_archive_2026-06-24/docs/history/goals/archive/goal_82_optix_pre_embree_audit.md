# Goal 82: OptiX Pre-Embree Audit

Date: 2026-04-04
Status: in progress

## Goal

Before starting Embree follow-up work, perform a focused review-and-test audit
of the published OptiX long-workload performance path.

## Scope

- validate the published Goal 80 and Goal 81 OptiX claims
- use focused local tests
- use focused Linux tests on a clean clone at the published head
- rerun the two accepted long OptiX performance boundaries on Linux:
  - execution-ready / prepared
  - repeated raw-input end-to-end
- keep the scope on OptiX only

## Acceptance

Goal 82 is accepted if:

- the focused local and Linux validation slices pass
- the accepted OptiX long-workload claims remain reproducible on Linux
- the audit package is reviewed before publish
