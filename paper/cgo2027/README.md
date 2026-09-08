# CGO 2027 anonymous manuscript workspace

`main.tex` and `main.pdf` are the current P-septuple-prime manuscript
candidate. The paper presents RTDL as a restricted-Python DSL and compiler for
bounded computations that repurpose ray-tracing hardware. The author selects
the geometric mapping and owns application semantics; for supported fixed
families, RTDL relates declared result obligations to role/effect admission,
typed data and ABI contracts, trusted traversal-action generation, executable
identity, and fail-closed result publication.

The manuscript makes four bounded contribution claims:

1. a restricted-Python programming model for immutable records, typed role
   functions, and manifests;
2. typed Callback IR plus whole-protocol admission;
3. generated Numba leaves, trusted topology wrappers, exact-IR
   specializations, and prepared runtime binding; and
4. V4 application/case-study evidence with explicit source-custody levels.

It does not claim arbitrary Python, arbitrary Callback IR, arbitrary-topology
synthesis, independent-user ease of use, a broad performance win, or that
prior systems cannot implement related guarantees. Whole-protocol/result-route
checking is one compiler contribution inside the DSL story, not the entire
paper theme.

## Current exact candidate

| Object | Exact identity |
| --- | --- |
| Candidate commit | `72d60cb392031134dd3064a8da5cb603bde18e47` |
| Candidate tree | `759cc1246830b785a8d30e98704b51266033194a` |
| Candidate parent | `700b3165ba2a0bca15981aa273c9f02ed9a63992` |
| `main.tex` | 61,234 bytes; SHA-256 `0dd724df5b1d64051e28ce7ee31f09f4e3e5adccf389a0775fa9be7ef36c6076` |
| `references.bib` | 21,640 bytes; SHA-256 `d27ce8c5db0a6855e9879b90a38e98fb07f56ecf993ee4fe2eaddea5b57619f5` |
| Exact PDF | 183,938 bytes; SHA-256 `32189aec5d5ebda4956c83dfe948128bef8dd50e3dbbeb308290988a2acaea07` |
| Source bundle | 29,743 bytes; SHA-256 `e4a291f9e86b125438f2b1c9a5334110a035a36b4a88955267ea319a4e596f6f` |
| Unchanged F2 artifact | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The measured implementation remains M commit
`d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
`d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`. Predecessor E remains
`12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`. Frozen offline tooling F2
remains commit `9771facece4ccd807e26c15b21892b9d0a701d32`, tree
`11c62c28bdebcc7d437f8ab3326635af0832ce48`.

The candidate-parent diff is empty under `src/`, `include/`, `experiments/`,
`scripts/`, `tests/`, and `paper/cgo2027/artifact_post_goal5851/`. No compiler,
runtime, native code, app, workload, timer, estimator, threshold, test, GPU
evidence, or F2 byte changed for P-septuple-prime.

## Evidence boundary

The final M evaluation contains two exact tasks run independently on RTX 4090
Ada and RTX 3090 Ampere. Prepared public RTDL/Direct latency ratios are
`1.077--1.175x`; these are overhead ratios, not intrinsic-language speedups.
The original written per-execution detailed-receipt requirement was not met:
4,096 timed Arm-A calls have 32 separate post-loop diagnostic receipts. All
post-import rows are adverse and reach `2.377129x`; predecessor first-result
comparisons are post hoc and lifecycle-confounded. Instrumentation evidence
qualifies Arm A only.

Historical V4 evidence records nine application mappings and thirteen selected
paper lanes. Current entry points were recovered for all nine; exact historical
per-file custody survives for Particle Tracking, Triangle Counting, and
LibRTS, while the other six retain archive-level audit records only. This does
not establish current runnability for all nine. The separate historical 34-row
V2-direct/V4 authority records 16 row-local median passes, 18 failures, 11
confidence-interval wins, 10 losses, and 13 uncertain rows. It is not a
PyOptiX comparison and is not pooled with final M.

The final application transaction adds selected-stage public-PyOptiX evidence
from three of nine mappings and four operation units on one RTX A4500. All 192
workers, 96 paired blocks, and 12 endpoint evaluations passed exact-output
checks with zero retry/discard, but every endpoint median was adverse to V4,
from `1.080x` to `75.533x`. `complete` starts after shared preprocessing,
`first execute` starts after case preparation, and timed execute includes
validation, digesting, and compact evidence projection. Physical routes also
differ. These data are not raw-domain end to end, broad performance,
productivity, causal-overhead, or unavoidable-language-cost evidence.

The nine-member F2 archive performs offline recount of retained evidence. It
does not rerun GPU work, install RTDL, verify novelty, or reconstruct missing
private history.

## Local validation

| Check | Result |
| --- | --- |
| Cached Tectonic build | PASS |
| Page count and size | 12 pages, 612 x 792 pt US Letter |
| Main-content boundary | Main content ends on page 11; references begin on page 11 |
| Paper/delivery PDF identity | Byte-identical |
| Horizontal/vertical overfull boxes | 0 / 0 |
| Unresolved citations/references | 0 |
| Embedded/subset/Unicode fonts | 12/12 / 12/12 / 12/12 |
| Render inspection | All 12 pages inspected; no clipping, overlap, blank page, missing glyph, or unreadable table |
| Local anonymity scan | PASS for tested private paths and identities |
| Source custody | Twin normalized bundles byte-identical; foreign-path build passed |
| Clean-pod F2 replay | Normal/optimized outputs byte-identical; offline recount PASS |
| Clean-pod application recount | Normal/optimized outputs byte-identical; exact after removing only environment-dependent paths |

BibTeX emits nonfatal completeness warnings for inherited conference records
and the in-press survey. That is not a zero-warning build claim. Independent
bibliography, live-link, content, novelty, and anonymity review remains open.

## Review and submission state

The exact review request is
`history/internal_docs/post_goal5851_submission_remediation_20260906/R7_PSEPTUPLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md`.
The author-side preflight is
`history/internal_docs/post_goal5851_submission_remediation_20260906/R8_PSEPTUPLEPRIME_LOCAL_PREFLIGHT_REPORT.md`.
Detailed current state is in `STATUS.json` and the 29-entry `CLAIM_LEDGER.json`
in the same control directory.

P-septuple-prime has zero of two required independent exact-byte acceptances.
No earlier candidate review transfers. All claim authorization flags remain
false. Authenticated submission-form checks, independent anonymity review,
upload, downloaded-byte verification, and a submission receipt remain open.
No upload or submission has occurred.

The hard executable-code freeze is 2026-09-08 00:00 America/New_York. After
that point, only frozen-tool execution, manuscript/bibliography edits, claim
narrowing, evidence preservation, packaging/replay, review, and submission
checks are permitted.
