# Goal 80: Long End-to-End Runtime-Cache Win

Date: 2026-04-04
Status: complete

## Goal

Establish whether RTDL can beat PostGIS on a long `county_zipcode`
positive-hit `pip` workload under an ordinary raw-input end-to-end call path,
without requiring manual `prepare_*`, `pack_*`, or `bind(...)` calls in user
code.

## Scope

- long `county_zipcode`
- positive-hit `pip`
- ordinary raw-input RTDL call path
- Linux only
- backends:
  - Embree
  - OptiX

## Required Outcome

Goal 80 is accepted if:

- at least one RTDL performance backend beats PostGIS on the long
  `county_zipcode` raw-input timing boundary
- parity remains exact
- the package states the timing boundary precisely

## Outcome

Accepted on the repeated raw-input end-to-end boundary for OptiX.

- package: real `top4_tx_ca_ny_pa` county/zipcode CDB pair on Linux
- backend: OptiX
- first raw-input run: slower than PostGIS
- repeated raw-input reruns: faster than PostGIS
- parity: exact on all reruns

Main report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal80_long_end_to_end_runtime_cache_win_2026-04-04.md`

## Non-Goals

- no Vulkan work
- no oracle performance work
- no manual prepared/prepacked calling convention in the final measured claim
