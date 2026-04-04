# Goal 69: PIP Performance Repair

Priority:
- higher than Vulkan scalability

Problem:
- On the accepted bounded packages, PostGIS is much faster than RTDL on `pip`.
- The main gap is not only implementation quality; it is also a contract mismatch.
- PostGIS answers an indexed positive-hit query.
- RTDL's accepted `pip` contract emits the full point x polygon matrix with `contains=0/1`.

Goal:
- add an explicit RTDL `pip` execution mode for positive-hit workloads
- preserve the existing full-matrix `pip` semantics as the default and accepted parity baseline
- measure the new mode against PostGIS on comparable positive-hit work
- prioritize performance work in this order:
  - OptiX
  - Embree
  - Vulkan later
  - native C oracle remains correctness-oriented, not a primary performance target

Planned scope:
1. add a predicate/result option for positive-hit `pip`
2. implement it in the Python reference and native backends
3. add unit/system tests
4. add a dedicated performance script/report
5. review with Gemini before any publish

Non-goals:
- changing the accepted Goal 50 / Goal 59 full-matrix parity contract
- redesigning all query semantics at once
- solving Vulkan scalability in this goal
