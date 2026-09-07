# R7 P-Quintuple-Prime Exact Final-Bytes Review Request

Date: 2026-09-07 America/New_York.

Please perform an independent hostile review of the exact P-quintuple-prime
manuscript bytes and unchanged F2 evidence archive below. This request is
self-contained enough to establish custody and review scope, but reviewers
must inspect the exact candidate rather than accepting author summaries.

P-quintuple-prime changes manuscript bytes after P-quadruple-prime. No review
of P-quadruple-prime or any earlier candidate transfers. Author analysis,
local preflight, rebuilt PDF bytes, and this request count as zero independent
acceptances.

## 1. Project and exact identities

RTDL is a restricted-Python compiler/runtime for using ray-tracing hardware on
non-rendering workloads. The bounded paper asks whether fixed observable
result obligations can constrain callback-effect admission, trusted traversal
interpretation, and fail-closed result publication while retaining
near-direct prepared latency.

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Superseded P-quadruple-prime | `70a081e90c4c50ecf92d24741529de9859841c70` | `b4b1628345536976e2ed8fbb67ab5b4ff21fc802` |
| **P-quintuple-prime under review** | **`41bbec66c6f9f8f770d18075fb9dacbed16d499d`** | **`135f2bc214927acdb305cf2edd2c5ef98690b4a2`** |

The candidate parent is
`8b4475893a7a4486fb89fa35f1ce2470fb2d13f4`. The parent-to-candidate diff is
empty under `src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No executable implementation,
measurement, workload, timer, estimator, threshold, or F2 byte changed. No GPU
ran in this pass.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 154,295 | `34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385` |
| `paper/cgo2027/main.pdf` | 154,295 | `34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385` |
| `paper/cgo2027/main.tex` | 45,064 | `537efb44319297733f8c94717be2769dbea88fdee738d8e7ac7c7e185bb58430` |
| `paper/cgo2027/references.bib` | 21,088 | `71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 23,637 | `f9e70fd7e709eeb611ba740628654379866e638d3534c9ddb94a3b8c0f3ea30a` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The PDF paths are byte-identical. The normalized source bundle contains only
directory entries plus exact `main.tex` and `references.bib`. F2 contains nine
members and performs offline evidence recount only; it does not rerun GPU work,
install the product, verify novelty, or reconstruct private history.

The candidate-commit versions of the author controls are:

| Record | SHA-256 |
| --- | --- |
| `history/internal_docs/lead_three_question_argument_closure_20260907.md` | `12a184249a5667bc33ae10b65f4ef40fa1c4783703cb92c94a5bce5439b0b635` |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `9b2a21a16011224b24be1c34923f7e25f4ae57191949f9b2626c42539a5d7518` |
| `CLAIM_LEDGER.json` | `97d7bc55a668ef0c5fd782a56abb54e0d45a12d964dd5510bf3ea7a4d25da75e` |

All 24 candidate-ledger claim flags are false.

## 3. Central contribution under review

The paper's bounded claim is that, for supported fixed ray-query families,
RTDL implements a result-route contract connecting observable output
obligations to effect admission, trusted traversal interpretation, semantic
and physical representation checks, executable identity, and fail-closed
publication. It does not claim arbitrary Python, arbitrary Callback IR,
automatic application-intent inference, topology-generic synthesis, formal
soundness, intrinsic language speedup, broad usability, or first/only status.

The review must answer the following three questions from the exact paper.

### Q1: What extra does the compiler know?

Check whether the paper clearly and accurately says that explicit, trusted
fixed-family rules encode result obligations beyond local role and machine
typing. Reject wording that implies automatic inference of application intent
or a proof certificate.

### Q2: What does that knowledge reject, generate, or select?

Trace these three decisions to source and evidence:

1. **Reject:** the current complete bounded-relation family accepts only
   `ACCEPT_CONTINUE`, so a locally role-legal terminate/ignore effect is not
   admitted for that route.
2. **Generate:** triangle all-hit logical acceptance updates/checks the payload
   and then physically calls `optixIgnoreIntersection()`, with required single
   any-hit delivery and checked overflow.
3. **Select:** exact standard count `+1` selects a fixed intrinsic; legal
   same-shape `+2` changes IR identity and exits to the general leaf path.

W1 is a fixed-family source rule plus existing bounded checks. W2 uses real
generic/specialized lowering source and inherited standard-route GPU evidence.
W3 is an existing source-to-wrapper component test. None is a new GPU
experiment, arbitrary semantic proof, or theorem about all enumeration.

### Q3: What is the increment over strong prior methods?

Audit whether the paper directly concedes:

- proof-carrying code as validation-before-execution precedent;
- Slang/Shader Components capability checking, interfaces, specialization,
  reflection, and RT support; and
- rich semantic/physical relations in typed linking and FFI work.

Then decide whether the remaining implemented connection from fixed RT result
obligations to effect admission, trusted lowering, and publication checks is a
concrete, nontrivial CGO systems/compiler increment under its bounded scope.
The paper must not rely on different predicate names, source silence,
impossibility claims, or superiority over richer frameworks. It must price the
design in restricted expressiveness and topology-specific trusted code.

## 4. General versus specialized path

Verify the new explicit connection in Section 3.2. For the exact standard
count program, the specialization directly performs the same known increment-
and-continue behavior that the general route obtains through the Numba leaf
ABI and trusted wrapper. The IR guard selects trusted code; it does not prove
semantic equivalence. Recognizer, wrapper, and lowerer remain in the TCB.

Check that measured prepared timings remain bound to exact specialized paths
rather than being represented as generic per-leaf callback execution.

## 5. Attribution and guarantee boundaries

Require the exact manuscript to retain all of these boundaries:

- payload-update-then-ignore and single-any-hit delivery are established OptiX
  techniques, not RTDL inventions;
- complete-relation effect restriction is one fixed route, not a universal
  enumeration law;
- the `+2` test establishes selection-boundary behavior, not GPU equivalence;
- exact hashes establish identity, not semantics;
- exact app-free runtime load/warm may precede route admission;
- topology-specific lowerers and specializations remain trusted;
- the finite checker has a retained early-return miss; and
- the strongest comparison result may remain `UNKNOWN` without implying that
  another system cannot implement the relation.

## 6. Performance and adverse evidence

Verify that the manuscript visibly retains:

- prepared public RTDL/Direct ratios of 1.077--1.175x, without turning them
  into intrinsic-language speedup;
- all four adverse post-import rows and maximum 2.377129x block;
- adverse, post-hoc, lifecycle-confounded M/E first-result medians;
- 4,096 timed Arm-A calls versus 32 separate diagnostic receipts;
- Arm-A-only paired instrumentation;
- about 2,635 topology-specific lines and 28 compiler-line changes for the
  selected sphere extension;
- provider double-fault and native-fork mock limits;
- zero independent-user authoring evidence; and
- offline-recount-only artifact scope.

No positive implementation-entry performance claim is authorized.

## 7. Exact-byte and format checks

Verify from candidate commit `41bbec66c...`, not only from the worktree:

- both PDF paths match the exact hash and are byte-identical;
- the PDF is anonymous, nine US-Letter pages, readable, and free of clipping,
  overlap, missing glyphs, unresolved citations/references, and overfull boxes;
- all fonts are embedded and private paths, usernames, hosts, keys, internal
  Goal IDs, agent names, and author identities are absent;
- the source archive has only exact source files and builds from a foreign path;
- F2 has nine members and the exact unchanged hash; and
- the executable/frozen-tool diff from the candidate parent is empty.

The author-side build, visual inspection, source replay, previous test replay,
and this request are evidence to challenge, not independent acceptance.

## 8. Required review output

Report every finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. Explicitly answer:

1. Can a reader accurately answer the three questions from the paper alone?
2. Is the implemented result-route relation concrete and nontrivial enough for
   a CGO paper under the stated bounded scope?
3. Does any central sentence exceed source, execution, or prior-art evidence?
4. Are trusted-code costs and adverse results prominent enough?
5. Are the exact bytes ready for submission-side R8, or must changed bytes be
   generated and independently rereviewed?

End with exactly one verdict:

```text
ACCEPT_PQUINTUPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact candidate commit/tree, PDF SHA-256, and F2
SHA-256. Two independent acceptances of these exact bytes are required. This
request authorizes no claim, upload, or submission.
