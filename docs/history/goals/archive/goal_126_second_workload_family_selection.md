# Goal 126: Second v0.2 Workload Family Selection

Date: 2026-04-06
Status: accepted

## Goal

Choose the second major workload-family target for RTDL v0.2 after
`segment_polygon_hitcount`.

This goal exists because v0.2 should not stop at one strong new feature line.
The next family should broaden RTDL meaningfully without dissolving scope
discipline.

## Required outcomes

1. evaluate the strongest candidate workload families against the v0.2 charter
2. reject families that are too close to the existing hitcount family or too
   broad to close honestly
3. name one recommended next workload family
4. define the acceptance boundary for the implementation goal that follows

## Chosen recommendation

The recommended second v0.2 workload family is:

- `segment_polygon_anyhit_rows`

Meaning:

- input:
  - segments
  - polygons
- output:
  - one boolean join-style row per true segment/polygon hit

## Why this family

It is the best next step because it is:

- clearly broader than `segment_polygon_hitcount`
- still close enough to reuse the now-strong candidate-generation and exact
  refine machinery
- directly useful for real screening, auditing, and downstream aggregation
  pipelines
- easier to close honestly than jumping immediately to broad `lsi`
  or nearest-neighbor families

## What it is not

This goal does **not** pick:

- broad `lsi` reopening
- full nearest-neighbor
- full overlay materialization
- arbitrary graph/counting novelty workloads

Those remain possible future directions, but they are not the best immediate
second workload-family target.

## Final status

Goal 126 closes as:

- second workload-family target chosen
- next implementation target defined
- v0.2 scope discipline preserved
