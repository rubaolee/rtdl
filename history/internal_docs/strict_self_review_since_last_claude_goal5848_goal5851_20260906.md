# RTDL CGO 2027 strict self-review and progress report since the last Claude review

Date: 2026-09-06

Review class: internal adversarial source, evidence, baseline-fairness,
generality, custody, manuscript, and artifact audit

Decision:
`REVIEW_READY__INTERNAL_PERFORMANCE_GATES_PASS__SUBMISSION_BLOCKERS_OPEN`

External-review state: `PENDING`

Public/manuscript claim state: `NOT_AUTHORIZED`

## 1. Executive conclusion

The work since the 2026-09-05 Claude review is substantial and directly closes
the largest performance-evidence gap that existed at that review. Goal5848 had
zero formal GPU transactions when Claude reviewed it. The final source is now
one clean pushed commit, and that identical source independently passes the
frozen correctness and performance protocol on one Ada GPU and one Ampere GPU.

The strongest current performance result is deliberately narrow:

- task 1 is a 16,384-query checked-U64 weighted triangle all-hit reduction;
- task 2 is a 4,096-query closed-AABB relation count;
- both use prepared, exact public replay contracts;
- both compare public RTDL to a same-contract Direct OptiX arm within each
  machine;
- RTDL/Direct median ratios are between `1.076852x` and `1.175066x`;
- all observed per-block ratios are between `1.066402x` and `1.211025x`;
- both frozen `1.20x` public/Direct median gates pass on both GPUs;
- there is no registered public/Direct worst-block gate, so the observed maxima
  are descriptive rather than an additional passing gate;
- each generation retains 512 instrumentation workers, 80 formal workers, and
  10,240 steady samples with zero retry and zero discard.

This is evidence that the two measured RTDL public paths can retain whole-
protocol checks without an unacceptable steady prepared-replay tax relative to
Direct OptiX on the two tested generations. It is not evidence that RTDL is
faster than Direct OptiX, that arbitrary callback protocols are efficient, or
that cross-machine raw times are comparable.

The submission is not ready. The current manuscript and its README still
describe older constructors, counts, hardware, and performance evidence. The
root README also presents a superseded performance state. The public artifact
is not assembled. External review has not accepted the new source/evidence.
Strict self-review also reproduces a provider-initialization double-fault
cleanup defect and a limitation in the Goal5840 structural checker that must be
disclosed or repaired before corresponding broad claims can appear.

The correct next action is external adversarial review of this exact packet,
followed by claim adjudication and writing. It is not another application,
another performance optimization, or a retrospective attempt to make every
historical test pass.

## 2. Deadline and scope

The CGO 2027 submission date is 2026-09-10. The controlling repository policy
sets an irreversible code freeze at 2026-09-08 00:00 America/New_York. After
that point, production, compiler, native, experiment, test, workload, arm,
timer, estimator, and threshold changes are forbidden. Writing, claim
narrowing, execution of frozen tools, artifact assembly, review, and submission
checks remain allowed.

This report audits the delta from the last external review through the final
Goal5848/Goal5851 evidence. It also revisits earlier findings where the new
performance work changes their disposition. It does not reopen all historical
V1-V3 engineering as current V4 product scope.

## 3. Exact review snapshot

Repository:
`/Users/rl2025/rtdl_v4_restricted_python_design`

Branch:
`codex/cgo-goal5836-handoff`

Last Claude review baseline:

- committed HEAD:
  `5de0e7ec3a48af73b2e645a5ff0edaae9b8c6696`;
- tree: `15a7c0d23a04e35aa936d8b976ad79b4c9c38931`;
- review-time dirty tracked diff SHA-256:
  `52f185f3d92fffdc792014add5344f593b79fbdd52589a3650a96766350de424`;
- review-time diffstat: 52 files, 16,040 insertions, 30 deletions;
- Goal5848 formal evidence at that time: `0/2` generations.

Final experiment source:

- commit: `d653fe4ad170c5b51fee309d653c9565944dcf2e`;
- tree: `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`;
- subject: `Reduce prepared triangle replay overhead`;
- predecessor fixed by the Goal5848 contract:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`;
- binary diff SHA-256 from the last review HEAD to the experiment source:
  `28bdeb72be0080292f50db86e05eb7bd0c0a5b94e8312a010422eab8f8b97273`.

Pre-report documentation checkpoint:

- commit: `2bc3a345c0593b739f000f65392608d50223e434`;
- tree: `61c3b43cf9508d7976035a90934de306f325f557`;
- branch and origin were synchronized;
- `d653fe4..2bc3a345c` changes only `AGENTS.md`, four Goal5851 reports/packets,
  and three memory files;
- no implementation, workload, baseline, timer, estimator, threshold, or test
  changed after `d653fe4`.

Delta from the last review HEAD to the pre-report checkpoint:

- 24 commits;
- 85 files changed;
- 24,014 insertions and 153 deletions;
- 61 implementation/experiment/test files changed through `d653fe4`, totaling
  17,764 insertions and 129 deletions in that selected set;
- pre-report textual diff SHA-256:
  `9f4074054832745fee73a3b82a77624ab4d3c58a136cd1b58be8b39ec9673ad8`.

At self-review start, the only unrelated working-tree entry was the untracked
file
`history/internal_docs/independent_reaudit_cfr_claude_adjudication_20260906.md`.
It was read as an internal lead, not modified, not committed, and not treated
as external review or consensus. The two counterexamples from it were
independently rerun during this self-review.

## 4. Research problem and claim ceiling

RTDL V4 addresses a protocol-composition problem in non-rendering OptiX use.
One logical computation is distributed across host setup, geometry and buffer
binding, ray generation, intersection, any-hit or closest-hit callbacks,
payload conventions, continuation, status handling, and the exact executable
that is launched. CUDA/OptiX fragments can each be locally legal while their
composition is globally incoherent, incomplete, or bound to the wrong
physical artifact.

RTDL's proposed contribution is to make the complete callback protocol the
unit of compilation and admission. The bounded implementation provides:

- restricted Python callback source parsed as data rather than imported;
- typed, role-indexed Callback IR and closed effect/resource contracts;
- cross-role semantic ABI and continuation checks;
- physical geometry, buffer, SBT, provider, and executable identity binding;
- compiler-owned target wrappers and topology-specific trusted lowerers;
- prepared public execution with status-before-output behavior;
- independent bounded target-structure checking; and
- exact, same-contract performance evidence for two representative prepared
  routes.

The current architecture is not a topology-generic lowering algorithm. The
schema-parametric part covers admission, canonical planning, identity,
provider binding, and lifecycle. Executable realization remains implemented by
compiler-owned topology-specific lowerers/templates. That is a bounded whole-
protocol compiler, not an arbitrary Callback IR compiler.

RTDL does not automatically discover a profitable RT formulation, prove an
application correct, compile arbitrary Python/CUDA, cover all OptiX callback
graphs, establish a soundness theorem, or prove usability/productivity. No
external human has authored an RTDL application, and the repository has no
real-world defect-prevalence result. Those claims must remain absent.

## 5. Closure of findings from the last Claude review

| Prior finding | Current disposition | Evidence or remaining action |
| --- | --- | --- |
| P0-1: the sealed Goal5838 core does not perform executable lowering | Accepted as a scope limit, not as proof that RTDL is not a compiler | Use "schema-parametric admission/identity/lifecycle with topology-specific trusted lowerers"; never claim topology-generic lowering |
| P0-2: the Goal5838 challenge domain is author-defined and narrow | Still true | Preserve the exact frozen ten-row domain and one selected previously unimplemented composition; do not call it an unbiased new-application sample |
| P0-3: Goal5845's 9.53x causal explanation overstated device-side canonicalization | Corrected additively | `CAUSAL_WORDING_CORRECTION_20260905.md` separates device deduplication from native-host final canonicalization; the weak-arm reciprocal is not paper-facing |
| P1-1: current-tree Goal5838/Goal5832 custody checks fail | Partially documented | `KNOWN_STALE_CUSTODY_CHECKS.md` explains those two, but current-tree Goal5837 and Goal5843 failures are still missing from that guide |
| P1-2: collision near-parallel exclusion is not enforced by the Boolean route | Claim narrowed, runtime not repaired | The case study is fixture-domain-only by construction; no general closed-capsule correctness claim is allowed |
| P1-3: historical native/raw evidence bytes are outside Git | Still open for artifact packaging | Goal5848 archives contain their exact current native, Direct, PyOptix, PTX, CUBIN, and receipts; older Goal5838/5840 off-Git byte limits remain |
| P1-4: manuscript is stale | Still open and now more stale | Rewrite is a P0 submission blocker |
| P2-1: provider identity is load-time image identity | Claim scope accepted | Do not imply per-call filesystem rehashing |
| P2-2: app-vocabulary blacklist is narrow | Hygiene only | Do not use a string blacklist as architectural app-neutrality proof |
| P2-3: legacy app vocabulary remains in the package | Artifact partition issue | Separate current V4 paths from retained V1-V3 modules in artifact documentation |
| P2-4: README had dead links and CFR misstated packaging | Locally closed | Local links now resolve; `pyproject.toml` exists, while offline build dependencies still require disclosure |
| P3-1: Goal5848 instrumentation was asymmetric | Closed before formal data | One explicit policy and paired ON/OFF protocol is used for both RTDL and PyOptix paths; 512 workers per generation qualify it |
| P3-2: pod endpoints exist in sealed evidence | Open packaging hygiene | Scrub only a derived anonymous artifact view; never mutate sealed authorities |
| Goal5848 had zero of two required GPU generations | Internally closed | Identical `d653fe4` source passes Ada and Ampere; external review is still required |

## 6. Work completed after the review

### 6.1 A strong, same-contract five-arm experiment

Goal5848 now defines five arms for each of two exact tasks:

| Arm | Meaning | Formal role |
| --- | --- | --- |
| A | Public RTDL prepared execution | Subject |
| B | Idiomatic pinned PyOptix | Competence reference |
| C | Pinned PyOptix plus equivalent device continuation | Strong Python baseline |
| D | Direct CUDA/OptiX executable | Low-level same-contract baseline |
| E | Frozen predecessor RTDL | Regression control |

The two frozen workloads are generated from one standard-library-only packed
authority:

| Task | Size | Semantics | Public result |
| --- | ---: | --- | --- |
| `BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1` | 16,384 triangles and 16,384 rays | one ray/triangle hit with checked U64 weights | one exact reduced U64 scalar |
| `CUSTOM_AABB_CLOSED_RELATION_COUNT_V1` | 4,096 indexed and source AABBs | closed overlap, one expected self pair per row | exact relation count/contract |

All arms consume pinned packed bytes and return the same task-level answer.
Source compilation, GAS/pipeline preparation, and static upload are outside the
steady prepared-execution interval for every arm. Direct and PyOptix support
artifacts are built and hash-bound in each transaction rather than downloaded
as unrecorded binaries.

### 6.2 Evidence and artifact hardening

The post-review implementation added or repaired:

- a content-addressed exact AOT cache with request, authority, and hit probes;
- pinned Direct source derivation and a compiled Direct worker;
- pinned PyOptix source/build receipts;
- independently built PTX and relation-compaction CUBIN receipts;
- regular NVRTC image selection with explicit rejection of CUDA `stubs/`;
- exact native DSO, PTX, CUBIN, workload, provider, and environment hashes;
- timer-free four-arm correctness witnesses for both tasks;
- strong-baseline competence checks before formal comparisons;
- a symmetric, independently reconstructed instrumentation qualification;
- one-shot fail-closed pod execution and archive creation;
- single-generation authority plus byte-identical recount; and
- a cross-generation authority that compares only within-machine gate
  direction and explicitly refuses cross-machine raw-time ratios.

### 6.3 Retained repair and failure chain

The project did not obtain the final result in one prospective attempt. The
complete sequence is part of the scientific record.

| Source or stage | Observed issue | Resolution and status |
| --- | --- | --- |
| `5d78ead7f...` pre-formal | duplicate resolved CUDA library aliases | canonicalized by `ed83b2143...`; no formal rows |
| next pre-formal | generated Direct source used a non-portable relative include | pinned two-file bundle in `6b76f2b1e...` |
| next pre-formal | CUDA link-time NVRTC stub selected | `d3d532b74...` rejects stubs and proves real NVRTC with fresh compilation |
| next pre-formal | content-addressed `.rtdlexe` renamed to `artifact.bin` | cache-entry v2 in `b132cdb99...` preserves the digest name |
| next pre-formal | timer-free bundle singleton-tuple construction bug | fixed by `e80a31e52...` |
| next nonformal witness | strong PyOptix guard and Direct task mapping errors | fixed by `ad7d2680f...` |
| next nonformal witness | guarded triangle scalar name differed | reviewed schema accepted by `4bd4c6b5e...` |
| first formal instrumentation gate | v1 compared separately ranked marginals instead of registered pairs | retained failure; paired authority v2 in `5f1942216...` |
| next instrumentation gate | eight single draws were underpowered for the fixed 5% limit | retained failure; 16 replicates per block/mode in `95f7d4fc1...` |
| `95f7d4fc...` complete formal transaction | old post-import lifecycle gate failed | retained archive `d29c0b79...`; endpoint diagnosis and v2 lifecycle in `70f85796a...` |
| `70f85796...` complete transaction | independent authority confused Direct's native runtime sentinel with Python | retained archive `fde22b987...`; corrected in `8f7b640a3...` |
| `8f7b640a...` complete transaction | relation RTDL/Direct median `1.209372x` exceeded `1.20x` | retained archive `412454f05...`; fused digest validation in `c4351f612...` |
| `c4351f612...` RTX 2000 Ada | first complete single-generation pass | retained archive `f487f4258...`; later source changes prevent pairing it with final source |
| `12ab7b49c...` through `a4dd1d5d...` | prepared triangle control overhead reduced | `a4dd1d5d...` passed Ampere but failed Ada triangle median at `1.249928x`; archive `76e3c1a0...` retained |
| `d653fe4...` | final generic prepared-triangle dispatch/evidence construction reduction | wholly fresh Ada and Ampere transactions both pass |

Two key scientific qualifications follow from this history.

First, thresholds, workloads, arms, timers, estimators, sample counts, and
failure-preservation rules remained fixed across the final repair sequence.
Second, implementation changes were informed by observed outcomes on these
same two tasks and, for the final source, by nonformal RTX 4090 decomposition.
The final result is therefore strong engineering-gate evidence, not an
outcome-blind confirmatory trial or an arbitrary-workload performance theorem.

### 6.4 Final implementation repair

The final `d653fe4` change is limited to generic prepared-triangle Python
control overhead:

- exact immutable replay bypasses repeated generic family redispatch;
- the existing native v9 replay and exact 32-byte query digest are unchanged;
- process, thread, owner, close, and non-reentrancy checks remain;
- native return status and compact status remain synchronous gates;
- the expected reduced U64 oracle remains checked before return;
- one raw native operation receipt is retained per call;
- Python receipt/status expansion occurs only when diagnostics request it;
- replay state is cleared after any `BaseException`; and
- no app vocabulary, physics/database formula, workload, native traversal, or
  result contract was added.

The current unit test explicitly verifies bypass of generic owner redispatch,
deferred receipt identity, process-generation failure, native failure cleanup,
and exact output behavior.

One wording limit is required: successful scalar output relies synchronously on
trusted native status and compact status. The detailed measurement receipt is
validated lazily when inspected. This lazy receipt behavior substantially
predates the final optimization; the final change also defers construction of
its Python wrapper. The paper must not claim that every measurement-only
receipt field is eagerly expanded and validated before ordinary scalar output
is observable.

## 7. Final two-generation evidence

### 7.1 Frozen gates

- public RTDL / Direct median: at most `1.20x`;
- public RTDL / Direct worst block: no registered gate; retain and report every
  block descriptively;
- RTDL / strong PyOptix implementation-entry median: at most `1.20x`;
- RTDL / strong PyOptix implementation-entry worst block: at most `1.35x`;
- strong PyOptix / idiomatic PyOptix steady median: at most `1.05x`;
- successor / predecessor RTDL steady median: at most `1.05x`;
- instrumentation overhead: at most 5%;
- exact correctness for every arm and task;
- zero formal retry and zero formal discard.

Ratios below 1 mean the numerator was faster. A passing overhead gate is not a
speedup claim.

### 7.2 Hardware and custody

| Generation | GPU | UUID | Driver | Archive SHA-256 |
| --- | --- | --- | --- | --- |
| Ada CC 8.9 | GeForce RTX 4090 | `GPU-01a12a86-b470-30ee-c81c-272e3b8fb6d7` | 580.159.04 | `c9128bae15da7ed326c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced` |
| Ampere CC 8.6 | GeForce RTX 3090 | `GPU-eda7acdc-0cc5-6c7f-689f-e8c6831f3b63` | 580.159.03 | `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2` |

Each archive contains 2,405 manifest-bound payload files. Mac-side portable
manifest recount found zero missing, extra, size-mismatched, or digest-
mismatched payloads:

- Ada: 125,718,265 payload bytes; manifest seal
  `8cbd609118b3b2c634a1a3dbec4c10ebd585fc527452083ae6f7ba650222fe06`;
- Ampere: 125,646,793 payload bytes; manifest seal
  `c0ff8626df78ac7039b3182de8e025d7d5ac440e1a135d9cb0235a9dffa7c240`.

Single-generation authorities and independent recounts are byte-identical:

- Ada file SHA-256:
  `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7`;
- Ampere file SHA-256:
  `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3`.

The cross-generation authority and independent rebuild are byte-identical with
file SHA-256
`99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692`
and internal seal
`0ec93d9e529a3ff3dc4a09a178b3c1c5eaf2aa930352777917c8753a7b748d9b`.
It records:

```text
PASS__GOAL5848_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING
cross_machine_raw_time_ratio_computed: false
external_review_complete: false
public_or_manuscript_claim_authorized: false
```

### 7.3 Registered performance results

| Generation | Task | RTDL/Direct median | Observed maximum block, not a registered Direct gate | RTDL/strong entry median | Old post-import diagnostic | Successor/predecessor |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Ada | Triangle | `1.175066x` | `1.211025x` | `0.642180x` | `1.559788x` adverse | `0.903016x` |
| Ada | Relation | `1.076852x` | `1.092253x` | `0.653826x` | `1.749327x` adverse | `0.584438x` |
| Ampere | Triangle | `1.133636x` | `1.142675x` | `0.618362x` | `1.637468x` adverse | `0.922388x` |
| Ampere | Relation | `1.094795x` | `1.118811x` | `0.681393x` | `1.837415x` adverse | `0.608228x` |

Descriptive steady medians, not substitutes for the registered median of
within-block ratios:

| Generation | Task | RTDL | Direct OptiX |
| --- | --- | ---: | ---: |
| Ada | Triangle | 59,811.5 ns | 50,977.0 ns |
| Ada | Relation | 280,976.5 ns | 261,218.5 ns |
| Ampere | Triangle | 60,822.5 ns | 53,613.5 ns |
| Ampere | Relation | 240,213.0 ns | 219,804.0 ns |

Strong PyOptix passed the competence check against idiomatic PyOptix on both
tasks and generations. In the formal estimator, strong/idiomatic medians were:

| Generation | Triangle | Relation |
| --- | ---: | ---: |
| Ada | `0.602851x` | `0.220775x` |
| Ampere | `0.654279x` | `0.226921x` |

### 7.4 Lifecycle interpretation

The primary first-result endpoint begins before implementation-specific
imports. This endpoint was adopted only after a complete retained transaction
showed that the prior post-import comparison began after pinned PyOptix had
already created CUDA state during its excluded import while RTDL remained lazy
and paid CUDA initialization inside its timer.

The corrected endpoint is a valid "from choosing an implementation to first
correct result" measurement, but it includes dependency import and CUDA-context
placement and therefore is not an intrinsic language or compiler speedup. The
old post-import endpoint is intentionally retained and remains adverse by
`1.559788x` to `1.837415x`. Both boundaries must be shown if first-result
performance appears in the paper.

The external reviewer must decide whether this dual-endpoint protocol is
scientifically defensible. The project may not hide the old result, rename the
new ratio as Direct parity, or combine either lifecycle ratio with steady
prepared-execution ratios in one causal statement.

## 8. Strict self-review verification

### 8.1 Current focused suites

Commands used the compatible Python 3.12 environment and disabled bytecode
writes.

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest discover -s tests -p 'goal5848*_test.py'
```

Result: `128/128 PASS` in 11.573 seconds.

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -O \
  -m unittest discover -s tests -p 'goal5848*_test.py'
```

Result: `128/128 PASS` in 11.755 seconds.

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5851_triangle_fused_replay_test
```

Result: `7/7 PASS`.

The prior final-source combined runtime/cross-generation suite passed 147 tests
with three declared environment skips. The two formal archives also retain
their own exact-source Goal5848 test logs.

### 8.2 Full repository discovery is not green

For hostile completeness, this self-review also ran:

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest discover -s tests -p '*_test.py'
```

Result after 165.971 seconds:

```text
Ran 13638 tests
FAILED (failures=756, errors=6214, skipped=600)
```

Dominant observed classes include absent recovered V1-V3
`history/examples_internal` modules, absent historical datasets and
Paper-reproduction trees, platform/GPU/native dependencies, and authorities
that intentionally bind earlier Git objects. This broad result is not evidence
that 6,970 current V4 runtime behaviors are broken, but it is decisive evidence
that the repository cannot advertise an undifferentiated `unittest discover`
as a passing artifact check. A current-source suite, historical-at-bound-commit
suite, platform suite, and optional reproduction suite must be separated.

The discovery run created nine untracked `docs/reports` payloads and one empty
`history/history.db`. This self-review enumerated and removed only those files.
The pre-existing unrelated untracked review file remained untouched.

### 8.3 Expected historical current-tree failures

These commands were rerun and failed exactly as shown:

| Command | Current result | Interpretation |
| --- | --- | --- |
| `python -m unittest tests.goal5838_core_seal_and_selection_test` | 8 pass, 1 error: sealed drift first at `src/rtdsl/v4_family_schema.py` | Goal5838 remains valid at its bound commit; current files changed later |
| `python -m unittest tests.goal5832_protocol_shape_algebra_test` | 22 pass, 1 error: `goal5831.source_authorities[1] byte count drift` | Goal5832 has no valid complete historical Git snapshot; use only its hash-bound terminology/schema scope |
| `python scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored` | `AUTHORITY_CURRENT_INPUT_MISMATCH` | verifier recomputes from changed current inputs rather than the bound historical snapshot |
| `python scripts/goal5843_build_final_authority.py --verify-stored` | preregistration differs from canonical builder | current source differs from the frozen Goal5843 source pins |

The first two are documented in `KNOWN_STALE_CUSTODY_CHECKS.md`; the latter two
are not. None should be resealed. The artifact needs an exact snapshot map and
explicit commands for historical-byte verification versus current-source
regression.

## 9. New or reconfirmed hostile findings

### P0-1: the manuscript and outward-facing evidence summaries are stale

`paper/cgo2027/main.tex` still states, among other old facts:

- two fixed public constructors;
- physical coverage of `2/6` and `2/4` kinds;
- zero prospective frozen-core extension exams;
- the older 324-worker, 7,128-timing RTX 4000 Ada study; and
- an evaluation state that predates the Goal5848/Goal5851 branch.

`paper/cgo2027/README.md` repeats the 324-worker result. The root `README.md`
still says only one bounded-relation AOT path has closed the old debt and that
the portfolio-wide evidence remains the earlier adverse cohort. The final
sprint plan header still says `GOAL5849_COMPLETE__GOAL5850_NEXT` even though
Goal5851 is internally complete.

These are not cosmetic defects. A submission from the current manuscript would
misstate both positive and negative evidence. The paper must be rewritten after
external review accepts a claim ledger. No current performance number should
be inserted before that adjudication.

### P0-2: external review and claim authorization remain absent

Both single-generation authorities and the cross-generation authority encode
`external_review_complete: false` and
`public_or_manuscript_claim_authorized: false`. Internal tests and this report
cannot change those fields. A positive paper-facing Goal5848 sentence requires
external source/evidence review and an explicit post-review adjudication.

### P1-1: the final evidence is outcome-adaptive engineering evidence

The project preserved failures and did not move thresholds, workloads, arms,
timers, estimators, or sample counts to obtain a pass. That is strong practice.
It nevertheless optimized implementation paths after observing results on the
same two tasks, including an RTX 4090 nonformal decomposition before the final
source. The two final formal transactions are fresh and same-source, but they
are not statistically independent of task-directed engineering.

Allowed interpretation: the final implementation satisfies the preregistered
engineering acceptance gates for the exact two tasks on the two GPUs.

Forbidden interpretation: an unbiased estimate of arbitrary RTDL overhead, a
general performance theorem, or evidence that another unseen topology will
have the same overhead.

### P1-2: provider bind/close double-fault cleanup can mask root cause and lose retry ownership

Current source at `src/rtdsl/v4_rtdlexe.py:3078-3092` releases the native image
and readiness lease inside the `bind()` exception handler without protecting
the original exception from a secondary cleanup exception. If release throws,
the later state-clearing block is skipped. Current `close()` at lines
`3096-3121` clears references and marks the object `CLOSED` before release can
fail.

An in-memory fault-injection replay against current source produced:

```text
bind_exception RuntimeError('SECONDARY_RELEASE_FAILURE')
bind_is_original False
state_after_bind BINDING
release_calls_after_bind 1
close_exception RuntimeError('SECONDARY_RELEASE_FAILURE')
state_after_close CLOSED
refs_cleared True
active_lease_retained True
release_phase PROVENANCE_UNREGISTERED
release_calls_after_third_close 2
```

This is a real implementation defect. It is not evidence that any successful
formal sample returned a wrong result, and it is outside the timed prepared
replay. It does refute a broad claim that every asynchronous provider failure
preserves the primary exception and retryable resource ownership.

Because any source repair would create a source identity different from the
two-generation performance evidence, the deadline-aware choice is either:

- explicitly descope the paper's failure-cleanup claim to the tested/supported
  paths and disclose this double-fault limitation; or
- repair before code freeze and accept that the existing two-generation
  performance evidence remains evidence for `d653fe4`, not for the new source.

The external reviewer must decide whether disclosure/descope is sufficient for
the paper's central fail-closed claim.

### P1-3: Goal5840 is a finite structural checker, not general partial evaluation

The Goal5840 checker is implementation-independent in the useful sense that it
is standard-library-only, does not import `rtdsl`, rejects compiler-provided
projections, and independently checks source/ABI/PTX/host-order anchors. Its
frozen 15-mutation, 20-property-application result remains valid at its bound
scope.

However, helper-level hostile mutation inserted an unconditional `return;` at
the beginning of the retained bounded-relation any-hit callback. Both
`_bounded_partial_evaluation_effects` and `_check_wrapper_status_flow` returned
the same accepted effect/status structures as for the original source. The
checker uses bounded source anchors, counts, and relative positions; it does
not prove C++ control-flow reachability, dominance, general numerical semantics,
or binary correctness.

This probe does not constitute a fully resealed authority bypass and does not
invalidate the frozen mutation experiment. It does require the paper to call
Goal5840 an independent finite structural check of specialized target output,
not general partial evaluation or an independent semantic proof.

### P1-4: custody and relocation are strong but not fully portable

Each final archive is complete and manifest-bound, and portable file/worker
recounts pass. The full authority builder also binds absolute pod paths under
`/workspace`. Running the unchanged builder after relocation to the Mac fails
closed. Full authorities were independently rebuilt twice at the original
layout; the Mac independently reconstructed workers and gates, not the exact
absolute-path authority.

The public artifact must either add a derived path-rebasing layer without
rewriting sealed evidence or accurately promise only manifest verification and
portable worker/gate recount after relocation. It must also distinguish current
Goal5848 bytes from older Goal5838/5840 off-Git historical binaries.

### P1-5: no single artifact test command currently represents repository health

Focused current Goal5848/5851 suites are green. Broad discovery is massively
red for mixed historical, missing-file, and environment reasons. Without a
curated test taxonomy and exact expected-failure list, artifact evaluators may
either encounter thousands of failures or be given an overly narrow green
command. The artifact README must define both and must not call expected
historical failures current regressions.

### P2-1: two performance reports contained Direct-gate reporting errors

`goal5850_generation_a_final_report_20260906.md` lists triangle Direct ratios
`1.452162`, `1.394327`, and `1.401147`, all above `1.35`, but says "the two
blocks above 1.35." The correct count is three of eight. That historical gate
was median-only, so the typo does not change its result.

An earlier revision of `goal5851_cross_generation_final_report_20260906.md`
also called `1.35x` a public/Direct worst-block limit. The contract registers
`1.35x` for the implementation-entry RTDL/strong-PyOptix worst block, not for
public RTDL/Direct. Public/Direct has only the `1.20x` median gate. Both reports
were corrected during this self-review with explicit errata; authorities and
raw ratios were not changed.

### P2-2: first Ampere launcher invocation failed before evidence creation

The first final-source Ampere invocation supplied an absolute runbook path but
did not enter the clean checkout. It failed at `validate_exact_git_checkout`
before creating the requested output root, dependencies, workers, or timing
samples. The corrected invocation used a new output root and GNU `env -C`.
This is an operational invocation error, not a formal performance failure, and
must remain disclosed exactly as such.

### P2-3: output receipt validation is partly lazy

Native return status, compact status, bounded capacity relations, and explicit
output oracle are synchronous. Measurement receipt dictionary expansion and
its detailed counter validation are lazy. The evidence workers do materialize
and bind those receipts after timing. General prose must distinguish the
semantic status-before-output gate from post-timer measurement-receipt
validation.

### P2-4: usability and prevalence remain unmeasured

There is no external human authoring record and no positive real-artifact
protocol-defect census. The correct deadline action is to remove ease,
productivity, learnability, and prevalence claims. Creating a rushed user study
or changing the application portfolio would be scientifically weaker than
honest claim deletion.

## 10. Claim ledger for external review

No item in the first table is authorized for publication until external review
accepts it.

### Candidate bounded claims

| Candidate claim | Current internal support | Required wording limit |
| --- | --- | --- |
| RTDL treats a complete callback/host/continuation protocol as an admission and identity unit | Source, tests, bounded target execution | Only supported protocol families/topologies; no arbitrary Callback IR claim |
| Goal5838 extended a frozen admission/identity/lifecycle framework to one selected composition | Bound historical authority | Author-defined ten-row domain, topology-specific post-selection implementation, past tense |
| Goal5840 independently checked specialized target structure | Bound historical authority | Finite structural anchors and frozen mutations; no general semantic/refinement theorem |
| Final public RTDL prepared replay stayed within the registered `1.20x` Direct median limit for two tasks on Ada and Ampere | Final same-source Goal5848/5851 authorities | Exact tasks, endpoints, source, GPUs, estimators, every per-block ratio, absence of a Direct worst-block gate, and the adverse lifecycle diagnostic must be named |
| Strong PyOptix was competent relative to the pinned idiomatic PyOptix arms | Formal competence gates | This does not prove globally optimal PyOptix or Python implementation |
| All failed formal/pre-formal outcomes were retained rather than pooled | Archives and reports | Do not call the final sequence outcome-blind |

### Forbidden or unsupported claims

- RTDL generically lowers arbitrary callback topologies.
- The Goal5838 candidate is an unbiased random new application.
- Goal5840 proves general target semantics or C++ control-flow reachability.
- RTDL is intrinsically faster than Direct OptiX.
- The implementation-entry result is a language-only speedup.
- RTDL has post-import parity with PyOptix.
- The two machines support raw cross-machine speed comparisons.
- RTDL has negligible overhead for all applications or protocols.
- RTDL is easier to use, more productive, or more learnable for humans.
- Whole-protocol composition defects are empirically prevalent in real code.
- Every provider-initialization double fault preserves root cause and resource
  ownership.
- The complete historical repository test suite passes.
- Every historical authority is replayable from the current tree.
- The current artifact is fully relocatable or self-contained.
- Internal self-review or authority generation constitutes external consensus.

## 11. Smallest credible pre-submission action set

1. Obtain strict external review of the exact source, raw authorities, this
   report, and current manuscript; adjudicate every P0/P1 finding in writing.
2. Freeze the claim ledger. Treat the provider double-fault either as an
   explicit bounded limitation or, only if judged central/fatal before freeze,
   repair it while clearly separating old-source performance evidence.
3. Rewrite the manuscript and paper README around the bounded whole-protocol
   contribution, Goal5838/5840 scope, two-generation Goal5848 evidence, adverse
   lifecycle endpoint, and explicit nonclaims.
4. Build an anonymous artifact with exact archives or a documented external
   evidence payload, a relocation-safe verification path, and layered current,
   historical, platform, and optional-reproduction test commands.
5. Run final bibliography, page-count, anonymity, link, PDF-render, and claim-
   authority checks. No new application, usability study, prevalence census,
   or performance tuning should displace these tasks.

## 12. Internal verdict

The compiler contribution remains potentially CGO-worthy if presented as a
bounded whole-protocol architecture whose generic framework is admission,
identity, lifecycle, and verification, while executable lowering is topology-
specific. Goal5848/Goal5851 now remove the prior strongest empirical objection:
the exact verified public prepared paths are within a preregistered, reasonable
overhead envelope relative to Direct OptiX on two GPU generations.

The evidence does not rescue overbroad generality, usability, prevalence,
startup, or universal performance claims. The manuscript and artifact remain
submission blockers. The provider double-fault and Goal5840 checker limitation
must be decided explicitly rather than hidden. Subject to those actions, the
correct verdict is:

`PROCEED_TO_EXTERNAL_REVIEW_AND_CLAIM_FREEZE__DO_NOT_START_NEW_DEVELOPMENT`
