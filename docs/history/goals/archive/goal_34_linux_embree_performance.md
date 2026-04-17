# Goal 34 Linux Embree Performance Characterization

Date: 2026-04-02

## Goal

Use `192.168.1.20` as the serious Embree performance host for the current exact-source `County ⊲⊳ Zipcode` family and measure the current Linux Embree backend on parity-clean exact-source slices.

## Scope

- reuse the staged full `USCounty` and `Zipcode` ArcGIS source pages on `192.168.1.20`
- build a reproducible size ladder using co-located exact-source slices selected by overlap count
- run both `lsi` and `pip` on each accepted slice
- measure `rt.run_cpu(...)` and `rt.run_embree(...)` on Linux
- keep parity checking in the loop; any non-parity-clean slice is reported but not accepted as a performance point
- produce a Linux-host performance report

## Planned Ladder

Initial target ladder:

- `1x4`
- `1x5`
- `1x6`
- `1x8`

Stretch target if parity and runtime remain acceptable:

- `1x10`
- `1x12`

## Acceptance

- a reproducible Linux-host performance harness exists in the repo
- the harness records parity and timing for `lsi` and `pip`
- the final report clearly separates accepted parity-clean points from attempted but rejected points
- Gemini reviews the plan and implementation/report
- Claude performs the final review if available
