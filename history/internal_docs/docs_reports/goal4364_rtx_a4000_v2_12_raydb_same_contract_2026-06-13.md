# Goal4364: RayDB-Style Same-Contract Prepared Grouped Reduction Pair

Date: 2026-06-13

Status: internal same-contract backend row; not public speedup authorization.

| Contract | Rows | Groups | Embree median sec | OptiX median sec | Embree / OptiX | Traversal ratio | Correctness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| prepared grouped i64 count reduction | 262144 | 1024 | 0.021954956 | 0.000991316 | 22.15x | 69.74x | cpu_reference_match_both=True |

Boundary: native RTDL prepared grouped count reduction only. This does not claim RayDB authors-code parity, SQL engine acceleration, typed hit-stream handoff speedup, release readiness, or public speedup wording.
