# RTDL App Group Deep Dives

This document expands the app primitive classification into implementation
guidance by group. It is for maintainers and reviewers, not a public benchmark
or tutorial page. It does not authorize public speedup, whole-app acceleration,
broad RTX, stable `COLLECT_K_BOUNDED`, or true zero-copy claims.

## Group 1: Reduction-First Apps

Reduction-first apps are the best fit for the current Python+RTDL architecture
because the user-visible result can be a compact scalar or compact per-query
summary.

Representative apps:

- Service coverage gaps
- Event hotspot screening
- Road hazard screening
- Segment/polygon hitcount
- Outlier detection
- DBSCAN core-count modes
- Robot collision hit-count and pose-flag modes

### Implementation Shape

Python prepares domain fixtures and parameters, then lowers the query into an
RTDL traversal. The backend performs traversal and emits a compact result such
as a count, any-hit flag, threshold decision, or per-segment/per-query count.
Python formats that result and applies app-level presentation logic.

The core migration target is:

- v1.0: named app-specific native continuation.
- Current direction: app-name-free `ANY_HIT`, `COUNT_HITS`, `REDUCE_INT`, or
  `REDUCE_FLOAT` primitive path.

### Copy Behavior

These apps reduce copy pressure by avoiding large intermediate rows. Python
still sends input geometry/query data to the backend, but the backend can return
compact summaries instead of returning every candidate or witness row.

Safe wording:

- reduced materialization
- compact summary
- native reduction
- explicit host/device transfer boundary

Unsafe wording without new evidence:

- true zero-copy
- whole-app acceleration
- SQL/GIS/robotics engine acceleration
- broad RTX speedup

### Testing Focus

For reduction-first apps, tests should prove:

- Reduction result parity against oracle or row-materialized reference.
- Backend summary output matches row-output semantics for the selected mode.
- No app-name-specific requirement leaks into the stable primitive contract.
- Claim flags and docs avoid whole-app and zero-copy wording.

## Group 2: Split-Contract Apps

Split-contract apps expose both compact decision modes and richer row/ranking
modes. The compact mode may be ready for generic primitive promotion before the
row mode.

Representative apps:

- Facility KNN assignment
- Hausdorff distance
- ANN candidate search
- Barnes-Hut force app

### Implementation Shape

The same app can have two valid but different contracts. For example, facility
assignment can ask for nearest-depot rows or only ask whether the service-radius
coverage threshold is satisfied. Those are not interchangeable workloads.

The core migration target is:

- Compact decision mode: map to `ANY_HIT`, `COUNT_HITS`, or threshold reduction.
- Rich output mode: keep rows, witnesses, ranking, or policy in Python unless a
  stable bounded collection contract exists.

### Copy Behavior

Compact decision modes reduce output movement. Rich modes still need rows or
witnesses, so they should not be described as reduced to a scalar unless the
user explicitly selected a compact output mode.

### Testing Focus

For split-contract apps, tests should prove:

- Compact and rich modes have separate schemas.
- The compact mode does not silently claim ranked rows, witness IDs, force
  vectors, or full clustering/planning output.
- Performance reports name the exact mode measured.

## Group 3: Candidate-Refinement Apps

Candidate-refinement apps use RTDL for a traversal/candidate phase, then apply
additional refinement or application-specific calculations.

Representative apps:

- Polygon-pair overlap area rows
- Polygon-set Jaccard

### Implementation Shape

RTDL helps find candidate interactions. A native or Python continuation then
computes exact area, set area, Jaccard, or summary values. This is a powerful
pattern, but it is not the same as claiming a complete polygon overlay engine.

The core migration target is:

- Candidate discovery: app-generic traversal where possible.
- Compact summaries: generic `REDUCE_INT(COUNT)` and `REDUCE_FLOAT(SUM)` where
  exact refinement data is already available.
- Row-producing similarity/overlap output: depends on stable bounded collection
  when candidate rows must be returned.

### Copy Behavior

Candidate-refinement apps can reduce output volume when users ask for aggregate
area/count summaries. If users need per-pair rows, output size remains part of
the workload and must be bounded explicitly.

### Testing Focus

For candidate-refinement apps, tests should prove:

- Candidate discovery does not drop true positives.
- Exact refinement remains parity-clean.
- Summary modes are not confused with row modes.
- Docs avoid broad overlay, GIS topology, or set-similarity acceleration claims.

## Group 4: Bounded-Collection Blocked Apps

Bounded-collection blocked apps need row or candidate output, not just counts.
They are where `COLLECT_K_BOUNDED` matters.

Representative apps:

- Segment/polygon any-hit pair rows
- Polygon-set Jaccard rows

### Implementation Shape

The backend receives a maximum output capacity and must either return bounded
rows within that capacity or fail closed with explicit overflow metadata. It
must not silently truncate results and call the output correct.

The core migration target is:

- Experimental: `COLLECT_K_BOUNDED` with strict overflow metadata.
- Candidate: Embree/OptiX parity, exact bounds tests, bounded result buffers,
  and accepted performance/profile evidence.
- Stable: only after external review and release decision.

### Copy Behavior

Bounded collection does not remove row output. It makes row output explicit,
bounded, and safer. If the user needs witnesses, the data must still be
returned or handed to a downstream consumer. In Python+RTDL that usually means a
host-visible result; in Python+partner+RTDL it may eventually mean partner-owned
device memory, but that is not the current claim.

### Testing Focus

For bounded-collection apps, tests should prove:

- Exact behavior at capacity 0, capacity 1, exact-fit capacity, and overflow.
- No silent truncation.
- Stable row schema.
- Embree/OptiX parity where claimed.
- Pod evidence uses the expected native path, not fallback smoke.

## Cross-Group Design Rules

- Keep app policy in Python unless it is intentionally part of the native
  primitive contract.
- Keep compact summaries and row-producing modes separate in names, schemas, and
  docs.
- Treat local GTX 1070 OptiX runs as smoke only for collect-k tiled evidence.
- Treat pod results as evidence only when preflight, parity, topology, and
  profile gates pass.
- Do not use `zero-copy` wording for Python+RTDL reduced-materialization work.
- Do not use whole-app speedup wording unless a separately reviewed whole-app
  benchmark authorizes it.

