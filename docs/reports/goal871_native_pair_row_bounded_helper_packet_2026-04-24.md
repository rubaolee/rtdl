# Goal871 Native Pair-Row Bounded Helper Packet

- helper: `run_seg_poly_anyhit_rows_optix_native_bounded`
- recommended status: `bounded_helper_added`

## Evidence

- helper present: `True`
- API delegates to helper: `True`
- empty-input success path present: `True`
- outputs zeroed before work: `True`
- not-implemented boundary present: `True`
- public rows path still host-indexed: `True`

## Current Behavior

- empty input: `success_zero_rows`
- non-empty input: `explicit_not_implemented_until_native_emitter_exists`
- public rows path: `unchanged_host_indexed`

## Boundary

This goal moves the bounded rows contract into a named workload-layer helper and gives empty inputs correct zero-row behavior. It still does not implement native OptiX pair-row emission or authorize readiness.

