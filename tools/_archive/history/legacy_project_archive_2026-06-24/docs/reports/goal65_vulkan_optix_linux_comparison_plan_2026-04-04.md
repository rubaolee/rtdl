# Goal 65 Vulkan OptiX Linux Comparison Plan

Date: 2026-04-04

## Plan

1. Reuse the accepted Linux packages already staged in earlier goals.
2. Build a single comparison harness covering:
   - bounded `County ⊲⊳ Zipcode` `1x4,1x5,1x6,1x8,1x10,1x12` ladder derived from `top4_tx_ca_ny_pa`
   - bounded `BlockGroup ⊲⊳ WaterBodies` `county2300_s04, county2300_s05`
   - bounded `LKAU ⊲⊳ PKAU` overlay-seed analogue
3. Compare:
   - native C oracle
   - Embree
   - OptiX
   - Vulkan
4. Record:
   - exact-row parity vs the native C oracle
   - warm runtime for all backends
   - prepare/cold/warm split for OptiX and Vulkan
5. Run the harness on `192.168.1.20`.
6. Write the final report and seek review consensus before publishing.

## Why this shape

- the host already has validated OptiX and Vulkan capability
- the accepted workload packages already exist on the Linux machine
- the whole `County ⊲⊳ Zipcode` `top4` `lsi` package currently exceeds Vulkan's
  `uint32` output-capacity contract, so the fair accepted County/Zipcode
  comparison surface is the already validated bounded `1xN` ladder
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s06` and above exceed Vulkan's
  current 512 MiB `lsi` guardrail, so the fair accepted block/water surface is
  the largest feasible bounded ladder on this host: `county2300_s04, county2300_s05`
- this avoids new public-data instability and keeps the comparison apples-to-apples
