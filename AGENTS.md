# RTDL Codex Working Guide

This file is the first-stop guide for Codex or any other coding agent working in
this repository. Read it before making changes, then read the files under
`memory/`.

## Durable Memory Protocol

Important project state must live in repository files, not only in a chat
thread. At the start of a session, read:

```text
AGENTS.md
memory/project-facts.md
memory/architecture.md
memory/decisions.md
memory/progress.md
memory/todo.md
memory/known-bugs.md
memory/roadmap.md
```

At any meaningful handoff or major goal boundary, update the relevant `memory/`
files before stopping:

- `architecture.md`: current system architecture and app/core ownership;
- `progress.md`: what was actually implemented, measured, and verified;
- `decisions.md`: durable architectural or claim-boundary decisions;
- `todo.md`: next concrete work, stale TODO removal, and review debt;
- `known-bugs.md`: recurring failure modes and how to avoid them;
- `roadmap.md`: only when the project direction changes.

Do not treat conversation history as the source of truth when a memory file or
goal report exists. If they conflict, inspect the files and report the conflict.

For long-running paper-reproduction work, this protocol is mandatory rather
than optional. Any fact that would be expensive to rediscover after a new Codex
session must be written into `memory/` or a goal report before handoff:

- current best numbers and their exact regime;
- claim boundaries and forbidden summaries;
- active POD endpoint / wrapper rule;
- next concrete goal and the reasons old alternatives were rejected;
- implemented-but-review-pending status.

Never rely on "the previous chat probably has it" for these items.

## Project Identity

RTDL is a general spatial language/system. Paper reproduction apps are evidence
and pressure tests for the language; they must not turn RTDL core into a
single-paper or single-app codebase.

Core principle:

```text
RTDL core exposes generic spatial/dataflow primitives.
Paper apps own paper-specific inputs, wrappers, comparators, formatting,
tolerances, and claim boundaries.
```

## Current Workstream

No paper-app implementation line is active. LibRTS received an unconditional
external approval for Goals5519-5525 on 2026-07-13 and is closed at `scoped
correctness and system extraction complete`. X-HD is a completed historical
line at its owner-approved same-input directed-HDResult boundary.

Closed LibRTS record:

- Goal5453 pins the PPoPP 2025 paper, author repository/commit, Zenodo artifact,
  and a five-row local CPU reference fixture;
- Goal5454 runs that same tiny input through pinned author RTSpatial/OptiX and
  RTDL OptiX on local Linux. Both report count `5`; RTDL also emits all five
  exact expected rows. The author example is count-only, so author pair-row
  equality is not claimed;
- Goal5455 adds a direction-discriminating range-contains fixture: correct
  indexed-box-contains-query count is `5`, reversed direction is `2`, and both
  author/RTDL OptiX report `5`;
- Goal5456 adds predicate-discriminating range-intersects: intersects count is
  `8` versus contains `5`; author/RTDL counts match and RTDL emits all 8 native
  rows;
- Goals5457-5459 add an app-neutral mutable AABB index with stable IDs and
  atomic snapshot rebuilds, validated on CPU and Linux OptiX. It explicitly
  does not claim native incremental mutation;
- Goal5460 runs the same insert/update/delete/insert/clear sequence through the
  patched-author public API and RTDL OptiX. Both produce counts
  `[2,1,0,1,0]` and append ID `2`. The author uses native GAS/IAS update while
  RTDL rebuilds snapshots, so execution/performance parity is not claimed;
- Goals5461-5462 add generic OptiX sparse-slot native refit for pure Update.
  Same-host GTX1070 diagnostics measure about `12.62x` at 4,096 boxes and
  `15.63x` at 65,536 boxes versus RTDL full snapshot rebuild. Insert/Delete/
  Clear still rebuild; these are RTDL system microbenchmarks, not paper or
  author-performance results;
- Goal5463 closes the sparse-refit review amendments: the call-for-review now
  reports the evidence-backed `12.62x` / `15.63x`, Linux hardware fault
  injection verifies old records/GAS recovery after a post-update fault, and a
  rollback failure poisons the prepared handle so later operations fail closed.
  Goals5461-5463 are externally reviewed and approved;
- Goals5464-5465 add a bounded same-input PIP gate from the exact author AE
  source chain. Author and RTDL OptiX both report `4` polygon-refined hits; RTDL emits
  all four expected rows, while the fixture has `5` MBR-only candidates.
  These goals are implemented / external review pending;
- Goals5466-5467 add a Level-B representative PIP gate with 64 public-source
  Block Group polygons and 100K points from the pinned author generator. The
  unmodified author, instrumented author comparator, and RTDL app-compatible
  route all produce 71,626 rows; complete pair-row hashes match. Standard RTDL
  PIP semantics produce 71,624 and that difference remains disclosed. These
  goals are implemented / external review pending;
- Goals5468-5469 pin the paper/source Ray-Multicast mechanism and add a generic
  `partitioned_traversal` Python reference contract. A Contact-Manifold-style
  broad-phase test proves complete pair coverage and non-LibRTS reuse. Native
  OptiX execution and runtime speedup are not implemented; one bounded POD
  spike is authorized only after strict review;
- the pinned author artifact needs a disclosed one-line update-buffer fix:
  `updateInstanceAccel` allocates `tempUpdateSizeInBytes` but originally passes
  `tempSizeInBytes` to OptiX;
- no LibRTS paper performance claim exists. The next recommended milestone is
  strict review of Goals5468-5469, followed by the bounded generic OptiX
  partitioned-traversal POD spike if approved;
- until a POD is available, use `lestat@192.168.1.20` for Linux functional
  validation. Treat its GTX 1070 as smoke hardware, not paper-performance
  evidence;
- Embree is explicitly out of scope for the entire LibRTS campaign. Do not
  build, test, compare, or report Embree evidence. HIPRT is also inactive.

Historical X-HD status:

Key status:

- bounded X-HD same-input value reproduction is complete and externally
  reviewed through Goal5126;
- generic nearest/witness/reduction extraction is complete through Goals5127
  and 5128;
- full paper reproduction is not complete because exact paper datasets are not
  available;
- Level B Stanford Dragon/HappyBuddha evidence is now the strongest current
  representative line;
- Goal5186 runs author `hd_exec` on the full public Dragon/HappyBuddha pair and
  matches the paper-branch author-log HDResult;
- Goal5187 runs the RTDL scalable all-source route on that same public pair and
  matches the author HDResult;
- Goal5188 records the full-public phase-boundary matrix and refuses a
  performance ratio because author internal timing, author process wall, RTDL
  route, and RTDL total are different denominators;
- Goal5189/5190 tested generic seed strategies; local-grid is faster than
  grid-branch-bound on the full-public Level-B route;
- Goal5191 raises the generic native inline-nearest threshold to consume all
  frontier rows and adds a fail-closed empty-frontier passthrough; current best
  Level-B route wall is about `3.65s`;
- Goal5192 adds optional native inline-nearest telemetry; the same route
  performs about `1.24B` inline point-distance evaluations inside OptiX payload
  code, so the remaining native collector floor is real inline work rather than
  Python continuation or row materialization;
- Goal5193 tested a generic bounded grid-cell seed and intermediate inline
  thresholds; both matched author HDResult but did not beat local-grid +
  inline512, so the current default remains unchanged;
- Goal5194 fixed native inline-nearest pruning to use the updated payload
  current best instead of only the initial query seed; full-public Level-B route
  still matches author HDResult, warmed route wall is about `3.46s`, and
  telemetry inline point evaluations drop from about `1.24B` to `0.40B`;
- Goal5195 moved the same payload-current-best prune into the native
  intersection stage before `optixReportIntersection` for inline-nearest /
  no-pruned-row mode; full-public Level-B route still matches author HDResult,
  warmed route wall is about `2.6s`, and native frontier / inline time is about
  `0.93-0.94s`;
- Goal5196 changed the generic grid-cell seed occupied-cell lookup from
  repeated binary search to a dense encoded-cell position table with fallback
  for local-grid, grid-cell-budget, and grid-branch-bound seed helpers;
  full-public Level-B route still matches author HDResult, dense local-grid
  route wall is about `2.26s`, and dense budget / branch-bound controls do not
  beat it;
- Goal5197 carries intersection-computed `min_sq` into any-hit via OptiX
  attributes and computes row-only distances lazily; full-public Level-B route
  still matches author HDResult and remains about `2.25-2.28s`, so this is a
  generic cleanup / neutral optimization rather than a new speedup headline;
- Goal5198 measures grid-shape telemetry and keeps 32^3 as the current default:
  24^3 fails the empty-frontier route at capacity 0, while 48^3/64^3/128^3
  match but are slower despite reducing inline point evaluations;
- Goal5199 tests a generic trace-tmax bound in the native OptiX cell-MBR
  traversal and records a no-go: correctness still matches, but inline cell hits
  and point evaluations are unchanged and route wall does not improve; the
  temporary code change was reverted;
- Goal5200 tests an explicit experimental generic native CUDA executor for the
  local-grid seed and records a no-go: correctness, POD build, focused tests,
  and a small native call pass, but same-POD full-public route wall worsens
  (`2.436s` native CUDA vs `2.258s` auto/Numba), so the default remains
  auto/Numba;
- Goal5201 instruments the generic native 3-D cell-MBR frontier collector and
  records that route-level `frontier_rows ~= 0.920s` contains native frontier
  total `~= 0.600s`, native OptiX launch / inline-nearest work `~= 0.377s`, and
  native accel build only `~= 0.0004s`;
- Goal5202 adds generic packed coordinate matrix reuse for point-column front
  doors; the full-public Level-B route still matches author HDResult and the
  no-timing route wall is about `2.027s` versus the Goal5200 auto/Numba control
  at about `2.258s`;
- Goal5203 changes the X-HD app-owned public PLY input front door to load
  directly into NumPy coordinate matrices; the full-public Level-B route still
  matches author HDResult and the route wall is about `1.238-1.239s`;
- Goal5204 makes the generic max-nearest reducer linear for finite distances
  by sorting only the maximum-distance tie set; the full-public Level-B route
  still matches author HDResult and the route wall is about `1.17-1.18s`;
- Goal5205 changes the app-owned public ASCII PLY input loader to use NumPy
  column loading instead of Python per-line tuple parsing; the same route still
  matches author HDResult, `load_full_inputs` is about `0.68s`, full gate total
  is about `2.06s`, and route wall remains about `1.16-1.17s`;
- Goal5206 records a first-use vs same-process warm diagnostic: one-shot route
  remains about `1.16-1.17s`, while a near-identical second case in the same
  process is about `0.61s`; this is a regime diagnostic only and must not
  replace the fresh headline;
- Goal5207 adds an explicit app-owned route warmup protocol:
  `--route-warmup-source-limit` records warmup separately and excludes it from
  measured summary statistics; current all-source warm measured route is about
  `0.626s` after a reported warmup case total of about `1.389s`;
- Goal5208 tested lower native inline-nearest thresholds under the explicit
  warmup protocol and records a no-go: 384 is noise-level and worsens the full
  warmup-including run, while 256/128 are slower because frontier rows and
  continuation work return; keep `max_inline_points=512`;
- Goal5209 tested static generic cell primitive ordering by point count and
  records a no-go: `point-count-asc` moves route median by only about 1.4ms and
  does not improve case-total median, while `point-count-desc` is slower; keep
  native cell order;
- Goal5210 disables closest-hit in the generic cell-MBR frontier OptiX raygen
  because that pipeline has no closest-hit program; correctness is preserved,
  but same-POD repeats show no material route or OptiX-launch speedup, so treat
  it as neutral semantic cleanup rather than a performance win;
- Goal5211 implements a generic global-bound early-break experiment for
  directed-Hausdorff/max-nearest reductions. It preserves the Goal5186 author
  HDResult and improves the Level-B Dragon/HappyBuddha route (`~0.849s` fresh
  route, `~0.362s` explicit-warm route median). It remains review pending and explicit: early-aborted per-source
  witnesses may be approximate, so this is a max-nearest/directed-HD contract,
  not a default for generic exact nearest-witness APIs.
- Goal5212 removes all-source subset materialization in the full-public runner;
  with Goal5211 enabled, fresh full total including load is about `1.531s`, and
  explicit-warm measured case total is about `0.288s`. This is app-runner
  hygiene, not native route speedup.
- Goals5272-5277 move Figure 11 memory from vague "missing accounting" into a
  status-bearing decision: author-side Figure 11 memory logs are extracted,
  RTDL has bounded native telemetry for OptiX GAS output bytes, but author `WL`
  is in/miss queues and author `WL Heavy Peak` is a heavy-cell offload peak.
  Current RTDL `WL` is generic frontier row-table capacity and has no
  author-like heavy offload peak, so `same_denominator_author_figure11=false`
  and Figure 11 remains not reproduced.
- Goal5279 implements the first generic system primitive for that Figure 11
  gap: `heavy_offload_worklist_numpy_columns` plus generic active/miss/deferred
  row schema and queue/peak telemetry at CPU-reference level. It is
  implemented but review pending, and native/POD peak telemetry still does not
  exist.
- Goal5280 adds a non-X-HD retry/backlog consumer for that generic worklist
  helper; it is implemented but review pending.
- Goal5281 adds the first native/POD v2 telemetry ABI for generic offload
  frontier rows. POD evidence shows both v1 and v2 symbols are exported and a
  tiny native route reports schema-v2 telemetry with six offload rows and
  96 peak queue bytes. It is implemented but review pending, and still does not
  reproduce X-HD Figure 11 or authorize author memory parity.
- Goal5282 maps that generic v2 telemetry into author-shaped X-HD fields:
  OffloadingSize row-count shape is available, and an author-width WL Heavy
  Peak candidate can be computed, but same-denominator Figure 11 remains false
  because RTDL measured queue bytes use 64-bit id pairs and RTDL WL is not the
  author's in_queue + miss_queue. It is implemented but review pending.
- Goal5283 closes the current Figure 11 line as
  denominator-not-aligned after native mapping. There is a shape-only offload
  candidate, but it is not a paper Figure 11 row and no memory ratio is
  authorized. Reopen Figure 11 only with a denominator-aligned generic native
  worklist or external review accepting a different memory question.
- Goal5284 maps the author paper-branch `run_all/auto_tune` logs for Figure 9.
  The logs contain 1814 `auto_tune` records over 907 pairs, with exactly two
  observed config labels and `Running.num_points_per_cell = 8` throughout.
  They are useful author-log semantics evidence, but they do not contain a
  multi-value grid-size sweep or paper-selected grid-size choices, so Figure 9
  remains not reproduced.
- Goal5285 audits the pinned author paper-branch Figure-9-like source/scripts:
  `effective_autoune.py` expects four auto-tune variants and saves
  `auto-tune.pdf`, but current `run_all/auto_tune` logs contain only two
  variants. `logs/train` sweeps exist, but they are a different denominator and
  must not be promoted to Figure 9 reproduction without an externally reviewed
  mapping.
- Goal5286 audits all pinned author branches for the missing Figure 9 variants:
  `paper` still has only the same two `run_all/auto_tune` configs and a
  checked-in `auto-tune.pdf`, while `main` and `hybrid` have no Figure-9-like
  logs/scripts/PDF. A checked-in PDF is evidence, not a reproducible RTDL/author
  denominator.
- Goal5287 closes the current Figure 9 line as
  `figure9_closed_current_line_author_denominator_missing`: the plot script
  expects four variants, current logs provide two, main/hybrid do not recover
  the missing variants, the checked-in PDF is not a reproducible denominator,
  and training sweeps require an externally reviewed mapping before use.
- Goal5288 audits Figure 5 timing denominators: author run_all logs cover 2535
  records / 507 complete pairs across BraTS, geo, and graphics, but current RTDL
  evidence lacks BraTS and geo full gates and author `Running.AvgTime` /
  `ReportedTime` is not the same denominator as RTDL route/process wall. Figure
  5 remains not reproduced and no speedup ratio is authorized.
- Goal5289 runs a bounded same-POD Figure 5 graphics probe on the currently
  available Dragon -> AsianDragon scaled-1e-3 candidate. The POD is reachable
  through the wrapper, author `hd_exec` runs, and RTDL runs on the same POD, but
  author X-HD/LB=256 returns `0.06545527279376984` while the RTDL exact route
  returns `0.06536787240753439` (`matched_value=false`). This candidate is a
  no-go for Figure 5 performance comparison and no ratio is authorized.
- Goal5290 performs the cheaper author-only value precheck for the same Figure
  5 graphics pair. The paper log target is `0.06536811590194702`; the available
  POD unscaled AsianDragon author run returns `52.4535`, and the scaled-1e-3
  variant returns `0.0654553`. Neither matches, so do not spend RTDL timing on
  this candidate again unless exact input provenance or a new value-matched
  variant appears.
- Goal5291 consolidates the Dragon -> HappyBuddha Figure 5 graphics candidate.
  Paper log `HDResult=0.12572969496250153`, author rerun
  `0.12572988867759705`, and RTDL route `0.12572988629271128` match within
  `1e-6`, so this is the strongest current Figure 5 graphics Level-B
  value-matched candidate. It is still not exact paper dataset reproduction,
  not the full Figure 5 matrix, and no author-vs-RTDL performance ratio is
  authorized because timing denominators differ.
- Goal5292 audits Figure 7 load-balance / heavy-cell offload source and logs.
  The pinned author source has `run_lb.sh` and `draw_lb.py`, and checked-in
  `run_all/rt_gpu` logs have LB=256 profiling-style fields, but the checked-in
  `lb_comparison` matrix has zero JSON files and there is no LB=0 counterpart.
  Figure 7 remains not reproduced; RTDL comparison should not start until an
  author `lb=0`/`lb=256` matrix is regenerated or a separately named Level-B
  diagnostic is approved. Goal5292 is implemented / review pending.
- Goal5293 audits Figure 8 radius-growing strategy source and logs. The pinned
  author source has `run_radius_tuning.sh` and `draw_tune_radius.py`, aligned on
  add/double/adaptive strategies and geo/graphics categories, but checked-in
  `logs/tune_radius` has zero JSON records and the paper-branch `run_all`
  mapping has no Figure 8 radius-strategy records. Figure 8 remains not
  reproduced; RTDL comparison should not start until the author
  add/double/adaptive matrix is regenerated or a separately named Level-B
  diagnostic is approved. Goal5293 is implemented / review pending.
- Goal5294 audits Figure 10 scalability / overlap source and logs. The pinned
  author source has `run_scalability.sh` and `draw_scalability.py`, aligned on
  size and translate/overlap sweeps over `all_nodes.wkt`, but checked-in
  `logs/scalability` has zero JSON records. The paper-branch `run_all` mapping
  has 4535 workload-family records, but no Figure 10 scale/overlap subset
  labels or overlap diagnostics. Figure 10 remains not reproduced; RTDL
  comparison should not start until the author size/translate matrix is
  regenerated or a separately named Level-B scalability/overlap diagnostic is
  approved. Goal5294 is implemented / review pending.
- Goal5295 checks whether the current POD can regenerate the missing Figure
  7/8/10 author matrices. The POD wrapper preflight succeeds and the author
  build exists, but `/local/storage/shared/HDDatasets` is missing, along with
  all required graphics/geo/all_nodes inputs. Only a partial Dragon/Asian
  temporary subset is present. Therefore exact author regeneration for Figures
  7/8/10 is blocked on the current POD; the POD is usable, but the author
  dataset root is absent. Goal5295 is implemented / review pending.
- Goal5296 uses that partial temporary Dragon/Asian input only as a separately
  named Level-B author-side load-balance diagnostic. Author `hd_exec` returns
  identical HDResult for `lb=0` and `lb=256` (`52.453487396240234`), but on
  this single run `lb=256` is slower by `Running.AvgTime` (`131.841ms` vs
  `107.254ms`) and process wall (`17.09s` vs `16.25s`) despite reducing
  iteration-3 compared points. This is not Figure 7 reproduction, not RTDL
  comparison, and not a performance ratio. Goal5296 is implemented / review
  pending.
- Goal5297 creates the X-HD dataset acquisition manifest. The current POD is
  usable but lacks `/local/storage/shared/HDDatasets`; local workspace has
  public Stanford graphics candidates for Dragon, HappyBuddha, AsianDragon, and
  ThaiStatuette with recorded hashes. These files can advance Level-B
  same-source graphics diagnostics after upload, but they are not exact paper
  datasets. BraTS, Census/TIGER, and OSM remain acquisition/provenance blocked.
  Recommended next goal: upload missing public Stanford graphics files to POD
  via `scripts/current_pod_ssh.py` and run author-only Level-B graphics value
  prechecks before any new RTDL comparison. Goal5297 is implemented / review
  pending.
- Goal5298 uploads the missing public Stanford graphics files to the current
  POD and runs author-only Level-B graphics value prechecks. Three cases match
  paper-branch author-log HDResult within `1e-6`: Dragon->HappyBuddha,
  ThaiStatuette-scaled->HappyBuddha, and ThaiStatuette-scaled->AsianDragon-
  scaled. Dragon->AsianDragon-scaled remains a no-go (`0.0654552728` vs paper
  log `0.0653681159`, diff `~8.7e-5`). Goal5298 does not run RTDL and does not
  authorize figure reproduction, exact dataset status, or performance ratios.
  Goal5298 is implemented / review pending.
- Goal5299 runs RTDL on the Goal5298 value-matched ThaiStatuette-scaled ->
  HappyBuddha case. Both `cell-mbr-exact-witness` and `cell-mbr-fast-scalar`
  match the author rerun scalar HDResult within `1e-6` (`abs diff ~= 6.3e-9`).
  Exact-witness route wall is about `5.00s` with `per_source_witness_exact=true`;
  fast-scalar route wall is about `1.00s` but has
  `per_source_witness_exact=false` because global-bound early-break leaves most
  per-source witnesses approximate. No author-vs-RTDL ratio, figure
  reproduction, exact dataset status, or author RT-core equivalence is
  authorized. Goal5299 is implemented / review pending.
- Goal5300 runs RTDL on the Goal5298 value-matched ThaiStatuette-scaled ->
  AsianDragon-scaled case. Both routes match the author rerun scalar HDResult
  within `1e-6` (`abs diff ~= 1.1e-8`). On this workload exact-witness is
  faster (`~10.76s` route wall, `per_source_witness_exact=true`) than
  fast-scalar (`~12.51s`, `per_source_witness_exact=false`) because
  fast-scalar produces `~4.66M` frontier rows and spends most time in nearest
  continuation. This is Level-B same-source scalar evidence only; no ratio,
  figure reproduction, exact dataset status, or author RT-core equivalence is
  authorized. Goal5300 is implemented / review pending.
- Goal5301 consolidates non-graphics X-HD dataset provenance. It does not run
  POD, author code, or RTDL code; the blocker is input identity/acquisition.
  Exact paper inputs still require file/hash provenance or deterministic author
  regeneration, not count/Gini matching. BraTS is access-gated, OSM
  Lakes/Parks/AllNodes are public but snapshot/filter/scale blocked, and
  Census/TIGER-like public geo inputs are the best next non-graphics target.
  Goal5301 is implemented / review pending.
- Goal5302 resolves the first Census/TIGER-like geo source plan. Author
  `run_fig5.sh` uses `dtl_cnty.wkt -> uszipcode.wkt` and
  `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` as
  2D WKT inputs with `normalize=false`; the author WKT loader emits polygon
  outer-ring vertices, linestring vertices, and points. Probe-verified
  TIGER2023 candidates exist for national COUNTY and ZCTA520; BG and AREAWATER
  are shard-based from the evidence here. County-ZCTA is the recommended first
  executable Level-B geo candidate. Goal5302 is implemented / review pending.
- Goal5303 creates the first bounded County-ZCTA WKT input artifact using
  ArcGIS name-matched County and ZIP/ZCTA FeatureServer exports. It writes
  one-geometry-per-line WKT files plus hashes and author-loader outer-ring
  point-count estimates. This is Level-B ingestion/conversion evidence only:
  the first County rows are Alabama counties and the first ZIP/ZCTA rows are
  Alaska ZCTAs, so it is not geographic representativeness, exact paper input,
  author/RTDL correctness, Figure 5, or performance evidence. Goal5303 is
  implemented / review pending.
- Goal5304 runs author `hd_exec` on that Goal5303 bounded WKT fixture on the
  current POD. Author ingestion succeeds with `HDResult=65.44752502441406`,
  point counts `38034/50272`, and `Running.AvgTime=6.169ms`. This is
  author-only Level-B ingestion evidence and remains implemented / review
  pending.
- Goal5305 runs RTDL on the same bounded County-ZCTA WKT fixture using the
  generic partner route `directed_max_of_nearest_distance_2d_partner_columns`
  with `partner="triton"` and `triton_strategy="dense_point_nearest_tiled"`.
  It matches the Goal5304 author scalar result: RTDL
  `65.44751976280666` vs author `65.44752502441406`, absolute difference
  `5.2616073986655465e-06 <= 1e-5`, point counts `38034/50272`.
  This is Level-B bounded same-fixture scalar correctness only; no exact geo
  dataset, Figure 5, author RT-core equivalence, performance ratio, or
  full-paper claim is authorized. The initial Numba partner attempt failed on
  this POD due to PTX/JIT compatibility (generated PTX 8.7, available path
  accepts PTX 8.4); treat that as a POD toolchain no-go, not a semantic
  mismatch. Goal5305 is implemented / review pending.
- Goal5306 creates the second bounded geo WKT fixture for
  `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` using
  ArcGIS name-matched WaterBodies and BlockGroups FeatureServer exports. It
  requests the first 5 features of each service by OBJECTID and records
  author-loader point-count estimates `124/894`. It is fixture evidence only,
  not exact paper input or Figure 5 reproduction. Goal5306 is implemented /
  review pending.
- Goal5307 runs author `hd_exec` and RTDL on the Goal5306 bounded
  WaterBodies->BlockGroups fixture. It matches the author scalar result:
  RTDL `72.38664516014835` vs author `72.38665008544922`, absolute difference
  `4.925300871150284e-06 <= 1e-5`, point counts `124/894`. This is Level-B
  bounded same-fixture scalar correctness only; no exact geo dataset, Figure 5,
  author RT-core equivalence, performance ratio, or full-paper claim is
  authorized. Goal5307 is implemented / review pending.
- Current geo status: both X-HD Figure-5 WKT pair names now have bounded
  author/RTDL scalar matches, but neither has exact paper input provenance or a
  denominator-aligned performance claim.
- Goal5308 records the geo exact/full-public decision: exact author WKT paths
  are known from paper logs but unavailable locally and on the current POD.
  Paper-log point counts are much larger than the bounded fixtures
  (`9,438,045/43,952,878` for County-ZCTA and
  `22,818,694/52,271,340` for WaterBodies-BG). Figure-5 and exact-input claims
  remain blocked. Goal5308 is implemented / review pending.
- Goal5309 fully probes the four name-matched full-public ArcGIS services for
  author-loader point counts and MBRs. All MBRs match paper logs to <1e-5
  degrees. ZCTA, WaterBodies, and BlockGroups point counts are very close to
  paper logs, but County has `12,477,179` points vs paper `9,438,045`
  (+32.2%), so County-ZCTA cannot be promoted to exact/Figure-5 status.
  WaterBodies-BlockGroups is the strongest full-public geo candidate
  (`+6,129` and `+127` points), but still lacks exact file/hash provenance.
  Goal5309 is implemented / review pending.
- do not repeat lower-threshold, static cell-order, scalar ray-extent, or
  trace-flag tuning without a changed execution model or new evidence, and do
  not prioritize prepared cell-MBR accel-build caching without new evidence.

## Claim Discipline

Never claim:

- full paper reproduction unless exact inputs, author contract, RTDL route, and
  review gates all support it;
- performance parity unless denominator, hardware, dataset, phase boundary, and
  runtime regime match;
- native backend completion when only a reference/front-door route exists;
- app-specific code as a generic RTDL system improvement.

Always distinguish:

- bounded same-input correctness;
- same-source representative correctness;
- exact paper dataset reproduction;
- author internal `Running.AvgTime` / `ReportedTime`;
- process wall time;
- RTDL route time;
- cold process vs warm long-lived process vs prepared replay.

## Important Directories

```text
src/rtdsl/                         RTDL public/system APIs
src/native/                        native backends
tests/                             regression and goal tests
Paper-reproduction-apps/           paper reproduction apps, app-owned wrappers
history/internal_docs/             goal reports, reviews, call-for-review docs
memory/                            durable project memory for future sessions
scripts/                           local/remote helper scripts
```

## Remote POD Rule

Do not use naked SSH for POD work. Use:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

The wrapper pins the current POD key:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Before declaring a POD broken or blocked, run the wrapper preflight. The recent
Goal5144 failure was caused by using the wrong local SSH key, not by a bad POD.

## Testing Expectations

Prefer focused tests for the touched goal, plus nearby regression tests. Example
for the current X-HD cell-MBR line:

```text
py -m unittest \
  tests.goal5145_dimension_generic_cell_mbr_frontdoor_test \
  tests.goal5144_cell_mbr_backend_assisted_gate_runner_test \
  tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5138_generic_grid_cell_candidate_api_test
```

On this Windows setup, `py` may print:

```text
Could not find platform independent libraries <prefix>
```

Treat that as noisy environment output if tests still pass.

## Editing Rules

- Use `apply_patch` for manual edits.
- Do not revert user or prior-agent changes unless explicitly asked.
- Keep app-specific paper semantics out of `src/rtdsl` and `src/native`.
- If a report says "implemented; review pending", do not silently upgrade it to
  reviewed/approved.
- Update `memory/progress.md`, `memory/decisions.md`, and `memory/todo.md` at
  meaningful handoff points.
