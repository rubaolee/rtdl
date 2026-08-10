# V3 Architecture

## The contract pipeline

```text
application-owned algorithm
        |
        v
typed semantic Action statement
        |
        v
canonical resolver  ---- target capabilities/resources
        |
        v
one source-bound physical provider
        |
        v
materialization + authority binding
        |
        v
execution + exact-output check + behavioral traversal receipt
```

The application owns algorithm policy.  For example, Triangle Counting asks
for RT-1A2 or RT-2A1, and Arkade asks for FR-L-infinity or MT-cosine.  V3 does
not choose between those paper algorithms.  Each algorithm maps to a distinct
semantic statement.  V3's job begins after that choice: it verifies and
materializes the canonical physical implementation for the exact statement.

## The four identities

V3 separates four things that older app-directed paths could conflate:

1. **Semantic statement** — algorithm contract, typed effects, and exact output
   semantics.
2. **Backend contract** — required providers, allowed execution classes,
   required physical capabilities, and whether behavioral proof is mandatory.
3. **Physical provider** — source-bound implementation identity, ABI, proof,
   resource, reuse, template, and memory contracts.
4. **Execution evidence** — the materialized plan identity plus a post-run
   receipt that proves complete bound traversal actually happened.

The implementation is centered in:

- `src/rtdsl/canonical_physical_resolution.py`;
- `src/rtdsl/action_api.py`;
- `src/rtdsl/default_compiler_frontdoor.py`.

`resolve_canonical_provider` is static: it never executes a candidate and it
does not use timing, learned costs, dataset names, or application names.
`bind_canonical_provider_to_materialized_plan` and
`bind_canonical_provider_to_direct_provider` prevent a compatibility
materializer or direct call from substituting a different provider after
resolution.

## Why this is more than a name table

A string-to-function table would accept a matching name and call it.  V3 also
checks:

- the digest of the semantic and backend contracts;
- the Action shape and admitted proof/resource/template digests;
- required providers and execution class;
- dynamic memory and cardinality bounds;
- provider source hash and source anchor;
- target identity and native ABI requirements;
- the identity of the materialized provider;
- exact output and behavior-level traversal evidence after execution.

The mapping is finite and registered, but the authority is semantic and
source-bound.  A name match with a changed implementation, missing capability,
insufficient memory, ambiguous provider, or unbound launch fails closed.

## DEFAULT means canonical, not cost-optimal

The production DEFAULT is deterministic resolution inside the supported
universe.  It is not SQL-style cost optimization.  It does not claim to find
the fastest physical plan.  If an application defines two different
algorithms, those remain two explicit application choices.  Cross-platform
backend contracts may select a compatible registered provider, but the NVIDIA
V3 research path requires the OptiX traversal contract where stated.
