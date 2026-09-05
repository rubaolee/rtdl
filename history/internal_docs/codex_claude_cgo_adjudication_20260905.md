# Codex adjudication of the 2026-09-05 Claude review

Date: 2026-09-05

Target: CGO 2027 submission due 2026-09-10

Status: `INTERNAL_ADJUDICATION_COMPLETE__REPAIRS_AND_POST_REPAIR_EXTERNAL_REVIEW_PENDING`

## 1. Purpose

This document audits both:

1. Claude's independent review in
   `history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md`;
   and
2. Codex's first response to that review.

It does not treat an external review as automatically correct, and it does not
claim final Codex-Claude consensus where the two analyses differ. It separates
source-supported findings, severity disagreements, factual corrections, and
the exact claim set that can support a defensible CGO submission.

## 2. Review custody and limits

Claude reviewed committed history through Goal5847 and a dirty Goal5848 working
tree at HEAD `5de0e7ec3a48af73b2e645a5ff0edaae9b8c6696`. Claude recorded the then-current
tracked diff digest as
`52f185f3d92fffdc792014add5344f593b79fbdd52589a3650a96766350de424` and ran
tests under workspace Python 3.10.12 because the pinned Python 3.12 environment
was not exposed to that reviewer.

The Goal5848 working tree changed after that review. The subsequent changes
include the local repairs listed in Section 12. This document deliberately does
not embed a transient digest of the diff that contains itself: adding the
adjudication to the commit would invalidate such a value. The post-repair bytes
must instead be identified by the clean Goal5849 Git commit/tree and by each
formal pod transaction's preregistration.
The subsequent changes include stricter exact-AOT publication, strict JSON
parsing, fail-closed cleanup, removal of production assertions from
`v4_rtdlexe.py`, and additional tests. Therefore Claude's Goal5848 readiness
verdict applies to the reviewed architecture and earlier bytes, not to every
current WIP byte.

The current pinned environment was used for this adjudication:

```text
/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python
PYTHONPATH=src:.
```

Current checks observed during adjudication:

- Goal5848 focused tests after the instrumentation-symmetry repair:
  `98/98 PASS` in ordinary Python and under `python -O`;
- Goal5838 current-tree seal test: `8 PASS, 1 ERROR`, with expected successor
  drift first reported at `src/rtdsl/v4_family_schema.py`;
- Goal5832 current-tree algebra/custody test: `22 PASS, 1 ERROR`, with drift at
  `goal5831.source_authorities[1]`;
- formal Goal5848 GPU evidence: `0/2` generations.

No performance result, public claim, or final consensus is created by this
document.

## 3. Executive adjudication

Claude's overall submission warning is correct: the current manuscript is not
ready, Goal5848 has no formal GPU transaction, historical/current custody must
be explained, and claims must be narrower than arbitrary callback-topology
compilation or usability superiority.

Claude's central scientific diagnosis is also substantially correct: RTDL's
strongest contribution is making the complete host/device callback protocol the
unit of compilation and admission, not automatic discovery or generic lowering
of arbitrary OptiX protocols.

Three parts of Claude's review require correction:

1. Goal5838 was preregistered to freeze schema admission, canonical planning,
   provider binding, identity, and lifecycle while explicitly allowing
   provider- and topology-specific implementation after selection. The 2,635
   post-selection lines limit the result but do not invalidate or mislabel the
   preregistered experiment. They show that lowering remains topology-specific.
2. The suspected duplicate challenge row is not duplicate. The pre-Goal5838
   round-linear-curve Boolean route used `closest_hit`; the challenge row uses
   `any_hit` with `terminate`. Under the frozen exact-role/effect/result
   exclusion rule, the denominator remains ten.
3. Goal5845's explanation is imprecise, but the source does not prove that the
   9.53x exact-arm ratio is unexplained. RTDL transfers device-deduplicated rows
   and performs final packed-row canonicalization in native C++; the weak
   PyOptix arm transfers raw duplicates, materializes Python objects, and runs
   Python `sorted(set(...))`. The result remains an exact measurement of those
   arms. It is not an intrinsic RTDL advantage and should not be a paper-facing
   speedup claim.

Accordingly, Codex and Claude agree on the submission thesis and most repair
work, but do not agree with Claude's severity and wording for P0-1, P0-2, and
P0-3. Final external consensus requires a post-repair re-review; it cannot be
declared from this adjudication alone.

## 4. Finding-by-finding decision

| Claude finding | Codex decision | Corrected severity | Submission action |
|---|---|---|---|
| P0-1: sealed generic core performs no lowering | `ACCEPT_OBSERVATION__CORRECT_CONCLUSION` | P0 only if the paper calls the sealed core a generic lowering engine; otherwise P1 terminology/scope | State that RTDL is a bounded whole-protocol compiler with a schema-parametric admission/identity/lifecycle framework and topology-specific trusted lowerers |
| P0-2: challenge domain is author-defined and narrow | `ACCEPT_LIMITATION__REJECT_EXPERIMENT_INVALIDATION` | P1 claim scope | State the exact 4-by-3 construction, exclusions, ten-row denominator, and that the selected row is a previously unimplemented combination of supported components |
| P0-2 denominator may be nine because curve Boolean existed | `REJECT_FACTUALLY` | none | Record that the old curve route was `closest_hit`, while the candidate was `any_hit + terminate`; retain denominator ten |
| P0-3: Goal5845 says device versus host canonicalization although RTDL also host-sorts/uniques | `ACCEPT_WORDING_DEFECT` | P1 internally; P0 only if 9.53x is promoted as an intrinsic/public language speedup | Correct the mechanism, retain the exact internal arm result, and use Goal5848 Arm C for the paper comparison |
| P0-3: 2x D2H cannot explain 9.53x | `REJECT_UNSUPPORTED_CAUSAL_INFERENCE` | none | Do not infer a bound from row count alone; Python object materialization and `set/sort` differ materially from native packed-row work |
| No real-world defect-prevalence evidence | `ACCEPT` | P1 claim removal | Remove empirical prevalence wording; motivate with constructed cross-role defect classes |
| No external human author | `ACCEPT` | P1 claim removal | Make no ease, productivity, usability, or learnability claim |
| P1-1: current-tree Goal5838 and Goal5832 custody tests fail | `ACCEPT_WITH_HISTORICAL_SCOPE_CORRECTION` | P1 artifact readiness | Locally repaired by the current-versus-historical replay guide; preserve old authorities and never reseal old evidence |
| P1-2: near-parallel exclusion is not enforced on Boolean/owner-grouped route | `ACCEPT_AS_DOMAIN_ENFORCEMENT_GAP` | P1 | Locally repaired by explicitly limiting the case study to by-construction fixtures; do not claim general closed-capsule correctness |
| P1-3: native DSOs/raw capsule are outside Git | `ACCEPT` | P1 artifact replay | Ship exact bytes in the artifact or clearly distinguish historical digest verification from source rebuild/functional replay |
| P1-4: manuscript is stale | `ACCEPT_FULLY` | P0 submission blocker | Rewrite abstract, contributions, design scope, evidence, evaluation, limitations, and artifact sections |
| P2-1: provider identity is load-time identity | `ACCEPT_AS_CLAIM_SCOPE` | P2 | State that the receipt binds the loaded provider image identity; do not imply per-call filesystem rehashing |
| P2-2: application-vocabulary blacklist exists on only one generator | `ACCEPT_AS_WEAK_HYGIENE_CHECK` | P3, not architectural proof | Generalize only if low risk; rely on structural ownership and source audit rather than a keyword blacklist for the main claim |
| P2-3: legacy app vocabulary exists under `src/rtdsl` | `ACCEPT_AS_ARTIFACT_PARTITION_ISSUE` | P2 | Partition V4 compiler/runtime from retained v1/v2 modules in the artifact README |
| P2-4: README contains dead links | `ACCEPT` | P1 artifact usability | Locally repaired; the root README now has no missing local link targets |
| Companion claim that packaging metadata is absent | `REJECT_FACTUALLY` | none | `pyproject.toml` exists and declares setuptools editable-build metadata; document build-isolation/offline prerequisites accurately |
| P3-1: Goal5848 phase instrumentation is asymmetric | `ACCEPT` | P1 before formal timing | Locally repaired and hostile-tested: RTDL and both PyOptix paths now use one explicit instrumentation policy |
| P3-2: rented pod endpoints appear in sealed authorities | `ACCEPT` | P3 packaging | Scrub only in a derived public-artifact view; do not mutate sealed authorities |
| Goal5840 independent checker is non-circular and bounded | `ACCEPT_FULLY` | closed at stated scope | Keep prominent, with exact three-route/four-mode/five-property denominator and no theorem claim |
| Goal5848 design is strong but evidence is 0/2 | `ACCEPT_FULLY` | P0 for the intended performance section | Finish current-byte self-review, commit/freeze, then run the exact experiment on two RTX generations before any result sentence |

## 5. Detailed resolution of the three disputed P0 findings

### 5.1 Goal5838 proves bounded framework extension, not generic lowering

The preregistered scientific question is explicit:

> Can one schema-driven admission, compilation-plan, provider-binding, and
> public-lifecycle core be frozen before selection, then execute an independently
> selected topology without changing a frozen-core byte?

The preregistration also explicitly permits unlimited post-selection work in:

- the selected protocol instance and restricted Callback IR;
- package-external or provider-specific implementation modules;
- app-owned input/oracle code;
- tests, runners, evidence, and build repair.

Therefore the post-selection implementation size is a disclosed cost and an
important limitation, not a violation of the registered experiment. Claude is
right that `lower_canonical_compilation_plan` produces a target-neutral,
non-executable canonical plan and that executable code generation resides in
trusted topology-specific modules. Claude is wrong to use this fact to reduce
RTDL as a whole to a non-compiler.

RTDL still has a real restricted-Python frontend, typed Callback IR,
verification, compiler-owned wrapper generation, PTX construction, and
materialization for its supported templates. The accurate classification is:

> RTDL is a bounded whole-protocol compiler. Its whole-protocol admission,
> identity, provider-binding, and lifecycle framework is schema-parametric;
> executable lowering is implemented by compiler-owned, topology-specific
> trusted templates rather than a topology-generic lowering algorithm.

This is publishable if the paper treats topology-specific lowering as a bounded
implementation and TCB limitation rather than hiding it.

### 5.2 Goal5838's table is narrow, but its ten-row denominator is valid

Claude correctly identifies the remaining selection channel: the authors chose
the challenge domain. NIST selection prevents choosing a convenient row after
the frozen table exists; it does not make the domain representative of all
OptiX protocols.

The exact evidence is therefore a prospective composition test over an
author-defined domain, not a random sample from an open protocol universe.
Every primitive kind had prior provider-path support, and every topology was an
any-hit per-query Boolean/U64 variant. Custom-primitive candidates add their
required `bounds` and `intersection` roles, but the result/continuation domain
is still narrow.

The denominator concern at Claude lines 315-319 does not survive source
inspection. At the Goal5838 baseline commit
`0f5c9d4297f73e412732e5a8ab133423fe4cfd21`,
`CURVE_ANY_CONTACT_BOOLEAN_SOURCE` declares roles `make_ray`, `closest_hit`,
`miss`, and `finalize`. The challenge row
`builtin_round_linear_curve::any_hit_terminate_bool_per_query` declares
`make_ray`, `any_hit(terminate)`, `miss`, and `finalize`. Because the frozen
exclusion rule removes only exact role/effect/result topologies, the row was
correctly eligible.

The safe Goal5838 sentence is:

> At commit `7da68056550818d8e2f6cdb4d7aa3e9029cc4524`, a NIST beacon selected one
> previously unimplemented primitive/topology combination from a frozen ten-row
> author-defined table crossing four already supported primitive kinds with
> three bounded any-hit continuation/result variants. RTDL realized and
> executed that combination through its public lifecycle, matched twelve
> independent oracle rows in two true OptiX launches, and changed zero bytes in
> the previously sealed admission/identity/lifecycle framework. Realization
> required 2,635 lines of topology-specific compiler/runtime code outside the
> seal. This is bounded prospective compositional-extension evidence, not
> arbitrary Callback IR or topology-generic lowering evidence.

### 5.3 Goal5845's arm measurement is valid; its broad causal wording is not

The native RTDL fast path:

1. obtains `unique_count_u32` after device-side semantic deduplication;
2. copies only `unique_rows` to a persistent host buffer; and
3. performs final `std::sort` and `std::unique` over packed native rows.

The pinned PyOptix compatible arm:

1. copies the raw hit counter and all raw relation rows to NumPy;
2. converts the array to Python lists and tuples; and
3. computes `sorted(set(...))` in Python.

Thus the report's phrase "semantic sort/unique compaction before transfer" is
too broad: device-side deduplication precedes transfer, while final canonical
ordering/uniquing remains on the RTDL native host path. Claude correctly caught
that wording defect.

Claude's further claim that a roughly 2x row-count difference cannot explain a
9.53x endpoint difference is not established. The arms differ in language
runtime, object materialization, allocation, conversion, and canonicalization,
not only transfer size. No phase experiment isolated their causal shares.

The exact ratio may remain in immutable internal history as a property of the
named weak arm. It must not be presented as RTDL's intrinsic speedup over
PyOptix. The paper-facing repair is Goal5848 Arm C, which equips PyOptix with
equivalent device continuation and tests baseline competence before comparing
RTDL.

## 6. Audit of Codex's first response

Codex's first response correctly accepted these points:

- the manuscript is stale and must be rewritten;
- arbitrary/generic callback-topology lowering is unsupported;
- Goal5840 is the strongest independent refinement artifact;
- current-tree custody failures require explicit artifact documentation;
- collision near-parallel semantics need a guard or an exact scope statement;
- Goal5848 is the right strong-baseline repair and remains `0/2`;
- ease-of-use and real-world prevalence claims must be removed without evidence.

It was too deferential in three places:

1. It did not state clearly enough that Goal5838 achieved exactly its
   preregistered bounded framework-extension objective. The correct criticism
   is about how far that evidence generalizes, not whether the experiment
   succeeded.
2. It repeated Claude's implication that the Goal5845 ratio is causally
   inexplicable from the source. The source only proves the prior explanation
   incomplete; it does not bound Python materialization/canonicalization cost.
3. It did not immediately dispose of Claude's curve-Boolean denominator
   suspicion by comparing the old `closest_hit` role topology with the candidate
   `any_hit + terminate` topology.

Codex also should have distinguished four different states more sharply:

- historical authority valid at its bound commit;
- current-tree replay test intentionally stale after legitimate successors;
- artifact self-containment incomplete because some binary bytes are absent;
- current Goal5848 WIP not covered byte-for-byte by Claude's earlier review.

This document corrects those omissions.

## 7. Jointly defensible CGO thesis

The submission should make one central claim:

> In RT-core programming, correctness obligations cross callback roles, host
> bindings, continuation/status rules, and the exact executable. RTDL makes this
> complete protocol, rather than an isolated Python callback or CUDA function,
> the unit of compilation and admission. For a bounded set of OptiX protocol
> templates, RTDL compiles restricted Python leaves, checks five cross-role
> obligations before execution, binds the admitted protocol to physical and
> executable identity, and publishes output only through a fail-closed
> lifecycle.

The paper can then support the thesis with four evidence classes:

1. Executed mutations showing that CP001-CP005 reject cross-role defects before
   result publication.
2. Goal5838's bounded prospective compositional extension with the exact
   ten-row author-defined denominator and 2,635-line trusted-lowering cost.
3. Goal5840's independent, RTDL-free structural/partial-evaluation checker over
   exactly three routes, four modes, and five properties.
4. Same-contract performance against idiomatic PyOptix, strong device-
   continuation PyOptix, and Direct OptiX, but only if Goal5848's frozen gates
   pass on both required RTX generations.

The collision case study is supporting evidence for app-neutral ownership, not
a reproduction claim and not the central contribution.

## 8. Claims that must not appear

- arbitrary Python or arbitrary Callback IR compilation;
- topology-generic lowering;
- coverage of the OptiX API or all OptiX primitive configurations;
- representative/unbiased sampling of the open protocol space;
- formal compiler soundness;
- Sui et al. reproduction or same-input performance comparison;
- general closed-capsule correctness outside the admitted case-study domain;
- usability, productivity, or ease superiority without a human study;
- real-world protocol-defect prevalence;
- intrinsic 9.53x superiority over PyOptix;
- negligible overhead or strong-baseline parity before Goal5848 passes;
- portability beyond the exact NVIDIA RTX generations and software stacks
  measured.

## 9. Actual submission blockers

### P0: manuscript/evidence consistency

The current manuscript still reports zero prospective exams, two leaf kinds,
and superseded performance. It must be rewritten around the bounded
whole-protocol thesis and exact current denominators.

### P0: strong performance result

Goal5848 remains `0/2`. The intended paper performance conclusion is not
available until the exact committed/preregistered transaction passes on two RTX
generations. A failed gate must be reported and repaired through a new disclosed
successor; it must not be weakened or silently retried.

### P1: Goal5838 wording

The paper must distinguish generic framework admission from topology-specific
lowering, disclose the author-defined challenge domain, and name the
post-selection implementation cost.

### P1: artifact replay story

The artifact must explain historical commit-bound authorities, expected
current-tree stale tests, off-repository binary bytes, and reproducible source
rebuild paths. Dead documentation links must be repaired.

### P1: collision domain boundary

Either enforce an executable sufficient near-parallel exclusion for the
Boolean/owner-grouped case-study path or state exactly that the frozen workloads
avoid that domain by construction. Do not imply general capsule-intersection
equivalence.

## 10. Deadline execution plan

### Phase A: local repair and freeze

1. Make Goal5848 phase instrumentation symmetric across RTDL, idiomatic
   PyOptix, and strong PyOptix.
2. Correct Goal5845's causal wording without rewriting or deleting its exact
   internal result.
3. Add the historical/current custody replay guide and repair README links.
4. Resolve the collision-domain statement or executable certificate.
5. Complete current-byte Goal5848 hostile self-review, run ordinary and
   optimized tests, compile/lint checks, and commit a clean exact source state.
6. Freeze the formal Goal5848 preregistration only after exploratory repair is
   complete.

Current Phase A state: items 1--4 and the local review/test portion of item 5
are complete. The exact clean commit and formal freeze in items 5--6 remain
pending. The manuscript rewrite is intentionally not folded into a historical
authority or performed before the performance experiment is frozen.

### Phase B: two-generation Goal5848 execution

1. Run timer-free preflight and baseline-competence checks.
2. Build exact AOT/device artifacts with complete toolchain and source identity.
3. Run all frozen blocks with zero sample discard for both tasks and all arms.
4. Preserve every failed or adverse transaction.
5. Repeat on a distinct RTX generation without pooling raw times or computing
   cross-machine speedups.
6. Build and independently replay per-generation and cross-generation
   authorities.

### Phase C: paper and artifact

1. Rewrite the paper around the thesis in Section 7.
2. Replace stale tables with authority-backed results only.
3. Include explicit TCB, topology-specific lowering, domain-selection,
   collision-domain, human-evidence, and artifact-replay limitations.
4. Package source/build recipes and exact retained evidence without mutating
   sealed historical authorities.
5. Obtain a fresh external review of the repaired manuscript, current Goal5848
   bytes, and final authorities; then write a consensus report.
6. Run anonymous-content, page-limit, clean-install, and artifact-replay checks.

## 11. Final verdict

`PROCEED_TO_REPAIR_AND_SUBMIT`, not `READY_TO_SUBMIT`.

The project has a coherent CGO contribution: bounded whole-protocol compilation
and admission for RT-core callbacks, with cross-role proof obligations,
fail-closed executable binding, one prospective composition result, and bounded
independent refinement evidence. Claude and Codex agree on that central thesis
and on the need to rewrite the manuscript and complete Goal5848.

The remaining disagreements do not require abandoning the submission. They are
resolved by exact claim language:

- Goal5838 is a valid bounded prospective framework/composition result, not
  generic lowering;
- Goal5845 is a valid weak-arm internal measurement with an imprecise causal
  description, not an intrinsic speedup;
- historical authorities remain valid at their commits even though current-tree
  replay tests are stale;
- the current Goal5848 implementation needs a fresh post-repair external review
  because Claude did not review its final bytes.

The submission is credible only after the blockers in Section 9 are closed and
the final external review confirms the repaired bytes and prose.

## 12. Post-adjudication repairs completed locally

The following repairs were made after comparing Claude's findings with the
current source. They resolve local defects; they do not convert the review into
final external consensus or create GPU evidence.

1. Phase instrumentation is now governed by the same explicit flag for RTDL,
   idiomatic PyOptix and strong PyOptix. Formal receipt validation requires the
   enabled state for all three measured Python arms, and hostile tests reject
   its omission.
2. Goal5845 now has a non-destructive causal-wording correction. The exact
   weak-arm measurement is retained, but the text no longer attributes the
   whole difference to a device-side sort/unique step that the RTDL source does
   not perform.
3. `KNOWN_STALE_CUSTODY_CHECKS.md` distinguishes valid exact-commit historical
   authorities from expected current-tree seal failures and documents the
   Goal5832 no-commit limitation instead of inventing a clean Git identity.
4. The owner-grouped collision case study now states that near-parallel
   boundary cases are excluded by fixture construction but not enforced by its
   current linear-size admission path.
5. Root README links were replaced with live current paths. The packaging
   statement was corrected: build-isolated editable installation is supported,
   while offline installation still requires the declared setuptools backend.
6. A pre-existing Goal5809 test fixture was repaired to construct the complete
   sealed target observation/runtime manifests required by current validation;
   it now reaches and checks its intended nested-artifact mutation. The five
   Goal5807 tests blocked by two absent historical files are disclosed rather
   than mislabeled as current runtime failures.

Post-repair local verification is `232/232` for adjacent Goal5844--Goal5848
tests and `98/98` for Goal5848 under both ordinary and optimized Python. Native
GPU compilation and every Goal5848 performance gate remain unexecuted. New
Goal5848 Python passes default Ruff, while the touched legacy
`v4_rtdlexe.py` passes the fatal `E9,F63,F7,F82` selectors; no repository-wide
style-cleanliness claim is made. The formal evidence state remains `0/2` RTX
generations.
