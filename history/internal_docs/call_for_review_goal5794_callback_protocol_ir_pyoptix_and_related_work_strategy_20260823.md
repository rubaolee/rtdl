# Call for external review — Goal5794 Callback-Protocol IR, PyOptiX comparison, and CGO execution plan

Date: 2026-08-23  
Review type: adversarial academic-contribution, baseline-fairness, and execution-plan review  
Target: CGO 2027 second round, standard research paper  
Paper deadline: 2026-09-10  
Requested reviewer posture: skeptical compiler/systems reviewer familiar with GPU and ray-tracing systems

**SEND ONLY THIS FILE FOR THIS REVIEW CYCLE.** Do not send a packet, archive, second Markdown file, or supporting attachment. This CFR is self-contained for a **strategy and gate review**; it is not evidence that the implemented Callback-Protocol IR has already passed artifact-level scientific review. No supporting artifact is incorporated by reference into this review. Local custody paths recorded near the end are not external evidence and must not be sent.

## Requested ruling

Return P0/P1/P2/P3 counts, answer every numbered question, and choose exactly one scoped disposition.

**Evidence-sufficiency rule.** This one-file review may approve or reject the proposed evidence path, but it may not certify that the implemented RTDL core already realizes the stated contribution. Unless an exact, independently accessible source artifact is supplied in a later review, Questions 1–3 and 9–14 must be answered `NOT_REVIEWABLE` for implementation truth, with a separate assessment of whether their proposed tests would be sufficient. `APPROVE` in this CFR therefore means only that the plan is credible to execute; it does not authorize the paper's core-contribution claim or submission.

Preferred favorable disposition:

```text
APPROVE_PLAN_FOR_GOALS5794_TO_5798
__CALLBACK_PROTOCOL_IR_IS_PLAUSIBLE_BUT_UNPROVEN
__IMPLEMENTATION_AND_MATCHED_EVIDENCE_REVIEW_REMAIN_REQUIRED
__CURRENT_PYOPTIX_MUST_BE_THE_ENGINEERING_BASELINE
__PUBLIC_API_MATCHED_TASKS_AND_EXECUTABLE_ABLATIONS_ARE_SUBMISSION_GATES
__SUBMISSION_NOT_YET_AUTHORIZED
```

or:

```text
APPROVE_WITH_CONDITIONS
```

with exact closure conditions, or:

```text
REJECT_CORE_POSITIONING
```

with a falsifiable explanation of whether RTDL is merely a narrower PyOptiX wrapper/validation layer, duplicates a cited abstraction, or lacks an evaluable compiler contribution.

This is not a request to praise research-process governance. The requested judgment is whether the system can still produce a real CGO contribution and whether the proposed work is the shortest way to prove it.

## 1. Proposed core contribution

The paper must not center on Python-to-OptiX, the number of applications, prior V2/V4 performance, or a claim to decide whether arbitrary new applications map to ray tracing. The proposed core is:

> **For its admitted bounded subset, RTDL introduces a Callback-Protocol IR that makes a complete traversal-driven protocol—not an individual kernel or shader—the unit of high-level compilation. It closes declared callback roles, cross-role effects, payload/attribute ABI and ownership, declared physical-geometry configuration obligations, trusted wrapper/pipeline/SBT composition, post-traversal continuation, device failure status, resource bounds, and executable identity before generating the supported OptiX composition. The application retains ownership of its algorithm, semantic oracle, and declared trusted physical partners.**

Here, “physical” means compatibility of the declared protocol with the selected custom-AABB or built-in-triangle realization. It does **not** mean that RTDL proves the selected geometry encodes the developer's intended algorithm.

The engineering distinction from PyOptiX is intentionally narrower:

> **PyOptiX exposes the mechanisms required to build the application; RTDL changes who owns the callback protocol, moving specified cross-callback obligations from application code to compiler validation and generation.**

This wording concedes that a capable programmer can implement the same repurposed applications directly with PyOptiX/OptiX. The claimed value is not possibility; it is a compiler abstraction that makes distributed protocol seams explicit, checked, and generated.

## 2. Problem being solved

In a repurposed ray-tracing application, the computation is distributed across host-side geometry and pipeline construction, multiple OptiX programs, payload/attribute encodings, traversal behavior, device status, and host continuation. Local Python, CUDA, shader, or API legality does not by itself establish that these pieces implement one coherent non-rendering computation.

Examples of whole-protocol defects include:

- one role failing to produce state required by a downstream role;
- producer and consumer assigning different types or meanings to the same payload/attribute slot;
- callback assumptions disagreeing with custom-AABB or built-in-triangle physical setup;
- device failure or incomplete output being consumed as a valid application result;
- a checked IR/certificate being paired with a different executable callback program.

RTDL does not claim to discover an arbitrary algorithm-to-ray-tracing mapping. Its bounded problem is: once a developer has chosen a traversal formulation, make the complete callback protocol a compiler-owned contract and fail closed before launch when that contract is not closed.

## 3. Actual RTDL mechanism and scope

RTDL defines seven **language roles**:

`bounds`, `make_ray`, `intersection`, `any_hit`, `closest_hit`, `miss`, and `finalize`.

These are not seven OptiX callback entry points. Actual OptiX entry roles are raygen, intersection, any-hit, closest-hit, and miss; a trusted raygen wrapper invokes language leaves and owns the trace/finalization boundary.

The following describes the current internal mechanism; it is **not** a claim that every listed mechanism is already reachable through the stable public GPU lifecycle. The implemented IR includes closed role effects, typed ABI, payload/attribute ownership, fail-closed verification, CPU reference semantics, and explicit resource ceilings. The current ceilings include 32 payload slots, 8 attribute slots, trace depth 1, and callable depth 0. Physical realization currently covers two OptiX geometry mechanisms—custom AABBs and built-in triangles—not two claimed application families. The verifier does not prove arbitrary user logic globally confluent, order-independent, or semantically correct.

The intended pipeline is:

```text
restricted source
  -> parse and typed/effect IR
  -> protocol and physical validation
  -> compiler-generated device leaves and trusted wrapper
  -> module/program groups/pipeline/SBT/GAS materialization
  -> prepared execution
  -> checked device status
  -> application continuation
```

## 4. Current evidence and hard limitations

The following facts are disclosed rather than converted into broad claims:

1. V4 has exact-output and behaviorally true-OptiX evidence across 9 applications and 13 paper lanes.
2. The final Goal5785 modern-RTX cohort contains 464/464 exact and behaviorally true-OptiX workers over 34 independent V2-direct/V4 rows.
3. By the registered row-local median criterion, V4 passes 16/34 and fails 18/34; cold is 4/15 and prepared is 12/19. By 95% CI classification, there are 11 clear V4 wins, 10 clear V4 losses, and 13 uncertain rows. Preparation is reported separately and is not free.
4. Those measurements compare V2-direct with V4. They are **not** a PyOptiX comparison and cannot support a PyOptiX performance claim.
5. The Goal5789 registered-lane semantic/physical inventory is 6 `COMPATIBLE`, 9 fail-closed `UNKNOWN`, and 0 `INCOMPATIBLE`. All 15 are target-capable and instance-admissible; the nine UNKNOWN rows lack independent semantic authority and retain physical/composition gaps. This is not a performance result or nine failed functional lanes.
6. Callback authority binding establishes exact program identity/projection, not semantic correctness. Particle and RTXRMQ once carried byte-identical callback programs.
7. A historical checker accepted emptied `roles[].effects` after resealing until a hostile audit exposed and repaired the inert leaf. Field presence and certificate seals therefore cannot substitute for mechanism ablation.
8. The current stable `rtdsl.v4` authoring surface exposes parse/verify, CPU role execution, ABI, and proof facilities. Generic GPU `materialize -> prepare -> execute -> close` remains outside the stable callback-authoring namespace; current prepared-provider routes are advanced/internal.
9. Source-backed responsibility evidence exists for all nine applications, but registered-interface loader encapsulation is 8/9. RayDB is the private `_load_optix_library` exception. It is an interface-hygiene exception, not evidence that RayDB manually constructs its pipeline/SBT.
10. Prospective new-problem generalization exams remain 0. Goal5793 stopped under its frozen no-repair/no-rerun rule after one live-provider response violated its frozen source-URL parser. This is an honesty disclosure, not generalization evidence or the paper contribution.
11. Usability studies, developer-time studies, and functionally matched PyOptiX/CUDA/OptiX baselines are all 0. No easier/simpler/less-code/more-productive claim is allowed.

## 5. Engineering baseline: current NVIDIA PyOptiX

The baseline must be the current official NVIDIA PyOptiX, not an obsolete or weakened proxy. As accessed on 2026-08-23, NVIDIA's `otk-pyoptix` repository describes itself as complete Python bindings for the OptiX host API and documents direct installation of OptiX 9.1 bindings with `pip install pyoptix`. Its exact commit, package artifact, dependencies, and supported device-authoring path have not yet been frozen; doing so is Goal5794.

NVIDIA's 2022 PyOptiX/Numba demonstration already showed Python-authored ray-generation, closest-hit, and miss programs and Python/Numba device lowering. RTDL therefore makes no first-Python, first-Python-callback, first-Python-to-PTX, or “PyOptiX cannot express repurposed applications” claim.

The fair comparison must preserve PyOptiX's advantages:

| Dimension | PyOptiX | RTDL hypothesis to test |
|---|---|---|
| Host API breadth | Complete/broad OptiX host mechanism access | Deliberately bounded public protocol API |
| Pipeline ownership | The proposed direct PyOptiX baseline makes modules, program groups, pipeline, SBT, GAS, and launch application-owned | Compiler validates and generates the supported composition |
| Callback seam ownership | The proposed direct PyOptiX baseline makes payload/attribute/SBT/trace contracts application-owned | IR closes roles, effects, ABI, ownership, physical/status/continuation contracts for admitted compositions |
| Extensibility | Broad, close to OptiX | Narrow; unsupported protocols must fail closed |
| Performance | Unknown for matched tasks | Must be measured without assuming superiority |
| Usability | No matched user study | No usability claim; only source-backed responsibility transfer |

The paper does not assume PyOptiX cannot implement the tasks; Goal5794 must establish that the frozen current baseline runs both matched tasks. The decisive engineering question is whether RTDL demonstrably removes specified cross-callback responsibilities while preserving correctness and reasonable, fully disclosed lifecycle costs.

## 6. Non-hostile academic positioning

### Slang

Slang's published capability system infers and enforces requirements over code-generation targets, shader stages, API extensions, and hardware features. Slang also supports an OptiX target. RTDL does not claim target-capability novelty and may use Slang as a leaf compiler.

The scoped difference is: Slang's published capability abstraction decides whether shader code is legal for a target/stage; it does not by itself establish RTDL's whole non-rendering callback/payload/SBT/status/continuation protocol as the unit of compilation.

### Dr.Jit

Dr.Jit traces high-level physically based rendering code, globally simplifies and specializes the resulting program, tracks dependencies, and JIT-compiles data-parallel CPU/GPU kernels. RTDL does not claim Dr.Jit-style global tracing, optimization, differentiation, or rendering performance.

The scoped difference is: Dr.Jit's published unit is traced rendering computation optimized as a whole; RTDL's unit is an explicit, restricted callback protocol whose cross-role obligations are closed before OptiX composition.

### CrossRT

CrossRT is the closest algorithmic threat and must not be dismissed as traditional rendering only. It translates hardware-agnostic object-oriented C++ algorithms to different ray-tracing APIs/hardware, supports CPU/GPU fallbacks and megakernel/wavefront forms, and evaluates BVH, SDF, Gaussian-splatting, and path-tracing tasks.

RTDL does not claim automatic mapping discovery, cross-platform translation, or expert-code performance. The scoped difference is: CrossRT addresses algorithm-to-backend translation; RTDL proposes a restricted callback-protocol IR that a translator or human could target, with compiler-owned cross-role effects, ABI, physical binding, failure status, continuation, and executable identity.

### Allowed related-work sentence

> Their cited published abstractions do not establish this compiler-owned non-graphics callback-protocol contract; RTDL must demonstrate the additional contract layer empirically.

The paper must not replace this with an absolute statement that Slang, Dr.Jit, CrossRT, or PyOptiX “cannot solve” the problem in principle.

## 7. Proposed evaluation

### 7.1 Two matched non-rendering tasks

Before implementation or formal timing, freeze two tasks that both systems can reasonably express:

1. **Custom-AABB spatial relation/count.** This exercises application-defined bounds, ray construction, intersection/effect behavior, status, and finalization.
2. **Built-in-triangle query/reduction.** This exercises a different physical geometry path, built-in attributes/hit processing, reduction/continuation, and lifecycle.

Both implementations must share the exact algorithm, inputs, precision, tie-break, resource budget, output schema, and independent CPU oracle. The tasks must not be chosen because PyOptiX lacks a needed feature. PyOptiX code must follow normal OptiX/PyOptiX practice and retain its complete host/device implementation, build options, pipeline/SBT/GAS structure, and version pins.

Neither task is an unseen, held-out, or prospective-generalization exam. They are matched mechanism and engineering case studies and may not be used to claim an arbitrary-new-application success rate.

RTDL implementations must use only the new stable public Callback-Protocol lifecycle API. No research Paper-App module, private loader, advanced/internal provider, hand-written PTX, or manual SBT/pipeline escape is allowed.

### 7.2 Responsibility-transfer evaluation

Raw LOC is not a primary metric. Use a preregistered source-backed rubric that counts and locates:

- user-authored callback role definitions;
- payload/attribute ABI declarations and packing;
- cross-role state/effect contracts;
- GAS/program-group/pipeline/SBT composition;
- lifecycle transitions;
- failure propagation;
- post-traversal continuation coordination;
- source-to-executable identity checks;
- compiler validators and generated code that replace each responsibility;
- unsupported cases and internal escapes.

Every “RTDL compiler-owned” entry must point to a validator or generator. Every “PyOptiX user-owned” entry must point to baseline source. This measures responsibility transfer, not subjective ease.

### 7.3 Executable mechanism ablation

Evaluate five single-factor mechanisms on the same matched tasks:

1. role/effect closure;
2. payload/attribute ABI and ownership;
3. physical wrapper/geometry binding;
4. device status and continuation ordering;
5. checked-program/executable identity binding.

For each mechanism, full RTDL must reject a concrete protocol violation before launch; the ablated system must accept the same invalid program and expose an attributable wrong result, failure, or invariant violation. A nearby valid control must remain accepted, preventing a reject-all checker from passing. Only the named mechanism may change. Digest-only mismatch cases are not sufficient evidence of semantic value.

Also report false rejection of valid controls, diagnostic specificity, compile/preparation cost, prepared runtime overhead, and the remaining TCB.

### 7.4 Matched performance

Run both systems on the same preregistered designated Linux host, not WSL, with the same GPU, driver, OptiX/CUDA versions, inputs, and oracle. Freeze the exact host identity in the environment manifest together with exact PyOptiX and RTDL sources, IR, generated PTX/native, flags, ordering, timer definitions, and raw-output schema before worker zero.

Report separately:

- fresh-process cold end to end;
- compilation/module/program-group/pipeline/GAS preparation;
- prepared execution;
- peak and steady-state memory;
- validation/code-generation overhead.

Preparation is not free and may not be hidden on either side. Incorrect outputs are correctness failures, not timing samples. Report all unfavorable or mixed results. A PyOptiX win does not refute the abstraction contribution, but it fixes the performance cost the paper must disclose.

## 8. Goals and dates

The 2026-09-03 through 2026-09-09 interval is reserved for paper writing; 2026-09-10 is the owner-controlled submission day.

| Goal | Dates | Required output | Hard gate |
|---|---|---|---|
| Goal5794 | Aug 23–24 | exact current PyOptiX/environment freeze, official smoke, matched-task spec, responsibility rubric, timing preregistration | no formal timing; both tasks fair and expressible |
| Goal5795 | Aug 24–26 | stable public RTDL `parse/verify -> materialize -> prepare -> execute -> close` API | no private/internal/provider/PTX/SBT escape in matched tasks |
| Goal5796 | Aug 26–28 | two exact RTDL/PyOptiX implementations, independent oracle, source-backed capability/responsibility matrix | both tasks exact on both systems |
| Goal5797 | Aug 29–31 | five single-factor executable mechanism ablations plus valid controls | both public-API implementations are frozen; no field-count/digest-only substitute |
| Goal5798 | Sep 1–2 | lifecycle-separated matched performance, memory, raw evidence, independent recount | all ablations complete; fair baseline; all unfavorable results retained |
| Goal5799 | Sep 3–10 | 11-page self-contained standard research paper, artifact, final claim review, owner upload | final evidence review returns by Sep 3; evidence freeze then; no new generalization search or performance tuning |

After this strategy review, two external checkpoints are required and deadline-bound: a **pre-timing design checkpoint** after the public API, matched-task implementations/specification, and baseline freeze; and a **final evidence/claim checkpoint** after all ablations and matched measurements. If either review is not returned by its stated gate, the affected formal step or submission is `NO_GO`; silence is not approval. Each checkpoint uses one self-contained CFR. Routine implementation and testing should not trigger serial review rounds unless they change the scientific question, baseline, algorithm, dataset, timer, or claim ceiling.

## 9. September 3 go/no-go gate

The standard research paper proceeds only if all are true:

1. the public Callback-Protocol GPU lifecycle is closed;
2. both matched tasks are exact in RTDL and current PyOptiX;
3. responsibility transfer is source-backed rather than inferred from LOC;
4. executable ablations show that core protocol mechanisms prevent concrete violations;
   - each full-versus-ablated result includes the exact invalid input, full and ablated acceptance receipts, a nearby valid control, observed outcome, and proof that no independent validator rejected the case first;
5. matched performance is complete **after the pre-timing checkpoint**, or a terminal, preregistered inability to obtain fair measurements is fully disclosed and the reviewer explicitly judges the remaining non-performance evidence sufficient;
6. the PyOptiX, Slang, Dr.Jit, and CrossRT comparison is primary-source anchored and non-hostile;
7. the 11-page paper is self-contained without relying on an appendix to explain the contribution.

If RTDL still requires internal provider/loader/PTX/SBT routes, or the ablations cannot show additional protocol errors prevented beyond a reasonable PyOptiX implementation, existing nine-application coverage and V2/V4 timing may not be used to declare the core proven.

## 10. Claim ceiling

If the work succeeds, the strongest intended claim is:

> For its admitted bounded subset, RTDL makes a complete traversal-driven callback protocol the compilation unit for repurposed OptiX applications. On the evaluated matched tasks and existing application suite, it transfers specified declared protocol responsibilities from application code to compiler validation/generation while retaining application-owned algorithms, semantic oracles, and declared trusted physical partners; it rejects demonstrated whole-protocol violations before launch, preserves exact outputs, and incurs the lifecycle-separated costs reported against the exact PyOptiX baseline.

The following remain prohibited:

- first Python OptiX, first Python callbacks, or first Python-to-PTX;
- PyOptiX cannot implement repurposed applications;
- universal semantic correctness, completeness, or mechanized proof;
- arbitrary-new-application proof/admission or a generalization rate;
- all application families or all OptiX workloads;
- easier, simpler, less code, more productive, or better than CUDA/OptiX without a real study;
- PyOptiX performance superiority without matched evidence;
- universal no-slower, production, public-release, or GA claims;
- artifact governance as academic novelty.

## 11. Questions requiring explicit answers

### Contribution and novelty

1. Based on the stated IR, API, and generated/runtime boundaries, is “complete callback protocol as compilation unit” materially different from packaging several device functions behind a wrapper?
2. Is the proposed increment over current PyOptiX real and useful: which exact cross-callback responsibilities move from the application to compiler enforcement/generation?
3. Would a skeptical reviewer reasonably classify RTDL as PyOptiX plus validation glue? If so, what exact mechanism/evidence must change that verdict?
4. Is the distinction from Slang's target/stage/capability system accurate and non-hostile? Is it credible that Slang could serve as a leaf compiler while RTDL supplies the protocol layer?
5. Is the distinction from Dr.Jit's traced whole-program rendering specialization accurate, while conceding that RTDL offers no comparable global optimization?
6. Is CrossRT fairly represented as algorithm-to-backend translation across CG/CV tasks, including SDF and Gaussian splatting, rather than incorrectly dismissed as rendering-only?
7. Does the proposed CrossRT/RTDL boundary survive scrutiny: translation/mapping versus an explicit targetable callback-protocol IR?
8. Are any “first,” “cannot solve,” formal-soundness, generalization, usability, or performance implications still hidden in the proposed language?

### API, capability, and mechanism evidence

9. Does the current public GPU lifecycle gap block the contribution, and are Goal5795's closure conditions sufficient?
10. Are the custom-AABB relation/count and built-in-triangle query/reduction tasks sufficiently different, non-rendering, and fair to both systems?
11. Does the responsibility rubric measure compiler ownership rather than superficial code size? What responsibility is missing?
12. Are effects, ABI/ownership, physical binding, status/continuation, and executable identity the right irreducible mechanisms?
13. For each mechanism, is the required full-versus-ablated accepted-invalid experiment strong enough to demonstrate value? Which case still risks being only metadata or a digest test?
14. Given the historical inert `roles[].effects` defect, what additional hostile test is mandatory before accepting the effect-closure claim?

### Baseline and performance

15. Does the plan protect PyOptiX baseline fairness, including its full API breadth, normal device-program path, source availability, and reasonable implementation quality?
16. Are cold, preparation, prepared execution, memory, validation/codegen, exact-output gating, and raw-sample recount sufficient timer/evidence boundaries?
17. If PyOptiX is consistently faster, do the safety/responsibility results still establish a CGO-worthy compiler abstraction with costs fully disclosed? Identify **missing qualitative evidence**, if any; do not impose an arbitrary performance ratio or “cost ceiling” absent a stated paper claim.

### CGO decision

18. Are Goals5794–5798 the shortest credible evidence path before the reserved writing week, or is one item unnecessary/missing?
19. Is the September 3 go/no-go gate strict enough to prevent substituting old application counts or V2/V4 performance for the missing PyOptiX/ablation evidence?
20. Assuming every gate passes, is the bounded claim plausible as a CGO standard research-paper contribution? If not, name the single most decisive missing contribution or experiment.

## 12. Required verdict schema

```yaml
review_scope:
  cfr_sha256: "<sha256 of this exact file>"
  reviewed_date: "YYYY-MM-DD"
  reviewer: "<name/model or anonymous external reviewer>"
  primary_sources_checked:
    pyoptix_current_repo: true|false
    pyoptix_numba_2022: true|false
    slang_capabilities_and_optix: true|false
    drjit: true|false
    crossrt: true|false
    cgo_2027_cfp: true|false

per_question:
  - id: 1
    verdict: "PASS|PARTIAL|FAIL|NOT_REVIEWABLE"
    severity_if_open: "P0|P1|P2|P3|NONE"
    evidence_checked: ["<sources/paths/commands>"]
    finding: "<falsifiable finding>"
    required_remedy: "<specific remedy; empty only for PASS>"
    evidence_access:
      implementation_inspected: true|false
      generated_artifacts_inspected: true|false
      raw_measurements_inspected: true|false
      strategy_only_assessment: true|false

claim_audit:
  core_claim: "PASS|PARTIAL|FAIL"
  pyoptix_boundary: "PASS|PARTIAL|FAIL"
  slang_boundary: "PASS|PARTIAL|FAIL"
  drjit_boundary: "PASS|PARTIAL|FAIL"
  crossrt_boundary: "PASS|PARTIAL|FAIL"
  approved_claims: ["<precisely bounded claims>"]
  prohibited_claims: ["<unsupported claims>"]
  required_disclosures: ["<limitations/adverse results>"]

experiment_audit:
  matched_tasks: "PASS|PARTIAL|FAIL"
  public_api_gate: "PASS|PARTIAL|FAIL"
  pyoptix_baseline_fairness: "PASS|PARTIAL|FAIL"
  responsibility_rubric: "PASS|PARTIAL|FAIL"
  executable_ablations: "PASS|PARTIAL|FAIL"
  timer_and_preparation_scope: "PASS|PARTIAL|FAIL"
  exactness_and_oracle: "PASS|PARTIAL|FAIL"
  reproducibility: "PASS|PARTIAL|FAIL"

go_no_go:
  goals5794_to_5798: "GO|CONDITIONAL_GO|NO_GO"
  blocking_conditions: ["<empty only if GO>"]
  minimum_remaining_evidence: ["<submission-critical item>"]
  september_3_gate: "ADEQUATE|REVISE|INADEQUATE"
  submission_authorized: false
  rationale: "<why this path can or cannot produce a CGO contribution>"

approval_guard:
  strategy_plan_approved: true|false
  implemented_core_approved: false
  reason: "This single-file CFR cannot approve the implemented core without a later exact-artifact review."

overall:
  p0_count: 0
  p1_count: 0
  p2_count: 0
  p3_count: 0
  verdict: "APPROVE|APPROVE_WITH_CONDITIONS|REJECT"
  reviewer_summary: "<maximum 250 words>"
```

## 13. Primary sources to check

- NVIDIA current PyOptiX repository: https://github.com/NVIDIA/otk-pyoptix
- NVIDIA PyOptiX/Numba callback demonstration: https://developer.nvidia.com/blog/writing-ray-tracing-apps-in-python-using-numba-for-pyoptix/
- Slang capability system: https://shader-slang.org/slang/user-guide/capabilities
- Slang OptiX support: https://docs.shader-slang.org/en/stable/external/slang/docs/cuda-target.html
- Dr.Jit: https://arxiv.org/abs/2202.01284
- CrossRT: https://arxiv.org/abs/2409.12617
- CGO 2027 call for papers: https://conf.researchr.org/track/cgo-2027/cgo-2027-papers

## 14. Local custody records — not incorporated into this review; do not send

These records merely let the owner locate the internal derivation after the review. They are not evidence available to this reviewer, are not incorporated by reference, and must not be sent with this CFR:

| Local path | Bytes | SHA-256 |
|---|---:|---|
| `history/internal_docs/goal5794_cgo_callback_protocol_ir_strategy_summary_20260823.md` | 20,775 | `81958053b1c50e3d21ac0efd6d1dae0e0daeb413f6ed308dbcd7c74bcc086db8` |
| `history/internal_docs/goal5794_to_goal5799_cgo_execution_plan_20260823.md` | 16,878 | `906b63b5490aa69dc81320056f1d8d07564bf70ffab8b8d098378089b64320f2` |

The reviewer should judge this CFR on its own. Do not request, send, or combine these records with the CFR.

## 15. Non-authorization

This CFR does not itself authorize submission, publication, public release, a performance claim, a usability/productivity claim, universal generalization, arbitrary-new-app admission, mechanized proof, production/GA status, or any claim against PyOptiX performance.

It requests a scientific and engineering ruling on the contribution thesis and the bounded Goals5794–5798 evidence path. Formal performance samples must still follow the frozen matched design and exact environment. Owner controls the final September 10 upload.

A favorable ruling on this CFR must not be cited as external validation of the current IR implementation, its public API, any mechanism ablation, PyOptiX fairness, or the paper's final novelty claim. Those require the later exact-evidence review specified above.
