# Goal 54 LKAU PKAU Four-System Closure

## Objective

Upgrade the existing bounded `LKAU ⊲⊳ PKAU` Australia slice from an Embree-only
validation into the same accepted four-system comparison standard used by Goal
50:

- PostGIS
- native C oracle
- Embree
- OptiX

## Why This Goal

The current project has already closed bounded four-system comparisons for:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

The largest remaining paper-family hole with existing acquisition/conversion
infrastructure is the Lakes/Parks family. The Australia slice is already
available as:

- bounded
- derived-input
- Linux-host executable
- parity-checked between the oracle and Embree

That makes it the highest-value next family to upgrade before taking on a fresh
continent-scale acquisition risk.

## Scope

Accepted in scope:

- reuse the Goal 37 Australia Overpass slice boundary
- convert the staged lakes/parks JSON into RTDL CDB inputs
- compare `lsi` and `pip` across:
  - PostGIS
  - native C oracle
  - Embree
  - OptiX
- record parity and timing on `192.168.1.20`
- write a report that clearly labels this as:
  - bounded
  - derived-input
  - Australia only

Out of scope:

- continent-scale `LKAU ⊲⊳ PKAU`
- multipolygon relation reconstruction
- the other lakes/parks continent families
- Table 4 / Figure 15 overlay closure

## Execution Plan

1. Add a dedicated Goal 54 harness that mirrors the Goal 50 four-system
   comparison structure for Overpass-derived lakes/parks inputs.
2. Add a small regression test for argument parsing and report wording.
3. Run the harness on `192.168.1.20` against the frozen Goal 37 Australia slice.
4. Write the result report.
5. Send the finished result to Gemini and Claude for review.
6. Publish only after at least 2-AI consensus.

## Acceptance

Goal 54 is accepted only if:

1. the harness runs on the Linux host without ad hoc manual query edits
2. PostGIS uses indexed SQL
3. `lsi` parity is clean across all four systems
4. `pip` parity is clean across all four systems
5. the final report states the bounded derived-input boundary explicitly
6. at least 2 AIs approve the result before publication
