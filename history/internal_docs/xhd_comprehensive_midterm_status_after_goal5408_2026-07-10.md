# X-HD Comprehensive Midterm Status After Goal5408

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__full_cover_surface_real__cell_namespace_remap_not_enough__explicit_lb_unsupported__full_paper_not_complete
```

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5407_2026-07-10.md
```

## 1. Executive Summary

X-HD remains the active full-paper-reproduction project. The current state is:

```text
bounded same-input value reproduction       = complete and externally reviewed
generic nearest/witness system extraction   = complete and externally reviewed
Level-B public scalar line                  = strong
exact paper datasets                        = not proven
full paper reproduction                     = not complete
explicit -lb / raw author offload stream    = unsupported
```

The strongest scalar Level-B line remains public Stanford
Dragon -> HappyBuddha:

```text
author hd_exec HDResult = 0.12572988867759705
RTDL route distance     = 0.12572988629271128
absolute difference     ~= 2.38e-9
```

The strongest fast scalar route remains:

```text
fresh route                         ~= 0.849s
fresh total including input load    ~= 1.531s
explicit-warm route median          ~= 0.362s
explicit-warm measured case total   ~= 0.288s
```

Boundary:

```text
This fast scalar route is exact for final directed-Hausdorff / max-nearest
value, but early-aborted per-source witnesses may be approximate.
```

The newest work is Goal5408. It checks whether Goal5407's author sample-row
gap is merely a compact/original cell-id namespace mismatch. Result:

```text
simple compact/original namespace remap does not recover sampled author rows.
```

Therefore the next explicit `-lb` decision is no longer "add missing rows" or
"rename cell ids"; it is whether a generic status-machine semantics explanation
exists, or whether explicit `-lb` must stay fail-closed.

## 2. What Has Been Completed

### 2.1 Bounded X-HD base

Completed and externally reviewed:

```text
Goal5110: X-HD scaffold / provenance.
Goals5111-5126: bounded same-input author JSON and RTDL route gates, including
                 directed-vs-symmetric discrimination.
Goals5127-5128: generic nearest pipeline extraction and non-Hausdorff consumer.
Goal5129: full-reproduction plan with review amendment incorporated.
```

This gives the project a valid bounded X-HD value reproduction and proves the
author contract is directed input1 -> input2, not symmetric Hausdorff.

### 2.2 Generic system extraction

X-HD has produced real app-neutral RTDL assets:

```text
pairwise L2 candidate rows
nearest witness
max-nearest / directed-Hausdorff reducer
grid-cell descriptors
cell-MBR candidate/frontier rows
nearest-state seed/frontier contracts
native 3-D cell-MBR OptiX traversal front doors
coordinate-matrix front-door convention
linear finite max-nearest reduction
active-query status-stream contracts and native smoke
```

The strongest system-design win is that Hausdorff itself is not a core
primitive. It is an app-level composition over generic nearest/witness/reducer
building blocks.

### 2.3 Representative Level-B scalar correctness

The public Dragon -> HappyBuddha route matches author HDResult at full public
scale. This is meaningful same-source representative evidence, but still not
exact paper dataset reproduction.

## 3. What Is Not Complete

The following are still not complete:

```text
exact paper input file/hash provenance;
full Figure 5-11 reproduction;
Figure 7 load-balance / explicit -lb parity;
Figure 11 same-denominator memory parity;
author-vs-RTDL performance ratio;
full X-HD paper reproduction.
```

Known dataset blocker:

```text
matching counts, bounding boxes, Gini, or HDResult is not exact input identity.
exact dataset status requires file/hash or equivalent provenance.
```

## 4. Explicit `-lb` Status

The current explicit `-lb` oracle is Goal5387 author trace v2:

```text
active queries          = 437,645
author raw offload rows = 27,133,990
author raw row hash     = 4333109858711462591
feedback_update_count   = 294
```

RTDL explored several surfaces:

```text
bridge rows             = 2,188,225
native v7 status rows   = 2,600,727
default raw kind2 rows  = 21,006,960
full-cover rows         = 24,508,120
author raw rows         = 27,133,990
```

The full-cover surface is the closest known RTDL surface, but not parity.

## 5. Goal5406 / Goal5407 / Goal5408 Findings

### Goal5406: real full-cover surface

```text
RTDL full-cover rows       = 24,508,120 = 56 * 437,645
author raw rows            = 27,133,990 = 62 * 437,645
delta                      = 2,625,870 = 6 * active_count
RTDL full-cover row hash   = 9732286907904247845
author raw row hash        = 4333109858711462591
hash parity                = false
```

Goal5406 proves RTDL can generate the real full-cover surface. It does not
prove explicit `-lb`.

### Goal5407: sample membership

Goal5407 shows RTDL full-cover is uniform:

```text
rows per active = exactly 56 for every active source
```

But sampled author rows are absent from the RTDL full-cover surface:

```text
source=11168,  author_cell=2924, present=false
source=210712, author_cell=17,   present=false
source=437119, author_cell=17,   present=false
```

Classification:

```text
author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap
```

### Goal5408: cell namespace reconciliation

Goal5408 checks the simple namespace hypothesis.

Grid contract:

```text
cell_id_contract  = compact_zero_based_with_original_cell_ids
grid_shape        = [96, 60, 72]
cell_count        = 14,710
compact id range  = [0, 14,709]
original id range = [3,406, 413,966]
```

Author sample reconciliation:

```text
source=11168, author_cell=2924:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false

source=210712, author_cell=17:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false

source=437119, author_cell=17:
  exists as global compact id?  true
  exists as global original id? false
  present for this source as compact?  false
  present for this source as original? false
```

Classification:

```text
author_sample_cell_ids_exist_globally_but_not_for_author_sources
```

Interpretation:

```text
The sample rows are not recovered by RTDL's compact/original id mapping.
The author sample cells exist as global compact ids, but they are not part of
the RTDL full-cover row set for those source ids. Therefore simple namespace
remapping is not enough.
```

## 6. Current Technical Root Cause

The remaining explicit `-lb` problem is now best described as:

```text
author raw offload stream semantics != current RTDL full-cover/status stream
```

More specifically:

```text
not only row count;
not only compact-vs-original cell id namespace;
not solved by v6 row remap;
not solved by existing status-stream knobs;
not solved by bounded 56+6 shape alone.
```

The next decision is whether this semantic gap can be represented by a generic
active-query status-machine transition, or whether it is author/app-specific
enough that explicit `-lb` must stay unsupported.

## 7. Validation

Goal5408 POD:

```text
POD_OK
hostname = 45c502cfccb5
GPU      = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD focused tests:

```text
Ran 11 tests OK (skipped=1)
```

POD real runner:

```text
status  = cell_namespace_reconciliation_complete__sample_rows_not_recovered
matched = true
```

Local validation after artifact download:

```text
$env:PYTHONPATH='src'; py -m json.tool `
  Paper-reproduction-apps/x-hd-paper/results/xhd_goal5408_cell_namespace_reconciliation_pod.json

$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5408_cell_namespace_reconciliation_test `
  tests.goal5407_full_cover_delta_membership_probe_test `
  tests.goal5406_real_full_cover_surface_stream_gate_test `
  tests.goal5405_full_cover_delta_status_bridge_test

Ran 20 tests OK
```

## 8. Next Plan

### Goal5409: status-machine semantics or fail-closed decision

Goal5409 should treat fail-close as the evidence-weighted default.  Continuing
is not an equal branch: it requires a named app-neutral state transition,
non-X-HD generic evidence, and bounded gates before any full X-HD row-identity
attempt.

Recommended branch: fail-close explicit `-lb`.

```text
The current evidence already shows that row count, full-cover surface, and
cell-id namespace are insufficient.  If the remaining row identity requires
author-only option semantics or X-HD constants, close explicit -lb as
unsupported under the current RTDL execution model.
```

Exception branch: continue with a generic semantic probe only if all of the
following can be stated before implementation:

```text
name the generic transition;
state why it is not X-HD-specific;
define row-count + row-identity + hash/sample evidence required;
provide or plan a non-X-HD consumer/proof;
start with bounded gate before any full-public native gate.
```

The fail-closed outcome would still preserve the successful parts of the
project:

```text
bounded X-HD value reproduction;
Level-B public scalar route;
generic nearest/witness/max-nearest system extraction;
generic cell-MBR route work;
explicit documentation of the author RT-core / -lb gap.
```

### Goal5410: consolidated review packet

After Goal5409, write a consolidated review packet for:

```text
Goal5401 status-state contract;
Goal5402 native smoke;
Goal5404 bounded oracle;
Goal5405 bounded full-cover bridge;
Goal5406 real full-cover surface;
Goal5407 sample membership;
Goal5408 namespace reconciliation;
Goal5409 continue/fail-close decision.
```

## 9. POD Usage Expectation

Goal5409 decision itself can start locally from existing artifacts:

```text
xhd_goal5387_author_trace_v2_execution.json
xhd_goal5406_real_full_cover_surface_stream_gate_pod.json
xhd_goal5407_full_cover_delta_membership_probe_pod.json
xhd_goal5408_cell_namespace_reconciliation_pod.json
```

POD is needed only if Goal5409 authorizes a new native/status-state probe.

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

## 10. Claim Boundary

Allowed:

```text
X-HD has a strong Level-B public same-source scalar line and real generic RTDL
system extraction. Goal5408 shows the current explicit -lb gap is not explained
by simple compact/original cell-id remapping.
```

Forbidden:

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
Figure 7 reproduction;
Figure 11 reproduction;
explicit -lb support;
row/hash parity with author raw stream;
author-vs-RTDL performance ratio;
warm/diagnostic numbers as default fresh performance;
X-HD-specific logic in RTDL core/native.
```
