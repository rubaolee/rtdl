# R7 Lead-Review Remediation and P-Prime Candidate

Date: 2026-09-06 America/New_York.

Status: `AUTHOR_REMEDIATED__PPRIME_PENDING_TWO_INDEPENDENT_FINAL_BYTE_REVIEWS`.

This report records author-side remediation of the independent lead review of
old snapshot P. It is not an independent review, does not count toward R7, and
does not authorize a public claim, upload, or submission.

## 1. Immutable input and successor identity

| Object | Identity |
| --- | --- |
| Measured implementation M | commit `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor control E | commit `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | commit `9771facece4ccd807e26c15b21892b9d0a701d32`, tree `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Rejected old P | commit `c6020fd63097b35b5294778cf54c2fb84c879ad6`, tree `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| Independent old-P review | `R7_LEAD_INDEPENDENT_FINAL_BYTES_REVIEW.md`, SHA-256 `c449a6c6eed4f177496a762b38f13434a09b1447aa3b3521db56c66b818d5ddd` |
| Old-P verdict | `REVISE_AND_REREVIEW_CHANGED_BYTES` |
| P-prime | commit `818c2ed284cde8acae9a09b531b8bfed3bf925ee`, tree `59e6eaacadac711f8b0d93980b1bfbbd3d772dc7` |

P-prime changes manuscript, PDF, source bundle, and additive control records
only. It changes no byte under `src/`, `include/`, `experiments/`, `scripts/`,
`tests/`, or `paper/cgo2027/artifact_post_goal5851/` relative to its parent.
No GPU experiment was rerun.

## 2. Exact P-prime delivery bytes

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 38,521 | `ef2a5387f8b54ee8b571688ce90f80d22350006e042e7124eb99eb190f97288f` |
| `paper/cgo2027/references.bib` | 19,067 | `7eda90e69e190c3cbd545f86fbf964fa252b75265bc523a1d8dc06c9c9310c66` |
| `paper/cgo2027/main.pdf` | 140,343 | `9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b` |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 140,343 | `9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 20,699 | `1d76d60b1f72487a414ef2fe649415938bc12a3ea6baedd65396b9378b4d90ed` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The two PDF paths are byte-identical. The nine-member artifact is unchanged
from F2 and old P.

## 3. Finding-closure matrix

| Finding | Author-side disposition | P-prime correction and location |
| --- | --- | --- |
| `R7-LEAD-01` major | `REMEDIATED_PENDING_REREVIEW` | Public status, optional caller-supplied expected-output checking, public return/steady timer end, worker validation/first-result end, and separate post-loop diagnostic are distinct in `main.tex:363-416`, Figure 1 on PDF p5, and its `Description`. The unmet condition is named the original preregistered per-execution detailed-receipt requirement. |
| `R7-LEAD-02` major | `REMEDIATED_PENDING_REREVIEW` | Exact implementation-entry, post-import, steady, import-context, A/C-history, and A/E-post-hoc definitions appear at `main.tex:529-551`; Table 6 states the A/E status at `main.tex:594-608` on PDF pp5-7. All adverse values, including 2.377129 in source evidence and 2.377 in the paper, remain. |
| `R7-LEAD-03` minor | `REMOVED_OVERCLAIM_PENDING_REREVIEW` | `main.tex:494-508` now says the checker checks selected lexical patterns and ordering constraints. The finite 3-route-group/4-mode/5-class/20-instance/15-mutation scope and early-return limitation remain. |
| `R7-LEAD-04` major | `REMEDIATED_PENDING_REREVIEW` | `main.tex:186-193` and `main.tex:696-705` state the registered-at-fork condition, native-fork evasion despite later public-API use, primary-exception replacement, lost cleanup retry ownership, focused mock reproduction, no public output, no observation in retained successful GPU workers, and unrepaired status. |
| `R7-LEAD-05` minor | `REMOVED_AMBIGUITY_PENDING_REREVIEW` | Abstract `main.tex:32-42` says implementation, not artifact. `main.tex:484-492` says private custody record. The nine-member package remains separately defined in Section 8. |
| `R7-LEAD-06` minor | `REMOVED_OVERCLAIMS_PENDING_REREVIEW` | D and E are named reference/control arms at `main.tex:518-525`; the cache statement uses prepared public-execution endpoint at `main.tex:577-581`; paired overhead is A-only at `main.tex:613-618`; `main.tex:687-694` denies minimum Direct latency and intrinsic-language-overhead conclusions. |
| `R7-LEAD-07` minor | `ADDITIVE_ERRATUM_RECORDED_PENDING_REREVIEW` | `R7_OLD_P_CONTROL_RECORD_ERRATUM.md` preserves both old records and corrects their A/C versus A/E classifications. P-prime itself makes the distinction at `main.tex:543-551` and in Table 6. |

No table value, measured artifact, authority, M source, or F2 tool changed.

## 4. P-prime author-side validation

- Tectonic returned exit 0. The PDF is eight US-Letter pages; main text ends on
  page 7 and references occupy page 8.
- The final log contains zero overfull boxes, zero unresolved citations or
  references, zero BibTeX warnings, and zero ACM-class warnings.
- All eight exact PDF pages were rendered at 140 DPI and visually inspected.
  No clipping, overlap, missing glyph, unreadable table, or color-only encoding
  was observed. Figure 1 and Table 6 are readable in black and white.
- All 12 listed fonts are embedded and have Unicode mappings. The PDF is not
  tagged, and no PDF/UA claim is made.
- PDF text, metadata, `main.tex`, and `references.bib` contain none of the
  tested private paths, username, pod/SSH endpoint, internal Goal identifier,
  private commit, or author-repository identity.
- Two independently staged, normalized ustar/gzip source bundles were
  byte-identical at `1d76d60b...90ed`. Extraction and Tectonic compilation from
  a foreign path containing spaces returned exit 0 and produced an eight-page
  Letter PDF. The rebuild is a buildability test, not the submission PDF.
- The unchanged artifact was extracted in two fresh roots. Normal and `-O`
  isolated replay passed in both roots; all four outputs were byte-identical at
  `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
- `tests.goal5852_submission_evidence_test` passed 14/14 normally and 14/14
  under `-O` in the pinned Python 3.12 environment.
- P-prime was pushed to `origin/codex/cgo-goal5836-handoff`; the branch was
  zero ahead and zero behind immediately after push.

## 5. Remaining authority boundary

The lead review accepted the bounded numerical observations and artifact
replay but rejected old-P PDF bytes. It cannot approve changed P-prime bytes.
P-prime therefore has zero of two required independent final-byte approvals.
R7 and R8 remain open, every ledger `claim_authorized` flag remains false, no
authenticated submission form has been checked, and no upload or submission
has occurred.
