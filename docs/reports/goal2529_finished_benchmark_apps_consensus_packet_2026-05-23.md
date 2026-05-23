# Goal2529: Finished Benchmark Apps Consensus Packet

Date: 2026-05-23

## Purpose

This packet asks for 3-AI consensus on the benchmark apps that are finished so
far. The consensus question is deliberately bounded:

```text
Can RTDL treat these benchmark apps as completed reconstruction instruments for
their stated scopes, without claiming full paper reproduction, authors-code
parity, broad public speedups, or app-specific native-engine behavior?
```

The answer should not authorize a release tag, package-install support, or
new public performance wording. It should only classify the finished benchmark
apps and lock the claim boundary for future docs.

## Consensus Scope

The finished benchmark apps are the five current research benchmark studies
under `examples/v2_0/research_benchmarks/`:

| App | Closeout status | Closeout evidence | Consensus classification |
| --- | --- | --- | --- |
| Hausdorff/X-HD-style | Round complete with bounded acceptance; v2.1 defaults refreshed, fresh current-main pod timing still needed before replacing May 16 numbers | `docs/reports/goal2141_rtdl_hausdorff_application_acceleration_synthesis_2026-05-16.md`, `docs/reports/goal2340_hausdorff_v2_1_benchmark_refresh_2026-05-18.md` | Finished as exact 2D projected-point Hausdorff reconstruction app; current-main performance refresh remains separate |
| Spatial RayJoin-style | Closed for v2.0 with boundary | `docs/reports/goal2315_rayjoin_v2_0_bounded_closure_2026-05-17.md` | Finished as scoped LSI/PIP RayJoin-style RTDL language/runtime app |
| RT-DBSCAN-style | Current v2.x project complete | `docs/reports/goal2478_rt_dbscan_project_completion_2026-05-21.md` | Finished as generic fixed-radius graph/component benchmark app |
| Robot-collision-style | Benchmark app closeout complete | `docs/reports/goal2491_robot_collision_benchmark_app_closeout_2026-05-22.md` | Finished as sampled finite-segment static-scene feasibility-screening app |
| RayDB-style | Benchmark app closeout complete after fused full-contract grouped stats path | `docs/reports/goal2528_raydb_style_benchmark_app_closeout_2026-05-23.md` | Finished as deterministic columnar grouped-aggregate reconstruction app |

Ordinary learner apps under `examples/v2_0/apps/` are not part of this
consensus. Goal2342 already audited ordinary apps and concluded that cosmetic
rewrites were not needed.

## Shared Closeout Rule

These benchmark apps are reconstruction instruments. A benchmark is finished
when it has forced and validated a reusable RTDL language/runtime contract, not
when it has reproduced every external paper system. This rule is recorded in
`docs/reports/goal2492_benchmark_app_reconstruction_principle_and_raydb_scope_2026-05-22.md`.

The completed apps share these properties:

- The native engine path is app-name-free for the supported primitive surface.
- App and domain semantics stay in Python examples, adapters, or benchmark
  scripts.
- Each app has a documented correctness oracle or same-contract parity path.
- Performance evidence is exact-subpath evidence only.
- Paper reproduction, authors-code comparison, and broad speedup wording remain
  blocked unless a later goal scopes and reviews that exact claim.

## App-By-App Decision Basis

### Hausdorff / X-HD-Style

The Hausdorff app is finished as an exact 2D projected-point Hausdorff
benchmark. It showed that Python can own X-HD-style policy while RTDL exposes
generic point-group threshold and nearest-witness reductions. Goal2141 records
bounded acceptance and reviewed evidence that RTDL/OptiX beat optimized grouped
CuPy on measured public dense graphics and geo rows. Goal2340 refreshed the
current v2.1 user path with scale-aware grouping, but explicitly says fresh pod
timing is still needed before replacing the May 16 public numbers.

Authorized boundary:

- RTDL can express exact 2D projected-point Hausdorff with app-level X-HD-style
  policy over generic RTDL primitives.
- Prior May 16 performance rows remain evidence-backed when quoted with their
  exact datasets, hardware, commands, and reviews.

Blocked boundary:

- Full X-HD reproduction, full 3D surface Hausdorff, MRI/BraTS reproduction,
  universal CUDA-vs-RT speedup, and fresh current-main performance replacement
  claims.

### Spatial RayJoin-Style

The RayJoin-style app is finished for scoped LSI and PIP workloads. Goal2315
closed the v2.0 lane after prepared generic segment intersection and prepared
closed-shape membership reached exact parity on imported 100k RayJoin-exported
streams. The closure explicitly records that the original RayJoin
implementation remains faster and that the comparison is research pressure, not
public win/loss wording.

Authorized boundary:

- RTDL can express and execute scoped RayJoin-style LSI/PIP workloads with
  generic prepared primitives.
- The route remains app-agnostic and supports low-millisecond prepared-query
  evidence for the measured streams.

Blocked boundary:

- Full RayJoin reproduction, RTDL-beats-RayJoin wording, whole-app speedup, and
  broad arbitrary spatial-join acceleration claims.

### RT-DBSCAN-Style

The RT-DBSCAN app is finished for the current v2.x scope. Goal2478 records a
working application shape:

```text
3-D fixed-radius neighbor search -> core-point threshold -> radius-graph components
```

The final implementation uses generic fixed-radius rows, threshold-capped
count/core columns, adjacency streams, grouped union/continuation columns, and
partner CuPy continuation. It does not add DBSCAN-specific native vocabulary or
ABI. The final pod matrix records correctness signatures and performance for
prepared CuPy, OptiX RT-count bridge, and grouped-stream continuation.

Authorized boundary:

- RTDL now has generic fixed-radius graph/component primitives sufficient for a
  serious RT-DBSCAN-style benchmark app.
- The app can be closed as a benchmark app because the remaining work is
  paper/authors-code/public-claim scoping, not missing current-scope runtime
  functionality.

Blocked boundary:

- Paper reproduction, paper-level speedup, broad DBSCAN acceleration, official
  dataset parity, or native DBSCAN semantics.

### Robot-Collision-Style

The robot-collision benchmark is finished as sampled discrete feasibility
screening over static triangles and grouped finite segment probes. Goal2491
records the final matrix and the supported contract. Python lowers robot poses
and link samples; Embree/OptiX evaluate generic grouped finite 3D segment
any-hit flags against prepared static triangle scenes; output is compact group
flags or count-only screening.

Authorized boundary:

- RTDL has reusable generic primitives for sampled feasibility screening over
  prepared static triangle scenes with grouped finite segment queries.
- The benchmark exposed and validated prepared query reuse, host/device query
  buffer reuse, compact flags, count-only screening, and phase telemetry.

Blocked boundary:

- General robot collision, continuous or swept collision, exact solid contact,
  authors-code comparison, public speedup wording, or robot-specific native
  ABI.

### RayDB-Style

The RayDB-style app is finished as a deterministic columnar grouped-aggregate
benchmark. Goal2528 closes it after the app forced partner-resident columnar
descriptors, a generic grouped i64 dispatcher, grouped min/max, fused
sum/count, raised partner-resident grouped-row capacity, and fused grouped
stats returning count/sum/min/max in one native launch.

Authorized boundary:

- RTDL can execute a deterministic columnar grouped aggregate contract with
  CPU correctness, PostgreSQL correctness/indexed timing, DuckDB timing, cuDF
  timing, and RTDL OptiX partner-resident fused full-contract timing.
- The new native operation is generic grouped integer statistics, not a
  RayDB-specific ABI.

Blocked boundary:

- RayDB paper reproduction, authors-code comparison, SSB reproduction, SQL
  engine/DBMS behavior, query optimization, Crystal/GPU-DBMS comparison, or
  broad public speedup wording.

## Cross-App RTDL Design Improvements

The finished apps collectively justify the following internal design conclusion:

| Pressure | App(s) that exposed it | Reusable RTDL result |
| --- | --- | --- |
| Exact RT-assisted continuation with witness/reduction semantics | Hausdorff/X-HD | Generic point-group threshold, nearest-witness, and reduction paths |
| Prepared spatial relationship queries and row/count distinction | Spatial RayJoin | Generic prepared segment/closed-shape relationship paths and row/count claim discipline |
| Fixed-radius graph continuation and memory-bounded streams | RT-DBSCAN | Generic threshold columns, adjacency streams, grouped union/continuation, and planner boundaries |
| Repeated dynamic query geometry over reusable static scenes | Robot collision | Generic grouped finite 3D segment probes, prepared scene reuse, reusable query buffers, compact flags |
| Columnar partner-resident grouped reductions | RayDB-style | Generic CUDA tensor descriptors and fused grouped integer statistics |

These are language/runtime improvements, not app-specific products.

## Proposed Consensus Verdict

Codex proposed verdict: `accept-with-boundary`.

Reason:

- All five research benchmark apps have enough evidence to be considered
  finished for their scoped reconstruction purposes.
- None should be represented as a full reproduction of the paper/application
  that inspired it.
- None authorizes broad public speedup wording without a separate exact-claim
  evidence and review gate.
- The native engine boundary remains the central invariant: supported primitive
  paths must remain app-name-free, while app semantics live in Python.

## Questions For Claude And Gemini

Please review this packet and answer with an explicit verdict:

- `ACCEPT`: The five-app finished classification and boundaries are sound.
- `ACCEPT-WITH-BOUNDARY`: The classification is sound only with additional
  wording constraints; specify them.
- `REJECT`: One or more apps should not be called finished; specify blockers.

Review requirements:

- Check whether the five-app set matches the evidence.
- Check whether Hausdorff's pending current-main pod refresh is handled
  correctly.
- Check whether RayJoin, RT-DBSCAN, Robot Collision, and RayDB are bounded away
  from full paper/authors-code/public-speedup claims.
- Check whether the native-engine app-agnostic boundary is stated strongly
  enough.
- Identify any wording that could mislead a reader into thinking these are
  full product implementations rather than reconstruction benchmark apps.
