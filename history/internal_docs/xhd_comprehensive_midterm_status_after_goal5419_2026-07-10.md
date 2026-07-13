# X-HD Comprehensive Midterm Status After Goal5419

## Status Label

```text
level_b_scalar_strong__same_pod_graphics_matrix_executed__explicit_lb_stopped__figure5_not_reproduced__full_paper_not_complete
```

## Executive Summary

The X-HD line has achieved strong Level-B same-source scalar correctness, has
extracted reusable RTDL system primitives, and now has a same-POD Level-B
graphics matrix for three Figure-5-like candidates.  It has **not** completed
full paper reproduction.

Current strongest positive evidence:

- bounded same-input X-HD value gates are complete and externally reviewed
  through Goal5126;
- generic nearest/witness/max-nearest extraction is complete and externally
  reviewed through Goals5127-5128;
- Level-B public graphics scalar correctness exists for Dragon/HappyBuddha,
  ThaiStatuette/HappyBuddha, and ThaiStatuette/AsianDragon;
- Goal5419 runs those three graphics cases on the same POD and records author
  internal timing, author process wall, RTDL route wall, RTDL process wall,
  input load, and witness exactness side by side.

Current hard blockers:

- exact paper input files/hashes are still unavailable;
- Figures 5-11 remain unreproduced under exact paper denominators;
- author-vs-RTDL performance ratios remain unauthorized;
- explicit X-HD `-lb` / load-balance row-identity support is stopped under the
  current RTDL execution model.

## What Is Complete

### Bounded Same-Input X-HD

Goals5111-5126 close bounded same-input scalar value reproduction:

```text
author HDResult matched by RTDL bounded routes
directed input1 -> input2 semantics proven by asymmetric fixture
not symmetric Hausdorff
```

This is value correctness under bounded fixtures. It is not full paper
reproduction.

### Generic System Extraction

Goals5127-5128 extract X-HD pressure into app-neutral RTDL building blocks:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
```

A non-Hausdorff facility/service-radius consumer proves these helpers are not
only an X-HD wrapper.

Later route work adds generic grid/cell-MBR/frontier/seed/native traversal
pieces. Those are system assets, but many later goals remain implemented /
review pending.

### Level-B Graphics Scalar Correctness

The strongest same-source public graphics line is:

```text
Dragon -> HappyBuddha
ThaiStatuette-scaled -> HappyBuddha
ThaiStatuette-scaled -> AsianDragon-scaled
```

These are public graphics inputs that match author rerun scalar values and
paper-branch author-log scalar values within tolerance. They are not exact paper
input bytes.

## Explicit `-lb` Line: Stopped

The `-lb` / load-balance row-identity line was investigated too deeply relative
to its evidence value.  It chased an implementation-level author offload stream
after exact dataset blockers were already known.  That stream is not needed for
the scalar HDResult evidence already achieved, and its direct paper-figure use
is blocked by missing exact datasets / same-denominator logs.

Evidence:

```text
Goal5406 RTDL full-cover rows = 24,508,120
Goal5387 author raw rows      = 27,133,990
delta                         = 2,625,870 = 6 * active_count
RTDL full-cover hash          = 9732286907904247845
author raw row hash           = 4333109858711462591
hash parity                   = false
```

Goal5407 showed sampled author rows are not present in the RTDL full-cover
surface. Goal5408 ruled out simple compact/original cell-id remapping. Goal5411
failed bounded sample-row recovery. Goal5412 fail-closed the current model, and
Goal5415 stopped the line.

Preserved system work:

```text
generic payload-transition trace contract
payload_transition_trace_summary_numpy_columns(...)
synthetic non-app trace behavior proof
```

Not authorized:

```text
explicit X-HD -lb support
Figure 7 reproduction
Figure 11 reproduction
author raw row/hash parity
memory/performance ratio
```

Any future continuation must first name an app-neutral status transition, prove
it with non-X-HD evidence, and pass bounded gates. It must not resume as an
X-HD-specific reverse-engineering chase.

## Goal5419 Same-POD Graphics Matrix

Goal5419 result:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json
```

POD:

```text
hostname = 45c502cfccb5
gpu      = NVIDIA RTX 4000 Ada Generation
driver   = 550.127.05
```

Execution status:

```text
same_pod_execution_claimed = true
matrix_rows_executed = 3
route_result_count = 6
matched = true
```

Critical preprocessing fix:

```text
all RTDL graphics commands include --translate-each-input-to-min-bound
```

This is required. Without it, Dragon/HappyBuddha produced an incorrect scalar
HDResult (`0.0778348243`); with it, the expected scalar is
`0.12572988629271128`.

Matrix summary:

| Case | Author AvgTime ms | Author process wall s | RTDL route | RTDL route wall s | RTDL process wall s | Exact witnesses |
|---|---:|---:|---|---:|---:|---|
| dragon_happy | 8.128 | 1.934 | fast-scalar | 0.540 | 2.243 | false |
| dragon_happy | 8.128 | 1.934 | exact-witness | 0.617 | 2.283 | true |
| thai_happy_scaled | 26.817 | 2.345 | exact-witness | 5.017 | 6.880 | true |
| thai_happy_scaled | 26.817 | 2.345 | fast-scalar | 1.099 | 3.035 | false |
| thai_asian_scaled | 19.281 | 2.437 | exact-witness | 10.805 | 12.748 | true |
| thai_asian_scaled | 19.281 | 2.437 | fast-scalar | 12.536 | 14.557 | false |

All RTDL scalar values match the same-POD author rerun scalar within `1e-6`.
All author reruns match the paper-branch author-log scalar within `1e-6`.

Interpretation:

```text
This is same-POD Level-B graphics evidence.
It is not Figure 5 reproduction.
It does not authorize an author-vs-RTDL ratio.
```

The ThaiStatuette/AsianDragon row is especially important: fast-scalar is slower
than exact-witness there, so global-bound early break is not a universal speed
win.

## Claim Boundary

Allowed:

- bounded same-input correctness;
- Level-B same-source scalar correctness;
- same-POD graphics matrix with separate denominator columns;
- route-local RTDL timing;
- exact-witness vs fast-scalar witness-contract distinction.

Forbidden:

- "full X-HD paper reproduced";
- "Figure 5 reproduced";
- author-vs-RTDL speedup/slowdown ratio;
- exact paper dataset claim for public/representative inputs;
- using fast-scalar evidence as exact per-source witness evidence;
- treating synthetic payload-transition traces as X-HD `-lb` support.

## Current Review State

Externally reviewed / approved foundation:

```text
Goal5110
Goals5111-5126
Goals5127-5128
```

Implemented / review pending:

```text
Goals5130-5419
```

This report does not silently promote review-pending goals to reviewed status.

## Next Plan

### Goal5420 - Matrix Consolidation And Decision

Goal5420 should decide:

1. stop and send the Goal5419 same-POD graphics matrix for strict review;
2. add a separate bounded-geo matrix packet using the partner/Triton runner
   family; or
3. return directly to exact dataset acquisition and figure blockers.

Default recommendation:

```text
Do not run more route micro-optimizations by default.
Consolidate Goal5419 and send for review.
```

### If A Bounded-Geo Matrix Is Authorized

It must be a separate packet because the geo rows use a different partner/Triton
runner family. It must keep:

```text
author scalar / RTDL scalar;
RTDL route wall / process wall;
input load;
partner/backend choice;
ratio_authorized = false.
```

### If Returning To Full Paper Reproduction Blockers

Priority remains:

```text
exact paper input provenance;
figure-by-figure data availability;
same-denominator timing only after data and phase boundaries align.
```

## POD Use Expectation

No additional POD is needed to review Goal5419.  POD is needed only if Goal5420
authorizes another execution packet, such as bounded geo or a new exact-input
probe.

If POD is used:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Never use naked SSH.
