# R8 P-Septuple-Prime Author-Side Local Preflight

Date: 2026-09-08 America/New_York.

Status: `AUTHOR_LOCAL_PREFLIGHT_PASSED__R7_AND_EXTERNAL_SUBMISSION_ACTIONS_PENDING`.

This report records author-side checks of exact P-septuple-prime. It is not an
independent content, novelty, bibliography, anonymity, or final-byte review;
upload authorization; public-claim authorization; or a submission receipt.
R7 remains 0/2.

## 1. Exact object under preflight

| Object | Exact identity |
| --- | --- |
| Candidate commit | `72d60cb392031134dd3064a8da5cb603bde18e47` |
| Candidate tree | `759cc1246830b785a8d30e98704b51266033194a` |
| Candidate parent | `700b3165ba2a0bca15981aa273c9f02ed9a63992` |
| `main.tex` | 61,234 bytes; SHA-256 `0dd724df5b1d64051e28ce7ee31f09f4e3e5adccf389a0775fa9be7ef36c6076` |
| `references.bib` | 21,640 bytes; SHA-256 `d27ce8c5db0a6855e9879b90a38e98fb07f56ecf993ee4fe2eaddea5b57619f5` |
| Exact PDF | 183,938 bytes; SHA-256 `32189aec5d5ebda4956c83dfe948128bef8dd50e3dbbeb308290988a2acaea07` |
| Source bundle | 29,743 bytes; SHA-256 `e4a291f9e86b125438f2b1c9a5334110a035a36b4a88955267ea319a4e596f6f` |
| Unchanged F2 | 180,308 bytes; SHA-256 `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Commit-object extraction reproduces every manuscript, source, delivery, and F2
identity. Both PDF paths are the same Git blob. The remote branch resolves to
the exact candidate commit. The parent-to-candidate diff changes exactly five
paper/delivery files and is empty for executable, experiment, test, raw
evidence, and F2 roots.

## 2. Manuscript and PDF checks

| Check | Result |
| --- | --- |
| Clean cached Tectonic build | PASS, exit 0 |
| Page count and size | 12 pages, 612 x 792 pt US Letter |
| Official text-page limit | Main text ends on page 11; references start on page 11 |
| Paper/delivery PDF identity | Byte-identical |
| Horizontal/vertical overfull boxes | 0 / 0 |
| Unresolved citations/references | 0 |
| Missing/duplicate BibTeX keys | 0 / 0 |
| Embedded/subset/Unicode fonts | 12/12 / 12/12 / 12/12 |
| Visual rendering | All 12 exact pages rendered and inspected |
| Visual defects | 0 clipping, overlap, blank page, missing glyph, or unreadable table |
| Review layout | `sigplan,screen,review,anonymous`, US Letter, page/line numbers |

The extracted text scan found no tested private filesystem path, local
username, pod/SSH host, key name, internal Goal ID, agent name, or author
identity. The two expected `Anonymous Author(s)` occurrences remain. This
author-side scan does not replace independent anonymity review.

BibTeX emits nonfatal inherited completeness warnings and Tectonic emits
font-request/underfull diagnostics. There are no unresolved citations or
references and no overfull boxes. This report does not claim a warning-free
build.

## 3. Source custody and buildability

Two independently staged normalized ustar archives used fixed zero
owner/group, read-only file modes, read/execute directory modes, 2000-01-01
timestamps, and `gzip -n`. They were byte-identical at the official source
bundle hash.

Extraction into a fresh foreign path containing spaces preserved both source
hashes and compiled successfully with cached Tectonic to a 12-page Letter PDF.
This establishes source custody and local buildability, not cross-environment
byte-for-byte PDF reproducibility.

## 4. Application evidence audit

The final application source is commit
`c5c8be48b743aa001e9c16c3344cc97c200600d1`, tree
`e3bb0001f4c2d1e3171ab0431c0479500dfc7136`. Direct recomputation from its
formal summary recovered 192 workers, 96 registered pairs, 12 evaluations,
zero retry/discard, and 96/96 individual paired block ratios greater than one.
Every paper table median and range was checked against the final JSON before
candidate creation.

The formal summary, independent recount, and archive hashes are respectively
`67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf`,
`667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64`,
and `2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff`.

The paper explicitly limits the study to selected stages from 3/9 mappings
and four operation units. It identifies `complete` as post-preprocessing,
`first execute` as post-preparation, and `prepared` as including one untimed
warmup. It discloses the Particle, triangle lifecycle, and LibRTS layout/kernel
differences and makes no speedup, end-to-end parity, productivity, or causal
overhead claim.

## 5. Clean-pod frozen replay

A fresh clone of exact candidate `72d60cb...` was made on the retained RTX
A4500 host used by the final application transaction. The replay did not
execute a GPU experiment.

The pod independently verified the candidate commit/tree and all four exact
delivery hashes. It extracted the source archive and reproduced both source
hashes. It then ran the unchanged nine-member F2 verifier from two independent
directories under normal and optimized Python. The outputs were byte-identical
at SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`
and reported `PASS__OFFLINE_PROJECTION_RECOUNT`, 20,480 formal steady samples,
160 formal workers, 1,024 instrumentation workers, 20 AOT observations, and
eight competence workers.

The pod also extracted the frozen application archive and ran the committed
recount tool under normal and optimized Python. Both outputs were byte-identical
at SHA-256
`63388474457a4e234f6915186aa364176ef80dd418936cf4c3e2c09cdc614fc8`.
After removing only environment-dependent absolute `formal_summary_path` and
worker `path` fields, the new recount was exactly equal to the retained recount:
192 worker files, 96 pairs, 12 evaluations, all 96 ratios adverse, and zero
retry/discard.

One diagnostic comparison initially removed only the formal-summary path and
correctly failed because worker absolute paths also differ after extraction.
A later print statement used the wrong ratio nesting and raised after the
equality assertions had passed. Both were author-side script invocations, not
changes to the verifier or evidence, and are not counted as successful evidence
steps. The corrected fail-closed comparison is the result recorded above.

## 6. Claim and executable scope

P-septuple-prime adds manuscript presentation of already frozen application
evidence. It does not change measured source M, final application source,
predecessor E, F2, raw evidence, callback/compiler/runtime/native code,
workloads, timers, estimators, thresholds, or tests.

All public/manuscript authorization flags remain false. The application rows
are retained adverse evidence, not a positive performance claim. The two-task
prepared RTDL/Direct observations remain bounded overhead ratios; the receipt,
instrumentation, lifecycle, TCB, custody, usability, and coverage limitations
remain visible.

## 7. Remaining R8 gate

The following remain open:

- two independent R7 acceptances of the exact P-septuple-prime PDF and
  unchanged F2;
- independent content, novelty, anonymity, bibliography, and live-link review;
- authenticated submission-form, category, author, topic, conflict, deadline,
  and time-zone verification;
- explicit user authorization for upload;
- downloaded-upload byte/hash comparison; and
- a real submission ID and receipt.

The correct state is `NOT_SUBMITTED`. No earlier candidate review transfers,
no claim is authorized, and this report does not permit upload.
