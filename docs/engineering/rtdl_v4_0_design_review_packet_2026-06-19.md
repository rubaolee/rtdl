# RTDL V4.0 Design Review Packet

Status: engineering design packet for study and external review.
Date: 2026-06-19.
Audience: RTDL maintainers, external systems reviewers, language-binding
reviewers, CUDA/OptiX reviewers, and framework-interop reviewers.

This document defines the intended V4.0 architecture before implementation.
It is not a release note, stable ABI promise, package-install promise, public
speedup claim, or true-zero-copy claim. It is the design target and review
contract for making RTDL an RT-core operator for host-owned GPU programs.

## One-Line Goal

V4.0 makes RTDL the RT-core operator that the Python GPU ecosystem
(CuPy / Numba / PyTorch) can call on its own device arrays, zero-copy and on
the caller's CUDA stream, with a C ABI substrate underneath that can later let
non-Python hosts in.

```text
V3.0: Python + RTDL owns the execution loop; partners are explicit guests.
V4.0: CuPy/Numba/PyTorch own the GPU loop; RTDL is the RT-core operator.
```

## Executive Summary

V4.0 should lead with product value: a Python GPU program passes existing
CuPy, Numba, or PyTorch device arrays to RTDL, RTDL runs an RT-core spatial
query on the caller's CUDA stream, and the result returns as a device array the
host can keep using.

The C ABI remains real, but it is the basement under that Python product, not
the product headline. The V4 foundation is therefore:

- a Python device-array RT-core route with one benchmark-valuable primitive,
  not a host-only plumbing route as the first product proof;
- zero-copy evidence for that exact route: pointer identity, no host-stage
  transfer evidence, stream-order proof, and correctness parity;
- a narrow C ABI substrate with opaque handles, status codes, versioning,
  capability queries, explicit ownership, last-error diagnostics, and no C++
  types across the boundary;
- external runtime ownership, where the host can provide the device, CUDA
  context, stream, allocator policy, and synchronization expectations;
- neutral buffer descriptors that can represent CUDA arrays,
  `__cuda_array_interface__`, and DLPack-style tensors;
- thin Python bindings over the substrate, with non-Python hosts and SDK
  packaging moved to V4.x.

Optional device-callable fusion remains an advanced V4 track. It should not
gate V4.0. It must be treated as a falsifiable experiment with register,
occupancy, correctness, and maintenance evidence before it is promoted.

## Product Pitch: The Missing RT-Core Lane

NVIDIA GPUs expose three useful compute lanes for modern accelerated programs:

| GPU engine | Who drives it from Python today |
| --- | --- |
| CUDA cores | CuPy, Numba, Triton, PyTorch |
| Tensor cores | PyTorch, Triton, cuBLAS/cuDNN-backed stacks |
| RT cores | nobody has a first-class Python numeric-stack path |

The Python accelerator ecosystem already has first-class ways to use CUDA
cores and tensor cores. It does not have a first-class way to use RT cores as
a normal lane in a tensor/device-array pipeline. RT cores are reachable through
ray-tracing runtimes such as OptiX, DXR, and Vulkan RT, but those APIs live in
C/C++ graphics/runtime territory rather than in CuPy, Numba, PyTorch, or
Triton workflows.

V4.0 therefore positions RTDL as the missing RT-core lane for the Python GPU
ecosystem: PyTorch/Triton handle tensor-core math, Numba/CuPy handle CUDA-core
math, and RTDL handles RT-core spatial/traversal work on the same device
arrays and caller stream.

The defensible claim is that those Python frameworks do not currently provide
first-class RT-core traversal. Performance remains route-specific: RT cores
help only when the operation is genuinely spatial/traversal-shaped and the
route has evidence at relevant scale. V4.0 must preserve that honesty.

## Design Review Status

Claude's 2026-06-19 review approves this packet as the V4.0 baseline and
requires five gaps to be closed before M1 design freeze. This revision accepts
those five decisions into the packet:

- D1: every query route supports RTDL-owned result handles and caller-provided
  output buffers with capacity, required-count reporting, and truncation
  status.
- D2: every public descriptor begins with `struct_size`; descriptors are
  append-only, and old-size callers get default values for absent trailing
  fields.
- D3: capability discovery uses one enum-keyed query function instead of an
  unbounded set of typed symbols.
- D4: every descriptor is validated before use; borrowed device pointers are
  caller-asserted and cannot be verified for liveness or residency by RTDL.
- D5: V4.0 ships with pre-1.0 experimental substrate wording until the Python
  device-array product route drives a device-buffer route end to end; AABB2
  proves plumbing, and a benchmark-valuable route shapes the ABI before stable
  wording.

The acceptance criteria and milestones below are now read with those decisions
as mandatory gates, not optional review notes.

## Product Reframing Status

The 2026-06-19 reframing note
`docs/reviews/v4_reframing_note_rt_core_operator_for_python_gpu_ecosystem_2026-06-19.md`
is accepted as a P0 input to M1 design freeze. It changes the packet's
sequencing:

- Phase 1 is now a Python device-array RT-core operator route with real
  zero-copy evidence.
- Phase 2 hardens the C ABI substrate beneath the Python binding using D1-D5.
- Phase 3/V4.x covers non-Python hosts and SDK packaging after the Python
  product route proves the device-buffer contract.

Scope decision accepted for M1 freeze:
V4.0 is Python actors only: CuPy, Numba, Triton, PyTorch, and JAX-style
device-array programs. There is no C++ host in current V4.0 scope. The full
public multi-language C ABI, C/C++/Rust SDK examples, generated bindings, and
pkg-config/CMake packaging are V4.x unless a future product decision reopens
them.

## Why V4 Exists

V3.0 closed the current benchmark-route system. It teaches users to write
Python application code around app-agnostic RTDL primitives, prepared execution,
backend choice, and explicit partner continuations. That is valuable, but it
still makes Python the normal host.

V4.0 exists because Python GPU programs need RT-core spatial queries without
leaving their own device-array pipeline:

- a CuPy pipeline wants to pass an existing CUDA array to RTDL and receive a
  CUDA result array without host staging;
- a Numba pipeline wants RT-core traversal as an operator alongside its own
  kernels, ordered on the caller's stream;
- a PyTorch pipeline wants device-buffer handoff through DLPack/CUDA metadata
  without forcing the user to write OptiX;
- a Python GPU application wants RTDL to be a hardware-specific island, like a
  `cupy.RawKernel` or Triton kernel, but for RT cores.

The V4 design question is therefore not "how do we expose every RTDL internal?"
It is "what is the smallest honest boundary that lets Python GPU hosts call
RTDL on their own device arrays without copies, hidden syncs, or private
runtime fights?"

Non-Python embedding remains strategically valuable, but it is V4.x work under
the current V4.0 scope decision. It must not reorder V4.0 around SDK packaging
or public C/Rust host examples.

## Relationship To Existing Preparatory Work

The repository already contains archived V4-preparatory material under:

`docs/history/v4_preparatory_embedding/`

Those files proved useful slices:

- draft `rtdl.h` C ABI shape;
- lifecycle, status, last-error, capability, context, buffer, index, and query
  symbols;
- a narrow host `F32` AABB2 overlap route returning host `U64`
  `(query_id, primitive_id)` pairs;
- source-tree, prefix, archive, CMake, and pkg-config staging proofs;
- C direct-link and dynamic-load examples;
- Python `ctypes` examples;
- CUDA descriptor metadata import/export;
- `__cuda_array_interface__` and DLPack-like descriptor bridges;
- fail-closed behavior for unsupported device-buffer query routes and external
  CUDA stream semantics.

That material remains preparatory evidence. V4.0 should use it as input, not
pretend it is already a stable SDK.

The archived draft header is also not the final V4 target. It predates the
`rtdl_query_plan` / `rtdl_result` / future `rtdl_event` split and the M1
decisions for result allocation, descriptor extensibility, and capability
queries.

## Core Design Principles

1. Host owns the loop.
   In V4.0, CuPy, Numba, PyTorch, Triton, or JAX-style Python GPU programs own
   the loop. In V4.x, the same rule can extend to C, C++, Rust, Julia, C#, and
   Java hosts if that product scope is reopened.

2. Substrate boundary first, public SDK later.
   The Python product should stand on a narrow internal C ABI/substrate. Every
   future stable non-Python binding should sit on that same C ABI. No public
   C++ ABI, exceptions, STL containers, templates, CUDA C++ classes, or OptiX
   internals cross the stable boundary.

3. Opaque handles only.
   Contexts, indices, query plans, compiled kernels, buffers, and result sets
   are opaque. Handles have explicit destroy functions.

4. Capability queries, not optimistic dispatch.
   Every backend, primitive, query kind, device type, dtype, layout, and stream
   mode must be discoverable and must fail closed when unsupported.

5. Explicit ownership.
   Every buffer is caller-retained, release-callback-owned, or RTDL-owned. No
   borrowed pointer is used after its documented lifetime.

6. External runtime compatibility.
   RTDL can accept host-provided context/stream metadata. It does not create
   hidden global CUDA state when embedded in a framework that already owns CUDA.

7. Device-buffer routes require evidence.
   Descriptor metadata is not zero-copy support. A route becomes device-buffer
   support only when the query actually consumes the device buffer correctly.
   A route becomes true zero-copy only when transfer-counter or equivalent
   evidence proves no host stage on the exact path.

8. Bindings are thin.
   Language packages wrap the C ABI. Binding layers should not contain
   duplicated primitive logic, scheduling policy, or backend-specific hacks.

9. App-agnostic native engine.
   V4 must preserve the V3 lesson: the native engine exposes generic primitives
   and query contracts, not Hausdorff, DBSCAN, robotics, graph, GIS, or DBMS
   application semantics.

10. Device-callable fusion is optional.
    Fusion may become valuable, but it is not the foundation. Zero-copy buffer
    interop and a stable substrate solve the common case first.

## Non-Goals For V4.0

- No stable C++ public ABI.
- No promise that every V3 Python example becomes a C ABI route.
- No automatic partner/backend selection.
- No broad "RTDL accelerates arbitrary PyTorch/CuPy/Numba code" claim; V4.0
  claims only reviewed RT-core operator routes.
- No public true-zero-copy wording unless the exact path is measured.
- No public RT-core speedup wording unless the exact app/backend/contract is
  reviewed.
- No app-specific native engine APIs.
- No device-callable fusion as a release blocker.
- No arbitrary DLPack capsule support until ownership, shape, dtype, device,
  stream, deleter, and lifetime rules are validated.

## Target Architecture

```text
L5  Review and evidence layer
    release gates, symbol manifests, transfer evidence, compatibility tests

L4  Host bindings and framework adapters
    Python GPU binding first; C/Rust/Julia/C#/Java in V4.x if reopened

L3  C ABI substrate
    opaque handles, status, versioning, capabilities, buffers, indices, queries

L2  Runtime interop layer
    external runtime metadata, stream policy, allocator hooks, buffer descriptors

L1  Native RTDL core
    app-agnostic primitive execution, prepared indices, traversal, result buffers

L0  Backend implementations
    CPU/oracle, Embree, OptiX first; HIPRT/Vulkan/Apple RT later by evidence
```

Dependencies point downward. L1 and L0 do not import language-binding logic,
framework logic, or application-specific policy.

## Primary User Stories

### Python GPU Host

A CuPy, Numba, or PyTorch program can:

1. keep ownership of its CUDA device arrays;
2. expose pointer, shape, dtype, device, and stream metadata through
   `__cuda_array_interface__` or DLPack;
3. call a Python RTDL operator for a generic RT-core spatial query;
4. have RTDL run on the caller's CUDA context and stream;
5. receive a device result array without host staging;
6. continue its Python GPU pipeline.

This is the V4.0 product story.

### Python Binding Substrate

Python can use a thin `ctypes`, `cffi`, or generated binding layer over the same
C ABI substrate. This binding must not bypass the substrate through private
C++/Python internals, but the user should experience it as a Python GPU
operator, not as a C API.

### Framework Tensor Host

A CuPy/PyTorch/JAX/Numba host can pass a device buffer descriptor into RTDL.
The first product milestone must execute at least one real device-buffer query
route with stream, ownership, and no-host-stage evidence.

### C Host

A C program can load `librtdl`, check ABI compatibility, import buffers, run a
route, and destroy handles deterministically. This is valuable as the substrate
proof and as a V4.x external-host target after the Python product route proves
the contract.

### Rust Host

A Rust program can generate bindings from `rtdl.h`, link to `librtdl`, and run
the same route without Python. This remains the first "not just C" ABI proof,
but it is V4.x under the current Python-only V4.0 scope decision.

### Native Backend Host

An embedded program can select CPU, Embree, or OptiX through capabilities and
receive deterministic failure if the selected route is unsupported.

## C ABI Design

### Versioning

The ABI exposes:

```c
uint32_t rtdl_abi_version_major(void);
uint32_t rtdl_abi_version_minor(void);
uint32_t rtdl_abi_version_patch(void);
uint32_t rtdl_abi_is_compatible(uint32_t major, uint32_t minor, uint32_t patch);
```

Before ABI 1.0, breaking changes are allowed but must update version markers,
symbol manifests, docs, examples, and tests. After ABI 1.0:

- no exported symbol is removed within a major version;
- enum/status values are not reused for different meanings;
- new optional symbols and capabilities may appear in minor versions;
- breaking behavior requires a major version or explicit opt-in capability.

V4.0 should therefore use `0.x` experimental SDK wording. ABI `1.0` is blocked
until a real external host, not only an in-tree toy client, drives at least one
device-buffer route end to end and the packaging/install gates pass.

### Descriptor Extensibility

Every public descriptor begins with:

```c
size_t struct_size;
```

RTDL reads only the fields present within the caller-provided `struct_size`.
Fields added after a caller's compiled header default to documented values.
Descriptor evolution is append-only until ABI `1.0`; fields are not reordered,
repurposed, or removed. Layout tests must pin `sizeof` and `offsetof` values,
and compatibility tests must pass descriptors with older sizes.

Use `sType` / `pNext` only if V4 later needs heterogeneous extension chains.
The base V4.0 contract is `struct_size`, not Vulkan-style extension plumbing.

### Opaque Handles

Stable handles should include:

```c
typedef struct rtdl_context rtdl_context;
typedef struct rtdl_buffer rtdl_buffer;
typedef struct rtdl_index rtdl_index;
typedef struct rtdl_query_plan rtdl_query_plan;
typedef struct rtdl_result rtdl_result;
```

The current draft has `rtdl_query`; V4 should decide whether query handles
represent executable plans, submitted async work, or both. The design
recommendation is to split them:

- `rtdl_query_plan`: immutable prepared query configuration;
- `rtdl_result`: completed result buffer/result-set handle;
- optional future `rtdl_event`: async completion and synchronization handle.

### Status And Errors

All ABI calls return `rtdl_status` or write through output pointers and return
`rtdl_status`.

Required status classes:

- OK
- invalid argument
- unsupported capability
- result truncated
- ABI/version mismatch
- out of memory
- backend failure
- stream/runtime failure
- shape/layout mismatch
- ownership/lifetime violation where detectable
- internal error

Last-error strings are diagnostic text. Callers branch on status codes, never
on string contents.

### Context Creation

Context creation should accept:

- requested backend or auto;
- device type and device id;
- optional external runtime metadata;
- optional allocator hooks;
- optional logging/diagnostic callback;
- ABI descriptor version.

Context creation must fail closed if the backend or external runtime mode is
not supported.

### Capability Queries

The C ABI must answer questions before users attempt execution, and it should
do that through one enum-keyed function:

```c
typedef enum rtdl_capability {
    RTDL_CAP_BACKEND_AVAILABLE = 1,
    RTDL_CAP_ROUTE_ACCEPTS_HOST_BUFFERS = 2,
    RTDL_CAP_ROUTE_ACCEPTS_DEVICE_BUFFERS = 3,
    RTDL_CAP_ROUTE_SUPPORTS_BORROWED_DEVICE_POINTERS = 4,
    RTDL_CAP_ROUTE_SUPPORTS_EXTERNAL_STREAM = 5,
    RTDL_CAP_ROUTE_DETERMINISTIC_ROW_ORDER = 6,
    RTDL_CAP_ROUTE_SUPPORTS_ASYNC = 7,
    RTDL_CAP_ROUTE_REQUIRES_RTDL_ALLOCATION = 8
} rtdl_capability;

rtdl_status rtdl_query_capability(
    const rtdl_context* context,
    const rtdl_route_desc* route, /* nullable for context-level queries */
    rtdl_capability cap,
    uint64_t* value_out);
```

Typed helper wrappers may exist during development, but the stable surface
should not grow a new exported symbol for every new capability. Unknown
capability enum values return `RTDL_STATUS_UNSUPPORTED`.

The initial capability inventory must answer:

- Is backend `X` available?
- Is primitive `P` supported for query `Q` on device type `D`?
- Does this route accept host buffers?
- Does this route accept device buffers?
- Does this route support borrowed device pointers?
- Does this route support external streams?
- Does this route produce deterministic row ordering?
- Does this route support async execution?
- Does this route require an RTDL-owned allocation?
- What dtypes, shapes, layouts, and alignment are accepted?

Capabilities must be machine-readable, not prose-only.

### Buffer Descriptor

The neutral buffer descriptor is the center of V4 interop:

```text
struct_size
data pointer
byte count
device type
device id
dtype
ndim
shape
strides
layout flags
ownership mode
release callback
producer protocol
stream/event metadata
user data
```

Required ownership modes:

- caller-retained borrowed pointer;
- release-callback-owned pointer;
- RTDL-owned allocation;
- imported external object with deleter bridge;
- exported borrowed view over an RTDL result.

V4 should keep fixed-size shape/stride arrays for C simplicity unless review
finds a strong reason for a variable-size layout. If fixed-size arrays remain,
the maximum rank must be documented and tested.

### Descriptor Validation

RTDL validates every descriptor before using any pointer or shape metadata.
Malformed input fails closed with `RTDL_STATUS_INVALID_ARGUMENT` or a narrower
status code. Negative tests must cover at least:

- null data pointer with nonzero `byte_count`;
- `ndim` greater than the documented maximum rank;
- `byte_count` inconsistent with shape, stride, item size, or layout flags;
- integer overflow while computing extents or byte ranges;
- unsupported dtype, layout, alignment, device type, or ownership mode;
- route descriptors that request unsupported primitive/query/backend/device
  combinations.

Borrowed device pointers are caller-asserted. RTDL can validate descriptor
shape and route support, but it cannot generally prove pointer residency,
liveness, aliasing safety, or that the producer object will outlive execution.
Misrepresenting those properties is caller undefined behavior.

### Index And Query Contracts

Each stable route must document:

- primitive kind;
- query kind;
- dtype;
- shape and field order;
- ownership and lifetime of input buffers;
- whether index build copies or borrows primitive data;
- whether query execution copies, borrows, or consumes query data;
- result dtype, shape, row ordering, and ownership;
- supported backend/device combinations;
- stream semantics;
- deterministic failure cases.

The first route should stay deliberately small. A good V4 base route is:

```text
host F32 AABB2 index
host F32 AABB2 overlap query
host U64 result pairs
CPU backend
deterministic ordering
```

Then expand one axis at a time:

1. host route via Embree;
2. host route via OptiX where meaningful;
3. CUDA descriptor route that still rejects query execution;
4. real CUDA device-buffer query route for one primitive/query pair;
5. external CUDA stream ordering proof;
6. zero-copy proof for that exact device-buffer route.

### Result Size And Output Allocation

Every query route supports two output modes.

Mode 1 is an RTDL-owned result handle:

```text
submit query -> rtdl_result*
inspect result shape/count/dtype
borrow or copy result rows through accessors
destroy result
```

This mode is the easiest binding target and the safest first Python/C example
because RTDL owns allocation and lifetime. Rust becomes the stricter ownership
proof when V4.x non-Python hosts open.

Mode 2 is a caller-provided output buffer:

```text
output pointer
output capacity in rows or bytes
required_count_out
written_count_out
status
```

RTDL must never write beyond capacity. If the exact result requires more rows
than capacity, RTDL writes at most capacity rows, writes the required count,
and returns `RTDL_STATUS_RESULT_TRUNCATED`. The caller can then allocate a
larger buffer and run a size-then-fill second call. Exact-fit and truncation
cases are mandatory route tests.

Framework-owned tensor outputs are treated as a caller-provided output buffer
with framework lifetime and stream rules. A route may reject this mode unless
capability queries say it is supported.

## Runtime, Context, And Stream Semantics

V4 must be explicit about who owns the runtime.

### Host-Owned Runtime

The host can provide:

- CUDA context handle;
- CUDA stream handle;
- device id;
- optional allocator hooks;
- optional user data;
- optional synchronization policy.

RTDL must not silently replace this with a private stream or device-wide
synchronization. If RTDL must synchronize, the operation must be documented and
visible in metadata.

### Stream Policy

V4 should define three stream modes:

| Mode | Meaning |
| --- | --- |
| synchronous host call | call returns after work and result are ready |
| caller-stream async | RTDL enqueues work on caller stream; caller owns ordering |
| RTDL-stream async | RTDL uses its own stream and returns an event/dependency |

The release target should support synchronous host calls first. CUDA stream
support should be added only with explicit tests for ordering and no hidden
device-wide syncs. CPU and Embree routes should be treated as synchronous
initially; async/event handles become part of V4 only when a shipped route has
real ordering tests. CUDA async is a CUDA-route feature, not a blanket promise
for every backend.

### Allocator Policy

The ABI should allow future allocator hooks without making them mandatory for
V4.0:

- RTDL default allocation;
- caller-provided host allocation hooks;
- caller-provided device allocation hooks;
- framework-owned device tensor output.

Allocator callbacks must be optional, versioned, and fail closed if the route
cannot honor them.

## Zero-Copy And Device Interop

### Definitions

Descriptor import:
RTDL records pointer, dtype, shape, strides, device, and ownership metadata.
This is not zero-copy execution.

Device-buffer query:
RTDL executes a route that consumes device memory without first requiring a
host buffer as the query input.

Zero-copy candidate:
The route uses the same device pointer and avoids host staging by design.

Public true-zero-copy claim:
The route has reviewed evidence, such as transfer counters, pointer identity,
stream/event checks, and negative host-stage checks, proving no host copy for
the exact command.

### Protocols

V4 should support these protocol families in order:

1. host C arrays;
2. `__array_interface__` metadata where appropriate;
3. `__cuda_array_interface__` for CuPy/Numba-style CUDA arrays;
4. DLPack for PyTorch/JAX/CuPy/framework-neutral handoff;
5. HIP/Metal/Vulkan buffer metadata only after CUDA is correct.

### DLPack Policy

DLPack is not just a pointer. It carries ownership and deleter rules. A V4
DLPack adapter must specify:

- whether the route accepts legacy `dltensor` capsules, versioned
  `dltensor_versioned` capsules, or both;
- when RTDL consumes a capsule;
- whether RTDL borrows or takes ownership;
- when the producer deleter is called;
- whether the capsule can be consumed once only;
- the consumed-capsule rename convention, such as `used_dltensor`;
- whether read-only or immutable producer flags are respected;
- dtype and layout mapping;
- stream synchronization expectations;
- device compatibility;
- error behavior for unsupported layouts.

Until these are tested, call it DLPack-like metadata, not DLPack support.

### CUDA Array Interface Policy

For `__cuda_array_interface__`, V4 must specify:

- pointer extraction;
- shape/stride mapping;
- dtype mapping;
- device id mapping;
- stream field interpretation;
- lifetime of the Python object producing the descriptor;
- whether RTDL holds a reference to the producer object;
- whether RTDL can execute on the producer stream.

### Evidence For True Zero-Copy

An exact route can claim true zero-copy only after a review packet includes:

- command and commit;
- hardware and driver/runtime versions;
- input producer type;
- backend and route;
- pointer identity before/after import;
- no host-stage transfer counters or equivalent instrumentation;
- stream-order proof;
- correctness parity;
- negative test showing host-only routes reject device buffers;
- statement of exact scope and blocked generalizations.

## Product-Led Roadmap

V4 should not expose every backend or every host at once. It should first prove
the product route users will feel.

### Phase 1: Python Device-Array RT-Core Operator

Goal: prove "CuPy/Numba/PyTorch array in -> RT cores -> device array out."

- Python entry point accepts CuPy/Numba/PyTorch device arrays through
  `__cuda_array_interface__` and DLPack-style handoff.
- RTDL uses the caller's CUDA context and stream where supported.
- One benchmark-valuable route runs end to end:
  `fixed_radius_count_threshold_2d`, with caller-owned CUDA point columns in
  and fixed-size CUDA output columns out.
- Result returns as a device buffer the host can wrap back into its own array
  type.
- Evidence includes pointer identity, no host-stage transfer counters or
  equivalent instrumentation, stream-order proof, and correctness parity.

### Phase 2: C ABI Substrate Hardening

Goal: make the boundary under the Python product durable.

- Keep the active `0.x` C ABI substrate underneath the Python binding.
- Apply and test D1-D5: result sizing, `struct_size`, enum capability query,
  descriptor validation, and pre-1.0 wording.
- Keep host AABB2 as a boring control-plane and result-contract proof, not as
  the product route.
- Add layout, old-size descriptor, symbol-manifest, and negative tests.

### Phase 3: Non-Python Hosts And SDK Packaging

Goal: expand after V4.0 only if non-Python hosts are reopened as product scope.

- C, then Rust, then Julia clients over the proven C ABI substrate.
- CMake/pkg-config stage, archive extraction, external consumer validation,
  symbol manifest, and layout audit.
- Under the current Python-only V4.0 scope decision, this phase is V4.x.

### Phase 4: Optional Advanced Fusion Track

Goal: test device-callable fusion without putting it on the release-critical
path.

- Numba-only spike.
- One primitive/query pair.
- Pinned CUDA/Numba/OptiX versions.
- Correctness parity, occupancy/register report, and comparison against the
  best buffer-level zero-copy path.

### Later Backend Expansion

HIPRT, Vulkan, Apple RT, broader Embree/OptiX routes, and generated bindings
remain behind capability gates until each has route tests, toolchain matrix,
platform-specific ownership rules, and claim-boundary evidence.

## Language Binding Strategy

### Python

Python is the V4.0 product binding. It should expose RT-core operators that
accept CuPy, Numba, and PyTorch device arrays while preserving caller ownership
and stream semantics. It should use the C ABI substrate or an equivalent thin
internal boundary, but it must not bypass route capability, validation,
ownership, or result contracts.

### C

C is the substrate validation target. It remains important because it keeps the
boundary honest, but public C host examples are V4.x under the current
Python-only V4.0 scope decision.

### C++

C++ should use a header-only or tiny wrapper over the C ABI. The C ABI remains
the compatibility contract when C++ hosts are reopened in V4.x.

### Rust

Rust is the recommended first external-language proof because it is strict
about ownership and makes C ABI mistakes visible. It is V4.x under the current
Python-only V4.0 scope decision. The Rust binding should:

- generate raw FFI bindings from `rtdl.h`;
- wrap handles in RAII structs;
- use `Result<T, RtdlError>`;
- enforce non-Send/non-Sync or Send/Sync according to actual threading rules;
- include one real query example.

### Julia

Julia can use `ccall` directly. It should be a thin validation target after C
and Rust when V4.x non-Python hosts open.

### C# / Java

C# P/Invoke and Java JNI/JNA can be later binding proofs. They are not needed
to prove the Python GPU product, but the ABI should avoid patterns that make
them impossible later.

### Generated Bindings

Generated bindings are a Phase 3/V4.x deliverable only after the C ABI is
stable enough to generate against.

## SDK And Packaging Design

V4.x should graduate from source-tree staging to a reviewed SDK only when gates
pass and non-Python hosts are back in product scope. For Python-only V4.0, the
public packaging story is the Python operator package and its binary/runtime
constraints, not a general C SDK.

### Stage Layout

The staged SDK should contain:

```text
include/rtdl/rtdl.h
lib/librtdl.*
lib/pkgconfig/rtdl.pc
lib/cmake/rtdl/rtdl-config.cmake
share/rtdl/symbol_manifest.json
share/rtdl/abi_manifest.json
examples/c/*
examples/python/*
examples/rust/*
LICENSE
README.md
```

### Package Metadata

Required:

- pkg-config metadata;
- CMake config with imported target;
- runtime search path guidance;
- symbol visibility audit;
- version manifest;
- platform/toolchain matrix.

Optional later:

- Python wheel for binding package;
- Rust crate;
- system packages;
- CUDA-enabled binary bundles.

### Release Claim Boundary

V4 can say "source-tree SDK stage" when only stage/archive tests exist.
It can say "stable SDK" only after install/package and compatibility gates pass.

## Threading And Concurrency

Threading rules must be stated in the ABI documentation:

- version/status/capability functions are thread-safe;
- independent contexts may execute concurrently only after backend-specific
  tests prove it;
- shared handles require external synchronization unless documented otherwise;
- no handle may be destroyed while another thread may use it;
- last-error state is context-local and mutable;
- callbacks must not re-enter RTDL on handles being destroyed.

V4 release should include:

- independent CPU contexts concurrent route test;
- independent Embree contexts concurrent route test if Embree is exposed;
- independent OptiX contexts/streams test only if OptiX C ABI route ships;
- shared-handle misuse negative tests or explicit external-lock rule.

OptiX concurrency should be treated as a separate proof, not inferred from CUDA
stream support. Pipeline, module, program group, and shader binding table state
can behave like process-level shared state unless the implementation proves
otherwise.

## Error Handling And Diagnostics

Every public call must be diagnosable without undefined behavior.

Required diagnostics:

- status string for every status code;
- context last-error;
- unsupported capability message;
- ABI mismatch message;
- invalid dtype/layout/shape messages;
- backend library unavailable message;
- external runtime unsupported message;
- device-buffer route unsupported message.

Diagnostics are for humans. Machine behavior uses status codes and capability
queries.

Context creation failures need a diagnostic path even when no context exists.
V4 should provide either a context-less last-create-error accessor, a structured
create-status object, or an output diagnostic buffer on context creation. The
chosen form must be thread-safe enough for concurrent failed creates and must
not require a valid `rtdl_context*`.

## Performance Model

V4 performance must be reported by phase:

- context creation;
- external runtime attach;
- buffer import;
- index build;
- query execution;
- output export;
- stream synchronization;
- host/device transfer if any;
- validation/oracle.

Never compare a hot V4 query against a cold V3 Python app unless the table says
that explicitly. Never hide host staging behind "device-buffer" wording. Never
claim "zero-copy" based only on a descriptor.

## Device-Callable Fusion Track

Device-callable fusion can be explored, but not as the V4 base.

### Why It Is Not The Foundation

- OptiX callables are not free inlining.
- Register pressure and occupancy may erase wins.
- Variable-length payloads still require memory indirection.
- Toolchain compatibility is fragile.
- Triton is not naturally a per-hit OptiX callable model.
- Debugging and safety are harder than buffer-level interop.

### Acceptable Spike Scope

One spike can be allowed:

- Numba device function only;
- one primitive/query pair;
- pinned CUDA, Numba, OptiX versions;
- correctness parity;
- occupancy/register report;
- comparison against the best buffer-level zero-copy path;
- kill criterion if not faster or too brittle.

Promotion requires evidence. Until then, fusion remains experimental and V4
must keep the row/column/device-buffer route as the durable path.

## Documentation Arrangement

During implementation:

- Keep V3 user docs current and stable.
- Put V4 design and review docs under `docs/engineering/`.
- Keep archived V4 preparatory evidence under
  `docs/history/v4_preparatory_embedding/`.
- Do not move V4 SDK docs into the main user front door until the implementation
  and release gates pass.

At V4 release:

- promote the V4 SDK docs into a current user-facing path;
- move superseded V3 release-specific docs to history;
- make the front door teach V4 without forcing users through archived V3/V4 prep
  artifacts;
- keep clear "current" versus "history" separation.

## Test And Gate Matrix

### Required For V4.0 Alpha

- Python operator accepts at least one real CuPy/Numba/PyTorch device-array
  input form.
- One benchmark-valuable RT-core route is selected and mechanically tested.
- The route executes against device buffers, not only host buffers.
- Caller-stream behavior is explicit and tested or explicitly rejected.
- RTDL-owned and caller-provided output modes are both represented in the
  substrate.
- Negative tests cover invalid ABI version, null handles, invalid dtype, invalid
  shape, unsupported backend, unsupported device, unsupported route.
- Capability tests cover enum-keyed queries and unknown capability values.
- Source-tree doctor has a V4 mode distinct from V3 current validation.
- No stable SDK or true-zero-copy wording appears without evidence.

### Required For V4.0 Beta

- Pointer identity, no-host-stage transfer evidence, stream-order proof, and
  correctness parity exist for the Phase 1 Python device-array route.
- Ownership/threading contract reviewed.
- Layout audit checks `sizeof` and `offsetof`.
- Old-size descriptor compatibility test passes against new code.
- Independent-context or caller-stream concurrency rules are tested for shipped
  routes.
- Public examples demonstrate the Python GPU operator, not only C lifecycle.
- Non-Python host and SDK work is explicitly documented as V4.x unless a future
  product decision reopens it.

### Required For V4.0 Stable

- ABI/substrate version policy published.
- Cross-version compatibility test exists for supported 1.x behavior, or V4.0
  clearly ships as pre-1.0 experimental SDK.
- Python package/install/runtime story exists for at least one supported CUDA
  platform if public Python operator wording is used.
- C/C++/Rust SDK package/install story exists only if stable non-Python SDK
  wording is used.
- Every public example is mechanically tested.
- Every public doc command is mechanically covered.
- Unsupported routes fail closed.
- External review findings are documented and addressed.
- Claim boundaries are machine-tested.

### Required For Any True Zero-Copy Claim

- exact route and command;
- pointer identity evidence;
- transfer-counter or equivalent no-host-stage evidence;
- stream-order proof;
- correctness parity;
- negative host-stage regression test;
- external review.

## Proposed Implementation Milestones

### M1: V4 Design Freeze

- This document reviewed.
- Product headline accepted: RTDL as Python GPU RT-core operator.
- Python-only V4.0 scope recorded; non-Python hosts are V4.x.
- First benchmark-valuable device-array route selected:
  `fixed_radius_count_threshold_2d`, not variable-length neighbor rows.
- D1-D5 review decisions accepted and reflected in ABI, tests, and wording.
- Remaining open decisions explicitly assigned to later milestones.
- C ABI substrate inventory approved.
- Reviewer checklist accepted.

### M2: Python Device-Array Intake

- CuPy/Numba/PyTorch array metadata intake through CUDA-array-interface and/or
  DLPack.
- Caller CUDA context and stream metadata captured.
- Unsupported layouts, dtypes, devices, and streams fail closed.
- No public zero-copy wording yet.

### M3: First Python RT-Core Operator Route

- `fixed_radius_count_threshold_2d` is the first route.
- fixed-size `query_ids`, `neighbor_counts`, and `threshold_flags` device
  columns are the first output contract.
- variable-length neighbor rows and ray/triangle any-hit are later routes.
- nonzero caller CUDA streams use the native on-stream symbol and synchronize
  that stream before return; async completion is not claimed yet.
- device-buffer query execution.
- result returned as a device buffer.
- Python example uses existing host-owned device arrays.
- correctness parity and deterministic failure behavior.

### M4: Zero-Copy Evidence Packet

- pointer identity.
- no-host-stage transfer counters or equivalent instrumentation.
- stream-order proof.
- correctness parity.
- negative host-stage regression test.

### M5: C ABI Substrate Hardening

- active `0.x` header/source aligned with Python device-array route.
- D1-D5 enforced by tests.
- host AABB2 retained as control-plane/result-contract proof.
- symbol manifest, layout audit, old-size descriptor compatibility.

### M6: Non-Python Host V4.x Path

- Record the non-Python host path as V4.x.
- Keep the active C ABI internal/experimental for V4.0 product work.
- Start C then Rust proof over the proven substrate only when V4.x scope opens.

### M7: SDK Or Python Package Stage

- Python package/runtime story for the operator.
- CMake/pkg-config/archive excluded from V4.0 public scope; keep only internal
  substrate tooling required by the Python operator.

### M8: V4 Release Candidate

- docs front door prepared.
- V4 test matrix stable.
- external review complete.
- claim-boundary scan complete.
- release packet written.

## M1 Resolved Design Decisions

These decisions close the highest-priority gaps from the 2026-06-19 external
review and are part of M1 design freeze.

### D1: Result Size And Output Allocation

Decision:
Every query route supports two output modes:

1. RTDL-owned result handle, inspected through accessors and released through a
   destroy function.
2. Caller-provided output buffer with capacity, `required_count_out`, and
   `written_count_out`.

If the caller-provided buffer is too small, RTDL must not exceed capacity. It
writes the required count, writes at most capacity rows, and returns
`RTDL_STATUS_RESULT_TRUNCATED`. The caller can then allocate enough storage and
rerun a size-then-fill call. Framework-owned tensor output uses the same
caller-provided-buffer contract when capability queries allow it.

Rationale:
RTDL-owned results make early bindings simple and safe. Caller-provided output
is required for serious host embedding, preallocated arenas, and framework
tensor ownership.

Gate:
Each shipped query route has tests for RTDL-owned output, caller-provided
output, exact-fit output, and truncation with correct required-count reporting.

### D2: ABI Struct Extensibility

Decision:
Every public input descriptor starts with `size_t struct_size`. RTDL reads only
fields present within the caller-provided size. Missing trailing fields receive
documented defaults. Descriptor evolution is append-only until ABI `1.0`.

Rationale:
The V4 ABI will change during the `0.x` line. `struct_size` gives older callers
a forward-compatible path without adding `sType` / `pNext` complexity before it
is needed.

Gate:
Layout tests pin `sizeof` and `offsetof`, and compatibility tests pass
old-size descriptors into new code.

### D3: Capability Query Shape

Decision:
The stable ABI uses one enum-keyed capability query:

```c
rtdl_status rtdl_query_capability(
    const rtdl_context* context,
    const rtdl_route_desc* route,
    rtdl_capability cap,
    uint64_t* value_out);
```

New capabilities are enum values, not new exported symbols. Unknown enum values
return `RTDL_STATUS_UNSUPPORTED`.

Rationale:
V4 needs capability growth across backends, devices, routes, ownership modes,
and stream modes. One query function keeps the symbol surface stable while the
capability inventory evolves.

Gate:
The enum policy is documented, unknown values are tested, and public examples
use capability discovery before executing optional routes.

### D4: Robustness And Input Validation

Decision:
RTDL validates every descriptor before use. Invalid shape, dtype, layout,
alignment, byte count, null pointer, unsupported route, and overflow cases fail
closed with status codes. Borrowed device pointers are caller-asserted: RTDL
cannot generally verify device pointer liveness, residency, aliasing, or
producer-object lifetime.

Rationale:
Embedding moves RTDL into host processes. Bad descriptors must produce
diagnostic failures, not unchecked reads or ambiguous behavior. At the same
time, the ABI must be honest about what a library can and cannot prove about
foreign device memory.

Gate:
Negative tests cover malformed descriptors and unsupported combinations. The
ownership/threading section explicitly states caller obligations for borrowed
device pointers.

### D5: Versioning, Wording, And First Routes

Decision:
V4.0 ships as a pre-1.0 experimental SDK. Do not use "stable SDK" or "1.0 ABI"
wording until install, compatibility, and product-route gates pass. AABB2 stays
as a plumbing/control-plane route, but the first V4.0 product route is the
benchmark-valuable `fixed_radius_count_threshold_2d` device-array route:
caller-owned CUDA point columns in, prepared OptiX fixed-radius count/threshold
execution, and fixed-size CUDA output columns out.

Rationale:
AABB2 is excellent for lifecycle, layout, output, and binding proofs. It is
not enough to sell or freeze V4.0 by itself. A benchmark-valuable device route
forces the ABI and Python binding to confront result cardinality,
route-specific capabilities, stream ownership, and performance-relevant memory
behavior.

Gate:
Wording tests reject premature stable-ABI and true-zero-copy claims. The M2-M4
matrix includes the Python device-array route and evidence before design claims
graduate beyond experimental SDK.

## Remaining Open Decisions

Closed M1 scope decision:
V4.0 is Python actors only. Non-Python hosts, full public multi-language C ABI
packaging, and generated SDK bindings are V4.x unless a later product decision
reopens them.

Closed M1 route decision:
The first product route is `fixed_radius_count_threshold_2d`. It is fixed-radius
count/threshold over 2-D point columns, not variable-length neighbor-row
enumeration. The first output shape is fixed-size `query_ids`,
`neighbor_counts`, and `threshold_flags` CUDA columns.

Closed M1 backend decision:
The first native backend is OptiX. CPU/Embree routes can remain correctness and
control-plane references, but they are not the V4.0 product route.

1. Buffer rank limit:
   Is fixed rank 8 acceptable for the C ABI, or should shape/stride arrays be
   dynamically sized?

2. Allocator hooks:
   Do allocator hooks belong in V4.0, or should V4.0 only support borrowed,
   caller-provided-output, and RTDL-owned buffers?

3. Rust binding:
   When V4.x opens non-Python hosts, should Rust be in-tree as an example or a
   separate generated artifact?

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| C ABI becomes the headline again | V4.0 misses the Python GPU product | freeze Python device-array RT-core route before SDK packaging |
| ABI grows too broad | impossible to stabilize | start with one route and capability queries |
| Binding logic diverges | each language becomes a fork | bindings stay thin over C ABI |
| Device-buffer metadata mistaken for zero-copy | public overclaim | machine-readable claim flags and transfer evidence gates |
| Hidden synchronization hurts hosts | poor framework integration | stream policy and no hidden device-wide syncs |
| C++/CUDA internals leak | unstable binary boundary | symbol visibility audit and C-only header |
| App semantics enter native API | violates RTDL design | primitive/query names stay generic |
| Device fusion distracts from common case | schedule slip | fusion track is optional and gated |
| Packaging claims outrun evidence | user confusion | source-tree stage vs stable SDK wording tests |
| Thread-safety overpromised | host crashes | shared-handle external sync rule until proven |

## Acceptance Criteria

V4.0 is ready only when a reviewer can say yes to these:

1. Can a CuPy/Numba/PyTorch user call an RTDL RT-core operator on existing
   device arrays?
2. Does the shipped route run on device buffers rather than staging through a
   host-only query path?
3. Are pointer identity, no-host-stage transfer evidence, stream-order proof,
   and correctness parity documented for every zero-copy claim?
4. Are unsupported backends/routes/device buffers rejected clearly?
5. Are ownership, result, destroy, and borrowed-pointer rules unambiguous?
6. Are context and caller-stream ownership rules explicit?
7. Is every public command and Python example mechanically tested?
8. Are package/stage/install claims exactly matched to evidence?
9. Are stable SDK and true-zero-copy claims either absent or backed by exact
   evidence?
10. Does the native engine remain app-agnostic?
11. Do result routes support both RTDL-owned and caller-provided output modes?
12. Do all public descriptors use and test `struct_size` compatibility?
13. Are capability queries enum-keyed and fail-closed for unknown values?
14. Are malformed descriptors rejected before pointer use?
15. Is the Python-only V4.0 and non-Python V4.x boundary explicit?

## Suggested External Review Request

Use this message when sending the design to an outside reviewer:

```text
Please critically review docs/engineering/rtdl_v4_0_design_review_packet_2026-06-19.md.

Context:
- RTDL V3.0 is a Python-hosted RT-shaped DSL/runtime with explicit partner
  continuations and app-agnostic native backends.
- V4.0 is reframed as an RT-core operator for the Python GPU ecosystem:
  CuPy/Numba/PyTorch programs call RTDL on their own device arrays, zero-copy
  and on the caller's stream.
- V4.0 is Python actors only. Non-Python hosts, multi-language SDK packaging,
  and generated C/C++/Rust bindings are V4.x.
- The C ABI is the substrate under that product, not the product headline.
- We specifically want to avoid overclaiming stable SDK, true zero-copy,
  automatic partner selection, or broad RT-core performance.

Please focus on:
1. Does the Python device-array RT-core operator make the right V4.0 headline?
2. Is Python-only V4.0, with non-Python hosts deferred to V4.x, the right
   product boundary?
3. Is the C ABI substrate narrow enough for the Python product and future V4.x
   hosts?
4. Are ownership, lifetime, threading, and error-handling rules complete enough
   for the Python binding and future external hosts?
5. Is the device-buffer/zero-copy plan honest and testable?
6. Is the new milestone order realistic?
7. Which parts are too broad for V4.0 and should move to V4.x?
8. What evidence would you require before accepting stable SDK wording?
9. What evidence would you require before accepting true-zero-copy wording?
10. What would make this design fail in Rust, C++, Python, PyTorch/CuPy, or a
   CUDA/OptiX host?

Please return:
- P0 blockers;
- P1 design risks;
- P2 clarity improvements;
- suggested tests/gates;
- exact wording that should be forbidden until proven.
```

## Reviewer Checklist

- C ABI has no C++ leakage.
- ABI versioning and compatibility policy are believable.
- Capability queries are complete enough.
- Status/error handling is usable from the Python binding and future
  non-Python hosts.
- Buffer descriptor can represent host and device arrays without ambiguity.
- Ownership modes cover borrowed, callback-owned, and RTDL-owned buffers.
- Stream/context semantics are not hand-waved.
- DLPack and CUDA-array-interface semantics distinguish metadata from execution.
- Python GPU device-array route is the first product proof.
- Zero-copy claims require evidence.
- Threading rules avoid overpromising.
- Packaging language distinguishes source-tree stage, prefix stage, archive,
  installed SDK, generated binding, and stable ABI.
- Device-callable fusion is isolated from the release-critical path.
- V4 docs can eventually become the current user front door without dragging
  old V3/V4-prep material into user learning.

## Files Reviewers Should Inspect

- `docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md`
- `docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md`
- `docs/history/v4_preparatory_embedding/v3_0_c_abi_stability_policy.md`
- `docs/history/v4_preparatory_embedding/v3_0_c_abi_ownership_threading_contract.md`
- `docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md`
- `docs/history/v4_preparatory_embedding/v3_0_zero_copy_interop_contract.md`
- `docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md`
- `docs/history/v4_preparatory_embedding/staging/include/rtdl/rtdl.h`
- `src/native/rtdl_c_api.cpp`
- `scripts/run_test_matrix.py`
- `Makefile`

## Recommended First Implementation Step

Do not begin with device fusion or broad language bindings.

Begin with the Python GPU operator proof:

1. record the Python-only V4.0 scope and V4.x non-Python boundary;
2. select the first benchmark-valuable RT-core route;
3. accept CuPy/Numba/PyTorch device arrays through CUDA-array-interface and/or
   DLPack;
4. run on the caller's CUDA context and stream where supported;
5. return a device result buffer the host can wrap;
6. collect pointer identity, no-host-stage, stream-order, and correctness
   evidence;
7. harden the C ABI substrate underneath with D1-D5 and keep host AABB2 as a
   control-plane/result-contract proof.

The product proof is the power move. The C ABI is still important, but it
serves the Python GPU route first and expands outward in V4.x only when a new
product decision justifies it.
