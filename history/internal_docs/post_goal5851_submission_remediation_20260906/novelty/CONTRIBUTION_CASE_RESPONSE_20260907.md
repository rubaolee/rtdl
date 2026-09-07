# P-Quadruple-Prime Contribution-Case Response

Date: 2026-09-07 America/New_York

Status: `AUTHOR_CASE_COMPLETE__PQUADRUPLEPRIME_R7_ZERO_OF_TWO__CLAIMS_UNAUTHORIZED`.

This response executes the stopping criteria in
`history/internal_docs/lead_cgo_contribution_case_and_three_day_execution_20260907.md`.
It binds the contribution argument to the immutable P-quadruple-prime
candidate. It is an author-side synthesis, not an independent review,
acceptance, claim authorization, upload, or submission record.

## 1. Final contribution sentence

For supported fixed ray-query families, RTDL implements a result-route
contract that makes observable output obligations constrain admissible
callback effects, trusted traversal interpretation, and fail-closed result
publication, then evaluates those concrete relations, their specialization
boundary, their extension cost, and their prepared runtime cost.

The sentence depends on three concrete witnesses:

- W1 establishes that role-local effect legality is insufficient for a fixed
  complete-relation route.
- W2 establishes that a logical effect may require a different physical
  traversal action in the trusted lowerer.
- W3 establishes that a source-semantic change with the same broad callback
  shape invalidates an exact-program specialization.

The claim is bounded. RTDL does not infer arbitrary result semantics, generate
arbitrary topology lowerers, prove semantic preservation, or accept arbitrary
Python or Callback IR.

## 2. Witness evidence and limits

| Witness | Implemented fact | Source identity | Existing/current check | Historical GPU relation | Evidence level and nonclaim |
| --- | --- | --- | --- | --- | --- |
| W1: result obligation restricts effects | `ANY_HIT` is role-valid with `ACCEPT_CONTINUE`, `IGNORE`, or `TERMINATE`; the fixed complete bounded-relation verifier accepts exactly `ACCEPT_CONTINUE` returns and otherwise fails with `any_hit_effect`. | `src/rtdsl/v4_callback_ir.py`; `src/rtdsl/v4_bounded_relation.py`, SHA-256 `4ac50a83ffb80400c6b950150a5702633b3cafa0e43b0b54527f7db44949467a` | Current four-test replay included deterministic bounded-relation generation, fail-closed capacity overflow, and canonical duplicate policy. It did not add a full-front-door terminate rejection test. | The standard relation route in measured M ran true OptiX, but no deliberately invalid terminate/ignore variant was executed on GPU for this pass. | Source trace plus existing bounded checks. This is not a general theorem that all complete enumeration must reject every `IGNORE`, nor a new GPU rejection-rate result. |
| W2: logical accept maps to physical ignore | The triangle all-hit route updates/checks the count payload and then calls `optixIgnoreIntersection()`; native geometry separately requires a single any-hit delivery. | `src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py`, SHA-256 `f7d1f07b4462a6713a4bcda7aaf64f3a480575f1034059f3fbe61d640044eecb`; native M source `src/native/optix/rtdl_optix_v4_callback_poc.cpp`, SHA-256 `4e9c05bdc227c48ccc998b10ec382d84e041a8c268c1dff9ca04d987455045a7` | Current replay exercised deterministic wrapper generation and the exact-standard-count specialization guard. | Frozen M contains the measured triangle route on RTX 4090 Ada and RTX 3090 Ampere. This pass performed no GPU run and did not alter M. | Real lowering source plus inherited GPU execution of the standard route. Ignore-after-update and single-delivery are established OptiX mechanisms, not RTDL inventions; RTDL's increment is their explicit connection to the fixed result route. |
| W3: semantic edit exits specialization | Replacing standard `payload.count + 1` with `payload.count + 2` remains front-end legal, changes verified IR identity, and selects the generic leaf path instead of the fixed count intrinsic. | `tests/goal5759_v4_triangle_reduction_target_test.py`, SHA-256 `3d44b0285afba026333e81abd4f262232db075b5b8150871c9fc14bab767101f`; wrapper generator hash above | `test_count_intrinsic_requires_the_exact_standard_callback_ir` passed in the current 4/4 replay. | Historical GPU evidence covers the standard `+1` route only. The `+2` variant was not run on GPU. | Executed source-to-wrapper component evidence. It checks specialization selection, not GPU equivalence, a general optimizer theorem, or semantic preservation for arbitrary specializations. |

The exact replay command used the committed Python 3.12 environment with
`PYTHONPATH=src:.` and selected one Goal5759 plus three Goal5760 tests. Result:
`Ran 4 tests in 0.017s`, `OK`, exit 0. A test name containing `true_optix`
describes generated structure; it does not mean this replay launched a GPU.

The tested Goal5760 module has SHA-256
`faa1550b98990c771c20b516b808258edc96b5d0de49c9caca6bf5a9dd4b99fd`.
All four source/test files above have zero diff from measured implementation M
`d653fe4ad170c5b51fee309d653c9565944dcf2e`.

## 3. Strongest neighbors and the remaining claim

| Neighbor | What it already covers | RTDL's narrower implemented remainder | Required boundary |
| --- | --- | --- | --- |
| Proof-carrying code | Consumer policy, proof-bearing native binaries, and validation before execution. | A fixed RT output obligation is connected to callback effects, physical traversal interpretation, provider preparation, and publication failures through trusted schemas and lowerers. | RTDL has no proof certificate and no PCC-style semantic guarantee. Validation-before-execution is prior art. |
| Shader Components and Slang | Modular interfaces, specialization, reflection, target/stage/API/hardware capability checking, and rich shader composition. | W1 and W2 expose a different predicate: whether an otherwise role/target-valid callback behavior preserves the fixed route's observable result and how its logical event maps to traversal action. | The predicate distinction does not prove Slang cannot express or be extended with it. The exact joint comparison remains `UNKNOWN`. |
| Typed linking and FFI checking | Cross-language types, layouts, tags, offsets, effects, registration, and rich boundary consistency. | RTDL instantiates a narrower RT-specific relation among event delivery, enumeration/reduction, bounded continuation, traversal wrappers, and publication. | Cross-representation and lifecycle checking are not new paradigms. RTDL does not present a new general linking calculus. |

The defensible research claim is therefore one bounded RT-domain design, one
implementation, and finite evidence. It is not first/only, an impossibility
claim, a general soundness proof, or evidence that neighboring systems lack the
capacity to implement the same relation.

## 4. Manuscript realization

| Contribution obligation | P-quadruple-prime location | PDF pages |
| --- | --- | ---: |
| Problem, bounded result-route design, and contribution | Title, Abstract, Introduction, contribution list | 1--2 |
| Four-row result-route decision table | Section 2.1, Table 1 | 3 |
| W1 result-driven restriction, W2 logical-to-physical lowering, W3 specialization exit | Section 3.2 | 3--4 |
| RQ1 local legality/result restriction | Sections 5 and 5.1 | 5--6 |
| RQ2 exact-program specialization invalidation | Section 5.1 | 5--6 |
| RQ3 shared reuse versus topology-specific implementation cost | Sections 5.2--5.3 | 6 |
| RQ4 exact prepared runtime cost and adverse lifecycle results | Sections 5.4--5.6 | 6--7 |
| PCC, Slang/Shader Components, and FFI/linking comparisons | Section 7 | 7--8 |
| Transfer boundary, limitations, and conclusion | Sections 6, 9, and 10 | 7--9 |

The P-quadruple-prime PDF has nine US-Letter pages. The extra page relative to
P-triple-prime was accepted rather than deleting adverse evidence or shrinking
the ACM format. It remains within the currently checked CGO limit of eleven
content pages excluding references; authenticated submission-form checks are
still open.

Synchronized author-side records:

| Record | SHA-256 |
| --- | --- |
| `novelty/RELATED_WORK_BOUNDARIES.md` | `0b933d85513808f2c62ae51d8d82ae4f8251675cc9a02667ce82d2567b93d1a0` |
| `novelty/PROTOCOL_WITNESS_AND_DERIVATION.md` | `91bb40d890bd2952499109dc519e3b6d7846aa2912d39e66c09dcff925b029fa` |
| `novelty/CGO_CONTRIBUTION_ARGUMENT.md` | `fd0d9b13b82c4238a48ce9bbbd55118187a2457789465c1691b28e5e52543147` |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `d4256e4ae77ff8066a34084d34081f98bcf887e898d80f94724d9b27925f1293` |
| `CLAIM_LEDGER.json` after candidate binding | `f6ab330fe3f5e42a27ee7d304f192504f8eef6483cb9490c7472435cd7c683da` |

All 24 ledger entries remain `claim_authorized=false`.

## 5. Costs, TCB, gaps, and adverse evidence retained

- The sealed shared core does not synthesize arbitrary executable topology
  lowering. The selected sphere extension required about 2,635 lines of
  topology-specific implementation plus 28 compiler-line changes; the result
  is bounded reuse evidence, not automatic backend synthesis or a productivity
  study.
- The TCB includes trusted family schemas, exact-program recognizers,
  topology-specific lowerers and measured-route specializations, native
  provider runtime, driver, GPU, and host. Hash equality is not a semantic
  preservation proof.
- The original preregistered per-execution detailed-receipt requirement remains
  unmet: 4,096 timed Arm-A calls have 32 separate post-loop diagnostic
  receipts. Interface-specific pre-return status/output checks and post-return
  worker oracles are not conflated with those receipts.
- All four post-import Arm-A/Arm-C rows remain adverse, reaching a 2.377129x
  worst block (rounded to 2.377x in the manuscript).
- M-versus-E first-result medians remain post hoc, non-gating, and adverse:
  about 8--22% at implementation entry and 16--31% post-import. Both endpoints
  are lifecycle/import-confounded.
- The paired instrumentation result covers Arm A only.
- The provider double-fault mock returned no public result. The native-fork
  mock accepted a public call through mock native code but performed no GPU
  work. Neither is generalized to every provider/fork or to retained successful
  GPU workers.
- The finite checker missed an early-return probe. The prospective challenge
  is one author-defined table over already supported primitive/topology
  vocabulary. Independent-user authoring evidence remains zero.
- F2 is an offline evidence recount, not a GPU rerun, novelty check, source
  build of M, or product installation.

No performance number, experimental denominator, M/E/F2 identity, receipt
count, executable source, timer, workload, threshold, or GPU result changed in
this pass.

## 6. Immutable candidate and remaining gates

| Object | Exact identity |
| --- | --- |
| P-quadruple-prime commit | `70a081e90c4c50ecf92d24741529de9859841c70` |
| P-quadruple-prime tree | `b4b1628345536976e2ed8fbb67ab5b4ff21fc802` |
| Candidate parent | `b608f9aa5e4e04d083d8a2963d552e00287b47cd` |
| `paper/cgo2027/main.tex` | 44,586 bytes; SHA-256 `22564330dea504e9f3005ce9cf9185c62306f47dc8e07c1a3bff430dec9d9dbc` |
| Both candidate PDF paths | 153,809 bytes; SHA-256 `bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca` |
| Normalized source bundle | 23,504 bytes; SHA-256 `e845010a64f8373dc40ac65f8cc42e4c4024687ce6fd1eb80b8fd4067a623266` |
| Unchanged F2 artifact | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Commit-object extraction reproduced every hash above, and the candidate-parent
diff is empty under `src/`, `include/`, `experiments/`, `scripts/`, `tests/`,
and `paper/cgo2027/artifact_post_goal5851/`.

R7 remains open at 0/2 independent acceptances for these exact changed bytes.
No review of P-triple-prime or an earlier candidate counts. R8 still requires
two independent anonymity/bibliography/link checks, authenticated form and
deadline verification, upload, downloaded-byte hash verification, and a real
submission receipt. No upload or submission has occurred.
