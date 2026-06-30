# Goal 36 BlockGroup WaterBodies Linux Performance

Date: 2026-04-02

## Goal

Close the first serious Linux-host Embree performance characterization round for:

- `BlockGroup ⊲⊳ WaterBodies`

using exact-source regional slices instead of a single one-off bbox.

## Scope

- keep the same exact-source live ArcGIS input families established in Goal 35
- derive a deterministic ladder from the accepted nontrivial `county2300_bbox` seed region
- stage and run multiple exact-source bbox slices on `192.168.1.20`
- report parity and timing for both `lsi` and `pip`
- keep the run bounded by using a single measured pass per point because the Python `lsi` oracle is already expensive on this family

## Frozen Ladder

Seed bbox:

- `county2300_bbox`
- `-76.701624,40.495434,-75.757807,40.9497400000001`

Frozen scale factors:

- `0.4`
- `0.5`
- `0.6`
- `0.75`
- `1.0`

Each point is the exact-source bbox obtained by scaling the seed bbox around its center.

## Acceptance

- reproducible Linux-host harness in the repo
- accepted points are parity-clean for both `lsi` and `pip`
- final report clearly states this is a regional exact-source ladder, not nationwide/full-family completion
- Gemini reviews the plan and final report
- Claude performs the final review after implementation and measured results are done
