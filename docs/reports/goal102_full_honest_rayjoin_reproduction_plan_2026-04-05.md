# Goal 102 Plan: Full Honest RayJoin Reproduction

Date: 2026-04-05
Status: in progress

## Core question

What is the fullest RayJoin paper experiment surface that RTDL can reproduce
honestly today, if we:

- keep only Embree and OptiX as the main execution backends
- ignore unavailable datasets rather than blocking on them
- separate exact rows from bounded analogues

## Planned structure

### Phase 1: Freeze the matrix

Build one explicit matrix covering:

- Table 3 style rows
- Figure 13 rows
- Figure 14 rows
- Table 4 / Figure 15 rows

Each row gets one of:

- `exact`
- `bounded_analogue`
- `unavailable`
- `not_applicable`

### Phase 2: Gather accepted evidence

Carry forward already accepted evidence where valid:

- bounded package closure
- long exact-source `county_zipcode` positive-hit `pip`
- accepted scalability analogues
- accepted overlay-seed analogue rows

### Phase 3: Fill missing runnable rows

Run the remaining rows that are:

- available
- not already closed by accepted artifacts
- relevant to Embree/OptiX-only reproduction

### Phase 4: Final package

Produce:

- one final reproduction matrix report
- one machine-readable summary
- one source-evidence list
- one explicit unavailable-row list

## Immediate working assumptions

- `County ⊲⊳ Zipcode` remains the strongest exact-source family
- `BlockGroup ⊲⊳ WaterBodies` remains the closest stable public analogue for
  `Block ⊲⊳ Water`
- continent-scale `LK* ⊲⊳ PK*` families remain likely unavailable unless a
  stable local acquisition path already exists
- overlay remains an `overlay-seed analogue`, not full polygon output

## External audit support

The planning pass should use external AI review for:

- exact vs bounded row classification
- missing/unavailable row identification

## Non-claim boundary

Goal 102 must not claim:

- full paper-identical dataset reproduction
- exact availability of every RayJoin family
- Vulkan as a primary reproduction backend
