# Goal 37 LKAU PKAU Linux Slice

Date: 2026-04-02

## Goal

Close the first real Lakes/Parks family slice on the Linux Embree host by running a bounded:

- `LKAU ⊲⊳ PKAU`

derived-input regional workload on:

- `192.168.1.20`

## Scope

- keep the work Embree-only
- use a live public OSM source because the historical SpatialHadoop direct download links remain unavailable
- freeze one deterministic Australia bbox for the first bounded family slice
- fetch both lakes and parks as OSM ways with full geometry
- convert those bounded OSM ways into RTDL CDB inputs
- run `lsi` and `pip` on Linux and report parity/timing

## Frozen Source Contract

Source endpoint:

- `https://overpass.kumi.systems/api/interpreter`

Frozen bbox label:

- `sunshine_tiny`

Frozen bbox:

- `-26.72,152.95,-26.55,153.10`

Frozen OSM filters:

- parks:
  - `way["leisure"="park"]`
  - `way["boundary"="national_park"]`
- lakes:
  - `way["natural"="water"]`

## Acceptance

- reproducible staging script in the repo
- reusable OSM-way to CDB conversion helper in the repo
- Linux-host execution report for the frozen bounded Australia slice
- report clearly labels this as:
  - derived-input
  - bounded regional
  - not continent-scale completion
- Gemini reviews the plan and final report
- Claude performs the final review after implementation and measured results are done
