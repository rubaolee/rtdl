# Goal 36 BlockGroup WaterBodies Linux Performance

Date: 2026-04-02

## Goal

Close the first serious Linux-host Embree performance characterization round for the exact-source `BlockGroup ⊲⊳ WaterBodies` family.

## Scope

- keep the Goal 35 live-source input path
- move from a one-off slice to a deterministic exact-source ladder
- use a frozen seed bbox and scale factors so the round is reproducible
- benchmark both `lsi` and `pip`
- accept only parity-clean points

## Frozen Ladder

- seed bbox label: `county2300_bbox`
- scale factors: `0.4,0.5,0.6,0.75,1.0`

## Review Rule

- Gemini reviews the plan and the finished implementation/report
- Claude performs the final review after the measured Linux results are frozen
