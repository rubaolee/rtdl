# X-HD Comprehensive Midterm Status After Goal5405 / Goal5406 Planned

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__bounded_full_cover_delta_bridge_passed__real_full_stream_next__explicit_lb_unsupported__full_paper_not_complete
```

## 1. Executive Summary

X-HD is the active major paper-reproduction project. The project has made
substantial progress in two directions:

1. It has built a strong Level-B representative X-HD route on public Stanford
   Dragon -> HappyBuddha inputs.
2. It has extracted several generic RTDL system primitives from the app pressure
   test.

It has not yet completed full paper reproduction.

The strongest scalar correctness result remains:

```text
workload                  = public Stanford Dragon -> HappyBuddha
author hd_exec HDResult   = 0.12572988867759705
RTDL route distance       = 0.12572988629271128
absolute difference       ~= 2.38e-9
```

The strongest current scalar route timing line is:

```text
Goal5211 fresh route                         ~= 0.849s
Goal5212 fresh total including input load    ~= 1.531s
Goal5211 explicit-warm route median          ~= 0.362s
Goal5212 explicit-warm measured case total   ~= 0.288s
```

This fast route is exact for the final directed Hausdorff / max-nearest scalar
value, but not for all per-source witnesses:

```text
per_source_witness_exact = false
early-aborted sources    = 409,376 / 437,645
```

Therefore this route is valid for the final X-HD scalar value contract, not for
consumers that require exact per-source nearest-witness rows.

The newest explicit `-lb` work is Goal5405:

```text
bounded full-cover-delta bridge matched = true
active_count                             = 2
rows per active                          = 56 + 6 = 62
total rows                               = 124
```

Goal5405 is stronger than Goal5404 because it uses the explicit `-lb`
denominator shape selected by Goals5393-5394. It is still bounded. It does not
generate the real full-public author stream:

```text
Goal5387 author active queries = 437,645
Goal5387 author raw rows       = 27,133,990
Goal5387 author raw hash       = 4333109858711462591
```

The immediate next step is Goal5406: generate or account for the real
full-cover surface / full Goal5387 stream and compare row count, hash/sample,
status counts, and feedback evidence. Until that passes, explicit `-lb` support
remains unsupported and fail-closed.

## 2. Project Objective

The active goal is not merely to write a custom X-HD app. The project objective
is:

```text
Build an X-HD paper-reproduction app on top of RTDL while improving RTDL as a
general spatial/dataflow language.
```

This creates two success criteria:

1. Paper-app evidence: reproduce author X-HD behavior as far as the available
   paper, source code, logs, and public datasets allow.
2. System improvement: extract generic RTDL APIs rather than adding X-HD-only
   semantics to `src/rtdsl` or `src/native`.

The project is currently successful on bounded correctness and generic system
extraction, partially successful on Level-B public representative correctness,
and not yet successful on full paper reproduction or explicit `-lb` figure
reproduction.

## 3. Completed And Externally Reviewed Foundation

The following foundation is complete and externally reviewed:

```text
Goal5110
  X-HD scaffold and provenance.

Goals5111-5126
  Bounded same-input author JSON gates, RTDL route gates, and directed-vs-
  symmetric discriminating fixture.

Goals5127-5128
  Generic nearest/witness/max-nearest extraction and a non-Hausdorff consumer.

Goal5129
  Full-reproduction plan with exact-dataset provenance discipline.
```

Durable conclusions from this foundation:

```text
author contract = directed input1 -> input2 Hausdorff distance
not symmetric Hausdorff

Hausdorff remains an app-level composition.
RTDL core exposes generic nearest/witness/reduction primitives.

Exact paper dataset identity requires file/hash or equivalent provenance.
Matching counts, statistics, logs, or HDResult is not enough.
```

## 4. Implemented / Review-Pending Body Of Work

Many later goals are implemented but still review pending. They are valid
project evidence, but they must not be silently upgraded to externally approved.

Major implemented / review-pending blocks:

```text
Goals5130-5131
  Paper target matrix and dataset provenance matrix.

Goals5132-5136
  Stanford graphics Level-B same-source public PLY acquisition and sample gates.

Goals5137-5148
  Algorithm gap analysis, grid-cell candidate APIs, nearest-state frontier API,
  cell-MBR traversal ABI, and native OptiX 3-D broadphase / frontier bricks.

Goals5149-5170
  Cell-MBR nearest continuation, seeded route improvements, native frontier row
  production, vectorized seed / continuation, and scaling profiles.

Goals5175-5188
  Author-log workload mapping, public full Dragon/HappyBuddha acquisition,
  author hd_exec full-public gate, RTDL all-source route gate, and phase matrix.

Goals5189-5212
  Route optimization sequence through global-bound early break and no-copy
  all-source selection.

Goals5379-5405
  Active-query status references, author trace, native status-stream ABI,
  generic status-state smoke, bounded status-state oracle, and bounded
  full-cover-delta bridge.
```

The current report treats these goals as implemented evidence unless a separate
review file says otherwise.

## 5. Paper-Reproduction Status

### 5.1 Bounded Same-Input

Status:

```text
complete and externally reviewed through Goal5126
```

What it proves:

```text
RTDL can match author HDResult on controlled same-input fixtures.
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
source active count = 437,645
```

Correctness:

```text
Goal5186 author hd_exec HDResult = 0.12572988867759705
Goal5187 RTDL route distance     = 0.12572988629271128
absolute difference              ~= 2.38e-9
```

Important boundary:

```text
This matches the author rerun on the public Level-B workload.
It is not exact paper-input reproduction.
It is not broad Level-B reproduction across all categories.
It is one strong public workload: Dragon -> HappyBuddha.
```

The paper-branch log proximity is useful, but not enough to prove exact dataset
identity. Previous review required the line to say:

```text
RTDL matches author rerun, not paper-log bytes.
The residual paper-log gap is a data provenance warning.
```

### 5.3 Full Paper Reproduction

Status:

```text
not complete
```

Open blockers:

```text
exact paper dataset files / hashes remain unavailable;
Figure 7 explicit -lb is not reproduced;
Figure 11 memory denominator is not aligned;
author-vs-RTDL performance ratio is not authorized;
full figure-level result matrix is not complete.
```

## 6. Performance Evolution

The performance line improved in stages. These numbers are route-local RTDL
numbers unless explicitly stated otherwise. They are not author-vs-RTDL ratios.

Representative route evolution:

```text
Goal5187/5188 full-public baseline             ~= 18.8s class
Goal5189 local-grid seed                       ~= 5.98s
Goal5191 inline512 / empty-frontier             ~= 3.65s
Goal5194 payload-current-best prune             ~= 3.46s
Goal5195 intersection current-best prune         ~= 2.6s
Goal5196 dense cell lookup                       ~= 2.26s
Goal5202 packed coordinate matrix reuse          ~= 2.03s
Goal5203 NumPy matrix input front door           ~= 1.24s
Goal5204 linear max-nearest reducer              ~= 1.17-1.18s
Goal5205 fast ASCII PLY matrix loader            route ~=1.16-1.17s,
                                                  total ~=2.06s
Goal5211 global-bound early break                fresh route ~=0.849s
Goal5212 no-copy all-source runner               fresh total incl load ~=1.531s
Goal5211/5212 explicit warm regime               route ~=0.362s,
                                                  measured case total ~=0.288s
```

Claim boundary for the best scalar route:

```text
The final directed-HD scalar value matches author.
Per-source witnesses may be approximate after early break.
Warm numbers are explicit-warm diagnostics and must not replace fresh headline.
No author-vs-RTDL ratio is authorized from these mixed denominators.
```

## 7. RTDL System Improvements Extracted From X-HD

The X-HD app has driven real system work. The most important generic assets are:

```text
generic pairwise L2 candidate rows;
generic nearest witness;
generic max-nearest reducer;
coordinate matrix front-door convention;
grid-cell MBR descriptors;
nearest-state frontier API;
cell-MBR traversal ABI row table;
native OptiX 3-D AABB / cell-MBR broadphase and frontier rows;
active-query status-stream ABI contracts;
generic status-state-machine native smoke;
bounded generic multiround status-state reference.
```

Genericity discipline:

```text
X-HD owns wrappers, author comparators, public PLY loaders, route flags,
tolerances, and paper claim boundaries.

RTDL core/native must remain app-neutral.
No X-HD option names, figure names, paper semantics, or author-only constants
should enter RTDL core/native APIs.
```

The system extraction is real, but not all of it is externally reviewed yet.

## 8. Explicit `-lb` / Figure 7 Status

This is the main unresolved technical mountain.

Known author oracle from Goal5387:

```text
active queries       = 437,645
raw offload rows     = 27,133,990
rows per active      = 62
raw row hash         = 4333109858711462591
feedback updates     = 294
```

Failed or bounded RTDL evidence:

```text
Goal5398 native v7 status stream:
  active query parity = true
  RTDL rows           = 2,600,727
  row ratio           = 0.09584756978240207
  row/hash parity     = false

Goal5400 existing knobs:
  no tested knob matches author row denominator/hash;
  some modes under-count badly, others overflow by orders of magnitude.

Goal5404 bounded status-state oracle:
  bounded app-shaped row/hash/status/feedback matched = true
  still not full Goal5387 parity.

Goal5405 bounded full-cover-delta bridge:
  bounded 56+6 rows/active shape matched = true
  still not full Goal5387 parity.
```

Goal5405 current bridge result:

```text
active queries in bounded fixture = 2
base rows per active              = 56
delta rows per active             = 6
total rows per active             = 62
expected total rows               = 124
matched                           = true
raw hash/sample/status            = matched
overflow fail-closed              = matched
```

What is still missing:

```text
real full-cover surface generation / hash;
real author target stream generation / hash;
status_count_offloading parity on full public workload;
feedback_update_count parity on full public workload;
proof that the remaining 6 rows/active can be generated generically;
or a fail-closed decision that explicit -lb cannot be supported without
X-HD-specific semantics.
```

Current rule:

```text
explicit -lb remains unsupported and fail-closed.
Figure 7 is not reproduced.
```

## 9. Figure 11 / Memory Status

Figure 11 is not reproduced under the current RTDL route.

Reason:

```text
author WL / WL Heavy Peak denominators are not the same as current RTDL
frontier row capacity / generic worklist telemetry.
```

Current decision:

```text
same_denominator_author_figure11 = false
Figure 11 remains not_reproduced
```

Allowed future direction:

```text
generic heavy/offload worklist API and native peak-queue telemetry;
then app-owned mapping to author memory fields;
then external review of denominator equivalence.
```

Not allowed:

```text
author memory parity claim;
Figure 11 reproduction claim;
author-vs-RTDL memory ratio from mismatched denominators.
```

## 10. Major Problems Already Solved

### 10.1 Direction Contract

Directed vs symmetric Hausdorff is resolved:

```text
author = directed input1 -> input2
```

This was proven through a discriminating asymmetric fixture.

### 10.2 Bounded Same-Input Correctness

Bounded author JSON gates and RTDL gates are closed through Goal5126.

### 10.3 Generic Nearest Pipeline Extraction

Hausdorff was not promoted as a core primitive. It was decomposed into generic
nearest/witness/reduction helpers, and a non-Hausdorff consumer was added.

### 10.4 Level-B Public Scalar Correctness

The Dragon -> HappyBuddha full-public scalar route matches the author rerun.

### 10.5 Route Cost Reduction

The representative route moved from multi-second / tens-of-seconds class down
to:

```text
fresh route ~=0.849s
fresh total including load ~=1.531s
explicit-warm route ~=0.362s
```

### 10.6 `-lb` Evidence Discipline

The project now has:

```text
author trace v2 oracle;
status-stream ABI;
native v7 smoke;
bounded status-state oracle;
bounded full-cover-delta bridge.
```

Equally important: the project has not lied about this. Explicit `-lb` remains
fail-closed until full row/hash/status/feedback parity is proven.

## 11. Major Problems Still Unsolved

### 11.1 Exact Dataset Provenance

Exact paper input files/hashes remain unavailable. Public-source inputs are
representative Level-B evidence, not exact paper inputs.

### 11.2 Full Explicit `-lb`

The full author trace is:

```text
27,133,990 rows
4333109858711462591 raw hash
294 feedback updates
```

RTDL does not yet generate a matching full stream.

### 11.3 Figure 7 / Figure 11

Figure 7 depends on explicit `-lb`; Figure 11 depends on denominator-aligned
memory/worklist telemetry. Neither is closed.

### 11.4 Fair Performance Ratio

Author internal `Running.AvgTime`, author process wall, RTDL route time, RTDL
total time, cold process, warm process, and prepared replay are different
denominators. No author-vs-RTDL ratio is authorized until denominator, hardware,
dataset, and phase boundaries align.

### 11.5 Review Debt

The late X-HD sequence contains substantial implemented / review-pending work.
The report must preserve that state. It should not convert implementation into
external approval without actual review files.

## 12. Current Next Work

Immediate next goal:

```text
Goal5406: real full-cover surface or full Goal5387 stream gate.
```

Goal5406 should answer:

```text
Can RTDL generate the real full-cover surface?
  full-cover rows = 24,508,120
  rows per active = 56

Can RTDL generate the full author target stream?
  author rows     = 27,133,990
  rows per active = 62
  raw hash        = 4333109858711462591
  feedback updates = 294
```

Required comparisons:

```text
active count;
row count;
deterministic row hash or samples;
status_count_offloading;
feedback_update_count where applicable;
overflow fail-closed behavior.
```

Possible Goal5406 outcomes:

```text
1. full_goal5387_stream_parity_passed
   Strongest outcome. Explicit -lb could move toward support after review.

2. real_full_cover_surface_generated__delta_remaining
   RTDL can generate the 56 rows/active surface but still lacks the 6 rows/active
   delta and/or feedback parity.

3. full_stream_requires_app_specific_semantics__lb_fail_closed
   Explicit -lb must remain unsupported under the current generic RTDL model.

4. row_stream_generation_infeasible_due_capacity_or_runtime
   Need a smaller bounded step or streaming hash/sample export before full row
   materialization.
```

## 13. Planned Work After Goal5406

### If Goal5406 Generates Full-Cover But Not Author Target

Plan:

```text
Goal5407: isolate the remaining 6 rows/active delta on the real public workload.
Goal5408: compare feedback update / terminal transition semantics.
Goal5409: decide whether the delta is generic state-machine behavior or
          author/X-HD-specific behavior.
```

### If Goal5406 Generates Author Target Rows

Plan:

```text
Goal5407: run full row hash/sample/status/feedback parity gate.
Goal5408: freeze explicit -lb semantics and update app route.
Goal5409: produce a Figure 7 readiness matrix without performance ratio unless
          denominators align.
```

### If Goal5406 Fails Generically

Plan:

```text
Goal5407: explicit -lb fail-closed closeout under current RTDL model.
Goal5408: define optional future R&D path for generic multi-round active-query
          traversal state, separate from the X-HD app closeout.
Goal5409: keep X-HD current release line as Level-B scalar correctness +
          system extraction, not full paper reproduction.
```

### Figure 11 / Memory Follow-Up

Only after explicit `-lb` semantics are settled:

```text
Goal5410+: revisit generic worklist / memory telemetry and decide whether
          Figure 11 can be mapped to RTDL under same-denominator rules.
```

## 14. POD Usage Expectation

POD is required for any native OptiX build or full-public row/hash gate.

Use only:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<cmd>"
```

Do not use naked SSH.

Expected POD workload for Goal5406:

```text
1. preflight
2. sync / verify repo state if needed
3. build OptiX only if native code changed
4. run targeted full-cover or full-stream gate
5. export JSON artifact
6. run focused artifact regression tests locally and on POD where appropriate
```

Estimated execution shape:

```text
analysis / artifact inspection       local, no POD
full row stream or native probe       POD required
native code changes                   POD build required
bounded-only decision artifact        local unless it invokes native OptiX
```

## 15. Time / Goal Plan

This plan is expressed as goal count rather than wall-clock guarantees.

```text
Goal5406
  real full-cover or full Goal5387 stream gate.

Goal5407
  either row/hash parity follow-up, remaining-delta probe, or fail-closed
  closeout depending on Goal5406.

Goal5408
  Figure 7 readiness / explicit-lb support decision, or unsupported decision.

Goal5409
  update comprehensive report, review packet, memory, and release boundary.

Goal5410+
  optional Figure 11 / memory denominator work if explicit-lb path remains
  viable and generic.
```

Rough expectation:

```text
If full-stream parity is close: 3-5 more goals before an explicit-lb decision.
If the full-stream surface is not generically reachable: 1-2 more goals to
close explicit-lb as unsupported for this release line.
If exact paper datasets become available: a separate dataset / figure matrix
line is required and should not be mixed with Goal5406.
```

## 16. Claim Boundary

Allowed current summary:

```text
RTDL has a strong Level-B public Dragon -> HappyBuddha scalar route matching
the author rerun HDResult, plus substantial generic system extraction. The
fastest scalar route is exact for the directed-HD final value but not for all
per-source witnesses. Explicit -lb and full figure reproduction remain open.
Goal5405 proves a bounded 56+6 rows/active status bridge, but not the full
27,133,990-row author stream.
```

Forbidden summaries:

```text
full X-HD paper reproduction complete;
exact paper dataset reproduced;
author performance parity;
Figure 7 reproduced;
Figure 11 reproduced;
explicit -lb supported;
bounded 124-row bridge proves full 27,133,990-row parity;
warm route time is the default result;
early-break route has exact per-source witnesses;
RTDL core contains an X-HD primitive.
```

## 17. Current Bottom Line

The project is in a strong but unfinished state:

```text
bounded X-HD correctness: complete / reviewed
generic RTDL system extraction: real
Level-B public scalar correctness: strong
Level-B scalar route performance: much improved
explicit -lb / Figure 7: not closed
Figure 11 memory: not closed
exact paper dataset reproduction: not closed
full paper reproduction: not complete
```

The next technical mountain is no longer scalar HDResult. It is the real
full-public explicit `-lb` status stream:

```text
437,645 active queries
27,133,990 raw rows
row hash 4333109858711462591
294 feedback updates
```

Goal5406 should either start closing that mountain with real full-stream
evidence or make a clean, evidence-backed fail-closed decision.
