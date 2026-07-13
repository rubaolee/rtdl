# X-HD Comprehensive Midterm Status After Goal5398

Date: 2026-07-10

## Executive Summary

X-HD paper reproduction has made real progress, but full paper reproduction is
not complete.

The project has achieved:

- bounded same-input X-HD value reproduction;
- generic RTDL system extraction for nearest/witness/max-nearest reductions;
- a strong Level-B public Dragon -> HappyBuddha directed-Hausdorff scalar
  reproduction against the author rerun;
- a substantially optimized RTDL route for that scalar;
- a real native v7 active-query status-stream front door.

The main blocker is now explicit X-HD `-lb` parity. Goal5398 shows the current
native v7 status stream does not match the author `-lb` trace:

```text
author rows = 27133990
RTDL v7 rows = 2600727
RTDL / author = 0.09584756978240207
hash parity = false
explicit -lb = fail-closed
```

The current honest status label is:

```text
level_b_scalar_strong__generic_system_extraction_real__fast_scalar_route_available__native_v7_status_stream_denominator_mismatch__explicit_lb_fail_closed__full_paper_not_complete
```

## Core Objective

The full objective remains:

```text
Make the X-HD paper app a serious RTDL/Python reproduction of the author
C++/CUDA/OptiX work, while preserving RTDL as a general spatial language and
not turning the core into an X-HD-specific app.
```

This means two tracks must both hold:

1. Paper reproduction evidence must be honest about input provenance, phase
   boundaries, author options, and performance denominators.
2. Any system improvement must be app-neutral and reusable outside X-HD.

## What Is Completed

### 1. Provenance Scaffold And Bounded Same-Input Line

Status:

```text
completed and externally reviewed through Goal5126
```

What this proves:

- author source and CLI/JSON contract were pinned;
- bounded same-input gates can compare author output with RTDL output;
- directed-vs-symmetric Hausdorff semantics were disambiguated with a
  directed-asymmetric fixture;
- RTDL and author were verified to compute directed input1 -> input2 HD in the
  bounded gate.

What it does not prove:

- full paper dataset reproduction;
- author RT-core algorithm reproduction;
- Figure 5-11 reproduction;
- performance parity.

### 2. Generic System Extraction From X-HD

Status:

```text
completed and externally reviewed through Goals5127-5128
```

System APIs extracted:

```text
pairwise_l2_distance_candidate_rows_numpy_columns
nearest_witness_numpy_columns
max_nearest_distance_witness_numpy_columns
directed_hausdorff_2d_numpy_columns = composition wrapper
directed_hausdorff_3d_numpy_columns = composition wrapper
```

Important point:

```text
Hausdorff itself remains an app-level composition.
RTDL exposes generic nearest/witness/reduction pieces.
```

Goal5128 added a non-Hausdorff facility-service-radius consumer, which is the
genericity proof that the primitives are not X-HD-only.

### 3. Level-B Public Dragon -> HappyBuddha Scalar Correctness

Status:

```text
strong representative same-source correctness, not exact paper reproduction
```

Current strongest scalar evidence:

```text
source = Dragon public mesh
target = HappyBuddha / AsianDragon public mesh
source count = 437645
target count = 3609600
author rerun HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
absolute diff ~= 2.38e-9
```

Important caveat:

```text
RTDL matches the author rerun closely.
The author rerun is not byte-identical to the paper-branch log.
The paper-input provenance gap remains visible.
```

### 4. Scalar Route Performance Progress

The route has moved from multi-second full-public execution toward a sub-second
scalar route, under carefully separated regimes.

Representative progression:

```text
Goal5191: route wall ~= 3.65s
Goal5194: route wall ~= 3.46s
Goal5195: route wall ~= 2.6s
Goal5196: route wall ~= 2.26s
Goal5202: no-timing route wall ~= 2.027s
Goal5203: route wall ~= 1.238-1.239s
Goal5204/5205: route wall ~= 1.16-1.18s
Goal5207: explicit warm route ~= 0.626s
Goal5211: early-break fresh route ~= 0.849s, explicit-warm route ~= 0.362s
Goal5212: fresh full total including load ~= 1.531s, explicit-warm measured
          case total ~= 0.288s
```

Claim boundary:

```text
Goal5211 early-break is exact for the directed-HD max scalar contract.
It is not exact for all per-source nearest witnesses.
per_source_witness_exact = false
early-aborted sources = 409376 / 437645
```

Therefore the fast path is a directed-Hausdorff / max-nearest scalar route, not
a generic exact nearest-witness route.

### 5. Explicit `-lb` Investigation

Status:

```text
in progress, currently fail-closed
```

Author trace v2 oracle from Goal5387:

```text
active queries = 437645
raw offload rows = 27133990 = 62 * active
raw hash = 4333109858711462591
status_count_offloading_append = 27133990
feedback_update_count = 294
```

Current RTDL native v7 result from Goal5398:

```text
active queries = 437645
native v7 rows = 2600727
row ratio = 0.09584756978240207
row delta = 24533263
raw hash = 12842101464127179321
row parity = false
hash parity = false
```

Interpretation:

```text
Goal5397 proved a real generic native v7 status-stream ABI and synthetic smoke.
Goal5398 proved that this ABI still does not match author -lb status semantics.
Explicit -lb remains unsupported.
```

## Big Problems Already Solved

### A. Directed vs Symmetric HD

Solved by Goal5126 with an asymmetric fixture:

```text
directed a->b = 0.5
directed b->a = 9.0
symmetric = 9.0
author HDResult = 0.5
RTDL directed a->b = 0.5
```

This prevents a definition-level apples-to-oranges bug.

### B. App vs System Boundary

Solved enough for current X-HD work:

```text
RTDL core/system owns generic nearest/witness/reduction primitives.
X-HD app owns paper wrappers, author build/run, tolerances, datasets, and
phase claims.
```

### C. Full Public Scalar Route

The scalar route now matches the author rerun on the largest public Dragon ->
HappyBuddha workload available in the current line.

### D. Performance Regime Discipline

The project now separates:

```text
author internal Running.AvgTime
author process wall
RTDL route time
RTDL total time
cold one-shot
warm same-process
explicit warmup
prepared replay
```

No performance ratio is allowed unless denominator, hardware, dataset, phase,
and regime match.

### E. POD Operation Discipline

The correct POD path is established:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<cmd>"
```

Do not use naked SSH for this project.

## Big Problems Still Open

### 1. Exact Paper Inputs

Exact paper input files or hashes are still not available.

Therefore:

```text
Level-B representative public input = strong evidence
exact paper dataset reproduction = not complete
```

### 2. Explicit X-HD `-lb`

Goal5398 establishes that the current native v7 stream is still far from the
author `-lb` stream:

```text
RTDL v7 emits about 2.60M rows.
Author emits about 27.13M rows.
```

This is not a small ordering/hash bug. It is a semantic denominator mismatch.

### 3. Figure 7 / Figure 11

Figure-level reproduction remains unavailable because explicit `-lb` semantics
and exact paper input provenance are not closed.

### 4. Per-Source Witness Exactness Under Early-Break

The fast Goal5211 route is exact for the max scalar, but most per-source
witnesses may be approximate because early-break stops after global-bound
sufficiency.

### 5. Author Runtime Parity

No fair author-vs-RTDL performance ratio is currently authorized. The author
and RTDL measurements still involve different denominators and implementation
contracts.

## Planned Next Work

### Goal5398 Review

Send Goal5398 to external review.

Expected review focus:

- whether the native v7 mismatch conclusion is supported;
- whether explicit `-lb` remains correctly fail-closed;
- whether the next gate should be semantic redesign rather than another
  denominator remap.

### Goal5399 - Status-Machine Semantic Gap Decision

Purpose:

```text
Decide whether to build a generic native active-query status-state machine that
can reproduce the author explicit -lb offloading stream, or stop this line.
```

Required inputs:

- Goal5387 author trace v2;
- Goal5392/5393 surface decomposition;
- Goal5398 native v7 mismatch artifact.

Likely questions:

1. What exactly are the missing author phases that produce 62 rows per active?
2. Can they be expressed as a generic RTDL active-query status stream rather
   than an X-HD-only option?
3. Can feedback update count 294 be represented generically?
4. Is exact row/hash parity necessary for the project goal, or is scalar
   correctness plus partial algorithm evidence the right stopping point?

Exit labels:

```text
authorize_generic_status_state_machine_goal
OR stop_explicit_lb_trace_parity_line__level_b_scalar_only
```

### Goal5400+ If Authorized - Generic Status-State Machine

Only if Goal5399 authorizes it:

- implement a generic status-state machine;
- keep X-HD option names out of RTDL core/native;
- compare row count, hash, deterministic samples, status counts, and feedback
  counts against the author trace;
- keep figure and performance claims forbidden until matched.

### Data Provenance Follow-Up

Continue searching for exact paper inputs and hashes, but do not let that block
Level-B scalar reporting.

Acceptable states:

```text
exact_inputs_found_and_verified
OR exact_inputs_unavailable__level_b_public_only
```

### Final X-HD Packaging

When the status-stream decision is made:

- update `Paper-reproduction-apps/x-hd-paper/README.md`;
- update `data/manifest.json` and `results/README.md`;
- produce a final claim matrix;
- run leak scans;
- update memory files;
- send a consolidated review packet.

## POD Usage Expectation

POD is still required for:

- native OptiX builds;
- large Dragon -> AsianDragon route gates;
- author executable runs;
- status-stream parity tests;
- any GPU/native timing evidence.

POD is not required for:

- documentation;
- local unit tests that do not call native CUDA/OptiX;
- memory updates;
- static leak scans.

Current POD endpoint used for Goal5398:

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
```

Expected next POD work:

```text
Goal5399: mostly analysis, may use POD only for targeted trace probes.
If Goal5400 is authorized: native build + full-public trace gate, likely
minutes per iteration.
```

## Final Midterm Position

The current project is strong but not complete:

```text
Strong: directed-HD scalar correctness on a full public Level-B workload.
Strong: generic RTDL system extraction from X-HD.
Strong: scalar route performance has improved substantially.
Weak/open: exact paper input provenance.
Weak/open: explicit -lb status stream and Figure 7/11 parity.
Blocked: full paper reproduction claims.
```

The next decision is strategic: either invest in a generic status-state machine
to chase explicit `-lb`, or stop the X-HD line at Level-B scalar correctness
plus documented algorithm-gap evidence.
