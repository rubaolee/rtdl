# Goal869 Native Pair-Row Emitter Implementation Packet

- app: `segment_polygon_anyhit_rows`
- mode: `rows`
- current blocker: `variable_length_native_pair_output_missing`
- recommended status: `implementation_packet_ready`

## Current Truth

- native hitcount foundation: `present`
- rows output shape: `variable_length_pair_rows`
- existing native output shape: `fixed_one_row_per_segment`
- public rows execution: `host_indexed`

## Source Evidence

- native hitcount pipeline present: `True`
- fixed-size hitcount output present: `True`
- public rows ABI present: `True`
- rows ABI calls host-indexed: `True`
- native rows impl present: `False`

## Implementation Plan

- Reuse the existing native segment-polygon custom-AABB traversal foundation rather than creating a second unrelated geometry encoding.
- Add a bounded native pair-row emission contract for variable-length output instead of the current fixed one-row-per-segment output buffer.
- Choose and document an overflow-safe strategy before promotion: either a two-pass count-then-emit contract or an explicit bounded-capacity plus overflow-status contract.
- Only after the native rows ABI exists should the public rows path stop calling the host-indexed helper and move into a strict correctness/performance gate.

## Acceptance Conditions

- A public OptiX rows ABI exists that no longer dispatches to the host-indexed helper.
- The native rows implementation is backed by the custom-AABB traversal foundation, not a disguised CPU loop.
- A local gate proves exact row-digest parity against the CPU reference.
- A real OptiX artifact exists before any RT-core readiness or RTX claim review.

## Boundary

This packet is implementation-facing only. It does not authorize promotion of rows mode. Its purpose is to turn the current blocker into a concrete engineering plan tied to the existing native hit-count foundation.

