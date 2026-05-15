# RTDL Current Architecture

This page describes the v2.0-facing architecture for learners and users. It
does not retell older release history. For that, use
[Legacy Learner Doc Version Notes](history/legacy_learner_doc_version_notes.md)
and the release-report archive.

## Current Status

RTDL v2.0 is a pre-release candidate. The engineering packet has reviewed
OptiX/RT evidence under documented contracts, but final release is still held
by the 3-AI consensus redline until a fresh Claude-family review lands.

## The User Contract

RTDL is a Python-hosted language/runtime for RT-shaped query kernels.

```text
input -> traverse -> refine -> emit
```

Python owns application code: loading data, naming domain objects, choosing
policies, reducing results, reporting answers, and calling partner libraries.

RTDL owns the kernel contract: typed inputs, traversal intent, refinement
predicates, emitted rows or device columns, backend dispatch, and correctness
checks for supported primitive paths.

Native engines must remain app-agnostic. App names belong in Python examples
and compatibility wrappers, not in exported native engine APIs.

## Main Layers

| Layer | Responsibility |
| --- | --- |
| Python application | domain data, command-line flags, labels, policies, app reductions, plots, files |
| RTDL language | kernel declaration, input roles, traversal/refinement, emitted schema |
| Partner adapter | NumPy, PyTorch, or CuPy column ownership and handoff |
| Native backend | generic RT-shaped primitive execution through CPU/oracle, Embree, or OptiX where supported |
| Evidence layer | exact benchmark artifacts, review files, and claim boundaries |

## Backends

| Backend | Current learner meaning |
| --- | --- |
| `cpu_python_reference` | portable learning path |
| `cpu` | native oracle/correctness path |
| Embree | CPU RT backend and same-contract comparison surface |
| OptiX | NVIDIA GPU RT backend for documented primitive paths |
| Vulkan, HIPRT, Apple RT | preserved proof/validation surfaces unless a current support page says otherwise |

Selecting a backend is not a public performance claim. Public wording must name
the workload, backend, partner, hardware, command shape, and artifact.

## Partner Architecture

The v2.0-facing partner design is protocol first:

```text
PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

Partners own tensor memory and normal framework continuations. RTDL owns only
the supported RTDL primitive call and its documented result contract.

Examples of valid v2.0-facing output contracts:

- compact count columns;
- boolean flag columns;
- threshold summaries;
- bounded candidate-summary columns;
- streaming exact witness columns.

The streaming witness-column contract is important because it avoids turning
large witness tables into Python dictionaries. The old full Python row-table
contract remains available where documented, but it is not the fast v2.0 shape.

## What Stays Outside RTDL

RTDL is not a renderer, DBMS, graph database, robotics planner, GIS engine, or
general PyTorch/CuPy optimizer. Users may call those systems from Python, and
they may write CuPy RawKernel, PyTorch, C, or C++ continuations, but that work
is user application code unless RTDL ships and reviews that exact contract.

## Read Next

- [Quick Tutorial](quick_tutorial.md)
- [RTDL Language Docs](rtdl/README.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [Capability Boundaries](capability_boundaries.md)
- [v2.0 Pre-Release Candidate](release_reports/v2_0_pre_release_candidate.md)
