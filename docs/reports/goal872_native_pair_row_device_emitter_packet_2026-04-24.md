# Goal872 Native Pair-Row Device Emitter Packet

- app: `segment_polygon_anyhit_rows`
- mode: `native_bounded_rows`
- recommended status: `device_emitter_implemented_pending_real_optix_gate`

## Evidence

- kernel present: `True`
- any-hit atomic append present: `True`
- overflow flag present: `True`
- pair payload present: `True`
- pipeline present: `True`
- launch present: `True`
- bounded copy present: `True`
- public rows path still host-indexed: `True`

## Current Behavior

- native bounded symbol: `attempts_device_emission`
- overflow semantics: `emitted_count_reports_total_hits; rows_out_receives_prefix_up_to_output_capacity; overflowed_out marks truncation`
- public rows path: `unchanged_host_indexed_until_gate`

## Remaining Gate

A Linux/RTX build must compile and run the new native bounded symbol, compare row digests against CPU reference, and then decide whether to promote the public rows path or keep it separate.

## Boundary

This goal implements the first native bounded device-emission path, but it does not promote the public rows app path. No RT-core readiness claim is authorized until a real OptiX artifact passes the strict gate.

