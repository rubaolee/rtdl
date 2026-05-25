# RTDL IR And Lowering

This page explains the current compiler/runtime plan model behind the public
RTDL DSL. It is for readers who want to understand what sits between a Python
kernel and a backend execution path.

## Current Pipeline

The current path is:

```text
Python RTDL kernel
  -> CompiledKernel
  -> RTExecutionPlan
  -> backend runtime or generated backend artifacts
  -> emitted rows or compact/native continuation output
```

The user-facing kernel shape remains:

```text
input -> traverse -> refine -> emit
```

The implementation records that shape in two main internal objects:

- `CompiledKernel`: the parsed/validated kernel-level representation.
- `RTExecutionPlan`: the backend-plan representation used by lowering,
  schema validation, and backend/codegen paths.

The current plan schema id is:

```text
https://rtdl.dev/schemas/rtdl-plan-v1alpha1.json
```

## What `CompiledKernel` Contains

`CompiledKernel` records the language-level kernel facts:

- kernel name
- requested DSL backend spelling
- precision policy
- input declarations and roles
- candidate set from `rt.traverse(...)`
- predicate from `rt.refine(...)`
- emitted field names from `rt.emit(...)`
- a human-readable lowering plan

This is still close to the authored DSL. It is useful for validation and for
explaining what the user wrote.

## What `RTExecutionPlan` Contains

`RTExecutionPlan` is the backend-plan shape. It records:

- workload kind
- build/probe input selection
- acceleration kind
- predicate and refine mode
- output record schema
- launch parameters
- payload registers
- buffers
- ray specification
- host steps
- device program names
- BVH policy

This is the boundary where RTDL moves from language semantics toward backend
execution. The same logical kernel may require different backend implementation
details, but the plan makes the intended execution contract explicit.

## Current Lowering Boundary

Current public lowering is predicate-specific at the Python language
surface. `lower_to_execution_plan(...)` accepts the current DSL kernel and
dispatches to workload lowerers such as:

- line-segment intersection
- point-in-polygon
- overlay composition
- ray/triangle hit count
- ray/triangle any-hit
- segment/polygon hit count
- segment/polygon any-hit rows
- polygon pair overlap area rows
- polygon set Jaccard
- point nearest segment
- fixed-radius neighbors
- KNN rows
- bounded KNN rows

This public surface is intentionally workload-aware because users write
meaningful Python programs. The engine boundary is stricter underneath: native
source and exported ABI terminology must stay app-agnostic.

## What Is Stable Today

Stable current facts:

- The public authoring model is `input -> traverse -> refine -> emit`.
- The accepted acceleration spelling is `accel="bvh"`.
- The accepted precision policy is `precision="float_approx"`.
- `CompiledKernel` and `RTExecutionPlan` are real repo objects, not just design
  notes.
- The plan can serialize to a schema-tagged dictionary.
- Some generated backend artifacts still use capacity/counter patterns and
  should not be treated as the final execution ABI.

## What The Current Engine Boundary Tightens

The current release-prep chain tightens app-specific engine customization by
turning common backend work into reviewed generic primitives and generic native
ABI terminology. The accepted direction separates primitives by result
semantics, not by app names:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- `COLLECT_K_BOUNDED` as an experimental/limited primitive

That distinction matters for ABI shape, determinism, grouping, numeric
tolerance, output capacity, and cross-backend parity.

## What v2.x Adds

The v2.x-facing path makes RTDL a Python+partner runtime, not only a Python row
DSL. The expected direction is:

- compile once into a stable execution plan
- bind flat native-ready buffers
- dispatch backend work directly
- expose thin result views when possible
- materialize Python dictionaries only when users ask for row convenience
- interoperate with GPU compute tools for non-RT phases instead of forcing
  Python to own heavy reductions, ranking, clustering, or force computation

## Where To Read Next

- [DSL Reference](dsl_reference.md)
- [Programming Guide](programming_guide.md)
- [ITRE App Programming Model](itre_app_model.md)
- [Performance Model](../performance_model.md)
- `src/rtdsl/ir.py`
- `src/rtdsl/lowering.py`
- `src/rtdsl/codegen.py`
