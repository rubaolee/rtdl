# R6 final delivery pair and replay report

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE__PENDING_R7_R8`

This report binds the final manuscript candidate to the exact anonymous
evidence package and records the R6 portability replay. It is not a new GPU
experiment, a full historical-authority reconstruction, an external review,
claim authorization, or a submission receipt.

## 1. Frozen identities and scope

| Role | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Final tooling snapshot F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |

R6 executed only the already frozen F2 verifier and archive plus manuscript,
documentation, packaging, hashing, extraction, and inspection tools. It did
not edit or rerun the measured implementation, GPU workload, timer, estimator,
threshold, raw evidence, or F2 executable tools.

## 2. Exact delivery pair

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 138,969 | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

`cmp` returned exit 0 between the delivery PDF and
`paper/cgo2027/main.pdf`. The tracked manuscript PDF therefore identifies the
same bytes as the delivery PDF.

`cmp` also returned exit 0 between the delivery archive and the archive
produced by the clean F2 rehearsal at:

```text
/tmp/rtdl-cgo2027-F2-9771face-build-a-20260906-173128/
  rtdl-cgo2027-artifact.tar.gz
```

The archive has exactly nine regular files. Every member has mode 0444,
uid/gid zero, empty owner/group names, and mtime zero. The member set is:

```text
rtdl-cgo2027-artifact/CLAIM_SCOPE.md
rtdl-cgo2027-artifact/DEPENDENCIES.md
rtdl-cgo2027-artifact/EXPECTED_RESULTS.md
rtdl-cgo2027-artifact/README.md
rtdl-cgo2027-artifact/REPLAY_MATRIX.md
rtdl-cgo2027-artifact/data/performance_projection.json
rtdl-cgo2027-artifact/data/recount_summary.json
rtdl-cgo2027-artifact/manifest.json
rtdl-cgo2027-artifact/verify.py
```

## 3. Two-root isolated replay

The exact delivery archive was extracted into two newly created roots. The
second path deliberately contains spaces:

```text
/tmp/rtdl-cgo-r6-a.fBH925/rtdl-cgo2027-artifact
/tmp/RTDL CGO R6 b.ZRgGFz/rtdl-cgo2027-artifact
```

From each extracted package, with project `PYTHONPATH` unset and user-site
packages disabled, both commands ran:

```text
PYTHONNOUSERSITE=1 /usr/bin/python3 -I verify.py --artifact-root .
PYTHONNOUSERSITE=1 /usr/bin/python3 -I -O verify.py --artifact-root .
```

All four invocations returned exit 0 and
`PASS__OFFLINE_PROJECTION_RECOUNT`. Their complete JSON outputs were
byte-identical with SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
Each reconstructed:

| Reconstructed population | Count |
| --- | ---: |
| Formal worker cells | 160 |
| Formal steady samples | 20,480 |
| Arm-A instrumentation workers | 1,024 |
| AOT qualifications | 20 |
| Nonformal competence workers | 8 |

Each output also reported:

```text
gpu_execution_performed=false
project_import_performed=false
public_or_manuscript_claim_authorized=false
```

The reconstructed self-seals were identical to the frozen F2 identities:

| Object | Self-seal |
| --- | --- |
| Performance projection | `fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca` |
| Recount summary | `54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105` |
| Public manifest | `4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32` |

## 4. Determinism and anonymous-delivery checks

R5 already proved two clean, repository-external F2 exports byte-identical
and proved that reusing an existing output root fails closed. R6 did not
regenerate or relabel the archive; it copied those exact final F2 bytes and
proved the copy identity before replay.

The R6 member-name and payload scan found no occurrence of the tested local
user path, username, internal `Goal<digits>` identifier, internal-history
path, author GitHub identity, live SSH endpoint, or retained pod IP prefixes.
The scan intentionally excluded `verify.py` from the payload-zero statement:
the verifier contains split byte literals such as
`b"ssh." + b"runpod.io"` as its generic deny-list implementation. This is a
check for forbidden input, not a leaked endpoint. No actual endpoint appears
in the verifier or elsewhere in the archive.

The final PDF has SHA-256
`4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453`,
eight US-Letter pages, anonymous author metadata, zero horizontal overfull
boxes, and no undefined citation or reference. The log contains one 1.90399pt
end-of-document output-routine overfull vbox; every page of these exact bytes
was rendered and visually inspected, with no visible clipping or overlap. The
PDF text and metadata scan found none of the same private identities or
endpoints.

## 5. Claim boundary and remaining gates

The artifact is an anonymous, standard-library offline evidence-recount
package. It is not a product installation, a GPU replay, a distribution of
CUDA/OptiX or measured binaries, or a reconstruction of the original private
pod environment. Its retained values are projections from immutable private
custody evidence, with private and public hashes kept distinct.

R6 is closed for the exact delivery pair above. R7 must still review those
actual PDF and archive bytes and adjudicate every material finding against the
claim ledger. R8 must still perform the final format, anonymity, citation,
hash, upload, and submission-receipt gate. Until both gates pass,
`public_or_manuscript_claim_authorized` remains false and no submission is
recorded.
