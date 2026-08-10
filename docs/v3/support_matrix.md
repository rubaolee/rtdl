# V3 Nine-Application Support Matrix

The final functional release candidate covers nine applications.  The table
describes application-owned algorithms and the canonical families used by V3;
it is not a performance ranking.

| Application | Application-owned algorithm/region | V3 canonical family or composition | Functional status |
| --- | --- | --- | --- |
| RTNN | ranked distance window | bounded spatial selection / prepared metric-kNN OptiX | Exact; traversal receipt required |
| RayDB | partitioned grouped I64 sum | keyed ray-triangle events plus grouped reduction | Exact; OptiX producer evidenced |
| LibRTS | AABB overlap and prepared AABB query | canonical AABB traversal families | Exact; OptiX traversal evidenced |
| X-HD | cell-MBR exact witness | cell-MBR nearest-state OptiX plus verified exact continuation | Exact; application fixes the algorithm |
| RT-DBSCAN | prepared fixed-radius spatial components | OptiX neighborhood producer plus verified grouped continuation | 17/17 bounded proof cases exact |
| RayJoin | point location, pair intersection, grouped reduction | OptiX planar-map producers plus verified Numba partner reduction | Exact composition; mixed provider contract explicit |
| RT-BarnesHut | aggregate hierarchy | aggregate-hierarchy OptiX traversal plus exact aggregation | Exact; traversal receipt required |
| Triangle Counting | RT-1A2 and RT-2A1 | all-hit count/value and any-hit weighted/value OptiX families | Both algorithms exact; DEFAULT never chooses between them |
| Arkade | FR-L-infinity and MT-cosine | prepared metric-kNN OptiX with persistent GAS and radius refit | Both algorithms exact; DEFAULT never chooses between them |

## Qualification scope

The clean Home-Linux qualification ran nine applications in eleven fresh
processes and covered fourteen canonical regions.  Every output and independent
canonical-authority reconstruction passed, and every required region produced
a complete behavioral OptiX receipt.  The qualification recorded no
performance timings.

OptiX traversal evidence is not the same as an RT-silicon utilization counter.
The Home machine used for the final functional qualification is a GTX 1070,
which can validate OptiX route behavior but has no hardware RT cores.
