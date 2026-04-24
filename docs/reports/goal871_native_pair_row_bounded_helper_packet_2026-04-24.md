# Goal871 Native Pair-Row Bounded Helper Packet

- helper: `run_seg_poly_anyhit_rows_optix_native_bounded`
- recommended status: `bounded_helper_added`

## Evidence

- helper present: `True`
- API delegates to helper: `True`
- empty-input success path present: `True`
- outputs zeroed before work: `True`
- device kernel present: `True`
- device launch present: `True`
- bounded output copy present: `True`
- public rows path still host-indexed: `True`

## Current Behavior

- empty input: `success_zero_rows`
- non-empty input: `bounded_native_emission_attempt`
- public rows path: `unchanged_host_indexed`

## Boundary

This goal records the bounded rows helper and device-emission path. It still does not authorize readiness because the public rows path remains host-indexed until a real OptiX gate passes.

