# Goal5832 — protocol-shape algebra, equivalence, and claim ceiling report

## Result

**PASS at research-specification and executable-reference-validator scope.**
Goal5832 defines what a protocol family is before attempting to claim that a
compiler is family-parametric. It adds a machine-readable authority, a
domain-separated canonical identity implementation, twelve adversarial unit
tests, documentation, and manuscript integration. It does not change RTDL
product code, invoke a GPU, or claim a generic GPU compiler.

This scope distinction is binding:

> Goal5832 makes “same family” mechanically decidable. It does not yet make a
> new family executable without changing the implementation core.

## Three identities, not one overloaded family label

1. **Family shape** records structural protocol facts only:
   `S = <G,R,V,E,H,B,C,X,L>`.
   These axes cover the physical graph, role topology, typed views, effects,
   nominal hit-channel ownership, physical bindings, result and continuation
   automaton, identity bind set, and resource limits.
2. **Protocol instance** adds typed parameter values, nominal application
   semantics, verified Callback IR, effects, ABI, and proof authorities.
3. **Deployment** adds target profile, provider, generated source, native
   binary, and actual executable identity.

The three SHA-256 identities use distinct domain prefixes. Therefore a nominal
semantic change changes the instance without redefining the structural shape,
and a target change changes the deployment without redefining either the shape
or instance.

## Equivalence rules

Family-shape equivalence is exact equality of canonical, alpha-normalized
shape bytes. Local binder spelling and set order do not matter. Role order,
argument order, result-operator order, producer/consumer ownership, topology,
and continuation order do matter. There is no fuzzy equivalence or manual
“looks similar” adjudication.

Canonicalization rejects duplicate JSON keys, floats in normative identity,
unknown/dangling local references, and forbidden application/file/timestamp
fields. Exact recursive typed schemas additionally reject schema-only objects,
unknown nested fields, bool-as-integer aliases, illegal role/effect pairs,
invalid operator unions, incomplete status-before-output automata, untyped
instance parameters, and incomplete target/provider deployments. It preserves
order-bearing arrays, sorts only declared set-valued fields, and alpha-normalizes
only local binders.

## Current support matrix semantics

Support is separated into five stages:

1. vocabulary;
2. verifier;
3. provider/code generation;
4. public lifecycle;
5. true-GPU evidence.

A word existing in an enum or schema cannot be promoted to executable support.
Curves, spheres, IAS/instance topology, trace depth above one, callable depth
above zero, and arbitrary reducers remain unsupported or vocabulary-only at
the later stages. The current two geometry paths remain family-specific in
provider/compiler code.

## Verification

- Scope validator: `GOAL5832_PROTOCOL_SHAPE_AUTHORITY_PASS`.
- Unit tests: 23/23 pass.
- Tests include hostile authority overclaim and support promotion, three-domain
  empty/garbage documents, nested unknown keys, bool-as-int, role/effect typing,
  binder/ordinal failures, operator and continuation failures, typed
  instance-to-shape binding, authority-set normalization, complete deployment
  binding, alpha-renaming, order sensitivity, and domain separation.
- The content-first manuscript builds to 17 pages with zero overfull boxes,
  zero undefined citations, and zero undefined references. This is not the
  final page-limited or anonymized submission artifact.

## What Goal5832 proves—and does not prove

It proves that the project now has a precise, executable vocabulary for
separating shape, instance, and deployment, and that current scope claims can
be checked against pinned source and platform facts.

It does not prove any of the following:

- that arbitrary verified Callback IR can execute on GPU;
- that the current provider/compiler is family-parametric;
- that curves, spheres, instances, or new continuation topologies work;
- that a frozen core has passed a prospective new-family exam;
- that a third party can author an application;
- that the two author-selected physical kinds represent the open universe.

Prospective new-shape exam count therefore remains **zero**. The next scientific
task is not another case-specific wrapper; it is to replace concrete-family
dispatch with a generic schema admission/compiler path, freeze that core, and
then attempt new geometry and topology challenges without changing it.
