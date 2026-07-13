# X-HD Comprehensive Midterm Report After Goal5402

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__status_state_native_smoke_passed__explicit_lb_parity_open__full_paper_not_complete
```

## 1. Executive Summary

X-HD is now the active major paper-reproduction project. The project has made
real progress, but it has not yet reached full paper reproduction.

The strongest current achievement is:

```text
RTDL reproduces the author HDResult on the public Stanford Dragon -> HappyBuddha
Level-B representative workload:

author hd_exec HDResult = 0.12572988867759705
RTDL route distance       = 0.12572988629271128
absolute difference       ~= 2.38e-9
```

The strongest current performance line is:

```text
Goal5211 fresh scalar route ~= 0.849s
Goal5212 fresh total including input load ~= 1.531s
Goal5211 explicit-warm route median ~= 0.362s
Goal5212 explicit-warm measured case total ~= 0.288s
```

This fast route is **exact-value-only** for directed Hausdorff / max-nearest:

```text
per_source_witness_exact = false
409,376 / 437,645 sources early-abort
```

Therefore it is valid for the final directed-HD scalar value, but not for
consumers that require exact per-source nearest witnesses.

The newest system work is Goal5402:

```text
Goal5402 builds and executes a generic native status-state-machine smoke on POD.
matched = true
native symbol = rtdl_optix_active_query_status_state_machine_smoke_v1
```

This is meaningful system progress, but it is still a synthetic smoke. It does
not yet close the author explicit `-lb` status-stream row/hash parity gap.

## 2. Core Goal

The project objective is:

```text
Build an X-HD paper-reproduction app on top of RTDL, while improving RTDL as a
general spatial/dataflow language rather than turning RTDL core into an X-HD
app-specific codebase.
```

There are two simultaneous success criteria:

1. Paper-app evidence: reproduce the author X-HD behavior as far as the
   available paper, source code, logs, and datasets allow.
2. System improvement: extract generic RTDL APIs from the app pressure test.

The current line has succeeded on the second criterion in several places and
has partially succeeded on the first criterion. Full paper reproduction remains
open because exact paper input files/hashes and several figure-level contracts
are still unavailable or unclosed.

## 3. Completed And Reviewed Foundation

The following goals are considered completed and externally reviewed:

```text
Goal5110
  X-HD scaffold and provenance.

Goals5111-5126
  Bounded same-input author JSON gates, RTDL value gates, and a directed-vs-
  symmetric discriminating fixture.

Goals5127-5128
  Generic nearest/witness/max-nearest extraction and a non-Hausdorff consumer.

Goal5129
  Full-reproduction plan with exact-dataset provenance discipline.
```

Important durable decisions from this phase:

```text
X-HD author contract = directed input1 -> input2 Hausdorff distance.
It is not symmetric Hausdorff.

Hausdorff remains an app-level composition.
RTDL core exposes generic nearest/witness/reduction primitives.

Exact paper dataset identity requires file/hash or equivalent provenance.
Matching count, Gini, log value, or HDResult is not enough.
```

## 4. Implemented / Review-Pending Body Of Work

Many later X-HD goals are implemented but remain review pending. They must not
be silently upgraded to "reviewed and approved."

Major implemented / review-pending areas:

```text
Goals5130-5131
  Paper target matrix and dataset provenance matrix.

Goals5132-5136
  Stanford graphics Level-B same-source acquisition and sample correctness.

Goals5137-5148
  Algorithm gap analysis, grid-cell candidate APIs, nearest-state frontier API,
  generic cell-MBR traversal ABI, and native OptiX 3-D broadphase / frontier
  bricks.

Goals5149-5170
  Cell-MBR frontier nearest continuation, representative route gates, seeded
  route improvements, vectorized seed / continuation, and route-local
  performance scaling.

Goals5175-5188
  Author-log workload mapping, public full Dragon/HappyBuddha acquisition,
  full-public author `hd_exec` gate, RTDL all-source route gate, and phase
  boundary matrix.

Goals5189-5212
  Full-public route optimization sequence and exact-value early-break route.

Goals5379-5402
  Active-query status reference / bridge / author trace / native status-stream
  parity probes / generic status-state-machine contract / native smoke.
```

The current report treats these as **implemented evidence**, not as externally
approved unless a separate review file exists.

## 5. Paper-Reproduction Status

### 5.1 Bounded Same-Input

Status:

```text
complete and externally reviewed through Goal5126
```

What it proves:

```text
RTDL can match author `HDResult` on controlled same-input fixtures.
The direction contract is author input1 -> input2.
```

What it does not prove:

```text
full paper reproduction;
exact paper dataset reproduction;
author X-HD RT-core algorithm reproduction;
performance parity.
```

### 5.2 Level-B Public Representative Workload

Current strongest public representative workload:

```text
source = public Stanford Dragon
target = public Stanford HappyBuddha
source points = 437,645
target points = 543,652
```

Correctness evidence:

```text
Goal5186 author hd_exec HDResult = 0.12572988867759705
Goal5187 RTDL route distance     = 0.12572988629271128
absolute difference              ~= 2.38e-9
```

Critical wording:

```text
This matches the author rerun on the public Level-B workload.
It must not be phrased as exact paper-input reproduction.
It must not be phrased as broad Level-B reproduction across all categories.
It is currently one strong public workload: Dragon -> HappyBuddha.
```

The paper-branch log proximity is useful but not sufficient for exact dataset
identity. Previous review explicitly required the report to say:

```text
RTDL matches author rerun, not paper-log bytes.
The residual paper-log gap is evidence that public data != exact paper input.
```

### 5.3 Full Paper Reproduction

Status:

```text
not complete
```

Open blockers:

```text
exact paper input file/hash provenance is unavailable;
Figure 5/7/8/9/10/11 are not fully reproduced;
author-vs-RTDL performance denominators are not aligned;
explicit X-HD -lb status-stream semantics remain unclosed.
```

## 6. Performance Status

The project has strong RTDL route-local improvement, but it does not yet have a
fair author-vs-RTDL performance ratio.

### 6.1 Route Evolution

Representative route-local milestones on the Dragon -> HappyBuddha line:

```text
Goal5188 baseline full-public route wall          ~= 7.30s
Goal5189 local-grid seed route wall               ~= 5.98s
Goal5191 inline512 empty-frontier route wall      ~= 3.65s
Goal5195 intersection current-best pruning        ~= 2.6s
Goal5196 dense grid-cell lookup route wall        ~= 2.26s
Goal5203 NumPy matrix input route wall            ~= 1.238-1.239s
Goal5204 linear max-nearest reducer route wall    ~= 1.17-1.18s
Goal5211 global-bound early-break fresh route     ~= 0.849s
Goal5212 fresh total including load               ~= 1.531s
Goal5211 explicit-warm route median               ~= 0.362s
Goal5212 explicit-warm measured case total        ~= 0.288s
```

### 6.2 Why No Author Ratio Yet

Goal5188 intentionally separated denominators:

```text
author internal Running.AvgTime
author process wall time
RTDL route time
RTDL total time
```

No ratio is authorized unless these are aligned on:

```text
dataset;
hardware;
phase boundary;
included setup/load/output costs;
runtime regime: cold process vs warm long-lived process vs replay/prepared.
```

Current conclusion:

```text
Performance improved substantially inside RTDL's route, but author-vs-RTDL
performance parity or speedup is not established.
```

## 7. System Improvements Extracted Into RTDL

X-HD has already improved RTDL as a general system. The important system assets
are not X-HD-specific primitives; they are generic spatial/dataflow components.

### 7.1 Generic Nearest / Witness / Reduction

Extracted through Goals5127-5128:

```text
pairwise L2 candidate rows
nearest witness
max-nearest distance witness
non-Hausdorff consumer proving genericity
```

Meaning:

```text
Hausdorff is now an app-level composition of generic RTDL primitives, not a
special RTDL core primitive.
```

### 7.2 Generic Grid / Cell-MBR / Frontier Route

Implemented across Goals5138-5160 and beyond:

```text
grid-cell candidate APIs;
nearest-state frontier API;
cell-MBR traversal ABI;
native OptiX 3-D AABB / cell-MBR frontier collection;
frontier row table modes;
active-row-only emission;
seeded nearest-state continuation.
```

Meaning:

```text
RTDL now has reusable building blocks for spatial broadphase + nearest-state
frontier traversal beyond X-HD.
```

### 7.3 Route And Front-Door Improvements

Implemented across Goals5161-5205:

```text
generic Numba seed executor;
generic Numba nearest-continuation executor;
packed coordinate matrix reuse;
NumPy matrix input front door;
linear max-nearest reducer;
fast app-owned ASCII PLY matrix loader.
```

Ownership split:

```text
RTDL owns generic array/frontier/reducer mechanisms.
The X-HD app owns PLY parsing, author wrappers, comparator tolerances, and
paper-specific route wiring.
```

### 7.4 Generic Status-State Machine Work

Current status:

```text
Goal5401 defines a generic active-query status-state-machine native spike
contract.

Goal5402 builds and runs a native synthetic smoke for that contract.
```

Native symbol:

```text
rtdl_optix_active_query_status_state_machine_smoke_v1
```

Python front door:

```text
active_query_status_state_machine_smoke_native(...)
```

This is system progress, but not X-HD explicit `-lb` completion.

## 8. Explicit `-lb` Status-Stream Problem

This is the current hard technical blocker.

Author trace v2 from Goal5387:

```text
active queries = 437,645
raw offload rows before sort/reduce = 27,133,990
raw row hash = 4333109858711462591
feedback_update_count = 294
```

RTDL native v7 parity gate from Goal5398:

```text
active_query_count_parity = true
RTDL v7 rows = 2,600,727
row_count_parity = false
hash_parity = false
feedback_update_count_parity = unresolved / null
```

Goal5400 exhausted existing knobs:

```text
no-inline / inline surfaces undercount;
emit-pruned / heavy-before-inline surfaces overflow by orders of magnitude;
existing route switches cannot repair the denominator.
```

Goal5402 current evidence:

```text
synthetic active queries = 3
synthetic raw offload rows = 2
feedback rows = 1
matched = true
```

Interpretation:

```text
RTDL now has a native generic smoke for the status-state contract, but not yet
the real author `-lb` row/hash/status/feedback semantics.
```

## 9. Completed Big Problems

1. Directed vs symmetric HD semantics are resolved.
2. Bounded same-input value reproduction is complete.
3. Hausdorff has been decomposed into generic primitives rather than embedded
   as a special core primitive.
4. Public Dragon -> HappyBuddha Level-B scalar HDResult matches author rerun.
5. The route no longer requires exact all-pairs materialization for the full
   public workload.
6. Route-local performance improved from multi-second baseline to sub-second
   scalar route under the early-break contract.
7. Exact paper dataset identity discipline is documented and enforced.
8. Existing explicit `-lb` knobs were tested and rejected before new native
   work was started.
9. A generic status-state-machine contract exists.
10. A native synthetic status-state smoke now builds and executes on POD.

## 10. Remaining Big Problems

1. Exact paper datasets are still not proven by file/hash provenance.
2. Full Figure 5/7/8/9/10/11 reproduction remains open.
3. Explicit X-HD `-lb` author trace row/hash/status/feedback parity remains
   open.
4. The fast early-break scalar route does not preserve exact per-source
   witnesses.
5. A fair author-vs-RTDL performance ratio remains unauthorized.
6. Many goals after Goal5130 are implemented / review pending rather than
   externally approved.
7. Current status-state native work is still synthetic and bounded, not full
   author trace execution.

## 11. Next Planned Work

### 11.1 Immediate Next Goal: Goal5403

Goal5403 should be a decision / gate goal, not another vague optimization.

It should read and reconcile:

```text
Goal5387 author trace v2 oracle;
Goal5398 RTDL native v7 mismatch evidence;
Goal5400 knob-exhaustion result;
Goal5401 status-state-machine contract;
Goal5402 native synthetic smoke artifact.
```

Goal5403 must decide one of:

```text
Option A:
  authorize a bounded X-HD app-shaped status-state oracle gate.

Option B:
  authorize direct full Goal5387 author-trace parity only if all native inputs
  and deterministic row/hash surfaces are ready.

Option C:
  keep explicit `-lb` fail-closed if parity requires X-HD-specific constants,
  author-only semantics, or app identity inside RTDL core/native.
```

Goal5403 should produce a machine-readable decision artifact with:

```text
active_count comparison;
raw row_count comparison;
row hash / deterministic sample comparison;
status_count_offloading comparison;
feedback_update_count comparison;
claim-boundary flags;
next-goal label.
```

### 11.2 Likely Follow-Up If Goal5403 Chooses Bounded Oracle

Potential Goal5404:

```text
Build a bounded app-shaped oracle gate that exercises raw offload rows +
feedback updates on a deterministic small fixture, then compare row count, row
hash/sample, status counts, and feedback counts.
```

This would bridge the gap between Goal5402's pure synthetic smoke and Goal5387's
huge full author trace.

### 11.3 Follow-Up If Bounded Oracle Passes

Potential Goal5405:

```text
Integrate the status-state machine into the real X-HD candidate/frontier stream
without adding X-HD-specific core semantics.
```

Potential Goal5406:

```text
Run a full Goal5387 author-trace parity gate:
  active_count;
  raw row_count;
  raw hash;
  sample rows;
  status_count_offloading;
  feedback_update_count.
```

### 11.4 Follow-Up If Full `-lb` Parity Passes

Only after full row/hash/status/feedback parity:

```text
revisit Figure 7 / explicit load-balance evidence;
revisit Figure 11 / memory denominator evidence;
prepare a reviewed performance matrix with matched phase boundaries.
```

### 11.5 If Full `-lb` Parity Fails

If parity requires app-specific semantics:

```text
stop explicit -lb support for this version;
record fail-closed reason;
keep Level-B scalar route as the strongest current X-HD evidence;
do not smuggle X-HD constants into RTDL core.
```

## 12. POD Use Plan

Any native continuation requires POD.

Use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Do not use naked SSH.

Before declaring POD blocked:

```text
run wrapper preflight;
confirm current key ~/.ssh/id_ed25519_rtdl_codex_current_pod;
record hostname/GPU/driver;
separate auth failure from remote build/test failure.
```

Current last-known working POD evidence from Goal5402:

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
hostname = 45c502cfccb5
GPU = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
```

Expected POD use for the next stage:

```text
Goal5403: likely local JSON decision unless it includes fresh native checks.
Goal5404: POD required if native bounded oracle is executed.
Goal5405+: POD required for native integration and full author-trace parity.
```

## 13. Review / Documentation Plan

The next review packet should include:

```text
Goal5402 result and call-for-review;
Goal5403 decision artifact and call-for-review;
any Goal5404 bounded oracle result if implemented;
the current claim-boundary table;
the route-performance table with early-break caveat;
the explicit list of review-pending goals.
```

The packet must preserve these forbidden summaries:

```text
Do not say "full X-HD paper reproduction is complete."
Do not say "RTDL matches paper log exactly" when evidence is author rerun or
same-source public data.
Do not say "Level-B complete" without saying "single public workload" unless
more workloads have passed.
Do not say "exact witnesses" for Goal5211 early-break route.
Do not report author-vs-RTDL speedup or parity without matched denominators.
Do not call Goal5402 explicit `-lb` support.
```

## 14. Completion Expectations

Short term:

```text
Goal5403 should clarify whether we can move from synthetic native status-state
smoke to bounded app-shaped oracle, direct full author-trace parity, or
fail-closed explicit -lb.
```

Medium term:

```text
If bounded and then full status-state parity pass, revisit Figure 7 and Figure
11 under strict denominator control.
If they do not pass, close explicit -lb as unsupported and keep scalar Level-B
route as the current strongest evidence.
```

Long term:

```text
Full paper reproduction requires exact dataset provenance or a documented
reason that exact datasets are unavailable, plus a reviewed mapping from
available public workloads to paper claims. Without exact inputs, the strongest
honest state remains Level-B same-source representative reproduction.
```

## 15. Bottom Line

The project is in a strong but unfinished state.

What is real:

```text
bounded X-HD correctness;
generic RTDL system extraction;
public Dragon -> HappyBuddha scalar correctness;
large route-local performance improvement;
native generic status-state smoke on POD.
```

What is still open:

```text
exact paper inputs;
full paper figures;
explicit -lb status-stream parity;
fair author-vs-RTDL performance ratio;
external review of the large implemented goal batch.
```

The next decisive step is not another micro-optimization. It is Goal5403: decide
the next legitimate status-state gate, based on the Goal5387 author oracle, the
Goal5398 mismatch, the Goal5400 knob exhaustion result, and the Goal5402 native
smoke.
