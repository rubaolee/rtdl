# RTDL V3

**Verified semantic lowering for non-graphical ray-tracing workloads on NVIDIA OptiX.**

RTDL 3.0 is the official V3 source release. It lets an application state a
bounded spatial or relational computation without providing an arbitrary
OptiX callback. The compiler resolves that semantic statement to a canonical,
source-bound physical provider, validates its proof and resource obligations,
and requires post-run evidence that the authorized OptiX traversal actually
executed.

```text
application-owned algorithm
        ↓
typed semantic Action statement
        ↓
canonical compiler resolution
        ↓
verified OptiX physical provider
        ↓
exact output + behavioral traversal receipt
```

V3 is intentionally not a SQL-style cost optimizer and does not claim to
invent the fastest algorithm. The application owns algorithmic choices such as
Triangle Counting RT-1A2 versus RT-2A1. V3 owns the correctness-critical step
after that choice: finding, validating, materializing, and auditing the one
registered physical implementation for the selected semantics.

## Start here

Requirements for the Python source surface are Python 3.10+ and NumPy. From a
fresh checkout:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
python3 -m pip install -e .
python3 examples/current/v3_canonical_mapping.py
```

Expected result:

```text
status: RESOLVED
statement: metric_knn.filter_refine_linf_3d.v1
backend: nvidia.optix_traversal.v1
provider: canonical_standalone/metric_knn_linf_filter_refine_3d/optix/prepared_metric_knn_3d_optix
cost input used: False
candidate executed: False
behavioral receipt still required: True
```

This first example performs static resolution only and therefore runs without
a GPU. Building and executing the NVIDIA path additionally requires a Linux
host with an NVIDIA driver, CUDA toolkit, OptiX SDK, C++ toolchain, and GEOS:

```bash
export OPTIX_PREFIX=/path/to/NVIDIA-OptiX-SDK
export CUDA_PREFIX=/usr/local/cuda
make build-optix
```

See [V3 release and installation](docs/v3/release.md) for the
target-rematerialized validation path.

## The V3 contract

The production compiler separates four identities that app-directed GPU code
often conflates:

| Identity | What V3 binds |
| --- | --- |
| Semantic statement | Input domain, typed effects, precision, ordering, ties, termination, and exact output semantics |
| Backend contract | NVIDIA OptiX execution class, required providers, resource rules, and evidence requirements |
| Physical provider | Source digest, ABI, template, proof, capacity, lifetime, and reuse contracts |
| Execution evidence | Materialized native/plan identity, exact output, and complete bound traversal receipt |

Resolution succeeds only when exactly one registered provider satisfies the
complete contract. Missing, ambiguous, stale, forged, or resource-ineligible
bindings fail before execution. A matching name is never sufficient.

The implementation centers on:

- [`canonical_physical_resolution.py`](src/rtdsl/canonical_physical_resolution.py)
- [`action_api.py`](src/rtdsl/action_api.py)
- [`default_compiler_frontdoor.py`](src/rtdsl/default_compiler_frontdoor.py)
- [`physical_execution_provenance.py`](src/rtdsl/physical_execution_provenance.py)

## Why this is not syntax sugar

A string-to-function table could dispatch a name. V3 additionally checks that:

- the provider refines the statement's input, effect, output, precision, and
  deterministic tie contracts;
- its exact source, ABI, template, proof, and native identities match the
  compiler registry;
- dynamic cardinality and memory bounds hold on the target;
- materialization did not substitute a different implementation;
- output matches the independent application oracle; and
- complete context-bound OptiX launches were behaviorally observed with zero
  failed, incomplete, unbound, pending, or session-error launches.

This makes physical execution auditable without exposing an unrestricted
device callback escape hatch.

## Nine validated applications

The V3 functional qualification covers nine paper applications and fourteen
canonical physical regions:

| Application | Application-owned algorithm or region |
| --- | --- |
| RTNN | ranked distance-window search |
| RayDB | partitioned grouped signed-I64 reduction |
| LibRTS | prepared AABB query and overlap |
| X-HD | cell-MBR exact witness |
| RT-DBSCAN | fixed-radius components |
| RayJoin | point location, intersection, and grouped reduction |
| RT-BarnesHut | aggregate hierarchy |
| Triangle Counting | RT-1A2 and RT-2A1 |
| Arkade | FR-L-infinity and MT-cosine |

All qualified outputs are exact under their declared contracts, and every
required physical region has behavior-level OptiX evidence. See the
[full support matrix](docs/v3/support_matrix.md) for compositions and limits.

## Extending V3

Applications compose existing typed statements. They cannot inject arbitrary
Python, Numba, PTX, or OptiX callbacks through the production front door.

When a required semantic component is missing, compilation fails closed. A
language implementer may add an app-neutral physical family by specifying its
domain, effects, output, precision, ordering, lifetime, capacity, fallback,
source, ABI, proof, and evidence contracts, then validating it with reference,
adversarial, and real-consumer tests. The complete process is documented in
[Correctness and extension](docs/v3/correctness_and_extension.md).

## Performance scope

RTDL V3 is a formally released research compiler/runtime, not a claim that
compiler orchestration is free or that every V3 endpoint beats handwritten
code. The project preserves favorable, parity, and unfavorable results. Cold
single-invocation paths may expose compiler setup cost; prepared execution may
amortize it only when the application genuinely reuses prepared state.

The release claim is therefore precise: **V3 provides correct, deterministic,
auditable lowering to true OptiX execution across the supported semantic
universe.** Performance claims remain workload-, lifecycle-, machine-, and
baseline-specific.

## Documentation

- [V3 overview](docs/v3/README.md)
- [Architecture](docs/v3/architecture.md)
- [Correctness and extension](docs/v3/correctness_and_extension.md)
- [Nine-application support matrix](docs/v3/support_matrix.md)
- [V3 release and installation](docs/v3/release.md)
- [V3.0.0 release notes](docs/v3/release_notes_3_0_0.md)
- [Canonical lowering tutorial](tutorials/v3_canonical_lowering.md)
- [Documentation index](docs/README.md)
- [Paper applications](Paper-reproduction-apps/README.md)

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | V3 Action language, compiler, runtime, canonical registry, and partner adapters |
| `src/native/optix/` | App-neutral NVIDIA OptiX/CUDA provider implementation |
| `Paper-reproduction-apps/` | Application-owned inputs, algorithms, comparators, and V2/V3 front doors |
| `examples/` | Runnable examples and non-paper consumers |
| `tutorials/` | Ordered learning material |
| `docs/v3/` | V3 architecture, correctness, support, and release documentation |
| `tests/` | Focused release and regression tests |

Historical v2 material remains available for reproducibility, but V3.0 is the
active project front door.

## Version

Current release: **RTDL 3.0.0**.
