# RTDL Programming Surfaces

Status: current v3.0 source-tree guidance.

RTDL is one language/runtime, but users enter it through three related
surfaces. Keep them distinct when learning, writing examples, or reporting
performance.

## The Three Surfaces

| Surface | Use it for | What it is not |
| --- | --- | --- |
| Kernel DSL | Teaching and expressing the generic `input -> traverse -> refine -> emit` shape. | Not a promise that every high-performance benchmark route is written as `@rt.kernel` today. |
| Primitive and prepared front doors | Promoted performance paths, prepared state reuse, and benchmark-backed generic contracts. | Not an app-specific private engine. The primitive must remain generic. |
| Partner continuation | CuPy or Numba work over typed columns when the app needs custom tensor-side continuation. | Not automatic partner selection, arbitrary acceleration, or a replacement for RT traversal. |

## Practical Rule

Start with primitive discovery:

```python
import rtdsl as rt

matches = rt.find_primitive(text="nearest points within radius")
for match in matches:
    print(match.name, match.node_id)
```

If an existing primitive or prepared front door expresses the RT-shaped work,
use it first. It is the most likely path to match the current benchmark
evidence.

If no primitive fits, write a small kernel or Python reference to clarify the
contract. Then decide whether the missing part is:

- a new generic primitive the engine should grow;
- a partner continuation over typed columns;
- plain Python application logic that should stay outside RTDL.

## Kernel DSL Boundary

The kernel DSL is the cleanest way to teach RTDL's mental model:

```text
input -> traverse -> refine -> emit
```

It is not yet the only route to performance. Several benchmark apps use
prepared primitive front doors directly because those routes expose prepared
state, bounded output policies, grouped summaries, or partner-column contracts
that the small teaching DSL does not currently lower to.

That is acceptable when documented honestly:

- app policy stays in Python;
- native engine contracts stay app-agnostic;
- public performance wording cites the exact primitive, backend, partner,
  dataset, command, hardware, and reviewed artifact.

## Benchmark Apps

Benchmark apps are reference compositions. They show how to combine generic
RTDL primitives, prepared execution, and explicit partner choices. They are not
evidence that every user app should be written by copying one app-specific API,
and they are not proof that all ten benchmark apps are broad RT-core wins.

Use these pages together:

- [Primitive Discovery Workflow](primitive_discovery_workflow.md)
- [Prepared Execution Pattern](prepared_execution_pattern.md)
- [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
- [Current Claim Boundaries](current_claim_boundaries.md)
- [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
