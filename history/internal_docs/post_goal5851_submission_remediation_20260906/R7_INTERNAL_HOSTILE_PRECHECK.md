# R7 internal hostile precheck of exact candidate bytes

Date: 2026-09-06

Status: `INTERNAL_PRECHECK_PASS__NOT_AN_INDEPENDENT_R7_REVIEW`

Reviewer: Codex lead execution session. The two passes below use separate
procedures, but they share one authoring/review context and therefore count as
zero of the two independent R7 reviews.

## 1. Bytes under review

| Object | Identity |
| --- | --- |
| P commit/tree | `c6020fd63097b35b5294778cf54c2fb84c879ad6` / `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| PDF | 138,969 bytes / `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| Artifact | 180,308 bytes / `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| Claim ledger | 21 claims / `476b623eecb92bdf30432623b95966c884ee13523ea57b88398f3369ab863006` |

## 2. Pass A: claim, source, and numerical hostility

Method:

- reread the exact PDF text and the claim ledger;
- search every mandatory adverse disclosure and prohibited broad-claim token;
- independently recalculate raw millisecond medians from the eight retained
  worker medians for each primary A/D row;
- compare all main-table ratios with the R2 projection;
- inspect Goal5838/Goal5840 scope wording and package-content wording;
- inspect M-to-P source and executable-tool diffs.

Results:

| Check | Result |
| --- | --- |
| Central claim | bounded whole-protocol admission; no arbitrary Python or generic-lowering claim |
| Topology-specific TCB | explicit in abstract, design, evaluation, related work, threats, and conclusion |
| Prospective exam | selected sphere row exact; curve item only eligible; author-defined domain and zero unbiased new app disclosed |
| Finite checker | five property classes in 20 registered instances and 15 mutations; not 20 applications or a soundness theorem |
| Stable/full-corpus counts | 2 constructors; 2/6 and 2/4 stable presence; 4/6 and 4/4 bounded-corpus presence; not complete support |
| Receipt deviation | 4,096 timed calls versus 32 separate diagnostics explicit in main text |
| Adverse lifecycle floor | all-four A/C adverse, 1.560--1.837 median range, 2.377 maximum, A/E regressions, endpoint revision, and confounds present |
| Primary A/D values | all four medians/maxima match R2 projection |
| Raw-ms spot check | Ada relation A/D 0.2809765/0.2612185; Ada triangle 0.0598115/0.0509770; Ampere relation 0.2402130/0.2198040; Ampere triangle 0.0608225/0.0536135; manuscript rounding matches |
| Artifact prose | nine-member evidence-only package; private provenance/receipts correctly outside package |
| M-to-P production diff | zero bytes under `src/`, `include/`, and `experiments/` |
| Executable whitelist | exactly verifier, exporter, and exporter test named in the R7 request |
| Claim authorization | global false; all 21 entries false; R7 pending |

Pass-A disposition: no new blocking contradiction found. This is an internal
readiness result only. Novelty and sufficiency of the bounded contribution still
require independent judgment.

## 3. Pass B: bytes, portability, format, and anonymity hostility

Method:

- compare the tracked PDF with the delivery PDF byte-for-byte;
- compare the delivery archive with the clean-F2 rehearsal archive;
- inspect PDF metadata and extracted text for local identity, paths, internal
  Goal identifiers, private commits, SSH endpoints, and author repository name;
- inspect all eight exact rendered pages;
- inspect the exact Tectonic and BibTeX logs;
- replay the exact artifact in two new extraction roots, one containing spaces,
  using normal and optimized isolated system Python;
- inspect archive member names, metadata, and forbidden payload tokens.

Results:

| Check | Result |
| --- | --- |
| PDF identity | tracked and delivery bytes identical |
| Artifact identity | delivery and clean-F2 rehearsal bytes identical |
| PDF format | 8 pages, US Letter, anonymous author surface |
| PDF metadata/text scan | no tested private identity, local path, internal Goal token, private commit, or live endpoint |
| Render inspection | all pages 1--8 inspected at 130 dpi; no clipping, overlap, unreadable table, or blank-content defect |
| Build diagnostics | 0 horizontal overfull; 0 undefined citations/references; 0 BibTeX warnings; 0 ACM class warnings |
| Disclosed layout warning | one 1.90399pt end-of-document output-routine overfull vbox; no visible defect |
| Artifact replay | 4/4 exit zero with `PASS__OFFLINE_PROJECTION_RECOUNT` |
| Replay determinism | four JSON outputs byte-identical at `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8` |
| Archive shape | 9 regular files, mode 0444, uid/gid 0, empty owner/group, mtime 0 |
| Forbidden scan | no actual private identity or endpoint; verifier retains only split generic deny-list literals |
| Frozen evidence tests | 14/14 pass |

Two legacy public-document test modules were also executed and failed with 13
missing-file errors plus one 41-link failure. The same signature reproduced at
untouched parent HEAD `63f738f82aaf84ad1be28531f970ff9ca1affe5b`.
Those suites target a historical documentation surface absent from this
restricted repository and are not counted as a candidate pass.

Pass-B disposition: the exact bytes are internally ready for independent
review. The output-routine warning is disclosed rather than hidden. The artifact
supports offline recount only and cannot independently reproduce GPU execution.

## 4. Open gates

| Gate | State | Reason |
| --- | --- | --- |
| R7 reviewer 1 | open | no independent response to exact P/PDF/artifact received |
| R7 reviewer 2 | open | no independent response to exact P/PDF/artifact received |
| R7 finding closure | open | depends on both actual responses |
| R8 final submission gate | open | R7 prerequisite unmet; no upload performed |
| Public/manuscript claim authorization | false | exact-byte independent review incomplete |

Internal conclusion: `READY_TO_REQUEST_R7__DO_NOT_CLAIM_CONSENSUS`.
