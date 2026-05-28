# RTDL Current Architecture

This page describes the v2.x-facing architecture for learners and users. It
does not retell older release history. For that, use
[Version Archive Notes](history/version_archive_notes.md)
and the release-report archive.

## Current Status

RTDL v2.3 is the current source-tree Python+partner+RTDL release. It preserves
the current v2.x language boundary and adds the current benchmark-vs-learner app
portfolio cleanup.
The current released version is `v2.3`.

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
| Partner adapter | Triton-first v2.5 continuation, Numba fallback, and legacy NumPy/PyTorch/CuPy handoff compatibility |
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

The v2.x-facing partner design is protocol first. v2.3 remains the current
released source-tree partner release, but the active v2.5 implementation
direction is Triton-first:

```text
Triton primary. Numba fallback. CuPy/PyTorch are not benchmark-path partners.
Engine absolutely app-agnostic throughout.
```

Triton owns generic post-traversal continuations such as segmented reductions,
mask compaction, grouped argmin, bounded finalize, and the generic adapter
front doors that route those operations from benchmark apps.
Torch CUDA tensors may be used as a launch carrier for Triton kernels, but that
does not make PyTorch the v2.5 partner. RTDL owns only the supported RTDL
primitive call and its documented result contract.

Examples of valid v2.x-facing output contracts:

- compact count columns;
- boolean flag columns;
- threshold summaries;
- bounded candidate-summary columns;
- grouped nearest/witness summaries;
- streaming exact witness columns.

The streaming witness-column contract is important because it avoids turning
large witness tables into Python dictionaries. The old full Python row-table
contract remains available where documented, but it is not the fast v2.x shape.

## What Stays Outside RTDL

RTDL is not a renderer, DBMS, graph database, robotics planner, GIS engine, or
general PyTorch/CuPy/Triton optimizer. Users may call those systems from
Python, but user-written kernels remain application code unless RTDL ships and
reviews that exact generic contract.

## Read Next

- [Quick Tutorial](quick_tutorial.md)
- [RTDL Language Docs](rtdl/README.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [Capability Boundaries](capability_boundaries.md)
- [v2.3 Release Package](release_reports/v2_3/README.md)
