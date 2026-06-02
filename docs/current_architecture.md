# RTDL Current Architecture

This page describes the v2.x-facing architecture for learners and users. It
does not retell older release history. For that, use
[Version Archive Notes](history/version_archive_notes.md)
and the release-report archive.

## Current Status

RTDL v2.3 is the current source-tree Python+partner+RTDL release. The active
internal v2.6 pre-release lane preserves the same v2.x language boundary and
adds clearer user-chosen partner guidance for CuPy and Numba continuations.
The current released version remains `v2.3`; v2.6 is not a release tag yet.

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
| Partner adapter | Explicit app-chosen partner continuations for unfused work; Numba fallback; PyTorch/CuPy/Triton interop where same-contract evidence supports it |
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
released source-tree partner release. The active v2.6 pre-release rule is
primitive-first:

```text
Use a fused generic native RTDL primitive when it exactly expresses the work.
Use an explicit partner continuation only for unfused work or app choice.
Users choose supported partners explicitly; benchmark recommendations must be
backed by same-contract evidence.
Engine absolutely app-agnostic throughout.
```

CuPy, Numba, PyTorch, and Triton are possible continuation partners, not hidden
defaults. CuPy remains the mature CUDA-array and library-continuation partner.
Numba is the current v2.6 lane for selected measured custom CUDA-style
continuations, including compact-mask and grouped-reduction shapes where the
same-contract evidence supports it. Triton is paused for recommended paths
until same-contract timing proves a win. RTDL owns only the supported RTDL
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
general PyTorch/CuPy/Numba/Triton optimizer. Users may call those systems from
Python, but user-written kernels remain application code unless RTDL ships and
reviews that exact generic contract.

Full residency-first, partner-neutral device-memory composition remains a
v3.0 roadmap item. v2.6 has selective reduced-transfer/device-resident evidence
for specific paths, not a general true-zero-copy product guarantee.

## Read Next

- [Quick Tutorial](quick_tutorial.md)
- [RTDL Language Docs](rtdl/README.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [Current Support Matrix](current_main_support_matrix.md)
- [Capability Boundaries](capability_boundaries.md)
- [v2.3 Release Package](release_reports/v2_3/README.md)
