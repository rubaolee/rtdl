# Goal4363: Robot Collision Same-Contract Prepared-Buffer Pair

Date: 2026-06-13

Status: internal same-contract backend row; not public speedup authorization.

| Contract | Groups | Embree total median sec | OptiX total median sec | Embree / OptiX total | Embree / OptiX traversal | Validation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| prepared grouped-segment any-hit compact flags | 4096 | 0.002454289 | 0.001538487 | 1.60x | 9.22x | probe signature match=True |

Boundary: native RTDL prepared-buffer compact flag decision only. This does not claim continuous collision, planner acceleration, paper reproduction, release readiness, or public speedup wording.
