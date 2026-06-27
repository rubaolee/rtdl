# RTDL Architecture During V3 Rebuild

Status: rebuild authority only, not a released architecture promise.

This page summarizes the architecture V3 is being rebuilt around. It must not
be read as a current release claim. The active release decision lives in
[V3 Rebuild Control](rebuild/v3/README.md).

## Current Status

RTDL V3 is being rebuilt as a Python-hosted language/runtime whose public value
must be proved against v2.x on current pod evidence. Until that evidence gate
passes, there is no current V3 release, no public performance claim, and no
polished tutorial surface.

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
| Partner adapter | Explicit app-chosen partner continuations for unfused work; any CuPy or Numba recommendation must be backed by fresh same-contract evidence |
| Native backend | generic RT-shaped primitive execution through CPU/oracle, Embree, or OptiX where supported |
| Evidence layer | exact benchmark artifacts, review files, and claim boundaries |

## Backends

| Backend | Current learner meaning |
| --- | --- |
| `cpu_python_reference` | portable learning path |
| `cpu` | native oracle/correctness path |
| Embree | CPU RT backend and same-contract comparison surface |
| OptiX | NVIDIA GPU RT backend for documented primitive paths |
| Vulkan, HIPRT, Apple RT | historical or proof surfaces until the rebuild gate says otherwise |

Selecting a backend is not a public performance claim. Public wording must name
the workload, backend, partner, hardware, command shape, and artifact.

## Partner Architecture

The intended V3 partner design is protocol first and primitive first:

```text
Use a fused generic native RTDL primitive when it exactly expresses the work.
Use an explicit partner continuation only for unfused work or app choice.
Users choose supported partners explicitly; benchmark recommendations must be
backed by same-contract evidence.
Engine absolutely app-agnostic throughout.
```

CuPy and Numba are explicit continuation partners, not hidden defaults. Any
claim that one partner is recommended for a workload must name the exact row,
hardware, command, and artifact that proves it. RTDL owns only the supported
RTDL primitive call and its documented result contract.

Candidate V3 output contracts include:

- compact count columns;
- boolean flag columns;
- threshold summaries;
- bounded candidate-summary columns;
- grouped nearest/witness summaries;
- streaming exact witness columns.

The streaming witness-column contract is important because it avoids turning
large witness tables into Python dictionaries. The rebuild must decide which
exact contracts are M7-qualified row-scoped and which remain historical or
experimental.

## What Stays Outside RTDL

RTDL is not a renderer, DBMS, graph database, robotics planner, GIS engine, or
general CuPy/Numba optimizer. Users may call those systems from
Python, but user-written kernels remain application code unless RTDL ships and
reviews that exact generic contract.

General device-residency or zero-copy wording is blocked during the rebuild.
Selective reduced-transfer/device-resident evidence may be discussed only for
the exact benchmark rows that fresh artifacts support.

## Read Next

- [Quick Tutorial](quick_tutorial.md)
- [RTDL Language Docs](rtdl/README.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [Current Support Matrix](current_main_support_matrix.md)
- [Capability Boundaries](capability_boundaries.md)
