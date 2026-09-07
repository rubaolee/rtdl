# P-Quintuple-Prime Three-Question Closure Response

Date: 2026-09-07 America/New_York.

Status: `AUTHOR_ARGUMENT_CLOSURE_COMPLETE__EXACT_BYTES_R7_R8_PENDING`.

This record answers the final lead directive in
`history/internal_docs/lead_three_question_argument_closure_20260907.md`.
It binds the response to P-quintuple-prime candidate commit
`41bbec66c6f9f8f770d18075fb9dacbed16d499d`, tree
`135f2bc214927acdb305cf2edd2c5ef98690b4a2`. It is author-side reasoning,
not an independent novelty finding, R7 acceptance, upload authorization, or
submission record.

## 1. Closure decision

The paper now gives accurate and locatable answers to all three lead
questions. The remaining risk is whether independent reviewers judge the
bounded increment important enough for CGO, not whether the manuscript omits
the mechanism or hides its cost. Further wording-only strengthening should
stop. Any later byte change invalidates review of this candidate and starts a
new exact-byte gate.

No compiler, runtime, native source, experiment, workload, frozen artifact,
or numerical result changed in this closure. No GPU ran, and no already-passed
test was rerun.

## 2. The three answers

### Q1: What does the compiler know beyond local callback typing?

For each explicitly supported fixed family, RTDL has an implemented rule for
the route's observable result obligation. The compiler does not infer
application intent. It is told, through trusted family definitions, which
effects preserve the route, which logical effects require which target
actions, which semantic and physical layouts must agree, and which failures
forbid result publication.

Concrete examples are:

- the current complete bounded-relation family permits only
  `ACCEPT_CONTINUE` returns even though the general any-hit role also admits
  ignore and terminate effects;
- triangle all-hit count requires accepted contributions to update the
  payload while the physical intersection is ignored so traversal continues;
  and
- the fixed standard-count intrinsic is available only for the exact known
  callback IR, not every callback with the same role and ABI shape.

This is fixed-family knowledge encoded in trusted rules. It is not automatic
semantic inference, arbitrary Python analysis, or a proof certificate.

### Q2: What decisions does that knowledge change?

The implementation makes three checkable compiler decisions:

| Decision | Result obligation and explicit rule | Compiler action | Evidence boundary |
| --- | --- | --- | --- |
| Reject | Complete bounded relation must not silently publish an incomplete relation; the family accepts only `ACCEPT_CONTINUE`. | Reject a route containing a locally legal but family-incompatible return effect. | Source trace plus existing bounded CPU checks; not a general enumeration theorem or new bad-program GPU run. |
| Generate | Triangle all-hit count must retain a contribution and continue traversal. | Emit/check the payload update, then call `optixIgnoreIntersection()` under the required delivery and overflow contract. | Generic and specialized lowering source plus inherited standard-route GPU evidence; the OptiX technique itself is prior practice. |
| Select | Only the exact known standard count program may use the fixed intrinsic. | Select the intrinsic for exact `+1` IR; changing to legal same-shape `+2` exits to the general leaf path. | Existing source-to-wrapper component test; not GPU equivalence or a general optimization theorem. |

The same table also records a representation decision: admission rejects a
mismatch between the trusted application-ID schema and compiled-contract
projection even when both fields have the same machine width.

### Q3: What is the increment over the strongest acknowledged prior methods?

The paper directly concedes that proof-carrying code established
validation-before-execution, Slang and Shader Components provide substantial
capability checking and specialization, and linking/FFI systems express rich
cross-boundary relations. RTDL does not claim those mechanisms as new and does
not claim that those systems cannot be extended to express the same relation.

The bounded increment is the implemented connection from fixed RT result
obligations to effect admission, trusted traversal lowering, and fail-closed
publication checks in restricted Python. The contribution is not that RTDL
uses different predicate names. Its cost is restricted expressiveness,
explicit family rules, guarded exact-program specializations, and
topology-specific trusted code. The finite evidence evaluates this
implementation and its costs; it does not establish superiority over richer
frameworks or an exhaustive first/only result.

## 3. General path versus measured specialization

The exact standard count specialization and the general Numba leaf route are
two implementations of the same known increment-and-continue behavior:

- the general route returns that behavior through the leaf ABI, after which
  the trusted wrapper checks the effect/status and performs target actions;
- the exact specialization performs the known payload increment and traversal
  continuation directly while retaining applicable static identity,
  overflow, failure, and publication checks.

The exact-IR guard only selects the trusted implementation. It does not prove
semantic equivalence. The recognizer, wrapper, and specialized lowering remain
in the trusted computing base. This explicit bridge closes the largest gap
identified by the final bounded reader check.

## 4. Exact manuscript actions

P-quintuple-prime makes three minimal edits relative to P-quadruple-prime:

1. Table 1 uses concrete reject, generate, and select language for every
   compiler decision.
2. Section 3.2 states the semantic connection and trusted division between
   the general leaf route and exact standard-count specialization.
3. Related Work states the implemented connection, its expressiveness/TCB
   cost, and the absence of a superiority claim.

The detailed mapping is in
`novelty/MANUSCRIPT_CHANGE_MAP.md`. N1, N2, and N3 were not rewritten because
they already contain the relevant primary-source concessions, witness
boundaries, and route comparison. This avoids creating a competing theory or
duplicate evidence record.

## 5. Evidence and claim boundaries preserved

The candidate retains all adverse and limiting observations, including:

- 4,096 timed Arm-A calls but only 32 separate detailed diagnostic receipts;
- all adverse post-import rows, with a maximum 2.377129x block;
- adverse, post-hoc, lifecycle-confounded predecessor first-result medians;
- Arm-A-only paired instrumentation;
- about 2,635 topology-specific lines and 28 compiler-line changes for the
  selected sphere extension;
- a finite checker miss, provider double-fault, and native-fork mock bypass;
- zero independent-user authoring evidence; and
- an artifact that performs offline evidence recount rather than GPU replay or
  product installation.

All 24 ledger entries remain `claim_authorized=false`. No performance number,
denominator, M/E/F2 identity, receipt count, or adverse result changed.

## 6. Exact candidate identity

| Object | Identity |
| --- | --- |
| Candidate commit | `41bbec66c6f9f8f770d18075fb9dacbed16d499d` |
| Candidate tree | `135f2bc214927acdb305cf2edd2c5ef98690b4a2` |
| Candidate parent | `8b4475893a7a4486fb89fa35f1ce2470fb2d13f4` |
| `main.tex` | 45,064 bytes; SHA-256 `537efb44319297733f8c94717be2769dbea88fdee738d8e7ac7c7e185bb58430` |
| Exact PDF | 154,295 bytes; SHA-256 `34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385` |
| Source bundle | 23,637 bytes; SHA-256 `f9e70fd7e709eeb611ba740628654379866e638d3534c9ddb94a3b8c0f3ea30a` |
| Unchanged F2 | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The two PDF paths are byte-identical. The candidate-parent diff is empty under
`src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and the frozen
artifact tool-source root.

## 7. Remaining gate

P-quintuple-prime starts at 0/2 independent exact-byte acceptances. It still
requires independent content and anonymity review, authenticated submission-
form checks, exact upload/download hash comparison, and a real submission
receipt. Until those gates close, claims remain unauthorized and the correct
state is `NOT_SUBMITTED`.
