# Codex Consensus: Goal 50 PostGIS Ground-Truth Comparison

Verdict: `APPROVE`

Consensus basis:

- Codex local review: approve
- Gemini review: approve

## Accepted Result

Goal 50 succeeded.

On `192.168.1.20`, with indexed PostGIS query plans:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
  - `lsi`: PostGIS == C oracle == Embree == OptiX
  - `pip`: PostGIS == C oracle == Embree == OptiX
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`
  - `lsi`: PostGIS == C oracle == Embree == OptiX
  - `pip`: PostGIS == C oracle == Embree == OptiX

## Important Boundary

- The accepted `pip` parity now relies on GEOS prepared-polygon `covers(point)` semantics in the RTDL refine path.
- This is an explicit correctness alignment choice made to satisfy the strict Goal 50 rule that accepted RTDL results may not differ from PostGIS on the tested packages.
- Goal 50 remains a bounded-package validation round. It does not claim full nationwide PostGIS reproduction of the RayJoin paper.
