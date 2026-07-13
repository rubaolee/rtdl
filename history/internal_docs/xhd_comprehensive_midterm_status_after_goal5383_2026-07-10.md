# X-HD Comprehensive Midterm Status After Goal5383

Date: 2026-07-10

## Executive Summary

The X-HD paper-app line has made real progress, but it is not a full paper
reproduction yet.

What is solid:

- Bounded same-input X-HD value reproduction is complete and externally
  reviewed through Goals5111-5126.
- Generic system extraction from the X-HD pressure test is real and externally
  reviewed through Goals5127-5128:
  pairwise L2 candidate rows, nearest witness, and max-nearest reduction are
  now app-neutral RTDL primitives with a non-Hausdorff consumer.
- The strongest representative route is the Level-B public Stanford
  Dragon -> HappyBuddha line.  Author `hd_exec` and the RTDL route agree on
  the directed HD scalar:

```text
source points = 437645
target points = 543652
author hd_exec HDResult ~= 0.12572988867759705
RTDL route distance    ~= 0.12572988629271128
absolute difference    ~= 2.38e-9
```

- Route-local performance improved dramatically during the Level-B route work:

```text
Goal5188 initial scalable route      ~= 7.30s
Goal5191 inline512 route             ~= 3.65s
Goal5195 intersection prune route    ~= 2.6s
Goal5196 dense local-grid route      ~= 2.26s
Goal5203 matrix input route          ~= 1.24s
Goal5204 linear max reducer route    ~= 1.17-1.18s
Goal5211 global-bound route          ~= 0.849s fresh route
Goal5211 explicit-warm route median  ~= 0.362s
Goal5212 full total incl load        ~= 1.531s
Goal5212 warm measured case total    ~= 0.288s
```

The strongest caution:

- The fast Goal5211/5212 route is exact for the final directed HD scalar, but
  not for every per-source nearest witness.  Goal5211 reports
  `per_source_witness_exact=false`; `409376 / 437645` sources early-abort.  It
  is therefore an exact-value / max-nearest route, not an exact witness route.
- The Level-B Dragon -> HappyBuddha result matches an author rerun.  It should
  not be phrased as exact paper input reproduction.  The public data appears
  close to the paper-log route, but exact file/hash provenance is still absent.
- No author-vs-RTDL performance ratio is authorized.  Author internal
  `Running.AvgTime`, author process wall time, RTDL route time, RTDL total time,
  and warm-route diagnostics are different denominators.

The current hard blocker is explicit author `-lb` / heavy-offload status-machine
behavior.  Goal5383 shows that another local prune-mode hypothesis failed:

```text
Goal5374 author lb=256 oracle:
  OffloadingSize / raw rows = 27133990

Goal5383 full seeded active-initial-best probe:
  active_query_count        = 437645
  candidate_row_count       = 2600727
  bridge_offload_row_count  = 2188225
  row_ratio_rtdl_div_author = 0.08064516129032258
  row_count_parity          = false
```

Conclusion: the remaining `-lb` gap is not solved by scalar radius alignment,
raw kind2 counting, global-bound early break, heavy-before-inline classification,
or active-initial-best classification.  The next valid work is a true
multi-round active-query status stream, or an explicit fail-closed closeout for
`-lb`.

## Current Status By Reproduction Level

### Level A - Bounded Same-Input Correctness

Status: complete and externally reviewed.

Evidence:

- Goals5111-5126 close bounded same-input X-HD scalar correctness.
- Goal5126 adds the directed-vs-symmetric discriminator:

```text
directed a->b = 0.5
directed b->a = 9.0
symmetric     = 9.0
author matches directed a->b
RTDL matches directed a->b
```

Meaning:

- RTDL and author agree on the directed input1-to-input2 Hausdorff definition.
- This is value-level correctness on bounded fixtures, not full paper
  reproduction.

### Level B - Same-Source Representative Correctness

Status: strongest current line; still not exact paper dataset reproduction.

Evidence:

- Public Stanford graphics representative data is available.
- Dragon -> HappyBuddha is the strongest Level-B candidate.
- Goal5186 runs author `hd_exec` on the public full pair and matches the
  paper-branch author-log HDResult within the allowed tolerance.
- Goal5187 runs the RTDL scalable route on the same full public pair and
  matches the author rerun scalar within about `2.38e-9`.

Limits:

- Exact author input bytes / hashes are not available.
- Public same-source Stanford files must not be silently upgraded to exact
  paper datasets.
- The Level-B route is representative evidence, not the whole Figure 5 matrix.

### Level C - Exact Paper Dataset Reproduction

Status: not complete.

Why:

- Exact paper input files / hashes are still unavailable.
- Matching counts, MBRs, Gini, or HDResult values is not enough to prove exact
  dataset identity.
- Graphics, ModelNet40, geo, and BraTS lines have useful evidence, but no
  complete exact-paper input package.

Current best:

- Dragon -> HappyBuddha is value-matched and representative.
- Some public geo candidates have bounded same-fixture scalar matches.
- Full-public ArcGIS probes show strong but imperfect proximity for some
  WKT-like candidates.

Still required:

- file/hash provenance or accepted deterministic regeneration for exact inputs;
- figure-specific workload mapping;
- separate review before any Level C claim.

### Level D - Figure / Performance Reproduction

Status: not complete.

Current figure status:

- Figure 5: partially explored through Level-B graphics and geo candidates; no
  denominator-aligned performance matrix and no full Figure 5 reproduction.
- Figure 6: pruning diagnostics exist, but full figure reproduction is not
  closed.
- Figure 7: explicit `-lb` / heavy offload remains unresolved.
- Figure 8: radius-growth semantics are partially mapped, but general
  `-tune_radius` and figure reproduction remain unclosed.
- Figure 9: current author logs do not provide the full expected auto-tune
  denominator.
- Figure 10: source/scripts exist, but the checked-in scalability matrix is not
  available.
- Figure 11: memory denominator is not aligned; current RTDL worklist telemetry
  is not author WL / WL Heavy Peak parity.

No performance ratio is currently authorized.

## What Has Been Completed

### 1. Paper-App Scaffold And Provenance

Completed:

- X-HD paper app scaffold.
- Author repository / CLI / JSON contract provenance.
- Paper-app manifest and claim boundaries.
- Separation between old `hausdorff_xhd` benchmark assets and the new X-HD
  paper app.

Important boundary:

- Old benchmark code was not simply renamed as paper reproduction.

### 2. Bounded Correctness And Directed-HD Semantics

Completed:

- Author `hd_exec` build/run gates.
- Bounded 2-D and 3-D same-input author JSON gates.
- RTDL bounded route gates.
- Directed-vs-symmetric discriminator proving author `HDResult` is directed
  input1-to-input2 for the tested contract.

### 3. Generic RTDL System Extraction

Completed:

- Pairwise L2 distance candidate rows.
- Nearest witness.
- Max-nearest distance witness.
- Non-Hausdorff facility/service-radius consumer proving that the extracted
  max-nearest path is not merely X-HD-shaped.
- Generic grid-cell and cell-MBR descriptors.
- Native 3-D AABB / cell-MBR frontier front doors.
- Generic nearest-state and frontier continuation contracts.
- Generic coordinate-matrix reuse and matrix-column front doors.
- Generic max-nearest finite-distance linear reducer.
- Generic active-query / status-machine CPU reference and candidate telemetry
  surfaces for the later `-lb` line.

These are the strongest system-language gains from the X-HD app so far.

### 4. Level-B Stanford Graphics Route

Completed:

- Paper-log workload mapping.
- Public Stanford Dragon/HappyBuddha bridge.
- Full public route on large representative data.
- Route correctness against author rerun scalar.
- Phase-boundary matrix refusing unfair performance ratios.
- Many route-local optimizations, each kept generic or app-owned:
  local-grid seed, inline-nearest threshold, payload-current-best pruning,
  intersection-stage pruning, dense cell lookup, coordinate-matrix reuse,
  fast PLY matrix loading, linear max-nearest reduction, explicit warmup, and
  global-bound early break.

Most important caveat:

- Goal5211/5212 is scalar-value exact, not per-source witness exact.

### 5. User-Facing `hd_exec` Compatibility Surface

Completed / implemented:

- RTDL app-owned `hd_exec`-compatible wrapper exists.
- Author variant names are accepted for directed HDResult value output.
- Unsupported author RT options fail closed rather than silently running with
  wrong semantics.

Boundary:

- Accepting variant names is value-surface compatibility, not algorithm parity.
- Non-`rt` author algorithms (`eb`, `nn`, `itk`, `clover`) are not reproduced as
  separate algorithms.
- Explicit author RT options like `-lb` remain unsupported unless separately
  proven.

### 6. Radius / Tune-Radius Semantics

Completed / implemented:

- Generic radius-growth schedule helper.
- Author trace mapping for available JSON traces.
- App-owned diagnostic route metadata.
- Narrow internal adaptive tune-radius mapping is available for traced cases.

Boundary:

- This does not close Figure 8.
- It does not authorize broad author `-tune_radius` support.

### 7. Load-Balance / Heavy-Offload Investigation

Completed / implemented through Goal5383:

- Author source audit of heavy-cell offload semantics.
- Author-side status-trace oracle via instrumentation.
- Generic active-query/status-machine CPU reference.
- Native status telemetry candidates.
- Current RTDL surface comparison against the author oracle.
- Active-query frontier bridge.
- Native status-stream design packet.
- Active-initial-best native probe.

Known hard numbers:

```text
Author Goal5374 lb=256 oracle:
  ActiveInQueueSize              = 437645
  StatusInitCount                = 437645
  OffloadingSize                 = 27133990
  RawOffloadRowsBeforeSortReduce = 27133990
  StatusOffloadingAppendCount    = 27133990
  RawOffloadRowsAuthorWidthBytes = 217071920

Goal5381 bridge:
  active_query_count        = 437645
  bridge_offload_row_count  = 2188225
  row_ratio                 = 0.08064516129032258
  row_count_parity          = false

Goal5383 seeded active-initial-best probe:
  active_query_count        = 437645
  bridge_offload_row_count  = 2188225
  row_ratio                 = 0.08064516129032258
  row_count_parity          = false
```

Conclusion:

- Current generic frontier rows are not the author raw status-machine stream.
- Explicit `-lb` remains fail-closed.

## Major Problems Already Solved

1. The project no longer confuses bounded value gates with full paper
   reproduction.
2. Directed HD semantics are pinned by a discriminator fixture rather than by
   assumption.
3. Hausdorff has been decomposed into generic nearest/witness/max-nearest
   primitives instead of becoming an X-HD-only RTDL core primitive.
4. The large Dragon/HappyBuddha representative route is no longer blocked by
   pairwise materialization.
5. Route-local runtime has been reduced from multi-second route walls to
   sub-second scalar-value route walls on the strongest Level-B case.
6. The project now has a repeatable POD operating rule and no longer treats SSH
   key mismatch as a POD failure.
7. Several tempting wrong paths have been killed with data:
   lower inline thresholds, static cell ordering, scalar ray `tmax`, native CUDA
   seed wrapper, prepared cell-MBR accel caching, scalar-radius-only `-lb`, raw
   kind2-only `-lb`, heavy-before-inline-prune, and active-initial-best prune.

## Major Problems Not Yet Solved

### 1. Exact Paper Inputs

The exact paper datasets are still missing.  Public / same-source candidates are
useful but remain Level B unless file/hash provenance or accepted deterministic
regeneration is obtained.

### 2. Full Figure Matrix

The route has strong scalar correctness evidence for selected workloads, but
the paper's full figure matrix is not reproduced.

### 3. Performance Denominator Alignment

No author-vs-RTDL performance ratio is currently fair.  The denominators differ:

```text
author internal Running.AvgTime
author process wall
RTDL route wall
RTDL total / case total
cold process
warm long-lived process
prepared / explicit warmup route
```

### 4. Explicit `-lb` / Heavy-Offload Parity

This is the current main technical hard problem.  The author uses a payload
status machine and load-balance processing that current RTDL surfaces do not
match.

The missing behavior appears to involve:

- multi-round active query feedback;
- active `in_queue` indices;
- per-source `cmin2` / current-best state;
- `kInit`, `kOffloading`, `kAborted` status transitions;
- `cmax2` MBR abort;
- miss queue behavior;
- raw offload row append before sort/reduce;
- `loadBalanceProcessing` feedback into the next iteration.

### 5. Review Debt

Many later X-HD goals are implemented / review pending.  The project must not
rewrite them as approved until a real external review exists.

## Current POD State

Use the wrapper only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Last verified:

```text
POD_OK
container = 45c502cfccb5
GPU       = NVIDIA RTX 4000 Ada Generation
driver    = 550.127.05
```

Remote workspace:

```text
/tmp/rtdl_goal5364
```

Caveat:

- That remote workspace is not a git checkout.  Changed local files must be
  uploaded explicitly and native OptiX rebuilt with `make build-optix`.

POD expected usage for the next phase:

- needed for native OptiX build / route probes;
- needed for Dragon -> AsianDragon `-lb` row-parity probes;
- not needed for pure documentation / requirements / CPU-reference tests.

## Planned Work

### P0 - Strict Review Packet

Send the current `-lb` status-machine packet for strict review before claiming
anything stronger:

```text
Goal5381 active-query frontier bridge probe
Goal5382 native status-machine stream design
Goal5383 active-initial-best status probe
```

Review should answer:

- Did Goal5381 correctly show that active query count aligns but offload row
  count fails?
- Is Goal5382's `generic_active_query_status_stream_v1` the right next
  contract?
- Does Goal5383 correctly kill the active-initial-best hypothesis?
- Should the next step be true multi-round status-stream work or fail-closed
  closeout?

### P1 - Goal5384: Multi-Round Active-Query Status Stream Requirements / Prototype

Recommended next implementation.

Purpose:

```text
Stop adding local prune modes.  Model the actual multi-round active-query
status stream needed to compare against the Goal5374 author oracle.
```

Minimum required fields:

```text
active_query_count
active_in_queue_indices
current_best_state_source
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
raw_offload_rows_before_sort_reduce
offload_row_count
author_width_bytes
row_count_parity_against_goal5374
```

Two acceptable exit paths:

```text
multiround_status_requirements_ready__need_stronger_author_trace_before_native_parity
multiround_status_stream_prototype_ready__row_count_parity_or_fail_closed
```

If a concrete prototype is not safe yet, Goal5384 should be a requirements /
oracle packet rather than a misleading implementation.

### P2 - Author Trace Strengthening If Needed

If RTDL cannot reconstruct the necessary state from existing artifacts, add an
author instrumentation goal.

Required author-side trace:

```text
per-batch in_queue size
per-batch radius
per-batch cmin2 / current-best vector hash or sample
per-batch raw offload rows before sort/reduce
status counts init / offloading / aborted
cmax2 MBR abort count
miss queue count
loadBalanceProcessing grouped output counts
OffloadingSize contribution per batch
```

This is not an RTDL feature by itself.  It is an oracle-building step.

### P3 - Native Generic Status Stream

Only after P1/P2 clarify the denominator:

- implement or refine a native generic active-query status stream;
- preserve app-neutral naming in `src/native` and `src/rtdsl`;
- keep X-HD option names and author JSON mapping in the app;
- run the Dragon -> AsianDragon row-parity probe against Goal5374.

Success condition:

```text
row_count_parity = true
or a reviewed explanation of why parity is impossible under the chosen generic
contract
```

Until then:

```text
explicit -lb remains unsupported / fail-closed
```

### P4 - Claim Matrix Refresh

After Goal5384 or a fail-closed decision, refresh the X-HD claim matrix:

- full paper reproduction status;
- Level-B representative status;
- exact dataset status;
- `-lb` / Figure 7 / Figure 11 status;
- RTDL system features extracted;
- review pending / approved split;
- allowed and forbidden summaries.

### P5 - Broader Paper Completion After `-lb`

Only after the `-lb` status-machine question is closed one way or the other:

- continue exact input acquisition / provenance;
- revisit figure-level reproduction targets;
- produce denominator-aligned performance matrices only where fair;
- decide whether a route is value-only, exact-witness, or author-algorithmic.

## Expected Process And Rough Time

This is a planning estimate, not a promise.

```text
0.5 day:
  write and review Goal5384 requirements/prototype plan;
  inspect author loadBalanceProcessing and existing author instrumentation;
  add local tests for required trace schema.

0.5-1 day with POD:
  if implementing a probe, sync files to /tmp/rtdl_goal5364;
  rebuild OptiX;
  run source64 and full Dragon -> AsianDragon row-parity probes;
  download artifacts and write result/call-for-review.

0.5 day:
  refresh midterm / claim matrix after Goal5384;
  send Goals5381-5384 for review.

Unknown / external:
  exact paper input acquisition;
  author-side instrumentation if the existing oracle is still too weak;
  denominator-aligned full figure reproduction.
```

## Current Allowed Summary

Allowed:

```text
X-HD is a strong Level-B same-source representative reproduction and system
extraction line.  RTDL matches author rerun scalar HDResult on the main public
Dragon -> HappyBuddha route and has extracted reusable nearest / witness /
max-nearest / grid-cell / cell-MBR / active-query status primitives.  The
fastest scalar route is exact for the final directed HD value but not for all
per-source witnesses.  Exact paper input reproduction and figure-level
performance reproduction remain open.  The main current technical blocker is
explicit author -lb / heavy-offload status-machine parity.
```

Forbidden:

```text
full X-HD paper reproduction is complete
RTDL matches author performance
RTDL supports explicit author -lb
Figure 7 / Figure 11 are reproduced
public Stanford files are exact paper inputs
Goal5211 proves exact per-source witnesses
Goal5383 is close to author OffloadingSize parity
```

## Immediate Next Command Checklist

Before any POD work:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Before declaring a route result:

```text
report dataset identity level
report runtime regime
report phase denominator
report review status
report whether per_source_witness_exact is true or false
report explicit -lb support as fail-closed unless row parity is proven
```
