# Call for critical review: RTDL CGO 2027 post-Goal5851 submission gate

Date: 2026-09-06

Target venue: CGO 2027

Review class: adversarial compiler/systems contribution, generality,
same-contract performance, evidence custody, manuscript, and artifact review

Requested reviewer: a fresh external reviewer with no assumed RTDL knowledge

Repository: `rtdl_v4_restricted_python_design`

Repository root on the producing machine:
`/Users/rl2025/rtdl_v4_restricted_python_design`

Branch: `codex/cgo-goal5836-handoff`

## 1. Review objective

The CGO 2027 submission deadline is 2026-09-10. Source development freezes at
2026-09-08 00:00 America/New_York. Review this work as a submission gate, not
as a request for an open-ended roadmap.

Return the smallest set of real blockers that materially affect acceptance.
Use claim deletion or narrowing for unsupported peripheral claims. Do not make
a new application, a rushed usability study, or a broad defect census a
precondition if the corresponding claim can be honestly removed.

The decisive question is:

> Does RTDL now support a scientifically defensible CGO paper about bounded
> whole-callback-protocol compilation and admission, with credible
> compositional/refinement evidence and acceptable measured public-path cost,
> or is it still primarily a collection of topology-specific implementations
> wrapped in evidence machinery?

## 2. Cold-start project primer

RTDL V4 is a restricted-Python compiler and runtime for non-rendering NVIDIA
OptiX programs. Repurposed RT workloads distribute one logical computation
across host setup, geometry and buffers, ray generation, intersection,
any-hit/closest-hit/miss callbacks, payload conventions, continuation, status,
and an exact native executable. Individually legal CUDA/OptiX fragments can
therefore compose into a globally incoherent, incomplete, or wrongly bound
protocol.

RTDL proposes to make the complete callback protocol the compilation and
admission unit. Its bounded implementation parses callback source as data,
builds typed role-indexed Callback IR, checks effects and cross-role semantic
ABI ownership, binds physical target resources and executable identity, lowers
supported protocols through trusted OptiX wrappers, and publishes output only
through a checked public lifecycle.

The intended ownership split is:

| Layer | Owns | Must not own |
| --- | --- | --- |
| Application | RT formulation, domain geometry/predicate, oracle, result meaning | generic compiler admission or native app dispatch |
| Restricted Python | closed callback-local syntax, types, effects, resource bounds | arbitrary Python/CUDA, imports, allocation, reflection, unrestricted control/atomics |
| Protocol IR/compiler | role topology, semantic ABI, obligations, target inputs, deterministic identity | automatic discovery of a profitable RT mapping or proof of application correctness |
| Runtime | materialize, bind, prepare, execute, status-gate, publish, close | checker-off fast paths or mutable/stale identity shortcuts |
| Native OptiX provider | compiler-owned wrappers, GAS/pipeline/SBT, traversal, generic bounded continuation, receipts | collision/database/graph/robot formulas or app-name dispatch |
| Evaluation | exact contracts, strong baselines, adverse-result custody, bounded gates | native-kernel-only speedups, unmatched work, or app-count generality |

The current implementation is explicitly bounded. Admission, canonical
planning, identity, provider binding, and lifecycle are schema-parametric.
Executable lowering remains compiler-owned and topology-specific. Do not award
or reject the paper based on a claim of topology-generic lowering that the
authors no longer intend to make.

RTDL does not claim arbitrary Python compilation, all OptiX protocols,
automatic RT mapping, application correctness, a soundness theorem, external
human usability, or real-world protocol-defect prevalence.

## 3. What changed since the last external review

The last Claude review is:
`history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md`.

At that review:

- HEAD was `5de0e7ec3a48af73b2e645a5ff0edaae9b8c6696`;
- Goal5848 existed as a 52-file dirty WIP diff with SHA-256
  `52f185f3d92fffdc792014add5344f593b79fbdd52589a3650a96766350de424`;
- formal Goal5848 GPU evidence was `0/2` generations;
- the latest honest first-result comparison was materially adverse;
- the manuscript was already stale.

Since then, the project committed the strong-baseline experiment, retained a
long sequence of pre-formal and formal failures, repaired measured generic
runtime/evidence defects without changing the frozen workloads, arms, timers,
estimators, or thresholds, and executed the final identical source on Ada and
Ampere.

The exact experiment source is:

- commit `d653fe4ad170c5b51fee309d653c9565944dcf2e`;
- tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`;
- predecessor `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`.

The pre-CFR documentation checkpoint is
`2bc3a345c0593b739f000f65392608d50223e434`. After `d653fe4`, only reports,
packets, policy, and memory files changed. At review start, capture the actual
current HEAD and verify that `git diff --name-only d653fe4..HEAD` contains no
source, native, experiment, workload, baseline, timer, estimator, threshold,
or test changes.

Goal5848/Goal5851 now have an internal cross-generation status of:

```text
PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING
```

This call does not ask you to ratify that string. It asks you to reconstruct
whether the underlying source, evidence, and bounded interpretation deserve it.

## 4. Required trust order and review conduct

Use this trust order:

1. raw evidence bytes and exact Git objects;
2. machine-readable authorities and independent recounts;
3. implementation source and focused tests;
4. final technical reports;
5. the strict self-review report;
6. this call for review;
7. README and manuscript prose.

A mismatch is a finding. Do not resolve it by selecting the more favorable
document.

Keep the review read-only. Do not edit source, regenerate or reseal old
evidence, discard an adverse run, update the manuscript, or silently substitute
a different checkout. You may create only your final review report.

At the beginning, record:

```bash
pwd
git rev-parse HEAD
git rev-parse HEAD^{tree}
git branch --show-current
git status --short
git diff --name-only d653fe4ad170c5b51fee309d653c9565944dcf2e..HEAD
```

The untracked file
`history/internal_docs/independent_reaudit_cfr_claude_adjudication_20260906.md`,
if still present, is an internal scratch review. It is not external consensus,
not part of the committed review packet, and must not substitute for your own
source/evidence reconstruction.

Use the compatible local Python when running focused checks:

```bash
cd /Users/rl2025/rtdl_v4_restricted_python_design
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest <selected-tests>
```

Do not begin with broad all-history discovery. It is known to mix absent
historical assets, optional platforms, and current tests. If you run it, report
its failures rather than using them indiscriminately as either current runtime
bugs or harmless noise.

## 5. Primary review inputs

Read these first:

1. This call for review.
2. `history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md`.
3. `history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md`.
4. `history/internal_docs/codex_claude_cgo_adjudication_20260905.md`.
5. `history/internal_docs/goal5851_cross_generation_final_report_20260906.md`.
6. `AGENTS.md` and `KNOWN_STALE_CUSTODY_CHECKS.md`.
7. `paper/cgo2027/main.tex` and `paper/cgo2027/README.md`.

Then inspect implementation and experiment source rather than relying on the
reports:

- `src/rtdsl/v4_rtdlexe.py`;
- `src/rtdsl/v4_aot_cache.py`;
- `src/native/optix/rtdl_optix_api.cpp`;
- `src/native/optix/rtdl_optix_core.cpp`;
- `src/native/optix/rtdl_optix_v4_callback_poc.cpp`;
- `experiments/goal5848_strong_baseline/contracts.py`;
- `experiments/goal5848_strong_baseline/controller.py`;
- `experiments/goal5848_strong_baseline/worker.py`;
- `experiments/goal5848_strong_baseline/strong_pyoptix.py`;
- `experiments/goal5848_strong_baseline/direct_bridge.py`;
- `experiments/goal5848_strong_baseline/workloads.py`;
- `scripts/goal5848_build_transaction_authority.py`;
- `scripts/goal5848_build_cross_generation_authority.py`;
- `scripts/goal5848_pod_prepare_and_run.sh`;
- `tests/goal5848_*_test.py`; and
- `tests/goal5851_triangle_fused_replay_test.py`.

For the older generality/refinement findings, inspect:

- `src/rtdsl/v4_family_schema.py`;
- `src/rtdsl/v4_family.py`;
- `src/rtdsl/v4_family_route_adapters.py`;
- `src/rtdsl/v4_sphere_any_hit_count_wrapper_codegen.py`;
- `scripts/goal5838_freeze_generic_core.py`;
- `scripts/goal5840_independent_target_checker.py`;
- `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json`;
- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_AUTHORITY.json`; and
- `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md`.

## 6. Raw Goal5848/Goal5851 evidence

The full evidence is intentionally outside Git on the producing machine.

Ada:
`/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/`

Ampere:
`/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/`

Cross-generation:
`/Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete/`

Expected archive SHA-256 values:

- Ada:
  `c9128bae15da7ed326c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced`;
- Ampere:
  `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2`.

Expected single-generation authority/recount file SHA-256 values:

- Ada:
  `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7`;
- Ampere:
  `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3`.

Expected cross-generation authority/recount file SHA-256:
`99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692`.

Do not trust only those digests. Inspect manifest counts, environment identity,
source commit/tree, task contracts, worker/process counts, retry/discard,
per-block ratios, baseline competence, instrumentation authority, exact AOT
hits, Direct derivation, and the authority/recount equality.

The full authority binds pod-absolute `/workspace` paths. Portable manifest and
worker/gate recounts pass after relocation; unchanged full-authority rebuilding
does not. Judge whether the proposed artifact wording makes that distinction
adequately.

## 7. Results to reconstruct, not assume

Every ratio is numerator/denominator. Lower is faster. The final registered
summary should reconstruct as:

| Generation | Task | RTDL/Direct median | Observed maximum Direct block, descriptive only | RTDL/strong entry | Old post-import diagnostic | Successor/predecessor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| RTX 4090 Ada CC 8.9 | Triangle | `1.175066x` | `1.211025x` | `0.642180x` | `1.559788x` adverse | `0.903016x` |
| RTX 4090 Ada CC 8.9 | Relation | `1.076852x` | `1.092253x` | `0.653826x` | `1.749327x` adverse | `0.584438x` |
| RTX 3090 Ampere CC 8.6 | Triangle | `1.133636x` | `1.142675x` | `0.618362x` | `1.637468x` adverse | `0.922388x` |
| RTX 3090 Ampere CC 8.6 | Relation | `1.094795x` | `1.118811x` | `0.681393x` | `1.837415x` adverse | `0.608228x` |

Each generation should contain exactly:

- 512 instrumentation processes;
- 80 formal processes;
- 10,240 retained steady samples;
- zero retry;
- zero discard;
- byte-identical authority and independent recount; and
- both task gates passing.

The cross-generation authority must not compare raw time across machines.

## 8. Mandatory adversarial questions

### 8.1 Contribution and generality

1. Is "bounded whole-protocol compiler" accurate when the admission,
   identity, and lifecycle framework is schema-parametric but executable
   lowerers remain topology-specific?
2. Is that architecture a meaningful compiler contribution for CGO, or does
   the topology-specific trusted code dominate enough to make the contribution
   primarily library engineering?
3. Does Goal5838 support exactly one prospective compositional-extension result
   over a frozen author-defined ten-row domain, or is even that wording too
   strong?
4. Which exact manuscript sentences must avoid "generic," "arbitrary," or
   "unbiased"?

### 8.2 Independent checking

5. Is Goal5840 correctly described as an independent finite structural check
   over specialized target output?
6. Does the self-review's unconditional-early-return probe require a stronger
   limitation than that wording, or does it invalidate any currently intended
   claim?
7. Does independence from `rtdsl` materially reduce circularity despite shared
   source-layout assumptions?

### 8.3 Baseline fairness and performance

8. For each task, do RTDL, strong PyOptix, idiomatic PyOptix, Direct OptiX, and
   predecessor RTDL execute the same semantic contract and place equivalent
   preparation/continuation work on the same side of each timer?
9. Is Arm C genuinely stronger and competent, or is material RTDL-favorable
   work placement still unmatched?
10. Does public RTDL versus Direct compare the public checked result path rather
    than a hidden native kernel-only path?
11. Does `d653fe4` preserve process/thread/reentrancy, identity, native status,
    compact status, and output-oracle obligations while deferring only
    measurement bookkeeping?
12. Does lazy receipt validation create a semantic publication gap, or is it
    correctly limited to trusted-provider measurement evidence after
    synchronous native status?
13. Is the registered `1.20x` public/Direct median threshold reasonable for a
    "no unacceptable median tax" claim? Public/Direct has no registered
    worst-block gate; judge whether retaining and reporting every block is
    sufficient, and do not borrow the `1.35x` implementation-entry limit or
    convert the median gate into a speedup/tail-bound claim.

### 8.4 Endpoint selection and adaptivity

14. Is changing the primary lifecycle endpoint after observing the old
    post-import state mismatch scientifically defensible when the old endpoint
    remains mandatory and adverse?
15. Must the paper show both implementation-entry and post-import results, and
    what exact causal wording is safe?
16. Given repeated result-informed repairs on the same two workloads, may the
    final transactions be called confirmatory, or only fresh engineering-gate
    validation of a task-tuned implementation?
17. Do frozen thresholds/workloads/arms/timers/estimators plus complete adverse
    custody sufficiently constrain p-hacking concerns for the bounded claim?

### 8.5 Evidence and artifact integrity

18. Reconstruct both single-generation authorities and the cross-generation
    gate direction. Are there missing, pooled, retried, discarded, or
    inconsistently sourced rows?
19. Is the absolute-path authority limitation acceptable if manifest and
    worker/gate recount are portable and the limitation is explicit?
20. Are historical Goal5832/5837/5838/5840/5843 custody boundaries sufficiently
    separable from current-source testing?
21. Does the full-repository discovery result require a submission blocker, or
    can a layered artifact test matrix adequately address it?

### 8.6 Failure semantics

22. Reproduce or inspect the provider bind/close double-fault described in the
    self-review. Does masking the primary exception and losing retry ownership
    contradict a central paper claim?
23. Can the paper defensibly descope that unmeasured double-fault while keeping
    status-before-output and ordinary cleanup claims, or must source be repaired
    before code freeze?
24. If repair is required, state explicitly whether the existing two-generation
    performance evidence can still be used as evidence for the old exact
    source, and how the paper must disclose the source difference.

### 8.7 Manuscript readiness

25. Identify every current manuscript count, architecture statement, hardware
    row, performance result, and conclusion that is stale or overbroad.
26. State the strongest one-sentence thesis and at most four contributions the
    current evidence can support.
27. Specify the exact adverse results and limitations that must remain visible.
28. Decide whether the paper is submit-worthy after bounded rewrites, even
    without human usability or prevalence evidence.

## 9. Known self-review findings that require independent judgment

Do not merely repeat these. Verify and accept, reject, or refine each one.

1. Manuscript, paper README, root evidence summary, and sprint status are stale.
2. The two-generation performance branch passes internally but remains
   outcome-adaptive engineering evidence.
3. The lifecycle endpoint repair is valid only with dual reporting and no
   intrinsic-language-speedup wording.
4. `InitializingRTDLProvider.bind/close` has a reproducible double-fault cleanup
   defect that can mask the primary exception and lose retry ownership.
5. Goal5840 independently checks bounded structure, not general control-flow or
   numerical semantics.
6. Current-tree historical checks for Goals5832, 5837, 5838, and 5843 fail for
   disclosed snapshot-drift reasons; the existing guide omits two.
7. Full repository discovery is not a usable green artifact gate: 13,638 tests
   produced 756 failures, 6,214 errors, and 600 skips in the current Mac
   environment.
8. Earlier Goal5850/Goal5851 report revisions miscounted three Direct blocks as
   two and mislabeled `1.35x` as a Direct worst-block gate. Current reports
   contain explicit corrections; the raw median-only Direct gates are
   unaffected. Verify that no downstream prose repeats either error.
9. Detailed operation-receipt validation is lazy, while native and compact
   status plus output oracle are synchronous.
10. No external author/usability study or real-world prevalence result exists.

## 10. Focused verification commands

At minimum, run:

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest discover -s tests -p 'goal5848*_test.py'

PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -O \
  -m unittest discover -s tests -p 'goal5848*_test.py'

PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5851_triangle_fused_replay_test
```

Inspect expected current-tree historical failures rather than hiding them:

```bash
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5838_core_seal_and_selection_test

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5832_protocol_shape_algebra_test

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5843_build_final_authority.py --verify-stored
```

Do not repair or reseal those historical authorities during review.

## 11. Required output format

Write one detailed Markdown report under `history/internal_docs/` with these
sections in this order:

1. exact custody snapshot and files reviewed;
2. cold-start restatement of the problem, contribution, nonclaims, and deadline;
3. closure table for every material finding from the 2026-09-05 Claude review;
4. new P0/P1/P2/P3 findings, ordered by submission severity, with source line
   references and direct evidence;
5. architecture/generality verdict;
6. Goal5838 bounded prospective-exam verdict;
7. Goal5840 independent-checker verdict;
8. baseline fairness and same-contract verdict for each arm/task;
9. Goal5848/Goal5851 evidence recount and performance verdict;
10. endpoint/adaptivity verdict;
11. provider double-fault and failure-semantics verdict;
12. artifact/custody/replay verdict;
13. manuscript claim ledger: supported, supported only after rewrite, forbidden;
14. the smallest credible repair plan with at most five actions; and
15. final verdict: `SUBMIT_AFTER_BOUNDED_REWRITE`,
    `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`, or `DO_NOT_SUBMIT`, with a
    concrete rationale.

For each finding, distinguish:

- source/runtime defect;
- experiment-design limitation;
- evidence/custody limitation;
- manuscript overclaim;
- artifact usability problem; or
- post-submission work.

Do not use test count, goal count, application count, or evidence volume as a
substitute for judging novelty, correctness, fairness, and claim scope.

## 12. Review decision boundary

An external `Accept` does not by itself authorize public claims. The project
must absorb the review, resolve factual disagreements against source/evidence,
freeze a claim ledger, and then rewrite the manuscript. Conversely, a finding
does not automatically kill the paper if the affected claim can be removed
without damaging the bounded central contribution.

The requested review should optimize for a defensible CGO submission, not for
protecting prior work or demanding unlimited new work.
