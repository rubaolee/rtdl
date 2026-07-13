# LibRTS Data Provenance

Goal5453 uses a tiny deterministic app-owned WKT fixture for the first
same-input contract gate:

```text
fixtures/tiny_boxes.wkt
fixtures/tiny_points.wkt
fixtures/tiny_point_contains_expected.json
```

The fixture avoids boundary-degenerate points. It is not a paper dataset.

The pinned GitHub repository also contains generated 1,000-row uniform and
Gaussian box/point fixtures under `dataset/`. The exact paper artifact is the
Zenodo v2 `PPoPPAE-v2.tar.gz` archive, which is 23.1 GB and is not vendored in
this repository. Acquisition and paper-matrix extraction are later goals.

The verified Zenodo archive was later acquired on the RTX 4000 Ada POD. Because
the full archive expands to about 88.23 GB, the app uses quota-safe selected
member extraction rather than claiming a complete expansion. Goals5482-5483
select and execute the five remaining Figure-6 point-contains geometry/query
pairs, each with archive-member path, size, and SHA-256 evidence. Together with
the `dtl_cnty` pair from Goal5480/5481, these provide six exact official-input
count gates. The author contract exposes only a count for this operation, so
the evidence does not claim pair rows, Figure-6 reproduction, or performance
parity.

Goal5485 reuses the exact `dtl_cnty` member pair on the replacement RTX 4000
Ada POD. The archive MD5 and selected-member SHA-256 values are verified, and
the pinned author query plus RTDL prepared AABB query both return `136475`.
The result records WKT load, index preparation, prepared query wall, native
primitive query, and author internal Query Time as separate fields. This is a
phase-boundary measurement candidate only; it does not authorize a performance
ratio or Figure-6 reproduction claim.

`librts_goal5486_prepared_phase_batch.json` extends the same prepared-index
contract to all six exact archive pairs. All six author/RTDL integer counts
match. The prepared query wall values are:

```text
dtl_cnty                       0.376076 s
USACensusBlockGroupBoundaries  0.189807 s
USADetailedWaterBodies        0.299463 s
parks_Europe                  0.226963 s
lakes.bz2                     0.178843 s
parks.bz2                     0.408325 s
```

The batch also records large input-front-door costs (`404.471s` WKT load for
`lakes.bz2` and `553.019s` for `parks.bz2`). These values are useful for
engineering diagnosis but are not author-vs-RTDL ratio denominators. The
matrix remains count-level only: it does not establish pointwise containment,
pair-row equality, Figure-6 reproduction, full-paper reproduction, or an
Embree comparison.

Goal5487 adds the app-neutral `Aabb2DColumns` /
`prepare_aabb_index_2d_columns` system contract. Its POD tiny gate matched the
existing row-shaped OptiX path (`point_contains=2` on both paths, both
RT-core-accelerated). This removes host Python row-object construction from
the new packing path, but it does not claim device zero-copy or a LibRTS
performance improvement.

Goal5488 applies the columnar front door to exact `dtl_cnty` and `lakes.bz2`.
Both counts match the author (`136475` and `103189`). For `lakes.bz2`, the
columnar prepare phase is `0.856s` versus `66.311s` in the earlier row/ctypes
route, while WKT load remains about `405s`. This is a phase diagnostic showing
removed host packing work, not a controlled end-to-end speedup or ratio.

Goal5489 repeats the same exact `dtl_cnty` point-query batch three times on one
prepared columnar index. All counts match `136475`; first and subsequent query
phases are recorded separately. The larger `lakes.bz2` case also matches
`103189` on all three repeats. This is a same-process reuse diagnostic only,
with no author ratio or Figure-6 claim.

Goal5490 tested an app-owned NumPy numeric WKT loader on exact `dtl_cnty`.
The count remained `136475`, but the separate-run load was `28.069s` versus
`27.994s` for the regex baseline, so no load speedup was demonstrated. The
variant remains experimental; WKT parsing is not promoted into RTDL core.

Goal5491 adds a hash-bound app-owned `.npz` cache for exact AABB columns. The
`lakes.bz2` cache has `8,327,448` rows and is `286MB`; cache load plus source
SHA validation is `8.101s`, with all three prepared queries matching `103189`.
The one-time cache build is separate and no end-to-end speedup is claimed.

Goal5489 repeats the same exact `dtl_cnty` point-query batch three times on one
prepared columnar index. All counts match `136475`; first and subsequent query
phases are recorded separately. This is a same-process reuse diagnostic only,
with no author ratio or Figure-6 claim.

Goals5492-5495 record the next exact-operation status. The verified archive
inventory contains `14` point-contains pairs, `14` range-contains pairs, and
`42` range-intersects pairs. It contains no exact PIP or mutation pairs.
Goal5493 selects the exact `dtl_cnty` range-contains pair and matches the
author count `117314` with the generic RTDL columnar route on the same hashed
files. Goal5494 keeps the cache lifecycle app-owned because no second generic
consumer exists. Goal5495 closes the current point/range-contains line and
queues range-intersects. These goals are implemented and review pending.

Goal5496 runs the exact `dtl_cnty` range-intersects member with 10,000 query
boxes. Author and RTDL both return `1,570,285` on the same archive-derived
files. The author configuration is `load_factor=1`; `0.0001` was tested and
failed with a CUDA invalid-program-counter error on this POD, so it is not
used for the gate. This remains count-level exact-input evidence only, with
no relation, Figure 6, full-paper, performance, zero-copy, or Embree claim.

Goal5497 adds a second exact range-intersects query member for the same
`dtl_cnty` geometry. The two author/RTDL count matches are `1,570,285` and
`242,920`; geometry provenance is shared and query provenance is distinct.
The two-case batch remains count-level evidence only and is implemented/review
pending.

Goal5498 closes the bounded two-case range-intersects line and leaves `40`
other exact archive pairs queued. It does not claim complete range-intersects
coverage, pointwise relation equality, Figure 6, full paper, performance,
device zero-copy, or Embree evidence.

Goal5499 adds a third exact range-intersects query member for the same
`dtl_cnty` geometry. Author and RTDL both return `239884`, extending the
count matrix to three query selectivity settings. Query provenance remains
distinct per case; this is not complete operation coverage.

Goal5500 extracts six official geometry/query pairs for the same
`range-intersects_select_0.01_queries_10000` family. The selected members are
`parks_Europe`, `parks.bz2`, `dtl_cnty`, `lakes.bz2`,
`USACensusBlockGroupBoundaries`, and `USADetailedWaterBodies`; each has a
recorded size and SHA-256 under the verified archive MD5. The batch is a
coverage attempt, not a completed matrix: three counts match, two counts
disagree, and `parks.bz2` fails at the author CUDA allocation step. Equal or
unequal counts do not establish pairwise relation equality because the author
binary exposes count only.

## Goal5501 bounded closeout

Goal5501 runs a same-source prefix diagnostic for the two Goal5500 count
disagreements and a 100,000-geometry capacity prefix for `parks.bz2`. RTDL
matches the independent CPU float32 AABB oracle on all three feasible probes.
The author differs from RTDL by five counts on the `parks_Europe` prefix and
four counts on the `parks.bz2` prefix, while the `lakes.bz2` prefix matches.
These results narrow the execution-contract question but do not prove a full
input root cause. The full `parks.bz2` author run remains an author-side CUDA
allocation failure, so the prefix is not a capacity fix.

The data line is closed at this bounded evidence boundary. Full
range-intersects coverage, pair-row adjudication, and capacity recovery are
new scope; no substitute input, count signature, or prefix result is promoted
to paper-figure or full-paper evidence.

## Goal5502 author-validity gate

Goal5502 applies a three-way decision to the Goal5501 prefix evidence. The
selected independent contract is inclusive float32 AABB intersection. RTDL
matches it on all five prefixes; the author matches on one prefix and
diverges on four prefixes. The gate does not infer a full-input author
bug from this alone, but it does reject copying the author divergence into
RTDL core. A future full-input campaign must either fix RTDL when it diverges
from the validated contract or preserve RTDL when the author diverges.

The gate is app-owned and prefix-only. It does not upgrade the current bounded
closeout to a complete range-intersects matrix or full paper reproduction.

## Goal5503 author GPU contract audit

Goal5503 audits the pinned source used by the author benchmark. The benchmark
stores coordinates as `float32` and writes float coordinates directly into
`OptixAabb`. The CPU envelope helper is inclusive, but the actual OptiX
range-intersects shader uses `RayParams<float,2>::IsHit` with a slab interval
starting at `0`, ending at `nextafterf(1.0, FLT_MAX)`, and an expanded far
bound `1 + 2 * FLT_GAMMA(3)`. It tests a query diagonal and then a reverse
envelope diagonal.

The Goal5502 CPU oracle is therefore retained as an independent generic
contract, not silently promoted to the author's GPU truth. CPU/GPU predicate
equivalence remains unproven. No RTDL core change, author-specific behavior,
full-input adjudication, performance ratio, or Embree evidence is authorized.

## Goal5504 semantics fixtures

Goal5504 compares an independent CPU inclusive float32 AABB contract with a
source-driven emulation of the author's GPU `RayParams<float,2>::IsHit`
forward plus backward diagonal path. One of five deterministic fixtures
discriminates at a one-ULP gap. The result is diagnostic only: the emulation
did not execute the author GPU binary, and no RTDL core change or full-input
adjudication is authorized. Goal5505 contains the subsequent POD runtime gate.

## Goal5505 same-input POD runtime gate

The five boundary queries were run one at a time through the pinned author
binary and generic RTDL OptiX on the same RTX 4000 Ada POD. In committed WKT
order, author counts are `[1,1,1,1,1]`; pre-fix RTDL counts are `[1,1,1,1,0]`.
The source-driven model matches all five author observations. The sole pre-fix
author/RTDL mismatch is `one_ulp_gap_after_box_max`. Goal5507 applies the
generic float32 interval and two-direction acceptance rule and matches the
author on the Goal5505 fixture and Goal5506 probe.

## Goal5506 scalable semantics probe

Goal5506 uses a deterministic 128-box by 64-query float32 probe (8,192 pairs).
The CPU inclusive count is 20, the source RayParams model is 21, the author
GPU runtime is 21, and RTDL OptiX is 20. This strengthens the bounded
contract-difference evidence without deciding full-input correctness or
author validity, and it authorizes no core change.

## Goal5508 generic float32-degenerate validity diagnosis

Goal5508 audits the two Goal5502 official-prefix disagreements against the
author's source validity behavior. Both prefixes contain four geometries that
become non-strict AABBs after float32 conversion. A four-record subset produces
the entire pre-fix RTDL excess (`27` for parks and `5,005` for lakes), while the
author returns zero. The generic OptiX kernel now rejects those invalid indexed
records in both intersection passes.

The fixed RTDL count matches the author on both full prefixes. This remains a
two-prefix correction, not a complete 42-pair archive matrix or pairwise
relation claim. It does not promote the author parser or validity behavior into
an app-specific RTDL API, and Embree remains out of scope.

## Goal5509 exact query-family batch

The second exact `range-intersects_select_0.0001_queries_10000` batch reuses
the six geometry members already verified from the archive and adds six
query-member SHA-256 records. Four cases have independent author/RTDL count
JSON checkpoints and match. Two large cases were attempted before the batch
process was reclaimed and are explicitly unresolved; no mismatch is inferred
from their missing checkpoints. The batch remains count-only and bounded.

## Goal5511 exact query-family batch

Goal5511 adds the verified archive query family
`range-intersects_select_0.001_queries_10000` for four independently
checkpointed geometry/query pairs. The query members are extracted from the
same MD5-verified archive and their SHA-256 values are recorded in
`results/librts_goal5511_range_intersects_batch_extraction.json`.

The four selected pairs are `parks_Europe`, `dtl_cnty`,
`USACensusBlockGroupBoundaries`, and `USADetailedWaterBodies`. The two
large-case failures from Goal5509 are not silently folded into this batch;
they remain separate unresolved process-capacity evidence. This input file
manifest therefore proves only a four-case exact-archive query-family gate,
not a complete archive matrix or paper figure.

## Goal5512 large-case capacity resolution

Goal5512 resolves the two Goal5509 `.0001` cases with independent results.
The lakes author/RTDL count is `10,579,596` on identical extracted files. The
parks author run fails with CUDA `bad_alloc`, so no RTDL comparison is made for
that case. The failure is recorded as an author capacity state and is not
promoted to a semantic mismatch. The verified archive identity remains
anchored by the existing extraction manifest and per-case SHA-256 values.

## Goal5513 exact query-family batch

Goal5513 adds four independently checkpointed cases from the verified
`range-intersects_select_0.01_queries_10000` family. The four cases are
parks_Europe, dtl_cnty, USACensusBlockGroupBoundaries, and
USADetailedWaterBodies. Their author/RTDL counts match, and each checkpoint
retains the extracted-file SHA-256 identity. This is a bounded query-family
gate, not a complete archive matrix or paper-figure result.

## Goal5514 six-geometry resolution

The `.01` query family is now resolved for all six geometry members: five
author/RTDL count matches and one explicit parks.bz2 author CUDA allocation
failure. The failure is not a semantic mismatch. This closes the family
state, not the full 42-pair operation matrix or any paper figure.

## Goal5515 mismatch resolution

Goal5515 rechecks the two historical `.01 x 10000` disagreements from
Goal5500 after the generic float32 indexed-AABB validity correction. The same
official `parks_Europe` and `lakes.bz2` files now produce zero RTDL-vs-author
count delta (`216,977,211` and `1,113,229,623`, respectively). The result is
evidence-level resolution of those observations, not a claim that every
possible range-intersects discrepancy has one universal cause.

## Goal5516 coverage ledger

Goal5516 reconciles the 42 exact range-intersects inventory pairs with actual
checkpointed evidence: 14 count matches, 2 author CUDA capacity failures, and
26 pairs not checkpointed. Missing checkpoints are not inferred to be either
semantic matches or mismatches. A future run must first prove that its exact
query member is present in the staged extraction.

## Goal5517 exact range-contains batch

Four exact archive pairs from `range-contains_queries_100000` were extracted
with eight member SHA-256 values and run independently. The verified target
was placed under `/tmp` after `/workspace` returned `Disk quota exceeded`.
Storage location is not part of the algorithm or timing claim. All four count
results match; the remaining range-contains inventory is separate work.

## Goal5521 parks.bz2 range-contains exact batch

The verified extraction contains one `parks.bz2` geometry member and five
distinct range-contains query members (50K through 800K), each with SHA-256.
The 50K author capacity precheck completed before the app-owned AABB cache and
matrix were authorized. The cache is a derived paper-app artifact; it does not
move WKT parsing or file semantics into RTDL core. All five exact count gates
match, completing the 14-pair range-contains count inventory.

## Goal5522 parks.bz2 point-query extension

Five point-query members are added to the existing verified parks.bz2 target
without copying or replacing its 8.3 GiB geometry member. The extension tool
requires the existing geometry to match its prior size and SHA-256, rejects an
unverified pre-existing query, stages missing members from the MD5-verified
archive, and atomically promotes each file. This is paper-app provenance and
storage reuse, not an RTDL core ingestion feature.

## Goal5523 parks_Europe point-contains exact batch

One exact parks_Europe geometry and five exact point-query cardinalities are
atomically extracted from the MD5-verified archive. Per-file hashes identify
all six members, and the 100K query hash agrees with the independent earlier
checkpoint. This closes the point-contains count inventory without claiming
the official binary exposes pointwise relation rows.
