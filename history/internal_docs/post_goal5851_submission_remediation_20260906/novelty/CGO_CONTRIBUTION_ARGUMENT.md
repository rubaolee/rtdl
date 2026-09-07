# CGO Contribution Argument

Date: 2026-09-07 America/New_York.

Status: `N3_PTRIPLEPRIME_REMEDIATED__SYSTEMS_DESIGN__INDEPENDENT_REVIEW_PENDING`.

This document joins the primary-source capability audit in
`RELATED_WORK_BOUNDARIES.md` (N1) with the implementation trace in
`PROTOCOL_WITNESS_AND_DERIVATION.md` (N2). It is an author-scope argument, not
an independent novelty opinion, final-byte acceptance, or claim authorization.

## 1. The four questions the contribution must answer

### 1.1 What do existing components already solve?

Existing work covers much of the mechanism space. DXR payload access
qualifiers and Slang capabilities check important stage, target, API, and
hardware relations. Vulkan specifies shader-interface and SBT validity.
Shader Components and Slang provide modularity, specialization, reflection,
and layout facilities. OWL, SlangPy, Luisa, Dr.Jit, and CrossRT provide Python
access, RT construction, staging, or code generation. Typestate, interface
automata, session types, linking types, and FFI checking provide stronger
general protocol or boundary theories than RTDL. Proof-carrying code (PCC)
already established consumer-side validation of a producer-supplied proof
against a policy before native execution (`RW-PT-06`).

RTDL therefore does not claim Python access to RT, pipeline/SBT construction,
typed effects, hashing, validation-before-execution, or general protocol
reasoning as new. The exact joint Q1-Q6 guarantee remains `UNKNOWN` for several
nearby systems after the N1 primary-source audit; source silence is not
inability and supports no first/only claim. Evidence IDs: `RW-RT-01`--`05`,
`RW-SC-01`--`08`, and `RW-PT-01`--`06`.

### 1.2 What does RTDL add?

RTDL's core design is a **protocol-carrying admitted executable** for fixed RT
families. One route contract explicitly represents and relates:

1. callback roles and permitted effects;
2. nominal payload or intersection-attribute ownership;
3. task, geometry, output, and reducer binding;
4. fail-closed continuation/status requirements; and
5. checked-program and executable identity.

The compiler defines where each fact originates, extracts a declaration and a
separately represented compiled projection, canonicalizes them, and applies one
five-relation decision before returning a materialized route. The accepted
identity is then carried through per-route preparation and the publication
checks implemented by each interface. Exact app-free native runtime loading or
warming may start before admission; it exposes no admitted route and does not
authorize per-route preparation or launch. Evidence IDs: `PC-01`--`PC-05` and
N2 Sections 4--5.

The same-width N2 witness makes the design concrete. Attribute zero can legally
hold physical `primitive_index:u32` or application `item_id:u32`; width and
layout alone cannot distinguish them. A trusted relation schema names the
intended source, a compiled contract carries it, and the route decision detects
representation drift. The bad rows are illustrative, not an executed defective
route. Both derivations remain in one compiler and depend on the trusted schema,
so this is consistency under a premise, not semantic inference or proof.

### 1.3 Why is this organization worth studying?

The contribution is not that five checks happen to differ. It is the concrete
systems choice to turn facts otherwise spread among restricted Python IR,
callback ABI, physical contracts, generated OptiX programs, runtime state, and
executable custody into one inspectable route object with named comparison and
enforcement points. That organization makes authority, representation drift,
trusted code, and fail-closed obligations explicit and auditable.

This is useful research evidence only to the extent demonstrated here: two
public protocol families, finite mutations, one sealed composition exercise, a
finite independent structural checker, two exact GPU tasks on two generations,
and reproducible offline recount. Another compiler or ordinary wrapper could
adopt equivalent assertions. RTDL offers a concrete domain-specific design and
implementation experience, not an impossibility result or new validation idea.
Evidence IDs: `EVIDENCE-BOUNDED-VALIDATION`, N2 Sections 6--9, and N1's Q table.

### 1.4 What are the costs and guarantees?

The guarantee is bounded representation consistency and fail-closed behavior at
the documented boundaries for the implemented routes, assuming trusted schemas,
compiler projections, exact-IR recognizers, topology lowerers, runtime, and
native provider. Digests bind identity; they do not prove semantics. RTDL
provides no PCC certificate, soundness theorem, arbitrary-topology synthesis,
or independent target trust root.

The implementation cost is substantial. The sealed extension required about
2,635 topology-specific LOC plus compiler changes. The measured routes use
trusted exact-standard-IR specializations. The materialized-program and measured
AOT prepared interfaces have different publication evidence. The formal A
population has 4,096 timed calls but only 32 separate post-loop detailed
receipts. First-result/post-import evidence is adverse and lifecycle-confounded,
and there is no independent human authoring study. Evidence IDs:
`CONTRIB-TYPED-EFFECT-LOWERING`, `EVIDENCE-BOUNDED-VALIDATION`, and N2 Sections
4.1, 5, 6, and 9.

## 2. One design, one implementation method, finite evidence

### 2.1 Core design (`CONTRIB-PROTOCOL-UNIT`)

For a fixed RT family, the shared route contract connects role/effect closure,
nominal attribute ownership, physical/result/reducer binding, continuation, and
executable identity. One decision checks those five relations before a
materialized route is returned. The accepted identity continues into per-route
preparation and interface-specific publication checks. This is the proposed
systems-design contribution.

It is not a claim that the declarations are independent authorities. The
semantic schema is trusted and both projections are produced inside one
compiler. A wrong but internally coherent schema can pass. The design catches
represented disagreement; it does not infer application intent.

### 2.2 Implementation method (`CONTRIB-TYPED-EFFECT-LOWERING`)

The general path verifies restricted Python callback effects, flattens them into
a deterministic ABI with status/effect tags, generates Numba leaves, and lets a
trusted topology wrapper interpret those results before issuing hardware
operations. The evaluated standard routes additionally use trusted exact-IR
specializations:

| Evaluated path | Actual hot execution | General work replaced | Checks retained |
| --- | --- | --- | --- |
| Triangle reduction | Exact callback IR plus checked-U64 reducer selects direct count/reduction raygen and any-hit entries. | Per-hit Numba leaf calls and per-leaf effect-tag checks at specialized roles. | Static schema/ABI/identity admission, native/compact failure handling, checked overflow, and supplied expected output. |
| Bounded relation | Exact standard relation IR selects fused intersection, counting/row emission, and continuation. Generated leaf identities remain bound but are not called. | Per-role leaf calls and effect-tag interpretation in fused roles. | Static schema/ABI/contract/identity admission, native status, capacity/overflow, canonical rows, and supplied expected rows. |

These exact-IR recognizers and specialized wrappers are part of the TCB. An IR
digest selects a known implementation path; it is not a semantic-preservation
proof. The canonical compilation plan remains descriptive, not executable, and
RTDL does not synthesize arbitrary wrappers from arbitrary protocol graphs. The
reported prepared latencies measure these specialized standard routes, not the
cost of executing every role through the general Numba-leaf ABI.

### 2.3 Interface and evidence boundaries

| Interface or phase | What actually happens | Prohibited generalization |
| --- | --- | --- |
| Materialized-program `ProtocolExecutionResult` | Execution identity, native/device status, output digest, and traversal receipt are validated before return. | The measured AOT calls all use this interface. |
| Measured AOT prepared `RTDLExecutionResult` | Owner/process/thread/reentrancy boundaries, native/compact failures, and supplied expected output are checked synchronously. Ordinary fast results may omit digest and detailed receipt. | Every fast return carries a detailed receipt or rehashes all disk artifacts. |
| Worker oracle | Output and digest are checked after prepared return; for first-result it is after the prepared timer but within the endpoint. | The oracle is an automatic compiler guarantee or part of the prepared steady timer. |
| Separate diagnostic | One post-loop execution per Arm-A worker retains detailed evidence. | Each of the preceding 128 timed calls has its own retained detailed receipt. |

## 3. Increment over close concepts

| Existing concept or capability | What it already solves | RTDL's narrower increment | What RTDL does not add |
| --- | --- | --- | --- |
| PCC | Policy-based admission of native binaries through validation of a supplied proof. | No proof certificate; instead, one bounded RT-specific route representation and selected compiler/runtime checks. | Validation-before-execution, proof-carrying safety, or a formal semantic theorem. |
| DXR PAQs and Slang capabilities | Stage accesses and target/stage/API/hardware requirements with compiler validation. | Connects selected role/effect facts to nominal attribute ownership, physical/result contract, continuation, and exact executable identity in one finite decision. | A new stage-capability system or better general shader typing. |
| Shader Components, Slang interfaces, reflection/cursors | Modular interfaces, specialization, parameter layout, marshalling, and binding. | Uses a bounded RT route rather than one component/type as the represented admission unit. | New modules, generics, reflection, marshalling, or caching. |
| OWL, SlangPy, Luisa, Dr.Jit, CrossRT | Python RT access, pipeline/SBT management, staging, code generation, dependency analysis, and cross-platform lowering. | Makes a particular semantic/physical/continuation/identity relation explicit for the supported RTDL families. | A broader language/platform or proof those systems cannot implement the relation. |
| Typestate, interface automata, session types | General state/protocol, compatibility, projection, and formal safety/progress machinery. | A finite engineering projection into a split RT compiler/runtime's concrete artifacts and lifecycle. | A state calculus, refinement algorithm, projection theorem, fidelity, or progress proof. |
| Linking types and FFI checking | Rich cross-language behavior and physical/semantic representation checks. | Binds one RT-specific set of roles, attributes, physical plans, continuation, and executable bytes. | A general linking type or FFI soundness theorem. |

## 4. Hostile reviewer questions

### 4.1 Existing types, layouts, and capabilities already do this

They solve important parts and the paper must say so. The N2 mismatch is a
nominal relation not implied by width/layout alone: two distinct meanings fit
the same `u32` slot. RTDL's trusted schema and route projection expose that
particular cross-representation assertion. This does not infer intent and does
not supersede PAQs, Slang capabilities, reflection, or SBT validation.

### 4.2 Is this just PCC, typestate, typed linking, FFI checking, and hashes?

Those are direct foundations and often stronger theories. PCC in particular
prevents any claim that policy validation before native execution is new. RTDL's
increment is only the concrete bounded RT design: which five facts are carried,
where they are extracted, where one route decision is made, and how its identity
is connected to preparation and interface-specific publication. Hashes provide
identity coherence, not semantic correctness.

### 4.3 Why not add assertions to OWL, SlangPy, or an ordinary wrapper?

A careful developer could, and another system could adopt this design. The
research question is whether an explicit protocol-carrying executable makes the
distributed authorities and obligations more inspectable and enforceable in a
real compiler/runtime. RTDL supplies one implementation and finite evidence. If
reviewers consider that only systems integration, the paper must accept that
classification rather than manufacture novelty or performance causality.

### 4.4 Is the common gate really before native load and every result?

No. Exact app-free native runtime loading/warming may begin before admission,
including concurrently with AOT artifact verification. Admission still gates
acceptance of a materialized route and subsequent per-route preparation and
launch. Only overlap-disabled mutation tests establish rejection before the
native-library loader. Publication evidence also differs between the
materialized-program and measured AOT prepared interfaces, as Section 2.3
states.

### 4.5 Is every measured callback executed through the advertised generic ABI?

No. The generic typed-effect/Numba-leaf path is implemented, but the reported
triangle and bounded-relation prepared latencies use the exact-standard-IR
specializations in Section 2.2. Those specializations remove leaf invocations
and per-leaf effect-tag checks in specialized roles while retaining the listed
static and runtime checks. They are trusted implementation code and a cost, not
evidence of automatic arbitrary-program lowering.

### 4.6 Is semantic-name comparison circular self-certification?

It would be circular if equality were presented as semantic proof. RTDL is
narrower: declaration and target projection are separately represented and
mutations between them are detected, but both are produced by one compiler and
the intended meaning begins in a trusted schema. The result is consistency
under that premise, not truth of the premise.

## 5. Contribution-to-evidence matrix

| ID | Proposed contribution statement | N1 boundary | N2 mechanism/evidence | Required limitation |
| --- | --- | --- | --- | --- |
| `CONTRIB-PROTOCOL-UNIT` | RTDL organizes five dispersed RT route obligations into one declaration/projection decision and carries the accepted identity into later route stages. | PCC and protocol/linking systems establish broader antecedents; exact Q1-Q6 remains `UNKNOWN` for several close systems. | `PC-01`--`PC-05`; N2 admission/initialization timeline | Domain-specific and finite; app-free warmup may precede admission; same-compiler derivations; trusted schema/lowerers; no exclusivity. |
| `CONTRIB-TYPED-EFFECT-LOWERING` | General callbacks lower through typed effects/ABI/Numba leaves/wrappers; measured standard routes use disclosed exact-IR specializations. | Existing languages already provide typed interfaces, specialization, and generation. | N2 Section 6 branch table and frozen M source | Implementation method, not new effect theory; specialization TCB; no arbitrary-lowerer claim. |
| `EVIDENCE-BOUNDED-VALIDATION` | Mutation, finite checking, sealed composition, two-generation exact-task measurements, and replayable recount support feasibility. | Does not decide novelty against other systems. | Existing M/E/F2 evidence and N2 classification | Finite scope, adverse results retained, no human study, no executed wrong-route witness, no formal semantics. |

## 6. Claims to retain, narrow, or delete

| Disposition | Claim |
| --- | --- |
| Retain, bounded | RTDL implements one route-level admission decision over five named seams for its supported finite families. |
| Retain, bounded | The accepted route identity is carried into per-route preparation and interface-specific publication checks. |
| Retain, implementation | General typed effects lower through a deterministic ABI and trusted wrappers; reported routes use disclosed exact-IR specializations. |
| Retain, evidence-only | With native-initialization overlap disabled, integrated projection mutations are rejected before the native-library loader. |
| Retain, evidence-only | Frozen two-generation results bound overhead only for the exact specialized prepared routes. |
| Narrow | Checked nearby primary sources do not document the same Q1-Q6 guarantee; several exact answers remain `UNKNOWN`. |
| Delete | Existing Python RT interfaces merely expose raw calls or cannot provide whole-route checks. |
| Delete | Validation-before-native-execution, typed effects, hashes, or protocol reasoning are new. |
| Delete | Every measured role executes through a Numba leaf and per-leaf effect-tag check. |
| Delete | Every public interface returns only after digest and detailed receipt validation. |
| Delete | The illustrative `(100,0),(101,1)` defective route was executed. |
| Delete | RTDL is first/only, proves semantic correctness, or supports arbitrary topology lowering. |

## 7. Cost and adverse-evidence disclosure

The canonical lowering plan is not executable. The sealed extension required
about 2,635 topology-specific LOC and compiler changes. Trusted semantic
schemas, exact-IR guards, wrapper generators, runtime/provider behavior, and
lifecycle checks form a sizable TCB. There is no independent human authoring or
prevalence evidence.

The performance evidence supports prepared-route overhead bounds for two exact
tasks on two NVIDIA generations. It does not show that generic Numba-leaf
execution has the same cost. All post-import A/C rows are adverse, including a
2.377129x worst block. Relative-to-E first-result medians regress about 8%--22%
at implementation entry and 16%--31% post-import; those comparisons are post
hoc and non-gating, and both endpoints are lifecycle/import-confounded. The
formal timed Arm-A population contains 4,096 calls but only 32 separate
post-loop detailed receipts. A-only instrumentation cannot qualify B/C.

The finite checker missed an early-return probe before repair, the double-fault
mock returned no public result, and the native-fork probe accepted a public call
through a mock native implementation without GPU work. Neither defect appeared
in retained successful GPU workers. These facts narrow the evidence; they do not
repair runtime defects.

## 8. N3 verdict

The work supports **one bounded compiler-systems design**, one concrete
implementation method, and finite evaluation evidence. It may be suitable for
CGO only if the manuscript states these exact boundaries and the P-triple-prime
bytes survive independent review. This author-side argument does not establish
novelty, authorize a claim, or support a new theory, arbitrary compiler,
universal Python RT safety, or categorical superiority over named systems.
