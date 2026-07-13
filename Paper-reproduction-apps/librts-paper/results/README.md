# LibRTS Results

Committed results must state their comparator and regime.

Current artifacts:

```text
tiny_point_contains_rtdl_reference.json
librts_goal5454_same_input_point_contains.json
librts_goal5455_same_input_range_contains.json
librts_goal5456_same_input_range_intersects.json
librts_goal5460_same_input_mutation.json
librts_goal5461_native_refit_mutation.json
librts_goal5462_native_sparse_refit_mutation.json
librts_goal5465_same_input_pip.json
librts_goal5467_representative_same_input_pip.json
librts_goal5467_representative_pip_semantics_diagnostic.json
librts_goal5468_5469_ray_multicast_feasibility.json
librts_goal5470_partitioned_range_probe_sparse_gtx1070.json
librts_goal5470_partitioned_range_probe_gtx1070.json
librts_goal5470_partitioned_range_probe_large_gtx1070.json
librts_goal5470_partitioned_range_probe_dense_gtx1070.json
librts_goal5471_full_paper_target_availability.json
librts_goal5472_author_paper_log_denominators.json
librts_goal5473_dataset_acquisition_decision.json
librts_goal5474_resume_safe_acquisition_plan.json
librts_goal5475_safe_extraction_plan.json
librts_goal5476_pod_acquisition_plan.json
librts_goal5477_author_pod_environment.json
librts_goal5479_pod_download_verified.json
librts_goal5479_archive_inventory.json
```

The first is a local RTDL CPU-reference result only. The Goal5454 artifact runs
the same input files through the pinned author RTSpatial/OptiX example and RTDL
OptiX. It proves matching result count (`5`) and RTDL exact fixture rows. The
author example does not expose pair rows, so author pair-relation agreement is
not claimed. Neither artifact contains paper-performance evidence.

Goal5455 adds a direction-discriminating range-contains count gate. Correct
direction count is `5`, reversed direction count is `2`, and both author and
RTDL OptiX report `5` on the same files.

Goal5456 proves same-input range-intersects count `8` for author and RTDL OptiX
and records all eight RTDL native intersection rows. The same fixture has only
five range-contains rows, so the predicate is discriminating.

Goal5460 records the same mutation sequence on the pinned author public API and
the generic RTDL mutable AABB API. Both produce counts `[2,1,0,1,0]` and assign
the appended geometry ID `2`. The artifact explicitly records that the author
uses native incremental GAS/IAS update while RTDL uses atomic snapshot rebuild;
it contains no mutation performance comparison.

Goal5462 reruns the same author/RTDL sequence after the generic native sparse
refit implementation. Counts remain `[2,1,0,1,0]`; RTDL reports native sparse
refit for Update and snapshot rebuild for Delete, Insert, and Clear.

The Goal5461 artifact is the intermediate full-array native-refit gate. It is
retained to document why sparse-slot handoff was needed, not as the final route.

Goal5465 runs the exact AE author PIP application and RTDL OptiX on the same
three-polygon/five-point fixture. Both report four polygon-refined hits. RTDL additionally
emits the expected four relation rows, while the fixture has five MBR-only
candidates. The author binary exposes count only, so author pair-row agreement
is not claimed. Author timing fields are diagnostic only.

Goal5467 uses 64 provenance-classified public Block Group polygons and 100,000
points from the pinned author generator. The unmodified author binary, the
row-dump comparator build, and the RTDL app-compatible route all report 71,626
rows. Author and RTDL pair-row SHA-256 values are identical. The companion
diagnostic preserves the fact that standard RTDL `point_in_polygon` semantics
produce 71,624 rows; exact artifact agreement requires an app-owned Numba CUDA
adapter for the author's float32 sentinel layout and fast-math PNPOLY. No timing
ratio is authorized.

Goals5468-5469 record the paper/source mapping for Ray-Multicast, distinguish
existing RTDL assets from five missing native capabilities, and exercise the
new generic partitioned-traversal reference contract. The artifact authorizes
one bounded POD spike but records `native_backend_implemented=false`,
`runtime_speedup_measured=false`, and `author_equivalence_claimed=false`.

Goal5470 records the bounded native partitioned-AABB spike before its code was
reverted. All `k=1/2/4/8` rows match exactly across sparse, representative,
large, and dense deterministic range-intersection shapes. Peak per-ray work
falls, but the best end-to-end speedup is at most `1.009x`, below the declared
`1.02x` continuation gate. These artifacts are same-host RTDL controls, not
author or paper-performance evidence.

Goal5471 pins the official PPoPPAE target/source matrix, including the final
paper-to-AE output numbering mismatch, 264 checked-in author logs, and three
dataset archive MD5s. Goal5472 normalizes those logs into figure-specific
denominator records. Exact inputs remain absent and no author/RTDL ratio is
authorized.

Goal5473 records the exact-dataset acquisition gate. Zenodo exposes the 23.1 GB
AE archive, but the current GTX 1070 / roughly 16 GiB RAM host is below the
paper-scale execution requirement and its measured transfer would take about
12.1 hours. Acquisition is deferred to a suitable Linux RTX host; this is a
resource decision, not evidence that the datasets are unavailable or that any
paper figure has been reproduced.

Goal5474 records the executable resume/checksum contract. The committed plan
fails the current-host resource gate and records no download, verification, or
extraction. A suitable POD must rerun it; only exact size+MD5 can promote the
partial file, and extraction is deliberately not part of this goal.

Goal5475 records the safe inventory/extraction contract. Its real archive is
absent, so all archive-present, verified, inventoried, extracted, and exact
input flags remain false. Tiny generated archives test traversal/link rejection
and atomic staging without claiming anything about the paper archive contents.

Goal5476 records the first suitable acquisition POD plan: acquisition is
authorized by Linux/disk/RAM, while the 20 GiB GPU fails only the separate
24 GiB complete-execution gate. The plan predates transfer completion and keeps
all download/verification/extraction claims false.

Goal5477 pins all author commits, records query/pip binary hashes, and verifies
author hardware smoke counts `5`/`4`. It authorizes exact-input gates that fit
this POD, not the complete paper matrix, a figure, or a performance ratio.

Goal5479 proves official archive size+MD5 and records the real safe member
inventory. At that goal boundary the archive was not yet extracted; subsequent
Goals5480 and 5482 perform quota-safe selected-member extraction. Individual
exact input files and paper results remain subject to their own gates.
`librts_goal5480_point_contains_subset_extraction.json` records the atomic,
quota-safe extraction of the exact `dtl_cnty` geometry and 100K point-query
members from the verified official archive.

`librts_goal5481_exact_point_contains.json` is the first exact official-input
author/RTDL gate: both report 136,475 results on identical files. Timing fields
are phase evidence only; no performance ratio or Figure-6 completion is
authorized.

`librts_goal5482_point_contains_remaining_subset.json` records the exact
archive members selected for the five remaining Figure-6 point-contains cases.
Each selected geometry/query file is bound to the verified archive and carries
its extracted size and SHA-256. `librts_goal5482_exact_point_contains_remaining_batch.json`
records five additional author/RTDL count matches:

```text
USACensusBlockGroupBoundaries = 148,970
USADetailedWaterBodies        = 118,622
parks_Europe                  = 109,279
lakes.bz2                     = 103,189
parks.bz2                     = 112,729
```

The five cases plus Goal5481's `dtl_cnty = 136,475` form a six-of-six exact
official-input count matrix. The largest `parks.bz2` case uses the public
count-only `query_aabb_index_2d` route instead of materializing relation rows;
the batch runner now uses that count-only route by default for all cases.
This closes only same-input count agreement: equal counts do not establish
equal point-to-polygon relations. It does not reproduce Figure 6, does not
establish pair-row agreement, and does not authorize a performance ratio or a
complete-paper claim.

The separate Goal5467 representative PIP result records all `71,626`
author/RTDL pair rows equal with a canonical SHA-256. That is a different
relation-level workload and must not be read as pair-row evidence for these six
exact Figure-6 point-contains cases. Raw RTDL route wall is seconds while the
author internal Query Time is sub-millisecond; the phase mismatch keeps the
ratio closed and exposes that the current RTDL route is much slower.

`librts_goal5484_exact_figure6_point_contains_denominator.json` audits the
author paper-branch `Figure 6 / RTSpatial / point-contains_queries_100000`
records against all six exact gates. Geometry count, query count, and result
count agree for every case. The author timing contract is recorded as internal
Query Time with Loading Time excluded; RTDL route wall is retained as evidence
but is not denominator-aligned for a ratio. This is a denominator audit, not a
Figure-6 reproduction or performance result.

`librts_goal5485_dtl_cnty_prepared_phase.json` records the live POD prepared-
index phase gate for the exact `dtl_cnty` input. The pinned author binary and
RTDL both report `136,475` results on the same hashed files. It separates RTDL
WKT load (`28.5173s`), index preparation (`1.1200s`), prepared query wall
(`0.3763s`), and native primitive query (`0.2162s`) from the author's internal
Query Time (`0.0688ms`). This is a phase-boundary candidate only; no
author-vs-RTDL ratio, Figure-6 reproduction, pair-row equality, or full-paper
claim is authorized.

`librts_goal5486_prepared_phase_batch.json` records the six-case extension of
that gate. All six exact archive member pairs matched integer counts. The
prepared query wall values were `0.376076s` (`dtl_cnty`), `0.189807s`
(`USACensusBlockGroupBoundaries`), `0.299463s` (`USADetailedWaterBodies`),
`0.226963s` (`parks_Europe`), `0.178843s` (`lakes.bz2`), and `0.408325s`
(`parks.bz2`). Per-case JSON files preserve the input hashes and phase fields.
The large-input WKT load and index preparation are also recorded, but the
author internal Query Time and RTDL prepared-query wall are not aligned ratio
denominators. This is exact-input count and phase evidence only, not Figure-6,
pair-row, full-paper, performance-parity, or Embree evidence.

`librts_goal5487_generic_aabb_columnar_pod_gate.json` records the tiny POD
behavior gate for the new generic `Aabb2DColumns` /
`prepare_aabb_index_2d_columns` front door. Columnar and row-shaped OptiX both
return `point_contains=2` and both report RT-core acceleration. The result is
an API/ABI correctness gate, not a device-zero-copy or performance claim.

`librts_goal5488_dtl_cnty_prepared_phase_columns.json` and
`librts_goal5488_lakes_bz2_prepared_phase_columns.json` record the app-integrated
columnar route. Both exact counts match. On `lakes.bz2`, prepare is `0.856s`
versus `66.311s` in Goal5486's row/ctypes route, while WKT load is about
`405s` in both. The result is evidence about phase composition; the query
phase was not run as a controlled median and no speedup ratio is authorized.

`librts_goal5489_dtl_cnty_repeat.json` and
`librts_goal5489_lakes_bz2_repeat.json` record three same-process queries on
prepared `Aabb2DColumns` indexes. All counts match their author counts. The
first-use/reuse split is diagnostic only and must not be converted into a
paper-performance ratio; the lakes WKT load alone was `406.570s`.

`librts_goal5490_dtl_cnty_numeric_loader.json` records the experimental NumPy
WKT loader. The exact count matches, but the separate-run load is `28.069s`
versus `27.994s` for the regex baseline; this is a no-go for a demonstrated
speedup and not a performance-ratio result.

`librts_goal5491_lakes_cache_build.json` and
`librts_goal5491_lakes_bz2_cache_repeat.json` record a hash-bound reusable
column cache for `lakes.bz2`. Cache load is `8.101s` after a separate one-time
build; three queries match `103189`. This is ingestion-cache phase evidence,
not an end-to-end or author-performance ratio.

`librts_goal5489_dtl_cnty_repeat.json` records three same-process queries on
one prepared `Aabb2DColumns` index. All counts match `136475`; route wall is
`0.369s`, `0.220s`, `0.218s`, and primitive phase is `0.202s`, `0.070s`,
`0.069s`. The first-use/reuse split is diagnostic only and must not be
converted into a paper-performance ratio.

`librts_goal5492_exact_archive_operation_inventory.json` records the verified
archive operation inventory: `14` exact point-contains pairs, `14` exact
range-contains pairs, and `42` exact range-intersects pairs, with no exact PIP
or mutation pairs. `librts_goal5493_range_contains_dtl_extraction.json` records
the selected member paths and SHA-256 values. The corresponding gate result
records author and RTDL count `117314` on the same exact `dtl_cnty` files,
with load, prepare, query, and primitive phases separated and no ratio.

Goal5494 keeps the cache app-owned, and Goal5495 closes the current exact AABB
point/range-contains line while queueing range-intersects. These results are
implemented and review pending. They do not claim pointwise relation equality,
Figure 6, full-paper reproduction, author performance parity, device zero-copy,
or Embree evidence.

`librts_goal5496_range_intersects_dtl_cnty_extraction.json` records the exact
archive-derived member pair and SHA-256 values. The corresponding gate result
records author and RTDL count `1,570,285` for `dtl_cnty` with 10,000 range
queries. The author uses `load_factor=1` because `0.0001` produced a CUDA
invalid-program-counter failure on the same POD; this configuration choice is
explicitly recorded. RTDL load, prepare, query wall, and primitive phases are
separate, and no author ratio or relation-level claim is made.

Goal5497 adds the second exact range-intersects artifact for the same geometry
with a distinct query SHA. The two-case batch records author and RTDL counts
`1,570,285` and `242,920`, uses the explicit author `load_factor=1`, and keeps
all RTDL phases separate. It remains count-level evidence with no relation,
performance, Figure 6, full-paper, zero-copy, or Embree claim.

Goal5498 records the bounded closeout: two exact range-intersects cases are
matched and `40` archive pairs remain explicitly queued. This is not a full
range-intersects matrix or a relation/performance result. The closeout remains
review pending.

Goal5499 records the third exact range-intersects case. The three-case batch
counts are `1570285`, `242920`, and `239884`; all use the shared geometry SHA
and distinct query SHAs. The result remains count-level and review pending.

Goal5500 records the six-geometry exact range-intersects batch attempt. The
official archive extraction contains six pairs and twelve members. The result
contains three count matches (`dtl_cnty`, `USACensusBlockGroupBoundaries`,
`USADetailedWaterBodies`), two count disagreements (`parks_Europe`, `lakes`),
and one author-side CUDA out-of-memory failure (`parks.bz2`). It is not a
six-case matrix claim, does not establish pointwise relation equality, and
does not authorize a performance ratio. RTDL WKT load, preparation,
prepared-query wall, and primitive query time remain separate from the
author's internal query metric.

## Goal5501 bounded project closeout

Goal5501 records the final mismatch diagnostic. It uses same-source prefixes
for author, RTDL, and independent CPU float64/float32 AABB overlap oracles.
RTDL equals the CPU float32 result on the `parks_Europe`, `lakes.bz2`, and
`parks.bz2` capacity prefixes. The author differs on the two parks prefixes
and agrees on the lakes prefix. This does not prove which full-input contract
is correct, and it does not establish pointwise relation equality because the
standard author binary exposes counts only.

The full `parks.bz2` author case remains a CUDA allocation failure. The project
is closed at the bounded evidence boundary: three full-input count matches,
two unresolved full-input count disagreements, one author OOM, and a generic
prefix diagnostic. Further full-input, pair-row, or capacity work is a new
scope. No complete matrix, Figure 6, full-paper reproduction, performance
ratio, zero-copy, or Embree result is authorized.

## Goal5502 author-validity gate

The author-validity artifact classifies each Goal5501 prefix against an
independent inclusive float32 AABB oracle. The five prefix cases contain four
where RTDL matches the oracle and the author diverges, plus one where both
match. The
result is a decision aid, not a full-input adjudication: it authorizes no
RTDL fix and no author-specific core behavior. It preserves the rule that a
count difference alone does not prove the author wrong.

If future full-input evidence shows author/oracle agreement and RTDL
divergence, the generic RTDL implementation must be fixed before an exact
reproduction claim. If RTDL/oracle agree and the author diverges, preserve the
generic route and record the author contract difference. Full matrix,
pair-row, performance, full-paper, zero-copy, and Embree claims remain closed.

## Goal5503 author GPU contract audit

`goal5503_author_contract_audit.json` records the source-backed contract for
the pinned author range-intersects path. The benchmark uses float32 input and
direct float-to-OptiX-AABB conversion. Its GPU shader is not represented by
the CPU inclusive helper alone: `RayParams<float,2>::IsHit` uses
`t0=0`, `nextafterf(1.0, FLT_MAX)`, and `tFar *= 1 + 2 * FLT_GAMMA(3)` on
forward and reverse diagonal rays.

This is a contract audit, not a correctness verdict. The independent CPU
float32 oracle and the author's GPU predicate are explicitly distinct until
discriminating Goal5504 fixtures establish their relationship. Goal5503 is
implemented and review pending; no RTDL core change, full-input validity,
performance ratio, paper reproduction, or Embree claim is authorized.

## Goal5504 semantics fixtures

`goal5504_range_intersects_semantics_fixtures.json` records five deterministic
float32 fixtures. One distinguishes the independent CPU inclusive AABB
predicate from a source-driven emulation of the author's forward plus
backward `RayParams<float,2>::IsHit` shader path. It is not an author GPU
runtime result, not a full-input verdict, and not authorization to alter RTDL
core. `goal5505_runtime_semantics_gate.json` records the subsequent same-input
POD runtime observations.

## Goal5505 same-input POD runtime gate

The five queries were run one at a time through the pinned author binary and
generic RTDL OptiX using identical geometry/query hashes. In committed WKT
order, author counts are `[1,1,1,1,1]`; pre-fix RTDL counts are `[1,1,1,1,0]`.
The source-driven model matches the author on all five; the only pre-fix
author/RTDL mismatch is `one_ulp_gap_after_box_max`. Goal5507 applies the
generic float32 interval and two-direction acceptance rule and matches the
author on the Goal5505 fixture and Goal5506's 8,192-pair probe. This does not
close the full-input disagreements.

## Goal5506 scalable semantics probe

goal5506_scalable_semantics_gate.json records a deterministic 8,192-pair POD
probe. Counts are CPU inclusive 20, source model 21, author 21, and RTDL 20.
The result is bounded contract evidence only: no full-input root cause, paper
reproduction, performance ratio, or RTDL core change is claimed.

## Goal5508 generic float32-degenerate indexed AABB validity fix

The two Goal5502 official count disagreements were traced to four indexed
geometries per prefix that become zero-width or zero-height after float32
conversion. The author returns zero for the isolated invalid subsets; pre-fix
RTDL returned `27` and `5,005`, exactly the two full-prefix excesses. After a
generic pass-correct strict-validity guard in the OptiX intersection kernel,
both isolated subsets return zero and both full prefixes match the author:

```text
parks_Europe: 34,240,217 == 34,240,217
lakes_bz2:    34,581,812 == 34,581,812
```

The gate records input hashes, invalid indices, source/library hashes, and
claim flags. This does not close the complete official range-intersects
matrix, prove official pair-row equality, authorize a performance ratio, or
claim paper reproduction.

## Goal5509 exact range-intersects next batch

Goal5509 adds a second exact query family and checkpoints four count matches:
parks_Europe `2,486,816`, dtl_cnty `242,920`, USACensusBlockGroupBoundaries
`423,893`, and USADetailedWaterBodies `651,647`. The parks.bz2 and lakes.bz2
large cases were attempted but did not produce independent checkpoints before
the batch process was reclaimed. They are unresolved capacity/process-lifetime
states, not mismatches. The complete 42-pair matrix, pair-row equality,
performance ratio, Figure 6, full paper, zero-copy, and Embree claims remain
closed.

## Goal5511 exact `select_0.001` range-intersects batch

Goal5511 independently checkpointed four additional exact-archive count
matches:

| Case | Author count | RTDL count |
|---|---:|---:|
| parks_Europe | 23,962,096 | 23,962,096 |
| dtl_cnty | 239,884 | 239,884 |
| USACensusBlockGroupBoundaries | 3,478,660 | 3,478,660 |
| USADetailedWaterBodies | 6,436,810 | 6,436,810 |

The query family is `range-intersects_select_0.001_queries_10000`. Each
case has an independent JSON checkpoint and the author and RTDL consume the
same extracted files. The result is count-level only; the standard author
binary does not expose pair rows. The full 42-pair matrix, Figure 6,
performance ratio, full-paper, zero-copy, author-parity, and Embree claims
remain closed.

## Goal5512 large-case capacity resolution

Goal5512 resolves the two Goal5509 large-case states:

| Case | Author | RTDL | Interpretation |
|---|---|---|---|
| lakes.bz2 | 10,579,596 | 10,579,596 | count match |
| parks.bz2 | CUDA `bad_alloc` | not run | author capacity failure |

The parks failure is not a semantic mismatch. The lakes result was retried
with a temporary serialize directory after a workspace quota/output-stream
failure. This remains count-level evidence and does not close the full
42-pair matrix, pair rows, Figure 6, performance ratio, full paper,
zero-copy, author parity, or Embree claims.

## Goal5513 exact `select_0.01` range-intersects batch

Goal5513 adds four exact-archive count matches:

| Case | Author count | RTDL count |
|---|---:|---:|
| parks_Europe | 216,977,211 | 216,977,211 |
| dtl_cnty | 1,570,285 | 1,570,285 |
| USACensusBlockGroupBoundaries | 33,404,355 | 33,404,355 |
| USADetailedWaterBodies | 55,205,607 | 55,205,607 |

The query family is `range-intersects_select_0.01_queries_10000`. Each case
has an independent JSON checkpoint and the author and RTDL consume the same
extracted files. The result is count-level only; the complete matrix, pair
rows, Figure 6, performance ratio, full paper, zero-copy, author parity, and
Embree claims remain closed.

## Goal5514 six-geometry `.01` resolution

Goal5514 resolves the final two `.01` family states:

| Case | Author | RTDL | Interpretation |
|---|---|---|---|
| lakes.bz2 | 1,113,229,623 | 1,113,229,623 | count match |
| parks.bz2 | CUDA `bad_alloc` | not run | author capacity failure |

Across Goal5513 and Goal5514, the family has five count matches and one
author capacity boundary. It remains count-level evidence and does not close
the complete 42-pair matrix, pair rows, Figure 6, performance ratio, full
paper, zero-copy, author parity, or Embree claims.

## Goal5515 historical mismatch resolution

Goal5515 compares the old Goal5500 deltas with the corrected same-input
recheck. `parks_Europe` moved from `+3,791` to `0`, and `lakes.bz2` moved from
`+54,695` to `0`. The result is a bounded resolution of the two observed
count disagreements after the generic indexed-AABB validity correction. It
does not upgrade the evidence to pair rows, a complete archive matrix,
Figure 6, a performance ratio, full paper reproduction, zero-copy, author
parity, or Embree support.

## Goal5516 exact range-intersects coverage ledger

The 42-pair ledger reports 14 exact same-input count matches, 2 explicit
author CUDA capacity failures, and 26 `not_checkpointed` entries. It is an
accounting artifact, not a complete matrix claim: count equality remains
distinct from pair-row equality, and no performance, Figure 6, full-paper,
zero-copy, author-parity, or Embree claim is authorized.

## Goal5517 exact range-contains batch

Goal5517 records four exact same-input count matches from the 100,000-query
range-contains family: `104,426`, `117,314`, `120,457`, and `112,637`.
Individual checkpoints retain input hashes and separate author internal time
from RTDL WKT load, prepare, and query phases. Count equality does not establish
pointwise containment equality, and no performance ratio or paper-figure claim
is authorized.

## Goal5521 exact range-contains count-matrix completion

The final parks.bz2 cardinality family matches at all five exact archive query
sizes: `52,849`, `105,826`, `211,714`, `423,396`, and `846,860`. A smallest-case
author capacity gate ran before the app-owned cache was built. All five query
files are distinct and were consumed by one prepared generic RTDL AABB base.
The exact archive range-contains inventory is now 14/14 at count level. Equal
counts do not establish pointwise relation equality, and no performance,
Figure 6, full-paper, author-parity, zero-copy, or Embree claim is authorized.

## Goal5522 parks.bz2 point-contains cardinalities

The five exact cardinalities match author and RTDL at `56,428`, `112,729`,
`225,699`, `451,007`, and `901,103`. Five per-cardinality checkpoints protect
the evidence from late-batch process loss. Since the 100K case already existed,
exact point-contains coverage becomes 10/14 rather than 11/14. Evidence remains
count-level; relation and performance claims are closed.

## Goal5523 exact point-contains count-matrix closeout

Five parks_Europe cardinalities match author and RTDL at `54,568`, `109,279`,
`218,598`, `437,276`, and `874,543`. The independent prior 100K identity is
rechecked rather than double-counted. The exact point-contains inventory is now
14/14 at count level. Relation equality remains separately scoped.

## Goal5524 system-value closeout

The final machine-readable matrix separates complete exact count coverage for
point/range contains, representative relation evidence for PIP, bounded
mutation semantics, and incomplete range-intersects coverage. It applies the
stop-loss gate to the remaining 26 app-only range-intersects combinations and
records the generic RTDL capabilities extracted from the paper app.
