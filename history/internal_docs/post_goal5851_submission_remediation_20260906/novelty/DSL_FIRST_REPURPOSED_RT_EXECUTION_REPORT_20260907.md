# DSL-First Repurposed-RT Manuscript Execution Report

Date: 2026-09-07 America/New_York.

Status: `AUTHOR_SCOPE_PASS__PSEXTUPLEPRIME_PRECOMMIT_BYTES_FROZEN__EXACT_COMMIT_BINDING_AND_TWO_INDEPENDENT_REVIEWS_PENDING`.

This report records execution of the DSL-first and repurposed-RT problem
directives. It is an author-side manuscript/evidence/control report, not an
independent review, public claim authorization, upload authorization, or
submission receipt.

## 1. Objective and constraints

The paper had to become a compiler paper about RTDL as a restricted-Python DSL
for repurposed ray tracing. Whole-protocol/result-route checking had to remain
one concrete contribution rather than the whole title-level identity. The
rewrite also had to:

- show real supported DSL source early;
- explain the language, typed IR, code generation, runtime, and applications;
- formulate a specific result-obligation compiler problem without claiming
  historical priority;
- compare directly with the strongest prior application abstractions and RT
  language/compiler systems;
- reconstruct the nine historical V4 mappings while exposing source-recovery
  limits;
- keep all historical, final-M, composition, checker, and artifact
  denominators separate; and
- preserve every adverse result, TCB cost, receipt gap, usability gap, and
  submission gate.

No compiler/runtime/native/app code, experiment, test, workload, timer,
estimator, threshold, raw evidence, or F2 byte was allowed to change. No GPU
execution or unchanged test-suite replay was allowed.

## 2. Evidence recovery before writing

The current checkout does not contain the nine historical application files or
the frozen 10.8 MB execution-source archive. The surviving source-index,
responsibility, integration, and independent-recount scripts were therefore
audited instead of pretending the apps were present.

The resulting evidence matrix records:

- exact historical application-source hashes for Particle, triangle counting,
  and LibRTS (`E1`);
- archive-level path and structural audit evidence for RayDB, X-HD, RTNN,
  RT-DBSCAN, Spatial RayJoin, and RT-BarnesHut (`E2`);
- the 8/9 registered-loader result and RayDB private-loader exception;
- author-owned application semantics and RTDL/shared responsibilities for all
  nine mappings; and
- the prohibition on calling E2 rows current runnable examples.

The matrix is
`novelty/DSL_FIRST_APPLICATION_EVIDENCE_MATRIX_20260907.md`.

## 3. Manuscript changes completed

The new manuscript is organized as:

1. Introduction with the repurposed-RT result-obligation problem and four
   compiler contributions.
2. `RTDL by Example and Programming Model`, including an abridged real
   supported all-hit count program and an author/compiler responsibility split.
3. `IR and Whole-Protocol Checking`, including language subset, typed effects,
   fail-closed judgments, semantic/physical ABI, and concrete result-route
   reject/generate/select decisions.
4. `Code Generation and Runtime`, separating generated Numba leaves, trusted
   wrappers, exact-IR specializations, the non-executable canonical plan, and
   lifecycle/identity checks.
5. `V4 Applications and Case Studies`, with all nine mappings, E1/E2 evidence,
   two contrasting mappings, and implementation-scope limits.
6. Evaluation with five RQs and strict separation of source traces, historical
   app evidence, sealed composition, finite target checking, and final-M
   performance.
7. Limitations, related work, artifact, threats, and conclusion.

The title is `RTDL: A Restricted-Python DSL for Repurposed RT`.

## 4. Prior-art and problem-boundary result

The manuscript now treats RTNN, RayJoin, RayDB, RT-DBSCAN, graph triangle
counting, and LibRTS as prior solutions to individual application obligations.
It treats LibRTS as the closest application-facing abstraction, not merely an
app baseline. It also concedes existing capability in OptiX, OSL, PyOptiX, OWL,
Slang/SlangPy, Shader Components, Luisa, CrossRT, Dr.Jit, Scion, TTA/TTA+,
typed linking/FFI, proof-carrying code, and formal GPU verification.

The remaining bounded increment is the implemented connection, for supported
fixed families, from declared result obligations to role-effect admission,
semantic and physical contracts, trusted traversal-action generation,
executable identity, and interface-specific failure checks. The paper does not
claim that RTDL first identified the broad problem, that rendering lacks
protocols, or that an adjacent system cannot implement similar checks.

The Scion citation was corrected to its final PLDI 2026 title and 39-page
record. TTA/TTA+ is cited with its MICRO 2024 DOI.

## 5. Evidence and performance boundaries retained

The paper reports the historical RTX 4000 Ada evidence only as the complete
mixed result: 464 exact behaviorally true-OptiX workers, 34 rows, 16 median
passes, 18 failures, 11 clear V4 wins, 10 clear losses, and 13 uncertain. The
raw archive is absent, this population was not rerun, it is not a PyOptiX
comparison, and it is not pooled with final M.

Final M remains exactly two specialized tasks across RTX 4090 Ada and RTX 3090
Ampere. Prepared public RTDL/Direct medians remain `1.077--1.175x`.
Post-import RTDL/strong-PyOptiX medians remain adverse at `1.560--1.837x` with
a `2.377x` worst block. The paper explicitly retains:

- lifecycle confounding and post-hoc M/E first-result regressions;
- 4,096 timed A calls versus 32 separate diagnostic receipts;
- A-only paired instrumentation qualification;
- the selected sphere route's approximately 2,635 topology-specific lines and
  28 compiler-line changes;
- the finite checker's missed early-return probe;
- provider double-fault and native-fork mock limitations;
- zero independent-user authoring evidence; and
- offline-recount-only artifact scope.

## 6. Exact pre-commit bytes

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 60,755 | `a339ace8ec2f071cd85c2416e9f67b5d76ae533d43a41a96dbfa2f6647be7de0` |
| `paper/cgo2027/references.bib` | 21,953 | `bb0b71ae0fec49492888fbc9252ed412897cb2d4d7f1e33008f902cdb3b74e61` |
| `paper/cgo2027/main.pdf` | 182,617 | `a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0` |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 182,617 | `a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 29,176 | `a49ea4aedc2b96084eefddf2ee987e20e968b59416c678caa30c5ab0c4606afa` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

## 7. Author-side QA

The exact PDF passed:

- cached Tectonic compilation, exit zero;
- 12 pages at 612 x 792 pt US Letter;
- main content ending on page 11, with references beginning on page 11;
- zero horizontal and vertical overfull boxes;
- zero undefined citations or references;
- 12/12 fonts embedded, subset, and Unicode mapped;
- byte identity between both PDF delivery paths;
- full visual inspection of all 12 rendered pages, with no clipping, overlap,
  blank page, missing glyph, or unreadable table;
- extracted-text scan with no tested private path, username, host, key, internal
  Goal ID, agent name, or author identity.

Two independently staged normalized ustar source archives were byte-identical.
The official bundle contains only normalized directory entries plus exact
`main.tex` and `references.bib`. Extraction to a fresh path containing spaces
preserved both source hashes and compiled to a 12-page Letter PDF.

BibTeX emits nonfatal completeness warnings for several inherited proceedings
records and the in-press survey. No citation is unresolved and every rendered
reference was visually inspected. This remains an item for independent
bibliography review, not a hidden clean-build claim.

## 8. Hostile self-review verdict

The rewrite materially improves the CGO contribution case because a reader can
now see a language, a real program, typed IR, concrete compiler decisions,
target generation, runtime binding, and applications before reaching the
evaluation. The broad research problem is supported by prior application
evidence rather than claimed as a first discovery.

The largest remaining risks are deliberately visible:

1. Six of nine historical application sources are not recoverable from the
   current evidence set.
2. The stable public facade has only two constructors, and topology-specific
   trusted code remains substantial.
3. The measured performance covers two exact specializations, not the general
   Numba-leaf path or all nine apps.
4. First-result performance is adverse and lifecycle-confounded.
5. There is no independent-user authoring or usability study.
6. Novelty relative to extensible adjacent systems remains an external-review
   judgment, not something source silence can close.

Author-side verdict:
`PASS_FOR_EXACT_CANDIDATE_BINDING_AND_INDEPENDENT_R7__NOT_AUTHORIZED_FOR_UPLOAD_OR_SUBMISSION`.

## 9. Remaining gates

- Create the immutable P-sextuple-prime candidate commit and bind its exact
  commit/tree in post-candidate controls.
- Issue a self-contained R7 request over those exact bytes.
- Obtain two independent acceptances of the exact candidate PDF and unchanged
  F2 artifact; earlier reviews do not transfer.
- Perform authenticated submission-form, category, author, topic, conflict,
  deadline, anonymity, upload-hash, and receipt checks.
- Do not upload or submit without explicit user authorization.

The claim ledger contains 28 claims and zero authorized flags.
