## Goal 17 Pre-Implementation Report

Current repo evidence shows that RTDL's main local performance problem is host/runtime overhead rather than a clearly different native Embree algorithm.

The first redesign slice should therefore target the host path, not the DSL syntax and not the native Embree core.

Proposed implementation boundary:

1. keep RTDL kernel authoring unchanged
2. add a prepared execution path that compiles once and binds native-ready inputs once
3. add packed input containers for:
   - segments
   - points
   - polygons
4. support the first slice for:
   - `lsi`
   - `pip`
5. benchmark:
   - current RTDL Embree
   - new prepared RTDL Embree
   - Goal 15 pure native C++ + Embree

Questions for review:

1. Is this the right first slice, or should the round be narrower?
2. How should the final report decide whether the result is acceptable?
3. What remaining performance gap would still count as a meaningful success for this round?
