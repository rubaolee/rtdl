# R7 P-Triple-Prime Exact Final-Bytes Review Request

Date: 2026-09-07 America/New_York

Please perform an independent hostile review of the exact P-triple-prime paper
bytes and unchanged F2 evidence artifact below. P-double-prime received the
verdict `REVISE_AND_REREVIEW_CHANGED_BYTES` with one major and six minor
findings. This request concerns changed bytes. The P-double-prime review,
author remediation, local preflight, or review of rebuilt rather than exact
bytes does not count as acceptance of P-triple-prime.

## 1. Exact identities

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Superseded P-double-prime (`REVISE`) | `b28076ad568d3b7b36cfa48b0c5846accff3cb95` | `2a63fecbcf09727dbe4e38f83edb253d80fa3cab` |
| **P-triple-prime under review** | **`c26c88a69382d9786c2f5f77c6cdc6763fc51e7c`** | **`b45bae5d83ec9c803657b28132c677d514897bb3`** |

P-triple-prime's parent is
`5334f0fc5deda053f54dbad12d09f4c43016875c`. Its parent diff is empty
under `src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No executable implementation,
measurement, timer, workload, threshold, or F2 byte changed; no GPU run
occurred.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 146,231 | `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303` |
| `paper/cgo2027/main.pdf` | 146,231 | `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303` |
| `paper/cgo2027/main.tex` | 39,252 | `32c827349fe593f3030803a59d46056458d35c3d8733eb94a20818d57003bc32` |
| `paper/cgo2027/references.bib` | 21,088 | `71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 21,624 | `26e80da4004761203a0e6542dcb9a186690768facaf12eee7400ecc519f2b16a` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The PDF paths are byte-identical. The source bundle is a normalized two-file
custody/buildability aid, not presumed submission material. The nine-member F2
archive supports offline evidence recount only; it does not rerun GPU work,
verify novelty, reconstruct private history, or install a product.

## 3. Required records

Read these records from the candidate or current control directory:

| Record | SHA-256 at P-triple-prime |
| --- | --- |
| `novelty/RELATED_WORK_BOUNDARIES.md` | `739bca412ea29e1ed149566b9f32d30f262bfecfc55ca15bdb8888ed92c3c15d` |
| `novelty/PROTOCOL_WITNESS_AND_DERIVATION.md` | `b8bc76ecbcb3e156bb405c0b46575fb61696a73bb076246b7c37bb8dbe87112e` |
| `novelty/CGO_CONTRIBUTION_ARGUMENT.md` | `9cf76575d7fe69d6e862880fbec43f3be98fcc83ca6f97bd38f49742ff287a99` |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `2ad6f499bf8bd5b6b89b89990f83df95d64364984a8fa6fffffafdd2469b7515` |

Also read `CLAIM_LEDGER.json`,
`R7_PDOUBLEPRIME_LEAD_INDEPENDENT_REVIEW_20260907.md`, and
`R7_PTRIPLEPRIME_REMEDIATION_REPORT.md`. The old review is immutable; the
remediation report contains its P-triple-prime errata. All 24 claim flags must
remain false during review.

## 4. Seven mandatory adjudications

### PDP-01: actual measured implementation

Verify that the manuscript clearly distinguishes general typed-effect/Numba
leaf lowering from the measured exact-standard-IR specializations. Trace both
triangle direct count/reduction and bounded-relation fused intersection/row
emission to source. Confirm that retained and replaced checks and expanded TCB
are accurate. Reject any implication that measured numbers exercise every role
through the general leaf ABI or establish a general optimization theorem.

### PDP-02: warm-up, admission, and use

Verify that exact app-free runtime load/warm may precede route admission, while
the shared decision still gates route acceptance and subsequent per-route
preparation/publication. Confirm mutation wording is limited to the actual
overlap-disabled configuration and tested loader.

### PDP-03: contribution and prior art

Audit the direct comparison to Necula and Lee's proof-carrying code and the
SlangPy capability inventory against primary sources. Decide whether RTDL's
increment is stated as one bounded RT-domain design, one implementation, and
finite evidence rather than validation-before-execution in general, a new
calculus, a soundness proof, or an exclusivity result. Preserve `UNKNOWN` where
the exact joint guarantee was not established.

### PDP-04: interface-specific publication evidence

Verify four distinct paths: materialized `ProtocolExecutionResult`, measured
AOT `RTDLExecutionResult`, post-return worker oracle, and separate detailed
diagnostic. Ensure 4,096 timed calls versus 32 detailed receipts remains
explicit and that no text attributes one interface's digest/receipt checks to
every measured public return.

### PDP-05: prospective challenge semantics

Independently count the frozen challenge table: six counts and four
first-accepted-hit Booleans, seven built-in and three custom, selected sphere
count/continue and eligible unselected curve terminate. Preserve two OptiX
launches and 12/12 oracle rows. `count_relation=query_count` is result
cardinality, not proof that all operations count.

### PDP-06: two unrepaired failures

Confirm that only the double-fault mock returned no public result. Confirm the
native-fork mock accepted a public call through mock native code and executed
no GPU work. Neither should be generalized to all providers, forks, or retained
successful GPU workers.

### PDP-07: SlangPy source identity

Verify v0.43.1 and exact commit
`2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248`, with dynamic stable docs separately
dated 2026-09-07. Check the four relevant capability groups: RT pipeline/hit
groups/dispatch; reflection/marshalling/binding; cache/identity; and device
callbacks/lifecycle. Do not infer an exact joint guarantee from source silence.

## 5. Core hostile-review questions

1. Does the paper provide a real bounded compiler/admission design, or merely
   relabel familiar hashes, schemas, wrappers, and special cases?
2. Is each protocol fact sourced, derived, compared, carried, and checked at a
   concrete boundary? A trusted but internally coherent wrong schema can pass;
   identity equality is not semantic correctness.
3. Are the two stable constructors, four leaf kinds, finite checker, one
   author-defined prospective exam, topology-specific lowerers, about 2,635
   new topology lines, and zero independent-user records disclosed plainly?
4. Are performance values tied only to the exact specialized prepared routes,
   exact GPUs/tasks, and declared timer boundaries? Direct is named, not proved
   optimal; no intrinsic speedup or broad parity claim is allowed.
5. Are all adverse observations visible: post-import A/C up to `2.377129x`,
   first-result regressions/confounding, receipt gap, Arm-A-only instrumentation,
   double-fault, fork mock, checker miss, and artifact scope?
6. Is the illustrative same-width semantic-ABI witness kept distinct from
   executed mutation evidence and the mocked adjacent control?
7. Does every research-value sentence remain supportable without claiming
   first/only, impossibility, arbitrary lowering, semantic inference, formal
   soundness, broad usability, or independent-user evidence?

## 6. Exact byte and format checks

Verify from commit P-triple-prime, not merely the worktree:

- both recorded PDF paths match the exact hash and are byte-identical;
- the PDF is anonymous, eight US-Letter pages in review mode, readable, and has
  no clipping, overlap, missing glyph, unresolved citation/reference, or
  overfull box;
- all fonts are embedded, and scanned private paths, usernames, hosts, keys,
  internal Goal IDs, and author identities are absent from PDF text/metadata;
- the source archive contains only normalized directories plus exact
  `main.tex` and `references.bib`, and builds from a foreign path;
- F2 has nine members and the exact unchanged hash; and
- the executable-path diff from the candidate's parent is empty.

The author-side build, page inspection, source replay, and test results are
evidence to challenge, not independent acceptance.

## 7. Required verdict

Report every finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. End with exactly one verdict:

```text
ACCEPT_PTRIPLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact P-triple-prime commit/tree, PDF SHA-256,
and F2 SHA-256. Two independent acceptances of these exact bytes are required.
This request authorizes no public claim, upload, or submission.
