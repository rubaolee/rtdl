# CGO 2027 anonymous manuscript workspace

`main.tex` and `main.pdf` are the current P-triple-prime manuscript candidate. The paper
has been rewritten around bounded whole-protocol admission: shared
schema/identity/lifecycle checks plus topology-specific trusted lowering. It
does not claim arbitrary Python, arbitrary Callback IR, topology-generic
lowering, intrinsic language speedup, broad usability, or a representative
unseen-application study.

The exact candidate PDF is eight US-Letter pages with SHA-256
`2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303`.
Every page of these bytes has been rendered and inspected. The PDF has no
overfull boxes, unresolved references, clipping, or overlap. The exact bytes
passed the current author-side anonymity scan.
This is a final-review candidate, not a submission record or claim
authorization.

## Frozen evidence identities

- Measured implementation M:
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.
- Predecessor E:
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree
  `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6`.
- Final tooling snapshot F2:
  `9771facece4ccd807e26c15b21892b9d0a701d32`, tree
  `11c62c28bdebcc7d437f8ab3326635af0832ce48`.
- Rejected old paper/package snapshot P:
  `c6020fd63097b35b5294778cf54c2fb84c879ad6`, tree
  `dc4b78ba3ec0f7816f87b87fdd74353c806caced`. Its independent lead verdict was
  `REVISE_AND_REREVIEW_CHANGED_BYTES`.
- Superseded P-prime snapshot:
  `818c2ed284cde8acae9a09b531b8bfed3bf925ee`, tree
  `59e6eaacadac711f8b0d93980b1bfbbd3d772dc7`.
- Superseded P-double-prime snapshot (independent `REVISE`):
  `b28076ad568d3b7b36cfa48b0c5846accff3cb95`, tree
  `2a63fecbcf09727dbe4e38f83edb253d80fa3cab`.
- Current P-triple-prime snapshot:
  `c26c88a69382d9786c2f5f77c6cdc6763fc51e7c`, tree
  `b45bae5d83ec9c803657b28132c677d514897bb3`.

Two exact tasks passed the machine numerical contract independently on RTX
4090 Ada and RTX 3090 Ampere. The main performance observation is prepared
public RTDL/Direct; no A/D worst-block gate exists. The original written
per-execution detailed-receipt requirement was not fulfilled: 4,096 timed
Arm-A calls have 32 separate post-loop diagnostic receipts. Synchronous
native/compact status and optional supplied expected-output checks occur before
public return; worker output-and-digest validation occurs afterward. No wrong
output was observed in the retained final GPU samples.

Implementation-entry is not an authorized positive performance claim.
Post-import is adverse on all four rows and reaches `2.377129x`. Relative to
E, first-result medians regress about 8%-22% at entry and 16%-31% post-import;
those rows are post hoc and non-gating. Both first-result endpoints are
lifecycle/import-confounded. The paired ON/OFF instrumentation study measured
Arm A only.

## Artifact state

`artifact_post_goal5851/` is the committed template and verifier-source root,
not an exporter output directory. Final tooling snapshot F2 was recovered
from a clean remote checkout and passed the complete normal/optimized
regression matrix, two byte-identical repository-external exports, existing-
root rejection, and isolated normal plus optimized replay.

The exact anonymous delivery pair is:

| Deliverable | SHA-256 |
| --- | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | `2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The nine-member archive is 180,308 bytes. The P-prime author-side remediation
replayed these exact bytes from two fresh extraction roots, including one with
spaces, in normal and optimized isolated Python. All four outputs were
byte-identical and reconstructed 160
formal cells, 20,480 steady samples, 1,024 Arm-A instrumentation workers, 20
AOT qualifications, and eight competence workers. The package explicitly says
that this is an offline evidence recount, not a GPU rerun or product install.

An additional anonymous source-custody bundle is at
`output/source/rtdl-cgo2027-source.tar.gz`, 21,624 bytes, SHA-256
`26e80da4004761203a0e6542dcb9a186690768facaf12eee7400ecc519f2b16a`.
It contains only exact-P-triple-prime `main.tex` and `references.bib`. Two normalized builds
were byte-identical, and extraction plus Tectonic compilation succeeded from a
foreign path containing spaces. It is not presumed to be a required HotCRP
upload.

Detailed controls are in:

```text
history/internal_docs/post_goal5851_submission_remediation_20260906/
  CLAIM_LEDGER.json
  R2_SUBMISSION_EVIDENCE_REPORT.md
  R3_CONTROL_AND_CUSTODY_CORRECTION_LEDGER.md
  R4_MANUSCRIPT_REWRITE_AND_RENDER_REPORT.md
  R5_FINAL_F2_REHEARSAL_REPORT.md
  R6_FINAL_DELIVERY_PAIR_AND_REPLAY_REPORT.md
  R7_FINAL_BYTES_REVIEW_REQUEST.md
  R7_INTERNAL_HOSTILE_PRECHECK.md
  R7_LEAD_INDEPENDENT_FINAL_BYTES_REVIEW.md
  R7_OLD_P_CONTROL_RECORD_ERRATUM.md
  R7_PPRIME_LEAD_REMEDIATION_REPORT.md
  R7_PPRIME_FINAL_BYTES_REVIEW_REQUEST.md
  R7_PDOUBLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md
  R7_PDOUBLEPRIME_LEAD_INDEPENDENT_REVIEW_20260907.md
  R7_PTRIPLEPRIME_REMEDIATION_REPORT.md
  R7_PTRIPLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md
  R8_LOCAL_PREFLIGHT_REPORT.md
  R8_PPRIME_LOCAL_PREFLIGHT_REPORT.md
  R8_PDOUBLEPRIME_LOCAL_PREFLIGHT_REPORT.md
  R8_PTRIPLEPRIME_LOCAL_PREFLIGHT_REPORT.md
  FREEZE_RECORD.md
  STATUS.json
  novelty/
```

## Remaining gates

Old P received one independent `REVISE` verdict. Its findings were remediated
author-side in P-prime, and P-double-prime then rewrote the novelty and
contribution argument. Independent lead review of P-double-prime returned one
major and six minor findings and no acceptance. P-triple-prime corrects those
seven findings author-side, including measured-path specializations, lifecycle
and interface boundaries, PCC, challenge semantics, failure evidence, and
SlangPy source identity. R7 requires two independent reviews of the exact
P-triple-prime PDF and unchanged F2 archive. No earlier review approves these
changed bytes. R8 still requires final independent anonymity,
bibliography, link, hash, upload, and submission-receipt checks. No upload has
occurred, and `public_or_manuscript_claim_authorized` remains false.

The current R7 request is
`history/internal_docs/post_goal5851_submission_remediation_20260906/R7_PTRIPLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md`.
The P-prime/P-double-prime/P-triple-prime remediation and local preflight are author-side checks, not
independent reviews, and do not close R7.

Local R8 checks for P-triple-prime that do not depend on reviewers or authenticated
submission state have passed. R8 itself remains open because R7, two independent anonymity
scans, HotCRP author/topic/conflict fields, upload, downloaded-byte verification,
and a real submission receipt remain pending.

The hard executable-code freeze is 2026-09-08 00:00 America/New_York. After
that point, only frozen-tool execution, manuscript/bibliography edits, claim
narrowing, evidence preservation, packaging/replay, review, and submission
checks are permitted.
