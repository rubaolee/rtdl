# v2.14.5 Entry Plan: Generalize From Two Paper Apps

Date: 2026-07-07

## Objective

v2.14.5 starts from the completed v2.14.4 state:

- RayJoin paper app established public planar-map / overlay-oriented primitives and device-columnar pipeline APIs.
- RT-BarnesHut paper app established generic 3-D aggregate-hierarchy / frontier-reduce APIs and closed a bounded same-input prepared-state reproduction.

The v2.14.5 objective is not to keep optimizing either app in place. The objective is to turn the two-app experience into a stable paper-reproduction application model and a clearer RTDL language surface.

## Product Principle

```text
RTDL is the generic language/runtime.
Paper reproduction apps are users of RTDL, not hidden extensions of RTDL core.
```

This means:

- app-specific comparators, author patches, output formatting, and prepared-state readers stay in paper-app directories;
- RTDL core may expose generic primitives, descriptors, contracts, and executors;
- a core API is promoted only when it has a non-app-specific name, a generic contract, tests, and at least one app-neutral proof or second consumer path.

## v2.14.4 Baseline

### RayJoin

RTDL gained:

- public planar-map LSI/PIP front doors,
- device-column row-buffer handoff,
- generic device ordering / descriptor-carrier pipeline work,
- writer-free binary operator framing.

Boundaries:

- RayJoin text-output reproduction remains app-owned;
- author comparator and contract patches remain explicitly disclosed;
- performance claims remain bounded by measured regime.

### RT-BarnesHut

RTDL gained:

- `AggregateHierarchy3D`,
- `PreparedAggregateHierarchy3D`,
- `SizeDistanceOpening`,
- `LeafOnlyOpening`,
- `ContinuationPayloadOpening`,
- reducer contract,
- CPU reference executor,
- optional Numba parity executor.

Boundaries:

- bounded same-input prepared-state reproduction closed;
- full paper reproduction not closed;
- independent tree construction not closed;
- broad envelope remains unfavorable to RTDL;
- phase-boundary performance not accepted.

## v2.14.5 Workstreams

### Goal5085: Paper-App Status Model And Registry

Create a single internal and user-facing status model for paper apps:

```text
paper_app_name
paper_scope
available_inputs
author_artifact_status
comparator_status
rtdl_public_api_used
bounded_reproduction_status
full_reproduction_status
performance_claim_status
claim_boundary
```

Deliverables:

- update `Paper-reproduction-apps/README.md` so RayJoin and RT-BarnesHut use the same status vocabulary;
- keep internal goal/review words out of public docs;
- add a small manifest schema or validation helper if the existing manifests diverge too much.

### Goal5086: Public RTDL API Surface Audit

Audit the public API surface created by RayJoin and RT-BarnesHut:

- planar-map LSI/PIP APIs,
- device-column / row-buffer APIs,
- ordering APIs,
- aggregate-hierarchy APIs,
- optional partner/Numba handoff APIs.

Deliverables:

- identify APIs ready for public documentation;
- identify legacy names or app-shaped internals that remain implementation debt;
- identify APIs that must stay experimental.

### Goal5087: Unified Paper-App Skeleton

Extract the shared app structure without moving app semantics into core:

```text
data manifest
author setup / patch disclosure
local contract gates
same-input comparator gates
performance-boundary gates
completion audit
claim-boundary README
```

Deliverables:

- a template or checklist under `Paper-reproduction-apps/`;
- at least RayJoin and RT-BarnesHut can be described by the same skeleton;
- no author/app-specific logic in the template.

### Goal5088: Third Validation Candidate Selection

Select the next validation target before implementing it.

Allowed choices:

1. third paper-reproduction app,
2. non-paper generic app that stresses the same APIs,
3. focused API stress test that proves cross-app reuse.

Selection criteria:

- exercises existing v2.14.4 APIs rather than demanding a new app-specific core feature;
- has accessible inputs or a bounded synthetic substitute;
- has a comparator or oracle;
- can be stopped with an honest bounded result if full reproduction is unavailable.

### Goal5089: AggregateHierarchy3D Documentation And Example

Promote the RT-BarnesHut-derived aggregate hierarchy API into a small user-facing example:

- synthetic hierarchy,
- opening policy,
- reducer,
- CPU reference run,
- optional Numba parity when available.

Non-goals:

- no native/backend claim,
- no paper-app comparator,
- no RT-BarnesHut names in the public example.

### Goal5090: v2.14.5 Entry Gate

Run a lightweight gate before deeper v2.14.5 implementation:

- paper-app public surface scan,
- aggregate-hierarchy tests,
- RayJoin public API smoke if local inputs are available,
- no internal review/process leakage in public docs,
- no new app-specific core symbols.

## Success Definition

v2.14.5 succeeds if a technically competent user can understand:

1. how paper-reproduction apps are structured,
2. which RTDL public APIs were extracted from RayJoin and RT-BarnesHut,
3. how to write a small aggregate-hierarchy RTDL program without touching RT-BarnesHut internals,
4. what remains experimental or app-owned,
5. what next validation target should exercise the language.

## Explicit Non-Goals

- Do not resume RayJoin performance tuning under v2.14.5 unless separately authorized.
- Do not resume RT-BarnesHut phase-boundary performance claims under v2.14.5 unless separately authorized.
- Do not claim full RT-BarnesHut paper reproduction.
- Do not build a native aggregate-hierarchy backend in this entry plan.
- Do not promote app-owned author/comparator/output logic into RTDL core.

## First Recommended Action

Start with Goal5085:

```text
paper-app status model and registry
```

This is the smallest step that converts v2.14.4's two successful paper-app lines into a reusable system pattern.
