# CGO Contribution Argument

Date: 2026-09-06 America/New_York.

Status: `N3_COMPLETE__SYSTEMS_METHOD_CLAIM__FINAL_REVIEW_PENDING`.

This document joins the primary-source comparison in
`RELATED_WORK_BOUNDARIES.md` (N1) with the implementation trace in
`PROTOCOL_WITNESS_AND_DERIVATION.md` (N2). It is an author-scope argument, not
an independent novelty opinion or claim authorization.

## 1. Paper-ready argument

### Problem

Programming an RT pipeline is not only a matter of typing each callback or
calling a host API. A finite route also depends on relations distributed across
callback roles, payload and intersection-attribute meanings, geometry and query
projections, generated wrapper behavior, device failure continuation, and the
executable that is ultimately loaded. A same-width substitution can preserve
ordinary ABI validity while changing application meaning. A locally valid
shader, SBT, or host call therefore does not by itself imply that the selected
pieces form the intended application result route.

This is not a claim that existing APIs or languages provide no safety. DXR has
stage-indexed payload access qualifiers; Vulkan specifies interface and SBT
validity; Slang provides interfaces, reflection, specialization, and current
capability checking; OWL, SlangPy, Luisa, Dr.Jit, and CrossRT provide substantial
construction, staging, or generation facilities. Protocol types, linking types,
and FFI work provide stronger general theories for stateful interaction and
cross-language boundaries than RTDL. The narrower observation is that the
checked primary sources do not document the same joint finite-route admission
relation. For several systems this is `UNKNOWN`, not a proof of absence.

### Core design contribution (`CONTRIB-PROTOCOL-UNIT`)

RTDL treats a bounded RT route as a protocol-carrying compilation and admission
unit. For each supported family, it records and jointly compares five concrete
relations:

1. callback role/effect closure;
2. payload or intersection-attribute semantic ownership;
3. task and physical geometry/output/reducer binding;
4. fail-closed device-status continuation; and
5. checked-program/executable identity.

The key design choice is not the use of equality checks or hashes. It is the
placement of a shared route contract across representations that are normally
validated or assembled separately, and the use of its decision at the actual
materialization, native-load, and public-result lifecycle boundaries. This
makes a finite cross-artifact relation explicit and auditable instead of leaving
it as an informal invariant distributed among Python code, generated device
code, wrapper templates, and runtime convention.

The current implementation derives a declaration from the verified program and
a projection from compiled ABI/physical-contract artifacts, canonicalizes and
compares the five seams, and refuses to return a materialized route on mismatch.
Before public result construction it additionally checks generated/native
identity, device status, output digest, and traversal receipt. These are
separate derivations within one compiler, not independent trust roots. Trusted
semantic declarations and specialized lowerers remain in the TCB.

### Implementation method (`CONTRIB-TYPED-EFFECT-LOWERING`)

Restricted Python callbacks return typed effects rather than directly invoking
RT hardware operations. The compiler checks role-specific effect variants and
fields, flattens them into a deterministic callback ABI with effect/status tags,
and emits Numba device leaves. A trusted topology-specific OptiX wrapper invokes
the leaf, validates its effect/status, and performs the corresponding hardware
operation, such as payload update, traversal continuation via
`optixIgnoreIntersection()`, or fail-closed termination.

This split puts user computation in a restricted, typed language while keeping
hardware control in a reviewed lowerer. It also exposes exactly where the
compiler's guarantee ends: the canonical plan is descriptive, not executable;
specialized lowerers and wrapper templates are trusted; RTDL does not synthesize
an arbitrary lowerer from an arbitrary protocol graph.

### Evidence contribution (`EVIDENCE-BOUNDED-VALIDATION`)

The evidence is deliberately finite:

- mutation checks show that each of five seams is live and that an integrated
  projection mismatch is rejected before native load;
- the independent finite checker inspects generated artifacts for the sealed
  challenge but is not a semantic proof;
- one sealed-snapshot extension demonstrates reuse over a finite matrix, while
  also requiring about 2,635 lines of topology-specific code and compiler
  changes;
- two GPU generations validate exact prepared routes and bounded overhead;
- the artifact independently recounts retained projections but cannot rerun the
  GPU or prove novelty.

The illustrative `primitive_index:u32` versus application `item_id:u32` witness
explains why machine typing alone is insufficient. It was not retained as an
executed defective route and must not be described as one.

### Claim level

The defensible contribution is a compiler-system design and implementation
method for jointly admitting finite RT callback routes. It is not a new general
analysis algorithm, type calculus, soundness theorem, automatic profitable-RT
mapping method, arbitrary-topology compiler, or proof that another system
cannot implement equivalent checks. No "first" or "unique" wording is needed.

## 2. What remains after removing RT names?

The reusable idea is a **protocol-carrying admitted executable**:

1. represent cross-component obligations that are not implied by each local
   component type;
2. derive a source-side declaration and a target-artifact projection;
3. compare them before minting/loading an executable capability;
4. bind the accepted decision to actual executable identities; and
5. make asynchronous failure/partial-output state part of the public-result
   admission boundary.

This pattern could apply to split host/device accelerator systems, RPC stubs,
storage accelerators, packet-processing pipelines, or generated foreign
interfaces. That is a design implication, not demonstrated generality. RTDL
evaluates it only for its bounded RT families and one backend/runtime stack.

## 3. Increment over close concepts

| Existing concept/capability | What it already solves | RTDL's narrower increment | What RTDL does not add |
| --- | --- | --- | --- |
| DXR PAQs and Slang capabilities | Stage access, target/stage/API/hardware requirements, compiler validation | Connects selected role/effect facts with application-named attribute ownership, physical/result contract, continuation, and executable identity in one finite route decision | New stage capability system or better general shader typing |
| Shader Components, Slang interfaces, reflection/cursors | Modular shader interfaces, specialization, parameter layout and binding support | Uses a route rather than a component/type as the admitted unit and carries the decision into native-load/publication lifecycle | New module/generic/reflection mechanism |
| OWL, SlangPy, Luisa, Dr.Jit, CrossRT | Python access, pipeline/SBT management, staging, code generation, dependency analysis, cross-platform lowering | Makes a particular semantic/physical/identity relation explicit and fail-closed for supported RTDL families | Broader language, broader platform support, or proof those systems cannot add the relation |
| Typestate and interface automata | General state/protocol and component compatibility models | Concrete engineering projection into RT callback/compiler/runtime artifacts | New state calculus, refinement algorithm, or formal compatibility result |
| Session types | Global protocol and local projection with formal safety/progress results | A fixed route declaration/projection check in a real split compiler/runtime stack | General projection theorem, communication fidelity, or progress theorem |
| Typed linking and FFI checking | Cross-language behavior and physical/semantic representation reasoning | Binds an RT-specific set of roles, attributes, physical plans, continuation and actual executable bytes | New general linking type or FFI soundness theorem |

## 4. Six hostile reviewer questions

### 4.1 Existing local types, capabilities, and layouts already do this

They do important parts. DXR PAQs express per-stage payload reads/writes; Slang
capabilities validate target/stage/API/hardware requirements; reflection and
shader cursors address layout/binding; Vulkan specifies extensive interface and
SBT constraints. RTDL must not relabel those as absent.

The N2 mismatch falls in a relation not implied by width/layout alone: attribute
slot zero can legally contain either a physical primitive index or an
application item ID, both `u32`. RTDL's emission schema assigns an application
semantic source, the compiled contract carries it, and the admission check
compares it with the program-side route declaration. This remains dependent on
a trusted semantic declaration; RTDL does not infer intent.

### 4.2 Typestate, interface automata, or session types can represent this

Yes, they can represent significant parts and offer stronger formal machinery.
RTDL's contribution is not a proof that those theories are inapplicable. Its
choice is an implementation specialization: a finite set of RT-specific facts
is projected from compiler artifacts and enforced at concrete materialization,
load, and publication points. The paper should present the formal work as
foundation and describe RTDL as a systems realization with a narrower theorem
surface: none.

### 4.3 Why not add assertions to OWL, Slang, or an ordinary wrapper?

A careful developer could add equivalent assertions, and another compiler
could adopt this design. The research value cannot rest on impossibility.

Scattered assertions, however, do not automatically define which artifact is
authoritative, how facts are normalized across source/ABI/physical/runtime
representations, which decision gates executable minting and native load, or
how that decision remains bound to the bytes and fail-closed output. RTDL's
method packages those choices into one explicit admission object and lifecycle.
The implementation demonstrates that organization for two public protocol
families. If reviewers judge this merely a configuration-consistency wrapper,
the paper must accept that limited systems contribution; no stronger theorem is
available.

### 4.4 Is this just typed linking or FFI checking plus hashes?

Typed linking and FFI research already show how to express rich cross-language
and representation properties. Hashing is also standard. RTDL's increment is
the selected domain model and where it is enforced: callback role/effect
closure, semantic attribute ownership, physical geometry/output contract,
device continuation, and actual RT executable lifecycle are one admitted unit.

Hash equality contributes identity coherence only. It does not show that the
source is correct, that the compiler preserved semantics, or that two equal
semantic names match application intent. The paper must state all three limits.

### 4.5 Is this a new analysis algorithm or type theorem?

No. The comparison is deterministic canonical equality over five finite seams;
the callback verifier uses conventional type/effect checks; the independent
checker is finite and structural. The contribution is a compiler-system design
and its integration/evaluation, not a new general algorithm or soundness
theorem. Mathematical notation may summarize the contract but must not imply a
formal result that was not proved.

### 4.6 Is semantic-name comparison circular self-certification?

It would be circular if both sides simply copied one mapping and equality were
presented as semantic proof. The implementation is somewhat stronger but still
limited: the public declaration is derived from the verified protocol program;
the target projection reads separately compiled ABI and physical/relation
contract objects; mutations between them are detected. Yet both paths belong to
the same compiler and the attribute meaning originates in a trusted schema.

Therefore the check proves representation consistency under that premise, not
truth of the premise. The manuscript should say "separately derived compiler
representations" rather than "independent trust roots," and "admission under a
trusted semantic contract" rather than "semantic correctness proof."

## 5. Contribution-to-evidence matrix

| ID | Proposed contribution statement | N1 boundary | N2 mechanism/evidence | Required limitation |
| --- | --- | --- | --- | --- |
| `CONTRIB-PROTOCOL-UNIT` | RTDL organizes five dispersed RT route obligations into a common declaration/projection admission unit used at lifecycle gates. | No checked close source documents the same exact unit; many exact-Q cells remain `UNKNOWN`. | `PC-01` through `PC-05`; materialization and publication trace | Domain-specific, finite, same-compiler derivations, trusted schema/lowerers, no exclusivity |
| `CONTRIB-TYPED-EFFECT-LOWERING` | Restricted callbacks return typed effects; trusted topology lowerers map accepted tags to RT hardware operations. | Role/effect/capability and code-generation precedents are strong. | Actual IR -> ABI -> Numba leaf -> OptiX wrapper chain in N2 Section 6 | Implementation method, not new effect theory; lowerers remain topology-specific TCB |
| `EVIDENCE-BOUNDED-VALIDATION` | Mutation, finite checking, sealed extension, two-generation performance and replayable recount support feasibility. | Does not decide novelty against other systems. | Existing tests and M/E/F2/P' authorities | Finite scope, adverse results retained, no human study, no wrong-route execution |

## 6. Claims to retain, narrow, or delete

| Disposition | Claim |
| --- | --- |
| Retain, bounded | RTDL implements a joint admission contract for five named seams in its supported finite RT routes. |
| Retain, bounded | Typed callback effects are lowered through a deterministic ABI and consumed by trusted topology-specific wrappers at hardware-control points. |
| Retain, evidence-only | Mutation tests demonstrate liveness of the five checks; integrated projection corruption is blocked before native load. |
| Retain, evidence-only | Frozen two-generation results bound overhead for the exact evaluated paths; they do not prove general performance. |
| Narrow | Checked nearby primary sources do not document the same Q1-Q6 guarantee; for several systems the exact answer remains unknown. |
| Delete | Existing Python RT interfaces merely expose raw calls or cannot provide whole-route checks. |
| Delete | Existing systems do not manage pipelines/SBTs or do not check cross-stage payload constraints. |
| Delete | The illustrative `(100,0),(101,1)` defective route was executed. |
| Delete | RTDL is the first/only system capable of this mechanism. |
| Delete | The protocol contract or finite checker proves semantic correctness or arbitrary-topology generality. |

## 7. Cost and tradeoff disclosure

The method's current cost is material and part of the contribution boundary.
The sealed extension required approximately 2,635 lines of topology-specific
code plus compiler modifications after the nominal generic core was frozen.
The canonical compilation plan remains non-executable. Specialized wrapper
generators, trusted semantic schemas, native provider behavior, and lifecycle
checks form a sizable TCB. There is no independent human authoring study.

The performance evidence supports prepared-route overhead bounds on two NVIDIA
GPU generations, but first-result/post-import measurements are adverse and
confounded by lifecycle placement. Per-call detailed receipts were not retained
for the 4,096 timed Arm-A calls. These costs do not erase the design result, but
they prohibit claims of automatic arbitrary extension, generally negligible
startup cost, or demonstrated ease of use.

## 8. N3 verdict

The work supports **one bounded compiler-systems contribution**, implemented by
a typed-effect/specialized-lowering method and backed by finite evidence. It is
potentially suitable for CGO if the manuscript is rewritten around this exact
increment and the final bytes survive independent review. The argument does not
support a new general type theory, automatic lowerer synthesis, universal Python
RT safety, or categorical superiority over the named systems.
