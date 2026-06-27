# Iteration 1 Response

Date: 2026-04-02
Round: 2026-04-02-goal-28c-linux-county-zipcode-exact-source-execution

Pre-implementation reviews accepted execution and identified two design declarations that must be explicit before the host run:

1. ring-to-chain rule:
   - one ArcGIS ring becomes one CDB chain
   - `left_face_id` is the source feature `OBJECTID`
   - `right_face_id` is `0`
   - multipart features therefore become multiple chains sharing the same face id
   - the current polygon execution path remains a chain-derived approximation, not a topological face rebuild

2. CPU meaning:
   - `CPU` in this round means the existing pure-Python RTDL reference path through `rt.run_cpu(...)`
   - `Embree` means the native local Embree backend through `rt.run_embree(...)`

Execution will stay inside a parity-checkable exact-source subset chosen from the converted Linux-host inputs after a size probe.
