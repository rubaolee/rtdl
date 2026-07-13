# X-HD Comprehensive Midterm Status After Goal5411

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_unsupported__full_paper_not_complete
```

## Executive Summary

The X-HD line has achieved a real but bounded result:

- bounded same-input X-HD value reproduction is complete and externally reviewed through Goal5126;
- the Hausdorff app route has been decomposed into reusable RTDL system pieces through Goals5127-5128;
- the strongest current representative evidence is Level-B same-source scalar correctness on public Stanford graphics and public geo candidates;
- several generic RTDL route and native traversal features have been extracted and exercised on real X-HD pressure tests;
- full X-HD paper reproduction is still not complete because exact paper input provenance, figure-level denominator alignment, and author RT-core behavior parity are not closed;
- explicit X-HD `-lb` support remains unsupported after Goal5411 because the current generic statused-deferral bridge does not recover author raw row identity.

The next work is not more blind performance tuning. The next decision point is
Goal5412:

```text
fail-close explicit -lb under the current RTDL execution model
or
design a new generic native traversal trace semantic that can be justified
without X-HD-specific constants, paper-figure semantics, or hard-coded author
sample rows.
```

## Core Objective

The owner objective is:

```text
Complete a comprehensive X-HD paper reproduction as far as evidence allows,
while using X-HD to improve RTDL as a general spatial language/system.
```

This has two independent requirements:

1. **Paper reproduction evidence**: author contract, same-input correctness,
   dataset provenance, figure-level mapping, and denominator-aligned performance
   where possible.
2. **System improvement**: any reusable capability extracted from X-HD must
   become generic RTDL machinery, not an X-HD-only primitive hidden in core.

The project is currently successful on bounded value reproduction and system
extraction, strong on Level-B same-source scalar correctness, and incomplete on
exact paper input recovery, full figure reproduction, and explicit author
RT-core behavior parity.

## Claim Boundary

Allowed current claim:

```text
RTDL has strong Level-B same-source X-HD scalar correctness evidence on selected
public graphics/geo inputs, and X-HD has driven real generic RTDL APIs for
nearest/witness/reduction, grid/cell-MBR traversal, status streams, worklists,
and route profiling.
```

Forbidden current claims:

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
Figure 5/7/8/9/10/11 reproduction;
author RT-core algorithm parity;
explicit -lb support;
author-vs-RTDL performance parity or speedup;
same-denominator memory ratio;
exact per-source witnesses for early-aborted global-bound routes.
```

## Completed And Externally Reviewed

### Goal5110: X-HD Scaffold / Provenance

The paper app scaffold, author source provenance, entrypoint contract, and
claim boundary were created and externally reviewed.

Outcome:

```text
approved scaffold only;
no reproduction claim;
no performance claim;
old hausdorff_xhd benchmark not reclassified as paper reproduction.
```

### Goals5111-5126: Bounded Same-Input Value Reproduction

The bounded same-input line established:

- author `hd_exec` can be built/run for tiny bounded inputs;
- RTDL can match author scalar `HDResult`;
- Goal5126 resolved the directed-vs-symmetric ambiguity with an asymmetric
  fixture:

```text
directed input1 -> input2 = 0.5
directed input2 -> input1 = 9.0
symmetric = 9.0
author HDResult = 0.5
```

Meaning:

```text
The author route being compared is directed input1-to-input2 Hausdorff.
```

Bounded status:

```text
bounded same-input value reproduction complete;
not full paper reproduction;
not X-HD RT-core algorithm parity;
not performance evidence.
```

### Goals5127-5128: Generic Nearest/Witness/Reduction Extraction

X-HD pressure was turned into generic RTDL system helpers:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
```

Goal5128 added a non-Hausdorff consumer, facility-service-radius /
worst-served-demand, proving the helpers are not just X-HD-shaped wrappers.

Outcome:

```text
Hausdorff remains an app-level composition;
RTDL exposes generic nearest/witness/reduction primitives;
system extraction succeeded.
```

## Implemented / Review Pending: Level-B And System Route Line

The following work is implemented and documented, but should remain
`review pending` until an external review approves the corresponding packets.

### Goals5130-5136: Target Matrix And Initial Dataset Provenance

These goals mapped paper targets, dataset availability, and initial Level-B
same-source candidates.

Key decision:

```text
exact paper input identity requires file/hash provenance or externally accepted
deterministic regeneration. Matching counts, statistics, MBRs, or HDResult is
not enough.
```

### Goals5137-5174: Generic Cell-MBR Route And Scaled Representative Route

This sequence built a generic RTDL route instead of an X-HD-only route:

- grid-cell descriptors;
- nearest-state frontier API;
- cell-MBR traversal ABI;
- native OptiX 3-D cell-MBR frontier producer;
- nearest continuation;
- active-row-only frontier emission;
- Numba seed and continuation executors;
- row-table-only route forms;
- author-directed route mode.

Representative sample/res4 route evidence improved substantially, but all
performance remains route-local and not denominator-aligned with the author.

Important boundary:

```text
These goals improve RTDL route internals.
They do not reproduce a paper figure or authorize an author-vs-RTDL ratio.
```

### Goals5175-5212: Full-Public Dragon -> HappyBuddha Level-B Route

This is the strongest current graphics Level-B line.

Author and RTDL scalar correctness:

```text
author full-public rerun HDResult = 0.12572988867759705
RTDL route HDResult              = 0.12572988629271128
abs diff                         ~= 2.38e-9
```

The route also produced a long performance evolution on the same representative
workload. Key route-local numbers:

```text
Goal5188 initial full-public RTDL route ~= 7.30s
Goal5191 inline512 route               ~= 3.65s
Goal5195 intersection prune route       ~= 2.6s
Goal5196 dense local-grid route         ~= 2.26s
Goal5203 matrix input route             ~= 1.24s
Goal5205 fast PLY loader route          ~= 1.16-1.17s
Goal5211 global-bound route             ~= 0.849s fresh route
Goal5212 full total incl load           ~= 1.531s
Goal5207/5211 explicit-warm route       ~= 0.362s route / ~=0.288s case total
```

These are useful RTDL route-local measurements, but not paper-performance
ratios. The warm numbers are explicitly warm/runtime-regime measurements, not
fresh paper results.

Goal5211 caveat:

```text
global-bound early break preserves scalar max-nearest / directed-HD value,
but early-aborted per-source witnesses may be approximate.
```

Therefore the global-bound route is suitable for directed-HD scalar evidence
only under an explicit contract, not for generic exact nearest-witness APIs.

### Goals5272-5283: Figure 11 Memory / Worklist Investigation

The Figure 11 line clarified denominators.

Author semantics:

```text
WL = in_queue + miss_queue
WL Heavy Peak = heavy-cell offload peak queue
```

Current RTDL semantics:

```text
WL-like quantity = generic frontier row-table / offload queue capacity
```

Outcome:

```text
same_denominator_author_figure11 = false;
Figure 11 remains not reproduced;
generic heavy/offload worklist support exists in reference/native telemetry
form, but author memory parity is not authorized.
```

### Goals5284-5287: Figure 9 Auto-Tune Audit

The author paper branch contains Figure-9-like scripts and a checked-in PDF,
but the available logs do not contain the full expected four-variant matrix.

Outcome:

```text
Figure 9 closed under current evidence as denominator missing;
checked-in PDF is evidence, not a reproducible RTDL/author denominator.
```

### Goals5288-5319: Figure 5 Graphics / Geo Level-B Evidence

Figure 5 is not reproduced, but several Level-B lines are now concrete.

Strong graphics row:

```text
Dragon -> HappyBuddha:
  author rerun matches paper-log HDResult within 1e-6
  RTDL matches author rerun by about 2.38e-9
```

Other graphics findings:

```text
Dragon -> AsianDragon-scaled: no-go for paper-log value;
ThaiStatuette-scaled -> HappyBuddha: value-matched Level-B;
ThaiStatuette-scaled -> AsianDragon-scaled: value-matched Level-B.
```

Geo bounded rows:

```text
County -> ZCTA bounded fixture: RTDL matches author scalar within 1e-5;
WaterBodies -> BlockGroups bounded fixture: RTDL matches author scalar within 1e-5.
```

WaterBodies -> BlockGroups full-public corrected comparison:

```text
author paper-config n_points_cell=8 = 0.8964367508888245
RTDL exact-witness float64          = 0.8964380566690101
same witness float32                = 0.8964367508888245
declared tolerance                  = 2e-6
```

Important correction:

```text
Goal5311 default author rerun used n_points_cell=15 and mismatched paper-log.
Goal5313 showed the paper-log denominator uses n_points_cell=8.
Goal5314 superseded the default-author denominator for paper-log comparison.
```

Still blocked:

```text
exact paper WKT file/hash provenance;
full Figure 5 matrix;
denominator-aligned performance ratio.
```

### Goals5292-5296: Figure 7 / Figure 8 / Figure 10 Audit And POD Data Limits

Figure 7/8/10 author scripts exist, but current logs/data do not provide
complete reproducible matrices.

POD state:

```text
POD is usable;
/local/storage/shared/HDDatasets is missing;
exact author regeneration for Figures 7/8/10 is blocked on dataset root.
```

Goal5296 provides a partial author-side Level-B `lb=0` vs `lb=256` diagnostic,
not Figure 7 reproduction and not an RTDL comparison.

## Implemented / Review Pending: `-lb` / Status Trace Line

The current active hard problem is explicit X-HD `-lb` / heavy-cell offload
semantics.

### Goals5363-5367: Initial LB / Heavy-Offload Denominator Work

These goals aligned several shapes but did not prove row-count parity.

Key boundary:

```text
explicit -lb remains unsupported;
Figure 7 and Figure 11 remain unreproduced;
same-denominator memory/row parity is not established.
```

### Goals5379-5402: Generic Active-Query Status Machine Infrastructure

This line created generic active-query status concepts:

- status-kind rows;
- offload/deferred/active row schemas;
- status-machine reference;
- native status-stream smoke;
- transition phases;
- feedback/update telemetry.

But native synthetic smoke is not enough for X-HD `-lb`.

### Goal5387 Author Trace Oracle

The author explicit `-lb` trace provides the target denominator:

```text
active queries          = 437,645
author raw offload rows = 27,133,990
raw hash                = 4333109858711462591
feedback_update_count   = 294
```

This is the key oracle for any future `-lb` support claim.

### Goals5406-5408: Full-Cover And Cell Namespace Reconciliation

Goal5406:

```text
RTDL full-cover rows = 24,508,120 = 56 * 437,645
author raw rows      = 27,133,990 = 62 * 437,645
delta                = 2,625,870 = 6 * active_count
```

Goal5407 showed the gap is not merely "add 6 rows per active". Author sample
rows are absent from RTDL full-cover:

```text
(source=11168,  cell=2924) absent
(source=210712, cell=17)   absent
(source=437119, cell=17)   absent
```

Goal5408 showed simple compact/original cell-id remapping does not recover the
samples. The author cell IDs exist globally as RTDL compact IDs, but not for
the sampled source rows.

Conclusion:

```text
The remaining -lb gap is row identity / traversal state semantics, not a simple
count or namespace patch.
```

### Goal5409: Decision To Try One More Generic Semantic Probe

Goal5409 selected one more generic probe, not support:

```text
statused_large_cell_deferral_stream
```

Reason:

```text
author source inspection shows raw offload rows are appended by the OptiX
shader after prune/current-best status logic and before loadBalanceProcessing.
The author raw stream is a traversal payload-state stream, not a pure geometric
full-cover surface.
```

### Goal5410: Synthetic Statused Deferral Stream

Goal5410 passed a synthetic app-neutral gate:

```text
offload rows   = 2
completed rows = 2
miss rows      = 1
aborted rows   = 1
pruned rows    = 1
matched        = true
```

This proves the existing generic active-query status-machine reference can
express a statused large-cell deferral stream.

It does not prove X-HD sample-row recovery.

### Goal5411: Bounded X-HD Statused Deferral Sample-Row Gate

Goal5411 is the latest hard result and is a no-go for the current bridge.

POD bounded gate:

```text
active_query_count  = 3
candidate_row_count = 168
offload_row_count   = 3
pruned rows         = 165
matched             = true for script/test execution, but author samples absent
```

Author sample membership:

```text
source 11168,  author_cell 2924 -> present false, RTDL statused cells [1554]
source 210712, author_cell 17   -> present false, RTDL statused cells [1554]
source 437119, author_cell 17   -> present false, RTDL statused cells [1554]
```

Decision from Goal5411:

```text
bounded_xhd_author_sample_row_gate_passed = false
direct_native_fix_authorized              = false
explicit_lb_support_authorized            = false
full_goal5387_row_identity_gate_authorized = false
```

Interpretation:

```text
The current generic statused deferral bridge does not recover author raw row
identity. Do not proceed to full Goal5387 row/hash parity under this model.
```

## Major Problems Already Solved

1. **Directed vs symmetric Hausdorff ambiguity**: solved by Goal5126.
2. **Hausdorff as app vs RTDL system API**: solved structurally by Goals5127
   and 5128.
3. **Naive full pairwise materialization infeasibility**: solved by scalable
   grid/cell-MBR/frontier/nearest route.
4. **Major Python front-door overheads on graphics route**: substantially
   reduced by matrix loading and generic route improvements.
5. **Figure-level claim discipline**: improved through status matrices and
   explicit no-ratio/no-exact-input rules.
6. **WaterBodies/BG apparent mismatch**: traced to author config
   `n_points_cell`; corrected denominator uses `n_points_cell=8`.
7. **Figure 11 memory ambiguity**: turned into denominator-not-aligned status
   rather than vague missing accounting.
8. **`-lb` row-count gap simplistic explanations**: ruled out by full-cover,
   sample-membership, and namespace reconciliation gates.

## Major Problems Not Yet Solved

1. **Exact paper input provenance**:
   public same-source candidates exist, but exact author input files/hashes are
   missing.

2. **Full Figure 5 reproduction**:
   several graphics and geo rows are strong Level-B candidates, but the full
   figure matrix and exact input status are not closed.

3. **Figure 7 / Figure 11 `-lb` / heavy-offload semantics**:
   explicit `-lb` remains unsupported because author raw row identity is not
   recovered.

4. **Figure 8 / tune-radius behavior**:
   radius schedule helpers and trace metadata exist, but current RTDL route is
   not author tune-radius compatible.

5. **Figure 9 / auto-tune denominator**:
   available logs do not contain the complete expected variant matrix.

6. **Figure 10 scalability / overlap denominator**:
   author scripts exist, but checked-in logs do not provide a complete
   reproducible scale/overlap matrix.

7. **Performance parity**:
   no author-vs-RTDL performance ratio is authorized because denominators,
   hardware, phase boundaries, and runtime regimes are not aligned.

8. **External review debt**:
   many implemented goals after 5130 remain review pending. Do not upgrade
   their status without actual review.

## Critical Self-Assessment

The strongest criticism of the current project trajectory is valid:

```text
After dataset provenance was already identified as the blocker for Level-C
exact paper reproduction and figure-level claims, the project spent a very
large number of goals on route internals, full-cover surfaces, status streams,
and explicit -lb / raw offload-row reconstruction.
```

This was not wholly useless: it produced real generic RTDL assets and clarified
that author `-lb` is a traversal payload-state stream rather than a geometric
surface. But as paper reproduction strategy, the `-lb` line has diminishing
returns:

```text
HD scalar value reproduction does not require reproducing the author's
27,133,990-row raw offload implementation stream.
```

The `-lb` raw stream matters mainly for:

```text
Figure 7 load-balance semantics;
Figure 11 heavy-offload memory denominator;
author RT-core algorithm parity claims.
```

Those claims are still blocked by missing exact datasets / author denominators
and by row-identity mismatch. Therefore continued `-lb` work must meet a higher
bar than "it might explain the author implementation." It must either:

1. produce a clearly generic RTDL system abstraction with non-X-HD evidence; or
2. stop and leave explicit `-lb` fail-closed.

The project must not continue reverse-engineering an X-HD-specific artifact
merely because previous work invested in that path.

Practical decision:

```text
For the current execution model, Branch B is the recommended conclusion:
fail-close explicit -lb.

Any continuation is not Branch A as an equal default. It is a narrow,
design-only exception: a generic native payload-transition trace contract that
must first prove app-neutral semantics and a non-X-HD synthetic consumer before
any bounded X-HD sample-row gate.
```

Forbidden future summaries:

```text
"We are close to explicit -lb support."
"The remaining work is just row-count/hash cleanup."
"The author raw offload stream is necessary for HD scalar reproduction."
"The -lb reverse-engineering line is justified without a non-X-HD generic
consumer."
```

## Current Best Performance And Regime

Use these numbers only with their regime labels.

Strongest full-public graphics Level-B scalar route:

```text
Dragon -> HappyBuddha public full input
author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
abs diff        ~= 2.38e-9
```

Representative route-local performance evolution:

```text
initial full-public route             ~= 7.30s
post native inline / pruning / loaders ~= 1.16-1.17s
Goal5211 global-bound fresh route      ~= 0.849s
Goal5212 full total incl load          ~= 1.531s
explicit-warm measured route           ~= 0.362s
explicit-warm measured case total      ~= 0.288s
```

Caveats:

```text
0.362s / 0.288s are explicit warm-regime diagnostics;
Goal5211 early-break may produce approximate per-source witnesses;
no author-vs-RTDL ratio is authorized.
```

## POD Status And Expected Use

Current known POD:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
```

Required access pattern:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<cmd>"
```

Do not use naked SSH. Previous authentication failures were caused by using the
wrong local key rather than by a bad POD.

POD is needed for:

- native OptiX / CUDA route execution;
- author `hd_exec` reruns;
- future native trace semantics experiments;
- any Level-B or Level-C behavior gate that needs GPU/native code.

POD is not needed for:

- local decision documents;
- review packets;
- source/provenance audits;
- pure schema/contract tests.

Immediate POD expectation:

```text
Goal5412 can be a local decision over Goal5407-5411 artifacts.
POD becomes necessary only if Goal5412 authorizes a new generic native traversal
trace semantics implementation.
```

## Next Planned Work

### Goal5412: Fail-Close Explicit `-lb` Or Design New Generic Native Trace Semantics

Purpose:

```text
Decide whether to stop explicit -lb under the current RTDL execution model, or
authorize a new generic native traversal trace semantic as a design/spec gate.
```

Inputs:

- Goal5387 author trace oracle;
- Goal5406 full-cover surface;
- Goal5407 sample membership no-go;
- Goal5408 namespace no-go;
- Goal5409 semantic decision;
- Goal5410 synthetic statused-deferral pass;
- Goal5411 bounded X-HD sample-row no-go.

Possible exits:

```text
explicit_lb_fail_closed_current_model
new_generic_native_traversal_trace_semantics_authorized_design_only
```

If a new generic trace semantic is authorized, it must satisfy:

```text
app-neutral name and schema;
native rows emitted at traversal / payload transition points, not after
frontier lowering;
fields for active query id, source id, cell id, status kind, transition phase,
current-best before/after, bounds, and work counters;
synthetic non-X-HD behavior gate first;
bounded X-HD sample-row gate second;
full Goal5387 row-count/hash/sample/status/feedback gate only after bounded
gate passes.
```

Forbidden in Goal5412:

```text
hard-coding 6 rows per active;
hard-coding 62 rows per active;
hard-coding author sample source/cell pairs;
adding X-HD option names or figure semantics to RTDL core/native;
claiming explicit -lb support;
claiming Figure 7/11 reproduction;
claiming performance parity;
claiming full paper reproduction.
```

### Review Packet Work

Several implemented goals are review pending. The next review node should
group related evidence rather than send a hundred independent fragments:

1. Goals5130-5212:
   Level-B route construction, performance evolution, global-bound route, and
   current route-local caveats.
2. Goals5272-5287:
   Figure 11 and Figure 9 denominator closure.
3. Goals5288-5319:
   Figure 5 graphics/geo Level-B evidence and exact-input acquisition gaps.
4. Goals5351-5411:
   author RT option surface, radius/tune-radius, `-lb`/status-stream trace,
   and the current Goal5411 no-go.

### Exact Dataset / Figure Work

Continue only evidence-driven work:

- exact paper input acquisition or deterministic regeneration;
- author-source/log mapping for missing figure denominators;
- Level-B candidates only when clearly labeled and value-matched;
- no performance ratio until denominator alignment is accepted.

### System Work

If continuing system extraction after Goal5412:

- prefer generic native traversal trace semantics over X-HD-specific `-lb`;
- keep route APIs app-neutral;
- require non-X-HD synthetic behavior tests for new generic abstractions;
- preserve app ownership of X-HD wrappers, author comparators, tolerances, and
  figure labels.

## Suggested Timeline

This is a work ordering estimate, not a calendar promise.

1. **Short node**: Goal5412 local decision and report.
   - No POD expected.
   - Output: fail-close or design-only authorization for new generic native
     traversal trace semantics.

2. **If design authorized**: one design/spec goal for generic native traversal
   trace.
   - No POD unless prototype execution is included.
   - Output: schema, native ABI contract, synthetic gate plan.

3. **If implementation authorized**: synthetic native/POD gate.
   - POD required.
   - Output: non-X-HD synthetic trace rows and fail-closed overflow behavior.

4. **If synthetic passes**: bounded X-HD sample-row gate.
   - POD required.
   - Output: recover or fail sample rows `(11168,2924)`, `(210712,17)`,
     `(437119,17)` without hard-coding.

5. **Only if bounded sample-row gate passes**: full Goal5387 parity gate.
   - POD required.
   - Output: row count, row hash/sample, status counts, feedback counters.

6. **Parallel non-POD work**: consolidate review packets and exact-dataset
   acquisition status.

## Bottom Line

X-HD has already improved RTDL as a system: generic nearest/witness/reduction,
grid/cell-MBR traversal, native frontier production, status/worklist telemetry,
route profiling, and strict claim discipline are real assets.

But full X-HD paper reproduction is not finished. The immediate technical
boundary is explicit `-lb` / author raw traversal status semantics. Goal5411
shows the current bridge does not recover author row identity. The next correct
move is a decision gate, not another unreviewed full-parity run.
