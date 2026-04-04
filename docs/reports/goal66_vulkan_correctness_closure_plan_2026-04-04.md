# Goal 66 Plan

Date: 2026-04-04

## Problem

Goal 65 showed that Vulkan was runnable on `192.168.1.20` but not parity-clean
on the accepted bounded comparison surface. The failures were concentrated in:

- County/Zipcode `lsi`
- County/Zipcode `pip`
- BlockGroup/WaterBodies `pip`
- bounded `LKAU ⊲⊳ PKAU` `overlay-seed`

## Planned repair

1. Mirror the accepted OptiX/oracle strategy in Vulkan:
   - exact host-side `pip` overwrite
   - host-side `overlay.requires_pip` supplement
2. If bounded `lsi` failures remain, move Vulkan `lsi` final truth to an exact
   host-side refine path rather than trusting raw GPU hit records.
3. Rebuild Vulkan on `192.168.1.20`.
4. Rerun:
   - `tests.rtdsl_vulkan_test`
   - `scripts/goal51_vulkan_validation.py`
   - full Goal 65 bounded comparison surface
5. Close only if the rerun is parity-clean.

## Expected boundary after repair

Even if Goal 66 succeeds, Vulkan may still remain bounded by:

- the current `uint32` `lsi` output-capacity contract
- the `512 MiB` output guardrail on larger `lsi` cases

So Goal 66 is a correctness-closure goal, not a claim of full Vulkan maturity.
