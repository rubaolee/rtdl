# Roadmap

## Goal5836 preaction-authoring gate open (2026-09-01)

The Mac hostile review closed at `P0=0/P1=0/P2=4/P3=2`. Only creation of a
Goal5836 preaction is authorized. The preaction must preserve the existing
edge-only claim and fail closed if exact Sui source does not support it; it must
also require a complete mesh-derived positive edge crossing and path-independent
custody. Author acquisition/comparison, Goal5836 execution, modern RTX, POD,
performance, Paper-App promotion and external review remain locked behind a
separate owner gate.

## Goal5835 closure checkpoint (2026-08-30)

Goal5835 is complete at bounded mapping scope. The next possible step is not
more local mapping polish. It is a separately frozen Goal5836 promotion plan
covering exact Sui paper/source provenance, one paper-source positive mesh
fixture, author-code same-input comparison, and a modern-RTX end-to-end run.
Until that plan is owner-authorized, Goal5836, POD use, performance and Paper
App promotion remain locked.

## Current CGO RT-CCD critical path (2026-08-30)

```text
Goal5833 built-in sphere public path: complete at bounded functional scope
Goal5834 general First Contact: incomplete numeric contract
Goal5834-B3 fixed Boolean bridge: complete, 11/11 registered fixtures
-> Goal5835 now active: exact registered-fixture Sui-derived mapping only
-> Goal5836 later: paper-source fixture + author same-input + modern RTX;
   Paper App promotion only if every gate passes
```

Goal5835 is an application mapping goal, not a runtime expansion. Do not add
new GPU fixtures, performance work, full RT-CCD scope or generic compiler work.
The immediate deliverable is a reader-checkable mapping from sphere/path
segments to curve capsules and deterministic obstacle-triangle edges to query
segments, plus reconstruction and a functional receipt over the existing B3
authority.

## Current Phase

The active fifth paper project is LibRTS. The four earlier app lines remain
closed at their scoped boundaries; there is no active X-HD optimization or
artifact-search task.

LibRTS sequence:

```text
Goal5453 provenance + local CPU reference gate
-> Goal5454 author OptiX vs RTDL OptiX tiny point-contains gate (complete,
   review pending)
-> Goal5455 range-contains gate (complete, review pending)
-> Goal5456 range-intersects gate (complete, review pending)
-> Goal5457 generic mutation-contract audit (complete, review pending)
-> Goal5458 generic mutable AABB CPU contract (complete, review pending)
-> Goal5459 Linux OptiX snapshot-rebuild gate (complete, review pending)
-> Goal5460 patched-author same-input mutation gate (complete, review pending)
-> Goals5461-5462 generic native sparse-slot OptiX refit
   (externally reviewed after amendments)
-> Goal5463 speedup correction + hardware rollback/fail-closed verification
   (externally reviewed and approved)
-> Goal5464 exact AE PIP source/build and discriminating fixture contract audit
   (implemented, review pending)
-> Goal5465 author/RTDL OptiX bounded same-input PIP gate: 4 refined hits versus
   5 MBR-only candidates (implemented, review pending)
-> Goal5466 Level-B representative public-source PIP data with 64 polygons and
   100K pinned-author-generated points (implemented, review pending)
-> Goal5467 full author/RTDL app-compatible relation match at 71,626 rows while
   preserving the standard RTDL 71,624-row semantic difference
   (implemented, review pending)
-> Goal5468 paper/source/history feasibility audit: static disjoint-layer
   traversal fanout is not query batching (implemented, review pending)
-> Goal5469 app-neutral partitioned-traversal reference and Contact-Manifold
   non-app consumer (implemented, review pending)
-> Goal5470 bounded generic native OptiX spike: exact rows and lower peak ray
   work, but only 1.000x-1.009x end-to-end; prototype reverted under kill gate
   (implemented, review pending)
-> Goals5471-5472 official AE target/source/log and denominator matrix: all 264
   logs mapped to Figures 6-12; exact inputs absent (implemented, review pending)
-> Goal5473 exact-dataset acquisition decision: Zenodo archive reachable, but
   current GTX1070/16GiB host is below execution requirements and would take
   about 12.1h to download (implemented, review pending)
-> Goal5474 app-owned resumable download + exact size/MD5 promotion gate
   (implemented and locally tested, download not executed, review pending)
-> Goal5475 safe tar inventory + staging/atomic extraction gate (implemented
   and locally tested, real archive absent, review pending)
-> Goal5476 RTX4000 Ada POD acquisition authorized and launched; complete
   execution gate remains conservative-false at 20 GiB VRAM (review pending)
-> Goal5477 pinned author query/pip GPU environment built and smoke-passed
   without Embree (implemented, review pending)
-> Goal5478 exact dtl_cnty point-contains runner contract, verified archive
   required and count-only claim (implemented, review pending)
-> Goal5479 official archive download/MD5 and safe 1,694-member inventory
   (implemented, review pending)
-> Goal5480 safe extraction, atomic promotion, exact path/hash inventory
-> Goal5481 execute exact dtl_cnty point-contains count gate
-> Goals5482-5483 execute the five remaining exact Figure-6 point-contains
   count gates and switch the batch runner to the generic count-only public
   route (externally reviewed and approved; 6/6 exact-input count matches,
   count-level only)
-> Goal5484 audit the Figure-6 author Query-Time denominator against all six
   exact gates (externally reviewed and approved; no ratio authorized)
-> Goal5485 separate generic RTDL prepared-index query timing from load/prepare
   (live exact-input count match; phase candidate recorded; ratio not authorized)
-> Goal5486 six-case exact prepared-index phase matrix
   (implemented; POD 6/6 count matches; phase fields recorded; review pending)
-> Goal5487 generic Aabb2DColumns / prepare_aabb_index_2d_columns front door
   (implemented; local ABI/CPU tests pass; POD tiny parity gate passed;
   review pending)
-> next: app-owned WKT/MBR column emission and same-input phase comparison;
   no device-zero-copy claim without a new ABI
-> performance only on aligned hardware, inputs, and denominators
```

Backend scope is fixed for this campaign:

```text
CPU = local semantic reference
OptiX = accelerated author/RTDL comparison
Embree = excluded
HIPRT = inactive
Linux fallback before POD = lestat@192.168.1.20 (functional evidence only)
```

The LibRTS project proceeds under the same portfolio discipline:

```text
provenance scaffold
-> smallest same-input author/RTDL correctness gate
-> honest input-identity classification
-> phase-boundary audit
-> map existing generic RTDL capabilities
-> add system API only when a non-app consumer proves genericity
-> performance only after correctness and denominators are fixed
```

The portfolio snapshot and Goal5452 regression gate are the handoff source of
truth. The X-HD material below records the completed historical extraction
phase and is not the current work queue.

## Historical X-HD System Extraction Phase

The current phase is system extraction from X-HD, not merely paper-app wrapping.

As of Goal5188, the current strongest X-HD evidence is:

```text
Level B full public candidate:
  Dragon source points      = 437645
  HappyBuddha target points = 543652

Author hd_exec HDResult = 0.12572988867759705
RTDL route distance     = 0.12572988629271128
author-vs-RTDL abs diff = ~2.38e-9

Author Running.AvgTime  = ~7.603 ms
Author process wall     = ~1.97 s
RTDL route wall         = ~7.30 s
RTDL total              = ~10.01 s
```

This is not exact paper dataset reproduction and not a denominator-aligned
performance comparison. It is full-public Level-B same-source evidence. The
route bottleneck is now the generic nearest-cell-MBR seed phase
(`~4.04s`), followed by frontier row production (`~1.94s`).

Goal5189 changes that profile with an app-neutral local-grid-cell seed. On the
same full-public Level-B route, local-grid seed still matches author HDResult
and lowers route wall to about `5.98s`, but frontier rows increase from about
`2.05M` to about `7.59M`. The new measured route costs are frontier row
production (`~2.30s`) and nearest continuation (`~2.03s`), with seed reduced to
about `0.90s`.

Goal5190 then tests a tighter app-neutral grid branch-bound seed. It matches
author HDResult and reduces frontier rows to about `1.81M`, but route wall is
about `7.71s` because seed search costs about `4.60s`. It should remain an
optional measured strategy; the best current route remains Goal5189 local-grid.

Goal5191 then increases the generic native inline-nearest threshold on the
local-grid route. At `max_inline_points=512`, native inline-nearest consumes all
frontier work on the full public Dragon/HappyBuddha Level-B route, and an
empty-frontier passthrough avoids calling the generic continuation on an empty
row table:

```text
route_wall ~= 3.65s
frontier_rows = 0
nearest_continuation ~= 0.016s
native frontier / inline-nearest collector ~= 2.00s
local-grid seed ~= 0.88s
```

Goal5192 measures the native inline-nearest work and Goal5193 rules out simple
bounded-grid seed / intermediate-threshold replacements. Goal5194 then fixes
the generic native payload pruning defect: later cells are classified against
the updated payload current best instead of only the initial seed distance.

```text
route_wall ~= 3.46s
frontier_rows = 0
nearest_continuation ~= 0.016s
native frontier / inline-nearest collector ~= 1.79s
local-grid seed ~= 0.90s
inline point evaluations ~= 0.40B
```

The best current route is now Goal5194 local-grid plus inline-nearest threshold
512 plus payload-current-best pruning. The next performance target, if any, is
a larger generic traversal/indexing change or local-grid seed cost, not Python
continuation or more small threshold guesses.

The high-level path is:

```text
bounded value gates
-> same-source representative gates
-> algorithmic gap analysis
-> generic grid/cell-MBR/frontier APIs
-> native 3-D cell-MBR traversal backend
-> fair phase/performance matrix if denominators can be aligned
```

## Near-Term Milestones

### M0. Goal5189 Generic Seed Attack

Completed implementation pending external review. The local-grid seed route is
faster on the full-public Level-B candidate but has a clear tradeoff: looser
seeds increase frontier/continuation work.

### M0b. Goal5190 Grid Branch-Bound Seed

Completed implementation pending external review. It proves that simply making
the seed tighter is not enough; seed cost can dominate again.

### M0c. Goal5191 Post-Seed Route Decision

Completed implementation pending external review. The threshold sweep shows
that larger native inline-nearest thresholds are the winning post-seed attack
for this full-public Level-B route; the empty-frontier passthrough removes the
remaining empty continuation overhead. Do not add X-HD-specific shortcuts.

### M0d. Post-Goal5191 Decision

Choose one:

- review and lock the current Level-B route;
- optimize the generic native inline-nearest collector;
- reduce local-grid seed cost;
- stop route micro-optimization and return to exact-dataset provenance/figure
  work.

### M1. Consolidated Review Node

Send Goals5130-5174 for strict review. The current packet has been written at
`history/internal_docs/call_for_review_goals5130_5174_xhd_level_b_author_directed_route_packet_2026-07-08.md`
and should emphasize:

- exact paper inputs unavailable;
- Stanford graphics gates are Level B same-source representative;
- Goal5144 verifies 2-D OptiX AABB broadphase-assisted front door;
- Goal5145 provides 3-D reference oracle;
- Goals5148-5150 provide a native 3-D cell-MBR frontier route and X-HD bounded
  route gate;
- Goals5152-5153 reduce continuation work with a generic nearest-cell-MBR seed;
- Goal5154 is a phase-separated performance matrix with no authorized ratio;
- Goal5155 separates production timing from exact-reference validation and
  profiles route subphases, but still makes no parity/speedup claim;
- Goal5156 makes route phase selection median-based and shows continuation/seed
  dominate native frontier on sample1024;
- Goal5157 vectorizes generic frontier nearest continuation and moves the
  dominant sample1024 phase to seed/frontier rather than continuation;
- Goal5158 vectorizes generic nearest-cell-MBR seed and moves the dominant
  sample1024 phase to native frontier row production;
- Goal5159 adds row-table-only native frontier consumption and shows split
  materialization is not the main remaining frontier cost;
- Goal5160 adds active-row-only native frontier emission and shows that skipping
  pruned diagnostic rows before atomic append/copy/sort reduces sample1024
  route median to ~0.079s; the next measured target is seed or deeper generic
  route design, not split materialization;
- Goal5161 adds a generic Numba seed executor and shows that avoiding the large
  NumPy seed matrix reduces sample1024 route median to ~0.022s; the next target
  should be selected by a fresh post-5161 profile or larger representative case;
- Goal5162 runs that larger representative sample2048 profile and shows nearest
  continuation dominates the measured route at the larger size;
- Goal5163 adds a generic Numba frontier nearest continuation executor and
  reduces sample2048 route median to ~0.025s;
- Goal5164 records the current post-Goal5163 same-POD matrix across
  sample256/sample1024/sample2048 with route medians ~0.009s/~0.025s/~0.025s;
- Goal5165 extends the same route to sample4096 with route median ~0.041s and
  total median ~0.067s;
- Goal5166 extends the same route to the full public Stanford res4 pair
  (Dragon 5205 points vs HappyBuddha 7108 points) with route median ~0.059s and
  total median ~0.100s;
- Goal5167 replaces generic grid cell-MBR Python min/max loops with NumPy
  reduceat; the full public res4 pair remains matched and route median improves
  to ~0.052s with total median ~0.092s;
- Goal5168 adds a generic Numba parallel nearest-cell-MBR seed executor; the
  full public res4 pair remains matched and route median improves to ~0.039s
  with total median ~0.079s;
- Goal5169 adds fail-closed inferred-capacity retry for streaming native
  frontier rows; the full public res4 pair remains matched and route median
  improves to ~0.036s with total median ~0.075s;
- Goal5170 adds a grouped Numba parallel frontier nearest-continuation executor;
  the full public res4 pair remains matched and route median improves to
  ~0.034s with total median ~0.075s;
- Goal5171 adds an app-neutral native frontier row-order option; the full public
  res4 pair remains matched and native-unsorted streaming rows improve the route
  median modestly from ~0.03376s to ~0.03309s, with some frontier savings moving
  into continuation grouping cost;
- Goal5172 adds app-neutral native inline-nearest payload reduction for inline
  3-D cell-MBR frontier rows; the full public res4 pair remains matched and the
  same-rebuild route median improves from ~0.03279s no-inline control to
  ~0.02916s inline-nearest, with continuation candidate evaluations dropping
  from ~1.15M to 7354;
- Goal5173 adds an author-directed route mode that uses the Goal5126-proved
  directed input1-to-input2 author contract and avoids the extra B->A
  diagnostic direction in production-style timing; the full public res4 pair
  remains matched and route median is ~0.01536s;
- Goal5174 records the author-directed native inline-nearest route across the
  current same-source Stanford scale ladder. sample256/sample1024/sample2048/
  sample4096/res4full all match author HDResult with route medians
  ~0.00307s/~0.00582s/~0.00635s/~0.01063s/~0.01492s;
- no performance or full paper reproduction claim.

### M2. Native 3-D Backend Decision

Decide whether to implement a native 3-D cell-MBR broadphase/backend now.
Prerequisites:

- Goal5145 oracle exists;
- app-neutral native symbol naming;
- fail-closed overflow;
- no X-HD terminology in RTDL core.

### M3. Performance Only After Backend Exists

Do not run or publish X-HD performance comparisons until a real scalable route
exists and phase denominators are aligned.

The current scalable-route work has reached a useful diagnostic state:

```text
sample1024 author Running.AvgTime ~= 4 ms
sample256 RTDL production route ~= 0.009 s after Goal5164
sample1024 RTDL production route ~= 0.025 s after Goal5164
sample2048 RTDL production route ~= 0.025 s after Goal5164
sample4096 RTDL production route ~= 0.041 s after Goal5165
full public res4 RTDL production route ~= 0.034 s after Goal5170
full public res4 RTDL production route ~= 0.033 s after Goal5171
full public res4 RTDL production route ~= 0.029 s after Goal5172
full public res4 RTDL production route ~= 0.015 s after Goal5173
```

This is not a denominator-aligned ratio. The next performance work must target
route internals. After Goal5158, median profile evidence points first to native
frontier row production, then the vectorized seed. Goal5159 shows the frontier
problem is not primarily unused split-frontier materialization, and Goal5160
removes most pruned-row volume from the streaming route. Goal5161 removes the
post-5160 seed bottleneck with a generic Numba executor. The next
profile-driven target is now available from Goal5162: on sample2048, nearest
continuation over active frontier rows dominates the measured route. Goal5163
then moves that continuation to a generic Numba executor. The route is now
balanced enough that another fresh profile or a consolidated review node is
preferable to blindly attacking a stale bottleneck. Goal5164 records the
three-sample lock point, Goal5165 extends it to sample4096, and Goal5166 extends
it to the full public Stanford res4 pair. Goal5167 then removes avoidable
Python-loop overhead from generic grid cell-MBR construction. Goal5168 then
parallelizes the generic seed executor. Goal5169 then removes avoidable
streaming frontier output over-allocation. Goal5170 then parallelizes frontier
nearest continuation by query group. The next representative step is either
exact-dataset provenance if it becomes available or a deliberate
route-internal optimization selected from the new full-res4 phase table.
Goal5171 shows that removing the native sorted+unique pass is only a small win,
because the downstream continuation still has to group native-emission rows.
Further route work should either consume native row order more directly or stop
for consolidated review before pursuing smaller micro-optimizations.
Goal5172 consumes most inline rows natively by carrying nearest-witness payload
state through the generic native 3-D cell-MBR frontier collector. It lowers the
full public res4 route to ~0.029s, but the win is bounded because native
frontier work increases while downstream continuation shrinks. The next step is
best treated as a consolidated review node or a fresh phase profile, not another
stale-bottleneck guess.
Goal5173 then aligns the production route with the author-directed output
contract and removes the unneeded B->A diagnostic pass from production timing,
lowering full public res4 route time to ~0.015s. Symmetric diagnostic mode
remains available, so this is a route policy correction rather than deletion of
diagnostic capability.
Goal5174 then locks that author-directed route across sample256, sample1024,
sample2048, sample4096, and full public res4 in one same-POD matrix. The route
is now stable across the current Level B representative scale ladder; the next
step is either consolidated review or exact paper dataset/provenance progress,
not another ratio claim.

Goal5175 moves the exact-dataset question forward by extracting an author-log
workload manifest from the pinned X-HD repository. It parses 281 current
main-branch author logs and inventories a much larger `origin/paper` log tree
with 41755 JSON blobs. This turns the dataset blocker from "unknown" into a
concrete provenance map, but it does not remove the blocker: exact input bytes
and hashes are still missing.

Goal5176 then parses that `origin/paper:expr/for_the_paper/logs` tree through
git object access rather than ordinary checkout. It parses all 41755 paper
branch JSON blobs with zero parse errors, retains all 4535 `run_all` records,
and records 1946 unique input paths. This gives the project a paper-branch
workload matrix to map against figures/tables. It still does not provide input
bytes or hashes.

Goal5177 maps the paper target matrix onto the Goal5176 paper-branch `run_all`
logs. It shows that Figure 5 has the strongest workload-family log coverage,
Figures 6/7/9/10 are only partially covered because phase counters, load-balance
metrics, adaptive-grid semantics, or scale/overlap labels are missing, and
Figures 8/11 are not covered by `run_all` timing logs. The next exact-dataset
step should use one of the priority subsets, preferably
`graphics_dragon_happy_buddha` for a first paper-log-to-route rehearsal, while
keeping it Level B unless file/hash provenance appears.

Goal5178 bridges that first priority subset to local public Stanford
full-resolution files. The author paper-branch logs report `dragon.ply` with
437645 points and `happy_buddha.ply` with 543652 points; the local public
Stanford `dragon_vrip.ply` and `happy_vrip.ply` files have exactly those vertex
counts and recorded SHA256 hashes. This is now a concrete Level B large-input
candidate. It is still not Level C exact paper dataset identity because author
input hashes/bytes or deterministic conversion provenance are absent.

Goal5179 profiles that full public Level B candidate before any route run. It
records `237926579540` point pairs for Dragon/HappyBuddha and shows that even
16-byte materialized candidate rows would require about 3.8 TB. Therefore the
old exact pairwise route is not a viable next step. The next route milestone is
a bounded full-public-candidate feasibility gate that uses the scalable
seeded/frontier/inline-nearest route, fail-closed row capacities, and phase
counters. This remains Level B planning evidence, not Level C exact paper
dataset reproduction and not a performance ratio.

Goal5180 executes that first bounded feasibility gate locally. It loads the
full public Stanford Dragon/HappyBuddha files, selects 16 deterministic
evenly-spaced Dragon source rows, runs the scalable route against the full
543652-point HappyBuddha target, and matches a vectorized exact subset oracle
with `route_abs_diff=0.0`. It records 58518 frontier rows and 12741 total
candidate distance evaluations for the bounded subset. This is still not an
all-source route run, not native/POD fail-closed capacity validation, and not a
performance ratio. The next route milestone is a POD/OptiX or larger-subset
gate with explicit fail-closed row capacity.

Goal5181 extends the local bounded gate to source limits 16, 64, and 128
against the same full public target. All three cases match exact subset oracles
with `route_abs_diff=0.0`; the largest observed frontier row count is 526006,
which yields a planning capacity of 789009 for the next bounded POD/OptiX gate.
This still does not prove all-source completion. It narrows the next route
milestone to native/POD fail-closed capacity and larger-subset behavior.

## Long-Term

If X-HD is to become a full paper reproduction:

- exact paper datasets or acceptable same-source status must be settled;
- author-log workload paths/statistics must not be confused with exact input
  file identity;
- the paper-branch `run_all` workload matrix should be mapped to specific
  figures/tables before claiming figure-level reproduction (Goal5177 provides
  this map, but does not reproduce the figures);
- public Stanford Dragon/HappyBuddha full files can be used as Level B
  same-source candidates after Goal5178/Goal5179, but not as Level C exact
  paper inputs without author byte/hash or conversion proof;
- any full public Dragon/HappyBuddha route must use the scalable
  seeded/frontier/inline-nearest path; the naive materialized pairwise exact
  path is prohibited at this scale by Goal5179's 237,926,579,540-pair estimate;
- Goal5180 proves the scalable route can consume the full public target for a
  bounded source subset, but all-source completion remains unproved until a
  larger/POD capacity gate and then an all-source route gate pass;
- Goal5181 provides the first bounded scaling matrix and a concrete row-capacity
  planning number (`789009`) for the next POD/OptiX gate;
- author phase semantics must remain explicit;
- RTDL route must reproduce algorithmic behavior, not only exact pairwise value;
- performance matrix must separate author `Running.AvgTime`, process wall,
  RTDL setup, RTDL route, and output/comparator costs.
## LibRTS after Goal5488

The generic AABB columnar front door is implemented, locally tested, built on
the POD, and integrated into the app-owned exact point-contains gate. Exact
counts still match on `dtl_cnty` and `lakes.bz2`; the large old lakes prepare
phase was reduced from host packing overhead to under one second, but WKT
parsing remains the dominant app-side cost. Goal5489 is the immediate
same-process repeat matrix so first-use and prepared-query reuse are not
confused. Goal5489 now has matched `dtl_cnty` and `lakes.bz2` POD repeats.
The next bounded experiment is an app-owned NumPy numeric WKT loader; only
after its evidence should we consider a generic numeric geometry ingestion contract
only if it has a non-LibRTS consumer and preserves exact input hashes.

Goal5490 tested that numeric loader on `dtl_cnty` and recorded a no-go: exact
counts match but load time was neutral within separate-run noise. Do not run
the same variant on `lakes.bz2` solely to seek a favorable number. A future
loader direction needs a new parsing hypothesis or a pre-tokenized numeric
input contract, with RTDL core remaining WKT-free.

Current correction: the Goal5490 WKT-loader experiment is historical and
closed. No further WKT parser optimization belongs on the RTDL roadmap. The
system roadmap starts at format-neutral columns/buffers; paper-app parsing time
is retained only for honest end-to-end phase accounting.

Goal5491 validated the reusable-cache direction on exact `lakes.bz2`: a 286MB
SHA-bound column cache loads in `8.101s`, and the prepared query remains about
`0.218s` while preserving count agreement. The next work should define cache
portability/lifecycle only if another app needs it; do not promote LibRTS WKT
or cache semantics into RTDL core.

## Next LibRTS milestones after the approved 5485-5491 batch

1. **Input inventory gate**: inspect the verified archive inventory for exact
   range-contains, range-intersects, PIP, and mutation members. Do not create
   substitutes and do not start a route without an exact-input contract.
2. **Operation gate**: for any available exact pair, reuse the generic
   `Aabb2DColumns` front door and report only the output level the author
   exposes (count versus relation rows). Keep phase denominators separate.
3. **Cache lifecycle decision**: keep the SHA-bound cache app-owned by default.
   A formal RTDL cache API requires a second non-LibRTS consumer, a generic
   lifecycle contract, and a separate review gate.
4. **Closeout or next system extraction**: if no second consumer or exact
   operation input exists, close the LibRTS line as a successful generic AABB
   pressure test rather than adding app-shaped APIs.

POD expectation: the existing RTX 4000 Ada POD is sufficient. Exact WKT cache
construction on the 6.7GB lakes member costs several minutes once; subsequent
cache-backed runs are under a minute. No new GPU or Embree resource is needed.

## LibRTS after Goal5481

The exact official archive is acquired and the first exact Figure-6 workload
row matches by result count. Continue by extracting workload members in bounded
batches under the same archive-evidence contract. The next portfolio milestone
is an exact-input operation matrix (point-contains, range-contains,
range-intersects, then PIP/mutation where feasible), followed by a separately
reviewed phase-denominator decision. Embree remains excluded.

## LibRTS after Goals5492-5495

The verified archive inventory is complete for the current operation decision:
`14` point-contains pairs, `14` range-contains pairs, `42` range-intersects
pairs, and no exact PIP or mutation pairs. The exact `dtl_cnty` range-contains
gate matches the author count `117314` through the generic columnar AABB path.
The current point/range-contains line is closed. Next, run a separate exact
range-intersects count gate using the same archive/member/SHA contract. Keep
PIP and mutation fail-closed until exact pairs exist. Keep the cache app-owned
unless a second non-LibRTS consumer justifies a generic lifecycle API. Do not
add Figure 6/full-paper/performance claims or reintroduce Embree.

## LibRTS after Goal5496

The exact range-intersects `dtl_cnty` gate now matches author and RTDL count
`1,570,285` on the same archive-derived files. The author configuration is
explicitly `load_factor=1` because `0.0001` failed with a CUDA invalid-program-
counter error on this POD. Keep the result count-only and review pending. The
next work is either an independently reviewed batch extension over the other
exact range-intersects pairs or a closeout of the current exact AABB operation
line. Do not infer pointwise relation equality or performance parity.

## LibRTS after Goal5497

The exact range-intersects line now has two matched `dtl_cnty` query cases at
different selectivity settings. Keep the batch count-only and review pending.
The next decision is whether the two-case matrix is sufficient for a bounded
operation closeout or whether another exact geometry/query pair adds material
coverage. Do not turn the batch into a Figure 6, full-paper, relation, or
performance claim.

## LibRTS after Goal5498

The bounded exact AABB operation line is closed through range-intersects with
two matched `dtl_cnty` query cases. Forty exact archive pairs remain queued;
choose explicitly between another bounded batch and stopping this line. Do
not promote the two-case result to a full operation matrix. PIP and mutation
remain input-blocked, and the cache remains app-owned.

## LibRTS after Goal5499

The bounded exact range-intersects matrix now has three matched query cases
for one geometry. Forty exact archive pairs remain unexecuted. Decide whether
to run a final representative pair, or close the bounded line and preserve
the remaining pairs as a future queue. Keep all evidence count-only.

## LibRTS after Goal5500

The next milestone is mismatch diagnosis, not route tuning. Goal5500 attempted
six exact official range-intersects pairs across six geometry families: three
matched counts, two count disagreements, and one author-side CUDA OOM. First
separate input/parser/float32/padding/intersection-contract causes with generic
or relation-level evidence; then decide whether a bounded correction or a
fail-closed capacity strategy is justified. Keep all complete-matrix,
pairwise, performance, Figure 6, full-paper, zero-copy, and Embree claims
closed until separately supported.

External review approved the Goal5492-5500 bounded packet. The next milestone
is Goal5501 mismatch diagnosis. It must use a generic/reference oracle to
separate RTDL behavior from author-contract differences before any broader
range-intersects claim or closeout. The current partial result remains the
authoritative state.

## LibRTS Goal5501 closeout

Goal5501 completed the mismatch diagnosis and closes this project at a bounded
evidence boundary. RTDL matches CPU float32 on all three feasible prefixes;
author differences remain on the two parks prefixes, and the full `parks.bz2`
author run remains OOM. No further LibRTS implementation goal is implied.
Future work must first define a new question: full-input execution-contract
alignment, author pair-row access, or an explicitly authorized capacity
campaign. Do not reopen route tuning or promote the prefix result to a full
paper or complete-matrix claim.

## LibRTS Goal5502 author-validity gate

The owner rule is now executable: compare author and RTDL to an independent
generic contract before changing the system. Goal5502 classifies the current
prefix evidence as RTDL/oracle agreement on all five cases, with author
divergence on four. This closes the immediate decision loop without changing
RTDL. Full-input adjudication remains a new scope requiring stronger evidence;
do not reopen the bounded line merely to chase an author discrepancy.

## LibRTS Midterm Review Before Goals5503-5508

The next project stage is deliberately gated by one consolidated review. The
plan starts with author contract semantics and independent oracle strength,
then addresses full-input capacity, and only then decides whether any generic
RTDL fix is justified. No performance campaign or author-specific core change
is implied before that decision.

Goal5503 completed the first stage: the author GPU contract is now source
audited. Goal5504 and Goal5505 then established a one-ULP source distinction
and validated the source model against a real POD runtime. If broader evidence
does not establish a single contract, close or narrow the LibRTS line; do not
tune RTDL or copy author behavior merely to erase count disagreements.

Goal5505 obtained the first runtime evidence. The source model matches the
author on five boundary queries; pre-fix RTDL differs on the committed WKT
`one_ulp_gap_after_box_max` case. The next milestone is Goal5506 scalable
relation/oracle evidence, or a deliberate bounded closeout if no generic
contract can be validated. Full-input capacity and any semantic fix remain
gated.
Goal5506 expanded the same-input runtime evidence to 8,192 pairs and preserved
the same result: source model/author 21, CPU inclusive/RTDL 20. The next
milestone is Goal5507, a decision gate for full-input validity or bounded
closeout. Goal5507 now supplies a generic, source-audited float32/two-direction
native correction: clean POD evidence is author/source/RTDL 5/5 and 21/21,
with no duplicate rows. Official-archive adjudication, performance, and full
paper claims remain closed pending a separate scope decision.

## LibRTS Goal5508

Goal5508 resolves the two previously disagreeing official prefixes. The
author/RTDL float32 MBR fingerprints match; four post-conversion-degenerate
indexed records per prefix account for the entire excess. A generic,
pass-correct strict-validity guard now makes those indexed records
non-matchable. Clean POD results match author on parks (`34,240,217`) and lakes
(`34,581,812`), and the isolated subsets both return zero. The remaining
official archive pairs, pair-row equality, full matrix, performance, and paper
claims remain separate and unclaimed. External review is the next gate.

## LibRTS Goal5509

The second exact range-intersects query family produced four new count-level
author/RTDL matches on the Goal5508 generic native route. Two large cases did
not checkpoint before a batch process resource termination and remain
unresolved. Continue with per-case checkpoints or explicitly close the
capacity branch; do not infer semantic mismatches from missing outputs.

## LibRTS Goal5511

The next exact query family, `range-intersects_select_0.001_queries_10000`,
now has four independent same-input count matches on the verified archive.
The next decision is not another blind batch: either retry the two Goal5509
large cases with a resource-aware per-case runner, or select additional exact
archive pairs. Any broader claim remains gated on coverage, relation-level
output availability, and external review. Embree remains out of scope.

## LibRTS Goal5512

The two Goal5509 large-case states are resolved: lakes matches at count level;
parks is blocked by the pinned author's CUDA allocation failure. The next
choice is remaining exact archive coverage or a separately authorized parks
capacity investigation. Do not reopen RTDL semantic tuning from this author
capacity result, and keep the full matrix, pair rows, performance, and paper
claims closed.

## LibRTS Goal5514

The exact `.01` range-intersects family is bounded-closed across all six
geometries: five count matches and one author CUDA capacity failure. The next
work, if authorized, is a new query family or relation-level/API question;
there is no unresolved state inside this family, and no permission to call it
the full 42-pair matrix or Figure 6.

## LibRTS Goal5513

Four `.01` exact range-intersects cases now match at count level. The next
choice is additional exact-family coverage versus a bounded review/closeout
node. Any next batch must keep per-case checkpoints, use `/tmp` when workspace
quota interferes, and keep pair-row, performance, Figure 6, and full-paper
claims closed.

## Post-v2.14.4 Baseline (2026-07-13)

No paper-app line is active. RayJoin, RT-BarnesHut, RT-DBSCAN, X-HD, and LibRTS
are closed at their reviewed bounded scopes. The next paper app must begin from
the `v2.14.4` source-tree tag, define input/output and claim boundaries before
implementation, reuse existing generic APIs first, and pass the stop-loss gate
before any author-internal artifact parity campaign.

## V4 after Goal5749 (2026-08-11)

The bounded backend/link/effect feasibility falsifier passed and both review
P1s are closed. The next possible goal is Goal5750: production stage-aware
Callback IR, fail-closed verifier and deterministic CPU interpreter. It is not
authorized by Goal5749. Goal5750 must explicitly select and justify the
production linkage mechanism. Goal5751 codegen/pipeline work, Goal5752 partner
composition, held-out generalization, nine-app migration and performance remain
later, separately gated work.
