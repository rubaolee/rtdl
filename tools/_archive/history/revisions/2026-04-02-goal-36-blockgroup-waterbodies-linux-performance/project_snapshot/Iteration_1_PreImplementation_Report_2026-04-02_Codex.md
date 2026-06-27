# Goal 36 Pre-Implementation Report

Date: 2026-04-02

Planned implementation:

- add a Linux-host harness for exact-source `BlockGroup ⊲⊳ WaterBodies` bbox ladders
- derive points by scaling the accepted `county2300_bbox` seed around its center
- run a single measured pass per point because the Python `lsi` oracle is already minutes-long at the top scale
- accept only parity-clean points

Why this is the next biggest step:

- Goal 35 proved the first nontrivial slice exists
- the next missing evidence is whether this family remains parity-clean and performant across a bounded increasing exact-source ladder
