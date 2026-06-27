# Goal 69 Plan: PIP Performance Repair

Date: 2026-04-04

Accepted diagnosis:
- PostGIS is fast on `pip` because it answers an indexed positive-hit query.
- RTDL currently pays for full-matrix row generation and exact finalization.
- A meaningful first repair is to support positive-hit `pip` directly instead of always materializing the full matrix.

Design choice:
- keep `point_in_polygon(..., result_mode="full_matrix")` as the default
- add `result_mode="positive_hits"` for workloads that only need hit rows

Why this is safe:
- existing kernels and reports keep their semantics
- performance-oriented workloads can opt into the sparse result mode explicitly
- the code path can be tested independently without weakening the accepted bounded package

Initial validation target:
- authored small PIP cases locally
- then the accepted bounded `County ⊲⊳ Zipcode` and `BlockGroup ⊲⊳ WaterBodies` positive-hit workloads on `192.168.1.20`
