# Related-Work Capability and Guarantee Boundaries

Date checked: 2026-09-07 America/New_York. The 2026-09-06 audit and
P-triple-prime corrections are retained below except where this
P-quadruple-prime authoring pass explicitly narrows the comparison.

Status: `N1_PQUADRUPLEPRIME_RESULT_ROUTE_REMEDIATED__AUTHOR_SCOPE__INDEPENDENT_REVIEW_PENDING`.

This is a primary-source boundary audit for the CGO 2027 RTDL manuscript. It
does not prove novelty, authorize a claim, or report a new opponent experiment.
Its purpose is narrower: state what nearby systems already provide, identify
which exact obligations their authors document, and prevent absence of a
documented guarantee from being rewritten as inability.

## 1. Comparison question

The comparison is not whether another system can express an RT algorithm or
construct and launch an RT pipeline. Many can. The concrete question is whether
the cited source documents a mechanism that jointly admits one bounded RT
execution route by relating all of the following across its representations:

| Proposition | Obligation under comparison |
| --- | --- |
| `Q1_ROLE` | The callback roles present in the route and the effects each role may return agree with the generated ABI and topology. |
| `Q2_SEMANTIC_ABI` | A same-width payload or intersection attribute has the declared semantic producer and consumer, not merely a compatible machine type and offset. |
| `Q3_PHYSICAL` | Geometry, query projection, result shape, and reduction/collection contract agree with the selected physical lowerer. |
| `Q4_CONTINUATION` | Device failure and overflow state prevent incomplete output from becoming an application result. |
| `Q5_IDENTITY` | The checked program is tied to the generated and loaded executable bytes used by the admitted route. |
| `Q6_JOINT_ADMISSION` | The preceding relations are checked as one route-level admission condition before a materialized route is accepted and before its subsequent per-route preparation, launch, or result publication. Exact app-free native runtime loading or warming may precede admission. |

This formulation is intentionally narrower than a general safety theorem. It
does not ask whether a sufficiently careful application could implement the
same checks. It asks what guarantee the cited system itself documents and what
RTDL must still establish in its actual implementation.

### 1.1 Concrete result-route predicates

Q1--Q6 remain useful for auditing the full executable boundary, but they are
not by themselves the paper's incremental research claim. The central
comparison is now three concrete predicates induced by an observable result:

| Predicate | Concrete RTDL question | Implemented RTDL relation | Comparison discipline |
| --- | --- | --- | --- |
| `RR1_COMPLETE_EFFECT` | May a locally role-legal `IGNORE` or `TERMINATE` be used by the current route that promises a complete bounded relation? | The family verifier collects all any-hit returns and requires exactly `ACCEPT_CONTINUE`; capacity overflow is fail closed. | Compare with role/stage capability checks, but do not infer that another language cannot add a result predicate or that filtering is impossible in another complete-enumeration design. |
| `RR2_LOGICAL_PHYSICAL` | Does logical event acceptance mean that the hardware intersection should be physically accepted? | The triangle all-hit lowerer updates count/payload and then calls `optixIgnoreIntersection()`; geometry separately requires single any-hit delivery and reduction checks overflow. | The OptiX operations are established mechanisms. The possible increment is their explicit connection to a fixed result contract inside RTDL's trusted route, not invention of all-hit traversal. |
| `RR3_SPECIALIZATION_IDENTITY` | Can two callbacks with the same role/ABI shape but updates `+1` and `+2` use the same fixed count intrinsic? | No. An exact-IR guard selects the standard intrinsic; the existing `+1` to `+2` test remains front-end legal but switches to the general leaf path. | Compare with existing specialization systems while limiting evidence to one source-to-wrapper component test, not a general optimization theorem or GPU equivalence result. |

These predicates identify what the compiler must decide beyond ordinary
machine-width compatibility. They do not establish exclusivity. For each named
neighbor, a missing express statement remains `UNKNOWN` rather than evidence of
inability.

### 1.2 Direct comparison on the same predicates

| Near neighbor | Capability already established | Concrete RTDL remainder | Mandatory boundary |
| --- | --- | --- | --- |
| Proof-carrying code (PCC) | Consumer policy, producer-supplied proof, and validation before native execution. | RTDL instantiates fixed RT result predicates and trusted lowering/publication relations without a proof certificate. | Admission-before-execution is not new; RTDL is theoretically weaker and trusts compiler/runtime components. |
| Shader Components and Slang | Interfaces, composition, specialization, reflection, and current target/stage/API/hardware capability inference and validation. | `RR1` and `RR2` ask distinct result predicates: preservation of a complete result and interpretation of logical acceptance as a physical RT action. | Capability predicates do not automatically answer these result predicates, but this does not show that Slang cannot be extended to express them. |
| FFI checking and linking types | Rich cross-language representation and behavior relations, including offsets, tags, and effects. | RTDL supplies a narrow RT event/result/capacity/traversal-wrapper relation and binds it to one executable route. | Cross-representation semantic checking is not new; RTDL contributes no general linking type or soundness theorem. |

## 2. Evidence vocabulary

| Label | Meaning |
| --- | --- |
| `DOCUMENTED_CAPABILITY` | A primary source expressly describes the capability. |
| `AUTHOR_BOUNDARY` | A primary source expressly leaves a responsibility to an application, engine, developer, or target-specific layer. |
| `INFERENCE` | The conclusion follows from documented interfaces or examples but is not an express guarantee. It may not be written as a categorical negative. |
| `UNKNOWN` | The searched primary sources do not settle the exact proposition. Silence is not inability. |
| `NOT_SAME_Q` | The source proves or discusses a different property and cannot support a claim about Q1-Q6. |

Only `DOCUMENTED_CAPABILITY` and a scope-matched `AUTHOR_BOUNDARY` may support
direct capability/boundary wording. `UNKNOWN` and `INFERENCE` require qualified
paper wording. No row below supports "cannot," "impossible," "first," or
"unique."

## 3. RT APIs, bindings, and construction frameworks

| Evidence ID | System/source and checked version | Documented capability that the paper must acknowledge | Exact Q result | Remaining RTDL burden and permitted wording |
| --- | --- | --- | --- | --- |
| `RW-RT-01` | NVIDIA OptiX 9.0 Programming Guide, 2025 | OptiX supplies programmable RT stages, payload/attribute mechanisms, modules, program groups, pipelines, SBTs, acceleration structures, validation facilities, and launch APIs. | `Q1-Q5`: the API specifies many local structural and runtime validity conditions. The checked guide does not document RTDL's joint Q1-Q6 admission object. `Q6=UNKNOWN`. | Say that RTDL builds above OptiX and adopts its mechanisms. Do not imply OptiX lacks validation. The RTDL obligation is to demonstrate its additional route-level relation and its trusted lowerer boundary. |
| `RW-RT-02` | NVIDIA `otk-pyoptix`, repository and package metadata checked 2026-09-06; current package line 9.1 | The project describes complete Python bindings to the OptiX host API and ships examples using Python with CUDA-side compilation and array support. | `Q1-Q5`: inherited OptiX/API capabilities are available to Python. The repository description and examples do not state a Q1-Q6 whole-route semantic-admission guarantee. Exact result: `UNKNOWN`, not absent. | Permitted: "PyOptiX exposes the OptiX host API to Python; the checked materials do not specify the same joint admission guarantee." Forbidden: "PyOptiX cannot enforce it" or "PyOptiX only wraps calls." |
| `RW-RT-03` | OWL repository/README and simple example, checked 2026-09-06 | OWL is a productivity layer over OptiX. It manages substantial host construction, including objects, buffers, acceleration structures, program groups/pipeline/SBT state and launches. Its example still asks the user to supply programs and launch-facing data/setup. | Strong `DOCUMENTED_CAPABILITY` for construction automation. No checked source states Q2 semantic ownership plus Q4/Q5 as a single Q6 admission guarantee. `Q6=UNKNOWN`; some responsibilities are explicit `AUTHOR_BOUNDARY`. | Acknowledge OWL's SBT and pipeline management. Compare only the additional protocol relation RTDL attempts, not boilerplate volume. |
| `RW-RT-04` | Microsoft DXR functional specification, current page checked 2026-09-06, payload access qualifiers section | PAQs declare per-stage read/write semantics, and the compiler enforces declaration-level predecessor/successor rules. This is a strong existing role/payload capability relevant to Q1 and part of Q2. | The spec says local shader copies are not access-restricted and assigns developers responsibility for honoring PAQs; the compiler attempts warnings. That is an `AUTHOR_BOUNDARY`, not absence of all checks. The checked section does not bind application-level semantic names, executable byte identity, and result continuation into Q6. | RTDL must explain the increment over PAQs: its bounded route connects declared role effects to a generated ABI and to selected physical/result/identity facts. It must not claim to invent stage-indexed payload checking. |
| `RW-RT-05` | Khronos Vulkan specification, current shader-interface and ray-tracing chapters checked 2026-09-06 | Vulkan defines extensive shader-interface, pipeline, SBT alignment, range, address, and indexing validity rules. | The RT chapter states that the application allocates/manages SBT buffers and must arrange records so indexing reaches correct entries. This supports an application responsibility for that exact mapping while preserving Vulkan's many structural guarantees. It does not settle all Q1-Q6. | Use Vulkan as evidence that local interface validity and application-owned cross-object organization coexist. Do not call Vulkan unchecked or unsafe. |

## 4. Shader languages, staged systems, and cross-platform frameworks

| Evidence ID | System/source and checked version | Documented capability that the paper must acknowledge | Exact Q result | Remaining RTDL burden and permitted wording |
| --- | --- | --- | --- | --- |
| `RW-SC-01` | Shader Components, TOG 2017 | First-class shader components encapsulate logic and parameters; the compiler performs static interface checking, specialization, and parameter-block layout work. | Strong component/interface precedent for Q1/Q3-like local relations. The paper leaves component-instance/variant caching and lookup policy to the engine. It does not document RTDL's exact Q2/Q4/Q5/Q6 object. | RTDL cannot claim component composition or static shader interfaces as new. It may compare the admitted unit: a bounded RT route crossing callback IR, physical schema, generated wrapper, loaded bytes, and public result. |
| `RW-SC-02` | Slang, TOG 2018 | Slang provides modules, generics with interface constraints, associated types, extensions, static specialization, reflection, and compiler services for extensible shading systems. | These are strong language and interface mechanisms. The 2018 paper does not establish the exact joint Q1-Q6 guarantee. `Q6=UNKNOWN`. | State the narrower increment, if retained, as protocol admission across representations rather than modularity, generics, or reflection. |
| `RW-SC-03` | Current Slang capability documentation, stable documentation checked 2026-09-06 | Slang capability requirements describe target, stage, API, and hardware constraints; requirements can be inferred and validated through public/interface methods and entry points. | Strong existing capability checking directly overlaps parts of Q1/Q3. The checked documentation does not describe application semantic ownership for same-width hit attributes or exact loaded-executable/result-publication admission. `Q2/Q4/Q5/Q6=UNKNOWN`. | The manuscript must acknowledge current Slang, not infer present limitations from the 2018 paper. RTDL must identify the concrete additional relation, not say "Slang leaves compatibility to users." |
| `RW-SC-04` | Slang Shader Cursors documentation, current stable page checked 2026-09-06 | Reflection supplies target-specific type/layout information; shader cursors and parameter blocks support composable, cross-platform parameter binding without duplicating target-specific application logic. | Strong capability for physical layout/navigation. The guide presents an application/engine policy and implementation pattern; it does not claim to enforce the application's whole RT architecture or Q1-Q6. | Acknowledge that reflection and cursors solve substantial layout/binding work. RTDL's claimed increment, if any, is not cursor-based binding but admission of selected semantic/physical/continuation/identity relations. |
| `RW-SC-05` | SlangPy v0.43.1 release, exact source commit `2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248`, plus dynamic stable API/changelog pages checked 2026-09-07 | SlangPy offers a high-level Python API, reflection-based marshalling and binding, ray-tracing pipelines, hit groups, shader tables, ray dispatch, module/shader/pipeline caching facilities, and device lifecycle/error-handling hooks. | Strong Python, RT construction, binding, caching, and lifecycle capabilities. The checked materials do not expressly establish or deny Q1-Q6 as one guarantee. Exact result: `UNKNOWN`. | Do not claim RTDL is the first Python route to hardware RT, that SlangPy is merely compute-only, or that its existing checks are absent. The paper may say the checked materials do not specify the same bounded route-level admission contract. |
| `RW-SC-06` | LuisaRender, TOG 2022, especially Sections 3.2, 4.5, 6.1; LuisaCompute official repository checked 2026-09-06 | Luisa provides an embedded typed DSL, unified resource runtime, multiple backends, resource-use analysis, dependency scheduling, and automatic RT pipeline/SBT/parameter/launch construction. A Python frontend is present in the current repository. | Strong staged generation, runtime, and RT automation. No matched primary-source statement was found for Q2 semantic-owner comparison plus Q4/Q5/Q6. Exact result: `UNKNOWN`. | Explicitly concede automatic RT construction. The possible RTDL increment is the represented admission relation, not pipeline generation or Python embedding. |
| `RW-SC-07` | Dr.Jit, TOG 2022 | Dr.Jit traces Python/C++ computations, including control flow, polymorphism, ray intersection and scene dependencies, and compiles/optimizes them through LLVM/OptiX. | Strong whole-program staging and dependency capture. Its differentiation caveats concern differentiable algorithms and are `NOT_SAME_Q`; they cannot evidence an RTDL gap. The checked paper does not settle exact Q1-Q6. | Compare compiler object and guarantee, not language breadth. RTDL is substantially less general; any claim must be about the bounded protocol relation it checks. |
| `RW-SC-08` | CrossRT arXiv:2409.12617v1, 2024 | CrossRT transforms C++ classes into cross-platform host/device RT code and applies pattern-directed and algorithmic optimizations. It supports user extension and reports performance comparable to expert implementations. | Strong generation and optimization capability. Sections on extension and debugging describe user-modifiable generated code but do not prove absence of Q1-Q6. Exact guarantee remains `UNKNOWN`. | Acknowledge CrossRT's broader cross-platform generation. The manuscript may contrast RTDL's fail-closed admitted route only as a documented design difference, not superiority or impossibility. |

### 4.1 SlangPy v0.43.1 capability recheck

The earlier 2026-09-06 audit recorded version 0.42.0 from a dynamic
documentation page. That historical observation is preserved but superseded
for the candidate by the fixed v0.43.1 release and source identity above. The
stable documentation is a separately dated, mutable source; it is not claimed
to be an immutable rendering of that tag.

| Capability group | Primary-source result | What remains unknown for Q1-Q6 |
| --- | --- | --- |
| RT pipeline, hit groups, shader table, dispatch | The stable API documents ray-tracing-pipeline creation with hit groups and payload/attribute sizes, shader-table creation and binding, ray-tracing pass encoding, and ray dispatch. | The checked API does not state that these objects participate in RTDL's exact joint route-admission relation. |
| Reflection, marshalling, binding | The API exposes reflection cursors and type layouts; the v0.43.0 changelog records a native reflection/binding/tensor overhaul and value conversion/marshalling work inherited by v0.43.1. | These substantial checks do not by themselves settle application semantic ownership, continuation, executable identity, or their joint admission. |
| Module, shader, pipeline cache and identity scope | The v0.43.0 changelog records `CacheWriter`, module caching, and persistent shader/pipeline caching, plus compilation reports. | Cache presence and compilation reporting do not establish the exact Q5 executable-identity relation or Q6 joint guarantee; those propositions remain `UNKNOWN`. |
| Device callbacks and lifecycle/error handling | The API documents device-close callbacks; the v0.43.0 changelog records close/stack cleanup, cached-reflection-layout leak repair, device recording IDs, and an error for reuse of a finished command encoder. | These are positive lifecycle facilities, not evidence for or against the full Q1-Q6 route contract. |

## 5. Protocol, state, and linking research

| Evidence ID | Work | What it already establishes | Relation to RTDL | Required manuscript boundary |
| --- | --- | --- | --- | --- |
| `RW-PT-01` | Strom and Yemini, Typestate, 1986 | A type can be refined by abstract object state so that semantically undefined operation sequences are detected statically. | Typestate can model multi-step object protocols; it is false to dismiss it as checking only ordinary value types or one operation. RTDL makes a concrete engineering choice to encode a bounded RT route's cross-artifact facts and enforce checks at materialization/preparation/publication boundaries. | Describe typestate as conceptual foundation. Do not claim a new general state system or soundness theorem. |
| `RW-PT-02` | de Alfaro and Henzinger, Interface Automata, 2001 | Component compatibility is defined relative to environments, with alternating refinement and algorithmic checks. | This is stronger formal compatibility theory than RTDL provides. RTDL has deterministic equality checks over a finite route projection, not a new compatibility calculus. | Claim implementation/design specialization only. |
| `RW-PT-03` | Honda, Yoshida, and Carbone, Multiparty Asynchronous Session Types, 2016 | A global protocol can be projected to communicating participants with safety/progress/fidelity results. | This is a close conceptual precedent for global-to-local role agreement. RTDL does not prove projection soundness or general communication progress; its target facts are separately derived in one compiler and checked for a fixed set of seams. | Use "inspired by" or "related to," not "generalizes" or "solves session typing for RT." |
| `RW-PT-04` | Patterson and Ahmed, Linking Types, 2017 | Linking types express cross-language boundary behavior that ordinary source types may not capture. | This directly weakens any claim that cross-representation constraints are unprecedented. RTDL's possible increment is the concrete set of RT objects connected in an executable admission workflow, not the idea of typed linking. | Acknowledge that richer linking contracts already exist; no general linking theorem is claimed. |
| `RW-PT-05` | Furr and Foster, FFI type checking, PLDI 2005 | Multi-language type inference relates OCaml and C representations, including offsets, tags, and GC effects, with soundness for a restricted subset. | Physical representation and semantic boundary checks already have strong precedents. RTDL adds a domain-specific relation among RT role/effect, attribute ownership, physical plan, continuation, and executable identity, but offers weaker theory. | Do not claim that existing FFI work checks only widths or cannot express semantics. |
| `RW-PT-06` | Necula and Lee, proof-carrying code, OSDI 1996 | A code producer supplies native code and a safety proof against a consumer-defined policy; the consumer validates the proof before executing the code. | This is a direct precedent for policy-based admission before native execution. RTDL supplies no proof certificate: trusted schemas, compiler projections, topology lowerers, and runtime checks implement a bounded domain-specific relation, while hashes establish identity rather than semantics. | Do not claim validation-before-execution as new. Position RTDL as one concrete RT protocol design and implementation with finite evidence, not as a general proof system. |

## 6. Corrected use of the RT-core survey

`RW-BG-01`: Meneses et al., *Ray Tracing Cores for General-Purpose
Computing*, surveys workloads, mappings, and conditions under which RT hardware
can be profitable. RTDL does not automatically discover a profitable mapping.
The survey's omission of a programming abstraction is not evidence that such an
abstraction is absent, nor evidence for RTDL novelty. It may be cited only for
application/mapping background. The contrary recommendation in the historical
Goal5794 review is superseded for the current manuscript; the historical file
itself remains unchanged.

## 7. Proposition disposition

| Proposed manuscript proposition | Result after primary-source audit | Paper action |
| --- | --- | --- |
| Existing Python interfaces make RT callable but do not establish a whole admitted execution. | Too categorical. PyOptiX and SlangPy capabilities are documented; the exact whole-route guarantee is not settled by checked materials. | Replace with scoped source statement: the checked documentation does not specify the same Q1-Q6 guarantee. |
| Existing frameworks leave pipeline/SBT work to users. | False as a general statement. OWL and Luisa automate substantial pipeline/SBT work; Slang/SlangPy also expose strong facilities. | Delete. Explicitly acknowledge these capabilities. |
| Existing shader types do not check cross-stage payload behavior. | False. DXR PAQs and Slang capabilities check important stage/target relations. | Delete. Identify the same-width application semantic-owner relation and whole-route admission increment instead. |
| Typestate handles only one object, so it cannot address RT protocols. | False and unnecessary. | Delete. Treat typestate/interface/session systems as formal antecedents and narrow RTDL to a domain-specific implementation method. |
| Typed linking and FFI check only machine layouts. | False/unsupported. | Delete. Acknowledge richer cross-language relations and state that RTDL specializes the concrete RT artifact set without a new theorem. |
| No existing work can implement an equivalent mechanism. | Unsupported and not required. | Prohibit. Ordinary code or another compiler could implement equivalent checks. |
| The checked systems' primary materials do not document the same fixed RT result-route relation. | Supported only as a source-bounded observation over RR1--RR3 and Q1--Q6, with several exact results still `UNKNOWN`. | Retain with named sources, checked versions, and no exclusivity implication. |
| Validation of a producer-supplied native program before execution is new. | False. Proof-carrying code is a direct policy-and-validation precedent. | Delete. State that RTDL has no proof certificate and contributes only its bounded RT-specific representation, enforcement points, implementation, and finite evidence. |

## 8. Source cards and search record

All sources below are primary author, standards-body, official project, or
publisher records. Access date is 2026-09-06 unless a row says 2026-09-07 or a
publication date is shown.
The audit used source claims rather than third-party summaries.

| Card | Primary source | Selected context | Use/exclusion decision |
| --- | --- | --- | --- |
| `SC-01` | [NVIDIA OptiX 9.0 Programming Guide](https://raytracing-docs.nvidia.com/optix9/guide/optix_guide.250130.A4.pdf) | Pipeline, SBT, payload, attributes, validation, launch | Selected for API capabilities; not used as a novelty authority. |
| `SC-02` | [NVIDIA otk-pyoptix](https://github.com/NVIDIA/otk-pyoptix) | Project description, package metadata, examples/dependencies | Selected for current Python binding scope. Repository silence on Q6 is `UNKNOWN`. |
| `SC-03` | [OWL repository](https://github.com/NVIDIA/OWL) | README and simple example | Selected for construction automation and documented user inputs. |
| `SC-04` | [DXR functional specification](https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html) | Payload access qualifiers, local working copy, compiler checks | Selected for strong existing stage/payload guarantees and explicit developer boundary. |
| `SC-05` | [Vulkan shader interfaces](https://docs.vulkan.org/spec/latest/chapters/interfaces.html) and [ray tracing](https://docs.vulkan.org/spec/latest/chapters/raytracing.html) | Interface matching and SBT validity/indexing | Selected for structural guarantees and SBT organization responsibility. |
| `SC-06` | [Shader Components project/paper](https://graphics.cs.cmu.edu/projects/shadercomp/) | Component interfaces, specialization, parameter blocks | Selected as a close compiler-unit precedent. |
| `SC-07` | [Slang 2018 paper](https://graphics.cs.cmu.edu/projects/slang/he18_slang.pdf) | Generics, interfaces, modules, reflection, specialization | Selected for historical language mechanisms. |
| `SC-08` | [Current Slang capabilities](https://docs.shader-slang.org/en/stable/external/slang/docs/user-guide/05-capabilities.html) | Requirement inference and target/stage/API validation | Selected; prevents stale limitations inferred from 2018. |
| `SC-09` | [Slang Shader Cursors](https://docs.shader-slang.org/en/stable/shader-cursors.html) | Reflection-driven cross-platform binding and parameter blocks | Selected for current layout/binding capabilities and policy boundary. |
| `SC-10A` | [SlangPy v0.43.1 release](https://github.com/shader-slang/slangpy/releases/tag/v0.43.1) and [exact source commit](https://github.com/shader-slang/slangpy/commit/2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248) | Fixed candidate-comparison version/source identity; checked 2026-09-07 | Selected as version identity. The v0.43.1 release is a wheel-availability patch, so inherited capabilities were checked in the v0.43.0 changelog and stable API rather than inferred from this release note alone. |
| `SC-10B` | [SlangPy stable API reference](https://slangpy.shader-slang.org/en/stable/src/api_reference.html) and [v0.43.0 changelog](https://slangpy.shader-slang.org/en/stable/changelog.html#version-0-43-0-july-13-2026) | RT pipeline/hit-group/SBT/dispatch; reflection/marshalling/binding; caches; lifecycle/error handling; checked 2026-09-07 | Selected as dynamic official documentation, not represented as immutable v0.43.1-tag documentation. Exact joint Q1-Q6 remains `UNKNOWN`. |
| `SC-11` | [LuisaRender paper](https://luisa-render.com/static/paper/paper.pdf) and [LuisaCompute repository](https://github.com/LuisaGroup/LuisaCompute) | Typed DSL, runtime, dependencies, RT construction, Python frontend | Selected; automatic RT construction must be conceded. |
| `SC-12` | [Dr.Jit paper](https://d38rqfq1h7iukm.cloudfront.net/media/papers/Jakob2022DrJit.pdf) | Whole-computation tracing, OptiX lowering, dependency capture | Selected; differentiation limitation excluded as `NOT_SAME_Q`. |
| `SC-13` | [CrossRT v1](https://arxiv.org/abs/2409.12617v1) | Cross-platform host/device generation, optimization, extension | Selected; no categorical negative inferred. |
| `SC-14` | [IBM Typestate record](https://research.ibm.com/publications/typestate-a-programming-language-concept-for-enhancing-software-reliability) | State-refined types and operation-sequence checks | Selected as formal antecedent. |
| `SC-15` | [Interface Automata author-institution record](https://research-explorer.ista.ac.at/record/4622) | Environment-relative component compatibility | Selected as formal antecedent. |
| `SC-16` | [Multiparty asynchronous session types author-institution record](https://pure.itu.dk/en/publications/multiparty-asynchronous-session-types/) | Global protocol projection and formal results | Selected as formal antecedent. |
| `SC-17` | [Linking Types paper](https://dbp.io/pubs/2017/linking-types-snapl.pdf) | Types for cross-language linking behavior | Selected as cross-representation antecedent. |
| `SC-18` | [FFI type-checking paper](https://www.cs.tufts.edu/~jfoster/papers/cs-tr-4627.pdf) | Cross-language representation/GC reasoning | Selected as physical/semantic boundary antecedent. |
| `SC-19` | [RT-core survey](https://arxiv.org/abs/2603.28771v1) | Application mappings and profitability | Background only; excluded from novelty-gap evidence. |
| `SC-20` | [Necula and Lee OSDI 1996 paper, Section 2](https://www.usenix.org/legacy/publications/library/proceedings/osdi96/full_papers/necula/html/node2.html) and [USENIX record](https://www.usenix.org/conference/osdi-96/safe-kernel-extensions-without-run-time-checking) | Consumer policy, producer-supplied proof, consumer-side proof validation before native execution | Selected as a direct admission-method precedent. It does not establish RTDL's particular RT relation, and RTDL does not provide proof-carrying code. |

## 9. Quotation and inference audit

This document intentionally paraphrases almost all source text. The only short
source phrases reproduced verbatim are project/specification labels or snippets
well below 25 words per source. No negative claim is inferred from silence.
Dynamic documentation is identified as documentation rather than peer-reviewed
publication. Current-system observations are not projected backward into older
papers, and old non-goals are not projected forward into current systems.

## 10. N1 conclusion

N1 supports a narrower, defensible problem statement, not an exclusivity claim.
Nearby systems and prior methods already provide Python access, RT construction,
shader modularity, reflection/layout support, capability checks, staged
generation, formal models of protocols and linking, and proof-validated native
code admission. The paper's concrete remainder is the implemented connection
from fixed RT output obligations to admissible effects, physical traversal
interpretation, specialization selection, and fail-closed publication. The
checked primary sources do not state this same bounded result-route contract,
but for several systems that result is `UNKNOWN`, not a demonstrated absence.
RTDL must therefore earn its contribution through the source-traced W1--W3
relations in N2 and the bounded implementation/evidence argument in N3.
