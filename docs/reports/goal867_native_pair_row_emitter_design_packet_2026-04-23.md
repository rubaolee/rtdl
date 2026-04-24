# Goal867 Native Pair-Row Emitter Design Packet

- app: `segment_polygon_anyhit_rows`
- mode: `rows`
- recommended status: `needs_native_pair_row_emitter_implementation`
- blocker: `native_pair_row_emitter_missing`

## Current Truth

- ABI surface: `present`
- runtime execution: `host_indexed_exact_cpu_loop`
- device codegen: `placeholder_only`

## Evidence

- api symbol present: `True`
- api calls host-indexed helper: `True`
- host-indexed helper present: `True`
- native pair-row impl present: `False`
- generated raygen placeholder present: `True`
- generated closesthit stub present: `True`

## Required Work

- Add a true native OptiX pair-row emitter instead of calling the host-indexed helper from the public C ABI.
- Define bounded native output memory semantics for pair-row emission, including count discovery and overflow policy.
- Replace the generated segment_polygon_anyhit_rows OptiX device placeholder with an implementation-backed contract.
- Add a strict correctness/performance gate with CPU reference digest and real OptiX artifact evidence before promotion.

## Boundary

Do not promote segment_polygon_anyhit_rows rows mode into any RT-core-ready or active RTX claim set until the public OptiX row path stops using the host-indexed helper and the generated device path is no longer placeholder-only.

