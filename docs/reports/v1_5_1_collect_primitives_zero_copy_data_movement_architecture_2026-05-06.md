# RTDL v1.5.1 Collect Primitives, Zero-Copy, and Bulk Data Movement Architecture - 2026-05-06

## Verdict

Collect primitives and zero-copy mechanisms solve different layers of the RTDL
architecture.

`COLLECT_K_BOUNDED` is a language/runtime primitive. It answers: what should
RTDL produce when traversal finds bounded row-like candidate output?

Zero-copy or reduced-copy buffer architecture is a data-movement mechanism. It
answers: how should Python, RTDL, native engines, CPU memory, and GPU memory
share large inputs and outputs without repeated bulk copies?

They are complementary. v1.5.1 should first make `COLLECT_K_BOUNDED`
semantically app-generic and fail-closed. Then the buffer contract can be used
to reduce unnecessary Python/native and host/device copies.

## Architectural Context

The current roadmap separates two architecture tracks:

- `v1.5.1-v1.5.10` and `v1.6`: finish Python+RTDL.
- `v1.7-v2.0`: build Python+partner+RTDL.

The core rule across both tracks is that stable Embree and NVIDIA RT engine
paths should be app-generic. The engine should know RTDL primitives, buffer
contracts, traversal contracts, and backend capabilities. It should not know
Jaccard, polygon overlay, database semantics, or other app-specific business
logic in stable primitive paths.

Python remains the app/control/lowering layer in the first track:

```text
Python app/control layer
    -> RTDL primitive and buffer contract
        -> app-generic Embree or OptiX engine path
```

The later partner track adds explicit partner systems for non-RT computation:

```text
Python app/control layer
    -> partner compute/data layer for app-specific non-RT logic
    -> RTDL primitive and buffer contract
        -> app-generic Embree or OptiX engine path
```

RTDL should not become a magic Python compiler or a general CUDA graph compiler.
Partner systems should connect through explicit contracts such as tensor or
buffer handoff.

## What Collect Primitives Solve

Existing stable primitives mostly return small scalar or fixed-size outputs:

```text
ANY_HIT                 -> bool-like result
COUNT_HITS              -> integer count
REDUCE_FLOAT(MIN/MAX/SUM) -> scalar float summary
REDUCE_INT(COUNT/SUM)   -> scalar integer summary
```

These are relatively easy to keep app-generic because each query or group
returns one compact value.

`COLLECT_K_BOUNDED` is different. It returns bounded row-like content:

```text
query_id -> up to K candidate rows
```

For example, a candidate row might be:

```text
(left_polygon_id, right_polygon_id)
```

But the primitive itself should not be polygon-specific. The app-generic shape
is:

```text
candidate_id_rows: int64[valid_count, row_width]
capacity: K
valid_count: number of emitted candidate rows
overflowed: false if complete, otherwise fail closed
```

`K` is owned by the caller-facing RTDL invocation, not by the native engine. In
v1.5.1, `K` should be treated as a per-call or per-batch capacity selected by
the Python+RTDL layer. If a reusable result buffer is used, changing `K` between
calls requires either a buffer with sufficient existing capacity or an explicit
buffer reallocation/rebind step. Native Embree and OptiX paths should receive
`K` as an explicit capacity argument and must not silently choose a smaller
capacity.

`row_width` is part of the primitive invocation contract. It may vary across
primitive uses, but it must be fixed for one result buffer and one native call.
For polygon-pair candidate rows, `row_width=2`. For one-dimensional candidate
IDs, `row_width=1`. A backend or wrapper must reject rows whose width does not
match the declared `row_width`.

The canonical ordering rule for v1.5.1 is stable lexicographic ordering by the
complete candidate-id row after candidate discovery. Backend traversal order is
not a public result-order contract. If a backend naturally emits rows in a
different order, the wrapper or native path must canonicalize before parity
comparison or before exposing the stable primitive result.

The duplicate rule for v1.5.1 is deduplicate identical candidate-id rows before
capacity checking. For a `row_width=2` polygon-pair result, duplicate means the
same `(left_id, right_id)` row. For a `row_width=1` result, duplicate means the
same candidate ID. Future primitives with richer row schemas must define the
row identity key explicitly before promotion.

The semantic problems solved by `COLLECT_K_BOUNDED` are:

- capacity definition;
- deterministic ordering;
- duplicate handling;
- exact `K` behavior;
- zero-result behavior;
- overflow behavior;
- fail-closed behavior before downstream score/reduction work;
- backend parity when Embree and OptiX are both claimed;
- stable result metadata independent of app names.

This is a language/runtime contract problem before it is a performance problem.

## What Zero-Copy Solves

Zero-copy is not a primitive. It is a memory ownership and interoperability
strategy.

Without a disciplined buffer contract, large workloads can suffer repeated
copies:

```text
Python objects
    -> temporary RTDL host buffers
        -> native engine input buffers
            -> device buffers for OptiX
                -> device result buffers
                    -> native host result buffers
                        -> Python objects
```

That is painful for row-returning workloads because output volume can be much
larger than scalar summaries.

The fundamental solution is not merely a faster wrapper. It is a stable buffer
ownership model:

```text
SceneBuffer
QueryBuffer
ResultBuffer
```

Each buffer should define:

```text
pointer or backend handle
dtype
shape
stride/layout
device: cpu | cuda
lifetime owner
mutability
capacity
valid count
overflow/fail-closed status
```

With that model, RTDL can fill preallocated buffers directly where possible
instead of constructing nested Python lists or repeatedly repacking data.

## Three Copy Boundaries

There are three distinct copy boundaries. They should not be confused.

### Python To RTDL

This boundary is about avoiding Python object materialization and conversion
overhead.

Bad hot-path shape:

```text
list[tuple[int, int]] -> convert every call -> native buffer
```

Better hot-path shape:

```text
typed contiguous buffer -> pointer/shape/dtype/lifetime contract
```

For CPU/Embree, this can begin with NumPy-compatible contiguous memory,
memoryviews, or equivalent typed host buffers. Python still controls the app,
but Python should not build millions of tiny objects for hot-path result rows.

### RTDL To Native Engine

This boundary is about avoiding repeated repacking between RTDL's logical
layout and the backend ABI.

Bad shape:

```text
RTDL canonical rows -> backend-specific rows -> run -> backend-specific rows -> RTDL rows
```

Better shape:

```text
RTDL buffer contract is already close to backend ABI
native engine reads/writes the agreed layout
```

For v1.5.1, this is why the app-generic row-buffer contract matters. Embree and
OptiX can keep backend-specific internals, but their stable primitive result
metadata should converge on one RTDL contract.

### CPU To GPU

This is the hardest boundary. If the data begins in CPU memory, OptiX cannot
use it on RT cores without getting it into GPU-accessible memory somehow.

So true zero-copy is only valid when data is already GPU-resident or externally
shareable through a supported device-memory mechanism.

Practical near-term OptiX goals are often reduced-copy or reduced-transfer:

```text
host pinned/staging buffer -> persistent device buffer -> repeated query reuse
```

or:

```text
prepared scene/query/result device buffers reused across batches
```

That is valuable, but it should not be called true zero-copy unless the measured
memory ownership and access path justify that exact wording.

CUDA unified memory or managed memory must also be named explicitly if used. It
is not automatically the same as true zero-copy; it may still migrate pages or
hide transfers.

## How This Solves Bulk Content Copy

Bulk copy is fundamentally solved by making result production buffer-oriented
rather than object-oriented.

For `COLLECT_K_BOUNDED`, the preferred shape is:

```text
candidate_id_rows: int64[K, row_width]
valid_count: int64
overflowed: bool
```

The primitive should fill that buffer under a fail-closed rule:

```text
if actual_count <= K:
    fill rows
    valid_count = actual_count
    overflowed = false
else:
    do not return partial semantic result
    overflowed = true
    raise or fail closed
```

This prevents silent truncation and prevents downstream app logic from using an
incomplete candidate set.

For CPU/Embree, the result buffer can be host memory with direct Python-visible
typed access.

For GPU/OptiX, the result buffer may be device memory, host-pinned staging
memory, or copied-back host memory depending on the release stage. The key is
that the contract must make the copy behavior explicit:

```text
true zero-copy
reduced-copy
reused persistent device buffer
ordinary copyback
```

Only exact measured paths should receive public performance wording.

## v1.5.1 Implication

v1.5.1 should not try to solve all zero-copy and partner integration at once.

The correct first step is:

```text
Promote COLLECT_K_BOUNDED as an app-generic primitive candidate,
with fail-closed overflow behavior and a stable bounded row-buffer shape.
```

Then:

```text
Make Embree and OptiX return or validate against that same contract.
```

Then:

```text
Measure exact copy counts, transfer costs, and performance on real workloads.
```

Only after that should the project decide what wording is allowed:

```text
no copy reduction claim
reduced Python/native copy claim
reused GPU buffer claim
true zero-copy claim
```

## Partner Track Implication

The partner track should start only after Python+RTDL has a stable primitive and
buffer contract.

The current consensus baseline for v1.7 is a DLPack-compatible tensor handoff,
with PyTorch or CuPy as the first practical consumer. This is a consensus
direction recorded in
`docs/reports/three_ai_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_consensus_2026-05-06.md`,
not an implemented capability claim. It remains subject to later partner-track
design, conformance tests, and measurement.

In the partner architecture, RTDL should produce candidate buffers that partner
systems can consume without converting them into Python object lists first.

## Claim Boundaries

This report is an architecture explanation only.

It does not claim:

- public `COLLECT_K_BOUNDED` promotion is complete;
- native Embree/OptiX parity is complete;
- any whole-app speedup;
- broad RTX/GPU acceleration;
- package-install support;
- true zero-copy;
- partner integration is implemented.

The allowed conclusion is narrower:

```text
COLLECT_K_BOUNDED is the semantic primitive for bounded row output.
Zero-copy/reduced-copy is the memory architecture for moving that output cheaply.
The common foundation is an explicit app-generic buffer contract.
```

## Recommendation

Use this architecture as the v1.5.1 implementation guide:

- keep the primitive app-generic;
- keep overflow fail-closed;
- make result buffers explicit;
- preserve old app-facing compatibility fields only as transition surfaces;
- measure copy/transfer behavior before making any public performance or
  zero-copy claim;
- defer partner-system semantics to v1.7-v2.0.
