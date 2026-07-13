# X-HD Comprehensive Midterm Status After Goal5397

Date: 2026-07-10

## Current Status Label

```text
level_b_scalar_strong__generic_system_extraction_real__native_v7_status_stream_smoke_passed__explicit_lb_parity_pending__full_paper_not_complete
```

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5396_goal5397_in_progress_2026-07-10.md
```

as the current X-HD working snapshot.

## Executive Summary

X-HD is in a strong midterm state, but it is not full paper reproduction yet.

What is strong:

```text
1. Bounded same-input X-HD value reproduction is externally reviewed through
   Goal5126.
2. Generic nearest / witness / max-nearest extraction is externally reviewed
   through Goals5127-5128.
3. The strongest Level-B public Stanford Dragon -> HappyBuddha scalar route
   matches author rerun HDResult to about 2.38e-9.
4. The fast scalar route has been improved to about 0.849s fresh route wall and
   about 0.362s explicit-warm route median under the directed-HD / max-nearest
   contract.
5. The explicit `-lb` line now has an author trace v2 oracle, a generic RTDL
   status-stream ABI, a rejected v6-remap shortcut, and a first real native v7
   status-stream symbol that builds and smokes on POD.
```

What is not complete:

```text
1. Exact paper input datasets are still unavailable.
2. Full Figure 5/7/8/9/10/11 reproduction is not complete.
3. No author-vs-RTDL performance ratio is authorized.
4. Explicit X-HD `-lb` is still unsupported because native v7 has not matched
   the author row-count / hash / status-transition oracle.
5. Many post-Goal5130 goals are implemented / review pending, not externally
   approved.
```

The current hard blocker is no longer the scalar directed-Hausdorff value on the
best Level-B public pair. The current hard blocker is explicit X-HD `-lb`:

```text
Can RTDL expose a generic native active-query status stream whose raw row count,
samples/hash, status counts, current-best transitions, and feedback telemetry
match the author `-lb` trace without app-specific constants or X-HD-only core
logic?
```

## Evidence Level Matrix

```text
Level A: bounded same-input correctness
  complete and externally reviewed through Goal5126

Level B: same-source public representative scalar route
  strong; Dragon -> HappyBuddha public pair matches author rerun HDResult
  within about 2.38e-9

Level C: exact paper dataset reproduction
  not complete; exact paper input bytes / hashes remain unavailable

Level D: paper figure / performance reproduction
  not complete; figure denominators, datasets, and timing boundaries remain
  incomplete or not aligned

Level E: explicit `-lb` / author RT-core status-stream parity
  not complete; Goal5397 proves a native v7 smoke only, not author parity
```

## What Is Completed And Externally Reviewed

### X-HD Scaffold And Bounded Correctness

```text
Goal5110:
  X-HD scaffold and provenance.

Goals5111-5126:
  bounded same-input author JSON and RTDL route gates, including the
  directed-vs-symmetric discriminating fixture.
```

Key meaning:

```text
RTDL can reproduce bounded X-HD HDResult values under an explicit directed
input1 -> input2 contract. This is not full paper reproduction.
```

### System Extraction From X-HD

```text
Goals5127-5128:
  generic nearest pipeline extraction:
    pairwise L2 candidate rows;
    nearest witness;
    max-nearest reduction;
  plus a non-Hausdorff consumer proving these helpers are not just an X-HD
  wrapper.
```

Key meaning:

```text
Hausdorff remains an app-level composition. RTDL core gained generic nearest /
witness / reduction APIs rather than an X-HD-specific primitive.
```

### Full-Reproduction Plan

```text
Goal5129:
  full-reproduction plan reviewed with amendment incorporated:
  exact paper dataset status requires file/hash or equivalent provenance, not
  only count/statistic matching.
```

Key meaning:

```text
The project is allowed to pursue full paper reproduction, but it must not
promote Level-B same-source evidence into exact paper dataset evidence.
```

## Implemented / Review Pending Work

The long X-HD line after Goal5130 is valuable, but most of it remains
implemented / review pending. Do not silently upgrade it to externally approved.

Important implemented blocks:

```text
Goals5130-5137:
  paper target matrix, dataset provenance, Stanford public graphics acquisition,
  sample gates, and algorithmic route gap analysis.

Goals5138-5150:
  generic grid-cell / cell-MBR / frontier API construction and bounded native
  3-D cell-MBR route gates.

Goals5151-5174:
  same-POD representative route scaling and route optimization on Stanford
  graphics samples up to full public res4.

Goals5175-5188:
  author paper-branch log inventory, priority Dragon -> HappyBuddha public
  input bridge, full-public author gate, full-public RTDL route gate, and phase
  matrix refusing author-vs-RTDL ratios.

Goals5189-5212:
  full-public route optimization and global-bound early-break.

Goals5272-5283:
  Figure 11 memory denominator audit and generic heavy/offload worklist
  telemetry line, ending with denominator-not-aligned closeout.

Goals5284-5287:
  Figure 9 author-log/source audit, ending with current-line closeout because
  the author denominator is missing.

Goals5288-5309:
  Figure 5 timing/data candidate work, Stanford graphics author prechecks,
  additional graphics/geo Level-B scalar checks, and geo provenance probing.

Goals5363-5397:
  explicit `-lb` / status-stream denominator investigation, author trace v2,
  RTDL status-trace summaries, denominator-surface reconciliation, native ABI
  gate, v6-remap no-go, and first native v7 status-stream smoke.
```

## Strongest Current Correctness Result

The strongest current scalar correctness result is the full public Stanford
Dragon -> HappyBuddha Level-B route:

```text
source points = 437,645
target points = 543,652

author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
absolute diff   ~= 2.38e-9
```

Boundaries:

```text
This is same-source public representative evidence, not exact paper dataset
reproduction.
It matches an author rerun on available public data, not proven exact paper
input bytes.
It is a directed input1 -> input2 Hausdorff scalar result.
```

## Current Performance Position

The best current scalar route after Goal5211 / Goal5212 is:

```text
fresh route wall                 ~= 0.849s
fresh full total including load  ~= 1.531s
explicit-warm route median       ~= 0.362s
explicit-warm measured case total ~= 0.288s
```

These are not one interchangeable number:

```text
fresh route wall:
  RTDL route phase only, not full process wall and not author denominator.

fresh full total including load:
  app input load + route under the current public Level-B runner boundary.

explicit-warm route / case total:
  measured after an explicit warmup protocol; useful diagnostic/prepared
  runtime evidence, not a replacement for fresh unless a prepared/warm product
  regime is explicitly selected.
```

Important correctness caveat:

```text
per_source_witness_exact = false
early-aborted sources = 409,376 / 437,645
```

The fast route preserves the directed-Hausdorff / max-nearest scalar value. It
does not preserve exact per-source nearest witnesses for early-aborted sources.
Therefore it is a max-nearest / directed-HD scalar contract, not a default exact
nearest-witness contract.

## Why No Author-vs-RTDL Performance Ratio Is Authorized

The known author and RTDL timings are different denominators:

```text
author internal Running.AvgTime:
  author internal algorithm timing

author process wall:
  author process timing on the POD

RTDL route wall:
  RTDL route phase under app runner boundaries

RTDL total / case total:
  app-defined total, sometimes with load and optional warmup reported separately
```

Until dataset, hardware, phase boundary, setup/load inclusion, and runtime
regime match, the project must report separate phase numbers and refuse ratios.

## Exact Paper Dataset Status

Exact paper reproduction is not complete.

Current input status:

```text
Public Stanford graphics data:
  useful Level-B same-source evidence.

Exact author paper input bytes / hashes:
  still unavailable for the key full-paper claims.

Count/statistic/log matching:
  useful evidence, but not sufficient for exact paper dataset identity.
```

Standing rule:

```text
Statistics do not prove exact dataset identity.
Exact paper dataset status requires file/hash provenance or equivalent
deterministic provenance.
```

## Paper Figure Status

```text
Figure 5:
  partial Level-B graphics/geo scalar evidence exists, but no full exact-input
  figure reproduction and no authorized performance ratio.

Figure 7:
  explicit load-balance / -lb matrix is not reproduced. Current work is blocked
  on author-compatible status-stream parity.

Figure 8:
  radius-strategy logs are missing under current checked-in artifacts; not
  reproduced.

Figure 9:
  current author logs do not provide the full expected auto-tune denominator;
  current line is closed as denominator missing.

Figure 10:
  scalability/overlap exact matrix is not reproduced because checked-in logs do
  not expose the required subset and exact inputs are missing.

Figure 11:
  memory denominator is not aligned. RTDL has generic heavy/offload telemetry,
  but author WL / WL Heavy Peak are not the same denominator as current RTDL
  rows/bytes.
```

## Explicit `-lb` Status

### Author Oracle

Goal5387 produced the strongest author `-lb` oracle:

```text
active_count = 437,645
raw_offload_rows_before_sort_reduce = 27,133,990
rows_per_active = 62
raw_offload_row_hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

### Known RTDL Denominator Surfaces

```text
current bridge rows = 2,188,225 = 5 * active_count
raw kind2 rows = 21,006,960 = 48 * active_count
full-cover rows = 24,508,120 = 56 * active_count
overcount rows ~= 304,981,889 ~= 696.87 * active_count
```

No known RTDL surface has row-count parity or hash parity.

The closest known surface is full-cover:

```text
author rows = 27,133,990 = 62 * active_count
full-cover rows = 24,508,120 = 56 * active_count
missing rows = 2,625,870 = 6 * active_count
```

### What Goal5396 Settled

Goal5396 rejected the unsafe shortcut:

```text
v6_column_remap_authorized = false
native_status_stream_backend_implemented_by_goal5396 = false
explicit_lb_remains_fail_closed = true
real_v7_backend_required = true
```

Meaning:

```text
Existing v6 frontier rows must not be relabeled into fake v7 status rows.
```

### What Goal5397 Adds

Goal5397 adds the first real generic native v7 status-stream symbol:

```text
rtdl_optix_collect_active_query_status_stream_3d_v1
```

and Python front door:

```text
collect_active_query_status_stream_3d_optix
```

POD evidence:

```text
preflight = POD_OK on NVIDIA RTX 4000 Ada Generation
POD focused Goal5397 tests = Ran 5 OK
POD make build-optix = succeeded
synthetic v7 status-stream smoke matched = true
valid_count = 4
attempted_count = 4
status_codes = [2]
```

What this proves:

```text
1. The v7 native symbol exists and builds on POD.
2. The Python front door can call it.
3. A synthetic fixture can emit app-neutral active-query status rows.
4. The work is not merely a v6 Python column remap.
```

What this does not prove:

```text
1. Explicit X-HD -lb support.
2. Row-count parity against Goal5387.
3. Hash/sample parity.
4. Missing 6x-active delta closure.
5. Figure 7 or Figure 11 reproduction.
6. Performance ratio.
7. Full X-HD paper reproduction.
```

Known limitation:

```text
The first v7 implementation emits status rows at existing native emitted-row
points. It may still inherit v6-like denominator behavior. Goal5398 must test
this directly against the author trace v2 oracle.
```

## Key Challenges

### Solved Or Substantially Reduced

```text
Directed-vs-symmetric HD ambiguity:
  solved by Goal5126 discriminating fixture.

Hausdorff-as-core-primitive risk:
  reduced by Goals5127-5128 generic extraction and non-Hausdorff consumer.

Large public Dragon -> HappyBuddha scalar value:
  solved at Level B by author rerun + RTDL scalar match.

Naive all-pairs materialization:
  avoided by scalable grid/cell-MBR/frontier/inline-nearest route.

Python tuple/input-loader overhead:
  greatly reduced by matrix front doors and fast PLY loading.

Max-nearest reduction overhead:
  reduced to a small cost by linear finite reduction with tie-only sorting.

Micro-optimization dead ends:
  lower inline thresholds, static cell ordering, scalar trace tmax, native
  seed wrapper, and prepared accel-build caching have no-go or neutral evidence.

Fake v6 remap risk:
  rejected by Goal5396.

Native v7 plumbing:
  first real symbol/front door/synthetic POD smoke completed by Goal5397.
```

### Still Unsolved

```text
Exact paper input identity:
  unresolved; public same-source evidence is not exact paper reproduction.

Full paper figures:
  unresolved; figure denominators and datasets are incomplete or not aligned.

Author-vs-RTDL performance ratio:
  unauthorized; denominators are not aligned.

Explicit X-HD -lb:
  unresolved; native v7 has not matched author row/hash/status oracle.

Native v7 full parity:
  not run yet; Goal5398 is required.

Review debt:
  many goals after 5130 are implemented / review pending.
```

## Next Planned Work

### Goal5398: Native v7 Status-Stream Parity Gate

Goal5398 is the immediate next implementation / measurement goal.

It must compare RTDL native v7 against Goal5387 author trace v2:

```text
active_count = 437,645
author raw rows = 27,133,990
author raw hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

Minimum comparisons:

```text
RTDL v7 row_count
RTDL v7 status_count_offloading
RTDL v7 deterministic samples or hash when semantics are comparable
status/transition code distribution
current_best_before_sq / current_best_after_sq availability
feedback / miss / completed / aborted telemetry, or explicit not-applicable
evidence
```

Goal5398 must not:

```text
claim explicit -lb support from Goal5397 smoke alone;
hard-code 6 rows per active or 62 rows per active;
hide a denominator mismatch behind a successful synthetic smoke;
claim Figure 7, Figure 11, performance ratio, exact dataset reproduction, or
full X-HD paper reproduction.
```

Possible Goal5398 exits:

```text
native_v7_status_stream_author_trace_parity_passed
native_v7_status_stream_denominator_mismatch__lb_remains_fail_closed
native_v7_status_stream_semantic_gap__new_generic_state_machine_required
```

### After Goal5398

If parity passes:

```text
1. Continue explicit -lb correctness work.
2. Keep Figure 7 / Figure 11 / performance ratio forbidden until denominator
   reviews and figure-specific gates pass.
3. Audit whether v7 status rows can support author-like memory telemetry.
```

If denominator mismatch remains:

```text
1. Record native v7 no-go or partial-gap result.
2. Keep explicit -lb fail-closed.
3. Decide whether a new generic multi-round status-machine execution model is
   justified, or close the explicit -lb line under the current RTDL model.
```

If v7 would require X-HD-specific constants:

```text
Reject it as an RTDL core feature.
Keep app-specific logic in the X-HD app only.
Do not hard-code 6x or 62x into native RTDL.
```

### Consolidated Review Packet

After Goal5398, prepare a strict review packet for:

```text
Goals5386-5398
```

Key review questions:

```text
1. Does the author trace v2 oracle support the claimed comparison?
2. Does native v7 emit a real status stream rather than relabeling old rows?
3. Are X-HD-specific constants absent from RTDL core/native?
4. Is explicit -lb still fail-closed until row/hash evidence passes?
5. Are Figure 7, Figure 11, and performance-ratio claims still forbidden?
```

## POD Usage Expectation

Current POD from memory:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

POD expectation:

```text
Goal5398 requires POD.
Reason: it must run native OptiX v7 against the full or bounded Dragon ->
AsianDragon status-stream comparison.
```

No POD needed for:

```text
local source-level tests;
report writing;
call-for-review preparation;
memory updates.
```

Before declaring POD failure:

```text
run wrapper preflight;
do not use naked SSH;
do not use old/default SSH keys.
```

## Effort / Schedule Estimate

This is an engineering estimate, not a guarantee:

```text
Goal5398 script + local tests:
  small-to-medium.

Goal5398 POD full/bounded run:
  medium-to-large. It may be memory/time-heavy because status rows can be large.

Goal5398 analysis/report/CFR:
  small once artifacts exist.

If v7 mismatches:
  next design decision may be large, because it may require a real multi-round
  native status-machine execution model rather than emitted-row status logging.
```

## Allowed Current Summary

```text
X-HD has strong Level-B directed-Hausdorff scalar correctness and real generic
RTDL system extraction. It is not full paper reproduction. The current hard
blocker is explicit -lb status-stream parity. Goal5397 proves a real generic
native v7 status-stream symbol builds on POD and emits synthetic status rows,
but explicit -lb remains unsupported until Goal5398 compares v7 against the
Goal5387 author trace v2 oracle.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports explicit X-HD -lb.
Goal5397 matches the author status-stream denominator.
Goal5397 solves the missing 6x-active delta.
RTDL has Figure 7 or Figure 11 reproduction.
RTDL has same-denominator author performance parity.
The fast route has exact per-source witnesses.
Public Stanford Dragon/HappyBuddha is exact paper input.
Implemented / review pending goals are externally approved.
```
