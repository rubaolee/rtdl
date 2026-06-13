# Goal4362: Barnes-Hut Same-Contract Node-Coverage Pair

Date: 2026-06-13

Status: internal same-contract backend row; not public speedup authorization.

| Contract | Bodies | Embree query median sec | OptiX query median sec | Embree / OptiX | Correctness |
| --- | ---: | ---: | ---: | ---: | --- |
| prepared node-coverage scalar threshold | 1000000 | 3.948736324 | 2.037808402 | 1.94x | oracle_match_both=True, covered_count_match=True |

Boundary: native RTDL prepared node-coverage decision only. This does not claim whole Barnes-Hut force-vector acceleration, paper reproduction, release readiness, or public speedup wording.
