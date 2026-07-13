# Architecture Memory

## System Boundary

RTDL is a generic spatial/dataflow language. Paper reproduction apps are
clients of RTDL and stress tests for reusable language features.

```text
src/rtdsl/ and src/native/
  generic RTDL APIs, native backends, columnar descriptors, frontier/continuation
  execution, row-buffer handoff, and partner-facing contracts

Paper-reproduction-apps/
  paper-specific data provenance, author wrappers, comparators, tolerance
  policy, CLI glue, figure/section labels, and claim boundaries
```

If a concept contains a paper name, author binary detail, figure number, output
format, or benchmark-specific tolerance, it belongs in the app unless a separate
generic API design and non-app consumer prove otherwise.

## Reusable System Assets Extracted So Far

- device-column and row-buffer handoff patterns from RayJoin;
- prepared-pipeline and writer-free binary operator discipline from RayJoin;
- aggregate hierarchy / continuation payload abstractions from RT-BarnesHut;
- partition-equivalence correctness discipline from RT-DBSCAN;
- generic nearest/witness/max-nearest pipeline from X-HD;
- generic grid cell descriptors, cell-MBR candidate/frontier rows, nearest
  state, frontier continuation, and native 3-D cell-MBR traversal front doors
- generic `MutableAabbIndex2D` with stable IDs, atomic prepared-snapshot
  rebuild, and CPU/OptiX execution from LibRTS;
- generic partitioned-traversal fanout and explicit cost-selection reference
  contract, with a Contact-Manifold non-app consumer from LibRTS pressure;

## Mutable AABB Architecture

The current public mutable execution model is hybrid:

```text
pure stable-ID OptiX Update
-> validate sparse slots and IDs
-> upload only changed packed-box and OptixAabb records
-> OptiX GAS refit with ALLOW_UPDATE
-> on failure restore changed records and refit old GAS

Insert/Delete/Clear or CPU mutation
-> construct replacement logical state
-> prepare replacement snapshot
-> atomically swap public state
-> release old prepared snapshot
```

Goals5461-5462 add the generic sparse refit ABI and remove all-box Python
packing/upload for sparse updates. Cardinality-changing operations deliberately
remain rebuilds; a future capacity/inactive-slot design requires separate
evidence. Goal5463 closes the prior rollback test gap with Linux/OptiX fault
injection for both successful post-write recovery and rollback-failure handle
poisoning.

## Current Paper-App Portfolio Boundary

The five completed scoped app lines are recorded in
`Paper-reproduction-apps/paper_app_status_snapshot.json`. Their current app
status does not change RTDL ownership: app comparators, paper data identity,
tolerances, format adapters, and performance regimes stay outside core.

## Closed LibRTS Architecture

LibRTS remains an app over generic RTDL AABB/index operations:

```text
LibRTS app owns:
  author checkout/build wrapper, WKT fixtures, operation mapping, canonical
  row comparator, mutation scenarios, tolerances, phase labels, paper claims

RTDL core owns:
  generic prepared AABB index, point membership rows, range containment rows,
  AABB intersection rows, stable-ID mutable AABB lifecycle, sparse-slot OptiX
  refit for fixed-cardinality updates, atomic snapshot rebuild for cardinality
  changes, and poisoned-handle fail-closed behavior after rollback failure
```

The input ownership boundary is explicit: RTDL consumes format-neutral
columns/buffers and does not parse WKT. Paper apps, database connectors, and
user code own WKT/GeoJSON/PLY/file parsing and provenance. A future Arrow,
DLPack, CUDA-array-interface, or equivalent bridge is system work only when its
contract is format-neutral and has a non-paper-app consumer.

The partitioned-traversal reference remains deliberately narrower than the
paper name: generic primitive partitions, fanout planning, and cost selection.
Goal5470 temporarily implemented disjoint traversal layers, ray fanout, payload
filtering, exact original-ID rows, and per-ray telemetry in OptiX. Exact rows
passed, but four same-host shapes produced at most `1.009x` end-to-end versus
`k=1`; the native/public implementation was reverted. Therefore native
partitioned traversal is not part of the RTDL architecture. Reopening it
requires a changed execution model, such as device-resident downstream row
consumption, rather than more `k` tuning on the current host-materialized route.

Goal5453 deliberately reuses the existing generic AABB surface and adds no
LibRTS-named core primitive. Goal5454 confirms that the accelerated comparison
can use pinned author OptiX and public RTDL OptiX on identical files. The author
example exposes count only; RTDL exposes exact rows, so the architecture keeps
those evidence strengths separate. Embree is outside the entire campaign and
must not re-enter through historical benchmark tests.

Goal5455 applies the same separation to range-contains. The public RTDL native
route and author example both expose count; the app-owned exact oracle supplies
direction-discriminating rows. This prevents an app oracle from being mislabeled
as a system/native row capability.

Goal5456 uses the existing generic native intersection-row API, so RTDL can
prove exact native rows for range-intersects without new core work. Goals5457-
5463 preserve the distinction between mutation contracts: pure stable-ID
updates use native sparse refit, cardinality changes atomically swap rebuilt
snapshots, and failed rollback invalidates the prepared handle rather than
allowing uncertain state to remain queryable.

Goals5464-5465 apply the same app/core separation to PIP:

```text
LibRTS app:
  exact AE source pins, PIP-only build compatibility, WKT parser, discriminating
  fixture, author count parser, comparator, and claim boundary

RTDL language/system:
  generic Points/Polygons inputs, traverse, point_in_polygon refine, emit,
  run_cpu, and run_optix
```

No PIP- or LibRTS-specific core primitive was added. Ray-Multicast remains a
separate possible execution-policy audit and cannot be inferred from this PIP
gate.

Goals5466-5467 establish the representative author-compatibility shape:

```text
generic RTDL OptiX expanded-AABB point-membership candidates
-> app-owned Numba CUDA PNPOLY compatibility refine
-> canonical pair rows
```

The app adapter owns the pinned author's float32 coordinates, `(0,0)` sentinel
layout, fast-math policy, and `1e-5` conservative candidate expansion. Standard
RTDL polygon semantics remain unchanged and visibly differ by six relations on
the representative workload. Do not promote the author adapter into core.

## Historical X-HD Architecture

The X-HD app closed at same-input directed-HDResult reproduction, not exact
paper reproduction. Its strongest historical system-extraction route was the
following Level-B same-source representative pipeline.

Current route shape:

```text
public Stanford Dragon source points
public Stanford HappyBuddha target points
-> generic grid/cell descriptors
-> local-grid-cell nearest-state seed
-> generic native 3-D cell-MBR frontier rows with inline nearest payload
-> nearest continuation only if rows remain / max-nearest reduction
-> app-owned comparison against author HDResult
```

The route must preserve the author-directed Hausdorff contract proved by
Goal5126: input1-to-input2 directed HDResult, not symmetric Hausdorff.

## Current Full-Public Evidence

Goal5186:

- author `hd_exec` on full public Dragon/HappyBuddha reports
  `HDResult=0.12572988867759705`;
- it matches paper-branch author-log HDResult within `1e-6`.

Goal5187:

- RTDL all-source route over `437645 x 543652` full public points reports
  `0.12572988629271128`;
- it matches the Goal5186 author HDResult with abs diff about `2.38e-9`;
- it skips all-source exact oracle because exact pair materialization is
  infeasible at this scale.

Goal5188:

- author internal `Running.AvgTime` is about `7.603ms`;
- author process wall is about `1.97s`;
- RTDL route wall is about `7.30s`;
- RTDL total is about `10.01s`;
- no ratio is authorized because these are different phase boundaries.

## Current Bottleneck

Before Goal5189, the dominant RTDL route phase on the full-public Level-B
candidate was generic nearest-cell-MBR seed:

```text
query_count = 437645
nonempty_cell_count = 6454
cell_mbr_tests = 2824560830
initial_state_seed ~= 4.04s
```

Goal5189 adds a generic local-grid-cell seed that avoids the all-cell MBR scan.
It is a valid upper-bound seed, not a nearest tight-MBR selector.

Post-Goal5189 full-public route profile:

```text
route_wall ~= 5.98s
initial_state_seed ~= 0.90s
frontier_rows ~= 2.30s
nearest_continuation ~= 2.03s
frontier_row_count = 7590188
```

The next route work should use this new profile. Either attack the enlarged
generic frontier/continuation work, or design a tighter indexed seed that stays
much cheaper than the all-cell nearest-MBR scan while reducing frontier growth.

Goal5190 tested the tighter indexed-seed direction with a generic grid
branch-bound seed. It matched author HDResult and reduced frontier rows, but its
seed search was too expensive:

```text
grid-branch-bound route_wall ~= 7.71s
grid-branch-bound seed ~= 4.60s
grid-branch-bound frontier_rows = 1811625
```

Goal5191 then measured larger generic native inline-nearest thresholds on top
of the local-grid seed. With `max_inline_points=512`, the native inline payload
resolves all queries on the full-public Dragon/HappyBuddha Level-B route:

```text
route_wall ~= 3.65s
frontier_row_count = 0
nearest_continuation ~= 0.016s
native frontier / inline-nearest collector ~= 2.00s
local-grid seed ~= 0.88s
```

Therefore the current best route is Goal5191 local-grid plus inline-nearest
threshold 512. Future route work should not target Python continuation for this
case; it should target the generic native inline-nearest collector or the
local-grid seed, or stop route optimization and return to review/provenance.

Goal5192 instruments the native inline-nearest collector with optional
diagnostic counters. On the same full-public route, telemetry reports:

```text
inline_cell_hit_count ~= 12.0M
inline_point_evaluation_count ~= 1.24B
```

Therefore the native collector floor is doing substantial point-distance work
inside OptiX payload code. The next generic performance question is how to
reduce native inline point evaluations or make that generic native collector
faster, without introducing an X-HD-specific shortcut.

Goal5193 tested a bounded grid-cell seed and intermediate inline thresholds.
Both preserved correctness, but neither beat the current local-grid +
inline512 route. Budgeted grid-cell seed either made the seed looser and
increased native inline work, or spent too much seed time. Intermediate inline
thresholds left frontier rows and were slower. This narrows the route problem:
small seed/threshold tweaks are not enough.

Goal5194 then fixes a generic native payload-state issue in the inline-nearest
collector. The any-hit program now prunes later cells against the updated
payload current best rather than only the initial query seed. On the full-public
Level-B route this keeps the author HDResult match, drops inline point
evaluations from about `1.24B` to `0.40B`, and moves warmed route wall to about
`3.46s`.

Goal5195 moves the same current-best prune one stage earlier into the native
intersection program for inline-nearest / no-pruned-row mode. Cells whose MBR
minimum distance is strictly greater than the payload current best now return
before `optixReportIntersection`, while equal-distance cells remain reportable
for lower-id tie-breaks. On the same full-public Level-B route this keeps the
author HDResult match and moves warmed route wall to about `2.6s`, with native
frontier / inline time about `0.93-0.94s`.

Goal5196 improves the generic local-grid seed lookup. For grid volumes under a
safe cap, `seed_nearest_witness_from_local_grid_cell_numpy_columns` now uses a
dense encoded-cell -> compact-cell row lookup table instead of binary searching
`original_cell_ids` for every probed grid cell. On the same full-public Level-B
route this keeps the author HDResult match and moves route wall to about
`2.26s`, with local-grid seed time about `0.55s`.

Goal5197 carries the intersection-computed query-to-cell `min_sq` to any-hit via
OptiX attributes, so any-hit no longer recomputes that minimum distance after
the intersection program already computed it. The any-hit row path now computes
row-only min/max distances lazily only when a row is actually emitted. On the
same full-public Level-B route this keeps the author HDResult match and remains
about `2.25-2.28s`; treat it as generic cleanup / neutral optimization rather
than a new speedup headline.

Goal5198 tests whether the generic grid shape itself is the next lever. It is
not: `24^3` fails the empty-frontier route at capacity 0, while `48^3`, `64^3`,
and `128^3` all match author HDResult but are slower than `32^3`. Finer grids
reduce native inline point evaluations (`400M -> 240M -> 166M -> 64M`) but grow
seed probes and inline cell hits enough to lose wall time. Therefore simple
grid-shape tuning should not be the next route attack.

Goal5199 tests whether the generic native OptiX ray extent is the next lever by
temporarily bounding cell-MBR trace `tmax` by radius or initial current-best
distance. It is not: correctness still matches, but inline cell hits and inline
point evaluations are unchanged and route wall does not improve. The temporary
change was reverted. The remaining system problem is therefore not scalar trace
extent; it is the broader generic inline-nearest execution model / spatial
index / work ordering.

The current default route is therefore:

```text
32^3 dense-lookup local-grid-cell seed
-> native inline-nearest max_inline_points=512
-> payload-current-best pruning
-> intersection-stage current-best pruning
-> intersection attribute min_sq reuse / lazy row distance
-> packed coordinate_matrix reuse for seed/frontier front doors
-> app-owned NumPy matrix input loader for public PLY inputs
-> linear finite max-nearest reduction with tie-only lexsort
-> empty-frontier passthrough
```

Goal5200 shows that wrapping the local-grid seed in a host-to-native CUDA call
does not help unless surrounding state becomes more device-resident. Goal5201
shows prepared cell-MBR acceleration-structure build is negligible
(`~0.0004s`) and should not be the next target. Goal5202 removes repeated
coordinate repacking inside generic seed/frontier helpers with
`coordinate_matrix` / `coordinate_matrix_fields`. Goal5203 removes the app
front-door tuple-row repack by loading public PLY inputs directly into NumPy
coordinate matrices. Goal5204 removes the full-array lexsort in the generic
max-nearest reducer for finite distances while preserving tie semantics and
non-finite fallback. Goal5205 keeps the app-owned public PLY front door but
switches its high-volume matrix parser to NumPy `loadtxt` with explicit
coordinate `usecols`.

Current Level-B route-local best:

```text
route_wall ~= 1.17-1.18s
same-process warm route_wall ~= 0.61s (diagnostic only)
explicit warmup measured route_wall ~= 0.626s
explicit warmup case_total ~= 1.389s
initial_state_seed ~= 0.23s
frontier_rows ~= 0.74s
source+target columns ~= 0.001-0.002s
load_full_inputs ~= 0.681-0.682s
full gate total ~= 2.06s
max_nearest_reduction ~= 0.001s
steady optix_launch / inline scan ~= 0.37-0.38s
```

The remaining route-local floor is now primarily native inline-nearest/frontier
work plus seed/grid costs. Goal5206 shows much of the one-shot route wall is
first-use runtime overhead, but the steady native inline scan remains a real
floor. Public input loading is still user-visible but no longer larger than the
route. The next attack should either expose an explicit prepared/warm generic
runtime regime beyond the app-owned Goal5207 measurement protocol, target a
broader generic inline-nearest execution model / spatial index / work ordering,
or pause for review/provenance instead of adding app-specific shortcuts.

## Non-Negotiable Claim Boundaries

- Level B same-source evidence is not Level C exact paper dataset reproduction.
- Paper-log paths, counts, statistics, and HDResult values are not input bytes
  or hashes.
- Do not report author-vs-RTDL performance ratios without denominator review.
- Do not describe app-owned wrappers or comparators as RTDL core features.
- Do not mark implemented goals as reviewed unless an external review exists.
