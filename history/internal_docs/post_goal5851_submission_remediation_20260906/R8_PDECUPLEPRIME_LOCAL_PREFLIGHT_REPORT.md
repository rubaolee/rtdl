# R8 P-Decuple-Prime Author-Side Local and Clean-Pod Preflight

Date: 2026-09-08 America/New_York.

Status:
`AUTHOR_PREFLIGHT_PASSED__R7_AND_AUTHENTICATED_SUBMISSION_ACTIONS_PENDING`.

This is an author-side preflight of exact P-decuple-prime. It is not an
independent content, novelty, bibliography, anonymity, or final-byte review;
public-claim authorization; upload authorization; or a submission receipt. R7
remains 0/2. No GPU experiment was run in this preflight.

## 1. Exact object under preflight

| Object | Exact identity |
| --- | --- |
| Candidate commit | `8a485a6aae353e0d1dbfee7ce5a96610cee5d31d` |
| Candidate tree | `b59d795819f489d4e53f34f264eb46d31f1ec45f` |
| Source-package assembly | commit `c0c23e20ee325fb246c769ba1920566474d869c6`; tree `c25914560f096175630f89453e33bcd42019992e` |
| Manuscript/evidence parent | commit `ed4df9330a3c47c116912cb5a817fd7a84dccdfe`; tree `d4bede2eea645716fe6749de479b69c9413da2bc` |
| Long-workload successor | commit `02e84374fc092d2bb916cca633eda9592b4ecf07`; tree `8aad15d686bbc9e1c3b11df998898a0a063a01f1` |
| Superseded P-nonuple-prime | commit `d20a0eb322c13ad17b591007116f8da616a5e60e`; tree `cec8fb10374943b757d205cb82daf04e4e768bba` |

The candidate differs from its source-package assembly commit only in
`paper/cgo2027/README.md`; submission bytes are unchanged. The assembly commit
differs from the manuscript/evidence parent only in
`output/source/rtdl-cgo2027-source.tar.gz`. That source bundle was built from
the exact parent-commit Git blobs. A pre-existing local OptiX-reference URL
edit and a whitespace-only native-source worktree change were not staged and
are absent from the candidate.

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 57,947 | `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `paper/cgo2027/references.bib` | 22,538 | `0bd5a31016fc847ef2ac52b45185533e16f0a23e439b83919d1794b9143da948` |
| both PDF paths | 254,212 | `3f4ec710fa54248dcd8dde0116920d94e75a00ce0424d7b8cf60b8f3e67202e3` |
| `paper/cgo2027/figures/reviewed_design_figures.pdf` | 62,908 | `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| `paper/cgo2027/figures/successor_application_performance.pdf` | 27,603 | `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 106,838 | `8015a14bdb6af036d45f1500152637a0a5c5f29f56018dc01324992dea240108` |
| unchanged F2 artifact | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| application projection | 84,598 | `d761ce92f55561be656a71712a9f0a78c57f2c7f8165d2ee8d8cb8cf60309e6f` |
| long-workload private raw archive | 730,851 | `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| CPU-sensitivity raw archive | 877,815 | `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |

Commit-object extraction and the clean-Pod checkout reproduced every identity.
The two PDF paths are byte-identical.

## 2. Manuscript and PDF checks

The exact committed source was compiled in an isolated canonical directory
containing only its canonical bibliography and the two referenced figure PDFs.

| Check | Result |
| --- | --- |
| Tectonic build | PASS, exit 0 |
| Page count and size | 13 pages, 612 x 792 pt US Letter |
| Official text-page boundary | Main text ends on page 11; references begin on page 12 |
| Horizontal overfull boxes | 0 |
| Vertical overfull boxes | One final-output `1.87198pt` event; no visible clipping or overlap |
| Unresolved citations/references | 0 |
| BibTeX completeness warnings | 17 nonfatal inherited warnings |
| Embedded/subset/Unicode fonts | 18/18 / 18/18 / 18/18, recursively including figure forms |
| Visual rendering | All 13 exact pages rendered and inspected |
| Visual defects | 0 clipping, overlap, blank page, missing glyph, or unreadable table |
| Tested private-identity scan | PASS |

The anonymity scan covered PDF text and metadata for private filesystem paths,
the local username, Pod/SSH identities, key names, internal Goal identifiers,
agent names, branch/candidate names, and local host data. The expected
anonymous-author text remains. Third-party cited author names are not identity
leaks. This author-side scan does not replace independent anonymity review.

The single small vertical event is emitted by ACM final bibliography output.
Visual inspection of pages 12 and 13 found no clipping or overlap. This is not
a zero-warning build claim.

## 3. Source custody and buildability

Two separate Python processes constructed normalized USTAR/gzip bundles from
the exact `ed4df9330...` Git blobs. The bundles were byte-identical. The eight
members are four directories plus the following four regular files:

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `rtdl-cgo2027-source/paper/cgo2027/main.tex` | 57,947 | `81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52` |
| `rtdl-cgo2027-source/paper/cgo2027/references.bib` | 22,538 | `0bd5a31016fc847ef2ac52b45185533e16f0a23e439b83919d1794b9143da948` |
| `rtdl-cgo2027-source/paper/cgo2027/figures/reviewed_design_figures.pdf` | 62,908 | `920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092` |
| `rtdl-cgo2027-source/paper/cgo2027/figures/successor_application_performance.pdf` | 27,603 | `3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf` |

Every member uses UID/GID zero, empty owner/group names, fixed 2000-01-01 UTC
timestamps, directory mode `0555`, file mode `0444`, and gzip mtime zero.
Extraction into a fresh path containing spaces preserved all four hashes. A
Tectonic build with output outside the read-only tree produced 13 US-Letter
pages with the same layout boundary. Its PDF bytes differ because creation-time
metadata differs; only source custody and buildability are claimed.

## 4. Local executable and deterministic-figure checks

The following focused suites passed locally with `PYTHONPATH=src:.`:

| Suite | Result |
| --- | --- |
| `tests.goal5852_submission_evidence_test` | 14/14 PASS |
| `unittest discover -s tests -p 'v4_long_workload*_test.py'` | 39/39 PASS |

The performance-figure builder is pinned to projection SHA-256
`ae2cb7011f407c37b3850aa2a854d177baa4a6494d704eb2ddf68e89f574578c`.
Two independent builds were byte-identical to the committed figure at SHA-256
`3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf`.
The builder asserts all ten expected rows before rendering.

The anonymous application projection passed ordinary and optimized Python and
the two outputs were byte-identical. It reconstructed 240 workers, 80 cells,
1,248 timed samples, 120 warmups, and all ten evaluations with zero retry,
discard, or timeout.

## 5. Clean-Pod exact-candidate replay

A fresh partial clone checked out detached exact candidate
`8a485a6aae353e0d1dbfee7ce5a96610cee5d31d` on host `4735c6e75b0c`, NVIDIA
RTX A4500, driver 550.127.05, Python 3.12.3. Its tree was
`b59d795819f489d4e53f34f264eb46d31f1ec45f`, and
`git status --porcelain` was empty before and after replay.

An earlier worktree-add SSH session ended while materializing 6,485 files and
left an `initializing` worktree. That incomplete tree was rejected and never
used as evidence. The fresh clone completed to 100% before any decision.

Three retained-data replays ran from separate extraction roots under ordinary
and optimized Python:

| Replay | Reconstructed population | Output SHA-256 | Result |
| --- | --- | --- | --- |
| F2 | 160 formal workers, 20,480 steady samples, 1,024 instrumentation workers, 20 AOT observations, 8 competence workers | `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8` | byte-identical; `PASS__OFFLINE_PROJECTION_RECOUNT` |
| Application projection | 240 workers, 80 cells, 1,248 timed samples, 120 warmups, 10 evaluations | `c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9` | byte-identical; `PASS__APPLICATION_PROJECTION_RECOUNT` |
| CPU sensitivity | 384 workers and 192 paired cells over 48 logical CPUs and 2 units | `005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0` | byte-identical; `PASS__POST_FORMAL_DESCRIPTIVE_CPU_SENSITIVITY_RECOUNT` |

The CPU recount retained the adverse CPU-8 values: Particle `1.399873664x`
(rank 47/48, lower is better) and LibRTS range `0.804614022x` (rank 6/48).
No row was filtered or pooled.

The Pod system Python lacked Numba. The first extra long-workload test attempt
therefore stopped at import with `ModuleNotFoundError: numba`; this was an
environment dependency failure, not counted as a test pass or code failure.
A checkout-external temporary venv then installed exact versions Numba 0.61.2,
NumPy 2.2.6, and llvmlite 0.44.0. In that environment, the 14 and 39 test suites
both passed under ordinary and optimized Python: 106/106 total invocations.
This does not establish zero-install or package-dependency completeness.

GNU tar 1.35, when run as container root, restored the application artifact's
`0555` root directory before creating children and failed extraction even with
`--delay-directory-restore --no-same-permissions`. Both failed attempts ended
before a verifier ran. Python 3.12 `tarfile --filter data` extracted the exact
same archive successfully, after which both verifier modes passed. This is a
real extraction-portability limitation and must not be hidden.

Tectonic was initially absent on the Pod. The author-side preflight fetched the
official Tectonic 0.17.0 Linux x86-64 release asset, verified its 22,749,118-byte
payload at SHA-256
`1a715688baf591e650c8aeb160ae934e181685eecbb38b317de30b269ac5d606`,
and installed it outside the checkout. Default GNU-tar extraction first failed
because the RunPod network volume rejected restoration of the release archive's
UID/GID; extraction into a new directory with `--no-same-owner` passed. That
environment failure is retained rather than rewritten as a first-attempt pass.

The exact candidate source package then compiled in a fresh extracted path.
After the first build populated Tectonic's resource cache, a second extraction
and build under `--only-cached` also passed, establishing cached/offline
buildability on this Linux environment. Both outputs had 13 US-Letter pages,
main text ending on page 11, references beginning on page 12, zero horizontal
overfull boxes, the same single `1.87198pt` vertical event, and zero unresolved
citations or references. The committed candidate PDF and both Linux builds had
identical extracted text on all 13 pages, with joined page-text SHA-256
`14d41d1173e172e6eef9f28a3dd5e1f78df9693fbb7e6099421e0ab7aa6a1a4c`.
The two Linux builds also had byte-identical `.aux`, `.bbl`, and `.out` files.
Their PDF byte hashes differ from each other and the committed candidate because
each records a different creation timestamp; cross-build PDF byte identity is
not claimed. This is an additional author-side replay on the same retained Pod,
not an independent R7 acceptance. No CUDA/OptiX execution or new GPU measurement
occurred.

## 6. Evidence and claim scope

The successor retains 240/240 workers, 80/80 paired cells, 1,248 timed samples,
120 warmups, exact outputs, and zero retry/discard/timeout. All ten registered
complete/prepared rows met the fixed 1.20x paired-median and 1.35x every-block
engineering envelope against public PyOptiX. Only cit-Patents/4M is a
multi-second prepared natural computation.

The post-formal CPU scan remains adverse to a stronger interpretation. CPU-8
Particle changed from a formal `0.772559x` median to `1.399874x`; only 36/48
Particle CPUs and 41/48 LibRTS CPUs kept both blocks at or below 1.35x. The
scan is descriptive and not pooled. Ascending CPU order, unlocked GPU clocks,
and absent per-worker clock traces remain disclosed confounders.

The manuscript retains all 12 initial adverse application rows, the adverse
post-import lifecycle rows, receipt shortfall, limited app coverage, no
independent user study, checker/TCB limits, six unexecuted mappings, and absent
formal peak-memory data. The 31-entry claim ledger contains zero authorized
claims. P-decuple-prime adds no public, upload, or submission authorization.

## 7. Remaining R7/R8 gates

The following remain open:

- two independent acceptances of exact P-decuple-prime PDF, source bundle,
  unchanged F2, figures, and application projection;
- independent content, novelty, anonymity, bibliography, and live-link review;
- authenticated submission-form, category, author, topic, conflict, deadline,
  and time-zone verification;
- explicit user authorization for upload;
- downloaded-upload byte/hash comparison; and
- a real submission ID and receipt.

The correct state is `NOT_SUBMITTED`. No earlier candidate review transfers,
no public claim is authorized, and this report does not permit upload or
submission.
