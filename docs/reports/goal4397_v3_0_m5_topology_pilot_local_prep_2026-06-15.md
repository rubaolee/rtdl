# Goal4397 V3.0 M5 Topology Pilot Local Preparation

Date: 2026-06-15

Status: local M5 topology graph preparation complete. Full M5 comparison remains blocked on pod hardware evidence and author-code timing evidence.

## Decision

M5 prepares the generic topology route required for point-location and topology-output benchmark comparisons without adding app-specific public API or native symbols.

The local checkpoint builds two no-execution V3 graphs:

| Graph | Primitive route | Continuation route |
| --- | --- | --- |
| `point_location_topology_pilot` | `primitive.closed_shape_boundary_event_2d` | `continuation.compact_mask` |
| `edge_intersection_topology_pilot` | `primitive.segment_intersect_2d` | `continuation.compact_mask` |

Both graphs share:

- topology contract: `topology_face_contract_v1`;
- topology stream output: `topology_face_ids`;
- status mask output: `topology_event_mask`;
- selected summary output: `selected_face_ids`;
- fail-closed overflow policy;
- OptiX and Embree target backends.

## Implemented Files

- `src/rtdsl/v3_0_m5_topology_pilots.py`
- `tests/goal4397_v3_0_m5_topology_pilot_test.py`
- Updated public exports in `src/rtdsl/__init__.py`

## Local Validation

The tests validate:

- exactly two topology pilot graphs are produced;
- both graphs are no-execution `PreparedGraph` objects;
- neither graph uses PartnerNode or automatic partner selection;
- both graphs share `topology_face_contract_v1`;
- both graphs use `continuation.compact_mask`;
- outputs are generic topology streams, status masks, and summaries;
- public claim flags remain false;
- author-code timing and pod evidence are still required.

## Test Results

Focused V3 M1-M5 stack:

```text
36 tests OK
```

## Boundary

This checkpoint does not claim:

- author-code reproduction;
- OptiX-vs-Embree performance;
- device-resident topology output;
- same-stream partner continuation;
- whole-application speedup;
- public V3.0 speedup.

## Full M5 Requirements

Full M5 completion requires:

- author code version and timing basis;
- exact dataset and scale;
- RTDL OptiX and RTDL Embree rows under the same topology contract;
- M3-grade phase accounting;
- hardware evidence for device residency or stream claims;
- separated build, upload, traversal, stream handoff, continuation, materialization/download, validation, and host-wrapper timings;
- fresh review before any public wording.

## Conclusion

M5 local graph preparation is complete. Hardware and author-code evidence are still required for full M5.
