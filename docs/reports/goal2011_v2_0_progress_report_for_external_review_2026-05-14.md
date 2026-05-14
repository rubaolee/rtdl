# Goal2011 v2.0 Progress Report For External Review

Date: 2026-05-14

Status: external-review-requested

## Purpose

This report summarizes the current RTDL v2.0 progress after the recent
partner-layer and pod-validation work. It is written for external review, not
as a release announcement.

The v2.0 goal is:

```text
Python + RTDL + partner tensors
```

where RTDL native engines remain app-agnostic and emit generic primitive
results, while PyTorch or CuPy performs app-level continuation over
partner-owned device columns. v2.0 is not trying to put app logic back inside
the RTDL native engine. It is trying to make the Python+partner layer powerful
enough that users can keep their app semantics outside native code without
falling back to slow host Python for the performance-critical continuation.

## Current High-Level State

v1.8 established the app-agnostic native engine boundary. v2.0 is now building
the partner-runtime layer on top of that boundary.

Current evidence supports this narrower statement:

```text
For selected app contracts, RTDL v2.0 can keep native OptiX generic, hand
candidate or compact primitive outputs to CuPy/Torch device columns, and perform
the app continuation on the partner GPU with exact parity and measured speedups.
```

Current evidence does not yet support:

- final v2.0 release authorization;
- broad RT-core speedup wording;
- arbitrary Python acceleration wording;
- arbitrary PyTorch/CuPy acceleration wording;
- package-install readiness;
- claiming every public app has a broad, fair, full-app v2 speedup.

## Architectural Boundary Being Protected

The important design rule is:

```text
RTDL native engine = generic primitive producer
Python + partner layer = app semantics, exact filters, reductions, summaries
```

This boundary matters because v1.0/v1.6 had app-shaped native engine paths.
v1.8 removed those app customizations. v2.0 must not reintroduce them under a
different name. Recent work therefore treats native OptiX rows such as
`generic_ray_primitive_candidate_witness_pairs` as candidate evidence only. Any
segment/polygon, road/hazard, graph, database, or geometry-specific meaning must
be added outside the native engine.

## Recent Goal Chain And Effects

### Goal1975-1985: Exact Partner-Reference Rows

Purpose:

Earlier v2.0 performance tables had several very fast but semantically weak
threshold-proxy rows. These were useful for proving partner plumbing, but not
enough for a learner or reviewer who expects the named app semantics.

Effect:

- Goal1975 added exact directed Hausdorff partner reductions.
- Goal1978 added exact ranked K-nearest facility assignment.
- Goal1979 added exact all-pairs force-vector partner output.
- Goal1983 added exact ANN candidate/full-search quality comparison.
- Goal1985 added a bounded exact DBSCAN component-label reference using a
  generic spatial-bucket candidate graph.

Review interpretation:

These goals improve semantic honesty. They do not by themselves authorize broad
RT-core speedup claims, because many are partner-reference contracts rather than
native RT acceleration claims.

### Goal1987-1997: Generic Partner Building Blocks

Purpose:

The v2.0 layer needed reusable primitives rather than one-off app-local
RawKernels for every demo.

Effect:

- Generic columnar predicate/reduction paths were added for database-style
  workloads.
- Generic metric-table payload/reduction paths were added for graph-like
  summary rows.
- Generic AABB pair payload and overlap-summary adapters were added for the
  polygon control rows.
- Generic partner column paging and ray/primitive witness-pair paging were
  added for bounded result materialization.

Review interpretation:

This moves v2.0 away from case-only demos and toward a real partner-runtime
surface. The rows remain bounded where the app semantics are narrow, but the
implementation direction is more reusable.

### Goal2000: Candidate Witness Contract Correction

Purpose:

The fresh A5000 pod run exposed two issues in the segment/polygon OptiX partner
path:

1. The native all-witness device-column ABI expected `float32` ray columns, but
   some runners passed `float64`.
2. The native all-witness output was being treated too strongly as exact
   segment/polygon rows, when it is actually a generic ray/primitive candidate
   witness contract.

Effect:

- The runtime now fails closed on incorrect all-witness ray-column dtypes.
- The metadata now records:
  `native_engine_row_contract: generic_ray_primitive_candidate_witness_pairs`.
- Exact segment/polygon row semantics are explicitly app-layer semantics.
- The initial exact filter was moved to host Python as a correctness repair,
  which fixed parity but exposed performance debt.

Evidence:

- Pod: NVIDIA RTX A5000, driver `570.211.01`.
- Strict row parity passed at counts 256, 2048, and 8192.
- Performance was negative at smaller counts because host exact filtering and
  witness management dominated.

Review interpretation:

Goal2000 was mainly a correctness and claim-boundary goal. It made v2.0 more
honest and identified the real next requirement: app exact filters must move
into the partner GPU layer, not into native OptiX and not back to host Python.

### Goal2003: CuPy RawKernel Exact Witness Filter

Purpose:

Move the exact segment/triangle filter from host Python to the CuPy partner
layer for the hit-count column path.

Effect:

- Native OptiX still emits only generic candidate witnesses.
- CuPy performs exact segment/triangle filtering on device.
- The existing generic unique-pair count reduction produces per-segment hit
  counts on the partner GPU.
- CuPy hit-count metadata can honestly record:
  `whole_app_true_zero_copy_authorized: true` for the exact count-column path.

Pod evidence:

| Count | v1.8 median s | v2.0 CuPy median s | Ratio |
| ---: | ---: | ---: | ---: |
| 256 | 0.001542602 | 0.003490211 | 2.263x slower |
| 2048 | 0.024160467 | 0.003498526 | 0.145x |
| 8192 | 0.333005326 | 0.004293237 | 0.0129x |

Effect on evidence:

Goal2003 turned a correctness-only fix into a real positive performance row at
medium and larger sizes. It also confirmed the design principle: native produces
generic candidates; partner adapters provide reusable exact filters and
reductions.

### Goal2006: Prepared CuPy Exact Filter Reuse

Purpose:

The unprepared CuPy path was exact and fast, but the prepared road-hazard reuse
path lost access to triangle geometry and therefore could not exact-filter
generic candidates on the partner GPU.

Effect:

- The prepared Python wrapper now retains caller-owned triangle columns while
  delegating native calls to the generic prepared OptiX scene.
- Prepared CuPy hit-count and road-hazard paths can exact-filter candidates on
  device before counting.
- Road-hazard perf runners build ray columns as `float32` for the OptiX
  all-witness ABI.

Pod evidence at count 2048:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.327098407 | 4699.62x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.003474137 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.003750768 | 1.080x |
| Goal2006 prepared CuPy exact-filter priority columns | 0.003149398 | 0.907x |

Note: the Goal2006 table above uses the refreshed pod artifact rerun that also
embedded exact-filter metadata into the JSON. The earlier Goal2007 Claude review
looked at the first Goal2006 pod artifact, where the prepared CuPy row was
`0.002599899 s` and `0.922x` versus that run's v1.8 prepared baseline. Both
runs support the same bounded conclusion: prepared CuPy exact filtering is
correct and modestly faster than the corresponding v1.8 prepared baseline, but
the exact median should be cited with its artifact path.

External review:

- Claude Goal2007: `accept-with-boundary`.
- Gemini Goal2008: `accept`.

Effect on evidence:

Goal2006 made the prepared road-hazard row correct and modestly faster than the
v1.8 prepared baseline while preserving the native app-agnostic boundary.

### Goal2009: Prepared CuPy Triangle Lookup Cache

Purpose:

Claude's Goal2007 review identified a non-blocking performance debt: the
prepared CuPy exact filter still rebuilt the triangle-ID lookup every query,
even though prepared triangle geometry is fixed.

Effect:

- `_PartnerPreparedTriangleScene` now owns a small CuPy triangle lookup cache.
- The cache lives only in the Python partner wrapper.
- Native OptiX remains unchanged and app-agnostic.
- Exact-filter semantics are unchanged; only repeated triangle-side sorting is
  skipped after the first prepared-scene query.

Pod evidence at count 2048:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 16.492227267 | 4741.70x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.003478130 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.003188476 | 0.917x |
| Goal2009 prepared CuPy cached exact-filter priority columns | 0.002519239 | 0.724x |

Pod evidence at count 4096:

| Row | Median seconds | Ratio vs v1.8 prepared |
| --- | ---: | ---: |
| v1.8 one-shot native OptiX road-hazard rows | 104.259560453 | 10757.88x slower |
| v1.8 prepared native OptiX road-hazard rows | 0.009691451 | 1.000x |
| v2.0 unprepared CuPy priority columns | 0.005996620 | 0.619x |
| Goal2009 prepared CuPy cached exact-filter priority columns | 0.003932310 | 0.406x |

External review:

- Claude Goal2010: `accept`.

Effect on evidence:

Goal2009 is the clearest recent proof that v2.0 can turn a previously weak
prepared row into a stronger partner-layer performance result without changing
native engine semantics. At count 4096, the prepared cached CuPy path is about
`2.46x` faster than the v1.8 prepared native row and about `1.52x` faster than
the unprepared v2.0 CuPy path, with strict priority-flag parity.

## Current Performance Picture

The all-app picture after Goal1946 and the Goal2000-2009 segment/polygon
corrections is:

- Fixed-radius and compact-output rows remain the strongest v2.0 evidence.
- Exact partner-reference rows make the table more semantically honest.
- Segment/polygon and road-hazard rows are no longer just "positive but
  awkward"; the CuPy path now demonstrates the intended v2.0 pattern:
  generic native candidate witnesses plus partner-side exact filtering and
  reduction.
- Robot collision remains a strong true device-handoff story.
- Database, graph, polygon area, and polygon Jaccard rows are useful but still
  bounded. They should not be marketed as arbitrary SQL, graph, or GIS overlay
  acceleration.

## Design Lessons

1. Candidate output is the right native contract.

Native OptiX should not know about road hazards, polygon hitcounts, or app row
semantics. It should produce generic candidate witness columns.

2. Exact app semantics need partner-side continuation primitives.

Goal2000 showed that host exact filtering fixes correctness but weakens
performance. Goal2003 and Goal2006 showed that CuPy RawKernel continuation can
restore both exactness and speed.

3. Prepared state needs app-layer companion state, not native app customization.

Goal2006 kept triangle columns beside the prepared native scene in a Python
wrapper. That is an important pattern: the native scene stays generic, while
the Python/partner layer retains whatever app data is needed for exact
continuation.

4. Reuse matters.

Goal2009 shows that v2.0 performance depends on caching partner-side lookup
state where the app contract is repeated-query/prepared-scene oriented.

5. CuPy RawKernel is currently part of the practical v2.0 partner story.

CuPy's normal ability to run custom kernels is useful when Torch tensor algebra
is not expressive enough for exact app continuation. This does not mean RTDL
native becomes app-specific; it means app continuation belongs in the partner
layer.

## Current Claim Boundary

Allowed, if external review agrees:

- v2.0 has a credible Python+RTDL+CuPy pattern for exact candidate filtering and
  reduction without app-specific native engine code.
- The road-hazard prepared CuPy row has pod evidence showing exact parity and
  speedup versus v1.8 prepared native rows at counts 2048 and 4096.
- The segment/polygon hit-count CuPy path has pod evidence showing strong
  larger-scale gains once exact filtering is moved to the partner GPU.
- The native engine remains app-agnostic in these rows.

Not allowed yet:

- final v2.0 release readiness;
- broad RT-core speedup claims;
- claiming all apps are faster in a fair full-app sense;
- package-install claims;
- arbitrary PyTorch/CuPy acceleration claims;
- treating bounded partner-reference rows as universal algorithms.

## Open Risks And Debt

- Some older all-app rows still need a refreshed all-app table that incorporates
  Goal2006/Goal2009 rather than only Goal1946-era numbers.
- Torch does not yet have an equivalent device-side exact segment/triangle
  filter; the current exact GPU continuation path is CuPy-first.
- The pod artifacts use source labels because the pod workspace was copied
  without `.git`, so `git_commit` appears as `unknown`.
- JIT warmup should be reported separately from warmed medians for RawKernel
  rows.
- Database, graph, polygon area, and polygon Jaccard still need more careful
  wording and possibly more general partner primitives before they can support
  broad learner-facing claims.

## Requested External Review Questions

1. Does this report accurately preserve the v1.8 app-agnostic native-engine
   boundary while explaining the v2.0 partner continuation work?
2. Are Goals2000, 2003, 2006, and 2009 described with the correct purpose and
   effect?
3. Are the road-hazard and segment/polygon performance claims narrow enough for
   the artifacts?
4. Does the report overclaim v2.0 readiness anywhere?
5. What should be the next blocking work before a final v2.0 release candidate:
   a refreshed all-app matrix, more pod runs, Torch parity, packaging, or
   broader partner primitives?
