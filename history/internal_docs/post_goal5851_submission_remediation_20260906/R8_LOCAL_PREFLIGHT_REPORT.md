# R8 local submission preflight report

Date: 2026-09-06

Status: `LOCAL_PREFLIGHT_COMPLETE__R7_AND_EXTERNAL_ACTIONS_PENDING`

This report executes every R8 check currently possible without two independent
R7 responses, an authenticated submission-form session, author/conflict data,
or upload authorization. It does not close R7, count as either independent
anonymity scan, authorize claims, or record a submission.

## 1. Candidate identities

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| Snapshot P commit/tree | n/a | `c6020fd63097b35b5294778cf54c2fb84c879ad6` / `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| Submission PDF | 138,969 | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| Evidence artifact | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| Anonymous source bundle | 20,108 | `159df8db4fd4ae801f3c7f71a012259023c255dcd3a7a866805cfe310c4f95f2` |

The PDF and artifact are the exact P delivery bytes. The source bundle was
generated afterward from P's exact `main.tex` and `references.bib`; it does not
change either reviewed delivery object.

## 2. Official-rule check

The official CGO 2027 Main Conference page was reread on 2026-09-06:
`https://2027.cgo.org/track/cgo-2027-papers`. The public HotCRP landing page was
also reached at `https://cgo27.hotcrp.com/` without an authenticated submission
session.

| Rule | Candidate check |
| --- | --- |
| Category | Standard research paper remains intentional; title has no Tool/Practical prefix |
| Deadline | R2 paper submission is 2026-09-10 AoE; project still targets earlier daytime completion |
| Length | Main text ends on PDF page 7 before references; limit is 11 text pages excluding references |
| Template | `\documentclass[sigplan,screen,review,anonymous]{acmart}` |
| Paper size | PDF reports 612 x 792 pt, US Letter |
| Review aids | page numbers and line numbers are visible in rendered pages |
| Language | paper is written in English |
| Appendix | no appendix exists in the main PDF |
| Supplement | evidence artifact is separate; no supplement is embedded in the main PDF |
| Double blind | anonymous author surface; no acknowledgements section; self-citations are not omitted |
| Black-and-white | no result depends on color; tables and the architecture figure remain readable in grayscale |
| PDF | exact deliverable is PDF 1.5 and unencrypted |

The official initial-paper form requires the PDF. Supplementary material is
optional and separately uploaded; accepted-paper artifact evaluation is a
separate process for a standard research paper. The source bundle is retained
for custody and rebuild, not presumed to be a required HotCRP upload.

## 3. Exact PDF checks

| Check | Result |
| --- | --- |
| Tracked/delivery byte identity | `cmp` exit 0 |
| Total pages | 8 |
| Main-text boundary | conclusion ends and references begin on page 7 |
| Page size | US Letter |
| Horizontal overfull | 0 |
| Undefined citations/references | 0 |
| BibTeX warnings | 0 |
| ACM class warnings | 0 |
| Embedded fonts | 12/12 font entries report `emb=yes` |
| Render inspection | all exact pages 1--8 inspected at 130 dpi; no clipping, overlap, unreadable table, or blank-content defect |
| Metadata/text anonymity scan | no tested username, local path, internal Goal identifier, private commit, live endpoint, or author repository identity |

The log contains one 1.90399pt end-of-document output-routine overfull vbox.
It is not horizontal text overflow and has no visible rendered defect. This
warning remains disclosed rather than suppressed by changing margins or font
size.

PDF metadata contains the anonymous title, TeX creator/producer, and creation
date. It contains no person-valued author field or local source path. macOS
indexes the TeX creator string in its author metadata slot; this is not an
author identity, but the independent R7 anonymity reviewers must check it
themselves.

## 4. Anonymous source bundle

Path: `output/source/rtdl-cgo2027-source.tar.gz`.

The bundle contains only:

```text
rtdl-cgo2027-source/paper/cgo2027/main.tex
rtdl-cgo2027-source/paper/cgo2027/references.bib
```

Directories are mode 0755; regular files are mode 0644; uid/gid and owner/group
are normalized to zero/empty; mtimes are fixed at 2000-01-01. The ustar stream
has no Git commit header. Two separately staged and normalized builds were
byte-identical at SHA-256
`159df8db4fd4ae801f3c7f71a012259023c255dcd3a7a866805cfe310c4f95f2`.

The archive was extracted under:

```text
/tmp/RTDL CGO source replay 20260906/
```

Both extracted sources were byte-identical to P. Running the frozen local
Tectonic executable from the extracted source returned exit 0 and generated an
eight-page US-Letter PDF with the same zero-horizontal-overfull,
zero-undefined-reference, zero-BibTeX-warning profile and the same disclosed
1.90399pt output-routine vbox. The rebuilt PDF differs by two bytes in size and
has a different SHA-256 because PDF generation metadata is time-dependent; it
is a buildability check, not a replacement for the exact submission PDF.

An extracted-source scan found no tested local username/path, internal Goal
identifier, private commit, live endpoint, or author repository identity.
Legitimate third-party GitHub URLs in the bibliography remain, as required for
complete citations.

## 5. Artifact checks inherited from exact R6 bytes

The evidence archive is unchanged from F2 and P. It remains byte-identical to
the clean-F2 rehearsal archive and passed four isolated replays from two roots,
normal and optimized. All four outputs were byte-identical at SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
It performs no GPU execution or project import and authorizes no claim.

## 6. Pending external/user-owned checks

| Requirement | State | Needed action |
| --- | --- | --- |
| Independent final-byte review 1 | open | reviewer must inspect/replay exact P PDF and artifact |
| Independent final-byte review 2 | open | second reviewer must independently inspect/replay exact P PDF and artifact |
| Two independent anonymity scans | open | record both reviewers' actual results |
| Finding dispositions | open | close or descope every material finding |
| Authenticated HotCRP fields | open | user supplies author, affiliation, topic, and conflict data in submission session |
| Exact upload | not executed | upload only after R7 and explicit authorization |
| Downloaded-byte verification | not executed | if HotCRP permits download, compare returned PDF hash |
| Submission receipt | absent | retain only after actual submission |

Local R8 conclusion:

```text
LOCAL_PREFLIGHT_PASS
R7_COMPLETE=false
INDEPENDENT_ANONYMITY_SCANS=0/2
UPLOAD_EXECUTED=false
SUBMISSION_RECEIPT_PRESENT=false
PUBLIC_OR_MANUSCRIPT_CLAIM_AUTHORIZED=false
```

The accurate overall state is
`FINAL_CANDIDATE_READY__R7_AND_UPLOAD_PENDING__NOT_SUBMITTED`.
