# Goal 83: Embree Long Exact-Source Repair

Bring RTDL + Embree to the same long exact-source `county_zipcode` positive-hit `pip`
surface used by Goals 81-82, with exact parity against PostGIS and a documented
performance boundary.

Scope:
- Linux only
- backend: Embree
- workload: long exact-source `county_zipcode` positive-hit `pip`
- compare against indexed PostGIS
- preserve exact parity

Non-goals:
- Vulkan
- oracle performance
- mixed-boundary claims
- publishing before a reviewed package exists
