# Goal2043 v2.0 Clean, Powerful, Traceable Plan

Date: 2026-05-14

Status: `plan-for-review`

## Purpose

This plan turns the remaining v2.0 weak spots into a concrete engineering track.

The target is not merely "more speedups." The target is a clean Python+partner+RTDL release where:

- the native engines stay app-agnostic;
- users can express rich app continuations outside the engine;
- Embree and OptiX expose the same conceptual contract;
- performance evidence is comparable across v1.8 and v2.0;
- every public claim is traceable to artifacts, tests, and independent review.

## Current State

Goal2041 repaired the slow Embree CPU-partner rows for the tested decision/summary contracts:

- facility coverage decision;
- ANN candidate coverage decision;
- Hausdorff threshold decision;
- polygon pair exact-area summary after CPU-partner bbox broadphase;
- polygon set Jaccard summary after CPU-partner bbox broadphase.

That is real progress, but it also clarified the unsolved richer requirements:

- exact K=3 facility fallback ranking at large scale;
- exact ANN ranking or recall/latency optimization;
- exact Hausdorff distance with witness extraction at large scale;
- broad general polygon overlay.

These gaps also exist for OptiX/RT. OptiX can accelerate traversal and candidate discovery, but it does not by itself solve top-K ranking, witness-carrying reductions, ANN index policy, or polygon topology assembly. Those must be solved as generic partner contracts, not as app-specific engine continuations.

## Core Design Rule

The native engine should emit generic geometric or relational rows. It should not know app names such as facility, ANN, Hausdorff, road, robot, or overlay.

The partner layer should own continuation policies:

- filtering;
- grouping;
- ranking;
- segmented reductions;
- witness preservation;
- topology assembly;
- optional user-defined kernels.

This keeps RTDL general-purpose while still allowing high-performance app programs.

## Required v2.0 Continuation Contracts

### 1. Candidate Row Contract

The engine emits rows with stable identity fields:

- query id;
- primitive id;
- optional witness id;
- optional distance or score;
- optional side-channel payload slot.

The row format must be backend-neutral. Embree rows live in host memory and are wrapped by NumPy or Torch-CPU. OptiX rows live in device memory and are wrapped by CuPy or Torch-CUDA. The public contract is the same even though the physical memory venue differs.

Deliverables:

- document the row schema;
- add small schema validation helpers;
- ensure all app examples record which row contract they consume.

### 2. Segmented Reduction Contract

Many apps need "reduce by query id" or "reduce by pair id":

- count;
- sum;
- min;
- max;
- argmin;
- argmax;
- any/all threshold;
- witness-carrying argmin/argmax.

This should become a reusable partner operator family, not duplicated per app.

Deliverables:

- `partner_segmented_count`;
- `partner_segmented_sum`;
- `partner_segmented_minmax`;
- `partner_segmented_argmin_argmax_with_witness`;
- NumPy and CuPy implementations first;
- Torch parity when practical.

### 3. Top-K Ranking Contract

Exact K=3 facility fallback and exact ranked KNN require a generic top-K primitive:

- group by query id;
- rank by distance or score;
- deterministic tie-break by primitive id;
- return values plus ids;
- optional fallback when fewer than K candidates exist.

This should be a generic partner contract named around `topk_by_group`, not `facility` or `knn`.

Deliverables:

- `partner_group_topk`;
- exact NumPy reference;
- CuPy implementation;
- deterministic tie-break tests;
- app examples migrate to this primitive.

### 4. Threshold Decision Contract

Goal2041 proved that fixed-radius threshold/count is powerful and app-agnostic.

The v2.0 API should make this explicit:

- threshold exists;
- threshold count;
- threshold any;
- threshold all;
- threshold with first witness.

Deliverables:

- promote current threshold paths from example-specific behavior into a documented partner primitive;
- preserve exact threshold semantics across Embree and OptiX;
- include app rows showing when the threshold contract is the correct problem formulation.

### 5. Witness Extraction Contract

Exact Hausdorff requires more than "distance exists." It needs:

- the query point that produced the maximum nearest-neighbor distance;
- the nearest candidate witness;
- the distance value;
- deterministic tie-breaking.

This is a generic `argmax_of_group_min` style contract.

Deliverables:

- `partner_group_min_then_global_argmax`;
- NumPy reference;
- CuPy implementation;
- exact correctness tests against SciPy or a trusted CPU reference when available;
- Hausdorff example with both threshold and exact witness modes clearly separated.

### 6. Polygon Topology Contract

Polygon overlap/Jaccard summaries are now much faster with bbox broadphase, but broad polygon overlay remains unsolved.

The generic contract should split the problem:

- candidate pair discovery;
- exact pair contribution summary;
- optional topology assembly.

The first two are v2.0 candidates. Full polygon overlay topology may be v2.x or v3.0 unless a clean generic partner implementation lands.

Deliverables:

- document `bbox_broadphase` as a partner policy, not an engine feature;
- keep exact area/Jaccard summaries as bounded v2.0 evidence;
- create a separate future plan for polygon overlay topology rather than hiding it inside v2.0 speed claims.

### 7. User-Defined Partner Kernel Contract

CuPy RawKernel is allowed as a partner capability when the user chooses CuPy. It is not engine customization.

For v2.0, the boundary should be:

- RTDL may provide raw candidate rows and helper wrappers;
- CuPy users may write RawKernel continuations over those rows;
- RTDL examples may include RawKernel variants when they are clearly labeled as partner code;
- public claims must say whether speed came from RTDL traversal, partner reductions, or user-defined partner kernels.

Triton and Numba should remain post-v2.0 or v2.x planning unless the user explicitly promotes them into v2.0 scope.

Deliverables:

- a short policy doc saying RawKernel is permitted as partner code;
- at least one example showing the pattern;
- claim-boundary wording that avoids presenting RawKernel app logic as an engine primitive.

## Execution Phases

### Phase A: Contract Documentation

Write the v2.0 partner contract spec:

- row schema;
- memory ownership;
- partner dispatch rules;
- exact claim vocabulary;
- allowed extension points;
- unsupported rich semantics.

Exit criteria:

- report exists;
- Gemini or Claude review exists;
- tests assert docs contain the supported and unsupported contracts.

### Phase B: NumPy Reference Layer

Build exact CPU reference partner operators first:

- segmented count/sum/min/max;
- group top-K;
- threshold decisions;
- witness-carrying min/argmax;
- bbox broadphase helper.

Exit criteria:

- all operators have deterministic tests;
- examples can run on local Linux without GPU;
- Embree all-thread matrix records which operator each app row uses.

### Phase C: CuPy Device Layer

Implement CuPy equivalents for the same contracts:

- prefer standard CuPy ops for simple reductions;
- use RawKernel only for kernels that standard CuPy cannot express cleanly;
- keep all RawKernel code in the partner/example layer, never inside native engines.

Exit criteria:

- pod evidence exists for OptiX+CuPy;
- each app row records RT time, partner time, transfer/wrap time, and total time;
- v1.8/v2.0 comparison uses same app contract.

### Phase D: Same-Contract App Matrix

Rebuild the app matrix around explicit contracts instead of vague app names.

Each row must state:

- app;
- backend: Embree or OptiX;
- contract: threshold, exact summary, top-K, witness, overlay, etc.;
- partner: NumPy, CuPy, Torch, RawKernel, or fallback;
- baseline: v1.8 Python+RTDL;
- v2.0 artifact path;
- correctness oracle;
- claim boundary.

Exit criteria:

- no `n/a` cells without explanation;
- no row says "covered by" another row unless the contract is identical;
- no row is counted as a speedup if it changed from exact rich semantics to threshold semantics without saying so.

### Phase E: Release Audit

Before v2.0 release:

- audit every post-v1.8 goal that affects partner contracts, performance, or public claims;
- ensure important goals have Codex plus one external AI review;
- ensure release/public architecture claims have Codex plus Claude plus Gemini;
- check docs, examples, tutorials, and front page describe v2.0 honestly.

Exit criteria:

- v2.0 release report exists;
- final Claude and Gemini reviews exist;
- consensus file accepts release wording;
- artifact manifest links every public claim to tests and evidence.

## Performance Evidence Rules

Every performance row must include:

- backend;
- partner;
- scale;
- hardware;
- commit hash;
- command;
- median time;
- correctness status;
- claim boundary.

For OptiX:

- pod evidence is required for release performance claims;
- local GTX 1070 evidence is smoke only;
- RT-core acceleration claims require exact subpath timing, not only whole-app improvement.

For Embree:

- local Linux all-thread evidence is acceptable for CPU-partner evidence;
- CPU speedups should not be described as RT-core speedups.

## What "Clean, Powerful, Consistent, Traceable" Means

Clean:

- app logic stays in Python/partner code;
- native engines expose generic primitives only;
- unsupported rich contracts are named instead of hidden.

Powerful:

- users can combine RTDL traversal with partner reductions;
- users can use CuPy RawKernel when they need custom GPU continuation;
- future Triton/Numba integration has a natural slot.

Consistent:

- Embree and OptiX use the same conceptual row contracts;
- NumPy and CuPy partner operators share semantics;
- examples name their exact contract.

Traceable:

- every public claim maps to a test, artifact, report, and review;
- every speedup says what work moved from Python to RTDL or partner code;
- every boundary says what remains unsolved.

## Recommended Next Goal

Goal2044 should implement Phase A and the first Phase B primitives:

1. write the partner continuation contract spec;
2. add NumPy reference operators for segmented reductions, group top-K, and witness-carrying reductions;
3. convert one unsolved rich app path, preferably exact Hausdorff with witness extraction, to use the generic operators;
4. run local Linux Embree tests;
5. seek external review.

This is the right next step because it addresses the real design gap. More ad hoc app repairs would improve individual rows, but would not make v2.0 clean, consistent, or explainable.

## Verdict

`plan-for-review`

This plan does not authorize v2.0 release. It defines the remaining work needed to make v2.0 a clean Python+partner+RTDL release rather than a collection of successful app-specific optimizations.
