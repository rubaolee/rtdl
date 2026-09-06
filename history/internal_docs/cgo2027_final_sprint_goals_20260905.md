# CGO 2027 final-sprint goals

Date: 2026-09-05

Submission date: 2026-09-10

Internal code-freeze deadline: **2026-09-08 00:00 America/New_York**

Status: `GOAL5849_COMPLETE__GOAL5850_NEXT`

## 1. Non-negotiable operating rule

No development work is permitted after the internal code-freeze deadline.
From 2026-09-08 onward, the submission may only consume already committed code,
already frozen protocols, and retained evidence.

After the freeze, permitted work is limited to:

- manuscript and bibliography editing;
- claim narrowing and evidence-ledger reconciliation;
- running already committed tests, builds and artifact scripts;
- copying and hashing retained evidence without changing it;
- anonymous artifact assembly and clean-checkout replay;
- external review and prose-only response; and
- submission-system checks and upload.

After the freeze, forbidden work includes:

- changes under `src/`, `include/`, `experiments/`, `scripts/` or `tests/`;
- changes to workloads, arms, thresholds, timers, estimators or sample policy;
- new optimizations, app routes, protocol families or native kernels;
- repairing a failed formal result and rerunning it under the same claim; and
- deleting, pooling, relabeling or selectively excluding adverse evidence.

If a code or experiment defect is found after the freeze, the affected claim is
removed or narrowed for this submission. The defect becomes post-submission
work. The deadline never justifies changing a frozen protocol.

## 2. Goal sequence

### Goal5849: commit the reviewed Goal5848 source checkpoint

Target window: 2026-09-05

Purpose: convert the large reviewed working tree into one exact, clean,
replayable source identity before any formal GPU transaction.

Acceptance criteria:

1. Claude's review, Codex's adjudication, the Goal5845 wording correction,
   custody guide and collision-domain boundary are included.
2. Phase instrumentation is symmetric across RTDL, idiomatic PyOptix and strong
   PyOptix, and all formal receipts require the enabled state.
3. Goal5848-focused tests pass `98/98` in ordinary Python and under `python -O`.
4. Goal5844--Goal5848 adjacent tests pass `232/232`.
5. All new Goal5848 Python and the modified Goal5847 test pass default Ruff;
   the touched legacy `v4_rtdlexe.py` passes the fatal correctness selectors
   `E9,F63,F7,F82`. Compileall, every Goal5848 CLI `--help`, Bash syntax and
   `git diff --check` also pass. Repository-wide style reformatting is outside
   this freeze and must not create an unrelated diff.
6. Root documentation has no missing local links.
7. A focused final diff review finds no unresolved local P0/P1 issue inside the
   bounded Goal5848 design.
8. All intended files are committed and pushed; the worktree is clean and the
   exact commit/tree identities are recorded.

Failure rule: do not begin a formal pod run from dirty or unpushed bytes.

### Goal5850: execute Goal5848 on RTX generation A

Target window: 2026-09-06

Purpose: produce the first complete formal strong-baseline transaction from the
exact Goal5849 commit.

Acceptance criteria:

1. The pod exposes exactly one idle supported RTX generation and checks out the
   exact Goal5849 commit in detached, clean state.
2. The committed one-shot runbook completes host/toolchain preflight, exact AOT
   construction, cache-hit qualification, timer-free correctness, baseline
   competence and instrumentation-overhead gates.
3. Exactly 80 formal cells execute: two tasks, five arms and eight balanced
   blocks, with zero retries and zero discarded samples.
4. Both tasks independently pass all frozen correctness and performance gates.
5. The authority and independent recount are byte-identical.
6. The output directory, archive, SHA-256 file and terminal transcript are
   retained off the source checkout.

Failure rule: retain the complete failure bundle. Before code freeze, a repair
is allowed only under a new source commit, a new output root and a completely
new transaction. Thresholds and adverse rows may not be changed.

### Goal5851: execute RTX generation B and build cross-generation authority

Target window: finish by 2026-09-07 20:00 America/New_York

Purpose: close Goal5848 on a second, distinct RTX architecture generation and
derive the non-pooled cross-generation authority.

Acceptance criteria:

1. Generation B differs from generation A in compute-capability generation and
   GPU UUID, while using the identical committed Goal5848 source identity.
2. Generation B independently satisfies every Goal5850 acceptance criterion.
3. The cross-generation builder accepts both authority/recount pairs.
4. Source and predecessor identities match across generations.
5. No raw timing is divided across machines; only within-machine gate direction
   is compared.
6. The cross-generation authority and all source archives are retained and
   hashed.

Failure rule: if two passing generations do not exist by the target time,
Goal5848 remains incomplete and supplies no positive paper-facing performance
claim. Existing adverse evidence remains in the artifact ledger.

### Goal5852: impose the irreversible code freeze and choose the evidence branch

Deadline: 2026-09-08 00:00 America/New_York

Purpose: end development with a binary decision instead of allowing performance
work to consume the writing window.

Acceptance criteria:

1. Record the frozen source commit, Git tree, submodule/upstream identities and
   clean status.
2. Record either `GOAL5848_TWO_GENERATION_PASS` or
   `GOAL5848_NOT_COMPLETE__POSITIVE_CLAIM_REMOVED`.
3. Produce a claim ledger mapping every intended sentence/table row to an exact
   authority, or marking it forbidden.
4. Record all historical/current custody limits and absent off-repository bytes.
5. Install the no-development-after-freeze rule in the manuscript and artifact
   work instructions.

There is no repair branch after Goal5852.

### Goal5853: rewrite the manuscript around the bounded contribution

Target window: 2026-09-08

Purpose: replace the stale manuscript with a source- and authority-consistent
CGO paper.

Acceptance criteria:

1. Abstract, introduction and contributions state bounded whole-protocol
   compilation/admission, not arbitrary Callback IR or topology-generic
   lowering.
2. The paper discloses topology-specific trusted lowerers, the Goal5838
   author-defined 10-row domain and its 2,635-line realization cost.
3. Goal5840 is described at its exact three-route, four-mode, five-property
   independent-checker scope.
4. No usability, productivity, real-world defect-prevalence, general capsule,
   universal portability or intrinsic 9.53x claim appears.
5. Performance text follows Goal5852's evidence branch. A failed or incomplete
   Goal5848 is reported or omitted, never converted into a success.
6. Native payload-access mechanisms and RTDL's residual contribution are
   compared explicitly.
7. Every quantitative statement identifies exact task, arm, regime, hardware,
   authority and claim boundary.
8. Limitations and threats state the narrow protocol families, author-defined
   challenge domain, topology-specific TCB, zero external human authors and
   artifact custody limits.

### Goal5854: build and replay the anonymous artifact

Target window: 2026-09-09 morning

Purpose: make the submitted evidence self-consistent, anonymous and replayable
without rewriting historical authorities.

Acceptance criteria:

1. Build from a fresh clean checkout of the Goal5852 frozen commit.
2. Include exact retained evidence bytes when distributable; otherwise disclose
   absent historical DSOs/capsules and provide source-rebuild or functional-
   replay instructions without claiming byte replay.
3. Separate current regression tests from expected historical seal-drift tests.
4. Run the artifact verifier twice and require byte-identical deterministic
   package output where the packaging contract promises determinism.
5. Scan source, archive contents, logs and rendered manuscript for names, local
   paths, IP/pod endpoints, internal review text, Goal identifiers and withdrawn
   claims.
6. Verify a clean install or the documented source-tree fallback in an isolated
   environment.
7. Record the artifact SHA-256 and anonymous upload destination.

### Goal5855: obtain final external review and close reviewer attacks

Target window: 2026-09-09 afternoon/evening

Purpose: ask Claude and at least one independent second reviewer to inspect the
actual frozen source/evidence, rewritten manuscript and anonymous artifact.

Acceptance criteria:

1. Reviewers receive a self-contained request naming the central thesis, exact
   claim ceilings, Goal5848 branch and known custody limitations.
2. Every reviewer finding receives `accept`, `reject-with-source-evidence`, or
   `claim-descope`; no finding is silently ignored.
3. Only prose, bibliography, captions or artifact documentation may change.
4. Any source/experiment defect causes claim removal, not post-freeze code work.
5. A final consensus report distinguishes genuine agreement from unresolved
   severity differences.

### Goal5856: final anonymous submission gate and upload

Target window: 2026-09-10, with upload completed well before the official cutoff

Purpose: freeze and submit exactly the reviewed bytes.

Acceptance criteria:

1. Paper builds without undefined references, overfull-box surprises or missing
   figures/tables, and satisfies the official page/format rules.
2. Two independent anonymity scans pass for manuscript and artifact.
3. The final PDF text is checked against the claim ledger and withdrawn-result
   list.
4. PDF, source bundle and artifact hashes are recorded before upload.
5. Uploaded bytes are downloaded or otherwise verified against the recorded
   hashes when the submission system permits.
6. Submission confirmation and timestamp are retained.

## 3. Critical path

```text
Goal5849 clean commit
  -> Goal5850 generation A
  -> Goal5851 generation B + cross-generation authority
  -> Goal5852 irreversible code/evidence freeze
  -> Goal5853 manuscript rewrite
  -> Goal5854 anonymous artifact
  -> Goal5855 external review and prose-only closure
  -> Goal5856 final gate and upload
```

Goal5851 is the only remaining GPU-dependent goal. Goal5849 and Goal5850 are
complete; Goal5851 is the next active goal. Goal5852 prevents either GPU
availability or a bad result from consuming the protected final two days.

## 4. Goal5849 completion record

Goal5849 completed locally on 2026-09-05.

- reviewed implementation commit:
  `1f5e06f67cd0ad08354d5659cf3684f5bb1e8e24`;
- reviewed implementation tree:
  `086a61d827f35fdaf5930d7d4963ab0087c1b491`;
- Goal5844--Goal5848 tests: `232/232 PASS`;
- Goal5848 tests under `python -O`: `98/98 PASS`;
- selected cross-goal provider/lifecycle/runtime tests: `212/212 PASS`, with
  four declared skips;
- default Ruff over new Goal5848 code: pass;
- fatal Ruff selectors over touched legacy files: pass;
- compileall, all Goal5848 CLI `--help`, Bash syntax, Markdown links,
  staged-diff validation and secret scan: pass.

At Goal5849 completion, the commit immediately following the reviewed
implementation changed only this sprint-status record and the repository work
guide and became the initial Goal5850 source. Goal5850's preserved failures then
activated its explicit pre-freeze successor rule. The controlling two-generation
source is therefore the successful `c4351f612...` identity recorded below, not
the initial Goal5849 checkpoint. No implementation byte may differ between the
two passing generations.

## 5. Goal5850 completion record

Goal5850 completed on 2026-09-06 under the preregistered successor rule. Three
complete failures were retained rather than relabeled: transaction 1 failed the
old post-import endpoint, transaction 2 failed Direct runtime-identity
authority, and transaction 3 failed the relation RTDL/Direct median gate at
`1.209372x`. Their archive SHA-256 values and repairs are preserved in
`goal5850_generation_a_final_report_20260906.md`.

The fresh passing transaction used source commit
`c4351f6120d1d73d7c2b72ff4d61ad747061f836`, tree
`1faf8ca2a99e4c1011443942479e2edf7b297edb`, on RTX 2000 Ada CC 8.9. It ran all
512 instrumentation workers and all 80 formal workers with zero retry/discard;
both tasks passed all primary gates, and two independent authorities were
byte-identical. The successful archive SHA-256 is
`f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8`.

Goal5851 must use the identical `c4351f612...` implementation source on a GPU
with a different compute-capability generation and UUID. Later documentation
commits do not supersede that experiment identity.

## 6. Submission success definition

The sprint succeeds when a scientifically defensible, anonymous paper and
replayable artifact are submitted on time. Acceptance is not under author
control. Honest claim scope, preserved adverse evidence, frozen measurement
rules and a complete upload are under author control and are mandatory.
