# Correctness and Extension Model

## What V3 can prove

V3's correctness claim is relative to its supported Action fragment and
registered physical families:

> If a program is admitted, canonical resolution succeeds, all proof/resource
> obligations validate, materialization preserves the resolved provider, the
> exact-output comparator passes, and the behavioral receipt is complete, then
> the executed provider implements the registered statement for that bounded
> execution.

This is not a completeness theorem for arbitrary applications.  A missing
mapping is reported as unsupported rather than filled with an opaque callback.

## How statement X is matched to provider Y

The core relation is a checked refinement contract:

```text
Y.precondition covers X.input_domain
Y.effects are permitted by X.typed_effect_contract
Y.output contract equals X.output_semantics
Y.precision and tie rules satisfy X.algorithm_contract
Y.resource bounds hold on the observed target
Y.source, ABI, template, and proof identities match the registry
```

The compiler registry stores this relation as a canonical binding.  Resolution
requires exactly one eligible binding.  Zero matches returns a typed
fail-closed receipt.  More than one canonical match is an ambiguity error, not
an opportunity for an unreviewed heuristic.

## Adding a physical family

Adding a reusable provider is compiler work, not ordinary app work:

1. define or reuse an app-neutral semantic statement;
2. specify input domain, output semantics, effects, precision, ordering, tie,
   lifetime, capacity, and fallback behavior;
3. implement an app-neutral provider and bind its exact source/ABI/template;
4. add reference and adversarial tests, including malformed and boundary cases;
5. prove at least one real consumer and keep application names out of core
   dispatch;
6. add functional output checks and independent behavioral traversal receipts;
7. register exactly one canonical binding for each supported backend contract.

This is more work than adding an OS syscall because the compiler is asserting
semantic equivalence and physical execution properties, not merely exposing an
ABI.  The payoff is that applications cannot inject arbitrary device code,
forge proof state, or silently select an unverified route.

## What happens when a primitive is missing

- If existing primitives compose to the required statement under the closed
  effect and termination rules, the compiler may lower the composition.
- If the necessary semantic component is absent, compilation fails closed.
- A language implementer may add a generic provider under the process above.
- The application cannot bypass this by passing an arbitrary OptiX, PTX,
  Numba, or Python callback through the production front door.

This boundary is intentional.  V3 trades open-ended callback expressiveness
for auditable semantics, deterministic lowering, and evidence that the claimed
physical route actually executed.
