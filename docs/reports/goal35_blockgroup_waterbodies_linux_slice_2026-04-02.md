# Goal 35 BlockGroup WaterBodies Linux Slice

Date: 2026-04-02

## Scope

Goal 35 closed the first exact-source Linux execution slice for:

- `BlockGroup ⊲⊳ WaterBodies`

on top of the current local Embree backend.

This round did three things:

1. replaced the old retired-item assumption for `BlockGroup` with the now-verified live Feature Service
2. added bbox-filter ArcGIS acquisition support for bounded exact-source regional slices
3. executed the first Linux exact-source `BlockGroup ⊲⊳ WaterBodies` slices with both `lsi` and `pip`

## Source Update

The important source correction in this round is:

- `BlockGroup` is no longer treated as only a retired layer-package listing
- the live Feature Service item is:
  - [USA Census Block Group Boundaries Feature Service](https://www.arcgis.com/home/item.html?id=2f5e592494d243b0aa5c253e75e792a4)
- service URL:
  - `https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer`

Verified count:

- `BlockGroup`: `239203`
- `WaterBodies`: `463591`

## New Code

- [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py)
  - live BlockGroup Feature Service registry entry
  - bbox/envelope support in ArcGIS query URL generation
- [goal35_stage_blockgroup_waterbodies_bbox.py](/Users/rl2025/rtdl_python_only/scripts/goal35_stage_blockgroup_waterbodies_bbox.py)
- [goal35_convert_and_run_blockgroup_waterbodies.py](/Users/rl2025/rtdl_python_only/scripts/goal35_convert_and_run_blockgroup_waterbodies.py)
- [goal35_blockgroup_waterbodies_test.py](/Users/rl2025/rtdl_python_only/tests/goal35_blockgroup_waterbodies_test.py)

## Host

- host: `192.168.1.20`
- OS: Ubuntu 24.04.4 LTS
- CPU: Intel Core i7-7700HQ
- threads: `8`
- memory: about `15 GiB`

## Regional Slice Policy

This round did not attempt nationwide `BlockGroup ⊲⊳ WaterBodies`.

Instead it used exact-source regional slices selected by a frozen bbox.

Two bbox candidates were executed:

1. `county826_bbox`
   - `-93.4995883569999,42.556702011,-93.02514654,42.9085146050001`
2. `county2300_bbox`
   - `-76.701624,40.495434,-75.757807,40.9497400000001`

These labels reuse known county envelopes from the earlier county/zipcode Linux work only as a deterministic regional selection rule. The inputs in this round are still exact-source BlockGroup and WaterBodies features from their own live ArcGIS services.

## Results

### `county826_bbox`

Service counts in bbox:

- `BlockGroup`: `27`
- `WaterBodies`: `27`

Converted inputs:

- BlockGroup features: `27`
- BlockGroup chains: `29`
- WaterBodies features: `27`
- WaterBodies chains: `27`

Measured results:

- `lsi`
  - CPU rows: `0`
  - Embree rows: `0`
  - pair parity: `true`
  - CPU sec: `0.916624966`
  - Embree sec: `0.024094472`
- `pip`
  - CPU rows: `783`
  - Embree rows: `783`
  - row parity: `true`
  - CPU sec: `0.031841499`
  - Embree sec: `0.007439717`

Interpretation:

- this is a valid exact-source slice
- but `lsi` happened to be empty in this region
- so it is more useful as a bounded smoke/validity slice than as the strongest first family result

### `county2300_bbox`

Service counts in bbox:

- `BlockGroup`: `279`
- `WaterBodies`: `172`

Converted inputs:

- BlockGroup features: `279`
- BlockGroup chains: `287`
- WaterBodies features: `172`
- WaterBodies chains: `248`

Measured results:

- `lsi`
  - CPU rows: `216`
  - Embree rows: `216`
  - pair parity: `true`
  - CPU sec: `139.025500371`
  - Embree sec: `0.221798215`
- `pip`
  - CPU rows: `71176`
  - Embree rows: `71176`
  - row parity: `true`
  - CPU sec: `2.194762260`
  - Embree sec: `0.191530104`

Interpretation:

- this is the stronger accepted first Linux exact-source `BlockGroup ⊲⊳ WaterBodies` slice
- both workloads are nontrivial
- parity holds for both workloads
- the current local Embree backend is materially faster than the Python oracle on this regional slice

## What Goal 35 Closed

Goal 35 closed:

- live-source correction for `BlockGroup`
- bounded exact-source bbox acquisition for `BlockGroup ⊲⊳ WaterBodies`
- first Linux exact-source execution slice for that family
- parity-clean `lsi` and `pip` execution on a nontrivial regional slice

## Boundary

Goal 35 does **not** claim:

- nationwide `BlockGroup ⊲⊳ WaterBodies` reproduction
- full Table 3 / Table 4 closure for the full paper family
- paper-scale execution on Linux for this family

The honest closure statement is:

- RTDL now has the first real Linux exact-source `BlockGroup ⊲⊳ WaterBodies` execution slice on Embree
- the accepted stronger slice is `county2300_bbox`
- this is regional exact-source progress, not full family completion
