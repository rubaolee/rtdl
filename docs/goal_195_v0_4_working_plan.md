# Goal 195: v0.4 Working Plan

Date: 2026-04-09
Status: planned

## Goal

Turn the settled `v0.4` nearest-neighbor direction into an executable plan with:

- a concrete goal ladder
- an open-dataset ladder
- an honest baseline strategy
- an explicit PostGIS support role

## Why this goal exists

The strategic direction is already settled:

- `v0.4` is a nearest-neighbor workload release
- first headline workload is `fixed_radius_neighbors`
- second workload is `knn_rows`

What is still needed before implementation starts is a practical build order.
That order must answer:

- how many goals there are
- which datasets are suitable
- which external baselines are credible
- how PostGIS helps without becoming the main comparison story

## Required result

This goal is complete when the repo contains:

- a reviewed `v0.4` working-plan report
- a concrete implementation order
- a public dataset ladder with source links and intended use
- a baseline section that names:
  - brute-force Python reference
  - `scipy.spatial.cKDTree`
  - bounded PostGIS support
- a `2+` AI consensus closure note

## Non-goals

This goal does not implement the workloads themselves.

It only fixes the execution plan for the upcoming `v0.4` build line.
