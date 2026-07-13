# LibRTS Paper Reproduction App

This directory starts the RTDL reproduction project for `LibRTS: A Spatial
Indexing Library by Ray Tracing`. It is separate from the historical
LibRTS-style benchmark app: that benchmark supplied useful generic AABB assets,
but it is not retroactively treated as paper-reproduction evidence.

## Paper And Artifact

- Paper: `LibRTS: A Spatial Indexing Library by Ray Tracing`
- Venue: PPoPP 2025
- DOI: `10.1145/3710848.3710850`
- Authors: Liang Geng, Rubao Lee, Xiaodong Zhang
- Paper page: `https://gengl.me/publications/ppopp25/`
- Author repository: `https://github.com/RTSpatial/RTSpatial`
- Pinned branch/commit: `main` / `52509e8022abeab722f5a9a89d1917e8b481defe`
- Zenodo AE v2: `10.5281/zenodo.14209767`
- AE archive: `PPoPPAE-v2.tar.gz`, MD5
  `89e589f086038f1cd3af9e3ed67da8c8`, published size `23.1 GB`

The GitHub source requires Linux, CMake 3.27+, CUDA 12+, OptiX 8.0, and an
NVIDIA driver 535 or newer. Its current CMake configuration compiles for
compute capability 7.5 by default.

## Author Contract

The public author API is `rtspatial::SpatialIndex<coord_t, 2>`:

```text
Init(Config)
Insert(envelopes)
Query(Predicate::kContains, points or envelopes)
Query(Predicate::kIntersects, envelopes)
Update(id, envelope)
Delete(ids)
Clear()
```

The paper's primary library surface includes point queries, range-contains,
range-intersects, mutations, and a PIP application. The initial author example
reports load time, query time, and result count. A stronger pair-row comparator
may be added app-side later; it must not become LibRTS-specific RTDL core code.

## Existing RTDL Assets

The repository already contains:

```text
src/rtdsl/aabb_index.py
examples/current/research_benchmarks/librts_spatial_index/
```

Reusable generic system APIs include:

```text
prepare_aabb_index_2d
query_aabb_index_2d
expanded_aabb_point_membership_rows_2d
aabb_intersection_pair_rows_2d
```

CPU reference, OptiX, Embree, and HIPRT support exist historically for
different subsets of the count/row contract. This paper-app campaign uses only
the CPU reference for local semantic checks and OptiX for accelerated POD
gates. Embree is explicitly out of scope for the entire LibRTS campaign, and
HIPRT is not an active comparison route.

## App-Owned Code

This paper app owns:

- author checkout/build and compatibility patches;
- WKT fixture and paper-dataset provenance;
- mapping author result IDs to canonical relation rows;
- Insert/Delete/Update workload policy;
- paper figure selection and performance regimes;
- comparison reports and claim boundaries.

## Reproduction Scope

Current status:

```text
bounded_project_closeout_ready__official_archive_verified__generic_columnar_aabb__exact_point_contains_and_range_contains_count_lines_closed__range_intersects_partial_with_diagnostic__full_paper_not_reproduced
```

The current project boundary is a bounded closeout, not a full paper
reproduction. Official archive provenance is verified. Exact point-contains
and range-contains count lines are recorded, and the range-intersects campaign
records three full-input count matches, two unresolved count disagreements,
and one author-side CUDA allocation failure. Goal5501 adds an independent CPU
float32 prefix diagnostic and closes the current engineering line at that
evidence boundary. Any attempt to recover all range-intersects pairs, author
pair rows, or the failed full `parks.bz2` case is a new scope.

Goal5453 provides a deterministic tiny WKT point-contains fixture. Goal5454
runs the same box and point files through the pinned author RTSpatial/OptiX
example and RTDL OptiX on local Linux. Both report five results. RTDL also emits
the exact expected `(query_id, indexed_box_id)` rows:

```text
(0, 0)
(1, 0)
(1, 1)
(2, 1)
(3, 2)
```

The author example exposes only a result count, not pair rows. Therefore the
closed bounded claim is same-input result-count agreement plus RTDL exact-row
agreement with the deterministic fixture. Author pair-relation agreement is
not claimed.

Goal5455 adds a direction-discriminating range-contains fixture. Correct
`indexed_box_contains_query_box` semantics produce five results; the reversed
direction produces two. Pinned author RTSpatial/OptiX and RTDL OptiX both report
five, and the RTDL-side exact fixture oracle records the five expected rows.

Goal5456 runs `range_intersects` on the same box-query fixture. Intersects has
eight matches while contains has five, so predicate confusion cannot pass. The
author example and RTDL OptiX both report eight; RTDL's generic native
intersection-row API also emits all eight expected rows.

Goals5457-5460 add the mutation line. The audit found that the author performs
native incremental GAS/IAS updates while existing RTDL prepared AABB handles
were immutable. RTDL now exposes an app-neutral `MutableAabbIndex2D` contract
with stable IDs and atomic prepared-snapshot rebuilds. A non-LibRTS dynamic
obstacle test proves generic reuse. On local Linux, the author public API and
RTDL OptiX run the same insert/query/update/query/delete/query/insert/query/
clear/query sequence and both produce counts:

```text
[2, 1, 0, 1, 0]
```

Both assign the final inserted geometry ID `2`. This closes bounded mutation
semantics and result-count agreement only. The execution models remain
different: author native incremental update versus RTDL atomic snapshot
rebuild.

Goals5461-5462 then improve the generic system implementation. Pure OptiX
Update now uses a rollback-protected native sparse-slot GAS refit; Insert,
Delete, and Clear remain atomic snapshot rebuilds. The same LibRTS sequence
still produces `[2,1,0,1,0]`. A same-host generic RTDL microbenchmark measures
about `12.6x` (4,096 boxes) and `15.6x` (65,536 boxes) versus RTDL rebuilding
the full snapshot. These are system refit-vs-rebuild diagnostics, not LibRTS
paper or author-performance results.

Goals5464-5465 add the first bounded PIP gate. The app uses the exact AE PIP
sources pinned through `RTSpatial/PPoPPAE` and an app-owned build wrapper that
excludes unrelated benchmark dependencies. The same three polygon and five
point files are passed to the author PIP binary and this RTDL program:

```python
points = rt.input("points", rt.Points, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
candidates = rt.traverse(points, polygons, accel="bvh")
hits = rt.refine(
    candidates,
    predicate=rt.point_in_polygon(
        exact=False,
        boundary_mode="inclusive",
        result_mode="positive_hits",
    ),
)
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

Both author and RTDL OptiX report four hits. RTDL also emits the four expected
rows `(0,0)`, `(0,2)`, `(2,1)`, `(4,0)`. A deliberately placed point lies
inside the triangle's MBR but outside the triangle, so an MBR-only route would
report five candidates and cannot pass this gate. The author binary reports
count only; author pair-row equality is therefore not claimed. This tiny gate
is not Figure 12, Ray-Multicast, a paper performance result, or a full paper
reproduction.

Goals5466-5467 raise PIP to a representative Level-B workload. The committed
input is a provenance-recorded subset of the public USA Census Block Groups
ArcGIS service: the first 64 source-order, single-ring, no-hole polygons
(`30,635` vertices). It is the same dataset family named by the author PIP
script, but it is not the author's exact WKT file. The pinned author
`GeneratePointQueries` implementation produces 100,000 points with seed `0`,
matching the paper query cardinality.

The larger gate exposed a real semantic boundary:

```text
unmodified author result count       71,626
standard RTDL point_in_polygon       71,624
app-compatible RTDL/Numba route      71,626
```

The standard route differs on six relations because the author stores
float32 polygon rows with `(0,0)` sentinels and compiles PNPOLY with CUDA fast
math. RTDL core was not changed to imitate this artifact detail. Instead, the
paper app composes the existing generic
`expanded_aabb_point_membership_rows_2d` OptiX candidate API with an app-owned
Numba CUDA compatibility refine. A separate comparator-only author build copies
the already collected result queue without changing the predicate or append
logic. The unmodified and instrumented author binaries both report `71,626`,
and all `71,626` author/RTDL pair rows match exactly with canonical SHA-256:

```text
7d30e35b6f50742aa69b047980a1f5dc7b0d586ce379c83848a4803c17a26c7b
```

This closes Level-B representative same-input relation agreement only. It does
not make the compatibility PNPOLY layout a generic RTDL primitive, and it is
not exact paper data, Figure 12, Ray-Multicast, or a performance result.

## Ray-Multicast Feasibility And Generic Contract

Goals5468-5469 pin Section 3.4, Figure 5, Equations 3-5, and the corresponding
author source at `RTSpatial@7c54c181`. The audit shows that Ray-Multicast is not
ordinary batching: it assigns traversal primitives to disjoint layers,
duplicates every original ray across those layers, filters hits by payload
partition, and selects a power-of-two fanout from sampled selectivity.

RTDL already had prepared AABB indexes, prepared query GAS, two-pass
Range-Intersects rows, and multi-stream query execution. It did not have
partition-layer encoding, per-ray fanout, layer-aware payload filtering, or
per-ray load telemetry.

Goal5469 adds an app-neutral Python reference contract:

```python
partitioned_traversal_fanout_plan(...)
estimate_partitioned_traversal_selectivity(...)
select_partitioned_traversal_fanout(...)
```

A Contact-Manifold-style broad-phase test is the required non-LibRTS consumer.
It proves exact pair coverage while reducing the static maximum primitive load
from `N` to `ceil(N/k)`. This authorizes a bounded native OptiX POD spike after
strict review. It does not prove a native backend, author equivalence, runtime
speedup, Figure 9, or full paper reproduction.

Goal5470 exercised that bounded native spike on a local GTX 1070. The temporary
layered traversal preserved exact rows and reduced maximum backward-ray work,
but four workload shapes produced only `1.000x` to `1.009x` best end-to-end
movement versus `k=1`, below the predeclared `1.02x` gate. The native/public
prototype was therefore reverted. RTDL retains the Goal5469 reference/planning
contract, not a native partitioned-traversal API. Repeating `k` tuning on the
same host-materialized canonical-row route requires a changed execution model.

Goals5471-5472 then audit the official PPoPPAE repository without downloading
the 23.1 GB dataset bundle. The pinned AE checkout contains 264 author/baseline
logs covering final-paper Figures 6-12, but no exact inputs. The audit records
the non-mechanical mapping from final-paper figure numbers to AE output files
and the distinct timing denominator for every target. Author logs are reference
targets only; no RTDL figure or performance ratio is claimed. The next step is
dataset access/size resolution, not another kernel optimization or POD run.

Goal5473 resolves that acquisition decision without downloading the archive.
Zenodo exposes the `PPoPPAE-v2.tar.gz` bundle at 23,062,425,365 bytes with the
published MD5 recorded in the manifest. The current local Linux host has enough
disk but only 8 GiB VRAM, about 16 GiB RAM, and a measured download estimate of
about 12.1 hours, so it is not an appropriate exact-matrix execution host. The
download is deferred to Linux with at least 64 GiB RAM and 70 GiB free disk;
24 GiB VRAM remains a separate conservative paper-execution gate. The three
author SharePoint URLs currently return 401, but this is not treated as proof
that they are permanently unavailable.

Goal5474 implements the corresponding app-owned resume-safe acquisition gate.
It writes to a `.part` file, resumes with curl, and promotes the archive only
after exact size and MD5 verification. The committed artifact is a blocked
plan from the current host: no download was executed and extraction remains a
separate future gate.

Goal5475 implements that separate safe extraction/inventory contract. It
rejects unsafe tar members and duplicate paths, inventories expanded bytes,
extracts only into a staging directory, and promotes only after complete
file/byte accounting. The real archive is absent, so the committed result is a
contract plan rather than extraction or exact-input evidence.

Goal5476 applies the split resource gate on an RTX 4000 Ada POD. Its Linux,
disk, and RAM satisfy acquisition, while 20,475 MiB VRAM remains below the
conservative 24 GiB complete-matrix gate. The resumable download is launched;
the committed plan does not claim transfer completion or archive verification.

Goal5477 builds the pinned author RTSpatial, `query`, and `pip` GPU paths on
that POD. Tiny author smoke counts remain `5` and `4`, proving the executables
run on Ada. Ubuntu-24 compatibility uses the author's pinned GEOS 3.11 with
GCC12; no author algorithm source or Embree path is introduced. Exact data and
complete-matrix capacity remain pending.

Goal5478 prepares, but does not execute, the first exact-input gate: Figure-6
`dtl_cnty` point-contains. It requires verified archive/extraction evidence,
feeds identical WKT bytes to author and RTDL, and compares count only because
the standard author binary exposes no pair rows. Timing phases stay separate
and no performance ratio is authorized.

Goal5479 completes official archive acquisition and safe inventory. Exact size
and published MD5 match; the archive contains 1,694 members and 88.23GB of
regular-file payload under one `PPoPPAE` top-level entry. Three safe relative
symlinks are accepted under the amended in-root policy. At the end of Goal5479,
extraction and individual exact-input identification were still pending; the
later Goals5480 and 5482 perform quota-safe selected-member extraction.

Goal5480 records the POD quota boundary and safely extracts only the two exact
members needed by the first paper workload. The verified archive remains bound
to MD5 `89e589f086038f1cd3af9e3ed67da8c8`; the extracted files are
`dtl_cnty.wkt` (363,987,023 bytes, SHA-256 `9177fdff...c7973f`) and its 100K
point-query file (3,976,199 bytes, SHA-256 `95241f4e...fe39d3`). This is an
atomic, evidence-bound subset extraction, not a claim that all 88.23GB are
simultaneously expanded.

Goal5481 executes the first exact official-input gate on the RTX 4000 Ada POD.
The author loader expands 3,143 WKT rows into 12,234 polygon index records;
RTDL mirrors that public WKT ingestion contract and uses the generic
`expanded_aabb_point_membership_rows_2d` OptiX API. Both implementations report
exactly 136,475 point-contains results for the same 100,000 query file. This
closes one exact-input correctness row; Figure 6, pair-row equality, and any
author-vs-RTDL performance ratio remain unclaimed.

Goals5482-5483 extend the exact archive gate to the five remaining Figure-6
point-contains pairs. The verified subset extraction records the selected
member paths, byte sizes, and SHA-256 values before either implementation is
run. On the RTX 4000 Ada POD, author and RTDL count results match on all five:

```text
USACensusBlockGroupBoundaries = 148,970
USADetailedWaterBodies        = 118,622
parks_Europe                  = 109,279
lakes.bz2                     = 103,189
parks.bz2                     = 112,729
```

Together with Goal5481's `dtl_cnty = 136,475`, this is a six-of-six exact
official-input Figure-6 point-contains **count** matrix. It is not a claim
that Figure 6 has been reproduced: the author query binary exposes counts but
not pair rows, and the figure's complete timing/plot denominator has not been
reconstructed. These are count-level matches only: equal totals do not prove
that the same individual query points were assigned to the same polygons. The
`parks.bz2` case uses the generic public count-only route
`query_aabb_index_2d(operation="point_contains")`; the earlier row-producing
route created avoidable cleanup pressure on this largest input. The batch
runner now defaults all cases to count-only execution. No performance ratio,
complete-paper claim, or Embree comparison is authorized.

Goal5484 then audits the six exact cases against the author paper-branch
`Figure 6 / RTSpatial / point-contains_queries_100000` records. Geometry count,
query count, and result count align for all six. The author metric is internal
Query Time with Loading Time excluded; RTDL route wall is not denominator
aligned, so the audit explicitly keeps performance-ratio authorization closed.
The separate Goal5467 representative PIP gate proves `71,626` pair rows with a
canonical hash; it is relation-level evidence for that different workload, not
pair-row evidence for these six exact Figure-6 point-contains cases. Raw RTDL
route wall is seconds while the author's internal query metric is sub-
millisecond, but the unlike phase boundaries forbid a ratio claim.

Goal5485 then ran the prepared-index phase gate on the same RTX 4000 Ada POD.
The official archive was verified by size and MD5, and the selected `dtl_cnty`
geometry/query files were passed unchanged to the pinned author binary and the
generic RTDL prepared-index API. Both returned `136,475` results. The phase
evidence is:

```text
author internal Query Time       0.0688 ms
RTDL WKT load                    28.5173 s
RTDL index preparation            1.1200 s
RTDL prepared query wall          0.3763 s
RTDL native primitive query       0.2162 s
```

The result separates preparation from query execution, but it does not authorize
a performance ratio: the author metric is an internal query metric, while the
RTDL value is prepared-query wall time from a different execution model. The
gate is exact-input count evidence plus a phase-boundary measurement candidate,
not Figure-6 reproduction, pair-row equality, or paper-performance evidence.

Goal5486 extends this prepared-index measurement to all six exact archive
member pairs on the same RTX 4000 Ada POD. The pinned author query and the
generic RTDL prepared API match all six integer counts:

```text
case                             author count  RTDL prepared query wall
dtl_cnty                              136,475                  0.376076 s
USACensusBlockGroupBoundaries         148,970                  0.189807 s
USADetailedWaterBodies                118,622                  0.299463 s
parks_Europe                          109,279                  0.226963 s
lakes.bz2                             103,189                  0.178843 s
parks.bz2                             112,729                  0.408325 s
```

The full matrix is in
`results/librts_goal5486_prepared_phase_batch.json`, with per-case input
hashes and separate WKT load, index preparation, prepared query, and native
primitive fields. The two largest inputs make the current front-door cost
visible: WKT/MBR loading is `404.471s` for `lakes.bz2` and `553.019s` for
`parks.bz2`, while index preparation is `66.311s` and `85.547s` respectively.
These are app-side input/preparation measurements, not an RT-core performance
claim.

Goal5486 is still count-level evidence. Equal counts do not establish equal
point-to-polygon relations, and the author binary does not expose pair rows for
this operation. The prepared-query values are a phase-boundary candidate only;
no author-vs-RTDL ratio, Figure-6 reproduction, full-paper claim, or Embree
comparison is authorized.

Goal5487 adds the generic host-column AABB front door
`prepare_aabb_index_2d_columns` and its `Aabb2DColumns` contract. A tiny POD
gate ran the columnar and existing row-shaped OptiX paths on the same boxes and
points: both returned `point_contains=2` and both reported RT-core
acceleration. This is a system/API behavior gate only. The structured NumPy
buffer is a host ABI view; it is not device zero-copy, and no LibRTS speedup or
paper-performance claim is made.

Goal5488 wires that generic front door into the app-owned prepared-phase gate
for exact `dtl_cnty` and `lakes.bz2`. Counts remain exact (`136,475` and
`103,189`). On `lakes.bz2`, the measured prepare phase moved from `66.311s`
with the old row/ctypes path to `0.856s` with the columnar path, while WKT
load stayed about `405s`. This is evidence of removed host packing work, not an
end-to-end speedup claim; the new single-run query phase includes uncontrolled
first-use state and is not used for a ratio.

Goal5489 repeats the exact `dtl_cnty` query three times on one prepared
columnar index in one POD process. All three counts remain `136,475`; route
wall is `0.369s`, `0.220s`, `0.218s`, and primitive query phase is `0.202s`,
`0.070s`, `0.069s`. This is first-use/reuse diagnostic evidence only. It is
not a Figure-6 reproduction, pointwise relation proof, author-performance
ratio, device-zero-copy claim, full-paper claim, or Embree comparison.

The same repeat protocol also ran on `lakes.bz2` (8,327,448 geometries): all
three counts were `103,189`, route wall was `0.598s`, `0.222s`, `0.220s`, and
primitive phase was `0.447s`, `0.072s`, `0.072s`. Its WKT load was `406.570s`.
This reinforces the phase boundary; it is not an end-to-end or author-ratio
claim.

Goal5490 probed an app-owned NumPy numeric WKT loader on exact `dtl_cnty`.
The count stayed `136,475`, but load was `28.069s` versus the Goal5489 regex
run's `27.994s` in separate POD runs. No material improvement was demonstrated,
so the numeric variant remains experimental and WKT stays out of RTDL core.

Goal5491 adds an app-owned exact AABB column cache bound to the source WKT
SHA-256. On `lakes.bz2`, the reusable cache is `286MB`; source-hash validation
plus cache load is `8.101s`, index preparation is `0.840s`, and the three
query walls are `0.350s`, `0.216s`, `0.218s`, all matching count `103,189`.
The original WKT parse was `406.570s`; cache construction is a separate
one-time phase, so this is reusable-ingestion evidence, not end-to-end or
author-ratio performance.

## Performance Scope

No paper-app performance result exists yet. Future measurements must separate:

```text
author build and process startup;
author index build / Insert;
author query phase;
RTDL process startup and backend initialization;
RTDL prepare/index build;
RTDL query and row materialization;
mutation/update cost.
```

Historical RTDL LibRTS-style benchmark numbers must not be promoted into this
paper app without a same-input, same-operation, same-hardware denominator.

Backend policy for this campaign:

```text
local correctness = RTDL CPU reference
accelerated reproduction = author RTSpatial/OptiX vs RTDL OptiX
Embree = excluded
HIPRT = inactive
```

## Boundary

Not claimed:

- author pair-relation agreement outside the app-instrumented Goal5467
  representative fixture;
- full LibRTS reproduction;
- native-incremental Insert/Delete/Clear or author mutation performance parity;
- paper dataset or figure reproduction;
- exact dataset acquisition on the current local Linux host;
- Ray Multicast or author load-balancing equivalence;
- native partitioned-traversal backend completion or runtime benefit;
- author PIP pair-row agreement outside Goal5467 or Figure 12 performance;
- whole-program speedup or author-performance parity;
- a new LibRTS-specific RTDL primitive.
- Embree comparison or Embree-derived performance evidence.

## Local Command

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/librts-paper/librts_reproduction.py \
  --mode local-point-contains \
  --output Paper-reproduction-apps/librts-paper/results/tiny_point_contains_rtdl_reference.json
```

The Linux same-input gate is implemented by
`run_same_input_point_contains_gate.py`. It requires the pinned author checkout,
the author executable, and `RTDL_OPTIX_LIB`. The committed Goal5454 result is
functional evidence from `lx1`; its author timing fields are diagnostic only.
The corresponding range-contains gate is
`run_same_input_range_contains_gate.py`; Goal5455 has the same evidence boundary.
Goal5456 uses `run_same_input_range_intersects_gate.py` and additionally checks
the generic RTDL native row contract.
Goal5460 uses `run_same_input_mutation_gate.py`; its app-owned author probe calls
the pinned public `SpatialIndex` mutation API, and the combined gate compares
the exact mutation count sequence while recording the execution-model
difference.
Goal5465 uses `run_same_input_pip_gate.py`; its pinned AE author build wrapper
and compatibility shim are documented under `author_patches/`. The committed
Linux result is functional evidence only and does not authorize a timing ratio.
Goal5467 uses `run_same_input_representative_pip_gate.py`. Its exact relation
comparison is app-instrumented and explicitly preserves the standard RTDL PIP
route's six-row difference in a separate diagnostic artifact.

Goals5492-5495 extend and close the current exact AABB operation line. The
verified official archive contains `14` exact point-contains pairs, `14` exact
range-contains pairs, and `42` exact range-intersects pairs. It contains no
exact PIP or mutation pairs, so those operations remain fail-closed for this
archive rather than being replaced with invented inputs.

Goal5493 runs one exact `dtl_cnty` range-contains pair through the pinned author
binary and the generic RTDL columnar front door. Both return count `117314` on
the same hashed geometry/query files. The evidence is count-level agreement;
it does not establish pointwise relation equality or a performance ratio.

Goal5494 keeps the reusable `.npz`/JSON cache app-owned. No RTDL cache lifecycle
API is promoted because the cache currently has only a LibRTS consumer and
also encodes WKT-specific parsing and provenance policy. A future promotion
requires a second non-LibRTS consumer and a generic lifecycle contract.

Goal5495 closes the current exact point/range-contains AABB line and queues
exact range-intersects as the next operation. These goals are implemented and
recorded, but remain external-review pending. They do not claim Figure 6,
full-paper reproduction, pointwise relation equivalence, author performance
parity, device zero-copy, or Embree evidence.

Goal5496 executes the next exact archive operation on `dtl_cnty` with a
10,000-query `range-intersects` member. Author and RTDL both return count
`1,570,285` on the same hashed files. The author gate uses `load_factor=1`
because the otherwise identical `0.0001` configuration fails on this POD with
CUDA `invalid program counter`; the working configuration is recorded, not
silently substituted. RTDL phases remain separate and no ratio is authorized.
Goal5496 is implemented and external-review pending.

Goal5497 extends the exact range-intersects evidence with a second official
query member for the same `dtl_cnty` geometry. The two author/RTDL counts are
`1,570,285` and `242,920`. The geometry SHA is identical across both cases;
the query SHAs are distinct. This is a two-case count matrix, still with no
pointwise relation, performance, Figure 6, full-paper, zero-copy, or Embree
claim. Goal5497 is implemented and external-review pending.

Goal5498 closes this bounded two-case range-intersects line. The archive still
has `40` exact range-intersects pairs not executed by this line; they remain a
separate queue, not implicit coverage. PIP and mutation remain blocked because
the verified archive has no exact pairs for them. The closeout is implemented
and external-review pending, with all Figure 6, full-paper, relation-level,
performance, zero-copy, and Embree claims closed.

Goal5499 adds a third exact range-intersects query member for the same
`dtl_cnty` geometry. The three author/RTDL count matches are `1,570,285`,
`242,920`, and `239,884`; the query hashes are distinct. This remains a
three-case, one-geometry count matrix, not complete range-intersects coverage,
relation equality, performance parity, Figure 6, full-paper, zero-copy, or
Embree evidence. Goal5499 is implemented and external-review pending.

Goal5500 attempts one official `range-intersects_select_0.01_queries_10000`
pair for each of six archive geometries: `parks_Europe`, `parks.bz2`,
`dtl_cnty`, `lakes.bz2`, `USACensusBlockGroupBoundaries`, and
`USADetailedWaterBodies`. All twelve members are selected from the verified
archive with per-member SHA-256 evidence and passed unchanged to author and
RTDL. The result is deliberately bounded: three count matches, two same-input
count disagreements requiring diagnosis, and one author CUDA allocation
failure (`parks.bz2`). It is not a complete matrix, relation equality, Figure
6, performance, full-paper, zero-copy, or Embree claim. Goal5500 is
implemented and external-review pending.

## Goal5501 LibRTS bounded project closeout

Goal5501 diagnoses the two Goal5500 full-input count disagreements with
same-source prefixes and an independent CPU AABB oracle. On the feasible
100,000-geometry prefixes, RTDL matches the CPU float32 oracle for
`parks_Europe`, `lakes.bz2`, and a `parks.bz2` capacity probe. The author
matches the `lakes.bz2` prefix, but differs from RTDL by five and four counts
on the two parks prefixes. The float64 oracle and indexed-box padding variant
are recorded separately; neither identifies a proven full-input root cause.

The full `parks.bz2` author run remains a CUDA allocation failure. The prefix
probe does not resolve that capacity boundary. The final claim is limited to
verified archive provenance, bounded count evidence, and a generic diagnostic
result. It does not claim a complete range-intersects matrix, pointwise
relation equality, Figure 6, full-paper reproduction, author performance
parity, device zero-copy, or Embree comparison. Further mismatch, pair-row,
or capacity work is a new explicitly authorized scope.

## Goal5502 Author-validity decision gate

Goal5502 applies an app-owned three-way decision to the Goal5501 prefixes using
an independent inclusive float32 AABB contract. RTDL matches that contract on
all five prefixes. The author matches on one prefix, but diverges on four
prefixes across the two parks families. This author divergence is not
called a proven full-input author bug; it is sufficient to reject copying the
divergence into RTDL core.

The gate therefore authorizes no RTDL semantic change and no author-specific
core behavior. If future full-input evidence shows the author matches the
independent contract while RTDL diverges, RTDL must be fixed before claiming
reproduction. Across the five current prefixes, RTDL matches the contract on
all five; the author matches on one and diverges on four. If RTDL matches and
the author diverges, the author mismatch can be ignored for generic RTDL
correctness and recorded as an author contract or implementation divergence.
The gate remains prefix-only and does not close full-input adjudication.

## Goal5503 Author GPU Contract Audit

Goal5503 audited the pinned author source rather than treating the Goal5502
CPU oracle as the author's ground truth. The benchmark uses `float32` coordinate
storage and direct float-to-`OptixAabb` conversion. Its CPU envelope helper is
inclusive, but the actual range-intersects GPU shader uses
`RayParams<float, 2>::IsHit`: a PBRT-style slab interval with
`t0=0`, `t1=nextafterf(1.0, FLT_MAX)`, and `tFar *= 1 + 2 * FLT_GAMMA(3)`,
applied first to the query diagonal and then to the reverse envelope diagonal.

This distinction is material. The independent CPU `inclusive_aabb_intersects`
oracle remains a named contract, but CPU-oracle agreement is not proof that the
oracle and the author's GPU predicate are equivalent on boundary-sensitive
inputs. Goal5503 therefore authorizes no RTDL semantic change, no
author-specific behavior, no full-input validity claim, and no performance
ratio. Goal5504 must provide discriminating fixtures before any full-input
campaign or RTDL change is considered. Embree remains out of scope.

## Goal5504 Contract-Divergence Fixtures

Goal5504 runs five deterministic float32 fixtures through an app-owned CPU
inclusive AABB predicate and a source-driven emulation of the author's GPU
`RayParams<float,2>::IsHit` forward plus backward path. One case discriminates:
the one-ULP gap is accepted by the source model because of the source's
`tFar` expansion, while the direct CPU inclusive predicate rejects it. This is
a contract warning, not a runtime result.

The result does not select a winner, authorize an RTDL semantic change, or
close the full-input count disagreements. Goal5505 then executes the same
cases on the POD author binary and RTDL, rather than treating the emulation as
ground truth. Full-input, performance, paper, zero-copy, and Embree claims
remain closed.

## Goal5505 POD runtime gate and Goal5507 generic correction

In committed WKT order, the pre-fix Goal5505 runtime counts were author
`[1,1,1,1,1]` and RTDL `[1,1,1,1,0]`; the source model matched the author.
The mismatch is `one_ulp_gap_after_box_max`. Goal5507 then corrected the
generic native float32 interval and two-direction acceptance rule. A clean POD
build matches author counts and rows on both the five-query fixture and the
8,192-pair Goal5506 probe, without LibRTS-specific names or behavior in core.
This is bounded generic correctness evidence, not full-input adjudication or
paper-performance evidence.

## Goal5506 Scalable Contract Probe

Goal5506 scales the runtime check to 128 boxes, 64 queries, and 8,192 pairs
with deterministic seed 5506, including exact, edge, ULP-gap, and corner
cases. The counts are CPU inclusive 20, source RayParams model 21, author
GPU 21, and the pre-fix RTDL OptiX result was 20. Goal5507's clean patched
build raises RTDL to 21 with 21 unique rows, matching author/source on this
probe. This remains a bounded generic correction, not a full archive
adjudication; no paper figure, full-paper, relation-level official archive,
or performance ratio is authorized.

## Goal5506 Scalable Contract Probe

Goal5506 scales the runtime check to 128 boxes, 64 queries, and 8,192 pairs
with deterministic seed 5506, including exact, edge, ULP-gap, and corner
cases. The counts are CPU inclusive 20, source RayParams model 21, author
GPU 21, and RTDL OptiX 20. The source model matches the author and RTDL
matches the independent CPU contract. This is a scalable bounded probe, not a
full archive adjudication; no RTDL core change or performance ratio is
authorized.

## Goal5508 Float32-degenerate indexed AABB fix

Goal5508 explains and fixes the two previously disagreeing official prefixes.
The author and RTDL parsers produced identical float32 MBR fingerprints. Four
indexed geometries in each prefix become zero-width or zero-height after the
author's float32 conversion. The author skips these invalid envelopes through
its strict `IsValid()` path; RTDL's generic native padding had allowed them to
remain traversable.

The generic OptiX intersection kernel now rejects indexed records that are not
strictly valid after float32 packing, selecting the correct indexed record in
both forward and backward passes. The isolated invalid subsets return `0` for
both author and RTDL. The full prefixes now match exactly:

```text
parks_Europe: author 34,240,217 == RTDL 34,240,217
lakes_bz2:    author 34,581,812 == RTDL 34,581,812
```

This is a generic native semantic correction, not a complete archive matrix,
pair-row proof, paper reproduction, performance ratio, author-specific core
behavior, or Embree result. The machine-readable gate and hashes are in
`results/goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json`.

## Goal5509 next exact range-intersects batch

Goal5509 reuses the verified Goal5500 geometry members and runs a second exact
query family, `range-intersects_select_0.0001_queries_10000`, through the same
author binary and generic RTDL OptiX columnar front door. Four checkpointed
cases match at count level:

```text
parks_Europe:                   2,486,816 == 2,486,816
dtl_cnty:                         242,920 ==   242,920
USACensusBlockGroupBoundaries:    423,893 ==   423,893
USADetailedWaterBodies:           651,647 ==   651,647
```

The `parks.bz2` and `lakes.bz2` cases were attempted in the large batch but did
not receive independent checkpoints before the POD process was reclaimed;
they remain unresolved capacity/process-lifetime cases, not semantic
mismatches. This is four new exact count matches, not a complete 42-pair
matrix, pointwise relation equality, Figure 6 reproduction, performance ratio,
full-paper reproduction, zero-copy, or Embree evidence.

## Goal5511 additional exact query family

Goal5511 independently checkpoints four cases from the verified archive using
the second query family `range-intersects_select_0.001_queries_10000`:

```text
parks_Europe:                   23,962,096 == 23,962,096
dtl_cnty:                          239,884 ==    239,884
USACensusBlockGroupBoundaries:   3,478,660 ==  3,478,660
USADetailedWaterBodies:           6,436,810 ==  6,436,810
```

Each case has its own author/RTDL JSON checkpoint, uses the same extracted
geometry and query files on both sides, and carries the verified archive
SHA-256 records. The evidence remains count-level only: the standard author
binary does not expose pair rows for this operation. It is a bounded query
family result, not a complete 42-pair matrix, Figure 6 reproduction,
pointwise relation proof, performance ratio, full-paper reproduction,
zero-copy, author parity, or Embree evidence.

## Goal5512 large-case capacity resolution

Goal5512 reran the two large `.0001` cases independently. `lakes.bz2`
completed and matched the author count:

```text
lakes_bz2: 10,579,596 == 10,579,596
```

`parks.bz2` failed in the pinned author CUDA path with
`cudaErrorMemoryAllocation` / Thrust `bad_alloc`; RTDL was not run after the
author failed. A separate capacity audit showed ample host memory, so this is
recorded as an author workload allocation boundary, not a semantic mismatch.
The lakes retry used a temporary serialize directory after the workspace
quota path produced an output-stream error. This resolves the two Goal5509
process states, but does not complete the 42-pair matrix or authorize
pairwise, Figure 6, performance, full-paper, zero-copy, author-parity, or
Embree claims.

## Goal5513 additional exact query family

Goal5513 independently checkpoints four cases from the verified archive using
`range-intersects_select_0.01_queries_10000`:

```text
parks_Europe:                   216,977,211 == 216,977,211
dtl_cnty:                         1,570,285 ==   1,570,285
USACensusBlockGroupBoundaries:   33,404,355 ==  33,404,355
USADetailedWaterBodies:           55,205,607 ==  55,205,607
```

Each case has an independent checkpoint and the same extracted geometry/query
files are passed to author and RTDL. The result remains count-level only and
does not claim the complete 42-pair matrix, pairwise relation equality,
Figure 6, performance parity, full-paper reproduction, zero-copy, author
parity, or Embree evidence.

## Goal5514 six-geometry `.01` resolution

Goal5514 resolves the last two members of the
`range-intersects_select_0.01_queries_10000` family:

```text
lakes_bz2: 1,113,229,623 == 1,113,229,623
parks_bz2: author CUDA bad_alloc; RTDL not run after author failure
```

Together with Goal5513, this is five exact same-input count matches plus one
explicit author capacity boundary across all six geometry members. It is not
the complete 42-pair archive matrix, pairwise relation proof, Figure 6,
performance parity, full-paper reproduction, zero-copy, author parity, or
Embree evidence.

## Goal5515 historical mismatch resolution

Goal5515 rechecks the two old `.01 x 10000` count disagreements recorded by
Goal5500 after the generic indexed-AABB validity correction. On the same
official files, the previous RTDL deltas `+3,791` for `parks_Europe` and
`+54,695` for `lakes.bz2` are now both zero. The current six-state family is
therefore five count matches plus the explicit `parks.bz2` author CUDA
capacity boundary.

This closes the observed mismatch at the evidence level; it does not claim a
universal root cause for every future range-intersects discrepancy. The full
42-pair matrix, pairwise relation equality, Figure 6, performance ratio,
full-paper reproduction, zero-copy, author parity, and Embree evidence remain
closed. See `results/goal5515_range_intersects_select001_correction_gate.json`.

## Goal5516 exact range-intersects coverage ledger

Goal5516 reconciles all 42 exact range-intersects inventory pairs with
checkpointed evidence: 14 exact same-input count matches, 2 explicit author
CUDA capacity failures, and 26 pairs that remain uncheckpointed. The last
category is intentionally not treated as a mismatch or a match. See
`results/goal5516_range_intersects_coverage_ledger.json`.

## Goal5517 exact range-contains batch

Goal5517 extracts four official `range-contains_queries_100000` pairs and
independently checkpoints exact author/RTDL count matches: parks_Europe
`104,426`, dtl_cnty `117,314`, BlockGroups `120,457`, and WaterBodies
`112,637`. The `/workspace` extraction first hit the POD user quota, so the
verified members were atomically extracted under `/tmp`; hashes and execution
inputs are unchanged. This is count-level evidence, not relation equality, a
complete 14-pair matrix, Figure 6, performance parity, full-paper, zero-copy,
author-parity, or Embree evidence.

## Goal5518 range-contains coverage ledger

Goal5518 reconciles the 14 exact archive range-contains pairs before further
execution: four `100000` cases are matched and ten pairs are not yet
checkpointed. Missing checkpoints are neither matches nor mismatches. The
remaining set consists of parks_Europe and parks.bz2 cardinality variants plus
the large lakes.bz2 case.

## Goal5519 operation-scoped AABB validity correction

The exact `lakes.bz2 range-contains_queries_100000` run exposed an RTDL
regression: author `101,418`, RTDL `101,339`. The `79`-row delta is fully
accounted for by two indexed AABBs that are valid in float64 but collapse in
float32. Goal5508 had applied the strict indexed-box validity guard to every
AABB operation even though the author contains shader uses the inclusive
contains predicate without the intersection shader's `IsValid()` guard.

The generic fix scopes strict packed-box validity to `range_intersects`.
`point_contains` and `range_contains` retain inclusive exact predicates after
numeric packing. The corrected exact lakes count is `101,418 == 101,418`; the
existing lakes range-intersects prefix remains `34,581,812` and its degenerate
subset remains zero. This is a generic operation-contract fix and one exact
count result, not relation equality, a complete range-contains matrix,
performance, Figure 6, full-paper, zero-copy, author parity, or Embree evidence.

## Goal5520 parks_Europe range-contains cardinality matrix

All five exact parks_Europe range-contains cardinalities now match author and
RTDL counts: 50K `52,245`, 100K `104,426`, 200K `208,918`, 400K `417,968`,
and 800K `835,864`. Four new distinct query files ran against one prepared
RTDL base; the 100K row remains the independent Goal5517 checkpoint. The
matrix therefore contains no same-input replay. Exact range-contains coverage
is now 9/14, with the five parks.bz2 cardinalities remaining. Count-level,
performance, figure, full-paper, zero-copy, author-parity, and Embree limits
remain unchanged.

## Goal5521 parks.bz2 range-contains cardinality matrix

The smallest 50K author run completed before the pipeline authorized RTDL
cache construction. All five exact parks.bz2 cardinalities then matched the
author, RTDL, and pinned author paper-log counts: 50K `52,849`, 100K `105,826`,
200K `211,714`, 400K `423,396`, and 800K `846,860`. The five query hashes are
distinct and one prepared generic RTDL AABB base consumes all five batches.

Together with Goals5517, 5519, and 5520, exact archive range-contains coverage
is now **14/14 count matches**. This completes the count matrix only; it does
not establish pointwise containment relations, performance parity, Figure 6,
full-paper reproduction, author algorithm equivalence, zero-copy, or Embree.

## Goal5522 parks.bz2 point-contains cardinality matrix

Five distinct exact point-query batches match author and RTDL counts: 50K
`56,428`, 100K `112,729`, 200K `225,699`, 400K `451,007`, and 800K `901,103`.
All five also match the pinned author logs. The 100K row was previously
checkpointed, so this adds four unique pairs and moves exact point-contains
coverage from 6/14 to 10/14. The geometry/cache reuse is app-owned; RTDL uses
only neutral AABB columns and its prepared point-contains count contract.

## Goal5523 exact point-contains count-matrix closeout

The parks_Europe 50K/100K/200K/400K/800K counts are `54,568`, `109,279`,
`218,598`, `437,276`, and `874,543`, with author and RTDL equal in every case.
The 100K file hash and count agree with the independent Goals5481-5484 result.
Combined with Goal5522, exact archive point-contains coverage is now **14/14
count matches**. Count equality remains distinct from pointwise relation
equality; no performance, Figure 6, full-paper, author-parity, zero-copy, or
Embree claim follows.

## Goal5524 scoped project closeout

LibRTS scoped correctness and system extraction are complete. Exact
point-contains and range-contains count matrices are each 14/14; representative
PIP has 71,626 canonical relation rows equal; bounded mutation counts are
`[2,1,0,1,0]`; range-intersects remains explicitly 14 matches, 2 author
capacity failures, and 26 uncheckpointed. Exhaustive repetition of those 26
cells is frozen by the project stop-loss rule because it adds no new generic
capability or unresolved semantic answer.

This is not full all-figure/performance paper reproduction. Performance parity,
Figure 6, complete range-intersects coverage, author algorithm equivalence,
zero-copy, and Embree remain unclaimed.

## Final external review

Goals5519-5525 received an unconditional external `approve` verdict on
2026-07-13. The review verified that the operation-scoped packed-AABB validity
rule is a generic geometric correction rather than author fitting, that both
contains matrices are distinct-query 14/14 count matches, and that freezing the
remaining range-intersects enumeration correctly applies the project stop-loss
rules.

The accepted final status is:

```text
LibRTS scoped correctness and system extraction complete
```

This approval does not widen the claim boundary: full-paper reproduction,
Figure 6 reproduction, performance parity, author algorithm equivalence,
complete range-intersects coverage, pointwise equality for count-only cases,
zero-copy, and Embree remain unclaimed. See
`history/internal_docs/review_goals5519_5525_librts_final_closeout_verified_2026-07-13.md`.
