# Goal 72: Vulkan Long County Prepared-Execution Check

Priority:
- after Goal 71
- before the Linux-wide test closure goal

Problem:
- Goal 66 made Vulkan parity-clean on the accepted bounded validation surface,
  but Vulkan still had unclear performance posture on the long `county_zipcode`
  positive-hit `pip` workload
- after Goals 70 and 71, the next honest question was whether Vulkan could stay
  parity-correct on the same execution-ready boundary and how far it remained
  from PostGIS

Goal:
- measure Vulkan on the long `county_zipcode` positive-hit `pip` workload under
  the execution-ready / prepacked timing boundary
- preserve exact parity
- document the result honestly whether it is a win or a loss

Accepted timing boundary:
- execution-ready / prepacked Vulkan timing
- the timed region may exclude:
  - `prepare_vulkan(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
  - `prepared.bind(...)`

Non-goals:
- forcing a Vulkan-over-PostGIS claim if the measurements do not support it
- changing full-matrix semantics
- broad Vulkan redesign in this goal
