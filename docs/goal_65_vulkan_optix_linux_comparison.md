# Goal 65 Vulkan OptiX Linux Comparison

## Objective

Run the Vulkan backend on the validated Linux GPU host and compare it directly
against OptiX on the same accepted workload packages.

## Scope

Use only already accepted, already staged Linux packages:

- bounded `County ⊲⊳ Zipcode` `1x4,1x5,1x6,1x8,1x10,1x12` ladder derived from `top4_tx_ca_ny_pa`
- bounded `BlockGroup ⊲⊳ WaterBodies` `county2300_s04,county2300_s05`
- bounded `LKAU ⊲⊳ PKAU` `sunshine_tiny` overlay-seed analogue

For each accepted package:

- run the native C oracle as correctness reference
- run Embree for context
- run OptiX
- run Vulkan

## Required outputs

- exact-row parity vs the native C oracle
- explicit prepare vs warm-run timing for:
  - OptiX
  - Vulkan
- one cold run is executed before the recorded warm run so the comparison does
  not confuse first-use backend initialization with steady-state runtime
- one bounded Linux comparison report

## Boundary

- this is a backend comparison goal, not a new PostGIS closure goal
- it uses accepted staged inputs instead of new public-data acquisition
- the whole `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa` `lsi` package is outside the
  current Vulkan `uint32` output-capacity contract, so the accepted County/Zipcode
  comparison surface here is the bounded `1xN` ladder
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s06` and larger currently exceed the
  Vulkan `lsi` 512 MiB output guardrail on this host, so the accepted block/water
  comparison surface here is the largest feasible bounded ladder:
  `county2300_s04, county2300_s05`
- claims remain bounded to the tested Linux host and accepted workload packages
