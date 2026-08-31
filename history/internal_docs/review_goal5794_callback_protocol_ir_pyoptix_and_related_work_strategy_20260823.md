# External review — Goal5794 Callback-Protocol IR, PyOptiX comparison, and CGO execution plan

**Reviewer posture:** skeptical compiler/systems reviewer familiar with GPU and ray-tracing systems, as requested. This is a strategy and gate review. I did not receive and did not inspect any implementation, generated artifact, or raw measurement; Questions 1–3 and 9–14 are answered for *implementation truth* as `NOT_REVIEWABLE` with a separate judgment on whether the proposed tests would suffice, exactly as the CFR's evidence-sufficiency rule requires.

**CFR:** `call_for_review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md`
`sha256 = 3f98be594ffd4befbca19344f779502627cd0460c634dee323378841b6b19c21` (29,915 bytes)

**Primary sources checked:** I fetched every source the CFR names, plus three it does not. The three it does not are where the decisive finding is.

---

## Headline

**The core positioning is defensible and I do not recommend rejecting it.** "Whole traversal-driven callback protocol as the unit of compilation, closed and fail-closed before OptiX composition" is a real compiler thesis, it is correctly scoped, and — importantly — I found published, contemporaneous, third-party support that this axis is an open gap in the RT-core repurposing literature.

**But the plan has one omission I judge likely fatal if it ships uncorrected, and it is not PyOptiX.** It is **NVIDIA OWL**, the OptiX Wrappers Library. OWL already takes ownership of SBT construction and population, acceleration-structure build/compact/refit, program/pipeline management, device memory transfer, and launch-parameter setup, and it is widely used in exactly the non-rendering RT-core community this paper addresses. The CFR's related work (Slang, Dr.Jit, CrossRT, PyOptiX) does not mention it, and the responsibility rubric of §7.2 counts "GAS/program-group/pipeline/SBT composition" as an RTDL-owned responsibility transferred away from a *raw* PyOptiX baseline. A skeptical reviewer of the requested profile knows OWL. The first question they will ask is **"isn't this OWL plus a type checker?"** — and the plan currently has no prepared answer, no baseline arm, and no ablation that isolates the residual.

The good news is that fixing this **strengthens** the paper rather than weakening it, and it is a scoped addition to Goals 5794/5796, not a re-plan. The residual delta over OWL is exactly the five mechanisms §7.3 already proposes to ablate — and demonstrating that those five defects survive a library that already owns pipeline/SBT/AS is a far sharper result than demonstrating them against raw PyOptiX, where a reviewer will attribute half the table to 2020-era engineering.

**Disposition: `APPROVE_WITH_CONDITIONS`.** P0 = 1, P1 = 4, P2 = 3, P3 = 2. Conditions are exact and listed in §5.

---

## 1. Primary-source verification

Every factual claim the CFR makes about external systems, I checked against the source. **All of them are accurate.** That is worth stating plainly before the findings, because it is unusual.

| CFR claim | Source | Verdict |
|---|---|---|
| CGO 2027 second round, submission 10 Sep 2026 | CGO 2027 CFP | **Correct.** Second round: submission 10 September 2026, rebuttal 20–22 October, notification 2 November 2026. |
| 11-page standard research paper | CGO 2027 CFP | **Correct.** "11 pages of text, excluding bibliography, using the ACM format"; references unlimited; `acmart` with `sigplan`. |
| otk-pyoptix is complete Python bindings for the OptiX host API; `pip install pyoptix`; OptiX 9.1 | NVIDIA/otk-pyoptix README | **Correct**, verbatim: "Complete Python bindings for the OptiX host API"; "Installation of the OptiX 9.1 Python bindings can be performed directly via pip." |
| 2022 PyOptiX/Numba demo showed Python-authored raygen, closest-hit, miss and Numba device lowering | NVIDIA developer blog, 1 June 2022 | **Correct**, and see P1-2 for what it did *not* show. |
| Slang's capability system infers/enforces over targets, stages, API extensions, hardware features | Slang capabilities user guide | **Correct**, verbatim: "Slang models code generation targets, shader stages, API extensions and hardware features as distinct capability atoms." |
| Slang does not thereby establish a whole non-rendering callback/payload/SBT/status/continuation protocol | same | **Correct.** The capability system does not reason about cross-stage data contracts, payload/attribute layout agreement, SBT composition, or host pipeline construction. |
| Dr.Jit traces high-level PBR code, globally simplifies/specializes, tracks dependencies, JITs data-parallel kernels | Dr.Jit paper abstract | **Correct.** |
| CrossRT translates hardware-agnostic OO C++ to multiple RT APIs/hardware with CPU/GPU fallbacks and megakernel/wavefront forms, evaluating BVH, SDF, Gaussian splatting, path tracing | CrossRT abstract | **Correct**, including the CV/SDF/3DGS tasks. CrossRT does not address payload contracts, SBT, or device failure status — so the CFR's scoped boundary holds. |

The related-work characterizations are accurate and non-hostile throughout. Nothing here is a straw man. That part of the work is done well and I have no correction to offer on it.

### 1.1 Three sources the CFR does not cite

**NVIDIA OWL — "The OptiX Wrappers Library" / "A Node Graph Abstraction Layer on top of OptiX 7."** From its own materials: the SBT "can be built and properly populated by a single call `owlBuildSBT(context)`"; acceleration structures are built, compacted and refitted automatically; program compilation and pipelines are managed by the library; device buffers, uploads and launch parameters are handled; `OWLVarDecl` arrays declare device-side struct layouts with type-safe setters such as `owlGeomSet3f()`. Its author frames raw OptiX 7 as "time-consuming and bug-prone," and says that with OWL, "even if you have no clue what [an SBT] is" you can still use it. Device programs remain CUDA C++, and I found **no** cross-program payload/attribute contract checking in its documentation. This is P0-1.

**"Ray Tracing Cores for General-Purpose Computing: A Literature Review" (arXiv 2603.28771, 2026).** Bibliometric analysis of 59 Scopus-indexed papers, systematic review of 35 proposing novel RT solutions across 32 distinct problems, taxonomised by domain (physics, geometric queries, databases, AI). Two things matter. First, it is now mandatory related work for any 2027 paper in this space. Second — and this is a gift — **it surveys no programming abstraction, DSL, compiler, framework or library for general-purpose RT-core programming at all**, and it observes that "these applications lack a clear pattern, and the conditions under which RT cores can provide computational benefits are still not clearly understood." That is contemporaneous, third-party, published evidence that the programmability/abstraction axis is an open gap. It is the single best external support this paper's novelty claim can have, and the CFR does not use it. This is P1-3.

**Adjacent RT-repurposing systems work** (e.g. the SIGMETRICS-venue RT-cores case study for BFS and triangle counting, `10.1145/3727108`, and the Purdue thesis "Repurposing GPU Ray Tracing Architecture for Accelerating Irregular Programs"). Also part of P1-3.

---

## 2. Findings

### P0-1 — NVIDIA OWL is absent from related work and from the baseline design, and it owns a large share of what the responsibility rubric credits to RTDL

**The problem.** §7.2's rubric counts, among nine responsibility classes, "GAS/program-group/pipeline/SBT composition" and "lifecycle transitions." Against a *raw* PyOptiX baseline, those rows will show a large, visually persuasive transfer. But OWL — published by NVIDIA, authored by a co-author of the original OptiX paper, in use since 2020, and commonly used by exactly the RT-core repurposing papers this work motivates itself from — already removes those responsibilities from the application without any compiler, any IR, and any static validation.

A reviewer of the profile the CFR requests will read the rubric table and attribute those rows to a 2020 library, not to a 2027 compiler contribution. The plan's §9 go/no-go gate would pass with this hole fully open, because none of its seven conditions mentions it.

**Why this is P0 and not P2.** It is not a citation oversight. It structurally miscalibrates the primary evidence instrument. The rubric is the paper's main non-performance result, and it is currently designed against a baseline that overstates the delta. Discovering this in an October rebuttal is unrecoverable; discovering it now costs one to two days.

**Why fixing it makes the paper better.** The residual delta of RTDL over OWL is precisely the five mechanisms §7.3 already ablates: role/effect closure, payload/attribute ABI and ownership, physical/geometry binding consistency, device status and continuation ordering, and checked-program/executable identity. OWL does not check any of them — it is a runtime convenience layer with host↔device variable declarations, not a static contract checker. So the strong form of the paper is:

> *Even given a mature library that already owns pipeline, SBT and acceleration-structure composition, these five classes of whole-protocol defect remain application-owned and silently accepted. Here they are, and here is a compiler that rejects each one before launch.*

That is a materially stronger claim than the same result against raw PyOptiX, and it pre-empts the reviewer's best objection instead of inviting it.

**Exact remedy (Goal5794 + Goal5796, scoped).**
1. Add OWL to §6 related work with a scoped, non-hostile boundary in the same style as the other three: *OWL removes host-side composition burden at runtime; it does not close cross-role effects, payload/attribute type agreement, physical binding consistency, device status/continuation, or source-to-executable identity, and does not fail closed before launch.* Verify this against the OWL source, not only its README, before asserting it.
2. Freeze OWL alongside PyOptiX in Goal5794 (commit, version, build).
3. Make the responsibility rubric **three-armed**: raw PyOptiX / PyOptiX+OWL / RTDL. Report the RTDL-over-OWL column as the headline; the RTDL-over-raw-PyOptiX column is context, not the result.
4. For each of the five ablations in §7.3, state explicitly whether the ablated system's acceptance of the invalid program also occurs under OWL. An ablation whose defect OWL would also catch is not evidence of the contribution.
5. If the schedule cannot carry a full third implementation arm, the minimum acceptable substitute is a **source-backed OWL responsibility analysis** — mapping each of the nine rubric rows to the OWL API call or absence thereof — plus an explicit statement in the paper that the OWL arm was analysed rather than implemented. Do not skip it silently.

---

### P1-1 — CGO 2027 is double-blind and the plan contains no anonymization gate

The CGO 2027 CFP states: "Papers are to be submitted for double-blind review," and recommends `\documentclass[sigplan,screen,review,anonymous]{acmart}`.

The plan's Goal5799 reads "11-page self-contained standard research paper, artifact, final claim review, owner upload." There is no anonymization step, no artifact-anonymization step, and no blinding item in the §9 go/no-go checklist.

This project is unusually exposed here. Its evidence chain is saturated with identifying material: a named system, a distinctive internal goal-numbering scheme, an owner-controlled external review series, a designated host at a specific private IP, Windows user paths in frozen runtime records, and a long trail of internal documents whose names would be recognisable to anyone who has seen any of them. An artifact assembled from those records without a scrub is a de-anonymisation vector, and CGO's artifact process runs on conditionally accepted papers.

**Remedy.** Add to Goal5799 and to the §9 gate: (a) paper compiled with the anonymous review option; (b) no self-identifying system history, host identity, personal filesystem paths, or internal goal numbering in the paper; (c) self-citation in third person; (d) any artifact prepared for review scrubbed of the same, with a named person responsible for the scrub and a checklist frozen in advance. Treat a blinding violation as a `NO_GO`, not as a copy-edit.

---

### P1-2 — The baseline's device-authoring path is unfrozen, probably not Python, and will confound the responsibility rubric

The CFR asserts, correctly, that the 2022 NVIDIA demonstration showed Python-authored raygen, closest-hit and miss with Numba lowering. Two things it does not say:

1. That demonstration **did not show an intersection program** authored in Python, and the blog explicitly describes the extension as "at the development stage," supporting "only certain OptiX types and intrinsics."
2. The **current** otk-pyoptix repository — the baseline §5 requires — documents host API bindings and states that "the OptiX SDK must be installed to allow JIT compilation of the example shaders." I found no current documentation of Python device-program authoring in the frozen-baseline repository.

Matched task 1 in §7.1 is a **custom-AABB spatial relation/count**. Custom AABB geometry has no built-in intersection; an intersection program is mandatory. So the most likely outcome is that the PyOptiX baseline authors its device programs in CUDA C++ while RTDL authors them in restricted Python.

If that happens, the §7.2 rubric measures two different things summed into one column: *protocol-ownership transfer* (the contribution) and *device-language authoring change* (explicitly **not** the contribution — §1 forbids centering on Python-to-OptiX, and §10 forbids first-Python and Python-to-PTX claims). A reviewer who notices will discount the entire table, and will be right to.

**Remedy.** Make the frozen baseline's device-authoring path a first-class Goal5794 deliverable, stated as a result rather than a configuration detail: does the frozen otk-pyoptix commit support Python/Numba device authoring at all, and specifically for **intersection** programs? Then split the rubric into two separately reported sections — responsibilities that move because the compiler owns the protocol, and responsibilities that change because the device language changed — and **never sum them**. If Numba-PyOptiX cannot express the intersection program, disclose that as a measured baseline limitation in the paper body; do not let it silently inflate the transfer count. This is also the honest answer to Q15.

---

### P1-3 — The RT-core repurposing literature, the field this paper motivates itself from, is entirely absent from related work

§6 covers four compiler/API systems and no application-domain work. But the paper's premise — that people repurpose RT hardware for non-graphics computation and that this is hard to get right — comes from a body of literature that a 2026 review catalogues as 59 indexed papers, 35 novel RT solutions, 32 problems. Omitting it will read as unfamiliarity with the field, which is the most damaging first impression a CGO submission can make.

It is also a missed opportunity. That review surveys **no** programming abstraction, DSL, compiler, framework or library for the space, and states that the conditions under which RT cores help "are still not clearly understood." Cited affirmatively, that is third-party published evidence for exactly the gap this paper claims to fill — far stronger than the paper asserting the gap itself.

**Remedy.** Add a related-work axis covering RT-core repurposing applications, anchored on the 2026 literature review plus a representative sample across its domain taxonomy (physics, geometric queries, databases, AI), and use the survey's own finding as support for the abstraction gap. Cross-check the sample against the frozen 186-row exposure registry, which almost certainly already contains most of it.

---

### P1-4 — The plan pre-registers everything except its own failure mode

§4.8 states that generic GPU `materialize → prepare → execute → close` is **outside** the stable callback-authoring namespace today, and that current prepared-provider routes are advanced/internal. §7.1 forbids any private-loader, internal-provider, hand-written-PTX or manual-SBT escape in the matched tasks. Goal5795 therefore has to ship new public API surface in **three days** (Aug 24–26), and Goals 5796, 5797 and 5798 are all strictly downstream of it. The reserved writing week begins Sep 3, with the final evidence review due back the same day.

There is no slack anywhere in this schedule and no stated fallback. That is a governance gap in a project whose entire methodology is pre-registration: a decision rule must be frozen before the situation that would tempt you. The specific temptation here is concrete and predictable — on Sep 1, with the API 80% closed, the cheapest path is one internal-provider route in one matched task, described as public. §7.1 forbids it, but forbidding a shortcut is not the same as having a pre-declared alternative to take instead.

**Remedy.** Freeze now, before Goal5795 starts, an explicit descope ladder with dates and owners, for example:
- **Aug 26 checkpoint:** if the public lifecycle is not closed for both geometry paths, drop to one matched task, or drop to a practical-experience paper, or declare `NO_GO` for the 10 Sep round.
- **Aug 31 checkpoint:** if fewer than five ablations are executable, the paper reports the executable subset and explicitly states which mechanisms are unevidenced — it does not substitute field-presence or digest tests, per §7.3.
- **Sep 2 checkpoint:** if matched timing is unobtainable on the frozen host, invoke §9(5)'s disclosed-inability branch rather than measuring on a substitute host.
- **Named alternative venue** if `NO_GO` fires, decided now rather than on Sep 9. CGO 2027's first round has already passed (submission 11 June 2026); the realistic alternatives are the next CGO cycle or a comparable venue. Deciding that in advance removes the pressure that produces a compromised submission.

---

### P2-1 — The "targetable IR" framing is asserted and unevaluated

§6 defends the CrossRT boundary partly on the ground that RTDL is "a restricted callback-protocol IR that a translator or human could target." Nothing in Goals 5794–5798 tests this. No translator targets it; no second front end exists; there is no evidence a translator *would* find it a useful target. As written it is an architectural aspiration presented inside a contribution boundary, and a reviewer will treat an unevidenced architectural claim as weakening the surrounding evidenced ones.

**Remedy.** Either demote it explicitly to future work and remove it from the contribution and boundary statements, or provide one cheap piece of evidence — for example, a written mapping from CrossRT's published algorithm description form onto the RTDL role/effect/ABI surface, identifying what would and would not translate. The mapping is a page of analysis and would materially strengthen §6; the assertion without it is a liability.

### P2-2 — Adverse results are disclosed to me but have no assigned place in the paper

§4 discloses, honestly, that the registered performance criterion gives 16/34 pass and 18/34 fail (cold 4/15, prepared 12/19), that CI classification gives 11 clear wins, 10 clear losses and 13 uncertain, that the Goal5789 registered-lane inventory is 6 `COMPATIBLE` and **9 fail-closed `UNKNOWN`**, that prospective generalization exams are 0, and that usability studies and matched baselines are 0.

The plan does not say where any of that appears in the 11 pages. §9(7) requires the paper to be self-contained without an appendix, which cuts the right way, but it is a structural requirement, not a disclosure rule. A paper that reports "6 COMPATIBLE lanes" without the 9 UNKNOWN beside it, or that quotes 11 clear wins without the 10 clear losses and 13 uncertain rows, would be precisely the concealment this project has spent months refusing to commit — and at 11 pages under deadline pressure, adverse results are what gets cut.

**Remedy.** Freeze a disclosure rule now: every adverse or mixed result named in §4 appears in the **main body**, adjacent to the favourable result it qualifies, in the same table or the immediately following sentence — never in a footnote, never deferred to an artifact, never aggregated away. Add it as an eighth condition to the §9 gate and make the final claim review check it line by line.

### P2-3 — Nothing verifies that the two matched tasks between them exercise all five ablated mechanisms

§7.1 freezes two tasks; §7.3 requires five single-factor ablations each needing a concrete protocol violation *and* a nearby valid control. Nothing in the plan checks that the two tasks can actually supply ten such inputs. Reading the task descriptions, "device status and continuation ordering" and "role/effect closure" are the two least obviously exercised: neither task as described centres on `any_hit` accept/continue behaviour or on a post-traversal continuation that could plausibly consume an incomplete device result.

If a mechanism has no natural violation in either task, the ablation becomes synthetic — and §7.3's own standard ("digest-only mismatch cases are not sufficient") would then rule it out.

I do **not** recommend adding a third task; the schedule cannot carry it alongside the P0-1 remedy. Instead:

**Remedy.** Add to Goal5794's deliverables a **mechanism × task coverage matrix**, produced before implementation starts, naming for each of the five mechanisms: which task supplies the invalid input, what the concrete violation is, what the nearby valid control is, and what the attributable wrong result or invariant violation in the ablated system will be. If a cell cannot be filled from the two frozen tasks, adjust the task specifications *now* — while they are still free to adjust — rather than discovering the gap on Aug 29.

---

### P3-1 — Taxonomy breadth must not be presented as capability

§3 discloses current ceilings of trace depth 1 and callable depth 0. The frozen structural vocabulary from the X2 work enumerates five continuation modes, of which four (`BOUNDED_STATIC_RETRACE`, `DATA_DEPENDENT_RETRACE`, `RECURSIVE_TRACE`, `STOCHASTIC_PATH_CONTINUATION`) are not realizable on device at trace depth 1, and all four frozen positive vectors are `SINGLE_TRACE`. If the paper presents the taxonomy as evidence of the abstraction's reach, it will be presenting a vocabulary the implementation cannot execute. Add an explicit guard: any taxonomy figure or table states which values are currently realizable and which are vocabulary only.

### P3-2 — The RayDB loader exception needs to be visible where the application table is

§4.9 discloses that registered-interface loader encapsulation is 8/9, with RayDB using the private `_load_optix_library`. If RayDB appears in the paper's application table, the exception must be marked at that row — not only in a limitations paragraph. A reader scanning a nine-application table should not have to find a caveat three pages later to learn that one row used a private route.

---

## 3. Answers to the twenty questions

### Contribution and novelty

**Q1 — Is "complete callback protocol as compilation unit" materially different from packaging several device functions behind a wrapper?**
`NOT_REVIEWABLE` for implementation truth; **PARTIAL** as a thesis. The distinction is real *in principle*: a wrapper packages code, whereas the described IR closes cross-role obligations — effect production/consumption, payload/attribute type and ownership agreement, physical configuration consistency, status and continuation ordering, executable identity — and refuses to generate when they are not closed. That is a contract, not packaging. But the difference is only demonstrated by §7.3's ablations, and only if each ablation shows a defect that survives a *reasonable* implementation on the baseline. Against raw PyOptiX some of them will look like packaging benefits; against PyOptiX+OWL, only the genuine contract mechanisms remain. This is why P0-1 is P0.

**Q2 — Is the increment over current PyOptiX real and useful; which responsibilities move?**
`NOT_REVIEWABLE` for implementation truth; **PASS** as a plan, conditional on P0-1 and P1-2. The five responsibilities that plausibly move and that no cited system claims are: (i) cross-role effect production/consumption closure; (ii) payload/attribute slot type and ownership agreement between producer and consumer roles; (iii) consistency between declared callback assumptions and the selected custom-AABB or built-in-triangle realization; (iv) device failure status and post-traversal continuation ordering; (v) binding of the checked IR/certificate to the actual executable program. Pipeline/SBT/GAS composition and lifecycle transitions **do not belong on this list against an OWL baseline**, and listing them there is the miscalibration P0-1 identifies.

**Q3 — Would a skeptical reviewer classify RTDL as PyOptiX plus validation glue? What changes that verdict?**
**PARTIAL — and today, against the plan as written, a well-informed reviewer would say "OWL plus validation glue," which is worse.** What changes the verdict is exactly one thing: an ablation table in which a competent PyOptiX+OWL implementation *accepts* a concretely invalid whole-protocol program and produces an attributable wrong result, a nearby valid control is *accepted* by RTDL, and no independent validator (OptiX validation mode, CUDA error checking, the oracle) catches the invalid case first. §7.3 already specifies that experiment correctly, including the reject-all guard and the "no independent validator caught it first" proof. Run it against the OWL arm and the verdict changes. Run it only against raw PyOptiX and it does not.

**Q4 — Slang distinction accurate and non-hostile? Slang as leaf compiler credible?**
**PASS.** Verified against the Slang capability documentation: it models targets, stages, API extensions and hardware features as capability atoms, infers requirements for internal/private functions, and enforces declared requirements on public and interface methods. It does not reason about cross-stage data contracts, payload/attribute layout agreement, SBT composition, or host pipeline construction. The CFR's boundary is accurate and generous. Slang as a leaf compiler is credible and costs nothing to state; do not over-invest in it, since it is not evidenced by any planned experiment.

**Q5 — Dr.Jit distinction accurate, conceding no comparable global optimization?**
**PASS.** Dr.Jit traces high-level simulation code, aggressively simplifies and specializes it, tracks data dependencies globally to eliminate redundant computation (notably under differentiation), and JIT-compiles data-parallel CPU/GPU kernels for physically based and differentiable rendering. The CFR's concession is correct and the unit-of-compilation contrast (traced whole computation vs explicit restricted protocol) is fair.

**Q6 — Is CrossRT fairly represented, including SDF and Gaussian splatting?**
**PASS.** Confirmed: hardware-agnostic object-oriented C++ translated to hardware-accelerated implementations, software fallbacks for non-accelerated CPUs and GPUs, megakernel and multi-kernel/wavefront path-tracing forms, evaluated on BVH build/traversal, ray-surface intersection (SDF), ray-volume intersection (3D Gaussian splatting), and path tracing. The CFR does not dismiss it as rendering-only, which is the correct call — it is the closest algorithmic threat.

**Q7 — Does the CrossRT/RTDL boundary survive scrutiny?**
**PARTIAL.** The *descriptive* boundary survives: CrossRT is algorithm-to-backend translation and does not address payload contracts, SBT composition, or device failure status. The *normative* half — that RTDL is a protocol IR a translator could target — does not survive, because nothing evaluates it. See P2-1. Keep the descriptive boundary; demote or evidence the targetability claim.

**Q8 — Are any "first," "cannot solve," soundness, generalization, usability or performance implications still hidden?**
**PASS on the explicit language, PARTIAL on structure.** §10's prohibition list is comprehensive and I found no residual absolute claim in the CFR text. Two structural risks remain: the responsibility rubric can imply a usability claim without stating one if the device-language confound of P1-2 is unaddressed; and the taxonomy can imply reach the implementation lacks (P3-1). Both are presentation guards, not wording fixes.

### API, capability, and mechanism evidence

**Q9 — Does the public GPU lifecycle gap block the contribution; are Goal5795's closure conditions sufficient?**
`NOT_REVIEWABLE` for implementation truth; **PARTIAL** as a plan. The conditions are correct in content — a stable public `parse/verify → materialize → prepare → execute → close` with no private loader, internal provider, hand-written PTX or manual SBT escape in the matched tasks — and §7.1's no-escape rule is the right gate. What is insufficient is the **schedule and the absence of a fallback**: three days for new public API surface, with three dependent goals behind it and zero slack. See P1-4. The gap does not block the contribution; the schedule risk around closing it is the live threat.

**Q10 — Are the two tasks sufficiently different, non-rendering, and fair to both systems?**
**PARTIAL.** Different: yes — they exercise the two distinct physical realizations, distinct hit processing, and distinct decode/continuation shapes. Non-rendering: yes. Fair: **not yet established**, for the reason in P1-2 — the custom-AABB task requires an intersection program, and the frozen baseline's ability to author one in Python is unverified and probably absent. Fairness here is not about whether PyOptiX *can* implement the task (it can) but about whether the comparison isolates protocol ownership from device language. Additionally, coverage of the five ablated mechanisms by these two tasks is unverified (P2-3).

**Q11 — Does the rubric measure compiler ownership rather than code size? What is missing?**
**PARTIAL.** The design is right: source-backed, located, with every "compiler-owned" entry pointing to a validator or generator and every "user-owned" entry pointing to baseline source, and LOC explicitly demoted. Three things are missing. (i) The OWL arm (P0-1) — without it the rubric measures ownership transfer against a baseline nobody in this community actually uses raw. (ii) The protocol/language split (P1-2). (iii) A row for **what the developer must still get right that neither system checks** — the semantic oracle, the geometry-encodes-my-algorithm judgment, the declared trusted physical partners. §1 and §3 concede these honestly in prose; putting them in the rubric as an explicit "remains application-owned" column converts a concession into a credibility asset and pre-empts "what does it *not* do?"

**Q12 — Are effects, ABI/ownership, physical binding, status/continuation and executable identity the right irreducible mechanisms?**
**PASS.** They are well chosen: each is a distinct failure mode, each maps to a defect class in §2, and together they cover producer/consumer disagreement, type disagreement, host/device configuration disagreement, failure-consumption, and certificate/executable substitution. I would not add a sixth. I would note that these five are also precisely the residual over OWL, which is why the ablation table is the paper.

**Q13 — Is each full-versus-ablated experiment strong enough? Which risks being metadata or a digest test?**
**PARTIAL.** The experimental form is correct and unusually well specified — invalid input, full rejects before launch, ablated accepts with an attributable wrong result or invariant violation, nearby valid control still accepted, only the named mechanism changed, plus false-rejection rate, diagnostic specificity, costs and remaining TCB. The one at clear risk is **(5) checked-program/executable identity binding**, which is intrinsically an identity property and will naturally reduce to "the digests differ" — which §7.3 rules out. To make it substantive, the ablated case must show a *coherently resealed* mismatched pairing that produces a wrong result the oracle catches and no independent validator catches — i.e. the attack must be semantically plausible, not a corrupted hash. Mechanism (3), physical binding, is the second at risk if the "violation" is a configuration flag mismatch rather than a genuine behavioural divergence; require that the ablated run produce a wrong output, not merely a mismatched declaration.

**Q14 — Given the historical inert `roles[].effects` defect, what additional hostile test is mandatory before accepting effect closure?**
**FAIL as specified — this is the one place the plan is materially under-specified, and the project's own history says so.** §4.7 records that a checker accepted emptied `roles[].effects` after resealing until a hostile audit exposed it. That defect was found by an adversary who *mutated the leaf and observed that the verdict did not move*. The mandatory test is therefore a **differential-response test on the mechanism itself**, not a rejection test:

For each of the five mechanisms, and specifically for effect closure: take a program the full system **accepts**, mutate only the mechanism's own declaration in a way that must change the verdict (empty the effect set; swap a producer/consumer pair; declare a payload slot type that contradicts its use), reseal every certificate so all identity and digest checks pass, and require that the verdict **changes**. A mechanism whose verdict is invariant under mutation of its own input is inert regardless of how many invalid programs it rejects. Run this for all five, not just effects, and report the mutation set and the verdict deltas in the paper. Without it, an informed reviewer who reads §4.7 — and the paper must disclose §4.7 — will ask exactly this question, and "we rejected some invalid programs" is not an answer to it.

### Baseline and performance

**Q15 — Does the plan protect PyOptiX baseline fairness?**
**PARTIAL.** The intent is right and stated unusually well: full API breadth preserved, normal OptiX/PyOptiX practice, complete host/device implementation, real build options and pipeline/SBT/GAS structure, version pins, tasks not chosen for baseline weakness, no obsolete proxy. Two gaps: the device-authoring path is unfrozen and probably not Python (P1-2), and the baseline that the target community actually uses is PyOptiX+OWL, not raw PyOptiX (P0-1). "Reasonable implementation quality" also needs an operational definition — the strongest available protection is to have the baseline implementations written to normal practice and then reviewed by the external checkpoint *before* any measurement, with the reviewer explicitly asked whether a competent OptiX developer would accept them.

**Q16 — Are the timer and evidence boundaries sufficient?**
**PASS.** Fresh-process cold end-to-end; compilation/module/program-group/pipeline/GAS preparation; prepared execution; peak and steady-state memory; validation/codegen overhead; preparation never hidden on either side; incorrect outputs treated as correctness failures rather than timing samples; all unfavorable and mixed results retained; independent recount. Same designated Linux host, not WSL, with GPU, driver, OptiX/CUDA versions, inputs and oracle frozen before worker zero. This is a better-specified timing protocol than most published GPU work. One addition: freeze the **run order and interleaving** between the arms, not just the environment, so drift cannot be attributed asymmetrically.

**Q17 — If PyOptiX is consistently faster, do the safety/responsibility results still establish a CGO-worthy abstraction?**
**Yes — conditionally, and I will not impose a ratio.** A compiler that rejects whole-protocol defects before launch and generates a correct composition is a contribution even at a disclosed cost; CGO publishes safety and abstraction work whose cost is measured and honest. The condition is that the cost be *lifecycle-separated and fully disclosed*, and that the ablation table carry the paper.

The **missing qualitative evidence**, since you asked me to name it: (i) **diagnostic quality** — for each ablated defect, what the baseline developer actually sees when it goes wrong (silent wrong answer? device crash? nothing?) versus RTDL's message; a compiler contribution that turns a silent wrong result into a precise pre-launch diagnostic is worth more than a speedup, and nothing in §7.3 currently captures the baseline's failure *experience*. (ii) **Where the cost goes** — if RTDL is slower, attribute it (validation, codegen, wrapper indirection, ABI packing), because an attributed cost is a design discussion and an unattributed one is a weakness. (iii) **What remains in the TCB** — §7.3 asks for it; make sure it lands in the paper body, since an honest TCB statement is itself a contribution in this space.

### CGO decision

**Q18 — Are Goals5794–5798 the shortest credible path; is anything unnecessary or missing?**
**PARTIAL.** Nothing in the five goals is unnecessary — each maps to a gate condition. **Three things are missing**, in priority order: the OWL baseline arm (P0-1); the mutation-based mechanism-liveness test of Q14, which is not in any goal today; and the mechanism × task coverage matrix (P2-3), which must precede implementation. Also missing across the whole plan: an anonymization gate (P1-1) and a pre-declared descope ladder (P1-4). None of these adds a new goal; all fit inside 5794, 5796 and 5797.

**Q19 — Is the September 3 gate strict enough to prevent substituting old application counts or V2/V4 timing?**
**PASS on that specific risk.** §9's closing sentence is explicit and correctly worded: if internal escapes remain, or the ablations cannot show additional protocol errors prevented beyond a reasonable PyOptiX implementation, then the nine-application coverage and V2/V4 timing may not be used to declare the core proven. §4.4 separately forecloses using V2/V4 numbers as a PyOptiX comparison. That is the right fence.

**REVISE**, though, for three additions: an eighth condition requiring adverse-result placement in the main body (P2-2); a ninth requiring double-blind compliance (P1-1); and a strengthening of condition 4 to require the mutation-liveness result of Q14, not only accepted-invalid demonstrations.

**Q20 — Assuming every gate passes, is the bounded claim plausible as a CGO standard research-paper contribution? If not, name the single most decisive missing item.**
**Plausible, not comfortable — and I would rather tell you that than flatter the plan.**

Plausible, because: the thesis is a genuine compiler thesis (a contract closed before code generation, fail-closed, with an IR); the claim ceiling in §10 is narrow enough to be defensible under adversarial review; the related-work boundaries are accurate against primary sources; a 2026 published literature review of this exact application space surveys *no* programming abstraction at all, which is strong third-party support for the gap; and the ablation methodology in §7.3 is genuinely well designed, including the reject-all guard and the independent-validator control that most papers omit.

Not comfortable, because: the entire contribution rests on one table — five ablations — and if those defects turn out to be ones a careful developer would not make, the paper reduces to a well-engineered validation layer. Two matched tasks is a case study, not an evaluation, and reviewers will say so. The public API does not exist yet, eighteen days out.

**The single most decisive missing item is the OWL comparison** (P0-1). It is decisive in both directions: omitted, it is the objection that sinks the paper; included and survived, it is what makes the contribution sharp — *a mature library already owns composition, and these five whole-protocol defects still get through*. **The single most decisive missing experiment is the mutation-liveness test of Q14**, because the project's own history contains an inert mechanism that passed every seal and every rejection test until someone mutated it.

---

## 4. On the two standing concerns

**Concern (1) — effect only where tested.** The plan handles this correctly and I want to be explicit about it, because the temptation at this moment is enormous. Generalization exams are 0 and will stay 0; §7.1 states in terms that neither matched task is an unseen, held-out or prospective-generalization exam and that they may not be used to claim an arbitrary-new-application success rate; §10 prohibits generalization rates and arbitrary-new-application admission; §9 forbids substituting the nine-application suite for the missing evidence. After the Goal5793 termination, the honest move was to stop claiming generalization and change the contribution to something the work can actually evidence. That is what this plan does. It is the right decision and I endorse it.

The residual risk is presentational: a "nine applications, 464/464 exact" sentence sitting near a "matched tasks" sentence will *read* as generalization to a skimming reviewer even if no sentence says it. Keep them structurally apart, and let §4.4's disclaimer appear where the numbers appear, not only in a limitations section.

**Concern (2) — flowery description, but harder to use than direct CUDA/OptiX.** §10 prohibits easier/simpler/less-code/more-productive claims and §4.11 records 0 usability studies, 0 developer-time studies, 0 matched baselines. The responsibility rubric is correctly framed as ownership transfer rather than ease. That is the right line and it is held.

But this concern is *closer to the surface here than in any previous packet*, for two reasons. First, P1-2: if the baseline authors device code in CUDA while RTDL authors in Python, the rubric will produce numbers that look exactly like a productivity claim, whatever the caption says. Second, and more bluntly: the honest engineering answer to "is it harder to use than direct CUDA/OptiX?" is that for anything outside the admitted subset, RTDL **must fail closed** — that is its design. The paper should say that as a feature and quantify it: report the false-rejection rate on valid controls (§7.3 already requires it) and report what fraction of the matched-task work had to be expressed inside the bounded subset without escape. A paper that volunteers "here is exactly where our abstraction refuses to help you" is far more credible than one that reports only what it catches.

---

## 5. Exact closure conditions for `APPROVE_WITH_CONDITIONS`

Blocking, before or within the named goal:

1. **(P0-1, Goal5794 + 5796)** Add OWL to related work with a source-verified scoped boundary; freeze it alongside PyOptiX; make the responsibility rubric three-armed with RTDL-over-OWL as the headline column; state for each ablation whether OWL would also catch the defect. Minimum acceptable substitute if the schedule breaks: a source-backed OWL responsibility analysis, explicitly labelled as analysed rather than implemented.
2. **(P1-1, Goal5799 + §9)** Add a double-blind compliance gate for both paper and artifact, with a frozen scrub checklist and a named owner; treat violation as `NO_GO`.
3. **(P1-2, Goal5794)** Freeze and report the baseline's device-authoring path as a first-class result, specifically for intersection programs; split the rubric into protocol-ownership transfer and device-language change, reported separately, never summed.
4. **(P1-3, Goal5794)** Add an RT-core repurposing related-work axis anchored on the 2026 literature review, and use its absence of any surveyed programming abstraction as affirmative support for the gap.
5. **(P1-4, before Goal5795)** Freeze a descope ladder with dated checkpoints (Aug 26 / Aug 31 / Sep 2) and a named alternative venue if `NO_GO` fires.
6. **(Q14, Goal5797)** Add the mutation-liveness test for all five mechanisms — mutate only the mechanism's own declaration in an accepted program, reseal everything, require the verdict to change — and report the mutation set and verdict deltas in the paper.
7. **(P2-3, Goal5794, before implementation)** Produce the mechanism × task coverage matrix; adjust the frozen task specifications now if any cell cannot be filled.
8. **(P2-2, §9)** Add the adverse-result placement rule: every adverse or mixed result named in §4 appears in the main body adjacent to the favourable result it qualifies.

Non-blocking but strongly recommended: P2-1 (demote or evidence the targetable-IR claim), P3-1 (taxonomy realizability guard), P3-2 (mark the RayDB loader exception at the application table), Q11(iii) (add a "remains application-owned" column), Q16 (freeze run order between arms), Q17(i) (capture baseline diagnostic experience).

---

## 6. Required verdict schema

```yaml
review_scope:
  cfr_sha256: "3f98be594ffd4befbca19344f779502627cd0460c634dee323378841b6b19c21"
  reviewed_date: "2026-08-23"
  reviewer: "anonymous external adversarial reviewer"
  primary_sources_checked:
    pyoptix_current_repo: true
    pyoptix_numba_2022: true
    slang_capabilities_and_optix: true
    drjit: true
    crossrt: true
    cgo_2027_cfp: true
  additional_primary_sources_checked:
    nvidia_owl_optix_wrappers_library: true
    rt_cores_general_purpose_literature_review_2026: true
    rt_core_repurposing_adjacent_systems_work: true

per_question:
  - id: 1
    verdict: "NOT_REVIEWABLE"
    severity_if_open: "P2"
    finding: "Contract-vs-packaging distinction is real in principle but is demonstrated only by the ablations; against raw PyOptiX several rows read as packaging."
    required_remedy: "Run the ablations against the OWL arm; report only the residual as the contract contribution."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 2
    verdict: "NOT_REVIEWABLE"
    severity_if_open: "P0"
    finding: "The list of moved responsibilities includes pipeline/SBT/GAS composition and lifecycle transitions, which OWL already owns."
    required_remedy: "Remove composition/lifecycle from the claimed increment against an OWL-aware baseline; keep the five contract mechanisms."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 3
    verdict: "PARTIAL"
    severity_if_open: "P0"
    finding: "Today an informed reviewer would say 'OWL plus validation glue', which is worse than the objection the CFR anticipates."
    required_remedy: "Ablation table against PyOptiX+OWL showing accepted-invalid whole-protocol programs with attributable wrong results and accepted valid controls."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 4
    verdict: "PASS"
    severity_if_open: "NONE"
    finding: "Verified against the Slang capability guide; the boundary is accurate and non-hostile, and leaf-compiler use is credible."
    required_remedy: ""
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 5
    verdict: "PASS"
    severity_if_open: "NONE"
    finding: "Verified against the Dr.Jit abstract; the concession on global optimization is correct."
    required_remedy: ""
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 6
    verdict: "PASS"
    severity_if_open: "NONE"
    finding: "Verified against the CrossRT abstract including SDF and 3D Gaussian splatting; not dismissed as rendering-only."
    required_remedy: ""
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 7
    verdict: "PARTIAL"
    severity_if_open: "P2"
    finding: "Descriptive boundary survives; the 'a translator could target RTDL' half is unevaluated by any planned experiment."
    required_remedy: "Demote to future work, or supply a written CrossRT-to-RTDL role/effect/ABI mapping."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 8
    verdict: "PASS"
    severity_if_open: "P2"
    finding: "No residual absolute claim in the CFR language; two structural implication risks remain (rubric confound, taxonomy breadth)."
    required_remedy: "Apply the P1-2 rubric split and the P3-1 taxonomy realizability guard."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 9
    verdict: "NOT_REVIEWABLE"
    severity_if_open: "P1"
    finding: "Closure conditions are correct in content; three days of new public API with three dependent goals and no fallback is the live risk."
    required_remedy: "Freeze the dated descope ladder before Goal5795 starts."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 10
    verdict: "PARTIAL"
    severity_if_open: "P1"
    finding: "Tasks are different and non-rendering; fairness unestablished because the baseline's intersection-program authoring path is unfrozen and probably CUDA."
    required_remedy: "Freeze and report the baseline device path; split the rubric; verify five-mechanism coverage by the two tasks."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 11
    verdict: "PARTIAL"
    severity_if_open: "P0"
    finding: "Rubric design is sound but is missing the OWL arm, the protocol/language split, and a 'remains application-owned' column."
    required_remedy: "Add all three."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 12
    verdict: "PASS"
    severity_if_open: "NONE"
    finding: "The five mechanisms are well chosen, mutually distinct, and are precisely the residual over an OWL-class library."
    required_remedy: ""
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 13
    verdict: "PARTIAL"
    severity_if_open: "P2"
    finding: "Mechanism 5 (executable identity) risks reducing to a digest test; mechanism 3 (physical binding) risks reducing to a declaration mismatch."
    required_remedy: "Require a coherently resealed semantically plausible mispairing for (5) and a wrong output rather than a mismatched declaration for (3)."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 14
    verdict: "FAIL"
    severity_if_open: "P1"
    finding: "No mutation-liveness test is specified. The historical inert effects defect was found by mutating the leaf and observing an unchanged verdict; rejection tests cannot detect that class."
    required_remedy: "For all five mechanisms: mutate only the mechanism's own declaration in an accepted program, reseal all certificates, require the verdict to change; publish the mutation set and verdict deltas."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 15
    verdict: "PARTIAL"
    severity_if_open: "P1"
    finding: "Fairness intent is strong; the community's actual baseline is PyOptiX+OWL, and the device-authoring path is unfrozen."
    required_remedy: "Add the OWL arm; freeze the device path; have the external checkpoint judge baseline implementation quality before any measurement."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 16
    verdict: "PASS"
    severity_if_open: "P3"
    finding: "Timer and evidence boundaries are better specified than most published GPU work; run order between arms is unfrozen."
    required_remedy: "Freeze run order and interleaving between arms."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 17
    verdict: "PASS"
    severity_if_open: "P2"
    finding: "Yes, with disclosed cost and no imposed ratio. Missing qualitative evidence: baseline diagnostic experience per defect, cost attribution, and TCB placement in the body."
    required_remedy: "Capture what the baseline developer actually observes for each ablated defect; attribute any RTDL cost by phase; put the TCB statement in the paper body."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 18
    verdict: "PARTIAL"
    severity_if_open: "P0"
    finding: "Nothing is unnecessary. Missing: OWL arm, mutation-liveness test, mechanism-by-task coverage matrix, anonymization gate, descope ladder."
    required_remedy: "Add all five inside Goals 5794/5796/5797/5799; no new goal required."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 19
    verdict: "PARTIAL"
    severity_if_open: "P2"
    finding: "Strict enough against the named substitution risk; missing adverse-result placement, double-blind compliance, and mutation-liveness in condition 4."
    required_remedy: "Add conditions 8 and 9; strengthen condition 4."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}
  - id: 20
    verdict: "PARTIAL"
    severity_if_open: "P0"
    finding: "Plausible but not comfortable. Most decisive missing contribution: the OWL comparison. Most decisive missing experiment: mutation-liveness of the five mechanisms."
    required_remedy: "Execute both."
    evidence_access: {implementation_inspected: false, generated_artifacts_inspected: false, raw_measurements_inspected: false, strategy_only_assessment: true}

claim_audit:
  core_claim: "PARTIAL"
  pyoptix_boundary: "PARTIAL"
  slang_boundary: "PASS"
  drjit_boundary: "PASS"
  crossrt_boundary: "PARTIAL"
  owl_boundary: "FAIL"
  approved_claims:
    - "For its admitted bounded subset, RTDL makes a complete traversal-driven callback protocol the compilation unit for repurposed OptiX applications."
    - "On the evaluated matched tasks, RTDL transfers specified declared protocol responsibilities from application code to compiler validation and generation, measured against a frozen current PyOptiX baseline and a frozen OWL baseline, with protocol-ownership transfer reported separately from device-language change."
    - "RTDL rejects demonstrated whole-protocol violations before launch that the ablated system and the baselines accept, with attributable wrong results and accepted nearby valid controls."
    - "RTDL preserves exact outputs against an independent CPU oracle on the evaluated tasks."
    - "The lifecycle-separated costs of RTDL against the frozen baselines are as reported, with preparation never hidden."
    - "Application algorithms, semantic oracles, and declared trusted physical partners remain application-owned."
  prohibited_claims:
    - "first Python OptiX, first Python callbacks, first Python-to-PTX"
    - "PyOptiX, OWL, Slang, Dr.Jit or CrossRT cannot implement or cannot solve"
    - "universal semantic correctness, completeness, or mechanized proof"
    - "arbitrary-new-application admission, generalization rate, or any prospective-generalization result"
    - "all application families or all OptiX workloads"
    - "easier, simpler, less code, more productive, or better than CUDA/OptiX/PyOptiX/OWL"
    - "performance superiority over any baseline without matched evidence; universal no-slower"
    - "production, GA, public release"
    - "artifact governance or research-process discipline as academic novelty"
    - "taxonomy vocabulary breadth presented as executable capability"
  required_disclosures:
    - "Prospective new-problem generalization exams = 0; Goal5793 terminated under its frozen no-repair/no-rerun rule after one live provider response violated its frozen source-URL parser."
    - "Usability studies = 0; developer-time studies = 0; functionally matched baselines exist only for the two evaluated tasks."
    - "Registered-lane semantic/physical inventory is 6 COMPATIBLE and 9 fail-closed UNKNOWN of 15."
    - "Registered row-local median criterion: V4 passes 16/34 and fails 18/34 (cold 4/15, prepared 12/19); CI classification gives 11 clear wins, 10 clear losses, 13 uncertain. These are V2-direct vs V4 and are not a PyOptiX comparison."
    - "Current ceilings: 32 payload slots, 8 attribute slots, trace depth 1, callable depth 0; two geometry mechanisms only."
    - "Registered-interface loader encapsulation is 8/9; RayDB uses a private loader."
    - "A historical checker accepted emptied roles[].effects after resealing until a hostile audit exposed it; mechanism liveness is therefore demonstrated by mutation, not by seals."
    - "False-rejection rate on valid controls, and the fraction of matched-task work expressible inside the bounded subset without escape."
    - "Remaining TCB, in the paper body."

experiment_audit:
  matched_tasks: "PARTIAL"
  public_api_gate: "PASS"
  pyoptix_baseline_fairness: "PARTIAL"
  owl_baseline_presence: "FAIL"
  responsibility_rubric: "PARTIAL"
  executable_ablations: "PARTIAL"
  mechanism_liveness_testing: "FAIL"
  timer_and_preparation_scope: "PASS"
  exactness_and_oracle: "PASS"
  reproducibility: "PASS"

go_no_go:
  goals5794_to_5798: "CONDITIONAL_GO"
  blocking_conditions:
    - "P0-1: OWL added to related work, frozen as a baseline arm, and reflected in the responsibility rubric and every ablation."
    - "P1-1: double-blind anonymization gate for paper and artifact, with a frozen scrub checklist and named owner."
    - "P1-2: baseline device-authoring path frozen and reported; rubric split into protocol-ownership transfer and device-language change, never summed."
    - "P1-3: RT-core repurposing related-work axis added, anchored on the 2026 literature review."
    - "P1-4: dated descope ladder and named alternative venue frozen before Goal5795 begins."
    - "Q14: mutation-liveness test specified and executed for all five mechanisms."
    - "P2-3: mechanism-by-task coverage matrix produced before implementation."
    - "P2-2: adverse-result placement rule added to the September 3 gate."
  minimum_remaining_evidence:
    - "Five executable single-factor ablations with accepted-invalid cases, attributable wrong results, accepted nearby valid controls, and proof no independent validator rejected first."
    - "Mutation-liveness verdict deltas for all five mechanisms."
    - "Three-armed source-backed responsibility matrix (raw PyOptiX / PyOptiX+OWL / RTDL)."
    - "Both matched tasks exact on all implemented arms against an independent CPU oracle."
    - "Public Callback-Protocol GPU lifecycle closed with no internal escape in the matched tasks."
    - "Lifecycle-separated matched performance on the frozen Linux host, or a preregistered disclosed inability."
  september_3_gate: "REVISE"
  submission_authorized: false
  rationale: >
    The contribution thesis is a genuine compiler thesis, correctly and narrowly scoped, and its
    related-work boundaries are accurate against every primary source the CFR names. A 2026 published
    literature review of RT-core general-purpose computing surveys no programming abstraction for the
    space, which is strong third-party support for the gap. The path can therefore produce a CGO
    contribution. It cannot do so as currently planned, because the responsibility rubric and the
    ablations are designed against a raw PyOptiX baseline while the community's actual baseline is
    PyOptiX plus NVIDIA OWL, which already owns pipeline, SBT and acceleration-structure composition.
    Corrected, the residual over OWL is exactly the five protocol-contract mechanisms, and demonstrating
    that those defects survive a mature composition library is a sharper result than the plan currently
    aims for. The schedule carries no slack and no pre-declared descope, which at eighteen days is the
    second-largest risk after the baseline.

approval_guard:
  strategy_plan_approved: true
  implemented_core_approved: false
  reason: "This single-file CFR cannot approve the implemented core without a later exact-artifact review."

overall:
  p0_count: 1
  p1_count: 4
  p2_count: 3
  p3_count: 2
  verdict: "APPROVE_WITH_CONDITIONS"
  reviewer_summary: >
    The core positioning survives adversarial review and I do not recommend rejecting it. Whole
    traversal-driven callback protocol as the compilation unit, closed and fail-closed before OptiX
    composition, is a real compiler thesis; the claim ceiling is narrow enough to defend; and every
    related-work characterisation checks out against primary sources. One omission is likely fatal if
    it ships: NVIDIA OWL. OWL already owns SBT construction, acceleration-structure build and refit,
    program and pipeline management, memory transfer and launch setup, and is used throughout the
    RT-repurposing community. The responsibility rubric credits several of those rows to RTDL against a
    raw PyOptiX baseline no practitioner uses. A skeptical reviewer will ask whether this is OWL plus a
    type checker, and the plan has no answer. Fixing it strengthens the paper: the residual over OWL is
    precisely the five contract mechanisms, and showing those defects survive a mature composition
    library is the strongest available result. Four further blockers: CGO 2027 is double-blind and the
    plan has no anonymization gate; the baseline's device-authoring path is unfrozen and probably CUDA,
    which would confound the rubric with a language change the paper forbids claiming; the RT-core
    repurposing literature is absent, including a 2026 review that supports the gap; and nothing
    pre-declares what to do if the public API slips. Add the mutation-liveness test the project's own
    inert-effects history demands. Conditional go.
```

---

## 7. Non-authorization

This review approves the **plan**, conditionally. It does not certify the implemented Callback-Protocol IR, its public API, any mechanism ablation, baseline fairness, or the paper's final novelty claim, none of which I have seen. It authorizes no submission, publication, public release, performance claim, usability or productivity claim, generalization claim, arbitrary-new-application admission, mechanized-proof claim, or production/GA status. A favorable ruling here must not be cited as external validation of any of those.

Generalization exams: **0**. Usability studies: **0**. Functionally matched baselines: **0**. Goal5793 prospective-generalization objective: **terminal-negative, undischarged**.

---

*External review complete. P0 = 1, P1 = 4, P2 = 3, P3 = 2. Disposition: APPROVE_WITH_CONDITIONS.*

## Sources

- [CGO 2027 call for papers](https://conf.researchr.org/track/cgo-2027/cgo-2027-papers)
- [NVIDIA otk-pyoptix](https://github.com/NVIDIA/otk-pyoptix)
- [Writing Ray Tracing Applications in Python Using Numba for PyOptiX](https://developer.nvidia.com/blog/writing-ray-tracing-apps-in-python-using-numba-for-pyoptix/)
- [Slang capability system](https://shader-slang.org/slang/user-guide/capabilities)
- [Dr.Jit: A Just-In-Time Compiler for Differentiable Rendering](https://arxiv.org/abs/2202.01284)
- [CrossRT](https://arxiv.org/abs/2409.12617)
- [NVIDIA OWL — The OptiX Wrappers Library](https://github.com/NVIDIA/OWL)
- [Introducing OWL: A Node Graph Abstraction Layer on top of OptiX 7](https://ingowald.blog/2020/11/08/introducing-owl-a-node-graph-abstraction-layer-on-top-of-optix-7/)
- [Ray Tracing Cores for General-Purpose Computing: A Literature Review](https://arxiv.org/abs/2603.28771)
- [A Case Study for Ray Tracing Cores: Performance Insights with Breadth-First Search and Triangle Counting in Graphs](https://dl.acm.org/doi/10.1145/3727108)
- [Repurposing GPU Ray Tracing Architecture for Accelerating Irregular Programs](https://hammer.purdue.edu/articles/thesis/Repurposing_GPU_Ray_Tracing_Architecture_for_Accelerating_Irregular_Programs/29613995/1)
