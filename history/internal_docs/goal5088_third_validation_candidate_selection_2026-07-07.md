# Goal5088 Third Validation Candidate Selection

Date: 2026-07-07

## Verdict Label

```text
completed_third_validation_candidate_selection__rt_dbscan_first
```

## Purpose

Goal5088 selects the next paper-app validation candidate for v2.14.5.

The selection must serve the system goal:

```text
Use paper apps to improve and validate RTDL as a generic language/system,
not to accumulate app-specific one-off reproductions.
```

The first two paper apps already cover:

- RayJoin: planar-map LSI/PIP, device columns, ordering, binary operator routes.
- RT-BarnesHut: generic aggregate hierarchy, opening policies, reducers,
  reference and optional Numba execution.

The third candidate should exercise a different RTDL surface.

## Candidate Chosen

```text
RT-DBSCAN-style paper app
```

Selected as the first v2.14.5 third-app candidate.

## Why RT-DBSCAN

Local evidence shows the repository already has a substantial RT-DBSCAN-style
system line:

```text
examples/current/research_benchmarks/rt_dbscan/
examples/current/apps/ml/rtdl_dbscan_clustering_app.py
history/internal_docs/docs_research/future_version_to_do_list.md
```

The current benchmark app describes the paper target as:

```text
RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware
```

It also exercises a system surface not covered by the two existing paper apps:

- fixed-radius neighbor / count-threshold traversal,
- DBSCAN core flags and core counts,
- partner continuation for component signatures,
- route choice between RT traversal and partner-side grid/component work,
- dense candidate management and grouped-union/component continuation pressure.

This is a better third validation target than another planar-map app or another
hierarchical force app, because it tests whether RTDL can express and govern a
density-neighborhood workload family.

## Why Not Treat It As Already Reproduced

The existing RT-DBSCAN assets are benchmark-app and research assets, not yet a
paper-app package under the new template.

Current assets include strong implementation and historical evidence, but the
paper-app line still needs:

- pinned paper and artifact metadata,
- explicit comparator/source-of-truth policy,
- explicit input provenance,
- a bounded reproduction target,
- a performance regime statement,
- a forbidden-claims list.

Therefore the selection does not authorize:

- full RT-DBSCAN paper reproduction,
- arbitrary DBSCAN acceleration claims,
- DBSCAN-native RTDL core ABI,
- automatic partner or route selection,
- promotion of app-specific clustering semantics into RTDL core.

## Recommended Initial Scope

The first bounded RT-DBSCAN paper-app target should be:

```text
prepared fixed-radius core-flag / core-count subpath, plus a bounded
component-signature continuation if comparator evidence is available.
```

Reason:

- existing code already supports core flags/core counts,
- historical evidence repeatedly warns that full DBSCAN clustering and cluster
  expansion are separate app-level continuations,
- a bounded subpath can test RTDL's generic fixed-radius/count-threshold surface
  without pretending to close the entire paper.

## System Surface To Audit

Before implementing a new paper app, the next requirements goal must audit:

- `fixed_radius_neighbors`,
- prepared fixed-radius count-threshold / core-flag paths,
- device-column outputs for threshold flags,
- partner component continuation assets,
- CuPy and Numba partner usage,
- any archived grouped-stream or direct-status route evidence,
- whether a generic fixed-radius component continuation contract exists or is
  still only a research note.

## Alternatives Considered

### RTNN / nearest-neighbor paper-style app

Useful later, but it overlaps with fixed-radius/ranked-neighbor assets and
does not appear to have as much immediately visible paper-app scaffolding.

### RayDB-style grouped aggregate

Useful later for database-style grouped count/sum. It would test grouped
aggregation, but the current two-app arc has just introduced aggregate hierarchy
and device-ordering surfaces; RT-DBSCAN gives a cleaner third family.

### Hausdorff / X-HD style

Useful later for distance decision and nearest/fixed-radius style queries, but
it is closer to pairwise distance benchmarking than to a distinct paper-app
reproduction line at the current evidence level.

## Next Recommended Goal

Goal5089 should be renamed from the earlier generic-doc idea into:

```text
Goal5089 RT-DBSCAN paper-app requirements and scaffold
```

It should:

1. create `Paper-reproduction-apps/rt-dbscan-paper/`,
2. fill `README.md` and `data/manifest.json` using the Goal5087 template,
3. list current RTDL APIs exercised,
4. list app-owned DBSCAN semantics,
5. decide the bounded first reproduction target,
6. identify what evidence already exists and what must be run on POD,
7. explicitly forbid full-paper and whole-app speedup claims.

## Claim Boundary

This goal is candidate selection only.

It does not:

- create a new paper app yet,
- run RT-DBSCAN,
- claim reproduction,
- claim performance,
- promote DBSCAN-specific logic into RTDL core.
