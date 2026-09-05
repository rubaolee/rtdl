# Call for critical review: RTDL progress since the 2026-08-29 Claude review

Date: 2026-09-05

Target venue: CGO 2027

Review class: adversarial compiler/systems architecture, generality, evidence,
baseline-fairness, and claim-boundary review

Requested reviewer: Claude, acting as an independent critical reviewer

Repository: `rtdl_v4_restricted_python_design`

Absolute repository root on this machine:
`/Users/rl2025/rtdl_v4_restricted_python_design`

Current branch: `codex/cgo-goal5836-handoff`

Committed baseline at request creation:
`5de0e7ec3a48af73b2e645a5ff0edaae9b8c6696`

## CGO mission card for a reviewer with zero project memory

Read this section before the goal history. Goal numbers are evidence addresses,
not the research contribution.

**What we are building.** RTDL V4 is a restricted-Python compiler and runtime
for non-rendering NVIDIA OptiX programs. Its proposed compiler contribution is
to make the complete cross-callback protocol, rather than an isolated callback
or kernel, the compilation and admission unit. The compiler checks role
effects, semantic ABI ownership, physical geometry/buffer/SBT binding,
fail-closed continuation/completeness, and executable identity before an exact
result is published.

**The paper's one-sentence thesis.** After a developer chooses an RT
formulation, a compiler can treat the complete host/callback/continuation
protocol as a typed, identity-bound compilation unit, reject selected globally
incoherent compositions that individually legal CUDA/OptiX fragments do not
exclude, and execute bounded admitted protocols through true OptiX without an
unacceptable public-path performance tax.

**System boundary that the review must preserve.** Do not infer the
architecture from application names. The intended ownership split is:

| Layer | Owns | Must not own or claim |
|---|---|---|
| Application/case study | Choice of RT mapping, domain geometry, predicates, application oracle, and result meaning | Compiler admission policy or generic native dispatch |
| Restricted-Python language | Closed callback-local syntax, types, effects, bounded control flow, and resource contracts | Arbitrary Python, arbitrary CUDA, imports, allocation, reflection, or unrestricted atomics |
| Callback-Protocol IR/compiler | Role topology, semantic ABI ownership, whole-protocol obligations, target refinement inputs, and deterministic identities | Automatic discovery of a profitable RT formulation or proof of application correctness |
| Public runtime/lifecycle | Materialize, prepare, execute, status-gate, publish exact result, and close under bound identities | Checker-off fast paths, stale mutable identity caches, or partial-result publication |
| Trusted native OptiX provider | Generic compiler-owned wrappers, GAS/pipeline/SBT construction, traversal, bounded generic continuation, and physical receipts | Collision, database, graph, robot, paper, or other application-specific formulas and dispatch |
| Evaluation | Exact output contracts, strong same-contract baselines, adverse-result custody, and bounded claim gates | Native-kernel-only speedups, unmatched work placement, application-count generality, or import-dominated language claims |

The architecture is defective if the recent sphere, curve, collision, or
performance work crosses these boundaries merely to obtain a passing example
or timing result.

**Why this problem matters.** Repurposed RT-core applications distribute one
logical computation across host setup, geometry, raygen/intersection/any-hit or
closest-hit callbacks, payload conventions, continuation, status, and the
eventual native executable. Individually compilable CUDA/OptiX fragments can
therefore compose into a globally incoherent or incomplete protocol. RTDL does
not choose the ray-tracing formulation; it aims to make a developer-chosen
formulation statically admissible, identity-bound, and fail closed.

**What changed since the last Claude review.** The project added bounded
built-in sphere and curve paths, a collision case study that keeps swept-shape
and collision meaning outside the engine, one preregistered prospective
new-topology exam against a frozen schema-driven core, an independently
implemented target-side refinement checker, causal performance attribution,
and several public-path/startup repairs. These additions are evidence probes,
not an application-count argument. The review must decide whether they show a
real bounded compiler architecture or merely more hand-built special cases.

**Research chain since the previous review.** This table is the navigation
map; the later sections contain the evidence and limitations.

| Work | Reviewer attack it was meant to address | Current honest status |
|---|---|---|
| Goals5830-5832 | Unstable public terminology and no explicit protocol-shape specification | Public bounded example, denominator repair, and reference algebra; not a generic GPU compiler result by themselves |
| Goals5833-5834 | Only custom/triangle physical routes | Bounded true-OptiX sphere and round-linear-curve routes; functional evidence, not complete primitive coverage or performance evidence |
| Goals5835-5837 | No realistic cross-callback pressure and risk of application logic entering the engine | Bounded collision case study plus app-neutral owner-grouped Boolean route; not full RT-CCD and not a Paper App |
| Goal5838 | Prior prospective-generalization count was zero | One preregistered selected topology passed with three frozen generic-core files unchanged; bounded evidence only |
| Goal5839 | No real-artifact evidence that protocol defects matter | Incomplete census with zero classified sources; no prevalence claim |
| Goal5840 | Compiler and lowering were effectively checking themselves | Separately implemented checker passed a frozen bounded denominator; not a soundness theorem |
| Goal5841 | No evidence that another human can author with RTDL | Unfinished and unavailable before submission; all ease/productivity claims must be removed |
| Goals5842-5847 | Weak baselines, unexplained overhead, and favorable boundary selection | Causal diagnosis and multiple generic repairs, including preserved adverse results; all performance statements remain exact-task and endpoint specific |
| Goal5848 | Latest honest post-import result is still materially slower than pinned precompiled PyOptix | Strong-baseline experiment and repairs are locally implemented, but formal GPU evidence is `0/2`; no result exists yet |

**Current highest objective.** Submit the strongest scientifically honest,
anonymous, reproducible CGO 2027 paper supportable by 2026-09-10. Only five
calendar days remain. Optimize the review for a submission decision and the
smallest high-value repair set, not for feature breadth, historical narration,
or perfecting evidence infrastructure.

The decisive question is not whether the repository contains substantial
engineering. It is whether the exact bounded contribution and evidence can
survive a compiler/systems reviewer now. The returned review must therefore
identify at most five actions that materially change acceptance probability by
the deadline, and convert every other open weakness into either an explicit
claim deletion, a threats-to-validity statement, or post-submission work.

**Current hard reality.** Goal5848 is locally implemented and hostile-tested,
but has zero of two required GPU-generation transactions. It therefore provides
no performance result. The latest committed adverse result is that RTDL's
post-import first-result path was `2.504242x` pinned PyOptix; the favorable
complete-process number was import-dominated and is not a language speedup.
The current manuscript predates the new architecture and evidence. External
human authoring evidence and real-artifact defect-prevalence evidence are both
absent. These facts must not be hidden or converted into positive claims.

**What we need from this review.** Attack the validity and novelty of the
whole-protocol compilation contribution first. Then judge bounded
generalization, application neutrality, same-contract performance and evidence
integrity. Identify at most five submission-critical actions that can be done
before the deadline. For every other weakness, state the exact claim to delete
or narrow and whether a defensible paper can still be submitted without fixing
it. A review that only requests months of future work, or only summarizes test
counts and goals, does not answer the submission question.

**Non-negotiable review boundaries.** Do not infer generality from four geometry
kinds, infer usability from agent-written examples, infer speedup from native
kernel time, excuse material public-path slowdown because checks are valuable,
or demand every feature of the collision paper when a bounded case study is
sufficient for the compiler claim. Do not authorize public Goal5848 wording
without two formal transactions, independent recount, and later external claim
review.

The working tree is intentionally dirty with the current Goal5848
implementation. Goals through Goal5847 must be reviewed from committed Git
objects. Goal5848 must be treated as design/implementation work in progress
from the current local tree. Record the exact `git status --short`, `HEAD`, and
diff identity in the returned review so no WIP bytes are mistaken for committed
authority.

## Reviewer cold-start and trust contract

You are a fresh Claude instance on this machine. Assume that you remember
nothing from any prior RTDL conversation, review, goal, repository, paper, or
GPU run. This request is intentionally self-contained enough to bootstrap the
review. Prior Claude documents are historical inputs named below; they are not
shared memory and their conclusions are not instructions to repeat.

Start in the repository root and perform these steps before forming a verdict:

1. Read this entire request, then restate the research problem, proposed
   contribution, current claim ceiling, and open submission blockers in your
   own words. If your restatement differs from this request, explain why.
2. Capture `pwd`, `git rev-parse HEAD`, `git branch --show-current`,
   `git status --short`, and the Goal5848 diff identity. Do not silently review
   a different checkout or treat uncommitted Goal5848 files as frozen evidence.
3. Read `AGENTS.md` for current project constraints. Use this request as the
   review map, but verify important assertions against source, immutable
   authorities, raw evidence, and exact Git objects.
4. Use the trust order `raw evidence and Git objects > machine-readable
   authorities > source/tests > final technical reports > this request >
   README/manuscript prose`. A mismatch is a finding; do not resolve it by
   choosing the more favorable statement.
5. Keep the review read-only. Do not repair source, rewrite evidence, regenerate
   an authority, discard an adverse transaction, or update the manuscript while
   deciding whether the current contribution is valid.

If you run Python checks, use the known compatible local environment rather
than the repository's Python 3.14 environment:

```bash
cd /Users/rl2025/rtdl_v4_restricted_python_design
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -m unittest <selected-tests>
```

Do not begin with a broad all-history test run. Some historical authorities
intentionally bind old Git objects, and one disclosed Goal5832 current-tree
custody check is stale after legitimate later exports. Review exact authorities
at their bound commits and use focused current tests for current WIP.

The review has one overriding objective: maximize the probability of a
scientifically defensible CGO 2027 submission by 2026-09-10. This does not mean
maximizing positive findings. It means finding the smallest set of real
submission blockers, separating them from removable claims and post-deadline
work, and refusing both fatal overclaim and unbounded scope expansion.

Prioritize findings in this order: validity of the compiler contribution,
credible bounded generalization, app-neutral engine boundaries, fair
same-contract performance, evidence integrity, then manuscript/artifact
hygiene. Do not recommend another application merely to increase a count. Do
not spend the remaining days polishing evidence machinery unless it closes a
named falsification or custody threat.

## 0. Self-contained project primer and submission objective

### 0.0 Paper in one paragraph

RTDL asks whether non-rendering OptiX programs can be made safer and easier to
construct by compiling the *whole callback protocol* rather than exposing a
collection of individually legal Python/CUDA/OptiX fragments. A developer still
chooses the RT formulation and application geometry. RTDL accepts a deliberately
restricted Python callback language, builds typed role-indexed Callback IR,
checks effects, semantic ABI ownership, physical binding, fail-closed
continuation, and executable identity across callback and host boundaries, then
lowers admitted leaves through compiler-owned OptiX wrappers. The intended CGO
contribution is this protocol-level compilation and admission architecture,
plus bounded prospective generalization and target-refinement evidence. It is
not automatic RT mapping, arbitrary Python compilation, full OptiX coverage, a
soundness theorem, or a claim that every workload is faster. The submission is
viable only if the genericity evidence is more than disguised special cases and
the verified public path stays within a reasonable measured overhead of a strong
same-contract PyOptix implementation and Direct OptiX.

### 0.1 Immediate situation

Assume no prior knowledge of RTDL or its goal history. The CGO 2027 submission
date is fixed at 2026-09-10, five days after this request. The highest objective
is not to maximize implemented features. It is to produce the strongest
scientifically honest, anonymous, reproducible CGO paper that the evidence can
support by the deadline.

Your review must therefore distinguish:

- a fatal flaw in the contribution or evidence;
- a blocker that can credibly be repaired before 2026-09-10;
- an unsupported claim that can be removed or narrowed without invalidating
  the paper;
- valuable follow-on work that is impossible or unnecessary before this
  submission.

Do not make a months-long study the only recommendation without also stating
whether a narrower paper remains submit-worthy now. Conversely, do not lower
scientific standards merely because the deadline is close.

The current manuscript and root README are not synchronized with the new
evidence. `paper/cgo2027/main.tex` still describes the 2026-08-29 state,
including two fixed constructors and zero prospective new-topology exams. The
root `README.md` currently links to an absent `docs/v4/` tree and instructs
`pip install -e .` even though this checkout has no packaging metadata that
authorizes an editable-install claim. Treat these as disclosed submission and
artifact blockers to classify and repair, not as evidence against or in favor
of the underlying compiler contribution.

### 0.2 What RTDL is

RTDL V4 is a research language/compiler/runtime for expressing bounded
non-rendering computations that intentionally repurpose NVIDIA OptiX traversal.
The user writes callback-local behavior in a closed, typed subset of Python.
RTDL parses that source as data and never imports or executes it as host Python.
The intended pipeline is:

```text
restricted Python callback text
             |
             v
typed, role-indexed Callback IR + effect/resource proof
             |
             v
whole-protocol semantic/physical/continuation/identity admission
             |
             v
isolated Numba device leaves + compiler-owned trusted OptiX wrapper
             |
             v
target-bound materialize -> prepare -> execute* -> close lifecycle
             |
             v
status-gated exact output + behavioral traversal receipt
```

The restricted language rejects imports, reflection, allocation, recursion,
dynamic loops, arbitrary calls, raw pointers, user PTX, unrestricted atomics,
and exception-based device control flow. Numba is used to compile isolated
admitted device leaves. The trusted compiler/runtime owns raw OptiX mechanics,
including traversal orchestration, pipeline/SBT construction, device status,
and output publication. Optional Numba/CuPy composition may perform admitted
bulk non-traversal continuation, but that is not the central contribution.

This V4 research line is distinct from the older v2.3 app-portfolio release.
Do not use v1/v2 claims, architecture, benchmark labels, or partner roadmap as
evidence for this V4 paper unless an exact V4 authority imports them.

### 0.3 The problem RTDL claims to address

Repurposed ray-tracing programs are protocols distributed across host code,
multiple device callbacks, payload and attribute conventions, geometry and SBT
bindings, continuation/reduction logic, error/overflow status, and the exact
executable eventually launched. CUDA/OptiX may accept every individual module
while the complete application protocol is semantically incoherent.

Representative failure classes are:

- a producer writes an application item identifier while a consumer interprets
  the same slot as a primitive index;
- one callback omits state required by a downstream role;
- a host consumes truncated output after overflow or failed device status;
- a physical geometry/SBT/layout binding disagrees with callback assumptions;
- a reviewed declaration is paired with different generated code or native
  provider bytes at execution.

The paper names five whole-protocol properties:

| Property | Meaning |
|---|---|
| `CP001_ROLE_EFFECT_CLOSURE` | Allowed role effects and required cross-role effect topology agree. |
| `CP002_SEMANTIC_ABI_OWNERSHIP` | Payload, attribute, SBT, and result meanings have consistent producers, consumers, and ownership. |
| `CP003_PHYSICAL_BINDING` | Callback assumptions agree with geometry, GAS/SBT, buffers, layouts, fields, reducers, and target binding. |
| `CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS` | Failure, overflow, truncation, or incompleteness prevents result publication or continuation. |
| `CP005_EXECUTABLE_IDENTITY_CHAIN` | The admitted protocol is bound to generated source/PTX, provider/native objects, target, and launched executable. |

The central research question is intentionally narrower than automatic mapping:

> After a developer has chosen a ray-tracing formulation, can the complete
> cross-callback protocol become the unit of compilation and admission, so that
> selected locally legal but globally incoherent programs are rejected before
> launch or result consumption?

### 0.4 The intended contribution

The contribution hypothesis to judge is:

1. **Compilation-unit insight.** The complete callback protocol, not one kernel
   or API call, is the right unit for compiling and admitting repurposed RT
   computations.
2. **Language and IR.** Restricted Python is lowered to a backend-neutral,
   typed, role-indexed Callback IR with bounded control flow, effects, numeric
   and resource contracts, and deterministic identity.
3. **Whole-protocol admission.** Callback IR is combined with separately
   sourced semantic, physical, continuation/completeness, target, provider, and
   executable authorities to enforce CP001-CP005 as one obligation set.
4. **Target realization.** Admitted programs are lowered through compiler-owned
   wrappers into true OptiX executions while the public lifecycle carries
   identities and fail-closed status from materialization through close.
5. **Bounded extensibility evidence.** A schema-driven core should allow at
   least one independently selected new protocol topology without modifying
   that frozen core, while independent target-side checking tests a declared
   refinement relation.
6. **Practicality.** For exact supported tasks, the public verified path should
   remain reasonably close to strong PyOptix and Direct CUDA/OptiX baselines.
   Performance is part of the contribution's viability; security or abstraction
   benefits do not excuse an avoidably slow implementation.

Items 5 and 6 were the largest engineering/evidence changes after the last
Claude review. They must be judged critically rather than accepted from the
project's labels.

### 0.5 What RTDL does not claim to solve

RTDL does not discover profitable ray-tracing mappings, translate arbitrary
Python, replace CUDA, expose the full OptiX API, prove arbitrary accepted
programs correct, or take responsibility for application algorithms and
semantic oracles. The application still owns the choice of RT formulation,
domain geometry construction, application-specific predicates, and final
meaning of the result.

The compiler should be application-neutral. A benchmark or case study may say
database, graph, collision, robot, or simulation; generic engine/runtime code
must instead express reusable behavior such as bounded relation, checked
reduction, first contact, or owner-grouped any-hit. Any application name,
formula, predicate, or paper-specific special case in the engine is a serious
architecture finding.

### 0.6 Why sphere, curve, and collision were added

These additions were not intended to inflate an application count.

- **Sphere** tests whether the protocol mechanism crosses from custom/triangle
  routes to an OptiX built-in primitive with compiler-owned intersection
  behavior.
- **Curve** completes bounded presence across the four pinned OptiX leaf-kind
  categories and exposes numeric/domain mismatches that a toy triangle-only
  system would not reveal.
- **Collision detection** pressures the abstraction with a real cross-callback
  any-hit workload. It asks whether a reusable owner-grouped Boolean reduction
  can live in the language/runtime while swept-sphere construction and
  collision meaning remain outside the engine.
- **Goal5838's prospective topology** then tests whether the schema-driven core
  can admit a selected new sphere/count/continue topology without changing the
  frozen generic files.

The value of this sequence is therefore architectural: physical diversity,
new callback topology, continuation behavior, and resistance to application
leakage. Full reproduction of every collision-paper feature is not required
unless it is necessary to validate that compiler argument.

### 0.7 Original and current public surface

Before this review interval, the stable V4 public GPU surface centered on two
fixed protocol constructors:

- a custom-AABB bounded canonical relation;
- a built-in-triangle checked reduction.

There was also one bounded caller-authored built-in-triangle Callback-IR
template. The system had application examples, but no prospective frozen-core
new-topology success and no external human author.

The post-review work adds bounded sphere and curve lifecycles, a root-exported
owner-grouped curve any-hit successor, a schema-driven generic lifecycle, one
prospective selected topology, and independent target refinement evidence. A
major review task is to decide whether this is a real move from closed
constructors toward bounded compiler extensibility or only a larger collection
of special cases.

The pre-existing application portfolio contains nine project-authored ports of
published RT mappings and thirteen selected lanes: triangle counting, particle
tracking, RayDB, Hausdorff distance, RTNN, RT-DBSCAN, X-HD, three Spatial
RayJoin lanes, and RT-BarnesHut. They exercise the base callback path and six
application-neutral composition batches. They are evidence of current-route
diversity and exact selected behavior, not third-party authorship, automatic
mapping, representative sampling, or thirteen independent protocol shapes.
The newer collision case study is separate and remains explicitly below Paper
App status.

Terminology used in the remainder of this request:

| Term | Meaning in this project |
|---|---|
| `true OptiX` | A receipt establishes actual OptiX API construction and `optixLaunch`/traversal. On Pascal this does not imply hardware RT-core silicon. |
| `RT-core evidence` | True OptiX execution on an RTX-generation GPU where hardware traversal units exist; still not automatically proof of speedup attribution. |
| `public path` | The documented RTDL lifecycle with all required admission, status, identity, output, and close obligations enabled. |
| `prepared steady` | Repeated execution after admitted program and static target preparation; excludes setup only when the comparator uses the same endpoint definition. |
| `post-import` | Timing begins after implementation imports, preventing a large dependency import from deciding the comparison. |
| `complete process` | Fresh interpreter/process through first exact result, including imports and all arm-specific dependency startup. |
| `authority` | Machine-readable evidence with exact inputs, outputs, identities, gates, and an independently recomputable seal. It is not external peer review. |
| `preregistration` | An experiment contract committed before the registered run. A repaired successor must be a new transaction and preserve the failed predecessor. |
| `claim ceiling` | The strongest statement the exact evidence permits; broader wording remains forbidden even if intuitively plausible. |
| `Paper App` | A stricter status requiring exact paper/source fidelity and the declared execution/comparison gates, not merely a paper-inspired mapping. |
| `PyOptix` | The pinned NVIDIA `otk-pyoptix` source/compatibility route used as a Python OptiX construction baseline. Baseline work placement must always be stated. |
| `Direct` | A purpose-built CUDA/OptiX route used as a lower-bound diagnostic under an explicitly matched output contract. |

### 0.8 Evaluation philosophy

The paper must not trade performance truth for language claims. Comparisons
must use the same application output contract and disclose work placement,
imports, compilation, setup, prepare, traversal, continuation, validation,
D2H transfer, and result materialization. PyOptix baselines must distinguish an
idiomatic route from a strongest credible device-continuation route. Direct
CUDA/OptiX is a lower-bound diagnostic, not automatically an equivalent public
API. Adverse transactions are evidence and may not be deleted after repair.

The current performance target is not "RTDL wins every benchmark." It is:

> The cost of whole-protocol admission and the public lifecycle is measured,
> attributable, and reduced to a reasonable bounded overhead relative to a
> strong same-contract PyOptix implementation and Direct CUDA/OptiX, without
> disabling checks, moving work outside timers, weakening outputs, or adding
> application-specific native paths.

Goal5848 is the current attempt to meet this target for two exact tasks and two
RTX generations. It is not complete.

### 0.9 What this review must optimize for

The returned review must help make a submission decision and execute the final
days. In addition to scientific verdicts, produce a deadline-aware action
matrix with these columns:

| Finding | Fatal if unfixed? | Repair or descope | Estimated focused hours | Exact files/evidence | Must finish before 2026-09-10? |
|---|---|---|---:|---|---|

Rank no more than five submission-critical actions. For every larger follow-on
recommendation, explicitly say whether the paper can proceed without it and
what claim must be removed. The top priority is a correct contribution and
credible evidence; the second is finishing the strongest feasible paper by the
fixed deadline; feature breadth is not a priority.

## 1. Purpose of this review

Please review the work completed since the project's last substantive Claude
advice on 2026-08-29. You are not expected to remember that review; its exact
documents and diagnosis are reproduced below. At that checkpoint RTDL had not
yet implemented the public built-in
sphere route, built-in curve route, bounded collision-detection case study,
prospective frozen-core topology exam, independent target-side refinement
evidence, or the later performance-debt repairs.

This request is deliberately not a request for praise, governance approval, or
a summary of engineering effort. Judge whether the resulting compiler/language
contribution is scientifically meaningful, whether the evidence supports it,
and whether the remaining gaps are fatal for a CGO submission.

The most important question is:

> Did the post-review work transform RTDL from two closed, hand-built public GPU
> protocol families plus a checker into a credible bounded callback-protocol
> compilation system with prospective evidence, or did it merely add carefully
> engineered specializations around the same limitation?

Please answer this question directly. Do not count goals, tests, commits, or
evidence machinery as contribution by themselves.

## 2. Prior review boundary

Treat these two 2026-08-29 advisory documents as the immediate prior review:

- `history/internal_docs/reviewer_guidance_path_to_strong_accept_20260829.md`
- `history/internal_docs/reviewer_guidance_twelve_day_submission_plan_20260829.md`

For earlier context, also consult:

- `history/internal_docs/review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md`

The 2026-08-29 review's central diagnosis was:

| Issue at prior review | Prior state |
|---|---|
| Core insight | Strong: the complete callback protocol, not an isolated kernel, is the compilation unit. |
| Generality | Zero: two closed public protocol families, no arbitrary Callback IR GPU execution, and zero prospective exams. |
| Real-world problem evidence | Weak: constructed defects in author-controlled examples; no credible prevalence result. |
| External use | Zero third-party authors and zero usability studies. |
| Native baseline boundary | OWL, native OptiX payload semantics, Direct CUDA/OptiX, and strongest PyOptix residuals needed clearer treatment. |
| Evaluation integrity | Needed a fair descope ladder, causal admission cost, matched baselines, adverse-result custody, and no boundary shopping. |
| Submission outlook | A bounded honest paper might be defensible; a strong accept was not then supported. |

The reviewer specifically warned against manufactured generalization, using an
AI agent as a substitute for a human author, arm-specific optimization that
destroys baseline symmetry, asymmetric timing boundaries, and erasing adverse
transactions. Review the new work against those warnings.

## 3. Exact review scope and evidence maturity

The review period begins with Goal5830 and ends at the current Goal5848 working
state. No completed work in this interval has yet received external review;
this document requests the first consolidated post-2026-08-29 review. The
period contains five different evidence classes that must not be merged:

1. Committed, frozen functional or scientific authority: Goals5830-5838 and
   Goal5840.
2. A preregistered but incomplete empirical track: Goal5839 discovery, with no
   protocol-property classifications or paper-ready result.
3. Committed, frozen internal performance authority: Goals5842-5847.
4. A deliberately unavailable evidence category: Goal5841 external-human
   authoring; the count remains zero.
5. Uncommitted work in progress: Goal5848 implementation and local audit;
   formal GPU evidence remains `0/2` generations.

Do not certify Goal5848 as complete. You may review its design and current
implementation for readiness, fairness, hidden semantic specialization, and
evidence weaknesses. It has no authorized performance result.

## 4. Executive change inventory

### 4.1 Public semantics, terminology, and protocol specification

**Goal5830: public stable-sort demonstration.**

RTDL gained a public V4 stable-sort demonstration that encodes the ordering
problem into the supported protocol and executes it through the public
lifecycle. This is a bounded functional/value example, not a new protocol
family, a generality exam, or performance evidence.

Primary report:

- `history/internal_docs/goal5830_v4_public_stable_sort_technical_report_20260830.md`

**Goal5831: terminology and denominator repair.**

The project removed the misleading phrase "exactly two public GPU families"
and separated several denominators. The pinned OptiX 9 taxonomy has six build
input kinds and four leaf primitive kinds. At that checkpoint RTDL publicly
instantiated two build-input enum kinds, two physical geometry kinds, two fixed
protocol constructors, and one bounded caller-authored built-in-triangle
template. `4/4`, when later used, means leaf-kind presence only, never complete
category, topology, or application coverage.

Primary report:

- `history/internal_docs/goal5831_public_gpu_surface_terminology_and_denominator_report_20260830.md`

**Goal5832: protocol-shape algebra.**

The work froze a typed protocol-shape algebra `<G,R,V,E,H,B,C,X,L>`, separated
family shape, protocol instance, and deployment identities, and implemented an
exact recursive reference validator with hostile tests. This remains a
specification/reference validator. It was not a family-parametric GPU compiler
and did not by itself answer the prior generality attack.

Primary report:

- `history/internal_docs/goal5832_protocol_shape_algebra_equivalence_and_claim_ceiling_report_20260830.md`

One historical current-tree custody test is known stale because Goal5831 froze
the then-current root `src/rtdsl/__init__.py`, while later legitimate exports
changed that mutable file. The historical manifest was not rewritten.

### 4.2 New physical leaf kinds: sphere and curve

**Goal5833: built-in sphere public lifecycle.**

RTDL added the public `rtdsl.v4_sphere` lifecycle:

```text
verify source -> compile protocol -> materialize -> prepare -> execute* -> close
```

The provider uses `OPTIX_BUILD_INPUT_TYPE_SPHERES` and
`OPTIX_PRIMITIVE_TYPE_SPHERE`, obtains the built-in intersection module from
OptiX, supplies no user intersection program, and executes a deterministic
First Contact contract. Five fixtures matched an independent RTDL-free CPU
oracle exactly. The run used OptiX 9 on GTX 1070/Pascal, so it proves true
OptiX traversal but not RT-core-silicon execution. It contains no registered
timing.

This is a sphere-specific bounded instantiation. It is not a prospective
generic-core exam and does not establish universal sphere support.

Primary reports:

- `history/internal_docs/goal5833_builtin_sphere_first_contact_technical_report_20260830.md`
- `history/internal_docs/goal5833_a3_repaired_home_final_technical_report_20260830.md`

**Goal5834: built-in round-linear curve public lifecycle.**

RTDL added an app-neutral static built-in curve lifecycle using
`OPTIX_BUILD_INPUT_TYPE_CURVES` and
`OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, constant positive float32 radius per
segment, indexed two-point segments, default round endcaps, one GAS, one SBT
record, and no user intersection program. Four reader-checkable fixtures were
bit-exact against an independent capsule oracle. The same prepared object was
reused with a reversed query batch.

An important adverse result is preserved: a ray exactly collinear with a
capsule axis was accepted by the initial domain, the closed-capsule oracle
reported a hit, and OptiX reported a miss. The final route therefore rejects a
bounded near-parallel domain before launch. That repair is a post-observation
domain restriction, not proof of general capsule equivalence.

The final run used OptiX 9 on GTX 1070/Pascal. It is true OptiX functional
evidence, not RT-core-silicon or performance evidence. The resulting `4/4`
statement is only coarse leaf-kind presence.

Primary reports:

- `history/internal_docs/goal5834_builtin_round_linear_curve_technical_report_20260830.md`
- `history/internal_docs/goal5834_b3_boolean_collision_bridge_technical_report_20260830.md`

### 4.3 Collision-detection case study and generic owner-grouped behavior

**Goal5835: bounded Sui-derived collision mapping.**

The case study maps a constant-radius robot sphere moving along a piecewise
linear path segment to a swept capsule, the capsule to a round-linear curve,
and obstacle edges to finite Boolean curve queries. It reconstructs application
identity and computes `collision = OR(per_edge_hit)` in application space.

This is not full RT-CCD. Initial overlap, near-tangent/near-parallel contact,
face-interior-only collision, exact time of impact, and collided primitive
identity are outside the frozen scope. Goal5835 added no new GPU launches and
no timing; it bound app-shaped bytes to the already executed Goal5834-B3
functional evidence. It remains `NOT_A_PAPER_APP`.

Primary report:

- `history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_technical_report_20260830.md`

**Goal5836: exact author-source fidelity gate and negative result.**

The exact arXiv v2 paper and author commit were acquired and hash-bound. Static
source inspection found a material predicate difference: the author benchmark
uses a strongly connected directed obstacle-edge graph to preserve
inside-start correctness for one-sided rays against hollow round curves,
whereas Goal5835 keeps one arbitrary deduplicated edge direction and explicitly
excludes initial overlap.

The preregistered result is:

```text
MATERIAL_PREDICATE_DIFFERENCE
TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE
```

Therefore Goal5836 correctly stopped before input freeze, build, execution,
timing, author comparison, or Paper App promotion. This is a completed
negative scientific branch, not proof that RTDL cannot express collision and
not a successful paper reproduction.

Primary reports:

- `history/internal_docs/goal5836_a0_source_acquisition_technical_report_20260901.md`
- `history/internal_docs/goal5836_a1_source_fidelity_technical_report_20260901.md`
- `history/internal_docs/goal5835_goal5836_strict_internal_audit_20260901.md`

**Goal5837: generic owner-grouped any-hit Boolean route.**

The generic behavior is:

```text
accepted event = (query_id, primitive_id)
owner = owner_ids[primitive_id]
owner_hit_bits[owner] |= 1
```

The engine vocabulary contains no collision, robot, trajectory, pose, or
RT-CCD semantics. The built-in curve provider performs true `optixTrace`,
`atomicOr`, and `optixIgnoreIntersection`; the application owns geometry
construction, collision interpretation, and its oracle.

On RTX 4000 Ada / OptiX 8, ten workloads repeated three times produced 30/30
true OptiX launches and oracle matches. The largest functional workload had 512
owners, 4,096 primitives, 1,024 queries, and 4,194,304 independently evaluated
pairs. No timing was registered.

The exact classification remains:

```text
ADDITIONAL_ROOT_EXPORTED_CLOSED_SUCCESSOR_ROUTE
NOT_STABLE_V4_FIXED_CONSTRUCTOR
```

The stable fixed-constructor count remained two. Goal5837 cannot be
retrospectively called a prospective exam, third stable constructor, Paper App,
or performance result.

Primary report:

- `history/internal_docs/goal5837_owner_grouped_classification_20260902/TECHNICAL_REPORT.md`

### 4.4 Prospective generic-core evidence

**Goal5838: sealed generic core and independently selected topology.**

This goal was designed to answer the prior "generality zero" attack in a
bounded, falsifiable way. Before selecting the challenge, the project froze:

- `src/rtdsl/v4_family_schema.py`
- `src/rtdsl/v4_generic_family_lifecycle.py`
- `src/rtdsl/v4_family.py`

It also froze a ten-row challenge table and a public NIST pulse selection
procedure. The selected topology was:

```text
builtin_sphere::any_hit_count_continue_u64_per_query
```

After selection, only the declared provider/app/oracle/test/build extension
layers could change. On RTX 2000 Ada / OptiX 9, two true OptiX executions
matched all 12 independent rational-oracle rows. The three frozen core files
changed by zero bytes. An RTDL-free verifier reproduced the authority
byte-identically.

The exact status is:

```text
PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE
```

This is one prospective frozen-core new-topology success. It is not arbitrary
Callback IR execution, a universal provider-independent compiler, application
correctness, a Paper App, performance evidence, external review, or consensus.

Primary reports:

- `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_TECHNICAL_REPORT.md`
- `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md`
- `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json`

### 4.5 Problem-prevalence and external-use evidence

**Goal5839: real-artifact protocol-property census.**

The intended new census did not reach protocol-property extraction or a final
classification. Goal5839 froze a 29-work denominator, discovery order,
eligibility policy, five-property label system, independent-adjudication rule,
and responsible-disclosure gate. It then preserved GitHub and general-web
discovery results plus execution deviations, including the fact that GitHub
collection ran before the preregistered paper/publisher step and that one web
collection aborted before a later complete rerun.

The earlier Goal5820 result was:

```text
0 ENFORCED / 4 NOT_FOUND / 16 UNCERTAIN
```

That result is not a Goal5839 final result and was already classified as
non-paper-ready. Goal5839 currently has zero candidate-source classifications,
zero adjudicated violations, and no paper-ready prevalence result. Provider
disconnects and documented discovery deviations further constrain it.
`UNCERTAIN` is not a defect; `NOT_FOUND` is not proof that a property is
absent; neither Goal5820 nor Goal5839 may be converted into "20 real bugs" or a
prevalence percentage. Unless the reviewer identifies a defensible narrower
use, both should remain excluded from the paper's empirical motivation.

Primary records:

- `history/internal_docs/goal5839_real_artifact_protocol_census_20260903/PREREGISTRATION.md`
- `history/internal_docs/goal5839_real_artifact_protocol_census_20260903/DISCOVERY_EXECUTION_DEVIATIONS.md`
- `history/internal_docs/goal5839_real_artifact_protocol_census_20260903/DISCOVERY_EXECUTION_BINDING.json`
- `history/internal_docs/goal5839_real_artifact_protocol_census_20260903/INTERNAL_HOSTILE_SELF_REVIEW.md`

**Goal5841: external-human authoring.**

No independent human developer has authored a route through the new system.
External-author count remains zero and usability-study count remains zero. The
owner has stated that this experiment is not feasible before submission. AI
agents, project authors, and independent verifiers must not be substituted for
human usability evidence.

Please state whether this absence is fatal, merely a limitation, or requires a
specific manuscript descope.

### 4.6 Independent target-side lowering/refinement

**Goal5840: bounded independent refinement evidence.**

A separately implemented target-side checker evaluated three route groups,
four modes, and five structural properties. Attempt 7 passed all four true
OptiX modes on RTX 2000 Ada / OptiX 9. The independent checker passed 20/20
property applications, and 15 unique frozen mutations were rejected across 20
mode applications. Attempts 1-6 remain preserved failures. The Goal5838 frozen
core changed by zero bytes.

The exact status is:

```text
PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE
```

This is bounded structural lowering/refinement evidence, not a compiler
soundness theorem, arbitrary Callback IR support, application correctness,
performance evidence, external review, or consensus.

Primary reports:

- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_TECHNICAL_REPORT.md`
- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md`
- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_AUTHORITY.json`

### 4.7 Causal performance diagnosis and repairs

**Goal5842: causal admission-cost and fair-provider baseline.**

The V12 experiment ran independently on RTX 2000 Ada and RTX A6000 Ampere with
distinct GPU UUIDs. Each generation retained 216 causal receipts, 216 baseline
subworker receipts, 108 composites, and seven passing formal stages. The
cross-generation gate passed without pooling raw times or computing invalid
cross-machine timing ratios.

The central causal result was adverse but useful: generic admission has a
measurable cost, but target materialization plus native preparation dominate
setup. On Ampere, prepared steady RTDL/PyOptix ratios were approximately 3.13x
for the relation path and 155.21x for triangle. These are current
implementation deficits, not intrinsic language costs. All adverse rows remain
preserved.

Primary report:

- `history/internal_docs/goal5842_causal_admission_cost_20260903/FORMAL_V12_AMPERE_SECOND_GENERATION_AND_CROSS_GENERATION_REPORT.md`

**Goal5842R1: implementation repair, not a comparison result.**

The implementation added validated prepared-target reuse, removed repeated
Python immutable-input scans, moved triangle checked-U64 reduction to a generic
device-resident path, and returned only the public scalar. Three nonformal
RTX A6000 repeats measured roughly 0.289-0.295 ms for the triangle scalar and
matched exact scalar/per-ray oracles. This was diagnostic engineering evidence;
it was not a fresh fair baseline.

Primary report:

- `history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903/FINAL_TECHNICAL_REPORT.md`

**Goal5843: fresh post-repair baseline.**

On RTX A6000 Ampere, the accepted transaction retained 108 composites and 216
subworker receipts. Triangle scalar improved materially but remained adverse:
RTDL was 0.436590 ms, 2.910x pinned PyOptix and 4.689x Direct. The relation row
path was 12.774231 ms, 3.333x PyOptix and 9.950x Direct. These results motivated
more engineering; no parity claim was made.

Primary report:

- `history/internal_docs/goal5843_post_r1_fair_baseline_20260904/FINAL_TECHNICAL_REPORT.md`

**Goal5844: public triangle execution-envelope repair.**

The first immutable transaction failed its target: RTDL/PyOptix was
`2.1713906352x`. Profiling attributed the gap mainly to repeated public proof
serialization and static identity hashing rather than the native OptiX
operation. The successor caches only already validated immutable identities,
retains validation of all native stamp words, and preserves the strict route
for external providers, mappings, and non-scalar outputs.

On the same RTX 2000 Ada GPU, the clean successor measured:

| Arm/metric | Result |
|---|---:|
| RTDL public median | 132,534 ns |
| Pinned PyOptix median | 131,744 ns |
| Median within-block RTDL/PyOptix | 1.0456709697x |
| Worst block | 1.1543425588x |
| Direct native median | 82,592 ns |

This meets the internal exact-task parity target. It does not prove language
speedup; the compared RTDL and PyOptix paths ultimately execute identical
device program bytes, so the result mainly establishes that the public
envelope no longer dominates this scalar route.

Primary report:

- `history/internal_docs/goal5844_public_execution_parity_20260904/FINAL_ENGINEERING_REPORT.md`

**Goal5845: relation device compaction and public steady path.**

The generic repair added bounded-relation device compaction, compact traversal
audit, and exact immutable packed-row transport. On RTX 2000 Ada, eight
balanced blocks retained 1,024 samples per arm:

| Arm/metric | Result |
|---|---:|
| RTDL public median | 366,340 ns |
| Pinned PyOptix median | 3,486,126 ns |
| Median within-block RTDL/PyOptix | 0.1049444491x |
| Worst block | 0.1073019810x |
| RTDL public/direct-native ratio | 1.3291058851x |

The apparent reciprocal `9.53x` is not an intrinsic language or API speedup.
The pinned PyOptix arm emits 8,192 raw duplicate events and canonicalizes 4,096
rows on the host, while RTDL performs generic device semantic compaction. This
is an exact public-output implementation comparison against that pinned arm,
not a strongest-possible PyOptix lower bound.

Primary report:

- `history/internal_docs/goal5845_relation_public_parity_20260904/FINAL_ENGINEERING_REPORT.md`

**Goal5846: warm-cache fresh-process startup repair.**

The project added a content-addressed executable cache, one-shot verified
handoff, overlap of independent CPU admission and native initialization, and a
generic initialization ordering fix. On RTX 2000 Ada for the 4,096-by-4,096
relation task:

| Metric | RTDL | Pinned PyOptix | Ratio |
|---|---:|---:|---:|
| Median setup plus first | 577.153 ms | 580.880 ms | descriptive 0.994x |
| Median paired-block ratio | - | - | 0.990957x |
| Worst paired block | 620.265 ms | 547.771 ms | 1.132343x |
| Prepared steady median | 364.985 us | 3,487.496 us | 0.104655x |

This closes only the exact warm-cache startup target against a source-compiling
PyOptix contract. First-ever cache fill remained 36.982 s. A diagnostic
precompiled-PTX PyOptix sensitivity was roughly 236.415 ms, making then-current
RTDL approximately 2.44x slower under that changed deployment contract. That
adverse sensitivity motivated Goal5847.

Primary report:

- `history/internal_docs/goal5846_relation_startup_20260905/FINAL_ENGINEERING_REPORT.md`

**Goal5847: deployable AOT startup.**

The implementation added a family-bound minimal AOT native runtime without an
eager runtime-compiler dependency, overlap-safe provider initialization,
signed artifact binding, and immutable output reuse. On RTX 2000 Ada, both RTDL
and PyOptix consumed precompiled device programs:

| Metric | Result |
|---|---:|
| Median paired complete-process RTDL/PyOptix | 0.229370x |
| Worst complete-process block | 0.258728x |
| Pooled steady RTDL/PyOptix | 0.085635x |
| Median paired post-import RTDL/PyOptix | 2.504242x |
| Worst post-import block | 3.211853x |

The favorable complete-process result is dominated by the pinned
PyOptix/CuPy dependency import and must not be described as a language speedup.
The scientifically important adverse result is post-import: RTDL took 637.846
ms versus 263.349 ms for PyOptix. Goal5848 exists to close this debt against a
stronger baseline without relying on import latency.

Primary report:

- `history/internal_docs/goal5847_aot_startup_20260905/FINAL_ENGINEERING_REPORT.md`

### 4.8 Goal5848: current uncommitted strong-baseline closure

Goal5848 is implemented and locally audited, but formal GPU evidence is
`0/2`. Its current exact status is:

```text
IMPLEMENTED_AND_LOCALLY_AUDITED__FORMAL_GPU_EVIDENCE_0_OF_2
```

It freezes two tasks:

- a 4,096-by-4,096 bounded canonical relation with exactly 4,096 rows;
- a 16,384-query weighted triangle checked-U64 scalar equal to `65530`.

It defines five arms:

| Arm | Meaning |
|---|---|
| A | RTDL public AOT route. |
| B | Idiomatic pinned PyOptix route. |
| C | Strong PyOptix route with equivalent device continuation. |
| D | Direct CUDA/OptiX lower-bound route. |
| E | Exact pre-Goal5848 RTDL predecessor control. |

The intended transaction has eight balanced blocks, 80 fresh workers, 128
prepared samples per arm/task/block, no discarded adverse samples, and separate
baseline-competence, preflight, instrumentation, formal, and cross-generation
authorities.

The main frozen gates include:

- exact output and physical OptiX execution for every relevant arm;
- strong baseline competence `C/B <= 1.05x`;
- post-import `A/C <= 1.20x` median and `<= 1.35x` in every block;
- prepared public `A/D <= 1.20x`;
- successor/predecessor regression `<= 1.05x`;
- no runtime compiler on the RTDL deploy route;
- exact AOT cache reuse and no hidden production-cache mutation;
- fail-closed artifact, provider, output, and route recounts;
- replication on two distinct RTX generations without cross-machine raw-time
  ratios.

Local hostile review already found and repaired several experiment defects:

- the experiment no longer disables the production OptiX disk cache by
  default; cache disabling is experiment-scoped;
- formal execution requires both `CUDA_CACHE_DISABLE=1` and an explicit RTDL
  OptiX disk-cache policy;
- shared PTX/CUBIN provenance binds exact device artifacts;
- actual public outputs are independently checked rather than trusting only a
  worker-reported digest;
- independent physical-path checks cover RTDL compact traversal, absence of a
  runtime compiler, PyOptix device continuation, Direct launch/D2H lifecycle,
  and inner/outer sample equality;
- output roots inside a Git checkout are rejected;
- device provenance binds invocation, working directory, SDK headers, target,
  and hardware;
- transaction and cross-generation authorities are rebuilt independently and
  checked for byte identity.

A newer cold-path audit performed after the first local hostile-review text
found additional issues and repaired them locally:

- RTDL provider initialization and strong-PyOptix adapter setup did not close
  every acquired resource when artifact load, typed-input construction, or
  baseline load/prepare failed. The worker now has explicit failure-path
  cleanup and three focused tests passed before the next aggregate rerun.
- the independent transaction-authority builder originally validated only part
  of the frozen preregistration and accepted each process command merely as a
  list. The hardened builder now independently reconstructs the preregistration,
  exact 80 worker commands, worker source trees, and source/predecessor/PyOptix
  Git identities.
- formal process receipts now bind working directory, module path, visible
  device, cache policy and Python isolation; hidden CUDA JIT/injection, CuPy or
  Numba cache, Python injection and BLAS-thread controls must be absent and are
  recorded as such; mismatches fail before worker zero.
- formal validators no longer rely on optimization-sensitive assertions, and
  strict JSON decoding rejects duplicate keys and non-finite constants at both
  experiment-authority and production exact-AOT cache boundaries.
- the timer-free RTDL preflight now uses the formal worker's same fail-closed
  admission and cleanup ownership rather than leaving pre-bind failures to
  process teardown.
- exact-AOT publication now hardens payload containment before rename and
  atomically rolls an entry back out of the public cache namespace if final
  root hardening fails; tests also prove that every bound request field changes
  the cache identity.

Claude must inspect these latest changes and report whether they fully close
resource-ownership and coherent-resealing/substituted-command attacks. Until
GPU execution, describe them only as locally verified implementation: focused
tests pass `96/96` in ordinary and optimized Python, adjacent Goal5844--5848
tests pass `230/230`, but formal evidence remains `0/2`.

The Goal5848 files are currently working-tree changes, not a clean committed
evidence transaction. Review the architecture and implementation only. Do not
infer a performance result, gate pass, cross-generation result, or paper claim.

Primary current documents:

- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md`
- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/LOCAL_HOSTILE_SELF_REVIEW.md`
- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/GPU_RUNBOOK.md`

## 5. Status ledger: positive, adverse, and unavailable evidence

| Area | Best current evidence | Required interpretation |
|---|---|---|
| Public leaf-kind breadth | Custom, triangle, built-in sphere, and tested round-linear curve routes exist. | Kind presence only; not complete 4/4 support. |
| Collision semantics | Bounded swept-sphere/edge mapping and app-neutral owner-grouped Boolean route. | Not full RT-CCD and not a Paper App. |
| Prospective generality | One independently selected sphere/count/continue topology passed with frozen generic-core bytes unchanged. | One bounded success, not arbitrary Callback IR. |
| Target refinement | Three route groups, four modes, five properties, 20/20 checks, mutation rejection. | Bounded structural evidence, not a soundness theorem. |
| Real-artifact prevalence | Goal5820 ended at `0 ENFORCED / 4 NOT_FOUND / 16 UNCERTAIN`; Goal5839 froze and ran discovery but has zero property classifications. | Neither is paper-ready; no defect prevalence claim. |
| External human authoring | 0 authors, 0 studies. | No ease-of-use/productivity claim. |
| Initial fair performance | Goal5842/5843 exposed severe relation and triangle deficits. | Mandatory adverse evidence; not intrinsic language lower bounds. |
| Triangle steady repair | Goal5844 reached 1.046x median against pinned PyOptix on one exact Ada task. | Internal exact-task parity only. |
| Relation steady repair | Goal5845 reached 0.105x against a host-continuation PyOptix arm. | Not strongest-baseline or 9.53x language claim. |
| Warm-cache startup | Goal5846 reached 0.991x against source-compiling PyOptix. | Contract-specific parity; precompiled sensitivity remained adverse. |
| AOT complete process | Goal5847 reached 0.229x against pinned PyOptix. | Dominated by CuPy import; not useful as a language-speed claim. |
| AOT post-import | Goal5847 measured 2.504x adverse. | Real open performance debt. |
| Strong-baseline closure | Goal5848 local implementation and hostile audit only; GPU evidence is `0/2`. | No performance result or manuscript claim yet. |

### 5.1 Author-side provisional assessment

This assessment is intentionally exposed so the reviewer can attack it rather
than infer an unstated favorable interpretation.

| Prior attack | Author-side current assessment |
|---|---|
| Generality was zero | Partially addressed, not closed broadly. Goal5838 changes the evidence from zero prospective examples to one bounded frozen-core success. It does not establish arbitrary Callback IR. |
| Only hand-built fixed families existed | Partially addressed. A schema-driven lifecycle and selected-topology instantiation now exist, but the reviewer must determine whether too much family-specific work remains outside the frozen core. |
| Real problem prevalence was unproven | Not closed. Goal5839 improved the protocol and discovery custody but produced no classified census. |
| No external developer used the system | Not closed and not expected to close before submission. All ease/productivity claims must be removed. |
| Application logic could pollute the engine | Addressed by design for the reviewed sphere/curve/owner-grouped paths, but requires source audit. Collision semantics are intended to remain in the case study. |
| Lowering correctness was asserted by the same implementation | Partially addressed by Goal5840's separate checker and mutation suite, but only for a bounded denominator. |
| Performance overhead was unexplained | Substantially addressed causally by Goals5842-5847. The resulting claims remain task- and endpoint-specific. |
| PyOptix comparison could be weak | Not yet closed. Goal5845's host-continuation arm is explicitly weak; Goal5848's Arm C is intended to provide the stronger device-continuation comparator. |
| Favorable results might hide failures | Addressed procedurally by preserving Goal5842/5843 deficits, Goal5844's first failed transaction, Goal5846's AOT sensitivity, Goal5847's adverse post-import result, and Goal5848's no-discard rule. Reviewer must verify that custody is real. |

The current CGO manuscript predates much of this work and must not be treated
as synchronized with the evidence summarized here. A favorable review of the
technical progress would still require a fresh claim-limited manuscript,
related-work update, evaluation rewrite, artifact map, anonymity scan, and
page-limit gate. This CFR requests a scientific and implementation review, not
approval of current submission bytes.

## 6. Required architecture and generality review

Please answer every question below.

1. Is the protocol-shape algebra a meaningful compiler abstraction, or merely
   a descriptive schema layered over concrete-family implementations?
2. Is the Goal5838 frozen core large enough to contain the scientifically
   important generic mechanism, or was it defined narrowly enough that the
   post-selection extension could hide topology-specific compiler work?
3. Audit the selected Goal5838 extension. Does it instantiate an already
   generic schema/lifecycle/lowering contract, or does it effectively implement
   a third special case outside the frozen core?
4. Is the NIST-pulse challenge selection and ten-row table credible protection
   against cherry-picking? If not, identify the exact remaining selection
   channel.
5. Does package-external provider construction represent a real extension
   boundary, or can it still access enough internal structure to invalidate the
   generalization claim?
6. What is the strongest exact generality sentence supported by Goal5838?
7. Does Goal5840 independently test a meaningful refinement relation, or does
   its checker share enough assumptions with the implementation to be circular?
8. Are the five Goal5840 properties sufficient for the claimed bounded
   refinement result? Name missing properties that must be checked.
9. Do Goals5838 and 5840 together support a bounded callback-protocol compiler
   contribution, or only a protocol checker plus selected lowering templates?
10. Is the absence of an external human author fatal for CGO, a paper
    limitation, or a reason to remove ease/productivity language only?

## 7. Required sphere, curve, and collision review

1. Confirm whether sphere and curve support use true OptiX built-in geometry
   and contain no hidden user intersection program.
2. Determine whether application semantics leaked into `src/rtdsl/**` or
   `src/native/**`. Search specifically for robot, collision, trajectory,
   swept-sphere, RT-CCD, Sui-specific orientation, and paper-specific IDs.
3. Assess whether the near-parallel curve-domain exclusion is principled,
   sufficiently visible, and enforced at all public entry points.
4. Determine whether `OWNER_GROUPED_ANY_HIT / BOOL_OR` is genuinely generic and
   reusable outside collision detection.
5. Verify that collision geometry construction, predicate interpretation, and
   oracle logic remain application-owned.
6. Decide whether Goal5835 is fairly described as a bounded case study rather
   than an executed Paper App.
7. Confirm that Goal5836's terminal source-fidelity result logically forbids
   same-input performance comparison and Paper App promotion.
8. Identify any path by which the current prose still invites a reader to
   mistake Goal5835/5837 for full Sui et al. reproduction.
9. State what additional work, if any, is scientifically necessary for the
   collision case study to support the compiler paper. Do not require full
   paper reproduction unless it changes the compiler argument.

## 8. Required performance and baseline-fairness review

The performance sequence intentionally preserves poor results and follows them
with new, separately frozen successor experiments. Judge whether this is valid
engineering closure or post-hoc baseline shopping.

1. Reconstruct the causal chain from Goal5842 through Goal5848. Did each repair
   address a measured generic cost, or did any repair add task-specific native
   code or special-case a benchmark?
2. Audit Goal5844's triangle fast path. Does it preserve all public correctness,
   status, proof, and traversal obligations while caching only immutable facts?
3. Audit Goal5845's relation compaction. Is it a generic semantic continuation
   available to any bounded relation, or a disguised application kernel?
4. Is Goal5844's approximately 1.046x median a fair public-envelope parity
   statement despite identical device program bytes?
5. Is Goal5845's approximately 9.53x reciprocal useful evidence at all given
   that its PyOptix arm performs host duplicate canonicalization? If included,
   what exact wording and placement prevents overclaim?
6. Does Goal5846 fairly compare warm-cache RTDL against source-compiling
   PyOptix, or should this be presented only as an engineering milestone?
7. Does Goal5847's complete-process result have scientific value after the
   CuPy import confound is disclosed, or should the paper report only the
   adverse post-import endpoint?
8. Did Goals5844-5847 violate the earlier warning against arm-specific
   optimization? The project position is that they repaired RTDL's generic
   public implementation after adverse measurement while retaining every old
   transaction. Confirm or reject that reasoning.
9. Are Arms B and C in Goal5848 sufficiently distinct? B is intended to show
   idiomatic pinned PyOptix; C must demonstrate baseline competence with
   equivalent device continuation. Identify any unfair work placement.
10. Is Direct Arm D a meaningful lower bound with matching output semantics,
    validation, launch counts, setup boundaries, and D2H obligations?
11. Is predecessor Arm E sufficient to prove Goal5848 did not gain post-import
    parity by regressing the previously fast prepared path?
12. Are the Goal5848 hard thresholds scientifically defensible: `A/C <=1.20x`
    median, every block `<=1.35x`, `A/D <=1.20x`, `C/B <=1.05x`, and
    successor/predecessor `<=1.05x`?
13. Does disabling CUDA and RTDL OptiX disk caches for the formal transaction
    improve fairness, or create an unrepresentative deployment claim?
14. Are eight balanced blocks and 128 prepared samples per arm/task/block
    sufficient? Require confidence intervals or additional repetitions only if
    they answer a concrete threat.
15. Does the two-generation design establish portability of the conclusion,
    given that raw times are not pooled or divided across machines?
16. What performance sentence, if any, could be used after Goal5848 passes and
    receives external review? State the exact task, endpoint, hardware scope,
    and comparator qualifications.

## 9. Required evidence-integrity and security review

1. Verify that every reported formal result is tied to an exact source commit,
   tree, task, output contract, device identity, toolchain, native DSO, and
   immutable authority.
2. Confirm that failed and superseded transactions remain visible and are not
   pooled into successor results.
3. Check whether any verifier imports the implementation or GPU package it is
   supposed to verify independently.
4. Inspect mutation suites for coordinated resealing, path substitution,
   duplicate-key JSON, non-finite values, artifact append, wrong-family bind,
   output substitution, route substitution, and timing-summary mutation.
5. Determine whether the Goal5838 frozen-core file set and Goal5840 target
   checker are hash-bound at the right points.
6. Inspect whether AOT manifests bind the executable, family, ABI, provider,
   target, toolchain, device artifact, and native library without trusting file
   names.
7. Confirm that Goal5848 production cache policy is unchanged unless the
   experiment explicitly selects a disabled-cache mode.
8. Verify that Goal5848's independent authority consumes raw worker evidence,
   independently computes outputs, ratios, gates, and traversal facts, and does
   not trust controller summaries.
9. Verify that the authority independently reconstructs every frozen
   preregistration field and exact worker command, binds source/predecessor/
   PyOptix Git trees, and rejects a coherently resealed command substitution.
10. Audit failure-path ownership for provider initialization, artifact-load,
    typed-input, strong-baseline load/prepare, execution, and close failures.
    Cleanup must not hide the original exception or leak an acquired resource.
11. Identify any stale current-tree custody test that is being incorrectly used
   as evidence. Known historical replay limitations must remain disclosed.
12. Search for evidence files generated inside the Git checkout that could
    perturb source identity or silently become experiment inputs.

## 10. Required manuscript and claim review

Please classify each statement as `SUPPORTED`, `SUPPORTED_WITH_REWRITE`,
`NOT_YET_SUPPORTED`, or `FORBIDDEN`:

1. "RTDL makes the complete callback protocol the compilation unit."
2. "RTDL enforces cross-role callback invariants before GPU execution."
3. "RTDL is a generic callback-protocol compiler."
4. "RTDL executes arbitrary restricted-Python callbacks on RT cores."
5. "A schema-driven frozen core admitted one independently selected unseen
   topology without modification."
6. "RTDL supports all OptiX primitive types."
7. "RTDL instantiates all four pinned OptiX leaf-primitive kinds in bounded
   public routes."
8. "RTDL reproduces Sui et al. RT-CCD."
9. "A bounded collision-detection case study consumes an app-neutral
   owner-grouped any-hit Boolean primitive."
10. "Independent developers can use RTDL more easily than PyOptix."
11. "RTDL has negligible runtime overhead."
12. "RTDL is 9.53x faster than PyOptix."
13. "On one exact scalar route, the repaired public envelope was within the
    preregistered parity bound of pinned PyOptix."
14. "On one exact row-returning route, generic RTDL device compaction was much
    faster than a pinned host-continuation PyOptix implementation."
15. "Goal5848 closes strong-baseline and post-import performance."
16. "The real-artifact census shows protocol bugs are prevalent."
17. "RTDL's target lowering is formally proven sound."
18. "A separately implemented checker found bounded structural refinement for
    three route groups, four modes, and five properties."

The current author-side claim ceiling is:

### Candidate claims, subject to this review

- The complete cross-role callback protocol is an appropriate compilation and
  verification unit for RT-repurposed programs.
- RTDL implements a bounded typed Callback-Protocol IR and public lifecycle.
- Public routes cover bounded custom, triangle, built-in sphere, and
  round-linear-curve cases; coverage is described by exact route and kind, not
  as universal geometry support.
- One independently selected prospective topology passed without changing the
  three-file frozen generic core.
- A separately implemented checker provides bounded structural refinement
  evidence over the exact declared route/mode/property denominator.
- A bounded collision-detection case study consumes a generic app-neutral
  owner-grouped Boolean any-hit behavior.
- Performance overhead can be diagnosed and substantially reduced without
  weakening the public correctness boundary, for the exact measured tasks.

### Forbidden or not-yet-supported claims

- Arbitrary Callback IR GPU execution.
- Universal provider portability or a general compiler-soundness theorem.
- Complete sphere, curve, geometry, topology, or application coverage.
- Full Sui et al. RT-CCD reproduction or Paper App status.
- Third-party ease of use, productivity, or usability improvement.
- Real-world defect prevalence from the `0/4/16` census.
- Intrinsic `9.53x` language/API speedup.
- Universal zero/negligible overhead or universal Direct parity.
- Any Goal5848 result before two formal GPU transactions, independent recount,
  external review, and explicit claim authorization.

## 11. Specific regression and design-smell search

Please search the current source, not only the reports, for:

- collision/application terms or formulas inside generic engine/runtime code;
- copied family-specific lifecycle code that should be generated from the
  schema;
- protocol validation duplicated inconsistently across Python and native
  boundaries;
- fixed constructor dispatch hidden behind generic names;
- output-specific caches that can return a stale result for changed inputs;
- proof or identity caches that survive mutable provider/source changes;
- RTDL-only work outside timed endpoints;
- baseline-only validation or continuation outside timed endpoints;
- host/device synchronization asymmetry;
- hidden compilation, disk-cache, context, or import state;
- task-specific device kernels in the AOT runtime;
- incomplete destroy/close/fork/failure ownership;
- evidence authorities that trust self-reported summaries;
- current prose that upgrades kind presence, bounded instantiation, or one
  prospective success into universal support.

If a finding is architectural rather than a local bug, say so explicitly and
name the smallest credible repair.

## 12. File review map

### Prior review and paper strategy

- `AGENTS.md`
- `README.md`
- `paper/cgo2027/main.tex`
- `history/internal_docs/reviewer_guidance_path_to_strong_accept_20260829.md`
- `history/internal_docs/reviewer_guidance_twelve_day_submission_plan_20260829.md`
- `history/internal_docs/review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md`

### Sphere, curve, collision, and generic behavior

- `src/rtdsl/v4_sphere.py`
- `src/rtdsl/v4_curve.py`
- `src/rtdsl/v4_curve_owner_grouped_any_hit_public.py`
- `src/rtdsl/v4_curve_owner_grouped_any_hit_optix_compiler.py`
- `src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py`
- `case_studies/sui_derived_edge_crossing_core/`
- `history/internal_docs/goal5833_builtin_sphere_first_contact_technical_report_20260830.md`
- `history/internal_docs/goal5834_builtin_round_linear_curve_technical_report_20260830.md`
- `history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_technical_report_20260830.md`
- `history/internal_docs/goal5836_a1_source_fidelity_technical_report_20260901.md`
- `history/internal_docs/goal5837_owner_grouped_classification_20260902/TECHNICAL_REPORT.md`

If any listed module path has since moved, locate the current root-exported
implementation and record the path mismatch as documentation debt rather than
silently skipping review.

### Generic schema/compiler and prospective exam

- `src/rtdsl/v4_family_schema.py`
- `src/rtdsl/v4_generic_family_lifecycle.py`
- `src/rtdsl/v4_family.py`
- `history/internal_docs/goal5838_generic_core_exam_20260902/`
- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/`

### Performance implementation and authorities

- `src/rtdsl/v4_generic_family_lifecycle.py`
- `src/rtdsl/v4_rtdlexe.py`
- `src/rtdsl/v4_aot_cache.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `history/internal_docs/goal5842_causal_admission_cost_20260903/`
- `history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903/`
- `history/internal_docs/goal5843_post_r1_fair_baseline_20260904/`
- `history/internal_docs/goal5844_public_execution_parity_20260904/`
- `history/internal_docs/goal5845_relation_public_parity_20260904/`
- `history/internal_docs/goal5846_relation_startup_20260905/`
- `history/internal_docs/goal5847_aot_startup_20260905/`

### Goal5848 work in progress

- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md`
- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/LOCAL_HOSTILE_SELF_REVIEW.md`
- `history/internal_docs/goal5848_strong_baseline_post_import_20260905/GPU_RUNBOOK.md`
- `experiments/goal5848_strong_baseline/`
- `scripts/goal5848_*.py`
- `scripts/goal5848_pod_prepare_and_run.sh`
- `tests/goal5848_*_test.py`

Pay particular attention to the latest uncommitted files:

- `experiments/goal5848_strong_baseline/worker.py`
- `scripts/goal5848_build_transaction_authority.py`
- `tests/goal5848_transaction_authority_test.py`
- `tests/goal5848_worker_failure_cleanup_test.py`

## 13. Required prior-finding closure table

Start the review with this table and fill every row:

| Prior attack | Current disposition | Evidence that closes or fails to close it | Remaining blocker | Severity |
|---|---|---|---|---|
| Only two closed protocol families; generality zero | | | | |
| No prospective frozen-core exam | | | | |
| No real-world protocol-defect prevalence evidence | | | | |
| No external human author | | | | |
| Native OptiX/OWL/PyOptix boundary unclear | | | | |
| No causal admission-cost analysis | | | | |
| Weak/asymmetric performance baseline | | | | |
| Application-specific logic may leak into engine | | | | |
| No independent lowering/refinement evidence | | | | |
| Adverse results could be hidden by successor optimization | | | | |

## 14. Required reviewer output

Return one self-contained Markdown report with these sections:

1. **Cold-start understanding**, restating the problem, contribution, non-goals,
   strongest current evidence, and largest open threat without copying the
   project wording.
2. **Prior-finding closure table** using Section 13.
3. **Executive verdict** in no more than ten sentences.
4. **P0/P1/P2/P3 findings**, with exact file and line references.
5. **Architecture/generalization verdict**.
6. **Sphere/curve/collision verdict**.
7. **Goal5838 prospective-exam verdict**.
8. **Goal5840 refinement-evidence verdict**.
9. **Performance and baseline-fairness verdict**.
10. **Goal5848 design-readiness verdict**, explicitly not a completion verdict
    and explicitly accounting for the latest authority-hardening WIP.
11. **Claim-by-claim classification** for all 18 statements in Section 10.
12. **Required manuscript edits and evidence cuts**.
13. **Smallest credible repair plan**, ordered by submission value rather than
    engineering convenience.
14. **Deadline-aware action matrix** using the columns and five-action limit in
    Section 0.9.
15. **Final verdicts** using the exact choices below.

Save the returned report as:

`history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md`

For each of the following areas choose exactly one:

- `ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS`
- `ACCEPT_WITH_BLOCKING_FIXES`
- `REJECT_CURRENT_CGO_CONTRIBUTION`

Areas:

- A. Architecture and bounded generalization.
- B. Sphere/curve/collision architecture boundary.
- C. Independent lowering/refinement evidence.
- D. Committed performance evidence through Goal5847.
- E. Goal5848 experiment design and implementation readiness.
- F. Current CGO submission readiness.

Finish with one overall recommendation selected from:

- `PROCEED_TO_CGO_PAPER_WITH_EXACT_SCOPED_CLAIMS`
- `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`
- `DO_NOT_SUBMIT_THIS_CONTRIBUTION_IN_CURRENT_FORM`

## 15. Review discipline

- Do not infer correctness from test count alone.
- Do not infer generality from the number of examples or leaf kinds.
- Do not infer performance from a fast native kernel if the public path is
  slow.
- Do not reward evidence infrastructure unless it blocks a concrete threat.
- Do not treat preserved failures as successes, but do credit them when they
  prevent result selection or overclaim.
- Do not require implementation of every feature in the cited collision paper
  unless that feature is necessary for the compiler claim.
- Do not let the absence of Goal5841 human evidence be replaced by agent logs.
- Do not authorize any Goal5848 performance sentence from local design work.
- Prefer exact bounded statements over broad adjectives such as generic,
  universal, negligible, easy, complete, or production-ready.

The purpose of this review is to determine whether the post-2026-08-29 work
created a defensible compiler contribution and what exact evidence remains
necessary before submission. It is not to validate the project's ambition or
the amount of work performed.
