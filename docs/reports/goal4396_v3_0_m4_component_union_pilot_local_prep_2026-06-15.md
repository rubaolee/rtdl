# Goal4396 V3.0 M4 Component-Union Pilot Local Preparation

Date: 2026-06-15

Status: local M4 graph-reuse preparation complete. Full M4 measurement remains blocked on pod hardware evidence.

## Decision

M4 requires the RTDBSCAN-style fused-continuation pilot to prove cross-app reuse by at least one non-DBSCAN workload. Locally, this checkpoint builds two no-execution V3 graphs that reuse the exact same generic continuation operation:

`continuation.component_union`

The two graphs are:

| Graph | Route | Purpose |
| --- | --- | --- |
| `fixed_radius_component_pilot` | fixed-radius candidate primitive -> component union | Represents fixed-radius component continuation without using app-specific API names. |
| `generic_edge_component_pilot` | generic edge row stream -> component union | Proves the same continuation can be reused by a non-fixed-radius workload. |

## Implemented Files

- `src/rtdsl/v3_0_m4_pilots.py`
- `tests/goal4396_v3_0_m4_component_union_pilot_test.py`
- Updated public exports in `src/rtdsl/__init__.py`

## Local Validation

The tests validate:

- exactly two pilot graphs are produced;
- both graphs are valid no-execution `PreparedGraph` objects;
- both graphs use the same `continuation.component_union` operation;
- neither graph uses PartnerNode or automatic partner selection;
- both graphs use the same `component_edge_contract_v1` logical output contract;
- public speedup claims remain unauthorized;
- pod evidence is still required.

## Test Results

Focused V3 M1-M4 stack:

```text
32 tests OK
```

## Boundary

This is not full M4 completion. It does not include:

- OptiX/RT-core measurements;
- Embree measurements;
- same-contract hardware phase tables;
- M3 evidence records from CUDA events or Nsight;
- public performance claims.

## Pod Requirement For Full M4

Full M4 completion requires:

- running both pilot graphs or their lowered equivalent on hardware with an OptiX-capable GPU;
- collecting M3-grade phase timings for OptiX and Embree;
- collecting evidence records for stream ordering, residency, transfer/materialization, and backend phase timing;
- showing that the same generic continuation operation is reused without app-specific native or public Python names;
- keeping all public claim flags false until M7.

## Conclusion

M4 local preparation is complete. The next missing piece is pod hardware evidence.
