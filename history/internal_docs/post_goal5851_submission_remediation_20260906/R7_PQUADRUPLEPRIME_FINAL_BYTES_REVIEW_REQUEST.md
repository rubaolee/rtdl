# R7 P-Quadruple-Prime Exact Final-Bytes Review Request

Date: 2026-09-07 America/New_York

Please perform an independent hostile review of the exact
P-quadruple-prime manuscript bytes and unchanged F2 evidence artifact below.
The review must decide whether the revised paper presents a concrete bounded
compiler contribution rather than novelty-by-vocabulary or a collection of
special cases. P-quadruple-prime changes the paper and contribution argument;
no review of P-triple-prime or any earlier bytes counts as acceptance.

Author analysis, local preflight, this request, and any review of rebuilt
rather than exact bytes do not count as independent acceptance.

## 1. Project and exact identities

RTDL is a restricted-Python compiler/runtime for using ray-tracing hardware on
non-rendering workloads. The current paper does not claim arbitrary Python,
arbitrary Callback IR, automatic topology-generic lowering, semantic
inference, a soundness theorem, independent usability, or intrinsic speedup.
It studies a bounded implementation with trusted family-specific lowering and
exact-program specializations.

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Superseded P-triple-prime | `c26c88a69382d9786c2f5f77c6cdc6763fc51e7c` | `b45bae5d83ec9c803657b28132c677d514897bb3` |
| **P-quadruple-prime under review** | **`70a081e90c4c50ecf92d24741529de9859841c70`** | **`b4b1628345536976e2ed8fbb67ab5b4ff21fc802`** |

P-quadruple-prime's parent is
`b608f9aa5e4e04d083d8a2963d552e00287b47cd`. Its parent diff is empty under
`src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No executable implementation,
measurement, timer, workload, threshold, or F2 byte changed; no GPU run
occurred in this pass.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 153,809 | `bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca` |
| `paper/cgo2027/main.pdf` | 153,809 | `bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca` |
| `paper/cgo2027/main.tex` | 44,586 | `22564330dea504e9f3005ce9cf9185c62306f47dc8e07c1a3bff430dec9d9dbc` |
| `paper/cgo2027/references.bib` | 21,088 | `71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 23,504 | `e845010a64f8373dc40ac65f8cc42e4c4024687ce6fd1eb80b8fd4067a623266` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The PDF paths are byte-identical. The normalized source bundle contains exact
`main.tex` and `references.bib` only, plus directory entries; it is a custody
and buildability aid, not presumed submission material. The nine-member F2
archive performs offline evidence recount only. It does not rerun GPU work,
verify novelty, reconstruct private history, or install a product.

## 3. Contribution under review

The paper's bounded contribution sentence is:

> For supported fixed ray-query families, RTDL implements a result-route
> contract that makes observable output obligations constrain admissible
> callback effects, trusted traversal interpretation, and fail-closed result
> publication, then evaluates those concrete relations, their specialization
> boundary, their extension cost, and their prepared runtime cost.

The paper uses three concrete witnesses:

- **W1:** `ANY_HIT` role typing permits continue, ignore, and terminate, while
  the fixed complete bounded-relation route accepts exactly
  `ACCEPT_CONTINUE` returns.
- **W2:** triangle logical acceptance updates/checks the payload and then
  physically calls `optixIgnoreIntersection()`; native geometry separately
  requests single any-hit delivery.
- **W3:** changing standard count `+1` to `+2` remains front-end legal, changes
  verified IR identity, and exits the fixed count intrinsic for the generic
  leaf path.

Read these exact author records:

| Record | SHA-256 |
| --- | --- |
| `novelty/CONTRIBUTION_CASE_RESPONSE_20260907.md` | `df37d50acef99b699d2ad37837f809a3a712d121a9decd2f2a493f4ede30759f` |
| `novelty/RELATED_WORK_BOUNDARIES.md` | `0b933d85513808f2c62ae51d8d82ae4f8251675cc9a02667ce82d2567b93d1a0` |
| `novelty/PROTOCOL_WITNESS_AND_DERIVATION.md` | `91bb40d890bd2952499109dc519e3b6d7846aa2912d39e66c09dcff925b029fa` |
| `novelty/CGO_CONTRIBUTION_ARGUMENT.md` | `fd0d9b13b82c4238a48ce9bbbd55118187a2457789465c1691b28e5e52543147` |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `d4256e4ae77ff8066a34084d34081f98bcf887e898d80f94724d9b27925f1293` |
| `CLAIM_LEDGER.json` after candidate binding | `f6ab330fe3f5e42a27ee7d304f192504f8eef6483cb9490c7472435cd7c683da` |

All 24 ledger claim flags must remain false during review.

## 4. Mandatory contribution adjudications

### RRC-01: a compiler relation, not renamed bookkeeping

Trace the result-route table and W1--W3 to source. Decide whether the paper
shows a meaningful relation that changes admission or lowering, or merely
renames familiar type, schema, hash, and wrapper checks. Identify precisely
which part is established RT practice, which part is RTDL's organization and
implementation, and which stronger statement lacks evidence.

### RRC-02: W1 accuracy and scope

Verify the role-level any-hit effect set and the bounded-relation requirement
in `src/rtdsl/v4_callback_ir.py` and `src/rtdsl/v4_bounded_relation.py`.
Reject any generalization from the fixed complete route to every enumeration
algorithm. Note that this pass has source evidence and existing bounded checks,
not a new full-front-door terminate/ignore GPU experiment.

### RRC-03: W2 lowering and attribution

Verify both generic and measured exact-count wrapper paths, payload update,
overflow behavior, `optixIgnoreIntersection()`, and native single-delivery
geometry flag. Treat ignore-after-update and single-delivery as established
OptiX techniques, not RTDL inventions. Decide whether explicitly relating them
to the fixed observable result is a defensible system-design contribution.

### RRC-04: W3 specialization boundary

Re-run or inspect
`test_count_intrinsic_requires_the_exact_standard_callback_ir`. Confirm that
`+1` to `+2` remains front-end legal and changes generated path. Do not treat
this component test as GPU equivalence, a general optimization theorem, or a
proof that exact hashes imply semantic preservation. Historical GPU evidence
covers the standard route only.

### RRC-05: direct prior-art boundary

Audit the comparisons to proof-carrying code, Shader Components/Slang, and
typed linking/FFI work. The paper must concede validation-before-execution,
modular specialization/capability checking, and rich cross-boundary relations.
It may claim only the narrower implemented RT result-route relation. Preserve
`UNKNOWN` where the exact joint guarantee was not established; absence of
documentation is not an impossibility result.

### RRC-06: evaluation alignment

Check that RQ1--RQ4 evaluate local legality/result restriction,
specialization invalidation, shared reuse versus topology-specific work, and
exact prepared runtime cost. Ensure W1/W2 source traces and W3 component replay
are not presented as new GPU experiments, and existing measured results remain
bound to exact specialized routes.

### RRC-07: costs and negative evidence

Confirm that the manuscript visibly retains:

- about 2,635 topology-specific implementation lines and 28 compiler-line
  changes for the selected sphere extension;
- 4,096 timed Arm-A calls but only 32 separate detailed receipts;
- all four adverse post-import Arm-A/Arm-C rows, worst block 2.377129x;
- adverse, post-hoc, lifecycle-confounded M/E first-result medians;
- Arm-A-only instrumentation;
- provider double-fault, native-fork mock bypass, and finite-checker miss;
- zero independent-user authoring evidence; and
- offline-recount-only artifact scope.

Reject first/only, impossibility, arbitrary lowering, semantic inference,
formal soundness, broad usability, intrinsic speedup, or universal parity.

The seven corrections inherited from P-triple-prime must also remain intact:
measured specializations, lifecycle/admission boundary, PCC comparison,
interface-specific publication evidence, correct six-count/four-Boolean
challenge semantics, distinct failure outcomes, and exact SlangPy v0.43.1
source identity.

## 5. Exact-byte and format checks

Verify from commit P-quadruple-prime, not only from the worktree:

- both PDF paths match the exact hash and are byte-identical;
- the PDF is anonymous, nine US-Letter pages in review mode, readable, and has
  no clipping, overlap, missing glyph, unresolved citation/reference, or
  overfull box;
- all fonts are embedded and private paths, usernames, hosts, keys, internal
  Goal IDs, and author identities are absent from PDF text/metadata;
- the source archive contains only normalized directories plus exact
  `main.tex` and `references.bib`, and builds from a foreign path;
- F2 has nine members and the exact unchanged hash; and
- the executable-path diff from the candidate's parent is empty.

The author-side build, nine-page visual inspection, source replay, four-test
witness replay, and F2 tests are evidence to challenge, not independent
acceptance.

## 6. Required review output

Report each finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. Explicitly answer:

1. Is the result-route contribution concrete and nontrivial enough for a CGO
   systems/compiler paper under its stated bounded scope?
2. Does any central sentence still exceed source, execution, or prior-art
   evidence?
3. Are costs and negative results prominent enough to prevent a misleading
   performance or generality impression?
4. Is the exact candidate ready for submission-side R8, or must changed bytes
   be generated and rereviewed?

End with exactly one verdict:

```text
ACCEPT_PQUADRUPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact P-quadruple-prime commit/tree, PDF SHA-256,
and F2 SHA-256. Two independent acceptances of these exact bytes are required.
This request authorizes no public claim, upload, or submission.
