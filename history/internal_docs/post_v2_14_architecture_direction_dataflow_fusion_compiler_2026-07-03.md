# Post-v2.14 Architecture Direction: Data-Flow Fusion Compiler

Date: 2026-07-03

Status: `architecture_direction__not_implementation_authorization`

## Why This Document Exists

The RayJoin reproduction and Goal4886/4887 discussion exposed the real
architectural gap.

The problem is not merely:

```text
RTDL lacks callbacks.
```

That is only a symptom.

The deeper distinction is:

```text
OptiX lets user computation run inside traversal kernels.
RTDL currently places most user computation after traversal, on materialized rows.
```

This difference creates two linked gaps:

1. **Expression gap**: users cannot inject custom per-hit logic into traversal.
2. **Fusion/performance gap**: traversal results must cross a boundary before
   user continuation can run.

The Goal4886 performance boundary made this visible:

```text
RTDL+Numba v2 core query compute: 18.880 s
AuthorPatch core query compute:   0.0421 s
```

The gap is not solved by a nicer wrapper. It requires a programming-model and
execution-model answer.

## Core Distinction

### OptiX Model

OptiX exposes programmable shader slots:

- any-hit;
- closest-hit;
- miss;
- callable programs;
- payload/register logic.

User code runs inside the traversal event stream. In effect:

```text
traversal + user computation = one fused native kernel system
```

This gives maximum performance and maximum low-level control, at the cost of
forcing the user into CUDA/C++/OptiX programming.

### Current RTDL Model

RTDL exposes fixed primitives such as:

- LSI;
- directed point-location / PIP;
- count/threshold-style fixed kernels where they already exist.

For most custom logic:

```text
traversal -> rows -> Python / Numba / CuPy continuation
```

User computation usually runs outside traversal.

Important precision:

RTDL is not completely traversal-external. RTDL already has some fixed,
closed-form in-kernel behavior, such as count/threshold-style primitives.

The real distinction is:

```text
RTDL currently has fixed, team-authored in-kernel behaviors.
OptiX has open, user-authored in-kernel behaviors.
```

## The Architectural Answer

RTDL should not simply expose raw callbacks and become a Python wrapper around
OptiX.

The desired direction is:

```text
Users write data-flow programs.
RTDL compiles recognized data-flow stages into traversal when safe.
Unfused stages run as explicit partner continuations.
```

This preserves RTDL's identity as a language/runtime while attacking the fusion
gap.

The strategic center is therefore:

```text
ITRE/data-flow -> traversal/continuation compiler
```

or more concretely:

```text
WHAT: user writes relational / spatial / reduction data flow.
WHERE/HOW: RTDL decides whether the stage becomes:
  - an in-traversal fused operator;
  - a device-resident continuation;
  - a partner continuation;
  - a host fallback.
```

This is the same class of idea as:

- database operator pushdown;
- Postgres LLVM/JIT expression compilation;
- Halide schedule separation;
- Triton-style data-flow kernels;
- OS syscall vs eBPF-style in-kernel computation.

RTDL's moat is not "we expose more OptiX knobs." RTDL's moat is:

```text
clean data-flow program + compiler-controlled fusion
```

## Attack Point 1: Programming Model And Compiler

This is the deepest attack point.

### Do Not Expose Raw Callback As The Main Model

Raw callback support would make RTDL look like:

```text
Python API -> user writes OptiX-ish shader callback
```

That would weaken the language identity and push users back into low-level GPU
programming.

Raw callback may exist later as an expert escape hatch, but it should not be
the main V-next programming model.

### Preferred Model: Data-Flow Reduce / Continuation

Users should write operations such as:

```python
neighbors = scene.traverse(query)
score = neighbors.reduce(sum_weighted_distance)
selected = neighbors.filter(predicate).topk(k)
```

The user describes the data-flow. RTDL decides:

- `sum`, `count`, `min`, `max`, `threshold`, `topk`, `knn`, simple masks:
  fuse into traversal where supported;
- custom but structured reduce:
  compile through Numba/CuPy/Triton-style partner path;
- unsupported logic:
  run downstream with explicit materialization and honest phase accounting.

### Tiered Fusion Model

Tier 1: fixed public primitives

```text
LSI, PIP, count, threshold, nearest candidate, etc.
```

Tier 2: recognized operator pushdown

```text
sum/count/min/max/threshold/knn/topk/filter/compact
```

RTDL owns fused kernels for these generic patterns.

Tier 3: structured user continuation

```text
Numba/CuPy/Triton user function over RTDL row buffers
```

The compiler or runtime may keep this device-resident when possible. It is not
automatically in-traversal unless a reviewed mechanism exists.

Tier 4: expert raw callback escape hatch

```text
possible future feature, not default model, not required for v2.14 recovery
```

## Attack Point 2: System Implementation

This is the near-term, safer layer.

For stages that cannot yet fuse into traversal, make the boundary cheap:

- prepared sessions;
- device-resident row buffers;
- stable row-buffer ABI;
- same-stream execution;
- no host materialization unless requested;
- count-only / mask-only paths that avoid producing unused rows;
- explicit partner continuation over RTDL-managed buffers;
- phase and materialization accounting.

This does not close a 448x kernel gap by itself. It can, however, remove the
avoidable part:

```text
Python orchestration
host materialization
row conversion
repeated load/pack
unnecessary output construction
```

Goal4888 exists because this avoidable part must be measured before promising a
performance target.

## Attack Point 3: Choose The Right Battlefield

RTDL should not claim it will beat a hand-fused OptiX kernel on a single narrow
hot path without doing comparable fusion.

RTDL's structural strengths are different:

1. **Multi-stage spatial pipelines**

   Users can compose traversal, filtering, reduction, grouping, and partner
   computation without writing a giant C++/CUDA/OptiX application.

2. **Heavy continuation work**

   Numba, CuPy, PyTorch, or other partners can own non-RT computation in a way
   that is much easier than wiring those frameworks into raw OptiX C++.

3. **Portability**

   The same data-flow program can target OptiX, CPU/reference, and potentially
   other backends.

4. **Development speed and correctness discipline**

   Python-level data-flow plus explicit correctness gates can make complex
   spatial programs easier to build and audit.

5. **Compiler-selected fusion**

   As recognized operators grow, the same user program can get faster without
   forcing the user to rewrite the app as shader code.

## Relationship To RayJoin

RayJoin is an exam, not the product model.

From RayJoin, RTDL should learn:

- planar-map LSI;
- directed point-location / PIP;
- row-buffer schemas;
- midpoint / candidate construction as generic data-flow;
- grouping/compaction/skip-mask as generic continuation;
- prepared sessions;
- phase accounting.

RTDL should not learn:

- a `rayjoin_fast()` primitive;
- output-chain semantics in core;
- AuthorOfficial comparator behavior as a language feature;
- a hidden native path keyed to Section 5.7.

The correct direction is:

```text
RayJoin app = public generic RTDL primitives + user/app data-flow + partner continuation
```

not:

```text
RayJoin app = private bundled helper or hidden core shortcut
```

## Relationship To Goal4887 And Goal4888

Goal4887 tried to jump from the correct direction to implementation with an
unsupported performance target.

Claude correctly blocked it because:

```text
RTDL+Numba v2 query+output:       20.920 s
RTDL+Numba v2 core query compute: 18.880 s
Goal4887 target query+output:      3-8 s
```

The plan did not prove that the `18.880 s` core bucket was removable by
prepared/fused continuation.

Goal4888 is therefore the required measurement gate:

```text
decompose 18.880 s -> classify bottleneck -> rewrite implementation goal
```

If the core bucket is native RT traversal dominated, then:

```text
prepared sessions and partner continuation are still good engineering,
but they are not sufficient to reach 3-8 s hot query+output.
```

If the bucket is host/materialization/Python dominated, then:

```text
prepared sessions + row buffers + formal partner continuation become a credible
performance path.
```

## Design Principles

1. **Data-flow first**

   Users should write what they want computed, not where each register lives.

2. **Compiler-controlled fusion**

   Fusion is an engine/compiler decision with evidence, not an app-specific
   patch.

3. **No hidden app identity**

   Generic primitives may support RayJoin-like programs. RTDL core must not
   contain RayJoin-specific public semantics.

4. **Explicit partner choice**

   Numba/CuPy/etc. are chosen by the user or app, never secretly by the engine.

5. **Honest phase accounting**

   Every claim separates:

   - cold load/pack;
   - prepared hot path;
   - RT traversal;
   - row materialization;
   - partner continuation;
   - output writing.

6. **Fallback and correctness parity**

   Every new fused or partner route needs a reference path and a parity gate.

7. **Do not overpromise hot-path parity**

   Beating a hand-fused OptiX kernel requires comparable fusion. Prepared
   sessions and Numba continuation alone may not be enough.

## Implementation Direction After Goal4888

Only after Goal4888 classifies the bottleneck should implementation begin.

Possible paths:

### Path A: Materialization/Python Dominated

Proceed with:

- prepared planar-map session;
- row-buffer ABI;
- formal Numba partner continuation;
- device-resident continuation where possible;
- materialization-aware pipeline.

Expected target can be based on measured removable cost.

### Path B: Native RT Traversal Dominated

Do not promise continuation-only speedups.

Choose between:

- generic native primitive/kernel improvement;
- recognized operator pushdown into traversal;
- algorithmic candidate pruning;
- a narrower engineering-hygiene goal with no speed promise.

### Path C: Mixed

Split the work:

- near-term: remove measured host/materialization/Python costs;
- longer-term: design generic operator pushdown for the native-dominated part.

## Non-Authorization

This document does not authorize:

- implementing Goal4887;
- changing `src/rtdsl/**` or `src/native/**`;
- adding raw callback support;
- adding RayJoin-specific runtime APIs;
- public release claims;
- hot-path speedup claims;
- treating V3/V4 experimental work as a current release surface.

It is a direction document only.

## Summary

The root issue is:

```text
user computation outside traversal vs inside traversal
```

The right RTDL answer is not:

```text
become a Python wrapper for raw OptiX callbacks
```

The right RTDL answer is:

```text
users write data-flow;
RTDL compiles/pushes recognized computation into traversal;
unfused stages run through explicit, measured partner continuation.
```

That compiler boundary is the real post-v2.14 architecture direction.
