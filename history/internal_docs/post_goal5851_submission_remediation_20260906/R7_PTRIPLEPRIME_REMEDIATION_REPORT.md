# P-Triple-Prime Remediation Execution Report

Date completed: 2026-09-07 America/New_York

Status: `AUTHOR_REMEDIATION_COMPLETE__P_TRIPLE_PRIME_R7_ZERO_OF_TWO`.

This report executes the lead directive for seven findings against the frozen
P-double-prime candidate. It records author-side corrections and local checks;
it is not an independent acceptance, claim authorization, upload, or submission
record.

## 1. Inputs and custody

| Item | Exact identity or state |
| --- | --- |
| Starting HEAD | commit `5334f0fc5deda053f54dbad12d09f4c43016875c`, tree `4281bfcbc1536473d45ec8bf83e7dc259bb73c5d` |
| Preserved P-double-prime | commit `b28076ad568d3b7b36cfa48b0c5846accff3cb95`, tree `2a63fecbcf09727dbe4e38f83edb253d80fa3cab`, PDF SHA-256 `a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84` |
| Lead review | `R7_PDOUBLEPRIME_LEAD_INDEPENDENT_REVIEW_20260907.md`, SHA-256 `8fa631c1c56076ea8fa6ac1a2f4085470cb2d63a63b2da74d4ac39a843ab20b7`, verdict `REVISE_AND_REREVIEW_CHANGED_BYTES` |
| Execution directive | `history/internal_docs/lead_pdoubleprime_remediation_directive_cgo2027_20260907.md`, SHA-256 `d88907fd0484b9bea16b46eaf1ce3ac003ebe68a051594b83ee54d73d9af5ae9` |
| Frozen implementation M | commit `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | commit `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | commit `9771facece4ccd807e26c15b21892b9d0a701d32`, tree `11c62c28bdebcc7d437f8ab3326635af0832ce48`, artifact SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| P-triple-prime candidate | commit `c26c88a69382d9786c2f5f77c6cdc6763fc51e7c`, tree `b45bae5d83ec9c803657b28132c677d514897bb3` |

The candidate commit changed manuscript, bibliography, supporting argument,
control input, and generated paper/source delivery bytes only. Its parent diff
is empty under `src/`, `include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No GPU work occurred and no M/E/F2
bytes changed.

## 2. Seven-finding remediation

| Finding | Author-side result | Exact correction and evidence |
| --- | --- | --- |
| PDP-01 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | The abstract, contributions, Section 3.2, performance methodology, N2, N3, and claims now distinguish the general typed-effect/Numba-leaf diagnostic route from the measured exact-standard-IR triangle intrinsic and relation fused routes. They state which per-leaf checks are replaced, which static/identity/status/capacity/output checks remain, and that these specializations are TCB. Existing measurements are bound to the specialized routes; no new speedup cause, theorem, or general optimizer is claimed. |
| PDP-02 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | Lifecycle text now permits exact app-free runtime load/warm before admission while preserving route acceptance, per-route preparation, and publication gates. The mutation claim is explicitly limited to overlap-disabled runs and to the native-library loader tested there. |
| PDP-03 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | The paper, N1, and N3 directly compare proof-carrying code. They concede policy-based consumer validation as prior art and contrast its supplied proof with RTDL's trusted schemas, compiler projections, topology lowerers, and finite domain-specific evidence. The contribution is organized as one bounded design, one implementation, and finite evidence rather than three new theories. |
| PDP-04 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | The materialized `ProtocolExecutionResult`, measured AOT `RTDLExecutionResult`, post-return worker oracle, and separate post-loop diagnostic receipt are now distinct. The text preserves 4,096 timed A calls versus 32 detailed diagnostics and states that ordinary measured results need not contain a full digest/receipt. |
| PDP-05 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | The ten prospective rows are now described as six counts and four terminate-on-first-accepted-hit Booleans, all with one result per query. Seven built-in/three custom, the selected sphere count/continue item, the eligible unselected curve terminate item, two launches, and 12/12 oracle rows remain explicit. |
| PDP-06 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | The double-fault mock is stated to return no public result. Separately, the native-fork mock accepted a public call through mock native code and performed no GPU work. Neither defect was observed in retained successful GPU workers. |
| PDP-07 | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_R7` | SlangPy identity is fixed to release v0.43.1 and commit `2f6c4625fdd2b3bd812ca6cd2802cf98bd89b248`; dynamic stable docs carry an access date. N1 records four capability groups and leaves the exact joint RTDL-style guarantee `UNKNOWN`. Historical v0.42.0 is retained only as superseded review history. |

The detailed claim/source/page mapping is in
`novelty/MANUSCRIPT_CHANGE_MAP.md`. N1, N2, and N3 are respectively:

| Record | SHA-256 |
| --- | --- |
| `novelty/RELATED_WORK_BOUNDARIES.md` | `739bca412ea29e1ed149566b9f32d30f262bfecfc55ca15bdb8888ed92c3c15d` |
| `novelty/PROTOCOL_WITNESS_AND_DERIVATION.md` | `b8bc76ecbcb3e156bb405c0b46575fb61696a73bb076246b7c37bb8dbe87112e` |
| `novelty/CGO_CONTRIBUTION_ARGUMENT.md` | `9cf76575d7fe69d6e862880fbec43f3be98fcc83ca6f97bd38f49742ff287a99` |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `2ad6f499bf8bd5b6b89b89990f83df95d64364984a8fa6fffffafdd2469b7515` |

## 3. P-double-prime errata

The immutable P-double-prime request and lead review remain preserved. For a
P-triple-prime review, apply these explicit corrections rather than editing the
old records:

| Old P-double-prime statement | P-triple-prime correction |
| --- | --- |
| Measured behavior was described through the general per-leaf path. | Measured triangle and relation routes use exact-IR trusted specializations; the general path remains relevant to diagnostic/general lowering. |
| Admission was summarized as preceding every native DSO load. | Exact app-free runtime load/warm may precede admission; admission gates route acceptance and per-route preparation/use. |
| Public publication checks were summarized as one interface. | Materialized, measured AOT, worker-oracle, and detailed-diagnostic paths have different checks and evidence. |
| All ten prospective rows were called counts. | Six are counts and four are first-accepted-hit Booleans; `count_relation=query_count` describes result cardinality. |
| Neither unrepaired path was said to produce output. | Only the double-fault mock had no public result; the native-fork mock accepted a public call but performed no GPU work. |
| SlangPy stable documentation was bound to v0.42.0. | Version identity is v0.43.1 at the exact commit above; dynamic docs are separately dated. |
| Related work omitted proof-carrying code. | P-triple-prime adds PCC as a direct validation-before-execution precedent and narrows the incremental claim. |

## 4. Exact candidate bytes

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 39,252 | `32c827349fe593f3030803a59d46056458d35c3d8733eb94a20818d57003bc32` |
| `paper/cgo2027/references.bib` | 21,088 | `71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6` |
| `paper/cgo2027/main.pdf` | 146,231 | `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303` |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 146,231 | `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 21,624 | `26e80da4004761203a0e6542dcb9a186690768facaf12eee7400ecc519f2b16a` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The two PDF paths are byte-identical. The normalized source bundle contains
three directory entries plus exact `references.bib` and `main.tex`; two
independent normalized staging bundles were byte-identical.

## 5. Local validation

- Final cached Tectonic build exited zero and produced eight 612-by-792-point
  US-Letter pages.
- Final build log had zero overfull boxes, unresolved citations/references, and
  BibTeX warnings. The earlier missing-pages warning for PCC was corrected by
  adding pages 229--243.
- All eight exact PDF pages were rendered at 130 DPI and inspected. No clipping,
  overlap, blank page, missing glyph, or unreadable table was found.
- Recursive PDF font inspection found 12/12 embedded font objects and 12/12
  ToUnicode mappings. The PDF remains untagged; no PDF/UA claim is made.
- Manuscript, bibliography, PDF text, and PDF metadata passed the tested private
  path, username, host/key, internal Goal-ID, and agent-name scan.
- A foreign-path extraction containing spaces matched both source files and
  built successfully to an eight-page Letter PDF.
- `tests.goal5852_submission_evidence_test` passed 14/14 normally and 14/14
  under optimized Python.
- The F2 archive remains the exact nine-member frozen archive. All 24
  `claim_authorized` fields remain false.

Process errors are retained in `VALIDATION_LOG.md`: early draft builds exposed
overfull boxes that were corrected; an initial `pdftotext` attempt was
unavailable; a first fallback extraction command had a local scripting error;
a naive top-level font scan undercounted descendant fonts before the recursive
check; and one hash command used the wrong artifact path. None changed frozen
evidence or was hidden as a successful check.

## 6. Retained adverse evidence and limits

P-triple-prime retains the 4,096/32 receipt gap, all four adverse post-import
A/C rows (worst block `2.377129x`), post-hoc and lifecycle-confounded A/E
first-result regressions, Arm-A-only instrumentation, provider double-fault,
native-fork mock bypass, finite-checker early-return miss, about 2,635 lines of
topology-specific implementation, zero independent-user authoring evidence,
and offline-recount-only F2 scope. It does not claim arbitrary Python/IR,
topology-generic lowering, semantic inference, proof of soundness, first/only,
impossibility, intrinsic speedup, universal parity, or independent usability.

## 7. Remaining gates

P-double-prime received one independent `REVISE` and zero acceptances.
P-triple-prime changes reviewed bytes and therefore starts at 0/2 independent
acceptances. Two independent hostile reviews must cite the exact P-triple-prime
commit/tree, PDF SHA-256, and unchanged F2 SHA-256. Final independent anonymity,
bibliography/link review, authenticated submission-form checks, upload,
downloaded-byte hash verification, deadline/time-zone verification, and a real
submission receipt remain open.

No public/manuscript claim is authorized, and no upload or submission has
occurred.
