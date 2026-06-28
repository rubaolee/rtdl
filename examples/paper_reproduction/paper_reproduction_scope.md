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
| RayJoin | RayJoin paper suite for LSI, PIP, and Section 5.7 Polygon Overlay | RTDL operator, partner, and measurement docs |

## Reading Order

1. Learn the small concept program first.
2. Open the standard benchmark app entrypoint when the paper route maps to the
   benchmark suite.
3. Use the paper-specific runner when the paper route has stricter inputs or
   timing rules.

## Boundary

These wrappers are paper-oriented app entrypoints. They do not claim that every
detail of an external paper artifact is reproduced. A full paper claim requires
the exact input status, backend route, correctness contract, and timing protocol
to be recorded together.

For RayJoin Section 5.7 Polygon Overlay, `overlay_seed` rows are not enough.
Use:

```bash
python3 examples/paper_reproduction/rayjoin.py --section57-plan --dataset-root data/rayjoin_section57_cdb
python3 examples/paper_reproduction/rayjoin.py --section57-run --dataset-root data/rayjoin_section57_cdb --query-exec /workspace/RayJoin_fresh/release/bin/query_exec --polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec
```
