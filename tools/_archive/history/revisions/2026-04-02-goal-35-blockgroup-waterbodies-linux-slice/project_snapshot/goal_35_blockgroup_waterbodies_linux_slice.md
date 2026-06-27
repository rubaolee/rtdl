# Goal 35 BlockGroup WaterBodies Linux Slice

Date: 2026-04-02

## Goal

Close the first exact-source Linux execution slice for `BlockGroup ⊲⊳ WaterBodies` on the Embree backend.

## Scope

- replace the old retired-item assumption with the now-verified live BlockGroup FeatureServer
- add bbox-filter ArcGIS query support for bounded exact-source regional acquisition
- stage a real BlockGroup/WaterBodies regional slice on `192.168.1.20`
- convert that slice into RTDL CDB/logical inputs
- run `lsi` and `pip` on Linux
- report parity and timing honestly

## Planned Slice

Initial frozen bbox candidate:

- label: `county826_bbox`
- bbox: `-93.4995883569999,42.556702011,-93.02514654,42.9085146050001`

This bbox is reused because it already proved manageable on the Linux host and contains nontrivial counts for both BlockGroup and WaterBodies.

## Acceptance

- live BlockGroup FeatureServer path is registered in the repo
- bbox staging works for both BlockGroup and WaterBodies
- Linux host exact-source slice executes for `lsi` and `pip`
- final report states clearly that this is a regional exact-source slice, not nationwide reproduction
