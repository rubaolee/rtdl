# Goal2643 Detailed Report: Current RTDL Benchmark-App Portfolio

Date: 2026-05-27

Status: internal detailed portfolio report. This is not a release/tag
operation, not public speedup wording, and not a whole-paper reproduction
claim.

## Executive Summary

RTDL currently has 10 promoted benchmark apps. They are not ordinary examples
and not product claims. They are reconstruction instruments: each app stresses
the Python+partner+RTDL language/runtime boundary, exposes missing generic
primitive behavior, and records where native Embree/OptiX engines must stay
app-agnostic.

Current promoted benchmark apps:

| # | Benchmark app | Core contract | Current benchmark status |
| ---: | --- | --- | --- |
| 1 | Hausdorff / X-HD-style | Hausdorff threshold/witness over point sets | Promoted; threshold Embree-vs-OptiX diff complete, exact-witness OptiX rows exist without same-contract Embree ratio. |
| 2 | Spatial RayJoin-style | PIP, LSI, and overlay-seed spatial relation rows/summaries | Promoted; scoped prepared spatial routes measured, not full RayJoin reproduction. |
| 3 | RT-DBSCAN-style | Fixed-radius density/core/component contract | Promoted; generic fixed-radius plus grouped continuation, no DBSCAN-native engine ABI. |
| 4 | Robot collision | Prepared static-scene collision flags | Promoted; static feasibility screening only, not a planner or swept solver. |
| 5 | RayDB-style grouped aggregate | Predicate-filtered grouped count/sum over typed columns | Promoted; partner-resident grouped reduction, not SQL/DBMS and not RT-core traversal. |
| 6 | Barnes-Hut / RT-BarnesHut-style | Node coverage and aggregate-frontier-style hierarchical candidate discovery | Promoted; latest Goal2641/2642 adds RT-core generic membership lowering without native force logic. |
| 7 | LibRTS-style spatial index | Generic 2-D AABB point/range count-only queries | Promoted; internal count-only slice, not mutable LibRTS reproduction. |
| 8 | RTNN neighbor search | Prepared 3-D fixed-radius ranked summary | Promoted; same-contract ranked summary, not full RTNN paper-system reproduction. |
| 9 | Triangle counting | RT-Graph-style triangle-counting summary | Promoted; triangle counting only, with segmented/streamed lowering still required for largest paper datasets. |
| 10 | Bounded contact witness / contact-manifold | Generic AABB broadphase plus bounded witness collection | Promoted; validates `COLLECT_K_BOUNDED`; no contact/collision native ABI. |

RayDB has two standard performance rows because grouped count and grouped sum
are distinct reduction contracts. GPU-RMQ and continuous Frechet are explicitly
not benchmark apps: they remain learner/design-pressure apps.

## Source Evidence

This report consolidates the current on-disk evidence from:

- `docs/application_catalog.md`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal2587_benchmark_apps_milestone_report_2026-05-24.md`
- `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`
- `docs/reports/goal2642_barnes_hut_embree_vs_optix_app_perf_2026-05-27.md`
- `examples/v2_0/research_benchmarks/*/README.md`

The main all-benchmark performance matrix is internal exact-subpath evidence
from an NVIDIA RTX A5000 pod. It does not authorize broad public wording.

## Portfolio Performance Summary

The current measured portfolio has:

| Matrix | Rows | OptiX wins | Min speedup | Median speedup | Geomean speedup | Max speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard all-benchmark matrix | 11 | 11 | 3.29x | 29.95x | 32.25x | 280.15x |
| Strengthened weak-row matrix | 13 | 13 | 1.81x | 23.38x | 16.90x | 170.63x |
| Strengthened stress matrix | 16 | 16 | 1.26x | 36.36x | 21.69x | 465.45x |

Correct narrow conclusion:

```text
On the recorded RTX A5000 artifacts, every current promoted benchmark app has
Embree/CPU-vs-OptiX evidence at its exact benchmark subpath boundary, and the
OptiX path wins every current standard and strengthened ratio row.
```

Incorrect conclusion:

```text
RTDL universally beats Embree/CUDA/author systems for whole applications.
```

That broader claim is not supported.

## Standard Embree-vs-OptiX Matrix

| App | Comparison group | Embree sec | OptiX sec | OptiX speedup | Boundary |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | Threshold decision | 0.102451 | 0.0311073 | 3.29x | Threshold-decision subpath, not every exact witness path. |
| Spatial RayJoin-style | Scoped all-backend query summary | 0.0203149 | 0.000529638 | 38.36x | Scoped spatial relation summary, not full RayJoin. |
| RT-DBSCAN-style | Cluster signature | 20.6102 | 1.62144 | 12.71x | App output contract; no DBSCAN-native ABI. |
| Robot collision | Prepared collision flags | 0.00853798 | 0.00161413 | 5.29x | Static-scene prepared flags only. |
| RayDB-style grouped aggregate | Grouped count | 0.222185 | 0.000793088 | 280.15x | Partner-resident grouped reduction, not RT-core traversal. |
| RayDB-style grouped aggregate | Grouped sum | 0.243746 | 0.000977349 | 249.40x | Partner-resident grouped reduction, not SQL/DBMS. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage prepared threshold decision | 0.0388851 | 0.00855045 | 4.55x | Node-coverage subpath, not full force solve. |
| LibRTS-style spatial index | AABB index count-only | 20.7070 | 0.691477 | 29.95x | Count-only generic AABB index contract. |
| RTNN neighbor search | Prepared 3-D ranked summary | 0.263800 | 0.00153247 | 172.14x | Ranked-summary contract only. |
| Triangle counting | RT-Graph-style RT-2A1 summary | 0.0390490 | 0.000364401 | 107.16x | Synthetic/backend-query contract; not paper-dataset speedup. |
| Bounded contact witness / contact-manifold | Generic AABB broadphase + bounded collection | 0.485812 | 0.0184764 | 26.29x | Generic AABB rows plus bounded collection. |

## Strengthened Rows For Previously Weak Apps

Goal2636 strengthened the weaker standard rows: Hausdorff, Spatial RayJoin,
RTNN, Barnes-Hut, and triangle counting.

| App | Strengthened workload | Embree sec | OptiX sec | OptiX speedup | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | Threshold, 4096 copies | 0.100719 | 0.0344760 | 2.92x | OptiX wins at small/standard scale. |
| Hausdorff / X-HD-style | Threshold, 16384 copies | 0.380607 | 0.181478 | 2.10x | OptiX wins at larger threshold scale. |
| Hausdorff / X-HD-style | Threshold, 65536 copies | 1.70826 | 0.946120 | 1.81x | OptiX still wins; margin narrows. |
| Spatial RayJoin-style | PIP authored tiled x512 | 0.0233497 | 0.000315720 | 73.96x | Nonzero tiled point-in-polygon route. |
| Spatial RayJoin-style | LSI authored tiled x512 | 0.0298779 | 0.000303850 | 98.33x | Nonzero tiled line-segment route. |
| Spatial RayJoin-style | Overlay-seed authored tiled x512 | 0.266497 | 0.0558806 | 4.77x | Overlay dependency route, not full overlay materialization. |
| RTNN neighbor search | Uniform 65536 ranked summary | 0.258464 | 0.0106400 | 24.29x | OptiX wins uniform distribution. |
| RTNN neighbor search | Clustered 65536 ranked summary | 2.16539 | 0.0926344 | 23.38x | OptiX wins density-risk clustered distribution. |
| RTNN neighbor search | Shell 65536 ranked summary | 0.934770 | 0.00547840 | 170.63x | OptiX wins shell distribution. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 8192 bodies | 0.0393546 | 0.00862844 | 4.56x | Same-contract node coverage positive. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 32768 bodies | 0.113009 | 0.0374079 | 3.02x | Same-contract app-internal timing positive. |
| Triangle counting | RT-Graph 2A1, 5000 K4 cliques | 0.0490641 | 0.000372456 | 131.73x | Generic RT-Graph backend-query row positive. |
| Triangle counting | RT-Graph 2A1, 20000 K4 cliques | 0.102953 | 0.000755426 | 136.28x | Current generic RT path positive. |

## Latest Barnes-Hut Follow-Up

After the standard and strengthened node-coverage rows, Goal2641/2642 added a
more relevant aggregate-frontier lowering:

```text
bucketized aggregate tree
  -> app-owned near-zone AABBs
  -> generic EXPANDED_AABB_POINT_MEMBERSHIP_2D rows
  -> Python opening continuation
  -> Python/app force interpretation
```

The native OptiX engine still sees only generic points, AABBs, IDs, row
capacity, row offsets, and rows. It does not contain Barnes-Hut theta, mass,
inverse-square force, or paper vocabulary.

| Bodies | Frontier rows | Near-zone rows | Embree total sec | OptiX total sec | Total speedup | Embree membership sec | OptiX membership sec | Membership speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | 4,543 | 1,340 | 0.0947 | 0.7066 | 0.13x | 0.0405 | 0.6543 | 0.06x |
| 512 | 28,988 | 7,362 | 0.3946 | 0.2816 | 1.40x | 0.1156 | 0.0127 | 9.09x |
| 2,048 | 258,495 | 37,087 | 3.5560 | 1.8440 | 1.93x | 1.6563 | 0.0539 | 30.74x |
| 8,192 | 1,188,963 | 203,083 | 74.9243 | 11.1908 | 6.70x | 66.0805 | 0.8848 | 74.68x |

This is now the best Barnes-Hut RT-core story: OptiX loses at tiny 128-body
scale due to setup/launch/row-transfer overhead, wins from 512 bodies onward,
and reaches 6.70x total app-lowering speedup at 8,192 bodies. The remaining
limiter is Python continuation and force interpretation, not RT candidate
discovery.

## App Details

### 1. Hausdorff / X-HD-style

Purpose:

The app computes exact or thresholded Hausdorff-style distance over point sets.
The benchmark is informed by X-HD-style ideas: threshold search, witness
extraction, grouping, active-set pruning, and reduced continuation.

RTDL contract:

- fixed-radius/nearest decision and witness primitives over point sets;
- grouped or reduced witness paths;
- Python/partner continuation for final exact value where needed.

What it added to RTDL:

- scale-aware grouped traversal;
- threshold-decision rows;
- witness extraction pressure;
- max-distance continuation and grouped reduction pressure;
- strict distinction between exact value and threshold interval.

Current performance meaning:

- Standard threshold decision: 3.29x OptiX over Embree.
- Strengthened threshold rows: 2.92x, 2.10x, and 1.81x.
- OptiX exact witness rows exist, but there is no same-contract Embree exact
  witness ratio in the current harness.

Boundary:

Do not claim RTDL beats every CUDA Hausdorff implementation. Earlier evidence
showed optimized grouped CuPy can remain faster on some exact 2-D projected
point cases.

### 2. Spatial RayJoin-style

Purpose:

The app expresses RayJoin-style spatial workloads: point-in-polygon, line
segment intersection, and overlay-seed dependency rows.

RTDL contract:

- generic point/polygon and segment/segment traversal;
- prepared spatial relation routes;
- rows/counts/summaries as app-selected outputs;
- Python owns positive-hit filtering, overlay continuation, and paper
  interpretation.

What it added to RTDL:

- prepared closed-shape queries;
- first-hit/count modes;
- generic shape-pair fixes;
- phase telemetry;
- overlay dependency rows as a continuation-pressure case.

Current performance meaning:

- Standard scoped query summary: 38.36x OptiX over Embree.
- Strengthened PIP/LSI rows: 73.96x and 98.33x.
- Overlay-seed route is positive at 4.77x but is not full polygon overlay.

Boundary:

This is not full RayJoin reproduction. Overlay materialization and spatial
database semantics remain outside the native engine.

### 3. RT-DBSCAN-style

Purpose:

The app implements DBSCAN-shaped density clustering over 3-D fixed-radius
queries and component continuation.

RTDL contract:

- fixed-radius count/threshold flags;
- neighbor rows or capped count summaries;
- grouped continuation over generic radius graph streams;
- Python/partner owns cluster semantics and label interpretation.

What it added to RTDL:

- 3-D fixed-radius count-threshold device columns;
- core-flag handoff;
- adjacency stream pressure;
- grouped-union continuation;
- dense-stream memory controls;
- explainable plan selection.

Current performance meaning:

- Standard app-contract row: 12.71x OptiX over Embree.
- Earlier closeout evidence showed grouped-stream RTDL beating prepared CuPy
  grid by roughly 3.9x to 4.9x on clustered3d rows.

Boundary:

There is no DBSCAN-native ABI in the engine. The engine owns generic
fixed-radius/grouped behavior; DBSCAN cluster expansion remains app/partner
logic.

### 4. Robot Collision

Purpose:

The app screens batched robot poses or link segments against a prepared static
triangle scene.

RTDL contract:

- prepared static scene;
- finite 3-D segment/triangle any-hit flags;
- grouped pose/link flags and count-only summaries;
- compact output modes.

What it added to RTDL:

- reusable prepared static scenes;
- query-buffer reuse;
- host/device output-buffer reuse;
- compact flag/count contracts;
- app-vocabulary purity guards.

Current performance meaning:

- Standard prepared collision flags: 5.29x OptiX over Embree.
- Supporting stress row: 8.84x OptiX over Embree for 32,768 poses and 512
  obstacles.

Boundary:

This is static-scene feasibility screening. It is not continuous collision
detection, a robot planner, physics simulation, or exact swept-volume solver.

### 5. RayDB-style Grouped Aggregate

Purpose:

The app expresses a RayDB-style grouped aggregate over typed columns.

RTDL contract:

- predicate-filtered grouped integer count/sum;
- partner-resident typed columns;
- grouped reduction dispatcher;
- compact result rows.

What it added to RTDL:

- `DeviceColumnDescriptor`;
- grouped i64/f64 reductions;
- fused grouped stats pressure;
- partner-resident execution as a first-class path;
- stronger distinction between DB-shaped workloads and DBMS semantics.

Current performance meaning:

- Grouped count standard row: 280.15x OptiX-labeled path over Embree/CPU path.
- Grouped sum standard row: 249.40x.
- These are CUDA/partner-resident grouped reductions, not RT-core traversal.

Boundary:

This is not SQL, SSB, transactions, indexes, query planning, or a DBMS. It is a
same-contract compact grouped aggregate.

### 6. Barnes-Hut / RT-BarnesHut-style

Purpose:

The app studies hierarchical aggregate-frontier discovery and force-accumulation
pressure inspired by RT-BarnesHut.

RTDL contract:

- bucketized aggregate tree rows;
- aggregate/frontier ID collection;
- generic expanded-AABB point-membership rows;
- Python/partner force interpretation;
- no native force law.

What it added to RTDL:

- bucketized Morton/DFS aggregate tree rows;
- `AGGREGATE_FRONTIER_COLLECT_2D` candidate behavior;
- `EXPANDED_AABB_POINT_MEMBERSHIP_2D` RT-core bridge;
- explicit rejection of app-specific inverse-square native kernels;
- pressure for device-resident continuation and vector reduction.

Current performance meaning:

- Standard node-coverage row: 4.55x OptiX over Embree.
- Strengthened node-coverage rows: 4.56x and 3.02x.
- Latest aggregate-frontier lowering: 6.70x total app-lowering speedup at
  8,192 bodies and 74.68x membership-primitive speedup.

Boundary:

Do not claim full RT-BarnesHut paper reproduction or full force-solver speedup.
The best current RT result accelerates generic candidate discovery; Python still
owns opening continuation and force interpretation.

### 7. LibRTS-style Spatial Index

Purpose:

The app studies LibRTS-style 2-D spatial-index point/range query semantics.

RTDL contract:

- generic `AABB_INDEX_QUERY_2D`;
- point contains, range contains, and range intersects;
- prepared query buffers;
- count-only summaries.

What it added to RTDL:

- generic AABB index operation;
- prepared AABB query-buffer reuse;
- two-pass range-intersects traversal;
- authors-code fixture interchange for count validation;
- clearer distinction between mutable spatial index systems and RTDL query
  primitives.

Current performance meaning:

- Standard AABB index count-only row: 29.95x OptiX over Embree.
- Earlier generated paper-like rows showed RTDL prepared OptiX close to or
  better than authors-code count-only timings for selected operations.

Boundary:

This is not full mutable LibRTS reproduction. It is an internal generic
AABB-index count-only slice.

### 8. RTNN Neighbor Search

Purpose:

The app studies RTNN-style 3-D neighbor search through prepared fixed-radius
ranked summaries.

RTDL contract:

- prepared 3-D fixed-radius neighbor/ranked-summary primitives;
- distribution-aware test rows;
- optional ANN candidate-quality helper outside the benchmark identity.

What it added to RTDL:

- prepared search-side structures;
- device-side ranked summary;
- candidate-quality references;
- density-aware partitioning pressure;
- top-k/ranked continuation pressure.

Current performance meaning:

- Standard prepared ranked summary: 172.14x OptiX over Embree.
- Strengthened distribution ladder: 24.29x uniform, 23.38x clustered, 170.63x
  shell.
- Supporting larger row: 313.66x for large prepared 3-D ranked summary.

Boundary:

This is not a full RTNN paper-system reproduction and not a general ANN index.
Official RTNN binary rows are diagnostic unless output-contract equivalence is
separately proven.

### 9. Triangle Counting

Purpose:

The app promotes only triangle counting from the broader graph examples. It is
informed by RT-Graph/SIGMETRICS 2025.

RTDL contract:

- RT-Graph-style RT-2A1 and RT-1A2 mappings;
- generic 3-D rays/triangles plus scalar summaries;
- graph preprocessing in Python/partner code;
- no graph-specific native ABI.

What it added to RTDL:

- graph-to-generic-ray/triangle lowering;
- raw row and compact summary paths;
- weighted any-hit / hit-count scalar summary pressure;
- strict separation between graph semantics and engine primitives;
- segmented/streamed lowering as a real future requirement.

Current performance meaning:

- Standard RT-2A1 summary: 107.16x OptiX over Embree.
- Strengthened K4 rows: 131.73x and 136.28x.
- Stress K4 rows include 144.83x and 465.45x.

Boundary:

The real paper datasets exposed scalability limits in current unsegmented CuPy
lowering. cuGraph remains the strongest current end-to-end baseline on real
paper datasets that completed. No paper-dataset speedup claim is authorized.

### 10. Bounded Contact Witness / Contact-Manifold

Purpose:

The app uses a contact/collision-flavored workload to force a generic bounded
witness-row primitive.

RTDL contract:

- generic `AABB_INDEX_QUERY_2D` broadphase rows;
- stable `COLLECT_K_BOUNDED`;
- exact fail-closed overflow semantics;
- app-owned exact triangle-intersection refinement and contact interpretation.

What it added to RTDL:

- stable bounded row collection;
- exact fail-closed overflow before materialization;
- prepared AABB broadphase row output;
- generic row schema and capacity discipline;
- no native contact/collision ABI.

Current performance meaning:

- Standard generic AABB broadphase + bounded collection: 26.29x OptiX over
  Embree.
- Supporting large contact broadphase stress row: 16.89x OptiX over CPU/Embree
  path.

Boundary:

The app may say contact or collision, but the engine primitive only says
bounded witness collection and generic candidate rows. Exact contact geometry
and contact summaries remain Python/app logic.

## Cross-App Primitive Pressure

The benchmark suite has converged on behavior-first primitives rather than
app-specific native kernels.

| Runtime theme | Apps that forced it | Resulting RTDL direction |
| --- | --- | --- |
| Prepared reusable state | RayJoin, robot collision, LibRTS, RTNN, RT-DBSCAN, Barnes-Hut | Serious benchmarks need prepared scenes, prepared query buffers, and reusable backend state. |
| Compact outputs | Robot collision, RayDB, RTNN, RT-DBSCAN, LibRTS, triangle counting | Flags, counts, summaries, and grouped reductions are often the right fast contract. |
| Row emission with capacity | Contact manifold, LibRTS, Barnes-Hut, Spatial RayJoin | Row paths need explicit schemas, offsets, capacity, and fail-closed overflow rules. |
| Bounded materialization | Contact manifold, RT-DBSCAN, RTNN | Materialization must be bounded or replaced by summaries/continuation. |
| Grouped/keyed reductions | RayDB, RT-DBSCAN, RTNN, Hausdorff | Grouped reductions are shared behavior, not app-specific database logic. |
| Partner-resident continuation | RayDB, Hausdorff, RT-DBSCAN, triangle counting, Barnes-Hut | Python+partner+RTDL is the correct architecture when continuation is not RT traversal. |
| Generic AABB indexing | LibRTS, contact manifold, Barnes-Hut | AABB point/range/membership rows are reusable primitives. |
| Aggregate/frontier pressure | Barnes-Hut, contact-style bounded rows | Frontier collection should become generic row/continuation behavior, not force-law native code. |
| Segmented/streamed lowering | Triangle counting, RT-DBSCAN, large row-output apps | Large intermediate row materialization is the next major runtime problem. |
| App-agnostic native boundary | All benchmark apps | Native engines must see generic geometry, columns, buffers, rows, summaries, and reductions; app formulas stay outside. |

## Current Primitive Inventory Exposed By Benchmarks

Stable or strong internal primitives:

- `ANY_HIT`
- `COUNT_HITS`
- fixed-radius count/threshold behavior
- `AABB_INDEX_QUERY_2D`
- `COLLECT_K_BOUNDED`
- scalar reductions
- grouped/keyed reductions as internal substrate
- columnar compact summaries

Candidate or still-maturing behaviors:

- `EXPANDED_AABB_POINT_MEMBERSHIP_2D`
- `AGGREGATE_FRONTIER_COLLECT_2D`
- segmented/chunked row streaming
- device-resident grouped continuation
- partner-resident force/vector reduction
- graph segmented RT-Graph lowering

Rejected as native engine primitives:

- DBSCAN cluster expansion;
- robot pose/link/planner semantics;
- Barnes-Hut inverse-square force law;
- contact/collision/manifold semantics;
- SQL/DBMS/query-planner semantics;
- graph triangle-counting semantics as a native app ABI.

## Non-Benchmark Apps

The following are explicitly outside the promoted benchmark set:

| App | Current status | Reason |
| --- | --- | --- |
| GPU-RMQ | Learner/design-pressure app | Useful for closest-hit and grouped candidate-merge pressure, but current RTDL path was slower than direct CUDA sparse-query code. |
| Continuous Frechet distance | Learner/demo app | Correct and useful for broadphase/free-space candidate discovery, but optimized CPU C++ was stronger in measured rows. |
| Graph BFS / visibility edges | Learner/demo/example paths | The promoted graph benchmark is triangle counting only. |
| General geospatial/ML/analytics examples | Learner examples | Useful for teaching, not promoted benchmark evidence. |

## Remaining Engineering Priorities

The portfolio is strong enough to guide v2.x runtime design, but several
technical debts remain:

1. Move more continuation work device-resident without app-specific native
   kernels.
2. Add segmented/chunked row streaming for triangle counting and dense
   fixed-radius workloads.
3. Improve zero-copy and typed host/device buffer contracts for columnar and
   row-heavy apps.
4. Promote `EXPANDED_AABB_POINT_MEMBERSHIP_2D` only after more cross-app use
   and review.
5. Continue Barnes-Hut by moving generic continuation/reduction closer to
   partner/native execution, while keeping force math outside the engine.
6. Keep RayDB clearly labeled as partner-resident grouped reduction, not an
   RT-core acceleration row.
7. For public docs, cite exact script, artifact, backend, hardware, commit,
   and output contract for every performance statement.

## Final Assessment

The benchmark portfolio now shows a coherent RTDL architecture:

```text
Python owns app semantics and lowering.
Partners own non-RT continuation when appropriate.
RTDL native engines own app-independent geometry traversal, row emission,
bounded materialization, prepared state, and reductions.
```

The main success is not just that many rows are faster with OptiX. The main
success is that multiple unrelated benchmark apps have forced the same small
set of reusable runtime behaviors. That is the evidence that RTDL is becoming
a general app-independent RT-oriented language/runtime for these supported
primitive families, rather than a pile of app-specific kernels.
