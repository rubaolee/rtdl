# X-HD Comprehensive Midterm Status After Goal5396 / Goal5397 In Progress

Date: 2026-07-10

## Current Status Label

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_v6_remap_rejected__goal5397_v7_native_status_stream_in_progress__full_paper_not_complete
```

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5396_2026-07-10.md
```

as the current working snapshot.

## Executive Summary

X-HD has reached a strong but bounded state:

- bounded same-input X-HD value reproduction is complete and externally
  reviewed through Goal5126;
- the generic nearest / witness / max-nearest system extraction is complete and
  externally reviewed through Goals5127-5128;
- the strongest current X-HD route is a Level-B same-source public Stanford
  Dragon -> HappyBuddha route, not an exact paper-input route;
- RTDL matches the author rerun HDResult on that public pair to about
  `2.38e-9`;
- the fast scalar route is now good evidence for the directed-Hausdorff scalar,
  but it is explicitly exact-value-only because early-break can make many
  per-source witnesses approximate;
- exact paper input provenance is still missing;
- paper figures are not fully reproduced;
- explicit X-HD `-lb` support is still unsupported because RTDL does not yet
  match the author raw status-stream denominator.

The current hard technical line is no longer "can RTDL compute the scalar
directed Hausdorff value?"  It can on the strongest Level-B public candidate.
The hard line is now:

```text
Can RTDL expose a generic native active-query status stream whose row count,
samples/hash, status transitions, and feedback telemetry can be compared to the
author X-HD -lb trace without hard-coding X-HD-specific constants?
```

Goal5396 rejected the unsafe shortcut of remapping existing v6 frontier rows
into the new status-stream ABI. Goal5397 is now in progress and has started a
real v7 native status-stream implementation, but that work is not yet compiled,
POD-validated, or comparable to the author oracle.

## Evidence Level Matrix

```text
Level A bounded same-input correctness:
  complete and externally reviewed through Goal5126

Level B same-source public representative scalar route:
  strong; current best public Dragon -> HappyBuddha evidence matches author
  rerun value within ~2.38e-9

Level C exact paper dataset reproduction:
  not complete; exact input file/hash provenance remains unavailable

Level D paper figure/performance reproduction:
  not complete; figure denominators, datasets, and author timing boundaries are
  not aligned enough for full figure reproduction or ratios

Level E explicit -lb / author RT-core status-stream parity:
  not complete; author trace v2 exists, RTDL counterpart still mismatches row
  denominator; v7 native status-stream backend is in progress only
```

## What Is Actually Complete

### Reviewed / Approved Foundations

```text
Goal5110:
  X-HD scaffold and provenance.

Goals5111-5126:
  bounded same-input author JSON and RTDL route gates, including the
  directed-vs-symmetric discriminating fixture.

Goals5127-5128:
  generic nearest pipeline extraction:
    pairwise L2 candidate rows;
    nearest witness;
    max-nearest reduction;
  plus a non-Hausdorff consumer proving the helpers are not just an X-HD app
  wrapper.

Goal5129:
  full-reproduction plan reviewed with amendment:
  exact paper dataset status requires file/hash or equivalent provenance, not
  only count/statistic matching.
```

### Implemented / Review Pending System And App Work

The long X-HD line after Goal5130 remains mostly implemented / review pending,
not externally approved. The important implemented blocks are:

```text
Goals5130-5137:
  target matrix, dataset provenance, Stanford public graphics acquisition,
  sample gates, and algorithmic gap analysis.

Goals5138-5150:
  generic grid-cell / cell-MBR / frontier API construction and bounded native
  3-D cell-MBR route gates.

Goals5151-5174:
  same-POD representative route scaling and system-route optimization on
  Stanford graphics samples up to full public res4.

Goals5175-5188:
  author paper-branch log inventory, priority Dragon -> HappyBuddha public
  input bridge, full-public author gate, full-public RTDL route gate, and phase
  matrix refusing performance ratios.

Goals5189-5212:
  full-public route optimization and global-bound early-break.

Goals5272-5283:
  Figure 11 memory denominator audit and generic heavy/offload worklist
  telemetry line, ending with denominator-not-aligned closeout.

Goals5284-5287:
  Figure 9 author-log/source audit, ending with current-line closeout because
  author denominator is missing.

Goals5288-5298:
  Figure 5 timing/data candidate work and Stanford graphics author prechecks.

Goals5299-5309:
  additional graphics/geo Level-B scalar checks and geo provenance probing.

Goals5363-5396:
  explicit -lb / status-stream denominator investigation, author trace v2,
  RTDL status-trace summaries, denominator-surface reconciliation, native ABI
  gate, and v6-remap no-go.
```

These are valuable, but they must not be described as externally reviewed unless
a separate review file exists.

## Strongest Current Correctness Result

The strongest current scalar correctness result is the public Stanford
Dragon -> HappyBuddha Level-B route:

```text
source points = 437,645
target points = 543,652

author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
absolute diff   ~= 2.38e-9
```

Important limitations:

```text
This is Level-B same-source public evidence, not exact paper dataset evidence.
It matches the author rerun, not proven exact paper input bytes.
It is a directed input1 -> input2 Hausdorff scalar result.
```

## Current Performance Position

The best current fast scalar route, after Goal5211 / Goal5212, is:

```text
fresh route wall                    ~= 0.849s
fresh full total including load      ~= 1.531s
explicit-warm route median           ~= 0.362s
explicit-warm measured case total    ~= 0.288s
```

These numbers must be kept in their regimes:

```text
fresh route wall:
  route phase only, not full CLI/process wall, not author denominator

fresh full total including load:
  includes app input load and route on the current public Level-B pair

explicit-warm route / case total:
  warm measured route after an explicit warmup protocol; diagnostic / prepared
  runtime evidence, not a replacement for fresh unless the product regime is
  explicitly prepared/warm
```

Important correctness caveat for the fast route:

```text
per_source_witness_exact = false
early-aborted sources = 409,376 / 437,645
```

This route preserves the directed-Hausdorff / max-nearest scalar value, but it
does not preserve exact per-source nearest witnesses for early-aborted sources.
Therefore it is a max-nearest / directed-HD route contract, not a default exact
nearest-witness API contract.

## Why No Author-vs-RTDL Performance Ratio Is Authorized

Known author and RTDL timings are not the same denominator:

```text
author internal Running.AvgTime:
  author's internal algorithm timing

author process wall:
  whole author process timing on the POD

RTDL route wall:
  RTDL route phase, excluding different setup/load boundaries

RTDL total / case total:
  app-defined total under RTDL runner boundaries
```

Because dataset identity, hardware, phase boundaries, and runtime regimes are
not all aligned, this project must continue to report separate phase numbers
instead of ratios.

## Exact Paper Dataset Status

Exact paper reproduction is not complete.

Current input status:

```text
Public Stanford graphics data:
  useful Level-B same-source evidence.

Exact author paper input bytes / hashes:
  still unavailable for the key full paper claims.

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

Current figure-level status:

```text
Figure 5:
  partial Level-B graphics/geo scalar evidence exists, but no full exact-input
  figure reproduction and no authorized performance ratio.

Figure 7:
  explicit load-balance / -lb matrix not reproduced. Current work is blocked on
  author-compatible status-stream semantics.

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

## Explicit `-lb` Status Before Goal5397

Goal5387 produced the strongest author `-lb` oracle:

```text
active_count = 437,645
raw_offload_rows_before_sort_reduce = 27,133,990
rows_per_active = 62
raw_offload_row_hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

Known RTDL denominator surfaces:

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

Goal5396 rejected the unsafe shortcut:

```text
v6_column_remap_authorized = false
native_status_stream_backend_implemented_by_goal5396 = false
explicit_lb_remains_fail_closed = true
real_v7_backend_required = true
```

## Goal5397 In-Progress State

Goal5397 is in progress and must not be reported as complete.

Current local edits show a first native v7 attempt has started:

```text
src/native/optix/rtdl_optix_prelude.h
  adds RtdlActiveQueryStatusStreamRow and
  rtdl_optix_collect_active_query_status_stream_3d_v1 prototype.

src/native/optix/rtdl_optix_workloads.cpp
  adds status_rows_out plumbing and status-row writes at emitted frontier row
  points.

src/native/optix/rtdl_optix_api.cpp
  adds a public C ABI symbol
  rtdl_optix_collect_active_query_status_stream_3d_v1.

src/rtdsl/optix_runtime.py
  adds collect_active_query_status_stream_3d_optix front door.
```

What this currently means:

```text
It is real native-code work, not merely a v6 column rename.
It is app-neutral in naming and contract intent.
It is not yet compiled on POD.
It has no POD smoke artifact yet.
It has no full Dragon -> AsianDragon row/hash comparison yet.
It does not prove explicit -lb support.
It does not prove row-count parity.
```

Expected first limitation:

```text
The initial v7 attempt appears to emit status rows where the current native
collector emits rows. If it still inherits v6-like emitted-row semantics, it
may not solve the 56x -> 62x denominator gap. That is acceptable as a first
native smoke only if the report labels it honestly and keeps -lb fail-closed.
```

## Current Key Challenges

### Solved Or Substantially Reduced

```text
Directed-vs-symmetric HD ambiguity:
  solved by Goal5126 discriminating fixture.

Hausdorff-as-core-primitive risk:
  reduced by Goals5127-5128 extracting generic nearest/witness/max-nearest
  helpers and proving a non-Hausdorff consumer.

Large public Dragon -> HappyBuddha scalar value:
  solved at Level-B by author rerun + RTDL match.

Naive all-pairs materialization:
  avoided by the scalable grid/cell-MBR/frontier/inline-nearest route.

Python tuple/input-loader overhead:
  greatly reduced by matrix front doors and fast PLY loading.

Max-nearest reduction overhead:
  reduced to a small cost by linear finite reduction with tie-only sorting.

Many micro-optimization dead ends:
  lower inline thresholds, static cell ordering, scalar trace tmax, native seed
  wrapper, and prepared accel-build caching have no-go or neutral evidence.
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
  unresolved; current RTDL status/offload surfaces do not match the author
  trace v2 oracle.

Native v7 status stream:
  in progress, not built / smoke-tested / compared.

Review debt:
  many goals after 5130 are implemented / review pending. Do not upgrade them
  to reviewed status without external review.
```

## Next Planned Work

### Step 1: Finish Goal5397 As A Native V7 Smoke / No-Go Gate

Immediate tasks:

```text
1. Add focused Goal5397 tests for:
   - native symbol/prototype/source plumbing;
   - Python front-door metadata and app-neutral naming;
   - no X-HD / figure / author semantics in RTDL core/front door;
   - fail-closed behavior when the native symbol is unavailable.

2. Build the native OptiX code on POD using scripts/current_pod_ssh.py.

3. Run a tiny synthetic native status-stream smoke:
   - verify the symbol is exported;
   - verify rows are emitted;
   - verify row columns are populated consistently;
   - write a result JSON artifact.

4. If the smoke fails at compile/runtime:
   - report the exact failure;
   - keep explicit -lb fail-closed;
   - do not claim v7 support.

5. If the smoke passes:
   - run the full Dragon -> AsianDragon status-stream comparison against
     Goal5387 author trace v2 only if runtime cost is feasible;
   - compare row_count, status_count_offloading, hash/samples, and status
     transition fields.
```

Goal5397 exit labels:

```text
native_v7_status_stream_smoke_passed__full_parity_pending
native_v7_status_stream_compiles_but_denominator_mismatch
native_v7_status_stream_no_go__explicit_lb_remains_fail_closed
```

### Step 2: If V7 Smoke Passes, Run Goal5398 Full Parity Gate

Goal5398 should compare against the Goal5387 author trace v2 oracle:

```text
active_count = 437,645
author raw rows = 27,133,990
author raw hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

Minimum pass requirements:

```text
active_query_count parity;
row_count parity or explicitly bounded no-go;
deterministic sample/hash comparison where row semantics are comparable;
status_count_offloading comparison;
current-best before/after fields present;
feedback / miss / completed / aborted telemetry accounted for or explicitly
declared absent.
```

### Step 3: Decide Explicit `-lb`

After Goal5397/5398:

```text
If row/hash or deterministic-sample parity is achieved:
  continue toward explicit -lb support, still without Figure 7/11 or performance
  claims until those denominators are reviewed.

If row-count remains 56x or otherwise mismatched:
  record a native v7 no-go and keep explicit -lb fail-closed.

If v7 requires hard-coded 6x/62x constants or author-only X-HD semantics:
  reject it as a generic RTDL system feature and keep -lb unsupported.
```

### Step 4: Consolidated Review Packet

Prepare a strict review packet for:

```text
Goals5386-5397, or Goals5386-5398 if Goal5398 follows immediately.
```

The packet should ask reviewers specifically:

```text
Does the author v2 oracle support the claimed comparison?
Does v7 emit a real status stream rather than remapping old rows?
Are app-specific X-HD constants absent from RTDL core/native?
Is explicit -lb still fail-closed until row/hash evidence passes?
Are Figure 7, Figure 11, and performance-ratio claims still forbidden?
```

### Step 5: Continue Full Paper Reproduction Only After `-lb` Decision

If explicit `-lb` remains unsupported, the next project move should be honest
closeout of the `-lb` line and a return to dataset/figure availability:

```text
exact input provenance;
missing Figure 7/8/9/10/11 denominators;
public Level-B candidate expansion only where author rerun and RTDL value both
match.
```

If explicit `-lb` becomes supported, the next work should still be staged:

```text
first row/hash/status correctness;
then memory denominator review;
then Figure 7/11 figure-level gates;
then performance matrix.
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

Expected POD usage for the next stage:

```text
Goal5397:
  required for native build and synthetic status-stream smoke.

Goal5398:
  required for full Dragon -> AsianDragon status-stream row/hash comparison.

No POD needed:
  purely local source-level tests, report writing, review packet preparation,
  and memory updates.
```

Before declaring the POD broken:

```text
run wrapper preflight;
do not use naked SSH;
do not use old/default SSH keys.
```

## Schedule / Effort Estimate

This is a planning estimate, not a promise:

```text
Goal5397 source/tests/report:
  small-to-medium; same work session if native compile is clean.

Goal5397 POD build/smoke:
  medium; may require one or more compile-fix cycles because it touches native
  OptiX ABI and launch params.

Goal5398 full row/hash gate:
  medium-to-large; only worth running after Goal5397 smoke passes.

Consolidated review packet:
  small once artifacts exist.

Full explicit -lb support:
  unknown; depends on whether a generic v7 status stream can match the author
  oracle without X-HD-specific constants.
```

## Allowed Current Summary

```text
X-HD is strong on Level-B directed-Hausdorff scalar correctness and has produced
real generic RTDL system APIs. It is not full paper reproduction. The current
hard blocker is explicit -lb status-stream parity. v6 remap is rejected; Goal5397
has started a real generic native v7 status-stream implementation, but it is
not yet built or validated. The next work is POD build/smoke, then row/hash
comparison against the Goal5387 author trace v2 oracle.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports explicit -lb.
Goal5397 is complete.
The v7 status stream matches author row/hash parity.
The missing 6x-active delta is solved.
RTDL has Figure 7 or Figure 11 reproduction.
RTDL has same-denominator author performance parity.
The fast route has exact per-source witnesses.
Public Stanford Dragon/HappyBuddha is exact paper input.
```
