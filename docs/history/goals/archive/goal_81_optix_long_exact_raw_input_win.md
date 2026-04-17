# Goal 81: OptiX Long Exact Raw-Input Win

Date: 2026-04-04
Status: complete

## Goal

Establish whether RTDL OptiX can beat PostGIS on the accepted long
`county_zipcode` positive-hit `pip` workload under ordinary raw-input calls,
without requiring user-visible manual prepared/prepacked execution steps.

## Scope

- Linux only
- backend:
  - OptiX
- workload:
  - `county_zipcode`
- source surface:
  - exact long county/zipcode feature-layer inputs
- timing boundary:
  - repeated raw-input end-to-end calls in one process

## Outcome

Accepted on the repeated raw-input end-to-end boundary.

- first raw-input call remained slower than PostGIS
- repeated raw-input OptiX reruns beat PostGIS on the accepted long exact
  source surface
- parity remained exact on every rerun

Main report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal81_optix_long_exact_raw_input_win_2026-04-04.md`
