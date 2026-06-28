# Paper Reproduction Scope

Paper-reproduction entrypoints are different from the standard benchmark app
entrypoints.

The standard benchmark apps teach the current RTDL V4 programming model. The
paper-reproduction entrypoints keep paper-oriented names and route to the
matching implementation so a reader can compare the RTDL route with the
paper-style workload.

## Current Entrypoints

| Paper-oriented app | What it routes to | What to learn first |
| --- | --- | --- |
| RT-BarnesHut | Barnes-Hut aggregate-frontier app | `aggregate_frontier_rows.py` |
| RayJoin | Spatial RayJoin app | `rayjoin_topology_intro.py` |

## Reading Order

1. Learn the small concept program first.
2. Open the standard benchmark app entrypoint.
3. Run the paper-reproduction wrapper only when you want the paper-labeled
   route.

## Boundary

These wrappers are paper-oriented app entrypoints. They do not claim that every
detail of an external paper artifact is reproduced. They show how the workload
is expressed through the current RTDL V4 app route.
