# Goal 59: Bounded v0.1 Reproduction Package

## Purpose

Produce the first final bounded v0.1 reproduction package from the workload
families and systems that are already accepted, instead of continuing to spend
time on unstable external data-acquisition paths.

## Why this goal now

The accepted bounded matrix is already strong:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
- bounded `LKAU ⊲⊳ PKAU`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed analogue`

Across:

- PostGIS
- native C oracle
- Embree
- OptiX

Meanwhile, the next paper-labeled lakes/parks continent families are currently
blocked by unstable public acquisition paths. That makes a bounded final package
more valuable than continuing to chase fragile new sources.

## Scope

- consolidate the accepted bounded workload/system matrix
- produce one clear v0.1 package/report stating:
  - what is closed
  - what is bounded
  - what remains deferred
  - what is still provisional
- include performance and correctness boundaries honestly
- keep deferred continent-family acquisition gaps explicit

## Exclusions

- no claim of full paper-identical reproduction
- no claim that deferred lakes/parks continent families are closed
- no Vulkan promotion beyond provisional status

## Acceptance

Goal 59 is complete only if:

1. the accepted bounded package is fully summarized in one coherent report
2. deferred and blocked families are explicitly listed
3. the package is reviewed by at least two AIs before publish
