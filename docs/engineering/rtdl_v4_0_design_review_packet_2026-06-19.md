# RTDL V4.0 Design Review Packet

Status: engineering design packet for study and external review.
Date: 2026-06-19.
Audience: RTDL maintainers, external systems reviewers, language-binding
reviewers, CUDA/OptiX reviewers, and framework-interop reviewers.

This document defines the intended V4.0 architecture before implementation.
It is not a release note, stable ABI promise, package-install promise, public
speedup claim, or true-zero-copy claim. It is the design target and review
contract for making RTDL embeddable.

## One-Line Goal

V4.0 changes RTDL from a Python-hosted runtime that owns the loop into an
embeddable library that a host language or framework can call while the host
owns the loop.

```text
V3.0: Python + RTDL owns the execution loop; partners are explicit guests.
V4.0: A host language/framework owns the execution loop; RTDL is the embedded extension.
```

## Executive Summary

V4.0 should be built around a stable boundary, not around spectacular fusion
first. The foundation is:

- a narrow C ABI with opaque handles, status codes, versioning, capability
  queries, explicit ownership, last-error diagnostics, and no C++ types across
  the boundary;
- external runtime ownership, where the host can provide the device, context,
  stream, allocator policy, and synchronization expectations;
- a neutral buffer descriptor that can represent host arrays, CUDA buffers,
  `__cuda_array_interface__`, and DLPack-style tensors;
- real device-buffer query routes, starting with one small route and expanding
  only after correctness, lifetime, stream, and transfer evidence are present;
- thin bindings over the C ABI for Python, C, Rust, Julia, C#, Java, and other
  hosts;
- staged SDK packaging with CMake and pkg-config, promoted to stable only
  after cross-version, cross-platform, non-Python client, and packaging gates
  pass.

Optional device-callable fusion remains an advanced V4 track. It should not
gate V4.0. It must be treated as a falsifiable experiment with register,
occupancy, correctness, and maintenance evidence before it is promoted.

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
- D5: V4.0 ships as a pre-1.0 experimental SDK until a real external host
  drives a device-buffer route end to end; AABB2 proves plumbing, and a second
  benchmark-valuable route shapes the ABI before stable wording.

The acceptance criteria and milestones below are now read with those decisions
as mandatory gates, not optional review notes.

## Why V4 Exists

V3.0 closed the current benchmark-route system. It teaches users to write
Python application code around app-agnostic RTDL primitives, prepared execution,
backend choice, and explicit partner continuations. That is valuable, but it
still makes Python the normal host.

V4.0 exists because external programs need RTDL as a library:

- a C++ application wants RTDL traversal without importing Python;
- a Rust service wants to build an index and run queries through FFI;
- a Julia notebook wants a thin binding over a stable C surface;
- a PyTorch, JAX, CuPy, or Numba program wants to pass existing device buffers
  to RTDL without staging them through host memory;
- a larger runtime wants RTDL work scheduled on its own CUDA context and
  stream, with clear synchronization and lifetime rules.

The V4 design question is therefore not "how do we expose every RTDL internal?"
It is "what is the smallest stable boundary that lets other hosts use RTDL
without rewriting the engine or fighting their runtime?"

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
   RTDL must fit inside C, C++, Rust, Julia, C#, Java, Python, and framework
   runtimes without assuming Python orchestration.

2. C ABI first.
   Every stable binding sits on a narrow C ABI. No public C++ ABI, exceptions,
   STL containers, templates, CUDA C++ classes, or OptiX internals cross the
   stable boundary.

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
    interop and stable embedding solve the common case first.

## Non-Goals For V4.0

- No stable C++ public ABI.
- No promise that every V3 Python example becomes a C ABI route.
- No automatic partner/backend selection.
- No broad "RTDL accelerates arbitrary PyTorch/CuPy/Numba code" claim.
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
    C, Python, Rust, Julia, C#, Java; DLPack/CUDA-array adapters

L3  Stable C ABI
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

### C Host

A C program can:

1. load `librtdl`;
2. check ABI compatibility;
3. create a context;
4. import host buffers;
5. build an AABB2 index;
6. execute an overlap query;
7. export a result buffer;
8. destroy every handle deterministically.

This is the first stable control-plane story.

### Rust Host

A Rust program can generate bindings from `rtdl.h`, link to `librtdl`, and run
the same route without Python. It owns safety wrappers around raw handles.

This is the first "not just C" proof for the ABI.

### Python Binding

Python can use a thin `ctypes`, `cffi`, or generated binding layer over the same
C ABI. This binding must not bypass the C ABI through private C++/Python
internals.

### Framework Tensor Host

A CuPy/PyTorch/JAX/Numba host can pass a device buffer descriptor into RTDL.
The first milestone may import/export metadata only, but the V4 release target
requires at least one real device-buffer query route with stream and ownership
evidence.

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

This mode is the easiest binding target and the safest first C/Rust/Python
example because RTDL owns allocation and lifetime.

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

## Backend Roadmap

V4 should not expose every backend through the C ABI at once.

### Phase 1: CPU Host Route

Goal: prove the stable C ABI and packaging story.

- CPU backend.
- Host AABB2 overlap.
- C and Rust clients.
- CMake/pkg-config stage.
- symbol manifest.
- layout audit.
- negative tests.

### Phase 2: Embree Host Route

Goal: prove a native backend can be embedded without Python.

- Embree-backed AABB2 or segment/triangle route.
- same result contract as CPU where possible.
- capability query says exactly when Embree is available.
- failure when library is absent is deterministic.

### Phase 3: OptiX Host Route

Goal: prove GPU RT backend execution through the C ABI.

- OptiX-backed route with host input staging explicitly reported, or
  device-buffer input if Phase 4 is ready.
- no RT-core speedup wording unless separately reviewed.
- CUDA/OptiX errors converted to `rtdl_status`.

### Phase 4: CUDA Device-Buffer Route

Goal: prove the host can pass device buffers to RTDL.

- one primitive/query pair only.
- caller-provided CUDA stream if supported.
- explicit sync behavior.
- correctness parity.
- transfer evidence.

### Phase 5: Other Backends

HIPRT, Vulkan, and Apple RT should remain behind capability gates until each has
its own C ABI route tests, toolchain matrix, and platform-specific ownership
rules.

## Language Binding Strategy

### C

C is the ground truth. Every release must include C examples and tests.

### C++

C++ should use a header-only or tiny wrapper over the C ABI. The C ABI remains
the compatibility contract.

### Python

Python bindings should use the C ABI. Python may expose convenience classes,
but they should own only handle lifetime, type conversion, and buffer protocol
bridges.

### Rust

Rust is the recommended first external-language proof because it is strict
about ownership and makes C ABI mistakes visible. The Rust binding should:

- generate raw FFI bindings from `rtdl.h`;
- wrap handles in RAII structs;
- use `Result<T, RtdlError>`;
- enforce non-Send/non-Sync or Send/Sync according to actual threading rules;
- include one real query example.

### Julia

Julia can use `ccall` directly. It should be a thin validation target after C
and Rust.

### C# / Java

C# P/Invoke and Java JNI/JNA can be later binding proofs. They are not needed
to prove V4.0, but the ABI must avoid patterns that make them impossible.

### Generated Bindings

Generated bindings are a V4 deliverable only after the C ABI is stable enough
to generate against. V4.0 can ship handwritten thin examples first; generated
bindings can be V4.x if needed.

## SDK And Packaging Design

V4 should graduate from source-tree staging to a reviewed SDK only when gates
pass.

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

- C header compiles as C11 and C++17.
- Shared library builds on Linux.
- Symbol manifest generated and checked.
- C client validates version/status/context lifecycle.
- C client validates one host query route.
- C client validates RTDL-owned and caller-provided result output modes.
- Python `ctypes` validates lifecycle and one host query route.
- Negative tests cover invalid ABI version, null handles, invalid dtype, invalid
  shape, unsupported backend, unsupported device, unsupported route.
- Capability tests cover enum-keyed queries and unknown capability values.
- Source-tree doctor has a V4 mode distinct from V3 current validation.

### Required For V4.0 Beta

- CMake and pkg-config prefix stage validated.
- Archive extraction and external consumer validated.
- Rust binding proof validates one real query route.
- Ownership/threading contract reviewed.
- Layout audit checks `sizeof` and `offsetof`.
- Old-size descriptor compatibility test passes against new code.
- Independent-context concurrency tested for shipped routes.
- Embree or OptiX route implemented through C ABI, or explicitly excluded from
  V4.0 stable surface.

### Required For V4.0 Stable

- ABI version policy published.
- Cross-version compatibility test exists for supported 1.x behavior, or V4.0
  clearly ships as pre-1.0 experimental SDK.
- Package/install story exists for at least one supported platform if stable SDK
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
- D1-D5 review decisions accepted and reflected in ABI, tests, and wording.
- Remaining open decisions explicitly assigned to later milestones.
- C ABI route inventory approved.
- Reviewer checklist accepted.

### M2: C ABI 0.2 Control Plane

- Clean `rtdl.h` promoted from archive into an active V4 development area.
- C lifecycle, status, version, last-error, capability, buffer lifecycle.
- symbol manifest and layout audit.

### M3: First Real Query Route

- host AABB2 overlap through CPU.
- C and Python examples.
- deterministic rows.
- RTDL-owned and caller-provided result modes.
- exact-fit and truncation output tests.
- negative tests.

### M4: SDK Stage

- prefix stage.
- CMake config.
- pkg-config.
- archive extraction.
- direct-link and dynamic-load examples.

### M5: First Non-Python Binding Proof

- Rust binding over C ABI.
- one query route.
- ownership-safe wrapper.

### M6: First Native Backend Route

- Embree or OptiX through C ABI.
- capability and failure behavior.
- same-contract comparison.
- second benchmark-valuable ABI-shaping route selected or implemented, such as
  fixed-radius neighbors or ray/triangle any-hit.

### M7: First Device-Buffer Route

- CUDA descriptor to actual query execution for one route.
- stream policy.
- transfer evidence.

### M8: V4 Release Candidate

- docs front door prepared.
- V4 test matrix stable.
- external review complete.
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
wording until install, compatibility, and external-host gates pass. AABB2 stays
as the first plumbing route, but the same milestone window must include a
second benchmark-valuable ABI-shaping route, such as fixed-radius neighbors or
ray/triangle any-hit.

Rationale:
AABB2 is excellent for lifecycle, layout, output, packaging, and binding
proofs. It is not enough to freeze a durable ABI by itself. A second route
forces the ABI to confront result cardinality, route-specific capabilities,
and performance-relevant memory behavior.

Gate:
Wording tests reject premature stable-ABI claims. The M3-M6 matrix includes
the second route before design claims graduate beyond experimental SDK.

## Remaining Open Decisions

1. First native backend:
   Embree first for lower platform risk, or OptiX first for V4 device-context
   motivation?

2. Buffer rank limit:
   Is fixed rank 8 acceptable for the C ABI, or should shape/stride arrays be
   dynamically sized?

3. Allocator hooks:
   Do allocator hooks belong in V4.0, or should V4.0 only support borrowed,
   caller-provided-output, and RTDL-owned buffers?

4. Rust binding:
   Should Rust be in-tree as an example, or a separate generated artifact?

## Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
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

1. Can a non-Python C client run a real query through the public ABI?
2. Can at least one non-C host binding run the same query without private
   internals?
3. Are unsupported backends/routes/device buffers rejected clearly?
4. Are ownership and destroy rules unambiguous?
5. Are context and stream ownership rules explicit?
6. Is every public command tested?
7. Is the ABI symbol set versioned and audited?
8. Are package/stage/install claims exactly matched to evidence?
9. Are true-zero-copy claims either absent or backed by exact evidence?
10. Does the native engine remain app-agnostic?
11. Do result routes support both RTDL-owned and caller-provided output modes?
12. Do all public descriptors use and test `struct_size` compatibility?
13. Are capability queries enum-keyed and fail-closed for unknown values?
14. Are malformed descriptors rejected before pointer use?
15. Is V4.0 wording still pre-1.0 experimental until external-host gates pass?

## Suggested External Review Request

Use this message when sending the design to an outside reviewer:

```text
Please critically review docs/engineering/rtdl_v4_0_design_review_packet_2026-06-19.md.

Context:
- RTDL V3.0 is a Python-hosted RT-shaped DSL/runtime with explicit partner
  continuations and app-agnostic native backends.
- V4.0 is intended to make RTDL embeddable in host languages/frameworks through
  a C ABI, neutral buffer interop, staged SDK packaging, and eventually real
  device-buffer routes.
- We specifically want to avoid overclaiming stable SDK, true zero-copy,
  automatic partner selection, or broad RT-core performance.

Please focus on:
1. Is the C ABI boundary narrow enough to stabilize?
2. Are ownership, lifetime, threading, and error-handling rules complete enough
   for external hosts?
3. Is the device-buffer/zero-copy plan honest and testable?
4. Is the milestone order realistic?
5. Which parts are too broad for V4.0 and should move to V4.x?
6. What evidence would you require before accepting stable SDK wording?
7. What evidence would you require before accepting true-zero-copy wording?
8. What would make this design fail in Rust, C++, Python, PyTorch/CuPy, or a
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
- Status/error handling is usable from non-Python hosts.
- Buffer descriptor can represent host and device arrays without ambiguity.
- Ownership modes cover borrowed, callback-owned, and RTDL-owned buffers.
- Stream/context semantics are not hand-waved.
- DLPack and CUDA-array-interface semantics distinguish metadata from execution.
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

Begin with an active V4 C ABI 0.2 branch:

1. promote the archived draft header into an active V4 development location;
2. update the version and symbol manifest;
3. make the host AABB2 route clean and boring;
4. add C and Python examples;
5. add a Rust binding proof;
6. keep every unsupported route fail-closed;
7. run this design through external review before expanding to device buffers.

The boring boundary is the power move. Once it is stable, every language and
framework gets a clean doorway into RTDL.
