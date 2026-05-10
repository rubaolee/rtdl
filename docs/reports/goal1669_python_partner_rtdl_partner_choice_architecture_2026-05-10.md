# Goal1669 Python+Partner+RTDL Partner Choice Architecture

Date: 2026-05-10

Status: design report for the v1.7-v2.0 Python+partner+RTDL track

## Executive Verdict

RTDL should not choose a partner by hardwiring one framework into the native
engine. The correct architecture is protocol-first and partner-pluggable:

```text
Python app/domain logic
  -> partner adapter selected in Python
  -> generic RTDL tensor/buffer descriptor
  -> app-agnostic RTDL primitive engine
```

The first public implementation should be:

```text
DLPack-compatible handoff as the contract,
CuPy as the first blessed partner,
PyTorch as the first follow-up partner.
```

CuPy is the recommended first partner because it is closest to NumPy semantics,
has direct GPU-array ownership, supports DLPack and CUDA array interop, avoids
ML/autograd assumptions, and is a natural fit for non-graphics RT benchmark
builders who want explicit GPU-resident arrays. PyTorch should follow quickly
because of ecosystem reach, but it should not define the core RTDL partner
contract.

## Non-Negotiable Boundary

The top-level roadmap invariant is:

- first: Python+RTDL;
- second: Python+partner+RTDL;
- both versions: RTDL engine internals must be app-agnostic.

The partner mechanism must not become a new app-specific native backdoor. The
native engine must not know database, graph, robot, polygon, or benchmark
semantics. It may only know generic memory descriptors, primitive packets,
RT-shaped traversal inputs, and generic reductions.

Goal1668 remains the controlling architecture gate: public release wording may
not claim fully app-agnostic native internals until app-shaped native leakage is
removed or mechanically quarantined outside the release surface.

## What "Partner" Means

A partner is an external Python-side compute or memory owner that can prepare,
hold, transform, or consume tensors without forcing RTDL to own the whole data
pipeline.

In Python+RTDL, the usual data shape is:

```text
Python/NumPy app arrays
  -> RTDL copies or prepares native buffers
  -> Embree/OptiX primitive execution
  -> Python receives results
```

In Python+partner+RTDL, the target shape is:

```text
Partner-owned CPU/GPU tensors
  -> RTDL borrows or imports generic descriptors
  -> Embree/OptiX primitive execution
  -> partner receives or views generic result tensors
```

The partner is not the application. The partner is a memory and compute
ecosystem that lets app code stay in Python while reducing unnecessary copying
and avoiding bespoke native app logic.

## Partner Choices

| Candidate | Strengths | Risks | Best Role |
| --- | --- | --- | --- |
| DLPack protocol | Cross-framework tensor capsule; standard handoff vocabulary; keeps RTDL independent from one partner | Protocol, not a full user framework; ownership/lifetime/stream rules must be strict | Core RTDL partner contract |
| CuPy | NumPy-like GPU arrays; direct CUDA orientation; supports DLPack and CUDA array interface; lightweight semantics for benchmark data | NVIDIA-first; less universal than PyTorch; users must install CUDA-matched wheels | First blessed partner and acceptance target |
| PyTorch | Huge user base; strong DLPack support; CUDA stream concepts; practical for ML-adjacent workloads | Heavy dependency; autograd/lifetime semantics can confuse RTDL ownership; install matrix is larger | First follow-up partner and tutorial target |
| Numba | Python kernel authoring; CUDA array interface; useful for custom preprocessing/postprocessing | CUDA target maturity and install friction; weaker as a universal memory owner | Optional compute-side adapter after CuPy/PyTorch |
| Triton | Excellent custom GPU kernels; strong performance story for fused transforms | Usually mediated through PyTorch; not a general tensor-owner UX by itself | Advanced partner-side preprocessing, not first adapter |
| JAX | DLPack support; high-performance functional array system | Async compilation/runtime model; device buffer semantics less beginner-friendly | Later adapter for specialized users |
| RAPIDS/cuDF | Dataframe and columnar GPU data; attractive for data workloads | Domain semantics can pull RTDL toward database-shaped APIs; dependency stack is large | Later app-layer integration through generic tensors only |
| Arrow/NumPy | CPU-side portability and data interchange; useful for Embree and ETL paths | Does not solve NVIDIA device-resident handoff by itself | CPU partner or staging format, not the first GPU partner |

## Why Not Pick PyTorch First?

PyTorch is the best adoption partner, but not the cleanest architecture
starting point. If RTDL begins with PyTorch as the first implementation, the
project risks letting ML-framework assumptions leak into the partner contract:
autograd, module/device conventions, implicit streams, and heavyweight install
requirements.

The core RTDL partner contract should be smaller than PyTorch:

- pointer or capsule import;
- dtype, shape, stride, device, and stream metadata;
- explicit ownership/lifetime rules;
- generic result descriptor creation;
- no autograd promise;
- no model/training semantics;
- no app-specific native callbacks.

Once that contract is proven with CuPy, PyTorch can be added as a high-value
adapter without changing the engine contract.

## Why CuPy First

CuPy is the best first blessed partner because it tests exactly the system
problem RTDL needs to solve:

- user data is already on NVIDIA GPU memory;
- the app wants RTDL to run a generic RT primitive over that memory;
- results should return as GPU arrays without avoidable host roundtrips;
- RTDL should not learn the app's business logic.

CuPy is also conceptually close to the current Python+RTDL user model. Users
already understand arrays; CuPy lets the same mental model move to GPU-resident
arrays without making RTDL an ML framework extension.

The recommended first acceptance demo is therefore:

```text
cupy arrays for rays / primitive packet fields / output buffers
  -> RTDL imports via DLPack-compatible descriptor
  -> OptiX executes an app-agnostic primitive path
  -> results remain in CuPy-owned or CuPy-readable GPU memory
```

This should be described carefully as a measured device-resident handoff only
after evidence exists. Until then, the project must not claim true zero-copy.

## Switchable Partner Architecture

RTDL should expose a Python-side registry and adapter protocol:

```python
class PartnerAdapter:
    name: str

    def can_export(self, obj) -> bool:
        ...

    def export_tensor(self, obj, *, access, stream=None) -> RtdlTensorDescriptor:
        ...

    def allocate_output(self, spec, *, stream=None):
        ...

    def import_output(self, descriptor):
        ...
```

Public user shape:

```python
import rtdsl as rt

ctx = rt.partner.use("cupy")      # or "torch", "auto", "none"
packet = ctx.tensor(rays_gpu)     # produces a generic RTDL descriptor
out = ctx.empty(shape=(n,), dtype="uint8", device="cuda:0")

rt.any_hit(packet, geometry, out=out, backend="optix")
```

The selection layer should support:

- `partner="auto"`: detect the object's native provider;
- `partner="cupy"`: require the CuPy adapter;
- `partner="torch"`: require the PyTorch adapter;
- `partner="none"`: current Python+RTDL path with owned/staged buffers;
- explicit fallback policy: `error`, `copy`, or `host_stage`.

This gives users the ability to choose or switch partners without changing the
RTDL engine. Switching partner changes how tensors are exported and outputs are
allocated, not how primitives are semantically executed.

Auto-detection must be deterministic. The first implementation should use this
priority order:

1. explicit `partner=` argument wins;
2. object module/type ownership wins for known adapters, for example CuPy array
   -> CuPy and PyTorch tensor -> PyTorch;
3. `__dlpack_device__` and `__dlpack__` are accepted through a generic DLPack
   adapter only if no known framework adapter claims the object;
4. `__cuda_array_interface__` is a named fallback for CuPy-like CUDA arrays,
   not the primary path;
5. unknown objects fail unless fallback policy allows copy or host staging.

The first release should prefer explicit partner selection in benchmarks. The
`auto` mode is user convenience, not accepted performance evidence by itself.

The Python module is currently `rtdsl`; the project and language are RTDL.
Public docs should either keep this distinction explicit or rename the module
in a separate compatibility plan. This design report does not authorize a
module rename.

## Engine-Facing ABI Shape

The native engine should receive only generic descriptors:

```text
RtdlTensorDescriptor
  data_ptr
  device_type
  device_id
  dtype
  ndim
  shape[]
  strides[]
  byte_offset
  access_mode
  stream_handle
```

The descriptor must not contain app terms such as table, graph, polygon,
robot, pose, database, BFS, KNN, Jaccard, or Hausdorff. If an app needs those
semantics, Python lowers them into generic primitive packets before calling
RTDL.

For OptiX, the first useful device path should focus on:

- device pointers already resident on the same CUDA device;
- explicit stream synchronization rules;
- output buffers allocated by the partner or by RTDL and exported back;
- strict dtype/layout validation before native launch;
- no implicit CPU roundtrip unless fallback policy says so.

For Embree, partner support should be CPU-compatible:

- NumPy/Arrow-style host descriptors;
- pinned-host staging only when measured and named accurately;
- no false "zero-copy" wording for host/device movement.

The first Embree acceptance sketch should be:

```text
NumPy contiguous host arrays
  -> generic RTDL host tensor descriptor
  -> Embree `ANY_HIT` or `COUNT_HITS`
  -> NumPy-owned output buffer or RTDL-owned output copied back explicitly
```

This is a compatibility and CPU-baseline partner path, not a GPU zero-copy
claim. Arrow can be added later for columnar CPU data only if app semantics
remain outside the engine.

## Ownership, Lifetime, And Streams

The riskiest part of Python+partner+RTDL is not syntax; it is ownership.

Rules:

- RTDL may borrow a partner buffer only for the duration authorized by the
  adapter.
- The adapter must keep the source object alive until the RTDL operation is
  complete.
- If using DLPack capsules, RTDL must respect one-consumer ownership rules and
  avoid consuming capsules twice.
- If using `__dlpack__`, RTDL should pass stream information where supported.
- If RTDL launches asynchronous CUDA work, the completion/lifetime protocol
  must be explicit.
- Result buffers must record who owns deallocation: partner, RTDL, or a scoped
  transfer token.

The first implementation should prefer synchronous correctness over clever
asynchronous overlap. Async streams can be promoted only after parity,
lifetime, and failure-path tests exist.

Canonical import rule for v1.7:

- primary path: Python Array API `__dlpack__` plus `__dlpack_device__`;
- fallback path: raw DLPack capsule, only when the user explicitly passes a
  capsule or an adapter exposes that path;
- named fallback: `__cuda_array_interface__`, only for adapters that explicitly
  validate shape, dtype, strides, device, and lifetime.

The descriptor fields `stream_handle` and `lifetime_token` are reserved in the
first synchronous implementation. `stream_handle` may appear in the v1.7
descriptor only as a reserved field, with `stream_handle=0` required.
`lifetime_token` must not enter the v1.7 native ABI as an untyped free-form
field; v1.7 should keep the partner Python object alive through a scoped
operation guard. A native `lifetime_token` can be added only after a later async
design defines its type, creator, consumer, and failure behavior.

Output allocation must include validation requirements. `allocate_output(spec)`
should receive at least dtype, shape, device, contiguity, byte alignment, and
access mode. If a partner allocation does not satisfy RTDL/OptiX alignment or
layout requirements, the adapter must fail before launch or use an explicitly
reported fallback allocation.

Minimum v1.7 allocation spec:

```text
RtdlOutputSpec
  dtype
  shape[]
  device_type
  device_id
  required_contiguous
  required_alignment_bytes
  access_mode
  fallback_policy
```

## Fallback Policy

Partner switching needs explicit fallback behavior, otherwise performance
claims become ambiguous.

Recommended fallback modes:

| Mode | Meaning | Public claim boundary |
| --- | --- | --- |
| `error` | fail if zero-copy or direct device import is not possible | best for benchmark evidence |
| `copy` | allow device-to-device or host/device copy as needed | not true zero-copy |
| `host_stage` | materialize through CPU memory | compatibility only, not performance evidence |

Benchmark and release tests should use `error` when validating true
device-resident handoff. Tutorials may use `copy` only if the text clearly
labels it as a fallback.

## First Acceptance Slice

The first Python+partner+RTDL milestone should be deliberately narrow:

1. CuPy adapter behind a generic `PartnerAdapter` registry.
2. DLPack-compatible import path for contiguous GPU tensors.
3. One OptiX primitive path, preferably `ANY_HIT` or `COUNT_HITS`, accepting
   partner-owned input and output buffers.
4. Strict parity against the existing Python+RTDL path.
5. Phase timing that separates adapter/export, RTDL launch, synchronization,
   and fallback/copy time.
6. Claim boundary file that says whether the run proves device-resident
   handoff, reduced-copy, or only functional compatibility.

This first slice should not attempt all stable apps, all primitives, all
partners, or async stream optimization. It should prove the architecture.

The matching CPU acceptance slice should be named separately:

```text
Embree NumPy host descriptor acceptance:
  NumPy contiguous host rays/geometry
  -> generic RTDL host tensor descriptor
  -> Embree ANY_HIT or COUNT_HITS
  -> NumPy-compatible output
```

This CPU slice should validate partner-registry symmetry and source-tree
runnability. It should not be used as GPU device-resident handoff evidence.

## Public API Sketch

Minimal user-facing surface:

```python
import cupy as cp
import rtdsl as rt

partner = rt.partner.use("cupy", fallback="error")

rays = cp.asarray(...)
geometry = rt.geometry.triangles(cp.asarray(...), partner=partner)
hits = partner.empty((rays.shape[0],), dtype=cp.uint8)

rt.any_hit(rays, geometry, out=hits, backend="optix", partner=partner)
```

Equivalent switch to PyTorch later:

```python
import torch
import rtdsl as rt

partner = rt.partner.use("torch", fallback="error")

rays = torch.as_tensor(..., device="cuda")
geometry = rt.geometry.triangles(torch.as_tensor(..., device="cuda"), partner=partner)
hits = partner.empty((rays.shape[0],), dtype=torch.uint8, device="cuda")

rt.any_hit(rays, geometry, out=hits, backend="optix", partner=partner)
```

The RTDL primitive call should not change meaning when the partner changes.
Only the adapter/export/allocation mechanics change.

Geometry partner semantics:

- `partner=` on geometry construction means "import this geometry buffer through
  this adapter now."
- The geometry object records its adapter family, device, dtype/layout contract,
  and fallback mode.
- A primitive call with a different explicit partner must fail unless the user
  requests a documented transfer fallback.
- Switching partner for a pipeline therefore means rebuilding or transferring
  partner-owned geometry descriptors, not silently reinterpreting an existing
  descriptor under a different framework.
- Benchmarks must use mismatch-as-error behavior.

PyTorch follow-up tests need additional cases beyond the CuPy suite:

- grad-enabled tensors must be rejected or explicitly detached;
- leaf tensors and views must have clear ownership behavior;
- non-contiguous tensors must either export valid strides or fail before native
  launch;
- DLPack export must not promise autograd integration.

## Release Claim Rules

Before evidence exists, allowed wording:

```text
RTDL is designing a Python+partner+RTDL track based on generic partner tensor
handoff.
```

After the CuPy slice passes functional tests but still copies:

```text
RTDL supports a CuPy adapter for partner-owned tensors on the measured primitive
path, with fallback copy behavior explicitly reported.
```

Only after a measured GPU-resident path proves no avoidable CPU roundtrip:

```text
RTDL supports a measured device-resident CuPy handoff for the exact reviewed
OptiX primitive path.
```

Blocked wording until separately proven:

- "RTDL has general true zero-copy support."
- "RTDL accelerates arbitrary PyTorch/CuPy programs."
- "RTDL optimizes partner code."
- "RTDL native internals are fully app-agnostic."
- "All partners are interchangeable with no performance differences."

## Implementation Roadmap

| Step | Deliverable | Exit Gate |
| --- | --- | --- |
| 1 | `PartnerAdapter` Python protocol and registry | unit tests for selection/fallback |
| 2 | generic tensor descriptor object | dtype/shape/stride/device validation tests |
| 3 | CuPy adapter | import/export tests without launching OptiX |
| 4 | OptiX one-primitive CuPy acceptance path | parity and phase timing |
| 5 | claim-boundary report | no true zero-copy claim unless measured |
| 6 | PyTorch adapter | same tests as CuPy, no engine ABI change |
| 7 | expanded primitive coverage | `COUNT_HITS`, reductions, then experimental collect |
| 8 | app migration | apps lower through generic Python packets only |

## Final Recommendation

Choose DLPack-compatible tensor handoff as the stable contract, choose CuPy as
the first blessed partner implementation, and design the API so PyTorch, Numba,
Triton-mediated workflows, JAX, and RAPIDS/cuDF can be added later without
changing the app-agnostic RTDL engine.

This choice gives RTDL a clean first implementation path, keeps the engine
generic, reduces the risk of ML-framework semantics polluting the core design,
and still leaves a clear route to the largest user ecosystem through PyTorch.
